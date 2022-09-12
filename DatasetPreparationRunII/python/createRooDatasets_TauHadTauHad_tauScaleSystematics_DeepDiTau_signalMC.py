#!/usr/bin/python
import ROOT
from ROOT import RooFit

baseDir="/afs/cern.ch/user/f/fengwang/workplace/public/ForRedwan/JECTrees/"
outDir="/eos/user/z/zhangj/HaaAnalysis/RooDatasets/TauHadTauHad_V3/"

scale =0.001
higgs_SM_xsec=48.58
higgs_BSM_xsec=0.0363647

fakerateUncertainty=0.20
scaleUp=1.0+fakerateUncertainty
scaleDown=1.0-fakerateUncertainty


#years=["2016","2017","2018"]
#years=["2018"]
years=["2016", "2017", "2018"]

lumi_map={"2017":41.529*1000,
          "2016":35.92*1000,
          "2018":59.74*1000
}

hXsecmap={"hm125":48.58,
          "hm250":10.2,
          "hm500":1.7089,
          "hm750":0.4969,
          "hm1000":0.1845


}


#mh=["h125","hm250","hm500","hm750","hm1000"]
#mh=["hm125"]
mh=["hm125", "hm1000"]
hamap ={
    "hm125":["am3p6","am5","am6","am7","am8","am9","am10","am11","am12","am13","am14","am15","am16","am17","am18","am19","am20","am21"], #am4 missing in 2018 so left out for now
    "hm250":["am5","am10","am15","am20"],
    "hm500":["am5","am10","am15","am20"],
    "hm750":["am10","am20","am25","am30"],
    "hm1000":["am10","am20","am30","am40"]
}

regions = ["FP", "PP"]
regionsTag = {"FP":"sideBand", "PP":"signalRegion"}

sfmaplow={
    "2016":{"nominal":0.63,"scaleUp":0.74,"scaleDown":0.52},
    "2017":{"nominal":1.00,"scaleUp":1.11,"scaleDown":0.89},
    "2018":{"nominal":0.94,"scaleUp":1.02,"scaleDown":0.86}
}


sfmaphigh={
    "2016":{"nominal":0.92,"scaleUp":0.88,"scaleDown":0.96},
    "2017":{"nominal":0.82,"scaleUp":0.78,"scaleDown":0.86},
    "2018":{"nominal":0.78,"scaleUp":0.74,"scaleDown":0.82}
}

sfmap={
    "2016":{"nominal":0.90,"scaleUp":1.00,"scaleDown":0.80},
    "2017":{"nominal":0.90,"scaleUp":1.00,"scaleDown":0.80},
    "2018":{"nominal":0.90,"scaleUp":1.00,"scaleDown":0.80}
}


