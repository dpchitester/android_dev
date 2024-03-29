<QucsStudio Schematic 0.0.19>
<Properties>
View=-2251,-647,-760,1570,1,0,0
Grid=10,10,1
DataSet=*.dat
DataDisplay=*.dpl
OpenDisplay=0
showFrame=0
FrameText0=Title
FrameText1=Drawn By:
FrameText2=Date:
FrameText3=Revision:
</Properties>
<Symbol>
.ID -20 -16 SUB
Line -20 20 40 0 #000080 2 1
Line 20 20 0 -40 #000080 2 1
Line -20 -20 40 0 #000080 2 1
Line -20 20 0 -40 #000080 2 1
</Symbol>
<Components>
Pac P2 5 -2070 -470 -101 -95 1 2 "1" 1 "50" 1 "-40 dBm" 0 "1 GHz" 0 "26.85" 0 "SUBCLICK" 0
GND * 1 -2070 -440 0 0 1 2
Pac P3 5 -2070 -310 -101 -95 1 2 "2" 1 "50" 1 "-40 dBm" 0 "1 GHz" 0 "26.85" 0 "SUBCLICK" 0
GND * 1 -2070 -280 0 0 1 2
GND * 1 -1870 -500 0 0 0 0
SPfile X2 1 -1870 -530 -26 -77 0 0 "C:/projects/sNp/4mloop.s1p" 1 "1" 0 "polar" 0 "linear" 0 "short" 0 "none" 0 "block" 0 "SOT23" 0
GND * 1 -1880 -370 0 0 0 1
Sub NIC2 1 -1880 -80 -27 -11 0 0 "FloatLNic.sch" 0
L L5 1 -1880 20 -22 20 0 0 "Lm" 1 "0" 0 "" 0 "SELF-WE-PD3S" 0
GND * 1 -1850 20 0 0 0 0
GND * 1 -1820 -110 0 0 0 1
L L3 1 -2010 -160 -56 -76 0 0 "Lm" 1 "0" 0 "" 0 "SELF-WE-PD3S" 0
L L4 1 -1870 -160 33 -74 0 0 "Lm" 1 "0" 0 "" 0 "SELF-WE-PD3S" 0
Pac P4 5 -2070 -70 -101 -95 1 2 "3" 1 "50" 1 "-40 dBm" 0 "1 GHz" 0 "26.85" 0 "SUBCLICK" 0
GND * 1 -2070 -40 0 0 1 2
Eqn Eqn1 5 -1440 -570 -47 20 0 0 "F1=1e6=" 1 "F2=30e6=" 1 "Fp=101=" 1 "Z0=50=" 1 "ms1=mag(S[1,1])=" 1 "vs1=(1+ms1)/(1-ms1)=" 1 "yes" 0
Sub NIC1 1 -1670 -130 34 -15 0 0 "FloatLNic.sch" 0
.SP SP1 1 -1360 -110 0 87 0 0 "lin" 1 "F1" 1 "F2" 1 "101" 1 "no" 0 "1" 0 "2" 0 "none" 0
Eqn Eqn3 5 -1210 -570 -47 20 0 0 "ms2=mag(S[2,2])=" 1 "vs2=(1+ms2)/(1-ms2)=" 1 "msDiff=ms2-ms1=" 1 "OG5=sum(msDiff^2)=" 1 "yes" 0
Eqn Eqn2 5 -1480 -340 0 8 0 0 "Lm=LmOpt*1e-6=" 1 "yes" 0
.Opt Opt1 5 -1360 160 0 50 0 0 "SP1" 1 "4|2000|0.95|0.8|50|3" 0 "Var=L1|yes|90.3748|0|200|linear" 0 "Var=L2|yes|0.599989|0|200|linear" 0 "Var=C1|yes|399.918|0|10000|linear" 0 "Var=C2|yes|228.56|0|10000|linear" 0 "Var=R1|yes|3.02135|0|33|linear" 0 "Var=LmOpt|yes|43.8515|0|200|linear" 0 "Goal=OG5|MIN|1|yes" 0
GND * 1 -1510 -130 0 0 0 0
SPfile X1 1 -1510 -160 -26 -77 0 0 "C:/projects/sNp/4mloop.s1p" 1 "1" 0 "polar" 0 "linear" 0 "short" 0 "none" 0 "block" 0 "SOT23" 0
Sub SUB2 1 -1670 -50 -39 -45 0 0 "magant-net.sch" 0 "L1" 0 "L2" 0 "C1" 0 "C2" 0 "R1" 0
Sub SUB3 1 -1960 -370 -42 -46 0 0 "magant-net.sch" 0 "L1" 0 "L2" 0 "C1" 0 "C2" 0 "R1" 0
</Components>
<Wires>
-2070 -530 -2070 -500 "" 0 0 0 ""
-2070 -530 -1900 -530 "" 0 0 0 ""
-2070 -370 -2070 -340 "" 0 0 0 ""
-2070 -370 -1990 -370 "" 0 0 0 ""
-1930 -370 -1880 -370 "" 0 0 0 ""
-1940 -110 -1910 -110 "" 0 0 0 ""
-1940 -160 -1940 -110 "" 0 0 0 ""
-1910 -50 -1910 20 "" 0 0 0 ""
-1850 -50 -1850 20 "" 0 0 0 ""
-1850 -110 -1820 -110 "" 0 0 0 ""
-1980 -160 -1940 -160 "" 0 0 0 ""
-1940 -160 -1900 -160 "" 0 0 0 ""
-2070 -160 -2040 -160 "" 0 0 0 ""
-2070 -160 -2070 -100 "" 0 0 0 ""
-1840 -160 -1700 -160 "" 0 0 0 ""
-1730 -100 -1700 -100 "" 0 0 0 ""
-1730 -100 -1730 -50 "" 0 0 0 ""
-1730 -50 -1700 -50 "" 0 0 0 ""
-1640 -50 -1610 -50 "" 0 0 0 ""
-1640 -100 -1610 -100 "" 0 0 0 ""
-1610 -100 -1610 -50 "" 0 0 0 ""
-1640 -160 -1540 -160 "" 0 0 0 ""
</Wires>
<Diagrams>
<Rect -2110 480 660 360 31 #c0c0c0 1 00 1 0 5e+06 3e+07 1 -1.17056 0.5 1.16749 1 0 0 0 315 0 225 "" "" "">
	<Legend 10 -100 0>
	<"msDiff" "" #0000ff 0 3 0 0 0 0 "">
	<"ms1" "" #ff0000 0 3 0 0 0 0 "">
	<"ms2" "" #00aa00 0 3 0 0 0 0 "">
</Rect>
<Rect -2110 1080 670 450 31 #c0c0c0 1 00 1 0 5e+06 3e+07 1 0.460962 0.1 1.049 1 0 0 0 315 0 225 "" "" "">
	<Legend 10 -100 0>
	<"S[1,1]" "" #ff0000 0 3 0 0 0 0 "">
	<"S[2,2]" "" #00ff00 0 3 0 0 0 0 "">
	<"S[3,3]" "" #0055ff 0 3 0 0 0 0 "">
</Rect>
<Tab -1380 550 580 90 71 #c0c0c0 1 00 1 0 1 1 1 0 1 1 1 0 1 1 315 0 225 "" "" "">
	<"OG5" "" #0000ff 0 3 1 0 0 0 "">
	<"LmOpt.opt" "" #0000ff 0 3 1 0 0 0 "">
	<"Lm" "" #0000ff 0 3 1 0 0 0 "">
</Tab>
</Diagrams>
<Paintings>
</Paintings>
