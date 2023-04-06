import asyncio
from pathlib import Path
from os import walk
import json
import datetime
import time
from dataclasses import dataclass, field
from fnmatch import fnmatch
from bisect import bisect_left

import asyncrun as ar
import config_vars as v
from bhash import blakeHash
from fmd5h import fmd5f


rto1 = 0  # 60*60*.5
rto2 = 0  # 60*1

@dataclass
class DE():
    nm: Path
    sz: int
    mt: float
    md5: bytes
    _hc: int = field(default=None)

    def __hash__(self):
        if self._hc is None:
            self._hc = blakeHash((self.nm, self.sz, self.mt, self.md5))
        return self._hc

    def __eq__(self, other):
        return (str(self.nm), self.sz, self.mt,
                self.md5) == (str(other.nm), other.sz, other.mt, other.md5)

    def __lt__(self, other):
        return (str(self.nm), self.sz, self.mt, self.md5) < (str(
            other.nm), other.sz, other.mt, other.md5)

def getRemoteDE(sf:Path):
    cmd = 'rclone lsjson "' + str(sf) + '" --hash'
    rc = ar.run1(cmd)
    if rc == 0:
        it = json.loads(ar.txt)[0]
        it1 = Path(it['Path'])
        it2 = it['Size']
        it3 = it['ModTime'][:-1] + '-00:00'
        it3 = datetime.datetime.fromisoformat(it3).timestamp()
        if 'Hashes' in it:
            it4 = bytes.fromhex(it['Hashes']['md5'])
        else:
            it4 = bytes()
        return DE(it1, it2, it3, it4)

def getfl(p):
    # print(str(p))
    fl = []
    try:
        if p.is_file():
            fl.append(p)
            return fl
        for pth, dirs, files in walk(p, topdown=True):
            if '.git' in pth:
                dirs = []
                break
            if '.git' in dirs:
                dirs.remove('.git')
            if '__pycache__' in dirs:
                dirs.remove('__pycache__')
            for f in files:
                fl.append(Path(pth, f))
        return fl
    except Exception as e:
        print(e)
        return None


def getDL(p):
    # print(str(p))
    fl = []
    try:
        for pth, dirs, files in walk(p, topdown=True):
            if '.git' in pth:
                dirs = []
                break
            if '.git' in dirs:
                dirs.remove('.git')
            if '__pycache__' in dirs:
                dirs.remove('__pycache__')
            for d in dirs.copy():
                fl.append(Path(pth, d))
                dirs.remove(d)
            break
        return fl
    except Exception as e:
        print("getDL", e)
        return None


def getdll0():
    td = ppre('gd')
    #print('getdll0',td)
    cmd = 'rclone lsjson "' + str(td) + '" --recursive --files-only --hash'
    rc = ar.run1(cmd)
    if rc == 0:
        l1 = json.loads(ar.txt)

        def es(it):
            it1 = Path(it['Path'])
            it2 = it['Size']
            it3 = it['ModTime'][:-1] + '-00:00'
            it3 = datetime.datetime.fromisoformat(it3).timestamp()
            if 'Hashes' in it:
                it4 = bytes.fromhex(it['Hashes']['md5'])
            else:
                it4 = bytes()
            return DE(it1, it2, it3, it4)

        st = list(map(es, l1))
        st.sort()
        print(len(st), "de's")
        return st
    return None


