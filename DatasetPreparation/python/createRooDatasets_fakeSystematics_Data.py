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
elif whichMethod == 'deepDitau' or whichMethod == 'deepTauID':
    finDir = prefix+'/eos/uscms/store/user/zfwd666/{}/bkgEffCheck/{}/'.format(whichYear, whichChannel)


finDir2017 = prefix+'/eos/uscms/store/user/zfwd666/2017/bkgEffCheck/{}/slimmedTausBoosted/'.format(whichChannel)

if whichChannel == 'TauHadTauHad':
    fakeRate = finDir2017+'fakeTauEff_{}.root'.format(whichChannel)
elif whichChannel == 'TauMuTauHad':
    fakeRate = '/uscms_data/d3/zfwd666/MuMuTauTauAnalyzer/CMSSW_9_4_13/src/MuMuTauTauAnalyzer/2017/DeepTauID/bkgEffCheck/TauMuTauHad/RooDatasets/fakeTauEff_TauMuTauHad.root'
#fakeRate = finDir+'fakeTauEff_{}.root'.format(whichChannel)


#fakeDir='/eos/uscms/store/user/zfwd666/2017/bkgEffCheck/TauHadTauHad/'
#fileinDir = "/eos/uscms/store/user/zfwd666/2017/bkgEffCheck/TauHadTauHad/"


outputDir=prefix+'/eos/uscms/store/user/zhangj/HaaLimits/RooDataSets/'

fakeRateUncertainty=0.2
scaleUp=1.0+fakeRateUncertainty
scaleDown = 1.0- fakeRateUncertainty

#TauMuTauHad_sideBand_looseDeepVSjet.root             
#TauMuTauHad_signalRegion_looseDeepVSjet.root

mlDisc = ["0.3","0.4","0.5","0.6","0.7","0.8","0.9"]
mvaDisc = ["vloose", "loose", "medium", "tight", "vtight", "vvtight"]

if whichMethod == 'boostedDitau' or whichMethod == 'deepTauID':
    discs = mvaDisc
elif whichMethod == 'deepDitau':
    discs = mlDisc

