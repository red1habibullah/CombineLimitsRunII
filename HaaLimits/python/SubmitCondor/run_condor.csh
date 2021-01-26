#!/bin/tcsh
echo "Starting job on " `date` #Date/time of start of job
echo "Running on: `uname -a`" #Condor job is running on this node
echo "System software: `cat /etc/redhat-release`" #Operating System on that node
source /cvmfs/cms.cern.ch/cmsset_default.csh  ## if a bash script, use .sh instead of .csh
echo ">>> copying code package from EOS to local..."
xrdcp root://cmseos.fnal.gov//eos/uscms/store/user/zhangj/HaaLimits/CMSSW.tgz CMSSW.tgz

echo ">>> unzipping the package locally..."
tar -xf CMSSW.tgz
echo ">>> finish unzipping the package!"
rm CMSSW.tgz

export SCRAM_ARCH=sl7_amd64_gcc700
cd CMSSW_10_2_13/src/
scramv1 b ProjectRename
eval `scramv1 runtime -csh` # cmsenv is an alias not on the workers
cd CombineLimitsRunII/HaaLimits/python/

echo "Arguments passed to this script are: "
echo "  for 1 (m): $1"
echo "  for 2 (MA): $2"
echo "  for 3 (datacard): $3"
echo "  for 4 (name): $4"
echo "  for 5 (output): $5"

combine -M AsymptoticLimits -m ${1} --setParameters MA=${2} ${3} -n ${4}
xrdcp ${5} root://cmseos.fnal.gov//eos/uscms/store/user/zhangj/HaaLimits/${5}

cd ${_CONDOR_SCRATCH_DIR}
rm -rf CMSSW_10_2_13
