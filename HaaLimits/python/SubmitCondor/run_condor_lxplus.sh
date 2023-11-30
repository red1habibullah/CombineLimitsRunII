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

#combine -M AsymptoticLimits -v 2 --noFitAsimov -m ${1} --setParameters MA=${2} --rMin -3 --rMax 3 --X-rtd TMCSO_AdaptivePseudoAsimov=0 --X-rtd TMCSO_PseudoAsimov=0 --freezeParameters=MA,higgs_theory,pdf_alpha,minbias_13TeV_2018,CMS_eff_m_2018 ${3} -n ${4}
combine -M AsymptoticLimits -v 2 --noFitAsimov -m ${1} --setParameters MA=${2} --rMin -3 --rMax 3 --X-rtd TMCSO_AdaptivePseudoAsimov=0 --X-rtd TMCSO_PseudoAsimov=0 --freezeParameters=MA ${3} -n ${4}

#combine -M AsymptoticLimits -v 2 --noFitAsimov -m ${1} --setParameters MA=${2} --rMin -3 --rMax 3 --freezeParameters=MA ${3} -n ${4}

#combine -M AsymptoticLimits -v 2 -m ${1} --setParameters MA=${2} --rMin -3 --rMax 3 --freezeParameters=MA ${3} -n ${4}

mv ${5} testPPonlyNov2023
