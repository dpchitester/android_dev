import contextlib
import datetime
import json
from bisect import bisect_left
from pathlib import Path
from threading import Thread
from time import sleep

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
    cmd = 'rclone lsjson "' + str(rd) + '" '
    cmd += ' --include="' + fn + '"'
    cmd += " --files-only"
    print(cmd)
    rc = ar.run1(cmd)
    sleep(0)
    jsl = json.loads(ar.txt) if rc == 0 else []
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
    jsl = []
    jstl = []

    def f1(fn):
        jsl.extend(getRemoteJSde(rd, fn))

    for fn in fl:
        th = Thread(target=f1, args=(fn,))
        th.start()
        print(th, 'started')
        jstl.append(th)
        while len(jstl) > 5:
            sleep(0)
            th = jstl.pop()
            th.join()
            print(th, 'joined')
    while len(jstl):
        sleep(0)
        th = jstl.pop()
        th.join()
        print(th, 'joined')
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

    return l1


def findDis(fp1: Path):
    l1 = {}
    for di, p in config.tgts.items():
        if isinstance(p, FS_Mixin):
            with contextlib.suppress(ValueError):
                l1[di] = fp1.relative_to(p)

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
