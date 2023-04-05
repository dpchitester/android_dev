#!/data/data/com.termux/files/usr/bin/bash

echo "create new bitbucket reponame: $1"
pushd /sdcard/projects

if [ "$1" != "" ]; then
    echo "$1"
    curl -X DELETE -H "Content-Type: application/json" -d '{ "scm": "git" }' https://dpchitester:ATBBCeteQw4LEu9HVJPLDezYyDYR83B8D743@api.bitbucket.org/2.0/repositories/dpchitester/$1
    if [ $? -eq 0 ]; then
        curl -X POST -H "Content-Type: application/json" -d '{ "scm": "git" }' https://dpchitester:ATBBCeteQw4LEu9HVJPLDezYyDYR83B8D743@api.bitbucket.org/2.0/repositories/dpchitester/$1
        if [ $? -eq 0 ]; then
            echo "command success"
        else
            echo "command failed"
        fi
    else
        echo "delete failed"
    fi
else
    echo "needs reponame parameter"
fi

popd