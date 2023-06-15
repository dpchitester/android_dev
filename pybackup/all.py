
def netup():
    return True


from tarjan import tarjan_recursive


def topological_sort(dependency_pairs):
    "Sort values subject to dependency constraints."
    nodes = {}
    for e in dependency_pairs:
        if e.di not in nodes:
            nodes[e.di] = []
        if e.si not in nodes:
            nodes[e.si] = []
        if e.di not in nodes[e.si]:
            nodes[e.si].append(e.di)
    out = tarjan_recursive(nodes)
    return out

from dataclasses import dataclass
from pathlib import Path


@dataclass(order=True)
class FSe:
    sz: int
    mt: float

    def __hash__(self):
        return hash((self.sz, round(self.mt)))

    def __eq__(self, other):
        return self.sz == other.sz and round(self.mt) == round(other.mt)


@dataclass(order=True)
class DE:
    nm: Path
    i: FSe

    def __hash__(self):
        return hash((self.nm, self.i.sz, round(self.i.mt)))

    def __eq__(self, other):
        return self.nm == other.nm and self.i == other.i

import pickle
from struct import pack

from xxhash import xxh64


def bhu(ho, it):
    from pathlib import Path

    from de import DE, FSe

    match it:
        case bytes():
            ho.update(it)
        case int():
            ho.update(pack("i", it))
        case float():
            ho.update(pack("f", it))
        case str():
            ho.update(it.encode())
        case Path():
            ho.update(bytes(it))
        case tuple() | set() | list() | DE() | FSe():
            bs = pickle.dumps(it)
            ho.update(bs)
        case _:
            print("bhash type error", type(it), "??")


# flattened list xxh64 with integer result
def xxh64Hash(it):
    ho = xxh64()
    bhu(ho, it)
    return ho.intdigest()
#!/data/data/com.termux/files/usr/bin/env python

from threading import Thread

import config
import ldsv as ls
from opexec import clean, opExec
from status import updatets

th3 = None


def rt2():
    global th1
    itc = 0
    while True:
        itc += 1
        cl = clean()
        if cl:
            print("no backups appear pending")
            break
        else:
            print("backups appear pending")
            opExec()


def main():
    global th3
    print("-main")
    config.initConfig()
    try:
        print("-main-2")
        updatets(0)
        print("-main-3")
        th3 = Thread(target=ls.save_bp)
        th3.start()
        print("-main-4")
        rt2()
        print("-main-5")
        config.quit_ev.set()
    except KeyboardInterrupt as exc:
        print(exc)
    finally:
        print("-main-6")
        if th3 and th3.is_alive():
            config.quit_ev.set()
            th3.join()


import json
from pathlib import PosixPath

from edge import Edge


class OpBaseEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, PosixPath):
            # print(1, obj.__class__)
            return str(obj)
        if isinstance(obj, OpBase):
            # print(2, obj.__class__)
            return {
                str(obj.__class__): {
                    "npl1": obj.npl1,
                    "npl2": obj.npl2,
                    "opts": obj.opts,
                }
            }
        if isinstance(obj, Edge):
            return [obj.di, obj.si, obj.cdt, obj.udt]
        if isinstance(obj, set):
            # print(4, obj.__class__)
            return list(obj)
        elif isinstance(obj, tuple):
            return repr(obj)
        elif isinstance(obj, bytes):
            return obj.hex()
        else:
            print(5, obj.__class__)
            return str(obj.__class__)
            # raise Exception('bad type:', obj.__class__)


class OpBase:
    def __init__(self, npl1, npl2, opts={}) -> None:
        self.npl1 = npl1
        self.npl2 = npl2
        self.opts = opts

    def ischanged(self, e: Edge):
        return e.chk_ct()

    def __repr__(self) -> str:
        return (
            str(self.__class__)
            + ": \n"
            + "\t"
            + str(self.npl1)
            + ", "
            + "\t"
            + str(self.npl2)
            + ", "
            + "\t"
            + str(self.opts)
            + "\n\n"
        )
import config


def stsupdate(Si, Dh):
    # print(Si, end=' ')
    print(Si, end=" ")
    # N1 = srcts[Si]
    for e in [e for e in config.eDep if e.si == Si]:
        e.rtset()
    config.src(Si).sdhset(Dh)


def onestatus(Si):
    # TODO: update as per src_statuses
    tr = config.src(Si).sdhck()
    if tr is not None:
        (Dh, changed) = tr
        if changed:
            stsupdate(Si, Dh)
            print()


def src_statuses():
    SDl = []
    for Si in config.srcs:
        # print('calling lckers', Si)
        tr = config.src(Si).sdhck()
        if tr is not None:
            (Dh, changed) = tr
            if changed:
                SDl.append((Si, Dh))
    return SDl

def src_statuses2():
    import concurrent.futures as cf
    tpe = cf.ThreadPoolExecutor(max_workers=4)
    SDl = []
    def f1(Si):
        # print('calling lckers', Si)
        tr = config.src(Si).sdhck()
        if tr is not None:
            (Dh, changed) = tr
            if changed:
                SDl.append((Si, Dh))
    for Si in config.srcs:
        tpe.submit(f1, Si)
    tpe.shutdown()
    return SDl


def updatets(N):
    print("Status", N)
    Sl = src_statuses2()
    if len(Sl):
        print("changed: ", end="")
        for rv in Sl:
            (Si, Dh) = rv
            stsupdate(Si, Dh)
        print()


import math
from os import utime, walk
from pathlib import Path
from shutil import make_archive

import config
from edge import Edge, findEdge
from findde import updateDEs
from opbase import OpBase
from status import onestatus


def getfl(p):
    # print(str(p))
    fl = []
    try:
        if p.is_file():
            fl.append(p)
            return fl
        for pth, _dirs, files in walk(p, topdown=True):
            for f in files:
                fl.append(Path(pth, f))
        return fl
    except OSError as e:
        print(e)
        return None


def maxmt(sd):
    l1 = getfl(sd)

    def es(it):
        # TODO: use Path
        fs = it.stat()
        it3 = fs.st_mtime_ns
        return it3

    st = list(map(es, l1))
    st.sort(reverse=True)
    return int(math.floor(st[0] / 1.0e6) * 1.0e6)


class Mkzip(OpBase):
    def __init__(self, npl1, npl2, opts={}) -> None:
        super().__init__(npl1, npl2, opts)

    def ischanged(self, e: Edge):
        return e.chk_ct()

    def __call__(self):
        print("Mkzip")
        sc = 0
        fc = 0
        di1, si1 = self.npl1
        e: Edge = findEdge(di1, si1)
        if e.chk_ct():
            di2, si2 = self.npl2
            sd = config.src(si2)
            td = config.tgt(di2)
            zf = self.opts.get("zipfile", "temp.zip")
            zp = td / Path(zf).stem
            try:
                fp = Path(make_archive(zp, "zip", sd, ".", True))
                print(fp)
                maxt = maxmt(sd)
                utime(fp, ns=(maxt, maxt))
                sc += 1
                updateDEs(td, [zf])
            except OSError as er:
                print(er)
                fc += 1
            if sc > 0:
                onestatus(di2)
        if fc == 0:
            e.clr()
        return (sc, fc)
import config
from edge import Edge, findEdge
from opbase import OpBase
from status import updatets
from toposort2 import topological_sort

_pass = 1


def changed_ops(T=None) -> list[OpBase]:
    rv: list[OpBase] = []
    for Op in config.opdep:
        di, si = Op.npl1
        if T is None or di == T:
            e: Edge = findEdge(di, si)
            if Op.ischanged(e):
                rv.append(Op)
    return rv


def incp():
    global _pass
    i = _pass
    _pass += 1
    return i


def clean():
    res = len(changed_ops()) == 0
    if res:
        print("clean")
    return res


def nodeps(T):
    return not any(e.si == T for e in config.eDep)


def istgt(T, dep2=None):
    if dep2 is None:
        dep2 = config.eDep
    return any(e.di == T for e in dep2)


def nts():
    print("-nts")
    p1 = topological_sort(config.eDep)
    ts = [t for elem in p1 for t in elem]
    ts = [d for d in ts if istgt(d)]
    ts.reverse()
    return ts

n = 1

def proc_nodes(L):
    import concurrent.futures as cf
    global n
    tpe = cf.ThreadPoolExecutor(max_workers=4)
    def f1(op):
        global n
        sc, fc = op()
        updatets(n)
        n += 1
    for node in L:
        # print("node:", node)
        ss = changed_ops(node)
        for op in ss:
            if nodeps(op.npl1[0]):
                tpe.submit(f1, op)
                #f1(op)
            else:
                f1(op)
    tpe.shutdown()
    updatets(n)

def opExec():
    print("-opexec")
    g1 = nts()
    incp()
    return proc_nodes(g1)


if __name__ == "__main__":
    config.initConfig()
    print(opExec())
from dataclasses import dataclass, field

import config
import ldsv as ls


