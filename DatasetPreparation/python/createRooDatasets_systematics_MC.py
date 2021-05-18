#!/usr/bin/python
import ROOT
from ROOT import RooFit

doUncert = False
#whichChannel = 'TauHadTauHad'
whichChannel = 'TauMuTauHad'
whichYear = '2017'
#whichMethod = 'deepDitau'
#whichMethod = 'boostedDitau'
whichMethod = 'deepTauID'

isCut = True

prefix='root://cmseos.fnal.gov/'

if whichMethod == 'boostedDitau':
    finDir = prefix+'/eos/uscms/store/user/zfwd666/{}/bkgEffCheck/{}/slimmedTausBoosted/'.format(whichYear, whichChannel)
elif whichMethod == 'deepDitau':
    finDir = prefix+'/eos/uscms/store/user/zfwd666/{}/bkgEffCheck/{}/'.format(whichYear, whichChannel)

scale =0.001
higgs_xsec=48.58
if whichYear == '2017':
    lumi = 41.54*1000
elif whichYear == '2016':
    lumi = 36.47*1000
elif whichYear == '2018':
    lumi = 59.96*1000


outputDir=prefix+'/eos/uscms/store/user/zhangj/HaaLimits/RooDataSets/'

fakeRateUncertainty=0.2
scaleUp=1.0+fakeRateUncertainty
scaleDown = 1.0- fakeRateUncertainty
amasses = ["am4", "am5", "am6", "am7", "am8", "am9", "am10", "am11", "am12", "am13", "am14", "am15", "am16", "am17", "am18", "am19", "am20", "am21"]
regions = ["signalRegion", "sideBand"]
mlDisc = ["0.3","0.4","0.5","0.6","0.7","0.8","0.9"]
mvaDisc = ["vloose", "loose", "medium", "tight", "vtight", "vvtight"]

if whichMethod == 'boostedDitau' or whichMethod == 'deepTauID':
    discs = mvaDisc
elif whichMethod == 'deepDitau':
    discs = mlDisc

for region in regions:
    for amass in amasses:
        for disc in discs:
            if whichChannel == 'TauHadTauHad':
                if region == 'signalRegion':
                    finDir = '/eos/uscms/store/user/zfwd666/HAA/MVATauID/slimmedTausBoosted/{}/'.format(amass)
                    Name = 'HAA_MC_{}MVAVSjetDisc.root'.format(disc)
                elif region == 'sideBand':
                    finDir = '/eos/uscms/store/user/zfwd666/HAA/MVATauID/ABCD/TauHadTauHad/{}/'.format(amass)
                    Name = 'HAA_MC_{}MVAVSjetDisc_B.root'.format(disc)
            elif whichChannel == 'TauMuTauHad':
                if region == 'signalRegion':
                    finDir = '/eos/uscms/store/user/zfwd666/HAA/DeepTauID/TauMuTauHad/slimmedTausMuonCleanedDeep/{}/'.format(amass)
                if region == 'sideBand':
                    finDir = '/eos/uscms/store/user/zfwd666/HAA/DeepTauID/TauMuTauHad/sideband/{}/'.format(amass)
                Name = 'HAA_MC_{}DeepVSjetDisc.root'.format(disc)
            finName = prefix+finDir+Name
            globals()["fin" + amass] = ROOT.TFile(finName)
            globals()["treein" + amass] = globals()["fin" + amass].Get("TreeMuMuTauTau")

            globals()["dimuMass" + amass] = ROOT.RooRealVar("invMassMuMu", "invMassMuMu", 2.5, 60)
            globals()["visDiTauMass" + amass] = ROOT.RooRealVar("visDiTauMass", "visDiTauMass", 0, 60)
            globals()["visFourbodyMass" + amass] = ROOT.RooRealVar("visFourbodyMass", "visFourbodyMass", 0, 1000)
            globals()["eventWeight" + amass] = ROOT.RooRealVar("eventWeight", "eventWeight", -1, 1)

            
            globals()["dataColl" + amass] = ROOT.RooDataSet("dataColl", "dataColl", ROOT.RooArgSet(globals()["dimuMass" + amass], globals()["visDiTauMass" + amass], globals()["visFourbodyMass" + amass], globals()["eventWeight" + amass]))

            for event in globals()["treein" + amass]:
                if isCut and event.Tau1Pt > event.Mu2Pt: continue
                globals()["dimuMass" + amass].setVal(event.invMassMuMu)
                globals()["visDiTauMass" + amass].setVal(event.visMassTauTau)
                globals()["visFourbodyMass" + amass].setVal(event.visMassMuMuTauTau)
                globals()["eventWeight" + amass].setVal(event.eventWeight*scale*higgs_xsec*lumi)
                globals()["dataColl" + amass].add(ROOT.RooArgSet(globals()["dimuMass" + amass], globals()["visDiTauMass" + amass], globals()["visFourbodyMass" + amass], globals()["eventWeight" + amass]))

            if isCut: whichYearTag = whichYear+'CutV2'
            else: whichYearTag = whichYear
            
            globals()["fout" + amass] = ROOT.TFile(outputDir+'HaaMC_{}_{}_{}_{}_{}_{}.root'.format(amass, whichChannel, whichYearTag, whichMethod, disc, region), "RECREATE")
            globals()["dataColl" + amass].Write()
            globals()["fout" + amass].Close()

            if doUncert:
                for event in globals()["treein" + amass]:
                    globals()["dimuMass" + amass].setVal(event.invMassMuMu)
                    globals()["visDiTauMass" + amass].setVal(event.visMassTauTau)
                    globals()["visFourbodyMass" + amass].setVal(event.visMassMuMuTauTau)
                    globals()["eventWeight" + amass].setVal(event.eventWeight*scale*higgs_xsec*lumi_2017*scaleUp)
                    globals()["dataColl" + amass].add(ROOT.RooArgSet(globals()["dimuMass" + amass], globals()["visDiTauMass" + amass], globals()["visFourbodyMass" + amass], globals()["eventWeight" + amass]))
      
                
                
                globals()["foutUp" + amass] = ROOT.TFile(outputDir+"TauHadTauHad_HaaMC_" + amass + "_" + suffix[j] + "_" + iName + "_" + "fakeUp" +".root", "RECREATE")
                globals()["dataColl" + amass].Write()
                globals()["foutUp" + amass].Close()
                
                for event in globals()["treein" + amass]:
                    globals()["dimuMass" + amass].setVal(event.invMassMuMu)
                    globals()["visDiTauMass" + amass].setVal(event.visMassTauTau)
                    globals()["visFourbodyMass" + amass].setVal(event.visMassMuMuTauTau)
                    globals()["eventWeight" + amass].setVal(event.eventWeight*scale*higgs_xsec*lumi_2017*scaleDown)
                    globals()["dataColl" + amass].add(ROOT.RooArgSet(globals()["dimuMass" + amass], globals()["visDiTauMass" + amass], globals()["visFourbodyMass" + amass], globals()["eventWeight" + amass]))
    
                
                globals()["foutDown" + amass] = ROOT.TFile(outputDir+"TauHadTauHad_HaaMC_" + amass + "_" + suffix[j] + "_" + iName +"_"+ "fakeDown" +".root", "RECREATE")
                globals()["dataColl" + amass].Write()
                globals()["foutDown" + amass].Close()
