#!/data/data/com.termux/files/usr/bin/env python


from os import walk
from pathlib import Path

import config as v
import ldsv
import status as st
from inotify_simple import flags
from opexec import clean, opExec
from status import onestatus

wdsi = {}
in1 = None
cel = None


async def wsetup():
    global wdsi, in1
    for si in v.srcs:
        try:
            p = v.src(si)
            rv = in1.add_watch(str(p), flags.MODIFY)
            # asyncio.sleep(0)
            wdsi[rv] = (si, p)
            if not p.is_file():
                for pth, dirs, files in walk(p, topdown=True):
                    if ".git" in pth:
                        dirs = []
                        break
                    if ".git" in dirs:
                        dirs.remove(".git")
                    if "__pycache__" in dirs:
                        dirs.remove("__pycache__")
                    for d in dirs:
                        cp = Path(pth, d)
                        rv = in1.add_watch(str(cp), flags.MODIFY)
                        wdsi[rv] = (si, cp)
                        # asyncio.sleep(0)
        except Exception as e:
            print(e)
    # for k,v in wdsi.items():
    # print(v[0],str(v[1]))
    print(len(wdsi), "watches")


tr = 0


async def cb1():
    global tr, in1
    sis = set()
    evs = await in1.read(1000, 1000)
    for ev in evs:
        # print(ev)
        si = wdsi[ev.wd][0]
        if si != "git":
            if si not in sis:
                sis.add(si)
                if si in v.srcs:
                    print("cb1 onestatus", si)
                    onestatus(si)
    tr -= 1


def cb2():
    global tr, cel
    if not tr:
        tr += 1
        cel.create_task(cb1())


ct1 = None


def rt2():
    itc = 0
    rv1 = False
    while True:
        itc += 1
        cl = clean()
        if cl:
            print("backups appear done")
            rv1 = False
            print("rv1", rv1)
        else:
            print("backups appear pending")
            rv1 = opExec()
            print("rv1", rv1)
        if not rv1:
            break
    ldsv.save_all()


def main():
    print("-main")
    v.initConfig()
    st.updatets(0)
    # dl.getrdlls()
    rt2()


if __name__ == "__main__":
    main()
