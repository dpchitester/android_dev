from hashlib import blake2b
from pathlib import Path, PosixPath
from struct import pack, unpack

import config_vars as v


def bhu(ho, it):
    def iu(it):
        for itit in it:
            bhu(ho, itit)

    bhuf = {
        bytes: lambda it: ho.update(it),
        int: lambda it: ho.update(pack("i", it)),
        float: lambda it: ho.update(pack("f", it)),
        str: lambda it: ho.update(it.encode()),
        Path: lambda it: ho.update(bytes(it)),
        PosixPath: lambda it: ho.update(bytes(it)),
        tuple: iu,
        set: iu,
        list: iu,
        v.DE: lambda it: iu((it.nm, it.sz, it.mt, it.md5)),
    }
    try:
        bhuf[type(it)](it)
    except KeyError:
        print("key error", type(it), "??")


# flattened list blake2b with integer result
def blakeHash(it):
    ho = blake2b(digest_size=4)
    bhu(ho, it)
    rv = unpack("i", ho.digest())
    return rv[0]
