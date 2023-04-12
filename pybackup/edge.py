import time

from bhash import blakeHash
import config as v
import ldsv


class Edge:
    def __init__(self, di, si):
        self.di = di
        self.si = si
        self.cdt = time.time()
        self.udt = self.cdt - 10
        self.rcdt = time.time()
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
        if self.udt < self.cdt:
            print("-clr", self.di, self.si)
            self.udt = self.cdt
            ldsv.saveedges()

    def rclr(self):
        if self.rudt < self.rcdt:
            print("-rclr", self.di, self.si)
            self.rudt = self.rcdt
            ldsv.saveedges()

    def rtset(self, mt=None):
        if mt is None:
            self.cdt = time.time()
        else:
            self.cdt = mt
        ldsv.saveedges()

    def rrtset(self, mt=None):
        if mt is None:
            self.rcdt = time.time()
        else:
            self.rcdt = mt
        ldsv.saveedges()

    def __repr__(self):
        return repr((self.di, self.si, self.cdt, self.udt, self.rcdt, self.rudt))


# change detected time


def findEdge(di, si) -> Edge:
    if len(v.edges) != len(v.eDep):
        for e in v.eDep:
            v.edges[e.di, e.si] = e
    return v.edges[di, si]


def lrtset(di, si):
    e: Edge = findEdge(di, si)
    e.rtset()


def addDep(j, i):
    e: Edge = Edge(j, i)
    if e not in v.eDep:
        v.eDep.add(e)


def addArc(op1):
    if op1 not in v.opdep:
        v.opdep.append(op1)
    j, i = op1.npl1
    addDep(j, i)



if __name__ == "__main__":
    lrtset("git", "pyth")