@dataclass(order=True)
class Edge:
    di: str = field(compare=True, hash=True)
    si: str = field(compare=True, hash=True)
    ss: bool = field(default=True, init=False, repr=True, hash=False, compare=False)
    ts: bool = field(default=True, init=False, repr=True, hash=False, compare=False)
    def __eq__(self, other):
        return self.si == other.si and self.di == other.di

    def __hash__(self):
        return hash((self.si, self.di))

    def chk_ct(self):
        return self.ss

    def rchk_ct(self):
        return self.ts

    def clr(self):
        with ls.dl:
            if self.ss:
                print("-clr", self.di, self.si)
                self.ss = False
                ls.sev.put("edges")

    def rclr(self):
        with ls.dl:
            if self.ts:
                print("-rclr", self.di, self.si)
                self.ts = False
                ls.sev.put("edges")

    def rtset(self):
        with ls.dl:
            self.ss = True
            ls.sev.put("edges")

    def rrtset(self):
        with ls.dl:
            self.ts = True
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
import json
import subprocess

from csubproc import ContinuousSubprocess, Qi1, Qi2

# from snoop import pp
# from snoop import snoop


def colored(r, g, b, text):
    return f"\033[38;2;{r};{g};{b}m{text}\033[0m"


idel = 1


def a_run(shell_command, cwd=None):
    txt = ""
    p = subprocess.run(
        shell_command,
        shell=True,
        cwd=cwd,
        text=True,
        capture_output=True,
    )
    so = p.stdout
    if so:
        txt = so
        if txt:
            print(txt)
    return p.returncode, txt


def a_run1(shell_command, cwd=None):
    txt = ""
    p = subprocess.run(
        shell_command,
        shell=True,
        cwd=cwd,
        text=True,
        capture_output=True,
    )
    so = p.stdout
    if so:
        txt = so
    return p.returncode, txt


def a_run2(shell_command, cwd=None):
    p = subprocess.run(
        shell_command,
        shell=True,
        cwd=cwd,
        text=True,
    )
    return p.returncode


def a_run3(shell_command, cwd=None):
    txt = ""
    msglst = []
    csp = ContinuousSubprocess(shell_command)
    olg = csp.execute(path=cwd)
    try:
        for ln in olg:
            match ln:
                case Qi1():
                    txt += ln
                    print(colored(0, 255, 0, ln), end="")
                case Qi2():
                    if ln and len(ln):
                        msg = json.loads(ln)
                        msglst.append(msg)
                    # print(colored(255, 0, 0, msg))

    except subprocess.CalledProcessError as exc:
        error_output = json.loads(exc.output)
        message = error_output["message"]
        trace = error_output["trace"]
        print(message)
        print(trace)
        return exc.returncode, txt, msglst
    return 0, txt, msglst


def a_run4(shell_command, cwd=None):
    csp = ContinuousSubprocess(shell_command)
    olg = csp.execute(path=cwd)
    txt1 = ""
    txt2 = ""
    try:
        for ln in olg:
            match ln:
                case Qi1():
                    txt1 += ln
                    print(colored(0, 255, 0, ln), end="")
                case Qi2():
                    txt2 += ln
                    print(colored(0, 0, 255, ln), end="")

    except subprocess.CalledProcessError as exc:
        error_output = json.loads(exc.output)
        message = error_output["message"]
        trace = error_output["trace"]
        print(message)
        print(trace)
        return exc.returncode, txt1, txt2
    return 0, txt1, txt2


run = a_run
run1 = a_run1
run2 = a_run2
run3 = a_run3
run4 = a_run4
from threading import RLock

import asyncrun as ar
import config
from edge import Edge, findEdge
from netup import netup
from opbase import OpBase

rl = RLock()


class GitAdd(OpBase):
    def __init__(self, npl1, npl2, opts={}) -> None:
        super().__init__(npl1, npl2, opts)

    def ischanged(self, e: Edge):
        return e.chk_ct() | e.rchk_ct()

    def __call__(self):
        print("GitAdd")
        tc = 0
        fc = 0
        s = ""
        anyd = False
        di, si = self.npl1
        e: Edge = findEdge(di, si)
        if e.chk_ct():
            s += "l"
            anyd = True
        if e.rchk_ct():
            s += "r"
            anyd = True
        if not anyd:
            return (tc, fc)
        with rl:
            rc, txt1, txt2 = ar.run4("git add -A . -v", cwd=config.src(si))
        if rc == 0:
            tc += 1
        else:
            fc += 1
        if fc == 0:
            e.clr()
            e.rclr()
        return (tc, fc)


class GitCommit(OpBase):
    def __init__(self, npl1, npl2, opts={}) -> None:
        super().__init__(npl1, npl2, opts)

    def ischanged(self, e: Edge):
        return e.chk_ct() | e.rchk_ct()

    def __call__(self):
        print("GitCommit")
        tc = 0
        fc = 0
        s = ""
        anyd = False
        di, si = self.npl1
        e: Edge = findEdge(di, si)
        if e.chk_ct():
            s += "l"
            anyd = True
        if e.rchk_ct():
            s += "r"
            anyd = True
        if not anyd:
            return (tc, fc)
        with rl:
            rc, txt1, txt2 = ar.run4("git commit -a -m pybak -v", cwd=self.opts["wt"])
        if rc in (0, 1):
            tc += 1
        else:
            print("git commit rc:", rc)
            fc += 1
        if fc == 0:
            e.clr()
            e.rclr()
        return (tc, fc)


class GitPush(OpBase):
    def __init__(self, npl1, npl2, opts={}) -> None:
        super().__init__(npl1, npl2, opts)

    def ischanged(self, e: Edge):
        return e.chk_ct() | e.rchk_ct()

    def __call__(self):
        rmt = self.opts.get("rmt")
        print("GitPush", rmt)
        tc = 0
        fc = 0
        s = ""
        anyd = False
        di, si = self.npl1
        e: Edge = findEdge(di, si)
        if e.chk_ct():
            s += "l"
            anyd = True
        if e.rchk_ct():
            s += "r"
            anyd = True
        if not anyd:
            return (tc, fc)
        if rmt == "local" or (netup()):
            with rl:
                rc, txt1, txt2 = ar.run4(
                    "git push " + rmt + " master", cwd=self.opts["wt"]
                )
            if rc == 0:
                tc += 1
            else:
                fc += 1
        if fc == 0:
            e.clr()
            e.rclr()
        return (tc, fc)
import bisect
import datetime
import os
from pathlib import Path

import asyncrun as ar
import config
from de import DE, FSe

dexs = {
    ".cargo",
    ".cache",
    ".git",
    "node_modules",
    "__pycache__",
    ".ropeproject",
    ".ruff_cache",
    ".mypyproject",
    ".mypy_cache",
    ".vite",
    ".yarnclean",
    "storage",
}


def cull_DEs(des):
    des[:] = [
        de
        for de in des
        if not any(sd for sd in de.nm.parent.parts if sd in config.dexs)
    ]


def cull_files(files, pt):
    files[:] = [
        pt(f)
        for f in files
        if not any(sd for sd in f.parent.parts if sd in config.dexs)
    ]


def cull_dirs(dirs, pt):
    dirs[:] = [pt(d) for d in dirs if not isbaddir(pt(d))]


def isbaddir(dir):
    return dir in config.dexs or dir in dexs


class FileList:
    def __new__(cls, sd, **kwargs):
        cls = RemoteFileList if sd.isremote else LocalFileList
        self = object.__new__(cls)
        return self

    def __init__(self, sd) -> None:
        self.sd = sd
        super().__init__()


class LocalFileList(FileList):
    def __init__(self, sd, **kwargs) -> None:
        super().__init__(sd)

    def getfl_str_fp(self, fp: str):
        from collections import deque

        q = deque()
        q.append(fp)

        while True:
            try:
                fp2 = q.popleft()
                # print(fp2)
                with os.scandir(fp2) as di:
                    for it1 in di:
                        if it1.is_file():
                            yield it1
                        elif not it1.is_symlink() and not isbaddir(it1.name):
                            q.append(it1.path)

            except IndexError:
                break

    def getfl(self):
        return self.getfl_str_fp(str(self.sd))

    def getdll(self):  # local-source
        import config

        config.dl1_cs += 1
        st = []
        for it in self.getfl():
            it1 = Path(it.path).relative_to(self.sd)
            try:
                fs = it.stat()
                it2 = fs.st_size
                it3 = fs.st_mtime_ns
                it3 = config.ns_trunc2ms(it3)
            except FileNotFoundError as exc:
                print(exc)
                it2 = 0
                it3 = 0
            fse = FSe(it2, it3)
            bisect.insort(st, DE(it1, fse), key=lambda de: de.nm)

        return st


