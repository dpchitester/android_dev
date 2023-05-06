from modulefinder import ModuleFinder

finder = ModuleFinder()
finder.run_script("pybackup.py")

moduleslist = {}
for name, mod in finder.modules.items():
    filename = mod.__file__
    if filename is None:
        continue
    if "__" in filename:
        continue
    if 'python3.11' in filename:
        continue
    # if "python" in filename.lower():
    #    continue
    moduleslist[name] = mod
    # print '%s: %s' % (name, filename)
    # print ','.join(mod.globalnames.keys()[:3])

print("Loaded modules:")
for name, val in sorted(moduleslist.items()):
    print(name)

