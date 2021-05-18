import os, sys

outputName = "mmmt_mm_h_parametric_unbinned_highmass_TauHadTauHad_2016_2017_2018_boostedDitau_medium_doubleExpo_DV_HToAAH125AX.txt"

inputCards = sys.argv[1:]
lastCard = inputCards[-1]

iCard = 0
while inputCards[iCard] != lastCard:
    card = inputCards[iCard]
    cardtmp = card+".tmp"
    cardnocr = card+".nocr"
    os.system("combineCards.py --xc control "+card+" > "+cardtmp)
    os.system("sed 's/ch1_//g' "+cardtmp+" > "+cardnocr)
    os.system("rm -rf "+cardtmp)
    iCard += 1

cards4Comb = inputCards[:-1]
combined = lastCard
for card in reversed(cards4Comb):
    cardname = card+".nocr"
    print cardname
    os.system("combineCards.py "+cardname+" "+combined+" > "+outputName+".tmp")
    #print "sed 's/ch1_//g' "+outputName+".tmp | sed 's/ch2_//g' > "+outputName
    os.system("sed 's/ch1_//g' "+outputName+".tmp | sed 's/ch2_//g' > "+outputName)
    combined = outputName
    os.system("rm -rf "+cardname)

os.system("rm -rf "+outputName+".tmp")
    
    
