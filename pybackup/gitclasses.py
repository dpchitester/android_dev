import asyncrun as ar
from sd import Local, Remote


class GitCmdFailure(Exception):
    pass


def gitcmd(cmd, wt):
    rc = ar.run1(cmd, cwd=wt)
    if rc != 0:
        raise GitCmdFailure("gitcmd rc: " + str(rc) + cmd)
    return ar.txt.rstrip()


class GitAdd(Local):
    def sdhck(self):
        Dh1 = self.sdh_f()
        cmd = "git status --porcelain --untracked-files=all"
        rv = gitcmd(cmd, self)
        rv = rv.split('\n')
        rv = len([ln for ln in rv if len(ln)>1 and ln[1]!=' '])
        Dh2 = rv
        if rv == 0:
            self.sdhset(Dh2)
        elif Dh2 != Dh1:
            print(rv)
        return (Dh2, rv > 0 and Dh2 != Dh1)

class GitCommit(Local):
    def sdhck(self):
        Dh1 = self.sdh_f()
        cmd = "git status --porcelain --untracked-files=all"
        rv = gitcmd(cmd, self)
        rv = rv.split('\n')
        rv = len([ln for ln in rv if len(ln)>1 and ln[0]!=' '])
        Dh2 = rv
        if rv == 0:
            self.sdhset(Dh2)
        elif Dh2 != Dh1:
            print(rv)
        return (Dh2, rv > 0 and Dh2 != Dh1)

class GitRepo(Local):
    rmts = []

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


class GitRemote(Remote):
    rmt = None
    url = None

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
