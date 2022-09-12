#!/bin/tcsh

#setenv channel TauMuTauHad_V2
setenv channel TauHadTauHad_V3
#setenv channel TauETauHad
#setenv channel TauMuTauE_Order_Scale
#setenv channel TauMuTauE_Rebin
#setenv channel TauMuTauMu_Order_Scale
#setenv channel TauMuTauMu_Rebin

foreach year (2016 2017 2018)
#foreach year (2018)
##     python haaLimitsDevToolsRunII.py mm h --parametric --addControl --unbinned --xRange 2.5 8.5 --tag lowmass_${channel}_${year}_MVAMedium_DG_DoubleExpo_Spline_wFake --channel ${channel}_${year} --yFitFunc DG --doubleExpo >& log1${year} &
##     python haaLimitsDevToolsRunII.py mm h --parametric --addControl --unbinned --xRange 6 14 --tag upsilon_${channel}_${year}_MVAMedium_DG_DoubleExpo_Spline_wFake --channel ${channel}_${year} --yFitFunc DG --doubleExpo >& log2${year} &
##     python haaLimitsDevToolsRunII.py mm h --parametric --addControl --unbinned --xRange 11 25 --tag highmass_${channel}_${year}_MVAMedium_DG_DoubleExpo_Spline_wFake --channel ${channel}_${year} --yFitFunc DG --doubleExpo >& log3${year} &

# TauETauHad    
##     python haaLimitsDevToolsRunII.py mm h --parametric --addControl --unbinned --xRange 2.5 8.5 --tag lowmass_${channel}_${year}_MVAMedium_DG_DoubleExpo_Spline_wFakeTauScale --channel ${channel}_${year} --yFitFunc DG --doubleExpo >& log1${year} &
##     python haaLimitsDevToolsRunII.py mm h --parametric --addControl --unbinned --xRange 6 14 --tag upsilon_${channel}_${year}_MVAMedium_DG_DoubleExpo_Spline_wFakeTauScale --channel ${channel}_${year} --yFitFunc DG --doubleExpo >& log2${year} &
##     python haaLimitsDevToolsRunII.py mm h --parametric --addControl --unbinned --xRange 11 50 --tag highmass_${channel}_${year}_MVAMedium_DG_DoubleExpo_Spline_wFakeTauScale --channel ${channel}_${year} --yFitFunc DG --doubleExpo >& log3${year} &

##     python haaLimitsDevToolsRunII.py mm --parametric --addControl --unbinned --xRange 2.5 8.5 --tag lowmass_${channel}_${year}_MVAMedium_1d_Spline_wFakeTauScale --channel ${channel}_${year} --yFitFunc DG --doubleExpo >& log1${year} &
##     python haaLimitsDevToolsRunII.py mm --parametric --addControl --unbinned --xRange 6 14 --tag upsilon_${channel}_${year}_MVAMedium_1d_Spline_wFakeTauScale --channel ${channel}_${year} --yFitFunc DG --doubleExpo >& log2${year} &
##     python haaLimitsDevToolsRunII.py mm --parametric --addControl --unbinned --xRange 11 25 --tag highmass_${channel}_${year}_MVAMedium_1d_Spline_wFakeTauScale --channel ${channel}_${year} --yFitFunc DG --doubleExpo >& log3${year} &

# TauMuTauHad
##     python haaLimitsDevToolsRunII.py mm h --parametric --addControl --unbinned --fitParams --xRange 2.5 8.5  --yRange 50 150 --tag lowmass_${channel}_${year}_MVAMedium_DG_DoubleExpo_yRange_wFakeTauScale --channel ${channel}_${year} --yFitFunc DG --doubleExpo >& log1${year} &
##     python haaLimitsDevToolsRunII.py mm h --parametric --addControl --unbinned --fitParams --xRange 6 14  --yRange 50 150 --tag upsilon_${channel}_${year}_MVAMedium_DG_DoubleExpo_yRange_wFakeTauScale --channel ${channel}_${year} --yFitFunc DG --doubleExpo >& log2${year} &
##     python haaLimitsDevToolsRunII.py mm h --parametric --addControl --unbinned --fitParams --xRange 11 50  --yRange 50 150 --tag highmass_${channel}_${year}_MVAMedium_DG_DoubleExpo_yRange_wFakeTauScale --channel ${channel}_${year} --yFitFunc DG --doubleExpo >& log3${year} &

##    python haaLimitsDevToolsRunII.py mm h --parametric --addControl --unbinned --fitParams --xRange 2.5 8.5 --yRange 50 1500 --tag lowmass_${channel}_${year}_MVAMedium_DG_DoubleExpo_yRange4m1000_wFakeTauScale --channel ${channel}_${year} --yFitFunc DG --doubleExpo >& log1${year} &
##    python haaLimitsDevToolsRunII.py mm h --parametric --addControl --unbinned --fitParams --xRange 6 14 --yRange 50 1500 --tag upsilon_${channel}_${year}_MVAMedium_DG_DoubleExpo_yRange4m1000_wFakeTauScale --channel ${channel}_${year} --yFitFunc DG --doubleExpo >& log2${year} &
##    python haaLimitsDevToolsRunII.py mm h --parametric --addControl --unbinned --fitParams --xRange 11 50 --yRange 50 1500 --tag highmass_${channel}_${year}_MVAMedium_DG_DoubleExpo_yRange4m1000_wFakeTauScale --channel ${channel}_${year} --yFitFunc DG --doubleExpo >& log3${year} &

