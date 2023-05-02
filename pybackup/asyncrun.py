import re
import subprocess
import sys
from threading import Lock

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
    olg = csp.execute(path=cwd)
    txt = ""
    try:
        for ln in olg:
            print(ln, end="")
            txt += ln
    except subprocess.CalledProcessError as exc:
        print(exc.output.message)
        print(exc.output.trace)
        return exc.returncode
    return 0


run = a_run
run1 = a_run1
run2 = a_run2
run3 = a_run3
