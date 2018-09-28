#!/bin/bash

export SCRAM_ARCH=slc6_amd64_gcc481
cd /afs/cern.ch/work/k/ktos/public/Plotting/CMSSW_8_1_0/src/CombineLimits/HaaLimits/python
eval `scramv1 runtime -sh`
cd -
source /afs/cern.ch/cms/caf/setup.sh
echo ""
echo "THIS MASS POINT IS:   MASSPOINT"
echo ""
combine -M AsymptoticLimits -m MASSPOINT /afs/cern.ch/work/k/ktos/public/Plotting/CMSSW_8_1_0/src/CombineLimits/HaaLimits/python/datacards_shape/MuMuTauTau/DIRNAME/mmmt_mm_parametric_HToAAH125AX.txt -n "HToAAH125AMASSPOINT_DIRNAMEADDON_NODE" 
echo "PWD"
pwd
eos  cp higgsCombineHToAAH125*_DIRNAMEADDON_NODE.AsymptoticLimits.mH*.root /eos/cms/store/user/ktos/rValues/DIRNAME_NODE/
exit 0
