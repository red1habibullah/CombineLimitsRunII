#!/bin/bash

#countXRANGE1=$(echo "(5.00)" | bc -l )
countXRANGE2=$(echo "(7.7)" | bc -l )
#countXRANGE3=$(echo "(12.0)" | bc -l )

INCREMENT=$(echo "(.1)" | bc -l)

#endXRANGE1=$(echo "(8.2)" | bc -l )
endXRANGE2=$(echo "(12.4)" | bc -l )
#endXRANGE3=$(echo "(21.0)" | bc -l )
REQ=0



COUNT=$countXRANGE2
END=$endXRANGE2
while [ $REQ -eq 0  ]; do
  name=${COUNT%.*}p${COUNT##*.}
  combine -M AsymptoticLimits -m $COUNT datacards_shape/MuMuTauTau/SkinnySig_SetLambda_6p5to11to14/XRANGE2/mmmt_mm_parametric_HToAAH125AX.txt -n "HToAAH125A$name" > OUTPUT_$name.out
  #mv *.root rValueFiles/
  #mv *.out rValueFiles/Output/
  echo "COUNT= $COUNT"
  COUNT=$(echo "($COUNT + $INCREMENT)" | bc -l )
  REQ=$(echo $COUNT'>'$END | bc -l )
done
exit 0
