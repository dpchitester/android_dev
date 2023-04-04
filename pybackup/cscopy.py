from opbase import OpBase
from edge import Edge

class SFc():
    sc = 0
    fc = 0
    def __init__(self):
        pass
    def value(self):
        return (self.sc, self.fc)

def fsync(sd, td, sfc):
    import asyncrun as ar
    from netup import netup
    if (netup()):
        # print('fsync', sd, td)
        cmd = 'rclone sync "' + str(sd) + '" "' + str(
            td.parent) + '" --progress'
        # cmd += ' --exclude ".git/**" --exclude "__pycache__/**"'
        print(cmd)
        rc = ar.run2(cmd)
        if rc == 0:
            sfc.sc+=1
            return True
        sfc.fc+=1
    return False


def fcopy(sd, td, sfc):
    import asyncrun as ar
    from netup import netup
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
            return True
        sfc.fc+=1
    return False


def fdel(td, sfc):
    import asyncrun as ar
    from netup import netup
    if (netup()):
        cmd = 'rclone delete "' + str(td) + '" --progress'
        print(cmd)
        rc = ar.run2(cmd)
        if rc == 0:
            sfc.sc+=1
            return True
        sfc.fc+=1
    return False


class BVars():
    def __init__(self, di, si, sfc):
        from config_funcs import pdir, tdir
        self.si = si
        self.di = di
        self.sd = pdir(si)
        self.td = tdir(di)
        self.src_dls = None
        self.dst_dls = None
        self.f2d = None
        self.f2c = None
        self.sfc = sfc
        self.ac1 = 0
        self.ac2 = 0

    def init2(self):
        from dirlist import dllcmp, lDlld, rDlld
        self.src_dls = lDlld(self.si)
        if self.src_dls is None:
            self.sfc.fc+=1
        self.dst_dls = rDlld(self.di)
        if self.dst_dls is None:
            self.sfc.fc+=1
        if self.src_dls is not None and self.dst_dls is not None:
            self.f2d, self.f2c = dllcmp(self.dst_dls, self.src_dls)

    def skip_matching(self):
        from os import utime
       # handle slip through mismatched on times or more recent
        for rf in self.f2d.copy():
            for lf in self.f2c.copy():
                # TODO: use Path
                if rf.nm == lf.nm:  # names match
                    if rf.md5 == lf.md5:  # hashes match
                        # TODO: correct for conflicting times
                        self.f2d.remove(rf)
                        self.f2c.remove(lf)
                        print('time conflict', rf.nm)
                        print(rf.mt, '--', lf.mt)
                        b1 = abs(rf.mt - lf.mt) <= .00101
                        b2 = rf.mt < lf.mt
                        if b1:
                            print('time diff is only', rf[2] - lf[2])
                        if b1 or b2:
                            print('retrograding local timestamp', lf.nm)
                            nt = int(rf.mt * 1000) * 1000000
                            print('to', nt)
                            utime(self.sd / lf.nm, ns=(nt, nt))
                            self.ac1 += 1
                    else:
                        b1 = rf.mt > lf.mt
                        if b1:
                            print('newer file on cloud', rf.nm)
                            self.f2d.remove(rf)
                            self.f2c.remove(lf)

    def do_copying(self):
        for lf in self.f2c.copy():
            # TODO: use Path
            cfp = lf.nm
            # print(cfp)
            if fsync(self.sd / cfp, self.td / cfp, self.sfc):
                self.ac2 += 1
                self.f2c.remove(lf)
                for rf in self.f2d.copy():
                    if rf.nm == lf.nm:
                        self.f2d.remove(rf)

    def do_deletions(self):
        for rf in self.f2d.copy():  # do deletions
            cfp = rf.nm
            if fdel(self.td / cfp, self.tcfc):
                self.f2d.remove(rf)
                self.ac2 += 1


class CSCopy(OpBase):
    def __init__(self, npl1, npl2, opts={}):
        super(CSCopy, self).__init__(npl1, npl2, opts)
        self.sfc = SFc()
    def ischanged(self, e:Edge):
        return e.chk_ct() | e.rchk_ct()        
    def __call__(self):
        import config_vars as v
        from netup import netup
        from edge import findEdge
        print('CSCopy')
        if not netup():
            return False
        di, si = self.npl1
        e:Edge = findEdge(di, si)
        if e.chk_ct():
            bv = BVars(di, si, self.sfc)
            bv.init2()
            if bv.sfc.fc == 0:
                print(len(bv.f2d), 'todelete', len(bv.f2c), 'tocopy')
                bv.skip_matching()
                bv.do_copying()
                if 'delete' in self.opts and self.opts['delete']:
                    bv.do_deletions()
                if bv.ac2:
                    del v.RDlls[di]
                    v.RDlls_changed = True
                    # rnoc(di)
                if bv.ac1:
                    del v.LDlls[si]
                    v.LDlls_changed = True
                    # noc(si)
        if self.sfc.fc == 0:
            e.clr()
        return self.sfc.value()
