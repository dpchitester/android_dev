import pickle
from struct import pack, unpack

from xxhash import xxh64


def bhu(ho, it):
    from pathlib import Path

    from de import DE, FSe

    match it:
        case bytes():
            ho.update(it)
        case int():
            ho.update(pack("i", it))
        case float():
            ho.update(pack("f", it))
        case str():
            ho.update(it.encode())
        case Path() | tuple() | set() | list() | DE() | FSe():
            bs = pickle.dumps(it)
            ho.update(bs)
        case _:
            print("key error", type(it), "??")


# flattened list blake2b with integer result
def blakeHash(it):
    ho = xxh64()
    bhu(ho, it)
    return ho.intdigest()