class RemoteFileList(FileList):
    def __init__(self, sd, **kwargs) -> None:
        super().__init__(sd, **kwargs)

    def getfl(self, sd):
        import json

        cmd = 'rclone lsjson "' + str(sd) + '" --recursive --files-only '
        rc, txt = ar.run1(cmd)
        if rc == 0:
            return json.loads(txt)
        if rc == 3:
            return []
        return None

    def getdll(self):  # remote-source
        import config

        config.dl2_cs += 1
        # print('getdll1', di, str(td))
        st = []
        for it in self.getfl(self.sd):
            # TODO: use Path
            it1 = Path(it["Path"])
            it2 = it["Size"]
            it3 = it["ModTime"][:-1] + "-00:00"
            it3 = datetime.datetime.fromisoformat(it3).timestamp()
            it3 = config.ts_trunc2ms(it3)
            fse = FSe(it2, it3)
            bisect.insort(st, DE(it1, fse), key=lambda de: de.nm)

        return st


from hashlib import sha256

import asyncrun as ar
import config
from edge import Edge, findEdge
from findde import updateDEs
from opbase import OpBase
from status import onestatus


class FileDiff:
    sf = None
    df = None
    fe = 0
    sz = 0
    mt = 0
    hd = False

    def __init__(self, sf, df) -> None:
        self.sf = sf
        self.df = df

    def chkdiff(self):
        sfe = self.sf.exists()
        if sfe:
            self.fe += 1
        dfe = self.df.exists()
        if dfe:
            self.fe -= 1
        if self.fe == 0:
            sfs = self.sf.stat()
            dfs = self.df.stat()
            if sfs.st_size > dfs.st_size:
                self.sz = 1
                print("source larger:", sfs.st_size - dfs.st_size, self.sf.name)
            elif sfs.st_size < dfs.st_size:
                self.sz = -1
                print("source smaller:", dfs.st_size - sfs.st_size, self.sf.name)
            if sfs.st_mtime_ns > dfs.st_mtime_ns:
                self.mt = 1
                print(
                    "source newer:",
                    (sfs.st_mtime_ns - dfs.st_mtime_ns) / 1e9,
                    self.sf.name,
                )
            elif sfs.st_mtime_ns < dfs.st_mtime_ns:
                self.mt = -1
                print(
                    "source older:",
                    (sfs.st_mtime_ns - dfs.st_mtime_ns) / 1e9,
                    self.sf.name,
                )
            if sha256sumf(self.sf) != sha256sumf(self.df):
                self.hd = True
                print("hash mismatch:", self.sf.name)

    def should_copy(self):
        self.chkdiff()
        if self.fe > 0:
            return True
        elif self.fe < 0:
            return False
        elif self.mt > 0:
            return True
        elif self.mt < 0:
            return False
        else:
            return self.hd


class SFc:
    def __init__(self, sc=0, fc=0) -> None:
        self.sc = sc
        self.fc = fc

    def value(self):
        return (self.sc, self.fc)


def sha256sums(S1):
    ho = sha256()
    ho.update(S1)
    return ho.hexdigest()


def sha256sumf(Fn):
    if Fn.exists():
        b = Fn.read_bytes()
        ho = sha256()
        ho.update(b)
        return ho.hexdigest()
    return None


def copy2(di, si, sd, td, sfc):
    # print('copying ', f1, 'to', f2)
    td2 = td.parent if td.is_file() else td
    cmd = "cp -u -p " + str(sd) + " " + str(td2)
    print("copying", sd.name)
    rv, txt = ar.run1(cmd)
    if rv == 0:
        sfc.sc += 1
    else:
        sfc.fc -= 1
        print(txt)
    return rv


# import shutil
# shutil.copy2(f1, f2)


class LocalCopy(OpBase):
    sfc = SFc()

    def __init__(self, npl1, npl2, opts={}) -> None:
        super().__init__(npl1, npl2, opts)

    def ischanged(self, e: Edge):
        return e.chk_ct()

    def __call__(self):
        di, si = self.npl1
        e: Edge = findEdge(di, si)
        if e.chk_ct():
            print("LocalCopy", self.npl1, self.npl2)
            sp = config.src(self.npl2[1])
            tp = config.tgt(self.npl2[0])
            gl = self.opts.get("files", ["**/*"])
            for g in gl:
                try:
                    fl = sp.glob(g)
                except OSError:
                    print("glob error in localcopy", e)
                    self.sfc.fc += 1
                    return self.sfc.value()
                for fsf in fl:
                    if fsf.is_dir():
                        continue
                    rf = fsf.relative_to(sp)
                    fdf = tp / rf
                    try:
                        if not fdf.parent.exists():
                            fdf.parent.mkdir(parents=True, exist_ok=True)
                        if fdf.parent.exists():
                            fdiff = FileDiff(fsf, fdf)
                            if fdiff.should_copy():
                                rv = copy2(di, si, fsf, fdf, self.sfc)
                                if rv == 0:
                                    print(" ...copied.")
                                    self.sfc.sc += 1
                                    if "exec" in self.opts:
                                        fdf.chmod(496)
                                    updateDEs(tp, [str(rf)])
                    except OSError as exc:
                        print(exc)
                        self.sfc.fc += 1
            if self.sfc.fc == 0:
                e.clr()
            if self.sfc.sc > 0 and di in config.srcs:
                onestatus(di)
        return self.sfc.value()
"""Module for continuous subprocess management.
modified by phil.
"""
import json
import subprocess
import types
from collections import deque
from collections.abc import Generator
from queue import Empty, Queue
from threading import Thread
from typing import IO, AnyStr

# logger = logging.getLogger(__name__)

Qi1 = types.new_class("Qi1", bases=(str,))
Qi2 = types.new_class("Qi2", bases=(str,))


class ContinuousSubprocess:
    """Creates a process to execute a wanted command and
    yields a continuous output stream for consumption.
    """

    def __init__(self, command_string: str) -> None:
        """Constructor.

        :param command_string: A command to execute in a separate process.
        """
        self.__command_string = command_string
        self.__process: subprocess.Popen | None = None

    @property
    def command_string(self) -> str:
        """Property for command string.

        :return: Command string.
        """
        return self.__command_string

    def terminate(self) -> None:
        if not self.__process:
            raise ValueError("Process is not running.")

        self.__process.terminate()

    def execute(
        self,
        shell: bool = True,
        path: str | None = None,
        max_error_trace_lines: int = 1000,
        *args,
        **kwargs,
    ) -> Generator[str, None, None]:
        """Executes a command and yields a continuous output from the process.

        :param shell: Boolean value to specify whether to
        execute command in a new shell.
        :param path: Path where the command should be executed.
        :param max_error_trace_lines: Maximum lines to return in case of an error.
        :param args: Other arguments.
        :param kwargs: Other named arguments.

        :return: A generator which yields output strings from an opened process.
        """
        # Check if the process is already running
        # (if it's set, then it means it is running).
        if self.__process:
            raise RuntimeError(
                "Process is already running. "
                "To run multiple processes initialize a second object."
            )

        with subprocess.Popen(
            self.__command_string,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=shell,
            cwd=path,
            *args,
            **kwargs,
            bufsize=1,
        ) as process:
            # Indicate that the process has started and is now running.
            self.__process = process

            # Initialize a mutual queue that will hold stdout and stderr messages.
            q1 = Queue()
            q2 = Queue()
            # Initialize a limited queue to hold last N of lines.
            dq = deque(maxlen=max_error_trace_lines)

            # Create a parallel thread that will read stdout stream.
            stdout_thread = Thread(
                target=ContinuousSubprocess.__read_stream, args=[process.stdout, q1]
            )
            stdout_thread.start()

            # Create a parallel thread that will read stderr stream.
            stderr_thread = Thread(
                target=ContinuousSubprocess.__read_stream, args=[process.stderr, q2]
            )
            stderr_thread.start()

            # logger.info(
            #    "Successfully started threads to capture stdout and stderr streams."
            # )

            while process.poll() is None:
                while not q1.empty():
                    try:
                        item = q1.get(False)
                        dq.append(item)
                        yield Qi1(item)
                    except Empty:
                        pass

                while not q2.empty():
                    try:
                        item = q2.get(False)
                        dq.append(item)
                        yield Qi2(item)
                    except Empty:
                        pass

            # Close streams.
            process.stdout.close()
            process.stderr.close()

            return_code = process.wait()

        # Make sure both threads have finished.
        stdout_thread.join()
        if stdout_thread.is_alive():
            raise RuntimeError("Stdout thread is still alive!")

        stderr_thread.join()
        if stderr_thread.is_alive():
            raise RuntimeError("Stderr thread is still alive!")

        # Indicate that the process has finished as is no longer running.
        self.__process = None

        if return_code:
            error_trace = list(dq)
            raise subprocess.CalledProcessError(
                returncode=return_code,
                cmd=self.__command_string,
                output=json.dumps(
                    {
                        "message": "An error has occurred while running the specified command.",
                        "trace": error_trace,
                        "trace_size": len(error_trace),
                        "max_trace_size": max_error_trace_lines,
                    }
                ),
            )

    @staticmethod
    def __read_stream(stream: IO[AnyStr], queue: Queue):
        try:
            for line in iter(stream.readline, ""):
                if line != "":
                    queue.put(line)
                else:
                    break
        # It is possible to receive: ValueError: I/O operation on closed file.
        except ValueError:
            # logger.exception("Got error while reading from a process stream.")
            pass
