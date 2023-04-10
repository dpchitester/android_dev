import math
from bisect import bisect_left
from os import utime, walk
from pathlib import Path
from shutil import make_archive

import config as v
from dirlist import getRemoteDE, findLDE, findRDE
from edge import Edge, findEdge
from opbase import OpBase
from status import onestatus, ronestatus


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
    return int(math.floor(st[0] / 1.0e6) * 1.0e6)


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
            sd = v.srcDir(si2)
            td = v.tgt(di2)
            zf = self.opts.get("zipfile", "temp.zip")
            rp = Path(zf)
            zp = td / rp.stem
            try:
                fp = Path(make_archive(zp, "zip", sd, ".", True))
                print(fp)
                maxt = maxmt(sd)
                utime(fp, ns=(maxt, maxt))
                sc += 1
                rde = None
                if di2 in v.SDlls:
                    rde = getRemoteDE(di2, fp)
                    ddei = findLDE(di2, fp, v.SDlls[di2])
                    if ddei < len(v.SDlls[di2]) and rde.nm == v.SDlls[di2][ddei].nm:
                        v.SDlls[di2][ddei] = rde
                        v.SDlls_changed = True
                    else:
                        v.SDlls[di2].insert(ddei, rde)
                        v.SDlls_changed = True
                if di2 in v.TDlls:
                    if rde is None:
                        rde = getRemoteDE(di2, fp)
                    ddei = findRDE(di2, fp, v.TDlls[di2])
                    if ddei < len(v.TDlls[di2]) and rde.nm == v.TDlls[di2][ddei].nm:
                        v.TDlls[di2][ddei] = rde
                        v.TDlls_changed = True
                    else:
                        v.TDlls[di2].insert(ddei, rde)
                        v.TDlls_changed = True
            except Exception as e:
                print(e)
                fc += 1
        if fc == 0:
            e.clr()
        if sc > 0:
            if di2 in v.SDlls:
                onestatus(di2)
            if di2 in v.TDlls:
                ronestatus(di2)
        return (sc, fc)
