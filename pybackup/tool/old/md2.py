from pathlib import Path
from pprint import pprint

import module_dependencies as md
import pygraphviz
from module_dependencies import Source

import asyncrun as ar

# This creates a Source instance for this file itself

gobn = "inspect/md2"

graph = pygraphviz.AGraph(strict=False, directed=True)

p = Path.cwd()

for pf in p.glob('*.py'):
    src = Source.from_file(pf.name)
    source = pf.stem
    deps = src.imports()
    print(source, deps)
    for dep in deps:
        print(source, dep)
        sink = dep.strip()
        if sink:
            graph.add_edge(source, sink)

graph.write(gobn+'.gv')

#cmd='dot -Tsvg -Kfdp -o '+gobn+'.svg '+gobn+'.gv'
#ar.run1(cmd)
