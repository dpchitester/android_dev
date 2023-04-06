from hashlib import md5
import config_vars as v
import snoop
from snoop import pp

def md5sumf(Fn):
    if Fn.exists():
        #print('-md5sumf', Fn)
        ho = md5()
        try:
            with open(Fn, 'rb') as fh:
                b = fh.read(1 << 15)
                while len(b) > 0:
                    ho.update(b)
                    b = fh.read(1 << 15)
            return ho.digest()
        except Exception as e:
            print(e)
            raise e
    return None


def finddict(d1, fp):
    ta = fp.parent.parts
    for dp in ta:
        if dp not in d1:
            d1[dp] = {}
        d2 = d1[dp]
    return d2


def fmd5f(fp, sz, mt):
    d1 = finddict(v.fmd5hd, fp)
    try:
        (osz, omt, oh) = d1[fp.name]
        v.hf_dh += 1
    except KeyError:
        (osz, omt, oh) = (-1, -1, b'')
        v.hf_dm += 1
        pp(fp, sz, mt, v.hf_dm)
    if osz == sz and omt == mt:
        v.hf_sth += 1
    else:
        try:
            oh = md5sumf(fp)
            d1[fp.name] = (sz, mt, oh)
            v.hf_dirty = True
            v.hf_stm += 1
            pp(fp, sz, mt, oh, v.hf_stm)
        except:
            pass
    return oh
