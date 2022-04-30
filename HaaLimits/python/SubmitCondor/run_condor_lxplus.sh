#!/bin/bash
cd /afs/cern.ch/user/r/rhabibul/CombineRunII_dev/CMSSW_10_2_13/src/

eval $(scramv1 runtime -sh)

cd CombineLimitsRunII/HaaLimits/python/


echo "Arguments passed to this script are: "
echo "  for 1 (m): $1"
echo "  for 2 (MA): $2"
echo "  for 3 (datacard): $3"
echo "  for 4 (name): $4"
echo "  for 5 (output): $5"


combine -M AsymptoticLimits -m ${1} --setParameters MA=${2} --freezeParameters=MA ${3} -n ${4}

rm /eos/cms/store/user/rhabibul/HaaLimits/${5}

xrdcp ${5} root://eoscms.cern.ch//store/user/rhabibul/HaaLimits/${5}



