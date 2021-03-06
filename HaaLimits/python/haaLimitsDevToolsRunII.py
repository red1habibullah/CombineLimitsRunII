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

# Change integration precision
# BAD!!!
#ROOT.RooAbsReal.defaultIntegratorConfig().setEpsAbs(1e-6)
#ROOT.RooAbsReal.defaultIntegratorConfig().setEpsRel(1e-6)

#from DevTools.Plotter.NtupleWrapper import NtupleWrapper
#from DevTools.Utilities.utilities import *
#from DevTools.Plotter.haaUtils import *
#from DevTools.Plotter.xsec import getXsec
#from CombineLimits.HaaLimits.HaaLimits import HaaLimits
#from CombineLimits.HaaLimits.HaaLimits2D import HaaLimits2D
from CombineLimitsRunII.HaaLimits.HaaLimitsNew import HaaLimits
from CombineLimitsRunII.HaaLimits.HaaLimits2DNew import HaaLimits2D

import CombineLimitsRunII.Plotter.CMS_lumi as CMS_lumi
import CombineLimitsRunII.Plotter.tdrstyle as tdrstyle

from RunIISampleMaps import *
from RunIIDatasetUtils import *


tdrstyle.setTDRStyle()

#logging.basicConfig(level=logging.DEBUG, stream=sys.stderr, format='%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logging.basicConfig(level=logging.INFO, stream=sys.stdout, format='%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
ROOT.RooMsgService.instance().setGlobalKillBelow(ROOT.RooFit.WARNING)


testing = True
detailed = False
skipSignal = False
correlation = False
skipPlots = False

subtractSR = True

xRange =[2.5,25] # with jpsi
xRangeFull = [2.5,25]

yRange = [0,1000] # h, hkf

#hmasses = [125,300,750]
#hmasses = [125,200,250,300,400,500,750,1000]
if testing: hmasses = [125]
#if testing: hmasses = [300]
#if testing: hmasses = [750]
#amasses = [4,5,7,8,9,10,11,12,13,14,15,17,18,19,20,21]
amasses = [4,5,7,9,10,11,12,13,14,15,17,18,19,20,21]
#if testing: amasses = ['3p6',5,9,13,17,21]
#vbfhmasses = [125,300,750]
#vbfamasses = [5,9,15,21]
hamap = {
    #125 : [4,5,7,8,9,10,11,12,13,14,15,17,18,19,20,21],
    #125 : [4,5,10,11,20,21],
    #125:[4,10,20],
    #125:[10,21],
    #125:[4,5,10,11],
    #125:[4,5,7,8,10,11,12,13,14,15,17,19,20,21]
    125:[4,5,7,9,10,11,12,13,14,15,17,19,20,21]  
    #125:[14,15,17,18,19],
    #125:[9,18],
    } 


    # 200 : [5,9,15],
#     250 : [5,9,15],
#     300 : [5,7,9,11,13,15,17,19,21],
#     400 : [5,9,15],
#     500 : [5,9,15],
#     750 : [5,7,9,11,13,15,17,19,21],
#     1000: [5,9,15],
# }
    
channels=['TauETauHad','TauMuTauHad','TauMuTauE']
regions=['A','B','C','D']
regionsnew=['sideBand','signalRegion']
discriminators=['vvlooseDeepVSjet','vlooseDeepVSjet','looseDeepVSjet','mediumDeepVSjet','tightDeepVSjet','vtightDeepVSjet','vvtightDeepVSjet']
muIdList = ["loose", "medium", "tight"]
muIdLabel = ["looseMuIso", "mediumMuIso", "tightMuIso"]
eleIdList = ["loose", "medium", "tight"]
eleIdLabel = ["looseEleId", "mediumEleId", "tightEleId"]


signame = 'HToAAH{h}A{a}'
# ggsigname = 'ggHToAAH{h}A{a}'
# vbfsigname = 'vbfHToAAH{h}A{a}'

xVar='invMassMuMu'
yVar='visFourbodyMass'
xbnwdth=0.001

#ybnwdth=10
xBins=[int((xRange[1]-xRange[0])/xbnwdth),xRange[0],xRange[1]]
print xBins
#yBins= int((yRange[1]-yRange[0])/ybnwdth)




j=0

