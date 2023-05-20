from threading import Thread, RLock

import config
from edge import Edge, findEdge
from opbase import OpBase
from status import updatets
from toposort import topological_sort

_pass = 1


def changed_ops(T=None) -> list[OpBase]:
    rv: list[OpBase] = []
    for Op in config.opdep:
        di, si = Op.npl1
        if T is None or di == T:
            e: Edge = findEdge(di, si)
            if Op.ischanged(e):
                rv.append(Op)
    return rv


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
    return not any(e.si == T for e in config.eDep)


def istgt(T, dep2=None):
    if dep2 is None:
        dep2 = config.eDep
    return any(e.di == T for e in dep2)


def nts():
    print("-nts")
    p1 = topological_sort(config.eDep)
    ts = [t for elem in p1 for t in elem]
    ts = [d for d in ts if istgt(d)]
    ts.reverse()
    return ts


def proc_nodes(L):
    slk = RLock()
    thl = []
    n = 1
    for node in L:
        # print("node:", node)
        ss = changed_ops(node)
        for op in ss:

            def f1(op):
                nonlocal n
                sc, fc = op()
                with slk:
                    updatets(n)
                # rupdatets(n)
                n += 1

            if nodeps(op.npl1[0]):
                th = Thread(target=f1, args=(op,))
                thl.append(th)
                th.start()
            else:
                f1(op)
    while len(thl):
        th = thl.pop(0)
        th.join()


def opExec():
    print("-opexec")
    g1 = nts()
    incp()
    return proc_nodes(g1)


if __name__ == "__main__":
    config.initConfig()
    print(opExec())
