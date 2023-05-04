python -m pybackup
gprof2dot -n0 -e0 -f pstats pybackup.pstats | dot -Tsvg -o pybackup.svg

