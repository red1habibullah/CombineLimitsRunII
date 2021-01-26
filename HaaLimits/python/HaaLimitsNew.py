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

import CombineLimitsRunII.Limits.Models as Models
from CombineLimitsRunII.Limits.Limits import Limits
from CombineLimitsRunII.Limits.utilities import *

import CombineLimitsRunII.Plotter.CMS_lumi as CMS_lumi
import CombineLimitsRunII.Plotter.tdrstyle as tdrstyle

tdrstyle.setTDRStyle()

class HaaLimits(Limits):
    '''
    Create the Haa Limits workspace
    '''

    # permanent parameters
    HMASSES = [125] #,200,250,300,400,500,750,1000]
    AMASSES = [4,5,7,8,9,10,11,12,13,14,15,17,18,19,20,21]
    HAMAP = {
        125 : [4,5,7,8,9,10,11,12,13,14,15,17,18,19,20,21],
        200 : [5,9,15],
        250 : [5,9,15],
        300 : [5,7,9,11,13,15,17,19,21],
        400 : [5,9,15],
        500 : [5,9,15],
        750 : [5,7,9,11,13,15,17,19,21],
        1000: [5,9,15],
    }

    HBINNING = 25 # GeV
    ABINNING = 0.1 # GeV

    SPLITBGS = True # False doesnt work!
    SKIPPLOTS = False

    XVAR = 'CMS_haa_x'

    SIGNAME = 'HToAAH{h}A{a}'
    SPLINENAME = 'ggH_haa_{h}'
    ALABEL = 'm_{a}'
    ARANGE = [0,25]
    HLABEL = 'm_{H}'
    HRANGE = [0,1200]

    XRANGE = [4,25]
    XBINNING = 210
    XLABEL = 'm_{#mu#mu}'
    UPSILONRANGE = [7, 12]

    CHANNELS = ''
    REGIONS = ['PP','FP']
    SHIFTS = []
    BACKGROUNDSHIFTS = []
    SIGNALSHIFTS = []
    QCDSHIFTS = [] # note, max/min of all (excluding 0.5/2)

    FIXFP = False

    COLORS = {
        125 : ROOT.kBlack,
        200 : ROOT.kMagenta,
        250 : ROOT.kCyan+1,
        300 : ROOT.kBlue,
        400 : ROOT.kRed,
        500 : ROOT.kOrange-3,
        750 : ROOT.kGreen+2,
        1000: ROOT.kViolet-1,
        5   : ROOT.kBlack,
        9   : ROOT.kBlue,
        15  : ROOT.kGreen+2,
    }
        

    def __init__(self,histMap,tag='',do2DInterpolation=False,doParamFit=False):
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

        top = [k for k in self.histMap.keys() if self.REGIONS[0] in k][0]
        sample = self.histMap[top][''].keys()[0]

        self.binned = self.histMap[top][''][sample].InheritsFrom('TH1')

        self.plotDir = 'figures/HaaLimits{}'.format('_'+tag if tag else '')
        self.fitsDir = 'fitParams/HaaLimits{}'.format('_'+tag if tag else '')

        self.do2D = do2DInterpolation
        if self.do2D:
            self.SPLINENAME = 'ggH_haa'
        self.doParamFit = doParamFit

    def rstrip(self,obj,string):
        if obj.endswith(string): obj = obj[:-1*len(string)]
        return obj

    def dump(self,name,results):
        with open(name,'w') as f:
            f.write(json.dumps(results, indent=4, sort_keys=True))
        with open(name.replace('.json','.pkl'),'wb') as f:
            pickle.dump(results,f)

    def load(self,name):
        with open(name.replace('.json','.pkl'),'rb') as f:
            results = pickle.load(f)
        return results

    def aToFloat(self,a):
        return float(str(a).replace('p','.'))

    def aToStr(self,a):
        return str(a).replace('.','p') if '.' in str(a) and not str(a).endswith('0') else int(a)

    def aSorted(self,As):
        avals = sorted([self.aToFloat(a) for a in As])
        return [self.aToStr(a) for a in avals]

    ###########################
    ### Workspace utilities ###
    ###########################
    def initializeWorkspace(self,**kwargs):
        logging.debug('initializeWorkspace')
        logging.debug(str(kwargs))
        self.addVar(self.XVAR,*self.XRANGE,unit='GeV',label=self.XLABEL,**kwargs)
        self.addMH(*self.HRANGE,unit='GeV',label=self.HLABEL,**kwargs)
        self.addMA(*self.ARANGE,unit='GeV',label=self.ALABEL,**kwargs)

    def buildModel(self, region, **kwargs):
        logging.debug('buildModel')
        logging.debug(', '.join([region,str(kwargs)]))
        workspace = kwargs.pop('workspace',self.workspace)
        xVar = kwargs.pop('xVar',self.XVAR)
        tag = kwargs.pop('tag',region)

        bgRes = Models.Voigtian
        #bgRes = Models.BreitWigner
        #bgResCB = Models.CrystalBall
        #bgRes = Models.DoubleCrystalBall
        #bgResDCB = Models.DoubleCrystalBall

        # jpsi
        nameJ1b = 'jpsi1S'
        
        workspace.factory('{0}[{1}, {2}, {3}]'.format('mean_{}'.format(nameJ1b), *[3.1,2.9,3.2]))
        workspace.factory('{0}[{1}, {2}, {3}]'.format('sigma_{}'.format(nameJ1b),*[0.035,0.001,0.5]))
        workspace.factory('{0}[{1}, {2}, {3}]'.format('width_{}'.format(nameJ1b),*[0.035,0.001,0.5]))
        workspace.factory('{0}[{1}, {2}, {3}]'.format('a_{}'.format( nameJ1b),*[1.9,0.001,10]))
        workspace.factory('{0}[{1}, {2}, {3}]'.format('n_{}'.format( nameJ1b),*[1.7,0.001,20]))
        workspace.factory('{0}[{1}, {2}, {3}]'.format('a1_{}'.format(nameJ1b),*[1.9,0.001,10]))
        workspace.factory('{0}[{1}, {2}, {3}]'.format('n1_{}'.format(nameJ1b),*[1.7,0.001,20]))
        workspace.factory('{0}[{1}, {2}, {3}]'.format('a2_{}'.format(nameJ1b),*[2.4,0.001,10]))
        workspace.factory('{0}[{1}, {2}, {3}]'.format('n2_{}'.format(nameJ1b),*[1.0,0.001,20]))
        jpsi1S = bgRes('jpsi1S',
            x = xVar,
            mean  = 'mean_{}'.format(nameJ1b),
            sigma = 'sigma_{}'.format(nameJ1b),
            width = 'width_{}'.format(nameJ1b),
            a  = 'a_{}'.format( nameJ1b),
            n  = 'n_{}'.format( nameJ1b),
            a1 = 'a1_{}'.format(nameJ1b),
            n1 = 'n1_{}'.format(nameJ1b),
            a2 = 'a2_{}'.format(nameJ1b),
            n2 = 'n2_{}'.format(nameJ1b),
        )
        nameJ1 = '{}{}'.format(nameJ1b,'_'+tag if tag else '')
        jpsi1S.build(workspace,nameJ1)
    
        nameJ2b = 'jpsi2S'
        workspace.factory('{0}[{1}, {2}, {3}]'.format('mean_{}'.format(nameJ2b), *[3.7,3.6,3.8]))
        workspace.factory('{0}[{1}, {2}, {3}]'.format('sigma_{}'.format(nameJ2b),*[0.04,0.001,0.5]))
        workspace.factory('{0}[{1}, {2}, {3}]'.format('width_{}'.format(nameJ2b),*[0.01,0.001,0.5]))
        workspace.factory('{0}[{1}, {2}, {3}]'.format('a_{}'.format( nameJ2b),*[2,0.001,10]))
        workspace.factory('{0}[{1}, {2}, {3}]'.format('n_{}'.format( nameJ2b),*[2,0.001,20]))
        workspace.factory('{0}[{1}, {2}, {3}]'.format('a1_{}'.format(nameJ2b),*[2,0.001,10]))
        workspace.factory('{0}[{1}, {2}, {3}]'.format('n1_{}'.format(nameJ2b),*[2,0.0001,20]))
        workspace.factory('{0}[{1}, {2}, {3}]'.format('a2_{}'.format(nameJ2b),*[2,0.001,10]))
        workspace.factory('{0}[{1}, {2}, {3}]'.format('n2_{}'.format(nameJ2b),*[2,0.0001,20]))
        jpsi2S = bgRes('jpsi2S',
            x = xVar,
            mean  = 'mean_{}'.format(nameJ2b),
            sigma = 'sigma_{}'.format(nameJ2b),
            width = 'width_{}'.format(nameJ2b),
            a  = 'a_{}'.format( nameJ2b),
            n  = 'n_{}'.format( nameJ2b),
            a1 = 'a1_{}'.format(nameJ2b),
            n1 = 'n1_{}'.format(nameJ2b),
            a2 = 'a2_{}'.format(nameJ2b),
            n2 = 'n2_{}'.format(nameJ2b),
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
        workspace.factory('{0}[{1}, {2}, {3}]'.format('a_{}'.format( nameU1b),*[2,0.001,10]))
        workspace.factory('{0}[{1}, {2}, {3}]'.format('n_{}'.format( nameU1b),*[2,0.001,20]))
        workspace.factory('{0}[{1}, {2}, {3}]'.format('a1_{}'.format(nameU1b),*[2,0.001,10]))
        workspace.factory('{0}[{1}, {2}, {3}]'.format('n1_{}'.format(nameU1b),*[2,0.001,20]))
        workspace.factory('{0}[{1}, {2}, {3}]'.format('a2_{}'.format(nameU1b),*[2,0.001,10]))
        workspace.factory('{0}[{1}, {2}, {3}]'.format('n2_{}'.format(nameU1b),*[2,0.001,20]))
        upsilon1S = bgRes('upsilon1S',
            x = xVar,
            mean  = 'mean_{}'.format(nameU1b),
            sigma = 'sigma_{}'.format(nameU1b),
            width = 'width_{}'.format(nameU1b),
            a  = 'a_{}'.format( nameU1b),
            n  = 'n_{}'.format( nameU1b),
            a1 = 'a1_{}'.format(nameU1b),
            n1 = 'n1_{}'.format(nameU1b),
            a2 = 'a2_{}'.format(nameU1b),
            n2 = 'n2_{}'.format(nameU1b),
        )
        nameU1 = '{}{}'.format(nameU1b,'_'+tag if tag else '')
        upsilon1S.build(workspace,nameU1)
    
        nameU2b = 'upsilon2S'
        workspace.factory('{0}[{1}, {2}, {3}]'.format('mean_{}'.format(nameU2b), *[10.0,9.8,10.15]))
        workspace.factory('{0}[{1}, {2}, {3}]'.format('sigma_{}'.format(nameU2b),*[0.06,0,0.3]))
        workspace.factory('{0}[{1}, {2}, {3}]'.format('width_{}'.format(nameU2b),*[0.1,0.01,1]))
        workspace.factory('{0}[{1}, {2}, {3}]'.format('a_{}'.format( nameU2b),*[2,0.001,10]))
        workspace.factory('{0}[{1}, {2}, {3}]'.format('n_{}'.format( nameU2b),*[2,0.001,20]))
        workspace.factory('{0}[{1}, {2}, {3}]'.format('a1_{}'.format(nameU2b),*[2,0.001,10]))
        workspace.factory('{0}[{1}, {2}, {3}]'.format('n1_{}'.format(nameU2b),*[2,0.001,20]))
        workspace.factory('{0}[{1}, {2}, {3}]'.format('a2_{}'.format(nameU2b),*[2,0.001,10]))
        workspace.factory('{0}[{1}, {2}, {3}]'.format('n2_{}'.format(nameU2b),*[2,0.001,20]))
        upsilon2S = bgRes('upsilon2S',
            x = xVar,
            mean  = 'mean_{}'.format(nameU2b),
            sigma = 'sigma_{}'.format(nameU2b),
            width = 'width_{}'.format(nameU2b),
            a  = 'a_{}'.format( nameU2b),
            n  = 'n_{}'.format( nameU2b),
            a1 = 'a1_{}'.format(nameU2b),
            n1 = 'n1_{}'.format(nameU2b),
            a2 = 'a2_{}'.format(nameU2b),
            n2 = 'n2_{}'.format(nameU2b),
        )
        nameU2 = '{}{}'.format(nameU2b,'_'+tag if tag else '')
        upsilon2S.build(workspace,nameU2)
    
        nameU3b = 'upsilon3S'
        workspace.factory('{0}[{1}, {2}, {3}]'.format('mean_{}'.format(nameU3b), *[10.3,10.22,10.5]))
        workspace.factory('{0}[{1}, {2}, {3}]'.format('sigma_{}'.format(nameU3b),*[0.07,0,0.3]))
        workspace.factory('{0}[{1}, {2}, {3}]'.format('width_{}'.format(nameU3b),*[0.1,0.01,1]))
        workspace.factory('{0}[{1}, {2}, {3}]'.format('a_{}'.format( nameU3b),*[2,0.001,10]))
        workspace.factory('{0}[{1}, {2}, {3}]'.format('n_{}'.format( nameU3b),*[2,0.001,20]))
        workspace.factory('{0}[{1}, {2}, {3}]'.format('a1_{}'.format(nameU3b),*[2,0.001,10]))
        workspace.factory('{0}[{1}, {2}, {3}]'.format('n1_{}'.format(nameU3b),*[2,0.001,20]))
        workspace.factory('{0}[{1}, {2}, {3}]'.format('a2_{}'.format(nameU3b),*[2,0.001,10]))
        workspace.factory('{0}[{1}, {2}, {3}]'.format('n2_{}'.format(nameU3b),*[2,0.001,20]))
        upsilon3S = bgRes('upsilon3S',
            x = xVar,
            mean  = 'mean_{}'.format(nameU3b),
            sigma = 'sigma_{}'.format(nameU3b),
            width = 'width_{}'.format(nameU3b),
            a  = 'a_{}'.format( nameU3b),
            n  = 'n_{}'.format( nameU3b),
            a1 = 'a1_{}'.format(nameU3b),
            n1 = 'n1_{}'.format(nameU3b),
            a2 = 'a2_{}'.format(nameU3b),
            n2 = 'n2_{}'.format(nameU3b),
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

        doPoly = False
        doPolyExpo = False

        # continuum background
        if doPoly:
            if self.XRANGE[0]<4 and  'control' in region:
                order = 5
            else:
                order = 1
            nameC = 'cont{}'.format('_'+tag if tag else '')
            cont = Models.Chebychev(nameC,
                                    x = xVar,
                                    order = order,
            )
            cont.build(workspace,nameC)

        elif doPolyExpo:
            nameC = 'cont{}'.format('_'+tag if tag else '')
            cont = Models.ExpoPoly(nameC,
                x = xVar,
                order = 3,
            )
            cont.build(workspace,nameC)

        else:
            if self.XRANGE[0]<4:
                nameC1 = 'cont1{}'.format('_'+tag if tag else '')
                #nameC1 = 'cont1'
                cont1 = Models.Exponential(nameC1,
                    x = xVar,
                    lamb = kwargs.pop('lambda_{}'.format(nameC1),[-2,-4,0]), #-2,-3,-1
                )
                cont1.build(workspace,nameC1)

                nameC2 = 'cont2{}'.format('_'+tag if tag else '')
                cont2 = Models.Exponential(nameC2,
                    x = xVar,
                    lamb = kwargs.pop('lambda_{}'.format(nameC2),[-0.6,-2,0]), #-5
                )

                #nameC2 = 'cont_poly{}'.format('_'+tag if tag else '')
                # cont_poly = Models.Chebychev(nameC2,
                #                     x = xVar,
                #                     order = 7,
                #                     )
                
                cont2.build(workspace,nameC2)

                nameC = 'cont{}'.format('_'+tag if tag else '')
                #cont = {'extended': True}
                cont = {'recursive': True}
                cont[nameC1] = [0.70,0,1]
                cont[nameC2] = [0.20,0,1]
                cont = Models.Sum(nameC, **cont)
                cont.build(workspace,nameC)
            else:
                nameC = 'cont1{}'.format('_'+tag if tag else '')
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
        interrs = results['integralerrs']
        return vals, errs, ints, interrs

    def fitSignal(self,h,a,region,shift='',**kwargs):
        scale = kwargs.get('scale',1)
        if isinstance(scale,dict): scale = scale.get(self.SIGNAME.format(h=h,a=a),1)
        results = kwargs.get('results',{})
        histMap = self.histMap[region][shift]
        tag = kwargs.get('tag','{}{}'.format(region,'_'+shift if shift else ''))

        aval = self.aToFloat(a)
        ws = ROOT.RooWorkspace('sig')
        ws.factory('{0}[{1}, {2}]'.format(self.XVAR,*self.XRANGE))
        ws.var(self.XVAR).setUnit('GeV')
        ws.var(self.XVAR).setPlotLabel(self.XLABEL)
        ws.var(self.XVAR).SetTitle(self.XLABEL)
        model = Models.Voigtian('sig',
            x = self.XVAR,
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
        results, errors = model.fit(ws, hist, name, saveDir=saveDir, save=True, doErrors=True, xRange=[0.9*aval,1.1*aval])
        if self.binned:
            integral = histMap[self.SIGNAME.format(h=h,a=a)].Integral() * scale
            integralerr = getHistogramIntegralError(histMap[self.SIGNAME.format(h=h,a=a)]) * scale
        else:
            integral = histMap[self.SIGNAME.format(h=h,a=a)].sumEntries('{0}>{1} && {0}<{2}'.format(self.XVAR,*self.XRANGE)) * scale
            integralerr = getDatasetIntegralError(histMap[self.SIGNAME.format(h=h,a=a)],'{0}>{1} && {0}<{2}'.format(self.XVAR,*self.XRANGE)) * scale

        savedir = '{}/{}'.format(self.fitsDir,shift if shift else 'central')
        python_mkdir(savedir)
        savename = '{}/h{}_a{}_{}.json'.format(savedir,h,a,tag)
        jsonData = {'vals': results, 'errs': errors, 'integrals': integral, 'integralerrs': integralerr}
        self.dump(savename,jsonData)

        return results, errors, integral, integralerr
        

    def fitSignals(self,region,shift='',**kwargs):
        '''
        Fit the signal model for a given Higgs mass.
        Required arguments:
            h = higgs mass
        '''
        load = kwargs.get('load',False)
        skipFit = kwargs.get('skipFit',False)
        tag = kwargs.get('tag','{}{}'.format(region,'_'+shift if shift else ''))

        histMap = self.histMap[region][shift]

        # initial fit
        if load:
            # load the previous fit
            results, errors, integrals, integralerrs = self.loadSignalFits(tag,region,shift)
        elif shift and not skipFit:
            # load the central fits
            cresults, cerrors, cintegrals, cintegralerrs = self.loadSignalFits(region,region)
        if not skipFit:
            results = {}
            errors = {}
            integrals = {}
            integralerrs = {}

            for h in self.HMASSES:
                results[h] = {}
                errors[h] = {}
                integrals[h] = {}
                integralerrs[h] = {}

                amasses = self.HAMAP[h]
                avals = [self.aToFloat(x) for x in amasses]

                for a in amasses:
                    if load or (shift and not skipFit):
                        results[h][a], errors[h][a], integrals[h][a], integralerrs[h][a] = self.fitSignal(h,a,region,shift,results=cresults[h][a],**kwargs)
                    elif not skipFit:
                        results[h][a], errors[h][a], integrals[h][a], integralerrs[h][a] = self.fitSignal(h,a,region,shift,**kwargs)
    
        savedir = '{}/{}'.format(self.fitsDir,shift if shift else 'central')
        python_mkdir(savedir)
        savename = '{}/{}.json'.format(savedir,tag)
        jsonData = {'vals': results, 'errs': errors, 'integrals': integrals, 'integralerrs': integralerrs}
        self.dump(savename,jsonData)

        fitFuncs = self.fitSignalParams(results,errors,integrals,integralerrs,region,shift)

        return results, errors, integrals, integralerrs, fitFuncs

    def fitSignalParams(self,results,errors,integrals,integralerrs,region,shift='',**kwargs):
        tag = kwargs.get('tag','{}{}'.format(region,'_'+shift if shift else ''))
        # Fit using ROOT rather than RooFit for the splines
        if self.do2D:
            fitFuncs = {
                'mean' :    ROOT.TF2('mean_{}'.format(tag),     '[0]+[1]*x+[2]*y',                           *self.HRANGE+self.ARANGE), 
                'width':    ROOT.TF2('width_{}'.format(tag),    '[0]+[1]*x+[2]*y+[3]*x*y+[4]*x*x+[5]*y*y',   *self.HRANGE+self.ARANGE), 
                'sigma':    ROOT.TF2('sigma_{}'.format(tag),    '[0]+[1]*x+[2]*y+[3]*x*y+[4]*x*x+[5]*y*y',   *self.HRANGE+self.ARANGE), 
                #'integral': ROOT.TF2('integral_{}'.format(tag), 'exp([0]+[1]*x)*([2]+[3]*y+[4]*y*y+[5]*x*y+[6]*y*y*y+[7]*y*y*y*y)',*self.HRANGE+self.ARANGE),
                #'integral': ROOT.TF2('integral_{}'.format(tag), '[0]+[1]*x+[2]*y+[3]*x*x+[4]*y*y+[5]*x*y+[6]*y*y*y+[7]*y*y*y*y',*self.HRANGE+self.ARANGE),
                'integral': ROOT.TF2('integral_{}'.format(tag), '[0]+[1]*x+TMath::Erf([2]+[3]*y+[4]*x)*TMath::Erfc([5]+[6]*y+[7]*x)',*self.HRANGE+self.ARANGE),
            }
            #fitFuncs['integral'].SetParameter(2,-0.005)
            #fitFuncs['integral'].SetParameter(3,0.02)
            #fitFuncs['integral'].SetParameter(5,-0.5)
            #fitFuncs['integral'].SetParameter(6,0.08)
            pp = [-0.426558,0.00260027,0.337455,0.149909,-0.00133535,1.00036,0.0130436,-0.00668657]
            fp = [-1.56521,0.000395383,1.06745,0.0843899,-0.000684469,-0.503411,0.0102577,-0.00216701]
            for i in range(8): fitFuncs['integral'].SetParameter(i,fp[i])
        else:
            fitFuncs = {}
            for h in self.HMASSES:
                fitFuncs[h] = {
                    'mean' :    ROOT.TF1('mean_h{}_{}'.format(h,tag),     '[0]+[1]*x',         *self.ARANGE), 
                    'width':    ROOT.TF1('width_h{}_{}'.format(h,tag),    '[0]+[1]*x+[2]*x*x', *self.ARANGE), 
                    'sigma':    ROOT.TF1('sigma_h{}_{}'.format(h,tag),    '[0]+[1]*x+[2]*x*x', *self.ARANGE), 
                    #'integral': ROOT.TF1('integral_h{}_{}'.format(h,tag), '[0]+[1]*x+[2]*x*x+[3]*x*x*x+[4]*x*x*x*x', *self.ARANGE),
                    'integral': ROOT.TF1('integral_h{}_{}'.format(h,tag), '[0]+TMath::Erf([1]+[2]*x)*TMath::Erfc([3]+[4]*x)', *self.ARANGE),
                    #'integral'      : ROOT.TF1('integral_h{}_{}'.format(h,tag),  '[0]+[1]*x+[2]*x*x', *self.ARANGE),
                }
                # set initial values
                fitFuncs[h]['integral'].SetParameter(1,-0.005)
                fitFuncs[h]['integral'].SetParameter(2,0.02)
                fitFuncs[h]['integral'].SetParameter(3,-0.5)
                fitFuncs[h]['integral'].SetParameter(4,0.08)

        for param in ['mean','width','sigma','integral']:
            Hs = sorted(results)
            As = {h: [self.aToStr(a) for a in sorted([self.aToFloat(x) for x in results[h]])] for h in Hs}
            xvals = [h for h in Hs for a in As[h]]
            xerrs = [0] * len(xvals)
            yvals = [self.aToFloat(a) for h in Hs for a in As[h]]
            yerrs = [0] * len(yvals)
            if param=='integral':
                zvals = [integrals[h][a] for h in Hs for a in As[h]]
                zerrs = [integralerrs[h][a] for h in Hs for a in As[h]]
            else:
                zvals = [results[h][a]['{}_h{}_a{}_{}'.format(param,h,a,tag)] for h in Hs for a in As[h]]
                zerrs = [errors[h][a]['{}_h{}_a{}_{}'.format(param,h,a,tag)] for h in Hs for a in As[h]]
            if self.do2D:
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

            for h in [125]: #,300,750]:
                xs = [yvals[i] for i in range(len(xvals)) if xvals[i]==h]
                ys = [zvals[i] for i in range(len(xvals)) if xvals[i]==h]

                g = ROOT.TGraph(len(xs),array('d',xs),array('d',ys))
                if not self.do2D:
                    g.Fit(fitFuncs[h][param])
                    g = ROOT.TGraph(len(xs),array('d',xs),array('d',ys)) # override so we dont plot the fits here
                g.SetLineColor(self.COLORS[h])
                g.SetMarkerColor(self.COLORS[h])
                g.SetTitle('H({h})'.format(h=h))

                legend.AddEntry(g,g.GetTitle(),'lp')
                mg.Add(g)

                fxs = []
                fys = []
                for a in range(self.ARANGE[0]*10,self.ARANGE[1]*10+1,1):
                    if self.do2D:
                        y = fitFuncs[param].Eval(h,a*0.1)
                    else:
                        y = fitFuncs[h][param].Eval(a*0.1)
                    fxs += [a*0.1]
                    fys += [y]
                fg = ROOT.TGraph(len(fxs),array('d',fxs),array('d',fys))
                fg.SetLineColor(self.COLORS[h])
                fg.SetLineWidth(3)
                fg.SetMarkerColor(self.COLORS[h])
                fmg.Add(fg)

            canvas.DrawFrame(self.ARANGE[0],min(zvals)*0.9,self.ARANGE[1],max(zvals)*1.1)
            if self.doParamFit:
                mg.Draw('p0')
            else:
                mg.Draw('L p0')
            mg.GetXaxis().SetTitle(self.ALABEL)
            mg.GetYaxis().SetTitle(param)
            if self.doParamFit: fmg.Draw('L')
            legend.Draw()
            canvas.Print('{}.png'.format(savename))

            if self.do2D:
                savename = '{}/{}_Fit_vsH'.format(savedir,name)

                canvas = ROOT.TCanvas(savename,savename,800,800)
                canvas.SetTopMargin(0.1)

                mg = ROOT.TMultiGraph()
                fmg = ROOT.TMultiGraph()

                legend = ROOT.TLegend(0.1,0.9,0.9,1.0,'','NDC')
                legend.SetTextFont(42)
                legend.SetBorderSize(0)
                legend.SetFillColor(0)
                legend.SetNColumns(len(self.HMASSES))

                for a in [5,9,15]:
                    xs = [xvals[i] for i in range(len(xvals)) if yvals[i]==a]
                    ys = [zvals[i] for i in range(len(xvals)) if yvals[i]==a]

                    g = ROOT.TGraph(len(xs),array('d',xs),array('d',ys))
                    g.SetLineColor(self.COLORS[a])
                    g.SetMarkerColor(self.COLORS[a])
                    g.SetTitle('a({a})'.format(a=a))

                    legend.AddEntry(g,g.GetTitle(),'lp')
                    mg.Add(g)

                    fxs = []
                    fys = []
                    for h in range(self.HRANGE[0]*10,self.HRANGE[1]*10+1,1):
                        y = fitFuncs[param].Eval(h*0.1,a)
                        fxs += [h*0.1]
                        fys += [y]
                    fg = ROOT.TGraph(len(fxs),array('d',fxs),array('d',fys))
                    fg.SetLineColor(self.COLORS[a])
                    fg.SetLineWidth(3)
                    fg.SetMarkerColor(self.COLORS[a])
                    fmg.Add(fg)

                canvas.DrawFrame(self.HRANGE[0],min(zvals)*0.9,self.HRANGE[1],max(zvals)*1.1)
                if self.doParamFit:
                    mg.Draw('p0')
                else:
                    mg.Draw('L p0')
                mg.GetXaxis().SetTitle(self.HLABEL)
                mg.GetYaxis().SetTitle(param)
                if self.doParamFit: fmg.Draw('L')
                legend.Draw()
                canvas.Print('{}.png'.format(savename))


        return fitFuncs

    def fitToList(self,fit,xvals):
        yvals = [fit.Eval(x) for x in xvals]
        return yvals

    def buildSpline(self,vals,errs,integrals,integralerrs,region,shifts=[],**kwargs):
        '''
        Get the signal spline for a given Higgs mass.
        Required arguments:
            h = higgs mass
            vals = dict with fitted param values
            errs = dict with fitted param errors
            integrals = dict with integrals for given distribution
            integralerrs = dict with integral errors for given distribution

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
        xVar = kwargs.pop('xVar',self.XVAR)
        fitFuncs = kwargs.get('fitFuncs',{})

        amasses = []
        a = self.ARANGE[0]
        while a<=self.ARANGE[1]:
            amasses += [a]
            a += self.ABINNING

        hmasses = []
        h = self.HRANGE[0]
        while h<=self.HRANGE[1]:
            hmasses += [h]
            h += self.HBINNING


        splines = {}
        params = ['mean','width','sigma']
        if self.doParamFit:
            for param in params+['integral']:
                if self.do2D:
                    name = '{param}_{splinename}_{region}'.format(param=param,region=region,splinename=self.SPLINENAME)
                    spline = Models.Spline(name,
                        MH = ['MH','MA'],
                        masses = None,
                        values = fitFuncs[''][param],
                        shifts = {shift: {'up': fitFuncs[shift+'Up'][param], 'down': fitFuncs[shift+'Down'][param],} for shift in shifts},
                    )
                    spline.build(workspace, name)
                    splines[name] = spline
                else:
                    for h in self.HMASSES:
                        name = '{param}_{splinename}_{region}'.format(param=param,region=region,splinename=self.SPLINENAME.format(h=h))
                        # here is using the TF1
                        #spline = Models.Spline(name,
                        #    MH = 'MA',
                        #    masses = None,
                        #    values = fitFuncs[''][h][param],
                        #    shifts = {shift: {'up': fitFuncs[shift+'Up'][h][param], 'down': fitFuncs[shift+'Down'][h][param],} for shift in shifts},
                        #)
                        # here is converting to a spline first
                        spline = Models.Spline(name,
                            MH = 'MA',
                            masses = amasses,
                            values = self.fitToList(fitFuncs[''][h][param],amasses),
                            shifts = {shift: 
                                {
                                    'up'  : self.fitToList(fitFuncs[shift+'Up'][h][param],amasses), 
                                    'down': self.fitToList(fitFuncs[shift+'Down'][h][param],amasses),
                                } for shift in shifts},
                        )
                        spline.build(workspace, name)
                        splines[name] = spline

            # create model
            if self.do2D:
                model = Models.Voigtian(self.SPLINENAME,
                    x = xVar,
                    **{param: '{param}_{splinename}_{region}'.format(param=param, splinename=self.SPLINENAME, region=region) for param in params}
                )
                model.build(workspace,'{}_{}'.format(self.SPLINENAME,region))

                return model
            else:
                models = {}
                for h in self.HMASSES:
                    model = Models.Voigtian(self.SPLINENAME.format(h=h),
                        x = xVar,
                        **{param: '{param}_{splinename}_{region}'.format(param=param, splinename=self.SPLINENAME.format(h=h), region=region) for param in params}
                    )
                    model.build(workspace,'{}_{}'.format(self.SPLINENAME.format(h=h),region))
                    models[h] = model

                return models



        # create parameter splines
        for param in params:
            if self.do2D:
                name = '{param}_{region}'.format(param=param,region=region)
                paramMasses = [[],[]]
                paramValues = []
                paramShifts = {}
                for h in sorted(vals['']):
                    for a in self.aSorted(vals[''][h]):
                        paramMasses[0] += [h]
                        paramMasses[1] += [self.aToFloat(a)]
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
            else:
                for h in self.HMASSES:
                    name = '{param}_h{h}_{region}'.format(param=param,region=region,h=h)
                    paramMasses = []
                    paramValues = []
                    paramShifts = {}
                    for a in self.aSorted(vals[''][h]):
                        paramMasses += [self.aToFloat(a)]
                        paramValues += [vals[''][h][a]['{param}_h{h}_a{a}_{region}'.format(param=param,h=h,a=a,region=region)]]
                        for shift in shifts:
                            if shift not in paramShifts: paramShifts[shift] = {'up': [], 'down': []}
                            paramShifts[shift]['up']   += [vals[shift+'Up'  ][h][a]['{param}_h{h}_a{a}_{region}_{shift}Up'.format(  param=param,h=h,a=a,region=region,shift=shift)]]
                            paramShifts[shift]['down'] += [vals[shift+'Down'][h][a]['{param}_h{h}_a{a}_{region}_{shift}Down'.format(param=param,h=h,a=a,region=region,shift=shift)]]
                    spline = Models.Spline(name,
                        MH = 'MA',
                        masses = paramMasses,
                        values = paramValues,
                        shifts = paramShifts,
                    )
                    spline.build(workspace, name)
                    splines[name] = spline

        # integral spline
        if self.do2D:
            name = 'integral_{}_{}'.format(self.SPLINENAME,region)
            paramMasses = [[],[]]
            paramValues = []
            paramShifts = {}
            for h in sorted(vals['']):
                for a in self.aSorted(vals[''][h]):
                    paramMasses[0] += [h]
                    paramMasses[1] += [self.aToFloat(a)]
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
        else:
            for h in self.HMASSES:
                name = 'integral_{}_{}'.format(self.SPLINENAME.format(h=h),region)
                paramMasses = []
                paramValues = []
                paramShifts = {}
                for a in self.aSorted(vals[''][h]):
                    paramMasses += [self.aToFloat(a)]
                    paramValues += [integrals[''][h][a]]
                    for shift in shifts:
                        if shift not in paramShifts: paramShifts[shift] = {'up': [], 'down': []}
                        paramShifts[shift]['up']   += [integrals[shift+'Up'  ][h][a]]
                        paramShifts[shift]['down'] += [integrals[shift+'Down'][h][a]]
                spline = Models.Spline(name,
                    MH = 'MA',
                    masses = paramMasses,
                    values = paramValues,
                    shifts = paramShifts,
                )
                spline.build(workspace, name)
                splines[name] = spline

        # create model
        if self.do2D:
            model = Models.Voigtian(self.SPLINENAME,
                x = xVar,
                **{param: '{param}_{region}'.format(param=param, region=region) for param in params}
            )
            model.build(workspace,'{}_{}'.format(self.SPLINENAME,region))

            return model
        else:
            models = {}
            for h in self.HMASSES:
                model = Models.Voigtian(self.SPLINENAME.format(h=h),
                    x = xVar,
                    **{param: '{param}_h{h}_{region}'.format(param=param, region=region, h=h) for param in params}
                )
                model.build(workspace,'{}_{}'.format(self.SPLINENAME.format(h=h),region))
                models[h] = model

            return models

    def plotModelX(self,workspace,xVar,data,model,region,shift='',**kwargs):
        xRange = kwargs.pop('xRange',[])
        postfix = kwargs.pop('postfix','')

        if xRange:
            xFrame = workspace.var(xVar).frame(ROOT.RooFit.Range(*xRange))
        else:
            xFrame = workspace.var(xVar).frame()
        data.plotOn(xFrame)
        if not self.SKIPPLOTS:
            if region == 'control':
                model.plotOn(xFrame,ROOT.RooFit.Components('cont_{}'.format(region)),ROOT.RooFit.LineStyle(ROOT.kDashed))
                model.plotOn(xFrame,ROOT.RooFit.Components('cont1_{}'.format(region)),ROOT.RooFit.LineStyle(ROOT.kDashed))
                model.plotOn(xFrame,ROOT.RooFit.Components('cont2_{}'.format(region)),ROOT.RooFit.LineStyle(ROOT.kDashed))
            else:
                model.plotOn(xFrame,ROOT.RooFit.Components('cont_{}_x'.format(region)),ROOT.RooFit.LineStyle(ROOT.kDashed))
                model.plotOn(xFrame,ROOT.RooFit.Components('cont1_{}_x'.format(region)),ROOT.RooFit.LineStyle(ROOT.kDashed))
                model.plotOn(xFrame,ROOT.RooFit.Components('cont2_{}_x'.format(region)),ROOT.RooFit.LineStyle(ROOT.kDashed))
            #model.plotOn(xFrame,ROOT.RooFit.Components('cont'),ROOT.RooFit.LineStyle(ROOT.kDashed))
            #model.plotOn(xFrame,ROOT.RooFit.Components('cont1'),ROOT.RooFit.LineStyle(ROOT.kDashed))
            #model.plotOn(xFrame,ROOT.RooFit.Components('cont2'),ROOT.RooFit.LineStyle(ROOT.kDashed))
            if self.XRANGE[0]<4 and region=='control':
                # jpsi
                model.plotOn(xFrame,ROOT.RooFit.Components('jpsi1S_{}'.format(region)),ROOT.RooFit.LineColor(ROOT.kRed))
                model.plotOn(xFrame,ROOT.RooFit.Components('jpsi2S_{}'.format(region)),ROOT.RooFit.LineColor(ROOT.kRed))
                #model.plotOn(xFrame,ROOT.RooFit.Components('jpsi1S'),ROOT.RooFit.LineColor(ROOT.kRed))
                #model.plotOn(xFrame,ROOT.RooFit.Components('jpsi2S'),ROOT.RooFit.LineColor(ROOT.kRed))
            elif self.XRANGE[0]<11 and region=='control':    
                model.plotOn(xFrame,ROOT.RooFit.Components('upsilon1S_{}'.format(region)),ROOT.RooFit.LineColor(ROOT.kRed))
                model.plotOn(xFrame,ROOT.RooFit.Components('upsilon2S_{}'.format(region)),ROOT.RooFit.LineColor(ROOT.kRed))
                model.plotOn(xFrame,ROOT.RooFit.Components('upsilon3S_{}'.format(region)),ROOT.RooFit.LineColor(ROOT.kRed))
            #model.plotOn(xFrame,ROOT.RooFit.Components('upsilon1S'),ROOT.RooFit.LineColor(ROOT.kRed))
            #model.plotOn(xFrame,ROOT.RooFit.Components('upsilon2S'),ROOT.RooFit.LineColor(ROOT.kRed))
            #model.plotOn(xFrame,ROOT.RooFit.Components('upsilon3S'),ROOT.RooFit.LineColor(ROOT.kRed))
            # combined model
            model.plotOn(xFrame)
        model.paramOn(xFrame,ROOT.RooFit.Layout(0.7,0.9,0.95))
        xFrame.getAttFill().SetFillStyle(0)

        if not self.SKIPPLOTS:
            resid = xFrame.residHist()
            pull = xFrame.pullHist()

        if xRange:
            xFrame2 = workspace.var(xVar).frame(ROOT.RooFit.Range(*xRange))
        else:
            xFrame2 = workspace.var(xVar).frame()
        if not self.SKIPPLOTS: xFrame2.addPlotable(pull,'P')

        canvas = ROOT.TCanvas('c','c',1200,800)
        ROOT.SetOwnership(canvas,False)
        #canvas.SetRightMargin(0.3)
        plotpad = ROOT.TPad("plotpad", "top pad", 0.0, 0.21, 1.0, 1.0)
        ROOT.SetOwnership(plotpad,False)
        plotpad.SetBottomMargin(0.00)
        plotpad.SetRightMargin(0.2)
        plotpad.Draw()
        ratiopad = ROOT.TPad("ratiopad", "bottom pad", 0.0, 0.0, 1.0, 0.21)
        ROOT.SetOwnership(ratiopad,False)
        ratiopad.SetTopMargin(0.05)
        ratiopad.SetRightMargin(0.2)
        ratiopad.SetBottomMargin(0.5)
        ratiopad.SetLeftMargin(0.16)
        ratiopad.SetTickx(1)
        ratiopad.SetTicky(1)
        ratiopad.Draw()
        if plotpad != ROOT.TVirtualPad.Pad(): plotpad.cd()
        xFrame.Draw()
        #prims = canvas.GetListOfPrimitives()
        prims = plotpad.GetListOfPrimitives()
        for prim in prims:
            #print "paramBox:", prim.GetName(), prim
            if 'paramBox' in prim.GetName():
                prim.SetTextSize(0.02)
                #print prim.GetX1NDC(), prim.GetX2NDC(), prim.GetY1NDC(), prim.GetY2NDC()
                prim.SetX1NDC(0.5)
                prim.SetX2NDC(0.9)
                prim.SetY1NDC(0.6)
                prim.SetY2NDC(0.9)
                print prim.GetX1NDC(), prim.GetX2NDC(), prim.GetY1NDC(), prim.GetY2NDC()
        mi = xFrame.GetMinimum()
        ma = xFrame.GetMaximum()
        if mi<0:
            xFrame.SetMinimum(0.1)
        ratiopad.cd()
        xFrame2.Draw()
        prims = ratiopad.GetListOfPrimitives()
        for prim in prims:
            if 'frame' in prim.GetName():
                prim.GetXaxis().SetLabelSize(0.09)
                prim.GetXaxis().SetTitleSize(0.21)
                prim.GetXaxis().SetTitleOffset(1.0)
                prim.GetXaxis().SetLabelOffset(0.03)
                prim.GetYaxis().SetLabelSize(0.08)
                prim.GetYaxis().SetLabelOffset(0.006)
                prim.GetYaxis().SetTitleSize(0.21)
                prim.GetYaxis().SetTitleOffset(0.35)
                prim.GetYaxis().SetNdivisions(508)
                prim.GetYaxis().SetTitle('Pull')
                prim.GetYaxis().SetRangeUser(-6,6)
                continue
        canvas.cd()
        python_mkdir(self.plotDir)
        canvas.Print('{}/model_fit_{}{}{}.png'.format(self.plotDir,region,'_'+shift if shift else '','_'+postfix if postfix else ''))
        #canvas.SetLogy(True)
        plotpad.SetLogy(True)
        canvas.Print('{}/model_fit_{}{}{}_log.png'.format(self.plotDir,region,'_'+shift if shift else '','_'+postfix if postfix else ''))

    def fitBackground(self,region,shift='', **kwargs):
        scale = kwargs.pop('scale',1)
        workspace = kwargs.pop('workspace',self.workspace)
        xVar = kwargs.pop('xVar',self.XVAR)
        model = workspace.pdf('bg_{}'.format(region))
        name = 'data_prefit_{}{}'.format(region,'_'+shift if shift else '')
        hist = self.histMap[region][shift]['dataNoSig']
        if hist.InheritsFrom('TH1'):
            integral = hist.Integral(hist.FindBin(self.XRANGE[0]),hist.FindBin(self.XRANGE[1])) * scale
            integralerr = getHistogramIntegralError(hist,hist.FindBin(self.XRANGE[0]),hist.FindBin(self.XRANGE[1])) * scale
            data = ROOT.RooDataHist(name,name,ROOT.RooArgList(workspace.var(xVar)),hist)
        else:
            integral = hist.sumEntries('{0}>{1} && {0}<{2}'.format(xVar,*self.XRANGE)) * scale
            integralerr = getDatasetIntegralError(hist,'{0}>{1} && {0}<{2}'.format(xVar,*self.XRANGE)) * scale
            # TODO add support for xVar
            data = hist.Clone(name)

        fr = model.fitTo(data, ROOT.RooFit.Save(), ROOT.RooFit.SumW2Error(True), ROOT.RooFit.PrintLevel(-1))

        workspace.var(xVar).setBins(self.XBINNING)

        #self.plotModelX(workspace,xVar,data,model,region,shift)
        if region=='control':
            if self.XRANGE[0]<4:
                self.plotModelX(workspace,xVar,data,model,region,shift,xRange=[2.5,5],postfix='jpsi')
            elif self.XRANGE[0]<11: 
                self.plotModelX(workspace,xVar,data,model,region,shift,xRange=[8,12],postfix='upsilon')
            

        pars = fr.floatParsFinal()
        vals = {}
        errs = {}
        for p in range(pars.getSize()):
            vals[pars.at(p).GetName()] = pars.at(p).getValV()
            errs[pars.at(p).GetName()] = pars.at(p).getError()

        python_mkdir(self.fitsDir)
        jfile = '{}/background_{}{}.json'.format(self.fitsDir,region,'_'+shift if shift else '')
        results = {'vals':vals, 'errs':errs, 'integral':integral, 'integralerr': integralerr}
        self.dump(jfile,results)

        return vals, errs, integral, integralerr


    ###############################
    ### Add things to workspace ###
    ###############################
    def addControlData(self,**kwargs):
        # build the models after doing the prefit stuff
        region = 'control'
        xVar = '{}_{}'.format(self.XVAR,region)
        #xVar = self.XVAR
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
        scale = kwargs.pop('scale',1)

        workspace = self.workspace

        for region in self.REGIONS:
            xVar = self.XVAR # decide if we want a different one for each region

            # build the models after doing the prefit stuff
            prebuiltParams = {p:p for p in self.background_params[region]}
            self.addVar(xVar, *self.XRANGE, unit='GeV', label=self.XLABEL, workspace=workspace)
            # this uses the parameters from the prefit with uncertainties
            self.buildModel(region=region,workspace=workspace,xVar=xVar,**prebuiltParams)
            # this just uses the initial guess
            #self.buildModel(region=region,workspace=workspace,xVar=xVar)
            self.loadBackgroundFit(region, workspace=workspace)

            x = workspace.var(xVar)
            print 'Entering workspace with x :',x
            x.setBins(self.XBINNING)
            
            # save binned data
            if doBinned:

                bgs = self.getComponentFractions(workspace.pdf('bg_{}'.format(region)))
                
                for bg in bgs:
                    bgname = bg if region in bg else '{}_{}'.format(bg,region)
                    pdf = workspace.pdf(bg)
                    integral = workspace.function('integral_{}'.format(bgname))

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
                # generate a toy data observation from the model
                model = workspace.pdf('bg_{}'.format(region))
                h = self.histMap[region]['']['dataNoSig']
                print h
                if h.InheritsFrom('TH1'):
                    integral = h.Integral(h.FindBin(self.XRANGE[0]),h.FindBin(self.XRANGE[1])) * scale
                    print "integral: " + str(integral)
                else:
                    integral = h.sumEntries('{0}>{1} && {0}<{2}'.format(xVar,*self.XRANGE)) * scale
                if asimov:
                    print "if asimov"
                    data_obs = model.generateBinned(ROOT.RooArgSet(self.workspace.var(xVar)),integral,1)
                    print data_obs
                else:
                    print "else condition"
                    data_obs = model.generate(ROOT.RooArgSet(self.workspace.var(xVar)),int(integral))
                    print data_obs
                if addSignal:
                    print " addSignal Condition "
                    # TODO, doesn't work with new setup
                    raise NotImplementedError
                    self.workspace.var('MH').setVal(mh)
                    self.workspace.var('MA').setVal(ma)
                    model = self.workspace.pdf('{}_{}'.format(self.SPLINENAME,region))
                    integral = self.workspace.function('integral_{}_{}'.format(self.SPLINENAME,region)).getVal()
                    if asimov:
                        print "asimov if condition"
                        sig_obs = model.generate(ROOT.RooArgSet(self.workspace.var(xVar)),integral,1)
                        print sig_obs
                        data_obs.add(sig_obs)
                    else:
                        print "else condition"
                        sig_obs = model.generate(ROOT.RooArgSet(self.workspace.var(xVar)),int(integral))
                        print sig_obs
                        data_obs.append(sig_obs)
                data_obs.SetName(name)
            else:
                # use the provided data
                if hist.InheritsFrom('TH1'):
                    data_obs = ROOT.RooDataHist(name,name,ROOT.RooArgList(self.workspace.var(xVar)),self.histMap[region]['']['data'])
                    
                else:
                    # TODO add support for xVar
                    data_obs = hist.Clone(name)
                    data_obs.get().find(xVar).setBins(self.XBINNING)
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
            xVar = '{}_{}'.format(self.XVAR,region)
            #xVar = self.XVAR
            name = 'data_obs_{}'.format(region)
            hist = self.histMap[region]['']['data']
            if hist.InheritsFrom('TH1'):
                data_obs = ROOT.RooDataHist(name,name,ROOT.RooArgList(self.workspace.var(xVar)),hist)
            else:
                # TODO add support for xVar
                data_obs = hist.Clone(name)
                data_obs.get().find(xVar).setBins(self.XBINNING)
            self.wsimport(data_obs, ROOT.RooFit.RecycleConflictNodes() )

    def getComponentFractions(self,model):
        logging.debug('getComponentFractions')
        logging.debug(model)
        #print "model", model
        if not model:
            print model
            raise
        if not isinstance(model,ROOT.RooAddPdf): 
            return {model.GetTitle(): []}
        pdfs = model.pdfList()
        #print "pdfs", pdfs
        coefs = model.coefList()
        #print "coefs", coefs
        result = {}
        for i in range(len(pdfs)):
            subresult = self.getComponentFractions(pdfs.at(i))
            #print "pdf:", pdfs.at(i)
            for res in subresult:
                #print "coefs:", [coefs.at(i)]
                subresult[res] += [coefs.at(i)]
            result.update(subresult)
        #print "result:", result
        logging.debug('returning')
        logging.debug(str(result))
        return result

    ### add constraints on the parameters
    def buildParams(self,region,vals,errs,integrals,integralerrs,**kwargs):
        logging.debug('buildParams')
        logging.debug(', '.join([region,str(vals),str(errs),str(integrals),str(integralerrs),str(kwargs)]))
        workspace = kwargs.pop('workspace',self.workspace)
        params = {}
        ppRegion = region.replace('FP','PP')
        fpRegion = region.replace('PP','FP')
        for param in vals[region]['']:
            if 'frac' in param: continue
            print "Building params...", region, param, self.FIXFP
            channel = region.split("_")[0]
            paramValue = vals[region][''][param]
            paramShifts = {}
            for shift in self.BACKGROUNDSHIFTS:
                shiftValueUp   = vals[region][shift+'Up'  ][param] - paramValue
                shiftValueDown = paramValue - vals[region][shift+'Down'][param]
                paramShifts[channel+"_"+shift] = {'up': shiftValueUp, 'down': shiftValueDown}
            if self.FIXFP:
                paramModel = Models.Param(param,
                    value  = paramValue,
                    shifts = paramShifts,
                )
                paramModel.build(workspace, param)
            else:
                fpValue = vals[fpRegion][''][param.replace(region,fpRegion)]
                ppValue = vals[ppRegion][''][param.replace(region,ppRegion)]
                scale   = ppValue/fpValue if fpValue else ppValue
                fpErr   = errs[fpRegion][''][param.replace(region,fpRegion)]
                if 'FP' in region:
                    workspace.factory('{}[{},{},{}]'.format(param,fpValue,fpValue-10*fpErr,fpValue+10*fpErr))
                    paramModel = None
                else:
                    print param, paramShifts, [param.replace(region,fpRegion)], scale
                    paramModel = Models.Param(param,
                        value  = '({})*@0'.format(scale),
                        valueArgs = [param.replace(region,fpRegion)],
                        shifts = paramShifts,
                    )
                    paramModel.build(workspace, param)
            params[param] = paramModel

        logging.debug('returning')
        logging.debug(str(params))
        #print "params:", params
        return params

    ### add constraints on the integrals
    def buildComponentIntegrals(self,region,vals,errs,integrals,integralerrs, pdf,**kwargs):
        logging.debug('buildComponentIntegrals')
        logging.debug(', '.join([region,str(vals),str(errs),str(integrals),str(integralerrs),str(pdf),str(kwargs)]))
        workspace = kwargs.pop('workspace',self.workspace)
        fracMap = self.getComponentFractions(pdf)
        components = sorted(fracMap.keys())
        regVals = vals
        regErrs = errs
        regInts = integrals
        regIntErrs = integralerrs
        if isinstance(integrals,dict):
            vals = vals[region]['']
            errs = errs[region]['']
            integrals = integrals[region]
            integralerrs = integralerrs[region]
        allerrors = {}
        allintegrals = {}
        integral_params = []
        for component in components:
            print "Building component integrals...", region, component
            channel = region.split("_")[0]
            subint = 1.
            suberr2 = 0.
            # TODO: errors are way larger than they should be, need to look into this
            # dont use these uncertainties
            #print fracMap.get(component,[])
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
            component = self.rstrip(component,'_x')
            component = self.rstrip(component,'_'+region)
            allerrors[component] = suberr

            print "subint integrals:",subint, integrals

            if isinstance(integrals,dict):
                paramValue = subint*integrals['']
                paramShifts = {}
                for shift in self.BACKGROUNDSHIFTS:
                    shiftValueUp   = subint*integrals[shift+'Up'  ] - paramValue
                    shiftValueDown = paramValue - subint*integrals[shift+'Down']
                    paramShifts[channel+"_"+shift] = {'up': shiftValueUp, 'down': shiftValueDown}
            else:
                paramValue = subint*integrals
            allintegrals[component] = paramValue

            name = 'integral_{}_{}'.format(component,region)
            integral_params += [name]
            if self.FIXFP:
                if isinstance(integrals,dict):
                    param = Models.Param(name,
                        value  = paramValue,
                        shifts = paramShifts,
                    )
                    param.build(workspace, name)
                else:
                    param = Models.Param(name,
                        value  = paramValue,
                    )
                    param.build(workspace, name)

            else:
                controlIntegrals = allintegrals if region=='control' else self.control_integralValues
                # 2S and 3S set to a scale factor times 1S that is common to all regions
                fpRegion = region.replace('PP','FP')
                ppRegion = region.replace('FP','PP')
                if 'PP' in region:
                    fpValue = subint*regInts[fpRegion]['']
                    ppValue = subint*regInts[ppRegion]['']
                    scale   = ppValue/fpValue if fpValue else ppValue
                    print name, paramShifts, [name.replace(region,fpRegion)], scale
                    param = Models.Param(name,
                        value  = '({})*@0'.format(scale),
                        valueArgs = [name.replace(region,fpRegion)],
                        shifts = paramShifts,
                    )
                    param.build(workspace, name)
                else:
                    if '2S' in component:
                        rname = 'relNorm_{}'.format(component)
                        if region=='control':
                            rvalue = controlIntegrals[component]/controlIntegrals[component.replace('2S','1S')]
                            workspace.factory('{}[{},{},{}]'.format(rname,rvalue,rvalue*0.5,rvalue*1.5))
                        param = Models.Param(name,
                            value = '@0*@1',
                            valueArgs = [rname,name.replace('2S','1S')],
                        )
                        param.build(workspace, name)
                    elif '3S' in component:
                        rname = 'relNorm_{}'.format(component)
                        if region=='control':
                            rvalue = controlIntegrals[component]/controlIntegrals[component.replace('3S','1S')]
                            workspace.factory('{}[{},{},{}]'.format(rname,rvalue,rvalue*0.5,rvalue*1.5))
                        param = Models.Param(name,
                            value = '@0*@1',
                            valueArgs = [rname,name.replace('3S','1S')],
                        )
                        param.build(workspace, name)
                    else:
                        # unconstrained for control, FP, but initialized to best fit value
                        value = allintegrals[component]
                        workspace.factory('{}[{},{},{}]'.format(name,value,value*0.5,value*1.5))

        # sum all integrals
        name = 'integral_bg_{}'.format(region)
        param = Models.Param(name,
            value = '+'.join(['@{}'.format(i) for i in range(len(components))]),
            valueArgs = integral_params,
        )
        param.build(workspace,name)

        python_mkdir(self.fitsDir)
        jfile = '{}/components_{}.json'.format(self.fitsDir,region)
        results = {'errs':allerrors, 'integrals':allintegrals}
        self.dump(jfile,results)


        logging.debug('returning')
        logging.debug(', '.join([str(allintegrals),str(allerrors)]))
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
        interrs = results['integralerr']
        for param in vals:
            try:
                workspace.var(param).setVal(vals[param])
            except:
                try:
                    workspace.function(param)
                except:
                    logging.error('cant find param {} in {} workspace'.format(param,region))
                    workspace.Print()
                    
        logging.debug('returning')
        logging.debug(', '.join([str(vals),str(errs),str(ints),str(interrs)]))
        return vals, errs, ints, interrs

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
            vals, errs, ints, interrs = self.loadBackgroundFit(region,workspace=workspace)
        if not skipFit:
            vals, errs, ints, interrs = self.fitBackground(region=region, workspace=workspace)

        if load:
            allintegrals, errors = self.loadComponentIntegrals(region)
        if not skipFit:
            allintegrals, errors = self.buildComponentIntegrals(region,vals,errs,ints,interrs, workspace.pdf('bg_control'), workspace=self.workspace)

        self.control_vals = vals
        self.control_errs = errs
        self.control_integrals = ints
        self.control_integralerrs = interrs
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
        integralerrs = {}
        errors = {}
        allintegrals = {}
        allparams = {}
        for region in self.REGIONS:
            vals[region] = {}
            errs[region] = {}
            integrals[region] = {}
            integralerrs[region] = {}
            self.buildModel(region=region, workspace=workspace)
            for shift in ['']+self.BACKGROUNDSHIFTS:
                if shift=='':
                    if load:
                        v, e, i, ie = self.loadBackgroundFit(region,workspace=workspace)
                    else:
                        v, e, i, ie = self.fitBackground(region=region, workspace=workspace, **kwargs)
                    vals[region][shift] = v
                    errs[region][shift] = e
                    integrals[region][shift] = i
                    integralerrs[region][shift] = ie
                    
                else:
                    if load:
                        vUp, eUp, iUp, ieUp = self.loadBackgroundFit(region,shift+'Up',workspace=workspace)
                        vDown, eDown, iDown, ieDown = self.loadBackgroundFit(region,shift+'Down',workspace=workspace)
                    if not skipFit:
                        vUp, eUp, iUp, ieUp = self.fitBackground(region=region, shift=shift+'Up', workspace=workspace, **kwargs)
                        vDown, eDown, iDown, ieDown = self.fitBackground(region=region, shift=shift+'Down', workspace=workspace, **kwargs
                        )
                    vals[region][shift+'Up'] = vUp
                    errs[region][shift+'Up'] = eUp
                    integrals[region][shift+'Up'] = iUp
                    integralerrs[region][shift+'Up'] = ieUp
                    vals[region][shift+'Down'] = vDown
                    errs[region][shift+'Down'] = eDown
                    integrals[region][shift+'Down'] = iDown
                    integralerrs[region][shift+'Down'] = ieDown


        for region in reversed(self.REGIONS):
            if load:
                allintegrals[region], errors[region] = self.loadComponentIntegrals(region)
            if not skipFit:
                allparams[region] = self.buildParams(region,vals,errs,integrals,integralerrs,workspace=self.workspace)
                allintegrals[region], errors[region] = self.buildComponentIntegrals(region,vals,errs,integrals,integralerrs,workspace.pdf('bg_{}'.format(region)), workspace=self.workspace)

        if fixAfterControl:
            self.fix(False, workspace=workspace)
        self.background_values = vals
        self.background_errors = errs
        self.background_integrals = integrals
        self.background_integralerrs = integralerrs
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
        integralerrs = {}
        fitFuncs = {}
        for region in self.REGIONS:
            models[region] = {}
            values[region] = {}
            errors[region] = {}
            integrals[region] = {}
            integralerrs[region] = {}
            fitFuncs[region] = {}
            for shift in ['']+self.SIGNALSHIFTS+self.QCDSHIFTS:
                values[region][shift] = {}
                errors[region][shift] = {}
                integrals[region][shift] = {}
                integralerrs[region][shift] = {}
                fitFuncs[region][shift] = {}
                if shift == '':
                    vals, errs, ints, interrs, fits = self.fitSignals(region=region,shift=shift,**kwargs)
                    values[region][shift] = vals
                    errors[region][shift] = errs
                    integrals[region][shift] = ints
                    integralerrs[region][shift] = interrs
                    fitFuncs[region][shift] = fits
                elif shift in self.QCDSHIFTS:
                    vals, errs, ints, interrs, fits = self.fitSignals(region=region,shift=shift,**kwargs)
                    values[region][shift] = vals
                    errors[region][shift] = errs
                    integrals[region][shift] = ints
                    integralerrs[region][shift] = interrs
                    fitFuncs[region][shift] = fits
                else:
                    valsUp, errsUp, intsUp, interrsUp, fitsUp = self.fitSignals(region=region,shift=shift+'Up',**kwargs)
                    valsDown, errsDown, intsDown, interrsDown, fitsDown = self.fitSignals(region=region,shift=shift+'Down',**kwargs)
                    values[region][shift+'Up'] = valsUp
                    errors[region][shift+'Up'] = errsUp
                    integrals[region][shift+'Up'] = intsUp
                    integralerrs[region][shift+'Up'] = interrsUp
                    fitFuncs[region][shift+'Up'] = fitsUp
                    values[region][shift+'Down'] = valsDown
                    errors[region][shift+'Down'] = errsDown
                    integrals[region][shift+'Down'] = intsDown
                    integralerrs[region][shift+'Down'] = interrsDown
                    fitFuncs[region][shift+'Down'] = fitsDown
            # special handling for QCD scale uncertainties
            if self.QCDSHIFTS:
                values[region]['QCDscale_ggHUp']      = {}
                values[region]['QCDscale_ggHDown']    = {}
                errors[region]['QCDscale_ggHUp']      = {}
                errors[region]['QCDscale_ggHDown']    = {}
                integrals[region]['QCDscale_ggHUp']   = {}
                integrals[region]['QCDscale_ggHDown'] = {}
                integralerrs[region]['QCDscale_ggHUp']   = {}
                integralerrs[region]['QCDscale_ggHDown'] = {}
                for h in values[region]['']:
                    values[region]['QCDscale_ggHUp'][h]      = {}
                    values[region]['QCDscale_ggHDown'][h]    = {}
                    errors[region]['QCDscale_ggHUp'][h]      = {}
                    errors[region]['QCDscale_ggHDown'][h]    = {}
                    integrals[region]['QCDscale_ggHUp'][h]   = {}
                    integrals[region]['QCDscale_ggHDown'][h] = {}
                    integralerrs[region]['QCDscale_ggHUp'][h]   = {}
                    integralerrs[region]['QCDscale_ggHDown'][h] = {}
                    for a in values[region][''][h]:
                        values[region]['QCDscale_ggHUp'][h][a]      = {}
                        values[region]['QCDscale_ggHDown'][h][a]    = {}
                        errors[region]['QCDscale_ggHUp'][h][a]      = {}
                        errors[region]['QCDscale_ggHDown'][h][a]    = {}
                        integrals[region]['QCDscale_ggHUp'  ][h][a] = max([integrals[region][shift][h][a] for shift in self.QCDSHIFTS])
                        integrals[region]['QCDscale_ggHDown'][h][a] = min([integrals[region][shift][h][a] for shift in self.QCDSHIFTS])
                        integralerrs[region]['QCDscale_ggHUp'  ][h][a] = max([integralerrs[region][shift][h][a] for shift in self.QCDSHIFTS])
                        integralerrs[region]['QCDscale_ggHDown'][h][a] = min([integralerrs[region][shift][h][a] for shift in self.QCDSHIFTS])
                        for val in values[region][''][h][a]:
                            values[region]['QCDscale_ggHUp'  ][h][a][val+'_QCDscale_ggHUp'  ] = max([values[region][shift][h][a][val+'_'+shift] for shift in self.QCDSHIFTS])
                            values[region]['QCDscale_ggHDown'][h][a][val+'_QCDscale_ggHDown'] = min([values[region][shift][h][a][val+'_'+shift] for shift in self.QCDSHIFTS])
                            errors[region]['QCDscale_ggHUp'  ][h][a][val+'_QCDscale_ggHUp'  ] = max([errors[region][shift][h][a][val+'_'+shift] for shift in self.QCDSHIFTS])
                            errors[region]['QCDscale_ggHDown'][h][a][val+'_QCDscale_ggHDown'] = min([errors[region][shift][h][a][val+'_'+shift] for shift in self.QCDSHIFTS])
                for shift in ['QCDscale_ggHUp','QCDscale_ggHDown']:
                    savedir = '{}/{}'.format(self.fitsDir,shift)
                    python_mkdir(savedir)
                    savename = '{}/{}_{}.json'.format(savedir,region,shift)
                    jsonData = {'vals': values[region][shift], 'errs': errors[region][shift], 'integrals': integrals[region][shift], 'integralerrs': integralerrs[region][shift]}
                    self.dump(savename,jsonData)
                fitFuncs[region]['QCDscale_ggHUp']   = self.fitSignalParams(values[region]['QCDscale_ggHUp'],  errors[region]['QCDscale_ggHUp'],  integrals[region]['QCDscale_ggHUp'],  integralerrs[region]['QCDscale_ggHUp'],  region,'QCDscale_ggHUp')
                fitFuncs[region]['QCDscale_ggHDown'] = self.fitSignalParams(values[region]['QCDscale_ggHDown'],errors[region]['QCDscale_ggHDown'],integrals[region]['QCDscale_ggHDown'],integralerrs[region]['QCDscale_ggHDown'],region,'QCDscale_ggHDown')

            if self.QCDSHIFTS:
                models[region] = self.buildSpline(values[region],errors[region],integrals[region],integralerrs[region],region,self.SIGNALSHIFTS+['QCDscale_ggH'],fitFuncs=fitFuncs[region],**kwargs)
            else:
                models[region] = self.buildSpline(values[region],errors[region],integrals[region],integralerrs[region],region,self.SIGNALSHIFTS,fitFuncs=fitFuncs[region],**kwargs)
        self.fitted_models = models

    ######################
    ### Setup datacard ###
    ######################
    def setupDatacard(self, addControl=False, doBinned=False):
        bgs = self.getComponentFractions(self.workspace.pdf('bg_'+self.REGIONS[0]))
        bgs = [self.rstrip(b,'_'+self.REGIONS[0]) for b in bgs]

        sigs = [self.SPLINENAME] if self.do2D else [self.SPLINENAME.format(h=h) for h in self.HMASSES]

        if self.SPLITBGS:
            self.bgs = bgs
        else:
            self.bgs = ['bg']
        self.sigs = sigs

        # setup bins
        for region in self.REGIONS:
            self.addBin(region)

        # add processes
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
                if proc not in sigs:
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

        self.addCrossSection()

        if addControl:
            region = 'control'

            self.addBin(region)

            for proc in bgs:
                #key = proc if proc in self.control_integralValues else '{}_{}'.format(proc,region)
                #integral = self.control_integralValues[key]
                #self.setExpected(proc,region,integral)
                self.setExpected(proc,region,1) 
                self.addRateParam('integral_{}_{}'.format(proc,region),region,proc)
                #if 'cont' not in proc and proc not in sigs:
                #    self.addShape(region,proc,proc)

            self.setObserved(region,-1) # reads from histogram

    def addCrossSection(self):
        # add higgs cross section
        tfile = ROOT.TFile.Open('/uscms/home/jingyu/nobackup/Haa/HaaLimits/CMSSW_10_2_13/src/CombineLimits/Limits/data/Higgs_YR4_BSM_13TeV.root')
        ws = tfile.Get('YR4_BSM_13TeV')
        ggF = ws.function('xsec_ggF_N3LO')
        vbf = ws.function('xsec_VBF')
        # uncs
        ggF_pdfalpha = ws.function('pdfalpha_err_ggF_N3LO')
        vbf_pdfalpha = ws.function('pdfalpha_err_VBF')

        # add gg+VBF/gg acceptance correction
        accfile = ROOT.TFile.Open('/uscms/home/jingyu/nobackup/Haa/HaaLimits/CMSSW_10_2_13/src/CombineLimitsRunII/HaaLimits/data/acceptance.root')
        acc = accfile.Get('acceptance')
        accgraph = accfile.Get('acceptance_graph')
        accgraph.Fit(acc)
        from CombineLimitsRunII.Limits.Models import buildSpline
        accspline = buildSpline(self.workspace, 'ggF_VBF_acceptance', ['MH','MA'], None, acc)
        self.workspace.factory('pdf_gg[0,-10,10]')
        for channel in self.CHANNELS:
            for region in self.REGIONS:
                regionText = channel+'_'+region
                for proc in self.sigs:
                    formula = '(@0*(1+@4*@2*0.01) + @1*(1+@4*@3*0.01))*@5*@6'
                    #formula = '(@0 + @1)*@2'
                    args = ROOT.RooArgList()
                    args.add(ggF)
                    args.add(vbf)
                    args.add(ggF_pdfalpha)
                    args.add(vbf_pdfalpha)
                    args.add(self.workspace.var('pdf_gg'))
                    args.add(accspline)
                    args.add(self.workspace.function('integral_{}_{}'.format(proc,regionText)))
                    name = 'fullIntegral_{}_{}'.format(proc,regionText)
                    spline = ROOT.RooFormulaVar(name,name,formula,args)
                    getattr(self.workspace,'import')(spline, ROOT.RooFit.RecycleConflictNodes())
                    print "Adding rateParam", name,regionText,proc+'_'+regionText
                    self.addRateParam(name,regionText,proc+'_'+regionText)

        # alternative SM xsec
        tfile = ROOT.TFile.Open('/uscms/home/jingyu/nobackup/Haa/HaaLimits/CMSSW_10_2_13/src/CombineLimits/Limits/data/Higgs_YR4_SM_13TeV.root')
        ws = tfile.Get('YR4_SM_13TeV')
        ggF = ws.function('xsec_ggF_N3LO')
        vbf = ws.function('xsec_VBF')
        # uncs
        ggF_pdfalpha = ws.function('pdfalpha_err_ggF_N3LO')
        vbf_pdfalpha = ws.function('pdfalpha_err_VBF')

        for channel in self.CHANNELS:
            for region in self.REGIONS:
                region = channel+'_'+region
                for proc in self.sigs:
                    formula = '(@0*(1+@4*@2*0.01) + @1*(1+@4*@3*0.01))*@5*@6'
                    #formula = '(@0 + @1)*@2'
                    args = ROOT.RooArgList()
                    args.add(ggF)
                    args.add(vbf)
                    args.add(ggF_pdfalpha)
                    args.add(vbf_pdfalpha)
                    args.add(self.workspace.var('pdf_gg'))
                    args.add(accspline)
                    args.add(self.workspace.function('integral_{}_{}'.format(proc,region)))
                    name = 'fullIntegral_SM_{}_{}'.format(proc,region)
                    spline = ROOT.RooFormulaVar(name,name,formula,args)
                    getattr(self.workspace,'import')(spline, ROOT.RooFit.RecycleConflictNodes())
                    #self.addRateParam(name,region,proc)


    ###################
    ### Systematics ###
    ###################
    def addSystematics(self,doBinned=False,addControl=False):
        logging.debug('addSystematics')
        self.sigProcesses = tuple([self.SPLINENAME]) if self.do2D else tuple([self.SPLINENAME.format(h=h) for h in self.HMASSES])
        bgs = self.getComponentFractions(self.workspace.pdf('bg_'+self.REGIONS[0]))
        bgs = [self.rstrip(b,'_'+self.REGIONS[0]) for b in bgs]
        if self.SPLITBGS:
            self.bgProcesses = tuple(bgs)
        else:
            self.bgProcesses = tuple(['bg'])
        self._addLumiSystematic()
        self._addMuonSystematic()
        #self._addTauSystematic()
        self._addShapeSystematic(doBinned=doBinned)
        #self._addComponentSystematic(addControl=addControl)
        self._addRelativeNormUnc()
        self._addHiggsSystematic()
        self._addAcceptanceSystematic()
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
        #return
        self.addSystematic('pdf_gg', 'param', systematics=[0,1])

        ## theory
        #syst = {}
        #if 125 in self.HMASSES: syst[((self.SPLINENAME.format(h=125),), tuple(self.REGIONS))] = (1+(0.046*48.52+0.004*3.779)/(48.52+3.779)    , 1+(-0.067*48.52-0.003*3.779)/(48.52+3.779))
        #if 300 in self.HMASSES: syst[((self.SPLINENAME.format(h=300),), tuple(self.REGIONS))] = (1+(0.015*6.59+0.003*1.256)/(6.59+1.256)      , 1+(-0.032*6.59-0.001*1.256)/(6.59+1.256))
        #if 750 in self.HMASSES: syst[((self.SPLINENAME.format(h=750),), tuple(self.REGIONS))] = (1+(0.020*0.4969+0.003*0.1915)/(0.4969+0.1915), 1+(-0.037*0.4969-0.004*0.1915)/(0.4969+0.1915))
        #self.addSystematic('higgs_theory','lnN',systematics=syst)

        ## pdf+alpha_s
        #syst = {}
        #if 125 in self.HMASSES: syst[((self.SPLINENAME.format(h=125),), tuple(self.REGIONS))] = 1+(0.032*48.52+0.021*3.779)/(48.52+3.779)
        #if 300 in self.HMASSES: syst[((self.SPLINENAME.format(h=300),), tuple(self.REGIONS))] = 1+(0.030*6.59+0.014*1.256)/(6.59+1.256)
        #if 750 in self.HMASSES: syst[((self.SPLINENAME.format(h=750),), tuple(self.REGIONS))] = 1+(0.040*0.4969+0.022*0.1915)/(0.4969+0.1915)
        #self.addSystematic('pdf_alpha','lnN',systematics=syst)


    def _addShapeSystematic(self,doBinned=False):
        #for shift in self.SHIFTS+['QCDscale_ggH']:
        print "shifts:", self.SHIFTS, "doBinned:", doBinned, self.CHANNELS
        for shift in self.SHIFTS:
            for channel in self.CHANNELS:
                #print self.workspace.var(shift)
                if shift=='QCDscale_ggH' and not self.QCDSHIFTS: continue
                if shift in self.BACKGROUNDSHIFTS and doBinned:
                    syst = {}
                    for proc in self.bgProcesses:
                        for region in self.REGIONS:
                            basename = '{}_{}_{}'.format(proc,region,shift)
                            syst[((proc,),(region,))] = (basename+'Up', basename+'Down')
                            #print "basename:", basename
                    self.addSystematic(shift,'shape',systematics=syst)
                else:
                    if self.workspace.var(channel+'_'+shift): self.addSystematic(channel+'_'+shift, 'param', systematics=[0,1])
    
    def _addAcceptanceSystematic(self):
        accproc = self.sigProcesses
        accsyst = {
            (accproc,tuple(c+'_'+r for r in self.REGIONS for c in self.CHANNELS)) : 1.005,
        }
        #print accsyst
        self.addSystematic('CMS_haa_acc','lnN',systematics=accsyst)

    def _addLumiSystematic(self):
        # lumi: 2.5% 2016
        lumiproc = self.sigProcesses
        lumisyst = {
            (lumiproc,tuple(c+'_'+r for r in self.REGIONS for c in self.CHANNELS)) : 1.025,
        }
        #print "lumisyst", lumisyst
        self.addSystematic('lumi_13TeV','lnN',systematics=lumisyst)

    def _addMuonSystematic(self, **kwargs):
        # from z: 1 % + 0.5 % + 0.5 % per muon for id + iso + trig (pt>20)
        muproc = self.sigProcesses
        musyst = {
            (muproc,tuple(c+'_'+r for r in self.REGIONS for c in self.CHANNELS)) : 1+math.sqrt(sum([0.01**2,0.005**2]*2+[0.01**2]+[0.005**2])), # 2 lead have iso, tau_mu doesnt, plus iso
        }
        self.addSystematic('CMS_eff_m','lnN',systematics=musyst)
        
    def _addTauSystematic(self):
        # 5% on sf 0.99 (VL/L) 0.97 (M) 0.95 (T) 0.93 (VT)
        tauproc = self.sigProcesses
        tausyst = {
            (tauproc,tuple(self.REGIONS)) : 1.05,
        }
        self.addSystematic('CMS_eff_t','lnN',systematics=tausyst)

    def _addComponentSystematic(self,addControl=False):
        bgs = self.getComponentFractions(self.workspace.pdf('bg_'+self.REGIONS[0]))
        bgs = [self.rstrip(b,'_'+self.REGIONS[0]) for b in bgs]
        if not self.SPLITBGS:
            bgs = ['bg']
        bins = self.REGIONS
        if addControl: bins = bins + ['control']
        syst = {}
        for bg in bgs:
            for b in bins:
                key = bg if bg in self.control_integralErrors else '{}_control'.format(bg)
                syst[(bg,),(b,)] = 1 + self.control_integralErrors[key]

        self.addSystematic('CMS_haa_{process}_normUnc','lnN',systematics=syst) 

    def _addRelativeNormUnc(self):
        relativesyst = {
           (tuple(['upsilon2S']),  tuple([self.REGIONS[0]])) : 1.05,
           (tuple(['upsilon3S']),  tuple([self.REGIONS[0]])) : 1.10,
           (tuple(['jpsi2S']),     tuple([self.REGIONS[0]])) : 1.20,
        }
        self.addSystematic('CMS_haa_relNormUnc_{process}', 'lnN', systematics=relativesyst)
        # These have been defined as params earlier
        #self.addSystematic('CMS_haa_relNormUnc_upsilon2S', 'param', systematics=[0,1])
        #self.addSystematic('CMS_haa_relNormUnc_upsilon3S', 'param', systematics=[0,1])
        #self.addSystematic('CMS_haa_relNormUnc_jpsi2S', 'param', systematics=[0,1])


    ###################################
    ### Save workspace and datacard ###
    ###################################
    def save(self,name='mmmt', subdirectory=''):
        processes = {}
        bgs = self.getComponentFractions(self.workspace.pdf('bg_'+self.REGIONS[0]))
        bgs = [self.rstrip(b,'_'+self.REGIONS[0]) for b in bgs]
        if not self.SPLITBGS:
            bgs = ['bg']
        if self.do2D:
            processes = [self.SPLINENAME] + bgs
        else:
            for h in self.HMASSES:
                processes[self.SIGNAME.format(h=h,a='X')] = [self.SPLINENAME.format(h=h)] + bgs
        if subdirectory == '':
            self.printCard('datacards_shape/MuMuTauTau/{}'.format(name),processes=processes,blind=False,saveWorkspace=True)
        else:
            self.printCard('datacards_shape/MuMuTauTau/' + subdirectory + '{}'.format(name),processes=processes,blind=False,saveWorkspace=True)
          
    def GetWorkspaceValue(self, variable):
        lam = self.workspace.argSet(variable)
        return lam.getRealValue(variable)
