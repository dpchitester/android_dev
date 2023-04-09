from hashlib import blake2b
from pathlib import Path, PosixPath
from struct import pack, unpack

import config as v


def bhu(ho, it1):
    bhuf = {
        bytes: lambda it: ho.update(it),
        int: lambda it: ho.update(pack("i", it)),
        float: lambda it: ho.update(pack("f", it)),
        str: lambda it: ho.update(it.encode()),
        Path: lambda it: ho.update(str(it).encode()),
        PosixPath: lambda it: ho.update(str(it).encode()),
        tuple: lambda it: [bhuf[type(it2)](it2) for it2 in it],
        set: lambda it: [bhuf[type(it2)](it2) for it2 in it],
        list: lambda it: [bhuf[type(it2)](it2) for it2 in it],
        v.DE: lambda it: [bhuf[type(it2)](it2) for it2 in (it.nm, it.sz, it.mt, it.md5)],
    }
    try:
        bhuf[type(it1)](it1)
    except KeyError:
        print("key error", type(it), "??")


# flattened list blake2b with integer result
def blakeHash(it):
    ho = blake2b(digest_size=4)
    bhu(ho, it)
    rv = unpack("i", ho.digest())
    return rv[0]
