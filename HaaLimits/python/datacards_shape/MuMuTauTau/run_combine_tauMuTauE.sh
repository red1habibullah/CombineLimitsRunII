#!/bin/bash

export channel=TauMuTauE_Order_Scale
#export channel=TauMuTauMu

export wp=looseMuIso_tightEleId
#export wp=looseMuIso_looseMuIso

combineCards.py --xc control mmmt_mm_parametric_lowmass_${channel}_2017_${wp}_1d_Spline_wFakeModelling_hm125_amX.txt mmmt_mm_parametric_lowmass_${channel}_2016_${wp}_1d_Spline_wFakeModelling_hm125_amX.txt > mmmt_mm_parametric_lowmass_${channel}_2016_2017_2018_${wp}_1d_Spline_wFakeModelling_hm125_amX.txt.tmp
sed 's/ch1_//g' mmmt_mm_parametric_lowmass_${channel}_2016_2017_2018_${wp}_1d_Spline_wFakeModelling_hm125_amX.txt.tmp | sed 's/ch2_//g' > mmmt_mm_parametric_lowmass_${channel}_2016_2017_2018_${wp}_1d_Spline_wFakeModelling_hm125_amX.txt
combineCards.py mmmt_mm_parametric_lowmass_${channel}_2016_2017_2018_${wp}_1d_Spline_wFakeModelling_hm125_amX.txt mmmt_mm_parametric_lowmass_${channel}_2018_${wp}_1d_Spline_wFakeModelling_hm125_amX.txt > mmmt_mm_parametric_lowmass_${channel}_2016_2017_2018_${wp}_1d_Spline_wFakeModelling_hm125_amX.txt.tmp
sed 's/ch1_//g' mmmt_mm_parametric_lowmass_${channel}_2016_2017_2018_${wp}_1d_Spline_wFakeModelling_hm125_amX.txt.tmp | sed 's/ch2_//g' > mmmt_mm_parametric_lowmass_${channel}_2016_2017_2018_${wp}_1d_Spline_wFakeModelling_hm125_amX.txt

combineCards.py --xc control mmmt_mm_parametric_highmass_${channel}_2017_${wp}_1d_Spline_wFakeModelling_hm125_amX.txt mmmt_mm_parametric_highmass_${channel}_2016_${wp}_1d_Spline_wFakeModelling_hm125_amX.txt > mmmt_mm_parametric_highmass_${channel}_2016_2017_2018_${wp}_1d_Spline_wFakeModelling_hm125_amX.txt.tmp
sed 's/ch1_//g' mmmt_mm_parametric_highmass_${channel}_2016_2017_2018_${wp}_1d_Spline_wFakeModelling_hm125_amX.txt.tmp | sed 's/ch2_//g' > mmmt_mm_parametric_highmass_${channel}_2016_2017_2018_${wp}_1d_Spline_wFakeModelling_hm125_amX.txt
combineCards.py mmmt_mm_parametric_highmass_${channel}_2016_2017_2018_${wp}_1d_Spline_wFakeModelling_hm125_amX.txt mmmt_mm_parametric_highmass_${channel}_2018_${wp}_1d_Spline_wFakeModelling_hm125_amX.txt > mmmt_mm_parametric_highmass_${channel}_2016_2017_2018_${wp}_1d_Spline_wFakeModelling_hm125_amX.txt.tmp
sed 's/ch1_//g' mmmt_mm_parametric_highmass_${channel}_2016_2017_2018_${wp}_1d_Spline_wFakeModelling_hm125_amX.txt.tmp | sed 's/ch2_//g' > mmmt_mm_parametric_highmass_${channel}_2016_2017_2018_${wp}_1d_Spline_wFakeModelling_hm125_amX.txt

combineCards.py --xc control mmmt_mm_parametric_upsilon_${channel}_2017_${wp}_1d_Spline_wFakeModelling_hm125_amX.txt mmmt_mm_parametric_upsilon_${channel}_2016_${wp}_1d_Spline_wFakeModelling_hm125_amX.txt > mmmt_mm_parametric_upsilon_${channel}_2016_2017_2018_${wp}_1d_Spline_wFakeModelling_hm125_amX.txt.tmp
sed 's/ch1_//g' mmmt_mm_parametric_upsilon_${channel}_2016_2017_2018_${wp}_1d_Spline_wFakeModelling_hm125_amX.txt.tmp | sed 's/ch2_//g' > mmmt_mm_parametric_upsilon_${channel}_2016_2017_2018_${wp}_1d_Spline_wFakeModelling_hm125_amX.txt
combineCards.py mmmt_mm_parametric_upsilon_${channel}_2016_2017_2018_${wp}_1d_Spline_wFakeModelling_hm125_amX.txt mmmt_mm_parametric_upsilon_${channel}_2018_${wp}_1d_Spline_wFakeModelling_hm125_amX.txt > mmmt_mm_parametric_upsilon_${channel}_2016_2017_2018_${wp}_1d_Spline_wFakeModelling_hm125_amX.txt.tmp
sed 's/ch1_//g' mmmt_mm_parametric_upsilon_${channel}_2016_2017_2018_${wp}_1d_Spline_wFakeModelling_hm125_amX.txt.tmp | sed 's/ch2_//g' > mmmt_mm_parametric_upsilon_${channel}_2016_2017_2018_${wp}_1d_Spline_wFakeModelling_hm125_amX.txt
