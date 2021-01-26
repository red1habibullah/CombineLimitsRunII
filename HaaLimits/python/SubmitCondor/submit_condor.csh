#!/bin/tcsh

setenv EosPrefix root://cmseos.fnal.gov//eos/uscms/store/user/zhangj/HaaLimits
setenv EosDir /eos/uscms/store/user/zhangj/HaaLimits
setenv CMSSW_BASE /uscms/home/jingyu/nobackup/Haa/HaaLimits/CMSSW_10_2_13

cd $CMSSW_BASE/src
tar -zcvf ../../CMSSW.tgz ../../CMSSW_10_2_13/ --exclude="./CombineLimitsRunII/HaaLimits/python/fitParams" --exclude="*.png" --exclude="*.pdf" --exclude="*.gif" --exclude=.git --exclude="*.log" --exclude="*stderr" --exclude="*stdout"
eosrm ${EosDir}/CMSSW.tgz
xrdcp ../../CMSSW.tgz ${EosPrefix}/CMSSW.tgz
cd $CMSSW_BASE/src/CombineLimitsRunII/HaaLimits/python/SubmitCondor


setenv HMASS 125
setenv CHANNEL TauHadTauHad

#foreach wp (0p3 0p5 0p7)
foreach wp (0p3)
    setenv WP $wp
    #foreach MREGION (lowmass upsilon highmass)
    foreach r (lowmass)
	setenv MREGION $r
	if ($MREGION == lowmass) then
	    foreach m (`seq 3.6 0.1 8.5`)
		setenv AMASS $m
		echo Arguments: $HMASS $AMASS $MREGION $CHANNEL $WP
		condor_submit condor.jdl
	    end
	endif
    end
end
	    
	    
	
    
