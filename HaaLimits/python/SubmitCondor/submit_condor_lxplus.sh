#!/bin/bash

export HMASS=125
export CHANNEL=TauMuTauE
                                         
for wpm in loose 
do    
    export WPM=$wpm
    for wpe in loose
    do
	export WPE=$wpe
	for r in lowmass upsilon highmass
	do
	    export MREGION=$r
	    echo $MREGION
	    if [[ $MREGION == lowmass ]]
	    then
		for m in `seq 3.6 0.1 8.5`
		do
		    export AMASS=$m
		    echo Arguments: $HMASS $AMASS $MREGION $CHANNEL $WPE $WPM
		    condor_submit condor_TauMuTauE.sub 
		done
	    fi
	    if [[ $MREGION == upsilon ]]
	    then
		for m in `seq 6 0.1 14`
		do
		    export AMASS=$m
		    echo Arguments: $HMASS $AMASS $MREGION $CHANNEL $WPE $WPM
		    condor_submit condor_TauMuTauE.sub
		done
	    fi
	    if [[ $MREGION == highmass ]]
	    then
		for m in `seq 11 0.1 25`
		do
		    export AMASS=$m
		    echo Arguments: $HMASS $AMASS $MREGION $CHANNEL $WPE $WPM
		    condor_submit condor_TauMuTauE.sub
		done
	    fi
	done
    done
done






