#!/bin/bash

#parse arguments
if [ $# -ne 7 ]
    then
    echo "Usage: ./generate.sh script_name star_val end_val step_val dir_name queue name_addon"
    exit 0
fi

script_name=$1
start_val=$2
end_val=$3
step_val=$4
dir_name=$5
queue=$6
name_addon=$7

echo ""
echo ""
mkdir -p BSUB/${dir_name}${name_addon}
cd BSUB/${dir_name}${name_addon}

REQ=$(echo "(0)" | bc -l )
INC=$(echo "($start_val)" | bc -l)
while [ $REQ -eq 0 ]
do
  echo "DIRNAME    = ${dir_name}"
  echo "Script name= ${script_name}_${dir_name}_${start_val}.sh"
  sed -e "s%MASSPOINT%${start_val}%g" -e "s%DIRNAME%${dir_name}%g" -e "s%ADDON%${name_addon}%g"  ../../${script_name}.sh > ${script_name}_${dir_name}${name_addon}_${start_val}.sh
  chmod u+x ${script_name}_${dir_name}${name_addon}_${start_val}.sh 
  bsub -q $queue ${script_name}_${dir_name}${name_addon}_${start_val}.sh
  start_val=$(echo "($start_val + $INC)" | bc -l )
  REQ=$(echo $start_val'>'$end_val | bc -l )
  echo 
  echo 
done 
cd ../../
exit 0
