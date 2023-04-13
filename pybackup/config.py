import json
import os
from dataclasses import dataclass, field
from functools import partial
from math import floor
from os import walk
from pathlib import Path
from typing import Callable, Dict, List, Set, Tuple, TypeAlias, Union

import ldsv
from cscopy import CSCopy
from csrestore import CSRestore
from edge import Edge, addArc, addDep
from gitops import GitOps, gitck1, gitck2, gitremoteck
from localcopy import LocalCopy
from mkzip import Mkzip
from opbase import OpBase, OpBaseEncoder
from statushash import ldhck, rdhck

NodeTag: TypeAlias = str

# any/all mostly local directory path(s)
paths: Dict[NodeTag, Path] = {}


# tag attributes/types/classes
pres: Set[NodeTag] = set()
# pdirs: Set[NodeTag] = set()
srcs: Set[NodeTag] = set()
tgts: Set[NodeTag] = set()
codes: Set[NodeTag] = set()

# checkers
lckers: Dict[NodeTag, Callable] = {}
rckers: Dict[NodeTag, Callable] = {}

# operations (function objects)
opdep: List[OpBase] = []

# dependencies as edge set
eDep: Set[Edge] = set()

# dependencies as stored by di,si
edges: Dict[Tuple[NodeTag, NodeTag], Edge] = {}

Hash: TypeAlias = bytes

Hdt1: TypeAlias = Dict[NodeTag, Hash]

# directory lists hashes

LDhd: Hdt1 = {}
RDhd: Hdt1 = {}

Hde: TypeAlias = Tuple[int, float, Hash]
Hdt2: TypeAlias = Dict[Path, Hde]

# local file md5 hashes
fmd5hd: Hdt2 = {}

# files lists
SDlls: Dict[NodeTag, List["DE"]] = {}
TDlls: Dict[NodeTag, List["DE"]] = {}

# update times of directory lists
SDlls_xt: Dict[NodeTag, float] = {}
TDlls_xt: Dict[NodeTag, float] = {}

SDlls_changed: bool = False
TDlls_changed: bool = False

# pickle file filenames
edgepf: Path | None = None
ldllsf: Path | None = None
rdllsf: Path | None = None
fmd5hf: Path | None = None
ldhpf: Path | None = None
rdhpf: Path | None = None

# worktree of git repo
worktree: Path | None = None

# directory list hashing stats
hf_dirty: bool = False
hf_dm: int = 0
hf_dh: int = 0
hf_pm: int = 0
hf_ph: int = 0
hf_stm: int = 0
hf_sth: int = 0
sfb: int = 0

# directory list getting stats
dl0_cs = 0
dl1_cs = 0
dl2_cs = 0
dl3_cs = 0


