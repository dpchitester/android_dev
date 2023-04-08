import asyncio

import config_vars as v
from status import changed_ops, rupdatets, updatets
from toposort import topological_sort

_pass = 1

tsks = []


def incp():
    global _pass
    i = _pass
    _pass += 1
    return i


def clean():
    res = len(changed_ops()) == 0
    if res:
        print("clean")
    return res


def nodeps(T):
    for e in v.eDep:
        if e.si == T:
            return False
    return True


def istgt(T, dep2=None):
    if dep2 is None:
        dep2 = v.eDep
    for e in dep2:
        if e.di == T:
            return True
    return False


def nts():
    print("-nts")
    p1 = topological_sort(v.eDep)
    ts = [t for elem in p1 for t in elem]
    ts = [d for d in ts if istgt(d)]
    ts.reverse()
    return ts


def proc_nodes(L):
    n = 1
    for node in L:
        print("node:", node)
        ss = changed_ops(node)
        for op in ss:
            tc, _ = op()
            if tc:
                updatets(n)
                # rupdatets(n)
                n += 1
    return True


def opExec():
    print("-opexec")
    g1 = nts()
    p1 = incp()
    if not proc_nodes(g1):
        return False
    if clean():
        return True
    return False


if __name__ == "__main__":
    import config

    print(opExec())
