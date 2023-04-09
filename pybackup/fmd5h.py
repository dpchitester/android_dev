from hashlib import md5

import config as v


def md5sumf(Fn):
    if Fn.exists():
        print("-md5sumf", Fn.name)
        ho = md5()
        with open(Fn, "rb") as fh:
            b = fh.read(1 << 15)
            while len(b) > 0:
                ho.update(b)
                b = fh.read(1 << 15)
        return ho.digest()
    return None


def finddict(d1, fp):
    ta = fp.parent.parts
    for dp in ta:
        if dp not in d1:
            d1[dp] = {}
        d1 = d1[dp]
    return d1


def fmd5f(fp, sz, mt):
    def new_hash():
        nh = md5sumf(fp)
        d1[fp.name] = (sz, mt, nh)
        v.hf_dirty = True
        return nh

    d1 = finddict(v.fmd5hd, fp)
    if fp.name not in d1:
        v.hf_dm += 1
        return new_hash()
    else:
        v.hf_dh += 1
        (osz, omt, oh) = d1[fp.name]
        if osz == sz and omt == mt:
            v.hf_sth += 1
            return oh
        else:
            v.hf_stm += 1
            return new_hash()
