from pathlib import Path
from edge import Edge
from opbase import OpBase
from typing import Dict, Set, List, Tuple, Union, Callable, TypeAlias
from dirlist import DE

NodeTag:TypeAlias = str

# any/all mostly local directory path(s)
paths:Dict[NodeTag, Path] = {}

# tag attributes/types/classes
pres:Set[NodeTag] = set()
pdirs:Set[NodeTag] = set()
tdirs:Set[NodeTag] = set()
srcs:Set[NodeTag] = set()
tgts:Set[NodeTag] = set()
codes:Set[NodeTag] = set()

# checkers
lckers:Dict[NodeTag, Callable] = {}
rckers:Dict[NodeTag, Callable] = {}

# operations (function objects)
opdep:List[OpBase] = []

# dependencies as edge set
eDep:Set[Edge] = set()

# dependencies as stored by di,si
edges:Dict[Tuple[NodeTag, NodeTag], Edge] = {}

Hash:TypeAlias = bytes

Hdt1:TypeAlias = Dict[NodeTag, Hash]

# directory lists hashes

LDhd:Hdt1 = {}
RDhd:Hdt1 = {}

Hde:TypeAlias = Tuple[int, float, Hash]
Hdt2:TypeAlias = Dict[Path, Union['Hdt2', Hde]] 

# local file md5 hashes
fmd5hd:Hdt2 = {}

# directory lists
LDlls:Dict[NodeTag, List[DE]] = {}
RDlls:Dict[NodeTag, List[DE]] = {}

# update times of directory lists
LDlls_xt:Dict[NodeTag, float] = {}
RDlls_xt:Dict[NodeTag, float] = {}

LDlls_changed:bool = False
RDlls_changed:bool = False

# pickle file filenames
edgepf:Path = None
ldllsf:Path = None
rdllsf:Path = None
fmd5hf:Path = None
ldhpf:Path = None
rdhpf:Path = None

# worktree of git repo
worktree:Path = None

# directory list hashing stats
hf_dirty = False
hf_dm:int = 0
hf_dh:int = 0
hf_pm:int = 0
hf_ph:int = 0
hf_stm:int = 0
hf_sth:int = 0
sfb:int = 0
dl0_cs = 0
dl1_cs= 0
dl2_cs = 0
dl3_cs = 0

