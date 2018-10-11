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

ROOT.gStyle.SetPalette(ROOT.kBird)

ROOT.gStyle.SetNumberContours(255)

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
        model = kwargs.pop('model',None)
        xVar = kwargs.pop('x',None)
        overlay = kwargs.pop('overlay',None)
        overlayLabels = kwargs.pop('overlayLabels',None)

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
            if asymptoticFilenames:
                twoSigma_asym.SetPoint(i,  xvals[i],     limits_asym[xvals[i]][0]) # 0.025
                oneSigma_asym.SetPoint(i,  xvals[i],     limits_asym[xvals[i]][1]) # 0.16
                expected_asym.SetPoint(i,  xvals[i],     limits_asym[xvals[i]][2]) # 0.5
                oneSigma_asym.SetPoint(2*n-i-1,xvals[i], limits_asym[xvals[i]][3]) # 0.84
                twoSigma_asym.SetPoint(2*n-i-1,xvals[i], limits_asym[xvals[i]][4]) # 0.975
                observed_asym.SetPoint(i,  xvals[i],     limits_asym[xvals[i]][5]) # obs
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
                twoSigmaSmooth_low    = twoSigmaSmoother_low.SmoothKern( twoSigma_low, 'normal',0.3,n)
                twoSigmaSmooth_high   = twoSigmaSmoother_high.SmoothKern(twoSigma_high,'normal',0.3,n)
                oneSigmaSmooth_low    = oneSigmaSmoother_low.SmoothKern( oneSigma_low, 'normal',0.3,n)
                oneSigmaSmooth_high   = oneSigmaSmoother_high.SmoothKern(oneSigma_high,'normal',0.3,n)
                expectedSmooth        = expectedSmoother.SmoothKern(     expected,     'normal',0.3,n)
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
                    if x>9 and x<11: continue # upsilon
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
        legend = self._getLegend(entries=entries,numcol=numcol,position=legendpos,title='95% CL upper limits')
        legend.Draw()


        if overlayLabels:
            entries = []
            for g,l in zip(overlay,overlayLabels):
                entries += [[g,l,'l']]
            legendOverlay = self._getLegend(entries=entries,numcol=1,position=32)
            legendOverlay.Draw()

        # cms lumi styling
        self._setStyle(canvas,position=lumipos,preliminary=isprelim)

        self._save(canvas,savename)


    def plotLimit2D(self,xvals,yvals,quartiles,scales,savename,**kwargs):
        '''Plot limits'''
        xaxis = kwargs.pop('xaxis','x')
        yaxis = kwargs.pop('yaxis','y')
        zaxis = kwargs.pop('zaxis','95% CLs Upper Limit on #sigma/#sigma_{model}')
        blind = kwargs.pop('blind',True)
        lumipos = kwargs.pop('lumipos',11)
        isprelim = kwargs.pop('isprelim',True)
        legendpos = kwargs.pop('legendpos',31)
        numcol = kwargs.pop('numcol',1)
        asymptoticFilenames = kwargs.pop('asymptoticFilenames',[])
        smooth = kwargs.pop('smooth',False)
        logz = kwargs.pop('logz',1)
        logy = kwargs.pop('logy',0)
        plotunity = kwargs.pop('plotunity',True)
        model = kwargs.pop('model',None)
        modelkey = kwargs.pop('modelkey',None)
        xVar = kwargs.pop('x',None)
        expectedBands = kwargs.pop('expectedBands', [])
        zmin = kwargs.pop('zmin',1e-2)
        zmax = kwargs.pop('zmax',1)

        logging.info('Plotting {0}'.format(savename))

        canvas = ROOT.TCanvas(savename,savename,50,50,600,600)
        canvas.SetLogz(logz)
        canvas.SetLogy(logy)
        canvas.SetLeftMargin(0.14)
        canvas.SetRightMargin(0.22)

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
                scale = scales[xvals[i]][modelkey].Eval(y)
                if scale<=0: scale = 1e-10
                twoSigma.SetPoint(     i,   xvals[i],     limits[xvals[i]][0]*scale) # 0.025
                oneSigma.SetPoint(     i,   xvals[i],     limits[xvals[i]][1]*scale) # 0.16
                expected.SetPoint(     i,   xvals[i],     limits[xvals[i]][2]*scale) # 0.5
                oneSigma.SetPoint(2*n-i-1,  xvals[i],     limits[xvals[i]][3]*scale) # 0.84
                twoSigma.SetPoint(2*n-i-1,  xvals[i],     limits[xvals[i]][4]*scale) # 0.975
                observed.SetPoint(     i,   xvals[i],     limits[xvals[i]][5]*scale) # obs
                twoSigma_high.SetPoint(i,   xvals[i],     limits[xvals[i]][0]*scale) # 0.025
                oneSigma_high.SetPoint(i,   xvals[i],     limits[xvals[i]][1]*scale) # 0.16
                oneSigma_low.SetPoint(n-i-1,xvals[i],     limits[xvals[i]][3]*scale) # 0.84
                twoSigma_low.SetPoint(n-i-1,xvals[i],     limits[xvals[i]][4]*scale) # 0.975
                twoSigmaForSmoothing_high.SetPoint(i, xvals[i],     math.log(limits[xvals[i]][0]*scale)) # 0.025
                oneSigmaForSmoothing_high.SetPoint(i, xvals[i],     math.log(limits[xvals[i]][1]*scale)) # 0.16
                oneSigmaForSmoothing_low.SetPoint(n-i-1, xvals[i],  math.log(limits[xvals[i]][3]*scale)) # 0.84
                twoSigmaForSmoothing_low.SetPoint(n-i-1, xvals[i],  math.log(limits[xvals[i]][4]*scale)) # 0.975
                expectedForSmoothing.SetPoint(     i, xvals[i],     math.log(limits[xvals[i]][2]*scale)) # 0.5
                if asymptoticFilenames:
                    twoSigma_asym.SetPoint(i,  xvals[i],     limits_asym[xvals[i]][0]*scale) # 0.025
                    oneSigma_asym.SetPoint(i,  xvals[i],     limits_asym[xvals[i]][1]*scale) # 0.16
                    expected_asym.SetPoint(i,  xvals[i],     limits_asym[xvals[i]][2]*scale) # 0.5
                    oneSigma_asym.SetPoint(2*n-i-1,xvals[i], limits_asym[xvals[i]][3]*scale) # 0.84
                    twoSigma_asym.SetPoint(2*n-i-1,xvals[i], limits_asym[xvals[i]][4]*scale) # 0.975
                    observed_asym.SetPoint(i,  xvals[i],     limits_asym[xvals[i]][5]*scale) # obs
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
                    twoSigmaSmooth_low    = twoSigmaSmoother_low.SmoothKern( twoSigma_low, 'normal',0.3,n)
                    twoSigmaSmooth_high   = twoSigmaSmoother_high.SmoothKern(twoSigma_high,'normal',0.3,n)
                    oneSigmaSmooth_low    = oneSigmaSmoother_low.SmoothKern( oneSigma_low, 'normal',0.3,n)
                    oneSigmaSmooth_high   = oneSigmaSmoother_high.SmoothKern(oneSigma_high,'normal',0.3,n)
                    expectedSmooth        = expectedSmoother.SmoothKern(     expected,     'normal',0.3,n)
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
                        if x>9 and x<11: continue # upsilon
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
                #if val<1e-3: val = 1e-3
                eb = expectedHist.GetBin(xi+1,yi+1)
                #eb = expectedHist.FindBin(x,y)
                expectedHist.SetBinContent(eb,val)

                oneSigmaLowHist.SetBinContent( eb, oneSigma_low.Eval(x))
                oneSigmaHighHist.SetBinContent(eb, oneSigma_high.Eval(x))
                twoSigmaLowHist.SetBinContent( eb, twoSigma_low.Eval(x))
                twoSigmaHighHist.SetBinContent(eb, twoSigma_high.Eval(x))

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

        expectedHist.GetXaxis().SetTitle(xaxis)
        expectedHist.GetYaxis().SetTitle(yaxis)
        expectedHist.GetZaxis().SetTitle(zaxis)
        expectedHist.GetYaxis().SetTitleSize(0.05)
        expectedHist.GetYaxis().SetTitleOffset(1.2)
        expectedHist.GetZaxis().SetTitleSize(0.05)
        expectedHist.GetZaxis().SetTitleOffset(1.5)
        expectedHist.GetZaxis().SetRangeUser(zmin,zmax)

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
        for eb in expectedBands:
            expected_graphs[eb] =  get_contours(expectedHistCont,eb)
            oneSigma_graphs[eb] =  get_contours(oneSigmaLowHist, eb)
            oneSigma_graphs[eb] += get_contours(oneSigmaHighHist,eb)
            twoSigma_graphs[eb] =  get_contours(twoSigmaLowHist, eb)
            twoSigma_graphs[eb] += get_contours(twoSigmaHighHist,eb)

        #print len(expected_graphs), len(oneSigma_graphs), len(twoSigma_graphs)

        colors = [ROOT.kBlack, ROOT.kRed+2, ROOT.kRed]

        expectedHist.Draw('colz')
        for i in range(len(expectedBands)):
            eb = expectedBands[i]
            c = colors[i]
            for g in expected_graphs[eb]:
                g.SetLineStyle(2)
                g.SetLineWidth(2)
                g.SetFillStyle(0)
                g.SetLineColor(c)
                g.SetMarkerStyle(0)
                g.Draw('same')
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

        # special legend
        entries = [[expected_graphs[eb][0],'#splitline{{Expected exclusion}}{{BR(H #rightarrow aa) = {}}}'.format(eb),'l'] for eb in expectedBands if len(expected_graphs[eb])]
        title = '#splitline{{2HDM+S Type {}}}{{95% CL upper limits}}'.format(modelkey)
        legend = self._getLegend(entries=entries,numcol=1,position=24,title=title)
        legend.Draw()

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
                


    def plotPValue(self,xvals,quartiles,savename,**kwargs):
        '''Plot p-values'''
        xaxis = kwargs.pop('xaxis','#Phi^{++} Mass (GeV)')
        yaxis = kwargs.pop('yaxis','Local p-value')
        blind = kwargs.pop('blind',True)
        lumipos = kwargs.pop('lumipos',11)
        isprelim = kwargs.pop('isprelim',True)
        smooth = kwargs.pop('smooth',False)
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
        expectedForSmoothing = ROOT.TGraph(n)

        for i in range(len(xvals)):
            expected.SetPoint(     i,   xvals[i],     limits[xvals[i]][0])
            observed.SetPoint(     i,   xvals[i],     limits[xvals[i]][1])
            try:
                expectedForSmoothing.SetPoint(     i, xvals[i],     math.log(limits[xvals[i]][0])) # 0.5
            except:
                print limits[xvals[i]]
                e = sys.exc_info()[0]
                print e
                raise

        smoothlog = True
        if smooth: # smooth out the expected bands

            expectedSmoother      = ROOT.TGraphSmooth()
            # smooth log, good for exponentially changing
            if smoothlog:
                expectedSmooth        = expectedSmoother.SmoothKern(     expectedForSmoothing,     'normal',0.5,n)
                for i in range(len(xvals)):
                    expected.SetPoint(     i,   expectedSmooth.GetX()[i],         math.exp(expectedSmooth.GetY()[i]))
            # smooth linear
            else:
                expectedSmooth        = expectedSmoother.SmoothKern(     expected,     'normal',0.3,n)
                #expectedSmooth        = expectedSmoother.SmoothLowess(expected,          '',0.1)
                #expectedSmooth        = expectedSmoother.SmoothSuper(expected,          '',0,0)
                for i in range(len(xvals)):
                    x = expectedSmooth.GetX()[i]
                    if x>3 and x<4: continue # jpsi
                    if x>9 and x<11: continue # upsilon
                    expected.SetPoint(     i,   expectedSmooth.GetX()[i],         expectedSmooth.GetY()[i])

        expected.SetLineStyle(5)
        expected.SetLineColor(ROOT.kAzure)
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

    def plotMultiExpected(self,xvals,quartiles,labels,savename,**kwargs):
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
        colors = kwargs.pop('colors',[])
        plotunity = kwargs.pop('plotunity',True)
        leftmargin = kwargs.pop('leftmargin',None)

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

        # cms lumi styling
        self._setStyle(canvas,position=lumipos,preliminary=isprelim)

        self._save(canvas,savename)

