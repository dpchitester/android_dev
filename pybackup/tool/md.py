import sys
from pathlib import Path
from pprint import pprint

from module_dependencies import Source


# This creates a Source instance for this file itself
src = Source.from_folder(".")

print(f"Module imports")
pprint(src.imports_mapping())
print()

print(f"Module dependencies")
pprint(src.dependencies_mapping())
