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

import CombineLimits.Plotter.CMS_lumi as CMS_lumi
import CombineLimits.Plotter.tdrstyle as tdrstyle

tdrstyle.setTDRStyle()

class HaaLimits(Limits):
    '''
    Create the Haa Limits workspace
    '''

    # permanent parameters
    HMASSES = [125,200,250,300,400,500,750,1000]
    AMASSES = ['3p6',4,5,6,7,9,11,13,15,17,19,21]

    HBINNING = 25 # GeV
    ABINNING = 0.1 # GeV

    SIGNAME = 'HToAAH{h}A{a}'
    SPLINENAME = 'sig'
    ALABEL = 'm_{a}'
    ARANGE = [0,25]
    HLABEL = 'm_{a}'
    HRANGE = [0,1000]

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

        top = [k for k in self.histMap.keys() if 'PP' in k][0]
        sample = self.histMap[top][''].keys()[0]

        self.binned = self.histMap[top][''][sample].InheritsFrom('TH1')

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
        self.addMH(*self.HRANGE,unit='GeV',label=self.HLABEL,**kwargs)
        self.addMA(*self.ARANGE,unit='GeV',label=self.ALABEL,**kwargs)

    def buildModel(self, region, **kwargs):
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

    def loadSignalFits(self, tag, region, shift=''):
        savedir = '{}/{}'.format(self.fitsDir,shift if shift else 'central')
        savename = '{}/{}.json'.format(savedir,tag)
        results = self.load(savename)
        vals = results['vals']
        errs = results['errs']
        ints = results['integrals']
        return vals, errs, ints

    def fitSignal(self,h,a,region,shift='',**kwargs):
        scaleLumi = kwargs.get('scaleLumi',1)
        results = kwargs.get('results',{})
        histMap = self.histMap[region][shift]
        tag = kwargs.get('tag','{}{}'.format(region,'_'+shift if shift else ''))

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
        

    def fitSignals(self,region,shift='',**kwargs):
        '''
        Fit the signal model for a given Higgs mass.
        Required arguments:
            h = higgs mass
        '''
        scaleLumi = kwargs.get('scaleLumi',1)
        fit = kwargs.get('fit',False)      # will fit the spline parameters rather than a simple spline
        load = kwargs.get('load',False)
        skipFit = kwargs.get('skipFit',False)
        tag = kwargs.get('tag','{}{}'.format(region,'_'+shift if shift else ''))

        histMap = self.histMap[region][shift]

        # initial fit
        if load:
            # load the previous fit
            results, errors, integrals = self.loadSignalFits(tag,region,shift)
        elif shift and not skipFit:
            # load the central fits
            cresults, cerrors, cintegrals = self.loadSignalFits(region,region)
        if not skipFit:
            results = {}
            errors = {}
            integrals = {}

            for h in self.HMASSES:
                results[h] = {}
                errors[h] = {}
                integrals[h] = {}

                amasses = self.AMASSES
                if h>125: amasses = [a for a in amasses if a not in ['3p6',4,6]]
                if h in [200,250,400,500,1000]: amasses = [5, 9, 15]
                avals = [float(str(x).replace('p','.')) for x in amasses]

                for a in amasses:
                    if load or (shift and not skipFit):
                        results[h][a], errors[h][a], integrals[h][a] = self.fitSignal(h,a,region,shift,results=cresults[h][a],**kwargs)
                    elif not skipFit:
                        results[h][a], errors[h][a], integrals[h][a] = self.fitSignal(h,a,region,shift,**kwargs)
    
        savedir = '{}/{}'.format(self.fitsDir,shift if shift else 'central')
        python_mkdir(savedir)
        savename = '{}/{}.json'.format(savedir,tag)
        jsonData = {'vals': results, 'errs': errors, 'integrals': integrals}
        self.dump(savename,jsonData)

        fitFuncs = self.fitSignalParams(results,errors,integrals,region,shift)

        return results, errors, integrals, fitFuncs

    def fitSignalParams(self,results,errors,integrals,region,shift='',**kwargs):
        tag = kwargs.get('tag','{}{}'.format(region,'_'+shift if shift else ''))
        # Fit using ROOT rather than RooFit for the splines
        fitFuncs = {
            'mean' :    ROOT.TF2('mean_{}'.format(tag),     '[0]+[1]*y',                                 *self.HRANGE+self.ARANGE), 
            'width':    ROOT.TF2('width_{}'.format(tag),    '[0]+[1]*x+[2]*y+[3]*x*y+[4]*x*x+[5]*y*y',   *self.HRANGE+self.ARANGE), 
            'sigma':    ROOT.TF2('sigma_{}'.format(tag),    '[0]+[1]*x+[2]*y+[3]*x*y+[4]*x*x+[5]*y*y',   *self.HRANGE+self.ARANGE), 
            'integral': ROOT.TF2('integral_{}'.format(tag), 'exp([0]+[1]*x)*([2]+[3]*y+[4]*y*y+[5]*x*y)',*self.HRANGE+self.ARANGE),
        }

        colors = {
            125 : ROOT.kBlack,
            200 : ROOT.kMagenta,
            250 : ROOT.kCyan+1,
            300 : ROOT.kBlue,
            400 : ROOT.kRed,
            500 : ROOT.kOrange-3,
            750 : ROOT.kGreen+2,
            1000: ROOT.kViolet-1,
        }
        
        for param in ['mean','width','sigma','integral']:
            xvals = [h for h in sorted(results) for a in sorted(results[h])]
            xerrs = [0] * len(xvals)
            yvals = [float(str(a).replace('p','.')) for h in sorted(results) for a in sorted(results[h])]
            yerrs = [0] * len(yvals)
            if param=='integral':
                zvals = [integrals[h][a] for h in sorted(results) for a in sorted(results[h])]
            else:
                zvals = [results[h][a]['{}_h{}_a{}_{}'.format(param,h,a,tag)] for h in sorted(results) for a in sorted(results[h])]
                zerrs = [errors[h][a]['{}_h{}_a{}_{}'.format(param,h,a,tag)] for h in sorted(results) for a in sorted(results[h])]
            #graph = ROOT.TGraph2DErrors(len(xvals), array('d',xvals), array('d',yvals), array('d',zvals), array('d',xerrs), array('d',yerrs), array('
            graph = ROOT.TGraph2D(len(xvals), array('d',xvals), array('d',yvals), array('d',zvals))
            graph.Fit(fitFuncs[param])

            name = '{}_{}'.format(param,tag)
            savedir = '{}/{}'.format(self.plotDir,shift if shift else 'central')
            python_mkdir(savedir)
            savename = '{}/{}_Fit'.format(savedir,name)

            canvas = ROOT.TCanvas(savename,savename,800,800)
            canvas.SetTopMargin(0.1)

            mg = ROOT.TMultiGraph()
            fmg = ROOT.TMultiGraph()

            legend = ROOT.TLegend(0.1,0.9,0.9,1.0,'','NDC')
            legend.SetTextFont(42)
            legend.SetBorderSize(0)
            legend.SetFillColor(0)
            legend.SetNColumns(len(self.HMASSES))

            for h in self.HMASSES:
                xs = [yvals[i] for i in range(len(xvals)) if xvals[i]==h]
                ys = [zvals[i] for i in range(len(xvals)) if xvals[i]==h]

                g = ROOT.TGraph(len(xs),array('d',xs),array('d',ys))
                g.SetLineColor(colors[h])
                g.SetMarkerColor(colors[h])
                g.SetTitle('H({h})'.format(h=h))

                legend.AddEntry(g,g.GetTitle(),'lp')
                mg.Add(g)

                fxs = []
                fys = []
                for a in range(self.ARANGE[0]*10,self.ARANGE[1]*10+1,1):
                    y = fitFuncs[param].Eval(h,a*0.1)
                    fxs += [a*0.1]
                    fys += [y]
                fg = ROOT.TGraph(len(fxs),array('d',fxs),array('d',fys))
                fg.SetLineColor(colors[h])
                fg.SetLineWidth(3)
                fg.SetMarkerColor(colors[h])
                fmg.Add(fg)

            canvas.DrawFrame(self.ARANGE[0],min(zvals)*0.9,self.ARANGE[1],max(zvals)*1.1)
            mg.Draw('p0')
            mg.GetXaxis().SetTitle(self.ALABEL)
            mg.GetYaxis().SetTitle(param)
            fmg.Draw('L')
            legend.Draw()
            canvas.Print('{}.png'.format(savename))

        return fitFuncs

    def buildSpline(self,vals,errs,integrals,region,shifts=[],**kwargs):
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
        fitFuncs = kwargs.get('fitFuncs',{})

        splines = {}
        if fit:
            params = ['mean','width','sigma','integral']
            for param in params:
                name = '{param}_{region}'.format(param=param,region=region)
                spline = Models.Spline(name,
                    MH = ['MH','MA'],
                    masses = None,
                    values = fitFuncs[''][param],
                    shifts = {shift: {'up': fitFuncs[shift+'Up'][param], 'down': fitFuncs[shift+'Down'][param],} for shift in shifts},
                )
                spline.build(workspace, name)
                splines[name] = spline

            # create model
            model = Models.Voigtian(self.SPLINENAME,
                x = xVar,
                **{param: '{param}_{region}'.format(param=param, region=region) for param in params}
            )
            model.build(workspace,'{}_{}'.format(self.SPLINENAME,region))

            return model



        # create parameter splines
        params = ['mean','width','sigma']
        for param in params:
            name = '{param}_{region}'.format(param=param,region=region)
            paramMasses = [[],[]]
            paramValues = []
            paramShifts = {}
            for h in vals['']:
                for a in vals[''][h]:
                    paramMasses[0] += [h]
                    paramMasses[1] += [float(str(a).replace('p','.'))]
                    paramValues += [vals[''][h][a]['{param}_h{h}_a{a}_{region}'.format(param=param,h=h,a=a,region=region)]]
                    for shift in shifts:
                        if shift not in paramShifts: paramShifts[shift] = {'up': [], 'down': []}
                        paramShifts[shift]['up']   += [vals[shift+'Up'  ][h][a]['{param}_h{h}_a{a}_{region}_{shift}Up'.format(  param=param,h=h,a=a,region=region,shift=shift)]]
                        paramShifts[shift]['down'] += [vals[shift+'Down'][h][a]['{param}_h{h}_a{a}_{region}_{shift}Down'.format(param=param,h=h,a=a,region=region,shift=shift)]]
            spline = Models.Spline(name,
                MH = ['MH','MA'],
                masses = paramMasses,
                values = paramValues,
                shifts = paramShifts,
            )
            spline.build(workspace, name)
            splines[name] = spline

        # integral spline
        name = 'integral_{}_{}'.format(self.SPLINENAME,region)
        paramMasses = [[],[]]
        paramValues = []
        paramShifts = {}
        for h in vals['']:
            for a in vals[''][h]:
                paramMasses[0] += [h]
                paramMasses[1] += [float(str(a).replace('p','.'))]
                paramValues += [integrals[''][h][a]]
                for shift in shifts:
                    if shift not in paramShifts: paramShifts[shift] = {'up': [], 'down': []}
                    paramShifts[shift]['up']   += [integrals[shift+'Up'  ][h][a]]
                    paramShifts[shift]['down'] += [integrals[shift+'Down'][h][a]]
        spline = Models.Spline(name,
            MH = ['MH','MA'],
            masses = paramMasses,
            values = paramValues,
            shifts = paramShifts,
        )
        spline.build(workspace, name)
        splines[name] = spline

        # create model
        model = Models.Voigtian(self.SPLINENAME,
            x = xVar,
            **{param: '{param}_{region}'.format(param=param, region=region) for param in params}
        )
        model.build(workspace,'{}_{}'.format(self.SPLINENAME,region))

        return model


    def fitBackground(self,region,shift='', **kwargs):
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
                    model = self.workspace.pdf('{}_{}'.format(self.SPLINENAME,region))
                    integral = self.workspace.function('integral_{}_{}'.format(self.SPLINENAME,region)).getVal()
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
        fitFuncs = {}
        for region in self.REGIONS:
            models[region] = {}
            values[region] = {}
            errors[region] = {}
            integrals[region] = {}
            fitFuncs[region] = {}
            for shift in ['']+self.SIGNALSHIFTS+self.QCDSHIFTS:
                values[region][shift] = {}
                errors[region][shift] = {}
                integrals[region][shift] = {}
                fitFuncs[region][shift] = {}
                if shift == '':
                    vals, errs, ints, fits = self.fitSignals(region=region,shift=shift,**kwargs)
                    values[region][shift] = vals
                    errors[region][shift] = errs
                    integrals[region][shift] = ints
                    fitFuncs[region][shift] = fits
                elif shift in self.QCDSHIFTS:
                    vals, errs, ints, fits = self.fitSignals(region=region,shift=shift,**kwargs)
                    values[region][shift] = vals
                    errors[region][shift] = errs
                    integrals[region][shift] = ints
                    fitFuncs[region][shift] = fits
                else:
                    valsUp, errsUp, intsUp, fitsUp = self.fitSignals(region=region,shift=shift+'Up',**kwargs)
                    valsDown, errsDown, intsDown, fitsDown = self.fitSignals(region=region,shift=shift+'Down',**kwargs)
                    values[region][shift+'Up'] = valsUp
                    errors[region][shift+'Up'] = errsUp
                    integrals[region][shift+'Up'] = intsUp
                    fitFuncs[region][shift+'Up'] = fitsUp
                    values[region][shift+'Down'] = valsDown
                    errors[region][shift+'Down'] = errsDown
                    integrals[region][shift+'Down'] = intsDown
                    fitFuncs[region][shift+'Down'] = fitsDown
                # special handling for QCD scale uncertainties
                if self.QCDSHIFTS:
                    values[region]['qcdUp']      = {}
                    values[region]['qcdDown']    = {}
                    errors[region]['qcdUp']      = {}
                    errors[region]['qcdDown']    = {}
                    integrals[region]['qcdUp']   = {}
                    integrals[region]['qcdDown'] = {}
                    for h in values[region]['']:
                        values[region]['qcdUp'][h]      = {}
                        values[region]['qcdDown'][h]    = {}
                        errors[region]['qcdUp'][h]      = {}
                        errors[region]['qcdDown'][h]    = {}
                        integrals[region]['qcdUp'][h]   = {}
                        integrals[region]['qcdDown'][h] = {}
                        for a in values[region][''][h]:
                            values[region]['qcdUp'][h][a]      = {}
                            values[region]['qcdDown'][h][a]    = {}
                            errors[region]['qcdUp'][h][a]      = {}
                            errors[region]['qcdDown'][h][a]    = {}
                            integrals[region]['qcdUp'  ][h][a] = max([integrals[region][shift][h][a] for shift in self.QCDSHIFTS])
                            integrals[region]['qcdDown'][h][a] = min([integrals[region][shift][h][a] for shift in self.QCDSHIFTS])
                            for val in values[region][''][h][a]:
                                values[region]['qcdUp'  ][h][a][val+'_qcdUp'  ] = max([values[region][shift][h][a][val+'_'+shift] for shift in self.QCDSHIFTS])
                                values[region]['qcdDown'][h][a][val+'_qcdDown'] = min([values[region][shift][h][a][val+'_'+shift] for shift in self.QCDSHIFTS])
                                errors[region]['qcdUp'  ][h][a][val+'_qcdUp'  ] = max([errors[region][shift][h][a][val+'_'+shift] for shift in self.QCDSHIFTS])
                                errors[region]['qcdDown'][h][a][val+'_qcdDown'] = min([errors[region][shift][h][a][val+'_'+shift] for shift in self.QCDSHIFTS])
                    for shift in ['qcdUp','qcdDown']:
                        savedir = '{}/{}'.format(self.fitsDir,shift)
                        python_mkdir(savedir)
                        savename = '{}/{}_{}.json'.format(savedir,region,shift)
                        jsonData = {'vals': values[region][shift], 'errs': errors[region][shift], 'integrals': integrals[region][shift]}
                        self.dump(savename,jsonData)
                    fitFuncs[region]['qcdUp']   = self.fitSignalParams(values[region]['qcdUp'],  errors[region]['qcdUp'],  integrals[region]['qcdUp'],  region,'qcdUp')
                    fitFuncs[region]['qcdDown'] = self.fitSignalParams(values[region]['qcdDown'],errors[region]['qcdDown'],integrals[region]['qcdDown'],region,'qcdDown')

            if self.QCDSHIFTS:
                models[region] = self.buildSpline(values[region],errors[region],integrals[region],region,self.SIGNALSHIFTS+['qcd'],fitFuncs=fitFuncs[region],**kwargs)
            else:
                models[region] = self.buildSpline(values[region],errors[region],integrals[region],region,self.SIGNALSHIFTS,fitFuncs=fitFuncs[region],**kwargs)
        self.fitted_models = models

    ######################
    ### Setup datacard ###
    ######################
    def setupDatacard(self, addControl=False, doBinned=False):
        bgs = self.getComponentFractions(self.workspace.pdf('bg_'+self.REGIONS[0]))

        bgs = [b.rstrip('_'+self.REGIONS[0]) for b in bgs]
        sigs = [self.SPLINENAME]

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
        self.sigProcesses = tuple([self.SPLINENAME])
        bgs = self.getComponentFractions(self.workspace.pdf('bg_'+self.REGIONS[0]))
        bgs = [b.rstrip('_'+self.REGIONS[0]) for b in bgs]
        self.bgProcesses = tuple(bgs)
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
        #TODO switch to spline
        return
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
        bgs = self.getComponentFractions(self.workspace.pdf('bg_'+self.REGIONS[0]))
        #bgs = [b.rstrip('_'+self.REGIONS[0]) for b in bgs if 'cont' not in b]
        bgs = [b.rstrip('_'+self.REGIONS[0]) for b in bgs]
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
           (tuple(['upsilon2S']),  tuple([self.REGIONS[0]])) : 1.05,
           (tuple(['upsilon3S']),  tuple([self.REGIONS[0]])) : 1.10,
           (tuple(['jpsi2S']),     tuple([self.REGIONS[0]])) : 1.20,
        }
        self.addSystematic('relNormUnc_{process}', 'lnN', systematics=relativesyst)

    ###################################
    ### Save workspace and datacard ###
    ###################################
    def save(self,name='mmmt', subdirectory=''):
        processes = {}
        bgs = self.getComponentFractions(self.workspace.pdf('bg_'+self.REGIONS[0]))
        bgs = [b.rstrip('_'+self.REGIONS[0]) for b in bgs]
        processes = [self.SPLINENAME] + bgs
        if subdirectory == '':
            self.printCard('datacards_shape/MuMuTauTau/{}'.format(name),processes=processes,blind=False,saveWorkspace=True)
        else:
            self.printCard('datacards_shape/MuMuTauTau/' + subdirectory + '{}'.format(name),processes=processes,blind=False,saveWorkspace=True)
          
    def GetWorkspaceValue(self, variable):
        lam = self.workspace.argSet(variable)
        return lam.getRealValue(variable)
