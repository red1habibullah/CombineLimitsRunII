#!/usr/bin/python
import ROOT
#import tdrStyle
import math
import array

#tdrStyle.setTDRStyle()
ROOT.gStyle.SetErrorX(0.5)

muIdList = ["loose", "medium", "tight"]
muIdLabel = ["looseMuIso", "mediumMuIso", "tightMuIso"]

histList = ["deltaRTauTau", "Tau1Pt", "Tau2Pt", "invMassMuMu", "visMassMuMuTauTau"]
histLabel = ["#DeltaR(#mu_{3}#mu_{4})", "p_{T}(#mu_{3})[GeV]", "p_{T}(#mu_{4})[GeV]", "M(#mu_{1}#mu_{2})[GeV]", "M(4#mu)[GeV]"]
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

prefix='root://cmseos.fnal.gov/'

whichChannel = 'TauMuTauMu'
whichYear = '2017'

inputDir=prefix+'/eos/uscms/store/user/zfwd666/{}/bkgEffCheck/{}/'.format(whichYear, whichChannel)
outputDirData=prefix+'/eos/uscms/store/user/zhangj/HaaLimits/RooDataHists/Data/'
outputDirDataDriven=prefix+'/eos/uscms/store/user/zhangj/HaaLimits/RooDataHists/DataDriven/'


inputFakeFile = ROOT.TFile(inputDir+"fakeTauEff_JetFakeMu.root")