import asyncrun as ar
import config
import gitops as go
import ldsv as ls
from sd import SD


class GitCmdFailure(Exception):
    pass


def gitcmd(cmd, wt):
    with go.rl:
        rc, txt = ar.run1(cmd, cwd=wt)
    if rc != 0:
        raise GitCmdFailure("gitcmd rc: " + str(rc) + cmd)
    return txt.rstrip()


class Local_Git_Mixin:
    def __init__(self, *args, **kwargs) -> None:
        super().__init__()

    @property
    def isremote(self):
        return False

    @property
    def SDh(self):
        if hasattr(self, "tag"):
            with ls.dl:
                if self.tag in config.LDhd:
                    return config.LDhd[self.tag]
        return 0

    @SDh.setter
    def SDh(self, val):
        if hasattr(self, "tag"):
            with ls.dl:
                config.LDhd[self.tag] = val
                ls.sev.put("ldhd")


class Remote_Git_Mixin:
    def __init__(self, *args, **kwargs) -> None:
        super().__init__()

    @property
    def isremote(self):
        return True

    @property
    def SDh(self):
        if hasattr(self, "tag") and self.tag in config.RDhd:
            return config.RDhd[self.tag]
        return 0

    @SDh.setter
    def SDh(self, val):
        if hasattr(self, "tag"):
            with ls.dl:
                config.RDhd[self.tag] = val
                ls.sev.put("rdhd")


class GitWT(SD, Local_Git_Mixin):
    def __init__(self, *args, **kwargs) -> None:
        for k, v2 in kwargs.items():
            setattr(self, k, v2)
        super().__init__(*args, **kwargs)

    def sdhck(self):
        Dh1 = self.sdh_f()
        cmd = "git status --porcelain --untracked-files=all"
        rv = gitcmd(cmd, self)
        rv = rv.split("\n")
        rv = len([ln for ln in rv if len(ln) > 1 and ln[1] != " "])
        Dh2 = rv
        if rv == 0:
            self.sdhset(Dh2)
        elif Dh2 != Dh1:
            # print(rv)
            pass
        return (Dh2, rv > 0 and Dh2 != Dh1)


class GitIndex(SD, Local_Git_Mixin):
    def __init__(self, *args, **kwargs) -> None:
        for k, v2 in kwargs.items():
            setattr(self, k, v2)
        super().__init__(*args, **kwargs)

    def sdhck(self):
        Dh1 = self.sdh_f()
        cmd = "git status --porcelain --untracked-files=all"
        rv = gitcmd(cmd, self)
        rv = rv.split("\n")
        rv = len([ln for ln in rv if len(ln) > 1 and ln[0] != " "])
        Dh2 = rv
        if rv == 0:
            self.sdhset(Dh2)
        elif Dh2 != Dh1:
            # print(rv)
            pass
        return (Dh2, rv > 0 and Dh2 != Dh1)


class GitRepo(SD, Local_Git_Mixin):
    def __init__(self, *args, **kwargs) -> None:
        for k, v2 in kwargs.items():
            setattr(self, k, v2)
        super().__init__(*args, **kwargs)

    def sdhck(self):
        return self.gitck2()

    def gitck2(self):
        Dh1 = self.sdh_f()
        if Dh1 is None:
            Dh1 = 0
        rv = 0
        for rmt in self.rmts:
            cmd = "git rev-list --count " + rmt + "/master..master"
            rv += int(gitcmd(cmd, self))
        Dh2 = rv
        if Dh2 == 0:
            self.sdhset(Dh2)
        return (Dh2, rv > 0 and Dh2 != Dh1)


class GitRemote(SD, Remote_Git_Mixin):
    def __init__(self, *args, **kwargs) -> None:
        for k, v2 in kwargs.items():
            setattr(self, k, v2)
        super().__init__(*args, **kwargs)

    def sdhck(self):
        return self.gitremoteck()

    def tdhck(self):
        return self.gitremoteck()

    def gitremoteck(self):
        Dh1 = self.sdh_f()
        Dh2 = None
        # print(Di, 'status here')
        cmd = ""
        try:
            cmd = "git branch master -u " + self.rmt + "/master"
            gitcmd(cmd, self)
            cmd = "git remote update " + self.rmt
            gitcmd(cmd, self)
            cmd = "git rev-parse @"
            lcomm = gitcmd(cmd, self)
            cmd = "git rev-parse @{u}"
            rcomm = gitcmd(cmd, self)
            cmd = "git merge-base @ @{u}"
            bcomm = gitcmd(cmd, self)
            # print('lcomm', lcomm)
            # print('rcomm', rcomm)
            # print('bcomm', bcomm)
            if lcomm == rcomm:
                print("up-to-date")
                Dh2 = 1
            elif lcomm == bcomm:
                print("need-to-pull")
                Dh2 = 3
            elif rcomm == bcomm:
                print("need-to-push")
                Dh2 = 2
            else:
                print("diverged")
                Dh2 = 4
        except GitCmdFailure as e:
            print(e)
        if Dh2 is not None:
            if Dh2 == 1:
                self.sdhset(Dh2)
            return (Dh2, Dh2 > 1 and Dh2 != Dh1)
        return (Dh1, True)
import pickle
from queue import Empty, SimpleQueue
from threading import RLock
from time import sleep

import config

# from snoop import snoop

dl = RLock()
sev = SimpleQueue()


def pstats():
    print(f"{'dl1_cs':6} {config.dl1_cs:6d}")
    print(f"{'dl2_cs':6} {config.dl2_cs:6d}")
    print(f"{'h_miss':6} {config.h_miss:6d}")
    print(f"{'h_hits':6} {config.h_hits:6d}")
    print(f"{'upd_cs':6} {config.upd_cs:6d}")
    print(f"{'sfb':6} {config.sfb:6d}")


def loadldlls():
    with dl:
        try:
            with open(config.ldllsf, "rb") as fh:
                td = pickle.load(fh)
                LDlls = td["ldlls"]
                LDlls_xt = td["ldlls_xt"]
        except OSError as e:
            print("loadldlls failed", e)
            return
        for si in config.srcs:
            if si in LDlls:
                config.LDlls[si] = LDlls[si]
                config.LDlls_xt[si] = LDlls_xt[si]
        for di in config.tgts:
            if di in LDlls:
                config.LDlls[di] = LDlls[di]
                config.LDlls_xt[di] = LDlls_xt[di]


def loadrdlls():
    with dl:
        try:
            with open(config.rdllsf, "rb") as fh:
                td = pickle.load(fh)
                RDlls = td["rdlls"]
                RDlls_xt = td["rdlls_xt"]
        except OSError as e:
            print("loadrdlls failed", e)
            return
        for si in config.srcs:
            if si in RDlls:
                config.RDlls[si] = RDlls[si]
                config.RDlls_xt[si] = RDlls_xt[si]
        for di in config.tgts:
            if di in RDlls:
                config.RDlls[di] = RDlls[di]
                config.RDlls_xt[di] = RDlls_xt[di]


def saveldlls():
    with dl:
        # print('-saveldlls')
        try:
            with open(config.ldllsf, "wb") as fh:
                td = {"ldlls": config.LDlls, "ldlls_xt": config.LDlls_xt}
                pickle.dump(td, fh)
                config.sfb += fh.tell()
        except OSError as e:
            print("savedlls failed", e)


def saverdlls():
    with dl:
        try:
            with open(config.rdllsf, "wb") as fh:
                td = {"rdlls": config.RDlls, "rdlls_xt": config.RDlls_xt}
                pickle.dump(td, fh)
                config.sfb += fh.tell()
        except OSError as e:
            print("saverdlls failed", e)


def loadedges():
    with dl:
        try:
            with open(config.edgepf, "rb") as fh:
                leDep = pickle.load(fh)
        except OSError as e:
            print("loadedges failed", e)
            return
        for e in config.eDep:
            for le in leDep:
                if le == e:
                    e.ss = le.ss
                    e.ts = le.ts


def saveedges():
    with dl:
        try:
            with open(config.edgepf, "wb") as fh:
                pickle.dump(config.eDep, fh)
                config.sfb += fh.tell()
        except OSError as e:
            print("saveedges failed", e)


def loadldh():
    with dl:
        try:
            with open(config.ldhpf, "rb") as fh:
                config.LDhd = pickle.load(fh)
        except OSError as e:
            print("loadldh failed", e)


def loadrdh():
    with dl:
        try:
            with open(config.rdhpf, "rb") as fh:
                config.RDhd = pickle.load(fh)
        except OSError as e:
            print("loadrdh failed", e)


