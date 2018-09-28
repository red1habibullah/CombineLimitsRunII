#!/bin/bash

#parse arguments
if [ $# -ne 6 ]
    then
    echo "Usage: ./generate.sh script_name startval endval stepval queue name_addon"
    exit 0
fi

script_name=$1
start_val=$2
end_val=$3
step_val=$4
queue=$5
name_addon=$6

for dir in ../python/datacards_shape/MuMuTauTau/*mu_AUG19*;
do
  dir_name=${dir##*/}
  curr_val=$(echo "($start_val)" | bc -l )
  echo ""
  mkdir -p BSUB/${dir_name}${name_addon}
  cd BSUB/${dir_name}${name_addon}
  
  REQ=$(echo "(0)" | bc -l )
  INC=$(echo "($step_val)" | bc -l)
  while [ $REQ -eq 0 ]
  do
    echo "DIRNAME    = ${dir_name}"
    echo "Script name= ${script_name}_${dir_name}_${curr_val}.sh"
    sed -e "s%MASSPOINT%${curr_val}%g" -e "s%DIRNAME%${dir_name}%g" -e "s%ADDON%${name_addon}%g"  ../../${script_name}.sh > ${script_name}_${dir_name}${name_addon}_${curr_val}.sh
    chmod u+x ${script_name}_${dir_name}${name_addon}_${curr_val}.sh 
    bsub -q $queue ${script_name}_${dir_name}${name_addon}_${curr_val}.sh
    curr_val=$(echo "($curr_val + $INC)" | bc -l )
    REQ=$(echo $curr_val'>'$end_val | bc -l )
    echo 
  done 
  
  cd ../../
done
exit 0
