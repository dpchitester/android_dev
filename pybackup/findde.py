import datetime
import json
import time
from bisect import bisect_left
from os.path import realpath
from pathlib import Path
from threading import Lock
from typing import Dict, List, Set, Tuple, TypeAlias

from snoop import snoop, pp
snoop.install(out='snoop.log',overwrite=True)

import asyncrun as ar
import ldsv as ls
from de import DE, FSe
from sd import FS_Mixin

@snoop
def findDE(dl, rp: Path):
    assert isinstance(dl[0], DE), "findde"
    assert isinstance(rp, Path), "findde"
    tde = DE(rp, FSe(0, 0))
    i = bisect_left(dl, tde)
    if i < len(dl):
        pp('tde', tde)
        pp('dl[i]', dl[i])
        pp('tde.nm==dl[i].nm',tde.nm == dl[i].nm)
        if tde.nm == dl[i].nm:
            return (dl[i], i)
    return (None, i)

@snoop
def getJSde(rd:Path, fn):
    cmd = 'rclone lsjson "' + str(rd) + '" '
    cmd += ' --include="' + fn + '"'
    cmd += " --files-only"
    pp('cmd', cmd)
    rc = ar.run1(cmd)
    pp(rc, ar.txt)
    if rc == 0:
        assert ar.txt != ""
        jsl = json.loads(ar.txt)
    else:
        jsl = []
    return jsl

@snoop
def getRemoteDE(rd:Path, fn:str):
    fp = rd / fn
    l1 = getJSde(fp.parent, fp.name)
    if len(l1):
        it = l1[0]
        it["Path"] = str(fp.relative_to(rd))
        return [it]
    else:
        return []
    
@snoop
def getRemoteDEs(rd: Path, fl: list[str]):
    import config as v

    pp("getRemoteDEs", rd, fl)
    jsl = []
    for fn in fl:
        jsl.extend(getRemoteDE(rd, fn))
    pt = Path
    pp(jsl)
    delst = []
    for it in jsl:
        it1 = pt(it["Path"])
        it2 = it["Size"]
        it3 = it["ModTime"][:-1] + "-00:00"
        it3 = datetime.datetime.fromisoformat(it3).timestamp()
        it3 = v.ts_trunc2ms(it3)
        fse = FSe(it2, it3)
        nde = DE(it1, fse)
        pp("new nde:", nde.nm, nde.i.sz, nde.i.mt)
        delst.append(nde)
    return delst


def findSis(fp1: Path):
    import config as v

    assert isinstance(fp1, Path)
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

    assert isinstance(fp1, Path)
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

    assert isinstance(fp, Path)
    sil = findSis(fp)
    assert isinstance(sil, Dict)
    de_l = []
    for si in sil:
        assert isinstance(si, str)
        p = v.src(si)
        rp = sil[si]
        assert isinstance(p, Path)
        assert isinstance(rp, Path)
        if isinstance(p, FS_Mixin) and p.Dll:
            de, i = findDE(p.Dll, rp)
            de_l.append((p.Dll, rp, de, i, si))
    return de_l


def findTDEs(fp: Path):
    import config as v

    assert isinstance(fp, Path)
    dil = findDis(fp)
    assert isinstance(dil, Dict)
    de_l = []
    for di in dil:
        assert isinstance(di, str)
        p = v.tgt(di)
        rp = dil[di]
        assert isinstance(p, Path)
        assert isinstance(rp, Path)
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
                pp("update", sde.nm, "->", tde.nm)
                if tde.i.sz != sde.i.sz:
                    pp("size mismatch")
                    tde.i.sz = sde.i.sz
                    ls.sev.put("ldlls" if not p.isremote else "rdlls")
                if tde.i.mt != sde.i.mt:
                    pp("modtime mismatch")
                    tde.i.mt = sde.i.mt
                    ls.sev.put("ldlls" if not p.isremote else "rdlls")
            else:
                pp("insert", sde.nm)
                fse = FSe(sde.i.sz, sde.i.mt)
                tde = DE(rp, fse)
                dl.insert(i, tde)
                ls.sev.put("ldlls" if not p.isremote else "rdlls")
        else:
            if tde:
                pp("would delete", rp)
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
                pp("update", sde.nm, "->", tde.nm)
                if tde.i.sz != sde.i.sz:
                    pp("size mismatch")
                    tde.i.sz = sde.i.sz
                    ls.sev.put("ldlls" if not p.isremote else "rdlls")
                if tde.i.mt != sde.i.mt:
                    pp("modtime mismatch")
                    tde.i.mt = sde.i.mt
                    ls.sev.put("ldlls" if not p.isremote else "rdlls")
            else:
                pp("insert", sde.nm)
                fse = FSe(sde.i.sz, sde.i.mt)
                tde = DE(rp, fse)
                dl.insert(i, tde)
                ls.sev.put("ldlls" if not p.isremote else "rdlls")
        else:
            if tde:
                pp("would delete", rp)
                # dl.pop(i)
                pass

    with ls.dl:
        sdel = getRemoteDEs(rd, flst)
        assert sdel is not None
        for fi in flst:
            assert isinstance(fi, str)
            fp = rd / fi
            sdes = findSDEs(fp)
            tdes = findTDEs(fp)
            assert sdes is not None
            assert tdes is not None

            for it in sdes:
                doSOne(*it)
            for it in tdes:
                doTOne(*it)
