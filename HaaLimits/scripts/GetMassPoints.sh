
for dir in BSUB/*;
do
  echo ""
  echo $dir
  cd $dir
  mkdir Resubmitted

  for i in LSFJOB_*; 
  do 
    for j in $(grep -lr "SysError" $i);
    do 
      grep_line=$(grep -r MASS  $j)
      mass_point=${grep_line##*IS:   }
      dir_name=${dir##*/}
      dir_name_noAdd=${dir_name%%_rValue*}
      echo "$mass_point  $dir_name  $dir_name_noAdd"
      echo " rValuesCalc_${dir_name}_${mass_point}.sh"
      sed -e "s%MASSPOINT%${mass_point}%g" -e "s%DIRNAME%${dir_name_noAdd}%g" -e "s%ADDON%_rValues%g"  ../../rValuesCalc.sh > rValuesCalc_${dir_name}_${mass_point}.sh
      bsub -q 2nd rValuesCalc_${dir_name}_${mass_point}.sh
      mv ${j%%/*} Resubmitted/
    done
  done

  for i in LSFJOB_*;
  do
    for j in $(grep -lr "LandS" $i);
    do
      grep_line=$(grep -r MASS  $j)
      mass_point=${grep_line##*IS:   }
      dir_name=${dir##*/}
      dir_name_noAdd=${dir_name%%_rValue*}
      echo "$mass_point  $dir_name  $dir_name_noAdd"
      echo " rValuesCalc_${dir_name}_${mass_point}.sh"
      sed -e "s%MASSPOINT%${mass_point}%g" -e "s%DIRNAME%${dir_name_noAdd}%g" -e "s%ADDON%_rValues%g"  ../../rValuesCalc.sh > rValuesCalc_${dir_name}_${mass_point}.sh
      bsub -q 2nd rValuesCalc_${dir_name}_${mass_point}.sh
      mv ${j%%/*} Resubmitted/
    done
  done

  cd -
done
exit 0
