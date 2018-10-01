#!/bin/bash

#parse arguments
if [ $# -ne 3 ]
    then
    echo "Usage: ./generate.sh script_name queue addon || addon should most likely be '_rValues_NODE'"
    exit 0
fi

script_name=$1
queue=$2
name_addon=$3
node="_NODE"
prefix="../../ToCommit_OUTPUT_"
suffix=".out"

for dir in BSUB/*_NODE;
do
  dir_name_temp=${dir##*/}
  dir_name=${dir_name_temp%%${name_addon}*}
  cd BSUB/${dir_name}${name_addon}
  filename=$prefix$dir_name$node$suffix
  echo""
  echo "dir=$dir"
  echo "filename=$filename"
  echo "dir_name_temp=$dir_name_temp"
  echo "dir_name=$dir_name"

  while IFS='' read -r line || [[ -n "$line" ]]; do  
    echo "DIRNAME    = ${dir_name}"
    echo "Script name= ${script_name}_${dir_name}_${line}.sh"
    test_val="$line"
    val=${test_val:(-1)}
    if [ "$val" == "0" ]; then
      test_val="${test_val%?}"
    fi
    if [ "$test_val" == "1" ]; then
      test_val="10"
    fi
    echo "$line  $test_val $val ${script_name}_${dir_name}${name_addon}_${test_val}.sh"

    sed -e "s%MASSPOINT%${test_val}%g" -e "s%DIRNAME%${dir_name}%g" -e "s%ADDON%${name_addon}%g"  ../../${script_name}.sh > ${script_name}_${dir_name}${name_addon}_${test_val}.sh
    chmod u+x ${script_name}_${dir_name}${name_addon}_${test_val}.sh 
    bsub -q $queue ${script_name}_${dir_name}${name_addon}_${test_val}.sh
    echo 
  done < "$filename"

  cd ../../
done
exit 0
