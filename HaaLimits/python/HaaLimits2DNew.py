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
from CombineLimits.HaaLimits.HaaLimitsNew import HaaLimits
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
        self.fitsDir = 'fitParams/HaaLimits2D{}'.format('_'+tag if tag else '')


    ###########################
    ### Workspace utilities ###
    ###########################
    def initializeWorkspace(self):
        self.addX(*self.XRANGE,unit='GeV',label=self.XLABEL)
        self.addY(*self.YRANGE,unit='GeV',label=self.YLABEL)
        self.addMH(*self.SPLINERANGE,unit='GeV',label=self.SPLINELABEL)

    def _buildYModel(self,region='PP',**kwargs):
        tag = kwargs.pop('tag',region)

        # try landau
        if self.YRANGE[1]>100:
            bg = Models.Landau('bg',
                x = 'y',
                mu    = [50,0,200],
                sigma = [10,0,100],
            )
        else:
            land1 = Models.Landau('land1',
                x = 'y',
                mu    = [5,0,200],
                sigma = [1,0,100],
            )
            nameL1 = 'land1{}'.format('_'+tag if tag else '')
            land1.build(self.workspace,nameL1)

            # add a guassian summed for tt ?
            gaus1 = Models.Gaussian('gaus1',
                x = 'y',
                mean = [1.5,0,4],
                sigma = [0.4,0,2],
            )
            nameG1 = 'gaus1{}'.format('_'+tag if tag else '')
            gaus1.build(self.workspace,nameG1)

            bg = Models.Sum('bg',
                **{
                    nameL1     : [0.9,0,1],
                    nameG1     : [0.5,0,1],
                    'recursive': True,
                }
            )

        #cont1 = Models.Exponential('conty1',
        #    x = 'y',
        #    #lamb = [-0.20,-1,0], # kinfit
        #    lamb = [-0.05,-1,0], # visible
        #)
        #nameC1 = 'conty1{}'.format('_'+tag if tag else '')
        #cont1.build(self.workspace,nameC1)

        ## higgs fit (mmtt)
        #if self.YRANGE[1]>100:
        #    erf1 = Models.Erf('erf1',
        #        x = 'y',
        #        erfScale = [0.05,0,1],
        #        erfShift = [70,10,200],
        #    )
        #    nameE1 = 'erf1{}'.format('_'+tag if tag else '')
        #    erf1.build(self.workspace,nameE1)

        #    bg = Models.Prod('bg',
        #        nameE1,
        #        nameC1,
        #    )
        ## pseudo fit (tt)
        #else:
        #    erf1 = Models.Erf('erf1',
        #        x = 'y',
        #        erfScale = [1,0.01,10],
        #        erfShift = [1,0.1,10],
        #    )
        #    nameE1 = 'erf1{}'.format('_'+tag if tag else '')
        #    erf1.build(self.workspace,nameE1)

        #    erfc1 = Models.Prod('erfc1',
        #        nameE1,
        #        nameC1,
        #    )
        #    nameEC1 = 'erfc1{}'.format('_'+tag if tag else '')
        #    erfc1.build(self.workspace,nameEC1)

        #    # add an upsilon to tt resonance
        #    #upsilon = Models.Gaussian('upsilony',
        #    #    x = 'y',
        #    #    mean  = [5.5,5,6.5],
        #    #    sigma = [0.25,0.1,1],
        #    #)
        #    #nameU = 'upsilony{}'.format('_'+tag if tag else '')
        #    #upsilon.build(self.workspace,nameU)

        #    # add a guassian summed for tt ?
        #    gaus1 = Models.Gaussian('gaus1',
        #        x = 'y',
        #        mean = [1.5,0,4],
        #        sigma = [0.4,0,2],
        #    )
        #    nameG1 = 'gaus1{}'.format('_'+tag if tag else '')
        #    gaus1.build(self.workspace,nameG1)

        #    bg = Models.Sum('bg',
        #        **{ 
        #            nameEC1    : [0.9,0,1],
        #            nameG1     : [0.5,0,1],
        #            #nameU      : [0.5,0,1],
        #            'recursive': True,
        #        }
        #    )

        name = 'bg_{}'.format(region)
        bg.build(self.workspace,name)

    def _buildXModel(self,region='PP',**kwargs):
        super(HaaLimits2D,self).buildModel(region,**kwargs)

    def buildModel(self,region='PP',**kwargs):
        tag = kwargs.pop('tag',region)

        # build the x variable
        self._buildXModel(region+'_x',**kwargs)

        # build the y variable
        self._buildYModel(region+'_y',**kwargs)

        # the 2D model
        bg = Models.Prod('bg',
            'bg_{}_x'.format(region),
            'bg_{}_y'.format(region),
        )

        name = 'bg_{}'.format(region)
        bg.build(self.workspace,name)


    def fitSignals(self,h,region='PP',shift='',**kwargs):
        '''
        Fit the signal model for a given Higgs mass.
        Required arguments:
            h = higgs mass
        '''
        ygausOnly = kwargs.get('ygausOnly',False)
        isKinFit = kwargs.pop('isKinFit',False)
        yFitFunc = kwargs.pop('yFitFunc','G')
        fit = kwargs.get('fit',False)
        dobgsig = kwargs.get('doBackgroundSignal',False)
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
        initialValuesDCB = self.GetInitialValuesDCB(isKinFit=isKinFit)
        for a in amasses:
            aval = float(str(a).replace('p','.'))
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
                mean  = [aval,0,30],
                width = [0.01*aval,0.001,5],
                sigma = [0.01*aval,0.001,5],
            )
            modelx.build(ws, 'sigx')
            if self.YRANGE[1]>100: # y variable is h mass
                if yFitFunc == "G": 
                    modely = Models.Gaussian('sigy',
                        x = 'y',
                        mean  = [h,0,1.25*h],
                        sigma = [0.1*h,0.01,0.5*h],
                    )
                elif yFitFunc == "V":
                    modely = Models.Voigtian('sigy',
                        x = 'y',
                        mean  = [h,0,1.25*h],
                        width = [0.1*h,0.01,0.5*h],
                        sigma = [0.1*h,0.01,0.5*h],
                    )
                elif yFitFunc == "CB":
                    modely = Models.CrystalBall('sigy',
                        x = 'y',
                        mean  = [h,0,1.25*h],
                        sigma = [0.1*h,0.01,0.5*h],
                        a = [1.0,.5,5],
                        n = [0.5,.1,10],
                    )
                elif yFitFunc == "DCB":
                    modely = Models.DoubleCrystalBall('sigy',
                        x = 'y',
                        mean  = [h,0,1.25*h],
                        sigma = [initialValuesDCB["h"+str(h)+"a"+str(a)]["sigma"],0.01,0.5*h],
                        a1    = [initialValuesDCB["h"+str(h)+"a"+str(a)]["a1"],0.1,10],
                        n1    = [initialValuesDCB["h"+str(h)+"a"+str(a)]["n1"],0.1,20],
                        a2    = [initialValuesDCB["h"+str(h)+"a"+str(a)]["a2"],0.1,10],
                        n2    = [initialValuesDCB["h"+str(h)+"a"+str(a)]["n2"],0.1,20],
                    )
                elif yFitFunc == "DG":
                    modely = Models.DoubleSidedGaussian('sigy',
                        x = 'y',
                        mean  = [h,0,1.25*h],
                        sigma1 = [0.1*h,0.05*h,0.5*h],
                        sigma2 = [0.2*h,0.05*h,0.5*h],
                        yMax = self.YRANGE[1],
                    )
                elif yFitFunc == "DV":
                    modely = Models.DoubleSidedVoigtian('sigy',
                        x = 'y',
                        mean  = [h,0,1.25*h],
                        sigma1 = [0.1*h,0.01,0.5*h],
                        sigma2 = [0.2*h,0.01,0.5*h],
                        width1 = [1.0,0.01,10.0],
                        width2 = [2.0,0.01,10.0],
                        yMax = self.YRANGE[1],
                    )
                else:
                    raise
                modely.build(ws, 'sigy')
                model = Models.Prod('sig',
                    'sigx',
                    'sigy',
                )
            else: # y variable is tt
                if yFitFunc == "G":
                    modely = Models.Gaussian('sigy',
                        x = 'y',
                        mean  = [aval,0,1.25*aval],
                        sigma = [0.1*aval,0.01,0.5*aval],
                    )
                elif yFitFunc == "V":
                    modely = Models.Voigtian('sigy',
                        x = 'y',
                        mean  = [aval,0,30],
                        width = [0.1*aval,0.01,5],
                        sigma = [0.1*aval,0.01,5],
                    )
                elif yFitFunc == "CB":
                    modely = Models.CrystalBall('sigy',
                        x = 'y',
                        mean  = [aval,0,30],
                        sigma = [0.1*aval,0,5],
                        a = [1.0,0.5,5],
                        n = [0.5,0.1,10],
                    )
                elif yFitFunc == "DCB":
                    modely = Models.DoubleCrystalBall('sigy',
                        x = 'y',
                        mean  = [aval,0,30],
                        sigma = [0.1*aval,0,5],
                        a1 = [1.0,0.1,6],
                        n1 = [0.9,0.1,6],
                        a2 = [2.0,0.1,10],
                        n2 = [1.5,0.1,10],
                    )
                elif yFitFunc == "DG":
                    modely = Models.DoubleSidedGaussian('sigy',
                        x = 'y',
                        mean  = [aval,0,30],
                        sigma1 = [0.1*aval,0.05*aval,0.4*aval],
                        sigma2 = [0.3*aval,0.05*aval,0.4*aval],
                        yMax = self.YRANGE[1],
                    )
                elif yFitFunc == "DV":
                    modely = Models.DoubleSidedVoigtian('sigy',
                        x = 'y',
                        mean  = [aval,0,30],
                        sigma1 = [0.1*aval,0.05*aval,0.4*aval],
                        sigma2 = [0.3*aval,0.05*aval,0.4*aval],
                        width1 = [0.1,0.01,5],
                        width2 = [0.3,0.01,5],
                        yMax = self.YRANGE[1],
                    )
                elif yFitFunc == "errG":
                    tterf = Models.Erf('tterf',
                       x = 'y',
                       erfScale = [0.2,0.1,5],
                       erfShift = [0.5*aval,0.1,30],
                    )
                    ttgaus = Models.Gaussian('ttgaus',
                       x = 'y',
                       mean  = [aval,0,30],
                       sigma = [0.1*aval,0.05*aval,0.4*aval],
                    )
                    ttgaus.build(ws,"ttgaus")
                    tterf.build(ws,"tterf")
                    modely = Models.Prod('sigy',
                            'ttgaus',
                            'tterf',
                    )
                elif yFitFunc == "L":
                    #modely = Models.Landau('sigy',
                    #    x = 'y',
                    #    mu  = [0.5*aval,0,30],
                    #    sigma = [0.1*aval,0.05*aval,aval],
                    #)
                    ttland = Models.Landau('ttland',
                        x = 'y',
                        mu  = [0.5*aval,0,30],
                        sigma = [0.1*aval,0.05*aval,aval],
                    )
                    ttland.build(ws,'ttland')
                    ttgaus = Models.Gaussian('ttgaus',
                       x = 'y',
                       mean  = [0.5*aval,0,30],
                       sigma = [0.1*aval,0.05*aval,0.4*aval],
                    )
                    ttgaus.build(ws,"ttgaus")
                    modely = Models.Prod('sigy',
                            'ttgaus',
                            'ttland',
                    )
                    #modely = Models.Sum('sigy',
                    #    **{
                    #        'ttland'     : [0.9,0,1],
                    #        'ttgaus'     : [0.5,0,1],
                    #        'recursive': True,
                    #    }
                    #)
                else:
                    raise

                modely.build(ws, 'sigy')

                if region=='PP' or not dobgsig:
                    model = Models.Prod('sig',
                        'sigx',
                        'sigy',
                    )
                else:
                    conty = Models.Exponential('conty',
                        x = 'y',
                        lamb = [-0.25,-1,-0.001], # visible
                    )
                    conty.build(ws,'conty')

                    erfy = Models.Erf('erfy',
                        x = 'y',
                        erfScale = [0.1,0.01,10],
                        erfShift = [2,0,10],
                    )
                    erfy.build(ws,'erfy')

                    erfc = Models.Prod('erfcy',
                        'erfy',
                        'conty',
                    )
                    erfc.build(ws,'erfcy')

                    modelymod = Models.Sum('bgsigy',
                        **{ 
                            'erfcy'    : [0.5,0,1],
                            'sigy'     : [0.5,0,1],
                            'recursive': True,
                        }
                    )
                    modelymod.build(ws,'bgsigy')

                    model = Models.Prod('sig',
                        'sigx',
                        'bgsigy',
                    )

            model.build(ws, 'sig')
            hist = histMap[self.SIGNAME.format(h=h,a=a)]
            saveDir = '{}/{}'.format(self.plotDir,shift if shift else 'central')
            results[h][a], errors[h][a] = model.fit2D(ws, hist, 'h{}_a{}_{}'.format(h,a,tag), saveDir=saveDir, save=True, doErrors=True)

            if self.binned:
                integral = histMap[self.SIGNAME.format(h=h,a=a)].Integral()
            else:
                integral = histMap[self.SIGNAME.format(h=h,a=a)].sumEntries('x>{} && x<{} && y>{} && y<{}'.format(*self.XRANGE+self.YRANGE))
            integrals[h][a] = integral

    
        savedir = '{}/{}'.format(self.fitsDir,shift if shift else 'central')
        python_mkdir(savedir)
        savename = '{}/h{}_{}.json'.format(savedir,h,tag)
        jsonData = {'vals': results, 'errs': errors, 'integrals': integrals}
        self.dump(savename,jsonData)

        # Fit using ROOT rather than RooFit for the splines
        if yFitFunc == "V":
            fitFuncs = {
                'xmean' : 'pol1',  
                'xwidth': 'pol2',
                'xsigma': 'pol2',
                'ymean' : 'pol1',
                'ywidth': 'pol2',
                'ysigma': 'pol2',
            }
        elif yFitFunc == "G":
            fitFuncs = {
                'xmean' : 'pol1',  
                'xwidth': 'pol2',
                'xsigma': 'pol2',
                'ymean' : 'pol1',
                'ysigma': 'pol2',
            }
        elif yFitFunc == "CB":
            fitFuncs = {
                'xmean' : 'pol1',  
                'xwidth': 'pol2',
                'xsigma': 'pol2',
                'ymean' : 'pol1',
                'ysigma': 'pol2',
                'ya': 'pol2',
                'yn': 'pol2',
            }
        elif yFitFunc == "DCB":
            fitFuncs = {
                'xmean' : 'pol1',  
                'xsigma': 'pol2',
                'ymean' : 'pol1',
                'ysigma': 'pol2',
                'ya1': 'pol2',
                'yn1': 'pol2',
                'ya2': 'pol2',
                'yn2': 'pol2',
            }
        elif yFitFunc == "DG":
            fitFuncs = {
                'xmean' : 'pol1',  
                'xwidth': 'pol2',
                'xsigma': 'pol2',
                'ymean' : 'pol1',
                'ysigma1': 'pol2',
                'ysigma2': 'pol2',
            }
        elif yFitFunc == "DV":
            fitFuncs = {
                'xmean' : 'pol1',  
                'xwidth': 'pol2',
                'xsigma': 'pol2',
                'ymean' : 'pol1',
                'ysigma1': 'pol2',
                'ysigma2': 'pol2',
                'ywidth1': 'pol2',
                'ywidth2': 'pol2',
            }
        elif yFitFunc == "errG":
            fitFuncs = {
                'xmean' : 'pol1',  
                'xwidth': 'pol2',
                'xsigma': 'pol2',
                'ymean' : 'pol1',
                'ysigma': 'pol2',
                'yerfScale': 'pol2',
                'yerfShift': 'pol2',
            }
        elif yFitFunc == "L":
            fitFuncs = {
                'xmean' : 'pol1',
                'xwidth': 'pol2',
                'xsigma': 'pol2',
                'ymean' : 'pol1',
                'ysigma': 'pol2',
                'mu'    : 'pol2',
                'sigma' : 'pol2',
            }
        else:
            raise

        xs = []
        x = self.XRANGE[0]
        while x<=self.XRANGE[1]:
            xs += [x]
            x += float(self.XRANGE[1]-self.XRANGE[0])/100
        ys = []
        y = self.YRANGE[0]
        while y<=self.YRANGE[1]:
            ys += [y]
            y += float(self.YRANGE[1]-self.YRANGE[0])/100
        fittedParams = {}
        if   yFitFunc == "V"   : yparameters = ['mean','width','sigma']
        elif yFitFunc == "G"   : yparameters = ['mean', 'sigma']
        elif yFitFunc == "CB"  : yparameters = ['mean', 'sigma', 'a', 'n']
        elif yFitFunc == "DCB" : yparameters = ['mean', 'sigma', 'a1', 'n1', 'a2', 'n2']
        elif yFitFunc == "DG"  : yparameters = ['mean', 'sigma1', 'sigma2']
        elif yFitFunc == "DV"  : yparameters = ['mean', 'sigma1', 'sigma2','width1','width2']
        elif yFitFunc == "errG": yparameters = ['mean_ttgaus', 'sigma_ttgaus','erfShift_tterf','erfScale_tterf']
        #elif yFitFunc == "L"   : yparameters = ['mu', 'sigma']
        elif yFitFunc == "L"   : yparameters = ['mean_ttgaus', 'sigma_ttgaus','mu_ttland','sigma_ttland']
        else: raise
        for param in ['mean','width','sigma']:
            name = '{}_{}{}'.format('x'+param,h,tag)
            xerrs = [0]*len(amasses)
            vals = [results[h][a]['{}_sigx'.format(param)] for a in amasses]
            errs = [errors[h][a]['{}_sigx'.format(param)] for a in amasses]
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
                fitResult = graph.Fit(fitFuncs['x'+param])
                func = graph.GetFunction(fitFuncs['x'+param])
                fittedParams['x'+param] = [func.Eval(x) for x in xs]
            canvas.Print('{}.png'.format(savename))

        for param in yparameters:
            name = '{}_{}{}'.format('y'+param,h,tag)
            xerrs = [0]*len(amasses)
            if yFitFunc == "errG" or yFitFunc == "L": 
              vals = [results[h][a][param] for a in amasses]
              errs = [errors[h][a][param] for a in amasses]
            else:
              vals = [results[h][a]['{}_sigy'.format(param)] for a in amasses]
              errs = [errors[h][a]['{}_sigy'.format(param)] for a in amasses]
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
                fitResult = graph.Fit(fitFuncs['y'+param])
                func = graph.GetFunction(fitFuncs['y'+param])
                fittedParams['y'+param] = [func.Eval(y) for y in ys]
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

    def buildSpline(self,h,vals,errs,integrals,region='PP',shifts=[],yFitFunc='G',isKinFit=True,**kwargs):
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
        ygausOnly = kwargs.get('ygausOnly',False)
        fit = kwargs.get('fit',False)
        dobgsig = kwargs.get('doBackgroundSignal',False)
        amasses = self.AMASSES
        if h>125: amasses = [a for a in amasses if a not in ['3p6',4,6]]
        avals = [float(str(x).replace('p','.')) for x in amasses]

        # create parameter splines
        params = ['mean','width','sigma']
        splines = {}
        for param in params:
            name = 'x{param}_h{h}_{region}_sigx'.format(param=param,h=h,region=region)
            paramMasses = avals
            paramValues = [vals[''][h][a]['{param}_sigx'.format(param=param,h=h,a=a,region=region)] for a in amasses]
            paramShifts = {}
            for shift in shifts:
                shiftValuesUp   = [vals[shift+'Up'  ][h][a]['{param}_sigx'.format(  param=param,h=h,a=a,region=region,shift=shift)] for a in amasses]
                shiftValuesDown = [vals[shift+'Down'][h][a]['{param}_sigx'.format(param=param,h=h,a=a,region=region,shift=shift)] for a in amasses]
                paramShifts[shift] = {'up': shiftValuesUp, 'down': shiftValuesDown}
            spline = Models.Spline(name,
                masses = paramMasses,
                values = paramValues,
                shifts = paramShifts,
            )
            spline.build(self.workspace, name)
            splines[name] = spline

        if   yFitFunc == "V"   : yparameters = ['mean','width','sigma']
        elif yFitFunc == "G"   : yparameters = ['mean', 'sigma']
        elif yFitFunc == "CB"  : yparameters = ['mean', 'sigma', 'a', 'n']
        elif yFitFunc == "DCB" : yparameters = ['mean', 'sigma', 'a1', 'n1', 'a2', 'n2']
        elif yFitFunc == "DG"  : yparameters = ['mean', 'sigma1', 'sigma2']
        elif yFitFunc == "DV"  : yparameters = ['mean', 'sigma1', 'sigma2','width1','width2']
        elif yFitFunc == "errG": yparameters = ['mean_ttgaus', 'sigma_ttgaus','erfShift_tterf','erfScale_tterf']
        #elif yFitFunc == "L"   : yparameters = ['mu', 'sigma']
        elif yFitFunc == "L"   : yparameters = ['mean_ttgaus', 'sigma_ttgaus','mu_ttland','sigma_ttland']
        else: raise

        for param in yparameters:
            name = 'y{param}_h{h}_{region}_sigy'.format(param=param,h=h,region=region)
            paramMasses = avals
            paramValues = [vals[''][h][a]['{param}_sigy'.format(param=param,h=h,a=a,region=region)] for a in amasses]
            paramShifts = {}
            for shift in shifts:
                shiftValuesUp   = [vals[shift+'Up'  ][h][a]['{param}_sigy'.format(  param=param,h=h,a=a,region=region,shift=shift)] for a in amasses]
                shiftValuesDown = [vals[shift+'Down'][h][a]['{param}_sigy'.format(param=param,h=h,a=a,region=region,shift=shift)] for a in amasses]
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
    
        # create model
        if fit:
            print 'Need to reimplement fitting'
            raise
        else:
            modelx = Models.Voigtian(self.SPLINENAME.format(h=h)+'_x',
                **{param: 'x{param}_h{h}_{region}_sigx'.format(param=param, h=h, region=region) for param in params}
            )
        modelx.build(self.workspace,'{}_{}'.format(self.SPLINENAME.format(h=h),tag+'_x'))

        if   yFitFunc == "V"   : ym = Models.Voigtian
        elif yFitFunc == "G"   : ym = Models.Gaussian
        elif yFitFunc == "CB"  : ym = Models.CrystalBall
        elif yFitFunc == "DCB" : ym = Models.DoubleCrystalBall
        elif yFitFunc == "DG"  : ym = Models.DoubleSidedGaussian
        elif yFitFunc == "DV"  : ym = Models.DoubleSidedVoigtian
        #elif yFitFunc == "errG": 
        else: raise

        if fit:
            print 'Need to reimplement fitting'
            raise
        else:
            if yFitFunc == 'errG':
                modely_gaus = Models.Gaussian("model_gaus",
                    x = 'y',
                     **{param: 'y{param}_h{h}_{region}_sigy'.format(param=param, h=h, region=region) for param in ['mean','sigma']}
                )
                modely_gaus.build(self.workspace,'{}_{}'.format(self.SPLINENAME.format(h=h),tag+'_gaus_y'))
                modely_erf = Models.Erf("model_erf",
                    x = 'y',
                     **{param: 'y{param}_h{h}_{region}_sigy'.format(param=param, h=h, region=region) for param in ['ergScales','erfShifts']}
                )
                modely_erf.build(self.workspace,'{}_{}'.format(self.SPLINENAME.format(h=h),tag+'_erf_y'))
                modely = Models.Prod(self.SPLINENAME.format(h=h)+'_y',
                    '{}_{}'.format(self.SPLINENAME.format(h=h),tag+'_gaus_y'),
                    '{}_{}'.format(self.SPLINENAME.format(h=h),tag+'_erf_y'),
                )
            elif yFitFunc == 'L':
                modely_gaus = Models.Gaussian("model_gaus",
                    x = 'y',
                     **{param: 'y{param}_h{h}_{region}_sigy'.format(param=param, h=h, region=region) for param in ['mean','sigma']}
                )
                modely_gaus.build(self.workspace,'{}_{}'.format(self.SPLINENAME.format(h=h),tag+'_gaus_y'))
                modely_land = Models.Erf("model_land",
                    x = 'y',
                     **{param: 'y{param}_h{h}_{region}_sigy'.format(param=param, h=h, region=region) for param in ['mu','sigma']}
                )
                modely_land.build(self.workspace,'{}_{}'.format(self.SPLINENAME.format(h=h),tag+'_land_y'))
                modely = Models.Prod(self.SPLINENAME.format(h=h)+'_y',
                    '{}_{}'.format(self.SPLINENAME.format(h=h),tag+'_gaus_y'),
                    '{}_{}'.format(self.SPLINENAME.format(h=h),tag+'_land_y'),
                )
            else:
                modely = ym(self.SPLINENAME.format(h=h)+'_y',
                    x = 'y',
                    **{param: 'y{param}_h{h}_{region}_sigy'.format(param=param, h=h, region=region) for param in yparameters}
                )
        modely.build(self.workspace,'{}_{}'.format(self.SPLINENAME.format(h=h),tag+'_y'))
                
        model = Models.Prod(self.SPLINENAME.format(h=h),
            '{}_{}'.format(self.SPLINENAME.format(h=h),tag+'_x'),
            '{}_{}'.format(self.SPLINENAME.format(h=h),tag+'_y'),
        )
        model.build(self.workspace,'{}_{}'.format(self.SPLINENAME.format(h=h),tag))

        return model

    def addControlModels(self, addUpsilon=True, setUpsilonLambda=False, voigtian=False, logy=False):
        region = 'control'
        self.buildModel(region=region, addUpsilon=addUpsilon, setUpsilonLambda=setUpsilonLambda, voigtian=voigtian)
        #self.workspace.factory('bg_{}_norm[1,0,2]'.format(region))
        vals, errs, ints = self.fitBackground(region=region, setUpsilonLambda=setUpsilonLambda, addUpsilon=addUpsilon, logy=logy)

        # integral
        name = 'integral_bg_{}'.format(region)
        paramValue = ints
        param = Models.Param(name,
            value  = paramValue,
        )
        param.build(self.workspace, name)

        allintegrals, errors = self.buildComponentIntegrals(region,vals,errs,ints,'bg_{}_x'.format(region))

        self.control_vals = vals
        self.control_errs = errs
        self.control_integrals = ints
        self.control_integralErrors = errors
        self.control_integralValues = allintegrals

    def fitBackground(self,region='PP',shift='',setUpsilonLambda=False,addUpsilon=True,logy=False):

        if region=='control':
            return super(HaaLimits2D, self).fitBackground(region=region, shift=shift, setUpsilonLambda=setUpsilonLambda,addUpsilon=addUpsilon,logy=logy)

        model = self.workspace.pdf('bg_{}'.format(region))
        name = 'data_prefit_{}{}'.format(region,'_'+shift if shift else '')
        hist = self.histMap[region][shift]['dataNoSig']
        print "region=", region, "\tshift=", shift, "\t", hist.GetName()
        if hist.InheritsFrom('TH1'):
            integral = hist.Integral() # 2D restricted integral?
            data = ROOT.RooDataHist(name,name,ROOT.RooArgList(self.workspace.var('x'),self.workspace.var('y')),hist)
        else:
            data = hist.Clone(name)
            integral = hist.sumEntries('x>{} && x<{} && y>{} && y<{}'.format(*self.XRANGE+self.YRANGE))

        data.Print("v")
        print "DataSetName=", data.GetName()
        fr = model.fitTo(data,ROOT.RooFit.Save(),ROOT.RooFit.SumW2Error(True))

        xFrame = self.workspace.var('x').frame()
        data.plotOn(xFrame)
        # continuum
        model.plotOn(xFrame,ROOT.RooFit.Components('cont1_{}_x'.format(region)),ROOT.RooFit.LineStyle(ROOT.kDashed))
        #model.plotOn(xFrame,ROOT.RooFit.Components('cont2_{}_x'.format(region)),ROOT.RooFit.LineStyle(ROOT.kDashed))
        #model.plotOn(xFrame,ROOT.RooFit.Components('cont1'),ROOT.RooFit.LineStyle(ROOT.kDashed))
        #model.plotOn(xFrame,ROOT.RooFit.Components('cont2'),ROOT.RooFit.LineStyle(ROOT.kDashed))
        if self.XRANGE[0]<4:
            # extended continuum when also fitting jpsi
            model.plotOn(xFrame,ROOT.RooFit.Components('cont3_{}_x'.format(region)),ROOT.RooFit.LineStyle(ROOT.kDashed))
            #model.plotOn(xFrame,ROOT.RooFit.Components('cont4_{}_x'.format(region)),ROOT.RooFit.LineStyle(ROOT.kDashed))
            #model.plotOn(xFrame,ROOT.RooFit.Components('cont3'),ROOT.RooFit.LineStyle(ROOT.kDashed))
            #model.plotOn(xFrame,ROOT.RooFit.Components('cont4'),ROOT.RooFit.LineStyle(ROOT.kDashed))
            # jpsi
            model.plotOn(xFrame,ROOT.RooFit.Components('jpsi2S'),ROOT.RooFit.LineColor(ROOT.kRed))
        if self.XRANGE[0]<3.3:
            model.plotOn(xFrame,ROOT.RooFit.Components('jpsi1S'),ROOT.RooFit.LineColor(ROOT.kRed))
        # upsilon
        model.plotOn(xFrame,ROOT.RooFit.Components('upsilon1S'),ROOT.RooFit.LineColor(ROOT.kRed))
        model.plotOn(xFrame,ROOT.RooFit.Components('upsilon2S'),ROOT.RooFit.LineColor(ROOT.kRed))
        model.plotOn(xFrame,ROOT.RooFit.Components('upsilon3S'),ROOT.RooFit.LineColor(ROOT.kRed))
        # combined model
        model.plotOn(xFrame)

        canvas = ROOT.TCanvas('c','c',800,800)
        xFrame.Draw()
        #canvas.SetLogy()
        python_mkdir(self.plotDir)
        canvas.Print('{}/model_fit_{}{}_xproj.png'.format(self.plotDir,region,'_'+shift if shift else ''))

        yFrame = self.workspace.var('y').frame()
        data.plotOn(yFrame)
        # continuum
        #model.plotOn(yFrame,ROOT.RooFit.Components('cont1_{}_y'.format(region)),ROOT.RooFit.LineStyle(ROOT.kDashed))
        model.plotOn(yFrame,ROOT.RooFit.Components('conty1_{}_y'.format(region)),ROOT.RooFit.LineStyle(ROOT.kDashed))
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

        python_mkdir(self.fitsDir)
        jfile = '{}/background_{}{}.json'.format(self.fitsDir,region,'_'+shift if shift else '')
        results = {'vals':vals, 'errs':errs, 'integral':integral}
        self.dump(jfile,results)

        return vals, errs, integral


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
                if h.InheritsFrom('TH1'):
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
                if hist.InheritsFrom('TH1'):
                    data_obs = ROOT.RooDataHist(name,name,ROOT.RooArgList(self.workspace.var('x'),self.workspace.var('y')),self.histMap[region]['']['data'])
                else:
                    data_obs = hist.Clone(name)
            self.wsimport(data_obs)

    def addBackgroundModels(self, fixAfterControl=False, fixAfterFP=False, addUpsilon=True, setUpsilonLambda=False, voigtian=False, logy=False):
        if fixAfterControl:
            self.fix()
        vals = {}
        errs = {}
        integrals = {}
        allintegrals = {}
        errors = {}
        for region in self.REGIONS:
            vals[region] = {}
            errs[region] = {}
            integrals[region] = {}
            self.buildModel(region=region, addUpsilon=addUpsilon, setUpsilonLambda=setUpsilonLambda, voigtian=voigtian)
            #self.workspace.factory('bg_{}_norm[1,0,2]'.format(region))
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

            allintegrals[region], errors[region] = self.buildComponentIntegrals(region,vals,errs,integrals,'bg_{}_x'.format(region))

        if fixAfterControl:
            self.fix(False)
        self.background_values = vals
        self.background_errors = errs
        self.background_integrals = integrals
        self.background_integralErrors = errors
        self.background_integralValues = allintegrals

    def addSignalModels(self,yFitFunc="G",isKinFit=True,**kwargs):
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
                        vals, errs, ints = self.fitSignals(h,region=region,shift=shift,yFitFunc=yFitFunc,isKinFit=isKinFit,**kwargs)
                        values[region][h][shift] = vals
                        errors[region][h][shift] = errs
                        integrals[region][h][shift] = ints
                    else:
                        valsUp, errsUp, intsUp = self.fitSignals(h,region=region,shift=shift+'Up',yFitFunc=yFitFunc,isKinFit=isKinFit,**kwargs)
                        valsDown, errsDown, intsDown = self.fitSignals(h,region=region,shift=shift+'Down',yFitFunc=yFitFunc,isKinFit=isKinFit,**kwargs)
                        valsDown, errsDown, intsDown = self.fitSignals(h,region=region,shift=shift+'Down',**kwargs)
                        values[region][h][shift+'Up'] = valsUp
                        errors[region][h][shift+'Up'] = errsUp
                        integrals[region][h][shift+'Up'] = intsUp
                        values[region][h][shift+'Down'] = valsDown
                        errors[region][h][shift+'Down'] = errsDown
                        integrals[region][h][shift+'Down'] = intsDown
                models[region][h] = self.buildSpline(h,values[region][h],errors[region][h],integrals[region][h],region,self.SIGNALSHIFTS,yFitFunc=yFitFunc,isKinFit=isKinFit,**kwargs)
                #self.workspace.factory('{}_{}_norm[1,0,9999]'.format(self.SPLINENAME.format(h=h),region))
        self.fitted_models = models

    ######################
    ### Setup datacard ###
    ######################
    def setupDatacard(self, addControl=False, doBinned=False):

        #bgs = ['bg']
        bgs = self.getComponentFractions(self.workspace.pdf('bg_PP_x'))
        bgs = [b.rstrip('_PP_x') for b in bgs]
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

        if doBinned: self.addBackgroundHists()

        # set expected
        for region in self.REGIONS:
            for proc in sigs+bgs:
                if proc in bgs and doBinned: continue
                if proc in sigs:
                    self.setExpected(proc,region,1)
                    self.addRateParam('integral_{}_{}'.format(proc,region),region,proc)
                else:
                    key = proc if proc in self.background_integralValues[region] else '{}_{}_x'.format(proc,region)
                    integral = self.background_integralValues[region][key]
                    self.setExpected(proc,region,integral)
                if 'cont' not in proc and proc not in sigs:
                    self.addShape(region,proc,proc)
                
            self.setObserved(region,-1) # reads from histogram

        if addControl:
            region = 'control'

            self.addBin(region)

            #h = self.histMap[region]['']['dataNoSig']
            #if h.InheritsFrom('TH1'):
            #    integral = h.Integral(h.FindBin(self.XRANGE[0]),h.FindBin(self.XRANGE[1]))
            #else:
            #    integral = h.sumEntries('x>{} && x<{}'.format(*self.XRANGE))
            #self.setExpected('bg',region,integral)
            for proc in bgs:
                #self.setExpected(proc,region,1)
                #self.addRateParam('integral_{}_{}'.format(proc,region),region,proc)
                key = proc if proc in self.control_integralValues else '{}_{}_x'.format(proc,region)
                integral = self.control_integralValues[key]
                self.setExpected(proc,region,integral)
                if 'cont' not in proc and proc not in sigs:
                    self.addShape(region,proc,proc)

            self.setObserved(region,-1) # reads from histogram

    def GetInitialValuesDCB(self, isKinFit=True):
        if isKinFit:
            initialValues = {
              "h125a3p6": { "a1": 6.0, "a2": 1.22, "n1": 5.9, "n2": 9.0, "sigma": 16.22},
              "h125a4"  : { "a1": 5.4, "a2": 0.99, "n1": 5.9, "n2": 9.0, "sigma": 14.78},
              "h125a5"  : { "a1": 5.0, "a2": 0.92, "n1": 6.0, "n2": 9.0, "sigma": 14.02},
              "h125a6"  : { "a1": 5.0, "a2": 1.10, "n1": 5.4, "n2": 9.4, "sigma": 14.18},
              "h125a7"  : { "a1": 5.0, "a2": 1.69, "n1": 3.9, "n2": 3.7, "sigma": 14.29},
              "h125a9"  : { "a1": 5.2, "a2": 1.07, "n1": 2.8, "n2": 9.0, "sigma": 10.58},
              "h125a11" : { "a1": 1.8, "a2": 1.55, "n1": 6.0, "n2": 4.1, "sigma": 9.770},
              "h125a13" : { "a1": 2.0, "a2": 2.66, "n1": 6.0, "n2": 1.4, "sigma": 10.04},
              "h125a15" : { "a1": 1.3, "a2": 2.19, "n1": 6.0, "n2": 1.9, "sigma": 7.840},
              "h125a17" : { "a1": 1.5, "a2": 2.08, "n1": 6.0, "n2": 1.8, "sigma": 6.990},
              "h125a19" : { "a1": 1.6, "a2": 3.34, "n1": 6.0, "n2": 0.6, "sigma": 6.220},
              "h125a21" : { "a1": 1.2, "a2": 1.78, "n1": 6.0, "n2": 2.0, "sigma": 5.339},
              "125" : {"a1" : 5.0, "a2": 1.5, "n1": 6.0, "n2": 1.5, "sigma": 10.0},
              "h300a5"  : { "a1": 2.5, "a2": 1.28, "n1": 6.0, "n2": 8.6, "sigma": 37.95},
              "h300a7"  : { "a1": 2.6, "a2": 1.19, "n1": 3.1, "n2": 9.0, "sigma": 35.05},
              "h300a9"  : { "a1": 2.2, "a2": 1.45, "n1": 6.0, "n2": 6.6, "sigma": 32.02},
              "h300a11" : { "a1": 2.2, "a2": 1.40, "n1": 5.6, "n2": 9.0, "sigma": 29.30},
              "h300a13" : { "a1": 1.8, "a2": 1.74, "n1": 6.0, "n2": 4.1, "sigma": 26.53},
              "h300a15" : { "a1": 1.6, "a2": 1.98, "n1": 6.0, "n2": 3.6, "sigma": 24.14},
              "h300a17" : { "a1": 1.5, "a2": 2.13, "n1": 6.0, "n2": 2.9, "sigma": 22.82},
              "h300a19" : { "a1": 1.3, "a2": 2.00, "n1": 6.0, "n2": 3.0, "sigma": 21.20},
              "h300a21" : { "a1": 1.2, "a2": 2.38, "n1": 6.0, "n2": 2.3, "sigma": 19.85},
              "300" : {"a1" : 2.0, "a2": 1.7, "n1": 6.0, "n2": 5.0, "sigma": 27.0},
              "h750a5"  : { "a1": 2.4, "a2": 1.28, "n1": 3.7, "n2": 9.5, "sigma": 104.2},
              "h750a7"  : { "a1": 3.0, "a2": 1.41, "n1": 0.9, "n2": 9.5, "sigma": 103.8},
              "h750a9"  : { "a1": 2.0, "a2": 1.46, "n1": 5.8, "n2": 9.5, "sigma": 92.20},
              "h750a11" : { "a1": 1.9, "a2": 1.57, "n1": 6.0, "n2": 9.5, "sigma": 84.60},
              "h750a13" : { "a1": 1.7, "a2": 1.60, "n1": 6.0, "n2": 9.5, "sigma": 77.03},
              "h750a15" : { "a1": 1.6, "a2": 1.66, "n1": 6.0, "n2": 9.5, "sigma": 73.03},
              "h750a17" : { "a1": 1.4, "a2": 1.69, "n1": 6.0, "n2": 8.3, "sigma": 67.98},
              "h750a19" : { "a1": 1.8, "a2": 2.10, "n1": 2.5, "n2": 4.0, "sigma": 69.00},
              "h750a21" : { "a1": 1.3, "a2": 1.90, "n1": 6.0, "n2": 6.2, "sigma": 61.96},
              "750" : {"a1" : 2.0, "a2": 1.7, "n1": 6.0, "n2": 7.5, "sigma": 80.0}
            }
        else:
            initialValues = {
              "h125a3p6": { "a1": 3.1, "a2": 2.96, "n1": 2.3, "n2": 1.3, "sigma": 12.10},
              "h125a4"  : { "a1": 5.0, "a2": 2.57, "n1": 3.3, "n2": 3.2, "sigma": 12.96},
              "h125a5"  : { "a1": 5.0, "a2": 3.16, "n1": 2.4, "n2": 1.2, "sigma": 14.46},
              "h125a6"  : { "a1": 6.0, "a2": 4.05, "n1": 2.4, "n2": 0.6, "sigma": 13.62},
              "h125a7"  : { "a1": 6.0, "a2": 3.36, "n1": 5.7, "n2": 0.8, "sigma": 14.13},
              "h125a9"  : { "a1": 6.0, "a2": 2.83, "n1": 3.4, "n2": 3.3, "sigma": 14.36},
              "h125a11" : { "a1": 5.9, "a2": 2.55, "n1": 3.0, "n2": 1.5, "sigma": 14.33},
              "h125a13" : { "a1": 6.0, "a2": 3.22, "n1": 2.5, "n2": 1.4, "sigma": 14.29},
              "h125a15" : { "a1": 5.0, "a2": 3.33, "n1": 2.0, "n2": 3.3, "sigma": 13.91},
              "h125a17" : { "a1": 5.5, "a2": 2.84, "n1": 4.9, "n2": 1.7, "sigma": 13.57},
              "h125a19" : { "a1": 5.3, "a2": 2.89, "n1": 4.5, "n2": 1.9, "sigma": 13.90},
              "h125a21" : { "a1": 5.3, "a2": 3.33, "n1": 1.2, "n2": 1.2, "sigma": 13.74},
              "125" : {"a1" : 5.0, "a2": 2.75, "n1": 4.0, "n2": 1.5, "sigma": 14.0},
              "h300a5"  : { "a1": 5.5, "a2": 3.55, "n1": 3.7, "n2": 2.2, "sigma": 36.24},
              "h300a7"  : { "a1": 3.3, "a2": 3.50, "n1": 6.0, "n2": 6.5, "sigma": 37.40},
              "h300a9"  : { "a1": 3.3, "a2": 3.47, "n1": 4.4, "n2": 3.8, "sigma": 39.80},
              "h300a11" : { "a1": 5.0, "a2": 3.50, "n1": 2.5, "n2": 8.0, "sigma": 39.77},
              "h300a13" : { "a1": 5.2, "a2": 5.60, "n1": 4.1, "n2": 5.9, "sigma": 40.83},
              "h300a15" : { "a1": 5.3, "a2": 3.61, "n1": 2.9, "n2": 3.0, "sigma": 40.16},
              "h300a17" : { "a1": 5.6, "a2": 3.79, "n1": 4.3, "n2": 1.9, "sigma": 40.49},
              "h300a19" : { "a1": 5.0, "a2": 3.77, "n1": 5.6, "n2": 2.1, "sigma": 41.08},
              "h300a21" : { "a1": 5.0, "a2": 3.53, "n1": 4.5, "n2": 8.7, "sigma": 40.63},
              "300" : {"a1" : 5.0, "a2": 3.5, "n1": 4.5, "n2": 5.0, "sigma": 40.00},
              "h750a5"  : { "a1": 2.5, "a2": 4.80, "n1": 7.00, "n2": 19.0, "sigma": 95.50},
              "h750a7"  : { "a1": 2.7, "a2": 3.90, "n1": 18.0, "n2": 16.0, "sigma": 102.8},
              "h750a9"  : { "a1": 3.4, "a2": 5.50, "n1": 20.0, "n2": 15.0, "sigma": 107.3},
              "h750a11" : { "a1": 4.7, "a2": 5.70, "n1": 3.20, "n2": 19.0, "sigma": 109.8},
              "h750a13" : { "a1": 4.8, "a2": 3.46, "n1": 8.30, "n2": 19.9, "sigma": 111.3},
              "h750a15" : { "a1": 4.1, "a2": 4.20, "n1": 12.5, "n2": 19.0, "sigma": 112.7},
              "h750a17" : { "a1": 4.0, "a2": 4.33, "n1": 9.20, "n2": 1.00, "sigma": 114.0},
              "h750a19" : { "a1": 5.8, "a2": 5.80, "n1": 4.30, "n2": 19.0, "sigma": 114.3},
              "h750a21" : { "a1": 4.1, "a2": 5.30, "n1": 17.6, "n2": 15.0, "sigma": 114.7},
              "750" : {"a1" : 4.8, "a2": 5.00, "n1": 4.6, "n2": 16.0, "sigma": 109.0}
            }
        return initialValues


    ###################
    ### Systematics ###
    ###################
    def addSystematics(self,doBinned=False,addControl=False):
        self.sigProcesses = tuple([self.SPLINENAME.format(h=h) for h in self.HMASSES])
        #self.bgProcesses = ('bg',)
        bgs = self.getComponentFractions(self.workspace.pdf('bg_PP_x'))
        bgs = tuple([b.rstrip('_PP_x') for b in bgs])
        self._addLumiSystematic()
        self._addMuonSystematic()
        self._addTauSystematic()
        self._addShapeSystematic()
        self._addControlSystematics()
        if not doBinned and not addControl: self._addControlSystematics()

    def _addComponentSystematic(self,addControl=False):
        bgs = self.getComponentFractions(self.workspace.pdf('bg_PP_x'))
        bgs = [b.rstrip('_PP_x') for b in bgs if 'cont' not in b]
        bins = self.REGIONS
        if addControl: bins += ['control']
        syst = {}
        for bg in bgs:
            for b in bins:
                key = bg if bg in self.control_integralErrors else '{}_control'.format(bg)
                syst[(bg,),(b,)] = 1 + self.control_integralErrors[key]
                #if b=='control':
                #    key = bg if bg in self.control_integralErrors else '{}_{}'.format(bg,b)
                #    syst[(bg,),(b,)] = 1 + self.control_integralErrors[key]
                #else:
                #    key = bg if bg in self.background_integralErrors[b] else '{}_{}'.format(bg,b)
                #    syst[(bg,),(b,)] = 1 + self.background_integralErrors[b][key]
        #self.addSystematic('{process}_normUnc','lnN',systematics=syst)

    ###################################
    ### Save workspace and datacard ###
    ###################################
    def save(self,name='mmmt', subdirectory=''):
        processes = {}
        bgs = self.getComponentFractions(self.workspace.pdf('bg_PP_x'))
        bgs = [b.rstrip('_PP_x') for b in bgs]
        for h in self.HMASSES:
            processes[self.SIGNAME.format(h=h,a='X')] = [self.SPLINENAME.format(h=h)] + bgs
        if subdirectory == '':
          self.printCard('datacards_shape/MuMuTauTau/{}'.format(name),processes=processes,blind=False,saveWorkspace=True)
        else:
          self.printCard('datacards_shape/MuMuTauTau/' + subdirectory + '{}'.format(name),processes=processes,blind=False,saveWorkspace=True)

