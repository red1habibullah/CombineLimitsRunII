#!/bin/bash

#parse arguments
if [ $# -ne 6 ]
    then
    echo "Usage: ./generate.sh script_name tag queue name_addon"
    exit 0
fi

script_name=$1
start_val=$2
end_val=$3
dir_name=$4
queue=$5
name_addon=$6

echo ""
echo ""
mkdir -p BSUB/${dir_name}${name_addon}
cd BSUB/${dir_name}${name_addon}

REQ=$(echo "(0)" | bc -l )
INC=$(echo "(0.1)" | bc -l)
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
