import os
import pickle
from pathlib import Path

def prep_save():
    import config as v
    v.LDlls = {}
    v.LDlls_xt = {}
    v.LDhd = {}
    v.RDlls = {}
    v.RDlls_xt = {}
    v.RDhd = {}
    for si in v.srcs:
        pth = v.src(si)
        if not pth.isremote:
            if pth.Dll:
                v.LDlls[si] = pth.Dll
                v.LDlls_xt[si] = pth.Dll_xt
                v.LDlls_changed |= pth.Dll_changed
            v.LDhd[si] = pth.SDh
        else:
            if pth.Dll:
                v.RDlls[si] = pth.Dll
                v.RDlls_xt[si] = pth.Dll_xt
                v.RDlls_changed |= pth.Dll_changed
            v.RDhd[si] = pth.SDh
    for di in v.tgts:
        pth = v.tgt(di)
        if not pth.isremote:
            if pth.Dll:
                v.LDlls[di] = pth.Dll
                v.LDlls_xt[di] = pth.Dll_xt
                v.LDlls_changed |= pth.Dll_changed
            v.LDhd[di] = pth.SDh
        else:
            if pth.Dll:
                v.RDlls[di] = pth.Dll
                v.RDlls_xt[di] = pth.Dll_xt
                v.RDlls_changed |= pth.Dll_changed
            v.RDhd[di] = pth.SDh

def after_load():
    import config as v
    for si in v.srcs:
        pth = v.src(si)
        if not pth.isremote:
            if si in v.LDlls:
                pth.Dll = v.LDlls[si]
                pth.Dll_xt = v.LDlls_xt[si]
                pth.SDh = v.LDhd[si]
        else:
            if si in v.RDlls:
                pth.Dll = v.RDlls[si]
                pth.Dlls_xt = v.RDlls_xt[si]
                pth.SDh = v.RDhd[si]
    for di in v.tgts:
        pth = v.tgt(di)
        if not pth.isremote:
            if di in v.LDlls:
                pth.Dll = v.LDlls[di]
                pth.Dll_xt = v.LDlls_xt[di]
                pth.SDh = v.LDhd[di]
        else:
            if di in v.RDlls:
                pth.Dll = v.RDlls[di]
                pth.Dll_xt = v.RDlls_xt[di]
                pth.SDh = v.RDhd[di]

    
def loadldlls():
    import config as v

    try:
        with open(v.ldllsf, "rb") as fh:
            td = pickle.load(fh)
            v.LDlls = td["ldlls"]
            v.LDlls_xt = td["ldlls_xt"]
    except Exception as e:
        print("loadldlls failed", e)


def loadrdlls():
    import config as v

    try:
        with open(v.rdllsf, "rb") as fh:
            td = pickle.load(fh)
            v.RDlls = td["rdlls"]
            v.RDlls_xt = td["rdlls_xt"]
    except Exception as e:
        print("loadrdlls failed", e)


def saveldlls():
    import config as v

    # print('-saveldlls')
    if v.LDlls_changed:
        try:
            with open(v.ldllsf, "wb") as fh:
                td = {"ldlls": v.LDlls, "ldlls_xt": v.LDlls_xt}
                pickle.dump(td, fh)
                v.SDlls_changed = False
        except Exception as e:
            print("savedlls failed", e)


def saverdlls():
    import config as v

    # print('-saverdlls')
    if v.RDlls_changed:
        try:
            with open(v.rdllsf, "wb") as fh:
                td = {"rdlls": v.RDlls, "rdlls_xt": v.RDlls_xt}
                pickle.dump(td, fh)
                v.RDlls_changed = False
        except Exception as e:
            print("saverdlls failed", e)


def loadedges():
    import config as v

    try:
        with open(v.edgepf, "rb") as fh:
            v.eDep = pickle.load(fh)
    except Exception as e:
        print("loadedges failed", e)


def saveedges():
    import config as v

    # print("-saveedges")
    try:
        with open(v.edgepf, "wb") as fh:
            pickle.dump(v.eDep, fh)
    except Exception as e:
        print("saveedges failed", e)


def loadfmd5h():
    import config as v

    try:
        with open(v.fmd5hf, "rb") as fh:
            v.fmd5hd = pickle.load(fh)
    except Exception as e:
        print("loadfmd5h failed", e)


def pstats():
    import config as v

    print("hash-dict name hit", v.hf_dh)
    print("hash-dict name miss", v.hf_dm)
    print("hash-dict sz-mt hit", v.hf_sth)
    print("hash-dict sz-mt miss", v.hf_stm)
    print("sfb", v.sfb)
    print("dl0_cs", v.dl0_cs)
    print("dl1_cs", v.dl1_cs)
    print("dl2_cs", v.dl2_cs)
    print("dl3_cs", v.dl3_cs)
    print("dl4_cs", v.dl4_cs)
    print("dl5_cs", v.dl5_cs)


def savefmd5h():
    import config as v

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
    import config as v

    try:
        with open(v.ldhpf, "rb") as fh:
            v.LDhd = pickle.load(fh)
    except Exception as e:
        print("loadldh failed", e)


def loadrdh():
    import config as v

    try:
        with open(v.rdhpf, "rb") as fh:
            v.RDhd = pickle.load(fh)
    except Exception as e:
        print("loadrdh failed", e)


def saveldh():
    import config as v

    try:
        with open(v.ldhpf, "wb") as fh:
            pickle.dump(v.LDhd, fh)
    except Exception as e:
        print("saveldh failed", e)


def saverdh():
    import config as v

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
    after_load()

def save_all():
    prep_save()
    saverdlls()
    saveldlls()
    saveedges()
    savefmd5h()
    saveldh()
    saverdh()
