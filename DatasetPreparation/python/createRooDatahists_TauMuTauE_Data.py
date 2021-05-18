#!/usr/bin/python
import ROOT
#import tdrStyle
import math
import array

whichChannel = 'TauMuTauE'
whichYear = '2017'

#tdrStyle.setTDRStyle()
ROOT.gStyle.SetErrorX(0.5)
ROOT.gROOT.SetBatch(ROOT.kTRUE)

prefix='root://cmseos.fnal.gov/'

muIdList = ["loose", "medium", "tight"]
muIdLabel = ["looseMuIso", "mediumMuIso", "tightMuIso"]

eleIdList = ["loose", "medium", "tight"]
eleIdLabel = ["looseEleId", "mediumEleId", "tightEleId"]

#histList = ["deltaRTauTau", "Tau1Pt", "Tau2Pt", "invMassMuMu", "visMassMuMuTauTau"]
histList =["invMassMuMu"]
histLabel = ["#DeltaR(#mu_{3}e)", "p_{T}(#mu_{3})[GeV]", "p_{T}(e)[GeV]", "M(#mu_{1}#mu_{2})[GeV]", "M(3#mue)[GeV]"]
binning = array.array('d', [3, 10, 20, 30, 50, 100, 200])

Colors = [ROOT.kBlue, ROOT.kMagenta, ROOT.kRed, ROOT.kOrange, ROOT.kGreen+1, ROOT.kGreen-8, ROOT.kCyan-7, ROOT.kOrange+3]

label1 = ROOT.TLatex(0.21,0.87, "CMS")
label1.SetNDC()
label1.SetTextSize(0.03)

label2 = ROOT.TLatex(0.19,0.96, "#sqrt{s} = 13 TeV, Lumi = 41.529 fb^{-1} (2017)")
label2.SetNDC()
label2.SetTextFont(42)
label2.SetTextSize(0.04)

label3 = ROOT.TLatex(0.21,0.82, "Preliminary")
label3.SetNDC()
label3.SetTextFont(52)
label3.SetTextSize(0.03)

inputDir=prefix+'/eos/uscms/store/user/zfwd666/{}/bkgEffCheck/{}/'.format(whichYear, whichChannel)
outputDirData=prefix+'/eos/uscms/store/user/zhangj/HaaLimits/RooDataHists/Data/'
outputDirDataDriven=prefix+'/eos/uscms/store/user/zhangj/HaaLimits/RooDataHists/DataDriven/'

inputFakeEleFile = ROOT.TFile(inputDir+"fakeTauEff_JetFakeEle.root")
inputFakeMuFile = ROOT.TFile(inputDir+"fakeTauEff_JetFakeMu.root")