systLabels = {
    'MuonEn': 'CMS_scale_m',
    'TauEn' : 'CMS_scale_t',
    'tau'   : 'CMS_eff_t',
    'lep'   : 'CMS_eff_m',
    'fake'  : 'CMS_fake_t',
    'btag'  : 'CMS_btag_comb',
    'pu'    : 'CMS_pu',
}

shiftTypes = ['pu','fake','btag','tau','MuonEn','TauEn']#,'JetEn','UnclusteredEn']
#shiftTypes = ['pu','fake','btag','tau']#,'MuonEn','TauEn']#,'JetEn','UnclusteredEn']
#if testing: shiftTypes = ['fake','tau','btag','pu'] if detailed else []
if testing: shiftTypes = ['fake','tau'] if detailed else []
#if testing: shiftTypes = ['tau'] if detailed else []

signalShiftTypes = ['pu','btag','tau','MuonEn','TauEn']#,'JetEn','UnclusteredEn']
#signalShiftTypes = ['pu','btag','tau']#,'MuonEn','TauEn']#,'JetEn','UnclusteredEn']
#if testing: signalShiftTypes = ['tau','btag','pu'] if detailed else []
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
    if s in systLabels: systLabels[s+'Up'] = systLabels[s]+'Up'
    if s in systLabels: systLabels[s+'Down'] = systLabels[s]+'Down'
shifts += qcdShifts



varHists = {
    'mm' : 'invMassMuMu',
    'tt' : 'visDiTauMass',
    'h'  : 'visFourbodyMass',
    'hkf': 'hMassKinFit',
}
varNames = {
    'mm' : 'invMassMuMu',
    'tt' : 'visDiTauMass',
    'h'  : 'visFourbodyMass',
    'hkf': 'h_massKinFit',
}

#invMassMuMu,visDiTauMass,visFourbodyMass,fakeRateEfficiency


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

#xsec splines
smtfile  = ROOT.TFile.Open('/uscms_data/d3/rhabibul/CombineRunII/CMSSW_10_2_13/src/CombineLimitsRunII/Limits/data/Higgs_YR4_SM_13TeV.root')
bsmtfile = ROOT.TFile.Open('/uscms_data/d3/rhabibul/CombineRunII/CMSSW_10_2_13/src/CombineLimitsRunII/Limits/data/Higgs_YR4_BSM_13TeV.root')
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
def getControlDataset(File):
    selDatasets = {
        'invMassMuMu' : '{0}>{1} && {0}<{2}'.format(xVar,*xRange),
    }
    return getRooDataset(File,selection=selDatasets['invMassMuMu'],xRange=xRange,weight='w',xVar=xVar)

def getDataset(File,channel,type):
    thisxrange = xRange
    thisyrange = yRange
    selDatasets = {
        'invMassMuMu' : '{0}>{1} && {0}<{2}'.format(xVar,*thisxrange),
        'visFourbodyMass' : '{0}>{1} && {0}<{2}'.format(yVar,*thisyrange),
    }
    # if project:
    #     if 'hMass' in plotname:
    #         dataset = wrapper.getDataset(plotname,selection=' && '.join([selDatasets['x'],selDatasets['y'],hCut]),xRange=thisxrange,weight='w',yRange=thisyrange,project=xVar,xVar=xVar,yVar=yVar)
    #     elif 'attMass' in plotname:
    #         dataset = wrapper.getDataset(plotname,selection=' && '.join([selDatasets['x'],selDatasets['y']]),xRange=thisxrange,weight='w',yRange=thisyrange,project=xVar,xVar=xVar,yVar=yVar)
    # else:
    #     if 'hMass' in plotname or 'attMass' in plotname:
    #         dataset = wrapper.getDataset(plotname,selection=' && '.join([selDatasets['x'],selDatasets['y']]),xRange=thisxrange,weight='w',yRange=thisyrange,xVar=xVar,yVarOB=yVar)
    #     else:
    #         dataset = wrapper.getDataset(plotname,selection=selDatasets['x'],xRange=thisxrange,weight='w',xVar=xVar)
            #if 'SUSY' in sample and h==125 and '11' in sample:
            #    integral = dataset.sumEntries('{0}>{1} && {0}<{2}'.format(xVar,*thisxrange))
            #    print sample, plotname, integral
    if channel=="TauMuTauHad" or channel=="TauETauHad":
        if project and 'datadriven' in type:
            dataset =getRooDatasetFake(File,selection=' && '.join([selDatasets['invMassMuMu'],selDatasets['visFourbodyMass']]),xRange=thisxrange,weight='fakeRateEfficiency',yRange=thisyrange,project=xVar,xVar=xVar,yVar=yVar)  
        elif not project and 'datadriven' in type:
            dataset =getRooDatasetFake(File,selection=' && '.join([selDatasets['invMassMuMu'],selDatasets['visFourbodyMass']]),xRange=thisxrange,weight='fakeRateEfficiency',yRange=thisyrange,project='',xVar=xVar,yVar=yVar)
        elif not project and 'data' in type:
            dataset =getRooDataset(File,selection=' && '.join([selDatasets['invMassMuMu'],selDatasets['visFourbodyMass']]),xRange=thisxrange,weight='',yRange=thisyrange,project='',xVar=xVar,yVar=yVar)
        else:
            dataset =getRooDataset(File,selection=' && '.join([selDatasets['invMassMuMu'],selDatasets['visFourbodyMass']]),xRange=thisxrange,weight='eventWeight',yRange=thisyrange,project='',xVar=xVar,yVar=yVar)
    # else:
    #      dataset =getRooDataset(File,selection=selDatasets['invMassMuMu'],xRange=thisxrange,weight='w',xVar=xVar)  
    elif channel =="TauMuTauE":
        print File
        if 'datadriven' in type:
            print type
            dataset=getHisto(File,process='datadriven')
        elif 'data' in type:
            dataset= getHisto(File,process='data')
        else:
            dataset=getHisto(File,process='signal')
    else:
        raise ValueError('Channel Unknown in getDataset')
                
            
    
    global j
    j+=1
    return dataset.Clone('hist'+str(j))


