#!/usr/bin/python
import ROOT
from ROOT import RooFit
import math
import array

#signalDir = "/eos/uscms/store/user/zfwd666/HAA/DeepTauID/TauMuTauHad/slimmedTausMuonCleanedDeep/"
#sidebandDir = "/eos/uscms/store/user/zfwd666/HAA/DeepTauID/TauMuTauHad/sideband/"
signalDir = "/eos/uscms/store/user/zfwd666/HAA/DeepTauID/TauMuTauMu/slimmedTausDeep/"
#sidebandDir1 = "/eos/uscms/store/user/zfwd666/HAA/DeepTauID/TauMuTauE/sideband/"
#sidebandDir2 = "/eos/uscms/store/user/zfwd666/HAA/DeepTauID/TauMuTauE/2P2F/"

#/eos/uscms/store/user/zfwd666/HAA/DeepTauID/TauMuTauE/slimmedTausDeep/am10/HAA_MC_mediumMuIso_mediumEleId.root

prefix='root://cmseos.fnal.gov/'

path = [signalDir]

scale =0.001
higgs_xsec=48.58
lumi_2017=41.529*1000
fileinDir = ["am4", "am5", "am6", "am7", "am8", "am9", "am10", "am11", "am12", "am13", "am14", "am15", "am16", "am17", "am18", "am19", "am20", "am21"]
suffix = ["signalRegion", "sideBand","sideBand2"]

MuonIso=["looseMuIso","mediumMuIso","tightMuIso"]

outputDir="/eos/uscms/store/user/zhangj/HaaLimits/RooDataHists/SignalMC/"

for j, index in enumerate(path):
    for i,ifile in enumerate(fileinDir):
        for m in MuonIso:
            finName = index + ifile + "/HAA_MC_" + m + ".root"
            globals()["fin" + ifile] = ROOT.TFile(finName)
            globals()["treein" + ifile] = globals()["fin" + ifile].Get("TreeMuMuTauTau")          
            globals()["hist" + ifile] = ROOT.TH1D("invMassMuMu","InvMassMuMu",600,0,60)
            globals()["2Dhist" + ifile] = ROOT.TH2D("invMassMuMuVisMassMuMuTauTau","InvMassMuMuVisMassMuMuTauTau",600,0,60, 500, 0, 1000)
                
                
                
            for event in globals()["treein" + ifile]:
               
                globals()["hist" + ifile].Fill(event.invMassMuMu, event.eventWeight*scale*higgs_xsec*lumi_2017)
                globals()["2Dhist" + ifile].Fill(event.invMassMuMu, event.visMassMuMuTauTau, event.eventWeight*scale*higgs_xsec*lumi_2017)  
                
            globals()["fout" + ifile] = ROOT.TFile(prefix+outputDir+"TauMuTauMu_HaaMC_" + ifile + "_" + m + "_" + suffix[j] + ".root", "RECREATE")
            globals()["fout" + ifile].cd()
            globals()["hist" + ifile].Write()
            globals()["2Dhist" + ifile].Write()
            globals()["fout" + ifile].Close()
