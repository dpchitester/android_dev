clear
rm pybackup.svg
python -m pybackup
gprof2dot -z pybackup:129:main -f pstats -o pybackup.gv pybackup.pstat
rm pybackup.pstat
dot -Tsvg -o pybackup.svg pybackup.gv
rm pybackup.gv
