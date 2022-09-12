#!/bin/bash

export HMASS=1000
#export CHANNEL=TauMuTauE
#export CHANNEL=TauHadTauHad_2016_2017_2018
                                         
export PREFIX=mmmt_mm_h_parametric_unbinned


#export CHANNEL=TauMuTauHad_TauETauHad_TauHadTauHad_TauMuTauE_2016_2017_2018
#export CHANNEL=TauMuTauHad_TauETauHad_TauHadTauHad_TauMuTauE_2018
#export CHANNEL=TauMuTauMu_TauMuTauE_TauMuTauHad_TauETauHad_TauHadTauHad_2016_2017_2018
#export CHANNEL=TauHadTauHad_2016_2017_2018
export CHANNEL=TauHadTauHad_V3_2018
#export CHANNEL=TauMuTauHad_V2_2016
#export CHANNEL=TauETauHad_2018


#export TFUNC=DG_DoubleExpo
export TFUNC=DG_DoubleExpo_yRange_Spline_wFakeTauScaleJEC
#export TFUNC=DG_DoubleExpo_yRange_wFakeTauScale
#export TFUNC=DG_DoubleExpo_Spline_wFakeTauScale

for wp in MVAMedium
do    
    export WP=$wp
    for r in upsilon highmass
    do
	export MREGION=$r
	echo $MREGION
	if [[ $MREGION == upsilon ]]
	then
	    for m in `seq 6 1 14`
	    do
		export AMASS=$m
		echo Arguments: $HMASS $AMASS $MREGION $CHANNEL $WP
		condor_submit condor_lxplus.sub
	    done
	fi
	if [[ $MREGION == highmass ]]
	then
	    for m in `seq 11 1 40`
	    do
		export AMASS=$m
		echo Arguments: $HMASS $AMASS $MREGION $CHANNEL $WP
		condor_submit condor_lxplus.sub
	    done
	fi
    done
done






