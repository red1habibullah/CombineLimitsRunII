import os
import sys
import logging
import itertools
import numpy as np
import argparse
import math
import errno

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.SetBatch()

import CombineLimits.Limits.Models as Models
from CombineLimits.Limits.Limits import Limits
from CombineLimits.HaaLimits.HaaLimits import HaaLimits
from CombineLimits.Limits.utilities import *

class HaaLimits2D(HaaLimits):
    '''
    Create the Haa Limits workspace
    '''

    YRANGE = [50,1000]
    YLABEL = 'm_{#mu#mu#tau_{#mu}#tau_{h}}'

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
        super(HaaLimits2D,self).__init__(histMap,tag=tag)

        self.plotDir = 'figures/HaaLimits2D{}'.format('_'+tag if tag else '')
        python_mkdir(self.plotDir)


    ###########################
    ### Workspace utilities ###
    ###########################
    def initializeWorkspace(self):
        self.addX(*self.XRANGE,unit='GeV',label=self.XLABEL)
        self.addY(*self.YRANGE,unit='GeV',label=self.YLABEL)
        self.addMH(*self.XRANGE,unit='GeV',label='m_{a}')

    def _buildYModel(self,region='PP',**kwargs):
        tag = kwargs.pop('tag',region)

        cont1 = Models.Exponential('cont1',
            x = 'y',
            #lamb = [-0.20,-1,0], # kinfit
            lamb = [-0.1,-0.5,0], # visible
        )
        nameC1 = 'cont1{}'.format('_'+tag if tag else '')
        cont1.build(self.workspace,nameC1)

        # higgs fit (mmtt)
        if self.YRANGE[1]>100:
            erf1 = Models.Erf('erf1',
                x = 'y',
                erfScale = [0.01,0,1],
                erfShift = [100,0,1000],
            )
            nameE1 = 'erf1{}'.format('_'+tag if tag else '')
            erf1.build(self.workspace,nameE1)

            bg = Models.Prod('bg',
                nameE1,
                nameC1,
            )
        # pseudo fit (tt)
        else:
            erf1 = Models.Erf('erf1',
                x = 'y',
                erfScale = [0.01,0,1],
                erfShift = [1,0,20],
            )
            nameE1 = 'erf1{}'.format('_'+tag if tag else '')
            erf1.build(self.workspace,nameE1)

            erfc1 = Models.Prod('erfc1',
                nameE1,
                nameC1,
            )
            nameEC1 = 'erfc1{}'.format('_'+tag if tag else '')
            erfc1.build(self.workspace,nameEC1)

            # add a guassian summed for tt ?
            gaus1 = Models.Gaussian('gaus1',
                x = 'y',
                mean = [2,0,20],
                sigma = [0.1,0,2],
            )
            nameG1 = 'gaus1{}'.format('_'+tag if tag else '')
            gaus1.build(self.workspace,nameG1)

            bg = Models.Sum('bg',
                **{ 
                    nameEC1    : [0.5,0,1],
                    nameG1     : [0.5,0,1],
                    'recursive': True,
                }
            )

        name = 'bg_{}'.format(region)
        bg.build(self.workspace,name)

    def _buildXModel(self,region='PP',**kwargs):
        super(HaaLimits2D,self).buildModel(region)

    def buildModel(self,region='PP',**kwargs):
        tag = kwargs.pop('tag',region)

        # build the x variable
        self._buildXModel(region+'_x')

        # build the y variable
        self._buildYModel(region+'_y')

        # the 2D model
        bg = Models.Prod('bg',
            'bg_{}_x'.format(region),
            'bg_{}_y'.format(region),
        )

        name = 'bg_{}'.format(region)
        bg.build(self.workspace,name)


    def buildSpline(self,h,region='PP',shift=''):
        '''
        Get the signal spline for a given Higgs mass.
        Required arguments:
            h = higgs mass
        '''
        histMap = self.histMap[region][shift]
        tag= '{}{}'.format(region,'_'+shift if shift else '')
        # initial fit
        results = {}
        errors = {}
        results[h] = {}
        errors[h] = {}
        for a in self.AMASSES:
            ws = ROOT.RooWorkspace('sig')
            ws.factory('x[{0}, {1}]'.format(*self.XRANGE))
            ws.var('x').setUnit('GeV')
            ws.var('x').setPlotLabel(self.XLABEL)
            ws.var('x').SetTitle(self.XLABEL)
            ws.factory('y[{0}, {1}]'.format(*self.YRANGE))
            ws.var('y').setUnit('GeV')
            ws.var('y').setPlotLabel(self.YLABEL)
            ws.var('y').SetTitle(self.YLABEL)
            modelx = Models.Voigtian('sigx',
                mean  = [a,0,30],
                width = [0.01*a,0.001,5],
                sigma = [0.01*a,0.001,5],
            )
            modelx.build(ws, 'sigx')
            modely = Models.Voigtian('sigy',
                x = 'y',
                #mean  = [h,0.75*h,1.25*h], # kinfit
                mean  = [0.75*h,0,1.25*h], # visible
                width = [0.1*h,0.1,0.5*h],
                sigma = [0.1*h,0.1,0.5*h],
            )
            modely.build(ws, 'sigy')
            model = Models.Prod('sig',
                'sigx',
                'sigy',
            )
            model.build(ws, 'sig')
            hist = histMap[self.SIGNAME.format(h=h,a=a)]
            results[h][a], errors[h][a] = model.fit2D(ws, hist, 'h{}_a{}_{}'.format(h,a,tag), saveDir=self.plotDir, save=True, doErrors=True)
            print h, a, results[h][a], errors[h][a]
    
        models = {
            'xmean' : Models.Chebychev('xmean',  order = 1, p0 = [0,-1,1], p1 = [0.1,-1,1], p2 = [0.03,-1,1]),
            'xwidth': Models.Chebychev('xwidth', order = 1, p0 = [0,-1,1], p1 = [0.1,-1,1], p2 = [0.03,-1,1]),
            'xsigma': Models.Chebychev('xsigma', order = 1, p0 = [0,-1,1], p1 = [0.1,-1,1], p2 = [0.03,-1,1]),
            'ymean' : Models.Chebychev('ymean',  order = 1, p0 = [0,-1,1], p1 = [0.1,-1,1], p2 = [0.03,-1,1], x = 'y'),
            'ywidth': Models.Chebychev('ywidth', order = 3, p0 = [0,-1,1], p1 = [0.1,-1,1], p2 = [0.03,-1,1], x = 'y'),
            'ysigma': Models.Chebychev('ysigma', order = 1, p0 = [0,-1,1], p1 = [0.1,-1,1], p2 = [0.03,-1,1], x = 'y'),
        }
    
        for param in ['mean', 'width', 'sigma']:
            ws = ROOT.RooWorkspace(param)
            ws.factory('x[{},{}]'.format(*self.XRANGE))
            ws.var('x').setUnit('GeV')
            ws.var('x').setPlotLabel(self.XLABEL)
            ws.var('x').SetTitle(self.XLABEL)
            model = models['x'+param]
            model.build(ws, 'x'+param)
            name = '{}_{}{}'.format('x'+param,h,tag)
            hist = ROOT.TH1D(name, name, len(self.AMASSES), 4, 22)
            vals = [results[h][a]['{}_sigx'.format(param)] for a in self.AMASSES]
            errs = [errors[h][a]['{}_sigx'.format(param)] for a in self.AMASSES]
            for i,a in enumerate(self.AMASSES):
                b = hist.FindBin(a)
                hist.SetBinContent(b,vals[i])
                hist.SetBinError(b,errs[i])
            model.fit(ws, hist, name, saveDir=self.plotDir, save=True)
    
            ws = ROOT.RooWorkspace(param)
            ws.factory('y[{},{}]'.format(*self.YRANGE))
            ws.var('y').setUnit('GeV')
            ws.var('y').setPlotLabel(self.YLABEL)
            ws.var('y').SetTitle(self.YLABEL)
            model = models['y'+param]
            model.build(ws, 'y'+param)
            name = '{}_{}{}'.format('y'+param,h,tag)
            hist = ROOT.TH1D(name, name, len(self.AMASSES), 4, 22)
            vals = [results[h][a]['{}_sigy'.format(param)] for a in self.AMASSES]
            errs = [errors[h][a]['{}_sigy'.format(param)] for a in self.AMASSES]
            for i,a in enumerate(self.AMASSES):
                b = hist.FindBin(a)
                hist.SetBinContent(b,vals[i])
                hist.SetBinError(b,errs[i])
            model.fit(ws, hist, name, saveDir=self.plotDir, save=True)
    
        # create model
        for a in self.AMASSES:
            print h, a, results[h][a]
        modelx = Models.VoigtianSpline(self.SPLINENAME.format(h=h)+'_x',
            **{
                'masses' : self.AMASSES,
                'means'  : [results[h][a]['mean_sigx'] for a in self.AMASSES],
                'widths' : [results[h][a]['width_sigx'] for a in self.AMASSES],
                'sigmas' : [results[h][a]['sigma_sigx'] for a in self.AMASSES],
            }
        )
        modelx.build(self.workspace,'{}_{}'.format(self.SPLINENAME.format(h=h),tag+'_x'))
        modely = Models.VoigtianSpline(self.SPLINENAME.format(h=h)+'_y',
            **{
                'x'      : 'y',
                'masses' : self.AMASSES,
                'means'  : [results[h][a]['mean_sigy'] for a in self.AMASSES],
                'widths' : [results[h][a]['width_sigy'] for a in self.AMASSES],
                'sigmas' : [results[h][a]['sigma_sigy'] for a in self.AMASSES],
            }
        )
        modely.build(self.workspace,'{}_{}'.format(self.SPLINENAME.format(h=h),tag+'_y'))
        model = Models.ProdSpline(self.SPLINENAME.format(h=h),
            '{}_{}'.format(self.SPLINENAME.format(h=h),tag+'_x'),
            '{}_{}'.format(self.SPLINENAME.format(h=h),tag+'_y'),
        )

        if self.binned:
            integrals = [histMap[self.SIGNAME.format(h=h,a=a)].Integral() for a in self.AMASSES]
        else:
            integrals = [histMap[self.SIGNAME.format(h=h,a=a)].sumEntries('x>{} && x<{} && y>{} && y<{}'.format(*self.XRANGE+self.YRANGE)) for a in self.AMASSES]
        print 'Integrals', tag, h, integrals
        model.setIntegral(self.AMASSES,integrals)
        model.build(self.workspace,'{}_{}'.format(self.SPLINENAME.format(h=h),tag))
        model.buildIntegral(self.workspace,'integral_{}_{}'.format(self.SPLINENAME.format(h=h),tag))

    def fitBackground(self,region='PP',shift=''):
        model = self.workspace.pdf('bg_{}'.format(region))
        name = 'data_prefit_{}{}'.format(region,'_'+shift if shift else '')
        hist = self.histMap[region][shift]['dataNoSig']
        if self.binned:
            data = ROOT.RooDataHist(name,name,ROOT.RooArgList(self.workspace.var('x'),self.workspace.var('y')),hist)
        else:
            data = hist.Clone(name)

        fr = model.fitTo(data,ROOT.RooFit.Save(),ROOT.RooFit.SumW2Error(True))

        xFrame = self.workspace.var('x').frame()
        data.plotOn(xFrame)
        # continuum
        model.plotOn(xFrame,ROOT.RooFit.Components('cont1_{}_x'.format(region)),ROOT.RooFit.LineStyle(ROOT.kDashed))
        model.plotOn(xFrame,ROOT.RooFit.Components('cont2_{}_x'.format(region)),ROOT.RooFit.LineStyle(ROOT.kDashed))
        if self.XRANGE[0]<4:
            # extended continuum when also fitting jpsi
            model.plotOn(xFrame,ROOT.RooFit.Components('cont3_{}_x'.format(region)),ROOT.RooFit.LineStyle(ROOT.kDashed))
            model.plotOn(xFrame,ROOT.RooFit.Components('cont4_{}_x'.format(region)),ROOT.RooFit.LineStyle(ROOT.kDashed))
            # jpsi
            model.plotOn(xFrame,ROOT.RooFit.Components('jpsi1S'),ROOT.RooFit.LineColor(ROOT.kGreen))
            model.plotOn(xFrame,ROOT.RooFit.Components('jpsi2S'),ROOT.RooFit.LineColor(ROOT.kGreen))
        # upsilon
        model.plotOn(xFrame,ROOT.RooFit.Components('upsilon1S'),ROOT.RooFit.LineColor(ROOT.kRed))
        model.plotOn(xFrame,ROOT.RooFit.Components('upsilon2S'),ROOT.RooFit.LineColor(ROOT.kRed))
        model.plotOn(xFrame,ROOT.RooFit.Components('upsilon3S'),ROOT.RooFit.LineColor(ROOT.kRed))
        # combined model
        model.plotOn(xFrame)

        canvas = ROOT.TCanvas('c','c',800,800)
        xFrame.Draw()
        #canvas.SetLogy()
        canvas.Print('{}/model_fit_{}{}_xproj.png'.format(self.plotDir,region,'_'+shift if shift else ''))

        yFrame = self.workspace.var('y').frame()
        data.plotOn(yFrame)
        # continuum
        model.plotOn(yFrame,ROOT.RooFit.Components('cont1_{}_y'.format(region)),ROOT.RooFit.LineStyle(ROOT.kDashed))
        # combined model
        model.plotOn(yFrame)

        canvas = ROOT.TCanvas('c','c',800,800)
        yFrame.Draw()
        #canvas.SetLogy()
        canvas.Print('{}/model_fit_{}{}_yproj.png'.format(self.plotDir,region,'_'+shift if shift else ''))

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
                    integral = h.Integral() # 2D integral?
                else:
                    integral = h.sumEntries('x>{} && x<{} && y>{} && y<{}'.format(*self.XRANGE+self.YRANGE))
                data_obs = model.generate(ROOT.RooArgSet(self.workspace.var('x'),self.workspace.var('y')),int(integral))
                if addSignal:
                    self.workspace.var('MH').setVal(ma)
                    model = self.workspace.pdf('{}_{}'.format(self.SPLINENAME.format(h=mh),region))
                    integral = self.workspace.function('integral_{}_{}'.format(self.SPLINENAME.format(h=mh),region)).getVal()
                    sig_obs = model.generate(ROOT.RooArgSet(self.workspace.var('x'),self.workspace.var('y')),int(integral))
                    data_obs.append(sig_obs)
                data_obs.SetName(name)
            else:
                # use the provided data
                if self.binned:
                    data_obs = ROOT.RooDataHist(name,name,ROOT.RooArgList(self.workspace.var('x'),self.workspace.var('y')),self.histMap[region]['']['data'])
                else:
                    data_obs = hist.Clone(name)
            self.wsimport(data_obs)

    def addBackgroundModels(self):
        for region in self.REGIONS:
            self.buildModel(region=region)
            self.workspace.factory('bg_{}_norm[1,0,2]'.format(region))
            self.fitBackground(region=region)

    def addSignalModels(self):
        for region in self.REGIONS:
            for shift in ['']+self.SHIFTS:
                for h in self.HMASSES:
                    self.buildSpline(h,region=region,shift=shift)
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
                integral = h.Integral() # 2D restricted integral?
            else:
                integral = h.sumEntries('x>{} && x<{} && y>{} && y<{}'.format(*self.XRANGE+self.YRANGE))
            self.setExpected('bg',region,integral)

            for proc in [self.SPLINENAME.format(h=h) for h in self.HMASSES]:
                self.setExpected(proc,region,1) # TODO: how to handle different integrals
                self.addRateParam('integral_{}_{}'.format(proc,region),region,proc)
                
            self.setObserved(region,-1) # reads from histogram

            

    ###################
    ### Systematics ###
    ###################
    def addSystematics(self):
        self.sigProcesses = tuple([self.SPLINENAME.format(h=h) for h in self.HMASSES])
        self._addLumiSystematic()
        self._addMuonSystematic()
        self._addTauSystematic()

    ###################################
    ### Save workspace and datacard ###
    ###################################
    def save(self,name='mmmt'):
        processes = {}
        for h in self.HMASSES:
            processes[self.SIGNAME.format(h=h,a='X')] = [self.SPLINENAME.format(h=h)] + ['bg']
        self.printCard('datacards_shape/MuMuTauTau/{}'.format(name),processes=processes,blind=False,saveWorkspace=True)


