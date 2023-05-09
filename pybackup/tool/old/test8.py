from tstamp import rtset

from config import path
from config import pdirs
from config import srcs
from config import tag
from config import tagid
from config import tags
from config import tdirs
from dirlist import getdll1
from dirlist import getdll2


def init():
    global dl1, dl2, ds1, ds2, f2c, f2d
    for si in srcs:
        dt = "gd_" + tag(si)
        if dt in tags:
            di = tagid(dt)
            print(tag(si), tag(di))
            if di in tdirs:
                dl1 = getdll2(path(pdirs, si))
                dl2 = getdll1(path(tdirs, di))
                ds1 = set(dl1)
                ds2 = set(dl2)
                f2c = ds1 - ds2
                f2d = ds2 - ds1
                print("to delete", len(f2d))
                print("to copy", len(f2c))
                # if len(f2c):
                # rtset(si)


init()