def saveldh():
    with dl:
        try:
            with open(config.ldhpf, "wb") as fh:
                pickle.dump(config.LDhd, fh)
                config.sfb += fh.tell()
        except OSError as e:
            print("saveldh failed", e)


def saverdh():
    with dl:
        try:
            with open(config.rdhpf, "wb") as fh:
                pickle.dump(config.RDhd, fh)
                config.sfb += fh.tell()
        except OSError as e:
            print("saverdh failed", e)


def load_all():
    loadrdlls()
    # loadldlls()
    loadedges()
    loadldh()
    loadrdh()


def save_all():
    with dl:
        saverdlls()
        # saveldlls()
        saveedges()
        saveldh()
        saverdh()
        pstats()


def save_bp():
    print("-savebp")
    svs = {}
    while True:
        try:
            qi = sev.get_nowait()
            try:
                svs[qi] += 1
            except KeyError:
                svs[qi] = 1
        except Empty:
            if config.quit_ev.is_set():
                break
            else:
                sleep(0.1)
    print("saves:", svs)
    for sv in svs:
        match sv:
            case "edges":
                saveedges()
            case "ldlls":
                saveldlls()
            case "rdlls":
                saverdlls()
            case "ldhd":
                saveldh()
            case "rdhd":
                saverdh()
    pstats()
import contextlib
import datetime
import json
from bisect import bisect_left
from pathlib import Path

import asyncrun as ar
import config
import ldsv as ls
from de import DE, FSe
from sd import FS_Mixin


def findDE(dl, rp: Path):
    tde = DE(rp, FSe(0, 0))
    i = bisect_left(dl, tde)
    if i < len(dl) and tde.nm == dl[i].nm:
        return (dl[i], i)
    return (None, i)


def getOneJSde(rd: Path, fn):
    cmd = 'rclone lsjson "' + str(rd / fn) + '" '
    cmd += "--stat"
    print(cmd)
    rc, txt = ar.run1(cmd)

    jsl = json.loads(txt) if rc == 0 and txt != "" else []
    return jsl


def getRemoteJSde(rd: Path, fn: str):
    fp = type(rd)(rd, fn)
    l1 = getOneJSde(fp.parent, fp.name)
    if len(l1):
        it = l1[0]
        it["Path"] = str(fp.relative_to(rd))
        return [it]
    else:
        return []


def getRemoteDEs(rd: Path, fl: list[str]):
    import concurrent.futures as cf
    tpe = cf.ThreadPoolExecutor(max_workers=4)
    jsl = []

    def f1(fn):
        jsl.extend(getRemoteJSde(rd, fn))

    for fn in fl:
        tpe.submit(f1, fn)
    tpe.shutdown()
    
    pt = Path
    delst = []
    for it in jsl:
        it1 = pt(it["Path"])
        it2 = it["Size"]
        it3 = it["ModTime"][:-1] + "-00:00"
        it3 = datetime.datetime.fromisoformat(it3).timestamp()
        it3 = config.ts_trunc2ms(it3)
        fse = FSe(it2, it3)
        nde = DE(it1, fse)
        delst.append(nde)

    return delst


def findSis(fp1: Path):
    l1 = {}
    for si, p in config.srcs.items():
        if isinstance(p, FS_Mixin):
            with contextlib.suppress(ValueError):
                l1[si] = fp1.relative_to(p)
    print('l1:', l1)
    return l1


def findDis(fp1: Path):
    l1 = {}
    for di, p in config.tgts.items():
        if isinstance(p, FS_Mixin):
            with contextlib.suppress(ValueError):
                l1[di] = fp1.relative_to(p)
    print('l1:', l1)
    return l1


def findSDEs(fp: Path):
    sil = findSis(fp)
    de_l = []
    for si in sil:
        p = config.src(si)
        rp = sil[si]

        if isinstance(p, FS_Mixin) and p.Dll:
            de, i = findDE(p.Dll, rp)
            de_l.append((p.Dll, rp, de, i, si))
    return de_l


def findTDEs(fp: Path):
    dil = findDis(fp)
    de_l = []
    for di in dil:
        p = config.tgt(di)
        rp = dil[di]

        if isinstance(p, FS_Mixin) and p.Dll:
            de, i = findDE(p.Dll, rp)
            de_l.append((p.Dll, rp, de, i, di))
    return de_l


def updateDEs(rd: Path, flst: list[str]):
    def doSOne(dl, rp, tde, i, si):
        if tde:
            sde = [sde for sde in sdel if sde.nm.name == tde.nm.name]
            sde = sde[0] if len(sde) else None
        else:
            sde = None
        p = config.src(si)
        if sde:
            if tde:
                if tde.i.sz != sde.i.sz:
                    tde.i.sz = sde.i.sz
                    if p.isremote:
                        ls.sev.put("rdlls")
                        config.Dllc[si].set()
                    else:
                        ls.sev.put("ldlls")
                        config.Dllc[si].set()
                    config.upd_cs += 1
                if tde.i.mt != sde.i.mt:
                    tde.i.mt = sde.i.mt
                    if p.isremote:
                        ls.sev.put("rdlls")
                        config.Dllc[si].set()
                    else:
                        ls.sev.put("ldlls")
                        config.Dllc[si].set()
                    config.upd_cs += 1
            else:
                fse = FSe(sde.i.sz, sde.i.mt)
                tde = DE(rp, fse)
                dl.insert(i, tde)
                if p.isremote:
                    ls.sev.put("rdlls")
                    config.Dllc[si].set()
                else:
                    ls.sev.put("ldlls")
                    config.Dllc[si].set()
                config.upd_cs += 1
        else:
            if tde:
                # dl.pop(i)
                pass

    def doTOne(dl, rp, tde, i, di):
        if tde:
            sde = [sde for sde in sdel if sde.nm.name == tde.nm.name]
            sde = sde[0] if len(sde) else None
        else:
            sde = None
        p = config.tgt(di)
        if sde:
            if tde:
                if tde.i.sz != sde.i.sz:
                    tde.i.sz = sde.i.sz
                    if p.isremote:
                        ls.sev.put("rdlls")
                        config.Dllc[di].set()
                    else:
                        ls.sev.put("ldlls")
                        config.Dllc[di].set()
                    config.upd_cs += 1
                if tde.i.mt != sde.i.mt:
                    tde.i.mt = sde.i.mt
                    if p.isremote:
                        ls.sev.put("rdlls")
                        config.Dllc[di].set()
                    else:
                        ls.sev.put("ldlls")
                        config.Dllc[di].set()
                    config.upd_cs += 1
            else:
                fse = FSe(sde.i.sz, sde.i.mt)
                tde = DE(rp, fse)
                dl.insert(i, tde)
                if p.isremote:
                    ls.sev.put("rdlls")
                    config.Dllc[di].set()
                else:
                    ls.sev.put("ldlls")
                    config.Dllc[di].set()
                config.upd_cs += 1
        else:
            if tde:
                # dl.pop(i)
                pass

    sdel = getRemoteDEs(rd, flst)
    with ls.dl:
        for fi in flst:
            fp = rd / fi
            sdes = findSDEs(fp)
            tdes = findTDEs(fp)

            for it in sdes:
                doSOne(*it)
            for it in tdes:
                doTOne(*it)
import time
from pathlib import PosixPath

import config
import ldsv as ls

# from snoop import pp
# from snoop import snoop


icl = 1
rto1 = 60 * 60


class SD(PosixPath):
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls, *args)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def sdh_f(self, dh=None):
        odh = self.SDh
        if dh is not None:
            self.SDh = dh
        return odh

    def sdhset(self, Dh=None):
        if Dh is None:
            Dh = self.sdh_d()
        if Dh is not None:
            self.sdh_f(Dh)

    def sdhck(self):
        Dh1 = self.sdh_f()
        Dh2 = self.sdh_d()
        if Dh2 is not None:
            return (Dh2, Dh1 != Dh2)
        return (None, False)


class Local_Mixin:
    def __init__(self, *args, **kwargs) -> None:
        super().__init__()

    @property
    def isremote(self):
        return False

    @property
    def Dll(self):
        if hasattr(self, "tag"):
            with ls.dl:
                if self.tag in config.LDlls:
                    return config.LDlls[self.tag]
        return None

    @Dll.setter
    def Dll(self, val):
        if hasattr(self, "tag"):
            with ls.dl:
                config.LDlls[self.tag] = val
                config.Dllc[self.tag].set()
                ls.sev.put("ldlls")

    @property
    def Dlls_xt(self):
        if hasattr(self, "tag"):
            with ls.dl:
                if self.tag in config.LDlls_xt:
                    return config.LDlls_xt[self.tag]
        return 0

    @Dlls_xt.setter
    def Dlls_xt(self, val):
        if hasattr(self, "tag"):
            with ls.dl:
                config.LDlls_xt[self.tag] = val
                ls.sev.put("ldlls")

    @property
    def SDh(self):
        if hasattr(self, "tag"):
            with ls.dl:
                if self.tag in config.LDhd:
                    return config.LDhd[self.tag]
        return 0

    @SDh.setter
    def SDh(self, val):
        if hasattr(self, "tag"):
            with ls.dl:
                config.LDhd[self.tag] = val
                config.Dllc[self.tag].clear()
                ls.sev.put("ldhd")


