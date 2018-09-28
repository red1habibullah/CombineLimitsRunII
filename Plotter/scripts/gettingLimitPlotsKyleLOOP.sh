#!/bin/bash

#for i in ../../HaaLimits/python/rValues/*SEP2*;
for i in /eos/cms/store/user/ktos/rValues/*;
do
  dirname=${i##*rValues/}
  echo ""
  echo ""
  echo $dirname
  sed -i -e "s|DIRNAME|${dirname}|g"  ../python/gettingLimitPlotsKyleLOOP.py
  python ../python/gettingLimitPlotsKyleLOOP.py > OUTPUT_${dirname}_Smoothing.out
  sed -i -e "s|${dirname}|DIRNAME|g"  ../python/gettingLimitPlotsKyleLOOP.py
done
                                                                                                                                  

