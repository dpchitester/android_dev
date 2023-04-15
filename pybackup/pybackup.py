#!/data/data/com.termux/files/usr/bin/env python
import asyncio
from os import environ, walk
from pathlib import Path
import multiprocessing as mp

import config as v
import ldsv
import status as st
from config import src, srcs

from inotify_simple import INotify, flags
from fsmixin import FS_Mixin
from netup import netup
from opexec import clean, opExec
from status import onestatus, updatets

wdsi = {}
in1 = None
cel = None


def wsetup():
    global wdsi, in1, v
    for si in v.srcs:
        try:
            p = v.src(si)
            pt = type(p)
            if isinstance(p, FS_Mixin):
                rv = in1.add_watch(str(p), flags.MODIFY)
                wdsi[rv] = (si, p)
                if p.is_dir():
                    # TODO: not up to date
                    for pth, dirs, files in walk(p, topdown=True):
                        if ".git" in pth:
                            dirs = []
                            break
                        if ".git" in dirs:
                            dirs.remove(".git")
                        if "__pycache__" in dirs:
                            dirs.remove("__pycache__")
                        for d in dirs:
                            cp = pt(pth) / d
                            rv = in1.add_watch(str(cp), flags.MODIFY)
                            wdsi[rv] = (si, cp)
                            # asyncio.sleep(0)
        except Exception as e:
            print(e)
    print(len(wdsi), "watches")


tr = 0


async def cb1():
    global tr, in1, v
    sis = set()
    evs = in1.read(1000, 1000)
    for ev in evs:
        print(ev)
        si = wdsi[ev.wd][0]
        if si in v.srcs:
            p = v.src(si)
            if si not in sis:
                if isinstance(p, FS_Mixin):
                    sis.add(si)
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
    while True:
        itc += 1
        updatets(itc)
        cl = clean()
        if cl:
            print("backups appear done")
            rv1 = False
        else:
            print("backups appear pending")
            rv1 = opExec()
        ldsv.save_all()
        time.sleep(12)


def main():
    global cel, wdsi, in1, v
    print("-main")
    v.initConfig()
    with INotify() as in1:
        cel.add_reader(in1.fd, cb2)
        wsetup()
        rt2()


if __name__ == "__main__":
    cel = asyncio.get_event_loop()
    cel.run_until_complete(main())
