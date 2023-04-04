from pathlib import Path
from edge import Edge
from opbase import OpBase

# any/all mostly local directory path(s)
paths:dict[str, Path] = {}

# tag attributes/types/classes
pres:set[str] = set()
pdirs:set[str] = set()
tdirs:set[str] = set()
srcs:set[str] = set()
tgts:set[str] = set()
codes:set[str] = set()

# checkers
lckers = {}
rckers = {}

# operations (function objects)
opdep:list[OpBase] = []

# dependencies as edge set
eDep:set[Edge] = set()

# dependencies as stored by di,si
edges:dict[(str, str),Edge] = {}

# local file md5 hashes
fmd5hd = {}

# directory lists hashes
LDhd = {}
RDhd = {}

# directory lists
LDlls = {}
RDlls = {}

# update times of directory lists
LDlls_xt = {}
RDlls_xt = {}

LDlls_changed = False
RDlls_changed = False

# pickle file filenames
edgepf:str = None
ldllsf:str = None
rdllsf:str = None
fmd5hf:str = None
ldhpf:str = None
rdhpf:str = None

# worktree of git repo
worktree:Path = None

# directory list hashing stats
hf_dirty = False
hf_dm = 0
hf_dh = 0
hf_pm = 0
hf_ph = 0
hf_stm = 0
hf_sth = 0
sfb = 0
