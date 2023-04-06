#!/data/data/com.termux/files/usr/bin/bash
# source ~/projects/bash/gb.env

pushd /sdcard/projects/bash
    f1=installs.sh
    f2=uninstalls.sh
    cp shebang.txt $f1
    cp shebang.txt $f2
    il=$(pkg list-installed)
    a=()
    mapfile -t a <<<"$il"
    for i in "${a[@]:1}"; do
        echo "# pkg install ${i%%/*}" >>$f1
        echo "# pkg uninstall ${i%%/*}" >>$f2
    done
    pl=$(pip list)
    a=()
    mapfile -t a <<<"$pl"
    for i in "${a[@]:1}"; do
        echo "# pip install ${i%%/*}" >>$f1
        echo "# pip uninstall ${i%%/*}" >>$f2
    done
popd

