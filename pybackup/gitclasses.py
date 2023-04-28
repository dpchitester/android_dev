import asyncrun as ar
import config as v
from sd import SD
import ldsv as ls


class GitCmdFailure(Exception):
    pass


def gitcmd(cmd, wt):
    rc = ar.run1(cmd, cwd=wt)
    if rc != 0:
        raise GitCmdFailure("gitcmd rc: " + str(rc) + cmd)
    return ar.txt.rstrip()


class Local_Git_Mixin:
    def __init__(self, *args, **kwargs):
        super(Local_Git_Mixin, self).__init__()

    @property
    def isremote(self):
        return False

    @property
    def SDh(self):
        if hasattr(self, "tag"):
            with ls.dl:
                if self.tag in v.LDhd:
                    return v.LDhd[self.tag]
        return 0

    @SDh.setter
    def SDh(self, val):
        if hasattr(self, "tag"):
            with ls.dl:
                v.LDhd[self.tag] = val
                ls.sev.put("ldhd")


class Remote_Git_Mixin:
    def __init__(self, *args, **kwargs):
        super(Remote_Git_Mixin, self).__init__()

    @property
    def isremote(self):
        return True

    @property
    def SDh(self):
        if hasattr(self, "tag"):
            if self.tag in v.RDhd:
                return v.RDhd[self.tag]
        return 0

    @SDh.setter
    def SDh(self, val):
        if hasattr(self, "tag"):
            with ls.dl:
                v.RDhd[self.tag] = val
                ls.sev.put("rdhd")


class GitWT(SD, Local_Git_Mixin):
    def __init__(self, *args, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        super().__init__(*args, **kwargs)

    def sdhck(self):
        Dh1 = self.sdh_f()
        cmd = "git status --porcelain --untracked-files=all"
        rv = gitcmd(cmd, self)
        rv = rv.split("\n")
        rv = len([ln for ln in rv if len(ln) > 1 and ln[1] != " "])
        Dh2 = rv
        if rv == 0:
            self.sdhset(Dh2)
        elif Dh2 != Dh1:
            # print(rv)
            pass
        return (Dh2, rv > 0 and Dh2 != Dh1)


class GitIndex(SD, Local_Git_Mixin):
    def __init__(self, *args, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        super().__init__(*args, **kwargs)

    def sdhck(self):
        Dh1 = self.sdh_f()
        cmd = "git status --porcelain --untracked-files=all"
        rv = gitcmd(cmd, self)
        rv = rv.split("\n")
        rv = len([ln for ln in rv if len(ln) > 1 and ln[0] != " "])
        Dh2 = rv
        if rv == 0:
            self.sdhset(Dh2)
        elif Dh2 != Dh1:
            # print(rv)
            pass
        return (Dh2, rv > 0 and Dh2 != Dh1)


class GitRepo(SD, Local_Git_Mixin):
    def __init__(self, *args, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        super().__init__(*args, **kwargs)

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
        return (Dh2, rv > 0 and Dh2 != Dh1)


class GitRemote(SD, Remote_Git_Mixin):
    def __init__(self, *args, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        super().__init__(*args, **kwargs)

    def sdhck(self):
        return self.gitremoteck()

    def tdhck(self):
        return self.gitremoteck()

    def gitremoteck(self):
        Dh1 = self.sdh_f()
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