def initConfig():
    addPre("FLAGS", os.environ["HOME"])
    # print("FLAGS=" + str(ppre('FLAGS')))

    global edgepf, ldllsf, rdllsf, fmd5hf, ldhpf, rdhpf

    edgepf = ppre("FLAGS") / "edges.pp"
    ldllsf = ppre("FLAGS") / "ldlls.pp"
    rdllsf = ppre("FLAGS") / "rdlls.pp"
    fmd5hf = ppre("FLAGS") / "fmd5h.pp"
    ldhpf = ppre("FLAGS") / "ldhd.pp"
    rdhpf = ppre("FLAGS") / "rdhd.pp"
    # print("pf's set now")
    # for pf in [edgepf, ldllsf, rdllsf, fmd5hf, ldhpf, rdhpf]:
    #    print(pf.name, str(pf))

    ldsv.load_all()

    addPre("sd", "/sdcard")
    addPre("proj", ppre("sd") / "projects")
    addPre("bkx", ppre("FLAGS") / ".bkx")
    addPre("gd", "GoogleDrive:")
    addPre("dsblog", os.environ["FDB_PATH"])

    addSrcDir("docs", ppre("sd") / "Documents", False)
    addSrcDir("blogds", ppre("dsblog"), False)
    addSrcDir("backups", ppre("sd") / "backups", False)
    addSrcDir("home", ppre("FLAGS"), False)
    addSrcDir("bin", src("home") / "bin", False)
    addSrcDir("vids", ppre("sd") / "VideoDownloader/Download", False)
    addSrcDir("zips", ppre("sd") / "zips", False)
    addSrcDir(".git", ppre("proj") / ".git", False)
    addSrcDir("proj", ppre("proj"), False)

    def f1():
        dl = getDL(ppre("proj"))
        for d in dl:
            addSrcDir(d.name, d, True)
            addDep("git_index", d.name)
            addDep("zips", d.name)
            addDep("proj", d.name)

    f1()

    global worktree
    worktree = ppre("sd") / "projects"

    srcs.add("git_index")
    lckers["git_index"] = partial(gitck1, "git_index", worktree)

    srcs.add("git")
    lckers["git"] = partial(gitck2, "git", worktree)

    tgts.add("bitbucket")
    tgts.add("github")

    rckers["bitbucket"] = partial(gitremoteck, "bitbucket", worktree)
    rckers["github"] = partial(gitremoteck, "github", worktree)

    addTgtDir("home", ppre("FLAGS"))
    addTgtDir("bin", tgt("home") / "bin")
    addTgtDir("sh", tgt("home") / "bin/sh")
    addTgtDir("pl", tgt("home") / "bin/pl")
    addTgtDir("backups", ppre("sd") / "backups")
    addTgtDir("zips", ppre("sd") / "zips")
    addTgtDir("blogds", ppre("dsblog"))
    addTgtDir("blog", ppre("proj") / "blog")
    addTgtDir("termux-backup", ppre("sd") / "backups" / "termux-backup")
    addTgtDir("bash", ppre("proj") / "bash")
    addTgtDir("plaid-node", ppre("proj") / "plaid-node")

    npl1 = ("bash", "home")
    op1 = LocalCopy(
        npl1,
        npl1,
        {
            "files": [
                ".termux/*",
                ".bashrc",
                ".bashrc0",
                ".profile",
                ".plaid-cli/*",
                ".plaid-cli/data/*",
                ".plaidrc",
                ".gitcredentials",
                ".gitconfig",
            ]
        },
    )
    addArc(op1)

    npl1 = ("home", "bash")
    op1 = LocalCopy(
        npl1,
        npl1,
        {
            "files": [
                ".termux/*",
                ".bashrc",
                ".bashrc0",
                ".profile",
                ".config/rclone/*",
                ".plaid-cli/*",
                ".plaid-cli/data/*",
                ".plaidrc",
                ".gitcredentials",
                ".gitconfig",
            ]
        },
    )
    addArc(op1)

    npl1 = ("bin", "bash")
    op1 = LocalCopy(
        npl1, npl1, {"files": ["termux-*", "pbu", "rbu", "qe"], "exec": True}
    )
    addArc(op1)

    npl1 = ("bash", "bin")
    op1 = LocalCopy(
        npl1, npl1, {"files": ["termux-*", "pbu", "rbu", "qe"], "exec": False}
    )
    addArc(op1)

    npl1 = ("sh", "bash")
    op1 = LocalCopy(npl1, npl1, {"files": ["*.sh", "*.env"], "exec": True})
    addArc(op1)

    npl1 = ("blogds", "blog")
    op1 = LocalCopy(npl1, npl1, {"files": ["blog.js"]})
    addArc(op1)

    npl1 = ("blog", "blogds")
    op1 = LocalCopy(npl1, npl1, {"files": ["*.db", "blog.js"]})
    addArc(op1)

    npl1 = ("plaid-node", "blogds")
    op1 = LocalCopy(npl1, npl1, {"files": ["*.db"]})
    addArc(op1)

    # npl1 = ('termux-backup', 'home')
    # op1 = LocalCopy(npl1, npl1, {'files': ['**/*.*']})
    # addArc(op1)

    npl1 = ("backups", "blogds")
    op1 = LocalCopy(npl1, npl1, {"files": ["*.db"]})
    addArc(op1)

    if "NOGIT" not in os.environ:
        npl1 = ("git", "git_index")
        op1 = GitOps(npl1, None, {"wt": worktree, "add": True, "commit": True})
        addArc(op1)

        npl1 = ("bitbucket", "git")
        op1 = GitOps(
            npl1,
            None,
            {"wt": worktree, "rmt": "bitbucket", "pull": True, "push": True},
        )
        addArc(op1)

        npl1 = ("github", "git")
        op1 = GitOps(
            npl1, None, {"wt": worktree, "rmt": "github", "pull": True, "push": True}
        )
        addArc(op1)

    for si in codes:
        npl1 = ("zips", si)
        op1 = Mkzip(npl1, npl1, {"zipfile": si + ".zip"})
        addArc(op1)

    for si in (".git",):
        npl1 = ("zips", si)
        op1 = Mkzip(npl1, npl1, {"zipfile": "projects-git.zip"})
        addArc(op1)

    for si in ("proj",*codes):
        p1 = src(si).relative_to(ppre("sd"))
        addTgtDir("gd_" + si, ppre("gd") / p1)
        npl1 = ("gd_" + si, si)
        # op1 = CSRestore(npl1, None, {})
        # addArc(op1)
        op1 = CSCopy(npl1, npl1, {"delete": True})
        addArc(op1)


