from opbase import OpBase
from edge import Edge, findEdge

class GitCmdException(Exception):
    pass

def gitcmd(cmd, wt):
    import asyncrun as ar
    rc = ar.run1(cmd, cwd=wt)
    if rc != 0:
        raise GitCmdException('gitcmd rc: ' + str(rc))
    return ar.txt.rstrip()

def gitck1(Si, wt):
    from statushash import ldh_f, ldhset, rdh_f, rdhset
    from bhash import blakeHash
    Dh1 = ldh_f(Si)
    cmd = 'git status --porcelain --untracked-files=all'
    rv = gitcmd(cmd, wt)
    Dh2 = blakeHash(rv)
    if len(rv) == 0:
        ldhset(Si, Dh2)
    elif Dh2 != Dh1:
        print(rv)
    return (Dh2, len(rv) > 0 and Dh2 != Dh1)


def gitck2(Si, wt):
    from statushash import ldh_f, ldhset, rdh_f, rdhset
    Dh1 = ldh_f(Si)
    if Dh1 is None:
        Dh1 = 0
    cmd = 'git rev-list --count bitbucket/master..master'
    rv1 = gitcmd(cmd. wt)
    cmd = 'git rev-list --count github/master..master'
    rv2 = gitcmd(cmd. wt)
    Dh2 = int(rv1) + int(rv2)
    if Dh2 == 0:
        ldhset(Si, Dh2)
    return (Dh2, Dh2 > Dh1)



def gitremoteck(Di, wt):
    from statushash import ldh_f, ldhset, rdh_f, rdhset
    Dh1 = rdh_f(Di)
    Dh2 = None
    # print(Di, 'status here')
    try:
        cmd = 'git branch master -u ' + Di + '/master'
        gitcmd(cmd, wt)
        cmd = 'git remote update ' + Di
        gitcmd(cmd, wt)
        cmd = 'git rev-parse @'
        lcomm = gitcmd(cmd, wt)
        cmd = 'git rev-parse @{u}'
        rcomm = gitcmd(cmd, wt)
        cmd = 'git merge-base @ @{u}'
        bcomm = gitcmd(cmd, wt)
        print('lcomm', lcomm)
        print('rcomm', rcomm)
        print('bcomm', bcomm)
        if lcomm == rcomm:
            print('up-to-date')
            Dh2 = 1
        elif lcomm == bcomm:
            print('need-to-pull')
            Dh2 = 3
        elif rcomm == bcomm:
            print('need-to-push')
            Dh2 = 2
        else:
            print('diverged')
            Dh2 = 4
    except Exception as e:
        print(e)
    if Dh2 is not None:
        if Dh2 == 1:
            rdhset(Di, Dh2)
        return (Dh2, Dh2 > 1 and Dh2 != Dh1)
    return (Dh1, True)


class GitOps(OpBase):
    def __init__(self, npl1, npl2, opts={}):
        super(GitOps, self).__init__(npl1, npl2, opts)
    def ischanged(self, e:Edge):
        return e.chk_ct() | e.rchk_ct()
    def __call__(self):
        import asyncrun as ar
        from statushash import ldh_f, ldhset, rdh_f, rdhset
        from netup import netup
        print('Gitbackup')
        tc = 0
        fc = 0
        s = ''
        anyd = False
        di, si = self.npl1
        e:Edge = findEdge(di, si)
        if e.chk_ct():
            s += 'l'
            anyd = True
        if e.rchk_ct():
            s += 'r'
            anyd = True
        if not anyd:
            return (tc, fc)
        wt = self.opts['wt']
        cmd = 'git branch master -u ' + di + '/master'
        rc = ar.run1(cmd, cwd=wt)
        if 'add' in self.opts:
            rc = ar.run2('git add -A .', cwd=wt)
            if rc == 0:
                tc += 1
            else:
                fc += 1
        if 'commit' in self.opts:
            rc = ar.run2('git commit -a -m pybak', cwd=wt)
            if rc in (0, 1):
                tc += 1
            else:
                print('git commit rc:', rc)
                fc += 1
        if 'pull' in self.opts and 'r' in s:
            rmt = self.opts.get('rmt')
            if rmt == 'local' or (netup()):
                rc = ar.run2('git pull ' + rmt + ' master', cwd=wt)
                if rc == 0:
                    tc += 1
                else:
                    fc += 1
        if 'push' in self.opts and 'l' in s:
            rmt = self.opts.get('rmt')
            if rmt == 'local' or (netup()):
                rc = ar.run2('git push ' + rmt + ' master', cwd=wt)
                if rc == 0:
                    tc += 1
                else:
                    fc += 1
        if fc == 0 and tc > 0:
            if 'l' in s:
                e.clr()
            if 'r' in s:
                e.rclr()
        return (tc, fc)
