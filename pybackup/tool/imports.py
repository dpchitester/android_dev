import pathlib
from import_deps import ModuleSet

# First initialise a ModuleSet instance with a list str of modules to track
pkg_paths = pathlib.Path('/sdcard/projects/pybackup').glob('pybackup.py')
module_set = ModuleSet([str(p) for p in pkg_paths])

# then you can get the set of imports
for imported in module_set.mod_imports('pybackup.pybackup'):
    print(imported)

# foo.foo_c
# foo.foo_b