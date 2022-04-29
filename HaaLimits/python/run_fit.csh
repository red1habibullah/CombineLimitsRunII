#!/bin/tcsh

#setenv channel TauMuTauHad_Order2
#setenv channel TauHadTauHad
#setenv channel TauETauHad
setenv channel TauMuTauE_Order_Scale
#setenv channel TauMuTauMu

foreach year (2016 2017 2018)
##     python haaLimitsDevToolsRunII.py mm h --parametric --addControl --unbinned --xRange 2.5 8.5 --tag lowmass_${channel}_${year}_MVAMedium_DG_DoubleExpo_Spline_wFake --channel ${channel}_${year} --yFitFunc DG --doubleExpo >& log1${year} &
##     python haaLimitsDevToolsRunII.py mm h --parametric --addControl --unbinned --xRange 6 14 --tag upsilon_${channel}_${year}_MVAMedium_DG_DoubleExpo_Spline_wFake --channel ${channel}_${year} --yFitFunc DG --doubleExpo >& log2${year} &
##     python haaLimitsDevToolsRunII.py mm h --parametric --addControl --unbinned --xRange 11 25 --tag highmass_${channel}_${year}_MVAMedium_DG_DoubleExpo_Spline_wFake --channel ${channel}_${year} --yFitFunc DG --doubleExpo >& log3${year} &
    
##     python haaLimitsDevToolsRunII.py mm h --parametric --addControl --unbinned --xRange 2.5 8.5 --yRange 50 150 --fitParams --tag lowmass_${channel}_${year}_MVAMedium_DG_DoubleExpo_wFake --channel ${channel}_${year} --yFitFunc DG --doubleExpo >& log1${year} &
##     python haaLimitsDevToolsRunII.py mm h --parametric --addControl --unbinned --xRange 6 14 --yRange 50 150 --fitParams --tag upsilon_${channel}_${year}_MVAMedium_DG_DoubleExpo_wFake --channel ${channel}_${year} --yFitFunc DG --doubleExpo >& log2${year} &
##     python haaLimitsDevToolsRunII.py mm h --parametric --addControl --unbinned --xRange 11 25 --yRange 50 150 --fitParams --tag highmass_${channel}_${year}_MVAMedium_DG_DoubleExpo_wFake --channel ${channel}_${year} --yFitFunc DG --doubleExpo >& log3${year} &

##     python haaLimitsDevToolsRunII.py mm h --parametric --addControl --xRange 2.5 8.5 --fitParams --tag lowmass_${channel}_${year}_looseMuIso_tightEleId_DG --channel ${channel}_${year} --yFitFunc DG >& log1${year} &
##     python haaLimitsDevToolsRunII.py mm h --parametric --addControl --xRange 6 14 --fitParams --tag upsilon_${channel}_${year}_looseMuIso_tightEleId_DG --channel ${channel}_${year} --yFitFunc DG >& log2${year} &
##     python haaLimitsDevToolsRunII.py mm h --parametric --addControl --xRange 11 25 --fitParams --tag highmass_${channel}_${year}_looseMuIso_tightEleId_DG --channel ${channel}_${year} --yFitFunc DG >& log3${year} &
    
    python haaLimitsDevToolsRunII.py mm --parametric --addControl --xRange 2.5 8.5 --fitParams --tag lowmass_${channel}_${year}_looseMuIso_tightEleId_1d_wFakeModelling --channel ${channel}_${year} >& log1${year} &
    python haaLimitsDevToolsRunII.py mm --parametric --addControl --xRange 6 14 --fitParams --tag upsilon_${channel}_${year}_looseMuIso_tightEleId_1d_wFakeModelling --channel ${channel}_${year} >& log2${year} &
    python haaLimitsDevToolsRunII.py mm --parametric --addControl --xRange 11 25 --fitParams --tag highmass_${channel}_${year}_looseMuIso_tightEleId_1d_wFakeModelling --channel ${channel}_${year} >& log3${year} &
end
