from os import utime
import json
from pathlib import Path
import datetime

import config_vars as v
from config_funcs import pdir, tdir, ppre
import asyncrun as ar
from netup import netup
from opbase import OpBase
from edge import Edge, findEdge
from dirlist import dllcmp, lDlld, rDlld, DE
from bisect import bisect_left
from status import onestatus

class SFc():
    sc = 0
    fc = 0
    def __init__(self):
        pass
    def value(self):
        return (self.sc, self.fc)

def getRemoteDE(di, sf:Path):
    cmd = 'rclone lsjson "' + str(sf) + '" --hash'
    rc = ar.run1(cmd)
    if rc == 0:
        rd = sf.relative_to(tdir(di)).parent
        it = json.loads(ar.txt)[0]
        it1 = rd / it['Path']
        it2 = it['Size']
        it3 = it['ModTime'][:-1] + '-00:00'
        it3 = datetime.datetime.fromisoformat(it3).timestamp()
        if 'Hashes' in it:
            it4 = bytes.fromhex(it['Hashes']['md5'])
        else:
            it4 = bytes()
        nde = DE(it1, it2, it3, it4)
        print('new nde:', str(nde))
        return nde

def findLDE(di, si, sd, td, dl):
    ld = sd.relative_to(pdir(si))
    de = DE(ld, 0, 0, b'')
    i = bisect_left(dl, de)
    return i

def findRDE(di, si, sd, td, dl):
    rd = td.relative_to(tdir(di))
    de = DE(rd, 0, 0, b'')
    i = bisect_left(dl, de)
    return i

def fsync(di, si, sd, td, sfc):
    if (netup()):
        # print('fsync', sd, td)
        cmd = 'rclone sync "' + str(sd) + '" "' + str(
            td.parent) + '" --progress'
        # cmd += ' --exclude ".git/**" --exclude "__pycache__/**"'
        print(cmd)
        rc = ar.run2(cmd)
        if rc == 0:
            sfc.sc += 1
            rde = getRemoteDE(di, td)
            ddei = findRDE(di, si, sd, td, v.RDlls[di])
            if ddei < len(v.RDlls[di]) and rde.nm == v.RDlls[di][ddei].nm:
                v.RDlls[di][ddei] = rde
                v.RDlls_changed = True
                onestatus(si)
            else:
                v.RDlls[di].insert(ddei, rde)
                v.RDlls_changed = True
                onestatus(si)
            return True
    sfc.fc+=1
    return False


def fcopy(di, si, sd, td, sfc):
    if (netup()):
        # print('fcopy', sd, td)
        cmd = 'rclone copyto "' + str(sd) + '" "' + str(
            td) + '" --ignore-checksum --ignore-times --no-traverse --progress'
        # if not sd.is_file():
        #    cmd += ' --exclude ".git/**" --exclude "__pycache__/**"'
        print(cmd)
        rc = ar.run2(cmd)
        if rc == 0:
            sfc.sc+=1
            rde = getRemoteDE(di, td)
            ddei = findRDE(di, si, sd, td, v.RDlls[di])
            if ddei < len(v.RDlls[di]) and rde.nm == v.RDlls[di][ddei].nm:
                v.RDlls[di][ddei] = rde
                v.RDlls_changed = True
                onestatus(si)
            else:
                v.RDlls[di].insert(ddei, rde)
                v.RDlls_changed = True
                onestatus(si)
            return True
        sfc.fc+=1
    return False


def fdel(di, si, sd, td, sfc):
    if (netup()):
        cmd = 'rclone delete "' + str(td) + '" --progress'
        print(cmd)
        rde = getRemoteDE(di, td)
        rc = ar.run2(cmd)
        if rc == 0:
            sfc.sc += 1
            ddei = findRDE(di, si, sd, td, v.RDlls[di])
            if ddei < len(v.RDlls[di]) and rde.nm == v.RDlls[di][ddei].nm:
                v.RDlls[di].pop(ddei)
                v.RDlls_changed = True
                onestatus(si)
            return True
        sfc.fc+=1
    return False


class BVars():
    def __init__(self, di, si, sfc):
        self.si = si
        self.di = di
        self.sd = pdir(si)
        self.td = tdir(di)
        self.src_dls = None
        self.dst_dls = None
        self.f2d = None
        self.f2c = None
        self.sfc = sfc
        self.ac2 = 0

    def init2(self):
        self.src_dls = lDlld(self.si)
        if self.src_dls is None:
            self.sfc.fc+=1
        self.dst_dls = rDlld(self.di)
        if self.dst_dls is None:
            self.sfc.fc+=1
        if self.src_dls is not None and self.dst_dls is not None:
            self.f2d, self.f2c = dllcmp(self.dst_dls, self.src_dls)

    def skip_matching(self):
       # handle slip through mismatched on times or more recent
        for rf in self.f2d.copy():
            for lf in self.f2c.copy():
                # TODO: use Path
                if rf.nm == lf.nm:  # names match
                    if rf.md5 == lf.md5:  # hashes match
                        self.f2d.remove(rf)
                        self.f2c.remove(lf)
                    else:
                        b1 = rf.mt > lf.mt
                        if b1:
                            print('newer mismatched file on cloud', rf.nm)
                            self.f2d.remove(rf)
                            self.f2c.remove(lf)

    def do_copying(self):
        for lf in self.f2c.copy():
            # TODO: use Path
            cfp = lf.nm
            # print(cfp)
            if fsync(self.di, self.si, self.sd / cfp, self.td / cfp, self.sfc):
                self.ac2 += 1
                self.f2c.remove(lf)
                for rf in self.f2d.copy():
                    if rf.nm == lf.nm:
                        self.f2d.remove(rf)

    def do_deletions(self):
        for rf in self.f2d.copy():  # do deletions
            cfp = rf.nm
            if fdel(self.di, self.si, self.sd /cfp, self.td / cfp, self.sfc):
                self.f2d.remove(rf)
                self.ac2 += 1


class CSCopy(OpBase):
    def __init__(self, npl1, npl2, opts={}):
        super(CSCopy, self).__init__(npl1, npl2, opts)
        self.sfc = SFc()
    def ischanged(self, e:Edge):
        return e.chk_ct() | e.rchk_ct()        
    def __call__(self):
        print('CSCopy')
        if not netup():
            self.sfc.fc+=1
            return self.sfc.value()
        di, si = self.npl1
        e:Edge = findEdge(di, si)
        if e.chk_ct():
            bv = BVars(di, si, self.sfc)
            bv.init2()
            if bv.sfc.fc == 0:
                print('raw', len(bv.f2d), 'todelete', len(bv.f2c), 'tocopy')
                bv.skip_matching()
                print('skip', len(bv.f2d), 'todelete', len(bv.f2c), 'tocopy')
            if bv.sfc.fc == 0:
                bv.do_copying()
            if bv.sfc.fc == 0:
                if 'delete' in self.opts and self.opts['delete']:
                    bv.do_deletions()
            if bv.ac2:
                pass
        if self.sfc.fc == 0:
            e.clr()
        return self.sfc.value()
