import config as v
import ldsv as ls


def stsupdate(Si, Dh):
    # print(Si, end=' ')
    print(Si, end=" ")
    # N1 = v.srcts[Si]
    for e in [e for e in v.eDep if e.si == Si]:
        e.rtset()
    v.src(Si).sdhset(Dh)


def onestatus(Si):
    # TODO: update as per src_statuses
    with ls.dl:
        tr = v.src(Si).sdhck()
        if tr is not None:
            (Dh, changed) = tr
            if changed:
                stsupdate(Si, Dh)
                print()


def src_statuses():
    SDl = []
    with ls.dl:
        for Si in v.srcs:
            # print('calling lckers', Si)
            tr = v.src(Si).sdhck()
            if tr is not None:
                (Dh, changed) = tr
                if changed:
                    SDl.append((Si, Dh))
    return SDl


def updatets(N):
    print("Status", N)
    Sl = src_statuses()
    if len(Sl):
        print("changed: ", end="")
        for Si, Dh in Sl:
            stsupdate(Si, Dh)
        print()
