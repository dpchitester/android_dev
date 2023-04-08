from os import walk, utime
from pathlib import Path
from shutil import make_archive
from opbase import OpBase
import config_vars as v
from edge import findEdge, Edge
from config_funcs import pdir, tdir
from status import onestatus
from dirlist import getRemoteDE, DE
from bisect import bisect_left


def getfl(p):
    # print(str(p))
    fl = []
    try:
        if p.is_file():
            fl.append(p)
            return fl
        for pth, dirs, files in walk(p, topdown=True):
            for f in files:
                fl.append(Path(pth, f))
        return fl
    except Exception as e:
        print(e)
        return None


def maxmt(sd):
    l1 = getfl(sd)

    def es(it):
        # TODO: use Path
        fs = it.stat()
        it3 = fs.st_mtime_ns
        return it3

    st = list(map(es, l1))
    st.sort(reverse=True)
    return st[0]


def findRDE(di, si, sd, td, dl):
    rd = td.relative_to(tdir(di))
    de = DE(rd, 0, 0, b"")
    i = bisect_left(dl, de)
    return i


class Mkzip(OpBase):
    def __init__(self, npl1, npl2, opts={}):
        super(Mkzip, self).__init__(npl1, npl2, opts)

    def ischanged(self, e: Edge):
        return e.chk_ct()

    def __call__(self):
        print("Mkzip")
        sc = 0
        fc = 0
        di1, si1 = self.npl1
        e: Edge = findEdge(di1, si1)
        if e.chk_ct():
            di2, si2 = self.npl2
            sd = pdir(si2)
            zf = self.opts.get("zipfile", "temp.zip")
            rp = Path(zf)
            td = tdir(di2)
            zp = td / rp.stem
            try:
                fp = Path(make_archive(zp, "zip", sd, ".", True))
                print(fp)
                maxt = maxmt(sd)
                utime(fp, ns=(maxt, maxt))
                sc += 1
                rde = None
                if di2 in v.LDlls:
                    rde = getRemoteDE(di2, zp)
                    ddei = findRDE(di2, si2, sd, td, v.LDlls[di2])
                    if ddei < len(v.LDlls[di2]) and rde.nm == v.LDlls[di2][ddei].nm:
                        v.LDlls[di2][ddei] = rde
                        v.LDlls_changed = True
                    else:
                        v.LDlls[di2].insert(ddei, rde)
                        v.LDlls_changed = True
                if di2 in v.RDlls:
                    if rde is None:
                        rde = getRemoteDE(di2, zp)
                    ddei = findRDE(di2, si2, sd, td, v.RDlls[di2])
                    if ddei < len(v.RDlls[di2]) and rde.nm == v.RDlls[di2][ddei].nm:
                        v.RDlls[di2][ddei] = rde
                        v.RDlls_changed = True
                    else:
                        v.RDlls[di2].insert(ddei, rde)
                        v.RDlls_changed = True
            except Exception as e:
                print(e)
                fc += 1
        if fc == 0:
            e.clr()
        if sc > 0:
            if di2 in v.LDlls:
                onestatus(di2)
            if di2 in v.RDlls:
                ronestatus(di2)
        return (sc, fc)
