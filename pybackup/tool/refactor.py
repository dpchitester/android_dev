#!/data/data/com.termux/files/usr/bin/python

from rope.base.exceptions import RefactoringError
from rope.base.libutils import analyze_modules
from rope.base.project import Project
from rope.contrib.findit import find_occurrences
from rope.refactor.move import create_move
from rope.refactor.rename import Rename

proj = Project(".")

# analyze_modules(proj)
import snoop

mods = []


def doChGl(old, new):
    global mods
    mods = proj.get_python_files()
    mods = list(filter(lambda fp: "/" not in str(fp.path), mods))
    for mod in mods:
        if doCh(mod, old, new):
            return


def doCh(mod, old, new):
    global mods
    try:
        idx = mod.read().index(old, 0)
    except ValueError as e:
        # print(e)
        return False
    rv = find_occurrences(proj, mod, idx, resources=mods)
    if len(rv) > 0:
        for i in rv:
            print(i.resource.name, i.region)
        try:
            rename = Rename(proj, mod, idx)
        except RefactoringError as e:
            print(e)
            return
        changes = rename.get_changes(new, resources=mods, in_hierarchy=True)
        print(changes.get_description())
        if doit:
            proj.do(changes)
        return True
    return False


doit = False

# mod2 = proj.get_resource(f2)

doChGl("lckers", "sckers")
#doChGl("rbctck", "rchk_ct")

proj.close()
