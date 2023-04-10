import asyncio
import json
import time
from bisect import insort
from math import floor
from os import environ, makedirs, utime
from pathlib import Path

import asyncrun as ar
import config as v
from dirlist import dllcmp, lDlld, rDlld
from edge import Edge, findEdge
from netup import netup
from opbase import OpBase
from statushash import ldh_d, ldhset, rdh_d, rdh_f


def fsync(sd, td, tcfc):
    if netup():
        # print('fsync', sd, td)
        if not td.exists():
            makedirs(td, exist_ok=True)
        cmd = 'rclone sync "' + str(sd) + '" "' + str(td) + '" --progress'
        # cmd += ' --exclude ".git/**" --exclude "__pycache__/**"'
        print(cmd)
        rc = ar.run2(cmd)
        if rc == 0:
            tcfc[0] += 1
            return True
        else:
            tcfc[1] += 1
    return False


class BVar:
    def __init__(self, di, si, tcfc):
        self.si = si
        self.di = di
        self.sd = v.src(si)
        self.td = v.tgt(di)
        self.dln = None
        self.dhn = None
        self.dlo = None
        self.dho = None
        self.f2d = None
        self.f2c = None
        self.tcfc = tcfc
        self.ac1 = 0

    def init2(self):
        self.dhn = ldh_d(self.si)
        if self.dhn is None:
            return 1
        self.dho = rdh_d(self.di)
        if self.dho is None:
            return 1
        if self.dho == self.dhn:
            return 2
        self.dln = lDlld(self.si)
        if self.dln is None:
            return 3
        self.dlo = rDlld(self.di)
        if self.dlo is None:
            return 3
        self.f2d, self.f2c = dllcmp(self.dlo, self.dln)
        return 4


class CSRestore(OpBase):
    def __init__(self, npl1, npl2, opts={}):
        super(CSRestore, self).__init__(npl1, npl2, opts)

    def ischanged(self, e: Edge):
        return e.chk_ct() | e.rchk_ct()

    def __call__(self):
        tcfc = [0, 0]
        print("CSRestore")
        if not netup():
            return (tcfc[0], tcfc[1])
        di, si = self.npl1
        e: Edge = findEdge(di, si)
        if e.rchk_ct():
            print("r", di, si)
            bv = BVar(di, si, tcfc)
            rv = bv.init2()
            # sd = v.pdir(si)
            if rv == 1:  # couldn't get remote hash
                pass
            else:
                if rv == 2:  # hashes match
                    e.rclr()
                else:
                    print("hash mismatch")
                    print(bv.si, bv.dho, bv.dhn)
                    if rv == 3:  # dlo not obtainable
                        pass
                    else:
                        if len(bv.f2d):
                            print(len(bv.f2d), "todelete")
                            for it in bv.f2d:
                                print("\t", it.nm)
                        if len(bv.f2c):
                            print(len(bv.f2c), "tocopy")
                            for it in bv.f2c:
                                print("\t", it.nm)

                        for rf in bv.f2d.copy():
                            found = False
                            for lf in bv.f2c.copy():
                                # TODO: use Path
                                if rf.nm == lf.nm:  # names match
                                    found = True
                                    if rf.md5 == lf.md5:  # hashes match
                                        if rf.mt < lf.mt:
                                            print(
                                                "hashes match but it has older file time!"
                                            )
                                            print(
                                                "retrograding local copy",
                                                rf.nm,
                                                rf.mt,
                                                lf.mt,
                                            )
                                            nt = int(rf.mt * 1000) * 1000000
                                            utime(bv.sd / lf.nm, ns=(nt, nt))
                                            bv.ac1 += 1
                                            tcfc[0] += 1
                                        elif abs(rf.mt - lf.mt) <= 0.00101:
                                            print(
                                                "hashes match but remote has newer file time",
                                                lf.nm,
                                                rf.mt,
                                                lf.mt,
                                            )
                                            print("time diff is only", rf.mt - lf.mt)
                                            print(
                                                "retrograding local copy",
                                                lf.nm,
                                                rf.mt,
                                                lf.mt,
                                            )
                                            nt = int(rf.mt * 1000) * 1000000
                                            utime(bv.sd / lf.nm, ns=(nt, nt))
                                            bv.ac1 += 1
                                            tcfc[0] += 1
                                        bv.f2d.remove(rf)
                                        bv.f2c.remove(lf)
                                    else:
                                        if rf.mt > lf.mt:
                                            if fsync(
                                                bv.td / rf.nm,
                                                bv.sd / lf.nm.parent,
                                                tcfc,
                                            ):
                                                bv.f2d.remove(rf)
                                                bv.f2c.remove(lf)
                                                bv.ac1 += 1
                            if not found:
                                if fsync(bv.td / rf.nm, bv.sd / rf.nm.parent, tcfc):
                                    bv.f2d.remove(rf)
                                    bv.ac1 += 1
            if bv.ac1:
                del v.SDlls[si]
                v.SDlls_changed = True
            if tcfc[1] == 0:
                e.rclr()
        return (tcfc[0], tcfc[1])


if __name__ == "__main__":
    t1 = time.time()
    environ["TSREST"] = "True"
    if netup():
        for op in v.opdep:
            if isinstance(op, CSRestore):
                op()
    t2 = time.time()
    print(t2 - t1)
