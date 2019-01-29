import os
import sys
import logging
import itertools
import numpy as np
import argparse
import math

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.SetBatch()

from DevTools.Plotter.NtupleWrapper import NtupleWrapper
from DevTools.Utilities.utilities import *
from DevTools.Plotter.haaUtils import *
#from DevTools.Plotter.xsec import getXsec
#from CombineLimits.HaaLimits.HaaLimits import HaaLimits
#from CombineLimits.HaaLimits.HaaLimits2D import HaaLimits2D
from CombineLimits.HaaLimits.HaaLimitsNew import HaaLimits
from CombineLimits.HaaLimits.HaaLimits2DNew import HaaLimits2D

import CombineLimits.Plotter.CMS_lumi as CMS_lumi
import CombineLimits.Plotter.tdrstyle as tdrstyle

tdrstyle.setTDRStyle()

logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
ROOT.RooMsgService.instance().setGlobalKillBelow(ROOT.RooFit.WARNING)


testing = False
detailed = True
skipSignal = False


xRange = [2.5,25] # with jpsi

yRange = [0,1200] # h, hkf

#hmasses = [125,300,750]
hmasses = [125,200,250,300,400,500,750,1000]
#if testing: hmasses = [125]
#if testing: hmasses = [300]
#if testing: hmasses = [750]
amasses = ['3p6',4,5,6,7,9,11,13,15,17,19,21]
#if testing: amasses = ['3p6',5,9,13,17,21]
vbfhmasses = [125,300,750]
vbfamasses = [5,9,15,21]
hamap = {
    125 : ['3p6',4,5,6,7,9,11,13,15,17,19,21],
    200 : [5,9,15],
    250 : [5,9,15],
    300 : [5,7,9,11,13,15,17,19,21],
    400 : [5,9,15],
    500 : [5,9,15],
    750 : [5,7,9,11,13,15,17,19,21],
    1000: [5,9,15],
}
    
signame = 'HToAAH{h}A{a}'
ggsigname = 'ggHToAAH{h}A{a}'
vbfsigname = 'vbfHToAAH{h}A{a}'

shiftTypes = ['lep','pu','fake','trig','btag','tau','MuonEn','TauEn']#,'JetEn','UnclusteredEn']
#if testing: shiftTypes = ['fake','tau','MuonEn'] if detailed else []
if testing: shiftTypes = ['fake','tau'] if detailed else []
#if testing: shiftTypes = ['tau'] if detailed else []

signalShiftTypes = ['lep','pu','trig','btag','tau','MuonEn','TauEn']#,'JetEn','UnclusteredEn']
#if testing: signalShiftTypes = ['tau','MuonEn'] if detailed else []
if testing: signalShiftTypes = ['tau'] if detailed else []

backgroundShiftTypes = ['fake']
if testing: backgroundShiftTypes = ['fake'] if detailed else []
#if testing: backgroundShiftTypes = []

qcdShifts = []
for muR in [0.5,1.0,2.0]:
    for muF in [0.5,1.0,2.0]:
        if muR/muF>=4 or muF/muR>=4: continue
        qcdShifts += ['muR{muR:3.1f}muF{muF:3.1f}'.format(muR=muR,muF=muF)]
if testing: qcdShifts = []

shifts = []
for s in shiftTypes:
    shifts += [s+'Up', s+'Down']
shifts += qcdShifts



varHists = {
    'mm' : 'ammMass',
    'tt' : 'attMass',
    'h'  : 'hMass',
    'hkf': 'hMassKinFit',
}
varNames = {
    'mm' : 'amm_mass',
    'tt' : 'att_mass',
    'h'  : 'h_mass',
    'hkf': 'h_massKinFit',
}
rebinning = {
    #'mm' : 5, # 10 MeV -> 50 MeV
    'mm' : 10, # 10 MeV -> 100 MeV
    #'mm' : 25, # 10 MeV -> 250 MeV
    'tt' : 1, # 100 MeV -> 100 MeV
    'h'  : 1, # 1 GeV -> 1 GeV
    'hkf': 1, # 1 GeV -> 5 GeV
}

project = False
hCut = '1'

# xsec splines
smtfile  = ROOT.TFile.Open('CombineLimits/Limits/data/Higgs_YR4_SM_13TeV.root')
bsmtfile = ROOT.TFile.Open('CombineLimits/Limits/data/Higgs_YR4_BSM_13TeV.root')
smws = smtfile.Get('YR4_SM_13TeV')
bsmws = bsmtfile.Get('YR4_BSM_13TeV')

