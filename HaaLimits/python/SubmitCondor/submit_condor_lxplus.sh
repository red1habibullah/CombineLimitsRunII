#!/bin/bash

export HMASS=125
#export CHANNEL=TauMuTauE
#export CHANNEL=TauHadTauHad_2016_2017_2018
                                         
export PREFIX=mmmt_mm_h_parametric_unbinned


#export CHANNEL=TauMuTauHad_TauETauHad_TauHadTauHad_TauMuTauE_2016_2017_2018
#export CHANNEL=TauMuTauHad_TauETauHad_TauHadTauHad_TauMuTauE_2018
#export CHANNEL=TauMuTauMu_TauMuTauE_TauMuTauHad_TauETauHad_TauHadTauHad_2016_2017_2018
#export CHANNEL=TauHadTauHad_2016_2017_2018
#export CHANNEL=TauHadTauHad_V3_2016
export CHANNEL=TauMuTauHad_V2_2018
#export CHANNEL=TauETauHad_2018


#export TFUNC=DG_DoubleExpo
#export TFUNC=DG_DoubleExpo_yRange_Spline_wFakeTauScaleJEC
export TFUNC=DG_DoubleExpo_yRange_wFakeTauScale
#export TFUNC=DG_DoubleExpo_Spline_wFakeTauScale

for wp in MVAMedium
do    
    export WP=$wp
    for r in lowmass upsilon highmass
    do
	export MREGION=$r
	echo $MREGION
	if [[ $MREGION == lowmass ]]
	then
	    for m in `seq 3.6 0.1 8.5`
	    do
		export AMASS=$m
		echo Arguments: $HMASS $AMASS $MREGION $CHANNEL $WP
		condor_submit condor_lxplus.sub 
		done
	fi
	if [[ $MREGION == upsilon ]]
	then
	    for m in `seq 6 0.1 14`
	    do
		export AMASS=$m
		echo Arguments: $HMASS $AMASS $MREGION $CHANNEL $WP
		condor_submit condor_lxplus.sub
	    done
	fi
	if [[ $MREGION == highmass ]]
	then
	    for m in `seq 11 0.1 22`
	    do
		export AMASS=$m
		echo Arguments: $HMASS $AMASS $MREGION $CHANNEL $WP
		condor_submit condor_lxplus.sub
	    done
	fi
    done
done






