import datetime
import json
from os import walk

import asyncrun as ar
from de import DE
from fsmixin import FS_Mixin


class PFS_Mixin(FS_Mixin):
    def getfl(self):
        import config as v

        pt = type(self)
        # print(str(p))
        fl = []
        try:
            if self.is_file():
                fl.append(self)
                return fl
            for pth, dirs, files in walk(self, topdown=True):
                pth = pt(pth)
                if not v.isbaddir(pth):
                    v.proc_dirs(dirs, pt)
                    for f in files:
                        fl.append(pth / f)
                else:
                    dirs = []
                    files = []
            return fl
        except Exception as e:
            print(e)
        return fl

    def getdll(self):  # local-source
        import config as v
        from fmd5h import fmd5f

        v.dl3_cs += 1
        # print('getdll3', si, str(sd))
        l1 = self.getfl()

        def es(it):
            it1 = it.relative_to(self)
            fs = it.stat()
            it2 = fs.st_size
            it3 = fs.st_mtime_ns
            it3 = v.trunc2ms(it3)
            fp = self / it1
            fse = fmd5f(fp, it2, it3)
            return DE(it1, fse)

        st = list(map(es, l1))
        st.sort(key=lambda de: de.nm)
        return st
