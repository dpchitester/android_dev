from hashlib import blake2b
from pathlib import Path
from pathlib import PosixPath
from struct import pack
from struct import unpack

from de import DE
from de import FSe
from sd import CS
from sd import SD
from sd import Ext3
from sd import Fat32


def bhu(ho, it1):
    bhuf = {
        bytes: lambda it: ho.update(it),
        int: lambda it: ho.update(pack("i", it)),
        float: lambda it: ho.update(pack("f", it)),
        str: lambda it: ho.update(it.encode()),
        Path: lambda it: ho.update(pack("i", hash(it))),
        PosixPath: lambda it: ho.update(pack("i", hash(it))),
        SD: lambda it: ho.update(pack("i", hash(it))),
        # Local: lambda it: ho.update(str(it).encode()),
        # Remote: lambda it: ho.update(str(it).encode()),
        Ext3: lambda it: ho.update(pack("i", hash(it))),
        Fat32: lambda it: ho.update(pack("i", hash(it))),
        CS: lambda it: ho.update(pack("i", hash(it))),
        tuple: lambda it: [bhuf[type(it2)](it2) for it2 in it],
        set: lambda it: [bhuf[type(it2)](it2) for it2 in it],
        list: lambda it: [bhuf[type(it2)](it2) for it2 in it],
        DE: lambda it: [bhuf[type(it2)](it2) for it2 in (it.nm, it.i)],
        FSe: lambda it: [bhuf[type(it2)](it2) for it2 in (it.sz, it.mt)],
    }
    try:
        bhuf[type(it1)](it1)
    except KeyError:
        print("key error", type(it1), "??")

def bhu2(ho, it):
    match type(it):
        case 'bytes':
            ho.update(it)
        case 'int':
            ho.update(pack("i", it))
        case 'float':
            ho.update(pack("f", it))
        case 'str':
            ho.update(it.encode())
        case 'Path' | 'PosixPath' | 'SD' | 'Ext3' | 'Fat32' | 'CS':
            ho.update(bytes(it))
        case 'tuple' | 'set' | 'list':
            for it2 in it:
                bhu(ho, it2)
        case 'DE':
            ho.update(bytes(it.nm))
            ho.update(pack("i", it.i.sz))
            ho.update(pack("f", it.i.mt))
        case 'FSe':
            ho.update(pack("i", it.sz))
            ho.update(pack("f", it.mt))
        case _:
            print("key error", type(it), "??")


# flattened list blake2b with integer result
def blakeHash(it):
    ho = blake2b(digest_size=4)
    bhu(ho, it)
    rv = unpack("i", ho.digest())
    return rv[0]