selHists = {
    'invMassMuMu' : '{0}>{1} && {0}<{2}'.format(xVar,*xRange),
    'visFourbodyMass' : '{0}>{1} && {0}<{2}'.format(yVar,*yRange),
    }


def getControlHist(proc,**kwargs):
    wrappers = kwargs.pop('wrappers',{})
    doUnbinned = kwargs.pop('doUnbinned',False)
    #plot = 'invMassMuMu'
    #plotname = 'deltaR_iso/default/{}'.format(plot)
    #if doUnbinned:
    #    plotname += '_dataset'
    # if doUnbinned:
    #     hists = [getControlDataset(s) for s in SampleMap2017[proc]]
    #     if len(hists) >1:
    #         hist = sumDatasets(proc,*hists)
    #     else:
    #         hist = hists[0].Clone(proc)

    #else:
    # Takes far too long to do this unbinned
    hists = [getHistControl(s,Binning=xBins) for s in SampleMap2017[proc]]
    if len(hists) >1:
        hist = sumHists(proc,*hists)
    else:
        hist = hists[0].Clone(proc)
        #hist.Rebin(0.5)
    return hist

def getHist(proc,channel,**kwargs):
    scale = kwargs.pop('scale',1)
    shift = kwargs.pop('shift','')
    region = kwargs.pop('region','A')
    do2D = kwargs.pop('do2D',False)
    chi2Mass = kwargs.pop('chi2Mass',0)
    doUnbinned = kwargs.pop('doUnbinned',False)
    var = kwargs.pop('var',['mm'])
    #wrappers = kwargs.pop('wrappers',{})
    #dm = kwargs.pop('dm',-1)
    #sumDM = kwargs.pop('sumDecayModes',[])
    name = proc+region+shift
    #if dm>=0: name += str(dm)
    #def getHist2D(f,selection='1',xVar='invMassMuMu',yVar='visFourbodyMass',xBinning='1',yBinning='10')
    if do2D:
        plot = '{}_{}'.format(*[varHists[v] for v in var])
     #hist=ds.createHistogram(ds.get().find(xVar),ds.get().find(yVar),int(xBinning),int(yBinning),selection,ds.GetName())
    else:
        plot = varHists[var[0]]
    if doUnbinned:
        plot += '_dataset'
        plotname = 'region{}/{}'.format(region,plot)
    #if chi2Mass: plotname = 'chi2_{}/{}'.format(chi2Mass,plotname)
    #if dm>=0: plotname = 'dm{}/{}'.format(dm,plotname)
    #if sumDM:
    #    plotnames = ['dm{}/{}'.format(dm,plotname) for dm in sumDM]
    #else:
    #    plotnames = [plotname]
    if channel=="TauMuTauHad" or channel=="TauETauHad":
        if doUnbinned:
            hists = []
            histsname=[]
            #hists=[getDataset(s,proc) for s in SampleMap2017[proc] if '_'+region in s and  channels[0] in s]
            #hists=[getDataset(s,proc) for s in SampleMap2017[proc] if '_'+region in s and  channels[1] in s and '_'+discriminators[6] in s]
            hists=[getDataset(s,channel,proc) for s in SampleMap2017[proc] if '_'+region in s and  channel in s and '_'+discriminators[6] in s]
            #histsname=[s for s in SampleMap2017[proc] if '_'+region in s and  channels[1] in s and '_'+discriminators[6] in s]
            #print hists
            #print histsname
            #hist = sumDatasets(name,*hists)
            
            if len(hists)>1:
                hist = sumDatasets(name,*hists) 
            else:
                hist = hists[0].Clone(name)

        else:
            hists = []
            #for plotname in plotnames:
            if do2D:
                #hists = [wrappers[s+shift].getHist2D(plotname) for s in sampleMap[proc]]
                #hists = [getHist2D(s,selection=' && '.join([selHists['invMassMuMu'],selHists['visFourbodyMass']])) for s in SampleMap2017[proc] if '_'+region in s and channel[0] in s]
                hists = [getHist2D(s,selection=' && '.join([selHists['invMassMuMu'],selHists['visFourbodyMass']])) for s in SampleMap2017[proc] if '_'+region in s and channel in s and '_'+ discriminators[6] in s]  
                if len(hists)>1:
                    hist = sumHists(name,*hists)
                else:
                    hist = hists[0].Clone(name)
            else:
            #hists = [wrappers[s+shift].getHist(plotname) for s in sampleMap[proc]]
                hists=[getDataset(s) for s in SampleMap2017[proc] if '_'+region in s and channels[1] in s]
    elif channel=='TauMuTauE':
        if proc =='data':
            print "Channel TauMuTauE"
            print proc
            print region
            hists=[getDataset(s,channel,proc) for s in SampleMapNew2017[proc] if '_'+region in s and channel in s and 'MuIso'+'_'+muIdList[1]+'_'+'EleId'+'_'+eleIdList[2] in s]
            print "Histogram Loaded"
            if len(hists)>1:
                hist = sumHists(name,*hists)
            else:
                hist = hists[0].Clone(name)

        else:
            hists=[getDataset(s,channel,proc) for s in SampleMapNew2017[proc] if '_'+region in s and channel in s and muIdLabel[1]+'_'+eleIdLabel[2] in s]
            if len(hists)>1:
                hist = sumHists(name,*hists)
            else:
                hist = hists[0].Clone(name)
    else:
        raise ValueError('Channel Unknown in getHist')
    return hist

