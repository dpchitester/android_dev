<Qucs Schematic 0.0.19>
<Properties>
  <View=0,0,948,800,1.5,40,237>
  <Grid=10,10,1>
  <DataSet=FloatL_NIC.dat>
  <DataDisplay=FloatL_NIC.dpl>
  <OpenDisplay=1>
  <Script=FloatL_NIC.m>
  <RunScript=0>
  <showFrame=0>
  <FrameText0=Title>
  <FrameText1=Drawn By:>
  <FrameText2=Date:>
  <FrameText3=Revision:>
</Properties>
<Symbol>
  <.ID -20 44 SUB>
  <.PortSym -30 -30 1 0>
  <.PortSym 30 -30 2 0>
  <.PortSym -30 30 3 0>
  <.PortSym 30 30 4 0>
  <Line -20 -40 40 0 #000080 2 1>
  <Line 20 -40 0 80 #000080 2 1>
  <Line -20 40 40 0 #000080 2 1>
  <Line -20 -40 0 80 #000080 2 1>
  <Line -30 -30 10 0 #000080 2 1>
  <Line 20 -30 10 0 #000080 2 1>
  <Line -30 30 10 0 #000080 2 1>
  <Line 20 30 10 0 #000080 2 1>
</Symbol>
<Components>
  <_BJT Q2N2222A_1 1 350 380 -153 -26 1 2 "npn" 0 "8.11e-14" 0 "1" 0 "1" 0 "0.5" 0 "0.225" 0 "113" 0 "24" 0 "1.06e-11" 0 "2" 0 "0" 0 "2" 0 "205" 0 "4" 0 "0" 0 "0" 0 "0.137" 0 "0.343" 0 "1.37" 0 "2.95e-11" 0 "0.75" 0 "0.33" 0 "1.52e-11" 0 "0.75" 0 "0.33" 0 "1" 0 "0" 0 "0.75" 0 "0" 0 "0.5" 0 "3.97e-10" 0 "0" 0 "0" 0 "0" 0 "8.5e-08" 0 "26.85" 0 "0" 0 "1" 0 "1" 0 "0" 0 "1" 0 "1" 0 "0" 0 "1.5" 0 "3" 0 "1.11" 0 "26.85" 0 "1" 0>
  <_BJT Q2N2222A_2 1 540 380 8 -26 0 0 "npn" 0 "8.11e-14" 0 "1" 0 "1" 0 "0.5" 0 "0.225" 0 "113" 0 "24" 0 "1.06e-11" 0 "2" 0 "0" 0 "2" 0 "205" 0 "4" 0 "0" 0 "0" 0 "0.137" 0 "0.343" 0 "1.37" 0 "2.95e-11" 0 "0.75" 0 "0.33" 0 "1.52e-11" 0 "0.75" 0 "0.33" 0 "1" 0 "0" 0 "0.75" 0 "0" 0 "0.5" 0 "3.97e-10" 0 "0" 0 "0" 0 "0" 0 "8.5e-08" 0 "26.85" 0 "0" 0 "1" 0 "1" 0 "0" 0 "1" 0 "1" 0 "0" 0 "1.5" 0 "3" 0 "1.11" 0 "26.85" 0 "1" 0>
  <GND * 1 190 170 0 0 0 0>
  <R R1 1 570 90 -26 15 0 0 "1k Ohm" 1 "26.85" 0 "0.0" 0 "0.0" 0 "26.85" 0 "US" 0>
  <GND * 1 710 90 0 0 0 1>
  <C C1 1 680 90 -26 17 0 0 "1 uF" 1 "" 0 "neutral" 0>
  <Vdc V1 1 190 140 18 -26 0 1 "10 V" 1>
  <Port P1 5 290 440 -120 -5 0 0 "1" 1 "analog" 0>
  <Port P3 5 600 440 54 -13 1 2 "3" 1 "analog" 0>
  <Tr Tr1 1 320 470 -29 38 0 0 "1" 1>
  <Tr Tr2 1 570 470 -29 38 0 0 "1" 1>
  <Tr Tr3 1 450 210 -29 38 0 0 "1" 1>
  <GND * 1 540 500 0 0 0 0>
  <GND * 1 350 500 2 -12 0 0>
  <Port P4 5 600 500 49 -8 1 2 "4" 1 "analog" 0>
  <Port P2 5 290 500 -117 -11 0 0 "2" 1 "analog" 0>
  <R R2 5 600 410 15 -26 0 1 "9e9 Ohm" 0 "26.85" 0 "0.0" 0 "0.0" 0 "26.85" 0 "US" 0>
  <GND * 1 600 380 0 0 0 2>
  <R R4 5 290 410 15 -26 0 1 "9e9 Ohm" 0 "26.85" 0 "0.0" 0 "0.0" 0 "26.85" 0 "US" 0>
  <GND * 1 290 380 0 0 0 2>
  <GND * 1 600 560 0 0 0 0>
  <R R3 5 600 530 -15 -26 0 3 "9e9 Ohm" 0 "26.85" 0 "0.0" 0 "0.0" 0 "26.85" 0 "US" 0>
  <GND * 1 290 560 0 0 0 0>
  <R R5 5 290 530 -15 -26 0 3 "9e9 Ohm" 0 "26.85" 0 "0.0" 0 "0.0" 0 "26.85" 0 "US" 0>
</Components>
<Wires>
  <480 180 540 180 "" 0 0 0 "">
  <540 180 540 320 "" 0 0 0 "">
  <190 90 190 110 "" 0 0 0 "">
  <190 90 420 90 "" 0 0 0 "">
  <420 90 420 180 "" 0 0 0 "">
  <420 90 540 90 "" 0 0 0 "">
  <600 90 630 90 "" 0 0 0 "">
  <630 90 650 90 "" 0 0 0 "">
  <350 410 350 440 "" 0 0 0 "">
  <540 410 540 440 "" 0 0 0 "">
  <380 380 490 380 "" 0 0 0 "">
  <540 320 540 350 "" 0 0 0 "">
  <490 380 510 380 "" 0 0 0 "">
  <490 320 540 320 "" 0 0 0 "">
  <490 320 490 380 "" 0 0 0 "">
  <630 90 630 240 "" 0 0 0 "">
  <480 240 630 240 "" 0 0 0 "">
  <350 240 350 350 "" 0 0 0 "">
  <350 240 420 240 "" 0 0 0 "">
</Wires>
<Diagrams>
</Diagrams>
<Paintings>
</Paintings>