class Remote_Mixin:
    def __init__(self, *args, **kwargs) -> None:
        super().__init__()

    @property
    def isremote(self):
        return True

    @property
    def Dll(self):
        if hasattr(self, "tag"):
            with ls.dl:
                if self.tag in config.RDlls:
                    return config.RDlls[self.tag]
        return None

    @Dll.setter
    def Dll(self, val):
        if hasattr(self, "tag"):
            with ls.dl:
                config.RDlls[self.tag] = val
                config.Dllc[self.tag].set()
                ls.sev.put("rdlls")

    @property
    def Dlls_xt(self):
        if hasattr(self, "tag"):
            with ls.dl:
                if self.tag in config.RDlls_xt:
                    return config.RDlls_xt[self.tag]
        return 0

    @Dlls_xt.setter
    def Dlls_xt(self, val):
        if hasattr(self, "tag"):
            with ls.dl:
                config.RDlls_xt[self.tag] = val
                ls.sev.put("rdlls")

    @property
    def SDh(self):
        if hasattr(self, "tag"):
            with ls.dl:
                if self.tag in config.RDhd:
                    return config.RDhd[self.tag]
        return 0

    @SDh.setter
    def SDh(self, val):
        if hasattr(self, "tag"):
            with ls.dl:
                config.RDhd[self.tag] = val
                config.Dllc[self.tag].clear()
                ls.sev.put("rdhd")


class FS_Mixin(SD):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def sdh_d(self):
        from bhash import xxh64Hash

        rv = None
        with ls.dl:
            match self.Dll_status():
                case 0:
                    if self.isremote:
                        rv = config.RDhd[self.tag]
                    else:
                        rv = config.LDhd[self.tag]
                    config.h_hits += 1
                case 1 | 2 | 3:
                    Si_dl = self.Dlld()
                    if Si_dl is not None:
                        rv = xxh64Hash(Si_dl)
                        config.h_miss += 1
        return rv

    def Dll_status(self):
        if self.Dll is None:
            return 3
        elif self.isremote and self.Dlls_xt + rto1 <= time.time():
            return 2
        elif config.Dllc[self.tag].is_set():
            return 1
        return 0

    def Dlld(self):
        from filelist import FileList

        # print('-ldlld', si)
        if self.Dll_status() > 1:
            #print("sucking/scanning for", self.tag, ch + "dll...", end="")
            rv = FileList(self).getdll()
            if rv is not None:
                #print("done.")
                self.Dll = rv
                self.Dlls_xt = time.time()
            else:
                #print("failed.")
                pass
        else:
            #print("fetched", self.tag, ch + "dll from cache.")
            pass
        return self.Dll


class CFS_Mixin(FS_Mixin, Remote_Mixin):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)


class PFS_Mixin(FS_Mixin, Local_Mixin):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)


class Ext3(PFS_Mixin):
    def __init__(self, *args, **kwargs) -> None:
        for k, v in kwargs.items():
            setattr(self, k, v)
        super().__init__(*args, **kwargs)


class Fat32(PFS_Mixin):
    def __init__(self, *args, **kwargs) -> None:
        for k, v in kwargs.items():
            setattr(self, k, v)
        super().__init__(*args, **kwargs)


class CS(CFS_Mixin):
    def __init__(self, *args, **kwargs) -> None:
        for k, v in kwargs.items():
            setattr(self, k, v)
        super().__init__(*args, **kwargs)
import contextlib
import datetime as dt
from math import floor

import asyncrun as ar
import config
from edge import Edge
from netup import netup
from opbase import OpBase


def colored(r, g, b, text):
    return f"\033[38;2;{r};{g};{b}m{text}\033[0m"


def ar_run(cmd):
    opmsg = []
    statmsg = []
    with config.rclk:
        rc, txt, msglst = ar.run3(cmd)

    def f1():  # for ar_run3
        for m in msglst:
            if "operations" in m["source"]:
                opmsg.append(m)
            elif "stats" in m["source"]:
                statmsg.append(m)

    f1()
    return rc, txt, opmsg, statmsg


def chunk_from(s1, amt):
    s2 = set()
    for it in s1:
        s2.add(it)
        if len(s2) == amt:
            yield s2
            s2 = set()
    if len(s2):
        yield s2


class SFc:
    sc = 0
    fc = 0

    def __init__(self) -> None:
        pass

    def value(self):
        return (self.sc, self.fc)


def ts2st(ts):
    t2 = config.ts_trunc2ms(ts)
    t2 = dt.datetime.fromtimestamp(t2, tz=dt.timezone.utc)
    t2 = t2.isoformat()[:-6]
    return t2


def ftouch(di, si, td, lf, sfc):
    if netup():
        nt = ts2st(lf.i.mt)
        cmd = (
            'rclone touch -t"'
            + nt
            + '" "'
            + str(td / lf.nm)
            + '" --progress --no-create -v --use-json-log'
        )
        # cmd += ' --exclude ".git/**" --exclude "__pycache__/**"'
        print(cmd)
        rc, txt, opmsg, statmsg = ar_run(cmd)
        if rc == 0:
            for m in opmsg:
                # print(json.dumps(m, indent=4))
                if str(lf) == m["object"]:
                    if m["msg"].startswith("Updated modification time"):
                        sfc.sc += 1
            opmsg.clear()
            for m in statmsg:
                # print(json.dumps(m, indent=4))
                sfc.sc += m["stats"]["checks"]
            statmsg.clear()
            return True
        else:
            sfc.fc += 1
            opmsg.clear()
            statmsg.clear()
            print(txt)
    return False


def fsync(di, si, sd, td, sfc):
    if netup():
        # print('copy', sd, td)
        cmd = (
            'rclone copy "'
            + str(sd.parent)
            + '" "'
            + str(td.parent)
            + '" --include "'
            + str(td.name)
            + '" --progress --no-traverse -v --use-json-log'
        )
        # cmd += ' --exclude ".git/**" --exclude "__pycache__/**"'
        print(cmd)
        rc, txt, opmsg, statmsg = ar_run(cmd)
        if rc == 0:
            for m in opmsg:
                # print(json.dumps(m, indent=4))
                if str(td.name) == m["object"]:
                    if m["msg"].startswith("Copied"):
                        sfc.sc += 1
                    elif m["msg"].startswith("Updated modification time"):
                        sfc.sc += 1
            opmsg.clear()
            for m in statmsg:
                # print(json.dumps(m, indent=4))
                sfc.sc += m["stats"]["checks"]
                sfc.sc += m["stats"]["transfers"]
            statmsg.clear()
            return True
        else:
            sfc.fc += 1
            opmsg.clear()
            statmsg.clear()
            print(txt)
    return False


def fsynclm(di, si, sd, td, fl1, sfc):
    return all(fsyncl(di, si, sd, td, fl2, sfc) for fl2 in chunk_from(fl1, 10))


def fsyncl(di, si, sd, td, fl, sfc):
    cmd = 'rclone copy "'
    cmd += str(sd) + '" "'
    cmd += str(td) + '" '
    for fn in fl:
        cmd += '--include "' + str(fn.nm) + '" '
    cmd += "--progress --no-traverse -v --use-json-log"
    # cmd += '--exclude "**/.git/**/*" '
    # cmd += '--exclude "**/__pycache__/**/*" '
    # cmd += '--exclude "**/node_modules/**/*" '
    # cmd += '--log-file="rclone.log" '
    # cmd += "--use-json-log"
    if netup():
        # print("copy", sd, td, list(map(lambda de: str(de.nm), fl)))
        print(cmd)
        rc, txt, opmsg, statmsg = ar_run(cmd)
        if rc == 0:
            for m in opmsg:
                # print(json.dumps(m, indent=4))
                for f in fl:
                    if str(f.nm) == m["object"]:
                        if m["msg"].startswith("Copied"):
                            sfc.sc += 1
                        elif m["msg"].startswith("Updated modification time"):
                            sfc.sc += 1
            opmsg.clear()
            for m in statmsg:
                # print(json.dumps(m, indent=4))
                sfc.sc += m["stats"]["checks"]
                sfc.sc += m["stats"]["transfers"]
            statmsg.clear()
            return True
        else:
            sfc.fc += 1
            opmsg.clear()
            statmsg.clear()
            print(txt)
    return False