for y in years:
    for h in mh:
        for ia,a in enumerate(hamap[h]):
            for ir,r in enumerate(regions):
                #fname= baseDir+y+"/"+r+"/"+h.replace('m','')+"/"+a.replace('m','')+"/HAA_MC_JECSyst_0.root"
                fname= baseDir+y+"/"+r+"/"+h+"/"+a+"/HAA_MC_JECSyst_0.root"
                print a,ir,y,lumi_map[y]
                print fname
                globals()["fin"+ a+ r]=ROOT.TFile(fname)
                globals()["treein"+ a+ r]=globals()["fin" + a + r].Get("TreeTauTau")
                globals()["dimuMass" + a + r] = ROOT.RooRealVar("invMassMuMu","invMassMuMu",2.5,60)
                globals()["visFourbodyMass" + a + r] = ROOT.RooRealVar("visFourbodyMass", "visFourbodyMass", 0, 2000)
                globals()["eventWeight" + a + r] = ROOT.RooRealVar("eventWeight", "eventWeight", -1, 1)
                globals()["dataColl" + a + r] = ROOT.RooDataSet("dataColl", "dataColl", ROOT.RooArgSet(globals()["dimuMass" + a + r], globals()["visFourbodyMass" + a + r], globals()["eventWeight" + a + r]))
                globals()["dataCollUp" + a + r] = ROOT.RooDataSet("dataColl", "dataColl", ROOT.RooArgSet(globals()["dimuMass" + a + r], globals()["visFourbodyMass" + a + r], globals()["eventWeight" + a + r]))
                globals()["dataCollDown" + a + r] = ROOT.RooDataSet("dataColl", "dataColl", ROOT.RooArgSet(globals()["dimuMass" + a + r], globals()["visFourbodyMass" + a + r], globals()["eventWeight" + a + r]))
                print "nominal"
                for event in globals()["treein" + a + r]:
                    #if event.mu2Pt_mt > event.mu3Pt_mt:
                    #if event.tauDisc_tt > 0.6:
                    globals()["dimuMass" + a + r].setVal(event.invMassMu1Mu2_tt)
                    globals()["visFourbodyMass" + a + r].setVal(event.visMass2Mu2Tau_tt)
                    #if event.tauPt_tt > 10 and event.tauPt_tt < 20 and event.tauDisc_tt > 0.6:
                        #print "low sf nominal:",sfmaplow[y]["nominal"] 
                     #   globals()["eventWeight" + a + r].setVal(event.eventWeight_tt*scale*lumi_map[y]*hXsecmap[h]*sfmaplow[y]["nominal"])
                    #if event.tauPt_tt > 20 and event.tauPt_tt < 10000 and event.tauDisc_tt > 0.6:
                    #print "sf nominal:",sfmap[y]["nominal"] 
                    globals()["eventWeight" + a + r].setVal(event.eventWeight_tt*scale*lumi_map[y]*hXsecmap[h]*sfmap[y]["nominal"])
                    globals()["dataColl" + a + r].add(ROOT.RooArgSet(globals()["dimuMass" + a + r], globals()["visFourbodyMass" + a + r], globals()["eventWeight" + a + r]))
                #globals()["fout"+ a + r]=ROOT.TFile(outDir+y+"/SignalMC/"+"Haa_MC_"+h+"_"+a+"_"+"TauHadTauHad"+"_"+y+"_"+"MVAMedium"+"_"+r+"_"+"nominal.root","RECREATE")
                #print outDir+y+"/signalMC/"+"Haa_MC_"+h+"_"+a+"_"+"TauHadTauHad"+"_"+y+"_"+"MVAMedium"+"_"+r+"_"+"nominal.root"
                #globals()["dataColl" + a + r].Write()
                #globals()["fout"+ a + r].Close()
                
                print "tauScaleUp"
                
                for event in globals()["treein" + a + r]:
                    #if event.mu2Pt_mt > event.mu3Pt_mt:
                    #if event.tauDisc_tt > 0.6:
                    globals()["dimuMass" + a + r].setVal(event.invMassMu1Mu2_tt)
                    globals()["visFourbodyMass" + a + r].setVal(event.visMass2Mu2Tau_tt)
                        # if event.tauPt_tt > 10 and event.tauPt_tt < 20 and event.tauDisc_tt > 0.6:
                        #     print "low sfscaleUp:",sfmaplow[y]["scaleUp"] 
                        #globals()["eventWeight" + a + r].setVal(event.eventWeight_tt*scale*lumi_map[y]*hXsecmap[h]*sfmaplow[y]["scaleUTp"])
                        #if event.tauPt_tt > 20 and event.tauPt_tt < 10000 and event.tauDisc_tt > 0.6:
                    #print "sf scaleUp:",sfmap[y]["scaleUp"] 
                    globals()["eventWeight" + a + r].setVal(event.eventWeight_tt*scale*lumi_map[y]*hXsecmap[h]*sfmap[y]["scaleUp"])
                    globals()["dataCollUp" + a + r].add(ROOT.RooArgSet(globals()["dimuMass" + a + r], globals()["visFourbodyMass" + a + r], globals()["eventWeight" + a + r]))
                globals()["foutUp"+ a + r]=ROOT.TFile(outDir+y+"/SignalMC/"+"Haa_MC_"+h+"_"+a+"_"+"TauHadTauHad_V3"+"_"+y+"_"+"MVAMedium"+"_"+regionsTag[r]+"_"+"tauScaleUp.root","RECREATE")
                
                globals()["dataCollUp" + a + r].Write()
                globals()["foutUp"+ a + r].Close()
                
                print "tauScaleDown"
               
                for event in globals()["treein" + a + r]:
                    #if event.mu2Pt_mt > event.mu3Pt_mt:
                    #if event.tauDisc_tt > 0.6:
                    globals()["dimuMass" + a + r].setVal(event.invMassMu1Mu2_tt)
                    globals()["visFourbodyMass" + a + r].setVal(event.visMass2Mu2Tau_tt)
                    #if event.tauPt_tt > 10 and event.tauPt_tt < 20  and event.tauDisc_tt > 0.6:
                        #print "low sf scaleDown:",sfmaplow[y]["scaleDown"] 
                        #globals()["eventWeight" + a + r].setVal(event.eventWeight_tt*scale*lumi_map[y]*hXsecmap[h]*sfmaplow[y]["scaleDown"])
                    #if event.tauPt_tt > 20 and event.tauPt_tt < 10000  and event.tauDisc_tt > 0.6:
                    #print "sf scaleDown:",sfmap[y]["scaleDown"] 
                    globals()["eventWeight" + a + r].setVal(event.eventWeight_tt*scale*lumi_map[y]*hXsecmap[h]*sfmap[y]["scaleDown"])
                    globals()["dataCollDown" + a + r].add(ROOT.RooArgSet(globals()["dimuMass" + a + r], globals()["visFourbodyMass" + a + r], globals()["eventWeight" + a + r]))
                globals()["foutDown"+ a + r]=ROOT.TFile(outDir+y+"/SignalMC/"+"Haa_MC_"+h+"_"+a+"_"+"TauHadTauHad_V3"+"_"+y+"_"+"MVAMedium"+"_"+regionsTag[r]+"_"+"tauScaleDown.root","RECREATE")
                
                globals()["dataCollDown" + a + r].Write()
                globals()["foutDown"+ a + r].Close()
               


exit()




