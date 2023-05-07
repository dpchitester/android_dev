from pathlib import Path

import pygraphviz

import asyncrun as ar

graph = pygraphviz.AGraph(strict=False, directed=True)

p = Path.cwd()

for pf in p.glob('*.py'):
    source = pf.stem
    cmd=f'python -m import_deps {p / pf}'
    print(cmd)
    ar.run1(cmd)
    deps = ar.txt.splitlines()
    print(deps)
    for dep in deps:
        print(source, dep)
        sink = dep.strip()
        if sink:
            graph.add_edge(source, sink)

gobn = "md1"

graph.write(gobn+'.dot')
cmd='dot -Tsvg -Kfdp -o '+gobn+'.svg '+gobn+'.dot'
ar.run1(cmd)
