import datetime
import json
import time
from bisect import bisect_left
from pathlib import Path
from threading import Lock
from typing import Dict, List, Set, Tuple, TypeAlias

import asyncrun as ar
import config as v
from de import DE, FSe

from fsmixin import FS_Mixin
from status import changed_ops, updatets

ul1 = Lock()


def findDE(dl, rp: Path):
    assert isinstance(dl[0], DE), "findde"
    assert isinstance(rp, Path), "findde"
    tde = DE(rp, FSe(0, 0))
    i = bisect_left(dl, tde)
    if i < len(dl) and tde.nm == dl[i].nm:
        return (dl[i], i)
    return (None, i)


def getRemoteDEs(rd: Path, fl: list[str]):
    assert isinstance(rd, Path)
    assert isinstance(fl, List)
    assert isinstance(fl[0], str)
    print("getRemoteDEs", rd, fl)
    pt = type(rd)
    cmd = 'rclone lsjson "' + str(rd) + '" '
    for fn in fl:
        cmd += '--include "' + fn + '" '
    cmd += " --recursive --files-only"
    rc = ar.run1(cmd)
    if rc == 0:
        assert ar.txt != ""

        delst = []
        jsl = json.loads(ar.txt)
        for it in jsl:
            it1 = pt(it["Path"])
            it2 = it["Size"]
            it3 = it["ModTime"][:-1] + "-00:00"
            it3 = datetime.datetime.fromisoformat(it3).timestamp()
            it3 = v.ts_trunc2ms(it3)
            fse = FSe(it2, it3)
            nde = DE(it1, fse)
            print("new nde:", nde.nm, nde.i.sz, nde.i.mt)
            delst.append(nde)
        return delst
    else:
        print("getRemoteDE returned", rc)


def findSis(fp1: Path):
    l1 = {}
    for si in v.srcs:
        try:
            fp2 = v.paths[si]
            if fp1.parent.is_relative_to(fp2):
                rp1 = fp1.relative_to(fp2)
                l1[si] = rp1
        except Exception as exc:
            print(exc)
            raise exc
    return l1


def findDis(fp1: Path):
    l1 = {}
    for di in v.tgts:
        try:
            fp2 = v.paths[di]
            if fp1.parent.is_relative_to(fp2):
                rp1 = fp1.relative_to(fp2)
                l1[di] = rp1
        except:
            print(exc)
            raise exc
    return l1


def findSDEs(fp: Path):
    assert isinstance(fp, Path)
    sil = findSis(fp)
    assert isinstance(sil, Dict)
    de_l = []
    for si in sil:
        assert isinstance(si, str)
        p = v.src(si)
        rp = sil[si]
        assert isinstance(rp, Path)
        if isinstance(p, FS_Mixin) and p.Dll:
            de, i = findDE(p.Dll, rp)
            de_l.append((p.Dll, rp, de, i, si))
    return de_l


def findTDEs(fp: Path):
    assert isinstance(fp, Path)
    dil = findDis(fp)
    assert isinstance(dil, Dict)
    de_l = []
    for di in dil:
        assert isinstance(di, str)
        p = v.tgt(di)
        rp = dil[di]
        assert isinstance(rp, Path)
        if isinstance(p, FS_Mixin) and p.Dll:
            de, i = findDE(p.Dll, rp)
            de_l.append((p.Dll, rp, de, i, di))
    return de_l


def updateDEs(rd: Path, flst: List[str]):
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
                print("update", sde.nm, "->", tde.nm)
                if tde.i.sz != sde.i.sz:
                    print("size mismatch")
                    tde.i.sz = sde.i.sz
                if tde.i.mt != sde.i.mt:
                    print("modtime mismatch")
                    tde.i.mt = sde.i.mt

            else:
                print("insert", sde.nm)
                fse = FSe(sde.i.sz, sde.i.mt)
                tde = DE(rp, fse)
                dl.insert(i, tde)
        else:
            if tde:
                print("would delete", rp)
                # dl.pop(i)

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
                print("update", sde.nm, "->", tde.nm)
                if tde.i.sz != sde.i.sz:
                    print("size mismatch")
                    tde.i.sz = sde.i.sz
                if tde.i.mt != sde.i.mt:
                    print("modtime mismatch")
                    tde.i.mt = sde.i.mt

            else:
                print("insert", sde.nm)
                fse = FSe(sde.i.sz, sde.i.mt)
                tde = DE(rp, fse)
                dl.insert(i, tde)
        else:
            if tde:
                print("would delete", rp)
                # dl.pop(i)

    with ul1:
        assert ul1.locked()
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


def test1():
    v.initConfig()
    updatets(0)
    rd = v.src("pybackup")
    f = "findde.py"
    updateDEs(rd, [f])
    updatets(1)
    print(changed_ops())


if __name__ == "__main__":
    test1()
