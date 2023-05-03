import re
import subprocess
import sys
from threading import Lock
import json

from snoop import snoop, pp

from csubproc import ContinuousSubprocess, Qi1, Qi2


def colored(r, g, b, text):
    return f"\033[38;2;{r};{g};{b}m{text}\033[0m"


txt = ""
js = []
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
    global txt, js
    csp = ContinuousSubprocess(shell_command)
    olg = csp.execute(path=cwd)
    txt = ""
    js = []
    try:
        for ln in olg:
            match ln:
                case Qi1():
                    print(colored(0, 255, 0, ln))
                    "".join([txt, ln])
                case Qi2():
                    js.append(json.loads(ln))
                    print(colored(255, 0, 0, ln))
            
    except subprocess.CalledProcessError as exc:
        error_output = json.loads(exc.output)
        message = error_output["message"]
        trace = error_output["trace"]
        print(message)
        print(trace)
        return exc.returncode
    return 0


run = a_run
run1 = a_run1
run2 = a_run2
run3 = a_run3
