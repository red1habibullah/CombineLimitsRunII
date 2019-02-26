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

import CombineLimits.Plotter.CMS_lumi as CMS_lumi
import CombineLimits.Plotter.tdrstyle as tdrstyle

tdrstyle.setTDRStyle()

class HaaLimits2D(HaaLimits):
    '''
    Create the Haa Limits workspace
    '''

    YRANGE = [50,1000]
    YBINNING = 950
    YLABEL = 'm_{#mu#mu#tau_{#mu}#tau_{h}}'
    YVAR = 'CMS_haa_y'

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
        super(HaaLimits2D,self).__init__(histMap,tag=tag,do2DInterpolation=do2DInterpolation,doParamFit=doParamFit)

        self.plotDir = 'figures/HaaLimits2D{}'.format('_'+tag if tag else '')
        self.fitsDir = 'fitParams/HaaLimits2D{}'.format('_'+tag if tag else '')


    ###########################
    ### Workspace utilities ###
    ###########################
    def initializeWorkspace(self,**kwargs):
        logging.debug('initializeWorkspace')
        logging.debug(str(kwargs))
        self.addVar(self.XVAR,*self.XRANGE,unit='GeV',label=self.XLABEL,**kwargs)
        self.addVar(self.YVAR,*self.YRANGE,unit='GeV',label=self.YLABEL,**kwargs)
        self.addMH(*self.HRANGE,unit='GeV',label=self.HLABEL,**kwargs)
        self.addMA(*self.ARANGE,unit='GeV',label=self.ALABEL,**kwargs)

    def _buildYModel(self,region,**kwargs):
        workspace = kwargs.pop('workspace',self.workspace)
        xVar = kwargs.pop('xVar',self.XVAR)
        yVar = kwargs.pop('yVar',self.YVAR)
        tag = kwargs.pop('tag',region)

        # try landau
        if self.YRANGE[1]>100:
            #bg = Models.Landau('bg',
            #    x = yVar,
            #    mu    = [50,0,200],
            #   sigma = [10,0,100],
            #)
            #bg = Models.Polynomial('bg',
            #    x = yVar,
            #    order = 3,
            #    p0 = [50,0,10000],
            #    p1 = [-5,-100,100],
            #    p2 = [-0.3,-100,100],
            #)

            #bg = Models.Polynomial('bg',
            #    x = yVar,
            #    order = 4,
            #    p0 = [-1,0,10000],
            #    p1 = [0.25,-100,100],
            #    p2 = [0.03,-100,100],
            #    p3 = [0.5,-100,100],
            #)

            #bg = Models.Polynomial('bg',
            #    x = yVar,
            #    order = 5,
            #    p0 = [965,0,10000],
            #    p1 = [-12, -100, 100],
            #    p2 = [0.06,-100,100],
            #    p3 = [-0.1,-100,100],
            #    p4 = [-0.01,-100,100],
            #)

            #nameP1 = 'erfShiftPoly{}'.format('_'+tag if tag else '')
            #poly1 = Models.PolynomialExpr('poly1',
            #    x = yVar,
            #    order = 1,
            #    p0 = kwargs.pop('p0_{}'.format(nameP1), [45,30,70]),
            #    p1 = kwargs.pop('p1_{}'.format(nameP1), [0.75,0,2]),
            #)
            #poly1.build(workspace,nameP1)

            nameE1 = 'erf1{}'.format('_'+tag if tag else '')
            erf1 = Models.Erf('erf1',
                x = yVar,
                erfScale = kwargs.pop('erfScale_{}'.format(nameE1), [0.05,0,10]),
                erfShift = kwargs.pop('erfShift_{}'.format(nameE1), [70,10,200]),
                #erfShift = nameP1,
            )
            erf1.build(workspace,nameE1)

            nameC1 = 'conty1{}'.format('_'+tag if tag else '')
            cont1 = Models.Exponential('conty1',
                x = yVar,
                lamb = kwargs.pop('lambda_{}'.format(nameC1), [-0.05,-1,0]),
            )
            cont1.build(workspace,nameC1)

            bg = Models.Prod('bg',
                nameE1,
                nameC1,
            )
        else:
            # Landau only
            #bg = Models.Landau('bg',
            #    x = yVar,
            #    mu    = [5,0,20],
            #    sigma = [1,0,10],
            #)

            # landau plus gaussian
            #land1 = Models.Landau('land1',
            #    x = yVar,
            #    mu    = [5,0,20],
            #    sigma = [1,0,10],
            #)
            #nameL1 = 'land1{}'.format('_'+tag if tag else '')
            #land1.build(workspace,nameL1)

            ## add a guassian summed for tt ?
            #gaus1 = Models.Gaussian('gaus1',
            #    x = yVar,
            #    mean = [1.5,0,4],
            #    sigma = [0.4,0,2],
            #)
            #nameG1 = 'gaus1{}'.format('_'+tag if tag else '')
            #gaus1.build(workspace,nameG1)

            #bg = Models.Sum('bg',
            #    **{
            #        nameL1     : [0.9,0,1],
            #        nameG1     : [0.5,0,1],
            #        'recursive': True,
            #    }
            #)

            ## landua plus upsilon gaussian
            nameL1 = 'land1{}'.format('_'+tag if tag else '')
            #land1 = Models.Landau('land1',
            #    x = yVar,
            #    mu    = kwargs.pop('mu_{}'.format(nameL1), [1.5,0,5]),
            #    sigma = kwargs.pop('sigma_{}'.format(nameL1), [0.4,0,2]),
            #)
            #land1.build(workspace,nameL1)

            ## jpsi
            ##jpsi2 = Models.Voigtian('jpsi2S',
            ##    x = yVar,
            ##    mean  = [3.7,3.6,3.8],
            ##    sigma = [0.1,0.01,0.5],
            ##    width = [0.1,0.01,0.5],
            ##)
            ##nameJ2 = 'jpsi2Stt'
            ##jpsi2.build(workspace,nameJ2)


            ## add a guassian for upsilon
            #nameU1 = 'upsilontt'
            #upsilon1 = Models.Gaussian('upsilon1',
            #    x = yVar,
            #    mean  = kwargs.pop('mean_{}'.format(nameU1), [6,5,7]),
            #    sigma = kwargs.pop('sigma_{}'.format(nameU1), [0.02,0,1]),
            #)
            #upsilon1.build(workspace,nameU1)

            #bg = Models.Sum('bg',
            #    **{
            #        nameL1     : [0.95,0,1],
            #        #nameJ2     : [0.1,0,1],
            #        nameU1     : [0.1,0,1],
            #        'recursive': True,
            #    }
            #)

            bg = Models.Landau('land1',
                x = yVar,
                mu    = kwargs.pop('mu_{}'.format(nameL1), [1.5,0,5]),
                sigma = kwargs.pop('sigma_{}'.format(nameL1), [0.4,0,2]),
            )


        #cont1 = Models.Exponential('conty1',
        #    x = yVar,
        #    #lamb = [-0.20,-1,0], # kinfit
        #    lamb = [-0.05,-1,0], # visible
        #)
        #nameC1 = 'conty1{}'.format('_'+tag if tag else '')
        #cont1.build(workspace,nameC1)

        ## higgs fit (mmtt)
        #if self.YRANGE[1]>100:
        #    erf1 = Models.Erf('erf1',
        #        x = yVar,
        #        erfScale = [0.05,0,1],
        #        erfShift = [70,10,200],
        #    )
        #    nameE1 = 'erf1{}'.format('_'+tag if tag else '')
        #    erf1.build(workspace,nameE1)

        #    bg = Models.Prod('bg',
        #        nameE1,
        #        nameC1,
        #    )
        ## pseudo fit (tt)
        #else:
        #    erf1 = Models.Erf('erf1',
        #        x = yVar,
        #        erfScale = [1,0.01,10],
        #        erfShift = [1,0.1,10],
        #    )
        #    nameE1 = 'erf1{}'.format('_'+tag if tag else '')
        #    erf1.build(workspace,nameE1)

        #    erfc1 = Models.Prod('erfc1',
        #        nameE1,
        #        nameC1,
        #    )
        #    nameEC1 = 'erfc1{}'.format('_'+tag if tag else '')
        #    erfc1.build(workspace,nameEC1)

        #    # add an upsilon to tt resonance
        #    #upsilon = Models.Gaussian('upsilony',
        #    #    x = yVar,
        #    #    mean  = [5.5,5,6.5],
        #    #    sigma = [0.25,0.1,1],
        #    #)
        #    #nameU = 'upsilony{}'.format('_'+tag if tag else '')
        #    #upsilon.build(workspace,nameU)

        #    # add a guassian summed for tt ?
        #    gaus1 = Models.Gaussian('gaus1',
        #        x = yVar,
        #        mean = [1.5,0,4],
        #        sigma = [0.4,0,2],
        #    )
        #    nameG1 = 'gaus1{}'.format('_'+tag if tag else '')
        #    gaus1.build(workspace,nameG1)

        #    bg = Models.Sum('bg',
        #        **{ 
        #            nameEC1    : [0.9,0,1],
        #            nameG1     : [0.5,0,1],
        #            #nameU      : [0.5,0,1],
        #            'recursive': True,
        #        }
        #    )

        name = 'bg_{}'.format(region)
        bg.build(workspace,name)

    def _buildXModel(self,region,**kwargs):
        super(HaaLimits2D,self).buildModel(region,**kwargs)

    def buildModel(self,region,**kwargs):
        workspace = kwargs.pop('workspace',self.workspace)
        tag = kwargs.pop('tag',region)

        # build the x variable
        self._buildXModel(region+'_x',workspace=workspace,**kwargs)

        # build the y variable
        self._buildYModel(region+'_y',workspace=workspace,**kwargs)

        # the 2D model
        cont1 = Models.Prod('cont1',
            'cont1_{}_x'.format(region),
            'bg_{}_y'.format(region),
        )
        name = 'cont1_{}_xy'.format(region)
        cont1.build(workspace,name)

        cont2 = Models.Prod('cont2',
            'cont2_{}_x'.format(region),
            'bg_{}_y'.format(region),
        )
        name = 'cont2_{}_xy'.format(region)
        cont2.build(workspace,name)

        jpsi1S = Models.Prod('jpsi1S',
            #'jpsi1S',
            'jpsi1S_{}_x'.format(region),
            'bg_{}_y'.format(region),
        )
        name = 'jpsi1S_{}_xy'.format(region)
        jpsi1S.build(workspace,name)
  
        jpsi2S = Models.Prod('jpsi2S',
            #'jpsi2S',
            'jpsi2S_{}_x'.format(region),
            'bg_{}_y'.format(region),
        )
        name = 'jpsi2S_{}_xy'.format(region)
        jpsi2S.build(workspace,name)

        upsilon1S = Models.Prod('upsilon1S',
            #'upsilon1S',
            'upsilon1S_{}_x'.format(region),
            'bg_{}_y'.format(region),
        )
        name = 'upsilon1S_{}_xy'.format(region)
        upsilon1S.build(workspace,name)

        upsilon2S = Models.Prod('upsilon2S',
            #'upsilon2S',
            'upsilon2S_{}_x'.format(region),
            'bg_{}_y'.format(region),
        )
        name = 'upsilon2S_{}_xy'.format(region)
        upsilon2S.build(workspace,name)

        upsilon3S = Models.Prod('upsilon3S',
            #'upsilon3S',
            'upsilon3S_{}_x'.format(region),
            'bg_{}_y'.format(region),
        )
        name = 'upsilon3S_{}_xy'.format(region)
        upsilon3S.build(workspace,name)

        bg = Models.Prod('bg',
            'bg_{}_x'.format(region),
            'bg_{}_y'.format(region),
        )
        name = 'bg_{}_xy'.format(region)
        bg.build(workspace,name)

    def fitSignal(self,h,a,region,shift='',**kwargs):
        scale = kwargs.get('scale',1)
        if isinstance(scale,dict): scale = scale.get(self.SIGNAME.format(h=h,a=a),1)
        ygausOnly = kwargs.get('ygausOnly',False)
        isKinFit = kwargs.get('isKinFit',False)
        yFitFunc = kwargs.get('yFitFunc','G')
        dobgsig = kwargs.get('doBackgroundSignal',False)
        results = kwargs.get('results',{})
        histMap = self.histMap[region][shift]
        tag = kwargs.get('tag','{}{}'.format(region,'_'+shift if shift else ''))

        if self.YRANGE[1] > 100: 
            if yFitFunc == "DCB_Fix": initialMeans = self.GetInitialDCBMean()
            if "DCB" in yFitFunc: initialValuesDCB = self.GetInitialValuesDCB(isKinFit=isKinFit)
            elif yFitFunc == "DG": initialValuesDG = self.GetInitialValuesDG(region=region)
        elif yFitFunc == "L": initialValuesL = self.GetInitialValuesDitau(isLandau=True)
        elif yFitFunc == "V": initialValuesV = self.GetInitialValuesDitau(isLandau=False)

        aval = self.aToFloat(a)
        thisxrange = [0.8*aval, 1.2*aval]
        thisyrange = [0.15*h, 1.2*h] if self.YRANGE[1]>100 else [self.YRANGE[0], 1.2*aval]
        if self.YRANGE[1]>100:
            thisyrange = [0.15*h, 1.2*h]
        ws = ROOT.RooWorkspace('sig')
        ws.factory('{0}[{1}, {2}]'.format(self.XVAR,*thisxrange)) 
        ws.var(self.XVAR).setUnit('GeV')
        ws.var(self.XVAR).setPlotLabel(self.XLABEL)
        ws.var(self.XVAR).SetTitle(self.XLABEL)
        ws.factory('{0}[{1}, {2}]'.format(self.YVAR,*thisyrange)) 
        ws.var(self.YVAR).setUnit('GeV')
        ws.var(self.YVAR).setPlotLabel(self.YLABEL)
        ws.var(self.YVAR).SetTitle(self.YLABEL)
        modelx = Models.Voigtian('sigx',
            x = self.XVAR,
            mean  = [aval,0,30],
            width = [0.01*aval,0.001,5],
            sigma = [0.01*aval,0.001,5],
        )
        modelx.build(ws, 'sigx')
        if self.YRANGE[1]>100: # y variable is h mass
            if yFitFunc == "G": 
                modely = Models.Gaussian('sigy',
                    x = self.YVAR,
                    mean  = [h,0,1.25*h],
                    sigma = [0.1*h,0.01,0.5*h],
                )
            elif yFitFunc == "V":
                modely = Models.Voigtian('sigy',
                    x = self.YVAR,
                    mean  = [0.75*h,0,1.25*h],
                    width = [0.1*h,0.01,0.5*h],
                    sigma = [0.1*h,0.01,0.5*h],
                )
            elif yFitFunc == "CB":
                modely = Models.CrystalBall('sigy',
                    x = self.YVAR,
                    mean  = [h,0,1.25*h],
                    sigma = [0.1*h,0.01,0.5*h],
                    a = [1.0,.5,5],
                    n = [0.5,.1,10],
                )
            elif yFitFunc == "DCB":
                modely = Models.DoubleCrystalBall('sigy',
                    x = self.YVAR,
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
                    x = self.YVAR,
                    mean  = [MEAN, MEAN-2, MEAN+2],
                    sigma = [initialValuesDCB["h"+str(h)+"a"+str(a)]["sigma"],0.05*h,0.5*h],
                    a1    = [initialValuesDCB["h"+str(h)+"a"+str(a)]["a1"],0.1,10],
                    n1    = [initialValuesDCB["h"+str(h)+"a"+str(a)]["n1"],1,20],
                    a2    = [initialValuesDCB["h"+str(h)+"a"+str(a)]["a2"],0.1,10],
                    n2    = [initialValuesDCB["h"+str(h)+"a"+str(a)]["n2"],0.1,5],
                )
            elif yFitFunc == "DG":
                modely = Models.DoubleSidedGaussian('sigy',
                    x = self.YVAR,
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
                    x = self.YVAR,
                    mean  = [h,0,1.25*h],
                    sigma1 = [0.1*h,0.01,0.5*h],
                    sigma2 = [0.2*h,0.01,0.5*h],
                    width1 = [1.0,0.01,10.0],
                    width2 = [2.0,0.01,10.0],
                    yMax = self.YRANGE[1],
                )
            elif yFitFunc == "MB":
                modely = Models.MaxwellBoltzmann('sigy',
                    x = self.YVAR,
                    scale = [0.5*h,0,1000],
                )
            elif yFitFunc == "B":
                modely = Models.Beta('sigy',
                    x = self.YVAR,
                    betaScale = [1/h,0,1],
                    betaA = [5,0,20],
                    betaB = [2,0,10],
                )
            elif yFitFunc == "G2":
                g1 = Models.Gaussian('g1',
                    x = self.YVAR,
                    mean  = [0.7*h, 0.6*h, h],
                    sigma = [0.1*h, 0, 0.5*h], 
                )
                g1.build(ws,'g1')
                g2 = Models.Gaussian('g2',
                    x = self.YVAR,
                    #mean  = 'mean_g1',
                    mean  = [0.8*h, 0.6*h, h],
                    sigma = [0.1*h, 0, 0.5*h], 
                )
                g2.build(ws,'g2')
                modely = Models.Sum('sigy',
                    **{
                        'g1'     : [0.7,0.5,0.9],
                        'g2'     : [0.5,0,1],
                        'recursive': True,
                        'x'      : self.YVAR,
                    }
                )
            elif yFitFunc == "G3":
                g1 = Models.Gaussian('g1',
                    x = self.YVAR,
                    mean  = [0.7*h, 0.6*h, h],
                    sigma = [0.1*h, 0, 0.5*h], 
                )
                g1.build(ws,'g1')
                g2 = Models.Gaussian('g2',
                    x = self.YVAR,
                    #mean  = 'mean_g1',
                    mean  = [0.8*h, 0.6*h, h],
                    sigma = [0.1*h, 0, 0.5*h], 
                )
                g2.build(ws,'g2')
                g3 = Models.Gaussian('g3',
                    x = self.YVAR,
                    #mean  = 'mean_g1',
                    mean  = [0.8*h, 0.6*h, h],
                    sigma = [0.1*h, 0, 0.5*h], 
                )
                g3.build(ws,'g3')
                modely = Models.Sum('sigy',
                    **{
                        'g1'     : [0.7,0.5,0.9],
                        'g2'     : [0.5,0,1],
                        'g3'     : [0.5,0,1],
                        'recursive': True,
                        'x'      : self.YVAR,
                    }
                )
            else:
                raise
            modely.build(ws, 'sigy')
            model = Models.Prod('sig',
                'sigx',
                'sigy',
                x = self.XVAR,
                y = self.YVAR,
            )
        else: # y variable is tt
            if yFitFunc == "G":
                modely = Models.Gaussian('sigy',
                    x = self.YVAR,
                    mean  = [0.5*aval,0,1.25*aval],
                    sigma = [0.1*aval,0.01,0.5*aval],
                )
            elif yFitFunc == "V":
                modely = Models.Voigtian('sigy',
                    x = self.YVAR,
                    mean  = [initialValuesV["h"+str(h)+"a"+str(a)]["mean_sigy"],0.75,30],
                    width = [initialValuesV["h"+str(h)+"a"+str(a)]["width_sigy"],0.01,5],
                    sigma = [initialValuesV["h"+str(h)+"a"+str(a)]["sigma_sigy"],0.01,5],
                )
            elif yFitFunc == "CB":
                modely = Models.CrystalBall('sigy',
                    x = self.YVAR,
                    mean  = [0.5*aval,0,30],
                    sigma = [0.1*aval,0,5],
                    a = [1.0,0.5,5],
                    n = [0.5,0.1,10],
                )
            elif yFitFunc == "DCB":
                modely = Models.DoubleCrystalBall('sigy',
                    x = self.YVAR,
                    mean  = [0.5*aval,0.5,30],
                    sigma = [0.1*aval,0.1,5],
                    a1 = [1.0,0.1,6],
                    n1 = [0.9,0.1,6],
                    a2 = [2.0,0.1,10],
                    n2 = [1.5,0.1,10],
                )
            elif yFitFunc == "DG":
                modely = Models.DoubleSidedGaussian('sigy',
                    x = self.YVAR,
                    mean  = [0.5*aval,0,30],
                    sigma1 = [0.1*aval,0.05*aval,0.4*aval],
                    sigma2 = [0.3*aval,0.05*aval,0.4*aval],
                    yMax = self.YRANGE[1],
                )
            elif yFitFunc == "DV":
                modely = Models.DoubleSidedVoigtian('sigy',
                    x = self.YVAR,
                    mean  = [0.5*aval,0,30],
                    sigma1 = [0.1*aval,0.05*aval,0.4*aval],
                    sigma2 = [0.3*aval,0.05*aval,0.4*aval],
                    width1 = [0.1,0.01,5],
                    width2 = [0.3,0.01,5],
                    yMax = self.YRANGE[1],
                )
            elif yFitFunc == "MB":
                modely = Models.MaxwellBoltzmann('sigy',
                    x = self.YVAR,
                    scale = [0.5*aval,0,30],
                )
            elif yFitFunc == "B":
                modely = Models.Beta('sigy',
                    x = self.YVAR,
                    betaScale = [1/a,0,1],
                    betaA = [5,0,20],
                    betaB = [2,0,10],
                )
            elif yFitFunc == "errG":
                tterf = Models.Erf('tterf',
                   x = self.YVAR,
                   erfScale = [0.4,0.1,5],
                   erfShift = [0.2*aval,0.05*aval,aval],
                )
                ttgaus = Models.Gaussian('ttgaus',
                   x = self.YVAR,
                   mean  = [0.45*aval,0,aval],
                   sigma = [0.1*aval,0.05*aval,0.4*aval],
                )
                ttgaus.build(ws,"ttgaus")
                tterf.build(ws,"tterf")
                modely = Models.Prod('sigy',
                        'ttgaus',
                        'tterf',
                        x = self.YVAR,
                )
            elif yFitFunc == "L":
                #modely = Models.Landau('sigy',
                #    x = self.YVAR,
                #    mu  = [0.5*aval,0,30],
                #    sigma = [0.1*aval,0.05*aval,aval],
                #)
                ttland = Models.Landau('ttland',
                    x = self.YVAR,
                    mu  = [initialValuesL["h"+str(h)+"a"+str(a)]["mu_ttland"],0.1*aval,0.7*aval],
                    sigma = [initialValuesL["h"+str(h)+"a"+str(a)]["sigma_ttland"],0.01,aval],
                )
                ttland.build(ws,'ttland')
                ttgaus = Models.Gaussian('ttgaus',
                   x = self.YVAR,
                   mean  = [initialValuesL["h"+str(h)+"a"+str(a)]["mean_ttgaus"],0.1*aval,0.7*aval],
                   #mean  = [initialValuesL["h"+str(h)+"a"+str(a)]["mean_ttgaus"],0.2*initialValuesL["h"+str(h)+"a"+str(a)]["mean_ttgaus"],30],
                   sigma = [initialValuesL["h"+str(h)+"a"+str(a)]["sigma_ttgaus"],0.01,aval],
                )
                ttgaus.build(ws,"ttgaus")
                modely = Models.Prod('sigy',
                        'ttgaus',
                        'ttland',
                        x = self.YVAR,
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

            if 'PP' in region or not dobgsig:
                model = Models.Prod('sig',
                    'sigx',
                    'sigy',
                    x = self.XVAR,
                    y = self.YVAR,
                )
            else:
                conty = Models.Exponential('conty',
                    x = self.YVAR,
                    lamb = [-0.25,-1,-0.001], # visible
                )
                conty.build(ws,'conty')

                erfy = Models.Erf('erfy',
                    x = self.YVAR,
                    erfScale = [0.1,0.01,10],
                    erfShift = [2,0,10],
                )
                erfy.build(ws,'erfy')

                erfc = Models.Prod('erfcy',
                    'erfy',
                    'conty',
                    x = self.YVAR,
                )
                erfc.build(ws,'erfcy')

                modelymod = Models.Sum('bgsigy',
                    **{ 
                        'erfcy'    : [0.5,0,1],
                        'sigy'     : [0.5,0,1],
                        'recursive': True,
                        'x'        : self.YVAR,
                    }
                )
                modelymod.build(ws,'bgsigy')

                model = Models.Prod('sig',
                    'sigx',
                    'bgsigy',
                    x = self.XVAR,
                    y = self.YVAR,
                )

        name = 'h{}_a{}_{}'.format(h,a,tag)
        model.build(ws, name)
        if results:
            for param in results:
                ws.var(param).setVal(results[param])
        hist = histMap[self.SIGNAME.format(h=h,a=a)]
        saveDir = '{}/{}'.format(self.plotDir,shift if shift else 'central')
        results, errors = model.fit2D(ws, hist, name, saveDir=saveDir, save=True, doErrors=True)
        if self.binned:
            integral = histMap[self.SIGNAME.format(h=h,a=a)].Integral() * scale
        else:
            integral = histMap[self.SIGNAME.format(h=h,a=a)].sumEntries('{0}>{2} && {0}<{3} && {1}>{4} && {1}<{5}'.format(self.XVAR,self.YVAR,*self.XRANGE+self.YRANGE)) * scale
            if integral!=integral:
                logging.error('Integral for spline is invalid: h{h} a{a} {region} {shift}'.format(h=h,a=a,region=region,shift=shift))
                raise
    
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
        ygausOnly = kwargs.get('ygausOnly',False)
        isKinFit = kwargs.get('isKinFit',False)
        yFitFunc = kwargs.get('yFitFunc','G')
        load = kwargs.get('load',False)
        skipFit = kwargs.get('skipFit',False)
        dobgsig = kwargs.get('doBackgroundSignal',False)
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

                amasses = self.HAMAP[h]
                avals = [self.aToFloat(x) for x in amasses]

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

        fitFuncs = self.fitSignalParams(results,errors,integrals,region,shift,yFitFunc=yFitFunc)

        return results, errors, integrals, fitFuncs

    def getParams(self,yFitFunc):
        xparams = ['mean_sigx','width_sigx','sigma_sigx']
        if   yFitFunc == "V"   : yparams = ['mean_sigy','width_sigy','sigma_sigy']
        elif yFitFunc == "G"   : yparams = ['mean_sigy', 'sigma_sigy']
        elif yFitFunc == "CB"  : yparams = ['mean_sigy', 'sigma_sigy', 'a_sigy', 'n_sigy']
        elif yFitFunc == "DCB" : yparams = ['mean_sigy', 'sigma_sigy', 'a1_sigy', 'n1_sigy', 'a2_sigy', 'n2_sigy']
        elif yFitFunc == "DG"  : yparams = ['mean_sigy', 'sigma1_sigy', 'sigma2_sigy']
        elif yFitFunc == "DV"  : yparams = ['mean_sigy', 'sigma1_sigy', 'sigma2_sigy','width1_sigy','width2_sigy']
        elif yFitFunc == "MB"  : yparams = ['scale_sigy']
        elif yFitFunc == "B"   : yparams = ['betaScale_sigy','betaA_sigy','betaB_sigy']
        elif yFitFunc == "errG": yparams = ['mean_ttgaus', 'sigma_ttgaus','erfShift_tterf','erfScale_tterf']
        elif yFitFunc == "L"   : yparams = ['mean_ttgaus', 'sigma_ttgaus','mu_ttland','sigma_ttland']
        elif yFitFunc == "G2"  : yparams = ['mean_g1', 'sigma_g1','mean_g2','sigma_g2','g1_frac']
        elif yFitFunc == "G3"  : yparams = ['mean_g1', 'sigma_g1','mean_g2','sigma_g2','mean_g3','sigma_g3','g1_frac','g2_frac']
        else: raise
        return xparams, yparams

    def fitSignalParams(self,results,errors,integrals,region,shift='',**kwargs):
        tag = kwargs.get('tag','{}{}'.format(region,'_'+shift if shift else ''))
        yFitFunc = kwargs.get('yFitFunc','G')

        if self.do2D:
            fitFuncs = {
                'mean_sigx'      : ROOT.TF2('xmean_{}'.format(tag),     '[0]+[1]*x+[2]*y',                           *self.HRANGE+self.ARANGE),
                'width_sigx'     : ROOT.TF2('xwidth_{}'.format(tag),    '[0]+[1]*x+[2]*y+[3]*x*y+[4]*x*x+[5]*y*y',   *self.HRANGE+self.ARANGE),
                'sigma_sigx'     : ROOT.TF2('xsigma_{}'.format(tag),    '[0]+[1]*x+[2]*y+[3]*x*y+[4]*x*x+[5]*y*y',   *self.HRANGE+self.ARANGE),
                'mean_sigy'      : ROOT.TF2('ymean_{}'.format(tag),     '[0]+[1]*x+[2]*y+[3]*x*y',                   *self.HRANGE+self.ARANGE),
                'width_sigy'     : ROOT.TF2('ywidth_{}'.format(tag),    '[0]+[1]*x+[2]*y+[3]*x*y+[4]*x*x+[5]*y*y',   *self.HRANGE+self.ARANGE),
                'width1_sigy'    : ROOT.TF2('ywidth1_{}'.format(tag),   '[0]+[1]*x+[2]*y+[3]*x*y+[4]*x*x+[5]*y*y',   *self.HRANGE+self.ARANGE),
                'width2_sigy'    : ROOT.TF2('ywidth2_{}'.format(tag),   '[0]+[1]*x+[2]*y+[3]*x*y+[4]*x*x+[5]*y*y',   *self.HRANGE+self.ARANGE),
                'sigma_sigy'     : ROOT.TF2('ysigma_{}'.format(tag),    '[0]+[1]*x+[2]*y+[3]*x*y+[4]*x*x+[5]*y*y',   *self.HRANGE+self.ARANGE),
                'sigma1_sigy'    : ROOT.TF2('ysigma1_{}'.format(tag),   '[0]+[1]*x+[2]*y+[3]*x*y+[4]*x*x+[5]*y*y',   *self.HRANGE+self.ARANGE),
                'sigma2_sigy'    : ROOT.TF2('ysigma2_{}'.format(tag),   '[0]+[1]*x+[2]*y+[3]*x*y+[4]*x*x+[5]*y*y',   *self.HRANGE+self.ARANGE),
                'a_sigy'         : ROOT.TF2('ya_{}'.format(tag),        '[0]+[1]*x+[2]*y+[3]*x*y+[4]*x*x+[5]*y*y',   *self.HRANGE+self.ARANGE),
                'a1_sigy'        : ROOT.TF2('ya1_{}'.format(tag),       '[0]+[1]*x+[2]*y+[3]*x*y+[4]*x*x+[5]*y*y',   *self.HRANGE+self.ARANGE),
                'a2_sigy'        : ROOT.TF2('ya2_{}'.format(tag),       '[0]+[1]*x+[2]*y+[3]*x*y+[4]*x*x+[5]*y*y',   *self.HRANGE+self.ARANGE),
                'n_sigy'         : ROOT.TF2('yn_{}'.format(tag),        '[0]+[1]*x+[2]*y+[3]*x*y+[4]*x*x+[5]*y*y',   *self.HRANGE+self.ARANGE),
                'n1_sigy'        : ROOT.TF2('yn1_{}'.format(tag),       '[0]+[1]*x+[2]*y+[3]*x*y+[4]*x*x+[5]*y*y',   *self.HRANGE+self.ARANGE),
                'n2_sigy'        : ROOT.TF2('yn2_{}'.format(tag),       '[0]+[1]*x+[2]*y+[3]*x*y+[4]*x*x+[5]*y*y',   *self.HRANGE+self.ARANGE),
                'betaScale_sigy' : ROOT.TF2('ybetaScale_{}'.format(tag),'[0]+[1]*x+[2]*y+[3]*x*y+[4]*x*x+[5]*y*y',   *self.HRANGE+self.ARANGE),
                'scale_sigy'     : ROOT.TF2('yscale_{}'.format(tag),    '[0]+[1]*x+[2]*y+[3]*x*y+[4]*x*x+[5]*y*y',   *self.HRANGE+self.ARANGE),
                'betaA_sigy'     : ROOT.TF2('ybetaA_{}'.format(tag),    '[0]+[1]*x+[2]*y+[3]*x*y+[4]*x*x+[5]*y*y',   *self.HRANGE+self.ARANGE),
                'betaB_sigy'     : ROOT.TF2('ybetaB_{}'.format(tag),    '[0]+[1]*x+[2]*y+[3]*x*y+[4]*x*x+[5]*y*y',   *self.HRANGE+self.ARANGE),
                'mean_ttgaus'    : ROOT.TF2('mean_ttgaus_{}'.format(tag),     '[0]+[1]*x+[2]*y+[3]*x*y+[4]*x*x+[5]*y*y',   *self.HRANGE+self.ARANGE),
                'sigma_ttgaus'   : ROOT.TF2('sigma_ttgaus_{}'.format(tag),    '[0]+[1]*x+[2]*y+[3]*x*y+[4]*x*x+[5]*y*y',   *self.HRANGE+self.ARANGE),
                'erfScale_tterf' : ROOT.TF2('yerfScale_tterf_{}'.format(tag), '[0]+[1]*x+[2]*y+[3]*x*y+[4]*x*x+[5]*y*y',   *self.HRANGE+self.ARANGE),
                'erfShift_tterf' : ROOT.TF2('yerfShift_tterf_{}'.format(tag), '[0]+[1]*x+[2]*y+[3]*x*y+[4]*x*x+[5]*y*y',   *self.HRANGE+self.ARANGE),
                'mu_ttland'      : ROOT.TF2('mu_ttland_{}'.format(tag),       '[0]+[1]*x+[2]*y+[3]*x*y+[4]*x*x+[5]*y*y',   *self.HRANGE+self.ARANGE),
                'sigma_ttland'   : ROOT.TF2('sigma_ttland_{}'.format(tag),    '[0]+[1]*x+[2]*y+[3]*x*y+[4]*x*x+[5]*y*y',   *self.HRANGE+self.ARANGE),
                'mean_g1'        : ROOT.TF2('mean_g1_{}'.format(tag),         '[0]+[1]*x+[2]*y+[3]*x*y+[4]*x*x+[5]*y*y',   *self.HRANGE+self.ARANGE),
                'sigma_g1'       : ROOT.TF2('sigma_g1_{}'.format(tag),        '[0]+[1]*x+[2]*y+[3]*x*y+[4]*x*x+[5]*y*y',   *self.HRANGE+self.ARANGE),
                'mean_g2'        : ROOT.TF2('mean_g2_{}'.format(tag),         '[0]+[1]*x+[2]*y+[3]*x*y+[4]*x*x+[5]*y*y',   *self.HRANGE+self.ARANGE),
                'sigma_g2'       : ROOT.TF2('sigma_g2_{}'.format(tag),        '[0]+[1]*x+[2]*y+[3]*x*y+[4]*x*x+[5]*y*y',   *self.HRANGE+self.ARANGE),
                'mean_g3'        : ROOT.TF2('mean_g3_{}'.format(tag),         '[0]+[1]*x+[2]*y+[3]*x*y+[4]*x*x+[5]*y*y',   *self.HRANGE+self.ARANGE),
                'sigma_g3'       : ROOT.TF2('sigma_g3_{}'.format(tag),        '[0]+[1]*x+[2]*y+[3]*x*y+[4]*x*x+[5]*y*y',   *self.HRANGE+self.ARANGE),
                'g1_frac'        : ROOT.TF2('g1_frac_{}'.format(tag),         '[0]+[1]*x+[2]*y+[3]*x*y+[4]*x*x+[5]*y*y',   *self.HRANGE+self.ARANGE),
                'g2_frac'        : ROOT.TF2('g2_frac_{}'.format(tag),         '[0]+[1]*x+[2]*y+[3]*x*y+[4]*x*x+[5]*y*y',   *self.HRANGE+self.ARANGE),
                'integral'       : ROOT.TF2('integral_{}'.format(tag),  '[0]+[1]*x+TMath::Erf([2]+[3]*y+[4]*x)*TMath::Erfc([5]+[6]*y+[7]*x)',*self.HRANGE+self.ARANGE),
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
                    'mean_sigx'     : ROOT.TF1('xmean_h{}_{}'.format(h,tag),     '[0]+[1]*x',         *self.ARANGE),
                    'width_sigx'    : ROOT.TF1('xwidth_h{}_{}'.format(h,tag),    '[0]+[1]*x+[2]*x*x', *self.ARANGE),
                    'sigma_sigx'    : ROOT.TF1('xsigma_h{}_{}'.format(h,tag),    '[0]+[1]*x+[2]*x*x', *self.ARANGE),
                    'mean_sigy'     : ROOT.TF1('ymean_h{}_{}'.format(h,tag),     '[0]+[1]*x',         *self.ARANGE),
                    'width_sigy'    : ROOT.TF1('ywidth_h{}_{}'.format(h,tag),    '[0]+[1]*x+[2]*x*x', *self.ARANGE),
                    'width1_sigy'   : ROOT.TF1('ywidth1_h{}_{}'.format(h,tag),   '[0]+[1]*x+[2]*x*x', *self.ARANGE),
                    'width2_sigy'   : ROOT.TF1('ywidth2_h{}_{}'.format(h,tag),   '[0]+[1]*x+[2]*x*x', *self.ARANGE),
                    'sigma_sigy'    : ROOT.TF1('ysigma_h{}_{}'.format(h,tag),    '[0]+[1]*x+[2]*x*x', *self.ARANGE),
                    'sigma1_sigy'   : ROOT.TF1('ysigma1_h{}_{}'.format(h,tag),   '[0]+[1]*x+[2]*x*x', *self.ARANGE),
                    'sigma2_sigy'   : ROOT.TF1('ysigma2_h{}_{}'.format(h,tag),   '[0]+[1]*x+[2]*x*x', *self.ARANGE),
                    'a_sigy'        : ROOT.TF1('ya_h{}_{}'.format(h,tag),        '[0]+[1]*x+[2]*x*x', *self.ARANGE),
                    'a1_sigy'       : ROOT.TF1('ya1_h{}_{}'.format(h,tag),       '[0]+[1]*x+[2]*x*x', *self.ARANGE),
                    'a2_sigy'       : ROOT.TF1('ya2_h{}_{}'.format(h,tag),       '[0]+[1]*x+[2]*x*x', *self.ARANGE),
                    'n_sigy'        : ROOT.TF1('yn_h{}_{}'.format(h,tag),        '[0]+[1]*x+[2]*x*x', *self.ARANGE),
                    'n1_sigy'       : ROOT.TF1('yn1_h{}_{}'.format(h,tag),       '[0]+[1]*x+[2]*x*x', *self.ARANGE),
                    'n2_sigy'       : ROOT.TF1('yn2_h{}_{}'.format(h,tag),       '[0]+[1]*x+[2]*x*x', *self.ARANGE),
                    'betaScale_sigy': ROOT.TF1('ybetaScale_h{}_{}'.format(h,tag),'[0]+[1]*x+[2]*x*x', *self.ARANGE),
                    'scale_sigy'    : ROOT.TF1('yscale_h{}_{}'.format(h,tag),    '[0]+[1]*x+[2]*x*x', *self.ARANGE),
                    'betaA_sigy'    : ROOT.TF1('ybetaA_h{}_{}'.format(h,tag),    '[0]+[1]*x+[2]*x*x', *self.ARANGE),
                    'betaB_sigy'    : ROOT.TF1('ybetaB_h{}_{}'.format(h,tag),    '[0]+[1]*x+[2]*x*x', *self.ARANGE),
                    'mean_ttgaus'   : ROOT.TF1('mean_ttgaus_h{}_{}'.format(h,tag),     '[0]+[1]*x+[2]*x*x', *self.ARANGE),
                    'sigma_ttgaus'  : ROOT.TF1('sigma_ttgaus_h{}_{}'.format(h,tag),    '[0]+[1]*x+[2]*x*x', *self.ARANGE),
                    'erfScale_tterf': ROOT.TF1('yerfScale_tterf_h{}_{}'.format(h,tag), '[0]+[1]*x+[2]*x*x', *self.ARANGE),
                    'erfShift_tterf': ROOT.TF1('yerfShift_tterf_h{}_{}'.format(h,tag), '[0]+[1]*x+[2]*x*x', *self.ARANGE),
                    'mu_ttland'     : ROOT.TF1('mu_ttland_h{}_{}'.format(h,tag),       '[0]+[1]*x+[2]*x*x', *self.ARANGE),
                    'sigma_ttland'  : ROOT.TF1('sigma_ttland_h{}_{}'.format(h,tag),    '[0]+[1]*x+[2]*x*x', *self.ARANGE),
                    'mean_g1'       : ROOT.TF1('mean_g1_h{}_{}'.format(h,tag),         '[0]+[1]*x+[2]*x*x', *self.ARANGE),
                    'sigma_g1'      : ROOT.TF1('sigma_g1_h{}_{}'.format(h,tag),        '[0]+[1]*x+[2]*x*x', *self.ARANGE),
                    'mean_g2'       : ROOT.TF1('mean_g2_h{}_{}'.format(h,tag),         '[0]+[1]*x+[2]*x*x', *self.ARANGE),
                    'sigma_g2'      : ROOT.TF1('sigma_g2_h{}_{}'.format(h,tag),        '[0]+[1]*x+[2]*x*x', *self.ARANGE),
                    'mean_g3'       : ROOT.TF1('mean_g3_h{}_{}'.format(h,tag),         '[0]+[1]*x+[2]*x*x', *self.ARANGE),
                    'sigma_g3'      : ROOT.TF1('sigma_g3_h{}_{}'.format(h,tag),        '[0]+[1]*x+[2]*x*x', *self.ARANGE),
                    'g1_frac'       : ROOT.TF1('g1_frac_h{}_{}'.format(h,tag),         '[0]+[1]*x+[2]*x*x', *self.ARANGE),
                    'g2_frac'       : ROOT.TF1('g2_frac_h{}_{}'.format(h,tag),         '[0]+[1]*x+[2]*x*x', *self.ARANGE),
                    'integral'      : ROOT.TF1('integral_h{}_{}'.format(h,tag),  '[0]+TMath::Erf([1]+[2]*x)*TMath::Erfc([3]+[4]*x)', *self.ARANGE),
                }
                # set initial values
                fitFuncs[h]['integral'].SetParameter(1,-0.005)
                fitFuncs[h]['integral'].SetParameter(2,0.02)
                fitFuncs[h]['integral'].SetParameter(3,-0.5)
                fitFuncs[h]['integral'].SetParameter(4,0.08)

        xparams, yparams = self.getParams(yFitFunc)

        for param in xparams+yparams+['integral']:
            logging.info('Fitting {}'.format(param))
            Hs = sorted(results)
            As = {h: [self.aToStr(a) for a in sorted([self.aToFloat(x) for x in results[h]])] for h in Hs}
            xvals = [h for h in Hs for a in As[h]]
            xerrs = [0] * len(xvals)
            yvals = [self.aToFloat(a) for h in Hs for a in As[h]]
            yerrs = [0] * len(yvals)
            if param=='integral':
                zvals = [integrals[h][a] for h in Hs for a in As[h]]
            else:
                zvals = [results[h][a][param] for h in Hs for a in As[h]]
                zerrs = [errors[h][a][param] for h in Hs for a in As[h]]
            if self.do2D:
                #graph = ROOT.TGraph2DErrors(len(xvals), array('d',xvals), array('d',yvals), array('d',zvals), array('d'
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

            for h in [125,300,750]:
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


    def buildSpline(self,vals,errs,integrals,region,shifts=[],isKinFit=False,**kwargs):
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
        xVar = kwargs.pop('xVar',self.XVAR)
        yVar = kwargs.pop('yVar',self.YVAR)
        yFitFunc = kwargs.pop('yFitFunc','G')
        ygausOnly = kwargs.get('ygausOnly',False)
        dobgsig = kwargs.get('doBackgroundSignal',False)
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

        # create parameter splines
        splines = {}
        xparams, yparams = self.getParams(yFitFunc)

        if   yFitFunc == "V"   : ym = Models.Voigtian
        elif yFitFunc == "G"   : ym = Models.Gaussian
        elif yFitFunc == "CB"  : ym = Models.CrystalBall
        elif yFitFunc == "DCB" : ym = Models.DoubleCrystalBall
        elif yFitFunc == "DG"  : ym = Models.DoubleSidedGaussian
        elif yFitFunc == "DV"  : ym = Models.DoubleSidedVoigtian
        elif yFitFunc == "MB"  : ym = Models.MaxwellBoltzmann
        elif yFitFunc == "B"   : ym = Models.Beta
        elif yFitFunc != "L" and yFitFunc != "errG" and yFitFunc != "G3" and yFitFunc != "G2": raise


        if self.doParamFit:
            for param in xparams+yparams+['integral']:
                if self.do2D:
                    name = '{param}_{splinename}_{region}'.format(param=param,splinename=self.SPLINENAME,region=region)
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
                        name = '{param}_{splinename}_{region}'.format(param=param,splinename=self.SPLINENAME.format(h=h),region=region)
                        # here is using TF1
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
                modelx = Models.Voigtian(self.SPLINENAME+'_x',
                    x = xVar,
                    **{param.rstrip('_sigx'): '{param}_{splinename}_{region}'.format(param=param, splinename=self.SPLINENAME, region=region) for param in xparams}
                )
                modelx.build(workspace,'{}_{}'.format(self.SPLINENAME,region+'_x'))

                if yFitFunc=='L':
                    modely_gaus = Models.Gaussian("model_gaus",
                        x = yVar,
                         **{param: '{param}_ttgaus_{splinename}_{region}'.format(param=param, splinename=self.SPLINENAME, region=region) for param in ['mean','sigma']}
                    )
                    modely_gaus.build(workspace,'{}_{}'.format(self.SPLINENAME,region+'_gaus_y'))
                    modely_land = Models.Landau("model_land",
                        x = yVar,
                         **{param: '{param}_ttland_{splinename}_{region}'.format(param=param, splinename=self.SPLINENAME, region=region) for param in ['mu','sigma']}
                    )
                    modely_land.build(workspace,'{}_{}'.format(self.SPLINENAME,region+'_land_y'))
                    modely = Models.Prod(self.SPLINENAME+'_y',
                        '{}_{}'.format(self.SPLINENAME,region+'_gaus_y'),
                        '{}_{}'.format(self.SPLINENAME,region+'_land_y'),
                    )
                else:
                    modely = ym(self.SPLINENAME+'_y',
                        x = yVar,
                        yMax = self.YRANGE[1],
                        **{param.rstrip('_sigy'): '{param}_{splinename}_{region}'.format(param=param, splinename=self.SPLINENAME, region=region) for param in yparams}
                    )
                modely.build(workspace,'{}_{}'.format(self.SPLINENAME,region+'_y'))
                        
                model = Models.Prod(self.SPLINENAME,
                    '{}_{}'.format(self.SPLINENAME,region+'_x'),
                    '{}_{}'.format(self.SPLINENAME,region+'_y'),
                )
                model.build(workspace,'{}_{}'.format(self.SPLINENAME,region))


                return model
            else:
                models = {}
                for h in self.HMASSES:
                    modelx = Models.Voigtian(self.SPLINENAME.format(h=h)+'_x',
                        x = xVar,
                        **{param.rstrip('_sigx'): '{param}_{splinename}_{region}'.format(param=param, splinename=self.SPLINENAME.format(h=h), region=region) for param in xparams}
                    )
                    modelx.build(workspace,'{}_{}'.format(self.SPLINENAME.format(h=h),region+'_x'))

                    if yFitFunc=='L':
                        modely_gaus = Models.Gaussian("model_gaus",
                            x = yVar,
                             **{param: '{param}_ttgaus_{splinename}_{region}'.format(param=param, splinename=self.SPLINENAME.format(h=h), region=region) for param in ['mean','sigma']}
                        )
                        modely_gaus.build(workspace,'{}_{}'.format(self.SPLINENAME.format(h=h),region+'_gaus_y'))
                        modely_land = Models.Landau("model_land",
                            x = yVar,
                             **{param: '{param}_ttland_{splinename}_{region}'.format(param=param, splinename=self.SPLINENAME.format(h=h), region=region) for param in ['mu','sigma']}
                        )
                        modely_land.build(workspace,'{}_{}'.format(self.SPLINENAME.format(h=h),region+'_land_y'))
                        modely = Models.Prod(self.SPLINENAME.format(h=h)+'_y',
                            '{}_{}'.format(self.SPLINENAME.format(h=h),region+'_gaus_y'),
                            '{}_{}'.format(self.SPLINENAME.format(h=h),region+'_land_y'),
                        )
                    else:
                        modely = ym(self.SPLINENAME.format(h=h)+'_y',
                            x = yVar,
                            yMax = self.YRANGE[1],
                            **{param.rstrip('_sigy'): '{param}_{splinename}_{region}'.format(param=param, splinename=self.SPLINENAME.format(h=h), region=region) for param in yparams}
                        )
                    modely.build(workspace,'{}_{}'.format(self.SPLINENAME.format(h=h),region+'_y'))
                            
                    model = Models.Prod(self.SPLINENAME.format(h=h),
                        '{}_{}'.format(self.SPLINENAME.format(h=h),region+'_x'),
                        '{}_{}'.format(self.SPLINENAME.format(h=h),region+'_y'),
                    )
                    model.build(workspace,'{}_{}'.format(self.SPLINENAME.format(h=h),region))


                    models[h] = model

                return models

        # create parameter splines
        for param in xparams+yparams:
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
                            paramShifts[shift]['up']   += [vals[shift+'Up'  ][h][a][param]]
                            paramShifts[shift]['down'] += [vals[shift+'Down'][h][a][param]]
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
                        paramValues += [vals[''][h][a][param]]
                        for shift in shifts:
                            if shift not in paramShifts: paramShifts[shift] = {'up': [], 'down': []}
                            paramShifts[shift]['up']   += [vals[shift+'Up'  ][h][a][param]]
                            paramShifts[shift]['down'] += [vals[shift+'Down'][h][a][param]]
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
            modelx = Models.Voigtian(self.SPLINENAME+'_x',
                x = xVar,
                **{param.rstrip('_sigx'): '{param}_{region}'.format(param=param, region=region) for param in xparams}
            )
            modelx.build(workspace,'{}_{}'.format(self.SPLINENAME,region+'_x'))

            if yFitFunc=='L':
                modely_gaus = Models.Gaussian("model_gaus",
                    x = yVar,
                     **{param: '{param}_ttgaus_{region}'.format(param=param, region=region) for param in ['mean','sigma']}
                )
                modely_gaus.build(workspace,'{}_{}'.format(self.SPLINENAME,region+'_gaus_y'))
                modely_land = Models.Landau("model_land",
                    x = yVar,
                     **{param: '{param}_ttland_{region}'.format(param=param, region=region) for param in ['mu','sigma']}
                )
                modely_land.build(workspace,'{}_{}'.format(self.SPLINENAME,region+'_land_y'))
                modely = Models.Prod(self.SPLINENAME+'_y',
                    '{}_{}'.format(self.SPLINENAME,region+'_gaus_y'),
                    '{}_{}'.format(self.SPLINENAME,region+'_land_y'),
                )
            else:
                modely = ym(self.SPLINENAME+'_y',
                    x = yVar,
                    yMax = self.YRANGE[1],
                    **{param.rstrip('_sigy'): '{param}_{region}'.format(param=param, region=region) for param in yparams}
                )
            modely.build(workspace,'{}_{}'.format(self.SPLINENAME,region+'_y'))
                    
            model = Models.Prod(self.SPLINENAME,
                '{}_{}'.format(self.SPLINENAME,region+'_x'),
                '{}_{}'.format(self.SPLINENAME,region+'_y'),
            )
            model.build(workspace,'{}_{}'.format(self.SPLINENAME,region))


            return model
        else:
            models = {}
            for h in self.HMASSES:
                modelx = Models.Voigtian(self.SPLINENAME.format(h=h)+'_x',
                    x = xVar,
                    **{param.rstrip('_sigx'): '{param}_h{h}_{region}'.format(param=param, h=h, region=region) for param in xparams}
                )
                modelx.build(workspace,'{}_{}'.format(self.SPLINENAME.format(h=h),region+'_x'))

                if yFitFunc=='L':
                    modely_gaus = Models.Gaussian("model_gaus",
                        x = yVar,
                         **{param: '{param}_ttgaus_h{h}_{region}'.format(param=param, h=h, region=region) for param in ['mean','sigma']}
                    )
                    modely_gaus.build(workspace,'{}_{}'.format(self.SPLINENAME.format(h=h),region+'_gaus_y'))
                    modely_land = Models.Landau("model_land",
                        x = yVar,
                         **{param: '{param}_ttland_h{h}_{region}'.format(param=param, h=h, region=region) for param in ['mu','sigma']}
                    )
                    modely_land.build(workspace,'{}_{}'.format(self.SPLINENAME.format(h=h),region+'_land_y'))
                    modely = Models.Prod(self.SPLINENAME.format(h=h)+'_y',
                        '{}_{}'.format(self.SPLINENAME.format(h=h),region+'_gaus_y'),
                        '{}_{}'.format(self.SPLINENAME.format(h=h),region+'_land_y'),
                    )
                else:
                    modely = ym(self.SPLINENAME.format(h=h)+'_y',
                        x = yVar,
                        yMax = self.YRANGE[1],
                        **{param.rstrip('_sigy'): '{param}_h{h}_{region}'.format(param=param, h=h, region=region) for param in yparams}
                    )
                modely.build(workspace,'{}_{}'.format(self.SPLINENAME.format(h=h),region+'_y'))
                        
                model = Models.Prod(self.SPLINENAME.format(h=h),
                    '{}_{}'.format(self.SPLINENAME.format(h=h),region+'_x'),
                    '{}_{}'.format(self.SPLINENAME.format(h=h),region+'_y'),
                )
                model.build(workspace,'{}_{}'.format(self.SPLINENAME.format(h=h),region))


                models[h] = model

            return models


    def addControlModels(self, load=False, skipFit=False):
        region = 'control'
        workspace = self.buildWorkspace('control')
        self.initializeWorkspace(workspace=workspace)
        super(HaaLimits2D, self).buildModel(region=region, workspace=workspace)
        if load:
            vals, errs, ints = self.loadBackgroundFit(region,workspace=workspace)
        if not skipFit:
            vals, errs, ints = self.fitBackground(region=region, workspace=workspace)
        
        if load:
            allintegrals, errors = self.loadComponentIntegrals(region)
        if not skipFit:
            allintegrals, errors = self.buildComponentIntegrals(region,vals,errs,ints, workspace.pdf('bg_control'))

        self.control_vals = vals
        self.control_errs = errs
        self.control_integrals = ints
        self.control_integralErrors = errors
        self.control_integralValues = allintegrals

    def fitBackground(self,region,shift='',**kwargs):
        scale = kwargs.pop('scale',1)

        if region=='control':
            return super(HaaLimits2D, self).fitBackground(region=region, shift=shift, **kwargs)

        workspace = kwargs.pop('workspace',self.workspace)
        xVar = kwargs.pop('xVar',self.XVAR)
        yVar = kwargs.pop('yVar',self.YVAR)

        model = workspace.pdf('bg_{}_xy'.format(region))
        name = 'data_prefit_{}{}'.format(region,'_'+shift if shift else '')
        hist = self.histMap[region][shift]['dataNoSig']
        if hist.InheritsFrom('TH1'):
            integral = hist.Integral() * scale # 2D restricted integral?
            data = ROOT.RooDataHist(name,name,ROOT.RooArgList(workspace.var(xVar),workspace.var(yVar)),hist)
        else:
            data = hist.Clone(name)
            integral = hist.sumEntries('{0}>{2} && {0}<{3} && {1}>{4} && {1}<{5}'.format(xVar,yVar,*self.XRANGE+self.YRANGE)) * scale

        fr = model.fitTo(data,ROOT.RooFit.Save(),ROOT.RooFit.SumW2Error(True), ROOT.RooFit.PrintLevel(-1))

        xFrame = workspace.var(xVar).frame()
        data.plotOn(xFrame)
        # continuum
        model.plotOn(xFrame,ROOT.RooFit.Components('cont1_{}_x'.format(region)),ROOT.RooFit.LineStyle(ROOT.kDashed))
        if self.XRANGE[0]<4:
            model.plotOn(xFrame,ROOT.RooFit.Components('cont3_{}_x'.format(region)),ROOT.RooFit.LineStyle(ROOT.kDashed))
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
        python_mkdir(self.plotDir)
        canvas.Print('{}/model_fit_{}{}_xproj.png'.format(self.plotDir,region,'_'+shift if shift else ''))
        if mi<0:
            xFrame.SetMinimum(0.1)
        canvas.SetLogy(True)
        canvas.Print('{}/model_fit_{}{}_xproj_log.png'.format(self.plotDir,region,'_'+shift if shift else ''))

        yFrame = workspace.var(yVar).frame()
        data.plotOn(yFrame)
        # continuum
        model.plotOn(yFrame,ROOT.RooFit.Components('conty1_{}_y'.format(region)),ROOT.RooFit.LineStyle(ROOT.kDashed))
        # combined model
        model.plotOn(yFrame)
        model.paramOn(yFrame,ROOT.RooFit.Layout(0.72,0.98,0.90))

        canvas = ROOT.TCanvas('c','c',800,800)
        canvas.SetRightMargin(0.3)
        yFrame.Draw()
        prims = canvas.GetListOfPrimitives()
        for prim in prims:
            if 'paramBox' in prim.GetName():
                prim.SetTextSize(0.02)
        mi = yFrame.GetMinimum()
        ma = yFrame.GetMaximum()
        canvas.Print('{}/model_fit_{}{}_yproj.png'.format(self.plotDir,region,'_'+shift if shift else ''))
        if mi<0:
            yFrame.SetMinimum(0.1)
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
    def addControlData(self,**kwargs):
        # build the models after doing the prefit stuff
        region = 'control'
        xVar = '{}_{}'.format(self.XVAR,region)
        #xVar = self.XVAR
        self.addVar(xVar, *self.XRANGE, unit='GeV', label=self.XLABEL, workspace=self.workspace)
        super(HaaLimits2D, self).buildModel(region=region, workspace=self.workspace, xVar=xVar)
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
        mh = kwargs.pop('h',125)
        ma = kwargs.pop('a',15)
        scale = kwargs.pop('scale',1)

        workspace = self.workspace

        for region in self.REGIONS:
            xVar = self.XVAR
            yVar = self.YVAR

            # build the models after doing the prefit stuff
            prebuiltParams = {p:p for p in self.background_params[region]}
            self.addVar(xVar, *self.XRANGE, unit='GeV', label=self.XLABEL, workspace=workspace)
            self.addVar(yVar, *self.YRANGE, unit='GeV', label=self.XLABEL, workspace=workspace)
            self.buildModel(region=region,workspace=workspace,xVar=xVar,yVar=yVar,**prebuiltParams)
            self.loadBackgroundFit(region,workspace=workspace)

            x = workspace.var(xVar)
            x.setBins(self.XBINNING)
            y = workspace.var(yVar)
            y.setBins(self.YBINNING)

            # save binned data
            if doBinned:

                bgs = self.getComponentFractions(workspace.pdf('bg_{}_x'.format(region)))

                for bg in bgs:
                    bgname = bg.strip('_x') if region in bg else '{}_{}'.format(bg,region)
                    pdf = workspace.pdf(bg)
                    integral = workspace.function('integral_{}'.format(bgname))

                    args = ROOT.RooArgSet(x,y)
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
                model = workspace.pdf('bg_{}_xy'.format(region))
                h = self.histMap[region]['']['dataNoSig']
                if h.InheritsFrom('TH1'):
                    integral = h.Integral() * scale # 2D integral?
                else:
                    integral = h.sumEntries('{0}>{2} && {0}<{3} && {1}>{4} && {1}<{5}'.format(xVar,yVar,*self.XRANGE+self.YRANGE)) * scale
                if asimov:
                    data_obs = model.generateBinned(ROOT.RooArgSet(self.workspace.var(xVar),self.workspace.var(yVar)),integral,1)
                else:
                    data_obs = model.generate(ROOT.RooArgSet(self.workspace.var(xVar),self.workspace.var(yVar)),int(integral))
                if addSignal:
                    # TODO, doesn't work with new setup
                    raise NotImplementedError
                    logging.info('Generating dataset with signal {}'.format(region))
                    self.workspace.var('MH').setVal(mh)
                    self.workspace.var('MA').setVal(ma)
                    model = self.workspace.pdf('{}_{}'.format(self.SPLINENAME.format(h=mh),region))
                    integral = self.workspace.function('integral_{}_{}'.format(self.SPLINENAME.format(h=mh),region)).getVal()
                    if asimov:
                        sig_obs = model.generate(ROOT.RooArgSet(self.workspace.var(xVar),self.workspace.var(yVar)),integral,1)
                        data_obs.add(sig_obs)
                    else:
                        sig_obs = model.generate(ROOT.RooArgSet(self.workspace.var(xVar),self.workspace.var(yVar)),int(integral))
                        data_obs.append(sig_obs)
                data_obs.SetName(name)
            else:
                # use the provided data
                if hist.InheritsFrom('TH1'):
                    data_obs = ROOT.RooDataHist(name,name,ROOT.RooArgList(self.workspace.var(xVar),self.workspace.var(yVar)),self.histMap[region]['']['data'])
                else:
                    data_obs = hist.Clone(name)
                    data_obs.get().find(xVar).setBins(self.XBINNING)
                    data_obs.get().find(yVar).setBins(self.YBINNING)
            self.wsimport(data_obs)

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
                canvas.Print('{}/data_obs_{}_xproj.png'.format(self.plotDir,region))
                canvas.SetLogy(True)
                canvas.Print('{}/data_obs_{}_xproj_log.png'.format(self.plotDir,region))

                yFrame = self.workspace.var(yVar).frame()
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
            xVar = '{}_{}'.format(self.XVAR,region)
            name = 'data_obs_{}'.format(region)
            hist = self.histMap[region]['']['data']
            if hist.InheritsFrom('TH1'):
                data_obs = ROOT.RooDataHist(name,name,ROOT.RooArgList(self.workspace.var(xVar)),hist)
            else:
                data_obs = hist.Clone(name)
                data_obs.get().find(xVar).setBins(self.XBINNING)
            self.wsimport(data_obs, ROOT.RooFit.RecycleConflictNodes() )


    def addBackgroundModels(self, fixAfterControl=False, fixAfterFP=False, load=False, skipFit=False, **kwargs):
        workspace = self.buildWorkspace('bg')
        self.initializeWorkspace(workspace=workspace)
        super(HaaLimits2D, self).buildModel(region='control', workspace=workspace)
        self.loadBackgroundFit('control',workspace=workspace)
        if fixAfterControl:
            self.fix(workspace=workspace)
        vals = {}
        errs = {}
        integrals = {}
        allintegrals = {}
        errors = {}
        allparams = {}
        for region in self.REGIONS:
            vals[region] = {}
            errs[region] = {}
            integrals[region] = {}
            self.buildModel(region=region, workspace=workspace)
            for shift in ['']+self.BACKGROUNDSHIFTS:
                if shift=='':
                    if load:
                        v, e, i = self.loadBackgroundFit(region, workspace=workspace)
                    else:
                        v, e, i = self.fitBackground(region=region, workspace=workspace, **kwargs)
                    vals[region][shift] = v
                    errs[region][shift] = e
                    integrals[region][shift] = i
                else:
                    if load:
                        vUp, eUp, iUp = self.loadBackgroundFit(region,shift+'Up', workspace=workspace)
                        vDown, eDown, iDown = self.loadBackgroundFit(region,shift+'Down', workspace=workspace)
                    if not skipFit:
                        vUp, eUp, iUp = self.fitBackground(region=region, shift=shift+'Up', workspace=workspace, **kwargs)
                        vDown, eDown, iDown = self.fitBackground(region=region, shift=shift+'Down', workspace=workspace, **kwargs)
                    vals[region][shift+'Up'] = vUp
                    errs[region][shift+'Up'] = eUp
                    integrals[region][shift+'Up'] = iUp
                    vals[region][shift+'Down'] = vDown
                    errs[region][shift+'Down'] = eDown
                    integrals[region][shift+'Down'] = iDown

        for region in reversed(self.REGIONS):
            if load:
                allintegrals[region], errors[region] = self.loadComponentIntegrals(region)
            if not skipFit:
                allparams[region] = self.buildParams(region,vals,errs,integrals)
                allintegrals[region], errors[region] = self.buildComponentIntegrals(region,vals,errs,integrals, workspace.pdf('bg_{}_x'.format(region)))

        if fixAfterControl:
            self.fix(False, workspace=workspace)
        self.background_values = vals
        self.background_errors = errs
        self.background_integrals = integrals
        self.background_integralErrors = errors
        self.background_integralValues = allintegrals
        self.background_params = allparams

    def addSignalModels(self,yFitFuncFP="V", yFitFuncPP="V",isKinFit=False,**kwargs):
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
            if 'PP' in region:  yFitFunc=yFitFuncPP
            else: yFitFunc = yFitFuncFP
            for shift in ['']+self.SIGNALSHIFTS+self.QCDSHIFTS:
                if shift == '':
                    vals, errs, ints, fits = self.fitSignals(region=region,shift=shift,yFitFunc=yFitFunc,isKinFit=isKinFit,**kwargs)
                    values[region][shift] = vals
                    errors[region][shift] = errs
                    integrals[region][shift] = ints
                    fitFuncs[region][shift] = fits
                elif shift in self.QCDSHIFTS:
                    vals, errs, ints, fits = self.fitSignals(region=region,shift=shift,yFitFunc=yFitFunc,isKinFit=isKinFit,**kwargs)
                    values[region][shift] = vals
                    errors[region][shift] = errs
                    integrals[region][shift] = ints
                    fitFuncs[region][shift] = fits
                else:
                    valsUp, errsUp, intsUp, fitsUp = self.fitSignals(region=region,shift=shift+'Up',yFitFunc=yFitFunc,isKinFit=isKinFit,**kwargs)
                    valsDown, errsDown, intsDown, fitsDown = self.fitSignals(region=region,shift=shift+'Down',yFitFunc=yFitFunc,isKinFit=isKinFit,**kwargs)
                    values[region][shift+'Up'] = valsUp
                    errors[region][shift+'Up'] = errsUp
                    integrals[region][shift+'Up'] = intsUp
                    fitFuncs[region][shift+'Up'] = fitsUp
                    values[region][shift+'Down'] = valsDown
                    errors[region][shift+'Down'] = errsDown
                    integrals[region][shift+'Down'] = intsDown
                    fitFuncs[region][shift+'Down'] = fitsDown
            if self.QCDSHIFTS:
                values[region]['QCDscale_ggHUp']      = {}
                values[region]['QCDscale_ggHDown']    = {}
                errors[region]['QCDscale_ggHUp']      = {}
                errors[region]['QCDscale_ggHDown']    = {}
                integrals[region]['QCDscale_ggHUp']   = {}
                integrals[region]['QCDscale_ggHDown'] = {}
                fitFuncs[region]['QCDscale_ggHUp']    = {}
                fitFuncs[region]['QCDscale_ggHDown']  = {}
                for h in values[region]['']:
                    values[region]['QCDscale_ggHUp'][h]      = {}
                    values[region]['QCDscale_ggHDown'][h]    = {}
                    errors[region]['QCDscale_ggHUp'][h]      = {}
                    errors[region]['QCDscale_ggHDown'][h]    = {}
                    integrals[region]['QCDscale_ggHUp'][h]   = {}
                    integrals[region]['QCDscale_ggHDown'][h] = {}
                    fitFuncs[region]['QCDscale_ggHUp'][h]    = {}
                    fitFuncs[region]['QCDscale_ggHDown'][h]  = {}
                    for a in values[region][''][h]:
                        values[region]['QCDscale_ggHUp'][h][a]      = {}
                        values[region]['QCDscale_ggHDown'][h][a]    = {}
                        errors[region]['QCDscale_ggHUp'][h][a]      = {}
                        errors[region]['QCDscale_ggHDown'][h][a]    = {}
                        integrals[region]['QCDscale_ggHUp'  ][h][a] = max([integrals[region][shift][h][a] for shift in self.QCDSHIFTS])
                        integrals[region]['QCDscale_ggHDown'][h][a] = min([integrals[region][shift][h][a] for shift in self.QCDSHIFTS])
                        for val in values[region][''][h][a]:
                            values[region]['QCDscale_ggHUp'  ][h][a][val] = max([values[region][shift][h][a][val] for shift in self.QCDSHIFTS])
                            values[region]['QCDscale_ggHDown'][h][a][val] = min([values[region][shift][h][a][val] for shift in self.QCDSHIFTS])
                            errors[region]['QCDscale_ggHUp'  ][h][a][val] = max([errors[region][shift][h][a][val] for shift in self.QCDSHIFTS])
                            errors[region]['QCDscale_ggHDown'][h][a][val] = min([errors[region][shift][h][a][val] for shift in self.QCDSHIFTS])
                for shift in ['QCDscale_ggHUp','QCDscale_ggHDown']:
                    savedir = '{}/{}'.format(self.fitsDir,shift)
                    python_mkdir(savedir)
                    savename = '{}/{}_{}.json'.format(savedir,region,shift)
                    jsonData = {'vals': values[region][shift], 'errs': errors[region][shift], 'integrals': integrals[region][shift]}
                    self.dump(savename,jsonData)
                fitFuncs[region]['QCDscale_ggHUp']   = self.fitSignalParams(values[region]['QCDscale_ggHUp'],  errors[region]['QCDscale_ggHUp'],  integrals[region]['QCDscale_ggHUp'],  region,'QCDscale_ggHUp',yFitFunc=yFitFunc)
                fitFuncs[region]['QCDscale_ggHDown'] = self.fitSignalParams(values[region]['QCDscale_ggHDown'],errors[region]['QCDscale_ggHDown'],integrals[region]['QCDscale_ggHDown'],region,'QCDscale_ggHDown',yFitFunc=yFitFunc)
            if self.QCDSHIFTS:
                models[region] = self.buildSpline(values[region],errors[region],integrals[region],region,self.SIGNALSHIFTS+['QCDscale_ggH'],yFitFunc=yFitFunc,isKinFit=isKinFit,fitFuncs=fitFuncs[region],**kwargs)
            else:
                models[region] = self.buildSpline(values[region],errors[region],integrals[region],region,self.SIGNALSHIFTS,yFitFunc=yFitFunc,isKinFit=isKinFit,fitFuncs=fitFuncs[region],**kwargs)
        self.fitted_models = models

    ######################
    ### Setup datacard ###
    ######################
    def setupDatacard(self, addControl=False, doBinned=False):
        bgs = self.getComponentFractions(self.workspace.pdf('bg_{}_x'.format(self.REGIONS[0])))
        bgs = [b.rstrip('_x') for b in bgs]
        bgs = [b.rstrip('_'+self.REGIONS[0]) for b in bgs]
        sigs = [self.SPLINENAME.format(h=h) for h in self.HMASSES]
        self.bgs = bgs
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

        for region in self.REGIONS:
            for proc in sigs+bgs:
                if proc in bgs and doBinned: 
                    self.setExpected(proc,region,-1)
                    self.addShape(region,proc,'{}_{}_binned'.format(proc,region))
                    continue
                self.setExpected(proc,region,1)
                if proc not in sigs:
                    self.addRateParam('integral_{}_{}'.format(proc,region),region,proc)
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
                if proc not in sigs:
                    self.addShape(region,proc,'{}_{}_xy'.format(proc,region))
                
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
                #if 'cont' in proc:
                #self.addShape(region,proc,'{}_{}'.format(proc,region))

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
              "h200a5"  : { "mean_ttgaus": 3.01, "sigma_ttgaus": 1.00, "mu_ttland": 1.10, "sigma_ttland": 0.20},# Can Be improved 
              "h200a9"  : { "mean_ttgaus": 3.01, "sigma_ttgaus": 1.00, "mu_ttland": 1.10, "sigma_ttland": 0.20},# Can Be improved 
              "h200a15" : { "mean_ttgaus": 3.01, "sigma_ttgaus": 1.00, "mu_ttland": 1.10, "sigma_ttland": 0.20},# Can Be improved 
              "h250a5"  : { "mean_ttgaus": 3.01, "sigma_ttgaus": 1.00, "mu_ttland": 1.10, "sigma_ttland": 0.20},# Can Be improved 
              "h250a9"  : { "mean_ttgaus": 3.01, "sigma_ttgaus": 1.00, "mu_ttland": 1.10, "sigma_ttland": 0.20},# Can Be improved 
              "h250a15" : { "mean_ttgaus": 3.01, "sigma_ttgaus": 1.00, "mu_ttland": 1.10, "sigma_ttland": 0.20},# Can Be improved 
              "h300a5"  : { "mean_ttgaus": 3.01, "sigma_ttgaus": 1.00, "mu_ttland": 1.10, "sigma_ttland": 0.20},# Can Be improved 
              "h300a7"  : { "mean_ttgaus": 4.01, "sigma_ttgaus": 1.20, "mu_ttland": 1.40, "sigma_ttland": 0.20},# Can Be improved 
              "h300a9"  : { "mean_ttgaus": 5.42, "sigma_ttgaus": 1.51, "mu_ttland": 1.66, "sigma_ttland": 0.30},
              "h300a11" : { "mean_ttgaus": 6.61, "sigma_ttgaus": 2.03, "mu_ttland": 2.10, "sigma_ttland": 0.58},
              "h300a13" : { "mean_ttgaus": 7.87, "sigma_ttgaus": 2.26, "mu_ttland": 2.14, "sigma_ttland": 0.56},
              "h300a15" : { "mean_ttgaus": 8.96, "sigma_ttgaus": 2.56, "mu_ttland": 2.52, "sigma_ttland": 0.70},
              "h300a17" : { "mean_ttgaus": 10.2, "sigma_ttgaus": 2.93, "mu_ttland": 2.89, "sigma_ttland": 0.80},
              "h300a19" : { "mean_ttgaus": 11.4, "sigma_ttgaus": 3.31, "mu_ttland": 3.14, "sigma_ttland": 0.96},
              "h300a21" : { "mean_ttgaus": 12.6, "sigma_ttgaus": 3.54, "mu_ttland": 3.33, "sigma_ttland": 0.94},
              "h400a5"  : { "mean_ttgaus": 3.01, "sigma_ttgaus": 1.00, "mu_ttland": 1.10, "sigma_ttland": 0.20},# Can Be improved 
              "h400a9"  : { "mean_ttgaus": 3.01, "sigma_ttgaus": 1.00, "mu_ttland": 1.10, "sigma_ttland": 0.20},# Can Be improved 
              "h400a15" : { "mean_ttgaus": 3.01, "sigma_ttgaus": 1.00, "mu_ttland": 1.10, "sigma_ttland": 0.20},# Can Be improved 
              "h500a5"  : { "mean_ttgaus": 3.01, "sigma_ttgaus": 1.00, "mu_ttland": 1.10, "sigma_ttland": 0.20},# Can Be improved 
              "h500a9"  : { "mean_ttgaus": 3.01, "sigma_ttgaus": 1.00, "mu_ttland": 1.10, "sigma_ttland": 0.20},# Can Be improved 
              "h500a15" : { "mean_ttgaus": 3.01, "sigma_ttgaus": 1.00, "mu_ttland": 1.10, "sigma_ttland": 0.20},# Can Be improved 
              "h750a5"  : { "mean_ttgaus": 2.51, "sigma_ttgaus": 2.00, "mu_ttland": 1.87, "sigma_ttland": 0.35},# Can Be improved 
              "h750a7"  : { "mean_ttgaus": 3.01, "sigma_ttgaus": 2.00, "mu_ttland": 1.80, "sigma_ttland": 0.35},# Can Be improved 
              "h750a9"  : { "mean_ttgaus": 4.00, "sigma_ttgaus": 2.00, "mu_ttland": 1.90, "sigma_ttland": 0.35},# Can Be improved 
              "h750a11" : { "mean_ttgaus": 6.64, "sigma_ttgaus": 1.97, "mu_ttland": 1.78, "sigma_ttland": 0.41},
              "h750a13" : { "mean_ttgaus": 8.00, "sigma_ttgaus": 2.00, "mu_ttland": 2.00, "sigma_ttland": 0.50},
              "h750a15" : { "mean_ttgaus": 8.90, "sigma_ttgaus": 2.80, "mu_ttland": 2.20, "sigma_ttland": 0.60},
              "h750a17" : { "mean_ttgaus": 10.1, "sigma_ttgaus": 2.98, "mu_ttland": 2.30, "sigma_ttland": 0.63},
              "h750a19" : { "mean_ttgaus": 11.2, "sigma_ttgaus": 3.25, "mu_ttland": 2.39, "sigma_ttland": 0.67},
              "h750a21" : { "mean_ttgaus": 12.4, "sigma_ttgaus": 3.69, "mu_ttland": 2.70, "sigma_ttland": 0.83},
              "h1000a5" : { "mean_ttgaus": 8.90, "sigma_ttgaus": 2.80, "mu_ttland": 2.20, "sigma_ttland": 0.60},
              "h1000a9" : { "mean_ttgaus": 8.90, "sigma_ttgaus": 2.80, "mu_ttland": 2.20, "sigma_ttland": 0.60},
              "h1000a15": { "mean_ttgaus": 8.90, "sigma_ttgaus": 2.80, "mu_ttland": 2.20, "sigma_ttland": 0.60},
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
              "h200a5"  : { "mean_sigy": 2.21, "sigma_sigy": 0.58, "width_sigy": 0.50},
              "h200a9"  : { "mean_sigy": 2.21, "sigma_sigy": 0.58, "width_sigy": 0.50},
              "h200a15" : { "mean_sigy": 2.21, "sigma_sigy": 0.58, "width_sigy": 0.50},
              "h250a5"  : { "mean_sigy": 2.21, "sigma_sigy": 0.58, "width_sigy": 0.50},
              "h250a9"  : { "mean_sigy": 2.21, "sigma_sigy": 0.58, "width_sigy": 0.50},
              "h250a15" : { "mean_sigy": 2.21, "sigma_sigy": 0.58, "width_sigy": 0.50},
              "h300a5"  : { "mean_sigy": 2.21, "sigma_sigy": 0.58, "width_sigy": 0.50},
              "h300a7"  : { "mean_sigy": 3.07, "sigma_sigy": 1.06, "width_sigy": 0.40},
              "h300a9"  : { "mean_sigy": 3.99, "sigma_sigy": 1.50, "width_sigy": 0.50},
              "h300a11" : { "mean_sigy": 4.85, "sigma_sigy": 1.98, "width_sigy": 0.40},
              "h300a13" : { "mean_sigy": 5.86, "sigma_sigy": 2.30, "width_sigy": 0.40},
              "h300a15" : { "mean_sigy": 6.73, "sigma_sigy": 2.80, "width_sigy": 0.30},
              "h300a17" : { "mean_sigy": 7.68, "sigma_sigy": 3.10, "width_sigy": 0.30},
              "h300a19" : { "mean_sigy": 8.59, "sigma_sigy": 3.50, "width_sigy": 0.30},
              "h300a21" : { "mean_sigy": 9.33, "sigma_sigy": 3.80, "width_sigy": 0.40},
              "h400a5"  : { "mean_sigy": 2.21, "sigma_sigy": 0.58, "width_sigy": 0.50},
              "h400a9"  : { "mean_sigy": 2.21, "sigma_sigy": 0.58, "width_sigy": 0.50},
              "h400a15" : { "mean_sigy": 2.21, "sigma_sigy": 0.58, "width_sigy": 0.50},
              "h500a5"  : { "mean_sigy": 2.21, "sigma_sigy": 0.58, "width_sigy": 0.50},
              "h500a9"  : { "mean_sigy": 2.21, "sigma_sigy": 0.58, "width_sigy": 0.50},
              "h500a15" : { "mean_sigy": 2.21, "sigma_sigy": 0.58, "width_sigy": 0.50},
              "h750a5"  : { "mean_sigy": 2.10, "sigma_sigy": 0.50, "width_sigy": 0.80},
              "h750a7"  : { "mean_sigy": 2.90, "sigma_sigy": 1.00, "width_sigy": 0.80},
              "h750a9"  : { "mean_sigy": 3.80, "sigma_sigy": 1.50, "width_sigy": 0.80},
              "h750a11" : { "mean_sigy": 4.60, "sigma_sigy": 2.00, "width_sigy": 0.80},
              "h750a13" : { "mean_sigy": 5.40, "sigma_sigy": 2.40, "width_sigy": 0.60},
              "h750a15" : { "mean_sigy": 6.20, "sigma_sigy": 2.80, "width_sigy": 0.70},
              "h750a17" : { "mean_sigy": 7.10, "sigma_sigy": 3.10, "width_sigy": 0.80},
              "h750a19" : { "mean_sigy": 8.00, "sigma_sigy": 3.50, "width_sigy": 0.50},
              "h750a21" : { "mean_sigy": 8.80, "sigma_sigy": 4.00, "width_sigy": 0.80},
              "h1000a5" : { "mean_sigy": 2.10, "sigma_sigy": 0.50, "width_sigy": 0.80},
              "h1000a9" : { "mean_sigy": 2.10, "sigma_sigy": 0.50, "width_sigy": 0.80},
              "h1000a15": { "mean_sigy": 2.10, "sigma_sigy": 0.50, "width_sigy": 0.80},
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
              "750" : {"a1" : 3.0, "a2": 6.5, "n1": 18.0, "n2": 17.0, "sigma": 110.0},
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
              #"750" : {"a1" : 4.8, "a2": 5.00, "n1": 4.6, "n2": 16.0, "sigma": 109.0},
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
              "h750a21" : { "mean": 550},
            }
        return initialValues

    def GetInitialValuesDG(self, region="FP"):
        if 'PP' in region: 
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
                "h200a5"  : { "mean": 140, "sigma1": 27.0, "sigma2": 20.0},
                "h200a9"  : { "mean": 140, "sigma1": 26.2, "sigma2": 22.1},
                "h200a15" : { "mean": 140, "sigma1": 25.5, "sigma2": 22.9},
                "h250a5"  : { "mean": 140, "sigma1": 27.0, "sigma2": 20.0},
                "h250a9"  : { "mean": 140, "sigma1": 26.2, "sigma2": 22.1},
                "h250a15" : { "mean": 140, "sigma1": 25.5, "sigma2": 22.9},
                "h300a5"  : { "mean": 215, "sigma1": 44.4, "sigma2": 26.4},
                "h300a7"  : { "mean": 211, "sigma1": 44.7, "sigma2": 29.6},
                "h300a9"  : { "mean": 209, "sigma1": 49.0, "sigma2": 39.5},
                "h300a11" : { "mean": 208, "sigma1": 48.2, "sigma2": 30.8},
                "h300a13" : { "mean": 207, "sigma1": 49.5, "sigma2": 31.3},
                "h300a15" : { "mean": 207, "sigma1": 48.4, "sigma2": 31.3},
                "h300a17" : { "mean": 206, "sigma1": 47.0, "sigma2": 33.0},
                "h300a19" : { "mean": 206, "sigma1": 49.4, "sigma2": 31.9},
                "h300a21" : { "mean": 206, "sigma1": 50.3, "sigma2": 30.4},
                "h400a5"  : { "mean": 240, "sigma1": 67.0, "sigma2": 40.0},
                "h400a9"  : { "mean": 240, "sigma1": 66.2, "sigma2": 42.1},
                "h400a15" : { "mean": 240, "sigma1": 65.5, "sigma2": 42.9},
                "h500a5"  : { "mean": 340, "sigma1": 87.0, "sigma2": 50.0},
                "h500a9"  : { "mean": 340, "sigma1": 86.2, "sigma2": 52.1},
                "h500a15" : { "mean": 340, "sigma1": 85.5, "sigma2": 52.9},
                "h750a5"  : { "mean": 522, "sigma1": 121, "sigma2": 68},
                "h750a7"  : { "mean": 510, "sigma1": 130, "sigma2": 75},
                "h750a9"  : { "mean": 508, "sigma1": 133, "sigma2": 80},
                "h750a11" : { "mean": 505, "sigma1": 137, "sigma2": 80},
                "h750a13" : { "mean": 503, "sigma1": 138, "sigma2": 82},
                "h750a15" : { "mean": 501, "sigma1": 145, "sigma2": 80},
                "h750a17" : { "mean": 500, "sigma1": 149, "sigma2": 76},
                "h750a19" : { "mean": 500, "sigma1": 154, "sigma2": 73},
                "h750a21" : { "mean": 499, "sigma1": 153, "sigma2": 75},
                "h1000a5" : { "mean": 640, "sigma1": 157.0, "sigma2": 80.0},
                "h1000a9" : { "mean": 640, "sigma1": 156.2, "sigma2": 82.1},
                "h1000a15": { "mean": 640, "sigma1": 155.5, "sigma2": 82.9},
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
                "h200a5"  : { "mean": 140, "sigma1": 27.0, "sigma2": 20.0},
                "h200a9"  : { "mean": 140, "sigma1": 26.2, "sigma2": 22.1},
                "h200a15" : { "mean": 140, "sigma1": 25.5, "sigma2": 22.9},
                "h250a5"  : { "mean": 140, "sigma1": 27.0, "sigma2": 20.0},
                "h250a9"  : { "mean": 140, "sigma1": 26.2, "sigma2": 22.1},
                "h250a15" : { "mean": 140, "sigma1": 25.5, "sigma2": 22.9},
                "h300a5"  : { "mean": 215, "sigma1": 47.0, "sigma2": 27.7},
                "h300a7"  : { "mean": 211, "sigma1": 51.0, "sigma2": 27.0},
                "h300a9"  : { "mean": 210, "sigma1": 49.0, "sigma2": 29.0},
                "h300a11" : { "mean": 209, "sigma1": 50.0, "sigma2": 31.0},
                "h300a13" : { "mean": 210, "sigma1": 51.0, "sigma2": 30.8},
                "h300a15" : { "mean": 208, "sigma1": 55.0, "sigma2": 28.0},
                "h300a17" : { "mean": 210, "sigma1": 52.0, "sigma2": 30.0},
                "h300a19" : { "mean": 209, "sigma1": 53.0, "sigma2": 29.0},
                "h300a21" : { "mean": 207, "sigma1": 50.0, "sigma2": 32.0},
                "h400a5"  : { "mean": 240, "sigma1": 67.0, "sigma2": 40.0},
                "h400a9"  : { "mean": 240, "sigma1": 66.2, "sigma2": 42.1},
                "h400a15" : { "mean": 240, "sigma1": 65.5, "sigma2": 42.9},
                "h500a5"  : { "mean": 340, "sigma1": 87.0, "sigma2": 50.0},
                "h500a9"  : { "mean": 340, "sigma1": 86.2, "sigma2": 52.1},
                "h500a15" : { "mean": 340, "sigma1": 85.5, "sigma2": 52.9},
                "h750a5"  : { "mean": 511, "sigma1": 148, "sigma2": 65},
                "h750a7"  : { "mean": 507, "sigma1": 150, "sigma2": 69},
                "h750a9"  : { "mean": 504, "sigma1": 148, "sigma2": 73},
                "h750a11" : { "mean": 507, "sigma1": 146, "sigma2": 78},
                "h750a13" : { "mean": 505, "sigma1": 155, "sigma2": 70},
                "h750a15" : { "mean": 502, "sigma1": 154, "sigma2": 72},
                "h750a17" : { "mean": 500, "sigma1": 156, "sigma2": 74},
                "h750a19" : { "mean": 502, "sigma1": 150, "sigma2": 75},
                "h750a21" : { "mean": 500, "sigma1": 158, "sigma2": 74},
                "h1000a5" : { "mean": 640, "sigma1": 157.0, "sigma2": 80.0},
                "h1000a9" : { "mean": 640, "sigma1": 156.2, "sigma2": 82.1},
                "h1000a15": { "mean": 640, "sigma1": 155.5, "sigma2": 82.9},
            }

        return initialValues

    ###################
    ### Systematics ###
    ###################
    def addSystematics(self,doBinned=False,addControl=False):
        self.sigProcesses = tuple([self.SPLINENAME.format(h=h) for h in self.HMASSES])
        bgs = self.getComponentFractions(self.workspace.pdf('bg_{}_x'.format(self.REGIONS[0])))
        bgs = [b.rstrip('_{}_x'.format(self.REGIONS[0])) for b in bgs]
        self.bgProcesses = bgs
        self._addLumiSystematic()
        self._addMuonSystematic()
        #self._addTauSystematic()
        self._addShapeSystematic(doBinned=doBinned)
        #self._addComponentSystematic(addControl=addControl)
        self._addRelativeNormUnc()
        self._addHiggsSystematic()
        self._addAcceptanceSystematic()
        if not doBinned and not addControl: self._addControlSystematics()


    ###################################
    ### Save workspace and datacard ###
    ###################################
    def save(self,name='mmmt', subdirectory=''):
        processes = {}
        bgs = self.getComponentFractions(self.workspace.pdf('bg_{}_x'.format(self.REGIONS[0])))
        bgs = [b.rstrip('_x') for b in bgs]
        bgs = [b.rstrip('_'+self.REGIONS[0]) for b in bgs]
        if self.do2D:
            processes = [self.SPLINENAME] + bgs
        else:
            for h in self.HMASSES:
                processes[self.SIGNAME.format(h=h,a='X')] = [self.SPLINENAME.format(h=h)] + bgs
        if subdirectory == '':
            self.printCard('datacards_shape/MuMuTauTau/{}'.format(name),processes=processes,blind=False,saveWorkspace=True)
        else:
            self.printCard('datacards_shape/MuMuTauTau/' + subdirectory + '{}'.format(name),processes=processes,blind=False,saveWorkspace=True)