def sepdlls(dlls):
    print("-sepdlls")
    for di in v.tdirs:
        if di.startswith('gd_'):
            v.RDlls[di] = []
            v.RDlls_xt[di] = time.time()
            v.RDlls_changed = True
            rd = tdir(di).relative_to(ppre('gd'))
            tds = str(rd) + '/'
            i = bisect_left(dlls, DE(tds, 0, 0, b''))
            # print(tds, i)
            if i == len(dlls):
                continue
            de = dlls[i]
            if not fnmatch(de.nm, tds + '*'):
                print('error')
                print(rd, tds, i, de.nm)
                # TODO: apply panic procedure
                continue
            while fnmatch(de.nm, tds + '*'):
                de2 = DE(de.nm, de.sz, de.mt, de.md5)
                # TODO: use Path
                de2.nm = de2.nm.relative_to(rd)
                # print(de2[0])
                #if de2 in csdlls[di]:
                #csdlls[di].remove(de2)
                v.RDlls[di].append(de2)
                i += 1
                if i == len(dlls):
                    break
                de = dlls[i]
    print(len(v.RDlls), 'rdlls')


def getdll1(di):
    td = tdir(di)
    #print('getdll1', di, str(td))
    cmd = 'rclone lsjson "' + str(
        td) + '" --recursive --files-only --hash --fast-list'
    # print(cmd)
    rc = ar.run1(cmd)
    if rc == 0:
        l1 = json.loads(ar.txt)

        def es(it):
            # TODO: use Path
            it1 = Path(it['Path'])
            it2 = it['Size']
            it3 = it['ModTime'][:-1] + '-00:00'
            it3 = datetime.datetime.fromisoformat(it3).timestamp()
            if 'Hashes' in it:
                it4 = bytes.fromhex(it['Hashes']['md5'])
            else:
                it4 = bytes()
            return DE(it1, it2, it3, it4)

        st = list(map(es, l1))
        st.sort()
        return st
    if rc == 3:
        return []
    return None


def getdll2(si):
    td = pdir(si)
    #print('getdll2', si, str(td))
    cmd = 'rclone lsjson "' + str(
        td) + '" --recursive --files-only --hash --fast-list'
    if not td.is_file():
        cmd += ' --exclude ".git/**" --exclude "__pycache__/**"'
    # print(cmd)
    rc = ar.run1(cmd)
    if rc == 0:
        l1 = json.loads(ar.txt)

        def es(it):
            # TODO: use Path
            it1 = Path(it['Path'])
            it2 = it['Size']
            it3 = it['ModTime'][:-7] + '-00:00'
            it3 = datetime.datetime.fromisoformat(it3).timestamp()
            if 'Hashes' in it:
                it4 = bytes.fromhex(it['Hashes']['md5'])
            else:
                it4 = bytes()
            return DE(it1, it2, it3, it4)

        st = list(map(es, l1))
        st.sort()
        return st
    if rc == 3:
        return []
    return None


def getdll3(si):
    sd = srcDir(si)
    #print('getdll3', si, str(sd))
    l1 = getfl(sd)

    def es(it):
        # TODO: use Path
        it1 = it.relative_to(sd)
        fs = it.stat()
        it2 = fs.st_size
        it3 = fs.st_mtime_ns
        it3 = trunc2ms(it3)
        it4 = fmd5f(it, it2, it3)
        return DE(it1, it2, it3, it4)

    st = list(map(es, l1))
    st.sort()
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
    #print('-ldlld', si)
    if si not in v.LDlls or v.LDlls_xt[si] + rto2 <= time.time():
        rv = getdll3(si)
        if rv is not None:
            #print(si, 'ldll obtained')
            v.LDlls[si] = rv
            v.LDlls_xt[si] = time.time()
            v.LDlls_changed = True
        return rv
    return v.LDlls[si]


def rDlld(di):
    #print('-rdlld', di)
    if di not in v.RDlls or v.RDlls_xt[di] + rto1 <= time.time():
        rv = getdll1(di)
        if rv is not None:
            #print(di, 'rdll obtained')
            v.RDlls[di] = rv
            v.RDlls_xt[di] = time.time()
            v.RDlls_changed = True
        return rv
    return v.RDlls[di]


def dllcmp(do, dn):
    dns = set(dn)
    dos = set(do)
    tocopy = dns - dos
    todelete = dos - dns
    return (todelete, tocopy)

from config_funcs import ppre, tdir, pdir, srcDir, trunc2ms