def getXsec(proc,mode):
    h = int(proc.split('H')[-1].split('A')[0])
    a = float(proc.split('A')[-1].replace('p','.'))
    # this was input as SM for 125 and BSM for others
    ws = smws if h==125 else bsmws
    #ws = bsmws
    names = {
        'gg' : 'xsec_ggF_N3LO',
        'vbf': 'xsec_VBF',
    }
    spline = ws.function(names[mode])
    ws.var('MH').setVal(h)
    return spline.getVal()
    


#################
### Utilities ###
#################
def getControlDataset(wrapper,plotname):
    selDatasets = {
        'x' : 'x>{} && x<{}'.format(*xRange),
    }
    return wrapper.getDataset(plotname,selection=selDatasets['x'],xRange=xRange,weight='w')

def getDataset(wrapper,plotname):
    thisxrange = xRange
    thisyrange = yRange
    sample = wrapper.sample
    if 'SUSY' in sample:
        if yRange[1]>100:
            if '200' in sample:    h = 200 #thisyrange = [20,260]
            elif '250' in sample:  h = 250 #thisyrange = [30,300]
            elif '300' in sample:  h = 300 #thisyrange = [40,360]
            elif '400' in sample:  h = 400 #thisyrange = [60,500]
            elif '500' in sample:  h = 500 #thisyrange = [80,700]
            elif '750' in sample:  h = 750 #thisyrange = [140,900]
            elif '1000' in sample: h = 1000 #thisyrange = [180,1200]
            else:                  h = 125 #thisyrange = [20,150]
            thisyrange = [0.15*h, 1.2*h]
    selDatasets = {
        'x' : 'x>{} && x<{}'.format(*thisxrange),
        'y' : 'y>{} && y<{}'.format(*thisyrange),
    }
    if project:
        if 'hMass' in plotname:
            return wrapper.getDataset(plotname,selection=' && '.join([selDatasets['x'],selDatasets['y'],hCut]),xRange=thisxrange,weight='w',yRange=thisyrange,project='x')
        elif 'attMass' in plotname:
            return wrapper.getDataset(plotname,selection=' && '.join([selDatasets['x'],selDatasets['y']]),xRange=thisxrange,weight='w',yRange=thisyrange,project='x')
    else:
        if 'hMass' in plotname or 'attMass' in plotname:
            return wrapper.getDataset(plotname,selection=' && '.join([selDatasets['x'],selDatasets['y']]),xRange=thisxrange,weight='w',yRange=thisyrange)
        else:
            return wrapper.getDataset(plotname,selection=selDatasets['x'],xRange=thisxrange,weight='w')

def getControlHist(proc,**kwargs):
    wrappers = kwargs.pop('wrappers',{})
    doUnbinned = kwargs.pop('doUnbinned',False)
    plot = 'mmMass'
    plotname = 'deltaR_iso/default/{}'.format(plot)
    #if doUnbinned:
    #    plotname += '_dataset'
    #if doUnbinned:
    #    hists = [getControlDataset(wrappers[s],plotname) for s in sampleMap[proc]]
    #    hist = sumDatasets(proc+'control',*hists)
    #else:
    # Takes far too long to do this unbinned
    hists = [wrappers[s].getHist(plotname) for s in sampleMap[proc]]
    hist = sumHists(proc+'control',*hists)
    return hist

def getHist(proc,**kwargs):
    scale = kwargs.pop('scale',1)
    shift = kwargs.pop('shift','')
    region = kwargs.pop('region','A')
    do2D = kwargs.pop('do2D',False)
    chi2Mass = kwargs.pop('chi2Mass',0)
    doUnbinned = kwargs.pop('doUnbinned',False)
    var = kwargs.pop('var',['mm'])
    wrappers = kwargs.pop('wrappers',{})
    if do2D:
        plot = '{}_{}'.format(*[varHists[v] for v in var])
    else:
        plot = varHists[var[0]]
    if doUnbinned:
        plot += '_dataset'
    plotname = 'region{}/{}'.format(region,plot)
    if chi2Mass: plotname = 'chi2_{}/{}'.format(chi2Mass,plotname)
    if doUnbinned:
        hists = [getDataset(wrappers[s+shift],plotname) for s in sampleMap[proc]]
        hist = sumDatasets(proc+region,*hists)
    else:
        if do2D:
            hists = [wrappers[s+shift].getHist2D(plotname) for s in sampleMap[proc]]
        else:
            hists = [wrappers[s+shift].getHist(plotname) for s in sampleMap[proc]]
        hist = sumHists(proc+region,*hists)
        hist.Scale(scale)
    return hist

