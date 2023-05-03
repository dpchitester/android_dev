python -m cProfile -o pybackup.pstats pybackup.py
gprof2dot.py -f pstats pybackup.pstats | dot -Tpng -o pybackup.png

