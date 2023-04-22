from pathlib import Path, PosixPath


class SD(PosixPath):
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls, *args)

    def __init__(self, *args, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.SDh = None

    def sdh_f(self, dh=None):
        odh = self.SDh
        if dh is not None:
            self.SDh = dh
        return odh

    def sdhset(self, Dh=None):
        if Dh is None:
            Dh = self.sdh_d()
        if Dh is not None:
            self.sdh_f(Dh)

    def sdhck(self):
        Dh1 = self.sdh_f()
        Dh2 = self.sdh_d()
        if Dh2 is not None:
            return (Dh2, Dh1 != Dh2)
        return (None, False)


class Local_Mixin():
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def isremote(self):
        return False

class Remote_Mixin():
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def isremote(self):
        return True

class FS_Mixin(SD):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.Dll = None
        self.Dll_xt = 0.0
        self.Dll_changed = False


    def sdh_d(self):
        from bhash import blakeHash

        Si_dl = self.Dlld()
        if Si_dl is not None:
            return blakeHash(Si_dl)
        return None

    def Dlld(self):
        p = self
        # print('-ldlld', si)
        if self.isremote:
            ch = "r"
        else:
            ch = "l"
        if self.Dll is None or (self.isremote and self.Dll_xt + rto1 <= time.time()):
            print("sucking/scanning for", self.tag, ch + "dll...", end="")
            rv = self.getdll()
            if rv is not None:
                print("done.")
                self.Dll = rv
                self.Dll_xt = time.time()
                self.Dll_changed = True
            else:
                print("failed.")
                pass
        else:
            print("fetched", self.tag, ch + "dll from cache.")
            pass
        return self.Dll

class CFS_Mixin(FS_Mixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def getfl(self):
        import config as v

        cmd = 'rclone lsjson "' + str(self) + '" --recursive --files-only '
        rc = ar.run1(cmd)
        if rc == 0:
            return json.loads(ar.txt)
        if rc == 3:
            return []
        return None

    def getdll(self):  # remote-source
        import config as v

        v.dl2_cs += 1
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


class CS(CFS_Mixin, Remote_Mixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class PFS_Mixin(FS_Mixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def getfl(self):
        import config as v

        pt = type(self)
        fl = []
        if self.is_file():
            fl.append(self)
            return fl
        wl = self.rglob("*")
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
            it1 = it.relative_to(self)
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

class Ext3(PFS_Mixin, Local_Mixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Fat32(PFS_Mixin, Local_Mixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