def getDatadrivenHist(**kwargs):
    shift = kwargs.pop('shift','')
    source = kwargs.pop('source','B')
    region = kwargs.pop('region','A')
    do2D = kwargs.pop('do2D',False)
    chi2Mass = kwargs.pop('chi2Mass',0)
    doUnbinned = kwargs.pop('doUnbinned',False)
    var = kwargs.pop('var',['mm'])
    wrappers = kwargs.pop('wrappers',{})
    if do2D:
        plot = '{}_{}'.format(*[varHists[v] for v in var])
    else:
        plot = varHists[var[0]]
    if doUnbinned:
        plot += '_dataset'
    plotname = 'region{}_fakeFor{}/{}'.format(source,region,plot)
    if chi2Mass: plotname = 'chi2_{}/{}'.format(chi2Mass,plotname)
    if doUnbinned:
        hists = [getDataset(wrappers[s+shift],plotname) for s in sampleMap['data']]
        hist = sumDatasets('data'+region+source,*hists)
    else:
        if do2D:
            hists = [wrappers[s+shift].getHist2D(plotname) for s in sampleMap['data']]
        else:
            hists = [wrappers[s+shift].getHist(plotname) for s in sampleMap['data']]
        hist = sumHists('data'+region+source,*hists)
    return hist

def getMatrixHist(proc,**kwargs):
    scale = kwargs.pop('scale',1)
    shift = kwargs.pop('shift','')
    region = kwargs.pop('region','A')
    sources = kwargs.pop('sources',['A','C'])
    doPrompt = kwargs.pop('doPrompt',True)
    doFake = kwargs.pop('doFake',False)
    do2D = kwargs.pop('do2D',False)
    chi2Mass = kwargs.pop('chi2Mass',0)
    doUnbinned = kwargs.pop('doUnbinned',False)
    var = kwargs.pop('var',['mm'])
    wrappers = kwargs.pop('wrappers',{})
    if do2D:
        plot = '{}_{}'.format(*[varHists[v] for v in var])
    else:
        plot = varHists[var[0]]
    if doUnbinned:
        plot += '_dataset'
    applot = ['matrixP/region{}_for{}/{}'.format(source,region,plot) for source in sources]
    afplot = ['matrixF/region{}_for{}/{}'.format(source,region,plot) for source in sources]
    if chi2Mass:
        applot = ['chi2_{}/{}'.format(chi2Mass,plotname) for plotname in applot]
        afplot = ['chi2_{}/{}'.format(chi2Mass,plotname) for plotname in afplot]
    hists = []
    for s in sampleMap[proc]:
        if doUnbinned:
            if doPrompt: hists += [getDataset(wrappers[s+shift],plotname) for plotname in applot]
            if doFake: hists += [getDataset(wrappers[s+shift],plotname) for plotname in afplot]
        else:
            if do2D:
                if doPrompt: hists += [wrappers[s+shift].getHist2D(plotname) for plotname in applot]
                if doFake: hists += [wrappers[s+shift].getHist2D(plotname) for plotname in afplot]
            else:
                if doPrompt: hists += [wrappers[s+shift].getHist(plotname) for plotname in applot]
                if doFake: hists += [wrappers[s+shift].getHist(plotname) for plotname in afplot]
    if doUnbinned:
        hist = sumDatasets(proc+region+source,*hists)
    else:
        hist = sumHists(proc+region+source,*hists)
        hist.Scale(scale)
    return hist

