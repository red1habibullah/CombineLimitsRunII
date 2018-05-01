#!/bin/bash

countXRANGE1=$(echo "(5.00)" | bc -l )
#countXRANGE2=$(echo "(8.3)" | bc -l )
#countXRANGE3=$(echo "(14.9)" | bc -l )

INCREMENT=$(echo "(.1)" | bc -l)

endXRANGE1=$(echo "(7.6)" | bc -l )
#endXRANGE2=$(echo "(14.0)" | bc -l )
#endXRANGE3=$(echo "(21.0)" | bc -l )
REQ=0



COUNT=$countXRANGE1
END=$endXRANGE1
while [ $REQ -eq 0  ]; do
  name=${COUNT%.*}p${COUNT##*.}
  combine -M AsymptoticLimits -m $COUNT datacards_shape/MuMuTauTau/SkinnySig_SetLambda_6p5to11to14/XRANGE1/mmmt_mm_parametric_HToAAH125AX.txt -n "HToAAH125A$name" > OUTPUT_$name.out
  #mv *.root rValueFiles/
  #mv *.out rValueFiles/Output/
  echo "COUNT= $COUNT"
  COUNT=$(echo "($COUNT + $INCREMENT)" | bc -l )
  REQ=$(echo $COUNT'>'$END | bc -l )
done
exit 0
