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
            #bg = Models.Landau('bg',
            #    x = 'y',
            #    mu    = [50,0,200],
            #   sigma = [10,0,100],
            #)
            #bg = Models.Polynomial('bg',
            #    order = 3,
            #    p0 = [50,0,10000],
            #    p1 = [-5,-100,100],
            #    p2 = [-0.3,-100,100],
            #)

            #bg = Models.Polynomial('bg',
            #    order = 4,
            #    p0 = [-1,0,10000],
            #    p1 = [0.25,-100,100],
            #    p2 = [0.03,-100,100],
            #    p3 = [0.5,-100,100],
            #)

            #bg = Models.Polynomial('bg',
            #    order = 5,
            #    p0 = [965,0,10000],
            #    p1 = [-12, -100, 100],
            #    p2 = [0.06,-100,100],
            #    p3 = [-0.1,-100,100],
            #    p4 = [-0.01,-100,100],
            #)

            erf1 = Models.Erf('erf1',
                x = 'y',
                erfScale = [0.05,0,10],
                erfShift = [70,10,200],
            )
            nameE1 = 'erf1{}'.format('_'+tag if tag else '')
            erf1.build(self.workspace,nameE1)

            cont1 = Models.Exponential('conty1',
                x = 'y',
                lamb = [-0.05,-1,0],
            )
            nameC1 = 'conty1{}'.format('_'+tag if tag else '')
            cont1.build(self.workspace,nameC1)

            bg = Models.Prod('bg',
                nameE1,
                nameC1,
            )
        else:
            # Landau only
            #bg = Models.Landau('bg',
            #    x = 'y',
            #    mu    = [5,0,20],
            #    sigma = [1,0,10],
            #)

            # landau plus gaussian
            #land1 = Models.Landau('land1',
            #    x = 'y',
            #    mu    = [5,0,20],
            #    sigma = [1,0,10],
            #)
            #nameL1 = 'land1{}'.format('_'+tag if tag else '')
            #land1.build(self.workspace,nameL1)

            ## add a guassian summed for tt ?
            #gaus1 = Models.Gaussian('gaus1',
            #    x = 'y',
            #    mean = [1.5,0,4],
            #    sigma = [0.4,0,2],
            #)
            #nameG1 = 'gaus1{}'.format('_'+tag if tag else '')
            #gaus1.build(self.workspace,nameG1)

            #bg = Models.Sum('bg',
            #    **{
            #        nameL1     : [0.9,0,1],
            #        nameG1     : [0.5,0,1],
            #        'recursive': True,
            #    }
            #)

            # landua plus upsilon gaussian
            land1 = Models.Landau('land1',
                x = 'y',
                mu    = [1.5,0,5],
                sigma = [0.4,0,2],
            )
            nameL1 = 'land1{}'.format('_'+tag if tag else '')
            land1.build(self.workspace,nameL1)

            # jpsi
            #jpsi2 = Models.Voigtian('jpsi2S',
            #    x = 'y',
            #    mean  = [3.7,3.6,3.8],
            #    sigma = [0.1,0.01,0.5],
            #    width = [0.1,0.01,0.5],
            #)
            #nameJ2 = 'jpsi2Stt'
            #jpsi2.build(self.workspace,nameJ2)


            # add a guassian for upsilon
            upsilon1 = Models.Gaussian('upsilon1',
                x = 'y',
                mean = [6,5,7],
                sigma = [0.02,0,1],
            )
            nameU1 = 'upsilontt'
            upsilon1.build(self.workspace,nameU1)

            bg = Models.Sum('bg',
                **{
                    nameL1     : [0.95,0,1],
                    #nameJ2     : [0.1,0,1],
                    nameU1     : [0.1,0,1],
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
        cont1 = Models.Prod('cont1',
            'cont1_{}_x'.format(region),
            'bg_{}_y'.format(region),
        )
        name = 'cont1_{}'.format(region)
        cont1.build(self.workspace,name)

        cont3 = Models.Prod('cont3',
            'cont3_{}_x'.format(region),
            'bg_{}_y'.format(region),
        )
        name = 'cont3_{}'.format(region)
        cont3.build(self.workspace,name)

        jpsi1S = Models.Prod('jpsi1S',
            'jpsi1S_{}_x'.format(region),
            'bg_{}_y'.format(region),
        )
        name = 'jpsi1S_{}'.format(region)
        jpsi1S.build(self.workspace,name)
  
        jpsi2S = Models.Prod('jpsi2S',
            'jpsi2S_{}_x'.format(region),
            'bg_{}_y'.format(region),
        )
        name = 'jpsi2S_{}'.format(region)
        jpsi2S.build(self.workspace,name)

        upsilon1S = Models.Prod('upsilon1S',
            'upsilon1S_{}_x'.format(region),
            'bg_{}_y'.format(region),
        )
        name = 'upsilon1S_{}'.format(region)
        upsilon1S.build(self.workspace,name)

        upsilon2S = Models.Prod('upsilon2S',
            'upsilon2S_{}_x'.format(region),
            'bg_{}_y'.format(region),
        )
        name = 'upsilon2S_{}'.format(region)
        upsilon2S.build(self.workspace,name)

        upsilon3S = Models.Prod('upsilon3S',
            'upsilon3S_{}_x'.format(region),
            'bg_{}_y'.format(region),
        )
        name = 'upsilon3S_{}'.format(region)
        upsilon3S.build(self.workspace,name)

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
        load = kwargs.get('load',False)
        skipFit = kwargs.get('skipFit',False)
        dobgsig = kwargs.get('doBackgroundSignal',False)
        amasses = self.AMASSES
        if h>125:      amasses = [a for a in amasses if a not in ['3p6',4,6]]
        avals = [float(str(x).replace('p','.')) for x in amasses]
        histMap = self.histMap[region][shift]
        tag= '{}{}'.format(region,'_'+shift if shift else '')

        # initial fit
        if load:
            # load the previous fit
            results, errors, integrals = self.loadSignalFit(h,tag,region,shift)
        elif shift and not skipFit:
            # load the central fits
            results, errors, integrals = self.loadSignalFit(h,region,region)
        else:
            results = {}
            errors = {}
            integrals = {}
            results[h] = {}
            errors[h] = {}
            integrals[h] = {}
        if self.YRANGE[1] > 100: 
            if yFitFunc == "DCB_Fix": initialMeans = self.GetInitialDCBMean()
            if "DCB" in yFitFunc: initialValuesDCB = self.GetInitialValuesDCB(isKinFit=isKinFit)
            elif yFitFunc == "DG": initialValuesDG = self.GetInitialValuesDG(region=region)
        elif yFitFunc == "L": initialValuesL = self.GetInitialValuesDitau(isLandau=True)
        elif yFitFunc == "V": initialValuesV = self.GetInitialValuesDitau(isLandau=False)
        for a in amasses:
            aval = float(str(a).replace('p','.'))
            thisxrange = [0.8*aval, 1.2*aval]
            thisyrange = [0.15*h, 1.2*h] if self.YRANGE[1]>100 else [self.YRANGE[0], 1.2*aval]
            if self.YRANGE[1]>100:
                if  h == 125:  thisyrange = [20, 150]
                elif h == 300: thisyrange = [40,360]
                elif h == 750: thisyrange = [140,900]
            ws = ROOT.RooWorkspace('sig')
            ws.factory('x[{0}, {1}]'.format(*thisxrange)) 
            #ws.factory('x[{0}, {1}]'.format(*self.XRANGE))
            ws.var('x').setUnit('GeV')
            ws.var('x').setPlotLabel(self.XLABEL)
            ws.var('x').SetTitle(self.XLABEL)
            ws.factory('y[{0}, {1}]'.format(*thisyrange)) 
            #ws.factory('y[{0}, {1}]'.format(*self.YRANGE))
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
                        mean  = [0.75*h,0,1.25*h],
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
                        sigma = [initialValuesDCB["h"+str(h)+"a"+str(a)]["sigma"],0.05*h,0.5*h],
                        a1    = [initialValuesDCB["h"+str(h)+"a"+str(a)]["a1"],0.1,10],
                        n1    = [initialValuesDCB["h"+str(h)+"a"+str(a)]["n1"],1,30],
                        a2    = [initialValuesDCB["h"+str(h)+"a"+str(a)]["a2"],0.1,10],
                        n2    = [initialValuesDCB["h"+str(h)+"a"+str(a)]["n2"],0.1,30],
                    )
                elif yFitFunc == "DCB_Fix":
                    MEAN = initialMeans["h"+str(h)+"a"+str(a)]["mean"]
                    self.YRANGE[0] = MEAN
                    modely = Models.DoubleCrystalBall('sigy',
                        x = 'y',
                        mean  = [MEAN, MEAN-2, MEAN+2],
                        sigma = [initialValuesDCB["h"+str(h)+"a"+str(a)]["sigma"],0.05*h,0.5*h],
                        a1    = [initialValuesDCB["h"+str(h)+"a"+str(a)]["a1"],0.1,10],
                        n1    = [initialValuesDCB["h"+str(h)+"a"+str(a)]["n1"],1,20],
                        a2    = [initialValuesDCB["h"+str(h)+"a"+str(a)]["a2"],0.1,10],
                        n2    = [initialValuesDCB["h"+str(h)+"a"+str(a)]["n2"],0.1,5],
                    )
                elif yFitFunc == "DG":
                    modely = Models.DoubleSidedGaussian('sigy',
                        x = 'y',
                        #mean  = [h,0,1.25*h],
                        #sigma1 = [0.1*h,0.05*h,0.5*h],
                        #sigma2 = [0.2*h,0.05*h,0.5*h],
                        mean    = [initialValuesDG["h"+str(h)+"a"+str(a)]["mean"],0,1.1*h],
                        sigma1  = [initialValuesDG["h"+str(h)+"a"+str(a)]["sigma1"],0.05*h,0.5*h],
                        sigma2  = [initialValuesDG["h"+str(h)+"a"+str(a)]["sigma2"],0.05*h,0.5*h],
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
                        mean  = [0.5*aval,0,1.25*aval],
                        sigma = [0.1*aval,0.01,0.5*aval],
                    )
                elif yFitFunc == "V":
                    modely = Models.Voigtian('sigy',
                        x = 'y',
                        mean  = [initialValuesV["h"+str(h)+"a"+str(a)]["mean_sigy"],0.75,30],
                        width = [initialValuesV["h"+str(h)+"a"+str(a)]["width_sigy"],0.01,5],
                        sigma = [initialValuesV["h"+str(h)+"a"+str(a)]["sigma_sigy"],0.01,5],
                    )
                elif yFitFunc == "CB":
                    modely = Models.CrystalBall('sigy',
                        x = 'y',
                        mean  = [0.5*aval,0,30],
                        sigma = [0.1*aval,0,5],
                        a = [1.0,0.5,5],
                        n = [0.5,0.1,10],
                    )
                elif yFitFunc == "DCB":
                    modely = Models.DoubleCrystalBall('sigy',
                        x = 'y',
                        mean  = [0.5*aval,0.5,30],
                        sigma = [0.1*aval,0.1,5],
                        a1 = [1.0,0.1,6],
                        n1 = [0.9,0.1,6],
                        a2 = [2.0,0.1,10],
                        n2 = [1.5,0.1,10],
                    )
                elif yFitFunc == "DG":
                    modely = Models.DoubleSidedGaussian('sigy',
                        x = 'y',
                        mean  = [0.5*aval,0,30],
                        sigma1 = [0.1*aval,0.05*aval,0.4*aval],
                        sigma2 = [0.3*aval,0.05*aval,0.4*aval],
                        yMax = self.YRANGE[1],
                    )
                elif yFitFunc == "DV":
                    modely = Models.DoubleSidedVoigtian('sigy',
                        x = 'y',
                        mean  = [0.5*aval,0,30],
                        sigma1 = [0.1*aval,0.05*aval,0.4*aval],
                        sigma2 = [0.3*aval,0.05*aval,0.4*aval],
                        width1 = [0.1,0.01,5],
                        width2 = [0.3,0.01,5],
                        yMax = self.YRANGE[1],
                    )
                elif yFitFunc == "errG":
                    tterf = Models.Erf('tterf',
                       x = 'y',
                       erfScale = [0.4,0.1,5],
                       erfShift = [0.2*aval,0.05*aval,aval],
                    )
                    ttgaus = Models.Gaussian('ttgaus',
                       x = 'y',
                       mean  = [0.45*aval,0,aval],
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
                        mu  = [initialValuesL["h"+str(h)+"a"+str(a)]["mu_ttland"],0.01,30],
                        sigma = [initialValuesL["h"+str(h)+"a"+str(a)]["sigma_ttland"],0.01,aval],
                    )
                    ttland.build(ws,'ttland')
                    ttgaus = Models.Gaussian('ttgaus',
                       x = 'y',
                       mean  = [initialValuesL["h"+str(h)+"a"+str(a)]["mean_ttgaus"],0.01,30],
                       #mean  = [initialValuesL["h"+str(h)+"a"+str(a)]["mean_ttgaus"],0.2*initialValuesL["h"+str(h)+"a"+str(a)]["mean_ttgaus"],30],
                       sigma = [initialValuesL["h"+str(h)+"a"+str(a)]["sigma_ttgaus"],0.01,aval],
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

            name = 'h{}_a{}_{}'.format(h,a,tag)
            model.build(ws, name)
            if load:
                for param in results[h][a]:
                    ws.var(param).setVal(results[h][a][param])
            elif shift and not skipFit:
                for param in results[h][a]:
                    #ws.var(param+'_{}'.format(shift)).setVal(results[h][a][param])
                    ws.var(param).setVal(results[h][a][param])
            hist = histMap[self.SIGNAME.format(h=h,a=a)]
            saveDir = '{}/{}'.format(self.plotDir,shift if shift else 'central')
            if not skipFit:
                results[h][a], errors[h][a] = model.fit2D(ws, hist, name, saveDir=saveDir, save=True, doErrors=True)
                if self.binned:
                    integral = histMap[self.SIGNAME.format(h=h,a=a)].Integral()
                else:
                    integral = histMap[self.SIGNAME.format(h=h,a=a)].sumEntries('x>{} && x<{} && y>{} && y<{}'.format(*self.XRANGE+self.YRANGE))
                    if integral!=integral:
                        logging.error('Integral for spline is invalid: h{h} a{a} {region} {shift}'.format(h=h,a=a,region=region,shift=shift))
                        raise
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
        elif yFitFunc == "L"   : yparameters = ['mean_ttgaus', 'sigma_ttgaus','mu_ttland','sigma_ttland']
        else: raise
        for param in ['mean','width','sigma']:
            name = '{}_{}{}'.format('x'+param,h,tag)
            xerrs = [0]*len(amasses)
            vals = [results[h][a]['{}_sigx'.format(param)] for a in amasses]
            errs = [errors[h][a]['{}_sigx'.format(param)] for a in amasses]
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

    def buildSpline(self,h,vals,errs,integrals,region='PP',shifts=[],isKinFit=False,**kwargs):
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
        yFitFunc = kwargs.pop('yFitFunc','G')
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
            if yFitFunc == "errG" or yFitFunc == "L": paramValues = [vals[''][h][a]['{param}'.format(param=param)] for a in amasses]
            else: paramValues = [vals[''][h][a]['{param}_sigy'.format(param=param)] for a in amasses]
            paramShifts = {}
            for shift in shifts:
                if yFitFunc == "errG" or yFitFunc == "L":
                    shiftValuesUp   = [vals[shift+'Up'  ][h][a]['{param}'.format(param=param)] for a in amasses]
                    shiftValuesDown = [vals[shift+'Down'][h][a]['{param}'.format(param=param)] for a in amasses]
                else:
                    shiftValuesUp   = [vals[shift+'Up'  ][h][a]['{param}_sigy'.format(param=param)] for a in amasses]
                    shiftValuesDown = [vals[shift+'Down'][h][a]['{param}_sigy'.format(param=param)] for a in amasses]
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
            modelx = Models.Voigtian(self.SPLINENAME.format(h=h)+'_x',
                **{param: 'x{param}_h{h}_{region}_sigx'.format(param=param, h=h, region=region) for param in params}
            )
        modelx.build(self.workspace,'{}_{}'.format(self.SPLINENAME.format(h=h),region+'_x'))

        if   yFitFunc == "V"   : ym = Models.Voigtian
        elif yFitFunc == "G"   : ym = Models.Gaussian
        elif yFitFunc == "CB"  : ym = Models.CrystalBall
        elif yFitFunc == "DCB" : ym = Models.DoubleCrystalBall
        elif yFitFunc == "DG"  : ym = Models.DoubleSidedGaussian
        elif yFitFunc == "DV"  : ym = Models.DoubleSidedVoigtian
        elif yFitFunc != "L" and yFitFunc != "errG": raise

        if fit:
            print 'Need to reimplement fitting'
            raise
        else:
            if yFitFunc == 'errG':
                modely_gaus = Models.Gaussian("model_gaus",
                    x = 'y',
                     **{param: 'y{param}_ttgaus_h{h}_{region}_sigy'.format(param=param, h=h, region=region) for param in ['mean','sigma']}
                )
                modely_gaus.build(self.workspace,'{}_{}'.format(self.SPLINENAME.format(h=h),region+'_gaus_y'))
                modely_erf = Models.Erf("model_erf",
                    x = 'y',
                     **{param: 'y{param}_tterf_h{h}_{region}_sigy'.format(param=param, h=h, region=region) for param in ['ergScales','erfShifts']}
                )
                modely_erf.build(self.workspace,'{}_{}'.format(self.SPLINENAME.format(h=h),region+'_erf_y'))
                modely = Models.Prod(self.SPLINENAME.format(h=h)+'_y',
                    '{}_{}'.format(self.SPLINENAME.format(h=h),region+'_gaus_y'),
                    '{}_{}'.format(self.SPLINENAME.format(h=h),region+'_erf_y'),
                )
            elif yFitFunc == 'L':
                modely_gaus = Models.Gaussian("model_gaus",
                    x = 'y',
                     **{param: 'y{param}_ttgaus_h{h}_{region}_sigy'.format(param=param, h=h, region=region) for param in ['mean','sigma']}
                )
                modely_gaus.build(self.workspace,'{}_{}'.format(self.SPLINENAME.format(h=h),region+'_gaus_y'))
                modely_land = Models.Landau("model_land",
                    x = 'y',
                     **{param: 'y{param}_ttland_h{h}_{region}_sigy'.format(param=param, h=h, region=region) for param in ['mu','sigma']}
                )
                modely_land.build(self.workspace,'{}_{}'.format(self.SPLINENAME.format(h=h),region+'_land_y'))
                modely = Models.Prod(self.SPLINENAME.format(h=h)+'_y',
                    '{}_{}'.format(self.SPLINENAME.format(h=h),region+'_gaus_y'),
                    '{}_{}'.format(self.SPLINENAME.format(h=h),region+'_land_y'),
                )
            else:
                modely = ym(self.SPLINENAME.format(h=h)+'_y',
                    x = 'y',
                    yMax = self.YRANGE[1],
                    **{param: 'y{param}_h{h}_{region}_sigy'.format(param=param, h=h, region=region) for param in yparameters}
                )
        modely.build(self.workspace,'{}_{}'.format(self.SPLINENAME.format(h=h),region+'_y'))
                
        model = Models.Prod(self.SPLINENAME.format(h=h),
            '{}_{}'.format(self.SPLINENAME.format(h=h),region+'_x'),
            '{}_{}'.format(self.SPLINENAME.format(h=h),region+'_y'),
        )
        model.build(self.workspace,'{}_{}'.format(self.SPLINENAME.format(h=h),region))

        return model

    def addControlModels(self, addUpsilon=True, setUpsilonLambda=False, voigtian=False, logy=False, load=False, skipFit=False):
        region = 'control'
        super(HaaLimits2D, self).buildModel(region=region, addUpsilon=addUpsilon, setUpsilonLambda=setUpsilonLambda, voigtian=voigtian)
        #self.workspace.factory('bg_{}_norm[1,0,2]'.format(region))
        if load:
            vals, errs, ints = self.loadBackgroundFit(region)
        if not skipFit:
            vals, errs, ints = self.fitBackground(region=region, setUpsilonLambda=setUpsilonLambda, addUpsilon=addUpsilon, logy=logy)
        
        # integral
        name = 'integral_bg_{}'.format(region)
        paramValue = ints
        param = Models.Param(name,
            value  = paramValue,
        )
        param.build(self.workspace, name)
        
        if load:
            allintegrals, errors = self.loadComponentIntegrals(region)
        if not skipFit:
            allintegrals, errors = self.buildComponentIntegrals(region,vals,errs,ints, 'bg_control')

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
        if hist.InheritsFrom('TH1'):
            integral = hist.Integral() # 2D restricted integral?
            data = ROOT.RooDataHist(name,name,ROOT.RooArgList(self.workspace.var('x'),self.workspace.var('y')),hist)
        else:
            data = hist.Clone(name)
            integral = hist.sumEntries('x>{} && x<{} && y>{} && y<{}'.format(*self.XRANGE+self.YRANGE))

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
        mi = xFrame.GetMinimum()
        ma = xFrame.GetMaximum()
        if mi<0:
            xFrame.SetMinimum(0.1)
        python_mkdir(self.plotDir)
        canvas.Print('{}/model_fit_{}{}_xproj.png'.format(self.plotDir,region,'_'+shift if shift else ''))
        canvas.SetLogy(True)
        canvas.Print('{}/model_fit_{}{}_xproj_log.png'.format(self.plotDir,region,'_'+shift if shift else ''))

        yFrame = self.workspace.var('y').frame()
        data.plotOn(yFrame)
        # continuum
        #model.plotOn(yFrame,ROOT.RooFit.Components('cont1_{}_y'.format(region)),ROOT.RooFit.LineStyle(ROOT.kDashed))
        model.plotOn(yFrame,ROOT.RooFit.Components('conty1_{}_y'.format(region)),ROOT.RooFit.LineStyle(ROOT.kDashed))
        # combined model
        model.plotOn(yFrame)

        canvas = ROOT.TCanvas('c','c',800,800)
        yFrame.Draw()
        mi = yFrame.GetMinimum()
        ma = yFrame.GetMaximum()
        if mi<0:
            yFrame.SetMinimum(0.1)
        canvas.Print('{}/model_fit_{}{}_yproj.png'.format(self.plotDir,region,'_'+shift if shift else ''))
        canvas.SetLogy(True)
        canvas.Print('{}/model_fit_{}{}_yproj_log.png'.format(self.plotDir,region,'_'+shift if shift else ''))

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
    def addData(self,asimov=False,addSignal=False,addControl=False,**kwargs):
        mh = kwargs.pop('h',125)
        ma = kwargs.pop('a',15)
        for region in self.REGIONS:
            name = 'data_obs_{}'.format(region)
            hist = self.histMap[region]['']['data']
            if asimov:
                # generate a toy data observation from the model
                model = self.workspace.pdf('bg_{}'.format(region))
                h = self.histMap[region]['']['dataNoSig']
                if h.InheritsFrom('TH1'):
                    integral = h.Integral() # 2D integral?
                else:
                    integral = h.sumEntries('x>{} && x<{} && y>{} && y<{}'.format(*self.XRANGE+self.YRANGE))
                data_obs = model.generate(ROOT.RooArgSet(self.workspace.var('x'),self.workspace.var('y')),int(integral))
                if addSignal:
                    logging.info('Generating dataset with signal {}'.format(region))
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

            if hist.InheritsFrom('TH1'):
                pass
            else:
                xFrame = self.workspace.var('x').frame()
                data_obs.plotOn(xFrame)
                canvas = ROOT.TCanvas('c','c',800,800)
                xFrame.Draw()
                mi = xFrame.GetMinimum()
                ma = xFrame.GetMaximum()
                if mi<0:
                    xFrame.SetMinimum(0.1)
                python_mkdir(self.plotDir)
                canvas.Print('{}/data_obs_{}_xproj.png'.format(self.plotDir,region))
                canvas.SetLogy(True)
                canvas.Print('{}/data_obs_{}_xproj_log.png'.format(self.plotDir,region))

                yFrame = self.workspace.var('y').frame()
                data_obs.plotOn(yFrame)
                canvas = ROOT.TCanvas('c','c',800,800)
                yFrame.Draw()
                mi = yFrame.GetMinimum()
                ma = yFrame.GetMaximum()
                if mi<0:
                    yFrame.SetMinimum(0.1)
                python_mkdir(self.plotDir)
                canvas.Print('{}/data_obs_{}_yproj.png'.format(self.plotDir,region))
                canvas.SetLogy(True)
                canvas.Print('{}/data_obs_{}_yproj_log.png'.format(self.plotDir,region))



        if addControl: #ADDED BY KYLE
            region = 'control'
            name = 'data_obs_{}'.format(region)
            hist = self.histMap[region]['']['data']
            if hist.InheritsFrom('TH1'):
                data_obs = ROOT.RooDataHist(name,name,ROOT.RooArgList(self.workspace.var('x')),hist)
            else:
                data_obs = hist.Clone(name)
            self.wsimport(data_obs, ROOT.RooFit.RecycleConflictNodes() )


    def addBackgroundModels(self, fixAfterControl=False, fixAfterFP=False, addUpsilon=True, setUpsilonLambda=False, voigtian=False, logy=False, load=False, skipFit=False):
        if fixAfterControl:
            self.fix()
        if setUpsilonLambda:
            self.workspace.arg('lambda_cont1_FP').setConstant(True)
            self.workspace.arg('lambda_cont1_PP').setConstant(True)
        vals = {}
        errs = {}
        integrals = {}
        allintegrals = {}
        errors = {}
        for region in self.REGIONS:
            vals[region] = {}
            errs[region] = {}
            integrals[region] = {}
            if region == 'PP' and fixAfterFP and addUpsilon and self.XRANGE[0]<=9 and self.XRANGE[1]>=11:
                self.fix()
            self.buildModel(region=region, addUpsilon=addUpsilon, setUpsilonLambda=setUpsilonLambda, voigtian=voigtian)
            #self.workspace.factory('bg_{}_norm[1,0,2]'.format(region))
            for shift in ['']+self.BACKGROUNDSHIFTS:
                if shift=='':
                    if load:
                        v, e, i = self.loadBackgroundFit(region)
                    else:
                        v, e, i = self.fitBackground(region=region, setUpsilonLambda=setUpsilonLambda, addUpsilon=addUpsilon, logy=logy)
                    vals[region][shift] = v
                    errs[region][shift] = e
                    integrals[region][shift] = i
                else:
                    if load:
                        vUp, eUp, iUp = self.loadBackgroundFit(region,shift+'Up')
                        vDown, eDown, iDown = self.loadBackgroundFit(region,shift+'Down')
                    if not skipFit:
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

            if load:
                allintegrals[region], errors[region] = self.loadComponentIntegrals(region)
            if not skipFit:
                allintegrals[region], errors[region] = self.buildComponentIntegrals(region,vals,errs,integrals, 'bg_{}_x'.format(region))

        if fixAfterControl:
            self.fix(False)
        self.background_values = vals
        self.background_errors = errs
        self.background_integrals = integrals
        self.background_integralErrors = errors
        self.background_integralValues = allintegrals

    def addSignalModels(self,yFitFuncFP="V", yFitFuncPP="V",isKinFit=False,**kwargs):
        models = {}
        values = {}
        errors = {}
        integrals = {}
        for region in self.REGIONS:
            models[region] = {}
            values[region] = {}
            errors[region] = {}
            integrals[region] = {}
            if region == 'PP':  yFitFunc=yFitFuncPP
            else: yFitFunc = yFitFuncFP
            for h in self.HMASSES:
                values[region][h] = {}
                errors[region][h] = {}
                integrals[region][h] = {}
                for shift in ['']+self.SIGNALSHIFTS+self.QCDSHIFTS:
                    if shift == '':
                        vals, errs, ints = self.fitSignals(h,region=region,shift=shift,yFitFunc=yFitFunc,isKinFit=isKinFit,**kwargs)
                        values[region][h][shift] = vals
                        errors[region][h][shift] = errs
                        integrals[region][h][shift] = ints
                    elif shift in self.QCDSHIFTS:
                        vals, errs, ints = self.fitSignals(h,region=region,shift=shift,yFitFunc=yFitFunc,isKinFit=isKinFit,**kwargs)
                        values[region][h][shift] = vals
                        errors[region][h][shift] = errs
                        integrals[region][h][shift] = ints
                    else:
                        valsUp, errsUp, intsUp = self.fitSignals(h,region=region,shift=shift+'Up',yFitFunc=yFitFunc,isKinFit=isKinFit,**kwargs)
                        valsDown, errsDown, intsDown = self.fitSignals(h,region=region,shift=shift+'Down',yFitFunc=yFitFunc,isKinFit=isKinFit,**kwargs)
                        values[region][h][shift+'Up'] = valsUp
                        errors[region][h][shift+'Up'] = errsUp
                        integrals[region][h][shift+'Up'] = intsUp
                        values[region][h][shift+'Down'] = valsDown
                        errors[region][h][shift+'Down'] = errsDown
                        integrals[region][h][shift+'Down'] = intsDown
                if self.QCDSHIFTS:
                    values[region][h]['qcdUp']      = {h:{a:{} for a in self.AMASSES}}
                    values[region][h]['qcdDown']    = {h:{a:{} for a in self.AMASSES}}
                    errors[region][h]['qcdUp']      = {h:{a:{} for a in self.AMASSES}}
                    errors[region][h]['qcdDown']    = {h:{a:{} for a in self.AMASSES}}
                    integrals[region][h]['qcdUp']   = {h:{a:0  for a in self.AMASSES}}
                    integrals[region][h]['qcdDown'] = {h:{a:0  for a in self.AMASSES}}
                    for a in values[region][h][''][h]:
                        for val in values[region][h][''][h][a]:
                            values[region][h]['qcdUp'  ][h][a][val] = max([values[region][h][shift][h][a][val] for shift in self.QCDSHIFTS])
                            values[region][h]['qcdDown'][h][a][val] = min([values[region][h][shift][h][a][val] for shift in self.QCDSHIFTS])
                            errors[region][h]['qcdUp'  ][h][a][val] = max([errors[region][h][shift][h][a][val] for shift in self.QCDSHIFTS])
                            errors[region][h]['qcdDown'][h][a][val] = min([errors[region][h][shift][h][a][val] for shift in self.QCDSHIFTS])
                        integrals[region][h]['qcdUp'  ][h][a] = max([integrals[region][h][shift][h][a] for shift in self.QCDSHIFTS])
                        integrals[region][h]['qcdDown'][h][a] = min([integrals[region][h][shift][h][a] for shift in self.QCDSHIFTS])
                    for shift in ['qcdUp','qcdDown']:
                        savedir = '{}/{}'.format(self.fitsDir,shift)
                        python_mkdir(savedir)
                        savename = '{}/h{}_{}_{}.json'.format(savedir,h,region,shift)
                        jsonData = {'vals': values[region][h][shift], 'errs': errors[region][h][shift], 'integrals': integrals[region][h][shift]}
                        self.dump(savename,jsonData)
                    models[region][h] = self.buildSpline(h,values[region][h],errors[region][h],integrals[region][h],region,self.SIGNALSHIFTS+['qcd'],yFitFunc=yFitFunc,isKinFit=isKinFit,**kwargs)
                else:
                    models[region][h] = self.buildSpline(h,values[region][h],errors[region][h],integrals[region][h],region,self.SIGNALSHIFTS,yFitFunc=yFitFunc,isKinFit=isKinFit,**kwargs)
                #self.workspace.factory('{}_{}_norm[1,0,9999]'.format(self.SPLINENAME.format(h=h),region))
        self.fitted_models = models

    ######################
    ### Setup datacard ###
    ######################
    def setupDatacard(self, addControl=False, doBinned=False):
        bgs = self.getComponentFractions(self.workspace.pdf('bg_PP_x')) #ADDED BY KYLE
        bgs = [b.rstrip('_x') for b in bgs]
        bgs = [b.rstrip('_PP') for b in bgs] #ADDED BY KYLE
        sigs = [self.SPLINENAME.format(h=h) for h in self.HMASSES] #ADDED BY KYLE

        # setup bins
        for region in self.REGIONS:
            self.addBin(region)

        # add processes
        for proc in bgs:
            self.addProcess(proc)

        for proc in sigs:
            self.addProcess(proc,signal=True)

        if doBinned: self.addBackgroundHists()

        for region in self.REGIONS:
            for proc in sigs+bgs:
                if proc in bgs and doBinned: continue
                if proc in sigs:
                    self.setExpected(proc,region,1)
                    self.addRateParam('integral_{}_{}'.format(proc,region),region,proc)
                else:
                    key = proc if proc in self.background_integralValues[region] else '{}_{}'.format(proc,region)
                    integral = self.background_integralValues[region][key]

                    self.setExpected(proc,region,integral)
                if 'cont' not in proc and proc not in sigs:
                    self.addShape(region,proc,proc)
                
            self.setObserved(region,-1) # reads from histogram

        if addControl:
            region = 'control'

            self.addBin(region)

            for proc in bgs:
                key = proc if proc in self.control_integralValues else '{}_{}'.format(proc,region)
                integral = self.control_integralValues[key]

                self.setExpected(proc,region,integral)
                if 'cont' not in proc and proc not in sigs:
                    self.addShape(region,proc,proc)

            self.setObserved(region,-1) # reads from histogram

    def GetInitialValuesDitau(self, isLandau=False):
        if isLandau:
            initialValues = {
              "h125a3p6": { "mean_ttgaus": 0.01, "sigma_ttgaus": 1.60, "mu_ttland": 1.48, "sigma_ttland": 0.22},# Can Be improved 
              "h125a4"  : { "mean_ttgaus": 0.01, "sigma_ttgaus": 1.70, "mu_ttland": 1.70, "sigma_ttland": 0.29},
              "h125a5"  : { "mean_ttgaus": 0.01, "sigma_ttgaus": 2.02, "mu_ttland": 2.37, "sigma_ttland": 0.56},
              "h125a6"  : { "mean_ttgaus": 0.01, "sigma_ttgaus": 1.93, "mu_ttland": 3.90, "sigma_ttland": 1.10},
              "h125a7"  : { "mean_ttgaus": 0.01, "sigma_ttgaus": 2.10, "mu_ttland": 6.00, "sigma_ttland": 1.60},
              "h125a9"  : { "mean_ttgaus": 5.60, "sigma_ttgaus": 1.46, "mu_ttland": 1.80, "sigma_ttland": 0.45},
              "h125a11" : { "mean_ttgaus": 6.83, "sigma_ttgaus": 1.82, "mu_ttland": 2.35, "sigma_ttland": 0.67},
              "h125a13" : { "mean_ttgaus": 7.97, "sigma_ttgaus": 2.17, "mu_ttland": 2.90, "sigma_ttland": 0.90},
              "h125a15" : { "mean_ttgaus": 8.99, "sigma_ttgaus": 2.59, "mu_ttland": 3.60, "sigma_ttland": 1.20},
              "h125a17" : { "mean_ttgaus": 9.90, "sigma_ttgaus": 2.90, "mu_ttland": 4.40, "sigma_ttland": 1.60},
              "h125a19" : { "mean_ttgaus": 11.0, "sigma_ttgaus": 3.80, "mu_ttland": 6.00, "sigma_ttland": 2.00},
              "h125a21" : { "mean_ttgaus": 12.0, "sigma_ttgaus": 3.80, "mu_ttland": 6.00, "sigma_ttland": 1.90},
              "h300a5"  : { "mean_ttgaus": 3.01, "sigma_ttgaus": 1.00, "mu_ttland": 1.10, "sigma_ttland": 0.20},# Can Be improved 
              "h300a7"  : { "mean_ttgaus": 4.01, "sigma_ttgaus": 1.20, "mu_ttland": 1.40, "sigma_ttland": 0.20},# Can Be improved 
              "h300a9"  : { "mean_ttgaus": 5.42, "sigma_ttgaus": 1.51, "mu_ttland": 1.66, "sigma_ttland": 0.30},
              "h300a11" : { "mean_ttgaus": 6.61, "sigma_ttgaus": 2.03, "mu_ttland": 2.10, "sigma_ttland": 0.58},
              "h300a13" : { "mean_ttgaus": 7.87, "sigma_ttgaus": 2.26, "mu_ttland": 2.14, "sigma_ttland": 0.56},
              "h300a15" : { "mean_ttgaus": 8.96, "sigma_ttgaus": 2.56, "mu_ttland": 2.52, "sigma_ttland": 0.70},
              "h300a17" : { "mean_ttgaus": 10.2, "sigma_ttgaus": 2.93, "mu_ttland": 2.89, "sigma_ttland": 0.80},
              "h300a19" : { "mean_ttgaus": 11.4, "sigma_ttgaus": 3.31, "mu_ttland": 3.14, "sigma_ttland": 0.96},
              "h300a21" : { "mean_ttgaus": 12.6, "sigma_ttgaus": 3.54, "mu_ttland": 3.33, "sigma_ttland": 0.94},
              "h750a5"  : { "mean_ttgaus": 2.51, "sigma_ttgaus": 2.00, "mu_ttland": 1.87, "sigma_ttland": 0.35},# Can Be improved 
              "h750a7"  : { "mean_ttgaus": 3.01, "sigma_ttgaus": 2.00, "mu_ttland": 1.80, "sigma_ttland": 0.35},# Can Be improved 
              "h750a9"  : { "mean_ttgaus": 4.00, "sigma_ttgaus": 2.00, "mu_ttland": 1.90, "sigma_ttland": 0.35},# Can Be improved 
              "h750a11" : { "mean_ttgaus": 6.64, "sigma_ttgaus": 1.97, "mu_ttland": 1.78, "sigma_ttland": 0.41},
              "h750a13" : { "mean_ttgaus": 8.00, "sigma_ttgaus": 2.00, "mu_ttland": 2.00, "sigma_ttland": 0.50},
              "h750a15" : { "mean_ttgaus": 8.90, "sigma_ttgaus": 2.80, "mu_ttland": 2.20, "sigma_ttland": 0.60},
              "h750a17" : { "mean_ttgaus": 10.1, "sigma_ttgaus": 2.98, "mu_ttland": 2.30, "sigma_ttland": 0.63},
              "h750a19" : { "mean_ttgaus": 11.2, "sigma_ttgaus": 3.25, "mu_ttland": 2.39, "sigma_ttland": 0.67},
              "h750a21" : { "mean_ttgaus": 12.4, "sigma_ttgaus": 3.69, "mu_ttland": 2.70, "sigma_ttland": 0.83},
            }
        else:
            initialValues = {
              "h125a3p6": { "mean_sigy": 1.56, "sigma_sigy": 0.17, "width_sigy": 0.31},
              "h125a4"  : { "mean_sigy": 1.80, "sigma_sigy": 0.27, "width_sigy": 0.56},
              "h125a5"  : { "mean_sigy": 2.26, "sigma_sigy": 0.59, "width_sigy": 0.54},
              "h125a6"  : { "mean_sigy": 2.86, "sigma_sigy": 0.86, "width_sigy": 0.44},
              "h125a7"  : { "mean_sigy": 3.41, "sigma_sigy": 1.11, "width_sigy": 0.24},
              "h125a9"  : { "mean_sigy": 4.52, "sigma_sigy": 1.49, "width_sigy": 0.40},
              "h125a11" : { "mean_sigy": 5.50, "sigma_sigy": 1.89, "width_sigy": 0.10},
              "h125a13" : { "mean_sigy": 6.65, "sigma_sigy": 2.23, "width_sigy": 0.10},
              "h125a15" : { "mean_sigy": 7.53, "sigma_sigy": 2.44, "width_sigy": 0.20},
              "h125a17" : { "mean_sigy": 8.51, "sigma_sigy": 3.16, "width_sigy": 0.10},
              "h125a19" : { "mean_sigy": 8.78, "sigma_sigy": 3.35, "width_sigy": 0.01},
              "h125a21" : { "mean_sigy": 9.94, "sigma_sigy": 3.93, "width_sigy": 0.01},
              "h300a5"  : { "mean_sigy": 2.21, "sigma_sigy": 0.58, "width_sigy": 0.50},
              "h300a7"  : { "mean_sigy": 3.07, "sigma_sigy": 1.06, "width_sigy": 0.40},
              "h300a9"  : { "mean_sigy": 3.99, "sigma_sigy": 1.50, "width_sigy": 0.50},
              "h300a11" : { "mean_sigy": 4.85, "sigma_sigy": 1.98, "width_sigy": 0.40},
              "h300a13" : { "mean_sigy": 5.86, "sigma_sigy": 2.30, "width_sigy": 0.40},
              "h300a15" : { "mean_sigy": 6.73, "sigma_sigy": 2.80, "width_sigy": 0.30},
              "h300a17" : { "mean_sigy": 7.68, "sigma_sigy": 3.10, "width_sigy": 0.30},
              "h300a19" : { "mean_sigy": 8.59, "sigma_sigy": 3.50, "width_sigy": 0.30},
              "h300a21" : { "mean_sigy": 9.33, "sigma_sigy": 3.80, "width_sigy": 0.40},
              "h750a5"  : { "mean_sigy": 2.10, "sigma_sigy": 0.50, "width_sigy": 0.80},
              "h750a7"  : { "mean_sigy": 2.90, "sigma_sigy": 1.00, "width_sigy": 0.80},
              "h750a9"  : { "mean_sigy": 3.80, "sigma_sigy": 1.50, "width_sigy": 0.80},
              "h750a11" : { "mean_sigy": 4.60, "sigma_sigy": 2.00, "width_sigy": 0.80},
              "h750a13" : { "mean_sigy": 5.40, "sigma_sigy": 2.40, "width_sigy": 0.60},
              "h750a15" : { "mean_sigy": 6.20, "sigma_sigy": 2.80, "width_sigy": 0.70},
              "h750a17" : { "mean_sigy": 7.10, "sigma_sigy": 3.10, "width_sigy": 0.80},
              "h750a19" : { "mean_sigy": 8.00, "sigma_sigy": 3.50, "width_sigy": 0.50},
              "h750a21" : { "mean_sigy": 8.80, "sigma_sigy": 4.00, "width_sigy": 0.80}
            }
        return initialValues


    def GetInitialValuesDCB(self, isKinFit=False):
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
              "h125a3p6": { "a1": 3.5, "a2": 3.5, "n1": 18.0, "n2": 1.3, "sigma": 12.0},
              "h125a4"  : { "a1": 3.5, "a2": 3.5, "n1": 18.0, "n2": 1.3, "sigma": 12.5},
              "h125a5"  : { "a1": 3.5, "a2": 3.5, "n1": 18.0, "n2": 1.3, "sigma": 13.5},
              "h125a6"  : { "a1": 3.5, "a2": 3.5, "n1": 18.0, "n2": 1.3, "sigma": 14.0},
              "h125a7"  : { "a1": 3.5, "a2": 3.5, "n1": 18.0, "n2": 1.3, "sigma": 14.0},
              "h125a9"  : { "a1": 3.5, "a2": 3.5, "n1": 18.0, "n2": 1.3, "sigma": 14.0},
              "h125a11" : { "a1": 3.5, "a2": 3.5, "n1": 18.0, "n2": 1.3, "sigma": 14.0},
              "h125a13" : { "a1": 3.5, "a2": 3.5, "n1": 18.0, "n2": 1.3, "sigma": 14.0},
              "h125a15" : { "a1": 3.5, "a2": 3.5, "n1": 18.0, "n2": 1.3, "sigma": 14.0},
              "h125a17" : { "a1": 3.5, "a2": 3.5, "n1": 18.0, "n2": 1.3, "sigma": 14.0},
              "h125a19" : { "a1": 3.5, "a2": 3.5, "n1": 18.0, "n2": 1.3, "sigma": 14.0},
              "h125a21" : { "a1": 3.5, "a2": 3.5, "n1": 18.0, "n2": 1.3, "sigma": 14.0},
              "125" : {"a1" : 3.5, "a2": 3.5, "n1": 18.0, "n2": 1.3, "sigma": 14.0},
              "h300a5"  : { "a1": 3.5, "a2": 3.5, "n1": 17.0, "n2": 5.0, "sigma": 35.0},
              "h300a7"  : { "a1": 3.5, "a2": 3.5, "n1": 17.0, "n2": 5.0, "sigma": 36.0},
              "h300a9"  : { "a1": 3.5, "a2": 3.5, "n1": 17.0, "n2": 5.0, "sigma": 38.0},
              "h300a11" : { "a1": 3.5, "a2": 3.5, "n1": 17.0, "n2": 5.0, "sigma": 39.0},
              "h300a13" : { "a1": 3.5, "a2": 3.5, "n1": 17.0, "n2": 5.0, "sigma": 40.0},
              "h300a15" : { "a1": 3.5, "a2": 3.5, "n1": 17.0, "n2": 5.0, "sigma": 40.0},
              "h300a17" : { "a1": 3.5, "a2": 3.5, "n1": 17.0, "n2": 5.0, "sigma": 40.0},
              "h300a19" : { "a1": 3.5, "a2": 3.5, "n1": 17.0, "n2": 5.0, "sigma": 40.0},
              "h300a21" : { "a1": 3.5, "a2": 3.5, "n1": 17.0, "n2": 5.0, "sigma": 40.0},
              "300" : {"a1" : 3.5, "a2": 3.0, "n1": 14.0, "n2": 5.0, "sigma": 40.00},
              "h750a5"  : { "a1": 3.0, "a2": 6.5, "n1": 18.0, "n2": 17.0, "sigma":  95},
              "h750a7"  : { "a1": 3.0, "a2": 6.5, "n1": 18.0, "n2": 17.0, "sigma": 103},
              "h750a9"  : { "a1": 3.0, "a2": 6.5, "n1": 18.0, "n2": 17.0, "sigma": 106},
              "h750a11" : { "a1": 3.0, "a2": 6.5, "n1": 18.0, "n2": 17.0, "sigma": 108},
              "h750a13" : { "a1": 3.0, "a2": 6.5, "n1": 18.0, "n2": 17.9, "sigma": 109},
              "h750a15" : { "a1": 3.0, "a2": 6.5, "n1": 18.0, "n2": 17.0, "sigma": 110},
              "h750a17" : { "a1": 3.0, "a2": 6.5, "n1": 18.0, "n2": 17.0, "sigma": 111},
              "h750a19" : { "a1": 3.0, "a2": 6.5, "n1": 18.0, "n2": 17.0, "sigma": 111},
              "h750a21" : { "a1": 3.0, "a2": 6.5, "n1": 18.0, "n2": 17.0, "sigma": 111},
              "750" : {"a1" : 3.0, "a2": 6.5, "n1": 18.0, "n2": 17.0, "sigma": 110.0}
              #"h125a3p6": { "a1": 3.1, "a2": 2.96, "n1": 2.3, "n2": 1.3, "sigma": 12.10},
              #"h125a4"  : { "a1": 3.0, "a2": 2.57, "n1": 3.3, "n2": 1.3, "sigma": 12.96},
              #"h125a5"  : { "a1": 3.0, "a2": 3.16, "n1": 2.4, "n2": 1.2, "sigma": 14.46},
              #"h125a6"  : { "a1": 3.0, "a2": 4.05, "n1": 2.4, "n2": 1.3, "sigma": 13.62},
              #"h125a7"  : { "a1": 3.0, "a2": 3.36, "n1": 2.7, "n2": 1.3, "sigma": 14.13},
              #"h125a9"  : { "a1": 3.0, "a2": 2.83, "n1": 3.4, "n2": 1.3, "sigma": 14.36},
              #"h125a11" : { "a1": 3.9, "a2": 2.55, "n1": 3.0, "n2": 1.5, "sigma": 14.33},
              #"h125a13" : { "a1": 3.0, "a2": 3.22, "n1": 2.5, "n2": 1.4, "sigma": 14.29},
              #"h125a15" : { "a1": 3.0, "a2": 3.33, "n1": 2.0, "n2": 1.3, "sigma": 13.91},
              #"h125a17" : { "a1": 3.5, "a2": 2.84, "n1": 2.9, "n2": 1.7, "sigma": 13.57},
              #"h125a19" : { "a1": 3.3, "a2": 2.89, "n1": 2.5, "n2": 1.9, "sigma": 13.90},
              #"h125a21" : { "a1": 3.3, "a2": 3.33, "n1": 1.2, "n2": 1.2, "sigma": 13.74},
              #"125" : {"a1" : 5.0, "a2": 2.75, "n1": 4.0, "n2": 1.5, "sigma": 14.0},
              #"h300a5"  : { "a1": 5.5, "a2": 3.55, "n1": 3.7, "n2": 2.2, "sigma": 36.24},
              #"h300a7"  : { "a1": 3.3, "a2": 3.50, "n1": 6.0, "n2": 6.5, "sigma": 37.40},
              #"h300a9"  : { "a1": 3.3, "a2": 3.47, "n1": 4.4, "n2": 3.8, "sigma": 39.80},
              #"h300a11" : { "a1": 5.0, "a2": 3.50, "n1": 2.5, "n2": 8.0, "sigma": 39.77},
              #"h300a13" : { "a1": 5.2, "a2": 5.60, "n1": 4.1, "n2": 5.9, "sigma": 40.83},
              #"h300a15" : { "a1": 5.3, "a2": 3.61, "n1": 2.9, "n2": 3.0, "sigma": 40.16},
              #"h300a17" : { "a1": 5.6, "a2": 3.79, "n1": 4.3, "n2": 1.9, "sigma": 40.49},
              #"h300a19" : { "a1": 5.0, "a2": 3.77, "n1": 5.6, "n2": 2.1, "sigma": 41.08},
              #"h300a21" : { "a1": 5.0, "a2": 3.53, "n1": 4.5, "n2": 8.7, "sigma": 40.63},
              #"300" : {"a1" : 5.0, "a2": 3.5, "n1": 4.5, "n2": 5.0, "sigma": 40.00},
              #"h750a5"  : { "a1": 2.5, "a2": 4.80, "n1": 7.00, "n2": 19.0, "sigma": 95.50},
              #"h750a7"  : { "a1": 2.7, "a2": 3.90, "n1": 18.0, "n2": 16.0, "sigma": 102.8},
              #"h750a9"  : { "a1": 3.4, "a2": 5.50, "n1": 20.0, "n2": 15.0, "sigma": 107.3},
              #"h750a11" : { "a1": 4.7, "a2": 5.70, "n1": 3.20, "n2": 19.0, "sigma": 109.8},
              #"h750a13" : { "a1": 4.8, "a2": 3.46, "n1": 8.30, "n2": 19.9, "sigma": 111.3},
              #"h750a15" : { "a1": 4.1, "a2": 4.20, "n1": 12.5, "n2": 19.0, "sigma": 112.7},
              #"h750a17" : { "a1": 4.0, "a2": 4.33, "n1": 9.20, "n2": 18.0, "sigma": 114.0},
              #"h750a19" : { "a1": 5.8, "a2": 5.80, "n1": 4.30, "n2": 19.0, "sigma": 114.3},
              #"h750a21" : { "a1": 4.1, "a2": 5.30, "n1": 17.6, "n2": 15.0, "sigma": 114.7},
              #"750" : {"a1" : 4.8, "a2": 5.00, "n1": 4.6, "n2": 16.0, "sigma": 109.0}
            }
        return initialValues

    def GetInitialDCBMean(self, isRegFP=False):
        if isRegFP:
            initialValues = {
              "h125a3p6": { "mean": 100},
              "h125a4"  : { "mean": 105},
              "h125a5"  : { "mean": 100},
              "h125a6"  : { "mean": 100},
              "h125a7"  : { "mean": 100},
              "h125a9"  : { "mean": 100},
              "h125a11" : { "mean": 95},
              "h125a13" : { "mean": 95},
              "h125a15" : { "mean": 90},
              "h125a17" : { "mean": 90},
              "h125a19" : { "mean": 90},
              "h125a21" : { "mean": 85},
              "h300a5"  : { "mean": 225},
              "h300a7"  : { "mean": 220},
              "h300a9"  : { "mean": 220},
              "h300a11" : { "mean": 220},
              "h300a13" : { "mean": 210},
              "h300a15" : { "mean": 205},
              "h300a17" : { "mean": 203},
              "h300a19" : { "mean": 205},
              "h300a21" : { "mean": 205},
              "h750a5"  : { "mean": 555},
              "h750a7"  : { "mean": 550},
              "h750a9"  : { "mean": 543},
              "h750a11" : { "mean": 545},
              "h750a13" : { "mean": 540},
              "h750a15" : { "mean": 538},
              "h750a17" : { "mean": 545},
              "h750a19" : { "mean": 550},
              "h750a21" : { "mean": 550},
            }
        else:
            initialValues = {
              "h125a3p6": { "mean": 100},
              "h125a4"  : { "mean": 100},
              "h125a5"  : { "mean": 100},
              "h125a6"  : { "mean": 96},
              "h125a7"  : { "mean": 100},
              "h125a9"  : { "mean": 95},
              "h125a11" : { "mean": 90},
              "h125a13" : { "mean": 97},
              "h125a15" : { "mean": 95},
              "h125a17" : { "mean": 97},
              "h125a19" : { "mean": 93},
              "h125a21" : { "mean": 97},
              "h300a5"  : { "mean": 225},
              "h300a7"  : { "mean": 225},
              "h300a9"  : { "mean": 220},
              "h300a11" : { "mean": 220},
              "h300a13" : { "mean": 220},
              "h300a15" : { "mean": 210},
              "h300a17" : { "mean": 215},
              "h300a19" : { "mean": 207},
              "h300a21" : { "mean": 205},
              "h750a5"  : { "mean": 555},
              "h750a7"  : { "mean": 545},
              "h750a9"  : { "mean": 543},
              "h750a11" : { "mean": 543},
              "h750a13" : { "mean": 540},
              "h750a15" : { "mean": 525},
              "h750a17" : { "mean": 540},
              "h750a19" : { "mean": 545},
              "h750a21" : { "mean": 550}
            }
        return initialValues

    def GetInitialValuesDG(self, region="FP"):
        if region == "PP": 
            initialValues = {
                "h125a3p6": { "mean": 93.5, "sigma1": 14.2, "sigma2": 10.1},
                "h125a4"  : { "mean": 93.7, "sigma1": 15.9, "sigma2": 10.4},
                "h125a5"  : { "mean": 94.2, "sigma1": 17.0, "sigma2": 10.0},
                "h125a6"  : { "mean": 93.1, "sigma1": 15.6, "sigma2": 11.9},
                "h125a7"  : { "mean": 93.3, "sigma1": 16.5, "sigma2": 11.7},
                "h125a9"  : { "mean": 92.2, "sigma1": 16.2, "sigma2": 12.1},
                "h125a11" : { "mean": 92.2, "sigma1": 16.0, "sigma2": 12.5},
                "h125a13" : { "mean": 91.8, "sigma1": 15.9, "sigma2": 12.5},
                "h125a15" : { "mean": 91.2, "sigma1": 15.5, "sigma2": 12.9},
                "h125a17" : { "mean": 91.1, "sigma1": 15.2, "sigma2": 12.2},
                "h125a19" : { "mean": 90.7, "sigma1": 15.4, "sigma2": 12.4},
                "h125a21" : { "mean": 91.3, "sigma1": 14.5, "sigma2": 12.3},
                "h300a5"  : { "mean": 215, "sigma1": 44.4, "sigma2": 26.4},
                "h300a7"  : { "mean": 211, "sigma1": 44.7, "sigma2": 29.6},
                "h300a9"  : { "mean": 209, "sigma1": 49.0, "sigma2": 39.5},
                "h300a11" : { "mean": 208, "sigma1": 48.2, "sigma2": 30.8},
                "h300a13" : { "mean": 207, "sigma1": 49.5, "sigma2": 31.3},
                "h300a15" : { "mean": 207, "sigma1": 48.4, "sigma2": 31.3},
                "h300a17" : { "mean": 206, "sigma1": 47.0, "sigma2": 33.0},
                "h300a19" : { "mean": 206, "sigma1": 49.4, "sigma2": 31.9},
                "h300a21" : { "mean": 206, "sigma1": 50.3, "sigma2": 30.4},
                "h750a5"  : { "mean": 522, "sigma1": 121, "sigma2": 68},
                "h750a7"  : { "mean": 510, "sigma1": 130, "sigma2": 75},
                "h750a9"  : { "mean": 508, "sigma1": 133, "sigma2": 80},
                "h750a11" : { "mean": 505, "sigma1": 137, "sigma2": 80},
                "h750a13" : { "mean": 503, "sigma1": 138, "sigma2": 82},
                "h750a15" : { "mean": 501, "sigma1": 145, "sigma2": 80},
                "h750a17" : { "mean": 500, "sigma1": 149, "sigma2": 76},
                "h750a19" : { "mean": 500, "sigma1": 154, "sigma2": 73},
                "h750a21" : { "mean": 499, "sigma1": 153, "sigma2": 75}
            }
        elif region == "FP": 
            initialValues = {
                "h125a3p6": { "mean": 93.4, "sigma1": 13.5, "sigma2": 13.0},
                "h125a4"  : { "mean": 95.8, "sigma1": 15.8, "sigma2": 12.2},
                "h125a5"  : { "mean": 96.1, "sigma1": 16.4, "sigma2": 12.1},
                "h125a6"  : { "mean": 94.9, "sigma1": 15.9, "sigma2": 12.8},
                "h125a7"  : { "mean": 94.5, "sigma1": 17.2, "sigma2": 12.4},
                "h125a9"  : { "mean": 93.6, "sigma1": 17.2, "sigma2": 12.2},
                "h125a11" : { "mean": 93.4, "sigma1": 15.8, "sigma2": 13.8},
                "h125a13" : { "mean": 94.0, "sigma1": 15.8, "sigma2": 12.3},
                "h125a15" : { "mean": 93.3, "sigma1": 14.3, "sigma2": 13.8},
                "h125a17" : { "mean": 93.5, "sigma1": 15.6, "sigma2": 13.9},
                "h125a19" : { "mean": 91.0, "sigma1": 13.9, "sigma2": 15.5},
                "h125a21" : { "mean": 93.2, "sigma1": 14.5, "sigma2": 15.8},
                "h300a5"  : { "mean": 215, "sigma1": 47.0, "sigma2": 27.7},
                "h300a7"  : { "mean": 211, "sigma1": 51.0, "sigma2": 27.0},
                "h300a9"  : { "mean": 210, "sigma1": 49.0, "sigma2": 29.0},
                "h300a11" : { "mean": 209, "sigma1": 50.0, "sigma2": 31.0},
                "h300a13" : { "mean": 210, "sigma1": 51.0, "sigma2": 30.8},
                "h300a15" : { "mean": 208, "sigma1": 55.0, "sigma2": 28.0},
                "h300a17" : { "mean": 210, "sigma1": 52.0, "sigma2": 30.0},
                "h300a19" : { "mean": 209, "sigma1": 53.0, "sigma2": 29.0},
                "h300a21" : { "mean": 207, "sigma1": 50.0, "sigma2": 32.0},
                "h750a5"  : { "mean": 511, "sigma1": 148, "sigma2": 65},
                "h750a7"  : { "mean": 507, "sigma1": 150, "sigma2": 69},
                "h750a9"  : { "mean": 504, "sigma1": 148, "sigma2": 73},
                "h750a11" : { "mean": 507, "sigma1": 146, "sigma2": 78},
                "h750a13" : { "mean": 505, "sigma1": 155, "sigma2": 70},
                "h750a15" : { "mean": 502, "sigma1": 154, "sigma2": 72},
                "h750a17" : { "mean": 500, "sigma1": 156, "sigma2": 74},
                "h750a19" : { "mean": 502, "sigma1": 150, "sigma2": 75},
                "h750a21" : { "mean": 500, "sigma1": 158, "sigma2": 74}
            }

        return initialValues

    ###################
    ### Systematics ###
    ###################
    def addSystematics(self,doBinned=False,addControl=False):
        self.sigProcesses = tuple([self.SPLINENAME.format(h=h) for h in self.HMASSES])
        self._addLumiSystematic()
        self._addMuonSystematic()
        #self._addTauSystematic()
        self._addShapeSystematic()
        #self._addComponentSystematic(addControl=addControl)
        self._addRelativeNormUnc()
        if not doBinned and not addControl: self._addControlSystematics()


    ###################################
    ### Save workspace and datacard ###
    ###################################
    def save(self,name='mmmt', subdirectory=''):
        processes = {}
        bgsx = self.getComponentFractions(self.workspace.pdf('bg_PP_x'))
        bgsy = self.getComponentFractions(self.workspace.pdf('bg_PP_y'))
        bgs = dict(bgsx, **bgsy)
        bgs = [b.rstrip('_x') for b in bgs]
        bgs = [b.rstrip('_PP') for b in bgs]
        for h in self.HMASSES:
            processes[self.SIGNAME.format(h=h,a='X')] = [self.SPLINENAME.format(h=h)] + bgs
        if subdirectory == '':
            self.printCard('datacards_shape/MuMuTauTau/{}'.format(name),processes=processes,blind=False,saveWorkspace=True)
        else:
            self.printCard('datacards_shape/MuMuTauTau/' + subdirectory + '{}'.format(name),processes=processes,blind=False,saveWorkspace=True)

