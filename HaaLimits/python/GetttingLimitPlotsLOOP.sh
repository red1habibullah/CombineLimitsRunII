#!/bin/bash

for i in rValueFiles/S*;
do
  dirname=${i##*rValueFiles/}
  echo $dirname
  for j in $i/*;
  do
    sample=${j##*/}
    echo "   $sample"
    sed -i -e "s|DIRNAME|${dirname}|g" -e "s|SAMPLE|${sample}|g" GetttingLimitPlotsLOOP.py
    python GetttingLimitPlotsLOOP.py > OUTPUT_${dirname}_${sample}.out
    sed -i -e "s|${dirname}|DIRNAME|g" -e "s|${sample}|SAMPLE|g" GetttingLimitPlotsLOOP.py
  done
done
                                                                                                                                  

