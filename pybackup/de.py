from dataclasses import dataclass
from pathlib import Path


@dataclass(order=True, unsafe_hash=True)
class FSe():
    sz: int
    mt: float

@dataclass(order=True, unsafe_hash=True)
class DE():
    nm: Path
    i: FSe

