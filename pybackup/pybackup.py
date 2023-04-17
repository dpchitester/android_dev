#!/data/data/com.termux/files/usr/bin/env python
import threading as th
import time
from os import environ, walk
from pathlib import Path

from asyncinotify import Event, Inotify, Mask, Watch

import config as v
import ldsv
import status as st
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
th1 = None
th2 = None


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
                    wa: Watch = in1.add_watch(pth, Mask(0x306))
                    wdsi[wa] = si
        except Exception as e:
            print(e)
    print(len(wdsi), "watches")


def cb1():
    global th2, in1, sis
    print("-cb1-1")
    for ev in in1:
        print("-cb1-4 ev:", ev)
        si = wdsi[ev.watch]
        print("-cb1-5 si:", si)
        p = ev.path
        print("-cb1-6 p:", p)
        if not ev.mask & Mask.ISDIR:
            rfn = str(p.relative_to(v.src(si)))
            print("-cb1-7 rfn:", rfn)
            if si not in sis:
                print("-cb1-8 []", [])
                sis[si] = []
            if rfn not in sis[si]:
                print("-cb1-9 rfn:", rfn)
                sis[si].append(rfn)
                if th2 is None:
                    print("-cb1-10 th2 is None")
                    th2 = th.Thread(target=proc_events)
                    th2.start()
                elif not th2.is_alive():
                    print("-cb1-11 th2 not is_alive")
                    th2 = th.Thread(target=proc_events)
                    th2.start()
    print("-cb1-13")


def proc_events():
    global sis
    print(sis)
    tsis, sis = sis, {}
    for si in tsis:
        p = v.src(si)
        fl = tsis[si]
        if len(fl):
            print("-proc_events-3: updateDEs", p, fl)
            updateDEs(p, fl)


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
            break
        else:
            print("-rt2-4")
            print("backups appear pending")
            rv1 = opExec()
        print("-rt2-5")


def main():
    global cel, wdsi, in1, v, th1, th2
    v.initConfig()
    with Inotify(sync_timeout=-1) as in1:
        wsetup()
        updatets(0)
        th1 = th.Thread(target=cb1)
        th1.start()
        rt2()
        while th2 and th2.is_alive():
            sleep(1)
        if th2 and th2.is_alive():
            th2.cancel()
        if th1 and th1.is_alive():
            th1.cancel()
    ldsv.save_all()


if __name__ == "__main__":
    main()
