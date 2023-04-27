class FileList:
    def __new__(cls, sd, **kwargs):
        if sd.isremote:
            cls = RemoteFileList
        else:
            cls = LocalFileList
        self = object.__new__(cls)
        return self

    def __init__(self, sd, **kwargs):
        self._sd = sd
        super(FileList, self).__init__()


class LocalFileList(FileList):
    def __init__(self, sd, **kwargs):
        super(LocalFileList, self).__init__(*args, **kwargs)

    def getfl(self):
        import config as v

        pt = type(self._sd)
        fl = []
        if self._sd.is_file():
            fl.append(self._sd)
            return fl
        wl = self._sd.rglob("*")
        for it in wl:
            if it.is_file():
                rp = pt(it)
                fl.append(rp)
        return fl

    def getdll(self):  # local-source
        import config as v

        v.dl1_cs += 1
        # print('getdll3', si, str(sd))
        l1 = self.getfl()

        def es(it):
            it1 = it.relative_to(self._sd)
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
    def __init__(self, sd, *args, **kwargs):
        super(RemoteFileList, self).__init__(*args, **kwargs)

    def getfl(self):
        import json

        import config as v

        cmd = 'rclone lsjson "' + str(self._sd) + '" --recursive --files-only '
        rc = ar.run1(cmd)
        if rc == 0:
            return json.loads(ar.txt)
        if rc == 3:
            return []
        return None

    def getdll(self):  # remote-source
        import config as v

        v.dl2_cs += 1
        pt = type(self._sd)
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
