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

import CombineLimitsRunII.Limits.Models as Models
from CombineLimitsRunII.Limits.Limits import Limits
from CombineLimitsRunII.HaaLimits.HaaLimitsNew import HaaLimits
from CombineLimitsRunII.Limits.utilities import *

import CombineLimitsRunII.Plotter.CMS_lumi as CMS_lumi
import CombineLimitsRunII.Plotter.tdrstyle as tdrstyle

tdrstyle.setTDRStyle()

class HaaLimits2D(HaaLimits):
    '''
    Create the Haa Limits workspace
    '''

    YRANGE = [50,1000]
    YBINNING = 950
    YLABEL = 'm_{#mu#mu#tau_{#mu}#tau_{h}}'
    YVAR = 'visFourbodyMass'
    YCORRELATION = False
    SPLITY = False
    DOUBLEEXPO = False
    NUMEXPO = 1

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

        resonances = []
        if self.XRANGE[0]<4:
            resonances += ['jpsi']
        if self.XRANGE[0] and self.XRANGE[1]>11:
            resonances += ['upsilon']
        continuums = ['cont1']
        if self.XRANGE[0]<4:
            continuums += ['cont2']

        if self.YRANGE[1]>100 and self.SPLITY:            
            erfs = {}
            conts = {}
            bgs = {}
            for rname in resonances+continuums:
                nameE = 'erf_{}{}'.format(rname,'_'+tag if tag else '')
                #print "JINGYU3:", rname, nameE, self.YCORRELATION
                if rname=='cont1' and self.YCORRELATION:
                    # build the correlation model for the y variable parameters
                    erfShiftName = kwargs.pop('erfShift_{}'.format(nameE),'erfShift_{}'.format(nameE))
                    erfShiftA0Name = 'erfShiftA0{}'.format('_'+tag if tag else '')
                    erfShiftA0 = kwargs.pop(erfShiftA0Name,[47,10,200])
                    if isinstance(erfShiftA0,str): erfShiftA0Name = erfShiftA0
                    erfShiftA1Name = 'erfShiftA1{}'.format('_'+tag if tag else '')
                    erfShiftA1 = kwargs.pop(erfShiftA1Name,[1.0])
                    if isinstance(erfShiftA1,str): erfShiftA1Name = erfShiftA1
                    erfShiftExpr = Models.Expression(erfShiftName,
                        expr = '{x}*{a1}+{a0}'.format(x=xVar,a0=erfShiftA0Name,a1=erfShiftA1Name),
                        variables = [xVar,erfShiftA1Name,erfShiftA0Name],
                        **{
                            xVar: xVar,
                            erfShiftA1Name: erfShiftA1,
                            erfShiftA0Name: erfShiftA0,
                        }
                    )
                    erfShiftExpr.build(workspace,erfShiftName)

                    erf = Models.Erf('erf1',
                        x = yVar,
                        #erfScale = erfScaleName,
                        erfScale = kwargs.pop('erfScale_{}'.format(nameE), [0.06,0,10]),
                        erfShift = erfShiftName,
                        #erfShift = kwargs.pop('erfShift_{}'.format(nameE), [65,10,200]),
                    )
                    erf.build(workspace,nameE)
                    erfs[rname] = erf
                else:
                    erf = Models.Erf('erf1',
                        x = yVar,
                        erfScale = kwargs.pop('erfScale_{}'.format(nameE), [0.05,0,10]),
                        erfShift = kwargs.pop('erfShift_{}'.format(nameE), [70,10,200]),
                    )
                    erf.build(workspace,nameE)
                    erfs[rname] = erf

                nameC = 'conty_{}{}'.format(rname,'_'+tag if tag else '')
                cont = Models.Exponential('conty',
                    x = yVar,
                    lamb = kwargs.pop('lambda_{}'.format(nameC), [-0.05,-1,0]),
                )
                cont.build(workspace,nameC)
                conts[rname] = cont

                bg = Models.Prod('bg',
                    nameE,
                    nameC,
                )
                name = 'bg_{}_{}'.format(rname,region)
                bg.build(workspace,name)
                bgs[rname] = bg

            return

                
        elif self.YRANGE[1]>100:
            nameE = 'erf{}'.format('_'+tag if tag else '')
            if not self.DOUBLEEXPO:
                if self.YCORRELATION:
                    # build the correlation model for the y variable parameters
                    erfShiftName = kwargs.pop('erfShift_{}'.format(nameE),'erfShift_{}'.format(nameE))
                    erfShiftA0Name = 'erfShiftA0{}'.format('_'+tag if tag else '')
                    erfShiftA0 = kwargs.pop(erfShiftA0Name,[47,10,200])
                    if isinstance(erfShiftA0,str): erfShiftA0Name = erfShiftA0
                    erfShiftA1Name = 'erfShiftA1{}'.format('_'+tag if tag else '')
                    #erfShiftA1 = kwargs.pop(erfShiftA1Name,[0.7,0,2])
                    erfShiftA1 = kwargs.pop(erfShiftA1Name,[1.0])
                    if isinstance(erfShiftA1,str): erfShiftA1Name = erfShiftA1
                    erfShiftExpr = Models.Expression(erfShiftName,
                        expr = '{x}*{a1}+{a0}'.format(x=xVar,a0=erfShiftA0Name,a1=erfShiftA1Name),
                        variables = [xVar,erfShiftA1Name,erfShiftA0Name],
                        **{
                            xVar: xVar,
                            erfShiftA1Name: erfShiftA1,
                            erfShiftA0Name: erfShiftA0,
                        }
                    )
                    erfShiftExpr.build(workspace,erfShiftName)

                    erf = Models.Erf('erf1',
                        x = yVar,
                        #erfScale = erfScaleName,
                        erfScale = kwargs.pop('erfScale_{}'.format(nameE), [0.06,0,10]),
                        erfShift = erfShiftName,
                        #erfShift = kwargs.pop('erfShift_{}'.format(nameE), [65,10,200]),
                    )
                    erf.build(workspace,nameE)

                else:
                    erf = Models.Erf('erf1',
                        x = yVar,
                        erfScale = kwargs.pop('erfScale_{}'.format(nameE), [0.05,0,10]),
                        erfShift = kwargs.pop('erfShift_{}'.format(nameE), [70,10,200]),
                    )
                    erf.build(workspace,nameE)
                    #print "JINGYU4: nameE", nameE

                nameC = 'conty{}'.format('_'+tag if tag else '')
                if self.YCORRELATION:
                    
                    cont = Models.Exponential('conty',
                        x = yVar,
                        #lamb = lambdaName,
                        lamb = kwargs.pop('lambda_{}'.format(nameC), [-0.025,-1,-0.001]),
                    )
                    cont.build(workspace,nameC)

                else:
                    cont = Models.Exponential('conty',
                        x = yVar,
                        lamb = kwargs.pop('lambda_{}'.format(nameC), [-0.05,-1,0]),
                    )
                    cont.build(workspace, nameC)
                    #print "JINGYU4: nameC", nameC

                bg = Models.Prod('bg',
                    nameE,
                    nameC,
                )

            if self.DOUBLEEXPO:
                # Double exponential
                nameE1 = 'erf1{}'.format('_'+tag if tag else '')
                erf1 = Models.Erf('erf1',
                    x = yVar,
                    erfScale = kwargs.pop('erfScale_{}'.format(nameE1), [0.05,0,10]),
                    erfShift = kwargs.pop('erfShift_{}'.format(nameE1), [70,10,200]),
                )
                erf1.build(workspace,nameE1)

                nameC1 = 'conty1{}'.format('_'+tag if tag else '')
                cont1 = Models.Exponential('conty1',
                    x = yVar,
                    lamb = kwargs.pop('lambda_{}'.format(nameC1), [-0.01,-0.2,0]),
                )
                cont1.build(workspace,nameC1)

                bg1 = Models.Prod('bg',
                    nameE1,
                    nameC1,
                )
                nameB1 = 'bg1{}'.format('_'+tag if tag else '')
                bg1.build(workspace,nameB1)

                nameE2 = 'erf2{}'.format('_'+tag if tag else '')
                erf2 = Models.Erf('erf2',
                    x = yVar,
                    #erfScale = kwargs.pop('erfScale_{}'.format(nameE2), [0.05,0,10]),
                    #erfShift = kwargs.pop('erfShift_{}'.format(nameE2), [70,10,200]),
                    erfScale = kwargs.pop('erfScale_{}'.format(nameE1),'erfScale_{}'.format(nameE1)),
                    erfShift = kwargs.pop('erfShift_{}'.format(nameE1),'erfShift_{}'.format(nameE1)),
                )
                erf2.build(workspace,nameE2)

                nameC2 = 'conty2{}'.format('_'+tag if tag else '')
                cont2 = Models.Exponential('conty2',
                    x = yVar,
                    lamb = kwargs.pop('lambda_{}'.format(nameC2), [-0.025,-0.2,0]),
                )
                cont2.build(workspace,nameC2)

                bg2 = Models.Prod('bg',
                    nameE2,
                    nameC2,
                )
                nameB2 = 'bg2{}'.format('_'+tag if tag else '')
                bg2.build(workspace,nameB2)

                bg = Models.Sum('bg',
                    **{
                        nameB1: [0.95,0,1],
                        nameB2: [0.05,0,1],
                    }
                )
        else:
            ## landua plus upsilon gaussian
            nameL1 = 'land1{}'.format('_'+tag if tag else '')

            bg = Models.Landau('land1',
                x = yVar,
                mu    = kwargs.pop('mu_{}'.format(nameL1), [1.5,0,5]),
                sigma = kwargs.pop('sigma_{}'.format(nameL1), [0.4,0,2]),
            )

        name = 'bg_{}'.format(region)
        bg.build(workspace,name)
        #print "JINGYU5:", bg, self.workspace.pdf('bg_PP_x')

    def _buildXModel(self,region,**kwargs):
        super(HaaLimits2D,self).buildModel(region,**kwargs)

    def buildModel(self,region,**kwargs):
        workspace = kwargs.pop('workspace',self.workspace)
        #tag = kwargs.pop('tag',region)
        
        # build the x variable
        self._buildXModel(region+'_x',workspace=workspace,**kwargs)

        # build the y variable
        self._buildYModel(region+'_y',workspace=workspace,**kwargs)

        xVar = kwargs.pop('xVar',self.XVAR)
        yVar = kwargs.pop('yVar',self.YVAR)

        doPoly = False
        doPolyExpo = False

        # the 2D model
        if self.SPLITY:
            if self.XRANGE[0]<4 and not (doPoly or doPolyExpo):
                if self.YCORRELATION:
                    cont1 = Models.Prod('cont1',
                        'bg_cont1_{}_y|{}'.format(region,xVar),
                        'cont1_{}_x'.format(region),
                    )
                else:
                    cont1 = Models.Prod('cont1',
                        'bg_cont1_{}_y'.format(region),
                        'cont1_{}_x'.format(region),
                    )
                nameC1 = 'cont1_{}_xy'.format(region)
                cont1.build(workspace,nameC1)

                cont2 = Models.Prod('cont2',
                    'bg_cont2_{}_y'.format(region),
                    'cont2_{}_x'.format(region),
                )
                nameC2 = 'cont2_{}_xy'.format(region)
                cont2.build(workspace,nameC2)
            else:
                if self.YCORRELATION:
                    cont1 = Models.Prod('cont1',
                        'bg_cont1_{}_y|{}'.format(region,xVar),
                        'cont1_{}_x'.format(region),
                    )
                else:
                    cont1 = Models.Prod('cont1',
                        'bg_cont1_{}_y'.format(region),
                        'cont1_{}_x'.format(region),
                    )
                nameC1 = 'cont1_{}_xy'.format(region)
                cont1.build(workspace,nameC1)

            jpsi1S = Models.Prod('jpsi1S',
                'bg_jpsi_{}_y'.format(region),
                'jpsi1S_{}_x'.format(region),
            )
            nameJ1 = 'jpsi1S_{}_xy'.format(region)
            jpsi1S.build(workspace,nameJ1)
  
            jpsi2S = Models.Prod('jpsi2S',
                'bg_jpsi_{}_y'.format(region),
                'jpsi2S_{}_x'.format(region),
            )
            nameJ2 = 'jpsi2S_{}_xy'.format(region)
            jpsi2S.build(workspace,nameJ2)

            upsilon1S = Models.Prod('upsilon1S',
                'bg_upsilon_{}_y'.format(region),
                'upsilon1S_{}_x'.format(region),
            )
            nameU1 = 'upsilon1S_{}_xy'.format(region)
            upsilon1S.build(workspace,nameU1)

            upsilon2S = Models.Prod('upsilon2S',
                'bg_upsilon_{}_y'.format(region),
                'upsilon2S_{}_x'.format(region),
            )
            nameU2 = 'upsilon2S_{}_xy'.format(region)
            upsilon2S.build(workspace,nameU2)

            upsilon3S = Models.Prod('upsilon3S',
                'bg_upsilon_{}_y'.format(region),
                'upsilon3S_{}_x'.format(region),
            )
            nameU3 = 'upsilon3S_{}_xy'.format(region)
            upsilon3S.build(workspace,nameU3)

            nameU23 = 'upsilon23_{}_xy'.format(region)
            workspace.factory('{0}_frac[{1},{2},{3}]'.format('upsilon2S',*[0.5,0,1]))
            workspace.factory('{0}_frac[{1},{2},{3}]'.format('upsilon3S',*[0.5,0,1]))
            upsilon23 = {'recursive': True}
            upsilon23[nameU2] = '{}_frac'.format('upsilon2S')
            upsilon23[nameU3] = '{}_frac'.format('upsilon3S')
            upsilon23 = Models.Sum(nameU23, **upsilon23)
            upsilon23.build(workspace,nameU23)

            nameU = 'upsilon_{}_xy'.format(region)
            workspace.factory('{0}_frac[{1},{2},{3}]'.format('upsilon1S',*[0.75,0,1]))
            workspace.factory('{0}_frac[{1},{2},{3}]'.format('upsilon23',*[0.5,0,1]))
            upsilon = {'recursive': True}
            upsilon[nameU1]  = '{}_frac'.format('upsilon1S')
            upsilon[nameU23] = '{}_frac'.format('upsilon23')
            upsilon = Models.Sum(nameU, **upsilon)
            upsilon.build(workspace,nameU)

            nameJ = 'jpsi_{}_xy'.format(region)
            workspace.factory('{0}_frac[{1},{2},{3}]'.format('jpsi1S',*[0.9,0,1]))
            workspace.factory('{0}_frac[{1},{2},{3}]'.format('jpsi2S',*[0.1,0,1]))
            jpsi = {'recursive': True}
            jpsi[nameJ1] = '{}_frac'.format('jpsi1S')
            jpsi[nameJ2] = '{}_frac'.format('jpsi2S')
            jpsi = Models.Sum('jpsi', **jpsi)
            jpsi.build(workspace,nameJ)

            if self.XRANGE[0]<4:
                nameC = 'cont_{}_xy'.format(region)
                #cont = {'extended': True}
                cont = {'recursive': True}
                cont[nameC1] = [0.75,0,1]
                cont[nameC2] = [0.5,0,1]
                cont = Models.Sum(nameC, **cont)
                cont.build(workspace,nameC)
            else:
                nameC = 'cont1_{}_xy'.format(region)

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
        elif self.YCORRELATION:
            if self.XRANGE[0]<4 and not (doPoly or doPolyExpo):
                cont1 = Models.Prod('cont1',
                    'bg_{}_y|{}'.format(region,xVar),
                    'cont1_{}_x'.format(region),
                )
                nameC1 = 'cont1_{}_xy'.format(region)
                cont1.build(workspace,nameC1)

                cont2 = Models.Prod('cont2',
                    'bg_{}_y|{}'.format(region,xVar),
                    'cont2_{}_x'.format(region),
                )
                nameC2 = 'cont2_{}_xy'.format(region)
                cont2.build(workspace,nameC2)
            else:
                cont1 = Models.Prod('cont1',
                    'bg_{}_y|{}'.format(region,xVar),
                    'cont1_{}_x'.format(region),
                )
                nameC1 = 'cont1_{}_xy'.format(region)
                cont1.build(workspace,nameC1)

            jpsi1S = Models.Prod('jpsi1S',
                'bg_{}_y|{}'.format(region,xVar),
                'jpsi1S_{}_x'.format(region),
            )
            nameJ1 = 'jpsi1S_{}_xy'.format(region)
            jpsi1S.build(workspace,nameJ1)
  
            jpsi2S = Models.Prod('jpsi2S',
                'bg_{}_y|{}'.format(region,xVar),
                'jpsi2S_{}_x'.format(region),
            )
            nameJ2 = 'jpsi2S_{}_xy'.format(region)
            jpsi2S.build(workspace,nameJ2)

            upsilon1S = Models.Prod('upsilon1S',
                'bg_{}_y|{}'.format(region,xVar),
                'upsilon1S_{}_x'.format(region),
            )
            nameU1 = 'upsilon1S_{}_xy'.format(region)
            upsilon1S.build(workspace,nameU1)

            upsilon2S = Models.Prod('upsilon2S',
                'bg_{}_y|{}'.format(region,xVar),
                'upsilon2S_{}_x'.format(region),
            )
            nameU2 = 'upsilon2S_{}_xy'.format(region)
            upsilon2S.build(workspace,nameU2)

            upsilon3S = Models.Prod('upsilon3S',
                'bg_{}_y|{}'.format(region,xVar),
                'upsilon3S_{}_x'.format(region),
            )
            nameU3 = 'upsilon3S_{}_xy'.format(region)
            upsilon3S.build(workspace,nameU3)

            bg = Models.Prod('bg',
                'bg_{}_y|{}'.format(region,xVar),
                'bg_{}_x'.format(region),
            )
        else:
            if self.XRANGE[0]<4 and not (doPoly or doPolyExpo):
                #print "JINGYU6:", "doPoly", doPoly, "doPolyExpo", doPolyExpo
                cont1 = Models.Prod('cont1',
                    'cont1_{}_x'.format(region),
                    'bg_{}_y'.format(region),
                )
                name = 'cont1_{}_xy'.format(region)
                cont1.build(workspace,name)

                #print "JINGYU6:", cont1, name

                cont2 = Models.Prod('cont2',
                    'cont2_{}_x'.format(region),
                    'bg_{}_y'.format(region),
                )
                name = 'cont2_{}_xy'.format(region)
                cont2.build(workspace,name)

                #print "JINGYU6:", cont2, name
            else:
                cont1 = Models.Prod('cont',
                    'cont1_{}_x'.format(region),
                    'bg_{}_y'.format(region),
                )
                name = 'cont1_{}_xy'.format(region)
                cont1.build(workspace,name)

            jpsi1S = Models.Prod('jpsi1S',
                'jpsi1S_{}_x'.format(region),
                'bg_{}_y'.format(region),
            )
            name = 'jpsi1S_{}_xy'.format(region)
            jpsi1S.build(workspace,name)
  
            jpsi2S = Models.Prod('jpsi2S',
                'jpsi2S_{}_x'.format(region),
                'bg_{}_y'.format(region),
            )
            name = 'jpsi2S_{}_xy'.format(region)
            jpsi2S.build(workspace,name)

            upsilon1S = Models.Prod('upsilon1S',
                'upsilon1S_{}_x'.format(region),
                'bg_{}_y'.format(region),
            )
            name = 'upsilon1S_{}_xy'.format(region)
            upsilon1S.build(workspace,name)

            upsilon2S = Models.Prod('upsilon2S',
                'upsilon2S_{}_x'.format(region),
                'bg_{}_y'.format(region),
            )
            name = 'upsilon2S_{}_xy'.format(region)
            upsilon2S.build(workspace,name)

            upsilon3S = Models.Prod('upsilon3S',
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
        tag = kwargs.get('tag','{}{}'.format(region,'_'+shift if shift else ''))


        histMap = self.histMap[region][shift]

        if self.YRANGE[1] > 100: 
            if yFitFunc == "DCB_Fix": initialMeans = self.GetInitialDCBMean()
            if "DCB" in yFitFunc: initialValuesDCB = self.GetInitialValuesDCB(isKinFit=isKinFit)
            elif yFitFunc == "DG": initialValuesDG = self.GetInitialValuesDG(region=region)
            elif yFitFunc == "L": initialValuesL = self.GetInitialValuesDitau(isLandau=True)
            elif yFitFunc == "V": initialValuesV = self.GetInitialValuesDitau(isLandau=False)
            elif yFitFunc == "BC": initialValuesBC =self.GetInitialValuesBC(region=region)
            elif yFitFunc == "DV": initialValuesDV =self.GetInitialValuesDV(region=region)

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
            mean  = [aval,0.9975*aval,1.0025*aval],#.9975,1.0025
            width = [0.0065*aval,0.001,1],#0.01*aval
            sigma = [0.0070*aval,0.001,1],#0.01*aval
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
                    mean    = [initialValuesDG["h"+str(h)+"a"+str(a)]["mean"],0.68*h,0.78*h],
                    sigma1  = [initialValuesDG["h"+str(h)+"a"+str(a)]["sigma1"],0.06*h,0.13*h],
                    sigma2  = [initialValuesDG["h"+str(h)+"a"+str(a)]["sigma2"],0.06*h,0.13*h],
                    yMax = self.YRANGE[1],
                )
            elif yFitFunc == "DV":
                modely = Models.DoubleSidedVoigtian('sigy',
                    x = self.YVAR,
                    # mean  = [0.7*h,0.64*h,0.76*h],
                    # sigma1 = [0.1*h,0.08*h,0.16*h],
                    # sigma2 = [0.125*h,0.09*h,0.18*h],
                    # width1 = [1.0,0.01,10.0],
                    # width2 = [1.0,0.01,10.0],
                    mean    = [initialValuesDV["h"+str(h)+"a"+str(a)]["mean"],0.68*h,0.76*h],
                    sigma1  = [initialValuesDV["h"+str(h)+"a"+str(a)]["sigma1"],0.06*h,0.16*h],
                    sigma2  = [initialValuesDV["h"+str(h)+"a"+str(a)]["sigma2"],0.06*h,0.14*h],
                    width1  = [initialValuesDV["h"+str(h)+"a"+str(a)]["width1"],0.01,10.0],
                    width2  = [initialValuesDV["h"+str(h)+"a"+str(a)]["width2"],0.01,10.0],
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
            elif yFitFunc == "BC":
                modely = Models.BetaConv('sigy',
                    x = self.YVAR,
                    betaScale = [initialValuesBC["h"+str(h)+"a"+str(a)]["betaScale"],0,1],
                    betaA =  [initialValuesBC["h"+str(h)+"a"+str(a)]["betaA"],0,20],
                    betaB = [initialValuesBC["h"+str(h)+"a"+str(a)]["betaB"],0,10],
                    mean = [initialValuesBC["h"+str(h)+"a"+str(a)]["mean"],0.6*h,h],
                    sigma = [initialValuesBC["h"+str(h)+"a"+str(a)]["sigma"],0,h],
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
        results, errors = model.fit2D(ws, hist, name, saveDir=saveDir, save=True, doErrors=True, xRange=[0.9*aval,1.1*aval])
        if self.binned:
            integral = histMap[self.SIGNAME.format(h=h,a=a)].Integral() * scale
            integralerr = getHistogram2DIntegralError(histMap[self.SIGNAME.format(h=h,a=a)]) * scale
        else:
            integral = histMap[self.SIGNAME.format(h=h,a=a)].sumEntries('{0}>{2} && {0}<{3} && {1}>{4} && {1}<{5}'.format(self.XVAR,self.YVAR,*self.XRANGE+self.YRANGE)) * scale
            integralerr = getDatasetIntegralError(histMap[self.SIGNAME.format(h=h,a=a)],'{0}>{2} && {0}<{3} && {1}>{4} && {1}<{5}'.format(self.XVAR,self.YVAR,*self.XRANGE+self.YRANGE)) * scale
            if integral!=integral:
                logging.error('Integral for spline is invalid: h{h} a{a} {region} {shift}'.format(h=h,a=a,region=region,shift=shift))
                raise
    
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

        fitFuncs = self.fitSignalParams(results,errors,integrals, integralerrs,region,shift,yFitFunc=yFitFunc)

        return results, errors, integrals, integralerrs, fitFuncs

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
        elif yFitFunc == "BC"  : yparams = ['betaScale_sigy','betaA_sigy','betaB_sigy','mean_sigy','sigma_sigy']
        elif yFitFunc == "errG": yparams = ['mean_ttgaus', 'sigma_ttgaus','erfShift_tterf','erfScale_tterf']
        elif yFitFunc == "L"   : yparams = ['mean_ttgaus', 'sigma_ttgaus','mu_ttland','sigma_ttland']
        elif yFitFunc == "G2"  : yparams = ['mean_g1', 'sigma_g1','mean_g2','sigma_g2','g1_frac']
        elif yFitFunc == "G3"  : yparams = ['mean_g1', 'sigma_g1','mean_g2','sigma_g2','mean_g3','sigma_g3','g1_frac','g2_frac']
        else: raise
        return xparams, yparams

    def fitSignalParams(self,results,errors,integrals,integralerrs,region,shift='',**kwargs):
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
                    #'integral'      : ROOT.TF1('integral_h{}_{}'.format(h,tag),  '[0]+TMath::Erf([1]+[2]*x)*TMath::Erfc([3]+[4]*x)', *self.ARANGE),
                    'integral'      : ROOT.TF1('integral_h{}_{}'.format(h,tag),  '[0]+[1]*x+[2]*x*x', *self.ARANGE),
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
                print "Here comes the integral"
                print zvals
                zerrs = [integralerrs[h][a] for h in Hs for a in As[h]]
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

            canvas.DrawFrame(self.ARANGE[0],min(zvals)*0.8,self.ARANGE[1],max(zvals)*1.2)
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


    def buildSpline(self,vals,errs,integrals,integralerrs,region,shifts=[],isKinFit=False,**kwargs):
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
        elif yFitFunc == "BC"  : ym = Models.BetaConv
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
                    **{self.rstrip(param,'_sigx'): '{param}_{splinename}_{region}'.format(param=param, splinename=self.SPLINENAME, region=region) for param in xparams}
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
                        **{self.rstrip(param,'_sigy'): '{param}_{splinename}_{region}'.format(param=param, splinename=self.SPLINENAME, region=region) for param in yparams}
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
                        **{self.rstrip(param,'_sigx'): '{param}_{splinename}_{region}'.format(param=param, splinename=self.SPLINENAME.format(h=h), region=region) for param in xparams}
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
                            **{self.rstrip(param,'_sigy'): '{param}_{splinename}_{region}'.format(param=param, splinename=self.SPLINENAME.format(h=h), region=region) for param in yparams}
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
                **{self.rstrip(param,'_sigx'): '{param}_{region}'.format(param=param, region=region) for param in xparams}
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
                    **{self.rstrip(param,'_sigy'): '{param}_{region}'.format(param=param, region=region) for param in yparams}
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
                    **{self.rstrip(param,'_sigx'): '{param}_h{h}_{region}'.format(param=param, h=h, region=region) for param in xparams}
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
                        **{self.rstrip(param,'_sigy'): '{param}_h{h}_{region}'.format(param=param, h=h, region=region) for param in yparams}
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
        print "Adding control region models..."
        region = 'control'
        workspace = self.buildWorkspace('control')
        self.initializeWorkspace(workspace=workspace)
        print workspace.Print("V")
        
        super(HaaLimits2D, self).buildModel(region=region, workspace=workspace)
        
        if load:
            vals, errs, ints, interrs = self.loadBackgroundFit(region,workspace=workspace)
        if not skipFit:
            vals, errs, ints, interrs = self.fitBackground(region=region, workspace=workspace)
            
        if load:
            allintegrals, errors = self.loadComponentIntegrals(region)
        if not skipFit:
            allintegrals, errors = self.buildComponentIntegrals(region,vals,errs,ints,interrs, workspace.pdf('bg_control'))

        print workspace.Print("V")

        self.control_vals = vals
        #print "control_vals", vals
        self.control_errs = errs
        #print "control_errs", errs
        self.control_integrals = ints
        #print "control_integrals", ints
        self.control_integralerrs = interrs
        #print "control_integralerrs", interrs
        self.control_integralErrors = errors
        #print "control_integralErrors", errors
        self.control_integralValues = allintegrals
        #print "control_integralValues", allintegrals
        

    def plotModelY(self,workspace,yVar,data,model,region,shift='',**kwargs):
        yRange = kwargs.pop('yRange',[])
        postfix = kwargs.pop('postfix','')

        if yRange:
            yFrame = workspace.var(yVar).frame(ROOT.RooFit.Range(*yRange))
        else:
            yFrame = workspace.var(yVar).frame()
        data.plotOn(yFrame)
        if not self.SKIPPLOTS:
            # continuum
            model.plotOn(yFrame,ROOT.RooFit.Components('conty_{}_y'.format(region)),ROOT.RooFit.LineStyle(ROOT.kDashed))
            #model.plotOn(yFrame,ROOT.RooFit.Components('conty1_{}_y'.format(region)),ROOT.RooFit.LineStyle(ROOT.kDashed))
            #model.plotOn(yFrame,ROOT.RooFit.Components('conty2_{}_y'.format(region)),ROOT.RooFit.LineStyle(ROOT.kDashed))
            #model.plotOn(yFrame,ROOT.RooFit.Components('conty3_{}_y'.format(region)),ROOT.RooFit.LineStyle(ROOT.kDashed))
            #model.plotOn(yFrame,ROOT.RooFit.Components('conty4_{}_y'.format(region)),ROOT.RooFit.LineStyle(ROOT.kDashed))
            # combined model
            model.plotOn(yFrame)
        model.paramOn(yFrame,ROOT.RooFit.Layout(0.72,0.98,0.90))

        if not self.SKIPPLOTS:
            resid = yFrame.residHist()
            pull = yFrame.pullHist()

        if yRange:
            yFrame2 = workspace.var(yVar).frame(ROOT.RooFit.Range(*yRange))
        else:
            yFrame2 = workspace.var(yVar).frame()
        if not self.SKIPPLOTS: yFrame2.addPlotable(pull,'P')

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
        ratiopad.SetTopMargin(0.00)
        ratiopad.SetRightMargin(0.2)
        ratiopad.SetBottomMargin(0.5)
        ratiopad.SetLeftMargin(0.16)
        ratiopad.SetTickx(1)
        ratiopad.SetTicky(1)
        ratiopad.Draw()
        if plotpad != ROOT.TVirtualPad.Pad(): plotpad.cd()
        yFrame.Draw()
        #prims = canvas.GetListOfPrimitives()
        prims = plotpad.GetListOfPrimitives()
        for prim in prims:
            if 'paramBox' in prim.GetName():
                prim.SetTextSize(0.02)
        mi = yFrame.GetMinimum()
        ma = yFrame.GetMaximum()
        if mi<0:
            yFrame.SetMinimum(0.1)
        ratiopad.cd()
        yFrame2.Draw()
        prims = ratiopad.GetListOfPrimitives()
        for prim in prims:
            if 'frame' in prim.GetName():
                prim.GetXaxis().SetLabelSize(0.09)
                prim.GetXaxis().SetTitleSize(0.21)
                prim.GetXaxis().SetTitleOffset(1.0)
                prim.GetXaxis().SetLabelOffset(0.03)
                prim.GetYaxis().SetLabelSize(0.09)
                prim.GetYaxis().SetLabelOffset(0.006)
                prim.GetYaxis().SetTitleSize(0.21)
                prim.GetYaxis().SetTitleOffset(0.35)
                prim.GetYaxis().SetNdivisions(505)
                prim.GetYaxis().SetTitle('Pull')
                prim.GetYaxis().SetRangeUser(-5,5)
                continue
        canvas.cd()
        python_mkdir(self.plotDir)
        canvas.Print('{}/model_fit_{}{}{}.png'.format(self.plotDir,region,'_'+shift if shift else '','_'+postfix if postfix else ''))
        if mi<0:
            yFrame.SetMinimum(0.1)
        #canvas.SetLogy(True)
        plotpad.SetLogy(True)
        canvas.Print('{}/model_fit_{}{}{}_log.png'.format(self.plotDir,region,'_'+shift if shift else '','_'+postfix if postfix else ''))

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
            integralerr = getHistogramIntegralError(hist) * scale
            data = ROOT.RooDataHist(name,name,ROOT.RooArgList(workspace.var(xVar),workspace.var(yVar)),hist)
        else:
            data = hist.Clone(name)
            integral = hist.sumEntries('{0}>{2} && {0}<{3} && {1}>{4} && {1}<{5}'.format(xVar,yVar,*self.XRANGE+self.YRANGE)) * scale
            integralerr = getDatasetIntegralError(hist,'{0}>{2} && {0}<{3} && {1}>{4} && {1}<{5}'.format(xVar,yVar,*self.XRANGE+self.YRANGE)) * scale

        fr = model.fitTo(data,ROOT.RooFit.Save(),ROOT.RooFit.SumW2Error(True), ROOT.RooFit.PrintLevel(-1))

        workspace.var(xVar).setBins(self.XBINNING)
        workspace.var(yVar).setBins(self.YBINNING)

        self.plotModelX(workspace,xVar,data,model,region,shift,postfix='xproj')
        if region=='control':
            self.plotModelX(workspace,xVar,data,model,region,shift,xRange=[2.5,5],postfix='xproj_jpsi')
            self.plotModelX(workspace,xVar,data,model,region,shift,xRange=[8,12],postfix='xproj_upsilon')

        self.plotModelY(workspace,yVar,data,model,region,shift,postfix='yproj')

        pars = fr.floatParsFinal()
        vals = {}
        errs = {}
        for p in range(pars.getSize()):
            vals[pars.at(p).GetName()] = pars.at(p).getValV()
            errs[pars.at(p).GetName()] = pars.at(p).getError()

        python_mkdir(self.fitsDir)
        jfile = '{}/background_{}{}.json'.format(self.fitsDir,region,'_'+shift if shift else '')
        results = {'vals':vals, 'errs':errs, 'integral':integral, 'integralerr':integralerr}
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
        super(HaaLimits2D, self).buildModel(region=region, workspace=self.workspace, xVar=xVar)
        self.loadBackgroundFit(region, workspace=self.workspace)

        #name = 'data_obs_{}'.format(region)
        name = 'data_obs'
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
        #print self.REGIONS

        for channel in self.CHANNELS:
            for region in self.REGIONS:
                xVar = self.XVAR
                yVar = self.YVAR
    
                region = channel+'_'+region
    
                # build the models after doing the prefit stuff
                prebuiltParams = {p:p for p in self.background_params[region]}
                self.addVar(xVar, *self.XRANGE, unit='GeV', label=self.XLABEL, workspace=workspace)
                self.addVar(yVar, *self.YRANGE, unit='GeV', label=self.XLABEL, workspace=workspace)
                self.buildModel(region=region,workspace=workspace,xVar=xVar,yVar=yVar,**prebuiltParams)
                self.fixXLambda(workspace=self.workspace)
                self.fixCorrelation(workspace=self.workspace)
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
            #namehist = 'data_obs_{}'.format(region)
            name = 'data_obs'
            hist = self.histMap[region]['']['data']
            if hist.InheritsFrom('TH1'):
                data_obs = ROOT.RooDataHist(name,name,ROOT.RooArgList(self.workspace.var(xVar)),hist)
            else:
                data_obs = hist.Clone(name)
                data_obs.get().find(xVar).setBins(self.XBINNING)
            self.wsimport(data_obs, ROOT.RooFit.RecycleConflictNodes() )


    def addBackgroundModels(self, fixAfterControl=False, fixAfterFP=False, load=False, skipFit=False, **kwargs):
        print "Adding background models..."
        workspace = self.buildWorkspace('bg')
        self.initializeWorkspace(workspace=workspace)
        super(HaaLimits2D, self).buildModel(region='control', workspace=workspace)
        self.loadBackgroundFit('control',workspace=workspace)
        if fixAfterControl:
            self.fix(workspace=workspace)
        vals = {}
        errs = {}
        integrals = {}
        integralerrs = {}
        allintegrals = {}
        errors = {}
        allparams = {}
        for channel in self.CHANNELS:
            for region in self.REGIONS:
                region=channel+'_'+region
                vals[region] = {}
                errs[region] = {}
                integrals[region] = {}
                integralerrs[region] = {}
                self.buildModel(region=region,workspace=workspace)
                self.fixXLambda(workspace=workspace)
                self.fixCorrelation(workspace=self.workspace)
                for shift in ['']+self.BACKGROUNDSHIFTS:
                    if shift=='':
                        if load:
                            v, e, i, ie = self.loadBackgroundFit(region, workspace=workspace)
                        else:
                            v, e, i, ie = self.fitBackground(region=region, workspace=workspace, **kwargs)
                        vals[region][shift] = v
                        errs[region][shift] = e
                        integrals[region][shift] = i
                        integralerrs[region][shift] = ie
                    else:
                        if load:
                            vUp, eUp, iUp, ieUp = self.loadBackgroundFit(region,shift+'Up', workspace=workspace)
                            vDown, eDown, iDown, ieDown = self.loadBackgroundFit(region,shift+'Down', workspace=workspace)
                        if not skipFit:
                            vUp, eUp, iUp, ieUp = self.fitBackground(region=region, shift=shift+'Up', workspace=workspace, **kwargs)
                            vDown, eDown, iDown, ieDown = self.fitBackground(region=region, shift=shift+'Down', workspace=workspace, **kwargs)
                        vals[region][shift+'Up'] = vUp
                        errs[region][shift+'Up'] = eUp
                        integrals[region][shift+'Up'] = iUp
                        integralerrs[region][shift+'Up'] = ieUp
                        vals[region][shift+'Down'] = vDown
                        errs[region][shift+'Down'] = eDown
                        integrals[region][shift+'Down'] = iDown
                        integralerrs[region][shift+'Down'] = ieDown

        print workspace.Print("V")
        
        for channel in self.CHANNELS:
            for region in reversed(self.REGIONS):
                region=channel+'_'+region
                if load:
                    allintegrals[region], errors[region] = self.loadComponentIntegrals(region)
                if not skipFit:
                    allparams[region] = self.buildParams(region,vals,errs,integrals,integralerrs)
                    allintegrals[region], errors[region] = self.buildComponentIntegrals(region,vals,errs,integrals,integralerrs, workspace.pdf('bg_{}_x'.format(region)))

        if fixAfterControl:
            self.fix(False, workspace=workspace)
        self.background_values = vals
        #print "background_values:", vals
        self.background_errors = errs
        #print "background_errs:", errs
        self.background_integrals = integrals
        self.background_integralerrs = integralerrs
        self.background_integralErrors = errors
        self.background_integralValues = allintegrals
        self.background_params = allparams

    def addSignalModels(self,yFitFuncFP="V", yFitFuncPP="V",isKinFit=False,**kwargs):
        models = {}
        values = {}
        errors = {}
        integrals = {}
        integralerrs = {}
        fitFuncs = {}
        for channel in self.CHANNELS:
            for region in self.REGIONS:
                region = channel+'_'+region
                models[region] = {}
                values[region] = {}
                errors[region] = {}
                integrals[region] = {}
                integralerrs[region] = {}
                fitFuncs[region] = {}
                if 'PP' in region:  yFitFunc=yFitFuncPP
                else: yFitFunc = yFitFuncFP
                for shift in ['']+self.SIGNALSHIFTS+self.QCDSHIFTS:
                    if shift == '':
                        #print self.histMap
                        vals, errs, ints, interrs, fits = self.fitSignals(region=region,shift=shift,yFitFunc=yFitFunc,isKinFit=isKinFit,**kwargs)
                        values[region][shift] = vals
                        errors[region][shift] = errs
                        integrals[region][shift] = ints
                        integralerrs[region][shift] = interrs
                        fitFuncs[region][shift] = fits
                    elif shift in self.QCDSHIFTS:
                        vals, errs, ints, interrs, fits = self.fitSignals(region=region,shift=shift,yFitFunc=yFitFunc,isKinFit=isKinFit,**kwargs)
                        values[region][shift] = vals
                        errors[region][shift] = errs
                        integrals[region][shift] = ints
                        integralerrs[region][shift] = interrs
                        fitFuncs[region][shift] = fits
                    else:
                        valsUp, errsUp, intsUp, interrsUp, fitsUp = self.fitSignals(region=region,shift=shift+'Up',yFitFunc=yFitFunc,isKinFit=isKinFit,**kwargs)
                        valsDown, errsDown, intsDown, interrsDown, fitsDown = self.fitSignals(region=region,shift=shift+'Down',yFitFunc=yFitFunc,isKinFit=isKinFit,**kwargs)
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
                if self.QCDSHIFTS:
                    values[region]['QCDscale_ggHUp']      = {}
                    values[region]['QCDscale_ggHDown']    = {}
                    errors[region]['QCDscale_ggHUp']      = {}
                    errors[region]['QCDscale_ggHDown']    = {}
                    integrals[region]['QCDscale_ggHUp']   = {}
                    integrals[region]['QCDscale_ggHDown'] = {}
                    integralerrs[region]['QCDscale_ggHUp']   = {}
                    integralerrs[region]['QCDscale_ggHDown'] = {}
                    fitFuncs[region]['QCDscale_ggHUp']    = {}
                    fitFuncs[region]['QCDscale_ggHDown']  = {}
                    for h in values[region]['']:
                        values[region]['QCDscale_ggHUp'][h]      = {}
                        values[region]['QCDscale_ggHDown'][h]    = {}
                        errors[region]['QCDscale_ggHUp'][h]      = {}
                        errors[region]['QCDscale_ggHDown'][h]    = {}
                        integrals[region]['QCDscale_ggHUp'][h]   = {}
                        integrals[region]['QCDscale_ggHDown'][h] = {}
                        integralerrs[region]['QCDscale_ggHUp'][h]   = {}
                        integralerrs[region]['QCDscale_ggHDown'][h] = {}
                        fitFuncs[region]['QCDscale_ggHUp'][h]    = {}
                        fitFuncs[region]['QCDscale_ggHDown'][h]  = {}
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
                                values[region]['QCDscale_ggHUp'  ][h][a][val] = max([values[region][shift][h][a][val] for shift in self.QCDSHIFTS])
                                values[region]['QCDscale_ggHDown'][h][a][val] = min([values[region][shift][h][a][val] for shift in self.QCDSHIFTS])
                                errors[region]['QCDscale_ggHUp'  ][h][a][val] = max([errors[region][shift][h][a][val] for shift in self.QCDSHIFTS])
                                errors[region]['QCDscale_ggHDown'][h][a][val] = min([errors[region][shift][h][a][val] for shift in self.QCDSHIFTS])
                    for shift in ['QCDscale_ggHUp','QCDscale_ggHDown']:
                        savedir = '{}/{}'.format(self.fitsDir,shift)
                        python_mkdir(savedir)
                        savename = '{}/{}_{}.json'.format(savedir,region,shift)
                        jsonData = {'vals': values[region][shift], 'errs': errors[region][shift], 'integrals': integrals[region][shift], 'integralerrs': integralerrs[region][shift]}
                        self.dump(savename,jsonData)
                    fitFuncs[region]['QCDscale_ggHUp']   = self.fitSignalParams(values[region]['QCDscale_ggHUp'],  errors[region]['QCDscale_ggHUp'],  integrals[region]['QCDscale_ggHUp'],  integralerrs[region]['QCDscale_ggHUp'],  region,'QCDscale_ggHUp',yFitFunc=yFitFunc)
                    fitFuncs[region]['QCDscale_ggHDown'] = self.fitSignalParams(values[region]['QCDscale_ggHDown'],errors[region]['QCDscale_ggHDown'],integrals[region]['QCDscale_ggHDown'],integralerrs[region]['QCDscale_ggHDown'],region,'QCDscale_ggHDown',yFitFunc=yFitFunc)
                if self.QCDSHIFTS:
                    models[region] = self.buildSpline(values[region],errors[region],integrals[region],integralerrs[region],region,self.SIGNALSHIFTS+['QCDscale_ggH'],yFitFunc=yFitFunc,isKinFit=isKinFit,fitFuncs=fitFuncs[region],**kwargs)
                else:
                    models[region] = self.buildSpline(values[region],errors[region],integrals[region],integralerrs[region],region,self.SIGNALSHIFTS,yFitFunc=yFitFunc,isKinFit=isKinFit,fitFuncs=fitFuncs[region],**kwargs)
        self.fitted_models = models

    ######################
    ### Setup datacard ###
    ######################
    def setupDatacard(self, addControl=False, doBinned=False):

        print "Setting up datacard..."
        #for channel in self.CHANNELS:
        bgs = self.getComponentFractions(self.workspace.pdf('bg_{}_x'.format(self.CHANNELS[0]+'_'+self.REGIONS[0])))
            #bgs_tmp = [self.getComponentFractions(self.workspace.pdf('bg_{}_x'.format(c+'_'+self.REGIONS[0])))for c in self.CHANNELS]
            #bgs=bgs_tmp[0]
            #while len(bgs_tmp) > 1:
            #    bgs.update(bgs_tmp[1])
            #    bgs_tmp.pop(1)
            #print "bgs:", bgs
        bgs = [self.rstrip(b,'_x') for b in bgs]
        bgs = [self.rstrip(b,'_'+self.REGIONS[0]) for b in bgs]
        bgs = [self.rstrip(b,'_'+self.CHANNELS[0]) for b in bgs]
        sigs = [self.SPLINENAME.format(h=h) for h in self.HMASSES]
        self.bgs = bgs
        self.sigs = sigs

        self.setChannels(self.CHANNELS)

        for channel in self.CHANNELS:
            # setup bins
            for region in self.REGIONS:
                region = channel+'_'+region
                self.addBin(region)
                print "Adding bin", region

        # add processes
        for proc in bgs:
            #if proc.split('_')[1] == region.split('_')[0]:
            self.addProcess(proc)
            print "Adding process", proc

        for proc in sigs:
            #proc = proc+'_'+channel
            self.addProcess(proc,signal=True)
            print "Adding process", proc
    
        for channel in self.CHANNELS:
            for region in self.REGIONS:
                for proc in sigs+bgs:
                    regionText = channel+'_'+region
                    proc = proc+'_'+regionText
                    #print regionText, proc, region
                    #print regionText, proc
                    #if not 'haa' in proc or not regionText.split('_')[1] == proc.split('_')[0]: continue
                    self.setExpected(proc,regionText,1)
                    if proc not in sigs:
                        if not 'haa' in proc: 
                            self.addRateParam('integral_{}'.format(proc),regionText,proc)
                    if 'haa' in proc:
                        print "Adding shape", regionText,proc,'{}'.format(proc)
                        self.addShape(regionText,proc,'{}'.format(proc))
                    else:
                        print "Adding shape", regionText,proc,'{}_xy'.format(proc)
                        self.addShape(regionText,proc,'{}_xy'.format(proc))
                self.setObserved(regionText,-1) # reads from histogram

        self.addCrossSection()
        
        if addControl:
            region = 'control'
            print "Adding control", addControl

            self.addBin(region)

            for proc in bgs:
                #key = proc if proc in self.control_integralValues else '{}_{}'.format(proc,region)
                #integral = self.control_integralValues[key]
                #self.setExpected(proc,region,integral)
                #proc = proc.split('_')[0]
                #print "DEBUG0:", proc, region
                self.setExpected(proc+'_control',region,1)
                self.addRateParam('integral_{}_{}'.format(proc,region),region,proc+'_control')
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
              "h125a8"  : { "mean_ttgaus": 0.01, "sigma_ttgaus": 2.22, "mu_ttland": 6.50, "sigma_ttland": 1.70},#Rough
              "h125a9"  : { "mean_ttgaus": 5.60, "sigma_ttgaus": 1.46, "mu_ttland": 1.80, "sigma_ttland": 0.45},
              "h125a10" : { "mean_ttgaus": 5.70, "sigma_ttgaus": 1.76, "mu_ttland": 1.95, "sigma_ttland": 0.55},#Rough
              "h125a11" : { "mean_ttgaus": 6.83, "sigma_ttgaus": 1.82, "mu_ttland": 2.35, "sigma_ttland": 0.67},
              "h125a12" : { "mean_ttgaus": 6.93, "sigma_ttgaus": 1.92, "mu_ttland": 2.45, "sigma_ttland": 0.77},#Rough
              "h125a13" : { "mean_ttgaus": 7.97, "sigma_ttgaus": 2.17, "mu_ttland": 2.90, "sigma_ttland": 0.90},
              "h125a14" : { "mean_ttgaus": 8.17, "sigma_ttgaus": 2.27, "mu_ttland": 3.20, "sigma_ttland": 1.05},#Rough
              "h125a15" : { "mean_ttgaus": 8.99, "sigma_ttgaus": 2.59, "mu_ttland": 3.60, "sigma_ttland": 1.20},
              "h125a17" : { "mean_ttgaus": 9.90, "sigma_ttgaus": 2.90, "mu_ttland": 4.40, "sigma_ttland": 1.60},
              "h125a18" : { "mean_ttgaus": 10.2, "sigma_ttgaus": 3.20, "mu_ttland": 5.20, "sigma_ttland": 1.80},#Rough
              "h125a19" : { "mean_ttgaus": 11.0, "sigma_ttgaus": 3.80, "mu_ttland": 6.00, "sigma_ttland": 2.00},
              "h125a20" : { "mean_ttgaus": 11.5, "sigma_ttgaus": 3.80, "mu_ttland": 6.00, "sigma_ttland": 1.99},#Rough
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
              "h125a8"  : { "mean_sigy": 4.31, "sigma_sigy": 1.21, "width_sigy": 0.34},#Rough
              "h125a9"  : { "mean_sigy": 4.52, "sigma_sigy": 1.49, "width_sigy": 0.40},
              "h125a10" : { "mean_sigy": 4.65, "sigma_sigy": 1.59, "width_sigy": 0.45},#Rough
              "h125a11" : { "mean_sigy": 5.50, "sigma_sigy": 1.89, "width_sigy": 0.10},
              "h125a12" : { "mean_sigy": 5.60, "sigma_sigy": 1.99, "width_sigy": 0.13},#Rough
              "h125a13" : { "mean_sigy": 6.65, "sigma_sigy": 2.23, "width_sigy": 0.10},
              "h125a14" : { "mean_sigy": 6.75, "sigma_sigy": 2.33, "width_sigy": 0.15},#Rough
              "h125a15" : { "mean_sigy": 7.53, "sigma_sigy": 2.44, "width_sigy": 0.20},
              "h125a17" : { "mean_sigy": 8.51, "sigma_sigy": 3.16, "width_sigy": 0.10},
              "h125a18" : { "mean_sigy": 8.61, "sigma_sigy": 3.26, "width_sigy": 0.15},#Rough
              "h125a19" : { "mean_sigy": 8.78, "sigma_sigy": 3.35, "width_sigy": 0.01},
              "h125a20" : { "mean_sigy": 8.98, "sigma_sigy": 3.55, "width_sigy": 0.01},#Rough 
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
              "h125a8"  : { "a1": 5.1, "a2": 1.65, "n1": 3.5, "n2": 3.6, "sigma": 14.19},#Rough
              "h125a9"  : { "a1": 5.2, "a2": 1.07, "n1": 2.8, "n2": 9.0, "sigma": 10.58},
              "h125a10" : { "a1": 5.1, "a2": 1.17, "n1": 2.9, "n2": 9.2, "sigma": 10.48},#Rough
              "h125a11" : { "a1": 1.8, "a2": 1.55, "n1": 6.0, "n2": 4.1, "sigma": 9.770},
              "h125a12" : { "a1": 1.9, "a2": 1.65, "n1": 6.0, "n2": 4.2, "sigma": 9.980},#Rough
              "h125a13" : { "a1": 2.0, "a2": 2.66, "n1": 6.0, "n2": 1.4, "sigma": 10.04},
              "h125a14" : { "a1": 2.0, "a2": 2.77, "n1": 6.0, "n2": 1.5, "sigma": 10.14},#Rough
              "h125a15" : { "a1": 1.3, "a2": 2.19, "n1": 6.0, "n2": 1.9, "sigma": 7.840},
              "h125a17" : { "a1": 1.5, "a2": 2.08, "n1": 6.0, "n2": 1.8, "sigma": 6.990},
              "h125a18" : { "a1": 1.5, "a2": 2.06, "n1": 6.0, "n2": 1.8, "sigma": 6.770},#Rough
              "h125a19" : { "a1": 1.6, "a2": 3.34, "n1": 6.0, "n2": 0.6, "sigma": 6.220},
              "h125a20" : { "a1": 1.6, "a2": 3.24, "n1": 6.0, "n2": 0.7, "sigma": 6.320},#Rough
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
              "h125a8"  : { "a1": 3.5, "a2": 3.5, "n1": 18.0, "n2": 1.3, "sigma": 14.0},#Rough
              "h125a9"  : { "a1": 3.5, "a2": 3.5, "n1": 18.0, "n2": 1.3, "sigma": 14.0},
              "h125a10" : { "a1": 3.5, "a2": 3.5, "n1": 18.0, "n2": 1.3, "sigma": 14.0},#Rough
              "h125a11" : { "a1": 3.5, "a2": 3.5, "n1": 18.0, "n2": 1.3, "sigma": 14.0},
              "h125a12" : { "a1": 3.5, "a2": 3.5, "n1": 18.0, "n2": 1.3, "sigma": 14.0},#Rough
              "h125a13" : { "a1": 3.5, "a2": 3.5, "n1": 18.0, "n2": 1.3, "sigma": 14.0},
              "h125a14" : { "a1": 3.5, "a2": 3.5, "n1": 18.0, "n2": 1.3, "sigma": 14.0},#Rough
              "h125a15" : { "a1": 3.5, "a2": 3.5, "n1": 18.0, "n2": 1.3, "sigma": 14.0},
              "h125a17" : { "a1": 3.5, "a2": 3.5, "n1": 18.0, "n2": 1.3, "sigma": 14.0},
              "h125a18" : { "a1": 3.5, "a2": 3.5, "n1": 18.0, "n2": 1.3, "sigma": 14.0},#Rough
              "h125a19" : { "a1": 3.5, "a2": 3.5, "n1": 18.0, "n2": 1.3, "sigma": 14.0},
              "h125a20" : { "a1": 3.5, "a2": 3.5, "n1": 18.0, "n2": 1.3, "sigma": 14.0},#Rough
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
              "h125a8"  : { "mean": 100},#Rough
              "h125a9"  : { "mean": 100},
              "h125a10" : { "mean": 98},#Rough
              "h125a11" : { "mean": 95},
              "h125a12" : { "mean": 95},#Rough
              "h125a13" : { "mean": 95},
              "h125a15" : { "mean": 90},
              "h125a14" : { "mean": 90},#Rough
              "h125a17" : { "mean": 90},
              "h125a18" : { "mean": 90},#Rough
              "h125a19" : { "mean": 90},
              "h125a20" : { "mean": 90},#Rough
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
              "h125a8"  : { "mean": 98},#Rough
              "h125a9"  : { "mean": 95},
              "h125a10" : { "mean": 95},#Rough
              "h125a11" : { "mean": 90},
              "h125a12" : { "mean": 92},#Rough
              "h125a13" : { "mean": 97},
              "h125a14" : { "mean": 97},#Rough
              "h125a15" : { "mean": 95},
              "h125a17" : { "mean": 97},
              "h125a18" : { "mean": 98},#Rough
              "h125a19" : { "mean": 93},
              "h125a20" : { "mean": 93},#Rough
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
                "h125a4"  : { "mean": 90.1, "sigma1": 15.1, "sigma2": 10.1}, #89.5 15.6 12.5 2.07
                "h125a5"  : { "mean": 94.2, "sigma1": 17.0, "sigma2": 10.0},
                "h125a6"  : { "mean": 93.1, "sigma1": 15.6, "sigma2": 11.9},
                "h125a7"  : { "mean": 93.3, "sigma1": 16.5, "sigma2": 11.7},
                "h125a8"  : { "mean": 92.5, "sigma1": 16.2, "sigma2": 12.1},#Rough
                "h125a9"  : { "mean": 91.2, "sigma1": 16.2, "sigma2": 12.1},#Change 1
                "h125a10" : { "mean": 89.5, "sigma1": 15.5, "sigma2": 11.5},#Change 1 88.5 15.1 11.1 2.14 89.5 15.5 11.5 2.09 
                "h125a11" : { "mean": 93.2, "sigma1": 16.0, "sigma2": 15.5},#Change 1
                "h125a12" : { "mean": 92.1, "sigma1": 16.0, "sigma2": 12.4},#Rough
                "h125a13" : { "mean": 91.8, "sigma1": 15.9, "sigma2": 12.5},
                "h125a14" : { "mean": 94.5, "sigma1": 16.8, "sigma2": 11.6},#Change 1
                "h125a15" : { "mean": 91.2, "sigma1": 15.5, "sigma2": 11.9},#Change 1
                "h125a17" : { "mean": 91.1, "sigma1": 15.2, "sigma2": 12.2},
                "h125a18" : { "mean": 91.0, "sigma1": 15.3, "sigma2": 12.3},#Rough
                "h125a19" : { "mean": 90.7, "sigma1": 15.4, "sigma2": 12.4},
                "h125a20" : { "mean": 89.5, "sigma1": 15.5, "sigma2": 11.6},#Rough
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
        elif 'FP' in region: 
            initialValues = {
                "h125a3p6": { "mean": 93.4, "sigma1": 13.5, "sigma2": 13.0},
                "h125a4"  : { "mean": 89.5, "sigma1": 15.5, "sigma2": 10.1},#Change 1 86.5 15.5 10.1 1.58 | 89.5 15.5 10.1 1.409 
                "h125a5"  : { "mean": 91.1, "sigma1": 15.5, "sigma2": 11.5},#Change 1 89.1 15.5 11.5 1.94 | 91.1 15.5 11.5 1.79 
                "h125a6"  : { "mean": 94.9, "sigma1": 15.9, "sigma2": 12.8},
                "h125a7"  : { "mean": 89.4, "sigma1": 15.3, "sigma2": 12.1},#Change 1 87.4 15.3 12.1 1.71 | 89.4 15.3 12.1 1.38
                "h125a8"  : { "mean": 91.5, "sigma1": 15.5, "sigma2": 12.1},#Change 1 89.3 15.1 12.2 2.24 90.2 15.3 12.1 2.15
                "h125a9"  : { "mean": 92.5, "sigma1": 15.5, "sigma2": 11.5},#Change 1                1.06(Bad Fit)
                "h125a10" : { "mean": 88.5, "sigma1": 15.5, "sigma2": 10.1},#Change 1 87.5 15.5 11.9 1.98 88.5 15.5 11.9 1.92
                "h125a11" : { "mean": 89.5, "sigma1": 14.9, "sigma2": 15.9},#Change 1 89.5 14.9 15.9 1.38
                "h125a12" : { "mean": 92.5, "sigma1": 15.5, "sigma2": 11.5},#Change 1 90.9 12.1 10.1 3.18 | 83.9 15.5 10.1 3.24 
                "h125a13" : { "mean": 94.5, "sigma1": 11.1, "sigma2": 16.5},#Change 1 97.1 13.1 12.1 4.11 | 97.1 11.1 12.1 4.11
                "h125a14" : { "mean": 88.3, "sigma1": 15.5, "sigma2": 11.5},#Change 1 87.3 15.2 11.5 1.85/1.76 88.3 15.5 11.5 1.63
                "h125a15" : { "mean": 90.8, "sigma1": 18.5, "sigma2": 11.5}, #Change 1 88.8 15.5 11.5 2.54  90.8 9.1 10.5 2.477
                "h125a17" : { "mean": 90.9, "sigma1": 18.5, "sigma2": 11.5}, #Change 1 88.9 15.5 11.1 2.42  90.9 14.5 9.1 2.42
                "h125a18" : { "mean": 86.1, "sigma1": 15.5, "sigma2": 11.5},#Change 1`86.1 15.5 11.5 1.62
                "h125a19" : { "mean": 90.1, "sigma1": 14.1, "sigma2": 15.1},#Change 1 89.0 15.2 11.1 2.12
                "h125a20" : { "mean": 89.2, "sigma1": 15.1, "sigma2": 10.1},#Change F 88.6 14.1 15.5 1.01   
                "h125a21" : { "mean": 87.7, "sigma1": 15.5, "sigma2": 12.4},#Change F 86.7 15.5 12.4 1.17 89.7 16.5 11.1 1.21 
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
    
    def GetInitialValuesBC(self, region="FP"):
        if 'PP' in region:
            initialValues = {
                "h125a4": { "betaScale": 1/125, "betaA": 5, "betaB": 2, "mean":89.5 , "sigma": 12},
                "h125a10": { "betaScale": 1/125, "betaA": 5, "betaB": 2, "mean":89.5 , "sigma": 12},
                "h125a20": { "betaScale": 1/125, "betaA": 5, "betaB": 2, "mean":89.5 , "sigma": 12},
                
                }
        elif 'FP' in region:
             initialValues = {
                 "h125a4": { "betaScale": 1/125, "betaA": 5, "betaB": 2, "mean":89.5 , "sigma": 12},
                 "h125a10": { "betaScale": 1/125, "betaA": 5, "betaB": 2, "mean":89.5 , "sigma": 12},
                 "h125a20": { "betaScale": 1/125, "betaA": 5, "betaB": 2, "mean":89.5 , "sigma": 12},
                 
                 }
             
        return initialValues
    # mean  = [0.7*h,0.64*h,0.76*h],
    # sigma1 = [0.1*h,0.08*h,0.16*h],
    # sigma2 = [0.125*h,0.09*h,0.18*h],
    # width1 = [1.0,0.01,10.0],
    # width2 = [1.0,0.01,10.0],
    def GetInitialValuesDV(self, region="FP"):
         if 'PP' in region:
            initialValues = {
                "h125a4": { "mean": 92.1,"sigma1": 15.1, "sigma2": 11.1, "width1":1.15 , "width2": 4.00 }, #1.00
                "h125a5": { "mean": 89.1,"sigma1": 15.1, "sigma2": 11.1, "width1":1.50 , "width2": 1.25 },
                "h125a7": { "mean": 89.1,"sigma1": 15.1, "sigma2": 11.1, "width1":1.50 , "width2": 1.20 },
                "h125a8": { "mean": 89.1,"sigma1": 15.1, "sigma2": 11.1, "width1":1.50 , "width2": 1.15 },
                "h125a9": { "mean": 89.5, "sigma1": 15.1, "sigma2": 11.5, "width1":1.75 , "width2": 1.25},
                "h125a10": { "mean": 89.5, "sigma1": 15.1, "sigma2": 11.5, "width1":1.75 , "width2": 1.25},
                "h125a11": { "mean": 92.5, "sigma1": 15.1, "sigma2": 11.1, "width1":1.50 , "width2": 1.25},
                "h125a12": { "mean": 91.5, "sigma1": 15.1, "sigma2": 11.5, "width1":1.50 , "width2": 1.15},
                "h125a13": { "mean": 90.5, "sigma1": 15.1, "sigma2": 11.5, "width1":1.50 , "width2": 1.15},
                "h125a14": { "mean": 90.5, "sigma1": 15.1, "sigma2": 11.5, "width1":1.75 , "width2": 4.20}, #1.20
                "h125a15": { "mean": 89.5, "sigma1": 15.1, "sigma2": 11.5, "width1":1.55 , "width2": 1.25},
                "h125a17": { "mean": 89.5, "sigma1": 15.1, "sigma2": 11.5, "width1":1.60 , "width2": 1.20},
                "h125a18": { "mean": 89.5, "sigma1": 15.1, "sigma2": 11.5, "width1":1.50 , "width2": 1.15},
                "h125a19": { "mean": 89.5, "sigma1": 15.1, "sigma2": 11.5, "width1":1.50 , "width2": 1.10},
                "h125a20": { "mean": 88.5, "sigma1": 15.1, "sigma2": 11.5, "width1":1.50 , "width2": 1.15},
                "h125a21": { "mean": 88.5, "sigma1": 15.1, "sigma2": 11.5, "width1":1.5 , "width2": 1.25}
                }
         elif 'FP' in region:
             initialValues = {
                 "h125a4": { "mean": 89.5, "sigma1": 15.1, "sigma2": 11.1, "width1":1.5 , "width2": 1.0},
                 "h125a5": { "mean": 92.5, "sigma1": 15.1, "sigma2": 10.5, "width1":1.60 , "width2": 1.00},
                 "h125a7": { "mean": 89.5,"sigma1": 15.1, "sigma2": 11.1, "width1":1.55 , "width2": 1.20 },
                 "h125a8": { "mean": 89.5,"sigma1": 15.1, "sigma2": 11.1, "width1":1.50 , "width2": 1.15 },
                 "h125a9": { "mean": 89.5, "sigma1": 15.1, "sigma2": 11.1, "width1":1.50 , "width2": 1.10},
                 "h125a10": { "mean": 89.5, "sigma1": 15.1, "sigma2": 11.1, "width1":1.50 , "width2": 1.25},
                 "h125a11": { "mean": 89.5, "sigma1": 15.1, "sigma2": 11.5, "width1":1.75 , "width2": 1.25},
                 "h125a12": { "mean": 90.5, "sigma1": 15.1, "sigma2": 11.1, "width1":1.50 , "width2": 1.15},
                 "h125a13": { "mean": 89.5, "sigma1": 15.1, "sigma2": 11.1, "width1":1.50 , "width2": 1.15},
                 "h125a14": { "mean": 89.5, "sigma1": 15.1, "sigma2": 11.1, "width1":1.75 , "width2": 1.20},
                 "h125a15": { "mean": 89.5, "sigma1": 15.1, "sigma2": 11.1, "width1":1.55 , "width2": 1.20},
                 "h125a17": { "mean": 89.5, "sigma1": 15.1, "sigma2": 11.1, "width1":1.75 , "width2": 1.00},
                 "h125a18": { "mean": 89.5, "sigma1": 15.1, "sigma2": 12.1, "width1":2.20, "width2": 1.10},
                 "h125a19": { "mean": 89.5, "sigma1": 15.1, "sigma2": 11.1, "width1":1.85, "width2": 1.00},
                 "h125a20": { "mean": 89.5, "sigma1": 15.1, "sigma2": 11.1, "width1":1.50, "width2": 1.20},
                 "h125a21": { "mean": 89.5, "sigma1": 15.1, "sigma2": 11.1, "width1":1.50, "width2": 1.20}
                 }
         return initialValues


         
         
    ###################
    ### Systematics ###
    ###################
    def addSystematics(self,doBinned=False,addControl=False):
        print "Adding systematics..."
        #print self.REGIONS
        #for channel in self.CHANNELS:
        self.sigProcesses = tuple([self.SPLINENAME.format(h=h)+'_'+c+'_'+r for r in self.REGIONS for h in self.HMASSES for c in self.CHANNELS])
        bgs = []
        for c in self.CHANNELS:
            for r in self.REGIONS:
                if r == 'control':
                    region = r
                else:
                    region = c+'_'+r
                bgs += self.getComponentFractions(self.workspace.pdf('bg_{}_x'.format(region)))
        bgs = [self.rstrip(b,'_'+region) for b in bgs]
        if not self.SPLITBGS: bgs = ['bg']
        self.bgProcesses = bgs
        #print "***", self.bgProcesses
        #print "sigProcesses:", self.sigProcesses
        #print "bgProcesses:", self.bgProcesses
        self._addLumiSystematic()
        self._addMuonSystematic()
        self._addAcceptanceSystematic()
##        #self._addTauSystematic()
##        self._addShapeSystematic(doBinned=doBinned)
##        #self._addComponentSystematic(addControl=addControl)
##        self._addRelativeNormUnc()
##        self._addHiggsSystematic()
##        if not doBinned and not addControl: self._addControlSystematics()
##        if self.YRANGE[1] > 100: self._addHModelSystematic()
            
    def _addHModelSystematic(self):
        
        #if selfDOUBLEEXPO: return
        return

        syst = {}
        if 125 in self.HMASSES: syst[((self.SPLINENAME.format(h=125),), tuple(self.REGIONS))] = 1.0
        if 300 in self.HMASSES: syst[((self.SPLINENAME.format(h=300),), tuple(self.REGIONS))] = 1.05
        if 750 in self.HMASSES: syst[((self.SPLINENAME.format(h=750),), tuple(self.REGIONS))] = 2.3
        self.addSystematic('CMS_haa_model_bias','lnN',systematics=syst)

    def fixXLambda(self,**kwargs):
        return
        workspace = kwargs.get('workspace',self.workspace)
        print 'WARNING: Fixing x lambda in continuum to b-only fit value'
        lambdaFP1 = workspace.var('lambda_cont1_FP_x')
        if lambdaFP1:
            lambdaFP1.setVal(-0.1021)
            lambdaFP1.setConstant(True)
        #intFP1 = workspace.var('integral_cont1_FP')
        #if lambdaFP1:
        #    intFP1.setConstant(True)

    def fixCorrelation(self,**kwargs):
        return
        workspace = kwargs.get('workspace',self.workspace)
        print 'WARNING: Fixing correlation parameters'
        erfShiftA0PP = workspace.var('erfShiftA0_PP_y')
        erfShiftA1PP = workspace.var('erfShiftA1_PP_y')
        erfShiftA0FP = workspace.var('erfShiftA0_FP_y')
        erfShiftA1FP = workspace.var('erfShiftA1_FP_y')
        if erfShiftA0PP:
            erfShiftA0PP.setVal(46.2)
            erfShiftA0PP.setConstant(True)
        if erfShiftA1PP:
            erfShiftA1PP.setVal(1.01)
            erfShiftA1PP.setConstant(True)
        if erfShiftA0FP:
            erfShiftA0FP.setVal(46.2)
            erfShiftA0FP.setConstant(True)
        if erfShiftA1FP:
            erfShiftA1FP.setVal(1.01)
            erfShiftA1FP.setConstant(True)



    ###################################
    ### Save workspace and datacard ###
    ###################################
    def save(self,name='mmmt', subdirectory=''):

        self.fixXLambda(workspace=self.workspace)
        self.fixCorrelation(workspace=self.workspace)


        processes = {}
        #region = self.CHANNEL+'_'+self.REGIONS[0]
        bgs_tmp = [self.getComponentFractions(self.workspace.pdf('bg_{}_x'.format(channel+'_'+self.REGIONS[0])))for channel in self.CHANNELS]
        bgs=bgs_tmp[0]
        while len(bgs_tmp) > 1:
            bgs.update(bgs_tmp[1])
            bgs_tmp.pop(1)
        #print "bgs:", bgs
        bgs = [self.rstrip(b,'_x') for b in bgs]
        bgs = [self.rstrip(b,'_'+self.REGIONS[0]) for b in bgs]
       
        if not self.SPLITBGS: bgs = ['bg']
        if self.do2D:
            processes = [self.SPLINENAME+'_'+self.CHANNEL] + bgs
        else:
            for h in self.HMASSES:
                processes[self.SIGNAME.format(h=h,a='X')] = [self.SPLINENAME.format(h=h)+'_'+channel for channel in self.CHANNELS] + bgs
        #print processes
        if subdirectory == '':
            self.printCard('datacards_shape/MuMuTauTau/{}'.format(name),processes=processes,blind=False,saveWorkspace=True)
        else:
            self.printCard('datacards_shape/MuMuTauTau/' + subdirectory + '{}'.format(name),processes=processes,blind=False,saveWorkspace=True)

