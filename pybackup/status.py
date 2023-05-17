from threading import Thread

import config
import ldsv as ls


def stsupdate(Si, Dh):
    # print(Si, end=' ')
    print(Si, end=" ")
    # N1 = config.srcts[Si]
    for e in [e for e in config.eDep if e.si == Si]:
        e.rtset()
    config.src(Si).sdhset(Dh)


def onestatus(Si):
    # TODO: update as per src_statuses
    with ls.dl:
        tr = config.src(Si).sdhck()
        if tr is not None:
            (Dh, changed) = tr
            if changed:
                stsupdate(Si, Dh)
                print()


def src_statuses():
    SDl = []
    with ls.dl:
        for Si in config.srcs:
            # print('calling lckers', Si)
            tr = config.src(Si).sdhck()
            if tr is not None:
                (Dh, changed) = tr
                if changed:
                    SDl.append((Si, Dh))
    return SDl


def src_statuses2():
    thl = []
    SDl = []
    for Si in config.srcs:

        def f1(Si):
            # print('calling lckers', Si)
            tr = config.src(Si).sdhck()
            if tr is not None:
                (Dh, changed) = tr
                if changed:
                    SDl.append((Si, Dh))

        th = Thread(target=f1, args=(Si,))
        th.start()
        thl.append(th)
        print(th)
    while len(thl):
        th = thl.pop()
        if th.is_alive():
            th.join()
        print(th)
    return SDl


def updatets(N):
    print("Status", N)
    Sl = src_statuses2()
    if len(Sl):
        print("changed: ", end="")
        for Si, Dh in Sl:
            stsupdate(Si, Dh)
        print()


if __name__ == "__main__":
    config.initConfig()
    updatets(1)
    ls.saveedges()
