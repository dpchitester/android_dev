from hashlib import md5

import config as v

from snoop import snoop, pp

def md5sumf(Fn):
    if Fn.exists():
        print("-md5sumf", str(Fn))
        ho = md5()
        with open(Fn, "rb") as fh:
            b = fh.read(1 << 15)
            while len(b) > 0:
                ho.update(b)
                b = fh.read(1 << 15)
        return ho.digest()
    return None

def fmd5f(fp, sz, mt, nh=None):
    d1 = v.fmd5hd
    if fp not in d1:
        v.hf_dm += 1
        if nh is None:
            nh = md5sumf(fp)
        nfse = v.FSe(sz, mt, nh)
        d1[fp] = nfse
        v.hf_dirty = True
        return nfse
    else: # existing
        v.hf_dh += 1
        ofse = d1[fp]
        if ofse.sz != sz or ofse.mt != mt:
            ofse.sz = sz
            ofse.mt = mt
            if nh is not None:
                ofse.md5 = nh
            else:
                ofse.md5 = md5sumf(fp)
        else:
            if nh is not None and ofse.md5 != nh:
                ofse.md5 = nh            
        return ofse