def getMatrixDatadrivenHist(**kwargs):
    shift = kwargs.pop('shift','')
    region = kwargs.pop('region','A')
    sources = kwargs.pop('sources',['A','C'])
    fakeRegion = kwargs.pop('fakeRegion','B')
    fakeSources = kwargs.pop('fakeSources',['B','D'])
    doPrompt = kwargs.pop('doPrompt',True)
    doFake = kwargs.pop('doFake',False)
    do2D = kwargs.pop('do2D',False)
    chi2Mass = kwargs.pop('chi2Mass',0)
    doUnbinned = kwargs.pop('doUnbinned',False)
    var = kwargs.pop('var',['mm'])
    wrappers = kwargs.pop('wrappers',{})
    if do2D:
        plot = '{}_{}'.format(*[varHists[v] for v in var])
    else:
        plot = varHists[var[0]]
    if doUnbinned:
        lot += '_dataset'
    bpplot = ['matrixP/region{}_for{}_fakeFor{}/{}'.format(source,fakeRegion,region,plot) for source in fakeSources]
    bfplot = ['matrixF/region{}_for{}_fakeFor{}/{}'.format(source,fakeRegion,region,plot) for source in fakeSources]
    if chi2Mass:
        bpplot = ['chi2_{}/{}'.format(chi2Mass,plotname) for plotname in bpplot]
        bfplot = ['chi2_{}/{}'.format(chi2Mass,plotname) for plotname in bfplot]
    hists = []
    for s in sampleMap['data']:
        if doUnbinned:
            if doPrompt: hists += [getDataset(wrappers[s+shift],plotname) for plotname in bpplot]
            if doFake: hists += [getDataset(wrappers[s+shift],plotname) for plotname in bfplot]
        else:
            if do2D:
                if doPrompt: hists += [wrappers[s+shift].getHist2D(plotname) for plotname in bpplot]
                if doFake: hists += [wrappers[s+shift].getHist2D(plotname) for plotname in bfplot]
            else:
                if doPrompt: hists += [wrappers[s+shift].getHist(plotname) for plotname in bpplot]
                if doFake: hists += [wrappers[s+shift].getHist(plotname) for plotname in bfplot]
    if doUnbinned:
        hist = sumDatasets('data'+region+source,*hists)
    else:
        hist = sumHists('data'+region+source,*hists)
    return hist

def sumHists(name,*hists):
    histlist = ROOT.TList()
    for hist in hists:
        histlist.Add(hist)
    hist = histlist[0].Clone(name)
    hist.Reset()
    hist.Merge(histlist)
    return hist

def sumDatasets(name,*datasets):
    dataset = datasets[0].Clone(name)
    for d in datasets[1:]:
        dataset.append(d)
    return dataset


###############
### Control ###
###############

