import datetime
import json
import time
from bisect import bisect_left
from os.path import realpath
from pathlib import Path
from threading import Lock
from typing import Dict, List, Set, Tuple, TypeAlias

import asyncrun as ar
import ldsv as ls
from de import DE, FSe
from sd import FS_Mixin


def findDE(dl, rp: Path):
    tde = DE(rp, FSe(0, 0))
    i = bisect_left(dl, tde)
    if i < len(dl):
        if tde.nm == dl[i].nm:
            return (dl[i], i)
    return (None, i)


def getOneJSde(rd: Path, fn):
    cmd = 'rclone lsjson "' + str(rd) + '" '
    cmd += ' --include="' + fn + '"'
    cmd += " --files-only"
    rc = ar.run1(cmd)
    if rc == 0:
        jsl = json.loads(ar.txt)
    else:
        jsl = []
    return jsl


def getRemoteJSde(rd: Path, fn: str):
    fp = rd / fn
    l1 = getOneJSde(fp.parent, fp.name)
    if len(l1):
        it = l1[0]
        it["Path"] = str(fp.relative_to(rd))
        return [it]
    else:
        return []


def getRemoteDEs(rd: Path, fl: list[str]):
    import config as v

    jsl = []
    for fn in fl:
        jsl.extend(getRemoteJSde(rd, fn))
    pt = Path
    delst = []
    for it in jsl:
        it1 = pt(it["Path"])
        it2 = it["Size"]
        it3 = it["ModTime"][:-1] + "-00:00"
        it3 = datetime.datetime.fromisoformat(it3).timestamp()
        it3 = v.ts_trunc2ms(it3)
        fse = FSe(it2, it3)
        nde = DE(it1, fse)
        delst.append(nde)
    return delst


def findSis(fp1: Path):
    import config as v

    l1 = {}
    for si, p in v.srcs.items():
        if isinstance(p, FS_Mixin):
            try:
                l1[si] = fp1.relative_to(p)
            except ValueError as exc:
                pass
    return l1


def findDis(fp1: Path):
    import config as v

    l1 = {}
    for di, p in v.tgts.items():
        if isinstance(p, FS_Mixin):
            try:
                l1[di] = fp1.relative_to(p)
            except ValueError:
                pass
    return l1


def findSDEs(fp: Path):
    import config as v

    sil = findSis(fp)
    de_l = []
    for si in sil:
        p = v.src(si)
        rp = sil[si]

        if isinstance(p, FS_Mixin) and p.Dll:
            de, i = findDE(p.Dll, rp)
            de_l.append((p.Dll, rp, de, i, si))
    return de_l


def findTDEs(fp: Path):
    import config as v

    dil = findDis(fp)
    de_l = []
    for di in dil:
        p = v.tgt(di)
        rp = dil[di]

        if isinstance(p, FS_Mixin) and p.Dll:
            de, i = findDE(p.Dll, rp)
            de_l.append((p.Dll, rp, de, i, di))
    return de_l


def updateDEs(rd: Path, flst: List[str]):
    import config as v

    def doSOne(dl, rp, tde, i, si):
        if tde:
            sde = [sde for sde in sdel if sde.nm.name == tde.nm.name]
            if len(sde):
                sde = sde[0]
            else:
                sde = None
        else:
            sde = None
        p = v.src(si)
        if sde:
            if tde:
                if tde.i.sz != sde.i.sz:
                    tde.i.sz = sde.i.sz
                    ls.sev.put("ldlls" if not p.isremote else "rdlls")
                if tde.i.mt != sde.i.mt:
                    tde.i.mt = sde.i.mt
                    ls.sev.put("ldlls" if not p.isremote else "rdlls")
            else:
                fse = FSe(sde.i.sz, sde.i.mt)
                tde = DE(rp, fse)
                dl.insert(i, tde)
                ls.sev.put("ldlls" if not p.isremote else "rdlls")
        else:
            if tde:
                # dl.pop(i)
                pass

    def doTOne(dl, rp, tde, i, di):
        if tde:
            sde = [sde for sde in sdel if sde.nm.name == tde.nm.name]
            if len(sde):
                sde = sde[0]
            else:
                sde = None
        else:
            sde = None
        p = v.tgt(di)
        if sde:
            if tde:
                if tde.i.sz != sde.i.sz:
                    tde.i.sz = sde.i.sz
                    ls.sev.put("ldlls" if not p.isremote else "rdlls")
                if tde.i.mt != sde.i.mt:
                    tde.i.mt = sde.i.mt
                    ls.sev.put("ldlls" if not p.isremote else "rdlls")
            else:
                fse = FSe(sde.i.sz, sde.i.mt)
                tde = DE(rp, fse)
                dl.insert(i, tde)
                ls.sev.put("ldlls" if not p.isremote else "rdlls")
        else:
            if tde:
                # dl.pop(i)
                pass

    with ls.dl:
        sdel = getRemoteDEs(rd, flst)
        for fi in flst:
            fp = rd / fi
            sdes = findSDEs(fp)
            tdes = findTDEs(fp)

            for it in sdes:
                doSOne(*it)
            for it in tdes:
                doTOne(*it)
