#!/bin/tcsh

#setenv channel TauETauHad
#setenv channel TauHadTauHad
setenv channel TauMuTauHad_Order2
#setenv channel TauMuTauE_Order_Scale

setenv prefix mmmt_mm_h_parametric_unbinned
#setenv prefix mmmt_mm_parametric

setenv wp MVAMedium
#setenv wp looseMuIso_tightEleId

#setenv method DG_DoubleExpo_wFake
#setenv method 1d
setenv method DG_DoubleExpo_Spline_wFake

foreach region (lowmass upsilon highmass)
    python combineChannels.py ${prefix}_${region}_${channel}_2016_2017_2018_${wp}_${method}_hm125_amX.txt ${prefix}_${region}_${channel}_2016_${wp}_${method}_hm125_amX.txt ${prefix}_${region}_${channel}_2017_${wp}_${method}_hm125_amX.txt ${prefix}_${region}_${channel}_2018_${wp}_${method}_hm125_amX.txt
    
    #python combineChannels.py mmmt_mm_h_parametric_unbinned_${region}_TauMuTauHad_TauMuTauE_2016_2017_2018_MVAMedium_DG_DoubleExpo_hm125_amX.txt mmmt_mm_h_parametric_unbinned_${region}_TauMuTauHad_Order2_2016_2017_2018_MVAMedium_DG_DoubleExpo_wFake_hm125_amX.txt mmmt_mm_parametric_${region}_TauMuTauE_Order_Scale_2016_2017_2018_looseMuIso_tightEleId_1d_hm125_amX.txt   
end
