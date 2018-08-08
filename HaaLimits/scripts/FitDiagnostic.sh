#!/bin/bash

export SCRAM_ARCH=slc6_amd64_gcc481
cd /afs/cern.ch/work/k/ktos/public/Plotting/CMSSW_8_1_0/src/CombineLimits/HaaLimits/python
eval `scramv1 runtime -sh`
source /afs/cern.ch/cms/caf/setup.sh
combine -M FitDiagnostics -m MASSPOINT /afs/cern.ch/work/k/ktos/public/Plotting/CMSSW_8_1_0/src/CombineLimits/HaaLimits/python/datacards_shape/MuMuTauTau/DIRNAME/mmmt_mm_parametric_HToAAH125AX.txt -n "_DIRNAME"
cp *DIRNAME* /afs/cern.ch/work/k/ktos/public/Plotting/CMSSW_8_1_0/src/CombineLimits/HaaLimits/python/figures/HaaLimits_DIRNAME/
cp *DIRNAME* /afs/cern.ch/work/k/ktos/public/Plotting/CMSSW_8_1_0/src/CombineLimits/HaaLimits/python/figures/HaaLimits2D_DIRNAME/
exit 0