def create_datacard(args):
    doMatrix = False
    doParametric = args.parametric
    doUnbinned = args.unbinned
    do2D = len(args.fitVars)==2
    chi2Mass = args.chi2Mass
    blind = not args.unblind
    addSignal = args.addSignal
    signalParams = {'h': args.higgs, 'a': args.pseudoscalar}
    wsname = 'w'
    var = args.fitVars
    
    if doUnbinned and not doParametric:
        logging.error('Unbinned only supported with parametric option')
        raise

    if chi2Mass and 'hkf' not in var:
        logging.error('Trying to use non-kinematic fit with chi2 cut')
        raise

    global xRange
    global yRange
    if do2D and var[1]=='tt': yRange = [0.75,30]
    #if do2D and var[1]=='tt': yRange = [0,25]
    if args.yRange: yRange = args.yRange
    xRange = args.xRange

    global project
    global hCut
    project = args.project
    if args.selection: hCut = args.selection

    xBinWidth = 0.1
    if do2D:
        yBinWidth = 0.25 if var[1]=='tt' else 10

    global hmasses
    if not args.do2DInterpolation:
        hmasses = [h for h in hmasses if h in [125, 300, 750]]

    #############
    ### Setup ###
    #############
    sampleMap = getSampleMap()
    
    backgrounds = ['datadriven']
    data = ['data']
    
    signals = [signame.format(h=h,a=a) for h in hmasses for a in amasses if a in hamap[h]]
    ggsignals = [ggsigname.format(h=h,a=a) for h in hmasses for a in amasses if a in hamap[h]]
    vbfsignals = [vbfsigname.format(h=h,a=a) for h in vbfhmasses for a in vbfamasses]
    signalToAdd = signame.format(**signalParams)

    
    wrappers = {}
    for proc in backgrounds+signals+ggsignals+vbfsignals+data:
        if proc=='datadriven': continue
        for sample in sampleMap[proc]:
            wrappers[sample] = NtupleWrapper('MuMuTauTau',sample,new=True,version='80X')
            for shift in shifts:
                wrappers[sample+shift] = NtupleWrapper('MuMuTauTau',sample,new=True,version='80X',shift=shift)

    wrappers_mm = {}
    for proc in data:
        for sample in sampleMap[proc]:
            wrappers_mm[sample] = NtupleWrapper('MuMu',sample,new=True,version='80X')
    
    ##############################
    ### Create/read histograms ###
    ##############################
    
    histMap = {}
    # The definitons of which regions match to which arguments
    # PP can take a fake rate datadriven estimate from FP, but FP can only take the observed values
    regionArgs = {
        'PP': {'region':'A','fakeRegion':'B','source':'B','sources':['A','C'],'fakeSources':['B','D'],},
        'FP': {'region':'B','sources':['B','D'],},
    }
    for mode in ['PP','FP']:
        histMap[mode] = {}
        for shift in ['']+shifts:
            histMap[mode][shift] = {}
            for proc in backgrounds+signals:
                logging.info('Getting {} {}'.format(proc,shift))
                if proc=='datadriven':
                    if mode=='PP':
                        if doMatrix:
                            #histMap[mode][shift][proc] = getMatrixDatadrivenHist(doUnbinned=doUnbinned,var=var,wrappers=wrappers,shift=shift,do2D=do2D,chi2Mass=chi2Mass,**regionArgs[mode])
                            histMap[mode][shift][proc] = getMatrixDatadrivenHist(doUnbinned=True,var=var,wrappers=wrappers,shift=shift,do2D=do2D,chi2Mass=chi2Mass,**regionArgs[mode])
                        else:
                            #histMap[mode][shift][proc] = getDatadrivenHist(doUnbinned=doUnbinned,var=var,wrappers=wrappers,shift=shift,do2D=do2D,chi2Mass=chi2Mass,**regionArgs[mode])
                            histMap[mode][shift][proc] = getDatadrivenHist(doUnbinned=True,var=var,wrappers=wrappers,shift=shift,do2D=do2D,chi2Mass=chi2Mass,**regionArgs[mode])
                    else:
                        if doMatrix:
                            #histMap[mode][shift][proc] = getMatrixHist('data',doUnbinned=doUnbinned,var=var,wrappers=wrappers,shift=shift,do2D=do2D,chi2Mass=chi2Mass,**regionArgs[mode])
                            histMap[mode][shift][proc] = getMatrixHist('data',doUnbinned=True,var=var,wrappers=wrappers,shift=shift,do2D=do2D,chi2Mass=chi2Mass,**regionArgs[mode])
                        else:
                            #histMap[mode][shift][proc] = getHist('data',doUnbinned=doUnbinned,var=var,wrappers=wrappers,shift=shift,do2D=do2D,chi2Mass=chi2Mass,**regionArgs[mode])
                            histMap[mode][shift][proc] = getHist('data',doUnbinned=True,var=var,wrappers=wrappers,shift=shift,do2D=do2D,chi2Mass=chi2Mass,**regionArgs[mode])
                else:
                    if proc in signals:
                        newproc = 'gg'+proc
                    else:
                        newproc = proc
                    # override xRange for signal only
                    oldXRange = xRange
                    xRange = [0,30]
                    if doMatrix:
                        #histMap[mode][shift][proc] = getMatrixHist(newproc,doUnbinned=doUnbinned,var=var,wrappers=wrappers,shift=shift,do2D=do2D,chi2Mass=chi2Mass,**regionArgs[mode])
                        histMap[mode][shift][proc] = getMatrixHist(newproc,doUnbinned=True,var=var,wrappers=wrappers,shift=shift,do2D=do2D,chi2Mass=chi2Mass,**regionArgs[mode])
                    else:
                        #histMap[mode][shift][proc] = getHist(newproc,doUnbinned=doUnbinned,var=var,wrappers=wrappers,shift=shift,do2D=do2D,chi2Mass=chi2Mass,**regionArgs[mode])
                        histMap[mode][shift][proc] = getHist(newproc,doUnbinned=True,var=var,wrappers=wrappers,shift=shift,do2D=do2D,chi2Mass=chi2Mass,**regionArgs[mode])
                    xRange = oldXRange
                #if do2D or doUnbinned:
                #    pass # TODO, figure out how to rebin 2D
                #else:
                #    histMap[mode][shift][proc].Rebin(rebinning[var[0]])
            #if shift: continue
            logging.info('Getting observed')
            samples = backgrounds
            if addSignal: samples = backgrounds + [signalToAdd]
            hists = []
            histsNoSig = []
            for proc in samples:
                hists += [histMap[mode][shift][proc].Clone()]
                if proc!=signalToAdd: histsNoSig += [histMap[mode][shift][proc].Clone()]
            #if doUnbinned:
            hist = sumDatasets('obs{}{}'.format(mode,shift),*hists)
            histNoSig = sumDatasets('obsNoSig{}{}'.format(mode,shift),*histsNoSig)
            #else:
            #    hist = sumHists('obs{}{}'.format(mode,shift),*hists)
            #    histNoSig = sumHists('obsNoSig{}{}'.format(mode,shift),*histsNoSig)
            #for b in range(hist.GetNbinsX()+1):
            #    val = int(hist.GetBinContent(b))
            #    if val<0: val = 0
            #    err = val**0.5
            #    hist.SetBinContent(b,val)
            #    #hist.SetBinError(b,err)
            if blind:
                histMap[mode][shift]['data'] = hist.Clone()
                histMap[mode][shift]['dataNoSig'] = histNoSig.Clone()
            else:
                #hist = getHist('data',doUnbinned=doUnbinned,var=var,wrappers=wrappers,do2D=do2D,chi2Mass=chi2Mass,**regionArgs[mode])
                hist = getHist('data',doUnbinned=True,var=var,wrappers=wrappers,do2D=do2D,chi2Mass=chi2Mass,**regionArgs[mode])
                histMap[mode][shift]['data'] = hist.Clone()
                histMap[mode][shift]['dataNoSig'] = histNoSig.Clone()
                #if do2D or doUnbinned:
                #    pass
                #else:
                #    histMap[mode][shift]['data'].Rebin(rebinning[var[0]])
                #    histMap[mode][shift]['dataNoSig'].Rebin(rebinning[var[0]])

    for mode in ['control']:
        histMap[mode] = {}
        for shift in ['']:
            histMap[mode][shift] = {}
            for proc in backgrounds:
                logging.info('Getting {} {}'.format(proc,shift))
                if proc=='datadriven':
                    histMap[mode][shift][proc] = getControlHist('data',doUnbinned=doUnbinned,var=var,wrappers=wrappers_mm)
            if shift: continue
            logging.info('Getting observed')
            hist = getControlHist('data',doUnbinned=doUnbinned,var=var,wrappers=wrappers_mm)
            histMap[mode][shift]['data'] = hist.Clone()
            histMap[mode][shift]['dataNoSig'] = hist.Clone()

    # rescale signal
    scales = {}
    for proc in signals:
        gg = getXsec(proc,'gg')
        vbf = getXsec(proc,'vbf')
        # divide out H cross section from sample
        # it was gg only, we will scale to gg+vbf with acceptance correction in the HaaLimits class
        scale = 1./gg
        scales[proc] = scale
        #print proc, gg, vbf, scale

    name = []
    if args.unbinned: name += ['unbinned']
    if do2D: name += [var[1]]
    n = '_'.join(name) if name else ''
    name = []
    if args.tag: name += [args.tag]
    if args.addSignal: name += ['wSig']
    name = n+'/'+'_'.join(name) if n else '_'.join(name)
    if var == ['mm']:
        haaLimits = HaaLimits(histMap,name,do2DInterpolation=args.do2DInterpolation,doParamFit=args.fitParams)
    elif do2D and project:
        haaLimits = HaaLimits(histMap,name,do2DInterpolation=args.do2DInterpolation,doParamFit=args.fitParams)
    elif do2D:
        haaLimits = HaaLimits2D(histMap,name,do2DInterpolation=args.do2DInterpolation,doParamFit=args.fitParams)
    else:
        logging.error('Unsupported fit vars: ',var)
        raise
    haaLimits.SHIFTS = shiftTypes
    haaLimits.SIGNALSHIFTS = signalShiftTypes
    haaLimits.BACKGROUNDSHIFTS = backgroundShiftTypes
    haaLimits.QCDSHIFTS = qcdShifts
    haaLimits.AMASSES = amasses
    haaLimits.HMASSES = [chi2Mass] if chi2Mass else hmasses
    haaLimits.HAMAP = hamap
    haaLimits.XRANGE = xRange
    haaLimits.XBINNING = int((xRange[1]-xRange[0])/xBinWidth)
    if do2D: 
        haaLimits.YRANGE = yRange
        haaLimits.YBINNING = int((yRange[1]-yRange[0])/yBinWidth)
    if 'tt' in var: haaLimits.YLABEL = 'm_{#tau_{#mu}#tau_{h}}'
    if 'h' in var or 'hkf' in var: haaLimits.YLABEL = 'm_{#mu#mu#tau_{#mu}#tau_{h}}'
    haaLimits.initializeWorkspace()
    haaLimits.addControlModels()
    haaLimits.addBackgroundModels(fixAfterControl=True)
    if not skipSignal:
        haaLimits.XRANGE = [0,30] # override for signal splines
        if project:
            haaLimits.addSignalModels(scale=scales)
        elif 'tt' in var:
            if args.yFitFunc:
                haaLimits.addSignalModels(scale=scales,yFitFuncFP=args.yFitFunc,yFitFuncPP=args.yFitFunc)#,cutOffFP=0.0,cutOffPP=0.0)
            else:
                haaLimits.addSignalModels(scale=scales,yFitFuncFP='V',yFitFuncPP='L')#,cutOffFP=0.75,cutOffPP=0.75)
        elif 'h' in var or 'hkf' in var:
            if args.yFitFunc:
                haaLimits.addSignalModels(scale=scales,yFitFuncFP=args.yFitFunc,yFitFuncPP=args.yFitFunc)#,cutOffFP=0.0,cutOffPP=0.0)
            else:
                haaLimits.addSignalModels(scale=scales,yFitFuncFP='DG',yFitFuncPP='DG')#,cutOffFP=0.0,cutOffPP=0.0)
        else:
            haaLimits.addSignalModels(scale=scales)
        haaLimits.XRANGE = xRange
    if args.addControl: haaLimits.addControlData()
    haaLimits.addData(blind=blind,asimov=args.asimov,addSignal=args.addSignal,doBinned=not doUnbinned,**signalParams) # this will generate a dataset based on the fitted model
    haaLimits.setupDatacard(addControl=args.addControl,doBinned=not doUnbinned)
    haaLimits.addSystematics(addControl=args.addControl,doBinned=not doUnbinned)
    name = 'mmmt_{}_parametric'.format('_'.join(var))
    if args.unbinned: name += '_unbinned'
    if args.tag: name += '_{}'.format(args.tag)
    if args.addSignal: name += '_wSig'
    haaLimits.save(name=name)


