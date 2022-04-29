#!/bin/tcsh

setenv EosPrefix root://cmseos.fnal.gov//eos/uscms/store/user/zhangj/HaaLimits
setenv EosDir /eos/uscms/store/user/zhangj/HaaLimits
setenv CMSSW_BASE /uscms/home/jingyu/nobackup/Haa/HaaLimits/CMSSW_10_2_13

cd $CMSSW_BASE/src
tar -zcvf ../../CMSSW.tgz ../../CMSSW_10_2_13/ --exclude="./CombineLimitsRunII/HaaLimits/python/fitParams" --exclude="*.png" --exclude="*.pdf" --exclude="*.gif" --exclude=.git --exclude="*.log" --exclude="*stderr" --exclude="*stdout" --exclude="*.pkl" --exclude="*.json"
eosrm ${EosDir}/CMSSW.tgz
xrdcp ../../CMSSW.tgz ${EosPrefix}/CMSSW.tgz
cd $CMSSW_BASE/src/CombineLimitsRunII/HaaLimits/python/SubmitCondor


#setenv TFUNC DG
#setenv TFUNC 1d
#setenv TFUNC DG_DoubleExpo_wFake
setenv TFUNC DG_DoubleExpo_Spline_wFake
#setenv TFUNC DG_DoubleExpo

setenv PREFIX mmmt_mm_h_parametric_unbinned
#setenv PREFIX mmmt_mm_h_parametric
#setenv PREFIX mmmt_mm_parametric

setenv HMASS 125
#setenv CHANNEL TauMuTauHad_2017CutV2
#setenv CHANNEL TauHadTauHad_2016
#setenv CHANNEL TauMuTauMu
#setenv CHANNEL TauMuTauHad_2017
#setenv CHANNEL TauMuTauHad_No_dR_Mtt_2017
#setenv CHANNEL TauETauHad_2016
#setenv CHANNEL TauETauHad_2017
#setenv CHANNEL TauETauHad_2018
#setenv CHANNEL TauHadTauHad_2018
#setenv CHANNEL TauHadTauHad_2016_2017_2018
setenv CHANNEL TauMuTauHad_Order2_2016_2017_2018
#setenv CHANNEL TauMuTauHad_2016_2017_2018
#setenv CHANNEL TauHadTauHad_2016_2017_2018
#setenv CHANNEL TauETauHad_2016_2017_2018
#setenv CHANNEL TauMuTauHad_TauETauHad_2016_2017_2018
#setenv CHANNEL TauMuTauE_Order_Scale_2016_2017_2018
#setenv CHANNEL TauMuTauHad_TauMuTauE_2016_2017_2018

foreach wp (MVAMedium)
#foreach wp (looseMuIso_tightEleId)
    setenv WP $wp
    foreach r (lowmass upsilon highmass)
	setenv MREGION $r
	if ($MREGION == lowmass) then
	    foreach m (`seq 3.6 0.1 8.5`)
		setenv AMASS $m
		echo Arguments: $HMASS $AMASS $MREGION $CHANNEL $WP
		condor_submit condor.jdl
	    end
	endif
	if ($MREGION == upsilon) then
	    foreach m (`seq 6 0.1 14`)
		setenv AMASS $m
		echo Arguments: $HMASS $AMASS $MREGION $CHANNEL $WP
		condor_submit condor.jdl
	    end
	endif
	if ($MREGION == highmass) then
	    foreach m (`seq 11 0.1 22`)
		setenv AMASS $m
		echo Arguments: $HMASS $AMASS $MREGION $CHANNEL $WP
		condor_submit condor.jdl
	    end
	endif
    end
end
	    
	    
	
    
