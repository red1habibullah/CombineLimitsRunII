#!/bin/tcsh

#setenv channel TauETauHad
setenv channel TauHadTauHad_V3
#setenv channel TauMuTauHad_V2
#setenv channel TauETauHad
#setenv channel TauMuTauE_Order_Scale

setenv prefix mmmt_mm_h_parametric_unbinned
#setenv prefix mmmt_mm_parametric

setenv wp MVAMedium
#setenv wp looseMuIso_tightEleId

#setenv method DG_DoubleExpo_wFake
#setenv method 1d
#setenv method DG_DoubleExpo_yRange_wFakeTauScale
#setenv method DG_DoubleExpo_Spline_wFakeTauScale
setenv method DG_DoubleExpo_yRange_Spline_wFakeTauScaleJEC

setenv year 2018

foreach region (lowmass upsilon highmass)
    ### combine same year different channels
    #python combineChannels.py ${prefix}_${region}_${channel}_2016_2017_2018_${wp}_${method}_hm125_amX.txt ${prefix}_${region}_${channel}_2016_${wp}_${method}_hm125_amX.txt ${prefix}_${region}_${channel}_2017_${wp}_${method}_hm125_amX.txt ${prefix}_${region}_${channel}_2018_${wp}_${method}_hm125_amX.txt
    

    ### combine same year different channels
    python combineChannels.py mmmt_mm_h_parametric_unbinned_${region}_TauMuTauMu_TauMuTauE_TauMuTauHad_TauETauHad_TauHadTauHad_${year}_MVAMedium_DG_DoubleExpo_hm125_amX.txt mmmt_mm_h_parametric_unbinned_${region}_TauMuTauHad_V2_${year}_MVAMedium_DG_DoubleExpo_yRange_wFakeTauScale_hm125_amX.txt  mmmt_mm_parametric_${region}_TauMuTauE_Order_Scale_${year}_looseMuIso_tightEleId_1d_Spline_wFakeModelling_hm125_amX.txt mmmt_mm_h_parametric_unbinned_${region}_TauETauHad_${year}_MVAMedium_DG_DoubleExpo_Spline_wFakeTauScale_hm125_amX.txt mmmt_mm_h_parametric_unbinned_${region}_TauHadTauHad_V3_${year}_MVAMedium_DG_DoubleExpo_yRange_Spline_wFakeTauScaleJEC_hm125_amX.txt mmmt_mm_parametric_${region}_TauMuTauMu_Order_Scale_${year}_looseMuIso_looseMuIso_1d_Spline_wFakeModelling_hm125_amX.txt
    sed -i 's/ch1/TauMuTauE_Order_Scale_${year}_PP/g' mmmt_mm_h_parametric_unbinned_${region}_TauMuTauMu_TauMuTauE_TauMuTauHad_TauETauHad_TauHadTauHad_${year}_MVAMedium_DG_DoubleExpo_hm125_amX.txt

    ### combine all
    #python combineChannels.py mmmt_mm_h_parametric_unbinned_${region}_TauMuTauMu_TauMuTauE_TauMuTauHad_TauETauHad_TauHadTauHad_2016_2017_2018_MVAMedium_DG_DoubleExpo_hm125_amX.txt mmmt_mm_h_parametric_unbinned_${region}_TauMuTauMu_TauMuTauE_TauMuTauHad_TauETauHad_TauHadTauHad_2016_MVAMedium_DG_DoubleExpo_hm125_amX.txt mmmt_mm_h_parametric_unbinned_${region}_TauMuTauMu_TauMuTauE_TauMuTauHad_TauETauHad_TauHadTauHad_2017_MVAMedium_DG_DoubleExpo_hm125_amX.txt mmmt_mm_h_parametric_unbinned_${region}_TauMuTauMu_TauMuTauE_TauMuTauHad_TauETauHad_TauHadTauHad_2018_MVAMedium_DG_DoubleExpo_hm125_amX.txt
end
