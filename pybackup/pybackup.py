#!/data/data/com.termux/files/usr/bin/env python

from os import environ
from os import walk
from pathlib import Path
from queue import Empty
from queue import Queue
from threading import Lock
from threading import Thread
from time import sleep

from asyncinotify import Event as WEvent
from asyncinotify import Inotify
from asyncinotify import Mask
from asyncinotify import Watch


# from snoop import pp
# from snoop import snoop

import asyncrun as ar
import config as v
import ldsv as ls
from findde import updateDEs
from netup import netup
from opexec import clean
from opexec import opExec
from sd import FS_Mixin
from status import onestatus
from status import updatets

in1 = None
wdsi: dict[Watch, v.NodeTag] = {}
weq = Queue()

th1 = None
th2 = None
th3 = None


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
                    v.cull_dirs(dirs, pt)
                    wa: Watch = in1.add_watch(pth, Mask(0x306))
                    wdsi[wa] = si
        except KeyboardInterrupt as exc:
            print(exc)
            break
        except OSError as exc:
            print(exc)
            break
    print(len(wdsi), "watches")


def cb1():
    global in1, weq
    print("-cb1 started")
    while True:
        try:
            for ev in in1:
                weq.put(ev)
        except BlockingIOError:
            pass
        if v.quit_ev.is_set():
            break
        sleep(1)


def proc_events():
    print("-proc_events started")
    sis: dict[v.NodeTag, list[str]] = {}
    sislk = Lock()

    def procq():
        nonlocal sis
        with sislk:
            tsis, sis = sis, {}
            for si in tsis:
                p = v.src(si)
                fl = tsis[si]
                if len(fl):
                    print("-procq updateDEs", p, fl)
                    updateDEs(p, fl)

    while True:
        try:
            we: WEvent = weq.get(timeout=0.666)
            if we is not None:
                si: v.NodeTag = wdsi[we.watch]
                p: Path = we.path
                if not we.mask & Mask.ISDIR:
                    rfn: Path | str = p.relative_to(v.src(si))
                    with sislk:
                        if si not in sis:
                            sis[si] = []
                        rfn = str(rfn)
                        if rfn not in sis[si]:
                            sis[si].append(rfn)
                weq.task_done()
            else:
                print("watch event is None")
        except Empty:
            if len(sis):
                th3 = Thread(target=procq)
                th3.start()
        if v.quit_ev.is_set():
            break
        sleep(1)


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
    with Inotify(sync_timeout=0.666) as in1:
        try:
            wsetup()
            updatets(0)
            th1 = Thread(target=cb1)
            th1.start()
            th2 = Thread(target=proc_events)
            th2.start()
            th3 = ls.save_bp()
            th3.start()
            rt2()
            v.quit_ev.set()
        except KeyboardInterrupt as exc:
            print(exc)
        finally:
            for th in [th1, th2, th3]:
                if th:
                    v.quit_ev.set()
                    print("waiting for", th.name, "shutdown")
                    th.join()


def pmain():
    import yappi

    yappi.start()
    main()
    yappi.stop()
    func_stats = yappi.get_func_stats()
    func_stats = func_stats.sort("tsub", "desc")
    func_stats = func_stats.strip_dirs()
    thread_stats = yappi.get_thread_stats()
    with open("temp.txt", "w") as fh:
        func_stats.print_all(fh)
        thread_stats.print_all(fh)
    func_stats.save("temp.pstat", type="pstat")

    yappi.clear_stats()
    cmd = "python -m gprof2dot -n.05 -e1 -f pstats -o temp.dot temp.pstat"
    ar.run1(cmd)
    cmd = "dot -Tsvg -Kfdp -o temp.svg temp.dot"
    ar.run1(cmd)


if __name__ == "__main__":
    for ex in ['.txt', '.pstat','.dot','.svg']:
        try:
            Path("temp"+ex).unlink()
        except FileNotFoundError:
            pass
    pmain()
