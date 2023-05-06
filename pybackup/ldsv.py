import pickle
from queue import Empty
from queue import SimpleQueue
from threading import Event
from threading import RLock
from threading import Thread
from time import sleep

# from snoop import snoop

dl = RLock()
sev = SimpleQueue()


def pstats():
    import config as v

    print("dl1_cs", v.dl1_cs)
    print("dl2_cs", v.dl2_cs)
    print("sfb", v.sfb)
    print("h_hits", v.h_hits)
    print("h_miss", v.h_miss)


def loadldlls():
    import config as v

    with dl:
        try:
            with open(v.ldllsf, "rb") as fh:
                td = pickle.load(fh)
                LDlls = td["ldlls"]
                LDlls_xt = td["ldlls_xt"]
        except IOError as e:
            print("loadldlls failed", e)
            return
        for si in v.srcs:
            if si in LDlls:
                v.LDlls[si] = LDlls[si]
                v.LDlls_xt[si] = LDlls_xt[si]
        for di in v.tgts:
            if di in LDlls:
                v.LDlls[di] = LDlls[di]
                v.LDlls_xt[di] = LDlls_xt[di]


def loadrdlls():
    import config as v

    with dl:
        try:
            with open(v.rdllsf, "rb") as fh:
                td = pickle.load(fh)
                RDlls = td["rdlls"]
                RDlls_xt = td["rdlls_xt"]
        except IOError as e:
            print("loadrdlls failed", e)
            return
        for si in v.srcs:
            if si in RDlls:
                v.RDlls[si] = RDlls[si]
                v.RDlls_xt[si] = RDlls_xt[si]
        for di in v.tgts:
            if di in RDlls:
                v.RDlls[di] = RDlls[di]
                v.RDlls_xt[di] = RDlls_xt[di]

def saveldlls():
    import config as v

    with dl:
        # print('-saveldlls')
        try:
            with open(v.ldllsf, "wb") as fh:
                td = {"ldlls": v.LDlls, "ldlls_xt": v.LDlls_xt}
                pickle.dump(td, fh)
                v.sfb += fh.tell()
        except IOError as e:
            print("savedlls failed", e)


def saverdlls():
    import config as v

    with dl:
        try:
            with open(v.rdllsf, "wb") as fh:
                td = {"rdlls": v.RDlls, "rdlls_xt": v.RDlls_xt}
                pickle.dump(td, fh)
                v.sfb += fh.tell()
        except IOError as e:
            print("saverdlls failed", e)


def loadedges():
    import config as v

    with dl:
        try:
            with open(v.edgepf, "rb") as fh:
                leDep = pickle.load(fh)
        except IOError as e:
            print("loadedges failed", e)
            return
        for e in v.eDep:
            for le in leDep:
                if le == e:
                    e.cdt = le.cdt
                    e.udt = le.udt
                    e.rcdt = le.rcdt
                    e.rudt = le.rudt


def saveedges():
    import config as v

    with dl:
        try:
            with open(v.edgepf, "wb") as fh:
                pickle.dump(v.eDep, fh)
                v.sfb += fh.tell()
        except IOError as e:
            print("saveedges failed", e)


def loadldh():
    import config as v

    with dl:
        try:
            with open(v.ldhpf, "rb") as fh:
                v.LDhd = pickle.load(fh)
        except IOError as e:
            print("loadldh failed", e)


def loadrdh():
    import config as v

    with dl:
        try:
            with open(v.rdhpf, "rb") as fh:
                v.RDhd = pickle.load(fh)
        except IOError as e:
            print("loadrdh failed", e)


def saveldh():
    import config as v

    with dl:
        try:
            with open(v.ldhpf, "wb") as fh:
                pickle.dump(v.LDhd, fh)
                v.sfb += fh.tell()
        except IOError as e:
            print("saveldh failed", e)


def saverdh():
    import config as v

    with dl:
        try:
            with open(v.rdhpf, "wb") as fh:
                pickle.dump(v.RDhd, fh)
                v.sfb += fh.tell()
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
    import config as v

    def save_th():
        svs = {}
        while not v.quit_ev.is_set():
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
