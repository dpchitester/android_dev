<Qucs Schematic 0.0.19>
<Properties>
  <View=172,202,1276,796,1.28283,0,0>
  <Grid=10,10,1>
  <DataSet=ant-net.dat>
  <DataDisplay=ant-net.dpl>
  <OpenDisplay=1>
  <Script=ant-net.m>
  <RunScript=0>
  <showFrame=0>
  <FrameText0=Title>
  <FrameText1=Drawn By:>
  <FrameText2=Date:>
  <FrameText3=Revision:>
</Properties>
<Symbol>
  <.PortSym -30 -30 1 0>
  <Line -20 -40 40 0 #000080 2 1>
  <Line -20 -40 0 20 #000080 2 1>
  <Line -30 -30 10 0 #000080 2 1>
  <Line 20 -30 10 0 #000080 2 1>
  <Line -20 -20 40 0 #000080 2 1>
  <Line 20 -40 0 20 #000080 2 1>
  <.PortSym 30 -30 2 180>
  <.ID -50 4 SPN "1=L1=1e-6=Value=" "1=C1=1e-12=Value=" "1=R1=1=Valur=" "1=SP=0=Series/Parallel=" "1=CS=0=ShortCap=" "1=LS=0=ShortCoil=">
</Symbol>
<Components>
  <Relais S1 1 260 410 49 -26 0 0 "0.5 V" 0 "0.1 V" 0 "0" 0 "1e12" 0 "26.85" 0>
  <Relais S2 1 460 410 49 -26 0 0 "0.5 V" 0 "0.1 V" 0 "0" 0 "1e12" 0 "26.85" 0>
  <Relais S3 1 650 410 49 -26 0 0 "0.5 V" 0 "0.1 V" 0 "0" 0 "1e12" 0 "26.85" 0>
  <Relais S4 1 850 410 49 -26 0 0 "0.5 V" 0 "0.1 V" 0 "0" 0 "1e12" 0 "26.85" 0>
  <GND * 1 230 440 0 0 0 0>
  <GND * 1 430 440 0 0 0 0>
  <GND * 1 620 440 0 0 0 0>
  <GND * 1 820 440 0 0 0 0>
  <Port P2 5 490 270 -23 12 0 0 "2" 1 "analog" 0>
  <Port P1 5 290 250 -23 12 0 0 "1" 1 "analog" 0>
  <Vdc V1 1 960 340 -26 -74 0 2 "SP" 1>
  <GND * 1 990 340 0 0 0 0>
  <Inv Y1 5 560 340 -26 -28 0 2 "1 V" 0 "0" 0 "10" 0 "old" 0>
  <Sub PARLC1 1 770 520 -39 25 0 0 "parallel-lc.sch" 0 "L1" 1 "C1" 1 "R1" 1 "CS" 1 "LS" 1>
  <Sub SERLC1 1 400 520 -40 26 0 0 "series-lc.sch" 0 "L1" 1 "C1" 1 "R1" 1 "CS" 1 "LS" 1>
</Components>
<Wires>
  <230 340 230 380 "" 0 0 0 "">
  <230 340 430 340 "" 0 0 0 "">
  <430 340 430 380 "" 0 0 0 "">
  <620 340 620 380 "" 0 0 0 "">
  <620 340 820 340 "" 0 0 0 "">
  <820 340 820 380 "" 0 0 0 "">
  <490 270 490 380 "" 0 0 0 "">
  <490 270 880 270 "" 0 0 0 "">
  <880 270 880 380 "" 0 0 0 "">
  <290 250 290 380 "" 0 0 0 "">
  <290 250 680 250 "" 0 0 0 "">
  <680 250 680 380 "" 0 0 0 "">
  <820 340 930 340 "" 0 0 0 "">
  <880 440 880 520 "" 0 0 0 "">
  <800 520 880 520 "" 0 0 0 "">
  <680 440 680 520 "" 0 0 0 "">
  <680 520 740 520 "" 0 0 0 "">
  <290 440 290 520 "" 0 0 0 "">
  <490 440 490 520 "" 0 0 0 "">
  <430 520 490 520 "" 0 0 0 "">
  <290 520 370 520 "" 0 0 0 "">
  <590 340 620 340 "" 0 0 0 "">
  <430 340 530 340 "" 0 0 0 "">
</Wires>
<Diagrams>
</Diagrams>
<Paintings>
</Paintings>
