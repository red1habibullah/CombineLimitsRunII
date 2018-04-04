import os
import sys
import logging
import itertools
import numpy as np
import argparse
import math
import errno
import array

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.SetBatch()

import CombineLimits.Limits.Models as Models
from CombineLimits.Limits.Limits import Limits
from CombineLimits.HaaLimits.HaaLimits import HaaLimits
from CombineLimits.Limits.utilities import *

class HaaLimitsHMass(HaaLimits):
    '''
    Create the Haa Limits workspace
    '''

    SPLINENAME = 'sig{a}'

    XRANGE = [50,1000]
    XLABEL = 'm_{#mu#mu#tau_{#mu}#tau_{h}}'

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
        super(HaaLimitsHMass,self).__init__(histMap)

        self.plotDir = 'figures/HaaLimitsHMass{}'.format('_'+tag if tag else '')
        python_mkdir(self.plotDir)


    ###########################
    ### Workspace utilities ###
    ###########################
    def initializeWorkspace(self):
        self.addX(*self.XRANGE,unit='GeV',label=self.XLABEL)
        self.addMH(*self.XRANGE,unit='GeV',label='m_{h}')

    def buildModel(self,region='PP',**kwargs):
        tag = kwargs.pop('tag',region)
    
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
        bg = Models.Sum('bg',
            **{
                #nameC : [0.1,0,1],
                nameC1: [0.5,0,1],
                nameC2: [0.7,0,1],
                'recursive' : True,
            }
        )
        name = 'bg_{}'.format(region)
        bg.build(self.workspace,name)


    def buildSpline(self,a,region='PP',shift=''):
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
        results[a] = {}
        errors[a] = {}
        for h in self.HMASSES:
            ws = ROOT.RooWorkspace('sig')
            ws.factory('x[{0}, {1}]'.format(*self.XRANGE))
            ws.var('x').setUnit('GeV')
            ws.var('x').setPlotLabel(self.XLABEL)
            ws.var('x').SetTitle(self.XLABEL)
            model = Models.Voigtian('sig',
                mean  = [h,0,1000],
                width = [0.1*h,0,0.5*h],
                sigma = [0.1*h,0,0.5*h],
            )
            model.build(ws, 'sig')
            hist = histMap[self.SIGNAME.format(h=h,a=a)]
            results[a][h], errors[a][h] = model.fit(ws, hist, 'h{}_a{}_{}'.format(h,a,tag), saveDir=self.plotDir, save=True, doErrors=True)
    
        models = {
            'mean' : Models.Chebychev('mean',  order = 1, p0 = [1,-5,50], p1 = [0.1,-5,5], p2 = [0.03,-5,5]),
            'width': Models.Chebychev('width', order = 1, p0 = [1,-5,50], p1 = [0.1,-5,5], p2 = [0.03,-5,5]),
            'sigma': Models.Chebychev('sigma', order = 1, p0 = [1,-5,50], p1 = [0.1,-5,5], p2 = [0.03,-5,5]),
        }
    
        for param in ['mean', 'width', 'sigma']:
            ws = ROOT.RooWorkspace(param)
            ws.factory('x[{},{}]'.format(*self.XRANGE))
            ws.var('x').setUnit('GeV')
            ws.var('x').setPlotLabel(self.XLABEL)
            ws.var('x').SetTitle(self.XLABEL)
            model = models[param]
            model.build(ws, param)
            name = '{}_{}{}'.format(param,a,tag)
            bins = [50,200,400,1000]
            hist = ROOT.TH1D(name, name, len(bins)-1, array.array('d',bins))
            vals = [results[a][h]['{}_h{}_a{}_{}'.format(param,h,a,tag)] for h in self.HMASSES]
            errs = [errors[a][h]['{}_h{}_a{}_{}'.format(param,h,a,tag)] for h in self.HMASSES]
            for i,h in enumerate(self.HMASSES):
                b = hist.FindBin(h)
                hist.SetBinContent(b,vals[i])
                hist.SetBinError(b,errs[i])
            model.fit(ws, hist, name, saveDir=self.plotDir, save=True)
    
        # create model
        for h in self.HMASSES:
            print h, a, results[a][h]
        model = Models.VoigtianSpline(self.SPLINENAME.format(a=a),
            **{
                'masses' : self.HMASSES,
                'means'  : [results[a][h]['mean_h{0}_a{1}_{2}'.format(h,a,tag)] for h in self.HMASSES],
                'widths' : [results[a][h]['width_h{0}_a{1}_{2}'.format(h,a,tag)] for h in self.HMASSES],
                'sigmas' : [results[a][h]['sigma_h{0}_a{1}_{2}'.format(h,a,tag)] for h in self.HMASSES],
            }
        )
        integrals = [histMap[self.SIGNAME.format(h=h,a=a)].Integral() for h in self.HMASSES]
        model.setIntegral(self.HMASSES,integrals)
        model.build(self.workspace,'{}_{}'.format(self.SPLINENAME.format(a=a),tag))
        model.buildIntegral(self.workspace,'integral_{}_{}'.format(self.SPLINENAME.format(a=a),tag))

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
    def addSignalModels(self):
        for region in self.REGIONS:
            for shift in ['']+self.SHIFTS:
                for a in self.AMASSES:
                    self.buildSpline(a,region=region,shift=shift)
            self.workspace.factory('{}_{}_norm[1,0,9999]'.format(self.SPLINENAME.format(a=a),region))

    ######################
    ### Setup datacard ###
    ######################
    def setupDatacard(self):

        # setup bins
        for region in self.REGIONS:
            self.addBin(region)

        # add processes
        self.addProcess('bg')

        for proc in [self.SPLINENAME.format(a=a) for a in self.AMASSES]:
            self.addProcess(proc,signal=True)

        # set expected
        for region in self.REGIONS:
            h = self.histMap[region]['']['dataNoSig']
            integral = h.Integral(h.FindBin(self.XRANGE[0]),h.FindBin(self.XRANGE[1]))
            self.setExpected('bg',region,integral)

            for proc in [self.SPLINENAME.format(a=a) for a in self.AMASSES]:
                self.setExpected(proc,region,1) # TODO: how to handle different integrals
                self.addRateParam('integral_{}_{}'.format(proc,region),region,proc)
                
            self.setObserved(region,-1) # reads from histogram

            

    ###################
    ### Systematics ###
    ###################
    def addSystematics(self):
        self.sigProcesses = tuple([self.SPLINENAME.format(a=a) for a in self.AMASSES])
        self._addLumiSystematic()
        self._addMuonSystematic()
        self._addTauSystematic()
        
    ###################################
    ### Save workspace and datacard ###
    ###################################
    def save(self,name='mmmt'):
        processes = {}
        for a in self.AMASSES:
            processes[self.SIGNAME.format(h='X',a=a)] = [self.SPLINENAME.format(a=a)] + ['bg']
        self.printCard('datacards_shape/MuMuTauTau/{}'.format(name),processes=processes,blind=False,saveWorkspace=True)