def parse_command_line(argv):
    parser = argparse.ArgumentParser(description='Create datacard')

    parser.add_argument('fitVars', type=str, nargs='*', default=[])
    parser.add_argument('--unblind', action='store_true', help='Unblind the datacards')
    parser.add_argument('--parametric', action='store_true', help='Create parametric datacards')
    parser.add_argument('--unbinned', action='store_true', help='Create unbinned datacards')
    parser.add_argument('--addSignal', action='store_true', help='Insert fake signal')
    parser.add_argument('--addControl', action='store_true', help='Add control channel')
    parser.add_argument('--asimov', action='store_true', help='Use asimov dataset (if blind)')
    parser.add_argument('--project', action='store_true', help='Project to 1D')
    parser.add_argument('--do2DInterpolation', action='store_true', help='interpolate v MH and MA')
    parser.add_argument('--fitParams', action='store_true', help='fit parameters')
    parser.add_argument('--higgs', type=int, default=125, choices=[125,300,750])
    parser.add_argument('--pseudoscalar', type=int, default=7, choices=[5,7,9,11,13,15,17,19,21])
    parser.add_argument('--yFitFunc', type=str, default='', choices=['G','V','CB','DCB','DG','DV','B','G2','G3','errG','L','MB'])
    parser.add_argument('--xRange', type=float, nargs='*', default=[4,25])
    parser.add_argument('--yRange', type=float, nargs='*', default=[])
    parser.add_argument('--tag', type=str, default='')
    parser.add_argument('--chi2Mass', type=int, default=0)
    parser.add_argument('--selection', type=str, default='')

    return parser.parse_args(argv)

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    args = parse_command_line(argv)

    create_datacard(args)

if __name__ == "__main__":
    status = main()
    sys.exit(status)
