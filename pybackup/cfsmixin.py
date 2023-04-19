import datetime
import json

import asyncrun as ar
from de import DE, FSe
from fsmixin import FS_Mixin


class CFS_Mixin(FS_Mixin):
    def getfl(self):
        import config as v

        cmd = 'rclone lsjson "' + str(self) + '" --recursive --files-only '
        for ex in v.dexs:
            cmd += ' --exclude "**/' + ex + '/*" '
        rc = ar.run1(cmd)
        if rc == 0:
            return json.loads(ar.txt)
        if rc == 3:
            return []
        return None

    def getdll(self):  # remote-source
        import config as v

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
                it3 = v.ts_trunc2ms(it3)
                fse = FSe(it2, it3)
                return DE(it1, fse)

            st = list(map(es, l1))
            st.sort(key=lambda de: de.nm)
            return st
        return None
