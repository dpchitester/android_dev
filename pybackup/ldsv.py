import pickle
from queue import Empty, SimpleQueue
from threading import Event, RLock, Thread
from time import sleep

from snoop import snoop

dl = RLock()
sev = SimpleQueue()


def pstats():
    import config as v

    print("dl1_cs", v.dl1_cs)
    print("dl2_cs", v.dl2_cs)
    print("sfb", v.sfb)


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
                v.eDep = pickle.load(fh)
        except IOError as e:
            print("loadedges failed", e)


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

        def chk_sq():
            try:
                qi = sev.get_nowait()
                try:
                    svs[qi] += 1
                except KeyError:
                    svs[qi] = 1
            except Empty:
                pass
            return not sev.empty()

        while True:
            while chk_sq():
                pass
            if v.quit_ev.is_set():
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
                return
            else:
                sleep(2)

    th3 = Thread(target=save_th)
    return th3
