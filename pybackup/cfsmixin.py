import datetime
import json

import asyncrun as ar
from de import DE
from fsmixin import FS_Mixin


class CFS_Mixin(FS_Mixin):
    def getfl(self):
        import config as v

        cmd = 'rclone lsjson "' + str(self) + '" --recursive --files-only --hash '
        for ex in v.dexs:
            cmd += ' --exclude "**/' + ex + '/*" '
        rc = ar.run1(cmd)
        if rc == 0:
            l1 = json.loads(ar.txt)
            return l1
        if rc == 3:
            return []
        return None

    def getdll(self):  # remote-source
        import config as v
        from fmd5h import fmd5f

        v.dl5_cs += 1
        pt = type(self)
        # print('getdll1', di, str(td))
        l1 = self.getfl()
        if l1:

            def es(it: dict):
                # TODO: use Path
                it1 = pt(it["Path"])
                it2 = it["Size"]
                it3 = it["ModTime"][:-1] + "-00:00"
                it3 = datetime.datetime.fromisoformat(it3).timestamp()
                if "Hashes" in it:
                    it4 = bytes.fromhex(it["Hashes"]["md5"])
                else:
                    it4 = bytes()
                fp = self / it1
                fse = fmd5f(fp, it2, it3, it4)
                return DE(it1, fse)

            st = list(map(es, l1))
            st.sort(key=lambda de: de.nm)
            return st
        return None
