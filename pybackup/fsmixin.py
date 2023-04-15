import time

rto1 = 60 * 15
rto2 = 60 * 15


class FS_Mixin:
    Dll = None
    Dll_xt = 0.0
    Dll_changed = False

    def sdh_d(self):
        from bhash import blakeHash

        Si_dl = self.Dlld()
        if Si_dl is not None:
            return blakeHash(Si_dl)
        return None

    def Dlld(self):
        p = self
        # print('-ldlld', si)
        if p.isremote:
            ch = "r"
        else:
            ch = "l"
        if p.Dll is None:  # or p.Dll_xt + rto1 <= time.time():
            print("obtaining", self.tag, ch + "dll...", end="")
            rv = p.getdll()
            if rv is not None:
                print("done.")
                p.Dll = rv
                p.Dll_xt = time.time()
                p.Dll_changed = True
            else:
                print("failed.")
        else:
            print("retrieved", self.tag, ch + "dll.")
        return p.Dll
