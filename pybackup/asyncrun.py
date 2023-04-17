import subprocess
from threading import Lock

import re

import sys

shell_lock = Lock()

txt = ""
idel = 1


def a_run(shell_command, cwd=None):
    global txt
    with shell_lock:
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
            so = re.sub(r"\r\n", "\n", so)
            txt = so
            if txt:
                print(txt)
        return p.returncode


def a_run1(shell_command, cwd=None):
    global txt
    with shell_lock:
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
            so = re.sub(r"\r\n", "\n", so)
            txt = so
        return p.returncode


def a_run2(shell_command, cwd=None):
    global txt
    with shell_lock:
        p = subprocess.run(
            shell_command,
            shell=True,
            cwd=cwd,
            text=True,
            universal_newlines=True,
        )
        return p.returncode


run = a_run
run1 = a_run1
run2 = a_run2
