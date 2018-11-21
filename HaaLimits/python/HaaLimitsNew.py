import os
import sys
import logging
import itertools
import numpy as np
import argparse
import math
import errno
import json
import pickle
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
    SPLINERANGE = [3.6,21]

    XRANGE = [4,25]
    XBINNING = 210
    XLABEL = 'm_{#mu#mu}'
    UPSILONRANGE = [7, 12]

    REGIONS = ['PP','FP']
    #REGIONS = ['PP']
    SHIFTS = []
    BACKGROUNDSHIFTS = []
    SIGNALSHIFTS = []
    QCDSHIFTS = [] # note, max/min of all (excluding 0.5/2)


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

        self.binned = self.histMap[self.histMap.keys()[0]]['']['data'].InheritsFrom('TH1')

        self.plotDir = 'figures/HaaLimits{}'.format('_'+tag if tag else '')
        self.fitsDir = 'fitParams/HaaLimits{}'.format('_'+tag if tag else '')

    def dump(self,name,results):
        with open(name,'w') as f:
            f.write(json.dumps(results, indent=4, sort_keys=True))
        with open(name.replace('.json','.pkl'),'wb') as f:
            pickle.dump(results,f)

    def load(self,name):
        with open(name.replace('.json','.pkl'),'rb') as f:
            results = pickle.load(f)
        return results

    ###########################
    ### Workspace utilities ###
    ###########################
    def initializeWorkspace(self,**kwargs):
        logging.debug('initializeWorkspace')
        logging.debug(str(kwargs))
        self.addX(*self.XRANGE,unit='GeV',label=self.XLABEL,**kwargs)
        self.addMH(*self.SPLINERANGE,unit='GeV',label=self.SPLINELABEL,**kwargs)

    def buildModel(self, region='PP', **kwargs):
        logging.debug('buildModel')
        logging.debug(', '.join([region,str(kwargs)]))
        workspace = kwargs.pop('workspace',self.workspace)
        xVar = kwargs.pop('xVar','x')
        tag = kwargs.pop('tag',region)

        bgRes = Models.Voigtian
        #bgRes = Models.BreitWigner

        # jpsi
        nameJ1b = 'jpsi1S'
        workspace.factory('{0}[{1}, {2}, {3}]'.format('mean_{}'.format(nameJ1b), *[3.1,2.9,3.2]))
        workspace.factory('{0}[{1}, {2}, {3}]'.format('sigma_{}'.format(nameJ1b),*[0.1,0,0.5]))
        workspace.factory('{0}[{1}, {2}, {3}]'.format('width_{}'.format(nameJ1b),*[0.1,0.01,0.5]))
        jpsi1S = bgRes('jpsi1S',
            x = xVar,
            mean  = 'mean_{}'.format(nameJ1b),
            sigma = 'sigma_{}'.format(nameJ1b),
            width = 'width_{}'.format(nameJ1b),
        )
        nameJ1 = '{}{}'.format(nameJ1b,'_'+tag if tag else '')
        jpsi1S.build(workspace,nameJ1)
    
        nameJ2b = 'jpsi2S'
        workspace.factory('{0}[{1}, {2}, {3}]'.format('mean_{}'.format(nameJ2b), *[3.7,3.6,3.8]))
        workspace.factory('{0}[{1}, {2}, {3}]'.format('sigma_{}'.format(nameJ2b),*[0.1,0,0.5]))
        workspace.factory('{0}[{1}, {2}, {3}]'.format('width_{}'.format(nameJ2b),*[0.1,0.01,0.5]))
        jpsi2S = bgRes('jpsi2S',
            x = xVar,
            mean  = 'mean_{}'.format(nameJ2b),
            sigma = 'sigma_{}'.format(nameJ2b),
            width = 'width_{}'.format(nameJ2b),
        )
        nameJ2 = '{}{}'.format(nameJ2b,'_'+tag if tag else '')
        jpsi2S.build(workspace,nameJ2)


        if self.XRANGE[0]<3.3:
            #jpsi = {'extended': True}
            workspace.factory('{0}_frac[{1},{2},{3}]'.format(nameJ1b,*[0.9,0,1]))
            workspace.factory('{0}_frac[{1},{2},{3}]'.format(nameJ2b,*[0.1,0,1]))
            jpsi = {'recursive': True}
            jpsi[nameJ1] = '{}_frac'.format(nameJ1b)
            jpsi[nameJ2] = '{}_frac'.format(nameJ2b)
            jpsi = Models.Sum('jpsi', **jpsi)
            nameJ = 'jpsi{}'.format('_'+tag if tag else '')
            jpsi.build(workspace,nameJ)

        # upsilon
        nameU1b = 'upsilon1S'
        workspace.factory('{0}[{1}, {2}, {3}]'.format('mean_{}'.format(nameU1b), *[9.5,9.3,9.7]))
        workspace.factory('{0}[{1}, {2}, {3}]'.format('sigma_{}'.format(nameU1b),*[0.05,0,0.3]))
        workspace.factory('{0}[{1}, {2}, {3}]'.format('width_{}'.format(nameU1b),*[0.1,0.01,1]))
        upsilon1S = bgRes('upsilon1S',
            x = xVar,
            mean  = 'mean_{}'.format(nameU1b),
            sigma = 'sigma_{}'.format(nameU1b),
            width = 'width_{}'.format(nameU1b),
        )
        nameU1 = '{}{}'.format(nameU1b,'_'+tag if tag else '')
        upsilon1S.build(workspace,nameU1)
    
        nameU2b = 'upsilon2S'
        workspace.factory('{0}[{1}, {2}, {3}]'.format('mean_{}'.format(nameU2b), *[10.0,9.8,10.15]))
        workspace.factory('{0}[{1}, {2}, {3}]'.format('sigma_{}'.format(nameU2b),*[0.06,0,0.3]))
        workspace.factory('{0}[{1}, {2}, {3}]'.format('width_{}'.format(nameU2b),*[0.1,0.01,1]))
        upsilon2S = bgRes('upsilon2S',
            x = xVar,
            mean  = 'mean_{}'.format(nameU2b),
            sigma = 'sigma_{}'.format(nameU2b),
            width = 'width_{}'.format(nameU2b),
        )
        nameU2 = '{}{}'.format(nameU2b,'_'+tag if tag else '')
        upsilon2S.build(workspace,nameU2)
    
        nameU3b = 'upsilon3S'
        workspace.factory('{0}[{1}, {2}, {3}]'.format('mean_{}'.format(nameU3b), *[10.3,10.22,10.5]))
        workspace.factory('{0}[{1}, {2}, {3}]'.format('sigma_{}'.format(nameU3b),*[0.07,0,0.3]))
        workspace.factory('{0}[{1}, {2}, {3}]'.format('width_{}'.format(nameU3b),*[0.1,0.01,1]))
        upsilon3S = bgRes('upsilon3S',
            x = xVar,
            mean  = 'mean_{}'.format(nameU3b),
            sigma = 'sigma_{}'.format(nameU3b),
            width = 'width_{}'.format(nameU3b),
        )
        nameU3 = '{}{}'.format(nameU3b,'_'+tag if tag else '')
        upsilon3S.build(workspace,nameU3)

        #upsilon = {'recursive': True}
        #upsilon[nameU1] = [0.75,0,1]
        #upsilon[nameU2] = [0.5,0,1]
        #upsilon[nameU3] = [0.5,0,1]
        #upsilon = Models.Sum('upsilon', **upsilon)
        #nameU = 'upsilon_{}'.format(region)
        #upsilon.build(workspace,nameU)

        nameU23b = 'upsilon23'.format('_'+tag if tag else '')
        nameU23 = '{}{}'.format(nameU23b,'_'+tag if tag else '')
        workspace.factory('{0}_frac[{1},{2},{3}]'.format(nameU2b,*[0.5,0,1]))
        workspace.factory('{0}_frac[{1},{2},{3}]'.format(nameU3b,*[0.5,0,1]))
        #upsilon23 = {'extended': True}
        upsilon23 = {'recursive': True}
        upsilon23[nameU2] = '{}_frac'.format(nameU2b)
        upsilon23[nameU3] = '{}_frac'.format(nameU3b)
        upsilon23 = Models.Sum(nameU23, **upsilon23)
        upsilon23.build(workspace,nameU23)

        nameUb = 'upsilon'
        nameU = '{}{}'.format(nameUb,'_'+tag if tag else '')
        workspace.factory('{0}_frac[{1},{2},{3}]'.format(nameU1b,*[0.75,0,1]))
        workspace.factory('{0}_frac[{1},{2},{3}]'.format(nameU23b,*[0.5,0,1]))
        #upsilon = {'extended': True}
        upsilon = {'recursive': True}
        upsilon[nameU1]  = '{}_frac'.format(nameU1b)
        upsilon[nameU23] = '{}_frac'.format(nameU23b)
        upsilon = Models.Sum(nameU, **upsilon)
        upsilon.build(workspace,nameU)

        # sum upsilon and jpsi
        #nameR = 'resonant{}'.format('_'+tag if tag else '')
        ##resonant = {'extended': True}
        #resonant = {'recursive': True}
        #resonant[nameU]  = [0.75,0,1]
        #if self.XRANGE[0]<3.3:
        #    resonant[nameJ] = [0.5,0,1]
        #elif self.XRANGE[0]<4.0:
        #    resonant[nameJ2] = [0.5,0,1]
        #resonant = Models.Sum(nameR, **resonant)
        #resonant.build(workspace,nameR)


        # continuum background
        if self.XRANGE[0]<4:
            nameC1 = 'cont1{}'.format('_'+tag if tag else '')
            #nameC1 = 'cont1'
            cont1 = Models.Exponential(nameC1,
                x = xVar,
                lamb = kwargs.pop('lambda_{}'.format(nameC1),[-2,-4,0]),
            )
            cont1.build(workspace,nameC1)

            nameC2 = 'cont2{}'.format('_'+tag if tag else '')
            #nameC2 = 'cont2'
            cont2 = Models.Exponential(nameC2,
                x = xVar,
                lamb = kwargs.pop('lambda_{}'.format(nameC2),[-0.75,-5,0]),
            )
            cont2.build(workspace,nameC2)

            nameC = 'cont{}'.format('_'+tag if tag else '')
            #cont = {'extended': True}
            cont = {'recursive': True}
            cont[nameC1] = [0.75,0,1]
            cont[nameC2] = [0.5,0,1]
            cont = Models.Sum(nameC, **cont)
            cont.build(workspace,nameC)
        else:
            nameC = 'cont{}'.format('_'+tag if tag else '')
            #nameC = 'cont'
            cont = Models.Exponential(nameC,
                x = xVar,
                lamb = kwargs.pop('lambda_{}'.format(nameC),[-2,-4,0]),
            )
            cont.build(workspace,nameC)
    
        # sum
        bgs = {'recursive': True}
        # continuum background
        # TODO, this was bugged, need to fix
        #bgs[nameC1] = [0.5,0,1]
        #bgs[nameC2] = [0.5,0,1]
        bgs[nameC] = [0.5,0,1]
        if self.XRANGE[0]<4 and self.XRANGE[1]>=11:
            bgs[nameJ] = [0.9,0,1]
            bgs[nameU] = [0.9,0,1]
        else:
            # jpsi
            if self.XRANGE[0]<3.3:
                bgs[nameJ] = [0.9,0,1]
            elif self.XRANGE[0]<4:
                bgs[nameJ2] = [0.9,0,1]
            # upsilon
            elif self.XRANGE[0]<=9 and self.XRANGE[1]>=11:
                bgs[nameU] = [0.9,0,1]
        bg = Models.Sum('bg', **bgs)
        name = 'bg_{}'.format(region)
        bg.build(workspace,name)

    def loadSignalFits(self, h, tag, region, shift=''):
        savedir = '{}/{}'.format(self.fitsDir,shift if shift else 'central')
        savename = '{}/h{}_{}.json'.format(savedir,h,tag)
        results = self.load(savename)
        vals = results['vals']
        errs = results['errs']
        ints = results['integrals']
        return vals, errs, ints

    def fitSignal(self,h,a,region='PP',shift='',**kwargs):
        scaleLumi = kwargs.get('scaleLumi',1)
        results = kwargs.get('results',{})
        histMap = self.histMap[region][shift]
        tag = '{}{}'.format(region,'_'+shift if shift else '')

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
        name = 'h{}_a{}_{}'.format(h,a,tag)
        model.build(ws, name)
        if results:
            for param in results:
                ws.var(param+'_{}'.format(shift) if shift else param).setVal(results[param])
        hist = histMap[self.SIGNAME.format(h=h,a=a)]
        saveDir = '{}/{}'.format(self.plotDir,shift if shift else 'central')
        results, errors = model.fit(ws, hist, name, saveDir=saveDir, save=True, doErrors=True)
        if self.binned:
            integral = histMap[self.SIGNAME.format(h=h,a=a)].Integral() * scaleLumi
        else:
            integral = histMap[self.SIGNAME.format(h=h,a=a)].sumEntries('x>{} && x<{}'.format(*self.XRANGE)) * scaleLumi

        savedir = '{}/{}'.format(self.fitsDir,shift if shift else 'central')
        python_mkdir(savedir)
        savename = '{}/h{}_a{}_{}.json'.format(savedir,h,a,tag)
        jsonData = {'vals': results, 'errs': errors, 'integrals': integral}
        self.dump(savename,jsonData)

        return results, errors, integral
        

    def fitSignals(self,h,region='PP',shift='',**kwargs):
        '''
        Fit the signal model for a given Higgs mass.
        Required arguments:
            h = higgs mass
        '''
        scaleLumi = kwargs.get('scaleLumi',1)
        fit = kwargs.get('fit',False)      # will fit the spline parameters rather than a simple spline
        load = kwargs.get('load',False)
        skipFit = kwargs.get('skipFit',False)
        amasses = self.AMASSES
        if h>125: amasses = [a for a in amasses if a not in ['3p6',4,6]]
        avals = [float(str(x).replace('p','.')) for x in amasses]
        histMap = self.histMap[region][shift]
        tag= '{}{}'.format(region,'_'+shift if shift else '')

        # initial fit
        if load:
            # load the previous fit
            results, errors, integrals = self.loadSignalFits(h,tag,region,shift)
        elif shift and not skipFit:
            # load the central fits
            results, errors, integrals = self.loadSignalFits(h,region,region)
        else:
            results = {}
            errors = {}
            integrals = {}
            results[h] = {}
            errors[h] = {}
            integrals[h] = {}
        for a in amasses:
            if load or (shift and not skipFit):
                results[h][a], errors[h][a], integrals[h][a] = self.fitSignal(h,a,region,shift,results=results[h][a],**kwargs)
            elif not skipFit:
                results[h][a], errors[h][a], integrals[h][a] = self.fitSignal(h,a,region,shift,**kwargs)
    
        savedir = '{}/{}'.format(self.fitsDir,shift if shift else 'central')
        python_mkdir(savedir)
        savename = '{}/h{}_{}.json'.format(savedir,h,tag)
        jsonData = {'vals': results, 'errs': errors, 'integrals': integrals}
        self.dump(savename,jsonData)

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
            xerrs = [0]*len(amasses)
            vals = [results[h][a]['{}_h{}_a{}_{}'.format(param,h,a,tag)] for a in amasses]
            errs = [errors[h][a]['{}_h{}_a{}_{}'.format(param,h,a,tag)] for a in amasses]
            graph = ROOT.TGraphErrors(len(avals),array('d',avals),array('d',vals),array('d',xerrs),array('d',errs))
            #graph = ROOT.TGraph(len(avals),array('d',avals),array('d',vals))
            savedir = '{}/{}'.format(self.plotDir,shift if shift else 'central')
            python_mkdir(savedir)
            savename = '{}/{}_Fit'.format(savedir,name)
            canvas = ROOT.TCanvas(savename,savename,800,800)
            graph.Draw()
            graph.SetTitle('')
            graph.GetHistogram().GetXaxis().SetTitle(self.SPLINELABEL)
            graph.GetHistogram().GetYaxis().SetTitle(param)
            if fit:
                fitResult = graph.Fit(fitFuncs[param])
                func = graph.GetFunction(fitFuncs[param])
                fittedParams[param] = [func.Eval(x) for x in xs]
            canvas.Print('{}.png'.format(savename))

        param = 'integral'
        funcname = 'pol2'
        name = '{}_{}{}'.format(param,h,tag)
        vals = [integrals[h][a] for a in amasses]
        graph = ROOT.TGraph(len(avals),array('d',avals),array('d',vals))
        savedir = '{}/{}'.format(self.plotDir,shift if shift else 'central')
        python_mkdir(savedir)
        savename = '{}/{}_Fit'.format(savedir,name)
        canvas = ROOT.TCanvas(savename,savename,800,800)
        graph.Draw()
        graph.SetTitle('')
        graph.GetHistogram().GetXaxis().SetTitle(self.SPLINELABEL)
        graph.GetHistogram().GetYaxis().SetTitle('integral')
        if fit:
            fitResult = graph.Fit(funcname)
            func = graph.GetFunction(funcname)
            newintegrals = [func.Eval(x) for x in xs]
            # dont fit integrals
            #model.setIntegral(xs,newintegrals)
        canvas.Print('{}.png'.format(savename))

        return results, errors, integrals


    def buildSpline(self,h,vals,errs,integrals,region='PP',shifts=[],**kwargs):
        '''
        Get the signal spline for a given Higgs mass.
        Required arguments:
            h = higgs mass
            vals = dict with fitted param values
            errs = dict with fitted param errors
            integrals = dict with integrals for given distribution

        The dict should be of the form:
            vals = {
                '' : vals_central,
                'shift0Up': vals_shift0Up,
                'shift0Down': vals_shift0Down,
                ...
            }
        where vals_central, etc ar the fitted values from "fitSignal"
        each shift key to be used should be included in the argument "shifts"
            shifts = [
                'shift0',
                'shift1',
                ...
            ]
        and similarly for errors and integrals.
        '''
        workspace = kwargs.pop('workspace',self.workspace)
        xVar = kwargs.pop('xVar','x')
        fit = kwargs.get('fit',False)      # will fit the spline parameters rather than a simple spline
        amasses = self.AMASSES
        if h>125: amasses = [a for a in amasses if a not in ['3p6',4,6]]
        avals = [float(str(x).replace('p','.')) for x in amasses]

        # create parameter splines
        params = ['mean','width','sigma']
        splines = {}
        for param in params:
            name = '{param}_h{h}_{region}'.format(param=param,h=h,region=region)
            paramMasses = avals
            paramValues = [vals[''][h][a]['{param}_h{h}_a{a}_{region}'.format(param=param,h=h,a=a,region=region)] for a in amasses]
            paramShifts = {}
            for shift in shifts:
                shiftValuesUp   = [vals[shift+'Up'  ][h][a]['{param}_h{h}_a{a}_{region}_{shift}Up'.format(  param=param,h=h,a=a,region=region,shift=shift)] for a in amasses]
                shiftValuesDown = [vals[shift+'Down'][h][a]['{param}_h{h}_a{a}_{region}_{shift}Down'.format(param=param,h=h,a=a,region=region,shift=shift)] for a in amasses]
                paramShifts[shift] = {'up': shiftValuesUp, 'down': shiftValuesDown}
            spline = Models.Spline(name,
                masses = paramMasses,
                values = paramValues,
                shifts = paramShifts,
            )
            spline.build(workspace, name)
            splines[name] = spline

        # integral spline
        name = 'integral_{}_{}'.format(self.SPLINENAME.format(h=h),region)
        paramMasses = avals
        paramValues = [integrals[''][h][a] for a in amasses]
        paramShifts = {}
        for shift in shifts:
            shiftValuesUp   = [integrals[shift+'Up'  ][h][a] for a in amasses]
            shiftValuesDown = [integrals[shift+'Down'][h][a] for a in amasses]
            paramShifts[shift] = {'up': shiftValuesUp, 'down': shiftValuesDown}
        spline = Models.Spline(name,
            masses = paramMasses,
            values = paramValues,
            shifts = paramShifts,
        )
        spline.build(workspace, name)
        splines[name] = spline
    
        # create model
        if fit:
            print 'Need to reimplement fitting'
            raise
        else:
            model = Models.Voigtian(self.SPLINENAME.format(h=h),
                x = xVar,
                **{param: '{param}_h{h}_{region}'.format(param=param, h=h, region=region) for param in params}
            )
        model.build(workspace,'{}_{}'.format(self.SPLINENAME.format(h=h),region))

        return model


    def fitBackground(self,region='PP',shift='', **kwargs):
        scaleLumi = kwargs.pop('scaleLumi',1)
        workspace = kwargs.pop('workspace',self.workspace)
        xVar = kwargs.pop('xVar','x')
        model = workspace.pdf('bg_{}'.format(region))
        name = 'data_prefit_{}{}'.format(region,'_'+shift if shift else '')
        hist = self.histMap[region][shift]['dataNoSig']
        if hist.InheritsFrom('TH1'):
            integral = hist.Integral(hist.FindBin(self.XRANGE[0]),hist.FindBin(self.XRANGE[1])) * scaleLumi
            data = ROOT.RooDataHist(name,name,ROOT.RooArgList(workspace.var(xVar)),hist)
        else:
            integral = hist.sumEntries('x>{} && x<{}'.format(*self.XRANGE)) * scaleLumi
            # TODO add support for xVar
            data = hist.Clone(name)

        fr = model.fitTo(data, ROOT.RooFit.Save(), ROOT.RooFit.SumW2Error(True) )

        xFrame = workspace.var(xVar).frame()
        data.plotOn(xFrame)
        model.plotOn(xFrame,ROOT.RooFit.Components('cont1_{}'.format(region)),ROOT.RooFit.LineStyle(ROOT.kDashed))
        model.plotOn(xFrame,ROOT.RooFit.Components('cont2_{}'.format(region)),ROOT.RooFit.LineStyle(ROOT.kDashed))
        model.plotOn(xFrame,ROOT.RooFit.Components('cont1'),ROOT.RooFit.LineStyle(ROOT.kDashed))
        model.plotOn(xFrame,ROOT.RooFit.Components('cont2'),ROOT.RooFit.LineStyle(ROOT.kDashed))
        if self.XRANGE[0]<4:
            # jpsi
            model.plotOn(xFrame,ROOT.RooFit.Components('jpsi1S_{}'.format(region)),ROOT.RooFit.LineColor(ROOT.kRed))
            model.plotOn(xFrame,ROOT.RooFit.Components('jpsi2S_{}'.format(region)),ROOT.RooFit.LineColor(ROOT.kRed))
            model.plotOn(xFrame,ROOT.RooFit.Components('jpsi1S'),ROOT.RooFit.LineColor(ROOT.kRed))
            model.plotOn(xFrame,ROOT.RooFit.Components('jpsi2S'),ROOT.RooFit.LineColor(ROOT.kRed))
        model.plotOn(xFrame,ROOT.RooFit.Components('upsilon1S_{}'.format(region)),ROOT.RooFit.LineColor(ROOT.kRed))
        model.plotOn(xFrame,ROOT.RooFit.Components('upsilon2S_{}'.format(region)),ROOT.RooFit.LineColor(ROOT.kRed))
        model.plotOn(xFrame,ROOT.RooFit.Components('upsilon3S_{}'.format(region)),ROOT.RooFit.LineColor(ROOT.kRed))
        model.plotOn(xFrame,ROOT.RooFit.Components('upsilon1S'),ROOT.RooFit.LineColor(ROOT.kRed))
        model.plotOn(xFrame,ROOT.RooFit.Components('upsilon2S'),ROOT.RooFit.LineColor(ROOT.kRed))
        model.plotOn(xFrame,ROOT.RooFit.Components('upsilon3S'),ROOT.RooFit.LineColor(ROOT.kRed))
        # combined model
        model.plotOn(xFrame)
        model.paramOn(xFrame,ROOT.RooFit.Layout(0.72,0.98,0.90))

        canvas = ROOT.TCanvas('c','c',800,800)
        canvas.SetRightMargin(0.3)
        xFrame.Draw()
        prims = canvas.GetListOfPrimitives()
        for prim in prims:
            if 'paramBox' in prim.GetName():
                prim.SetTextSize(0.02)
        mi = xFrame.GetMinimum()
        ma = xFrame.GetMaximum()
        if mi<0:
            xFrame.SetMinimum(0.1)
        python_mkdir(self.plotDir)
        canvas.Print('{}/model_fit_{}{}.png'.format(self.plotDir,region,'_'+shift if shift else ''))
        canvas.SetLogy(True)
        canvas.Print('{}/model_fit_{}{}_log.png'.format(self.plotDir,region,'_'+shift if shift else ''))

        pars = fr.floatParsFinal()
        vals = {}
        errs = {}
        for p in range(pars.getSize()):
            vals[pars.at(p).GetName()] = pars.at(p).getValV()
            errs[pars.at(p).GetName()] = pars.at(p).getError()

        python_mkdir(self.fitsDir)
        jfile = '{}/background_{}{}.json'.format(self.fitsDir,region,'_'+shift if shift else '')
        results = {'vals':vals, 'errs':errs, 'integral':integral}
        self.dump(jfile,results)

        return vals, errs, integral


    ###############################
    ### Add things to workspace ###
    ###############################
    def addControlData(self,**kwargs):
        # build the models after doing the prefit stuff
        region = 'control'
        xVar = 'x_{}'.format(region)
        #xVar = 'x'
        self.addVar(xVar, *self.XRANGE, unit='GeV', label=self.XLABEL, workspace=self.workspace)
        self.buildModel(region=region, workspace=self.workspace, xVar=xVar)
        self.loadBackgroundFit(region, workspace=self.workspace)

        name = 'data_obs_{}'.format(region)
        hist = self.histMap[region]['']['data']
        # use the provided data
        if hist.InheritsFrom('TH1'):
            data_obs = ROOT.RooDataHist(name,name,ROOT.RooArgList(self.workspace.var(xVar)),self.histMap[region]['']['data'])
        else:
            # TODO add support for xVar
            data_obs = hist.Clone(name)
        self.wsimport(data_obs, ROOT.RooFit.RecycleConflictNodes() )


    def addData(self,blind=True,asimov=False,addSignal=False,addControl=False,doBinned=False,**kwargs):
        logging.debug('addData')
        logging.debug(str(kwargs))
        mh = kwargs.pop('h',125)
        ma = kwargs.pop('a',15)
        scaleLumi = kwargs.pop('scaleLumi',1)

        workspace = self.workspace

        for region in self.REGIONS:
            xVar = 'x' # decide if we want a different one for each region

            # build the models after doing the prefit stuff
            prebuiltParams = {p:p for p in self.background_params[region]}
            self.addVar(xVar, *self.XRANGE, unit='GeV', label=self.XLABEL, workspace=workspace)
            self.buildModel(region=region,workspace=workspace,xVar=xVar,**prebuiltParams)
            self.loadBackgroundFit(region, workspace=workspace)

            # save binned data
            if doBinned:

                bgs = self.getComponentFractions(workspace.pdf('bg_{}'.format(region)))
                
                for bg in bgs:
                    bgname = bg if region in bg else '{}_{}'.format(bg,region)
                    pdf = workspace.pdf(bg)
                    integral = workspace.function('integral_{}'.format(bgname))

                    x = workspace.var(xVar)
                    x.setBins(self.XBINNING)
                    args = ROOT.RooArgSet(x)
                    for shift in ['']+self.BACKGROUNDSHIFTS:
                        if shift:
                            s = workspace.var(shift)

                            s.setVal(1)
                            i = integral.getValV()
                            dh = pdf.generateBinned(args, i, True)
                            dh.SetName(bgname+'_binned_{}Up'.format(shift))
                            self.wsimport(dh)
                            
                            s.setVal(-1)
                            i = integral.getValV()
                            dh = pdf.generateBinned(args, i, True)
                            dh.SetName(bgname+'_binned_{}Down'.format(shift))
                            self.wsimport(dh)

                            s.setVal(0)
                            
                        else:
                            i = integral.getValV()
                            dh = pdf.generateBinned(args, i, True)
                            dh.SetName(bgname+'_binned')
                            self.wsimport(dh)


            name = 'data_obs_{}'.format(region)
            hist = self.histMap[region]['']['data']
            if blind:
                x = workspace.var(xVar)
                x.setBins(self.XBINNING)
                # generate a toy data observation from the model
                model = workspace.pdf('bg_{}'.format(region))
                h = self.histMap[region]['']['dataNoSig']
                if h.InheritsFrom('TH1'):
                    integral = h.Integral(h.FindBin(self.XRANGE[0]),h.FindBin(self.XRANGE[1])) * scaleLumi
                else:
                    integral = h.sumEntries('x>{} && x<{}'.format(*self.XRANGE)) * scaleLumi
                if asimov:
                    data_obs = model.generateBinned(ROOT.RooArgSet(self.workspace.var(xVar)),integral,1)
                else:
                    data_obs = model.generate(ROOT.RooArgSet(self.workspace.var(xVar)),int(integral))
                if addSignal:
                    self.workspace.var('MH').setVal(ma)
                    model = self.workspace.pdf('{}_{}'.format(self.SPLINENAME.format(h=mh),region))
                    integral = self.workspace.function('integral_{}_{}'.format(self.SPLINENAME.format(h=mh),region)).getVal()
                    if asimov:
                        sig_obs = model.generate(ROOT.RooArgSet(self.workspace.var(xVar)),integral,1)
                        data_obs.add(sig_obs)
                    else:
                        sig_obs = model.generate(ROOT.RooArgSet(self.workspace.var(xVar)),int(integral))
                        data_obs.append(sig_obs)
                data_obs.SetName(name)
            else:
                # use the provided data
                if hist.InheritsFrom('TH1'):
                    data_obs = ROOT.RooDataHist(name,name,ROOT.RooArgList(self.workspace.var(xVar)),self.histMap[region]['']['data'])
                else:
                    # TODO add support for xVar
                    data_obs = hist.Clone(name)
            self.wsimport(data_obs, ROOT.RooFit.RecycleConflictNodes() )

            if hist.InheritsFrom('TH1'):
                pass
            else:
                xFrame = self.workspace.var(xVar).frame()
                data_obs.plotOn(xFrame)
                canvas = ROOT.TCanvas('c','c',800,800)
                xFrame.Draw()
                mi = xFrame.GetMinimum()
                ma = xFrame.GetMaximum()
                if mi<0:
                    xFrame.SetMinimum(0.1)
                python_mkdir(self.plotDir)
                canvas.Print('{}/data_obs_{}.png'.format(self.plotDir,region))
                canvas.SetLogy(True)
                canvas.Print('{}/data_obs_{}_log.png'.format(self.plotDir,region))

        if addControl:
            region = 'control'
            xVar = 'x_{}'.format(region)
            #xVar = 'x'
            name = 'data_obs_{}'.format(region)
            hist = self.histMap[region]['']['data']
            if hist.InheritsFrom('TH1'):
                data_obs = ROOT.RooDataHist(name,name,ROOT.RooArgList(self.workspace.var(xVar)),hist)
            else:
                # TODO add support for xVar
                data_obs = hist.Clone(name)
            self.wsimport(data_obs, ROOT.RooFit.RecycleConflictNodes() )

    def getComponentFractions(self,model):
        logging.debug('getComponentFractions')
        logging.debug(model)
        if not model:
            print model
            raise
        if not isinstance(model,ROOT.RooAddPdf): 
            return {model.GetTitle(): []}
        pdfs = model.pdfList()
        coefs = model.coefList()
        result = {}
        for i in range(len(pdfs)):
            subresult = self.getComponentFractions(pdfs.at(i))
            for res in subresult:
                subresult[res] += [coefs.at(i)]
            result.update(subresult)
        return result

    def buildParams(self,region,vals,errs,integrals,**kwargs):
        logging.debug('buildParams')
        logging.debug(region,vals,errs,integrals,kwargs)
        workspace = kwargs.pop('workspace',self.workspace)
        params = {}
        for param in vals[region]['']:
            if 'frac' in param: continue
            paramValue = vals[region][''][param]
            paramShifts = {}
            for shift in self.BACKGROUNDSHIFTS:
                shiftValueUp   = vals[region][shift+'Up'  ][param]
                shiftValueDown = vals[region][shift+'Down'][param]
                paramShifts[shift] = {'up': shiftValueUp, 'down': shiftValueDown}
            paramModel = Models.Param(param,
                value  = paramValue,
                shifts = paramShifts,
            )
            paramModel.build(workspace, param)
            params[param] = paramModel
            workspace.Print()
        return params


    def buildComponentIntegrals(self,region,vals,errs,integrals, pdf,**kwargs):
        logging.debug('buildComponentIntegrals')
        logging.debug(', '.join([region,str(vals),str(errs),str(integrals),str(pdf),str(kwargs)]))
        workspace = kwargs.pop('workspace',self.workspace)
        fracMap = self.getComponentFractions(pdf)
        if isinstance(integrals,dict):
            vals = vals[region]['']
            errs = errs[region]['']
            integrals = integrals[region]
        allerrors = {}
        allintegrals = {}
        for component in fracMap:
            subint = 1.
            suberr2 = 0.
            # TODO: errors are way larger than they should be, need to look into this
            # dont use these uncertainties
            for frac in fracMap.get(component,[]):
                key = frac.GetTitle()
                if isinstance(frac,ROOT.RooRecursiveFraction):
                    subint *= frac.getVal()
                    #TODO correct this
                    #suberr2 += (frac.getError()/frac.getVal())**2
                else:
                    subint *= frac.getVal()
                    suberr2 += (frac.getError()/frac.getVal())**2
            suberr = suberr2**0.5
            component = component.rstrip('_x')
            component = component.rstrip('_'+region)
            allerrors[component] = suberr

            name = 'integral_{}_{}'.format(component,region)
            if isinstance(integrals,dict):
                paramValue = subint*integrals['']
                paramShifts = {}
                for shift in self.BACKGROUNDSHIFTS:
                    shiftValueUp   = subint*integrals[shift+'Up'  ]
                    shiftValueDown = subint*integrals[shift+'Down']
                    paramShifts[shift] = {'up': shiftValueUp, 'down': shiftValueDown}
                param = Models.Param(name,
                    value  = paramValue,
                    shifts = paramShifts,
                )
            else:
                paramValue = subint*integrals
                param = Models.Param(name,
                    value  = paramValue,
                )
            param.build(workspace, name)
            allintegrals[component] = paramValue

        python_mkdir(self.fitsDir)
        jfile = '{}/components_{}.json'.format(self.fitsDir,region)
        results = {'errs':allerrors, 'integrals':allintegrals}
        self.dump(jfile,results)


        return allintegrals, allerrors


    def loadBackgroundFit(self, region, shift='', **kwargs):
        logging.debug('loadBackgroundFit')
        logging.debug(', '.join([region,shift,str(kwargs)]))
        workspace = kwargs.pop('workspace',self.workspace)
        jfile = '{}/background_{}{}.json'.format(self.fitsDir,region,shift)
        results = self.load(jfile)
        vals = results['vals']
        errs = results['errs']
        ints = results['integral']
        for param in vals:
            try:
                workspace.var(param).setVal(vals[param])
            except:
                try:
                    workspace.function(param)
                except:
                    print 'ERROR on finding param {} in {} workspace'.format(param,region)
                    workspace.Print()
                    
        return vals, errs, ints

    def loadComponentIntegrals(self, region):
        logging.debug('loadComponentIntegrals')
        logging.debug(region)
        jfile = '{}/components_{}.json'.format(self.fitsDir,region)
        results = self.load(jfile)
        allintegrals = results['integrals']
        errors = results['errs']
        return allintegrals, errors

    def addControlModels(self, load=False, skipFit=False):
        region = 'control'
        workspace = self.buildWorkspace('control')
        self.initializeWorkspace(workspace=workspace)
        self.buildModel(region=region, workspace=workspace)
        if load:
            vals, errs, ints = self.loadBackgroundFit(region,workspace=workspace)
        if not skipFit:
            vals, errs, ints = self.fitBackground(region=region, workspace=workspace)

        if load:
            allintegrals, errors = self.loadComponentIntegrals(region)
        if not skipFit:
            allintegrals, errors = self.buildComponentIntegrals(region,vals,errs,ints, workspace.pdf('bg_control'), workspace=self.workspace)

        self.control_vals = vals
        self.control_errs = errs
        self.control_integrals = ints
        self.control_integralErrors = errors
        self.control_integralValues = allintegrals

    def fix(self,fix=True,**kwargs):
        workspace = kwargs.pop('workspace',self.workspace)
        #workspace.arg('lambda_cont1').setConstant(fix)
        #workspace.arg('lambda_cont2').setConstant(fix)
        workspace.arg('mean_upsilon1S').setConstant(fix)
        workspace.arg('mean_upsilon2S').setConstant(fix)
        workspace.arg('mean_upsilon3S').setConstant(fix)
        workspace.arg('sigma_upsilon1S').setConstant(fix)
        workspace.arg('sigma_upsilon2S').setConstant(fix)
        workspace.arg('sigma_upsilon3S').setConstant(fix)
        workspace.arg('width_upsilon1S').setConstant(fix)
        workspace.arg('width_upsilon2S').setConstant(fix)
        workspace.arg('width_upsilon3S').setConstant(fix)
        workspace.arg('upsilon1S_frac').setConstant(fix) 
        workspace.arg('upsilon2S_frac').setConstant(fix) 
        workspace.arg('upsilon3S_frac').setConstant(fix) 
        workspace.arg('upsilon23_frac').setConstant(fix) 
        workspace.arg('mean_jpsi1S').setConstant(fix)
        workspace.arg('mean_jpsi2S').setConstant(fix)
        workspace.arg('sigma_jpsi1S').setConstant(fix)
        workspace.arg('sigma_jpsi2S').setConstant(fix)
        workspace.arg('width_jpsi1S').setConstant(fix)
        workspace.arg('width_jpsi2S').setConstant(fix)
        if self.XRANGE[0]<3.3: workspace.arg('jpsi1S_frac').setConstant(fix) 
        if self.XRANGE[0]<4: workspace.arg('jpsi2S_frac').setConstant(fix) 
        #workspace.arg('upsilon_frac').setConstant(fix) 
        #if self.XRANGE[0]<3.3: workspace.arg('jpsi_frac').setConstant(fix) 

    def addBackgroundModels(self, fixAfterControl=False, fixAfterFP=False, load=False, skipFit=False, **kwargs):
        workspace = self.buildWorkspace('bg')
        self.initializeWorkspace(workspace=workspace)
        self.buildModel(region='control', workspace=workspace)
        self.loadBackgroundFit('control',workspace=workspace)
        if fixAfterControl:
            self.fix(workspace=workspace)
        vals = {}
        errs = {}
        integrals = {}
        errors = {}
        allintegrals = {}
        allparams = {}
        for region in self.REGIONS:
            vals[region] = {}
            errs[region] = {}
            integrals[region] = {}
            self.buildModel(region=region, workspace=workspace)
            for shift in ['']+self.BACKGROUNDSHIFTS:
                if shift=='':
                    if load:
                        v, e, i = self.loadBackgroundFit(region,workspace=workspace)
                    else:
                        v, e, i = self.fitBackground(region=region, workspace=workspace, **kwargs)
                    vals[region][shift] = v
                    errs[region][shift] = e
                    integrals[region][shift] = i
                    
                else:
                    if load:
                        vUp, eUp, iUp = self.loadBackgroundFit(region,shift+'Up',workspace=workspace)
                        vDown, eDown, iDown = self.loadBackgroundFit(region,shift+'Down',workspace=workspace)
                    if not skipFit:
                        vUp, eUp, iUp = self.fitBackground(region=region, shift=shift+'Up', workspace=workspace, **kwargs)
                        vDown, eDown, iDown = self.fitBackground(region=region, shift=shift+'Down', workspace=workspace, **kwargs
                        )
                    vals[region][shift+'Up'] = vUp
                    errs[region][shift+'Up'] = eUp
                    integrals[region][shift+'Up'] = iUp
                    vals[region][shift+'Down'] = vDown
                    errs[region][shift+'Down'] = eDown
                    integrals[region][shift+'Down'] = iDown


        for region in self.REGIONS:
            if load:
                allintegrals[region], errors[region] = self.loadComponentIntegrals(region)
            if not skipFit:
                allparams[region] = self.buildParams(region,vals,errs,integrals,workspace=self.workspace)
                allintegrals[region], errors[region] = self.buildComponentIntegrals(region,vals,errs,integrals,workspace.pdf('bg_{}'.format(region)), workspace=self.workspace)

        if fixAfterControl:
            self.fix(False, workspace=workspace)
        self.background_values = vals
        self.background_errors = errs
        self.background_integrals = integrals
        self.background_integralErrors = errors
        self.background_integralValues = allintegrals
        self.background_params = allparams


    def addBackgroundHists(self):
        shifts = {}
        for region in self.REGIONS:
            name = 'bg_{}'.format(region)
            hist = self.histMap[region]['']['datadriven'].Clone(name)
            self.setExpected('bg',region,hist)

            shifts[region] = {}
            for shift in self.BACKGROUNDSHIFTS:
                nameUp = 'bg_{}_{}Up'.format(region,shift)
                histUp = self.histMap[region][shift+'Up']['datadriven'].Clone(nameUp)

                nameDown = 'bg_{}_{}Down'.format(region,shift)
                histDown = self.histMap[region][shift+'Down']['datadriven'].Clone(nameDown)

                shifts[region][shift] = (histUp,histDown)

        for shift in self.BACKGROUNDSHIFTS:
            systs = {}
            for region in self.REGIONS:
                systs[(('bg',),(region,))] = shifts[region][shift]
            self.addSystematic(shift,'shape',systematics=systs)


    def addSignalModels(self,**kwargs):
        models = {}
        values = {}
        errors = {}
        integrals = {}
        for region in self.REGIONS:
            models[region] = {}
            values[region] = {}
            errors[region] = {}
            integrals[region] = {}
            for h in self.HMASSES:
                values[region][h] = {}
                errors[region][h] = {}
                integrals[region][h] = {}
                for shift in ['']+self.SIGNALSHIFTS+self.QCDSHIFTS:
                    if shift == '':
                        vals, errs, ints = self.fitSignals(h,region=region,shift=shift,**kwargs)
                        values[region][h][shift] = vals
                        errors[region][h][shift] = errs
                        integrals[region][h][shift] = ints
                    elif shift in self.QCDSHIFTS:
                        vals, errs, ints = self.fitSignals(h,region=region,shift=shift,**kwargs)
                        values[region][h][shift] = vals
                        errors[region][h][shift] = errs
                        integrals[region][h][shift] = ints
                    else:
                        valsUp, errsUp, intsUp = self.fitSignals(h,region=region,shift=shift+'Up',**kwargs)
                        valsDown, errsDown, intsDown = self.fitSignals(h,region=region,shift=shift+'Down',**kwargs)
                        values[region][h][shift+'Up'] = valsUp
                        errors[region][h][shift+'Up'] = errsUp
                        integrals[region][h][shift+'Up'] = intsUp
                        values[region][h][shift+'Down'] = valsDown
                        errors[region][h][shift+'Down'] = errsDown
                        integrals[region][h][shift+'Down'] = intsDown
                # special handling for QCD scale uncertainties
                if self.QCDSHIFTS:
                    values[region][h]['qcdUp']      = {h:{a:{} for a in self.AMASSES}}
                    values[region][h]['qcdDown']    = {h:{a:{} for a in self.AMASSES}}
                    errors[region][h]['qcdUp']      = {h:{a:{} for a in self.AMASSES}}
                    errors[region][h]['qcdDown']    = {h:{a:{} for a in self.AMASSES}}
                    integrals[region][h]['qcdUp']   = {h:{a:0  for a in self.AMASSES}}
                    integrals[region][h]['qcdDown'] = {h:{a:0  for a in self.AMASSES}}
                    for a in values[region][h][''][h]:
                        for val in values[region][h][''][h][a]:
                            values[region][h]['qcdUp'  ][h][a][val+'_qcdUp'  ] = max([values[region][h][shift][h][a][val+'_'+shift] for shift in self.QCDSHIFTS])
                            values[region][h]['qcdDown'][h][a][val+'_qcdDown'] = min([values[region][h][shift][h][a][val+'_'+shift] for shift in self.QCDSHIFTS])
                            errors[region][h]['qcdUp'  ][h][a][val+'_qcdUp'  ] = max([errors[region][h][shift][h][a][val+'_'+shift] for shift in self.QCDSHIFTS])
                            errors[region][h]['qcdDown'][h][a][val+'_qcdDown'] = min([errors[region][h][shift][h][a][val+'_'+shift] for shift in self.QCDSHIFTS])
                        integrals[region][h]['qcdUp'  ][h][a] = max([integrals[region][h][shift][h][a] for shift in self.QCDSHIFTS])
                        integrals[region][h]['qcdDown'][h][a] = min([integrals[region][h][shift][h][a] for shift in self.QCDSHIFTS])
                    for shift in ['qcdUp','qcdDown']:
                        savedir = '{}/{}'.format(self.fitsDir,shift)
                        python_mkdir(savedir)
                        savename = '{}/h{}_{}_{}.json'.format(savedir,h,region,shift)
                        jsonData = {'vals': values[region][h][shift], 'errs': errors[region][h][shift], 'integrals': integrals[region][h][shift]}
                        self.dump(savename,jsonData)

                    models[region][h] = self.buildSpline(h,values[region][h],errors[region][h],integrals[region][h],region,self.SIGNALSHIFTS+['qcd'],**kwargs)
                else:
                    models[region][h] = self.buildSpline(h,values[region][h],errors[region][h],integrals[region][h],region,self.SIGNALSHIFTS,**kwargs)
        self.fitted_models = models

    ######################
    ### Setup datacard ###
    ######################
    def setupDatacard(self, addControl=False, doBinned=False):
        bgs = self.getComponentFractions(self.workspace.pdf('bg_PP'))

        bgs = [b.rstrip('_PP') for b in bgs]
        sigs = [self.SPLINENAME.format(h=h) for h in self.HMASSES]

        # setup bins
        for region in self.REGIONS:
            self.addBin(region)

        # add processes
        #self.addProcess('bg')
        for proc in bgs:
            self.addProcess(proc)

        for proc in sigs:
            self.addProcess(proc,signal=True)

        #if doBinned: self.addBackgroundHists()

        # set expected
        for region in self.REGIONS:
            for proc in sigs+bgs:
                if proc in bgs and doBinned:
                    self.setExpected(proc,region,-1) 
                    self.addShape(region,proc,'{}_{}_binned'.format(proc,region))
                    continue
                self.setExpected(proc,region,1) 
                self.addRateParam('integral_{}_{}'.format(proc,region),region,proc)
                #self.addRateParam('integral_{}_{}'.format(proc,region),region,proc)
                #if proc in sigs:
                #    self.setExpected(proc,region,1) 
                #    self.addRateParam('integral_{}_{}'.format(proc,region),region,proc)
                #else:
                #    key = proc if proc in self.background_integralValues[region] else '{}_{}'.format(proc,region)
                #    integral = self.background_integralValues[region][key]
                #    self.setExpected(proc,region,integral)
                # overrides shape name to constrain them between regions
                #if 'cont' not in proc and proc not in sigs: 
                #    self.addShape(region,proc,proc)

            self.setObserved(region,-1) # reads from histogram

        if addControl:
            region = 'control'

            self.addBin(region)

            for proc in bgs:
                key = proc if proc in self.control_integralValues else '{}_{}'.format(proc,region)
                integral = self.control_integralValues[key]
                self.setExpected(proc,region,integral)
                #if 'cont' not in proc and proc not in sigs:
                #    self.addShape(region,proc,proc)

            self.setObserved(region,-1) # reads from histogram


    ###################
    ### Systematics ###
    ###################
    def addSystematics(self,doBinned=False,addControl=False):
        logging.debug('addSystematics')
        self.sigProcesses = tuple([self.SPLINENAME.format(h=h) for h in self.HMASSES])
        bgs = self.getComponentFractions(self.workspace.pdf('bg_PP'))
        bgs = [b.rstrip('_PP') for b in bgs]
        self.bgProcesses = bgs
        self._addLumiSystematic()
        self._addMuonSystematic()
        #self._addTauSystematic()
        self._addShapeSystematic(doBinned=doBinned)
        #self._addComponentSystematic(addControl=addControl)
        self._addRelativeNormUnc()
        self._addHiggsSystematic()
        if not doBinned and not addControl: self._addControlSystematics()

    def _addControlSystematics(self):
        '''Add the prefit control region values to datacard'''

        if not hasattr(self,'control_vals'): return

        params = [
            'mean_upsilon1S',
            'mean_upsilon2S',
            'mean_upsilon3S',
            'sigma_upsilon1S',
            'sigma_upsilon2S',
            'sigma_upsilon3S',
            'width_upsilon1S',
            'width_upsilon2S',
            'width_upsilon3S',
            #'upsilon1S_frac',
            #'upsilon2S_frac',
            #'upsilon3S_frac',
            #'upsilon23_frac',
            'mean_jpsi1S',
            'mean_jpsi2S',
            'sigma_jpsi1S',
            'sigma_jpsi2S',
            'width_jpsi1S',
            'width_jpsi2S',
            #'jpsi1S_frac',
            #'jpsi2S_frac',
            #'upsilon_frac',
        ]
        #if self.XRANGE[0]<3.3: params += ['jpsi_frac']

        for param in params:
            if param not in self.control_vals: continue
            v = self.control_vals[param]
            e = self.control_errs[param]
            rel_err = e/v
            self.addSystematic(param, 'param', systematics=[v,e])

    def _addHiggsSystematic(self):
        # theory
        syst = {}
        if 125 in self.HMASSES: syst[((self.SPLINENAME.format(h=125),), tuple(self.REGIONS))] = (1+(0.046*48.52+0.004*3.779)/(48.52+3.779)    , 1+(-0.067*48.52-0.003*3.779)/(48.52+3.779))
        if 300 in self.HMASSES: syst[((self.SPLINENAME.format(h=300),), tuple(self.REGIONS))] = (1+(0.015*6.59+0.003*1.256)/(6.59+1.256)      , 1+(-0.032*6.59-0.001*1.256)/(6.59+1.256))
        if 750 in self.HMASSES: syst[((self.SPLINENAME.format(h=750),), tuple(self.REGIONS))] = (1+(0.020*0.4969+0.003*0.1915)/(0.4969+0.1915), 1+(-0.037*0.4969-0.004*0.1915)/(0.4969+0.1915))
        self.addSystematic('higgs_theory','lnN',systematics=syst)

        # pdf+alpha_s
        syst = {}
        if 125 in self.HMASSES: syst[((self.SPLINENAME.format(h=125),), tuple(self.REGIONS))] = 1+(0.032*48.52+0.021*3.779)/(48.52+3.779)
        if 300 in self.HMASSES: syst[((self.SPLINENAME.format(h=300),), tuple(self.REGIONS))] = 1+(0.030*6.59+0.014*1.256)/(6.59+1.256)
        if 750 in self.HMASSES: syst[((self.SPLINENAME.format(h=750),), tuple(self.REGIONS))] = 1+(0.040*0.4969+0.022*0.1915)/(0.4969+0.1915)
        self.addSystematic('pdf_alpha','lnN',systematics=syst)


    def _addShapeSystematic(self,doBinned=False):
        for shift in self.SHIFTS+['qcd']:
            if shift=='qcd' and not self.QCDSHIFTS: continue
            if shift in self.BACKGROUNDSHIFTS and doBinned:
                syst = {}
                for proc in self.bgProcesses:
                    for region in self.REGIONS:
                        basename = '{}_{}_{}'.format(proc,region,shift)
                        syst[((proc,),(region,))] = (basename+'Up', basename+'Down')
                self.addSystematic(shift,'shape',systematics=syst)
            else:
                if self.workspace.var(shift): self.addSystematic(shift, 'param', systematics=[0,1])
    
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

    def _addComponentSystematic(self,addControl=False):
        bgs = self.getComponentFractions(self.workspace.pdf('bg_PP'))
        #bgs = [b.rstrip('_PP') for b in bgs if 'cont' not in b]
        bgs = [b.rstrip('_PP') for b in bgs]
        bins = self.REGIONS
        if addControl: bins += ['control']
        syst = {}
        for bg in bgs:
            for b in bins:
                key = bg if bg in self.control_integralErrors else '{}_control'.format(bg)
                syst[(bg,),(b,)] = 1 + self.control_integralErrors[key]

        self.addSystematic('{process}_normUnc','lnN',systematics=syst) 

    def _addRelativeNormUnc(self):
        relativesyst = {
           (tuple(['upsilon2S']),  tuple(['PP'])) : 1.05,
           (tuple(['upsilon3S']),  tuple(['PP'])) : 1.10,
           (tuple(['jpsi2S']), tuple(['PP'])) : 1.20,
        }
        self.addSystematic('relNormUnc_{process}', 'lnN', systematics=relativesyst)

    ###################################
    ### Save workspace and datacard ###
    ###################################
    def save(self,name='mmmt', subdirectory=''):
        processes = {}
        bgs = self.getComponentFractions(self.workspace.pdf('bg_PP'))
        bgs = [b.rstrip('_PP') for b in bgs]
        for h in self.HMASSES:
            processes[self.SIGNAME.format(h=h,a='X')] = [self.SPLINENAME.format(h=h)] + bgs
        if subdirectory == '':
            self.printCard('datacards_shape/MuMuTauTau/{}'.format(name),processes=processes,blind=False,saveWorkspace=True)
        else:
            self.printCard('datacards_shape/MuMuTauTau/' + subdirectory + '{}'.format(name),processes=processes,blind=False,saveWorkspace=True)
          
    def GetWorkspaceValue(self, variable):
        lam = self.workspace.argSet(variable)
        return lam.getRealValue(variable)
