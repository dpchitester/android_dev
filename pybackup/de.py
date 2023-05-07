from dataclasses import dataclass
from pathlib import Path


@dataclass(order=True)
class FSe:
    sz: int
    mt: float
    def __hash__(self):
        return hash((self.sz,self.mt))


@dataclass(order=True)
class DE:
    nm: Path
    i: FSe
    def __hash__(self):
        return hash((self.nm,self.i.sz,self.i.mt))
