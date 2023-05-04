from modulefinder import ModuleFinder

finder = ModuleFinder()
finder.run_script("pybackup.py")

moduleslist = {}
for name, mod in finder.modules.items():
    filename = mod.__file__
    if filename is None:
        continue
    if '__' in name:
        continue
    #if "python" in filename.lower():
    #    continue
    moduleslist[name] = mod
    #print '%s: %s' % (name, filename)
    #print ','.join(mod.globalnames.keys()[:3])

print( 'Loaded modules:')
for name, mod in moduleslist.items():
    print(name, end=': ')
    print(', '.join(list(mod.globalnames)))

#input("Press Enter to continue...")
