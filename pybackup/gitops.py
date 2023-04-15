import asyncrun as ar
from edge import Edge, findEdge
from gitclasses import gitcmd
from netup import netup
from opbase import OpBase
import config as v

class GitAdd(OpBase):
    def __init__(self, npl1, npl2, opts={}):
        super(GitAdd, self).__init__(npl1, npl2, opts)
    def ischanged(self, e: Edge):
        return e.chk_ct() | e.rchk_ct()
    def __call__(self):
        print("GitAdd")
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
        rc = ar.run2("git add -A .", cwd=v.paths[si])
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
        
class GitCommit(OpBase):
    def __init__(self, npl1, npl2, opts={}):
        super(GitCommit, self).__init__(npl1, npl2, opts)
    def ischanged(self, e: Edge):
        return e.chk_ct() | e.rchk_ct()
    def __call__(self):
        print("GitCommit")
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
        rc = ar.run2("git commit -a -m pybak", cwd=self.opts['wt'])
        if rc in (0, 1):
            tc += 1
        else:
            print("git commit rc:", rc)
            fc += 1
        if fc == 0 and tc > 0:
            if "l" in s:
                e.clr()
            if "r" in s:
                e.rclr()
        return (tc, fc)


class GitPush(OpBase):
    def __init__(self, npl1, npl2, opts={}):
        super(GitPush, self).__init__(npl1, npl2, opts)

    def ischanged(self, e: Edge):
        return e.chk_ct() | e.rchk_ct()

    def __call__(self):
        rmt = self.opts.get("rmt")
        print("GitPush", rmt)
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
        if rmt == "local" or (netup()):
            rc = ar.run2("git push " + rmt + " master", cwd=self.opts['wt'])
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
