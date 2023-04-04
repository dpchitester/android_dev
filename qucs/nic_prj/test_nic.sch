<Qucs Schematic 0.0.22>
<Properties>
  <View=-20,426,1243,1325,1.0285,0,0>
  <Grid=10,10,1>
  <DataSet=test_nic.dat>
  <DataDisplay=test_nic.dpl>
  <OpenDisplay=1>
  <Script=test_nic.m>
  <RunScript=0>
  <showFrame=0>
  <FrameText0=Title>
  <FrameText1=Drawn By:>
  <FrameText2=Date:>
  <FrameText3=Revision:>
</Properties>
<Symbol>
</Symbol>
<Components>
  <.DC DC1 1 980 520 0 52 0 0 "26.85" 0 "0.001" 0 "1 pA" 0 "1 uV" 0 "no" 0 "150" 0 "no" 0 "none" 0 "CroutLU" 0>
  <Sub S11_Probe1 1 170 520 80 -54 1 2 "S11_Probe.sch" 0 "50" 1>
  <Sub S21_Probe1 1 790 630 -218 -157 0 0 "S21_Probe.sch" 0 "50" 1>
  <GND * 1 270 790 0 0 0 0>
  <.AC AC1 1 975 635 0 52 0 0 "log" 1 "1e6" 1 "30e6" 1 "30" 1 "no" 0>
  <L L1 1 330 880 10 -26 0 1 "L1" 0 "" 0>
  <C C1 1 390 880 17 -26 0 1 "C1" 0 "" 0 "neutral" 0>
  <R R4 5 300 790 -26 15 0 0 "9e9" 1 "26.85" 0 "0.0" 0 "0.0" 0 "26.85" 0 "US" 0>
  <SPICE X1 1 320 640 -26 -77 0 0 "C:/projects/python-win-rf/temp.cir" 0 "_netp1,_netp2" 0 "no" 0 "none" 0>
  <GND * 1 320 670 0 0 0 0>
  <GND * 1 710 740 0 0 0 0>
  <R_SPICE R2 1 710 700 15 -26 0 1 "50" 1 "" 0 "" 0 "" 0 "" 0>
  <GND * 1 580 780 0 0 0 0>
  <R R3 5 550 780 -26 15 0 0 "9e9" 1 "26.85" 0 "0.0" 0 "0.0" 0 "26.85" 0 "US" 0>
  <R R5 1 470 580 -37 -79 0 0 "1 GOhm" 1 "26.85" 0 "0.0" 0 "0.0" 0 "26.85" 0 "US" 0>
  <R_SPICE R1 1 170 640 -32 -73 0 2 "50" 1 "" 0 "" 0 "" 0 "" 0>
  <GND * 1 130 730 0 0 0 0>
  <S4Q_V V1 1 130 700 -57 -37 0 1 "dc 0 ac 1" 0 "" 0 "" 0 "" 0 "" 0>
  <Sub NIC1 1 470 670 -20 44 0 0 "FloatL_NIC.sch" 0>
  <Eqn Eqn1 5 700 830 -47 20 0 0 "RatioLC=5e6" 1 "Fres=5e6" 1 "L1=sqrt(RatioLC)/(2*pi*Fres)" 1 "C1=1/(2*pi*Fres*sqrt(RatioLC))" 1 "VSWR=abs((1+abs(v(nS11)))/(1-abs(v(nS11))))" 1 "yes" 0>
</Components>
<Wires>
  <710 550 710 640 "" 0 0 0 "">
  <250 540 250 640 "" 0 0 0 "">
  <230 540 250 540 "" 0 0 0 "">
  <250 640 290 640 "" 0 0 0 "">
  <330 700 440 700 "" 0 0 0 "">
  <330 700 330 790 "" 0 0 0 "">
  <330 850 390 850 "" 0 0 0 "">
  <330 910 390 910 "" 0 0 0 "">
  <330 790 330 850 "" 0 0 0 "">
  <440 580 440 640 "" 0 0 0 "">
  <500 580 500 640 "" 0 0 0 "">
  <350 640 440 640 "" 0 0 0 "">
  <500 640 710 640 "" 0 0 0 "">
  <710 730 710 740 "" 0 0 0 "">
  <710 640 710 670 "" 0 0 0 "">
  <330 910 330 930 "" 0 0 0 "">
  <330 930 520 930 "" 0 0 0 "">
  <500 700 520 700 "" 0 0 0 "">
  <520 700 520 780 "" 0 0 0 "">
  <520 780 520 930 "" 0 0 0 "">
  <200 640 250 640 "" 0 0 0 "">
  <130 640 140 640 "" 0 0 0 "">
  <130 640 130 670 "" 0 0 0 "">
  <110 540 110 540 "nS11" 20 490 0 "">
  <830 550 830 550 "nS21" 860 490 0 "">
</Wires>
<Diagrams>
</Diagrams>
<Paintings>
</Paintings>
