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
ROOT.gStyle.SetPalette(ROOT.kBlueGreenYellow)
ROOT.TGaxis.SetMaxDigits(3)

#stops = array('d',[0, 0.749, 0.751, 1.0])
#red   = array('d',[  0./255,   51./255,  51./255,   0./255])
#green = array('d',[ 51./255,  204./255, 153./255, 204./255])
#blue  = array('d',[204./255,  255./255,  51./255,   0./255])
#number = 4
#nb = 255
#ROOT.TColor.CreateGradientColorTable(number, stops, red, green, blue, nb)
#ROOT.gStyle.SetPalette(nb)

#ROOT.gStyle.SetPalette(ROOT.kBird)
#ROOT.gStyle.SetPalette(ROOT.kDeepSea)

# Manually reimplement DeepSea with a white bit at the top
stops = array('d',[ 0.0000, 0.1250, 0.2500, 0.3750, 0.5000, 0.6250, 0.7500, 0.8750, 0.998, 0.999, 1.0000,])
red   = array('d',[  0./255.,  9./255., 13./255., 17./255., 24./255.,  32./255.,  27./255.,  25./255.,  29./255., 255./255., 255./255.])
green = array('d',[  0./255.,  0./255.,  0./255.,  2./255., 37./255.,  74./255., 113./255., 160./255., 221./255., 255./255., 255./255.])
blue  = array('d',[ 28./255., 42./255., 59./255., 78./255., 98./255., 129./255., 154./255., 184./255., 221./255., 255./255., 255./255.])
nb = ROOT.TColor.CreateGradientColorTable(11, stops, red, green, blue, 255, 1)
ROOT.gStyle.SetPalette(nb)

ROOT.gStyle.SetNumberContours(255)

