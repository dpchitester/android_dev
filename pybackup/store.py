import datetime
import time
from pathlib import Path, PosixPath
from os import walk
import json

import asyncrun as ar
import ldsv

rto1 = 60 * 0
rto2 = 60 * 0


class SD(type(Path())):
    _flavour = type(Path())._flavour
    tag = None
    issrc = None
    istgt = None
    isremote = False
    Dll = None
    Dll_xt = 0
    Dll_changed = False
    SDh = None
    TDh = None



    def sdh_f(self, dh=None):
        odh = self.SDh
        if dh is not None:
            self.SDh = dh
        return odh

    def sdh_d(self):
        from bhash import blakeHash

        Si_dl = self.Dlld()
        if Si_dl is not None:
            return blakeHash(Si_dl)
        return None

    def sdhset(self, Dh=None):
        import ldsv

        if Dh is None:
            Dh = self.sdh_d()
        if Dh is not None:
            self.sdh_f(Dh)
            ldsv.saveldh()

    def sdhck(self):
        Dh1 = self.sdh_f()
        Dh2 = self.sdh_d()
        if Dh2 is not None:
            return (Dh2, Dh1 != Dh2)
        return (None, False)

    def Dlld(self):
        p = self
        # print('-ldlld', si)
        print("obtaining", self.tag, "dll...", end="")
        if p.Dll is None or p.Dll_xt + rto1 <= time.time():
            rv = p.getdll()
            if rv is not None:
                print("done.")
                p.Dll = rv
                p.Dll_xt = time.time()
                p.Dll_changed = True
            else:
                print("failed.")
        else:
            print("retrieved.")
            pass
        return p.Dll


class Local(SD):
    _flavour = type(Path())._flavour


    def getfl(self):
        import config as v

        pt = type(self)
        # print(str(p))
        fl = []
        try:
            if self.is_file():
                fl.append(self)
                return fl
            for pth, dirs, files in walk(self, topdown=True):
                pth = pt(pth)
                if not v.isbaddir(pth):
                    v.proc_dirs(dirs, pt)
                    for f in files:
                        fl.append(pth / f)
                else:
                    dirs = []
                    files = []
            return fl
        except Exception as e:
            print(e)
        return fl

    def getdll(self):  # local-source
        import config as v
        from fmd5h import fmd5f

        v.dl3_cs += 1
        # print('getdll3', si, str(sd))
        l1 = self.getfl()

        def es(it):
            it1 = it.relative_to(self)
            fs = it.stat()
            it2 = fs.st_size
            it3 = fs.st_mtime_ns
            it3 = v.trunc2ms(it3)
            fp = self / it1
            fse = fmd5f(fp, it2, it3)
            return v.DE(it1, fse)

        st = list(map(es, l1))
        st.sort(key=lambda de: de.nm)
        return st


class Remote(SD):
    _flavour = type(Path())._flavour
    isremote = True


class Ext3(Local):
    _flavour = type(Path())._flavour


class Fat32(Local):
    _flavour = type(Path())._flavour


class CS(Remote):
    _flavour = type(Path())._flavour


    def getfl(self):
        import config as v

        cmd = 'rclone lsjson "' + str(self) + '" --recursive --files-only --hash '
        for ex in v.dexs:
            cmd += ' --exclude "**/' + ex + '/*" '
        rc = ar.run1(cmd)
        if rc == 0:
            l1 = json.loads(ar.txt)
            return l1
        if rc == 3:
            return []
        return None

    def getdll(self):  # remote-source
        import config as v
        from fmd5h import fmd5f

        v.dl5_cs += 1
        pt = type(self)
        # print('getdll1', di, str(td))
        l1 = self.getfl()
        if l1:

            def es(it: dict):
                # TODO: use Path
                it1 = pt(it["Path"])
                it2 = it["Size"]
                it3 = it["ModTime"][:-1] + "-00:00"
                it3 = datetime.datetime.fromisoformat(it3).timestamp()
                if "Hashes" in it:
                    it4 = bytes.fromhex(it["Hashes"]["md5"])
                else:
                    it4 = bytes()
                fp = self / it1
                fse = fmd5f(fp, it2, it3, it4)
                return v.DE(it1, fse)

            st = list(map(es, l1))
            st.sort(key=lambda de: de.nm)
            return st
        return None


class GitCmdFailure(Exception):
    pass


def gitcmd(cmd, wt):
    rc = ar.run1(cmd, cwd=wt)
    if rc != 0:
        raise GitCmdFailure("gitcmd rc: " + str(rc) + cmd)
    return ar.txt.rstrip()


class GitIndex(Local):

    def sdhck(self):
        return self.gitck1()

    def gitck1(self):
        from bhash import blakeHash
        Dh1 = self.sdh_f()
        cmd = "git status --porcelain --untracked-files=all"
        rv = gitcmd(cmd, self)
        Dh2 = blakeHash(rv)
        if len(rv) == 0:
            self.sdhset(Dh2)
        elif Dh2 != Dh1:
            print(rv)
        return (Dh2, len(rv) > 0 and Dh2 != Dh1)


class GitRepo(Local):
    rmts = None


    def sdhck(self):
        return self.gitck2()

    def gitck2(self):
        Dh1 = self.sdh_f()
        if Dh1 is None:
            Dh1 = 0
        rv = 0
        for rmt in self.rmts:
            cmd = "git rev-list --count " + rmt + "/master..master"
            rv += int(gitcmd(cmd, self))
        Dh2 = rv
        if Dh2 == 0:
            self.sdhset(Dh2)
        return (Dh2, Dh2 > Dh1)

class GitRemote(Remote):
    rmt = None


    def tdhck(self):
        return self.gitremoteck()

    def gitremoteck(self):
        Dh1 = self.tdh_f()
        Dh2 = None
        # print(Di, 'status here')
        cmd = ""
        try:
            cmd = "git branch master -u " + self.rmt + "/master"
            gitcmd(cmd, self)
            cmd = "git remote update " + self.rmt
            gitcmd(cmd, self)
            cmd = "git rev-parse @"
            lcomm = gitcmd(cmd, self)
            cmd = "git rev-parse @{u}"
            rcomm = gitcmd(cmd, self)
            cmd = "git merge-base @ @{u}"
            bcomm = gitcmd(cmd, self)
            # print('lcomm', lcomm)
            # print('rcomm', rcomm)
            # print('bcomm', bcomm)
            if lcomm == rcomm:
                print("up-to-date")
                Dh2 = 1
            elif lcomm == bcomm:
                print("need-to-pull")
                Dh2 = 3
            elif rcomm == bcomm:
                print("need-to-push")
                Dh2 = 2
            else:
                print("diverged")
                Dh2 = 4
        except GitCmdFailure as e:
            print(e)
        if Dh2 is not None:
            if Dh2 == 1:
                self.sdhset(Dh2)
            return (Dh2, Dh2 > 1 and Dh2 != Dh1)
        return (Dh1, True)
