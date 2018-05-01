#!/bin/bash

for i in rValueFiles/U*;
do
  dirname=${i##*rValueFiles/}
  echo $dirname
#  for j in $i/*;
#  do
#    sample=${j##*/}
#    echo "   $sample"
  sed -i -e "s|DIRNAME|${dirname}|g"  GetttingLimitPlotsLOOP.py
  python GetttingLimitPlotsLOOP.py > OUTPUT_${dirname}_${sample}.out
  sed -i -e "s|${dirname}|DIRNAME|g"  GetttingLimitPlotsLOOP.py
#  done
done
                                                                                                                                  