class LimitPlotter(PlotterBase):
    '''Basic limit plotter utilities'''

    def __init__(self,**kwargs):
        '''Initialize the plotter'''
        super(LimitPlotter, self).__init__('Limits',**kwargs)
        # initialize stuff

    def _getGraphs(self,xvals,limits,**kwargs):
        xVar = kwargs.pop('xVar',None)
        smooth = kwargs.pop('smooth',False)
        model = kwargs.pop('model',None)
        scales = kwargs.pop('scales',None)
        modelkey = kwargs.pop('modelkey',None)
        y = kwargs.pop('y',None)
        detailed = kwargs.pop('detailed',False)

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

        if xVar:
            w = ROOT.RooRealVar('w','w',0,10000)
            twoSigmaDS_low  = ROOT.RooDataSet('twoSigmaLow', 'twoSigmaLow', ROOT.RooArgSet(xVar,w),w.GetName())
            twoSigmaDS_high = ROOT.RooDataSet('twoSigmaHigh','twoSigmaHigh',ROOT.RooArgSet(xVar,w),w.GetName())
            oneSigmaDS_low  = ROOT.RooDataSet('oneSigmaLow', 'oneSigmaLow', ROOT.RooArgSet(xVar,w),w.GetName())
            oneSigmaDS_high = ROOT.RooDataSet('oneSigmaHigh','oneSigmaHigh',ROOT.RooArgSet(xVar,w),w.GetName())
            expectedDS      = ROOT.RooDataSet('expected',    'expected',    ROOT.RooArgSet(xVar,w),w.GetName())

        for i in range(len(xvals)):
            if not all(limits[xvals[i]]):
                print i, xvals[i], limits[xvals[i]]
                continue
            twoSigma.SetPoint(     i,   xvals[i],     limits[xvals[i]][0]) # 0.025
            oneSigma.SetPoint(     i,   xvals[i],     limits[xvals[i]][1]) # 0.16
            expected.SetPoint(     i,   xvals[i],     limits[xvals[i]][2]) # 0.5
            oneSigma.SetPoint(2*n-i-1,  xvals[i],     limits[xvals[i]][3]) # 0.84
            twoSigma.SetPoint(2*n-i-1,  xvals[i],     limits[xvals[i]][4]) # 0.975
            observed.SetPoint(     i,   xvals[i],     limits[xvals[i]][5]) # obs
            twoSigma_high.SetPoint(i,   xvals[i],     limits[xvals[i]][0]) # 0.025
            oneSigma_high.SetPoint(i,   xvals[i],     limits[xvals[i]][1]) # 0.16
            oneSigma_low.SetPoint(n-i-1,xvals[i],     limits[xvals[i]][3]) # 0.84
            twoSigma_low.SetPoint(n-i-1,xvals[i],     limits[xvals[i]][4]) # 0.975
            twoSigmaForSmoothing_high.SetPoint(i, xvals[i],     math.log(limits[xvals[i]][0])) # 0.025
            oneSigmaForSmoothing_high.SetPoint(i, xvals[i],     math.log(limits[xvals[i]][1])) # 0.16
            oneSigmaForSmoothing_low.SetPoint(n-i-1, xvals[i],  math.log(limits[xvals[i]][3])) # 0.84
            twoSigmaForSmoothing_low.SetPoint(n-i-1, xvals[i],  math.log(limits[xvals[i]][4])) # 0.975
            expectedForSmoothing.SetPoint(     i, xvals[i],     math.log(limits[xvals[i]][2])) # 0.5
            if xVar:
                xVar.setVal(xvals[i])
                w.setVal(limits[xvals[i]][0])
                twoSigmaDS_high.add(ROOT.RooArgSet(xVar,w))
                w.setVal(limits[xvals[i]][1])
                oneSigmaDS_high.add(ROOT.RooArgSet(xVar,w))
                w.setVal(limits[xvals[i]][2])
                expectedDS.add(ROOT.RooArgSet(xVar,w))
                w.setVal(limits[xvals[i]][3])
                oneSigmaDS_low.add(ROOT.RooArgSet(xVar,w))
                w.setVal(limits[xvals[i]][4])
                twoSigmaDS_low.add(ROOT.RooArgSet(xVar,w))

        
        def fit(savename,ds):
            model.fitTo(ds,ROOT.RooFit.Save(),ROOT.RooFit.SumW2Error(True))
            xFrame = xVar.frame()
            ds.plotOn(xFrame)
            model.plotOn(xFrame)
            canvas = ROOT.TCanvas(savename,savename,800,800)
            xFrame.Draw()
            canvas.Print('{0}.png'.format(savename))
            
        if model and xVar:
            # smooth to a pdf
            fit('twoSigma_low', twoSigmaDS_low)
            fit('oneSigma_low', oneSigmaDS_low)
            fit('expected',     expectedDS)
            fit('oneSigma_high',oneSigmaDS_high)
            fit('twoSigma_high',twoSigmaDS_high)


        smoothlog = False
        if smooth: # smooth out the expected bands

            # smooth via function
            twoSigmaSmoother_low  = ROOT.TGraphSmooth()
            twoSigmaSmoother_high = ROOT.TGraphSmooth()
            oneSigmaSmoother_low  = ROOT.TGraphSmooth()
            oneSigmaSmoother_high = ROOT.TGraphSmooth()
            expectedSmoother      = ROOT.TGraphSmooth()
            # smooth log, good for exponentially changing
            if smoothlog:
                twoSigmaSmooth_low    = twoSigmaSmoother_low.SmoothKern( twoSigmaForSmoothing_low, 'normal',0.5,n)
                twoSigmaSmooth_high   = twoSigmaSmoother_high.SmoothKern(twoSigmaForSmoothing_high,'normal',0.5,n)
                oneSigmaSmooth_low    = oneSigmaSmoother_low.SmoothKern( oneSigmaForSmoothing_low, 'normal',0.5,n)
                oneSigmaSmooth_high   = oneSigmaSmoother_high.SmoothKern(oneSigmaForSmoothing_high,'normal',0.5,n)
                expectedSmooth        = expectedSmoother.SmoothKern(     expectedForSmoothing,     'normal',0.5,n)
                for i in range(n-2):
                    twoSigma_high.SetPoint(i+1,   twoSigmaSmooth_high.GetX()[i+1],    math.exp(twoSigmaSmooth_high.GetY()[i+1]))
                    twoSigma_low.SetPoint( i+1,   twoSigmaSmooth_low.GetX()[i+1],     math.exp(twoSigmaSmooth_low.GetY()[i+1]))
                    oneSigma_high.SetPoint(i+1,   oneSigmaSmooth_high.GetX()[i+1],    math.exp(oneSigmaSmooth_high.GetY()[i+1]))
                    oneSigma_low.SetPoint( i+1,   oneSigmaSmooth_low.GetX()[i+1],     math.exp(oneSigmaSmooth_low.GetY()[i+1]))
                    expected.SetPoint(     i+1,   expectedSmooth.GetX()[i+1],         math.exp(expectedSmooth.GetY()[i+1]))
            # smooth linear
            else:
                twoSigmaSmooth_low    = twoSigmaSmoother_low.SmoothKern( twoSigma_low, 'normal',1.3,n) # originally 0.3, increased to smooth out highmass
                twoSigmaSmooth_high   = twoSigmaSmoother_high.SmoothKern(twoSigma_high,'normal',1.3,n)
                oneSigmaSmooth_low    = oneSigmaSmoother_low.SmoothKern( oneSigma_low, 'normal',1.3,n)
                oneSigmaSmooth_high   = oneSigmaSmoother_high.SmoothKern(oneSigma_high,'normal',1.3,n)
                expectedSmooth        = expectedSmoother.SmoothKern(     expected,     'normal',1.3,n)
                #twoSigmaSmooth_low    = twoSigmaSmoother_low.SmoothLowess(twoSigma_low,  '',0.1)
                #twoSigmaSmooth_high   = twoSigmaSmoother_high.SmoothLowess(twoSigma_high,'',0.1)
                #oneSigmaSmooth_low    = oneSigmaSmoother_low.SmoothLowess(oneSigma_low,  '',0.1)
                #oneSigmaSmooth_high   = oneSigmaSmoother_high.SmoothLowess(oneSigma_high,'',0.1)
                #expectedSmooth        = expectedSmoother.SmoothLowess(expected,          '',0.1)
                #twoSigmaSmooth_low    = twoSigmaSmoother_low.SmoothSuper(twoSigma_low,  '',0,0)
                #twoSigmaSmooth_high   = twoSigmaSmoother_high.SmoothSuper(twoSigma_high,'',0,0)
                #oneSigmaSmooth_low    = oneSigmaSmoother_low.SmoothSuper(oneSigma_low,  '',0,0)
                #oneSigmaSmooth_high   = oneSigmaSmoother_high.SmoothSuper(oneSigma_high,'',0,0)
                #expectedSmooth        = expectedSmoother.SmoothSuper(expected,          '',0,0)
                for i in range(n-2):
                    x = twoSigmaSmooth_high.GetX()[i+1]
                    if x>3 and x<4: continue # jpsi
                    if x>8.5 and x<11.5: continue # upsilon
                    twoSigma_high.SetPoint(i+1,   twoSigmaSmooth_high.GetX()[i+1],    twoSigmaSmooth_high.GetY()[i+1])
                    twoSigma_low.SetPoint( i+1,   twoSigmaSmooth_low.GetX()[i+1],     twoSigmaSmooth_low.GetY()[i+1])
                    oneSigma_high.SetPoint(i+1,   oneSigmaSmooth_high.GetX()[i+1],    oneSigmaSmooth_high.GetY()[i+1])
                    oneSigma_low.SetPoint( i+1,   oneSigmaSmooth_low.GetX()[i+1],     oneSigmaSmooth_low.GetY()[i+1])
                    expected.SetPoint(     i+1,   expectedSmooth.GetX()[i+1],         expectedSmooth.GetY()[i+1])

            for i in range(n-2):
                twoSigma.SetPoint(     i+1,   twoSigma_high.GetX()[i+1],    twoSigma_high.GetY()[i+1])
                twoSigma.SetPoint(     n+i+1, twoSigma_low.GetX()[n-1-i-1], twoSigma_low.GetY()[n-1-i-1])
                oneSigma.SetPoint(     i+1,   oneSigma_high.GetX()[i+1],    oneSigma_high.GetY()[i+1])
                oneSigma.SetPoint(     n+i+1, oneSigma_low.GetX()[n-1-i-1], oneSigma_low.GetY()[n-1-i-1])

        # now scale
        for i in range(len(xvals)):
            if not all(limits[xvals[i]]):
                print i, xvals[i], limits[xvals[i]]
                continue
            scale = 1
            if scales and modelkey:
                scale = scales[xvals[i]][modelkey].Eval(y)
                if scale<=0: scale = 1e-10
            twoSigma.SetPoint(     i,   twoSigma.GetX()[i],    twoSigma.GetY()[i]*scale) # 0.025
            oneSigma.SetPoint(     i,   oneSigma.GetX()[i],    oneSigma.GetY()[i]*scale) # 0.16
            expected.SetPoint(     i,   expected.GetX()[i],    expected.GetY()[i]*scale) # 0.5
            oneSigma.SetPoint(2*n-i-1,  oneSigma.GetX()[2*n-i-1],    oneSigma.GetY()[2*n-i-1]*scale) # 0.84
            twoSigma.SetPoint(2*n-i-1,  twoSigma.GetX()[2*n-i-1],    twoSigma.GetY()[2*n-i-1]*scale) # 0.975
            observed.SetPoint(     i,   observed.GetX()[i],    observed.GetY()[i]*scale) # obs
        
        twoSigma.SetFillColor(ROOT.kOrange)
        twoSigma.SetLineColor(ROOT.kOrange)
        twoSigma.SetMarkerStyle(0)
        oneSigma.SetFillColor(ROOT.kGreen+1)
        oneSigma.SetLineColor(ROOT.kGreen+1)
        oneSigma.SetMarkerStyle(0)
        expected.SetLineStyle(5)
        expected.SetLineColor(ROOT.kAzure)
        expected.SetMarkerStyle(0)
        expected.SetFillStyle(0)
        observed.SetMarkerStyle(0)
        observed.SetFillStyle(0)

        if detailed:
            return expected, oneSigma, twoSigma, observed, oneSigma_low, oneSigma_high, twoSigma_low, twoSigma_high
        return expected, oneSigma, twoSigma, observed

    def plotLimit(self,xvals,quartiles,savename,**kwargs):
        '''Plot limits'''
        xaxis = kwargs.pop('xaxis','x')
        yaxis = kwargs.pop('yaxis','95% CL upper limit on #sigma/#sigma_{model}')
        legendtitle = kwargs.pop('legendtitle','95% CL upper limits')
        blind = kwargs.pop('blind',True)
        lumipos = kwargs.pop('lumipos',11)
        isprelim = kwargs.pop('isprelim',True)
        legendpos = kwargs.pop('legendpos',31)
        numcol = kwargs.pop('numcol',1)
        smooth = kwargs.pop('smooth',False)
        ymin = kwargs.pop('ymin',None)
        ymax = kwargs.pop('ymax',None)
        logy = kwargs.pop('logy',1)
        plotunity = kwargs.pop('plotunity',True)
        leftmargin = kwargs.pop('leftmargin',None)
        model = kwargs.pop('model',None)
        xVar = kwargs.pop('x',None)
        overlay = kwargs.pop('overlay',None)
        overlayLabels = kwargs.pop('overlayLabels',None)
        additionaltext = kwargs.pop('additionaltext','')

        logging.info('Plotting {0}'.format(savename))

        canvas = ROOT.TCanvas(savename,savename,50,50,600,600)
        canvas.SetLogy(logy)
        if leftmargin: canvas.SetLeftMargin(leftmargin)

        limits = quartiles

        expected, oneSigma, twoSigma, observed = self._getGraphs(xvals,limits,xVar=xVar,smooth=smooth,model=model)

        expected.GetXaxis().SetLimits(xvals[0],xvals[-1])
        expected.GetXaxis().SetTitle(xaxis)
        expected.GetYaxis().SetTitle(yaxis)
        expected.GetYaxis().SetTitleSize(0.05)
        expected.GetYaxis().SetTitleOffset(1.6)

        expected.Draw()
        if ymin is not None: expected.SetMinimum(ymin)
        if ymax is not None: expected.SetMaximum(ymax)
        twoSigma.Draw('f')
        oneSigma.Draw('f')

        expected.Draw('same')
        ROOT.gPad.RedrawAxis()

        colors = [ROOT.kRed, ROOT.kBlue-4, ROOT.kMagenta+1, ROOT.kAzure, ROOT.kOrange+7]
        if overlay:
            c = 0
            for graph in overlay:
                graph.SetLineColor(colors[c])
                graph.SetLineWidth(2)
                graph.Draw('same')
                c += 1
                if c >= len(colors): c = 0

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
        legend = self._getLegend(entries=entries,numcol=numcol,position=legendpos,title=legendtitle)
        legend.Draw()


        if overlayLabels:
            entries = []
            for g,l in zip(overlay,overlayLabels):
                entries += [[g,l,'l']]
            legendOverlay = self._getLegend(entries=entries,numcol=1,position=32)
            legendOverlay.Draw()

        if additionaltext:
            nlines = 1 if isinstance(additionaltext,str) else len(additionaltext)
            text = ROOT.TPaveText(0.20,0.90-nlines*0.04,0.45,0.92,'NB NDC')
            text.SetTextFont(42)
            text.SetBorderSize(0)
            text.SetFillColor(0)
            text.SetTextAlign(11)
            if isinstance(additionaltext,list):
                for addt in additionaltext:
                    text.AddText(addt)
            else:
                text.AddText(additionaltext)
            text.Draw()

        # cms lumi styling
        self._setStyle(canvas,position=lumipos,preliminary=isprelim)

        self._save(canvas,savename)

    def plotLimit2DProjection(self,xvals,yval,quartiles,scales,savename,**kwargs):
        '''Plot limits'''
        xaxis = kwargs.pop('xaxis','x')
        yaxis = kwargs.pop('yaxis','95% CL upper limit on #sigma/#sigma_{model}')
        legendtitle = kwargs.pop('legendtitle','95% CL upper limits')
        blind = kwargs.pop('blind',True)
        lumipos = kwargs.pop('lumipos',0)
        isprelim = kwargs.pop('isprelim',True)
        legendpos = kwargs.pop('legendpos',31)
        numcol = kwargs.pop('numcol',1)
        asymptoticFilenames = kwargs.pop('asymptoticFilenames',[])
        smooth = kwargs.pop('smooth',False)
        logy = kwargs.pop('logy',1)
        model = kwargs.pop('model',None)
        modelkey = kwargs.pop('modelkey',None)
        xVar = kwargs.pop('x',None)
        ymin = kwargs.pop('ymin',1e-2)
        ymax = kwargs.pop('ymax',10)
        expectedBands = kwargs.pop('expectedBands', [])
        additionaltext = kwargs.pop('additionaltext','')

        logging.info('Plotting {0}'.format(savename))

        #ROOT.gStyle.SetPalette(ROOT.kBird)
        #ROOT.gStyle.SetPalette(ROOT.kDeepSea)
        ROOT.gStyle.SetPalette(nb)

        canvas = ROOT.TCanvas(savename,savename,50,50,600,600)
        canvas.SetLogy(logy)
        canvas.SetLeftMargin(0.18)

        xmin = xvals[0]
        xmax = xvals[-1]
        dx = xvals[1]-xvals[0]
        nx = int(float(xmax-xmin)/dx)
        observedHist     = ROOT.TH1D('obs', 'obs', nx+1,xmin-0.5*dx,xmax+0.5*dx)
        expectedHist     = ROOT.TH1D('exp', 'exp', nx+1,xmin-0.5*dx,xmax+0.5*dx)
        emptyHist        = ROOT.TH1D('emp', 'emp',    1,xmin-0.5*dx,xmax+0.5*dx)
        oneSigmaLowHist  = ROOT.TH1D('onel','onel',nx+1,xmin-0.5*dx,xmax+0.5*dx)
        oneSigmaHighHist = ROOT.TH1D('oneh','oneh',nx+1,xmin-0.5*dx,xmax+0.5*dx)
        twoSigmaLowHist  = ROOT.TH1D('twol','twol',nx+1,xmin-0.5*dx,xmax+0.5*dx)
        twoSigmaHighHist = ROOT.TH1D('twoh','twoh',nx+1,xmin-0.5*dx,xmax+0.5*dx)

        limits = quartiles

        expected, oneSigma, twoSigma, observed, oneSigma_low, oneSigma_high, twoSigma_low, twoSigma_high = self._getGraphs(xvals,limits,xVar=xVar,smooth=smooth,model=model,scales=scales,modelkey=modelkey,y=yval,detailed=True)

        def cross(val,prev,curr):
            if prev>=val and curr<=val: return True
            if prev<=val and curr>=val: return True
            return False

        for xi in range(nx+1):
            x = xmin + xi*dx
            val = expected.Eval(x)
            eb = expectedHist.GetBin(xi+1)
            expectedHist.SetBinContent(eb,val)

            oneSigmaLowHist.SetBinContent( eb, oneSigma_low.Eval(x))
            oneSigmaHighHist.SetBinContent(eb, oneSigma_high.Eval(x))
            twoSigmaLowHist.SetBinContent( eb, twoSigma_low.Eval(x))
            twoSigmaHighHist.SetBinContent(eb, twoSigma_high.Eval(x))

            oval = observed.Eval(x)
            observedHist.SetBinContent(eb, oval)


        expectedHistCont = expectedHist.Clone()
        observedHistCont = observedHist.Clone()


        def setHistStyle(hist):
            hist.GetXaxis().SetTitle(xaxis)
            hist.GetYaxis().SetTitle(yaxis)
            hist.GetYaxis().SetTitleSize(0.05)
            hist.GetYaxis().SetTitleOffset(1.2)

        setHistStyle(expectedHist)
        setHistStyle(observedHist)
        setHistStyle(emptyHist)

        expected.SetLineStyle(2)
        expected.SetLineWidth(2)
        expected.Draw('AC')
        expected.GetXaxis().SetTitle(xaxis)
        expected.GetXaxis().SetRangeUser(xmin,xmax)
        expected.GetYaxis().SetTitle(yaxis)
        expected.GetYaxis().SetRangeUser(ymin,ymax)
        if not blind:
            observed.SetLineStyle(1)
            observed.SetLineWidth(2)
            observed.Draw('C')

        #colors = [ROOT.kBlack, ROOT.kRed+2, ROOT.kRed]
        colors = [ROOT.kRed+1, ROOT.kGreen+2]

        lines = []
        for i,eb in enumerate(expectedBands):
            c = colors[i]
            line = ROOT.TGraph(2,array('d',[xmin,xmax]),array('d',[eb,eb]))
            line.SetLineStyle(2)
            line.SetLineWidth(2)
            line.SetLineColor(c)
            line.SetMarkerStyle(0)
            line.SetFillStyle(0)
            line.Draw('c')
            lines += [line]

        # special legend
        entries = [[expected, 'Expected Exclusion','l']]
        if not blind:
            entries += [[observed, 'Observed Exclusion','l']]
        entries += [[lines[i],'B(H #rightarrow aa) = {}'.format(eb),'l'] for i,eb in enumerate(expectedBands)]
        #legend = self._getLegend(entries=entries,numcol=1,position=24,title=legendtitle)
        legend = self._getLegend(entries=entries,numcol=1,position=[0.52,0.15,0.96,0.45],title=legendtitle)
        legend.Draw()

        if additionaltext:
            nlines = 1 if isinstance(additionaltext,str) else len(additionaltext)
            text = ROOT.TPaveText(0.20,0.90-nlines*0.04,0.45,0.92,'NB NDC')
            text.SetTextFont(42)
            text.SetBorderSize(0)
            text.SetFillColor(0)
            text.SetTextAlign(11)
            if isinstance(additionaltext,list):
                for addt in additionaltext:
                    text.AddText(addt)
            else:
                text.AddText(additionaltext)
            text.Draw()

        # manually add the 1 sigma bands
        leg_one_low  = ROOT.TGraph(2,array('d',[11.72,12.91]),array('d',[8.84,8.84]))
        leg_one_high = ROOT.TGraph(2,array('d',[11.72,12.91]),array('d',[8.69,8.69]))
        leg_two_low  = ROOT.TGraph(2,array('d',[11.72,12.91]),array('d',[8.91,8.91]))
        leg_two_high = ROOT.TGraph(2,array('d',[11.72,12.91]),array('d',[8.62,8.62]))

        leg_one_low.SetLineStyle(2)
        leg_one_low.SetLineWidth(2)
        #leg_one_low.Draw('same')
        leg_one_high.SetLineStyle(2)
        leg_one_high.SetLineWidth(2)
        #leg_one_high.Draw('same')
        leg_two_low.SetLineStyle(6)
        leg_two_low.SetLineWidth(2)
        #leg_two_low.Draw('same')
        leg_two_high.SetLineStyle(6)
        leg_two_high.SetLineWidth(2)
        #leg_two_high.Draw('same')

        # cms lumi styling
        self._setStyle(canvas,position=lumipos,preliminary=isprelim)

        self._save(canvas,savename)

        xSave = [3.6,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21]
        ySave = [yval]

        save = []
        for x in xSave:
            for y in ySave:
                be = expectedHist.FindBin(x)
                ve = expectedHist.GetBinContent(be)
                vel = oneSigmaLowHist.GetBinContent(be)
                veh = oneSigmaHighHist.GetBinContent(be)
                save += [(x,y,ve,vel,veh)]

        self._saveCSV(save,savename)
                

    def plotLimit2DProjectionMulti(self,xvalsMulti,yval,quartilesMulti,scalesMulti,savename,**kwargs):
        '''Plot limits'''
        xaxis = kwargs.pop('xaxis','x')
        yaxis = kwargs.pop('yaxis','95% CL upper limit on #sigma/#sigma_{model}')
        legendtitle = kwargs.pop('legendtitle','95% CL upper limits')
        blind = kwargs.pop('blind',True)
        lumipos = kwargs.pop('lumipos',0)
        isprelim = kwargs.pop('isprelim',True)
        legendpos = kwargs.pop('legendpos',31)
        numcol = kwargs.pop('numcol',1)
        asymptoticFilenames = kwargs.pop('asymptoticFilenames',[])
        smooth = kwargs.pop('smooth',False)
        logy = kwargs.pop('logy',1)
        model = kwargs.pop('model',None)
        modelkey = kwargs.pop('modelkey',None)
        xVar = kwargs.pop('x',None)
        ymin = kwargs.pop('ymin',1e-2)
        ymax = kwargs.pop('ymax',10)
        expectedBands = kwargs.pop('expectedBands', [])
        additionaltext = kwargs.pop('additionaltext','')

        logging.info('Plotting {0}'.format(savename))

        #ROOT.gStyle.SetPalette(ROOT.kBird)
        #ROOT.gStyle.SetPalette(ROOT.kDeepSea)
        ROOT.gStyle.SetPalette(nb)

        canvas = ROOT.TCanvas(savename,savename,50,50,600,600)
        canvas.SetLogy(logy)
        canvas.SetLeftMargin(0.18)

        xmin = xvalsMulti[0][0]
        xmax = xvalsMulti[-1][-1]
        dx = xvalsMulti[0][1]-xvalsMulti[0][0]
        nx = int(float(xmax-xmin)/dx)
        observedHist     = ROOT.TH1D('obs', 'obs', nx+1,xmin-0.5*dx,xmax+0.5*dx)
        expectedHist     = ROOT.TH1D('exp', 'exp', nx+1,xmin-0.5*dx,xmax+0.5*dx)
        emptyHist        = ROOT.TH1D('emp', 'emp',    1,xmin-0.5*dx,xmax+0.5*dx)
        oneSigmaLowHist  = ROOT.TH1D('onel','onel',nx+1,xmin-0.5*dx,xmax+0.5*dx)
        oneSigmaHighHist = ROOT.TH1D('oneh','oneh',nx+1,xmin-0.5*dx,xmax+0.5*dx)
        twoSigmaLowHist  = ROOT.TH1D('twol','twol',nx+1,xmin-0.5*dx,xmax+0.5*dx)
        twoSigmaHighHist = ROOT.TH1D('twoh','twoh',nx+1,xmin-0.5*dx,xmax+0.5*dx)

        expected = {}
        oneSigma = {}
        twoSigma = {}
        observed = {}
        oneSigma_low = {}
        oneSigma_high = {}
        twoSigma_low = {}
        twoSigma_high = {}

        for ilim, (xvals, quartiles,scales) in enumerate(zip(xvalsMulti, quartilesMulti,scalesMulti)):
            limits = quartiles

            expected[ilim], oneSigma[ilim], twoSigma[ilim], observed[ilim], oneSigma_low[ilim], oneSigma_high[ilim], twoSigma_low[ilim], twoSigma_high[ilim] = self._getGraphs(xvals,limits,xVar=xVar,smooth=smooth,model=model,scales=scales,modelkey=modelkey,y=yval,detailed=True)

        def cross(val,prev,curr):
            if prev>=val and curr<=val: return True
            if prev<=val and curr>=val: return True
            return False

        for xi in range(nx+1):
            x = xmin + xi*dx
            for ilim, xvals in enumerate(xvalsMulti):
                if x>=xvals[0] and x<=xvals[-1]: break
            val = expected[ilim].Eval(x)
            eb = expectedHist.GetBin(xi+1)
            expectedHist.SetBinContent(eb,val)

            oneSigmaLowHist.SetBinContent( eb, oneSigma_low[ilim].Eval(x))
            oneSigmaHighHist.SetBinContent(eb, oneSigma_high[ilim].Eval(x))
            twoSigmaLowHist.SetBinContent( eb, twoSigma_low[ilim].Eval(x))
            twoSigmaHighHist.SetBinContent(eb, twoSigma_high[ilim].Eval(x))

            oval = observed[ilim].Eval(x)
            observedHist.SetBinContent(eb, oval)


        expectedHistCont = expectedHist.Clone()
        observedHistCont = observedHist.Clone()


        def setHistStyle(hist):
            hist.GetXaxis().SetTitle(xaxis)
            hist.GetYaxis().SetTitle(yaxis)
            hist.GetYaxis().SetTitleSize(0.05)
            hist.GetYaxis().SetTitleOffset(1.2)

        setHistStyle(expectedHist)
        setHistStyle(observedHist)
        setHistStyle(emptyHist)

        for ilim in range(len(xvalsMulti)):
            expected[ilim].SetLineStyle(2)
            expected[ilim].SetLineWidth(2)
            if ilim==0:
                expected[ilim].GetXaxis().SetLimits(xmin,xmax)
                expected[ilim].Draw('AC')
                expected[ilim].GetXaxis().SetTitle(xaxis)
                expected[ilim].GetXaxis().SetRangeUser(xmin,xmax)
                expected[ilim].GetYaxis().SetTitle(yaxis)
                expected[ilim].GetYaxis().SetRangeUser(ymin,ymax)
            else:
                expected[ilim].Draw('C')
            if not blind:
                observed[ilim].SetLineStyle(1)
                observed[ilim].SetLineWidth(2)
                observed[ilim].Draw('C')

        #colors = [ROOT.kBlack, ROOT.kRed+2, ROOT.kRed]
        colors = [ROOT.kRed+1, ROOT.kGreen+2]

        lines = []
        for i,eb in enumerate(expectedBands):
            c = colors[i]
            line = ROOT.TGraph(2,array('d',[xmin,xmax]),array('d',[eb,eb]))
            line.SetLineStyle(2)
            line.SetLineWidth(2)
            line.SetLineColor(c)
            line.SetMarkerStyle(0)
            line.SetFillStyle(0)
            line.Draw('c')
            lines += [line]

        # special legend
        entries = [[expected[0], 'Expected Exclusion','l']]
        if not blind:
            entries += [[observed[0], 'Observed Exclusion','l']]
        entries += [[lines[i],'B(H #rightarrow aa) = {}'.format(eb),'l'] for i,eb in enumerate(expectedBands)]
        #legend = self._getLegend(entries=entries,numcol=1,position=24,title=legendtitle)
        legend = self._getLegend(entries=entries,numcol=1,position=[0.52,0.15,0.96,0.45],title=legendtitle)
        legend.Draw()

        if additionaltext:
            nlines = 1 if isinstance(additionaltext,str) else len(additionaltext)
            text = ROOT.TPaveText(0.20,0.90-nlines*0.04,0.45,0.92,'NB NDC')
            text.SetTextFont(42)
            text.SetBorderSize(0)
            text.SetFillColor(0)
            text.SetTextAlign(11)
            if isinstance(additionaltext,list):
                for addt in additionaltext:
                    text.AddText(addt)
            else:
                text.AddText(additionaltext)
            text.Draw()


        # manually add the 1 sigma bands
        leg_one_low  = ROOT.TGraph(2,array('d',[11.72,12.91]),array('d',[8.84,8.84]))
        leg_one_high = ROOT.TGraph(2,array('d',[11.72,12.91]),array('d',[8.69,8.69]))
        leg_two_low  = ROOT.TGraph(2,array('d',[11.72,12.91]),array('d',[8.91,8.91]))
        leg_two_high = ROOT.TGraph(2,array('d',[11.72,12.91]),array('d',[8.62,8.62]))

        leg_one_low.SetLineStyle(2)
        leg_one_low.SetLineWidth(2)
        #leg_one_low.Draw('same')
        leg_one_high.SetLineStyle(2)
        leg_one_high.SetLineWidth(2)
        #leg_one_high.Draw('same')
        leg_two_low.SetLineStyle(6)
        leg_two_low.SetLineWidth(2)
        #leg_two_low.Draw('same')
        leg_two_high.SetLineStyle(6)
        leg_two_high.SetLineWidth(2)
        #leg_two_high.Draw('same')


        # cms lumi styling
        self._setStyle(canvas,position=lumipos,preliminary=isprelim)

        self._save(canvas,savename)

        xSave = [3.6,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21]
        ySave = [yval]

        save = []
        for x in xSave:
            for y in ySave:
                be = expectedHist.FindBin(x)
                ve = expectedHist.GetBinContent(be)
                vel = oneSigmaLowHist.GetBinContent(be)
                veh = oneSigmaHighHist.GetBinContent(be)
                save += [(x,y,ve,vel,veh)]

        self._saveCSV(save,savename)
                


    def plotLimitMulti(self,xvalsMulti,quartilesMulti,savename,**kwargs):
        '''Plot limits
        
        Structure should be:
            xvals: [[x00, x01, ...], [x10, x11, ...], ...]
            quartiles: similarly but with [xij] replaced by {xij: [-2s, -1s, exp, +1s, +2s, obs]}

        Each set will correspond to a limit.
        '''
        xaxis = kwargs.pop('xaxis','x')
        yaxis = kwargs.pop('yaxis','95% CL upper limit on #sigma/#sigma_{model}')
        legendtitle = kwargs.pop('legendtitle','95% CL upper limits')
        drawlines = kwargs.pop('drawlines',True)
        blind = kwargs.pop('blind',True)
        lumipos = kwargs.pop('lumipos',11)
        isprelim = kwargs.pop('isprelim',True)
        legendpos = kwargs.pop('legendpos',31)
        numcol = kwargs.pop('numcol',1)
        smooth = kwargs.pop('smooth',False)
        ymin = kwargs.pop('ymin',None)
        ymax = kwargs.pop('ymax',None)
        logy = kwargs.pop('logy',1)
        plotunity = kwargs.pop('plotunity',True)
        leftmargin = kwargs.pop('leftmargin',None)
        model = kwargs.pop('model',None)
        xVar = kwargs.pop('x',None)
        overlay = kwargs.pop('overlay',None)
        overlayLabels = kwargs.pop('overlayLabels',None)
        additionaltext = kwargs.pop('additionaltext','')

        logging.info('Plotting {0}'.format(savename))

        canvas = ROOT.TCanvas(savename,savename,50,50,600,600)
        canvas.SetLogy(logy)
        if leftmargin: canvas.SetLeftMargin(leftmargin)

        twoSigma = {}
        oneSigma = {}
        expected = {}
        observed = {}

        lines = {}
        ratiounity = {}

        for ilim, (xvals, quartiles) in enumerate(zip(xvalsMulti, quartilesMulti)):

            limits = quartiles
            expected[ilim], oneSigma[ilim], twoSigma[ilim], observed[ilim] = self._getGraphs(xvals,limits,xVar=xVar,smooth=smooth,model=model)

            if ilim==0:
                expected[ilim].GetXaxis().SetLimits(xvalsMulti[0][0],xvalsMulti[-1][-1])
                expected[ilim].GetXaxis().SetTitle(xaxis)
                expected[ilim].GetYaxis().SetTitle(yaxis)
                expected[ilim].GetYaxis().SetTitleSize(0.05)
                expected[ilim].GetYaxis().SetTitleOffset(1.6)
                expected[ilim].Draw()

                if ymin is not None: expected[ilim].SetMinimum(ymin)
                if ymax is not None: expected[ilim].SetMaximum(ymax)
            twoSigma[ilim].Draw('f')
            oneSigma[ilim].Draw('f')

            expected[ilim].Draw('same')
            ROOT.gPad.RedrawAxis()

            colors = [ROOT.kRed, ROOT.kBlue-4, ROOT.kMagenta+1, ROOT.kAzure, ROOT.kOrange+7]
            if overlay:
                c = 0
                for graph in overlay:
                    graph.SetLineColor(colors[c])
                    graph.SetLineWidth(2)
                    graph.Draw('same')
                    c += 1
                    if c >= len(colors): c = 0

            if not blind: observed[ilim].Draw('same')

            ratiounity[ilim] = ROOT.TLine(expected[ilim].GetXaxis().GetXmin(),1,expected[ilim].GetXaxis().GetXmax(),1)
            if plotunity: ratiounity[ilim].Draw()

            if drawlines and ilim:
                lines[ilim] = ROOT.TLine(xvals[0],expected[0].GetMinimum(),xvals[0],expected[0].GetMaximum())
                lines[ilim].SetLineStyle(2)
                lines[ilim].Draw()

        # get the legend
        entries = [
            [expected[0],'Median expected','l'],
            [oneSigma[0],'68% expected','F'],
            [twoSigma[0],'95% expected','F'],
        ]
        if not blind: entries = [[observed[0],'Observed','l']] + entries
        legend = self._getLegend(entries=entries,numcol=numcol,position=legendpos,title=legendtitle)
        legend.Draw()


        if overlayLabels:
            entries = []
            for g,l in zip(overlay,overlayLabels):
                entries += [[g,l,'l']]
            legendOverlay = self._getLegend(entries=entries,numcol=1,position=32)
            legendOverlay.Draw()

        if additionaltext:
            nlines = 1 if isinstance(additionaltext,str) else len(additionaltext)
            text = ROOT.TPaveText(0.20,0.90-nlines*0.04,0.45,0.92,'NB NDC')
            text.SetTextFont(42)
            text.SetBorderSize(0)
            text.SetFillColor(0)
            text.SetTextAlign(11)
            if isinstance(additionaltext,list):
                for addt in additionaltext:
                    text.AddText(addt)
            else:
                text.AddText(additionaltext)
            text.Draw()

        ## HACK
        ## plot 750 GeV FullCLs over
        #fullcls = {}
        #fullcls[750] = {}
        #fullcls[750][4.5] = [ 3.537,3.931,5.088,8.369,17.679,10.839]
        #fullcls[750][5.0] = [ 2.999,3.611,4.535,7.422,15.703,15.249]
        #fullcls[750][5.5] = [ 3.366,3.542,4.180,6.882,14.947,15.782]
        #fullcls[750][6.0] = [ 2.697,3.034,3.915,6.491,14.452,14.306]
        #fullcls[750][6.5] = [ 2.413,2.883,3.834,6.352,14.150,10.091]

        #if '750_br_smooth' in savename:
        #    fcls_as = [4.5,5.0,5.5,6.0,6.5]
        #    fcls_two_low  = ROOT.TGraph(len(fcls_as), array('d',fcls_as), array('d',[fullcls[750][a][0]*1e-3 for a in fcls_as]))
        #    fcls_one_low  = ROOT.TGraph(len(fcls_as), array('d',fcls_as), array('d',[fullcls[750][a][1]*1e-3 for a in fcls_as]))
        #    fcls_exp      = ROOT.TGraph(len(fcls_as), array('d',fcls_as), array('d',[fullcls[750][a][2]*1e-3 for a in fcls_as]))
        #    fcls_one_high = ROOT.TGraph(len(fcls_as), array('d',fcls_as), array('d',[fullcls[750][a][3]*1e-3 for a in fcls_as]))
        #    fcls_two_high = ROOT.TGraph(len(fcls_as), array('d',fcls_as), array('d',[fullcls[750][a][4]*1e-3 for a in fcls_as]))
        #    fcls_obs      = ROOT.TGraph(len(fcls_as), array('d',fcls_as), array('d',[fullcls[750][a][5]*1e-3 for a in fcls_as]))
        #    gs = [fcls_two_low,fcls_one_low,fcls_exp,fcls_one_high,fcls_two_high,fcls_obs]
        #    cs = [ROOT.kOrange+1,ROOT.kGreen+3,ROOT.kBlue,ROOT.kGreen+3,ROOT.kOrange+1,ROOT.kBlack]
        #    for g,c in zip(gs,cs):
        #        g.SetLineWidth(2)
        #        g.SetLineColor(c)
        #        g.SetMarkerColor(c)
        #    mg = ROOT.TMultiGraph()
        #    mg.Add(fcls_two_low)
        #    mg.Add(fcls_one_low)
        #    mg.Add(fcls_exp)
        #    mg.Add(fcls_one_high)
        #    mg.Add(fcls_two_high)
        #    mg.Add(fcls_obs)
        #    mg.Draw('lp')

        # cms lumi styling
        self._setStyle(canvas,position=lumipos,preliminary=isprelim)

        self._save(canvas,savename)

    def plotLimit2D(self,xvals,yvals,quartiles,scales,savename,**kwargs):
        '''Plot limits'''
        xaxis = kwargs.pop('xaxis','x')
        yaxis = kwargs.pop('yaxis','y')
        zaxis = kwargs.pop('zaxis','95% CL upper limit on #sigma/#sigma_{model}')
        legendtitle = kwargs.pop('legendtitle','95% CL upper limits')
        blind = kwargs.pop('blind',True)
        lumipos = kwargs.pop('lumipos',0)
        isprelim = kwargs.pop('isprelim',True)
        legendpos = kwargs.pop('legendpos',31)
        numcol = kwargs.pop('numcol',1)
        smooth = kwargs.pop('smooth',False)
        logz = kwargs.pop('logz',1)
        logy = kwargs.pop('logy',0)
        plotunity = kwargs.pop('plotunity',True)
        model = kwargs.pop('model',None)
        modelkey = kwargs.pop('modelkey',None)
        xVar = kwargs.pop('x',None)
        expectedBands = kwargs.pop('expectedBands', [])
        zmin = kwargs.pop('zmin',1e-2)
        zmax = kwargs.pop('zmax',10)
        plotcolz = kwargs.pop('plotcolz',True)
        plotfill = kwargs.pop('plotfill',False)
        additionaltext = kwargs.pop('additionaltext','')

        logging.info('Plotting {0}'.format(savename))

        #ROOT.gStyle.SetPalette(ROOT.kBird)
        #ROOT.gStyle.SetPalette(ROOT.kDeepSea)
        ROOT.gStyle.SetPalette(nb)

        canvas = ROOT.TCanvas(savename,savename,50,50,600,600)
        canvas.SetLogz(logz)
        canvas.SetLogy(logy)
        canvas.SetLeftMargin(0.14)
        if plotcolz: canvas.SetRightMargin(0.22)

        xmin = xvals[0]
        xmax = xvals[-1]
        dx = xvals[1]-xvals[0]
        nx = int(float(xmax-xmin)/dx)
        ymin = yvals[0]
        ymax = yvals[-1]
        dy = yvals[1]-yvals[0]
        ny = int(float(ymax-ymin)/dy)
        observedHist     = ROOT.TH2D('obs', 'obs', nx+1,xmin-0.5*dx,xmax+0.5*dx,ny+1,ymin-0.5*dy,ymax+0.5*dy)
        expectedHist     = ROOT.TH2D('exp', 'exp', nx+1,xmin-0.5*dx,xmax+0.5*dx,ny+1,ymin-0.5*dy,ymax+0.5*dy)
        emptyHist        = ROOT.TH2D('emp', 'emp',    1,xmin-0.5*dx,xmax+0.5*dx,   1,ymin-0.5*dy,ymax+0.5*dy)
        oneSigmaLowHist  = ROOT.TH2D('onel','onel',nx+1,xmin-0.5*dx,xmax+0.5*dx,ny+1,ymin-0.5*dy,ymax+0.5*dy)
        oneSigmaHighHist = ROOT.TH2D('oneh','oneh',nx+1,xmin-0.5*dx,xmax+0.5*dx,ny+1,ymin-0.5*dy,ymax+0.5*dy)
        twoSigmaLowHist  = ROOT.TH2D('twol','twol',nx+1,xmin-0.5*dx,xmax+0.5*dx,ny+1,ymin-0.5*dy,ymax+0.5*dy)
        twoSigmaHighHist = ROOT.TH2D('twoh','twoh',nx+1,xmin-0.5*dx,xmax+0.5*dx,ny+1,ymin-0.5*dy,ymax+0.5*dy)

        limits = quartiles


        expected_vals = []
        oneSigma_low_vals = []
        oneSigma_high_vals = []
        twoSigma_low_vals = []
        twoSigma_high_vals = []


        for yi in range(ny+1):
            y = ymin + yi*dy
            expected, oneSigma, twoSigma, observed, oneSigma_low, oneSigma_high, twoSigma_low, twoSigma_high = self._getGraphs(xvals,limits,xVar=xVar,smooth=smooth,model=model,scales=scales,modelkey=modelkey,y=y,detailed=True)


            def cross(val,prev,curr):
                if prev>=val and curr<=val: return True
                if prev<=val and curr>=val: return True
                return False

            #expected_prev = 0
            #oneSigma_low_prev = 0
            #oneSigma_high_prev = 0
            #twoSigma_low_prev = 0
            #twoSigma_high_prev = 0
            for xi in range(nx+1):
                x = xmin + xi*dx
                val = expected.Eval(x)
                if val<zmin: val = zmin
                eb = expectedHist.GetBin(xi+1,yi+1)
                #eb = expectedHist.FindBin(x,y)
                expectedHist.SetBinContent(eb,val)

                oneSigmaLowHist.SetBinContent( eb, oneSigma_low.Eval(x))
                oneSigmaHighHist.SetBinContent(eb, oneSigma_high.Eval(x))
                twoSigmaLowHist.SetBinContent( eb, twoSigma_low.Eval(x))
                twoSigmaHighHist.SetBinContent(eb, twoSigma_high.Eval(x))

                oval = observed.Eval(x)
                # TODO: try
                if oval<zmin: oval = 0
                if oval>zmax: oval = 999*zmax
                observedHist.SetBinContent(eb, oval)

                #expected_curr      = expected.Eval(x)
                #oneSigma_low_curr  = oneSigma_low.Eval(x)
                #oneSigma_high_curr = oneSigma_high.Eval(x)
                #twoSigma_low_curr  = twoSigma_low.Eval(x)
                #twoSigma_high_curr = twoSigma_high.Eval(x)

                #if xi:
                #    if cross(1,expected_prev,     expected_curr)     : expected_vals      += [(x,y)]
                #    if cross(1,oneSigma_low_prev, oneSigma_low_curr) : oneSigma_low_vals  += [(x,y)]
                #    if cross(1,oneSigma_high_prev,oneSigma_high_curr): oneSigma_high_vals += [(x,y)]
                #    if cross(1,twoSigma_low_prev, twoSigma_low_curr) : twoSigma_low_vals  += [(x,y)]
                #    if cross(1,twoSigma_high_prev,twoSigma_high_curr): twoSigma_high_vals += [(x,y)]

                #expected_prev      = expected_curr
                #oneSigma_low_prev  = oneSigma_low_curr
                #oneSigma_high_prev = oneSigma_high_curr
                #twoSigma_low_prev  = twoSigma_low_curr
                #twoSigma_high_prev = twoSigma_high_curr

        expectedHistCont = expectedHist.Clone()
        observedHistCont = observedHist.Clone()


        def setHistStyle(hist):
            hist.GetXaxis().SetTitle(xaxis)
            hist.GetYaxis().SetTitle(yaxis)
            hist.GetZaxis().SetTitle(zaxis)
            hist.GetYaxis().SetTitleSize(0.05)
            hist.GetYaxis().SetTitleOffset(1.2)
            hist.GetZaxis().SetTitleSize(0.05)
            hist.GetZaxis().SetTitleOffset(1.5)
            hist.GetZaxis().SetRangeUser(zmin,zmax)

        setHistStyle(expectedHist)
        setHistStyle(observedHist)
        setHistStyle(emptyHist)

        def get_contours(hist,val=1.0):
            contours = array('d',[val])
            hist.SetContour(1,contours)
            hist.Draw('cont z list')
            canvas.Update()
            graphs = []
            conts = ROOT.gROOT.GetListOfSpecials().FindObject('contours')
            i = 0 # why is this needed?!?!?
            if i in range(conts.GetSize()):
                contLevel = conts.At(i)
                for j in range(contLevel.GetSize()):
                    graphs += [contLevel.At(j).Clone()]
                    
            return graphs

        expected_graphs = {}
        oneSigma_graphs = {}
        twoSigma_graphs = {}
        observed_graphs = {}
        for eb in expectedBands:
            expected_graphs[eb] =  get_contours(expectedHistCont,eb)
            observed_graphs[eb] =  get_contours(observedHistCont,eb)
            oneSigma_graphs[eb] =  get_contours(oneSigmaLowHist, eb)
            oneSigma_graphs[eb] += get_contours(oneSigmaHighHist,eb)
            twoSigma_graphs[eb] =  get_contours(twoSigmaLowHist, eb)
            twoSigma_graphs[eb] += get_contours(twoSigmaHighHist,eb)

        #print len(expected_graphs), len(oneSigma_graphs), len(twoSigma_graphs)

        if plotcolz:
            if blind:
                expectedHist.Draw('colz')
            else:
                observedHist.Draw('colz')
        else:
            emptyHist.Draw()

        #colors = [ROOT.kBlack, ROOT.kRed+2, ROOT.kRed]
        colors = [ROOT.kRed+1, ROOT.kGreen+2]

        mg = ROOT.TMultiGraph()
        if plotfill:
            # not working
            #if not blind:
            #    contours = array('d',expectedBands)
            #    colpalette = [colors[i] for i in range(len(expectedBands))]
            #    ROOT.gStyle.SetPalette(len(colpalette), array('i',colpalette))
            #    observedHistCont.SetContour(len(contours),contours)
            #    observedHistCont.Draw('cont0 same')
            # will only work in cases of exclusion on 1 side
            tval = expectedHist.GetBinContent(expectedHist.FindBin(6.0,ymax))
            bval = expectedHist.GetBinContent(expectedHist.FindBin(6.0,ymin))
            lval = expectedHist.GetBinContent(expectedHist.FindBin(xmin,3.0))
            rval = expectedHist.GetBinContent(expectedHist.FindBin(xmax,3.0))
            above = tval<=bval
            left = lval<=rval

            for i,eb in enumerate(expectedBands):
                c = colors[i]
                if not blind:
                    xvals = []
                    yvals = []
                    x = ROOT.Double()
                    y = ROOT.Double()
                    allxvals = []
                    allyvals = []
                    for g in observed_graphs[eb]:
                        thisxvals = []
                        thisyvals = []
                        n = g.GetN()
                        for i in range(n):
                            g.GetPoint(i,x,y)
                            thisxvals += [float(x)]
                            thisyvals += [float(y)]

                        allxvals += [thisxvals]
                        allyvals += [thisyvals]

                    if len(allxvals)==1:
                        if left and allyvals[0][0]<allyvals[0][-1]:
                            xvals = [x for x in reversed(allxvals[0])]
                            yvals = [y for y in reversed(allyvals[0])]
                        else:
                            xvals = allxvals[0]
                            yvals = allyvals[0]
                    elif all([x[0]>x[-1] for x in allxvals]):
                        for thisx, thisy in zip(allxvals,allyvals):
                            xvals = thisx + xvals
                            yvals = thisy + yvals
                    else:
                        for thisx, thisy in zip(allxvals,allyvals):
                            xvals = xvals + thisx
                            yvals = yvals + thisy

                    fx = xvals[0]
                    lx = xvals[-1]
                    fy = yvals[0]
                    ly = yvals[-1]
                    mx = xmin+float(xmax-xmin)/2
                    my = ymin+float(ymax-ymin)/2
                    ty = ymax+1 if above else ymin-1
                    if fx<lx:
                        if fy<ymax-1: # bottom
                            startx = [xmin-1, xmin-1]
                            starty = [ty, fy]
                        else: # top
                            startx = [xmin-1, fx]
                            starty = [ty, ty]
                        if ly<ymax-1: # bottom
                            endx = [xmax+1, xmax+1]
                            endy = [ly, ty]
                        else: # top
                            endx = [lx, xmax+1]
                            endy = [ty, ty]
                    else:
                        # order reversed
                        if fy<ymax-1: # bottom
                            startx = [xmax+1, xmax+1]
                            starty = [ty, fy]
                        else: # top
                            startx = [fx, xmax+1]
                            starty = [ty, ty]
                        if ly<ymax-1: # bottom
                            endx = [xmin-1, xmin-1]
                            endy = [ly, ty]
                        else: # top
                            endx = [lx, xmin-1]
                            endy = [ty, ty]
                    xvals = startx + xvals + endx
                    yvals = starty + yvals + endy
                    #print eb, xvals[:3], xvals[-3:], yvals[:3], yvals[-3:]
                    #print xvals
                    #print yvals

                    g = ROOT.TGraph(len(xvals),array('d',xvals),array('d',yvals))
                    g.SetLineStyle(1)
                    g.SetLineWidth(2)
                    g.SetLineColor(c)
                    g.SetFillColor(c)
                    g.SetFillColorAlpha(c,0.4)
                    g.SetMarkerStyle(0)
                    g.SetFillStyle(1)
                    g.Draw('f')
                    mg.Add(g)
        for i,eb in enumerate(expectedBands):
            c = colors[i]
            if not blind:
                for g in observed_graphs[eb]:
                    g.SetLineStyle(1)
                    g.SetLineWidth(2)
                    g.SetLineColor(c)
                    g.SetMarkerStyle(0)
                    g.SetFillStyle(0)
                    g.Draw('c')
                    mg.Add(g)
        for i,eb in enumerate(expectedBands):
            c = colors[i]
            for g in expected_graphs[eb]:
                g.SetLineStyle(2)
                g.SetLineWidth(2)
                g.SetFillStyle(0)
                g.SetLineColor(c)
                g.SetMarkerStyle(0)
                mg.Add(g)
                g.Draw('c')
            #for g in oneSigma_graphs[eb]:
            #    g.SetLineStyle(2)
            #    g.SetLineWidth(2)
            #    g.SetFillStyle(0)
            #    g.SetLineColor(c)
            #    g.SetMarkerStyle(0)
            #    g.Draw('same')
            #for g in twoSigma_graphs[eb]:
            #    g.SetLineStyle(6)
            #    g.SetLineWidth(2)
            #    g.SetFillStyle(0)
            #    g.SetLineColor(c)
            #    g.SetMarkerStyle(0)
            #    #g.Draw('same')

        #mg.Draw('same')

        # special legend
        if blind:
            entries = [[expected_graphs[eb][0],'#splitline{{Expected exclusion}}{{B(H #rightarrow aa) = {}}}'.format(eb),'l'] for eb in expectedBands if len(expected_graphs[eb])]
        else:
            entries = []
            for eb in expectedBands:
                if len(expected_graphs[eb]): entries += [[expected_graphs[eb][0],'#splitline{{Expected exclusion}}{{B(H #rightarrow aa) = {}}}'.format(eb),'l']]
                if len(observed_graphs[eb]): entries += [[observed_graphs[eb][0],'#splitline{{Observed exclusion}}{{B(H #rightarrow aa) = {}}}'.format(eb),'l']]
        #legend = self._getLegend(entries=entries,numcol=1,position=24,title=legendtitle)
        if plotcolz:
            legend = self._getLegend(entries=entries,numcol=1,position=[0.42,0.59,0.75,0.92],title=legendtitle)
        else:
            legend = self._getLegend(entries=entries,numcol=1,position=[0.52,0.55,0.95,0.92],title=legendtitle)
        legend.Draw()

        if additionaltext:
            nlines = 1 if isinstance(additionaltext,str) else len(additionaltext)
            text = ROOT.TPaveText(0.16,0.90-nlines*0.04,0.38,0.92,'NB NDC')
            text.SetTextFont(42)
            text.SetBorderSize(0)
            text.SetFillColor(0)
            text.SetTextAlign(11)
            if isinstance(additionaltext,list):
                for addt in additionaltext:
                    text.AddText(addt)
            else:
                text.AddText(additionaltext)
            text.Draw()

        # manually add the 1 sigma bands
        leg_one_low  = ROOT.TGraph(2,array('d',[11.72,12.91]),array('d',[8.84,8.84]))
        leg_one_high = ROOT.TGraph(2,array('d',[11.72,12.91]),array('d',[8.69,8.69]))
        leg_two_low  = ROOT.TGraph(2,array('d',[11.72,12.91]),array('d',[8.91,8.91]))
        leg_two_high = ROOT.TGraph(2,array('d',[11.72,12.91]),array('d',[8.62,8.62]))

        leg_one_low.SetLineStyle(2)
        leg_one_low.SetLineWidth(2)
        #leg_one_low.Draw('same')
        leg_one_high.SetLineStyle(2)
        leg_one_high.SetLineWidth(2)
        #leg_one_high.Draw('same')
        leg_two_low.SetLineStyle(6)
        leg_two_low.SetLineWidth(2)
        #leg_two_low.Draw('same')
        leg_two_high.SetLineStyle(6)
        leg_two_high.SetLineWidth(2)
        #leg_two_high.Draw('same')


        # cms lumi styling
        self._setStyle(canvas,position=lumipos,preliminary=isprelim)

        self._save(canvas,savename)

        xSave = [3.6,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21]
        ySave = [1,1.5,2,3,5,10,20,50]

        save = []
        for x in xSave:
            for y in ySave:
                be = expectedHist.FindBin(x,y)
                ve = expectedHist.GetBinContent(be)
                vel = oneSigmaLowHist.GetBinContent(be)
                veh = oneSigmaHighHist.GetBinContent(be)
                save += [(x,y,ve,vel,veh)]

        self._saveCSV(save,savename)
                



    def plotLimit2DMulti(self,xvalsMulti,yvals,quartilesMulti,scalesMulti,savename,**kwargs):
        '''Plot limits'''
        xaxis = kwargs.pop('xaxis','x')
        yaxis = kwargs.pop('yaxis','y')
        zaxis = kwargs.pop('zaxis','95% CL upper limit on #sigma/#sigma_{model}')
        legendtitle = kwargs.pop('legendtitle','95% CL upper limits')
        blind = kwargs.pop('blind',True)
        lumipos = kwargs.pop('lumipos',0)
        isprelim = kwargs.pop('isprelim',True)
        legendpos = kwargs.pop('legendpos',31)
        numcol = kwargs.pop('numcol',1)
        smooth = kwargs.pop('smooth',False)
        logz = kwargs.pop('logz',1)
        logy = kwargs.pop('logy',0)
        plotunity = kwargs.pop('plotunity',True)
        model = kwargs.pop('model',None)
        modelkey = kwargs.pop('modelkey',None)
        xVar = kwargs.pop('x',None)
        expectedBands = kwargs.pop('expectedBands', [])
        zmin = kwargs.pop('zmin',1e-2)
        zmax = kwargs.pop('zmax',10)
        plotcolz = kwargs.pop('plotcolz',True)
        plotfill = kwargs.pop('plotfill',False)
        additionaltext = kwargs.pop('additionaltext','')

        logging.info('Plotting {0}'.format(savename))

        #ROOT.gStyle.SetPalette(ROOT.kBird)
        #ROOT.gStyle.SetPalette(ROOT.kDeepSea)
        ROOT.gStyle.SetPalette(nb)

        canvas = ROOT.TCanvas(savename,savename,50,50,600,600)
        canvas.SetLogz(logz)
        canvas.SetLogy(logy)
        canvas.SetLeftMargin(0.14)
        if plotcolz: canvas.SetRightMargin(0.22)

        xmin = xvalsMulti[0][0]
        xmax = xvalsMulti[-1][-1]
        dx = xvalsMulti[0][1]-xvalsMulti[0][0]
        nx = int(float(xmax-xmin)/dx)
        ymin = yvals[0]
        ymax = yvals[-1]
        dy = yvals[1]-yvals[0]
        ny = int(float(ymax-ymin)/dy)
        observedHist     = ROOT.TH2D('obs', 'obs', nx+1,xmin-0.5*dx,xmax+0.5*dx,ny+1,ymin-0.5*dy,ymax+0.5*dy)
        expectedHist     = ROOT.TH2D('exp', 'exp', nx+1,xmin-0.5*dx,xmax+0.5*dx,ny+1,ymin-0.5*dy,ymax+0.5*dy)
        emptyHist        = ROOT.TH2D('emp', 'emp',    1,xmin-0.5*dx,xmax+0.5*dx,   1,ymin-0.5*dy,ymax+0.5*dy)
        oneSigmaLowHist  = ROOT.TH2D('onel','onel',nx+1,xmin-0.5*dx,xmax+0.5*dx,ny+1,ymin-0.5*dy,ymax+0.5*dy)
        oneSigmaHighHist = ROOT.TH2D('oneh','oneh',nx+1,xmin-0.5*dx,xmax+0.5*dx,ny+1,ymin-0.5*dy,ymax+0.5*dy)
        twoSigmaLowHist  = ROOT.TH2D('twol','twol',nx+1,xmin-0.5*dx,xmax+0.5*dx,ny+1,ymin-0.5*dy,ymax+0.5*dy)
        twoSigmaHighHist = ROOT.TH2D('twoh','twoh',nx+1,xmin-0.5*dx,xmax+0.5*dx,ny+1,ymin-0.5*dy,ymax+0.5*dy)

        expected_vals = []
        oneSigma_low_vals = []
        oneSigma_high_vals = []
        twoSigma_low_vals = []
        twoSigma_high_vals = []

        expected = {}
        oneSigma = {}
        twoSigma = {}
        observed = {}
        oneSigma_low = {}
        oneSigma_high = {}
        twoSigma_low = {}
        twoSigma_high = {}


        for yi in range(ny+1):
            y = ymin + yi*dy

            for ilim, (xvals, quartiles, scales) in enumerate(zip(xvalsMulti, quartilesMulti, scalesMulti)):

                limits = quartiles
                expected[ilim], oneSigma[ilim], twoSigma[ilim], observed[ilim], oneSigma_low[ilim], oneSigma_high[ilim], twoSigma_low[ilim], twoSigma_high[ilim] = self._getGraphs(xvals,limits,xVar=xVar,smooth=smooth,model=model,scales=scales,modelkey=modelkey,y=y,detailed=True)


                def cross(val,prev,curr):
                    if prev>=val and curr<=val: return True
                    if prev<=val and curr>=val: return True
                    return False

            for xi in range(nx+1):
                x = xmin + xi*dx
                for ilim, xvals in enumerate(xvalsMulti):
                    if x>=xvals[0] and x<=xvals[-1]: break
                val = expected[ilim].Eval(x)
                if val<zmin: val = zmin
                eb = expectedHist.GetBin(xi+1,yi+1)
                #eb = expectedHist.FindBin(x,y)
                expectedHist.SetBinContent(eb,val)

                oneSigmaLowHist.SetBinContent( eb, oneSigma_low[ilim].Eval(x))
                oneSigmaHighHist.SetBinContent(eb, oneSigma_high[ilim].Eval(x))
                twoSigmaLowHist.SetBinContent( eb, twoSigma_low[ilim].Eval(x))
                twoSigmaHighHist.SetBinContent(eb, twoSigma_high[ilim].Eval(x))

                oval = observed[ilim].Eval(x)
                # TODO: try
                if oval<zmin: oval = 0
                if oval>zmax: oval = 999*zmax
                observedHist.SetBinContent(eb, oval)


        expectedHistCont = expectedHist.Clone()
        observedHistCont = observedHist.Clone()


        def setHistStyle(hist):
            hist.GetXaxis().SetTitle(xaxis)
            hist.GetYaxis().SetTitle(yaxis)
            hist.GetZaxis().SetTitle(zaxis)
            hist.GetYaxis().SetTitleSize(0.05)
            hist.GetYaxis().SetTitleOffset(1.2)
            hist.GetZaxis().SetTitleSize(0.05)
            hist.GetZaxis().SetTitleOffset(1.5)
            hist.GetZaxis().SetRangeUser(zmin,zmax)

        setHistStyle(expectedHist)
        setHistStyle(observedHist)
        setHistStyle(emptyHist)

        def get_contours(hist,val=1.0):
            contours = array('d',[val])
            hist.SetContour(1,contours)
            hist.Draw('cont z list')
            canvas.Update()
            graphs = []
            conts = ROOT.gROOT.GetListOfSpecials().FindObject('contours')
            i = 0 # why is this needed?!?!?
            if i in range(conts.GetSize()):
                contLevel = conts.At(i)
                for j in range(contLevel.GetSize()):
                    graphs += [contLevel.At(j).Clone()]
                    
            return graphs

        expected_graphs = {}
        oneSigma_graphs = {}
        twoSigma_graphs = {}
        observed_graphs = {}
        for eb in expectedBands:
            expected_graphs[eb] =  get_contours(expectedHistCont,eb)
            observed_graphs[eb] =  get_contours(observedHistCont,eb)
            oneSigma_graphs[eb] =  get_contours(oneSigmaLowHist, eb)
            oneSigma_graphs[eb] += get_contours(oneSigmaHighHist,eb)
            twoSigma_graphs[eb] =  get_contours(twoSigmaLowHist, eb)
            twoSigma_graphs[eb] += get_contours(twoSigmaHighHist,eb)

        #print len(expected_graphs), len(oneSigma_graphs), len(twoSigma_graphs)

        if plotcolz:
            if blind:
                expectedHist.Draw('colz')
            else:
                observedHist.Draw('colz')
        else:
            emptyHist.Draw()

        #colors = [ROOT.kBlack, ROOT.kRed+2, ROOT.kRed]
        colors = [ROOT.kRed+1, ROOT.kGreen+2]

        mg = ROOT.TMultiGraph()
        if plotfill:
            # not working
            #if not blind:
            #    contours = array('d',expectedBands)
            #    colpalette = [colors[i] for i in range(len(expectedBands))]
            #    ROOT.gStyle.SetPalette(len(colpalette), array('i',colpalette))
            #    observedHistCont.SetContour(len(contours),contours)
            #    observedHistCont.Draw('cont0 same')
            # will only work in cases of exclusion on 1 side
            tval = expectedHist.GetBinContent(expectedHist.FindBin(6.0,ymax))
            bval = expectedHist.GetBinContent(expectedHist.FindBin(6.0,ymin))
            lval = expectedHist.GetBinContent(expectedHist.FindBin(xmin,3.0))
            rval = expectedHist.GetBinContent(expectedHist.FindBin(xmax,3.0))
            above = tval<=bval
            left = lval<=rval

            for i,eb in enumerate(expectedBands):
                c = colors[i]
                if not blind:
                    xvals = []
                    yvals = []
                    x = ROOT.Double()
                    y = ROOT.Double()
                    allxvals = []
                    allyvals = []
                    for g in observed_graphs[eb]:
                        thisxvals = []
                        thisyvals = []
                        n = g.GetN()
                        for i in range(n):
                            g.GetPoint(i,x,y)
                            thisxvals += [float(x)]
                            thisyvals += [float(y)]

                        allxvals += [thisxvals]
                        allyvals += [thisyvals]

                    if len(allxvals)==1:
                        if left and allyvals[0][0]<allyvals[0][-1]:
                            xvals = [x for x in reversed(allxvals[0])]
                            yvals = [y for y in reversed(allyvals[0])]
                        else:
                            xvals = allxvals[0]
                            yvals = allyvals[0]
                    elif all([x[0]>x[-1] for x in allxvals]):
                        for thisx, thisy in zip(allxvals,allyvals):
                            xvals = thisx + xvals
                            yvals = thisy + yvals
                    else:
                        for thisx, thisy in zip(allxvals,allyvals):
                            xvals = xvals + thisx
                            yvals = yvals + thisy

                    fx = xvals[0]
                    lx = xvals[-1]
                    fy = yvals[0]
                    ly = yvals[-1]
                    mx = xmin+float(xmax-xmin)/2
                    my = ymin+float(ymax-ymin)/2
                    ty = ymax+1 if above else ymin-1
                    if fx<lx:
                        if fy<ymax-1: # bottom
                            startx = [xmin-1, xmin-1]
                            starty = [ty, fy]
                        else: # top
                            startx = [xmin-1, fx]
                            starty = [ty, ty]
                        if ly<ymax-1: # bottom
                            endx = [xmax+1, xmax+1]
                            endy = [ly, ty]
                        else: # top
                            endx = [lx, xmax+1]
                            endy = [ty, ty]
                    else:
                        # order reversed
                        if fy<ymax-1: # bottom
                            startx = [xmax+1, xmax+1]
                            starty = [ty, fy]
                        else: # top
                            startx = [fx, xmax+1]
                            starty = [ty, ty]
                        if ly<ymax-1: # bottom
                            endx = [xmin-1, xmin-1]
                            endy = [ly, ty]
                        else: # top
                            endx = [lx, xmin-1]
                            endy = [ty, ty]
                    xvals = startx + xvals + endx
                    yvals = starty + yvals + endy
                    #print eb, xvals[:3], xvals[-3:], yvals[:3], yvals[-3:]
                    #print xvals
                    #print yvals

                    g = ROOT.TGraph(len(xvals),array('d',xvals),array('d',yvals))
                    g.SetLineStyle(1)
                    g.SetLineWidth(2)
                    g.SetLineColor(c)
                    g.SetFillColor(c)
                    g.SetFillColorAlpha(c,0.4)
                    g.SetMarkerStyle(0)
                    g.SetFillStyle(1)
                    g.Draw('f')
                    mg.Add(g)
        for i,eb in enumerate(expectedBands):
            c = colors[i]
            if not blind:
                for g in observed_graphs[eb]:
                    g.SetLineStyle(1)
                    g.SetLineWidth(2)
                    g.SetLineColor(c)
                    g.SetMarkerStyle(0)
                    g.SetFillStyle(0)
                    g.Draw('c')
                    mg.Add(g)
        for i,eb in enumerate(expectedBands):
            c = colors[i]
            for g in expected_graphs[eb]:
                g.SetLineStyle(2)
                g.SetLineWidth(2)
                g.SetFillStyle(0)
                g.SetLineColor(c)
                g.SetMarkerStyle(0)
                mg.Add(g)
                g.Draw('c')
            #for g in oneSigma_graphs[eb]:
            #    g.SetLineStyle(2)
            #    g.SetLineWidth(2)
            #    g.SetFillStyle(0)
            #    g.SetLineColor(c)
            #    g.SetMarkerStyle(0)
            #    g.Draw('same')
            #for g in twoSigma_graphs[eb]:
            #    g.SetLineStyle(6)
            #    g.SetLineWidth(2)
            #    g.SetFillStyle(0)
            #    g.SetLineColor(c)
            #    g.SetMarkerStyle(0)
            #    #g.Draw('same')

        #mg.Draw('same')

        # special legend
        if blind:
            entries = [[expected_graphs[eb][0],'#splitline{{Expected exclusion}}{{B(H #rightarrow aa) = {}}}'.format(eb),'l'] for eb in expectedBands if len(expected_graphs[eb])]
        else:
            entries = []
            for eb in expectedBands:
                if len(expected_graphs[eb]): entries += [[expected_graphs[eb][0],'#splitline{{Expected exclusion}}{{B(H #rightarrow aa) = {}}}'.format(eb),'l']]
                if len(observed_graphs[eb]): entries += [[observed_graphs[eb][0],'#splitline{{Observed exclusion}}{{B(H #rightarrow aa) = {}}}'.format(eb),'l']]
        #legend = self._getLegend(entries=entries,numcol=1,position=24,title=legendtitle)
        if plotcolz:
            legend = self._getLegend(entries=entries,numcol=1,position=[0.42,0.59,0.75,0.92],title=legendtitle)
        else:
            legend = self._getLegend(entries=entries,numcol=1,position=[0.52,0.55,0.95,0.92],title=legendtitle)
        legend.Draw()

        if additionaltext:
            nlines = 1 if isinstance(additionaltext,str) else len(additionaltext)
            text = ROOT.TPaveText(0.16,0.90-nlines*0.04,0.40,0.92,'NB NDC')
            text.SetTextFont(42)
            text.SetBorderSize(0)
            text.SetFillColor(0)
            text.SetTextAlign(11)
            if isinstance(additionaltext,list):
                for addt in additionaltext:
                    text.AddText(addt)
            else:
                text.AddText(additionaltext)
            text.Draw()

        # manually add the 1 sigma bands
        leg_one_low  = ROOT.TGraph(2,array('d',[11.72,12.91]),array('d',[8.84,8.84]))
        leg_one_high = ROOT.TGraph(2,array('d',[11.72,12.91]),array('d',[8.69,8.69]))
        leg_two_low  = ROOT.TGraph(2,array('d',[11.72,12.91]),array('d',[8.91,8.91]))
        leg_two_high = ROOT.TGraph(2,array('d',[11.72,12.91]),array('d',[8.62,8.62]))

        leg_one_low.SetLineStyle(2)
        leg_one_low.SetLineWidth(2)
        #leg_one_low.Draw('same')
        leg_one_high.SetLineStyle(2)
        leg_one_high.SetLineWidth(2)
        #leg_one_high.Draw('same')
        leg_two_low.SetLineStyle(6)
        leg_two_low.SetLineWidth(2)
        #leg_two_low.Draw('same')
        leg_two_high.SetLineStyle(6)
        leg_two_high.SetLineWidth(2)
        #leg_two_high.Draw('same')

        # cms lumi styling
        self._setStyle(canvas,position=lumipos,preliminary=isprelim)

        self._save(canvas,savename)

        xSave = [3.6,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21]
        ySave = [1,1.5,2,3,5,10,20,50]

        save = []
        for x in xSave:
            for y in ySave:
                be = expectedHist.FindBin(x,y)
                ve = expectedHist.GetBinContent(be)
                vel = oneSigmaLowHist.GetBinContent(be)
                veh = oneSigmaHighHist.GetBinContent(be)
                save += [(x,y,ve,vel,veh)]

        self._saveCSV(save,savename)
                


    def plotMultiExpected(self,xvals,quartiles,labels,savename,**kwargs):
        '''Plot limits'''
        xaxis = kwargs.pop('xaxis','x')
        yaxis = kwargs.pop('yaxis','95% CL upper limit on #sigma/#sigma_{model}')
        blind = kwargs.pop('blind',True)
        lumipos = kwargs.pop('lumipos',11)
        isprelim = kwargs.pop('isprelim',True)
        legendpos = kwargs.pop('legendpos',31)
        numcol = kwargs.pop('numcol',1)
        smooth = kwargs.pop('smooth',False)
        ymin = kwargs.pop('ymin',None)
        ymax = kwargs.pop('ymax',None)
        logy = kwargs.pop('logy',1)
        colors = kwargs.pop('colors',[])
        plotunity = kwargs.pop('plotunity',True)
        leftmargin = kwargs.pop('leftmargin',None)
        additionaltext = kwargs.pop('additionaltext','')

        logging.info('Plotting {0}'.format(savename))

        canvas = ROOT.TCanvas(savename,savename,50,50,600,600)
        canvas.SetLogy(logy)
        if leftmargin: canvas.SetLeftMargin(leftmargin)

        expected = {}
        observed = {}
        expectedForSmoothing = {}
        expectedSmooth = {}

        for x in range(len(xvals)):
            limits = quartiles[x]

            n = len(xvals[x])
            expected[x] = ROOT.TGraph(n)
            observed[x] = ROOT.TGraph(n)
            expectedForSmoothing[x] = ROOT.TGraph(n)

            for i in range(len(xvals[x])):
                if not all(limits[xvals[x][i]]):
                    print i, xvals[x][i], limits[xvals[x][i]]
                    continue
                expected[x].SetPoint(     i,   xvals[x][i],     limits[xvals[x][i]][2]) # 0.5
                observed[x].SetPoint(     i,   xvals[x][i],     limits[xvals[x][i]][5]) # obs
                expectedForSmoothing[x].SetPoint(     i, xvals[x][i],     math.log(limits[xvals[x][i]][2])) # 0.5

            smoothlog = False
            if smooth: # smooth out the expected bands

                expectedSmoother      = ROOT.TGraphSmooth()
                # smooth log, good for exponentially changing
                if smoothlog:
                    expectedSmooth[x]        = expectedSmoother.SmoothKern(     expectedForSmoothing[x],     'normal',0.5,n)
                    for i in range(len(xvals[x])):
                        expected[x].SetPoint(     i,   expectedSmooth[x].GetX()[i],         math.exp(expectedSmooth[x].GetY()[i]))
                # smooth linear
                else:
                    expectedSmooth[x]        = expectedSmoother.SmoothKern(     expected[x],     'normal',0.3,n)
                    #expectedSmooth[x]        = expectedSmoother.SmoothLowess(expected[x],          '',0.1)
                    #expectedSmooth[x]        = expectedSmoother.SmoothSuper(expected[x],          '',0,0)
                    for i in range(len(xvals[x])):
                        xi = expected[x].GetX()[i]
                        if xi>3 and xi<4: continue # jpsi
                        if xi>9 and xi<11: continue # upsilon
                        expected[x].SetPoint(     i,   expectedSmooth[x].GetX()[i],         expectedSmooth[x].GetY()[i])

            expected[x].SetLineStyle(5)
            expected[x].SetLineColor(ROOT.kAzure)
            expected[x].SetLineWidth(2)
            expected[x].SetMarkerStyle(0)
            expected[x].SetFillStyle(0)
            observed[x].SetMarkerStyle(0)
            observed[x].SetFillStyle(0)
            observed[x].SetLineWidth(2)
            if len(colors)>=x:
                expected[x].SetLineColor(colors[x])
                observed[x].SetLineColor(colors[x])

            expected[x].GetXaxis().SetLimits(xvals[x][0],xvals[x][-1])
            expected[x].GetXaxis().SetTitle(xaxis)
            expected[x].GetYaxis().SetTitle(yaxis)
            expected[x].GetYaxis().SetTitleSize(0.05)
            expected[x].GetYaxis().SetTitleOffset(1.6)

            if x:
                expected[x].Draw('same')
            else:
                expected[x].Draw()
                if ymin is not None: expected[x].SetMinimum(ymin)
                if ymax is not None: expected[x].SetMaximum(ymax)

            if not blind: observed[x].Draw('same')

        ratiounity = ROOT.TLine(expected[0].GetXaxis().GetXmin(),1,expected[0].GetXaxis().GetXmax(),1)
        if plotunity: ratiounity.Draw()

        # get the legend
        entries = []
        for x in range(len(xvals)):
            entries += [[expected[x],'#splitline{'+labels[x]+'}{Expected}', 'l']]
            if not blind: entries += [[observed[x],'#splitline{'+labels[x]+'}{Observed}','l']]
        legend = self._getLegend(entries=entries,numcol=numcol,position=legendpos,widthScale=1.2)
        legend.Draw()

        if additionaltext:
            nlines = 1 if isinstance(additionaltext,str) else len(additionaltext)
            text = ROOT.TPaveText(0.20,0.90-nlines*0.04,0.45,0.92,'NB NDC')
            text.SetTextFont(42)
            text.SetBorderSize(0)
            text.SetFillColor(0)
            text.SetTextAlign(11)
            if isinstance(additionaltext,list):
                for addt in additionaltext:
                    text.AddText(addt)
            else:
                text.AddText(additionaltext)
            text.Draw()

        # cms lumi styling
        self._setStyle(canvas,position=lumipos,preliminary=isprelim)

        self._save(canvas,savename)

