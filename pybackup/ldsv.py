import pickle
from queue import Empty, SimpleQueue
from threading import RLock, Thread
from time import sleep

import config

# from snoop import snoop

dl = RLock()
sev = SimpleQueue()


def pstats():
    print("dl1_cs", config.dl1_cs)
    print("dl2_cs", config.dl2_cs)
    print("sfb", config.sfb)
    print("h_hits", config.h_hits)
    print("h_miss", config.h_miss)


def loadldlls():
    with dl:
        try:
            with open(config.ldllsf, "rb") as fh:
                td = pickle.load(fh)
                LDlls = td["ldlls"]
                LDlls_xt = td["ldlls_xt"]
        except IOError as e:
            print("loadldlls failed", e)
            return
        for si in config.srcs:
            if si in LDlls:
                config.LDlls[si] = LDlls[si]
                config.LDlls_xt[si] = LDlls_xt[si]
        for di in config.tgts:
            if di in LDlls:
                config.LDlls[di] = LDlls[di]
                config.LDlls_xt[di] = LDlls_xt[di]


def loadrdlls():
    with dl:
        try:
            with open(config.rdllsf, "rb") as fh:
                td = pickle.load(fh)
                RDlls = td["rdlls"]
                RDlls_xt = td["rdlls_xt"]
        except IOError as e:
            print("loadrdlls failed", e)
            return
        for si in config.srcs:
            if si in RDlls:
                config.RDlls[si] = RDlls[si]
                config.RDlls_xt[si] = RDlls_xt[si]
        for di in config.tgts:
            if di in RDlls:
                config.RDlls[di] = RDlls[di]
                config.RDlls_xt[di] = RDlls_xt[di]


def saveldlls():
    with dl:
        # print('-saveldlls')
        try:
            with open(config.ldllsf, "wb") as fh:
                td = {"ldlls": config.LDlls, "ldlls_xt": config.LDlls_xt}
                pickle.dump(td, fh)
                config.sfb += fh.tell()
        except IOError as e:
            print("savedlls failed", e)


def saverdlls():
    with dl:
        try:
            with open(config.rdllsf, "wb") as fh:
                td = {"rdlls": config.RDlls, "rdlls_xt": config.RDlls_xt}
                pickle.dump(td, fh)
                config.sfb += fh.tell()
        except IOError as e:
            print("saverdlls failed", e)


def loadedges():
    with dl:
        try:
            with open(config.edgepf, "rb") as fh:
                leDep = pickle.load(fh)
        except IOError as e:
            print("loadedges failed", e)
            return
        for e in config.eDep:
            for le in leDep:
                if le == e:
                    e.cdt = le.cdt
                    e.udt = le.udt
                    e.rcdt = le.rcdt
                    e.rudt = le.rudt


def saveedges():
    with dl:
        try:
            with open(config.edgepf, "wb") as fh:
                pickle.dump(config.eDep, fh)
                config.sfb += fh.tell()
        except IOError as e:
            print("saveedges failed", e)


def loadldh():
    with dl:
        try:
            with open(config.ldhpf, "rb") as fh:
                config.LDhd = pickle.load(fh)
        except IOError as e:
            print("loadldh failed", e)


def loadrdh():
    with dl:
        try:
            with open(config.rdhpf, "rb") as fh:
                config.RDhd = pickle.load(fh)
        except IOError as e:
            print("loadrdh failed", e)


def saveldh():
    with dl:
        try:
            with open(config.ldhpf, "wb") as fh:
                pickle.dump(config.LDhd, fh)
                config.sfb += fh.tell()
        except IOError as e:
            print("saveldh failed", e)


def saverdh():
    with dl:
        try:
            with open(config.rdhpf, "wb") as fh:
                pickle.dump(config.RDhd, fh)
                config.sfb += fh.tell()
        except IOError as e:
            print("saverdh failed", e)


def load_all():
    loadrdlls()
    # loadldlls()
    loadedges()
    loadldh()
    loadrdh()


def save_all():
    with dl:
        saverdlls()
        # saveldlls()
        saveedges()
        saveldh()
        saverdh()
        pstats()


def save_bp():
    def save_th():
        svs = {}
        while not config.quit_ev.is_set():
            try:
                qi = sev.get_nowait()
                try:
                    svs[qi] += 1
                except KeyError:
                    svs[qi] = 1
                continue
            except Empty:
                sleep(0.05)
        print("saves:", svs)
        for sv in svs:
            match sv:
                case "edges":
                    saveedges()
                case "ldlls":
                    saveldlls()
                case "rdlls":
                    saverdlls()
                case "ldhd":
                    saveldh()
                case "rdhd":
                    saverdh()
        pstats()

    th3 = Thread(target=save_th)
    return th3
