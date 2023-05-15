from dataclasses import dataclass, field
from time import time

import config
import ldsv as ls


@dataclass(order=True)
class Edge:
    di: str = field(compare=True, hash=True)
    si: str = field(compare=True, hash=True)
    cdt: float = field(default=time(), init=False, repr=True, hash=False, compare=False)
    udt: float = field(
        default=time() - 10, init=False, repr=True, hash=False, compare=False
    )
    rcdt: float = field(
        default=time(), init=False, repr=True, hash=False, compare=False
    )
    rudt: float = field(
        default=time() - 10, init=False, repr=True, hash=False, compare=False
    )

    def __eq__(self, other):
        return self.si == other.si and self.di == other.di

    def __hash__(self):
        return hash((self.si, self.di))

    def chk_ct(self):
        return self.cdt > self.udt

    def rchk_ct(self):
        return self.rcdt > self.rudt

    def clr(self):
        with ls.dl:
            if self.udt < self.cdt:
                print("-clr", self.di, self.si)
                self.udt = self.cdt
                ls.sev.put("edges")

    def rclr(self):
        with ls.dl:
            if self.rudt < self.rcdt:
                print("-rclr", self.di, self.si)
                self.rudt = self.rcdt
                ls.sev.put("edges")

    def rtset(self, mt=None):
        with ls.dl:
            if mt is None:
                self.cdt = time()
            else:
                self.cdt = mt
            ls.sev.put("edges")

    def rrtset(self, mt=None):
        with ls.dl:
            if mt is None:
                self.rcdt = time()
            else:
                self.rcdt = mt
            ls.sev.put("edges")

    def __repr__(self) -> str:
        return repr((self.di, self.si, self.cdt, self.udt, self.rcdt, self.rudt))


# change detected time


def findEdge(di, si) -> Edge:
    with ls.dl:
        for e in config.eDep:
            if (e.di, e.si) not in config.edges or config.edges[(e.di, e.si)] != e:
                config.edges[(e.di, e.si)] = e
                ls.sev.put("edges")
    return config.edges[(di, si)]


def lrtset(di, si):
    e: Edge = findEdge(di, si)
    e.rtset()


def addDep(j, i):
    with ls.dl:
        e: Edge = Edge(j, i)
        if e not in config.eDep:
            config.eDep.add(e)
            ls.sev.put("edges")


def addArc(op1):
    with ls.dl:
        if op1 not in config.opdep:
            config.opdep.append(op1)
        j, i = op1.npl1
        addDep(j, i)


if __name__ == "__main__":
    lrtset("git", "pyth")
