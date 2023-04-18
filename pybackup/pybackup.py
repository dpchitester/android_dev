#!/data/data/com.termux/files/usr/bin/env python

from os import environ, walk
from pathlib import Path
from queue import Empty, Queue
from threading import Thread, Event, Lock, Thread
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
        except KeyboardInterrupt as exc:
            print(exc)
            raise exc
        except Exception as exc:
            print(exc)
            raise exc
    print(len(wdsi), "watches")


def cb1():
    global in1, eq1, qe1
    print("-cb1 started")
    while True:
        try:
            for ev in in1:
                eq1.put(ev)
                qs = eq1.qsize()
                print(qs)
        except BlockingIOError:
            pass
        except KeyboardInterrupt as exc:
            print(exc)
            break
        except Exception as exc:
            print(exc)
            raise exc
        if qe1.is_set():
            break


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
                    print("-proc_events-3: updateDEs", p, fl)
                    updateDEs(p, fl)

    while True:
        try:
            ev1: WEvent = eq1.get(timeout=0.666)
            if ev1 is None:
                continue
            qs = eq1.qsize()
            print(qs)
            try:
                si: NodeTag = wdsi[ev1.watch]
                wp = ev1.watch.path
                p: Path = ev1.path
                sip = v.src(si)
                assert wp == p == sip
                print('wp, p, sip', wp, p, sip)
                if not ev1.mask & Mask.ISDIR:
                    rfn: Path = p.relative_to(v.src(si))
                    with sislk:
                        if si not in sis:
                            sis[si] = []
                        rfn = str(rfn)
                        if rfn not in sis[si]:
                            sis[si].append(rfn)
            finally:
                eq1.task_done()
        except Empty:
            if len(sis):
                th3 = Thread(target=procq)
                th3.start()
        except KeyboardInterrupt as exc:
            print(exc)
            break
        except Exception as exc:
            print(exc)
            break
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
    with Inotify(sync_timeout=0.666) as in1:
        try:
            wsetup()
            updatets(0)
            th1 = Thread(target=cb1)
            th1.start()
            th2 = Thread(target=proc_events)
            th2.start()
            rt2()
        except KeyboardInterrupt as exc:
            print(exc)
        except Exception as exc:
            print(exc)
        finally:
            qe1.set()
            for th in [th1, th2]:
                if th:
                    th.join()
            ldsv.save_all()


if __name__ == "__main__":
    main()
