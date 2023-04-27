import datetime
import time

import asyncrun as ar
import config as v
import ldsv as ls
from de import DE, FSe

dexs = {
    ".cargo",
    ".cache",
    ".git",
    "node_modules",
    "__pycache__",
    ".ropeproject",
    ".mypyproject",
    ".mypy_cache",
    ".vite",
    ".yarnclean",
    "storage",
}


def cull_DEs(des):
    des[:] = [
        de for de in des if not any([sd for sd in de.nm.parent.parts if sd in dexs])
    ]


def cull_files(files, pt):
    files[:] = [
        pt(f) for f in files if not any([sd for sd in f.parent.parts if sd in dexs])
    ]


def cull_dirs(dirs, pt):
    dirs[:] = [pt(d) for d in dirs if not isbaddir(pt(d))]


def isbaddir(dir):
    return dir in dexs



class FileList:
    def __new__(cls, sd, **kwargs):
        if sd.isremote:
            cls = RemoteFileList
        else:
            cls = LocalFileList
        self = object.__new__(cls)
        return self

    def __init__(self, sd):
        self.sd = sd
        super(FileList, self).__init__()


class LocalFileList(FileList):
    def __init__(self, sd, **kwargs):
        super(LocalFileList, self).__init__(sd)

    def getfl(self, sd):
        import config as v

        pt = type(sd)
        fl1 = []
        if sd.is_file():
            fl1.append(sd)
            return fl1
        if isbaddir(str(sd.name)):
            return fl1
        fdi = sd.iterdir()
        for it in fdi:
            if it.is_file():
                rp = pt(it)
                fl1.append(rp)
            else:
                if not isbaddir(str(it.name)):
                    rp = pt(it)
                    fl2 = self.getfl(rp)
                    fl1.extend(fl2)
        return fl1

    def getdll(self):  # local-source
        import config as v

        v.dl1_cs += 1
        # print('getdll3', si, str(sd))
        l1 = self.getfl(self.sd)

        def es(it):
            it1 = it.relative_to(self.sd)
            try:
                fs = it.stat()
                it2 = fs.st_size
                it3 = fs.st_mtime_ns
                it3 = v.ns_trunc2ms(it3)
            except FileNotFoundError as exc:
                print(exc)
                it2 = 0
                it3 = 0
            fse = FSe(it2, it3)
            return DE(it1, fse)

        st = list(map(es, l1))
        st.sort(key=lambda de: de.nm)
        return st


class RemoteFileList(FileList):
    def __init__(self, sd, **kwargs):
        super(RemoteFileList, self).__init__(sd, **kwargs)

    def getfl(self, sd):
        import json

        import config as v

        cmd = 'rclone lsjson "' + str(sd) + '" --recursive --files-only '
        rc = ar.run1(cmd)
        if rc == 0:
            return json.loads(ar.txt)
        if rc == 3:
            return []
        return None

    def getdll(self):  # remote-source
        import config as v

        v.dl2_cs += 1
        pt = type(self.sd)
        # print('getdll1', di, str(td))
        l1 = self.getfl(self.sd)
        if l1:

            def es(it: dict):
                # TODO: use Path
                it1 = pt(it["Path"])
                it2 = it["Size"]
                it3 = it["ModTime"][:-1] + "-00:00"
                it3 = datetime.datetime.fromisoformat(it3).timestamp()
                it3 = v.ts_trunc2ms(it3)
                fse = FSe(it2, it3)
                return DE(it1, fse)

            st = list(map(es, l1))
            st.sort(key=lambda de: de.nm)
            return st
        return None
