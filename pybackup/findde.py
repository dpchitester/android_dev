import datetime
import json
import time
from bisect import bisect_left
from pathlib import Path
from threading import Lock

import asyncrun as ar
import config as v
from de import DE
from fmd5h import fmd5f
from fsmixin import FS_Mixin
from status import changed_ops, updatets

ul1 = Lock()
from snoop import snoop, pp

def findDE(dl, rp: Path):
    i = bisect_left(dl, rp, key=lambda de: de.nm)
    if i < len(dl) and rp.name == dl[i].nm.name:
        return (dl[i], i)
    return (None, i)

@snoop
def getRemoteDEs(rd: Path, fl: list[str]):
    pt = type(rd)
    cmd = 'rclone lsjson "' + str(rd) + '" '
    for fn in fl:
        cmd += '--include "' + fn + '" '
    cmd += " --recursive --files-only --hash"
    rc = ar.run1(cmd)
    if rc == 0:
        print('json return', ar.txt)
        if ar.txt == "[]":
            print("lsjson returned empty list")
            return []
        delst = []
        jsl = json.loads(ar.txt)
        for it in jsl:
            it1 = pt(it["Path"])
            it2 = it["Size"]
            it3 = it["ModTime"][:-1] + "-00:00"
            it3 = datetime.datetime.fromisoformat(it3).timestamp()
            if "Hashes" in it:
                it4 = bytes.fromhex(it["Hashes"]["md5"])
            else:
                it4 = bytes()
            fse = fmd5f(rd / it1, it2, it3, it4)
            nde = DE(it1, fse)
            print("new nde:", nde.nm, nde.i.sz, nde.i.mt)
            delst.append(nde)
        return delst
    else:
        print("getRemoteDE returned", rc)
    return []


def findSis(fp1: Path):
    l1 = {}
    for si in v.srcs:
        try:
            fp2 = v.paths[si]
            if fp1.parent.is_relative_to(fp2):
                rp1 = fp1.relative_to(fp2)
                l1[si] = rp1
        except:
            pass
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
            pass
    return l1


def findSDEs(fp: Path):
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
    dil = findDis(fp)
    de_l = []
    for di in dil:
        p = v.tgt(di)
        rp = dil[di]
        if isinstance(p, FS_Mixin) and p.Dll:
            de, i = findDE(p.Dll, rp)
            de_l.append((p.Dll, rp, de, i, di))
    return de_l


def updateDEs(rd: Path, flst: list[str]):
    with ul1:
        sdel = getRemoteDEs(rd, flst)
        for fi in flst:
            fp = rd / fi
            sdes = findSDEs(fp)
            tdes = findTDEs(fp)

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
                        if tde.i.md5 != sde.i.md5:
                            print("md5 mismatch")
                            tde.i.md5 = sde.i.md5
                    else:
                        print("insert", sde.nm)
                        fse = fmd5f(fp, sde.i.sz, sde.i.mt, sde.i.md5)
                        tde = DE(rp, fse)
                        dl.insert(i, tde)
                else:
                    if tde:
                        print("delete", rp)
                        dl.pop(i)

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
                        if tde.i.md5 != sde.i.md5:
                            print("md5 mismatch")
                            tde.i.md5 = sde.i.md5
                    else:
                        print("insert", sde.nm)
                        fse = fmd5f(fp, sde.i.sz, sde.i.mt, sde.i.md5)
                        tde = DE(rp, fse)
                        dl.insert(i, tde)
                else:
                    if tde:
                        print("delete", rp)
                        dl.pop(i)

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
