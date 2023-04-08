from os import walk, utime
from pathlib import Path
from shutil import make_archive
from opbase import OpBase
import config_vars as v
from edge import findEdge, Edge
from config_funcs import pdir, tdir
from status import onestatus


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


class Mkzip(OpBase):
    def __init__(self, npl1, npl2, opts={}):
        super(Mkzip, self).__init__(npl1, npl2, opts)
    def ischanged(self, e:Edge):
        return e.chk_ct()
    def __call__(self):
        print('Mkzip')
        tc = 0
        fc = 0
        di1, si1 = self.npl1
        e:Edge = findEdge(di1, si1)
        if e.chk_ct():
            di2, si2 = self.npl2
            sd = pdir(si2)
            zf = self.opts.get('zipfile', 'temp.zip')
            rp = Path(zf)
            zp = tdir(di2) / rp.stem
            try:
                fp = make_archive(zp, 'zip', sd, '.', True)
                print(fp)
                maxt = maxmt(sd)
                utime(fp, ns=(maxt, maxt))
                tc += 1
            except Exception as e:
                print(e)
                fc += 1
        if fc == 0:
            e.clr()
        if tc > 0:
            tv = self.npl2[0]
            if tv in v.LDlls:
                del v.LDlls[tv]
                v.LDlls_changed = True
                onestatus(tv)
        return (tc, fc)
