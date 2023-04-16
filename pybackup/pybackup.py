#!/data/data/com.termux/files/usr/bin/env python
import asyncio
from os import environ, walk
from pathlib import Path
import multiprocessing as mp
import time

import config as v
import ldsv
import status as st

from asyncinotify import Inotify, Mask, Event
from findde import updateDEs
from fsmixin import FS_Mixin
from netup import netup
from opexec import clean, opExec

from status import onestatus, updatets

wdsi: dict[int, tuple[str, FS_Mixin]] = {}
in1 = None
cel = None
cb2t = None
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
                    rv = in1.add_watch(pth, Mask.MODIFY|Mask.ACCESS)
                    wdsi[rv] = (si, pth)
        except Exception as e:
            print(e)
    print(len(wdsi), "watches")


sis: dict[str, list[str]] = {}

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

def proc_events():
    print("-proc_events-1")
    for si in sis:
        print('-proc_events-2')
        p = v.src(si)
        sis[si], fl = [], sis[si]
        updateDEs(p, fl)


async def cb1():
    global tr1, in1, v, sis
    print("-cb1-1")

    try:
        async for ev in in1:
            print("-cb1-2")
            si = wdsi[ev.wd][0]
            print("-cb1-3")
            p = wdsi[ev.wd][1]
            print("-cb1-4")
            fn = ev.name
            print("-cb1-5")
            p = p.relative_to(v.src(si))
            print("-cb1-6")
            if si not in sis:
                print("-cb1-7")
                sis[si] = []
            if fn not in sis[si]:
                print("-cb1-8")
                sis[si].append(p / fn)
    except Exception as e:
        print(e)
    print("-cb1-9")
    tr1 -= 1


def cb2():
    global tr1, cel, cb2t
    print("-cb2-1")
    if not tr1:
        print("-cb2-2")
        tr1 += 1
        cb2t = cel.create_task(cb1())
        




async def main():
    global cel, wdsi, in1, v
    print("-main-1")
    v.initConfig()
    print("-main-2")
    in1 = Inotify()
    print("-main-3")
    cel.add_reader(in1.fd, cb2)
    print("-main-4")
    wsetup()
    print("-main-5")
    updatets(0)
    print("-main-6")
    rt2()
    print("-main-7")
    if cb2t:
        print("-main-8")
        #cb2t.cancel()


if __name__ == "__main__":
    cel = asyncio.get_event_loop()
    try:
        cel.run_until_complete(main())
    except KeyboardInterrupt:
        print('shutting down')
    finally:
        cel.run_until_complete(cel.shutdown_asyncgens())
        cel.close()