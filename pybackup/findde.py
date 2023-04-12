import datetime
import json
import time
from bisect import bisect_left
from math import floor
from pathlib import Path

from snoop import snoop, pp

import asyncrun as ar
import config as v
from fmd5h import fmd5f
from status import changed_ops, rupdatets, updatets


def findDE(dl, rp):
    i = bisect_left(dl, rp, key=lambda de: de.nm)
    if i < len(dl) and rp.name == dl[i].nm.name:
        return (dl[i], i)
    return (None, i)


def getRemoteDEs(rd: Path, fl: list[str]):
    cmd = 'rclone lsjson "' + str(rd) + '" '
    for fn in fl:
        cmd += '--include "' + fn + '" '
    cmd += ' --hash'
    rc = ar.run1(cmd)
    if rc == 0:
        if ar.txt == "[]":
            print("lsjson returned empty list")
            return []
        delst = []
        jsl = json.loads(ar.txt)
        for it in jsl:
            it1 = Path(it["Path"])
            it2 = it["Size"]
            it3 = it["ModTime"][:-1] + "-00:00"
            it3 = datetime.datetime.fromisoformat(it3).timestamp()
            if "Hashes" in it:
                it4 = bytes.fromhex(it["Hashes"]["md5"])
            else:
                it4 = bytes()
            fse = fmd5f(rd / it1, it2, it3, it4)
            nde = v.DE(it1, fse)
            print("new nde:", nde.nm, nde.i.sz, nde.i.mt)
            delst.append(nde)
        return delst
    else:
        print("getRemoteDE returned", rc)
    return []


def findSis(fp1):
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


def findDis(fp1):
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


def findSDEs(fp):
    sil = findSis(fp)
    de_l = []
    for si in sil:
        rp = sil[si]
        if si in v.SDlls:
            de, i = findDE(v.SDlls[si], rp)
            de_l.append((v.SDlls[si], rp, de, i, si))
    return de_l


def findTDEs(fp):
    dil = findDis(fp)
    de_l = []
    for di in dil:
        rp = dil[di]
        if di in v.TDlls:
            de, i = findDE(v.TDlls[di], rp)
            de_l.append((v.TDlls[di], rp, de, i, di))
    return de_l

@snoop
def updateDEs(rd, flst):
    sdel = getRemoteDEs(rd, flst)
    for sde in sdel:
        fp = rd / sde.nm
        sdes = findSDEs(fp)
        tdes = findTDEs(fp)
    
        def doSOne(dl, rp, tde, i, si):
            if sde:
                if tde:
                    print("update", sde.nm, "->", tde.nm)
                    if tde.i.sz != sde.i.sz:
                        print("size mismatch")
                        tde.i.sz = sde.i.sz
                        v.SDlls_xt[si] = time.time()
                        v.SDlls_changed = True
                    if tde.i.mt != sde.i.mt:
                        print("modtime mismatch")
                        tde.i.mt = sde.i.mt
                        v.SDlls_xt[si] = time.time()
                        v.SDlls_changed = True
                    if tde.i.md5 != sde.i.md5:
                        print("md5 mismatch")
                        tde.i.md5 = sde.i.md5
                        v.SDlls_xt[si] = time.time()
                        v.SDlls_changed = True
                else:
                    print("insert", sde.nm)
                    fse = fmd5f(fp, sde.i.sz, sde.i.mt, sde.i.md5)
                    tde = v.DE(rp, fse)
                    dl.insert(i, tde)
                    v.SDlls_xt[si] = time.time()
                    v.SDlls_changed = True
            else:
                if tde:
                    print("delete", rp)
                    dl.pop(i)
                    v.SDlls_xt[si] = time.time()
                    v.SDlls_changed = True
    
        def doTOne(dl, rp, tde, i, di):
            if sde:
                if tde:
                    print("update", sde.nm, "->", tde.nm)
                    if tde.i.sz != sde.i.sz:
                        print("size mismatch")
                        tde.i.sz = sde.i.sz
                        v.TDlls_xt[di] = time.time()
                        v.TDlls_changed = True
                    if tde.i.mt != sde.i.mt:
                        print("modtime mismatch")
                        tde.i.mt = sde.i.mt
                        v.TDlls_xt[di] = time.time()
                        v.TDlls_changed = True
                    if tde.i.md5 != sde.i.md5:
                        print("md5 mismatch")
                        tde.i.md5 = sde.i.md5
                        v.TDlls_xt[di] = time.time()
                        v.TDlls_changed = True
                else:
                    print("insert", sde.nm)
                    fse = fmd5f(fp, sde.i.sz, sde.i.mt, sde.i.md5)
                    tde = v.DE(rp, fse)
                    dl.insert(i, tde)
                    v.TDlls_xt[di] = time.time()
                    v.TDlls_changed = True
            else:
                if tde:
                    print("delete", rp)
                    dl.pop(i)
                    v.TDlls_xt[di] = time.time()
                    v.TDlls_changed = True
    
        for it in sdes:
            doSOne(*it)
        for it in tdes:
            doTOne(*it)


def test1():
    v.initConfig()
    updatets(0)
    rd = v.src("pybackup")
    f = "findde.py"
    updateDEs(rd, f)
    updatets(1)
    print(changed_ops())


if __name__ == "__main__":
    test1()
