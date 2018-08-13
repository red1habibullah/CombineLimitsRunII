import os
import sys
import logging
import itertools
import numpy as np
import argparse
import math
import errno
import json
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
    BACKGROUNDSHIFTS = []
    SIGNALSHIFTS = []


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

    ###########################
    ### Workspace utilities ###
    ###########################
    def initializeWorkspace(self):
        self.addX(*self.XRANGE,unit='GeV',label=self.XLABEL)
        self.addMH(*self.SPLINERANGE,unit='GeV',label=self.SPLINELABEL)

    def buildModel(self, region='PP', addUpsilon=True, setUpsilonLambda=False, voigtian=False, **kwargs):
        tag = kwargs.pop('tag',region)

        bgRes = Models.Voigtian if voigtian else Models.Gaussian

        # jpsi
        jpsi1S = bgRes('jpsi1S',
            mean  = [3.1,2.9,3.2],
            sigma = [0.1,0,0.5],
            width = [0.1,0.01,0.5],
        )
        nameJ1 = 'jpsi1S'
        jpsi1S.build(self.workspace,nameJ1)
    
        jpsi2S = bgRes('jpsi2S',
            mean  = [3.7,3.6,3.8],
            sigma = [0.1,0.01,0.5],
            width = [0.1,0.01,0.5],
        )
        nameJ2 = 'jpsi2S'
        jpsi2S.build(self.workspace,nameJ2)

        jpsiErr = Models.Erf('jpsiErr',
            erfScale = [-10,-500,-1],
            erfShift = [6.5,5,8],
        )
        nameJE = 'jpsiErr'
        jpsiErr.build(self.workspace,nameJE)
    
        #jpsi = {'recursive': True}
        #jpsi[nameJ1] = [0.9,0,1]
        #jpsi[nameJ2] = [0.1,0,1]
        #jpsi = Models.Sum('jpsi', **jpsi)
        #nameJ = 'jpsi_{}'.format(region)
        #jpsi.build(self.workspace,nameJ)

        if self.XRANGE[0]<3.3:
            jpsi = {'extended': True}
            jpsi[nameJ1] = [0.9,0,1]
            jpsi[nameJ2] = [0.1,0,1]
            jpsi = Models.Sum('jpsi', **jpsi)
            nameJ = 'jpsi'
            jpsi.build(self.workspace,nameJ)

        # upsilon
        upsilon1S = bgRes('upsilon1S',
            mean  = [9.5,9.3,9.7],
            sigma = [0.1,0.01,0.3],
        )
        nameU1 = 'upsilon1S'
        upsilon1S.build(self.workspace,nameU1)
    
        upsilon2S = bgRes('upsilon2S',
            mean  = [10.0,9.8,10.15],
            sigma = [0.1,0.01,0.3],
        )
        nameU2 = 'upsilon2S'
        upsilon2S.build(self.workspace,nameU2)
    
        upsilon3S = bgRes('upsilon3S',
            mean  = [10.3,10.22,10.5],
            sigma = [0.1,0.04,0.3],
        )
        nameU3 = 'upsilon3S'
        upsilon3S.build(self.workspace,nameU3)

        #upsilon = {'recursive': True}
        #upsilon[nameU1] = [0.75,0,1]
        #upsilon[nameU2] = [0.5,0,1]
        #upsilon[nameU3] = [0.5,0,1]
        #upsilon = Models.Sum('upsilon', **upsilon)
        #nameU = 'upsilon_{}'.format(region)
        #upsilon.build(self.workspace,nameU)

        nameU23 = 'upsilon23'
        upsilon23 = {'extended': True}
        upsilon23[nameU2] = [0.5,0,1]
        upsilon23[nameU3] = [0.5,0,1]
        upsilon23 = Models.Sum(nameU23, **upsilon23)
        upsilon23.build(self.workspace,nameU23)

        nameU = 'upsilon'
        upsilon = {'extended': True}
        upsilon[nameU1]  = [0.75,0,1]
        upsilon[nameU23] = [0.5,0,1]
        upsilon = Models.Sum(nameU, **upsilon)
        upsilon.build(self.workspace,nameU)

        # sum upsilon and jpsi
        nameR = 'resonant'
        resonant = {'extended': True}
        resonant[nameU]  = [0.75,0,1]
        if self.XRANGE[0]<3.3:
            resonant[nameJ] = [0.5,0,1]
        elif self.XRANGE[0]<4.0:
            resonant[nameJ2] = [0.5,0,1]
        resonant = Models.Sum(nameR, **resonant)
        resonant.build(self.workspace,nameR)


        # continuum background
        nameC = 'cont{}'.format('_'+tag if tag else '')
        cont = Models.Chebychev(nameC,
            order = 2,
            p0 = [-1,-1.4,0],
            p1 = [0.25,0,0.5],
            p2 = [0.03,-1,1],
        )
        cont.build(self.workspace,nameC)
    
        nameC1 = 'cont1{}'.format('_'+tag if tag else '')
        #nameC1 = 'cont1'
        cont1 = Models.Exponential(nameC1,
            lamb = [-2,-4,0],
        )
        cont1.build(self.workspace,nameC1)

        #nameC2 = 'cont2{}'.format('_'+tag if tag else '')
        ##nameC2 = 'cont2'
        #cont2 = Models.Exponential(nameC2,
        #    lamb = [-0.5,-2,0],
        #)
        #cont2.build(self.workspace,nameC2)
    
        nameC3 = 'cont3{}'.format('_'+tag if tag else '')
        #nameC3 = 'cont3'
        cont3 = Models.Exponential(nameC3,
            lamb = [-0.75,-5,0],
        )
        cont3.build(self.workspace,nameC3)
    
        #nameC4 = 'cont4{}'.format('_'+tag if tag else '')
        ##nameC4 = 'cont4'
        #cont4 = Models.Exponential(nameC4,
        #    lamb = [-2,-5,0],
        #)
        #cont4.build(self.workspace,nameC4)

        # sum
        bgs = {'recursive': True}
        # continuum background
        bgs[nameC1] = [0.5,0,1]
        if self.XRANGE[0]<=4 and self.XRANGE[1]>=11:
            bgs[nameR] = [0.9,0,1]
            bgs[nameC3] = [0.5,0,1]
        else:
            # jpsi
            if self.XRANGE[0]<3.3:
                bgs[nameJ] = [0.9,0,1]
                bgs[nameC3] = [0.5,0,1]
            elif self.XRANGE[0]<4:
                bgs[nameJ2] = [0.9,0,1]
                bgs[nameC3] = [0.5,0,1]
            # upsilon
            if self.XRANGE[0]<=9 and self.XRANGE[1]>=11:
                #bgs[nameU1] = [0.9,0,1]
                #bgs[nameU2] = [0.9,0,1]
                #bgs[nameU3] = [0.9,0,1]
                bgs[nameU] = [0.9,0,1]
                bgs[nameC3] = [0.5,0,1]
        bg = Models.Sum('bg', **bgs)
        name = 'bg_{}'.format(region)
        bg.build(self.workspace,name)

    def fitSignals(self,h,region='PP',shift='',**kwargs):
        '''
        Fit the signal model for a given Higgs mass.
        Required arguments:
            h = higgs mass
        '''
        fit = kwargs.get('fit',False)      # will fit the spline parameters rather than a simple spline
        amasses = self.AMASSES
        if h>125: amasses = [a for a in amasses if a not in ['3p6',4,6]]
        avals = [float(str(x).replace('p','.')) for x in amasses]
        histMap = self.histMap[region][shift]
        tag= '{}{}'.format(region,'_'+shift if shift else '')

        # initial fit
        results = {}
        errors = {}
        integrals = {}
        results[h] = {}
        errors[h] = {}
        integrals[h] = {}
        for a in amasses:
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
            if self.binned:
                integral = histMap[self.SIGNAME.format(h=h,a=a)].Integral()
            else:
                integral = histMap[self.SIGNAME.format(h=h,a=a)].sumEntries('x>{} && x<{}'.format(*self.XRANGE))
            integrals[h][a] = integral
    
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
            spline.build(self.workspace, name)
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
        spline.build(self.workspace, name)
        splines[name] = spline
    
        # create model
        if fit:
            print 'Need to reimplement fitting'
            raise
        else:
            model = Models.Voigtian(self.SPLINENAME.format(h=h),
                **{param: '{param}_h{h}_{region}'.format(param=param, h=h, region=region) for param in params}
            )
        model.build(self.workspace,'{}_{}'.format(self.SPLINENAME.format(h=h),region))

        return model


    def fitBackground(self,region='PP',shift='', setUpsilonLambda=False, addUpsilon=True, logy=False):
        model = self.workspace.pdf('bg_{}'.format(region))
        name = 'data_prefit_{}{}'.format(region,'_'+shift if shift else '')
        print region, shift
        hist = self.histMap[region][shift]['dataNoSig']
        if hist.InheritsFrom('TH1'):
            integral = hist.Integral(hist.FindBin(self.XRANGE[0]),hist.FindBin(self.XRANGE[1]))
            data = ROOT.RooDataHist(name,name,ROOT.RooArgList(self.workspace.var('x')),hist)
        else:
            integral = hist.sumEntries('x>{} && x<{}'.format(*self.XRANGE))
            data = hist.Clone(name)

        if setUpsilonLambda:
            self.workspace.var('x').setRange('low', self.XRANGE[0], self.UPSILONRANGE[0] )
            self.workspace.var('x').setRange('high', self.UPSILONRANGE[1], self.XRANGE[1])
            fr = model.fitTo(data, ROOT.RooFit.Save(), ROOT.RooFit.SumW2Error(True), ROOT.RooFit.Range('low,high') )
        else:
            fr = model.fitTo(data, ROOT.RooFit.Save(), ROOT.RooFit.SumW2Error(True) )

        xFrame = self.workspace.var('x').frame()
        data.plotOn(xFrame)
        # continuum
        model.plotOn(xFrame,ROOT.RooFit.Components('cont1_{}'.format(region)),ROOT.RooFit.LineStyle(ROOT.kDashed))
        model.plotOn(xFrame,ROOT.RooFit.Components('cont2_{}'.format(region)),ROOT.RooFit.LineStyle(ROOT.kDashed))
        model.plotOn(xFrame,ROOT.RooFit.Components('cont1'),ROOT.RooFit.LineStyle(ROOT.kDashed))
        model.plotOn(xFrame,ROOT.RooFit.Components('cont2'),ROOT.RooFit.LineStyle(ROOT.kDashed))
        if self.XRANGE[0]<4:
            # extended continuum when also fitting jpsi
            model.plotOn(xFrame,ROOT.RooFit.Components('cont3_{}'.format(region)),ROOT.RooFit.LineStyle(ROOT.kDashed))
            model.plotOn(xFrame,ROOT.RooFit.Components('cont4_{}'.format(region)),ROOT.RooFit.LineStyle(ROOT.kDashed))
            model.plotOn(xFrame,ROOT.RooFit.Components('cont3'),ROOT.RooFit.LineStyle(ROOT.kDashed))
            model.plotOn(xFrame,ROOT.RooFit.Components('cont4'),ROOT.RooFit.LineStyle(ROOT.kDashed))
            # jpsi
            model.plotOn(xFrame,ROOT.RooFit.Components('jpsi1S'),ROOT.RooFit.LineColor(ROOT.kRed))
            model.plotOn(xFrame,ROOT.RooFit.Components('jpsi2S'),ROOT.RooFit.LineColor(ROOT.kRed))
        if self.XRANGE[0]<8:
            model.plotOn(xFrame,ROOT.RooFit.Components('jpsiErr'),ROOT.RooFit.LineColor(ROOT.kGreen),ROOT.RooFit.LineStyle(ROOT.kDashed))
        # upsilon
        model.plotOn(xFrame,ROOT.RooFit.Components('upsilon1S'),ROOT.RooFit.LineColor(ROOT.kRed))
        model.plotOn(xFrame,ROOT.RooFit.Components('upsilon2S'),ROOT.RooFit.LineColor(ROOT.kRed))
        model.plotOn(xFrame,ROOT.RooFit.Components('upsilon3S'),ROOT.RooFit.LineColor(ROOT.kRed))
        # combined model
        model.plotOn(xFrame)

        canvas = ROOT.TCanvas('c','c',800,800)
        xFrame.Draw()
        canvas.SetLogy(logy)
        python_mkdir(self.plotDir)
        canvas.Print('{}/model_fit_{}{}.png'.format(self.plotDir,region,'_'+shift if shift else ''))

        pars = fr.floatParsFinal()
        vals = {}
        errs = {}
        for p in range(pars.getSize()):
            vals[pars.at(p).GetName()] = pars.at(p).getValV()
            errs[pars.at(p).GetName()] = pars.at(p).getError()
        for v in sorted(vals.keys()):
            print '  ', v, vals[v], '+/-', errs[v]

        python_mkdir(self.fitsDir)
        jfile = '{}/background_{}{}.json'.format(self.fitsDir,region,'_'+shift if shift else '')
        results = {'vals':vals, 'errs':errs, 'integral':integral}
        self.dump(jfile,results)

        return vals, errs, integral


    ###############################
    ### Add things to workspace ###
    ###############################
    def addControlData(self,asimov=False,**kwargs):
        region = 'control'
        name = 'data_obs_{}'.format(region)
        hist = self.histMap[region]['']['data']
        if asimov:
            # generate a toy data observation from the model
            model = self.workspace.pdf('bg_{}'.format(region))
            h = self.histMap[region]['']['dataNoSig']
            if h.InheritsFrom('TH1'):
                integral = h.Integral(h.FindBin(self.XRANGE[0]),h.FindBin(self.XRANGE[1]))
            else:
                integral = h.sumEntries('x>{} && x<{}'.format(*self.XRANGE))
            data_obs = model.generate(ROOT.RooArgSet(self.workspace.var('x')),int(integral))
            data_obs.SetName(name)
        else:
            # use the provided data
            if hist.InheritsFrom('TH1'):
                data_obs = ROOT.RooDataHist(name,name,ROOT.RooArgList(self.workspace.var('x')),self.histMap[region]['']['data'])
            else:
                data_obs = hist.Clone(name)
        self.wsimport(data_obs, ROOT.RooFit.RecycleConflictNodes() )

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
                if h.InheritsFrom('TH1'):
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
                if hist.InheritsFrom('TH1'):
                    data_obs = ROOT.RooDataHist(name,name,ROOT.RooArgList(self.workspace.var('x')),self.histMap[region]['']['data'])
                else:
                    data_obs = hist.Clone(name)
            self.wsimport(data_obs, ROOT.RooFit.RecycleConflictNodes() )

    def addControlModels(self, addUpsilon=True, setUpsilonLambda=False, voigtian=False, logy=False):
        region = 'control'
        self.buildModel(region=region, addUpsilon=addUpsilon, setUpsilonLambda=setUpsilonLambda, voigtian=voigtian)
        self.workspace.factory('bg_{}_norm[1,0,2]'.format(region))
        vals, errs, ints = self.fitBackground(region=region, setUpsilonLambda=setUpsilonLambda, addUpsilon=addUpsilon, logy=logy)
        self.control_vals = vals
        self.control_errs = errs
        self.control_integrals = ints

    def fix(self,fix=True):
        #self.workspace.arg('lambda_cont1').setConstant(fix)
        #self.workspace.arg('lambda_cont2').setConstant(fix)
        #self.workspace.arg('lambda_cont3').setConstant(fix)
        #self.workspace.arg('lambda_cont4').setConstant(fix)
        self.workspace.arg('mean_upsilon1S').setConstant(fix)
        self.workspace.arg('mean_upsilon2S').setConstant(fix)
        self.workspace.arg('mean_upsilon3S').setConstant(fix)
        self.workspace.arg('sigma_upsilon1S').setConstant(fix)
        self.workspace.arg('sigma_upsilon2S').setConstant(fix)
        self.workspace.arg('sigma_upsilon3S').setConstant(fix)
        self.workspace.arg('width_upsilon1S').setConstant(fix)
        self.workspace.arg('width_upsilon2S').setConstant(fix)
        self.workspace.arg('width_upsilon3S').setConstant(fix)
        self.workspace.arg('upsilon1S_frac').setConstant(fix) 
        self.workspace.arg('upsilon2S_frac').setConstant(fix) 
        self.workspace.arg('upsilon3S_frac').setConstant(fix) 
        self.workspace.arg('upsilon23_frac').setConstant(fix) 
        self.workspace.arg('mean_jpsi1S').setConstant(fix)
        self.workspace.arg('mean_jpsi2S').setConstant(fix)
        self.workspace.arg('sigma_jpsi1S').setConstant(fix)
        self.workspace.arg('sigma_jpsi2S').setConstant(fix)
        self.workspace.arg('width_jpsi1S').setConstant(fix)
        self.workspace.arg('width_jpsi2S').setConstant(fix)
        if self.XRANGE[0]<3.3: self.workspace.arg('jpsi1S_frac').setConstant(fix) 
        if self.XRANGE[0]<4: self.workspace.arg('jpsi2S_frac').setConstant(fix) 
        self.workspace.arg('upsilon_frac').setConstant(fix) 
        if self.XRANGE[0]<3.3: self.workspace.arg('jpsi_frac').setConstant(fix) 

    def addBackgroundModels(self, fixAfterControl=False, fixAfterFP=False, addUpsilon=True, setUpsilonLambda=False, voigtian=False, logy=False):
        if fixAfterControl:
            self.fix()
        if setUpsilonLambda:
            self.workspace.arg('lambda_cont1_FP').setConstant(True)
            self.workspace.arg('lambda_cont1_PP').setConstant(True)
        vals = {}
        errs = {}
        integrals = {}
        for region in self.REGIONS:
            vals[region] = {}
            errs[region] = {}
            integrals[region] = {}
            if region == 'PP' and fixAfterFP and addUpsilon and self.XRANGE[0]<=9 and self.XRANGE[1]>=11:
                self.fix()
            self.buildModel(region=region, addUpsilon=addUpsilon, setUpsilonLambda=setUpsilonLambda, voigtian=voigtian)
            self.workspace.factory('bg_{}_norm[1,0,2]'.format(region))
            for shift in self.BACKGROUNDSHIFTS+['']:
                if shift=='':
                    v, e, i = self.fitBackground(region=region, setUpsilonLambda=setUpsilonLambda, addUpsilon=addUpsilon, logy=logy)
                    vals[region][shift] = v
                    errs[region][shift] = e
                    integrals[region][shift] = i
                else:
                    vUp, eUp, iUp = self.fitBackground(region=region, shift=shift+'Up', setUpsilonLambda=setUpsilonLambda, addUpsilon=addUpsilon, logy=logy)
                    vDown, eDown, iDown = self.fitBackground(region=region, shift=shift+'Down', setUpsilonLambda=setUpsilonLambda, addUpsilon=addUpsilon, logy=logy)
                    vals[region][shift+'Up'] = vUp
                    errs[region][shift+'Up'] = eUp
                    integrals[region][shift+'Up'] = iUp
                    vals[region][shift+'Down'] = vDown
                    errs[region][shift+'Down'] = eDown
                    integrals[region][shift+'Down'] = iDown
            if region == 'PP' and fixAfterFP and addUpsilon and self.XRANGE[0]<=9 and self.XRANGE[1]>=11: 
                self.fix(False)

            # integral
            name = 'integral_bg_{}'.format(region)
            paramValue = integrals[region]['']
            paramShifts = {}
            for shift in self.BACKGROUNDSHIFTS:
                shiftValueUp   = integrals[region][shift+'Up'  ]
                shiftValueDown = integrals[region][shift+'Down']
                paramShifts[shift] = {'up': shiftValueUp, 'down': shiftValueDown}
            param = Models.Param(name,
                value  = paramValue,
                shifts = paramShifts,
            )
            param.build(self.workspace, name)

        if fixAfterControl:
            self.fix(False)
        self.background_values = vals
        self.background_errors = errs
        self.background_integrals = integrals


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
                for shift in ['']+self.SIGNALSHIFTS:
                    if shift == '':
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
                models[region][h] = self.buildSpline(h,values[region][h],errors[region][h],integrals[region][h],region,self.SIGNALSHIFTS,**kwargs)
                self.workspace.factory('{}_{}_norm[1,0,9999]'.format(self.SPLINENAME.format(h=h),region))
        self.fitted_models = models

    ######################
    ### Setup datacard ###
    ######################
    def setupDatacard(self, addControl=False):

        # setup bins
        for region in self.REGIONS:
            self.addBin(region)

        # add processes
        self.addProcess('bg')

        for proc in [self.SPLINENAME.format(h=h) for h in self.HMASSES]:
            self.addProcess(proc,signal=True)

        # set expected
        for region in self.REGIONS:
            for proc in [self.SPLINENAME.format(h=h) for h in self.HMASSES]+['bg']:
                self.setExpected(proc,region,1)
                self.addRateParam('integral_{}_{}'.format(proc,region),region,proc)
                
            self.setObserved(region,-1) # reads from histogram

        if addControl:
            region = 'control'

            self.addBin(region)

            h = self.histMap[region]['']['dataNoSig']
            if h.InheritsFrom('TH1'):
                integral = h.Integral(h.FindBin(self.XRANGE[0]),h.FindBin(self.XRANGE[1]))
            else:
                integral = h.sumEntries('x>{} && x<{}'.format(*self.XRANGE))
            self.setExpected('bg',region,integral)

            self.setObserved(region,-1) # reads from histogram
            

    ###################
    ### Systematics ###
    ###################
    def addSystematics(self):
        print 'ADDING SYSTEMATICS'
        self.sigProcesses = tuple([self.SPLINENAME.format(h=h) for h in self.HMASSES])
        self.bgProcesses = ('bg',)
        self._addLumiSystematic()
        self._addMuonSystematic()
        self._addTauSystematic()
        self._addShapeSystematic()
        self._addControlSystematics()

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
            'upsilon1S_frac',
            'upsilon2S_frac',
            'upsilon3S_frac',
            'upsilon23_frac',
            'mean_jpsi1S',
            'mean_jpsi2S',
            'sigma_jpsi1S',
            'sigma_jpsi2S',
            'width_jpsi1S',
            'width_jpsi2S',
            'jpsi1S_frac',
            'jpsi2S_frac',
            'upsilon_frac',
        ]
        if self.XRANGE[0]<3.3: params += ['jpsi_frac']

        for param in params:
            if param not in self.control_vals: continue
            v = self.control_vals[param]
            e = self.control_errs[param]
            rel_err = e/v
            self.addSystematic(param, 'param', systematics=[v,e])

    def _addShapeSystematic(self):
        # decide if we keep a given shape uncertainty
        #if hasattr(self,'fitted_models'):
        #    for shift in self.SIGNALSHIFTS:
        #        for region in self.REGIONS:
        #            for h in self.HMASSES:
        #                model = self.fitted_models[region][''][h]
        #                modelUp, modelDown = self.fitted_models[region][shift][h]

        #                # check integrals
        #                integrals = model.getIntegrals()
        #                integralsUp = modelUp.getIntegrals()
        #                integralsDown = modelDown.getIntegrals()
        #                diffUp = [i[1]-i[0] for i in zip(integrals,integralsUp)]
        #                diffDown = [i[0]-i[1] for i in zip(integrals,integralsDown)]
        #                hasNormUp = any([abs(i[1]/i[0])>0.005 for i in zip(integrals,diffUp)])
        #                hasNormDown = any([abs(i[1]/i[0])>0.005 for i in zip(integrals,diffDown)])
        #                hasNorm = hasNormUp or hasNormDown

        #                # check params
        #                params = model.getParams()
        #                for param in params:
        #                    


        for shift in self.SHIFTS:
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
