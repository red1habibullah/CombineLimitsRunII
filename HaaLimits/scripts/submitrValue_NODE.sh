#!/bin/bash

#parse arguments
if [ $# -ne 6 ]
    then
    echo "Usage: ./generate.sh script_name start_val end_val dir queue name_addon"
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
mkdir -p BSUB/${dir_name}${name_addon}_NODE
cd BSUB/${dir_name}${name_addon}_NODE
eos mkdir /eos/cms/store/user/ktos/rValues/${dir_name}_NODE

REQ=$(echo "(0)" | bc -l )
INC=$(echo "(0.1)" | bc -l)
while [ $REQ -eq 0 ]
do
  echo "DIRNAME    = ${dir_name}"
  echo "Script name= ${script_name}_${dir_name}_${start_val}.sh"
  test_val="$start_val"
  val=${test_val:(-1)}
  if [ "$val" == "0" ]; then
    test_val="${test_val%?}"
  fi
  echo "$start_val  $test_val $val"
  sed -e "s%MASSPOINT%${test_val}%g" -e "s%DIRNAME%${dir_name}%g" -e "s%ADDON%${name_addon}%g"  ../../${script_name}.sh > ${script_name}_${dir_name}${name_addon}_${test_val}.sh
  chmod u+x ${script_name}_${dir_name}${name_addon}_${test_val}.sh 
  bsub -q $queue ${script_name}_${dir_name}${name_addon}_${test_val}.sh
  start_val=$(echo "($start_val + $INC)" | bc -l )
  REQ=$(echo $start_val'>'$end_val | bc -l )
  echo 
  echo 
done 
cd ../../
exit 0
