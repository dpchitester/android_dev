import os
from math import floor
from os import walk
from pathlib import Path
from typing import Dict, List, Set, Tuple, TypeAlias

from cscopy import CSCopy
from de import DE, FSe
from edge import Edge, addArc, addDep
from gitclasses import GitAdd, GitCommit, GitRemote, GitRepo
from gitops import GitAdd as opGitAdd
from gitops import GitCommit as opGitCommit
from gitops import GitPush as opGitPush
from ldsv import load_all
from localcopy import LocalCopy
from mkzip import Mkzip
from opbase import OpBase
from sd import CS, SD, Ext3, Fat32

NodeTag: TypeAlias = str

# any/all mostly local directory path(s)
paths: Dict[NodeTag, Path] = {}


# tag attributes/types/classes
pres: Set[NodeTag] = set()
# pdirs: Set[NodeTag] = set()
srcs: Set[NodeTag] = set()
tgts: Set[NodeTag] = set()
codes: Set[NodeTag] = set()


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

Hdt2: TypeAlias = Dict[Path, FSe]


# files lists
LDlls: Dict[NodeTag, List["DE"]] = {}
RDlls: Dict[NodeTag, List["DE"]] = {}

# update times of directory lists
LDlls_xt: Dict[NodeTag, float] = {}
RDlls_xt: Dict[NodeTag, float] = {}

LDlls_changed: bool = False
RDlls_changed: bool = False

# pickle file filenames
edgepf: Path = None
ldllsf: Path = None
rdllsf: Path = None

ldhpf: Path = None
rdhpf: Path = None

# worktree of git repo
worktree: Path = None

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
dl4_cs = 0
dl5_cs = 0

home: Ext3 = None
sdcard: Fat32 = None
cloud1: CS = None
cloud2: CS = None
cloud3: CS = None


def initConfig():
    global home, sdcard, cloud1, cloud2, cloud3
    home = Ext3(os.environ["HOME"])
    sdcard = Fat32("/sdcard")
    cloud1 = CS("GoogleDrive:")
    cloud2 = CS("OneDrive:")
    cloud3 = CS("DropBox:")

    addPre("FLAGS", home)
    # print("FLAGS=" + str(ppre('FLAGS')))

    global edgepf, ldllsf, rdllsf, ldhpf, rdhpf

    edgepf = ppre("FLAGS") / "edges.pp"
    ldllsf = ppre("FLAGS") / "ldlls.pp"
    rdllsf = ppre("FLAGS") / "rdlls.pp"

    ldhpf = ppre("FLAGS") / "ldhd.pp"
    rdhpf = ppre("FLAGS") / "rdhd.pp"
    # print("pf's set now")
    # for pf in [edgepf, ldllsf, rdllsf, ldhpf, rdhpf]:
    #    print(pf.name, str(pf))

    addPre("sd", sdcard)
    addPre("proj", ppre("sd") / "projects")
    addPre("gd", cloud1)
    addPre("od", cloud2)
    addPre("db", cloud3)
    addPre("dsblog", Fat32(os.environ["FDB_PATH"]))

    addSrcDir("docs", ppre("sd") / "Documents", False)
    addSrcDir("blogds", ppre("dsblog"), False)
    addSrcDir("backups", ppre("sd") / "backups", False)
    addSrcDir("home", home, False)
    addSrcDir("bin", src("home") / "bin", False)
    addSrcDir("vids", ppre("sd") / "VideoDownloader/Download", False)
    addSrcDir("zips", ppre("sd") / "zips", False)
    addSrcDir(".git", ppre("proj") / ".git", False)
    addSrcDir("proj", ppre("proj"), False)

    def f1():
        dl = getDL(ppre("proj"))
        for d in dl:
            addSrcDir(d.name, d, True)
            addDep("git_add", d.name)
            addDep("zips", d.name)
            addDep("proj", d.name)

    f1()

    global worktree
    worktree = ppre("sd") / "projects"

    ga1 = GitAdd(worktree)
    ga1.tag = "git_add"
    addSrcDir("git_add", ga1)

    gc1 = GitCommit(worktree)
    gc1.tag = "git_commit"
    addSrcDir("git_commit", gc1)

    gre1 = GitRepo(worktree)
    gre1.tag = "git"
    gre1.rmts = ["bitbucket", "github"]
    addSrcDir("git", gre1)

    gre2 = GitRemote(worktree)
    gre2.url = "https://www.bitbucket.org/dpchitester/android_dev.git"
    gre2.tag = "bitbucket"
    gre2.rmt = "bitbucket"
    addTgtDir("bitbucket", gre2)

    gre3 = GitRemote(worktree)
    gre3.url = "https://github.com/dpchitester/android_dev.git"
    gre3.tag = "github"
    gre3.rmt = "github"
    addTgtDir("github", gre3)

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
        npl1 = ("git_commit", "git_add")
        op1 = opGitAdd(npl1, npl1, {"wt": worktree})
        addArc(op1)

        npl1 = ("git", "git_commit")
        op1 = opGitCommit(npl1, npl1, {"wt": worktree})
        addArc(op1)

        npl1 = ("bitbucket", "git")
        op1 = opGitPush(
            npl1,
            None,
            {"wt": worktree, "rmt": "bitbucket"},
        )
        addArc(op1)

        npl1 = ("github", "git")
        op1 = opGitPush(
            npl1,
            None,
            {"wt": worktree, "rmt": "github"},
        )
        addArc(op1)

    # for si in codes:
    # npl1 = ("zips", si)
    # op1 = Mkzip(npl1, npl1, {"zipfile": si + ".zip"})
    # addArc(op1)

    # for si in (".git",):
    # npl1 = ("zips", si)
    # op1 = Mkzip(npl1, npl1, {"zipfile": "projects-git.zip"})
    # addArc(op1)

    for cs in ("gd",):
        for si in ("proj", *codes, "vids", "zips"):
            p1 = src(si).relative_to(ppre("sd"))
            addTgtDir(cs + "_" + si, ppre(cs) / p1)
            npl1 = (cs + "_" + si, si)
            # op1 = CSRestore(npl1, None, {})
            # addArc(op1)
            op1 = CSCopy(npl1, npl1, {"delete": False})
            addArc(op1)

    load_all()


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
    if not isinstance(pth, SD):
        raise Exception("not an SD type")
    if tg in paths and paths[tg] != pth:
        raise Exception("path tag collision", tg, pth, paths[tg])
    paths[tg] = pth
    pth.tag = tg
    pth.istgt = True
    tgts.add(tg)