def getDatadrivenHist(proc,channel,**kwargs):
    shift = kwargs.pop('shift','')
    source = kwargs.pop('source','B')
    region = kwargs.pop('region','A')
    do2D = kwargs.pop('do2D',False)
    chi2Mass = kwargs.pop('chi2Mass',0)
    doUnbinned = kwargs.pop('doUnbinned',False)
    var = kwargs.pop('var',['mm'])
    #wrappers = kwargs.pop('wrappers',{})
    #dm = kwargs.pop('dm',-1)
    #sumDM = kwargs.pop('sumDecayModes',[])
    name = 'datadriven'+region+source+shift
    #if dm>=0: name += str(dm)
    if do2D:
        plot = '{}_{}'.format(*[varHists[v] for v in var])
    else:
        plot = varHists[var[0]]
   # if doUnbinned:
    #    plot += '_dataset'
    #plotname = 'region{}_fakeFor{}/{}'.format(source,region,plot)
    #if chi2Mass: plotname = 'chi2_{}/{}'.format(chi2Mass,plotname)
    #if dm>=0: plotname = 'dm{}/{}'.format(dm,plotname)
    #if sumDM:
    #    plotnames = ['dm{}/{}'.format(dm,plotname) for dm in sumDM]
    #else:
    #    plotnames = [plotname]
    if channel=='TauMuTauHad' or channel=='TauETauHad':
        if doUnbinned:
            hists = []
            histsname=[]
            #for plotname in plotnames:
            #hists=[getDataset(s,'data') for s in SampleMap2017['datadriven'] if '_'+region in s and channels[0] in s]
            #hists=[getDataset(s,'data') for s in SampleMap2017['datadriven'] if '_'+region in s and channels[1] in s and '_'+discriminators[6] in s]
            ### Loading with fakaRate?? ###
            hists=[getDataset(s,channel,proc) for s in SampleMap2017['datadriven'] if '_'+region in s and channel in s and '_'+discriminators[6] in s]

            #histsname=[s for s in SampleMap2017['datadriven'] if '_'+region in s and  channels[1] in s and '_'+discriminators[6] in s]
            #print histsname
            if len(hists) >1:
                hist = sumDatasets(name,*hists)
            else:
                hist = hists[0].Clone(name)
        else:
            hists = []
            #for plotname in plotnames:
            if do2D:
                #hists = [getHist2D(s,selection=' && '.join([selHists['invMassMuMu'],selHists['visFourbodyMass']])) for s in SampleMap2017[proc] if '_'+region in s and channel[0] in s]
                hists = [getHist2D(s,selection=' && '.join([selHists['invMassMuMu'],selHists['visFourbodyMass']])) for s in SampleMap2017[proc] if '_'+region in s and channel in s and '_'+discriminators[6] in s]
                #hists += [wrappers[s+shift].getHist2D(plotname) for s in sampleMap['datadriven'] if '_'+region in s and channels[1] in s]
            else:
                hists += [wrappers[s+shift].getHist(plotname) for s in sampleMap['datadriven'] if '_'+region in s and channels[3] in s] 
                #hist = sumHists(name,*hists)
    elif channel=='TauMuTauE':
        print 'here'
        hists=[getDataset(s,channel,proc) for s in SampleMapNew2017['datadriven'] if '_'+region in s and channel in s and 'MuIso'+'_'+muIdList[1]+'_'+'EleId'+'_'+eleIdList[2] in s]
        if len(hists) >1:
            hist = sumDatasets(name,*hists)
        else:
            hist = hists[0].Clone(name)
                
        
        #MuIso_loose_EleId_loose
    else:
        raise ValueError('Channel Unknown in getDatadrivenHist')
    
    return hist