for disc in discs:
    if whichMethod == 'deepDitau':
        finname = finDir + 'deepDiTauRaw_{}.root'.format(disc)
    elif whichMethod == 'boostedDitau':
        finname = finDir + 'MVATauVSele_loose_MVATauVSmu_loose_MVATauVSjet_{}.root'.format(disc)
    elif whichMethod == 'deepTauID':
        finname = finDir + 'deepTauVSele_vvvloose_deepTauVSmu_vloose_deepTauVSjet_{}.root'.format(disc)

    fin = ROOT.TFile(finname)
    print fin
    
    treein = fin.Get("TreeMuMuTauTau")

    invMassMuMu = ROOT.RooRealVar("invMassMuMu", "invMassMuMu", 2.5, 60)
    visDiTauMass = ROOT.RooRealVar("visDiTauMass", "visDiTauMass", 0, 60)
    visFourbodyMass = ROOT.RooRealVar("visFourbodyMass", "visFourbodyMass", 0, 1000)
    fakeRateEfficiency = ROOT.RooRealVar("fakeRateEfficiency", "fakeRateEfficiency", 0, 1)
    
    dataColl = ROOT.RooDataSet("dataColl", "dataColl", ROOT.RooArgSet(invMassMuMu, visDiTauMass, visFourbodyMass, fakeRateEfficiency))

    if whichMethod == 'deepDitau':
        plotname = "DeepDiTauDCM=" + disc
    elif whichMethod == 'boostedDitau':
        plotname = '{}MVAVSjet'.format(disc)
    elif whichMethod == 'deepTauID':
        plotname = '{}DeepVSjet'.format(disc)
        
        
    print plotname
    finFakeEff = ROOT.TFile(fakeRate)
    histFakeEff = finFakeEff.Get(plotname)
    
    for event in treein:
        if isCut and event.Tau1Pt > event.Mu2Pt: continue
        nbins = histFakeEff.GetNbinsX()
        for ibin in xrange(nbins):
            binlowEdge = histFakeEff.GetXaxis().GetBinLowEdge(ibin+1)
            binhighEdge = histFakeEff.GetXaxis().GetBinLowEdge(ibin+1) + histFakeEff.GetXaxis().GetBinWidth(ibin+1)
            if (event.Tau2Pt >= binlowEdge and event.Tau2Pt < binhighEdge):
                fakeRateEfficiency.setVal(histFakeEff.GetBinContent(ibin+1))

        invMassMuMu.setVal(event.invMassMuMu)
        visDiTauMass.setVal(event.visMassTauTau)
        visFourbodyMass.setVal(event.visMassMuMuTauTau)
        dataColl.add(ROOT.RooArgSet(invMassMuMu, visDiTauMass, visFourbodyMass, fakeRateEfficiency))

    if isCut: whichYearTag = whichYear+'CutV2'
    else: whichYearTag = whichYear
        
    ### temperarily not contain 
    fout = ROOT.TFile(outputDir+'{}_{}_{}_{}_signalRegion.root'.format(whichChannel, whichYearTag, whichMethod, disc), "RECREATE")
    dataColl.Write()
    fout.Close()
    
    foutcopy= ROOT.TFile(outputDir+'{}_{}_{}_{}_sideBand.root'.format(whichChannel, whichYearTag, whichMethod, disc), "RECREATE")
    dataColl.Write()
    foutcopy.Close()

    if doUncert == True:
        for event in treein:
            finFakeEff = ROOT.TFile(fakeDir+"fakeTauEff_TauHadTauHad.root")
            histFakeEff = ROOT.TH1D()
            histFakeEff = finFakeEff.Get(plotname)
    
            nbins = histFakeEff.GetNbinsX()
            for ibin in xrange(nbins):
                binlowEdge = histFakeEff.GetXaxis().GetBinLowEdge(ibin+1)
                binhighEdge = histFakeEff.GetXaxis().GetBinLowEdge(ibin+1) + histFakeEff.GetXaxis().GetBinWidth(ibin+1)
                if (event.Tau2Pt >= binlowEdge and event.Tau2Pt < binhighEdge):
                    fakeRateEfficiency.setVal(histFakeEff.GetBinContent(ibin+1)*scaleUp)
                    
            invMassMuMu.setVal(event.invMassMuMu)
            visDiTauMass.setVal(event.visMassTauTau)
            visFourbodyMass.setVal(event.visMassMuMuTauTau)
            dataColl.add(ROOT.RooArgSet(invMassMuMu, visDiTauMass, visFourbodyMass, fakeRateEfficiency))
        foutUp =  ROOT.TFile(outputDir+"TauHadTauHad" + "_"+ "signalRegion"+"_"+ifile +"_" + "fakeUp" + ".root", "RECREATE")
        dataColl.Write()
        foutUp.Close()
        
        foutUpcopy =  ROOT.TFile(outputDir+"TauHadTauHad" + "_"+ "sideBand"+"_"+ifile +"_" + "fakeUp" + ".root", "RECREATE")
        dataColl.Write()
        foutUpcopy.Close()
        
        
        for event in treein:
            finFakeEff = ROOT.TFile(fakeDir+"fakeTauEff_TauHadTauHad.root")
            histFakeEff = ROOT.TH1D()
            histFakeEff = finFakeEff.Get(plotname)
    
            nbins = histFakeEff.GetNbinsX()
            for ibin in xrange(nbins):
                binlowEdge = histFakeEff.GetXaxis().GetBinLowEdge(ibin+1)
                binhighEdge = histFakeEff.GetXaxis().GetBinLowEdge(ibin+1) + histFakeEff.GetXaxis().GetBinWidth(ibin+1)
                if (event.Tau2Pt >= binlowEdge and event.Tau2Pt < binhighEdge):
                    fakeRateEfficiency.setVal(histFakeEff.GetBinContent(ibin+1)*scaleDown)
    
            invMassMuMu.setVal(event.invMassMuMu)
            visDiTauMass.setVal(event.visMassTauTau)
            visFourbodyMass.setVal(event.visMassMuMuTauTau)
            dataColl.add(ROOT.RooArgSet(invMassMuMu, visDiTauMass, visFourbodyMass, fakeRateEfficiency))
        foutDown =  ROOT.TFile(outputDir+"TauHadTauHad" + "_"+ "signalRegion"+"_"+ifile +"_" + "fakeDown" + ".root", "RECREATE")
        dataColl.Write()
        foutDown.Close()
    
        foutDowncopy =  ROOT.TFile(outputDir+"TauHadTauHad" + "_"+ "sideBand"+"_"+ifile +"_" + "fakeDown" + ".root", "RECREATE")
        dataColl.Write()
        foutDowncopy.Close()
