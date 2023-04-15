import asyncrun as ar
from edge import Edge, findEdge
from gitclasses import gitcmd
from netup import netup
from opbase import OpBase


class GitOps(OpBase):
    def __init__(self, npl1, npl2, opts={}):
        super(GitOps, self).__init__(npl1, npl2, opts)

    def ischanged(self, e: Edge):
        return e.chk_ct() | e.rchk_ct()

    def __call__(self):
        print("Gitbackup")
        tc = 0
        fc = 0
        s = ""
        anyd = False
        di, si = self.npl1
        e: Edge = findEdge(di, si)
        if e.chk_ct():
            s += "l"
            anyd = True
        if e.rchk_ct():
            s += "r"
            anyd = True
        if not anyd:
            return (tc, fc)
        wt = self.opts["wt"]
        if "pull" in self.opts or "push" in self.opts:
            cmd = "git branch master -u " + di + "/master"
            try:
                rv = gitcmd(cmd, wt)
                print(rv)
            except:
                print("error:", cmd)
        if "add" in self.opts:
            rc = ar.run2("git add -A .", cwd=wt)
            if rc == 0:
                tc += 1
            else:
                fc += 1
        if "commit" in self.opts:
            rc = ar.run2("git commit -a -m pybak", cwd=wt)
            if rc in (0, 1):
                tc += 1
            else:
                print("git commit rc:", rc)
                fc += 1
        if "pull" in self.opts and "r" in s:
            rmt = self.opts.get("rmt")
            if rmt == "local" or (netup()):
                rc = ar.run2("git pull " + rmt + " master", cwd=wt)
                if rc == 0:
                    tc += 1
                else:
                    fc += 1
        if "push" in self.opts and "l" in s:
            rmt = self.opts.get("rmt")
            if rmt == "local" or (netup()):
                rc = ar.run2("git push " + rmt + " master", cwd=wt)
                if rc == 0:
                    tc += 1
                else:
                    fc += 1
        if fc == 0 and tc > 0:
            if "l" in s:
                e.clr()
            if "r" in s:
                e.rclr()
        return (tc, fc)