def sumHists(name,*hists):
    global j
    j += 1
    histlist = ROOT.TList()
    for hist in hists:
        histlist.Add(hist)
    hist = histlist[0].Clone(name+str(j))
    hist.Reset()
    hist.Merge(histlist)
    return hist

def sumDatasets(name,*datasets):
    global j
    j += 1
    dataset = datasets[0].Clone(name+str(j))
    for d in datasets[1:]:
        dataset.append(d)
    #tempPlot('temp_{}'.format(name),dataset)
    return dataset

def tempPlot(name,dataset):

    x = ROOT.RooRealVar(xVar,xVar,*xRange)
    frame = x.frame()
    dataset.plotOn(frame)
    canvas = ROOT.TCanvas('c','c',800,600)
    frame.Draw()
    canvas.Print('{}.png'.format(name))



###############
### Control ###
###############

def create_datacard(args):
    global j
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
    channel=args.channel
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

    xBinWidth = 0.05
    if do2D:
        yBinWidth = 0.25 if var[1]=='tt' else 10

    global hmasses
    if not args.do2DInterpolation:
        hmasses = [h for h in hmasses if h in [125, 300, 750]]

    #############
    ### Setup ###
    #############
    SampleMap2017 = getSampleMap2017()
    
    SampleMapNew2017 = getSampleMapNew2017()
    backgrounds = ['datadriven']
    data = ['data']
    
    signals=[signame.format(h='125',a=a) for a in hamap[125]]
    #signals = [signame.format(h=h,a=a) for h in hmasses[0] for a in amasses if a in hamap[h]]
    #ggsignals = [ggsigname.format(h=h,a=a) for h in hmasses for a in amasses if a in hamap[h]]
    #vbfsignals = [vbfsigname.format(h=h,a=a) for h in vbfhmasses for a in vbfamasses]
    signalToAdd = signame.format(**signalParams)

    
    # wrappers = {}
    # allsamples = backgrounds
    # if not skipSignal: allsamples = allsamples + signals + ggsignals + vbfsignals
    # allsamples = allsamples + data
    # for proc in allsamples:
    #     if proc=='datadriven': continue
    #     for sample in sampleMap[proc]:
    #         wrappers[sample] = NtupleWrapper('MuMuTauTau',sample,new=True,version='80X')
    #         for shift in shifts:
    #             wrappers[sample+shift] = NtupleWrapper('MuMuTauTau',sample,new=True,version='80X',shift=shift)

    # wrappers_mm = {}
    # for proc in data:
    #     for sample in sampleMap[proc]:
    #         wrappers_mm[sample] = NtupleWrapper('MuMu',sample,new=True,version='80X')
    
    ##############################
    ### Create/read histograms ###
    ##############################
    
    histMap = {}
    # The definitons of which regions match to which arguments
    # PP can take a fake rate datadriven estimate from FP, but FP can only take the observed values
    regionArgs = {
        #TODO Decide a common naming scenario on which everyone agrees upor
        # 'PP': {'region':'A','fakeRegion':'B','source':'B','sources':['A','C'],'fakeSources':['B','D'],},
        # 'FP': {'region':'B','sources':['B','D'],},
        'PP': {'region':'signalRegion','fakeRegion':'B','source':'B','sources':['A','C'],'fakeSources':['B','D'],},
        'FP': {'region':'sideBand','sources':['B','D'],},
    }
    modes = ['PP','FP']
    thesesamples = backgrounds
    if not skipSignal: thesesamples = backgrounds + signals
    for mode in modes:
        histMap[mode] = {}
        for shift in ['']+shifts:
            #shiftLabel = systLabels.get(shift,shift)
            histMap[mode][shift] = {}
            for proc in thesesamples:
                logging.info('Getting {} {} {}'.format(mode,proc,shift))
                if proc=='datadriven':
                    if 'PP' in mode:
                        #if doMatrix:
                           # histMap[mode][shiftLabel][proc] = getMatrixDatadrivenHist(doUnbinned=True,var=var,wrappers=wrappers,shift=shift,do2D=do2D,chi2Mass=chi2Mass,**regionArgs[mode])
                        #else:
                        #histMap[mode][shift][proc] = getDatadrivenHist(doUnbinned=True,var=var,shift=shift,**regionArgs[mode])
                        histMap[mode][shift][proc] = getDatadrivenHist(proc,channel,doUnbinned=True,var=var,shift=shift,do2D=do2D,**regionArgs[mode])

                    else:
                        # if doMatrix:
                        #     histMap[mode][shiftLabel][proc] = getMatrixHist('data',doUnbinned=True,var=var,wrappers=wrappers,shift=shift,do2D=do2D,chi2Mass=chi2Mass,**regionArgs[mode]
                                                                            
                        #histMap[mode][shift][proc] = getHist('data',doUnbinned=True,var=var,shift=shift,do2D=do2D,**regionArgs[mode])
                        ### As datadriven so try to load appropriate RooDatasets ###
                        histMap[mode][shift][proc] = getHist('data',channel,doUnbinned=True,var=var,shift=shift,do2D=do2D,**regionArgs[mode])

                       # histMap[mode][shift][proc] = getHist('data',doUnbinned=True,var=var,shift=shift,**regionArgs[mode])
                else:
                    if proc in signals:
                    #     newproc = 'gg'+proc
                    # else:
                    #     newproc = proc
                    # override xRange for signal only
                        oldXRange = xRange
                        xRange = [0,30]
                    # if doMatrix:
                    #     histMap[mode][shiftLabel][proc] = getMatrixHist(newproc,doUnbinned=True,var=var,wrappers=wrappers,shift=shift,do2D=do2D,chi2Mass=chi2Mass,**regionArgs[mode])
                    # else:
                        #histMap[mode][shift][proc] = getHist(proc,doUnbinned=True,var=var,shift=shift,**regionArgs[mode])
                        histMap[mode][shift][proc] = getHist(proc,channel,doUnbinned=True,var=var,shift=shift,do2D=do2D,**regionArgs[mode])
                        
                    xRange = oldXRange
                #if do2D or doUnbinned:
                #    pass # TODO, figure out how to rebin 2D
                #else:
                #    histMap[mode][shiftLabel][proc].Rebin(rebinning[var[0]])
            #if shift: continue
            logging.info('Getting observed')
            samples = backgrounds
            if addSignal: samples = backgrounds + [signalToAdd]
            hists = []
            histsNoSig = []
            for proc in samples:
                j+=1
                hists += [histMap[mode][shift][proc].Clone('hist'+str(j))]
                j+=1
                if proc!=signalToAdd: histsNoSig += [histMap[mode][shift][proc].Clone('hist'+str(j))]
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
                j+=1
                histMap[mode][shift]['data'] = hist.Clone('hist'+str(j))
                j+=1
                histMap[mode][shift]['dataNoSig'] = histNoSig.Clone('hist'+str(j))
            else:
                #hist = getHist('data',doUnbinned=True,var=var,wrappers=wrappers,do2D=do2D,chi2Mass=chi2Mass,**regionArgs[mode])
                #histMap[mode][shift][proc] = getHist(proc,doUnbinned=True,var=var,shift=shift,**regionArgs[mode])
                histMap[mode][shift][proc] = getHist(proc,doUnbinned=True,var=var,shift=shift,do2D=do2D,**regionArgs[mode])

                j+=1
                histMap[mode][shift]['data'] = hist.Clone('hist'+str(j))
                j+=1
                histMap[mode][shift]['dataNoSig'] = histNoSig.Clone('hist'+str(j))
                #if do2D or doUnbinned:
                #    pass
                #else:
                #    histMap[mode][shiftLabel]['data'].Rebin(rebinning[var[0]])
                #    histMap[mode][shiftLabel]['dataNoSig'].Rebin(rebinning[var[0]])

    for mode in ['control']:
        histMap[mode] = {}
        for shift in ['']:
            #shiftLabel = systLabels.get(shift,shift)
            histMap[mode][shift] = {}
            for proc in backgrounds:
                logging.info('Getting {} {}'.format(proc,shift))
                if proc=='datadriven':
                    hist = getControlHist('datadriven-control',doUnbinned=doUnbinned,var=var)
                    # if subtractSR:
                    #     # subtract off the signal region and sideband from the control region
                    #     for mode2 in modes:
                    #         histsub = getHist('data',doUnbinned=False,var=var,wrappers=wrappers,do2D=False,chi2Mass=chi2Mass,**regionArgs[mode2])
                    #         histsub.Rebin(histsub.GetNbinsX()/hist.GetNbinsX())
                    #         hist.Add(histsub,-1)
                    # histMap[mode][shiftLabel][proc] = hist
            if shift: continue
            logging.info('Getting observed')
            hist = getControlHist('control',doUnbinned=doUnbinned,var=var)
            # if subtractSR:
            #     # subtract off the signal region and sideband from the control region
            #     for mode2 in modes:
            #         histsub = getHist('data',doUnbinned=False,var=var,wrappers=wrappers,do2D=False,chi2Mass=chi2Mass,**regionArgs[mode2])
            #         histsub.Rebin(histsub.GetNbinsX()/hist.GetNbinsX())
            #         hist.Add(histsub,-1)
            j+=1
            histMap[mode][shift]['data'] = hist.Clone('hist'+str(j))
            j+=1
            histMap[mode][shift]['dataNoSig'] = hist.Clone('hist'+str(j))

    # rescale signal
    scales = {}
    for proc in signals:
        gg = getXsec(proc,'gg')
        vbf = getXsec(proc,'vbf')
        # divide out H cross section from sample
        # it was gg only, we will scale to gg+vbf with acceptance correction in the HaaLimits class
        #scale = 1./1.
        scale= 1./gg
        scales[proc] = scale
        #print proc, gg,scale #vbf


    # before doing anything print out integrals to make sure things are okay
    #h=125
    #a=10
    #SIGNAME = 'HToAAH{h}A{a}'
    #for s in ['']+[systLabels.get(shift,shift) for shift in shiftTypes]:
    #    if s:
    #        integral = histMap['PP'][s+'Up'][SIGNAME.format(h=h,a=a)].sumEntries('{0}>{1} && {0}<{2}'.format(xVar,*xRange))
    #        print s, 'Up', integral
    #        integral = histMap['PP'][s+'Down'][SIGNAME.format(h=h,a=a)].sumEntries('{0}>{1} && {0}<{2}'.format(xVar,*xRange))
    #        print s, 'Down', integral
    #    else:
    # integral = histMap['FP'][''][SIGNAME.format(h=h,a=a)].sumEntries('{0}>{1} && {0}<{2}'.format(xVar,*xRange))
    # print 'central X:', integral
    # integralY = histMap['FP'][''][SIGNAME.format(h=h,a=a)].sumEntries('{0}>{1} && {0}<{2}'.format(yVar,*yRange))
    # print 'central Y:', integralY
    # #return
    # print 'RooDataset', (histMap['FP'][''][SIGNAME.format(h=h,a=a)]).Print('v')
    
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
    if args.decayMode: haaLimits.REGIONS = modes
    if 'h' in var:
        haaLimits.YCORRELATION = correlation
    haaLimits.SKIPPLOTS = skipPlots
    haaLimits.SHIFTS = [systLabels.get(shift,shift) for shift in shiftTypes]
    haaLimits.SIGNALSHIFTS = [systLabels.get(shift,shift) for shift in signalShiftTypes]
    haaLimits.BACKGROUNDSHIFTS = [systLabels.get(shift,shift) for shift in backgroundShiftTypes]
    haaLimits.QCDSHIFTS = [systLabels.get(shift,shift) for shift in qcdShifts]
    haaLimits.AMASSES = amasses
    haaLimits.HMASSES = [chi2Mass] if chi2Mass else hmasses
    haaLimits.HAMAP = hamap
    haaLimits.XRANGE = xRange
    haaLimits.XBINNING = int((xRange[1]-xRange[0])/xBinWidth)
    haaLimits.XVAR = xVar
    if do2D: 
        haaLimits.YVAR = yVar
        haaLimits.YRANGE = yRange
        haaLimits.YBINNING = int((yRange[1]-yRange[0])/yBinWidth)
        haaLimits.DOUBLEEXPO = args.doubleExpo
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
                haaLimits.addSignalModels(scale=scales,yFitFuncFP='DV',yFitFuncPP='DV')#,cutOffFP=0.0,cutOffPP=0.0)
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
    parser.add_argument('--decayMode', action='store_true', help='Split by decay mode')
    parser.add_argument('--sumDecayModes', type=int, nargs='*', default=[])
    parser.add_argument('--parametric', action='store_true', help='Create parametric datacards')
    parser.add_argument('--unbinned', action='store_true', help='Create unbinned datacards')
    parser.add_argument('--addSignal', action='store_true', help='Insert fake signal')
    parser.add_argument('--addControl', action='store_true', help='Add control channel')
    parser.add_argument('--asimov', action='store_true', help='Use asimov dataset (if blind)')
    parser.add_argument('--project', action='store_true', help='Project to 1D')
    parser.add_argument('--do2DInterpolation', action='store_true', help='interpolate v MH and MA')
    parser.add_argument('--fitParams', action='store_true', help='fit parameters')
    parser.add_argument('--doubleExpo', action='store_true', help='Use double expo')
    parser.add_argument('--higgs', type=int, default=125, choices=[125,300,750])
    parser.add_argument('--pseudoscalar', type=int, default=7, choices=[5,7,9,11,13,15,17,19,21])
    parser.add_argument('--yFitFunc', type=str, default='', choices=['G','V','CB','DCB','DG','DV','B','G2','G3','errG','L','MB'])
    parser.add_argument('--xRange', type=float, nargs='*', default=[2.5,25])
    parser.add_argument('--yRange', type=float, nargs='*', default=[])
    parser.add_argument('--tag', type=str, default='')
    parser.add_argument('--chi2Mass', type=int, default=0)
    parser.add_argument('--selection', type=str, default='')
    parser.add_argument('--channel', type=str, default='TauMuTauHad', choices=['TauMuTauE','TauETauHad','TauMuTauHad','TauHadTauHad'])

    return parser.parse_args(argv)

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    args = parse_command_line(argv)

    create_datacard(args)

if __name__ == "__main__":
    status = main()
    sys.exit(status)
#/eos/uscms/store/user/rhabibul/HtoAA/HtoAA2017Deep/TauMuTauE/RooDatasets/Data/TauMuTauE_sideBand_MuIso_loose_EleId_loose.root
#/eos/uscms/store/user/rhabibul/HtoAA/HtoAA2017Deep/TauMuTauE/RooDatasets/DataDriven/TauMuTauE_signalRegion_MuIso_loose_EleId_loose.root
#/eos/uscms/store/user/rhabibul/HtoAA/HtoAA2017Deep/TauMuTauE/RooDatasets/SignalMC/TauMuTauE_HaaMC_am9_tightMuIso_tightEleId_signalRegion.root 
