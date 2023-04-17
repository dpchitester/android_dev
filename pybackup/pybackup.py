#!/data/data/com.termux/files/usr/bin/env python

from os import environ, walk
from pathlib import Path
from queue import Empty, Queue
from threading import Thread, Event, Lock
from time import sleep

from asyncinotify import Event as WEvent, Inotify, Mask, Watch

import config as v
import ldsv
import status as st
from findde import updateDEs
from fsmixin import FS_Mixin
from netup import netup
from opexec import clean, opExec
from status import onestatus, updatets

wdsi: dict[Watch, tuple[str, FS_Mixin]] = {}
in1 = None

th1 = None
th2 = None
th3 = None

qe1 = Event()
dl1 = Lock()
eq1 = Queue()


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
    global in1, eq1
    print("-cb1-1")
    while True:
        try:
            for ev in in1:
                eq1.put(ev)
        except BlockingIOError:
            pass
        if qe1.is_set():
            break


def proc_events():
    global th3
    sis: dict[v.NodeTag, list[str]] = {}
    sislk = Lock()
    while True:
        try:
            ev1:WEvent = eq1.get(timeout=1)
            si:NodeTag = wdsi[ev1.watch]
            p:Path = ev1.path
            if not ev1.mask & Mask.ISDIR:
                rfn:Path = str(p.relative_to(v.src(si)))
                with sislk:
                    if si not in sis:
                        sis[si] = []
                    if rfn not in sis[si]:
                        sis[si].append(rfn)
            continue
        except Empty:
            def proc1():
                nonlocal sis
                with sislk:
                    tsis, sis = sis, {}
                    for si in tsis:
                        p = v.src(si)
                        fl = tsis[si]
                        if len(fl):
                            print("-proc_events-3: updateDEs", p, fl)
                            updateDEs(p, fl)

            if len(sis):
                th3 = Thread(target=proc1)
                th3.start()
        if qe1.is_set():
            break


def rt2():
    global th1
    # print("-rt2-1")
    itc = 0
    while True:
        itc += 1
        # print("-rt2-2")
        cl = clean()
        if cl:
            # print("-rt2-3")
            print("no backups appear pending")
            rv1 = False
            break
        else:
            # print("-rt2-4")
            print("backups appear pending")
            rv1 = opExec()
        # print("-rt2-5")


def main():
    global cel, wdsi, in1, v, th1, th2, th3
    v.initConfig()
    with Inotify(sync_timeout=1) as in1:
        wsetup()
        updatets(0)
        th1 = Thread(target=cb1)
        th1.start()
        th2 = Thread(target=proc_events)
        th2.start()
        rt2()
        qe1.set()
        for th in [th1, th2, th3]:
            while th and th.is_alive():
                sleep(1)
    ldsv.save_all()


if __name__ == "__main__":
    main()
