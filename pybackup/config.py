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
Hash: TypeAlias = bytes
Hdt1: TypeAlias = Dict[NodeTag, int]
Hdt2: TypeAlias = Dict[Path, FSe]

# any/all mostly local directory path(s)
# paths: Dict[NodeTag, Path] = {}


class SetDict(dict):
    paths: Dict[NodeTag, SD] = {}

    def __init__(self, *args):
        super(SetDict, self).__init__(*args)

    def add(self, tg:str, sd:SD):
        if not hasattr(sd, "tag"):
            setattr(sd, "tag", tg)
        if tg in self.paths and sd != self.paths[tg]:
            raise ValueError("tag " + tg + " already in paths-dict with different path")
        self[tg] = sd
        self.paths[tg] = sd


pres = SetDict()
srcs = SetDict()
tgts = SetDict()
codes = SetDict()


def ppre(s):
    return pres[s]


def src(s):
    return srcs[s]


def tgt(s):
    return tgts[s]


def cdir(s):
    return codes[s]


def addSrcDir(tg, pth, iscode=False):
    if not isinstance(pth, SD):
        raise Exception("not an SD subclass")
    srcs.add(tg, pth)
    pth.issrc = True
    if iscode:
        codes.add(tg, pth)
    if pth.isremote:
        RDlls[tg] = None
        RDlls_xt[tg] = 0
        RDlls_changed = False
        RDhd[tg] = 0
    else:
        LDlls[tg] = None
        LDlls_xt[tg] = 0
        LDlls_changed = False
        LDhd[tg] = 0


def addTgtDir(tg, pth):
    if not isinstance(pth, SD):
        raise Exception("not an SD subclass")
    tgts.add(tg, pth)
    pth.istgt = True
    if pth.isremote:
        RDlls[tg] = None
        RDlls_xt[tg] = 0
        RDlls_changed = False
        RDhd[tg] = 0
    else:
        LDlls[tg] = None
        LDlls_xt[tg] = 0
        LDlls_changed = False
        LDhd[tg] = 0


def addPre(tg, frag):
    if not isinstance(frag, SD):
        raise Exception("not an SD subclass")
    pres.add(tg, frag)


# operations (function objects)
opdep: List[OpBase] = []

# dependencies as edge set
eDep: Set[Edge] = set()

# dependencies as stored by di,si
edges: Dict[Tuple[NodeTag, NodeTag], Edge] = {}


# directory lists hashes

LDhd: Hdt1 = {}
RDhd: Hdt1 = {}


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

sfb: int = 0

# directory list getting stats

dl1_cs = 0
dl2_cs = 0


home: Ext3 = None
sdcard: Fat32 = None
cloud1: CS = None
cloud2: CS = None
cloud3: CS = None

sdhes = {}


def update_sdhes(t, h, nh):
    global sdhes
    if t not in sdhes:
        sdhes[t] = [0, 0]
    sdhes[t][0] += h
    sdhes[t][1] += nh


def check_sdhes(i):
    global sdhes
    return
    print("check _sdhes (" + str(i) + ")")
    sdhes = {}
    ha = 0
    nha = 0
    for tg in srcs:
        it = src(tg)
        cha = hasattr(it, "_sdh")
        if cha:
            update_sdhes(type(it), 1, 0)
        else:
            update_sdhes(type(it), 0, 1)
    for t in sdhes:
        print(sdhes[t][0], t, "'s have", sdhes[t][1], "don't")


