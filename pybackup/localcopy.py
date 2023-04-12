import json
from bisect import bisect_left
from hashlib import sha256
from os import makedirs
from pathlib import Path

import asyncrun as ar
import config as v
from edge import Edge, findEdge
from findde import updateDEs
from opbase import OpBase
from status import onestatus, ronestatus


class FileDiff:
    sf = None
    df = None
    fe = 0
    sz = 0
    mt = 0
    hd = False

    def __init__(self, sf, df):
        self.sf = sf
        self.df = df

    def chkdiff(self):
        sfe = self.sf.exists()
        if sfe:
            self.fe += 1
        dfe = self.df.exists()
        if dfe:
            self.fe -= 1
        if self.fe == 0:
            sfs = self.sf.stat()
            dfs = self.df.stat()
            if sfs.st_size > dfs.st_size:
                self.sz = 1
                print("source larger:", sfs.st_size - dfs.st_size, self.sf.name)
            elif sfs.st_size < dfs.st_size:
                self.sz = -1
                print("source smaller:", dfs.st_size - sfs.st_size, self.sf.name)
            if sfs.st_mtime_ns > dfs.st_mtime_ns:
                self.mt = 1
                print(
                    "source newer:",
                    (sfs.st_mtime_ns - dfs.st_mtime_ns) / 1e9,
                    self.sf.name,
                )
            elif sfs.st_mtime_ns < dfs.st_mtime_ns:
                self.mt = -1
                print(
                    "source older:",
                    (sfs.st_mtime_ns - dfs.st_mtime_ns) / 1e9,
                    self.sf.name,
                )
            if sha256sumf(self.sf) != sha256sumf(self.df):
                self.hd = True
                print("hash mismatch:", self.sf.name)

    def should_copy(self):
        self.chkdiff()
        if self.fe > 0:
            return True
        elif self.fe < 0:
            return False
        elif self.mt > 0:
            return True
        elif self.mt < 0:
            return False
        else:
            return self.hd


class SFc:
    def __init__(self, sc=0, fc=0):
        self.sc = sc
        self.fc = fc

    def value(self):
        return (self.sc, self.fc)


def sha256sums(S1):
    ho = sha256()
    ho.update(S1)
    return ho.hexdigest()


def sha256sumf(Fn):
    if Fn.exists():
        b = Fn.read_bytes()
        ho = sha256()
        ho.update(b)
        return ho.hexdigest()
    return None


def copy2(di, si, sd, td, sfc):
    # print('copying ', f1, 'to', f2)
    if td.is_file():
        td2 = td.parent
    else:
        td2 = td
    cmd = "cp -u -p " + str(sd) + " " + str(td2)
    print("copying", sd.name)
    rv = ar.run1(cmd)
    if rv == 0:
        sfc.sc += 1
    else:
        sfc.fc -= 1
        print(ar.txt)
    return rv


# import shutil
# shutil.copy2(f1, f2)


class LocalCopy(OpBase):
    sfc = SFc()

    def __init__(self, npl1, npl2, opts={}):
        super(LocalCopy, self).__init__(npl1, npl2, opts)

    def ischanged(self, e: Edge):
        return e.chk_ct()

    def __call__(self):
        di, si = self.npl1
        e: Edge = findEdge(di, si)
        if e.chk_ct():
            print("LocalCopy", self.npl1, self.npl2)
            sp = v.src(self.npl2[1])
            dp = v.tgt(self.npl2[0])
            gl = self.opts.get("files", ["**/*"])
            for g in gl:
                try:
                    fl = sp.glob(g)
                except Exception as e:
                    print("glob error in localcopy", e)
                    self.sfc.fc += 1
                    return self.sfc.value()
                for fsf in fl:
                    if fsf.is_dir():
                        continue
                    rf = fsf.relative_to(sp)
                    fdf = dp / rf
                    pd = fdf.parent
                    try:
                        if not pd.exists():
                            makedirs(pd, exist_ok=True)
                        fdiff = FileDiff(fsf, fdf)
                        if fdiff.should_copy():
                            rv = copy2(di, si, fsf, fdf, self.sfc)
                            if rv == 0:
                                print(" ...copied.")
                                if "exec" in self.opts:
                                    fdf.chmod(496)
                                updateDEs(dp, [str(rf)])
                    except Exception as e:
                        print(e)
                        self.sfc.fc += 1
            if self.sfc.fc == 0:
                e.clr()
            if self.sfc.sc > 0:
                if di in v.srcs:
                    onestatus(di)
                if di in v.tgts:
                    ronestatus(di)
        return self.sfc.value()
