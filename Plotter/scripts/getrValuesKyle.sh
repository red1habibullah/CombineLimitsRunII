#!/bin/bash

COUNT=$(echo "(5.0)" | bc -l )
INCREMENT=$(echo "(.1)" | bc -l)
END=$(echo "(21.0)" | bc -l )
REQ=0
while [ $REQ -eq 0  ]; do
  name=${COUNT%.*}p${COUNT##*.}
  combine -M AsymptoticLimits -m $COUNT datacards_shape/MuMuTauTau/UpConst_SetLambda_8p5to11p0_v4/mmmt_mm_parametric_HToAAH125AX.txt -n "HToAAH125A$name" > OUTPUT_$name.out
  echo "COUNT= $COUNT"
  COUNT=$(echo "($COUNT + $INCREMENT)" | bc -l )
  REQ=$(echo $COUNT'>'$END | bc -l )
done
exit 0