def initConfig():
    check_sdhes(0)
    global home, sdcard, cloud1, cloud2, cloud3
    home = Ext3(os.environ["HOME"], tag="home")
    sdcard = Fat32("/storage/emulated/0", tag="sdcard")
    cloud1 = CS("GoogleDrive:", tag="cloud1")
    cloud2 = CS("OneDrive:", tag="cloud2")
    cloud3 = CS("DropBox:", tag="cloud3")

    addPre("FLAGS", home)
    # print("FLAGS=" + str(ppre('FLAGS')))

    global edgepf, ldllsf, rdllsf, ldhpf, rdhpf

    edgepf = home / "edges.pp"
    ldllsf = home / "ldlls.pp"
    rdllsf = home / "rdlls.pp"

    ldhpf = home / "ldhd.pp"
    rdhpf = home / "rdhd.pp"
    # print("pf's set now")
    # for pf in [edgepf, ldllsf, rdllsf, ldhpf, rdhpf]:
    #    print(pf.name, str(pf))

    check_sdhes(1)

    addPre("sd", sdcard)
    addPre("gd", cloud1)
    addPre("od", cloud2)
    addPre("db", cloud3)
    addPre("dsblog", Fat32(os.environ["FDB_PATH"], tag="dsblog"))
    check_sdhes(2)

    addSrcDir("home", home, False)
    addSrcDir("bin", home / "bin", False)
    addSrcDir("proj", sdcard / "projects", True)
    addSrcDir("docs", sdcard / "Documents", False)
    addSrcDir("blogds", ppre("dsblog"), False)
    addSrcDir("backups", sdcard / "backups", False)
    addSrcDir("vids", sdcard / "VideoDownloader/Download", False)
    addSrcDir("zips", sdcard / "zips", False)
    addSrcDir(".git", src("proj") / ".git", False)
    check_sdhes(3)

    def f1():
        dl = getDL(src("proj"))
        for d in dl:
            addSrcDir(d.name, d, True)
            addDep("git_add", d.name)
            addDep("zips", d.name)
            addDep("proj", d.name)

    f1()
    check_sdhes(4)

    global worktree
    worktree = sdcard / "projects"

    ga1 = GitAdd(worktree, tag="git_add")
    addSrcDir("git_add", ga1)

    gc1 = GitCommit(worktree, tag="git_commit")
    addSrcDir("git_commit", gc1)

    gre1 = GitRepo(worktree, tag="git", rmts=["bitbucket", "github"])
    addSrcDir("git", gre1)

    gre2 = GitRemote(
        worktree,
        url="https://www.bitbucket.org/dpchitester/android_dev.git",
        tag="bitbucket",
        rmt="bitbucket",
    )
    addTgtDir("bitbucket", gre2)

    gre3 = GitRemote(
        worktree,
        url="https://github.com/dpchitester/android_dev.git",
        tag="github",
        rmt="github",
    )
    addTgtDir("github", gre3)
    check_sdhes(5)

    addTgtDir("home", home)
    addTgtDir("bin", home / "bin")
    addTgtDir("sh", home / "bin/sh")
    addTgtDir("pl", home / "bin/pl")
    addTgtDir("backups", sdcard / "backups")
    addTgtDir("termux-backup", tgt("backups") / "termux-backup")
    addTgtDir("zips", sdcard / "zips")
    addTgtDir("blogds", ppre("dsblog"))
    addTgtDir("blog", src("proj") / "blog")
    addTgtDir("bash", src("proj") / "bash")
    addTgtDir("plaid-node", src("proj") / "plaid-node")
    check_sdhes(6)

    load_all()
    check_sdhes(7)

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
    op2 = LocalCopy(
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
    addArc(op2)

    npl1 = ("bin", "bash")
    op3 = LocalCopy(
        npl1, npl1, {"files": ["termux-*", "pbu", "rbu", "qe"], "exec": True}
    )
    addArc(op3)

    npl1 = ("bash", "bin")
    op4 = LocalCopy(
        npl1, npl1, {"files": ["termux-*", "pbu", "rbu", "qe"], "exec": False}
    )
    addArc(op4)

    npl1 = ("sh", "bash")
    op5 = LocalCopy(npl1, npl1, {"files": ["*.sh", "*.env"], "exec": True})
    addArc(op5)

    npl1 = ("blogds", "blog")
    op6 = LocalCopy(npl1, npl1, {"files": ["blog.js"]})
    addArc(op6)

    npl1 = ("blog", "blogds")
    op7 = LocalCopy(npl1, npl1, {"files": ["*.db", "blog.js"]})
    addArc(op7)

    npl1 = ("plaid-node", "blogds")
    op8 = LocalCopy(npl1, npl1, {"files": ["*.db"]})
    addArc(op8)

    # npl1 = ('termux-backup', 'home')
    # op1 = LocalCopy(npl1, npl1, {'files': ['**/*.*']})
    # addArc(op1)

    npl1 = ("backups", "blogds")
    op9 = LocalCopy(npl1, npl1, {"files": ["*.db"]})
    addArc(op9)

    if "NOGIT" not in os.environ:
        npl1 = ("git_commit", "git_add")
        op10 = opGitAdd(npl1, npl1, {"wt": worktree})
        addArc(op10)

        npl1 = ("git", "git_commit")
        op11 = opGitCommit(npl1, npl1, {"wt": worktree})
        addArc(op11)

        npl1 = ("bitbucket", "git")
        op12 = opGitPush(
            npl1,
            None,
            {"wt": worktree, "rmt": "bitbucket"},
        )
        addArc(op12)

        npl1 = ("github", "git")
        op13 = opGitPush(
            npl1,
            None,
            {"wt": worktree, "rmt": "github"},
        )
        addArc(op13)

    # for si in codes:
    # npl1 = ("zips", si)
    # op1 = Mkzip(npl1, npl1, {"zipfile": si + ".zip"})
    # addArc(op1)

    # for si in (".git",):
    # npl1 = ("zips", si)
    # op1 = Mkzip(npl1, npl1, {"zipfile": "projects-git.zip"})
    # addArc(op1)
    check_sdhes(8)

    for cs in ("gd",):
        for si in ("proj", *codes, "vids", "zips"):
            p1 = src(si).relative_to(ppre("sd"))
            addTgtDir(cs + "_" + si, ppre(cs) / p1)
            npl1 = (cs + "_" + si, si)
            # op1 = CSRestore(npl1, None, {})
            # addArc(op1)
            op14 = CSCopy(npl1, npl1, {"delete": False, "listdeletions": True})
            addArc(op14)
    check_sdhes(9)


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
    ".yarnclean",
}


def cull_DEs(des):
    des[:] = [
        de for de in des if not any([sd for sd in de.nm.parent.parts if sd in dexs])
    ]


def cull_files(files, pt):
    files[:] = [
        pt(f) for f in files if not any([sd for sd in f.parent.parts if sd in dexs])
    ]


def cull_dirs(dirs, pt):
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
                cull_dirs(dirs, pt)
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
