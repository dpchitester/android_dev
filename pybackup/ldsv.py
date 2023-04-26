import pickle
from threading import Thread, RLock, Event
from queue import SimpleQueue, Empty

from snoop import snoop

dl = RLock()
sev = SimpleQueue()

def loadldlls():
    import config as v
    with dl:
        try:
            with open(v.ldllsf, "rb") as fh:
                td = pickle.load(fh)
                v.LDlls = td["ldlls"]
                v.LDlls_xt = td["ldlls_xt"]
        except IOError as e:
            print("loadldlls failed", e)


def loadrdlls():
    import config as v
    with dl:
        try:
            with open(v.rdllsf, "rb") as fh:
                td = pickle.load(fh)
                v.RDlls = td["rdlls"]
                v.RDlls_xt = td["rdlls_xt"]
        except IOError as e:
            print("loadrdlls failed", e)


def saveldlls():
    import config as v
    with dl:
    # print('-saveldlls')
        if v.LDlls_changed:
            print("LDlls changed")
        try:
            with open(v.ldllsf, "wb") as fh:
                td = {"ldlls": v.LDlls, "ldlls_xt": v.LDlls_xt}
                pickle.dump(td, fh)
                v.LDlls_changed = False
        except IOError as e:
            print("savedlls failed", e)


def saverdlls():
    import config as v
    with dl:
        if v.RDlls_changed:
            print("RDlls changed")
        try:
            with open(v.rdllsf, "wb") as fh:
                td = {"rdlls": v.RDlls, "rdlls_xt": v.RDlls_xt}
                pickle.dump(td, fh)
                v.RDlls_changed = False
        except IOError as e:
            print("saverdlls failed", e)


def loadedges():
    import config as v
    with dl:
        try:
            with open(v.edgepf, "rb") as fh:
                v.eDep = pickle.load(fh)
        except IOError as e:
            print("loadedges failed", e)


def saveedges():
    import config as v
    with dl:
        try:
            with open(v.edgepf, "wb") as fh:
                pickle.dump(v.eDep, fh)
        except IOError as e:
            print("saveedges failed", e)


def pstats():
    import config as v

    print("dl1_cs", v.dl1_cs)
    print("dl2_cs", v.dl2_cs)
    print("sfb", v.sfb)


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
        except IOError as e:
            print("saveldh failed", e)


def saverdh():
    import config as v
    with dl:
        try:
            with open(v.rdhpf, "wb") as fh:
                pickle.dump(v.RDhd, fh)
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
    import pybackup as pb
    def save_th():
        def chk_save():
            try:
                qi = sev.get(timeout=3)
                if qi is not None:
                    # print("save", qi)
                    match qi:
                        case "edges":
                            saveedges()
                        case "ldlls":
                            saveldlls()
                        case "rdlls":
                            saverdlls()
                        case "ldh":
                            saveldh()
                        case "rdh":
                            saverdh()
            except Empty:
                pass
        with snoop(depth=2):
            while True:
                chk_save()
                if pb.quit_ev.is_set():
                    return
    th3 = Thread(target=save_th)
    return th3
