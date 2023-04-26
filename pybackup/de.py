from dataclasses import dataclass
from pathlib import Path


@dataclass
class FSe:
    sz: int
    mt: float

    def __init__(self, sz: int, mt: float):
        self.sz = sz
        self.mt = mt


@dataclass
class DE:
    nm: Path
    i: FSe

    def __lt__(self, other):
        return self.nm < other.nm

    def __eq__(self, other):
        return self.nm == other.nm

    def __hash__(self):
        return hash((self.nm, self.i.sz, self.i.mt))
