import os
import sys
import logging
import math
from array import array
from collections import OrderedDict

import ROOT

from CombineLimits.Plotter.PlotterBase import PlotterBase
from CombineLimits.Utilities.utilities import python_mkdir
import CombineLimits.Plotter.CMS_lumi as CMS_lumi
import CombineLimits.Plotter.tdrstyle as tdrstyle

ROOT.gROOT.SetBatch(ROOT.kTRUE)
ROOT.gROOT.ProcessLine("gErrorIgnoreLevel = 1001;")
tdrstyle.setTDRStyle()
ROOT.gStyle.SetPalette(1)

class LimitPlotter(PlotterBase):
    '''Basic limit plotter utilities'''

    def __init__(self,**kwargs):
        '''Initialize the plotter'''
        super(LimitPlotter, self).__init__('Limits',**kwargs)
        # initialize stuff

    def plotLimit(self,xvals,quartiles,savename,**kwargs):
        '''Plot limits'''
        xaxis = kwargs.pop('xaxis','x')
        yaxis = kwargs.pop('yaxis','95% CLs Upper Limit on #sigma/#sigma_{model}')
        blind = kwargs.pop('blind',True)
        lumipos = kwargs.pop('lumipos',11)
        isprelim = kwargs.pop('isprelim',True)
        legendpos = kwargs.pop('legendpos',31)
        numcol = kwargs.pop('numcol',1)
        asymptoticFilenames = kwargs.pop('asymptoticFilenames',[])
        smooth = kwargs.pop('smooth',False)
        ymin = kwargs.pop('ymin',None)
        ymax = kwargs.pop('ymax',None)
        logy = kwargs.pop('logy',1)
        plotunity = kwargs.pop('plotunity',True)
        leftmargin = kwargs.pop('leftmargin',None)

        logging.info('Plotting {0}'.format(savename))

        canvas = ROOT.TCanvas(savename,savename,50,50,600,600)
        canvas.SetLogy(logy)
        if leftmargin: canvas.SetLeftMargin(leftmargin)

        limits = quartiles

        n = len(xvals)
        twoSigma = ROOT.TGraph(2*n)
        oneSigma = ROOT.TGraph(2*n)
        expected = ROOT.TGraph(n)
        observed = ROOT.TGraph(n)
        twoSigma_low = ROOT.TGraph(n)
        twoSigma_high = ROOT.TGraph(n)
        oneSigma_low = ROOT.TGraph(n)
        oneSigma_high = ROOT.TGraph(n)
        twoSigmaForSmoothing_low = ROOT.TGraph(n)
        twoSigmaForSmoothing_high = ROOT.TGraph(n)
        oneSigmaForSmoothing_low = ROOT.TGraph(n)
        oneSigmaForSmoothing_high = ROOT.TGraph(n)
        expectedForSmoothing = ROOT.TGraph(n)
        twoSigma_asym = ROOT.TGraph(2*n)
        oneSigma_asym = ROOT.TGraph(2*n)
        expected_asym = ROOT.TGraph(n)
        observed_asym = ROOT.TGraph(n)

        for i in range(len(xvals)):
            if not all(limits[xvals[i]]):
                print i, xvals[i], limits[xvals[i]]
                continue
            twoSigma.SetPoint(     i,   xvals[i],     limits[xvals[i]][0]) # 0.025
            oneSigma.SetPoint(     i,   xvals[i],     limits[xvals[i]][1]) # 0.16
            expected.SetPoint(     i,   xvals[i],     limits[xvals[i]][2]) # 0.5
            #oneSigma.SetPoint(     n+i, xvals[n-i-1], limits[xvals[n-i-1]][3]) # 0.84
            #twoSigma.SetPoint(     n+i, xvals[n-i-1], limits[xvals[n-i-1]][4]) # 0.975
            oneSigma.SetPoint(2*n-i-1,  xvals[i],     limits[xvals[i]][3]) # 0.84
            twoSigma.SetPoint(2*n-i-1,  xvals[i],     limits[xvals[i]][4]) # 0.975
            observed.SetPoint(     i,   xvals[i],     limits[xvals[i]][5]) # obs
            twoSigma_high.SetPoint(i,   xvals[i],     limits[xvals[i]][0]) # 0.025
            oneSigma_high.SetPoint(i,   xvals[i],     limits[xvals[i]][1]) # 0.16
            #oneSigma_low.SetPoint( i,   xvals[n-i-1], limits[xvals[n-i-1]][3]) # 0.84
            #twoSigma_low.SetPoint( i,   xvals[n-i-1], limits[xvals[n-i-1]][4]) # 0.975
            oneSigma_low.SetPoint(n-i-1,xvals[i],     limits[xvals[i]][3]) # 0.84
            twoSigma_low.SetPoint(n-i-1,xvals[i],     limits[xvals[i]][4]) # 0.975
            twoSigmaForSmoothing_high.SetPoint(i, xvals[i],     math.log(limits[xvals[i]][0])) # 0.025
            oneSigmaForSmoothing_high.SetPoint(i, xvals[i],     math.log(limits[xvals[i]][1])) # 0.16
            #oneSigmaForSmoothing_low.SetPoint( i, xvals[n-i-1], math.log(limits[xvals[n-i-1]][3])) # 0.84
            #twoSigmaForSmoothing_low.SetPoint( i, xvals[n-i-1], math.log(limits[xvals[n-i-1]][4])) # 0.975
            oneSigmaForSmoothing_low.SetPoint(n-i-1, xvals[i],  math.log(limits[xvals[i]][3])) # 0.84
            twoSigmaForSmoothing_low.SetPoint(n-i-1, xvals[i],  math.log(limits[xvals[i]][4])) # 0.975
            expectedForSmoothing.SetPoint(     i, xvals[i],     math.log(limits[xvals[i]][2])) # 0.5
            if asymptoticFilenames:
                twoSigma_asym.SetPoint(i,  xvals[i],     limits_asym[xvals[i]][0]) # 0.025
                oneSigma_asym.SetPoint(i,  xvals[i],     limits_asym[xvals[i]][1]) # 0.16
                expected_asym.SetPoint(i,  xvals[i],     limits_asym[xvals[i]][2]) # 0.5
                #oneSigma_asym.SetPoint(n+i,xvals[n-i-1], limits_asym[xvals[n-i-1]][3]) # 0.84
                #twoSigma_asym.SetPoint(n+i,xvals[n-i-1], limits_asym[xvals[n-i-1]][4]) # 0.975
                oneSigma_asym.SetPoint(2*n-i-1,xvals[i], limits_asym[xvals[i]][3]) # 0.84
                twoSigma_asym.SetPoint(2*n-i-1,xvals[i], limits_asym[xvals[i]][4]) # 0.975
                observed_asym.SetPoint(i,  xvals[i],     limits_asym[xvals[i]][5]) # obs

        if smooth: # smooth out the expected bands
            twoSigmaSmoother_low  = ROOT.TGraphSmooth()
            twoSigmaSmoother_high = ROOT.TGraphSmooth()
            oneSigmaSmoother_low  = ROOT.TGraphSmooth()
            oneSigmaSmoother_high = ROOT.TGraphSmooth()
            expectedSmoother      = ROOT.TGraphSmooth()
            #twoSigmaSmooth_low    = twoSigmaSmoother_low.Approx(twoSigma_low,  'linear',n)
            #twoSigmaSmooth_high   = twoSigmaSmoother_high.Approx(twoSigma_high,'linear',n)
            #oneSigmaSmooth_low    = oneSigmaSmoother_low.Approx(oneSigma_low,  'linear',n)
            #oneSigmaSmooth_high   = oneSigmaSmoother_high.Approx(oneSigma_high,'linear',n)
            #expectedSmooth        = expectedSmoother.Approx(expected,          'linear',n)
            twoSigmaSmooth_low    = twoSigmaSmoother_low.SmoothKern( twoSigmaForSmoothing_low, 'normal',200,n)
            twoSigmaSmooth_high   = twoSigmaSmoother_high.SmoothKern(twoSigmaForSmoothing_high,'normal',200,n)
            oneSigmaSmooth_low    = oneSigmaSmoother_low.SmoothKern( oneSigmaForSmoothing_low, 'normal',200,n)
            oneSigmaSmooth_high   = oneSigmaSmoother_high.SmoothKern(oneSigmaForSmoothing_high,'normal',200,n)
            expectedSmooth        = expectedSmoother.SmoothKern(     expectedForSmoothing,     'normal',200,n)
            #twoSigmaSmooth_low    = twoSigmaSmoother_low.SmoothLowess(twoSigma_low,  '',0.4)
            #twoSigmaSmooth_high   = twoSigmaSmoother_high.SmoothLowess(twoSigma_high,'',0.4)
            #oneSigmaSmooth_low    = oneSigmaSmoother_low.SmoothLowess(oneSigma_low,  '',0.4)
            #oneSigmaSmooth_high   = oneSigmaSmoother_high.SmoothLowess(oneSigma_high,'',0.4)
            #expectedSmooth        = expectedSmoother.SmoothLowess(expected,          '',0.4)
            #twoSigmaSmooth_low    = twoSigmaSmoother_low.SmoothSuper(twoSigma_low,  '',0,0)
            #twoSigmaSmooth_high   = twoSigmaSmoother_high.SmoothSuper(twoSigma_high,'',0,0)
            #oneSigmaSmooth_low    = oneSigmaSmoother_low.SmoothSuper(oneSigma_low,  '',0,0)
            #oneSigmaSmooth_high   = oneSigmaSmoother_high.SmoothSuper(oneSigma_high,'',0,0)
            #expectedSmooth        = expectedSmoother.SmoothSuper(expected,          '',0,0)
            for i in range(n-2):
                twoSigma_high.SetPoint(i+1,   twoSigmaSmooth_high.GetX()[i+1],    math.exp(twoSigmaSmooth_high.GetY()[i+1]))
                twoSigma_low.SetPoint( i+1,   twoSigmaSmooth_low.GetX()[i+1],     math.exp(twoSigmaSmooth_low.GetY()[i+1]))
                oneSigma_high.SetPoint(i+1,   oneSigmaSmooth_high.GetX()[i+1],    math.exp(oneSigmaSmooth_high.GetY()[i+1]))
                oneSigma_low.SetPoint( i+1,   oneSigmaSmooth_low.GetX()[i+1],     math.exp(oneSigmaSmooth_low.GetY()[i+1]))
                expected.SetPoint(     i+1,   expectedSmooth.GetX()[i+1],         math.exp(expectedSmooth.GetY()[i+1]))
            for i in range(n-2):
                twoSigma.SetPoint(     i+1,   twoSigma_high.GetX()[i+1],    twoSigma_high.GetY()[i+1])
                twoSigma.SetPoint(     n+i+1, twoSigma_low.GetX()[n-1-i-1], twoSigma_low.GetY()[n-1-i-1])
                oneSigma.SetPoint(     i+1,   oneSigma_high.GetX()[i+1],    oneSigma_high.GetY()[i+1])
                oneSigma.SetPoint(     n+i+1, oneSigma_low.GetX()[n-1-i-1], oneSigma_low.GetY()[n-1-i-1])

        twoSigma.SetFillColor(ROOT.kOrange)
        twoSigma.SetLineColor(ROOT.kOrange)
        twoSigma.SetMarkerStyle(0)
        oneSigma.SetFillColor(ROOT.kGreen+1)
        oneSigma.SetLineColor(ROOT.kGreen+1)
        oneSigma.SetMarkerStyle(0)
        expected.SetLineStyle(7)
        expected.SetMarkerStyle(0)
        expected.SetFillStyle(0)
        observed.SetMarkerStyle(0)
        observed.SetFillStyle(0)

        expected.GetXaxis().SetLimits(xvals[0],xvals[-1])
        expected.GetXaxis().SetTitle(xaxis)
        expected.GetYaxis().SetTitle(yaxis)
        expected.GetYaxis().SetTitleSize(0.05)
        expected.GetYaxis().SetTitleOffset(1.6)

        expected.Draw()
        if ymin: expected.SetMinimum(ymin)
        if ymax: expected.SetMaximum(ymax)
        twoSigma.Draw('f')
        oneSigma.Draw('f')

        expected.Draw('same')
        ROOT.gPad.RedrawAxis()
        if not blind: observed.Draw('same')

        ratiounity = ROOT.TLine(expected.GetXaxis().GetXmin(),1,expected.GetXaxis().GetXmax(),1)
        if plotunity: ratiounity.Draw()

        # get the legend
        entries = [
            [expected,'Median expected','l'],
            [oneSigma,'68% expected','F'],
            [twoSigma,'95% expected','F'],
        ]
        if not blind: entries = [[observed,'Observed','l']] + entries
        legend = self._getLegend(entries=entries,numcol=numcol,position=legendpos)
        legend.Draw()

        # cms lumi styling
        self._setStyle(canvas,position=lumipos,preliminary=isprelim)

        self._save(canvas,savename)


    def plotPValue(self,xvals,quartiles,savename,**kwargs):
        '''Plot p-values'''
        xaxis = kwargs.pop('xaxis','#Phi^{++} Mass (GeV)')
        yaxis = kwargs.pop('yaxis','Local p-value')
        blind = kwargs.pop('blind',True)
        lumipos = kwargs.pop('lumipos',11)
        isprelim = kwargs.pop('isprelim',True)
        legendpos = kwargs.pop('legendpos',31)
        numcol = kwargs.pop('numcol',1)
        nsigmas = kwargs.pop('nsigmas',7)
        ymin = kwargs.pop('ymin',ROOT.RooStats.SignificanceToPValue(nsigmas))
        ymax = kwargs.pop('ymax',1)
        logy = kwargs.pop('logy',1)

        logging.info('Plotting {0}'.format(savename))

        canvas = ROOT.TCanvas(savename,savename,50,50,600,600)
        canvas.SetLogy(logy)
        canvas.SetRightMargin(0.06)

        limits = quartiles

        n = len(xvals)
        expected = ROOT.TGraph(n)
        observed = ROOT.TGraph(n)

        for i in range(len(xvals)):
            expected.SetPoint(     i,   xvals[i],     limits[xvals[i]][0])
            observed.SetPoint(     i,   xvals[i],     limits[xvals[i]][1])

        expected.SetLineStyle(7)
        expected.SetMarkerStyle(0)
        expected.SetFillStyle(0)
        observed.SetMarkerStyle(0)
        observed.SetFillStyle(0)
        observed.SetLineWidth(2)

        expected.GetXaxis().SetLimits(xvals[0],xvals[-1])
        expected.GetXaxis().SetTitle(xaxis)
        expected.GetYaxis().SetTitle(yaxis)

        expected.Draw()
        if ymin: expected.SetMinimum(ymin)
        if ymax: expected.SetMaximum(ymax)

        def getNDC(x,y):
            ROOT.gPad.Update()
            if ROOT.gPad.GetLogx(): x = ROOT.TMath.Log10(x)
            if ROOT.gPad.GetLogy(): y = ROOT.TMath.Log10(y)
            xndc = (x - ROOT.gPad.GetX1())/(ROOT.gPad.GetX2() - ROOT.gPad.GetX1())
            yndc = (y - ROOT.gPad.GetY1())/(ROOT.gPad.GetY2() - ROOT.gPad.GetY1())
            return xndc, yndc

        sigmaratios = {}
        sigmatext = {}
        for s in range(nsigmas):
            sigma = s+1
            p = ROOT.RooStats.SignificanceToPValue(sigma)
            sigmaratios[sigma] = ROOT.TLine(expected.GetXaxis().GetXmin(),p,expected.GetXaxis().GetXmax(),p)
            sigmaratios[sigma].SetLineColor(ROOT.kRed)
            sigmaratios[sigma].Draw()
            sigmatext[sigma] = ROOT.TLatex()
            sigmatext[sigma].SetNDC()
            sigmatext[sigma].SetTextSize(0.04)
            sigmatext[sigma].SetTextColor(ROOT.kRed)
            sigmatext[sigma].DrawLatex(0.95,getNDC(1,p)[1],'{0}#sigma'.format(sigma))

        #expected.Draw('same')
        #ROOT.gPad.RedrawAxis()
        if not blind: observed.Draw('same')

        # get the legend
        entries = [
            [expected,'Median expected','l'],
        ]
        if not blind: entries = [[observed,'Observed','l']] + entries
        legend = self._getLegend(entries=entries,numcol=numcol,position=legendpos)
        legend.Draw()

        # cms lumi styling
        self._setStyle(canvas,position=lumipos,preliminary=isprelim)

        self._save(canvas,savename)

