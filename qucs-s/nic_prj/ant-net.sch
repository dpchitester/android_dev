<Qucs Schematic 0.0.22>
<Properties>
  <View=172,210,975,741,1.72105,39,0>
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
  <.ID -20 44 CLNET "1=V1=1e-6=Value=" "1=R1=1=Resistor=">
  <.PortSym -30 -30 1 0>
  <.PortSym -30 30 3 0>
  <Line -20 -40 40 0 #000080 2 1>
  <Line 20 -40 0 80 #000080 2 1>
  <Line -20 40 40 0 #000080 2 1>
  <Line -20 -40 0 80 #000080 2 1>
  <Line -30 -30 10 0 #000080 2 1>
  <Line 20 -30 10 0 #000080 2 1>
  <Line -30 30 10 0 #000080 2 1>
  <.PortSym 30 -30 2 180>
</Symbol>
<Components>
  <Relais S1 1 260 410 49 -26 0 0 "0.5 V" 0 "0.1 V" 0 "0" 0 "1e12" 0 "26.85" 0>
  <Relais S2 1 460 410 49 -26 0 0 "0.5 V" 0 "0.1 V" 0 "0" 0 "1e12" 0 "26.85" 0>
  <Relais S3 1 650 410 49 -26 0 0 "0.5 V" 0 "0.1 V" 0 "0" 0 "1e12" 0 "26.85" 0>
  <Relais S4 1 850 410 49 -26 0 0 "0.5 V" 0 "0.1 V" 0 "0" 0 "1e12" 0 "26.85" 0>
  <R R1 5 330 410 15 -26 0 1 "9e9 Ohm" 0 "26.85" 0 "0.0" 0 "0.0" 0 "26.85" 0 "US" 0>
  <R R2 5 530 410 15 -26 0 1 "9e9 Ohm" 0 "26.85" 0 "0.0" 0 "0.0" 0 "26.85" 0 "US" 0>
  <R R3 5 720 410 15 -26 0 1 "9e9 Ohm" 0 "26.85" 0 "0.0" 0 "0.0" 0 "26.85" 0 "US" 0>
  <R R4 5 920 410 15 -26 0 1 "9e9 Ohm" 0 "26.85" 0 "0.0" 0 "0.0" 0 "26.85" 0 "US" 0>
  <GND * 1 230 440 0 0 0 0>
  <GND * 1 430 440 0 0 0 0>
  <GND * 1 620 440 0 0 0 0>
  <GND * 1 820 440 0 0 0 0>
  <Port P2 5 490 270 -23 12 0 0 "2" 1 "analog" 0 "v" 0 "" 0>
  <Port P1 5 290 250 -23 12 0 0 "1" 1 "analog" 0 "v" 0 "" 0>
  <Port P3 5 820 340 -91 -23 0 3 "3" 1 "analog" 0 "v" 0 "" 0>
  <Sub CAP1 1 400 520 -20 14 0 0 "capacitor.sch" 0 "R1" 1 "V1" 1>
  <Sub IND1 1 790 530 -20 14 0 0 "inductor.sch" 0 "R1" 1 "V1" 1>
  <GND * 1 570 430 0 0 0 0>
  <Vdc V1 1 570 400 -32 64 0 1 "Vinv" 1>
  <Eqn Eqn1 1 570 560 -47 20 0 0 "Vinv=1-Vin" 1 "yes" 0>
</Components>
<Wires>
  <290 380 330 380 "" 0 0 0 "">
  <290 440 330 440 "" 0 0 0 "">
  <490 380 530 380 "" 0 0 0 "">
  <490 440 530 440 "" 0 0 0 "">
  <680 380 720 380 "" 0 0 0 "">
  <680 440 720 440 "" 0 0 0 "">
  <880 380 920 380 "" 0 0 0 "">
  <880 440 920 440 "" 0 0 0 "">
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
  <880 440 880 530 "" 0 0 0 "">
  <820 530 880 530 "" 0 0 0 "">
  <680 440 680 530 "" 0 0 0 "">
  <680 530 760 530 "" 0 0 0 "">
  <490 440 490 520 "" 0 0 0 "">
  <430 520 490 520 "" 0 0 0 "">
  <290 440 290 520 "" 0 0 0 "">
  <290 520 370 520 "" 0 0 0 "">
  <430 340 570 340 "" 0 0 0 "">
  <570 340 570 370 "" 0 0 0 "">
  <620 340 620 340 "Vin" 630 290 0 "">
</Wires>
<Diagrams>
</Diagrams>
<Paintings>
</Paintings>
