#!/bin/bash

for i in ../../HaaLimits/python/rValueFiles/M*;
do
  dirname=${i##*rValueFiles/}
  echo $dirname
#  for j in $i/*;
#  do
#    sample=${j##*/}
#    echo "   $sample"
  sed -i -e "s|DIRNAME|${dirname}|g"  ../python/gettingLimitPlotsKyleLOOP.py
  python ../python/gettingLimitPlotsKyleLOOP.py > OUTPUT_${dirname}_Smoothing.out
  sed -i -e "s|${dirname}|DIRNAME|g"  ../python/gettingLimitPlotsKyleLOOP.py
#  done
done
                                                                                                                                  

