gobn = "inspect/callgraph"
from pathlib import Path

import pybackup
import asyncrun as ar

def pmain():
    import yappi
    import snakeviz

    yappi.start()
    pybackup.main()
    yappi.stop()
    func_stats = yappi.get_func_stats()
    func_stats = func_stats.sort("ttot", "desc")
    func_stats = func_stats.strip_dirs()
    thread_stats = yappi.get_thread_stats()
    with open(gobn + ".prof", "w") as fh:
        func_stats.print_all(fh)
        thread_stats.print_all(fh)
    func_stats.save(gobn + ".pstat", type="pstat")

    yappi.clear_stats()

    snakeviz.main([gobn + ".pstat"])
    


if __name__ == "__main__":
    for ex in [".prof", ".pstat", ".gv", ".svg"]:
        try:
            Path(gobn + ex).unlink()
        except FileNotFoundError:
            pass
    pmain()
