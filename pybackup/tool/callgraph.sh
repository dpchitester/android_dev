python -m pybackup
gprof2dot -n0 -e0 -f callgrind pybackup.cg | dot -Tpng -o pybackup.png

