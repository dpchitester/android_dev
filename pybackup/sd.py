from pathlib import Path, PosixPath

from cfsmixin import CFS_Mixin
from pfsmixin import PFS_Mixin


class SD(PosixPath):
    _flavour = type(Path())._flavour
    tag = None
    issrc = None
    istgt = None
    SDh = None

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


class Local(SD):
    _flavour = type(Path())._flavour
    isremote = False


class Remote(SD):
    _flavour = type(Path())._flavour
    isremote = True


class Ext3(Local, PFS_Mixin):
    _flavour = type(Path())._flavour


class Fat32(Local, PFS_Mixin):
    _flavour = type(Path())._flavour


class CS(Remote, CFS_Mixin):
    _flavour = type(Path())._flavour
