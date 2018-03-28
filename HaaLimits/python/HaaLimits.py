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
from CombineLimits.Limits.utilities import *

class HaaLimits(Limits):
    '''
    Create the Haa Limits workspace
    '''

    # permanent parameters
    HMASSES = [125,300,750]
    AMASSES = [5,7,9,11,13,15,17,19,21]

    SIGNAME = 'HToAAH{h}A{a}'
    SPLINENAME = 'sig{h}'

    XRANGE = [4,25]

    REGIONS = ['FP','PP']
    SHIFTS = []

    def __init__(self,histMap):
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

        self.plotDir = 'figures/HaaLimits'
        python_mkdir(self.plotDir)


    ###########################
    ### Workspace utilities ###
    ###########################
    def initializeWorkspace(self):
        self.addX(*self.XRANGE,unit='GeV',label='m_{#mu#mu}')
        self.addMH(*self.XRANGE,unit='GeV',label='m_{a}')

    def buildModel(self,region='PP',**kwargs):
        tag = kwargs.pop('tag',region)
    
        # jpsi
        jpsi1S = Models.Voigtian('jpsi1S',
            mean  = [3.1,2.9,3.2],
            sigma = [0.1,0,1],
            width = [0.1,0.01,1],
        )
        #nameJ1 = 'jpsi1S{}'.format('_'+tag if tag else '')
        nameJ1 = 'jpsi1S'
        jpsi1S.build(self.workspace,nameJ1)
    
        jpsi2S = Models.Gaussian('jpsi2S',
            mean  = [3.7,3.6,3.8],
            sigma = [0.1,0.01,1],
            width = [0.1,0.01,1],
        )
        #nameJ2 = 'jpsi2S{}'.format('_'+tag if tag else '')
        nameJ2 = 'jpsi2S'
        jpsi2S.build(self.workspace,nameJ2)
    
        #jpsi = Models.Sum('jpsi',
        #    **{
        #        nameJ1 : [0.5,0,1] if tag=='PP' else [0.5,0,1],
        #        nameJ2 : [0.6,0,1] if tag=='PP' else [0.2,0,1],
        #        'recursive' : True,
        #    }
        #)
        ##nameJ = 'jpsi{}'.format('_'+tag if tag else '')
        #nameJ= 'jpsi'
        #jpsi.build(self.workspace,nameJ)
    
        # upsilon
        upsilon1S = Models.Gaussian('upsilon1S',
            mean  = [9.5,9.3,9.7],
            sigma = [0.1,0.01,0.3],
        )
        #nameU1 = 'upsilon1S{}'.format('_'+tag if tag else '')
        nameU1 = 'upsilon1S'
        upsilon1S.build(self.workspace,nameU1)
    
        upsilon2S = Models.Gaussian('upsilon2S',
            mean  = [10.0,9.8,10.2],
            sigma = [0.1,0.01,0.3],
        )
        #nameU2 = 'upsilon2S{}'.format('_'+tag if tag else '')
        nameU2 = 'upsilon2S'
        upsilon2S.build(self.workspace,nameU2)
    
        upsilon3S = Models.Gaussian('upsilon3S',
            mean  = [10.3,10.2,10.5],
            sigma = [0.1,0.02,0.3],
        )
        #nameU3 = 'upsilon3S{}'.format('_'+tag if tag else '')
        nameU3 = 'upsilon3S'
        upsilon3S.build(self.workspace,nameU3)
    
        #upsilon = Models.Sum('upsilon',
        #    **{
        #        nameU1 : [0.43,0,1],
        #        nameU2 : [0.20,0,1],
        #        nameU3 : [1,0,1],
        #        'recursive' : True,
        #    }
        #)
        ##nameU = 'upsilon{}'.format('_'+tag if tag else '')
        #nameU= 'upsilon'
        #upsilon.build(self.workspace,nameU)
    
        # continuum background
        cont = Models.Chebychev('cont',
            order = 2,
            p0 = [-1,-1.4,0],
            p1 = [0.25,0,0.5],
            p2 = [0.03,-1,1],
        )
        nameC = 'cont{}'.format('_'+tag if tag else '')
        cont.build(self.workspace,nameC)
    
        cont1 = Models.Exponential('cont1',
            lamb = [-0.20,-1,0],
        )
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
    
        #cont = Models.Sum('cont',
        #    **{
        #        nameC1 : [0.95,0,1],
        #        nameC2 : [0.05,0,1],
        #        'recursive' : True,
        #    }
        #)
        #nameC = 'cont{}'.format('_'+tag if tag else '')
        #cont.build(self.workspace,nameC)
    
        # sum
        if self.XRANGE[0]<4 and self.XRANGE[1]>10:
            # jpsi and upsilon
            bg = Models.Sum('bg',
                **{
                    #nameC : [0.1,0,1],
                    nameC1: [0.2,0,1],
                    nameC2: [0.5,0,1],
                    nameC3: [0.8,0,1],
                    #nameC4: [0.1,0,1],
                    #nameJ : [0.9,0,1],
                    nameJ1: [0.9,0,1],
                    nameJ2: [0.9,0,1],
                    #nameU : [0.1,0,1],
                    nameU1: [0.1,0,1],
                    nameU2: [0.1,0,1],
                    nameU3: [0.1,0,1],
                    'recursive' : True,
                }
            )
        elif self.XRANGE[0]<4:
            # only jpsi
            bg = Models.Sum('bg',
                **{
                    #nameC : [0.1,0,1],
                    nameC3: [0.1,0,1],
                    nameC2: [0.1,0,1],
                    #nameJ : [0.9,0,1],
                    nameJ1: [0.9,0,1],
                    nameJ2: [0.9,0,1],
                    'recursive' : True,
                }
            )
        else:
            # only upsilon
            bg = Models.Sum('bg',
                **{
                    #nameC : [0.1,0,1],
                    nameC1: [0.5,0,1],
                    nameC2: [0.7,0,1],
                    #nameU : [0.5,0,1],
                    nameU1: [0.5,0,1],
                    nameU2: [0.5,0,1],
                    nameU3: [0.5,0,1],
                    'recursive' : True,
                }
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
            ws.var('x').setPlotLabel('m_{#mu#mu}')
            ws.var('x').SetTitle('m_{#mu#mu}')
            model = Models.Voigtian('sig',
                mean  = [a,0,30],
                width = [0.01*a,0,5],
                sigma = [0.01*a,0,5],
            )
            model.build(ws, 'sig')
            hist = histMap[self.SIGNAME.format(h=h,a=a)]
            results[h][a], errors[h][a] = model.fit(ws, hist, 'h{}_a{}_{}'.format(h,a,tag), saveDir=self.plotDir, save=True, doErrors=True)
    
        models = {
            'mean' : Models.Chebychev('mean',  order = 1, p0 = [0,-1,1], p1 = [0.1,-1,1], p2 = [0.03,-1,1]),
            'width': Models.Chebychev('width', order = 1, p0 = [0,-1,1], p1 = [0.1,-1,1], p2 = [0.03,-1,1]),
            'sigma': Models.Chebychev('sigma', order = 1, p0 = [0,-1,1], p1 = [0.1,-1,1], p2 = [0.03,-1,1]),
        }
    
        for param in ['mean', 'width', 'sigma']:
            ws = ROOT.RooWorkspace(param)
            ws.factory('x[{},{}]'.format(*self.XRANGE))
            ws.var('x').setUnit('GeV')
            ws.var('x').setPlotLabel('m_{#mu#mu}')
            ws.var('x').SetTitle('m_{#mu#mu}')
            model = models[param]
            model.build(ws, param)
            name = '{}_{}{}'.format(param,h,tag)
            hist = ROOT.TH1D(name, name, len(self.AMASSES), 4, 22)
            vals = [results[h][a]['{}_h{}_a{}_{}'.format(param,h,a,tag)] for a in self.AMASSES]
            errs = [errors[h][a]['{}_h{}_a{}_{}'.format(param,h,a,tag)] for a in self.AMASSES]
            for i,a in enumerate(self.AMASSES):
                b = hist.FindBin(a)
                hist.SetBinContent(b,vals[i])
                hist.SetBinError(b,errs[i])
            model.fit(ws, hist, name, saveDir=self.plotDir, save=True)
    
        # create model
        for a in self.AMASSES:
            print h, a, results[h][a]
        model = Models.VoigtianSpline(self.SPLINENAME.format(h=h),
            **{
                'masses' : self.AMASSES,
                'means'  : [results[h][a]['mean_h{0}_a{1}_{2}'.format(h,a,tag)] for a in self.AMASSES],
                'widths' : [results[h][a]['width_h{0}_a{1}_{2}'.format(h,a,tag)] for a in self.AMASSES],
                'sigmas' : [results[h][a]['sigma_h{0}_a{1}_{2}'.format(h,a,tag)] for a in self.AMASSES],
            }
        )
        integrals = [histMap[self.SIGNAME.format(h=h,a=a)].Integral() for a in self.AMASSES]
        model.setIntegral(self.AMASSES,integrals)
        model.build(self.workspace,'{}_{}'.format(self.SPLINENAME.format(h=h),tag))

    def fitBackground(self,region='PP',shift=''):
        model = self.workspace.pdf('bg_{}'.format(region))
        name = 'data_prefit_{}{}'.format(region,'_'+shift if shift else '')
        data = ROOT.RooDataHist(name,name,ROOT.RooArgList(self.workspace.var('x')),self.histMap[region][shift]['dataNoSig'])

        fr = model.fitTo(data,ROOT.RooFit.Save(),ROOT.RooFit.SumW2Error(True))

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
    def addData(self):
        for region in self.REGIONS:
            name = 'data_obs_{}'.format(region)
            data_obs = ROOT.RooDataHist(name,name,ROOT.RooArgList(self.workspace.var('x')),self.histMap[region]['']['data'])
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
            integral = h.Integral(h.FindBin(self.XRANGE[0]),h.FindBin(self.XRANGE[1]))
            self.setExpected('bg',region,integral)

            for proc in [self.SPLINENAME.format(h=h) for h in self.HMASSES]:
                self.setExpected(proc,region,1) # TODO: how to handle different integrals
                
            self.setObserved(region,-1) # reads from histogram

            

    ###################
    ### Systematics ###
    ###################
    def addSystematics(self):
        self._addLumiSystematic()

    def _addLumiSystematic(self):
        # lumi: 2.5% 2016
        lumiproc = tuple([self.SPLINENAME.format(h=h) for h in self.HMASSES])
        lumisyst = {
            (lumiproc,tuple(self.REGIONS)) : 1.025,
        }
        self.addSystematic('lumi','lnN',systematics=lumisyst)
        
    ###################################
    ### Save workspace and datacard ###
    ###################################
    def save(self,name='mmmt'):
        processes = {}
        for h in self.HMASSES:
            processes[self.SIGNAME.format(h=h,a='X')] = [self.SPLINENAME.format(h=h)] + ['bg']
        self.printCard('datacards_shape/MuMuTauTau/{}'.format(name),processes=processes,blind=False,saveWorkspace=True)


