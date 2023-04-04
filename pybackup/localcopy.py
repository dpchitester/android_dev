from opbase import OpBase
from edge import Edge, findEdge

class FileDiff():
    sf = None
    df = None
    fe = 0
    sz = 0
    mt = 0
    hd = False

    def __init__(self, sf, df):
        self.sf = sf
        self.df = df
        
    def chkdiff(self):
        sfe = self.sf.exists()
        if sfe:
            self.fe -= 1
        dfe = self.df.exists()
        if dfe:
            self.fe += 1
        if self.fe == 0:
            sfs = self.sf.stat()
            dfs = self.df.stat()
            if dfs.st_size < sfs.st_size:
                self.sz = -1
                print('size less:', dfs.st_size - sfs.st_size)
            elif dfs.st_size > sfs.st_size:
                self.sz = 1
                print('size more:', dfs.st_size - sfs.st_size)
            if dfs.st_mtime_ns < sfs.st_mtime_ns:
                self.mt = -1
                print('time later:', (dfs.st_mtime_ns - sfs.st_mtime_ns) / 1E9)
            elif dfs.st_mtime_ns > sfs.st_mtime_ns:
                self.mt = 1
                print('time later:', (dfs.st_mtime_ns - sfs.st_mtime_ns) / 1E9)
            if sha256sumf(self.sf) != sha256sumf(self.df):
                self.hd = True
                print('hash diff:', str(self.sf), str(self.df))

    def should_copy(self):
        self.chkdiff()
        if self.fe < 0:
            return True
        elif self.fe > 0:
            return False
        elif self.mt < 0:
            return True
        elif self.mt > 0:
            return False
        else:
            return self.hd

class SFc():
    def __init__(self, sc=0, fc=0):
        self.sc=sc
        self.fc=fc
    def value(self):
        return (self.sc, self.fc)

def sha256sums(S1):
    from hashlib import sha256
    ho = sha256()
    ho.update(S1)
    return ho.hexdigest()

def sha256sumf(Fn):
    from hashlib import sha256
    if Fn.exists():
        b = Fn.read_bytes()
        ho = sha256()
        ho.update(b)
        return ho.hexdigest()
    return None

def copy2(f1, f2):
    from asyncrun import run1
    # print('copying ', f1, 'to', f2)
    if f1.is_file():
        f2 = f2.parent
    cmd = 'cp -f -p ' + str(f1) + ' ' + str(f2)
    print(cmd)
    return run1(cmd)

#import shutil
#shutil.copy2(f1, f2)


class LocalCopy(OpBase):
    sfc = SFc()
    def __init__(self, npl1, npl2, opts={}):
        super(LocalCopy, self).__init__(npl1, npl2, opts)
    def ischanged(self, e:Edge):
        return e.chk_ct()
    def __call__(self):
        from config_funcs import pdir, tdir
        from edge import Edge, findEdge
        import config_vars as v
        from os import makedirs
        di, si = self.npl1
        e:Edge = findEdge(di, si)
        if e.chk_ct():
            print('LocalCopy', self.npl1, self.npl2)
            sp = pdir(self.npl2[1])
            dp = tdir(self.npl2[0])
            gl = self.opts.get('files', ['**/*'])
            for g in gl:
                try:
                    fl = sp.glob(g)
                except Exception as e:
                    print("glob error in localcopy", e)
                    self.sfc.fc += 1
                    return self.sfc.value()
                for fsf in fl:
                    rf = fsf.relative_to(sp)
                    fdf = dp / rf
                    pd = fdf.parent
                    try:
                        if not pd.exists():
                            makedirs(pd, exist_ok=True)
                        fdiff = FileDiff(fsf, fdf)
                        if fdiff.should_copy():
                            rv = copy2(fsf, fdf)
                            if rv == 0:
                                if 'exec' in self.opts:
                                    fdf.chmod(496)
                                self.sfc.sc += 1
                            else:
                                self.sfc.fc += 1
                    except Exception as e:
                        print(e)
                        self.sfc.fc += 1
            if self.sfc.fc == 0:
                e.clr()
            if self.sfc.sc > 0:
                tv = self.npl2[0]
                if tv in v.LDlls:
                    del v.LDlls[tv]
                    v.LDlls_changed = True
        return self.sfc.value()
