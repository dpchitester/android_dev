#!/data/data/com.termux/files/usr/bin/env python
from sys import exit

from subprocess import run
from pathlib import Path

print("-- rfmt.py --")

cmd = 'black -t py311 *.py'
print(cmd)
res = run(cmd, shell=True)
exit(res)
