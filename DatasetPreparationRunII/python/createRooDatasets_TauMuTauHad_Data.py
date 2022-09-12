#!/usr/bin/python
import ROOT
from ROOT import RooFit


fakebaseDir='/afs/cern.ch/user/f/fengwang/workplace/public/ForRedwan/fakeRate/'
baseDir = "/afs/cern.ch/user/f/fengwang/workplace/public/ForRedwan/sidebandFilesAndTransferFactors/"
outputDir= "/eos/user/z/zhangj/HaaAnalysis/RooDatasets/TauMuTauHad_V2/"

#'/eos/uscms/store/user/rhabibul/HtoAA/HtoAA2017Deep/TauETauHad/RooDataSets/DataSystematics/'
years=["2016","2017","2018"]
dmodes=["decayMode0","decayMode1","decayMode10"]

dmodematch={
    "decayMode0":0.0,
    "decayMode1":1.0,
    "decayMode10":10.0
}

#fakeRateUncertainty=0.2
#scaleUp=1.0+fakeRateUncertainty
#scaleDown = 1.0- fakeRateUncertainty


for iy,y in enumerate(years):
    #print baseDir+y+"/"+"All_"+y+"_sideBand_nominal.root"
    #fin=ROOT.TFile(baseDir+y+"/Histogram/"+"All_"+y+"_sideBand_nominal.root")
    fin=ROOT.TFile(baseDir+y+"/data_0.832.root")
    treein = fin.Get("TreeMuTau")
    invMassMuMu = ROOT.RooRealVar("invMassMuMu", "invMassMuMu", 2.5, 60)
    visFourbodyMass = ROOT.RooRealVar("visFourbodyMass", "visFourbodyMass", 0, 2000)
    fakeRateEfficiency = ROOT.RooRealVar("fakeRateEfficiency", "fakeRateEfficiency", 0, 1)
    
    dataColl = ROOT.RooDataSet("dataColl", "dataColl", ROOT.RooArgSet(invMassMuMu, visFourbodyMass, fakeRateEfficiency))
    
    for event in treein:
        for id,d in enumerate(dmodes): 
            finFakeEff = ROOT.TFile(fakebaseDir+y+"/"+"fakeTauEff_TauMuTauHad.root")
            histFakeEff = ROOT.TH1D()
            histFakeEff = finFakeEff.Get(d)
            nbins = histFakeEff.GetNbinsX()
             
            for ibin in xrange(nbins):
                binlowEdge = histFakeEff.GetXaxis().GetBinLowEdge(ibin+1)
                binhighEdge = histFakeEff.GetXaxis().GetBinLowEdge(ibin+1) + histFakeEff.GetXaxis().GetBinWidth(ibin+1)
                #print "decayMode from tau in event ",event.tauDM_mt
                #print "decayMode from file ",dmodematch[d]
                if event.tauDM_mt == dmodematch[d] and (event.tauPt_mt >= binlowEdge and event.tauPt_mt < binhighEdge):
                    #print "match"
                    fakeRateEfficiency.setVal(histFakeEff.GetBinContent(ibin+1)*0.8)
                # else:
                #     print "unmatch- skip"                 
        if event.mu2Pt_mt > event.mu3Pt_mt and event.invMassMu1Mu2_mt > event.visMassMu3Tau_mt:
            invMassMuMu.setVal(event.invMassMu1Mu2_mt)
            visFourbodyMass.setVal(event.visMass3MuTau_mt)
            dataColl.add(ROOT.RooArgSet(invMassMuMu, visFourbodyMass, fakeRateEfficiency))
            
    

    fout = ROOT.TFile(outputDir+y+"/"+"DataDriven/"+"TauMuTauHad_V2" + "_"+y+"_MVAMedium_" +"signalRegion_fakeDown.root", "RECREATE")
    dataColl.Write()
    fout.Close()
    
    foutcopy = ROOT.TFile(outputDir+y+"/"+"DataDriven/"+"TauMuTauHad_V2" + "_"+y+"_MVAMedium_" +"sideBand_fakeDown.root", "RECREATE")
    dataColl.Write()
    foutcopy.Close()

exit()



