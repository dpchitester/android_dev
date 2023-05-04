rm pybackup.svg
python -m pybackup
gprof2dot -z pybackup:129:main -f pstats -o pybackup.gv pybackup.pstats
dot -Tsvg -O pybackup.gv
rm pybackup.pstats
rm pybackup.gv
