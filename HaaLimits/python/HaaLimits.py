import os
import sys
import logging
import itertools
import numpy as np
import argparse
import math
import errno
from array import array

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.SetBatch()

import CombineLimits.Limits.Models as Models
from CombineLimits.Limits.Limits import Limits
from CombineLimits.Limits.utilities import *

class HaaLimits(Limits):
    '''
    Create the Haa Limits workspace
    '''

    # permanent parameters
    HMASSES = [125,300,750]
    AMASSES = ['3p6',4,5,6,7,9,11,13,15,17,19,21]

    SIGNAME = 'HToAAH{h}A{a}'
    SPLINENAME = 'sig{h}'
    SPLINELABEL = 'm_{a}'
    SPLINERANGE = [0,30]

    XRANGE = [4,25]
    XLABEL = 'm_{#mu#mu}'
    UPSILONRANGE = [7, 12]

    REGIONS = ['FP','PP']
    SHIFTS = []


    def __init__(self,histMap,tag=''):
        '''
        Required arguments:
            histMap = histogram map. the structure should be:
                histMap[region][shift][process] = ROOT.TH1()
                where:
                    region  : 'PP' or 'FP' for regions A and B, respectively
                    shift   : '', 'shiftName', 'shiftNameUp', or 'shiftNameDown'
                        ''                   : central value
                        'shiftName'          : a symmetric shift (ie, jet resolution)
                        'shiftName[Up,Down]' : an asymmetric shift (ie, fake rate, lepton efficiencies, etc)
                        shiftName            : the name the uncertainty will be given in the datacard
                    process : the name of the process
                        signal must be of the form 'HToAAH{h}A{a}'
                        data = 'data'
                        background = 'datadriven'
        '''
        super(HaaLimits,self).__init__()

        self.histMap = histMap
        self.tag = tag

        self.binned = self.histMap['PP']['']['data'].InheritsFrom('TH1')

        self.plotDir = 'figures/HaaLimits{}'.format('_'+tag if tag else '')
        python_mkdir(self.plotDir)


    ###########################
    ### Workspace utilities ###
    ###########################
    def initializeWorkspace(self):
        self.addX(*self.XRANGE,unit='GeV',label=self.XLABEL)
        self.addMH(*self.SPLINERANGE,unit='GeV',label=self.SPLINELABEL)

    def buildModel(self, region='PP', addUpsilon=True, setUpsilonLambda=False, **kwargs):
        tag = kwargs.pop('tag',region)
        # jpsi
        jpsi1S = Models.Gaussian('jpsi1S',
            mean  = [3.1,2.9,3.2],
            sigma = [0.1,0,0.5],
            width = [0.1,0.01,0.5],
        )
        nameJ1 = 'jpsi1S'
        jpsi1S.build(self.workspace,nameJ1)
    
        jpsi2S = Models.Gaussian('jpsi2S',
            mean  = [3.7,3.6,3.8],
            sigma = [0.1,0.01,0.5],
            width = [0.1,0.01,0.5],
        )
        nameJ2 = 'jpsi2S'
        jpsi2S.build(self.workspace,nameJ2)
    
        # upsilon
        upsilon1S = Models.Gaussian('upsilon1S',
            mean  = [9.5,9.3,9.7],
            sigma = [0.1,0.01,0.3],
        )
        nameU1 = 'upsilon1S'
        upsilon1S.build(self.workspace,nameU1)
    
        upsilon2S = Models.Gaussian('upsilon2S',
            mean  = [10.0,9.8,10.15],
            sigma = [0.1,0.01,0.3],
        )
        nameU2 = 'upsilon2S'
        upsilon2S.build(self.workspace,nameU2)
    
        upsilon3S = Models.Gaussian('upsilon3S',
            mean  = [10.3,10.22,10.5],
            sigma = [0.1,0.04,0.3],
        )
        nameU3 = 'upsilon3S'
        upsilon3S.build(self.workspace,nameU3)


        # continuum background
        cont = Models.Chebychev('cont',
            order = 2,
            p0 = [-1,-1.4,0],
            p1 = [0.25,0,0.5],
            p2 = [0.03,-1,1],
        )
        nameC = 'cont{}'.format('_'+tag if tag else '')
        cont.build(self.workspace,nameC)
    
        cont1 = Models.Exponential('cont1', lamb = [-0.20,-1,0],  )
        nameC1 = 'cont1{}'.format('_'+tag if tag else '')
        cont1.build(self.workspace,nameC1)

        cont2 = Models.Exponential('cont2',
            lamb = [-0.05,-1,0],
        )
        nameC2 = 'cont2{}'.format('_'+tag if tag else '')
        cont2.build(self.workspace,nameC2)
    
        cont3 = Models.Exponential('cont3',
            lamb = [-0.75,-5,0],
        )
        nameC3 = 'cont3{}'.format('_'+tag if tag else '')
        cont3.build(self.workspace,nameC3)
    
        cont4 = Models.Exponential('cont4',
            lamb = [-2,-5,0],
        )
        nameC4 = 'cont4{}'.format('_'+tag if tag else '')
        cont4.build(self.workspace,nameC4)

        # sum
        bgs = {'recursive': True}
        # continuum background
        bgs[nameC1] = [0.5,0,1]
        # jpsi
        if self.XRANGE[0]<4:
            print "ADDING J/PSI"
            bgs[nameJ1] = [0.9,0,1]
            bgs[nameJ2] = [0.9,0,1]
            bgs[nameC3] = [0.5,0,1]
        # upsilon
        if addUpsilon and self.XRANGE[0]<=9 and self.XRANGE[1]>=11:
            print "ADDING UPSILON"
            bgs[nameU1] = [0.9,0,1]
            bgs[nameU2] = [0.9,0,1]
            bgs[nameU3] = [0.9,0,1]
        bg = Models.Sum('bg', **bgs)
        name = 'bg_{}'.format(region)
        bg.build(self.workspace,name)
            

    def buildSpline(self,h,region='PP',shift='',**kwargs):
        '''
        Get the signal spline for a given Higgs mass.
        Required arguments:
            h = higgs mass
        '''
        fit = kwargs.get('fit',False)      # will fit the spline parameters rather than a simple spline
        avals = [float(str(x).replace('p','.')) for x in self.AMASSES]
        histMap = self.histMap[region][shift]
        tag= '{}{}'.format(region,'_'+shift if shift else '')
        # initial fit
        results = {}
        errors = {}
        results[h] = {}
        errors[h] = {}
        for a in self.AMASSES:
            aval = float(str(a).replace('p','.'))
            ws = ROOT.RooWorkspace('sig')
            ws.factory('x[{0}, {1}]'.format(*self.XRANGE))
            ws.var('x').setUnit('GeV')
            ws.var('x').setPlotLabel(self.XLABEL)
            ws.var('x').SetTitle(self.XLABEL)
            model = Models.Voigtian('sig',
                mean  = [aval,0,30],
                width = [0.01*aval,0,5],
                sigma = [0.01*aval,0,5],
            )
            model.build(ws, 'sig')
            hist = histMap[self.SIGNAME.format(h=h,a=a)]
            saveDir = '{}/{}'.format(self.plotDir,shift if shift else 'central')
            results[h][a], errors[h][a] = model.fit(ws, hist, 'h{}_a{}_{}'.format(h,a,tag), saveDir=saveDir, save=True, doErrors=True)
    
        #models = {
        #    'mean' : Models.Chebychev('mean',  order = 1, p0 = [0,-1,1], p1 = [0.1,-1,1], p2 = [0.03,-1,1]),
        #    'width': Models.Chebychev('width', order = 1, p0 = [0,-1,1], p1 = [0.1,-1,1], p2 = [0.03,-1,1]),
        #    'sigma': Models.Chebychev('sigma', order = 1, p0 = [0,-1,1], p1 = [0.1,-1,1], p2 = [0.03,-1,1]),
        #}

        #for param in ['mean', 'width', 'sigma']:
        #    ws = ROOT.RooWorkspace(param)
        #    ws.factory('x[{},{}]'.format(*self.XRANGE))
        #    ws.var('x').setUnit('GeV')
        #    ws.var('x').setPlotLabel(self.SPLINELABEL)
        #    ws.var('x').SetTitle(self.SPLINELABEL)
        #    model = models[param]
        #    model.build(ws, param)
        #    name = '{}_{}{}'.format(param,h,tag)
        #    hist = ROOT.TH1D(name, name, len(self.AMASSES), 4, 22)
        #    vals = [results[h][a]['{}_h{}_a{}_{}'.format(param,h,a,tag)] for a in self.AMASSES]
        #    errs = [errors[h][a]['{}_h{}_a{}_{}'.format(param,h,a,tag)] for a in self.AMASSES]
        #    for i,a in enumerate(self.AMASSES):
        #        b = hist.FindBin(a)
        #        hist.SetBinContent(b,vals[i])
        #        hist.SetBinError(b,errs[i])
        #    saveDir = '{}/{}'.format(self.plotDir,shift if shift else 'central')
        #    model.fit(ws, hist, name, saveDir=saveDir, save=True)

        # Fit using ROOT rather than RooFit for the splines
        fitFuncs = {
            'mean' : 'pol1',
            'width': 'pol2',
            'sigma': 'pol2',
        }

        xs = []
        x = self.XRANGE[0]
        while x<=self.XRANGE[1]:
            xs += [x]
            x += float(self.XRANGE[1]-self.XRANGE[0])/100
        fittedParams = {}
        for param in ['mean','width','sigma']:
            name = '{}_{}{}'.format(param,h,tag)
            xerrs = [0]*len(self.AMASSES)
            vals = [results[h][a]['{}_h{}_a{}_{}'.format(param,h,a,tag)] for a in self.AMASSES]
            errs = [errors[h][a]['{}_h{}_a{}_{}'.format(param,h,a,tag)] for a in self.AMASSES]
            graph = ROOT.TGraphErrors(len(avals),array('d',avals),array('d',vals),array('d',xerrs),array('d',errs))
            savename = '{}/{}/{}_Fit'.format(self.plotDir,shift if shift else 'central',name)
            canvas = ROOT.TCanvas(savename,savename,800,800)
            graph.Draw()
            graph.SetTitle('')
            graph.GetHistogram().GetXaxis().SetTitle(self.SPLINELABEL)
            graph.GetHistogram().GetYaxis().SetTitle(param)
            fit = graph.Fit(fitFuncs[param])
            canvas.Print('{}.png'.format(savename))
            func = graph.GetFunction(fitFuncs[param])
            fittedParams[param] = [func.Eval(x) for x in xs]

    
        # create model
        for a in self.AMASSES:
            print h, a, results[h][a]
        if fit:
            model = Models.VoigtianSpline(self.SPLINENAME.format(h=h),
                **{
                    'masses' : xs,
                    'means'  : fittedParams['mean'],
                    'widths' : fittedParams['width'],
                    'sigmas' : fittedParams['sigma'],
                }
            )
        else:
            model = Models.VoigtianSpline(self.SPLINENAME.format(h=h),
                **{
                    'masses' : avals,
                    'means'  : [results[h][a]['mean_h{0}_a{1}_{2}'.format(h,a,tag)] for a in self.AMASSES],
                    'widths' : [results[h][a]['width_h{0}_a{1}_{2}'.format(h,a,tag)] for a in self.AMASSES],
                    'sigmas' : [results[h][a]['sigma_h{0}_a{1}_{2}'.format(h,a,tag)] for a in self.AMASSES],
                }
            )
        if self.binned:
            integrals = [histMap[self.SIGNAME.format(h=h,a=a)].Integral() for a in self.AMASSES]
        else:
            integrals = [histMap[self.SIGNAME.format(h=h,a=a)].sumEntries('x>{} && x<{}'.format(*self.XRANGE)) for a in self.AMASSES]
        print 'Integrals', tag, h, integrals

        if fit:
            param = 'integral'
            funcname = 'pol2'
            name = '{}_{}{}'.format(param,h,tag)
            vals = integrals
            graph = ROOT.TGraph(len(avals),array('d',avals),array('d',vals))
            savename = '{}/{}/{}_Fit'.format(self.plotDir,shift if shift else 'central',name)
            canvas = ROOT.TCanvas(savename,savename,800,800)
            graph.Draw()
            graph.SetTitle('')
            graph.GetHistogram().GetXaxis().SetTitle(self.SPLINELABEL)
            graph.GetHistogram().GetYaxis().SetTitle('integral')
            fit = graph.Fit(funcname)
            canvas.Print('{}.png'.format(savename))
            func = graph.GetFunction(funcname)
            newintegrals = [func.Eval(x) for x in xs]
            # dont fit integrals
            #model.setIntegral(xs,newintegrals)
        model.setIntegral(avals,integrals)

        model.build(self.workspace,'{}_{}'.format(self.SPLINENAME.format(h=h),tag))
        model.buildIntegral(self.workspace,'integral_{}_{}'.format(self.SPLINENAME.format(h=h),tag))

    def fitBackground(self,region='PP',shift='', setUpsilonLambda=False, addUpsilon=True):
        model = self.workspace.pdf('bg_{}'.format(region))
        name = 'data_prefit_{}{}'.format(region,'_'+shift if shift else '')
        hist = self.histMap[region][shift]['dataNoSig']
        if self.binned:
            data = ROOT.RooDataHist(name,name,ROOT.RooArgList(self.workspace.var('x')),hist)
        else:
            data = hist.Clone(name)

        if setUpsilonLambda:
            self.workspace.var("x").setRange("low", self.XRANGE[0], self.UPSILONRANGE[0] )
            self.workspace.var("x").setRange("high", self.UPSILONRANGE[1], self.XRANGE[1])
            fr = model.fitTo(data, ROOT.RooFit.Save(), ROOT.RooFit.SumW2Error(True), ROOT.RooFit.Range("low,high") )
        else:
            fr = model.fitTo(data, ROOT.RooFit.Save(), ROOT.RooFit.SumW2Error(True) )

        xFrame = self.workspace.var('x').frame()
        data.plotOn(xFrame)
        # continuum
        model.plotOn(xFrame,ROOT.RooFit.Components('cont1_{}'.format(region)),ROOT.RooFit.LineStyle(ROOT.kDashed))
        model.plotOn(xFrame,ROOT.RooFit.Components('cont2_{}'.format(region)),ROOT.RooFit.LineStyle(ROOT.kDashed))
        if self.XRANGE[0]<4:
            # extended continuum when also fitting jpsi
            model.plotOn(xFrame,ROOT.RooFit.Components('cont3_{}'.format(region)),ROOT.RooFit.LineStyle(ROOT.kDashed))
            model.plotOn(xFrame,ROOT.RooFit.Components('cont4_{}'.format(region)),ROOT.RooFit.LineStyle(ROOT.kDashed))
            # jpsi
            model.plotOn(xFrame,ROOT.RooFit.Components('jpsi1S'),ROOT.RooFit.LineColor(ROOT.kRed))
            model.plotOn(xFrame,ROOT.RooFit.Components('jpsi2S'),ROOT.RooFit.LineColor(ROOT.kRed))
        # upsilon
        model.plotOn(xFrame,ROOT.RooFit.Components('upsilon1S'),ROOT.RooFit.LineColor(ROOT.kRed))
        model.plotOn(xFrame,ROOT.RooFit.Components('upsilon2S'),ROOT.RooFit.LineColor(ROOT.kRed))
        model.plotOn(xFrame,ROOT.RooFit.Components('upsilon3S'),ROOT.RooFit.LineColor(ROOT.kRed))
        # combined model
        model.plotOn(xFrame)

        canvas = ROOT.TCanvas('c','c',800,800)
        xFrame.Draw()
        #canvas.SetLogy()
        canvas.Print('{}/model_fit_{}{}.png'.format(self.plotDir,region,'_'+shift if shift else ''))

        pars = fr.floatParsFinal()
        vals = {}
        errs = {}
        for p in range(pars.getSize()):
            vals[pars.at(p).GetName()] = pars.at(p).getValV()
            errs[pars.at(p).GetName()] = pars.at(p).getError()
        for v in sorted(vals.keys()):
            print '  ', v, vals[v], '+/-', errs[v]


    ###############################
    ### Add things to workspace ###
    ###############################
    def addData(self,asimov=False,addSignal=False,**kwargs):
        mh = kwargs.pop('h',125)
        ma = kwargs.pop('a',15)
        for region in self.REGIONS:
            name = 'data_obs_{}'.format(region)
            hist = self.histMap[region]['']['data']
            if asimov:
                # generate a toy data observation from the model
                # TODO addSignal
                model = self.workspace.pdf('bg_{}'.format(region))
                h = self.histMap[region]['']['dataNoSig']
                if self.binned:
                    integral = h.Integral(h.FindBin(self.XRANGE[0]),h.FindBin(self.XRANGE[1]))
                else:
                    integral = h.sumEntries('x>{} && x<{}'.format(*self.XRANGE))
                data_obs = model.generate(ROOT.RooArgSet(self.workspace.var('x')),int(integral))
                if addSignal:
                    self.workspace.var('MH').setVal(ma)
                    model = self.workspace.pdf('{}_{}'.format(self.SPLINENAME.format(h=mh),region))
                    integral = self.workspace.function('integral_{}_{}'.format(self.SPLINENAME.format(h=mh),region)).getVal()
                    sig_obs = model.generate(ROOT.RooArgSet(self.workspace.var('x')),int(integral))
                    data_obs.append(sig_obs)
                data_obs.SetName(name)
            else:
                # use the provided data
                if self.binned:
                    data_obs = ROOT.RooDataHist(name,name,ROOT.RooArgList(self.workspace.var('x')),self.histMap[region]['']['data'])
                else:
                    data_obs = hist.Clone(name)
            self.wsimport(data_obs, ROOT.RooFit.RecycleConflictNodes() )

    def addBackgroundModels(self, fixAfterFP=False, addUpsilon=True, setUpsilonLambda=False):
        if setUpsilonLambda:
            self.workspace.arg("lambda_cont1_FP").setConstant(True)
            self.workspace.arg("lambda_cont1_PP").setConstant(True)
        for region in self.REGIONS:
            if region == 'PP' and fixAfterFP and addUpsilon and self.XRANGE[0]<=9 and self.XRANGE[1]>=11:
                print "Setting mean sigma and fraction of Upsilon 1S, 2S, 3S constant after fitting to FP"
                self.workspace.arg("mean_upsilon1S").setConstant(True)
                self.workspace.arg("mean_upsilon2S").setConstant(True)
                self.workspace.arg("mean_upsilon3S").setConstant(True)
                self.workspace.arg("sigma_upsilon1S").setConstant(True)
                self.workspace.arg("sigma_upsilon2S").setConstant(True)
                self.workspace.arg("sigma_upsilon3S").setConstant(True)
                self.workspace.arg("upsilon1S_frac").setConstant(True) 
                self.workspace.arg("upsilon2S_frac").setConstant(True) 
                self.workspace.arg("upsilon3S_frac").setConstant(True) 
            self.buildModel(region=region, addUpsilon=addUpsilon, setUpsilonLambda=setUpsilonLambda)
            self.workspace.factory('bg_{}_norm[1,0,2]'.format(region))
            self.fitBackground(region=region, setUpsilonLambda=setUpsilonLambda, addUpsilon=addUpsilon)
            if region == 'PP' and fixAfterFP and addUpsilon and self.XRANGE[0]<=9 and self.XRANGE[1]>=11: 
                print "SETTING NOT CONSTANT"
                self.workspace.arg("mean_upsilon1S").setConstant(False)
                self.workspace.arg("mean_upsilon2S").setConstant(False)
                self.workspace.arg("mean_upsilon3S").setConstant(False)
                self.workspace.arg("sigma_upsilon1S").setConstant(False)
                self.workspace.arg("sigma_upsilon2S").setConstant(False)
                self.workspace.arg("sigma_upsilon3S").setConstant(False)
                self.workspace.arg("upsilon1S_frac").setConstant(False) 
                self.workspace.arg("upsilon2S_frac").setConstant(False) 
                self.workspace.arg("upsilon3S_frac").setConstant(False) 

    def addSignalModels(self,**kwargs):
        for region in self.REGIONS:
            for shift in ['']+self.SHIFTS:
                for h in self.HMASSES:
                    if shift == '':
                        self.buildSpline(h,region=region,shift=shift,**kwargs)
                    else:
                        self.buildSpline(h,region=region,shift=shift+'Up',**kwargs)
                        self.buildSpline(h,region=region,shift=shift+'Down',**kwargs)
            self.workspace.factory('{}_{}_norm[1,0,9999]'.format(self.SPLINENAME.format(h=h),region))

    ######################
    ### Setup datacard ###
    ######################
    def setupDatacard(self):

        # setup bins
        for region in self.REGIONS:
            self.addBin(region)

        # add processes
        self.addProcess('bg')

        for proc in [self.SPLINENAME.format(h=h) for h in self.HMASSES]:
            self.addProcess(proc,signal=True)

        # set expected
        for region in self.REGIONS:
            h = self.histMap[region]['']['dataNoSig']
            if self.binned:
                integral = h.Integral(h.FindBin(self.XRANGE[0]),h.FindBin(self.XRANGE[1]))
            else:
                integral = h.sumEntries('x>{} && x<{}'.format(*self.XRANGE))
            self.setExpected('bg',region,integral)

            for proc in [self.SPLINENAME.format(h=h) for h in self.HMASSES]:
                self.setExpected(proc,region,1)
                self.addRateParam('integral_{}_{}'.format(proc,region),region,proc)
                
            self.setObserved(region,-1) # reads from histogram

            

    ###################
    ### Systematics ###
    ###################
    def addSystematics(self):
        print "ADDING SYSTEMATICS"
        self.sigProcesses = tuple([self.SPLINENAME.format(h=h) for h in self.HMASSES])
        self._addLumiSystematic()
        self._addMuonSystematic()
        self._addTauSystematic()
        self._addShapeSystematic()

    def _addShapeSystematic(self):
        for shift in self.SHIFTS:
            shapeproc = self.sigProcesses
            shapesyst = { (shapeproc, tuple( self.REGIONS)) :shift, }
            self.addSystematic(shift, 'shape', systematics=shapesyst)
    
    def _addLumiSystematic(self):
        # lumi: 2.5% 2016
        lumiproc = self.sigProcesses
        lumisyst = {
            (lumiproc,tuple(self.REGIONS)) : 1.025,
        }
        self.addSystematic('lumi','lnN',systematics=lumisyst)

    def _addMuonSystematic(self):
        # from z: 1 % + 0.5 % + 0.5 % per muon for id + iso + trig (pt>20)
        muproc = self.sigProcesses
        musyst = {
            (muproc,tuple(self.REGIONS)) : 1+math.sqrt(sum([0.01**2,0.005**2]*2+[0.01**2])), # 2 lead have iso, tau_mu doesnt
        }
        self.addSystematic('muid','lnN',systematics=musyst)
        
        musyst = {
            (muproc,tuple(self.REGIONS)) : 1.005, # 1 triggering muon
        }
        self.addSystematic('mutrig','lnN',systematics=musyst)
        
    def _addTauSystematic(self):
        # 5% on sf 0.99 (VL/L) 0.97 (M) 0.95 (T) 0.93 (VT)
        tauproc = self.sigProcesses
        tausyst = {
            (tauproc,tuple(self.REGIONS)) : 1.05,
        }
        self.addSystematic('tauid','lnN',systematics=tausyst)
        
    ###################################
    ### Save workspace and datacard ###
    ###################################
    def save(self,name='mmmt', subdirectory=''):
        processes = {}
        for h in self.HMASSES:
            processes[self.SIGNAME.format(h=h,a='X')] = [self.SPLINENAME.format(h=h)] + ['bg']
        if subdirectory == '':
          self.printCard('datacards_shape/MuMuTauTau/{}'.format(name),processes=processes,blind=False,saveWorkspace=True)
        else:
          self.printCard('datacards_shape/MuMuTauTau/' + subdirectory + '{}'.format(name),processes=processes,blind=False,saveWorkspace=True)
          
    def GetWorkspaceValue(self, variable):
        lam = self.workspace.argSet(variable)
        return lam.getRealValue(variable)
