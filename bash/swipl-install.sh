#!/usr/bin/sh

ARCH=`dpkg --print-architecture`
VER="8.1.3-1"
SWIPL_DEB="swi-prolog_${VER}_${ARCH}.deb"
UUID_DEB="ossp-uuid_1.6.2-2_${ARCH}.deb"
TMP=`pwd`/deb.$$

download_deb() {
   mkdir -p "$TMP" && \
      curl https://raw.githubusercontent.com/erlanger/swipl-termux/master/debs/$1 -s -o "$TMP/$1"
}

install_deb() {
cd "$TMP" && \
   apt --fix-broken -y install "./$1"
}

#Download swipl and oosp-uuid packages
download_deb $SWIPL_DEB && download_deb $UUID_DEB

#Install package
install_deb $UUID_DEB     && \
   install_deb $SWIPL_DEB

rm -rf "$TMP"

