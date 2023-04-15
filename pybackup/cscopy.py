import asyncrun as ar
import config as v
from dirlist import dllcmp
from edge import Edge, findEdge
from findde import updateDEs
from netup import netup
from opbase import OpBase
from status import onestatus


class SFc:
    sc = 0
    fc = 0

    def __init__(self):
        pass

    def value(self):
        return (self.sc, self.fc)


def fsync(di, si, sd, td, sfc):
    if netup():
        # print('copy', sd, td)
        cmd = (
            'rclone copy "'
            + str(sd.parent)
            + '" "'
            + str(td.parent)
            + '" --include "'
            + str(td.name)
            + '" --progress'
        )
        # cmd += ' --exclude ".git/**" --exclude "__pycache__/**"'
        print(cmd)
        rc = ar.run2(cmd)
        if rc == 0:
            sfc.sc += 1
            return True
        else:
            sfc.fc += 1
            print(ar.txt)
    return False


def fsyncl(di, si, sd, td, fl, sfc):
    cmd = 'rclone copy "'
    cmd += str(sd) + '" "'
    cmd += str(td) + '" '
    for fn in fl:
        cmd += '--include "' + str(fn.nm) + '" '
    cmd += "--progress "
    # cmd += '--exclude "**/.git/**/*" '
    # cmd += '--exclude "**/__pycache__/**/*" '
    # cmd += '--exclude "**/node_modules/**/*" '
    # cmd += '--log-file="rclone.log" '
    # cmd += "--use-json-log"
    if netup():
        print("copy", sd, td, list(map(lambda de: str(de.nm), fl)))
        # print(cmd)
        rc = ar.run2(cmd)
        if rc == 0:
            sfc.sc += len(fl)
            return True
        else:
            sfc.fc += 1
            print(ar.txt)
    return False


def fdel(di, si, sd, td, sfc):
    if netup():
        cmd = 'rclone delete "' + str(td) + '"' + " --progress"
        print(cmd)
        rc = ar.run2(cmd)
        if rc == 0:
            sfc.sc += 1
            return True
        else:
            sfc.fc += 1
            print(ar.txt)
    return False


def fdell(di, si, sd, td, fl, sfc):
    cmd = 'rclone delete "'
    cmd += str(td) + '" '
    for fn in fl:
        cmd += '--include "' + str(fn.nm) + '" '
    cmd += "--progress "
    # cmd += '--log-file="rclone.log" '
    # cmd += "--use-json-log"
    if netup():
        print("delete", sd, td, list(map(lambda de: str(de.nm), fl)))
        # print(cmd)
        rc = ar.run2(cmd)
        if rc == 0:
            sfc.sc += 1
            return True
        else:
            sfc.fc += 1
            print(ar.txt)
    return False


class BVars:
    def __init__(self, di, si, sfc):
        self.si = si
        self.di = di
        self.sd = v.src(si)
        self.td = v.tgt(di)
        self.src_dls = None
        self.dst_dls = None
        self.f2d = None
        self.f2c = None
        self.sfc = sfc
        self.ac2 = 0

    def init2(self):
        self.src_dls = self.sd.Dlld()
        if self.src_dls is None:
            self.sfc.fc += 1
        self.dst_dls = self.td.Dlld()
        if self.dst_dls is None:
            self.sfc.fc += 1
        if self.src_dls is not None and self.dst_dls is not None:
            self.f2d, self.f2c = dllcmp(self.dst_dls, self.src_dls)

    def skip_matching(self):
        # handle slip through mismatched on times or more recent
        for rf in self.f2d.copy():
            for lf in self.f2c.copy():
                # TODO: use Path
                if rf.nm == lf.nm:  # names match
                    if rf.i.md5 == lf.i.md5:  # hashes match
                        self.f2d.remove(rf)
                        self.f2c.remove(lf)
                    else:
                        b1 = rf.i.mt > lf.i.mt
                        if b1:
                            print("newer mismatched file on cloud", rf.nm)
                            self.f2d.remove(rf)
                            self.f2c.remove(lf)

    def do_copying(self):
        # TODO: use Path
        cfpl = self.f2c.copy()
        if len(cfpl) == 0:
            return
        # print(cfp)
        if fsyncl(self.di, self.si, self.sd, self.td, cfpl, self.sfc):
            for lf in cfpl:
                self.ac2 += 1
                self.f2c.remove(lf)
                for rf in self.f2d.copy():
                    if rf.nm == lf.nm:
                        self.f2d.remove(rf)
            updateDEs(self.td, [str(de.nm) for de in cfpl])

    def do_deletions(self):
        cfpl = self.f2d.copy()
        if len(cfpl) == 0:
            return
        if fdell(self.di, self.si, self.sd, self.td, cfpl, self.sfc):
            for rf in cfpl:  # do deletions
                self.ac2 += 1
                self.f2d.remove(rf)
            updateDEs(self.td, [str(de.nm) for de in cfpl])


class CSCopy(OpBase):
    def __init__(self, npl1, npl2, opts={}):
        super(CSCopy, self).__init__(npl1, npl2, opts)
        self.sfc = SFc()

    def ischanged(self, e: Edge):
        return e.chk_ct() or e.rchk_ct()

    def __call__(self):
        print("CSCopy")
        if not netup():
            self.sfc.fc += 1
            return self.sfc.value()
        di, si = self.npl1
        e: Edge = findEdge(di, si)
        if e.chk_ct():
            bv = BVars(di, si, self.sfc)
            bv.init2()
            if bv.sfc.fc == 0:
                print("raw", len(bv.f2d), "todelete", len(bv.f2c), "tocopy")
                bv.skip_matching()
                print("skip", len(bv.f2d), "todelete", len(bv.f2c), "tocopy")
            if bv.sfc.fc == 0:
                bv.do_copying()
            if bv.sfc.fc == 0:
                if "delete" in self.opts and self.opts["delete"]:
                    bv.do_deletions()
            if bv.ac2:
                pass
        if self.sfc.fc == 0:
            e.clr()
            e.rclr()
        if self.sfc.sc > 0:
            if di in v.srcs:
                onestatus(di)
        return self.sfc.value()
