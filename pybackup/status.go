package main

import (
"fmt")



import ("config")
func Stsupdate[T0 any, T1 any](Si T0 any, Dh T1 any) {
fmt.Printf("%v\n",Si, " ");
for _, e := range config.eDep.iter().cloned().filter(|&e| e.si == Si).map(|e| e).collect::<Vec<_>>() {
rtset(e);
}
sdhset(config.src(Si), Dh);}


func Onestatus[T0 any](Si T0 any) {
tr := sdhck(config.src(Si))
if(tr != nil) {
var Dh, changed = tr
if(changed) {
Stsupdate(Si, Dh);
fmt.Printf("\n",);
}
}}


func SrcStatuses() List {
var SDl List = []None{}
for _, Si := range config.srcs {
tr := sdhck(config.src(Si))
if(tr != nil) {
var Dh, changed = tr
if(changed) {
SDl = append(SDl, Si, Dh);
}
}
}
return SDl}


func Updatets[T0 any](N T0 any) {
fmt.Printf("%v %v\n","Status", N);
var Sl List = SrcStatuses()
if(len(Sl)) {
fmt.Printf("%v\n","changed: ", "");
for _, Si, Dh := range Sl {
Stsupdate(Si, Dh);
}
fmt.Printf("\n",);
}}


