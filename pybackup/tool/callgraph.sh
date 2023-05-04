rm pybackup.svg
python -m pybackup
gprof2dot -z pybackup:129:main -f pstats -o pybackup.gv pybackup.pstats
rm pybackup.pstats
dot -Tsvg -Kfdp -o pybackup.svg pybackup.gv
rm pybackup.gv