for j,imuid in enumerate(muIdList):

    # ===========  prepare the canvas for comparison  ===============
    #canvas = ROOT.TCanvas("comparison","data",900,900)
    #canvas.cd()
    #canvas.SetTopMargin(0.06)
    #canvas.SetLeftMargin(0.16)
    #canvas.SetBottomMargin(0.14)
    # ==============================================================

    #legend = ROOT.TLegend(0.55,0.14,0.95,0.27)
    legend = ROOT.TLegend(0.55,0.74,0.95,0.94)
    legend.SetFillColor(0)
    legend.SetTextSize(0.04)

    globals()["data3P1FFile" + str(j)] = ROOT.TFile(inputDir+"3P1F_" + imuid + ".root")
    globals()["data2P2FFile" + str(j)] = ROOT.TFile(inputDir+"2P2F_" + imuid + ".root")
    globals()["zz3P1FFile" + str(j)] = ROOT.TFile(inputDir+"3P1F_" + imuid + "_zz.root")
    globals()["zz4PFile" + str(j)] = ROOT.TFile(inputDir+"4P_" + imuid + "_zz.root")

    globals()["data3P1FTree" + str(j)] = globals()["data3P1FFile" + str(j)].Get("TreeMuMuTauTau")
    globals()["data2P2FTree" + str(j)] = globals()["data2P2FFile" + str(j)].Get("TreeMuMuTauTau")
    globals()["zz3P1FTree" + str(j)] = globals()["zz3P1FFile" + str(j)].Get("TreeMuMuTauTau")
    globals()["zz4PTree" + str(j)] = globals()["zz4PFile" + str(j)].Get("TreeMuMuTauTau")
    histFakeEff = inputFakeFile.Get(muIdLabel[j])

    globals()["data3P1FHist" + str(j)] = ROOT.TH1D()
    globals()["data2P2FHist" + str(j)] = ROOT.TH1D()
    globals()["data2P2FextHist" + str(j)] = ROOT.TH1D()
    globals()["zz3P1FHist" + str(j)] = ROOT.TH1D()
    globals()["zz4PHist" + str(j)] = ROOT.TH1D()

    globals()["2Ddata3P1FHist" + str(j)] = ROOT.TH2D()
    globals()["2Ddata2P2FHist" + str(j)] = ROOT.TH2D()
    globals()["2Ddata2P2FextHist" + str(j)] = ROOT.TH2D()
    globals()["2Dzz3P1FHist" + str(j)] = ROOT.TH2D()
    globals()["2Dzz4PHist" + str(j)] = ROOT.TH2D()

    nbinsx = 60
    nbinsy = 200

    histKey = "invMassMuMu"
    globals()["data3P1FHist" + str(j)] = ROOT.TH1D(histKey + "3P1F", histKey + "3P1F", nbinsx, 0, 60)
    globals()["data2P2FHist" + str(j)] = ROOT.TH1D(histKey + "2P2F", histKey + "2P2F", nbinsx, 0, 60)
    globals()["data2P2FextHist" + str(j)] = ROOT.TH1D(histKey + "2P2F_ext", histKey + "2P2F_ext", nbinsx, 0, 60)
    globals()["zz3P1FHist" + str(j)] = ROOT.TH1D(histKey + "3P1F_ZZ", histKey + "3P1F_ZZ", nbinsx, 0, 60)
    globals()["zz4PHist" + str(j)] = ROOT.TH1D(histKey + "4P_ZZ", histKey + "4P_ZZ", nbinsx, 0, 60)

    histKey = "invMassMuMuVisMassMuMuTauTau"
    globals()["2Ddata3P1FHist" + str(j)] = ROOT.TH2D(histKey + "3P1F", histKey + "3P1F", nbinsx, 0, 60, nbinsy, 0, 1000)
    globals()["2Ddata2P2FHist" + str(j)] = ROOT.TH2D(histKey + "2P2F", histKey + "2P2F", nbinsx, 0, 60, nbinsy, 0, 1000)
    globals()["2Ddata2P2FextHist" + str(j)] = ROOT.TH2D(histKey + "2P2F_ext", histKey + "2P2F_ext", nbinsx, 0, 60, nbinsy, 0, 1000)
    globals()["2Dzz3P1FHist" + str(j)] = ROOT.TH2D(histKey + "3P1F_ZZ", histKey + "3P1F_ZZ", nbinsx, 0, 60, nbinsy, 0, 1000)
    globals()["2Dzz4PHist" + str(j)] = ROOT.TH2D(histKey + "4P_ZZ", histKey + "4P_ZZ", nbinsx, 0, 60, nbinsy, 0, 1000)

    for event in globals()["data3P1FTree" + str(j)]:

        fakeEff = 1.0
        nbins = histFakeEff.GetNbinsX()
        for ibin in xrange(nbins):
            binlowEdge = histFakeEff.GetXaxis().GetBinLowEdge(ibin+1)
            binhighEdge = histFakeEff.GetXaxis().GetBinLowEdge(ibin+1) + histFakeEff.GetXaxis().GetBinWidth(ibin+1)
            if (event.Tau2Pt >= binlowEdge and event.Tau2Pt < binhighEdge):
                fakeEff = histFakeEff.GetBinContent(ibin+1)/(1.0-histFakeEff.GetBinContent(ibin+1))

        globals()["data3P1FHist" + str(j)].Fill(event.invMassMuMu, fakeEff)

        globals()["2Ddata3P1FHist" + str(j)].Fill(event.invMassMuMu, event.visMassMuMuTauTau, fakeEff)

    globals()["data3P1FHist" + str(j)].Sumw2()
    globals()["2Ddata3P1FHist" + str(j)].Sumw2()
    #globals()["data3P1FHist" + str(j)].SetStats(0)
    #globals()["data3P1FHist" + str(j)].SetFillStyle(0)
    #globals()["data3P1FHist" + str(j)].SetLineColor(ROOT.kRed)
    #globals()["data3P1FHist" + str(j)].SetLineWidth(2)
    #globals()["data3P1FHist" + str(j)].GetXaxis().SetTitle(histLabel[ihist])
    #globals()["data3P1FHist" + str(j)].GetXaxis().SetTitleOffset(1.3)
    #globals()["data3P1FHist" + str(j)].GetXaxis().SetTitleSize(0.05)
    #globals()["data3P1FHist" + str(j)].GetXaxis().SetLabelSize(0.04)
    #globals()["data3P1FHist" + str(j)].GetYaxis().SetTitle("# Events")
    #globals()["data3P1FHist" + str(j)].GetYaxis().SetTitleOffset(1.3)
    #globals()["data3P1FHist" + str(j)].GetYaxis().SetTitleSize(0.05)
    #globals()["data3P1FHist" + str(j)].GetYaxis().SetLabelSize(0.05)


    for event in globals()["data2P2FTree" + str(j)]:

        fakeEff1 = 0.5
        fakeEff2 = 0.5
        fakeEff = 1.0
        nbins = histFakeEff.GetNbinsX()
        for ibin in xrange(nbins):
            binlowEdge = histFakeEff.GetXaxis().GetBinLowEdge(ibin+1)
            binhighEdge = histFakeEff.GetXaxis().GetBinLowEdge(ibin+1) + histFakeEff.GetXaxis().GetBinWidth(ibin+1)
            if (event.Tau1Pt >= binlowEdge and event.Tau1Pt < binhighEdge):
                fakeEff1 = histFakeEff.GetBinContent(ibin+1)/(1.0-histFakeEff.GetBinContent(ibin+1))

            if (event.Tau2Pt >= binlowEdge and event.Tau2Pt < binhighEdge):
                fakeEff2 = histFakeEff.GetBinContent(ibin+1)/(1.0-histFakeEff.GetBinContent(ibin+1))
                fakeEff = histFakeEff.GetBinContent(ibin+1)/(1.0-histFakeEff.GetBinContent(ibin+1))

        
        globals()["data2P2FHist" + str(j)].Fill(event.invMassMuMu, (fakeEff1 + fakeEff2)*fakeEff)

        globals()["2Ddata2P2FHist" + str(j)].Fill(event.invMassMuMu, event.visMassMuMuTauTau, (fakeEff1 + fakeEff2)*fakeEff)

    globals()["data2P2FHist" + str(j)].Sumw2()
    globals()["2Ddata2P2FHist" + str(j)].Sumw2()


    for event in globals()["zz3P1FTree" + str(j)]:

        fakeEff = 1.0
        nbins = histFakeEff.GetNbinsX()
        for ibin in xrange(nbins):
            binlowEdge = histFakeEff.GetXaxis().GetBinLowEdge(ibin+1)
            binhighEdge = histFakeEff.GetXaxis().GetBinLowEdge(ibin+1) + histFakeEff.GetXaxis().GetBinWidth(ibin+1)
            if (event.Tau2Pt >= binlowEdge and event.Tau2Pt < binhighEdge):
                fakeEff = histFakeEff.GetBinContent(ibin+1)/(1.0-histFakeEff.GetBinContent(ibin+1))

        globals()["zz3P1FHist" + str(j)].Fill(event.invMassMuMu, event.eventWeight*fakeEff)

        globals()["2Dzz3P1FHist" + str(j)].Fill(event.invMassMuMu, event.visMassMuMuTauTau, event.eventWeight*fakeEff)


    globals()["zz3P1FHist" + str(j)].Sumw2()
    globals()["2Dzz3P1FHist" + str(j)].Sumw2()
    globals()["zz3P1FHist" + str(j)].Scale(41.529*1.212*1000)
    globals()["2Dzz3P1FHist" + str(j)].Scale(41.529*1.212*1000)


    for event in globals()["data2P2FTree" + str(j)]:

        fakeEff1 = 1.0
        fakeEff2 = 1.0
        nbins = histFakeEff.GetNbinsX()
        for ibin in xrange(nbins):
            binlowEdge = histFakeEff.GetXaxis().GetBinLowEdge(ibin+1)
            binhighEdge = histFakeEff.GetXaxis().GetBinLowEdge(ibin+1) + histFakeEff.GetXaxis().GetBinWidth(ibin+1)
            if (event.Tau1Pt >= binlowEdge and event.Tau1Pt < binhighEdge):
                fakeEff1 = histFakeEff.GetBinContent(ibin+1)/(1.0-histFakeEff.GetBinContent(ibin+1))

            if (event.Tau2Pt >= binlowEdge and event.Tau2Pt < binhighEdge):
                fakeEff2 = histFakeEff.GetBinContent(ibin+1)/(1.0-histFakeEff.GetBinContent(ibin+1))

        
        globals()["data2P2FextHist" + str(j)].Fill(event.invMassMuMu, fakeEff1*fakeEff2)

        globals()["2Ddata2P2FextHist" + str(j)].Fill(event.invMassMuMu, event.visMassMuMuTauTau, fakeEff1*fakeEff2)

    globals()["data2P2FextHist" + str(j)].Sumw2()
    globals()["2Ddata2P2FextHist" + str(j)].Sumw2()
    #globals()["data2P2FextHist" + str(j)].SetStats(0)


    for event in globals()["zz4PTree" + str(j)]:

        
        globals()["zz4PHist" + str(j)].Fill(event.invMassMuMu, event.eventWeight)

        globals()["2Dzz4PHist" + str(j)].Fill(event.invMassMuMu, event.visMassMuMuTauTau, event.eventWeight)

    #globals()["zz4PHist" + str(j)].SetStats(0)
    globals()["zz4PHist" + str(j)].Sumw2()
    globals()["2Dzz4PHist" + str(j)].Sumw2()
    globals()["zz4PHist" + str(j)].Scale(41.529*1.212*1000)
    globals()["2Dzz4PHist" + str(j)].Scale(41.529*1.212*1000)
    #globals()["zz4PHist" + str(j)].SetFillStyle(1001)
    #globals()["zz4PHist" + str(j)].SetFillColor(ROOT.kBlue)
    #globals()["zz4PHist" + str(j)].SetLineColor(ROOT.kBlue)


    globals()["data3P1FHist" + str(j)].Add(globals()["data2P2FHist" + str(j)], -1)
    globals()["data3P1FHist" + str(j)].Add(globals()["zz3P1FHist" + str(j)], -1)
    globals()["data3P1FHist" + str(j)].Add(globals()["data2P2FextHist" + str(j)])
    globals()["data3P1FHist" + str(j)].Add(globals()["zz4PHist" + str(j)])

    globals()["2Ddata3P1FHist" + str(j)].Add(globals()["2Ddata2P2FHist" + str(j)], -1)
    globals()["2Ddata3P1FHist" + str(j)].Add(globals()["2Dzz3P1FHist" + str(j)], -1)
    globals()["2Ddata3P1FHist" + str(j)].Add(globals()["2Ddata2P2FextHist" + str(j)])
    globals()["2Ddata3P1FHist" + str(j)].Add(globals()["2Dzz4PHist" + str(j)])

    #print "2Ddata3P1FHist" + str(j), globals()["2Ddata3P1FHist" + str(j)]

    nbins = globals()["data3P1FHist" + str(j)].GetNbinsX()
    for ibin in xrange(nbins):
        binValue = globals()["data3P1FHist" + str(j)].GetBinContent(ibin+1)
        if binValue < 0:
            #print "***** negative bins: ", binValue
            globals()["data3P1FHist" + str(j)].SetBinContent(ibin+1, 0)
            globals()["data3P1FHist" + str(j)].SetBinError(ibin+1, 0)


    
    nbinsX = globals()["2Ddata3P1FHist" + str(j)].GetNbinsX()
    nbinsY = globals()["2Ddata3P1FHist" + str(j)].GetNbinsY()
    for ibinx in xrange(nbinsX):
        for ibiny in xrange(nbinsY):
            binValue = globals()["2Ddata3P1FHist" + str(j)].GetBinContent(ibinx+1, ibiny+1)
            if binValue < 0:
                globals()["2Ddata3P1FHist" + str(j)].SetBinContent(ibinx+1, ibiny+1, 0)
                globals()["2Ddata3P1FHist" + str(j)].SetBinError(ibinx+1, ibiny+1, 0)
                

    globals()["fout3" + str(j)] = ROOT.TFile(outputDirDataDriven+"TauMuTauMu_" + "signalRegion" + "_" + "MuIso_" + imuid + ".root", "RECREATE")

    #print "data3P1FHist" + str(j), globals()["data3P1FHist" + str(j)]

    globals()["fout3" + str(j)].cd()

    #print "data3P1FHist" + str(j), globals()["data3P1FHist" + str(j)]
    globals()["data3P1FHist" + str(j)].Write()
    globals()["2Ddata3P1FHist" + str(j)].Write()

    globals()["fout3" + str(j)].Close()
    

    #legend.AddEntry(globals()["data3P1FHist" + str(j)],"3P1F+2P2F extr.","f")
    #legend.AddEntry(globals()["zz4PHist" + str(j)], "ZZ(4l)", "f")

    #if histKey.find("Pt")!=-1:
    #   canvas.SetLogy()
    #   globals()["data3P1FHist" + str(j)].GetYaxis().SetRangeUser(0.5, globals()["data3P1FHist" + str(j)].GetMaximum()*100.0)

    #if histKey.find("deltaR")!=-1:
    #   canvas.SetLogy()
    #   globals()["data3P1FHist" + str(j)].GetYaxis().SetRangeUser(0.5, globals()["data3P1FHist" + str(j)].GetMaximum()*100.0)

    #if histKey.find("Mass")!=-1:
    #   globals()["data3P1FHist" + str(j)].GetYaxis().SetRangeUser(0.5, globals()["data3P1FHist" + str(j)].GetMaximum()*1.2)

    #globals()["data3P1FHist" + str(j)].Draw("HIST")
    #globals()["zz4PHist" + str(j)].Draw("HIST same")
    #globals()["data3P1FHist" + str(j)].Draw("HIST same")
    #ROOT.gPad.RedrawAxis()
    #legend.Draw("same")
    #label1.Draw("same")
    #label2.Draw("same")
    #label3.Draw("same")

    #canvas.SaveAs("plots/4P/" + histKey + "_" + imuid +"_Yield.pdf")
