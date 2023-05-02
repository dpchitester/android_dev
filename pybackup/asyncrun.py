import re
import subprocess
import sys
from threading import Lock

from snoop import snoop, pp

from csubproc import ContinuousSubprocess

txt = ""
idel = 1


def a_run(shell_command, cwd=None):
    global txt
    txt = ""
    p = subprocess.run(
        shell_command,
        shell=True,
        cwd=cwd,
        text=True,
        universal_newlines=True,
        capture_output=True,
    )
    so = p.stdout
    if so:
        txt = so
        if txt:
            print(txt)
    return p.returncode


def a_run1(shell_command, cwd=None):
    global txt
    txt = ""
    p = subprocess.run(
        shell_command,
        shell=True,
        cwd=cwd,
        text=True,
        universal_newlines=True,
        capture_output=True,
    )
    so = p.stdout
    if so:
        txt = so
    return p.returncode


def a_run2(shell_command, cwd=None):
    global txt
    p = subprocess.run(
        shell_command,
        shell=True,
        cwd=cwd,
        text=True,
        universal_newlines=True,
    )
    return p.returncode


def a_run3(shell_command, cwd=None):
    csp = ContinuousSubprocess(shell_command)
    olg = csp.execute(path=cwd, text=False, universal_newlines=False)
    txt = ""
    cc = {}
    try:
        for ln in olg:
            print(ln, end="")
            for c in ln:
                if c in cc:
                    cc[c]+=1
                else:
                    cc[c] = 1
            txt += ln
    except subprocess.CalledProcessError as exc:
        error_output = json.loads(ex.output) 
        message = error_output['message'] 
        trace = error_output['trace'] 
        print(message)
        print(trace)
        return exc.returncode
    pp('cc', cc)
    cc = cc.items()
    pp('cc.items', cc)
    cc = sorted(list(cc))
    pp('sorted(list(cc))', cc)
    return 0


run = a_run
run1 = a_run1
run2 = a_run2
run3 = a_run3
