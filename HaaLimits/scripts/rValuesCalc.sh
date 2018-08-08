#!/bin/bash

export SCRAM_ARCH=slc6_amd64_gcc481
cd /afs/cern.ch/work/k/ktos/public/Plotting/CMSSW_8_1_0/src/CombineLimits/HaaLimits/python
eval `scramv1 runtime -sh`
source /afs/cern.ch/cms/caf/setup.sh
echo ""
echo "THIS MASS POINT IS:   MASSPOINT"
echo ""
combine -M AsymptoticLimits -m MASSPOINT /afs/cern.ch/work/k/ktos/public/Plotting/CMSSW_8_1_0/src/CombineLimits/HaaLimits/python/datacards_shape/MuMuTauTau/DIRNAME/mmmt_mm_parametric_HToAAH125AX.txt -n "HToAAH125AMASSPOINT_DIRNAMEADDON" 
mkdir /afs/cern.ch/work/k/ktos/public/Plotting/CMSSW_8_1_0/src/CombineLimits/HaaLimits/python/rValues/DIRNAME/
cp higgsCombineHToAAH125AMASSPOINT_DIRNAME.AsymptoticLimits.mHMASSPOINT.root /afs/cern.ch/work/k/ktos/public/Plotting/CMSSW_8_1_0/src/CombineLimits/HaaLimits/python/rValues/DIRNAME/
exit 0
