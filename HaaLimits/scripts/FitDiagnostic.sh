#!/bin/bash
#parse arguments
if [ $# -ne 2 ]
    then 
    echo "Usage: ./generate.sh  mass_point name_addon"
    exit 0
fi

mass_point=$1
name_addon=$2


eval `scramv1 runtime -sh`
source /afs/cern.ch/cms/caf/setup.sh

for dir in ../python/datacards_shape/MuMuTauTau/*;
do
  dir_name=${dir##*/}
  echo ""
  echo "${dir_name}"
  mkdir -p BSUB/${dir_name}${name_addon}

  combine -M FitDiagnostics -m ${mass_point} /afs/cern.ch/work/k/ktos/public/Plotting/CMSSW_8_1_0/src/CombineLimits/HaaLimits/python/datacards_shape/MuMuTauTau/${dir_name}/mmmt_mm_parametric_HToAAH125AX.txt -n "_${dir_name}_${mass_point}" --plots > /afs/cern.ch/work/k/ktos/public/Plotting/CMSSW_8_1_0/src/CombineLimits/HaaLimits/scripts/BSUB/${dir_name}${name_addon}/FitDiagnosticOutput_${mass_point}.out

  for i in *.png;
  do
     name=${i%%.png}
     cp $i /afs/cern.ch/work/k/ktos/public/Plotting/CMSSW_8_1_0/src/CombineLimits/HaaLimits/scripts/BSUB/${dir_name}${name_addon}/${name}_${dir_name}_${mass_point}.png
  done
done
exit 0
