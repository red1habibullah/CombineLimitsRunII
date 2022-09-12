#!/usr/bin/python
import ROOT
from ROOT import RooFit

channel = "TauHadTauHad_V3"

fakebaseDir='/afs/cern.ch/user/f/fengwang/workplace/public/ForRedwan/sidebandFilesAndTransferFactors/'
baseDir = "/afs/cern.ch/user/f/fengwang/workplace/public/ForRedwan/sidebandFilesAndTransferFactors/"
outputDir= "/eos/user/z/zhangj/HaaAnalysis/RooDatasets/"+channel+"/"

#fakebaseDir='/afs/cern.ch/user/r/rhabibul/DatasetPrepRunII_Boosted/CMSSW_10_2_13/src/DatasetPreparationRunII/data/'
#baseDir = "/afs/cern.ch/work/r/rhabibul/FlatTreeProductionRunII/CMSSW_10_6_24/src/MuMuTauTauAnalyzer/flattrees/dataSideband/"
#outputDir= "/eos/user/z/zhangj/HaaAnalysis/RooDatasets/TauHadTauHad/"

#'/eos/uscms/store/user/rhabibul/HtoAA/HtoAA2017Deep/TauETauHad/RooDataSets/DataSystematics/'
years=["2016","2017","2018"]
#years=['2018']
disc=["DeepDiTauDCM=0.832;1"]
#disc=["DeepDiTauDCM=0.7;1"]

dmodematch={
    "decayMode0":0.0,
    "decayMode1":1.0,
    "decayMode10":10.0
}



for iy,y in enumerate(years):
    #print baseDir+y+"/"+"All_"+y+"_sideBand_nominal.root"
    #print baseDir+y+"/"+"All_"+y+"_signalRegion_nominal.root"
    fin=ROOT.TFile(baseDir+y+"/data_0.832.root")
    #fin=ROOT.TFile(baseDir+y+"/Histogram/"+"All_"+y+"_sideBand_nominal.root")
    #print baseDir+y+"/data_0.832.root"
    #finSignal=ROOT.TFile(baseDir+y+"/Histogram/"+"All_"+y+"_signalRegion_nominal.root")
    
    treein = fin.Get("TreeTauTau")
    #treeinSignal = finSignal.Get("TreeTauTau")
    
    invMassMuMu = ROOT.RooRealVar("invMassMuMu", "invMassMuMu", 2.5, 60)
    visFourbodyMass = ROOT.RooRealVar("visFourbodyMass", "visFourbodyMass", 0, 2000)
    fakeRateEfficiency = ROOT.RooRealVar("fakeRateEfficiency", "fakeRateEfficiency", 0, 1)
    
    dataColl = ROOT.RooDataSet("dataColl", "dataColl", ROOT.RooArgSet(invMassMuMu, visFourbodyMass, fakeRateEfficiency))
    dataCollSignal = ROOT.RooDataSet("dataColl", "dataColl", ROOT.RooArgSet(invMassMuMu, visFourbodyMass, fakeRateEfficiency))

    for event in treein:
        for id,d in enumerate(disc): 
            finFakeEff = ROOT.TFile(fakebaseDir+y+"/"+"fakeTauEff_TauHadTauHad.root")
            histFakeEff = ROOT.TH1D()
            histFakeEff = finFakeEff.Get(d)
            #print "got histfake"
            nbins = histFakeEff.GetNbinsX()
             
            for ibin in xrange(nbins):
                binlowEdge = histFakeEff.GetXaxis().GetBinLowEdge(ibin+1)
                binhighEdge = histFakeEff.GetXaxis().GetBinLowEdge(ibin+1) + histFakeEff.GetXaxis().GetBinWidth(ibin+1)
                # print "binlowEdge: ",binlowEdge
                # print "binhighEdge: ",binhighEdge
                # print "============="
                # print "tau pt: ",event.tauPt_tt
                #print "decayMode from tau in event ",event.tauDM_mt
                #print "decayMode from file ",dmodematch[d]
                if (event.tauPt_tt >= binlowEdge and event.tauPt_tt < binhighEdge):
                    #print "match"
                    fakeRateEfficiency.setVal(histFakeEff.GetBinContent(ibin+1))
                    #print "nominal",histFakeEff.GetBinContent(ibin+1)
                # else:
                #     print "unmatch- skip"                 
        #if event.mu1Pt_mt > event.mu3Pt_mt:
        if event.tauDisc_tt > 0.2:
            #print "here!"
            invMassMuMu.setVal(event.invMassMu1Mu2_tt)
            visFourbodyMass.setVal(event.visMass2Mu2Tau_tt)
            dataColl.add(ROOT.RooArgSet(invMassMuMu, visFourbodyMass, fakeRateEfficiency))
            dataCollSignal.add(ROOT.RooArgSet(invMassMuMu, visFourbodyMass, fakeRateEfficiency))
            
    # for unblind        
    # for event in treeinSignal:
    #     if event.tauDisc_tt >0.3:
    #         invMassMuMu.setVal(event.invMassMu1Mu2_tt)
    #         visFourbodyMass.setVal(event.visMass2Mu2Tau_tt)        
    #         #fakeRateEfficiency.setVal(1.0)
    #         dataCollSignal.add(ROOT.RooArgSet(invMassMuMu, visFourbodyMass, fakeRateEfficiency))





    #fout = ROOT.TFile(outputDir+y+"/"+"DataDriven/"+"TauHadTauHad" + "_"+y+"_MVAMedium_" +"signalRegionUnblind_nominal.root", "RECREATE")
    print "Start!"
    fout = ROOT.TFile(outputDir+y+"/"+"DataDriven/"+ channel + "_"+y+"_MVAMedium_" +"signalRegion_nominal.root", "RECREATE")
    #fout = ROOT.TFile(outputDir+y+"/"+"DataDriven/"+"TauHadTauHad" + "_"+y+"_MVAMedium_" +"signalRegion_nominal.root", "RECREATE")
    dataCollSignal.Write()
    fout.Close()
    print "done signal!"
    foutcopy = ROOT.TFile(outputDir+y+"/"+"DataDriven/"+ channel + "_"+y+"_MVAMedium_" +"sideBand_nominal.root", "RECREATE")
    #foutcopy = ROOT.TFile(outputDir+y+"/"+"DataDriven/"+"TauHadTauHad" + "_"+y+"_MVAMedium_" +"sideBand_nominal.root", "RECREATE")
    dataColl.Write()
    foutcopy.Close()
    print "done sideband!"

exit()



