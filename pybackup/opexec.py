import asyncio
from toposort import topological_sort
import config_vars as v
import snoop
import sys

_pass = 1

tsks = []


def incp():
    global _pass
    i = _pass
    _pass += 1
    return i

def clean():
    from status import changed_ops
    res = len(changed_ops()) == 0
    if res:
        print('clean')
    return res

def nodeps(T):
    import config_vars as v
    for e in v.eDep:
        if e.si == T:
            return False
    return True


def istgt(T, dep2=None):
    import config_vars as v
    if dep2 is None:
        dep2 = v.eDep
    for e in dep2:
        if e.di == T:
            return True
    return False


def nts():
    import config_vars as v
    print('-nts')
    p1 = topological_sort(v.eDep)
    ts = [t for elem in p1 for t in elem]
    ts = [d for d in ts if istgt(d)]
    ts.reverse()
    return ts


def proc_nodes(L):
    from status import updatets, rupdatets, changed_ops
    n = 1
    for node in L:
        print('node:', node)
        ss = changed_ops(node)
        for op in ss:
            tc, _ = op()
            if tc:
                updatets(n)
                #rupdatets(n)
                n += 1
    return True

try:
    depth = int(sys.argv[1])
except:
    depth = 1

@snoop(depth=depth)
def opExec():
    print('-opexec')
    g1 = nts()
    p1 = incp()
    if not proc_nodes(g1):
        return False
    if clean():
        return True
    return False


if __name__ == '__main__':
    import config
    print(opExec())
