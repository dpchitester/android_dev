import config_vars as v
from bhash import blakeHash
from dirlist import lDlld, rDlld
import ldsv

def ldh_f(Si, dh=None):
    if Si not in v.LDhd:
        v.LDhd[Si] = None
    odh = v.LDhd[Si]
    if dh is not None:
        v.LDhd[Si] = dh
    return odh


def rdh_f(Di, dh=None):
    if Di not in v.RDhd:
        v.RDhd[Di] = None
    odh = v.RDhd[Di]
    if dh is not None:
        v.RDhd[Di] = dh
    return odh


def ldh_d(Si):
    Si_dl = lDlld(Si)
    if Si_dl is not None:
        return blakeHash(Si_dl)
    return None


def rdh_d(Di):
    Di_dl = rDlld(Di)
    if Di_dl is not None:
        return blakeHash(Di_dl)
    return None


def ldhset(Si, Dh=None):
    if Dh is None:
        Dh = ldh_d(Si)
    if Dh is not None:
        ldh_f(Si, Dh)
        ldsv.saveldh()


def rdhset(Di, Dh=None):
    if Dh is None:
        Dh = rdh_d(Di)
    if Dh is not None:
        rdh_f(Di, Dh)
        ldsv.saverdh()


def ldhck(Si):
    Dh1 = ldh_f(Si)
    Dh2 = ldh_d(Si)
    if Dh2 is not None:
        return (Dh2, Dh1 != Dh2)
    return (None, False)


def rdhck(Di):
    Dh1 = rdh_f(Di)
    Dh2 = rdh_d(Di)
    if Dh2 is not None:
        return (Dh2, Dh1 != Dh2)
    return (None, False)
