import json
import subprocess

from csubproc import ContinuousSubprocess, Qi1, Qi2

# from snoop import pp
# from snoop import snoop


def colored(r, g, b, text):
    return f"\033[38;2;{r};{g};{b}m{text}\033[0m"


txt = ""
txt1 = ""
txt2 = ""
msglst = []
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
    global txt, msglst
    csp = ContinuousSubprocess(shell_command)
    olg = csp.execute(path=cwd)
    txt = ""
    msglst = []
    try:
        for ln in olg:
            match ln:
                case Qi1():
                    "".join([txt, ln])
                    print(colored(0, 255, 255, ln), end="")
                case Qi2():
                    if ln and len(ln):
                        msg = json.loads(ln)
                        msglst.append(msg)
                    # print(colored(255, 0, 0, msg))
    except subprocess.CalledProcessError as exc:
        error_output = json.loads(exc.output)
        message = error_output["message"]
        trace = error_output["trace"]
        print(message)
        print(trace)
        return exc.returncode
    return 0


def a_run4(shell_command, cwd=None):
    global txt1, txt2
    csp = ContinuousSubprocess(shell_command)
    olg = csp.execute(path=cwd)
    txt1 = ""
    txt2 = ""
    try:
        for ln in olg:
            match ln:
                case Qi1():
                    "".join([txt1, ln])
                    print(colored(0, 255, 0, ln), end="")
                case Qi2():
                    "".join([txt2, ln])
                    print(colored(255, 0, 0, ln), end="")
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
run4 = a_run4