def fdel(di, si, sd, td, sfc):
    if netup():
        cmd = 'rclone delete "'
        cmd += str(td.parent)
        cmd += '" --include="' + td.name
        cmd += '" --progress -v --use-json-log'
        print(cmd)
        rc, txt, opmsg, statmsg = ar_run(cmd)
        if rc == 0:
            for m in opmsg:
                # print(json.dumps(m, indent=4))
                if str(td.name) == m["object"] and m["msg"].startswith("Deleted"):
                    sfc.sc += 1
            opmsg.clear()
            for m in statmsg:
                # print(json.dumps(m, indent=4))
                sfc.sc += m["stats"]["checks"]
                sfc.sc += m["stats"]["deletes"]
            statmsg.clear()
            return True
        else:
            sfc.fc += 1
            opmsg.clear()
            statmsg.clear()
            print(txt)
    return False


def fdellm(di, si, td, fl1, sfc):
    return all(fdell(di, si, td, fl2, sfc) for fl2 in chunk_from(fl1, 10))


def fdell(di, si, td, fl, sfc):
    cmd = 'rclone delete "'
    cmd += str(td) + '" '
    for fn in fl:
        cmd += '--include "' + str(fn.nm) + '" '
    cmd += "--progress -v --use-json-log"
    # cmd += '--log-file="rclone.log" '
    # cmd += "--use-json-log"
    if netup():
        # print("delete", td, list(map(lambda de: str(de.nm), fl)))
        print(cmd)
        rc, txt, opmsg, statmsg = ar_run(cmd)
        if rc == 0:
            for m in opmsg:
                # print(json.dumps(m, indent=4))
                for f in fl:
                    if str(f.nm) == m["object"] and m["msg"].startswith("Deleted"):
                        sfc.sc += 1
            opmsg.clear()
            for m in statmsg:
                # print(json.dumps(m, indent=4))
                sfc.sc += m["stats"]["checks"]
                sfc.sc += m["stats"]["deletes"]
            statmsg.clear()
            return True
        else:
            sfc.fc = len(fl)
            opmsg.clear()
            statmsg.clear()
            print(txt)
    return False


class BVars:
    def __init__(self, di, si, sfc) -> None:
        self.si = si
        self.di = di
        self.sd = config.src(si)
        self.td = config.tgt(di)
        self.src_dls = None
        self.dst_dls = None
        self.f2d = None
        self.f2c = None
        self.f2t = None
        self.sfc = sfc
        self.ac2 = 0

    def init2(self):
        self.src_dls = self.sd.Dlld()
        if self.src_dls is None:
            self.sfc.fc += 1
        self.dst_dls = self.td.Dlld()
        if self.src_dls is not None and self.dst_dls is not None:
            config.cull_DEs(self.src_dls)
            config.cull_DEs(self.dst_dls)
            self.f2d, self.f2c = config.dllcmp(self.dst_dls, self.src_dls)
        else:
            config.cull_DEs(self.src_dls)
            self.f2d = set()
            self.f2c = set(self.src_dls)
        self.f2t = set()

    def skip_matching(self):
        # handle slip through mismatched on times or more recent

        for rf in self.f2d.copy():
            for lf in self.f2c.copy():
                # TODO: use Path
                if rf.nm == lf.nm:  # names match
                    if rf.i.sz == lf.i.sz and rf.i.mt == lf.i.mt:  # sz,mt match
                        self.f2d.remove(rf)
                        self.f2c.remove(lf)
                    elif rf.i.sz == lf.i.sz:
                        if round(rf.i.mt) == round(lf.i.mt) or floor(rf.i.mt) == floor(
                            lf.i.mt
                        ):
                            self.f2d.remove(rf)
                            self.f2c.remove(lf)
                            self.f2t.add(lf)

    def do_touching(self):
        # TODO: use Path
        from findde import updateDEs

        cfpl = self.f2t.copy()
        if len(cfpl) == 0:
            return
        # print(cfp)
        for lf in cfpl:
            if ftouch(self.di, self.si, self.td, lf, self.sfc):
                self.ac2 += 1
                with contextlib.suppress(KeyError):
                    self.f2t.remove(lf)
        updateDEs(self.td, [str(de.nm) for de in cfpl])
        print("302 complete")

    def do_copying(self):
        # TODO: use Path

        cfpl = self.f2c.copy()
        if len(cfpl) == 0:
            return
        # print(cfp)
        if fsynclm(self.di, self.si, self.sd, self.td, cfpl, self.sfc):
            from findde import updateDEs

            for lf in cfpl:
                self.ac2 += 1
                with contextlib.suppress(KeyError):
                    self.f2c.remove(lf)

                for rf in self.f2d.copy():
                    if str(rf.nm) == str(lf.nm):
                        with contextlib.suppress(KeyError):
                            self.f2d.remove(rf)
            updateDEs(self.td, [str(de.nm) for de in cfpl])
            print("324 complete")

    def do_deletions(self):
        from findde import updateDEs

        cfpl = self.f2d.copy()
        if fdellm(self.di, self.si, self.td, cfpl, self.sfc):
            for rf in cfpl:  # do deletions
                self.ac2 += 1
                with contextlib.suppress(KeyError):
                    self.f2d.remove(rf)

        updateDEs(self.td, [str(de.nm) for de in cfpl])
        print("337 complete")

    def list_deletions(self):
        cfpl = self.f2d.copy()
        print("potential deletions", cfpl)


class CSCopy(OpBase):
    def __init__(self, npl1, npl2, opts={}) -> None:
        super().__init__(npl1, npl2, opts)
        self.sfc = SFc()

    def ischanged(self, e: Edge):
        return e.chk_ct() or e.rchk_ct()

    def __call__(self):
        from edge import Edge, findEdge
        from status import onestatus

        di, si = self.npl1
        print("CSCopy", si + "->" + di)
        if not netup():
            self.sfc.fc += 1
            return self.sfc.value()
        e: Edge = findEdge(di, si)
        if e.chk_ct():
            bv = BVars(di, si, self.sfc)
            bv.init2()
            if bv.sfc.fc == 0:
                print("raw", len(bv.f2d), "todelete", len(bv.f2c), "tocopy")
                bv.skip_matching()
                print("skip", len(bv.f2d), "todelete", len(bv.f2c), "tocopy")
            # if bv.sfc.fc == 0:
            # bv.do_touching()
            if bv.sfc.fc == 0:
                bv.do_copying()
            if bv.sfc.fc == 0:
                if "delete" in self.opts and self.opts["delete"] and len(bv.f2d):
                    bv.do_deletions()
            if bv.ac2:
                pass
        if self.sfc.fc == 0:
            e.clr()
            e.rclr()
        if self.sfc.sc > 0 and di in config.srcs:
            onestatus(di)
        return self.sfc.value()
import os
from math import floor
from os import walk
from pathlib import Path
from threading import Event, RLock
from typing import TypeAlias

from cscopy import CSCopy
from de import DE, FSe
from edge import Edge, addArc, addDep
from gitclasses import GitIndex, GitRemote, GitRepo, GitWT
from gitops import GitAdd, GitCommit, GitPush
from ldsv import load_all
from localcopy import LocalCopy
from opbase import OpBase
from sd import CS, SD, Ext3, Fat32

# from snoop import pp
# from snoop import snoop


quit_ev = Event()
rclk = RLock()

NodeTag: TypeAlias = str
Hash: TypeAlias = bytes
Hdt1: TypeAlias = dict[NodeTag, int]
Hdt2: TypeAlias = dict[Path, FSe]
Hdt3: TypeAlias = dict[NodeTag, Event]

# any/all mostly local directory path(s)
# paths: Dict[NodeTag, Path] = {}


class SetDict(dict):
    paths: dict[NodeTag, SD] = {}

    def __init__(self, *args) -> None:
        super().__init__(*args)

    def add(self, tg: str, sd: SD):
        if not hasattr(sd, "tag"):
            sd.tag = tg
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
        raise ValueError("not an SD subclass")
    srcs.add(tg, pth)
    pth.issrc = True
    if iscode:
        codes.add(tg, pth)
    if pth.isremote:
        RDlls[tg] = None
        RDlls_xt[tg] = 0
        RDhd[tg] = 0
    else:
        LDlls[tg] = None
        LDlls_xt[tg] = 0
        LDhd[tg] = 0
    Dllc[tg] = Event()


def addTgtDir(tg, pth):
    if not isinstance(pth, SD):
        raise ValueError("not an SD subclass")
    tgts.add(tg, pth)
    pth.istgt = True
    if pth.isremote:
        RDlls[tg] = None
        RDlls_xt[tg] = 0
        RDhd[tg] = 0
    else:
        LDlls[tg] = None
        LDlls_xt[tg] = 0
        LDhd[tg] = 0
    Dllc[tg] = Event()


def addPre(tg, frag):
    if not isinstance(frag, SD):
        raise ValueError("not an SD subclass")
    pres.add(tg, frag)
    Dllc[tg] = Event()


# operations (function objects)
opdep: list[OpBase] = []

# dependencies as edge set
eDep: set[Edge] = set()

# dependencies as stored by di,si
edges: dict[tuple[NodeTag, NodeTag], Edge] = {}


# directory lists hashes

LDhd: Hdt1 = {}
RDhd: Hdt1 = {}

Dllc: Hdt3 = {}


