from pathlib import Path
import config as v
from snoop import snoop, pp

def findAllSi(fp1):
    l1 = []
    for si in v.srcs:
        try:
            fp2 = v.paths[si]
            if fp1.parent.is_relative_to(fp2):
                rp1 = fp1.relative_to(fp2)
                l1.append({si: rp1})
        except:
            pass
    return l1

def findAllDi(fp1):
    l1 = []
    for di in v.tgts:
        try:
            fp2 = v.paths[di]
            if fp1.parent.is_relative_to(fp2):
                rp1 = fp1.relative_to(fp2)
                l1.append({di: rp1})
        except:
            pass
    return l2
            
def test1():
    v.initConfig()
    f1 = Path('GoogleDrive:/zips/python.zip')
    sil = findAllSi(f1)
    dil = findAllDi(f1)
    print(sil)
    print(dil)

if __name__ == "__main__":
    test1()
