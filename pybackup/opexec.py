import config as v
from status import changed_ops, updatets
from toposort import topological_sort

_pass = 1


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
    sc = 0
    fc = 0
    for node in L:
        print("node:", node)
        ss = changed_ops(node)
        for op in ss:
            sc, fc = op()
            if sc:
                updatets(n)
                # rupdatets(n)
                n += 1
    return fc == 0


def opExec():
    print("-opexec")
    g1 = nts()
    incp()
    return proc_nodes(g1) and clean()


if __name__ == "__main__":
    import config

    print(opExec())
