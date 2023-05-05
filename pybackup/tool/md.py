import sys
from pathlib import Path
from pprint import pprint

from module_dependencies import Source


# This creates a Source instance for this file itself
src = Source.from_file('pybackup.py')

print(f"Module imports")
pprint(src.imports())
print()

print(f"Module dependencies")
pprint(src.dependencies())
    