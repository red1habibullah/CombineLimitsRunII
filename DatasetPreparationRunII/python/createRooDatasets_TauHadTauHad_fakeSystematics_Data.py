#!/usr/bin/python
import ROOT
from ROOT import RooFit



fakebaseDir='/afs/cern.ch/user/f/fengwang/workplace/public/ForRedwan/sidebandFilesAndTransferFactors/'
baseDir = "/afs/cern.ch/user/f/fengwang/workplace/public/ForRedwan/sidebandFilesAndTransferFactors/"
outputDir= "/eos/user/z/zhangj/HaaAnalysis/RooDatasets/TauHadTauHad_V3/"

#'/eos/uscms/store/user/rhabibul/HtoAA/HtoAA2017Deep/TauETauHad/RooDataSets/DataSystematics/'
years=["2016","2017","2018"]
#years = ["2018"]
disc=["DeepDiTauDCM=0.832;1"]

dmodematch={
    "decayMode0":0.0,
    "decayMode1":1.0,
    "decayMode10":10.0
}

fakeRateUncertainty=0.2
scaleUp=1.0+fakeRateUncertainty
scaleDown = 1.0- fakeRateUncertainty



for iy,y in enumerate(years):
    #print baseDir+y+"/"+"All_"+y+"_sideBand_nominal.root"
    fin=ROOT.TFile(baseDir+y+"/data_0.832.root")
    treein = fin.Get("TreeTauTau")
    invMassMuMu = ROOT.RooRealVar("invMassMuMu", "invMassMuMu", 2.5, 60)
    visFourbodyMass = ROOT.RooRealVar("visFourbodyMass", "visFourbodyMass", 0, 2000)
    fakeRateEfficiency = ROOT.RooRealVar("fakeRateEfficiency", "fakeRateEfficiency", 0, 1)
    
    dataColl = ROOT.RooDataSet("dataColl", "dataColl", ROOT.RooArgSet(invMassMuMu, visFourbodyMass, fakeRateEfficiency))
    dataCollNew = ROOT.RooDataSet("dataColl", "dataColl", ROOT.RooArgSet(invMassMuMu, visFourbodyMass, fakeRateEfficiency))
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
                #print "binlowEdge: ",binlowEdge
                #print "binhighEdge: ",binhighEdge
                #print "============="
                #print "tau pt: ",event.tauPt_tt
                #print "decayMode from tau in event ",event.tauDM_mt
                #print "decayMode from file ",dmodematch[d]
                #if (event.tauPt_tt >= binlowEdge and event.tauPt_tt < binhighEdge):
                if (event.tauPt_tt >= binlowEdge and event.tauPt_tt < binhighEdge):
                    #print "***match***"
                    fakeRateEfficiency.setVal(histFakeEff.GetBinContent(ibin+1)*scaleUp)
                    #print "nominal",histFakeEff.GetBinContent(ibin+1)
                    #print "fakeUp",histFakeEff.GetBinContent(ibin+1)*scaleUp
                # else:
                #     print "unmatch- skip"                 
            if event.tauDisc_tt > 0.6:
                invMassMuMu.setVal(event.invMassMu1Mu2_tt)
                visFourbodyMass.setVal(event.visMass2Mu2Tau_tt)
                dataColl.add(ROOT.RooArgSet(invMassMuMu, visFourbodyMass, fakeRateEfficiency))





    foutUp = ROOT.TFile(outputDir+y+"/"+"DataDriven/"+"TauHadTauHad_V3" + "_"+y+"_MVAMedium_" +"signalRegion_fakeUp.root", "RECREATE")
    dataColl.Write()
    print "Up",dataColl.sumEntries()
    foutUp.Close()
    
    foutcopyUp = ROOT.TFile(outputDir+y+"/"+"DataDriven/"+"TauHadTauHad_V3" + "_"+y+"_MVAMedium_" +"sideBand_fakeUp.root", "RECREATE")
    dataColl.Write()
    foutcopyUp.Close()
    print "done Up!"

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
                #print "decayMode from tau in event ",event.tauDM_mt                                                                  
                #print "decayMode from file ",dmodematch[d]                                                                           
                #print "binlowEdge: ",binlowEdge
                #print "binhighEdge: ",binhighEdge
                #print "============="
                #print "tau pt: ",event.tauPt_tt
                #if (event.tauPt_tt >= binlowEdge and event.tauPt_tt < binhighEdge):
                if ( event.tauPt_tt >= binlowEdge and event.tauPt_tt < binhighEdge):
                    fakeRateEfficiency.setVal(histFakeEff.GetBinContent(ibin+1)*scaleDown)
                    #print "nominal",histFakeEff.GetBinContent(ibin+1)
                    #print "fakeUp",histFakeEff.GetBinContent(ibin+1)*scaleDown

                # else:                                                                                                               
                #     print "unmatch- skip"                                                                                           
        #if event.mu1Pt_mt > event.mu3Pt_mt:                                                                                        
        if event.tauDisc_tt > 0.6:
            #print "lala"
            invMassMuMu.setVal(event.invMassMu1Mu2_tt)
            visFourbodyMass.setVal(event.visMass2Mu2Tau_tt)
            dataCollNew.add(ROOT.RooArgSet(invMassMuMu, visFourbodyMass, fakeRateEfficiency))





    foutUp = ROOT.TFile(outputDir+y+"/"+"DataDriven/"+"TauHadTauHad_V3" + "_"+y+"_MVAMedium_" +"signalRegion_fakeDown.root", "RECREATE")
    dataCollNew.Write()
    print "Down",dataCollNew.sumEntries()
    foutUp.Close()

    foutcopyUp = ROOT.TFile(outputDir+y+"/"+"DataDriven/"+"TauHadTauHad_V3" + "_"+y+"_MVAMedium_" +"sideBand_fakeDown.root", "RECREATE")
    dataCollNew.Write()
    foutcopyUp.Close()
    print "done Down!"


exit()



