import sys
from pathlib import Path
from pprint import pprint

from module_dependencies import Source

fn = sys.argv[1]
# This creates a Source instance for this file itself
src = Source(fn)

print(f"Module imports for '{fn}'")
pprint(src.imports())
print()

print(f"Module dependencies for '{fn}'")
pprint(src.dependencies())
