import os, sys, re

#outputName = "mmmt_mm_h_parametric_unbinned_highmass_TauHadTauHad_2016_2017_2018_boostedDitau_medium_doubleExpo_DV_HToAAH125AX.txt"

#outputName = "mmmt_mm_h_parametric_unbinned_lowmass_TauETauHad_2016_2017_2018_MVAMedium_DV_hm125_amX.txt"
#outputName = "mmmt_mm_h_parametric_unbinned_highmass_TauETauHad_2016_2017_2018_MVAMedium_DV_hm125_amX.txt"
#outputName = "mmmt_mm_h_parametric_unbinned_upsilon_TauETauHad_2016_2017_2018_MVAMedium_DV_hm125_amX.txt"

#outputName = "mmmt_mm_h_parametric_unbinned_lowmass_TauMuTauHad_Order2_2016_2017_2018_MVAMedium_DV_DoubleExpo_hm125_amX.txt"
#outputName = "mmmt_mm_h_parametric_unbinned_upsilon_TauMuTauHad_Order2_2016_2017_2018_MVAMedium_DV_DoubleExpo_hm125_amX.txt"
#outputName = "mmmt_mm_h_parametric_unbinned_highmass_TauMuTauHad_Order2_2016_2017_2018_MVAMedium_DV_DoubleExpo_hm125_amX.txt"

#outputName = "mmmt_mm_h_parametric_unbinned_lowmass_TauHadTauHad_2016_2017_2018_MVAMedium_DV_DoubleExpo_hm125_amX.txt"
#outputName = "mmmt_mm_h_parametric_unbinned_upsilon_TauHadTauHad_2016_2017_2018_MVAMedium_DV_DoubleExpo_hm125_amX.txt"
#outputName = "mmmt_mm_h_parametric_unbinned_highmass_TauHadTauHad_2016_2017_2018_MVAMedium_DV_DoubleExpo_hm125_amX.txt"

year = sys.argv[1]
outputName = sys.argv[2]
inputCards = sys.argv[3:]
lastCard = inputCards[-1]

channels = ['TauMuTauHad_V2', 'TauHadTauHad_V3', 'TauETauHad', 'TauMuTauE', 'TauMuTauMu']


iCard = 0
while inputCards[iCard] != lastCard:
    card = inputCards[iCard]
    cardtmp = card+".tmp"
    cardnocr = card+".nocr"
    os.system("combineCards.py --xc control_"+year+" "+card+" > "+cardtmp)
    print "combineCards.py --xc control_"+year+" "+card+" > "+cardtmp
    os.system("sed 's/ch1_//g' "+cardtmp+" > "+cardnocr)
    print "sed 's/ch1_//g' "+cardtmp+" > "+cardnocr
    os.system("rm -rf "+cardtmp)
    print "rm -rf "+cardtmp
    iCard += 1

cards4Comb = inputCards[:-1]
combined = lastCard
for card in reversed(cards4Comb):
    cardname = card+".nocr"
    print cardname
    for ch in channels:
        if re.search(ch, cardname):
            os.system("combineCards.py "+ch+"_"+year+"_PP="+cardname+" "+combined+" > "+outputName+".tmp")
            print "combineCards.py "+cardname+" "+combined+" > "+outputName+".tmp"
            os.system("sed 's/ch2_//g' "+outputName+".tmp > "+outputName)
            print "sed 's/ch2_//g' "+outputName+".tmp > "+outputName
            combined = outputName
    os.system("rm -rf "+cardname)
    print "rm -rf "+cardname

os.system("rm -rf "+outputName+".tmp")
print "rm -rf "+outputName+".tmp"

print "----"
    
    