# TauHadTauHad
##    python haaLimitsDevToolsRunII.py mm h --parametric --addControl --unbinned --xRange 2.5 8.5 --yRange 50 150 --tag lowmass_${channel}_${year}_MVAMedium_DG_DoubleExpo_yRange_Spline_wFakeTauScaleJEC --channel ${channel}_${year} --yFitFunc DG --doubleExpo >& log1${year} &
##    python haaLimitsDevToolsRunII.py mm h --parametric --addControl --unbinned --xRange 6 14 --yRange 50 150 --tag upsilon_${channel}_${year}_MVAMedium_DG_DoubleExpo_yRange_Spline_wFakeTauScaleJEC --channel ${channel}_${year} --yFitFunc DG --doubleExpo >& log2${year} &
##    python haaLimitsDevToolsRunII.py mm h --parametric --addControl --unbinned --xRange 11 50 --yRange 50 150 --tag highmass_${channel}_${year}_MVAMedium_DG_DoubleExpo_yRange_Spline_wFakeTauScaleJEC --channel ${channel}_${year} --yFitFunc DG --doubleExpo >& log3${year} &

##     python haaLimitsDevToolsRunII.py mm --parametric --addControl --unbinned --xRange 2.5 8.5 --yRange 50 150 --tag lowmass_${channel}_${year}_MVAMedium_1d_yRange_Spline_wFakeTauScaleJEC --channel ${channel}_${year} --yFitFunc DG --doubleExpo >& log1${year} &
##     python haaLimitsDevToolsRunII.py mm --parametric --addControl --unbinned --xRange 6 14 --yRange 50 150 --tag upsilon_${channel}_${year}_MVAMedium_1d_yRange_Spline_wFakeTauScaleJEC --channel ${channel}_${year} --yFitFunc DG --doubleExpo >& log2${year} &
##     python haaLimitsDevToolsRunII.py mm --parametric --addControl --unbinned --xRange 11 25 --yRange 50 150 --tag highmass_${channel}_${year}_MVAMedium_1d_yRange_Spline_wFakeTauScaleJEC --channel ${channel}_${year} --yFitFunc DG --doubleExpo >& log3${year} &

  python haaLimitsDevToolsRunII.py mm h --parametric --addControl --unbinned --xRange 2.5 8.5 --yRange 50 1500 --tag lowmass_${channel}_${year}_MVAMedium_DG_DoubleExpo_yRange4m1000_Spline_wFakeTauScaleJEC --channel ${channel}_${year} --yFitFunc DG --doubleExpo >& log1${year} &
  python haaLimitsDevToolsRunII.py mm h --parametric --addControl --unbinned --xRange 6 14 --yRange 50 1500 --tag upsilon_${channel}_${year}_MVAMedium_DG_DoubleExpo_yRange4m1000_Spline_wFakeTauScaleJEC --channel ${channel}_${year} --yFitFunc DG --doubleExpo >& log2${year} &
  python haaLimitsDevToolsRunII.py mm h --parametric --addControl --unbinned --xRange 11 50 --yRange 50 1500 --tag highmass_${channel}_${year}_MVAMedium_DG_DoubleExpo_yRange4m1000_Spline_wFakeTauScaleJEC --channel ${channel}_${year} --yFitFunc DG --doubleExpo >& log3${year} &


#TauMuTauE
##     python haaLimitsDevToolsRunII.py mm --parametric --addControl --xRange 2.5 8.5 --tag lowmass_${channel}_${year}_looseMuIso_tightEleId_1d_Spline_wFakeModelling --channel ${channel}_${year} >& log1${year} &
##     python haaLimitsDevToolsRunII.py mm --parametric --addControl --xRange 6 14 --tag upsilon_${channel}_${year}_looseMuIso_tightEleId_1d_Spline_wFakeModelling --channel ${channel}_${year} >& log2${year} &
##     python haaLimitsDevToolsRunII.py mm --parametric --addControl --xRange 11 25 --tag highmass_${channel}_${year}_looseMuIso_tightEleId_1d_Spline_wFakeModelling --channel ${channel}_${year} >& log3${year} &


#TauMuTauMu
##    python haaLimitsDevToolsRunII.py mm --parametric --addControl --unblind --xRange 2.5 8.5 --tag lowmass_${channel}_${year}_looseMuIso_looseMuIso_1d_Spline_wFakeModelling_unblind --channel ${channel}_${year} >& log1${year} &
##    python haaLimitsDevToolsRunII.py mm --parametric --addControl --unblind --xRange 6 14 --tag upsilon_${channel}_${year}_looseMuIso_looseMuIso_1d_Spline_wFakeModelling_unblind --channel ${channel}_${year} >& log2${year} &
##    python haaLimitsDevToolsRunII.py mm --parametric --addControl --unblind --xRange 11 25 --tag highmass_${channel}_${year}_looseMuIso_looseMuIso_1d_Spline_wFakeModelling_unblind --channel ${channel}_${year} >& log3${year} &
end
