from time import time

import ldsv as ls
from bhash import blakeHash


class Edge:
    def __init__(self, di, si):
        self.di = di
        self.si = si
        self.cdt = time()
        self.udt = self.cdt - 10
        self.rcdt = time()
        self.rudt = self.rcdt - 10

    def __hash__(self):
        return blakeHash((self.di, self.si))

    def __eq__(self, other):
        return (self.di, self.si) == (other.di, other.si)

    def chk_ct(self):
        return self.cdt > self.udt

    def rchk_ct(self):
        return self.rcdt > self.rudt

    def clr(self):
        with ls.ul1:
            if self.udt < self.cdt:
                print("-clr", self.di, self.si)
                self.udt = self.cdt
                ls.sev1.set()

    def rclr(self):
        with ls.ul1:
            if self.rudt < self.rcdt:
                print("-rclr", self.di, self.si)
                self.rudt = self.rcdt
                ls.sev1.set()

    def rtset(self, mt=None):
        with ls.ul1:
            if mt is None:
                self.cdt = time()
            else:
                self.cdt = mt
            ls.sev1.set()

    def rrtset(self, mt=None):
        with ls.ul1:
            if mt is None:
                self.rcdt = time()
            else:
                self.rcdt = mt
            ls.sev1.set()

    def __repr__(self):
        return repr((self.di, self.si, self.cdt, self.udt, self.rcdt, self.rudt))


# change detected time


def findEdge(di, si) -> Edge:
    import config as v
    with ls.ul1:
        for e in v.eDep:
            if (e.di, e.si) not in v.edges or v.edges[e.di, e.si] != e:
                v.edges[e.di, e.si] = e
                ls.sev1.set()
    return v.edges[di, si]


def lrtset(di, si):
    e: Edge = findEdge(di, si)
    e.rtset()


def addDep(j, i):
    import config as v
    with ls.ul1:
        e: Edge = Edge(j, i)
        if e not in v.eDep:
            v.eDep.add(e)
            ls.sev1.set()


def addArc(op1):
    import config as v

    with ls.ul1:
        if op1 not in v.opdep:
            v.opdep.append(op1)
            ls.sev1.set()
        j, i = op1.npl1
        addDep(j, i)


if __name__ == "__main__":
    lrtset("git", "pyth")