# files lists
LDlls: dict[NodeTag, list["DE"]] = {}
RDlls: dict[NodeTag, list["DE"]] = {}

# update times of directory lists
LDlls_xt: dict[NodeTag, float] = {}
RDlls_xt: dict[NodeTag, float] = {}

# pickle file filenames
edgepf: Path | None = None
ldllsf: Path | None = None
rdllsf: Path | None = None

ldhpf: Path | None = None
rdhpf: Path | None = None

# worktree of git repo
worktree: Path | None = None

# directory list hashing stats

sfb: int = 0

# directory list getting stats

dl1_cs = 0
dl2_cs = 0

# hashing stats
h_hits = 0
h_miss = 0

upd_cs = 0

home: Ext3 | None = None
sdcard: Fat32 | None = None
cloud1: CS | None = None
cloud2: CS | None = None
cloud3: CS | None = None
dsbog: Fat32 | None = None


def initConfig():
    global home, sdcard, cloud1, cloud2, cloud3, dsblog
    home = Ext3(os.environ["HOME"], tag="home")
    sdcard = Fat32("/sdcard", tag="sdcard")
    cloud1 = CS("GoogleDrive:", tag="cloud1")
    cloud2 = CS("OneDrive:", tag="cloud2")
    cloud3 = CS("DropBox:", tag="cloud3")
    dsblog = Fat32(os.environ["FDB_PATH"])

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

    addPre("sd", sdcard)
    addPre("gd", cloud1)
    addPre("od", cloud2)
    addPre("db", cloud3)

    addSrcDir("home", home, False)
    addSrcDir("bin", home / "bin", False)
    addSrcDir("sh", home / "bin/sh")
    addSrcDir("proj", sdcard / "projects", False)
    addSrcDir("bash", src("proj") / "bash")
    addSrcDir("blog", src("proj") / "blog")
    addSrcDir("docs", sdcard / "Documents", False)
    addSrcDir("blogds", dsblog, False)
    addSrcDir("backups", sdcard / "backups", False)
    addSrcDir("vids", sdcard / "VideoDownloader/Download", False)
    addSrcDir("zips", sdcard / "zips", False)
    # addSrcDir(".git", src("proj") / ".git", False)

    def f1():
        dl = getDL(src("proj"))
        for d in dl:
            dn = "proj" + "/" + d.name
            addSrcDir(dn, d, True)
            addDep("git_worktree", dn)
            addDep("zips", dn)
            addDep("proj", dn)

    # f1()

    addDep("git_worktree", "proj")

    global worktree
    worktree = sdcard / "projects"

    ga1 = GitWT(worktree, tag="git_worktree")
    addSrcDir("git_worktree", ga1)

    gc1 = GitIndex(worktree, tag="git_index")
    addSrcDir("git_index", gc1)

    gre1 = GitRepo(worktree, tag="git_repo", rmts=["bitbucket", "github"])
    addSrcDir("git_repo", gre1)

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

    addTgtDir("home", home)
    addTgtDir("bin", home / "bin")
    addTgtDir("sh", home / "bin/sh")
    addTgtDir("pl", home / "bin/pl")
    addTgtDir("backups", sdcard / "backups")
    addTgtDir("termux-backup", tgt("backups") / "termux-backup")
    addTgtDir("zips", sdcard / "zips")
    addTgtDir("blogds", dsblog)
    addTgtDir("blog", src("proj") / "blog")
    addTgtDir("bash", src("proj") / "bash")
    addTgtDir("plaid-node", src("proj") / "plaid-node")
    addTgtDir("docs", sdcard / "Documents")
    
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
                ".plaid-cli/**/*",
                ".plaidrc",
                ".git-credentials",
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
                ".plaid-cli/**/*",
                ".plaidrc",
                ".git-credentials",
                ".gitconfig",
            ]
        },
    )
    addArc(op2)

    npl1 = ("bin", "bash")
    op3 = LocalCopy(
        npl1,
        npl1,
        {
            "files": ["termux-*", "pbu", "ppc", "rbu", "rcu", "qe", "ftp*", "nt"],
            "exec": True,
        },
    )
    addArc(op3)

    npl1 = ("bash", "bin")
    op4 = LocalCopy(
        npl1,
        npl1,
        {
            "files": ["termux-*", "pbu", "ppc", "rcu", "rbu", "qe", "ftp*", "nt"],
            "exec": False,
        },
    )
    addArc(op4)

    npl1 = ("sh", "bash")
    op5 = LocalCopy(npl1, npl1, {"files": ["*.sh", "*.env"], "exec": True})
    addArc(op5)

    npl1 = ("bash", "sh")
    op6 = LocalCopy(npl1, npl1, {"files": ["*.sh", "*.env"], "exec": True})
    addArc(op6)

    npl1 = ("blogds", "blog")
    op7 = LocalCopy(npl1, npl1, {"files": ["blog.js"]})
    addArc(op7)

    npl1 = ("blog", "blogds")
    op8 = LocalCopy(npl1, npl1, {"files": ["*.db", "blog.js"]})
    addArc(op8)

    npl1 = ("plaid-node", "blogds")
    op9 = LocalCopy(npl1, npl1, {"files": ["*.db"]})
    addArc(op9)

    # npl1 = ('termux-backup', 'home')
    # op1 = LocalCopy(npl1, npl1, {'files': ['**/*.*']})
    # addArc(op1)

    npl1 = ("backups", "blogds")
    op10 = LocalCopy(npl1, npl1, {"files": ["*.db"]})
    addArc(op10)

    if "NOGIT" not in os.environ:
        npl1 = ("git_index", "git_worktree")
        op11 = GitAdd(npl1, npl1, {"wt": worktree})
        addArc(op11)

        npl1 = ("git_repo", "git_index")
        op12 = GitCommit(npl1, npl1, {"wt": worktree})
        addArc(op12)

        npl1 = ("bitbucket", "git_repo")
        op13 = GitPush(
            npl1,
            None,
            {"wt": worktree, "rmt": "bitbucket"},
        )
        addArc(op13)

        npl1 = ("github", "git_repo")
        op14 = GitPush(
            npl1,
            None,
            {"wt": worktree, "rmt": "github"},
        )
        addArc(op14)

    # for si in codes:
    # npl1 = ("zips", si)
    # op1 = Mkzip(npl1, npl1, {"zipfile": si + ".zip"})
    # addArc(op1)

    # for si in (".git",):
    # npl1 = ("zips", si)
    # op1 = Mkzip(npl1, npl1, {"zipfile": "projects-git.zip"})
    # addArc(op1)

    for cs in ("gd", "db", "od"):
        for si in ("proj", "vids", "zips"):
            if src(si).is_relative_to(ppre("sd")):
                p1 = src(si).relative_to(ppre("sd"))
            elif src(si).is_relative_to(src("home").parent):
                p1 = src(si).relative_to(src("home").parent)
            else:
                print("relative dir not found")
                raise ValueError()
            addTgtDir(cs + "_" + si, ppre(cs) / p1)
            npl1 = (cs + "_" + si, si)
            # op15 = CSRestore(npl1, None, {})
            # addArc(op15)
            op16 = CSCopy(npl1, npl1, {"delete": False})
            addArc(op16)

    load_all()


dexs = {
    ".cargo",
    ".cache",
    ".git",
    "go",
    "node_modules",
    "__pycache__",
    ".ropeproject",
    ".mypyproject",
    ".mypy_cache",
    ".ruff_cache",
    ".vite",
    ".yarnclean",
    "storage",
    "ldlls.pp",
    "rdlls.pp",
    "rdhd.pp",
    "ldhd.pp",
    "edges.pp",
    "rclone.conf",
}


def cull_DEs(des):
    des[:] = [de for de in des if not any(sd for sd in de.nm.parts if sd in dexs)]


def cull_files(files, pt):
    files[:] = [
        pt(f) for f in files if not any(sd for sd in f.parent.parts if sd in dexs)
    ]


def cull_dirs(dirs, pt):
    dirs[:] = [pt(d) for d in dirs if not isbaddir(pt(d))]


def isbaddir(dir):
    return any(dp for dp in dir.parts if dp in dexs)


def getDL(p):
    pt = type(p)
    # print(str(p))
    fl = []
    try:
        for pth, dirs, _files in walk(p, topdown=True):
            if not isinstance(pth, pt):
                pth = pt(pth)
            cull_dirs(dirs, pt)
            for d in dirs:
                fl.append(pth / d)
            dirs.clear()
        return fl
    except OSError as e:
        print("getDL", e)
        return fl


def ts_trunc2ms(s):
    return floor(s * 1.0e3) / 1.0e3


def ns_trunc2ms(ns):
    return floor(ns / 1.0e6) / 1.0e3


def dllcmp(do, dn):
    dns = set(dn)
    dos = set(do)
    tocopy = dns - dos
    todelete = dos - dns
    return (todelete, tocopy)

if __name__ == "__main__":
    main()

