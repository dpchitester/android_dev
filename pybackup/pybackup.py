#!/data/data/com.termux/files/usr/bin/env python
import asyncio
from os import environ, walk
from pathlib import Path
import multiprocessing as mp
import time

import config as v
import ldsv
import status as st

from inotify_simple import INotify, flags, Event
from findde import updateDEs
from fsmixin import FS_Mixin
from netup import netup
from opexec import clean, opExec

from status import onestatus, updatets

wdsi: dict[int, tuple[str, FS_Mixin]] = {}
in1 = None
cel = None
cb2t = None


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
                    rv = in1.add_watch(str(pth), flags.MODIFY)
                    wdsi[rv] = (si, pth)
        except Exception as e:
            print(e)
    print(len(wdsi), "watches")


sis: dict[str, list[str]] = {}


def proc_events():
    print("-proc_events")
    for si in sis:
        p = v.src(si)
        sis[si], fl = [], sis[si]
        updateDEs(p, fl)


def cb1():
    global tr, in1, v, sis
    print("-cb1")
    evs = in1.read(1000, 1000)
    for ev in evs:
        si = wdsi[ev.wd][0]
        p = wdsi[ev.wd][1]
        fn = ev.name
        p = p.relative_to(v.src(si))
        if si not in sis:
            sis[si] = []
        if fn not in sis[si]:
            sis[si].append(p / fn)

async def cb2():
    global tr, cel, cb2t
    print("-cb2")
    if cb2t:
        await cb2t
    cb2t = cel.create_task(cb1())


def rt2():
    print("-rt2-1")
    itc = 0
    while True:
        itc += 1
        print("-rt2-2")
        proc_events()
        cl = clean()
        if cl:
            print("-rt2-3")
            print("no backups appear pending")
            rv1 = False
            break
        else:
            print("-rt2-4")
            print("backups appear pending")
            rv1 = opExec()
            print("-rt2-5")
            ldsv.save_all()
        print("-rt2-6")
        time.sleep(10)


async def main():
    global cel, wdsi, in1, v
    print("-main")
    v.initConfig()
    in1 = INotify()
    cel.add_reader(in1.fd, cb2())
    wsetup()
    updatets(0)
    rt2()
    if cb2t:
        cb2t.cancel()


if __name__ == "__main__":
    cel = asyncio.get_event_loop()
    asyncio.run(main())
