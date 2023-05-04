rm pybackup.png
python -m pybackup
gprof2dot -z pybackup:129:main -f pstats -o pybackup.gv pybackup.pstats
rm pybackup.pstats
dot -Tpng -o pybackup.png pybackup.gv
rm pybackup.gv
