from pathlib import Path
from module_dependencies import Source
from pprint import pprint
import sys


fn = sys.argv[1]
# This creates a Source instance for this file itself
src = Source(fn)

print(f"Module imports for '{fn}'")
pprint(src.imports())
print()

print(f"Module dependencies for '{fn}'")
pprint(src.dependencies())
