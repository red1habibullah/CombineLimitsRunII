#!/bin/bash
cd /afs/cern.ch/work/z/zhangj/private/RunIILimits/CMSSW_10_2_13/src/

eval $(scramv1 runtime -sh)

cd CombineLimitsRunII/HaaLimits/python/


echo "Arguments passed to this script are: "
echo "  for 1 (m): $1"
echo "  for 2 (MA): $2"
echo "  for 3 (datacard): $3"
echo "  for 4 (name): $4"
echo "  for 5 (output): $5"

combine -M AsymptoticLimits -m ${1} --setParameters MA=${2} --rMin 0 --rMax 1 --freezeParameters=MA ${3} -n ${4}