def addSrcDir(tg, pth, iscode=False):
    if not isinstance(pth, SD):
        raise Exception("not an SD type")
    if tg in paths and paths[tg] != pth:
        raise Exception("path tag collision", tg, pth, paths[tg])
    paths[tg] = pth
    pth.tag = tg
    pth.issrc = True
    srcs.add(tg)
    if iscode:
        codes.add(tg)


def addPre(tg, frag):
    if not isinstance(frag, SD):
        raise Exception("not an SD type")
    if tg in paths and paths[tg] != frag:
        raise Exception("path tag collision", tg, paths[tg])
    paths[tg] = frag
    frag.tag = tg
    pres.add(tg)


dexs = {
    ".cargo",
    ".cache",
    ".git",
    "node_modules",
    "__pycache__",
    ".ropeproject",
    ".mypyproject",
    ".mypy_cache",
    ".vite",
    ".idea",
    ".yarnclean",
}

def proc_DEs(des):
    des[:] = [de for de in des if not any([sd for sd in de.nm.parent.parts if sd in dexs])]

def proc_files(files, pt):
    files[:] = [pt(f) for f in files if not any([sd for sd in f.parent.parts if sd in dexs])]


def proc_dirs(dirs, pt):
    dirs[:] = [pt(d) for d in dirs if not isbaddir(pt(d))]


def isbaddir(dir):
    return any([dp for dp in dir.parts if dp in dexs])


def getDL(p):
    pt = type(p)
    # print(str(p))
    fl = []
    try:
        for pth, dirs, files in walk(p, topdown=True):
            pth = pt(pth)
            if not isbaddir(pth):
                proc_dirs(dirs, pt)
                for d in dirs.copy():
                    fl.append(pth / d)
                    dirs.remove(d)
            else:
                dirs.clear()
                files.clear()
        return fl
    except Exception as e:
        print("getDL", e)
        return fl


def ts_trunc2ms(s):
    return floor(s * 1.0e3) / 1.0e3


def ns_trunc2ms(ns):
    return floor(ns / 1.0e6) / 1.0e3