for j,imuid in enumerate(muIdList):

    for k,ieleid in enumerate(eleIdList):
        
        globals()["data3P1F1File" + str(j) + str(k)] = ROOT.TFile(inputDir+"3P1F1_" + "MuIso_" + imuid + "_EleId_" + ieleid + ".root")
        globals()["data3P1F2File" + str(j) + str(k)] = ROOT.TFile(inputDir+"3P1F2_" + "MuIso_" + imuid + "_EleId_" + ieleid + ".root")
        globals()["data2P2FFile" + str(j) + str(k)] = ROOT.TFile(inputDir+"2P2F_" + "MuIso_" + imuid + "_EleId_" + ieleid + ".root")
        globals()["zz3P1F1File" + str(j) + str(k)] = ROOT.TFile(inputDir+"3P1F1_" + "MuIso_" + imuid + "_EleId_" + ieleid + "_zz.root")
        globals()["zz3P1F2File" + str(j) + str(k)] = ROOT.TFile(inputDir+"3P1F2_" + "MuIso_" + imuid + "_EleId_" + ieleid + "_zz.root")
        globals()["zz4PFile" + str(j) + str(k)] = ROOT.TFile(inputDir+"4P_" + "MuIso_" + imuid + "_EleId_" + ieleid + "_zz.root")

        globals()["data3P1F1Tree" + str(j) + str(k)] = globals()["data3P1F1File" + str(j) + str(k)].Get("TreeMuMuTauTau")
        globals()["data3P1F2Tree" + str(j) + str(k)] = globals()["data3P1F2File" + str(j) + str(k)].Get("TreeMuMuTauTau")
        globals()["data2P2FTree" + str(j) + str(k)] = globals()["data2P2FFile" + str(j) + str(k)].Get("TreeMuMuTauTau")
        globals()["zz3P1F1Tree" + str(j) + str(k)] = globals()["zz3P1F1File" + str(j) + str(k)].Get("TreeMuMuTauTau")
        globals()["zz3P1F2Tree" + str(j) + str(k)] = globals()["zz3P1F2File" + str(j) + str(k)].Get("TreeMuMuTauTau")
        globals()["zz4PTree" + str(j) + str(k)] = globals()["zz4PFile" + str(j) + str(k)].Get("TreeMuMuTauTau")
            
        histFakeMuEff = inputFakeMuFile.Get(muIdLabel[j])
        histFakeEleEff = inputFakeEleFile.Get(eleIdLabel[k])

        #Final Extrapolated DataHist in Signal Region
        globals()["data3P1FHist" + str(j) + str(k)] = ROOT.TH1D()
        globals()["data3P1F1Hist" + str(j) + str(k)] = ROOT.TH1D()
        globals()["data3P1F2Hist" + str(j) + str(k)] = ROOT.TH1D()

        globals()["2Ddata3P1FHist" + str(j) + str(k)] = ROOT.TH2D()
        globals()["2Ddata3P1F1Hist" + str(j) + str(k)] = ROOT.TH2D()
        globals()["2Ddata3P1F2Hist" + str(j) + str(k)] = ROOT.TH2D()
            
        #Data on sideband FP
        globals()["data3P1FHistOnly" + str(j) + str(k)] = ROOT.TH1D()
        #globals()["data3P1F1Hist" + str(j) + str(k)] = ROOT.TH1D()
        #globals()["data3P1F2Hist" + str(j) + str(k)] = ROOT.TH1D()

        globals()["2Ddata3P1FHistOnly" + str(j) + str(k)] = ROOT.TH2D()
        
        #Data on sideband2 FF
        globals()["data2P2F1Hist" + str(j) + str(k)] = ROOT.TH1D()
        globals()["data2P2F2Hist" + str(j) + str(k)] = ROOT.TH1D()
            
        globals()["data2P2FHistOnly" + str(j) + str(k)] = ROOT.TH1D()
        globals()["data2P2FextHist" + str(j) + str(k)] = ROOT.TH1D()

        globals()["2Ddata2P2F1Hist" + str(j) + str(k)] = ROOT.TH2D()
        globals()["2Ddata2P2F2Hist" + str(j) + str(k)] = ROOT.TH2D()
            
        globals()["2Ddata2P2FHistOnly" + str(j) + str(k)] = ROOT.TH2D()
        globals()["2Ddata2P2FextHist" + str(j) + str(k)] = ROOT.TH2D()
        
        ## skip zz for now as zz contribution nearly zero
        #globals()["zz3P1F1Hist" + str(j) + str(k)] = ROOT.TH1D()
        #globals()["zz3P1F2Hist" + str(j) + str(k)] = ROOT.TH1D()
        #globals()["zz4PHist" + str(j) + str(k)] = ROOT.TH1D()

        nbins = 240

        nbinsy = 200
            
        histKey = "invMassMuMu"
        globals()["data3P1F1Hist" + str(j) + str(k)] = ROOT.TH1D(histKey + "3P1F1",histKey+"3P1F1", nbins, 0, 60)
        globals()["data3P1F2Hist" + str(j) + str(k)] = ROOT.TH1D(histKey+"3P1F2", histKey+"3P1F2", nbins, 0, 60)
        globals()["data3P1FHistOnly" + str(j) + str(k)] = ROOT.TH1D(histKey+"3P1F1Only",histKey + "3P1F1Only", nbins, 0, 60)

        globals()["data2P2F1Hist" + str(j) + str(k)] = ROOT.TH1D(histKey+"2P2F1",histKey+"2P2F1", nbins, 0, 60)
        globals()["data2P2F2Hist" + str(j) + str(k)] = ROOT.TH1D(histKey+"2P2F2",histKey+"2P2F2", nbins, 0, 60)
        globals()["data2P2FHistOnly" + str(j) + str(k)] = ROOT.TH1D(histKey+"2P2FOnly",histKey+ "2P2FOnly", nbins, 0, 60)       
        globals()["data2P2FextHist" + str(j) + str(k)] = ROOT.TH1D(histKey+"2P2Fext",histKey+"2P2Fext", nbins, 0, 60)

        histKey = "invMassMuMuVisMassMuMuTauTau"
        globals()["2Ddata3P1F1Hist" + str(j) + str(k)] = ROOT.TH2D(histKey + "3P1F1",histKey+"3P1F1", nbins, 0, 60, nbinsy, 0, 1000)
        globals()["2Ddata3P1F2Hist" + str(j) + str(k)] = ROOT.TH2D(histKey+"3P1F2", histKey+"3P1F2", nbins, 0, 60, nbinsy, 0, 1000)
        globals()["2Ddata3P1FHistOnly" + str(j) + str(k)] = ROOT.TH2D(histKey+"3P1F1Only",histKey + "3P1F1Only", nbins, 0, 60, nbinsy, 0, 1000)

        globals()["2Ddata2P2F1Hist" + str(j) + str(k)] = ROOT.TH2D(histKey+"2P2F1",histKey+"2P2F1", nbins, 0, 60, nbinsy, 0, 1000)
        globals()["2Ddata2P2F2Hist" + str(j) + str(k)] = ROOT.TH2D(histKey+"2P2F2",histKey+"2P2F2", nbins, 0, 60, nbinsy, 0, 1000)
        globals()["2Ddata2P2FHistOnly" + str(j) + str(k)] = ROOT.TH2D(histKey+"2P2FOnly",histKey+ "2P2FOnly", nbins, 0, 60, nbinsy, 0, 1000)       
        globals()["2Ddata2P2FextHist" + str(j) + str(k)] = ROOT.TH2D(histKey+"2P2Fext",histKey+"2P2Fext", nbins, 0, 60, nbinsy, 0, 1000)


            
        for event in globals()["data3P1F1Tree" + str(j) + str(k)]:

            fakeEff = 1.0
            nbins = histFakeEleEff.GetNbinsX()
            for ibin in xrange(nbins):
                binlowEdge = histFakeEleEff.GetXaxis().GetBinLowEdge(ibin+1)
                binhighEdge = histFakeEleEff.GetXaxis().GetBinLowEdge(ibin+1) + histFakeEleEff.GetXaxis().GetBinWidth(ibin+1)
                if (event.Tau2Pt >= binlowEdge and event.Tau2Pt < binhighEdge):
                    fakeEff = histFakeEleEff.GetBinContent(ibin+1)/(1.0-histFakeEleEff.GetBinContent(ibin+1))

        
            globals()["data3P1F1Hist" + str(j) + str(k)].Fill(event.invMassMuMu, fakeEff)
            globals()["2Ddata3P1F1Hist" + str(j) + str(k)].Fill(event.invMassMuMu, event.visMassMuMuTauTau, fakeEff)

        for event in globals()["data3P1F2Tree" + str(j) + str(k)]:

            fakeEff = 1.0
            nbins = histFakeMuEff.GetNbinsX()
            for ibin in xrange(nbins):
                binlowEdge = histFakeMuEff.GetXaxis().GetBinLowEdge(ibin+1)
                binhighEdge = histFakeMuEff.GetXaxis().GetBinLowEdge(ibin+1) + histFakeMuEff.GetXaxis().GetBinWidth(ibin+1)
                if (event.Tau1Pt >= binlowEdge and event.Tau1Pt < binhighEdge):
                    fakeEff = histFakeMuEff.GetBinContent(ibin+1)/(1.0-histFakeMuEff.GetBinContent(ibin+1))
        
            globals()["data3P1F2Hist" + str(j) + str(k)].Fill(event.invMassMuMu, fakeEff)
            globals()["2Ddata3P1F2Hist" + str(j) + str(k)].Fill(event.invMassMuMu, event.visMassMuMuTauTau, fakeEff)
                

        for event in globals()["data2P2FTree" + str(j) + str(k)]:

            globals()["data2P2FHistOnly" + str(j) + str(k)].Fill(event.invMassMuMu)
            globals()["2Ddata2P2FHistOnly" + str(j) + str(k)].Fill(event.invMassMuMu, event.visMassMuMuTauTau)

            fakeEff1 = 0.5
            fakeEff2 = 0.5
            fakeEff = 1.0
            nbinsMu = histFakeMuEff.GetNbinsX()
            nbinsEle = histFakeEleEff.GetNbinsX()

            for ibin in xrange(nbinsMu):
                binlowEdge = histFakeMuEff.GetXaxis().GetBinLowEdge(ibin+1)
                binhighEdge = histFakeMuEff.GetXaxis().GetBinLowEdge(ibin+1) + histFakeMuEff.GetXaxis().GetBinWidth(ibin+1)
                if (event.Tau1Pt >= binlowEdge and event.Tau1Pt < binhighEdge):
                    fakeEff1 = histFakeMuEff.GetBinContent(ibin+1)/(1.0-histFakeMuEff.GetBinContent(ibin+1))

            for ibin in xrange(nbinsEle):
                binlowEdge = histFakeEleEff.GetXaxis().GetBinLowEdge(ibin+1)
                binhighEdge = histFakeEleEff.GetXaxis().GetBinLowEdge(ibin+1) + histFakeEleEff.GetXaxis().GetBinWidth(ibin+1)
                if (event.Tau2Pt >= binlowEdge and event.Tau2Pt < binhighEdge):
                    fakeEff2 = histFakeEleEff.GetBinContent(ibin+1)/(1.0-histFakeEleEff.GetBinContent(ibin+1))
        
            globals()["data2P2F1Hist" + str(j) + str(k)].Fill(event.invMassMuMu, (fakeEff1 + fakeEff2)*fakeEff2)
            globals()["data2P2F2Hist" + str(j) + str(k)].Fill(event.invMassMuMu, (fakeEff1 + fakeEff2)*fakeEff1)
            
            globals()["data3P1FHistOnly" + str(j) + str(k)].Fill(event.invMassMuMu,(fakeEff1+fakeEff2))
                
            globals()["data2P2FextHist" + str(j) + str(k)].Fill(event.invMassMuMu, fakeEff1*fakeEff2)

            globals()["2Ddata2P2F1Hist" + str(j) + str(k)].Fill(event.invMassMuMu, event.visMassMuMuTauTau, (fakeEff1 + fakeEff2)*fakeEff2)
            globals()["2Ddata2P2F2Hist" + str(j) + str(k)].Fill(event.invMassMuMu, event.visMassMuMuTauTau, (fakeEff1 + fakeEff2)*fakeEff1)
            
            globals()["2Ddata3P1FHistOnly" + str(j) + str(k)].Fill(event.invMassMuMu, event.visMassMuMuTauTau, (fakeEff1+fakeEff2))
                
            globals()["2Ddata2P2FextHist" + str(j) + str(k)].Fill(event.invMassMuMu, event.visMassMuMuTauTau, fakeEff1*fakeEff2)
        

        globals()["data3P1F1Hist" + str(j) + str(k)].Add(globals()["data2P2F1Hist" + str(j) + str(k)], -1)
        #globals()["data3P1F2Hist" + str(j) + str(k)].Add(globals()["data2P2F2Hist" + str(j) + str(k)], -1)
        globals()["2Ddata3P1F1Hist" + str(j) + str(k)].Add(globals()["2Ddata2P2F1Hist" + str(j) + str(k)], -1)


            #if binValue2 < 0:
            #    print "***** negative bins: ", ibin+1, binValue2
            #    globals()["data3P1F2Hist" + str(j) + str(k)].SetBinContent(ibin+1, 0)
            #    globals()["data3P1F2Hist" + str(j) + str(k)].SetBinError(ibin+1, 0)
                #binval = globals()["data3P1F2Hist" + str(j) + str(k)].GetBinContent(ibin+1)

        

        globals()["data3P1F1Hist" + str(j) + str(k)].Add(globals()["data3P1F2Hist" + str(j) + str(k)])

        globals()["2Ddata3P1F1Hist" + str(j) + str(k)].Add(globals()["2Ddata3P1F2Hist" + str(j) + str(k)])
        
        globals()["data3P1F1Hist" + str(j) + str(k)].Add(globals()["data2P2FextHist" + str(j) + str(k)])

        globals()["2Ddata3P1F1Hist" + str(j) + str(k)].Add(globals()["2Ddata2P2FextHist" + str(j) + str(k)])
        
        #globals()["data3P1F1HistOnly" + str(j) + str(k)].Add(globals()["data2P2FHist" + str(j) + str(k)], -1)

        nbins = globals()["data3P1F1Hist" + str(j) + str(k)].GetNbinsX()
        for ibin in xrange(nbins):
            binValue1 = globals()["data3P1F1Hist" + str(j) + str(k)].GetBinContent(ibin+1)
            binValue2 = globals()["data3P1F2Hist" + str(j) + str(k)].GetBinContent(ibin+1)
            if binValue1 < 0:
                #print "***** negative bins: ", ibin+1, binValue1
                globals()["data3P1F1Hist" + str(j) + str(k)].SetBinContent(ibin+1, 0)
                globals()["data3P1F1Hist" + str(j) + str(k)].SetBinError(ibin+1, 0)
                #binval = globals()["data3P1F1Hist" + str(j) + str(k)].GetBinContent(ibin+1)

        nbinsX = globals()["2Ddata3P1F1Hist" + str(j) + str(k)].GetNbinsX()
        nbinsY = globals()["2Ddata3P1F1Hist" + str(j) + str(k)].GetNbinsY()
        for ibinx in xrange(nbinsX):
            for ibiny in xrange(nbinsY):
            #binValue1 = globals()["data3P1F1Hist" + str(j) + str(k)].GetBinContent(ibin+1)
            #binValue2 = globals()["data3P1F2Hist" + str(j) + str(k)].GetBinContent(ibin+1)
                binValue = globals()["2Ddata3P1F1Hist" + str(j) + str(k)].GetBinContent(ibinx+1, ibiny+1)
                if binValue < 0:
                    #print "***** negative bins: ", ibinx+1, ibiny+1, binValue
                    globals()["2Ddata3P1F1Hist" + str(j) + str(k)].SetBinContent(ibinx+1, ibiny+1, 0)
                    globals()["2Ddata3P1F1Hist" + str(j) + str(k)].SetBinError(ibinx+1, ibiny+1, 0)
                #binval = globals()["data3P1F1Hist" + str(j) + str(k)].GetBinContent(ibin+1)

                
        globals()["fout1" + str(j) + str(k) ] = ROOT.TFile(outputDirData+"TauMuTauE_" + "sideBand" + "_" + "MuIso_" + imuid + "_EleId_" + ieleid + ".root", "RECREATE")
        globals()["fout2" + str(j) + str(k) ] = ROOT.TFile(outputDirData+"TauMuTauE_" + "sideBand2" + "_" + "MuIso_" + imuid + "_EleId_" + ieleid + ".root", "RECREATE")
        globals()["fout3" + str(j) + str(k) ] = ROOT.TFile(outputDirDataDriven+"TauMuTauE_" + "signalRegion" + "_" + "MuIso_" + imuid + "_EleId_" + ieleid + ".root", "RECREATE")
        
        globals()["fout1" + str(j) + str(k) ].cd()
        globals()["data3P1FHistOnly" + str(j) + str(k)].Write()
        globals()["fout1" + str(j) + str(k) ].Close()

        globals()["fout2" + str(j) + str(k) ].cd()
        globals()["data2P2FHistOnly" + str(j) + str(k)].Write()
        globals()["fout2" + str(j) + str(k) ].Close()

        globals()["fout3" + str(j) + str(k) ].cd()
        globals()["data3P1F1Hist" + str(j) + str(k)].Write()
        globals()["2Ddata3P1F1Hist" + str(j) + str(k)].Write()
        #globals()["data3P1F2Hist" + str(j) + str(k)].Write()
        #globals()["data2P2F1Hist" + str(j) + str(k)].Write()
        #globals()["data2P2F2Hist" + str(j) + str(k)].Write()
        #globals()["data2P2FextHist" + str(j) + str(k)].Write()
        
        globals()["fout3" + str(j) + str(k) ].Close()