def ppre(s):
    if s in pres:
        return paths[s]
    else:
        raise KeyError(s + " tag not in pres")


def src(s):
    if s in srcs:
        return paths[s]
    else:
        raise KeyError(s + " tag not in srcs")


def tgt(s):
    if s in tgts:
        return paths[s]
    else:
        raise KeyError(s + " tag not in tgts")


def cdir(s):
    if s in codes:
        return paths[s]
    else:
        raise KeyError(s + " tag not in codes")


def addTgtDir(tg, pth):
    if not isinstance(pth, Path):
        pth = Path(pth)
    if tg in paths and paths[tg] != pth:
        raise Exception("path tag collision", tg, pth, paths[tg])
    paths[tg] = pth
    tgts.add(tg)
    rckers[tg] = partial(rdhck, tg)


def addSrcDir(tg, pth, iscode=False):
    if not isinstance(pth, Path):
        pth = Path(pth)
    if tg in paths and paths[tg] != pth:
        raise Exception("path tag collision", tg, pth, paths[tg])
    paths[tg] = pth
    srcs.add(tg)
    lckers[tg] = partial(ldhck, tg)
    if iscode:
        codes.add(tg)


def addPre(tg, frag):
    if not isinstance(frag, Path):
        frag = Path(frag)
    if tg in paths and paths[tg] != frag:
        raise Exception("path tag collision", tg, paths[tg])
    paths[tg] = frag
    pres.add(tg)


dexs = {".cache", ".git", "node_modules", "__pycache__", ".ropeproject", ".mypyproject"}


def proc_dirs(dirs):
    dirs[:] = [d for d in dirs if not isbaddir(d)]


def isbaddir(dir):
    return any([dp for dp in Path(dir).parts if dp in dexs])


def getDL(p):
    # print(str(p))
    fl = []
    try:
        for pth, dirs, files in walk(p, topdown=True):
            if not isbaddir(pth):
                proc_dirs(dirs)
                for d in dirs.copy():
                    fl.append(Path(pth, d))
                    dirs.remove(d)
            else:
                dirs = []
                files = []
        return fl
    except Exception as e:
        print("getDL", e)
        return fl


def round2ms(ns):
    return int(str(ns + 500000)[:-6]) / 1e3


def trunc2ms(ns):
    return floor(ns / 1.0e6) / 1.0e3


@dataclass
class FSe:
    sz: int
    mt: float
    md5: bytes

    def __init__(self, sz: int, mt: float, md5: bytes):
        self.sz = sz
        self.mt = mt
        self.md5 = md5


@dataclass
class DE:
    nm: Path
    i: FSe

    def __lt__(self, other):
        return self.nm < other.nm

    def __eq__(self, other):
        return self.nm == other.nm

    def __hash__(self):
        return hash((self.nm, self.i.sz, self.i.mt, self.i.md5))
