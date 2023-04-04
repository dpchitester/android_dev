from pathlib import Path
import pickle
import os


def loadldlls():
    import config_vars as v
    try:
        with open(v.ldllsf, "rb") as fh:
            td = pickle.load(fh)
            v.LDlls = td['ldlls']
            v.LDlls_xt = td['ldlls_xt']
    except Exception as e:
        print("loadldlls failed", e)


def loadrdlls():
    import config_vars as v
    try:
        with open(v.rdllsf, "rb") as fh:
            td = pickle.load(fh)
            v.RDlls = td['rdlls']
            v.RDlls_xt = td['rdlls_xt']
    except Exception as e:
        print("loadrdlls failed", e)


def saveldlls():
    # print('-saveldlls')
    import config_vars as v
    if v.LDlls_changed:
        try:
            with open(v.ldllsf, "wb") as fh:
                td = {"ldlls": v.LDlls, "ldlls_xt": v.LDlls_xt}
                pickle.dump(td, fh)
                v.LDlls_changed = False
        except Exception as e:
            print("savedlls failed", e)


def saverdlls():
    # print('-saverdlls')
    import config_vars as v
    if v.RDlls_changed:
        try:
            with open(v.rdllsf, "wb") as fh:
                td = {"rdlls": v.RDlls, "rdlls_xt": v.RDlls_xt}
                pickle.dump(td, fh)
                v.RDlls_changed = False
        except Exception as e:
            print("saverdlls failed", e)


def loadedges():
    import config_vars as v
    try:
        with open(v.edgepf, "rb") as fh:
            v.eDep = pickle.load(fh)
    except Exception as e:
        print("loadedges failed", e)


def saveedges():
    import config_vars as v
    #print("-saveedges")
    try:
        with open(v.edgepf, "wb") as fh:
            pickle.dump(v.eDep, fh)
    except Exception as e:
        print("saveedges failed", e)


def loadfmd5h():
    import config_vars as v
    try:
        with open(v.fmd5hf, "rb") as fh:
            v.fmd5hd = pickle.load(fh)
    except Exception as e:
        print("loadfmd5h failed", e)


def pstats():
    import config_vars as v
    print('fp miss', v.hf_dm)
    print('fp hit', v.hf_dh)
    print('szmt miss', v.hf_stm)
    print('szmt hit', v.hf_sth)
    print('sfb', v.sfb)


def savefmd5h():
    import config_vars as v
    if v.hf_dirty:
        try:
            with open(v.fmd5hf, "wb") as fh:
                pickle.dump(v.fmd5hd, fh)
            v.sfb += v.fmd5hf.stat().st_size
            pstats()
            v.hf_dirty = False
        except Exception as e:
            print("savefmd5h failed", e)


def loadldh():
    import config_vars as v
    try:
        with open(v.ldhpf, "rb") as fh:
            v.LDhd = pickle.load(fh)
    except Exception as e:
        print("loadldh failed", e)


def loadrdh():
    import config_vars as v
    try:
        with open(v.rdhpf, "rb") as fh:
            v.RDhd = pickle.load(fh)
    except Exception as e:
        print("loadrdh failed", e)


def saveldh():
    import config_vars as v
    try:
        with open(v.ldhpf, "wb") as fh:
            pickle.dump(v.LDhd, fh)
    except Exception as e:
        print("saveldh failed", e)


def saverdh():
    import config_vars as v
    try:
        with open(v.rdhpf, "wb") as fh:
            pickle.dump(v.RDhd, fh)
    except Exception as e:
        print("saverdh failed", e)


def load_all():
    loadrdlls()
    loadldlls()
    loadedges()
    loadfmd5h()
    loadldh()
    loadrdh()


def save_all():
    saverdlls()
    saveldlls()
    saveedges()
    savefmd5h()
    saveldh()
    saverdh()
