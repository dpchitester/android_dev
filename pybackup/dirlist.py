import asyncio
import datetime
import json
import time
from bisect import bisect_left
from fnmatch import fnmatch
from math import floor
from os import walk
from pathlib import Path

from snoop import pp, snoop

import asyncrun as ar
import config as v
from fmd5h import fmd5f

rto1 = 60 * 5
rto2 = 60 * 60


def getfl(p):
    # print(str(p))
    fl = []
    try:
        if p.is_file():
            fl.append(p)
            return fl
        for pth, dirs, files in walk(p, topdown=True):
            if not v.isbaddir(pth):
                v.proc_dirs(dirs)
                for f in files:
                    fl.append(Path(pth, f))
            else:
                dirs = []
                files = []
        return fl
    except Exception as e:
        print(e)
        return fl


def getDL(p):
    # print(str(p))
    fl = []
    try:
        for pth, dirs, files in walk(p, topdown=True):
            if not v.isbaddir(pth):
                v.proc_dirs(dirs)
                for d in dirs.copy():
                    fl.append(Path(pth, d))
                    dirs.remove(d)
            else:
                dirs = []
                files = []
        return fl
    except Exception as e:
        print("getDL", e)
        return fl


def getdll0():
    v.dl0_cs += 1
    td = v.ppre("gd")
    # print('getdll0',td)
    cmd = 'rclone lsjson "' + str(td) + '" --recursive --files-only --hash '
    for ex in dexs:
        cmd += ' --exclude "**/' + ex + '/*" '
    rc = ar.run1(cmd)
    if rc == 0:
        l1 = json.loads(ar.txt)

        def es(it: dict):
            it1 = Path(it["Path"])
            it2 = it["Size"]
            it3 = it["ModTime"][:-1] + "-00:00"
            it3 = datetime.datetime.fromisoformat(it3).timestamp()
            if "Hashes" in it:
                it4 = bytes.fromhex(it["Hashes"]["md5"])
            else:
                it4 = bytes()
            fp = td / it1
            fse = fmd5f(fp, it2, it3, it4)
            return v.DE(it1, fse)

        st = list(map(es, l1))
        st.sort(key=lambda de: de.nm)
        print(len(st), "de's")
        return st
    return None


def sepdlls(dlls):
    print("-sepdlls")
    for di in v.tgts:
        if di.startswith("gd_"):
            v.TDlls[di] = []
            v.TDlls_xt[di] = time.time()
            v.TDlls_changed = True
            bd = v.tgts(di)
            rd = bd.relative_to(v.ppre("gd"))
            tds = str(rd) + "/"
            i = bisect_left(dlls, tds, key=lambda de: de.nm)
            # print(tds, i)
            if i == len(dlls):
                continue
            de = dlls[i]
            if not fnmatch(de.nm, tds + "*"):
                print("error")
                print(rd, tds, i, de.nm)
                # TODO: apply panic procedure
                continue
            while fnmatch(de.nm, tds + "*"):
                fp = v.ppre("gd") / de.nm
                fse = fmd5f(fp, de.i.sz, de.i.mt, de.i.md5)
                de2 = v.DE(de.nm, fse)
                # TODO: use Path
                de2.nm = de2.nm.relative_to(rd)
                v.TDlls[di].append(de2)
                i += 1
                if i == len(dlls):
                    break
                de = dlls[i]
    print(len(v.TDlls), "rdlls")


def getdll1(di):
    v.dl1_cs += 1
    td = v.tgt(di)
    # print('getdll1', di, str(td))
    cmd = 'rclone lsjson "' + str(td) + '" --recursive --files-only --hash --fast-list '
    for ex in dexs:
        cmd += ' --exclude "**/' + ex + '/*" '
    # print(cmd)
    rc = ar.run1(cmd)
    if rc == 0:
        l1 = json.loads(ar.txt)
        if l1 is None:
            l1 = []

        def es(it: dict):
            # TODO: use Path
            it1 = Path(it["Path"])
            it2 = it["Size"]
            it3 = it["ModTime"][:-1] + "-00:00"
            it3 = datetime.datetime.fromisoformat(it3).timestamp()
            if "Hashes" in it:
                it4 = bytes.fromhex(it["Hashes"]["md5"])
            else:
                it4 = bytes()
            fp = td / it1
            fse = fmd5f(fp, it2, it3, it4)
            return v.DE(it1, fse)

        st = list(map(es, l1))
        st.sort(key=lambda de: de.nm)
        return st
    if rc == 3:
        return []
    return None


def getdll2(si):
    v.dl2_cs += 1
    td = v.src(si)
    # print('getdll2', si, str(td))
    cmd = 'rclone lsjson "' + str(td) + '" --recursive --files-only --hash --fast-list '
    if not td.is_file():
        for ex in dexs:
            cmd += ' --exclude "**/' + ex + '/*" '
    # print(cmd)
    rc = ar.run1(cmd)
    if rc == 0:
        l1 = json.loads(ar.txt)

        def es(it: dict):
            # TODO: use Path
            it1 = Path(it["Path"])
            it2 = it["Size"]
            it3 = it["ModTime"][:-7] + "-00:00"
            it3 = datetime.datetime.fromisoformat(it3).timestamp()
            if "Hashes" in it:
                it4 = bytes.fromhex(it["Hashes"]["md5"])
            else:
                it4 = bytes()
            fp = td / it1
            fse = fmd5f(fp, it2, it3, it4)
            return v.DE(it1, fse)

        st = list(map(es, l1))
        st.sort(key=lambda de: de.nm)
        return st
    if rc == 3:
        return []
    return None


def getdll3(si):
    v.dl3_cs += 1
    td = v.src(si)
    # print('getdll3', si, str(sd))
    l1 = getfl(td)

    def es(it: Path):
        # TODO: use Path
        it1 = it.relative_to(td)
        fs = it.stat()
        it2 = fs.st_size
        it3 = fs.st_mtime_ns
        it3 = v.trunc2ms(it3)
        fp = td / it1
        fse = fmd5f(fp, it2, it3)
        return v.DE(it1, fse)

    st = list(map(es, l1))
    st.sort(key=lambda de: de.nm)
    return st


def getrdlls():
    t1 = time.time()
    rv = getdll0()
    if rv is not None:
        t2 = time.time()
        sepdlls(rv)
        t3 = time.time()
        print(round(t2 - t1, 3), round(t3 - t2, 3))


def lDlld(si):
    # print('-ldlld', si)
    # print("obtaining", si, "ldll...", end="")
    if si not in v.SDlls or v.SDlls_xt[si] + rto1 <= time.time():
        rv = getdll3(si)
        if rv is not None:
            # print("done.")
            v.SDlls[si] = rv
            v.SDlls_xt[si] = time.time()
            v.SDlls_changed = True
        else:
            print("failed.")
    else:
        # print("retrieved.")
        pass
    return v.SDlls[si]


def rDlld(di):
    # print('-rdlld', di)
    # print("obtaining", di, "rdll...", end="")
    if di not in v.TDlls or v.TDlls_xt[di] + rto2 <= time.time():
        rv = getdll1(di)
        if rv is not None:
            # print("done.")
            v.TDlls[di] = rv
            v.TDlls_xt[di] = time.time()
            v.TDlls_changed = True
        else:
            print("failed.")
    else:
        # print("retrieved.")
        pass
    return v.TDlls[di]


def dllcmp(do, dn):
    dns = set(dn)
    dos = set(do)
    tocopy = dns - dos
    todelete = dos - dns
    return (todelete, tocopy)
