import datetime
import os
from pathlib import Path

import asyncrun as ar
import config as v
from de import DE, FSe

dexs = {
    ".cargo",
    ".cache",
    ".git",
    "node_modules",
    "__pycache__",
    ".ropeproject",
    ".ruff_cache",
    ".mypyproject",
    ".mypy_cache",
    ".vite",
    ".yarnclean",
    "storage",
}


def cull_DEs(des):
    des[:] = [
        de for de in des if not any([sd for sd in de.nm.parent.parts if sd in v.dexs])
    ]


def cull_files(files, pt):
    files[:] = [
        pt(f) for f in files if not any([sd for sd in f.parent.parts if sd in v.dexs])
    ]


def cull_dirs(dirs, pt):
    dirs[:] = [pt(d) for d in dirs if not isbaddir(pt(d))]


def isbaddir(dir):
    return dir in v.dexs or dir in dexs


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

    def getfl_str_fp(self, fp: str):
        from queue import Queue
        q = Queue()
        q.put(fp)
        
        fl1 = []
        while not q.empty():
            fp2 = q.get()
            with os.scandir(fp2) as di:
                for it1 in di:
                    if it1.is_file():
                        fl1.append(it1)
                    elif not it1.is_symlink():
                        if not isbaddir(it1.name):
                            q.put(it1.path)
        return fl1

    def getfl(self):
        return self.getfl_str_fp(str(self.sd))

    def getdll(self):  # local-source
        import config as v

        v.dl1_cs += 1
        l1 = self.getfl()
        st = []
        for it in l1:
            it1 = Path(it.path).relative_to(self.sd)
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
            st.append(DE(it1, fse))
        st.sort(key=lambda de: de.nm)
        return st


class RemoteFileList(FileList):
    def __init__(self, sd, **kwargs):
        super(RemoteFileList, self).__init__(sd, **kwargs)

    def getfl(self, sd):
        import json

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
        pt = Path
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


if __name__ == "__main__":
    pass
