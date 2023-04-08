from pathlib import Path
from os import walk
from functools import partial

import config_vars as v
from statushash import rdhck, ldhck


def ppre(s):
    if s in v.pres:
        return v.paths[s]
    else:
        raise KeyError(s + " tag not in pres")


def pdir(s):
    if s in v.pdirs:
        return v.paths[s]
    else:
        raise KeyError(s + " tag not in pdirs")


def tdir(s):
    if s in v.tdirs:
        return v.paths[s]
    else:
        raise KeyError(s + " tag not in tdirs")


def srcDir(s):
    if s in v.srcs:
        return v.paths[s]
    else:
        raise KeyError(s + " tag not in srcs")


def tdir(s):
    if s in v.tgts:
        return v.paths[s]
    else:
        raise KeyError(s + " tag not in tgts")


def cdir(s):
    if s in v.codes:
        return v.paths[s]
    else:
        raise KeyError(s + " tag not in codes")


def addTgtDir(tg, pth):
    if not isinstance(pth, Path):
        pth = Path(pth)
    if tg in v.paths and v.paths[tg] != pth:
        raise Exception("path tag collision", tg, pth, v.paths[tg])
    v.paths[tg] = pth
    v.tgts.add(tg)
    v.rckers[tg] = partial(rdhck, tg)
    v.tdirs.add(tg)


def addSrcDir(tg, pth, iscode=False):
    if not isinstance(pth, Path):
        pth = Path(pth)
    if tg in v.paths and v.paths[tg] != pth:
        raise Exception("path tag collision", tg, pth, v.paths[tg])
    v.paths[tg] = pth
    v.pdirs.add(tg)
    v.srcs.add(tg)
    v.lckers[tg] = partial(ldhck, tg)
    if iscode:
        v.codes.add(tg)


def addPre(tg, frag):
    if not isinstance(frag, Path):
        frag = Path(frag)
    if tg in v.paths and v.paths[tg] != frag:
        raise Exception("path tag collision", tg, v.paths[tg])
    v.paths[tg] = frag
    v.pres.add(tg)


def getDL(p):
    # print(str(p))
    fl = []
    try:
        for pth, dirs, files in walk(p, topdown=True):
            if ".git" in pth:
                dirs = []
                break
            if ".git" in dirs:
                dirs.remove(".git")
            if "__pycache__" in dirs:
                dirs.remove("__pycache__")
            for d in dirs.copy():
                fl.append(Path(pth, d))
                dirs.remove(d)
            break
        return fl
    except Exception as e:
        print("getDL", e)
        return None


def round2ms(ns):
    return int(str(ns + 500000)[:-6]) / 1e3


def trunc2ms(ns):
    return int(str(ns)[:-6]) / 1e3
