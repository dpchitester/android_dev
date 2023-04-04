def ldh_f(si, dh=None):
    import config_vars as v
    if si not in v.LDhd:
        v.LDhd[si] = None
    odh = v.LDhd[si]
    if dh is not None:
        v.LDhd[si] = dh
    return odh


def rdh_f(di, dh=None):
    import config_vars as v
    if di not in v.RDhd:
        v.RDhd[di] = None
    odh = v.RDhd[di]
    if dh is not None:
        v.RDhd[di] = dh
    return odh


def ldh_d(si):
    from bhash import blakeHash
    from dirlist import lDlld
    si_dl = lDlld(si)
    if si_dl is not None:
        return blakeHash(si_dl)
    return None


def rdh_d(di):
    from bhash import blakeHash
    from dirlist import rDlld
    di_dl = rDlld(di)
    if di_dl is not None:
        return blakeHash(di_dl)
    return None


def ldhset(Si, Dh=None):
    import ldsv
    if Dh is None:
        Dh = ldh_d(Si)
    if Dh is not None:
        ldh_f(Si, Dh)
        ldsv.saveldh()


def rdhset(Di, Dh=None):
    import ldsv
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
