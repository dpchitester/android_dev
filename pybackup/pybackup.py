#!/data/data/com.termux/files/usr/bin/env python
import asyncio
from os import environ, walk
from pathlib import Path
import multiprocessing as mp
import time

import config as v
import ldsv
import status as st

from asyncinotify import Inotify, Mask, Event, Watch
from findde import updateDEs
from fsmixin import FS_Mixin
from netup import netup
from opexec import clean, opExec

from status import onestatus, updatets

wdsi: dict[Watch, tuple[str, FS_Mixin]] = {}
sis: dict[v.NodeTag, list[str]] = {}
in1 = None
cel = None
cb1t = None
tr1 = 0


def wsetup():
    global wdsi, in1, v
    print("-wsetup")
    for si in v.srcs:
        try:
            p = v.src(si)
            pt = type(p)
            if p.is_dir() and not v.isbaddir(p) and isinstance(p, FS_Mixin):
                # TODO: not up to date
                for pth, dirs, files in walk(p, topdown=True):
                    pth = pt(pth)
                    v.proc_dirs(dirs, pt)
                    wa: Watch = in1.add_watch(pth, Mask.ACCESS | Mask.MODIFY | Mask.ATTRIB | Mask.CLOSE_WRITE | Mask.CLOSE_NOWRITE | Mask.OPEN | Mask.MOVED_FROM | Mask.MOVED_TO | Mask.CREATE | Mask.DELETE | Mask.DELETE_SELF | Mask.MOVE_SELF)
                    wdsi[wa] = si
        except Exception as e:
            print(e)
    print(len(wdsi), "watches")


def rt2():
    print("-rt2-1")
    itc = 0
    while True:
        itc += 1
        print("-rt2-2")
        cl = clean()
        if cl:
            print("-rt2-3")
            print("no backups appear pending")
            rv1 = False
            ldsv.save_all()
            break
        else:
            print("-rt2-4")
            print("backups appear pending")
            rv1 = opExec()
            ldsv.save_all()
            print("-rt2-5")
        asyncio.sleep(0)
        proc_events()
        print("-rt2-6")


async def cb1():
    global tr1, in1, v, sis
    print("-cb1-1")

    try:
        async for ev in in1:
            print("-cb1-2")
            si = wdsi[ev.watch]
            print("-cb1-3")
            p = ev.path
            if p.is_file():
                p = ev.path.parent
                print("-cb1-4")
                fn = ev.name
                print("-cb1-5")
                rp = p.relative_to(v.src(si))
                rfn = rp / fn
                print("-cb1-6")
                if si not in sis:
                    print("-cb1-7")
                    sis[si] = []
                if fn not in sis[si]:
                    print("-cb1-8")
                    sis[si].append(rfn)
            asyncio.sleep(0)
    except Exception as e:
        print(e)
    print("-cb1-9")
    tr1 -= 1




def proc_events():
    print("-proc_events-1")
    print(sis)
    for si in sis:
        print("-proc_events-2")
        p = v.src(si)
        sis[si], fl = [], sis[si]
        updateDEs(p, fl)


async def main():
    global cel, wdsi, in1, v
    print("-main-1")
    wsetup()
    print("-main-2")
    updatets(0)
    print("-main-3")
    rt2()
    print("-main-4")
    if cb1t:
        print("-main-6")
        # cb1t.cancel()


if __name__ == "__main__":
    v.initConfig()
    in1 = Inotify()
    cel = asyncio.get_event_loop()
    try:
        tsk1 = cel.create_task(main())
        tsk2 = cel.create_task(cb1())
        grp = asyncio.gather(tsk1, tsk2)
        cel.run_until_complete(grp)
    except KeyboardInterrupt:
        print("shutting down")
    finally:
        if cb1t and not cb1t.done():
            cb1t.cancel()
        if in1:
            in1.close()
        cel.run_until_complete(cel.shutdown_asyncgens())
        cel.close()
