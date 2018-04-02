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
from CombineLimits.HaaLimits.HaaLimits import HaaLimits
from CombineLimits.HaaLimits.HaaLimitsHMass import HaaLimitsHMass

logging.basicConfig(level=logging.DEBUG, stream=sys.stderr, format='%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

varHists = {
    'mm' : 'ammMass',
    'tt' : 'attMass',
    'h'  : 'hMass',
    'hkf': 'hMassKinFit',
}
varDatasets = {
    'mm' : 'ammMass_dataset',
}
varNames = {
    'mm' : 'amm_mass',
    'tt' : 'att_mass',
    'h'  : 'h_mass',
    'hkf': 'h_massKinFit',
}
varBinning = {
    'mm' : [42,4,25],
    'tt' : [60,0,60],
    'h'  : [50,0,1000],
    'hkf': [50,0,1000],
}
rebinning = {
    'mm' : 5, # 10 MeV -> 50 MeV
    'tt' : 1, # 100 MeV -> 100 MeV
    'h'  : 1, # 1 GeV -> 1 GeV
    'hkf': 1, # 1 GeV -> 5 GeV
}
#xRange = [2,25] # with jpsi
xRange = [4,25] # no jpsi
#xRange = [2.5,4.5] # jpsi only

hmasses = [125,300,750]
#hmasses = [125]
amasses = [5,7,9,11,13,15,17,19,21]
#amasses = [5,11,15,21]
    
signame = 'HToAAH{h}A{a}'

shiftTypes = ['lep','pu','fake','trig']
shiftTypes = []
shifts = []
for s in shiftTypes:
    shifts += [s+'Up', s+'Down']

#################
### Utilities ###
#################
def getHist(proc,**kwargs):
    scale = kwargs.pop('scale',1)
    shift = kwargs.pop('shift','')
    region = kwargs.pop('region','A')
    do2D = kwargs.pop('do2D',False)
    doUnbinned = kwargs.pop('doUnbinned',False)
    var = kwargs.pop('var',['mm'])
    wrappers = kwargs.pop('wrappers',{})
    if do2D:
        plot = '{}_{}'.format(*[varHists[v] for v in var])
    elif doUnbinned:
        plot = varDatasets[var[0]]
    else:
        plot = varHists[var[0]]
    plotname = 'region{}/{}'.format(region,plot)
    if do2D:
        hists = [wrappers[s+shift].getHist2D(plotname) for s in sampleMap[proc]]
    elif doUnbinned:
        hists = [wrappers[s+shift].getDataset(plotname) for s in sampleMap[proc]]
    else:
        hists = [wrappers[s+shift].getHist(plotname) for s in sampleMap[proc]]
    if doUnbinned:
        hist = sumDatasets(proc+region,*hists)
    else:
        hist = sumHists(proc+region,*hists)
        hist.Scale(scale)
    return hist

def getDatadrivenHist(**kwargs):
    shift = kwargs.pop('shift','')
    source = kwargs.pop('source','B')
    region = kwargs.pop('region','A')
    do2D = kwargs.pop('do2D',False)
    doUnbinned = kwargs.pop('doUnbinned',False)
    var = kwargs.pop('var',['mm'])
    wrappers = kwargs.pop('wrappers',{})
    if do2D:
        plot = '{}_{}'.format(*[varHists[v] for v in var])
    elif doUnbinned:
        plot = varDatasets[var[0]]
    else:
        plot = varHists[var[0]]
    plotname = 'region{}_fakeFor{}/{}'.format(source,region,plot)
    if do2D:
        hists = [wrappers[s+shift].getHist2D(plotname) for s in sampleMap['data']]
    elif doUnbinned:
        hists = [wrappers[s+shift].getDataset(plotname) for s in sampleMap['data']]
    else:
        hists = [wrappers[s+shift].getHist(plotname) for s in sampleMap['data']]
    if doUnbinned:
        hist = sumDatasets('data'+region+source,*hists)
    else:
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
    doUnbinned = kwargs.pop('doUnbinned',False)
    var = kwargs.pop('var',['mm'])
    wrappers = kwargs.pop('wrappers',{})
    if do2D:
        plot = '{}_{}'.format(*[varHists[v] for v in var])
    elif doUnbinned:
        plot = varDatasets[var[0]]
    else:
        plot = varHists[var[0]]
    applot = ['matrixP/region{}_for{}/{}'.format(source,region,plot) for source in sources]
    afplot = ['matrixF/region{}_for{}/{}'.format(source,region,plot) for source in sources]
    hists = []
    for s in sampleMap[proc]:
        if do2D:
            if doPrompt: hists += [wrappers[s+shift].getHist2D(plotname) for plotname in applot]
            if doFake: hists += [wrappers[s+shift].getHist2D(plotname) for plotname in afplot]
        elif doUnbinned:
            if doPrompt: hists += [wrappers[s+shift].getDataset(plotname) for plotname in applot]
            if doFake: hists += [wrappers[s+shift].getDataset(plotname) for plotname in afplot]
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
    doUnbinned = kwargs.pop('doUnbinned',False)
    var = kwargs.pop('var',['mm'])
    wrappers = kwargs.pop('wrappers',{})
    if do2D:
        plot = '{}_{}'.format(*[varHists[v] for v in var])
    elif doUnbinned:
        plot = varDatasets[var[0]]
    else:
        plot = varHists[var[0]]
    bpplot = ['matrixP/region{}_for{}_fakeFor{}/{}'.format(source,fakeRegion,region,plot) for source in fakeSources]
    bfplot = ['matrixF/region{}_for{}_fakeFor{}/{}'.format(source,fakeRegion,region,plot) for source in fakeSources]
    hists = []
    for s in sampleMap['data']:
        if do2D:
            if doPrompt: hists += [wrappers[s+shift].getHist2D(plotname) for plotname in bpplot]
            if doFake: hists += [wrappers[s+shift].getHist2D(plotname) for plotname in bfplot]
        elif doUnbinned:
            if doPrompt: hists += [wrappers[s+shift].getDataset(plotname) for plotname in bpplot]
            if doFake: hists += [wrappers[s+shift].getDataset(plotname) for plotname in bfplot]
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
    blind = not args.unblind
    addSignal = args.addSignal
    signalParams = {'h': args.higgs, 'a': args.pseudoscalar}
    wsname = 'w'
    var = args.fitVars
    
    if do2D and doParametric:
       logging.error('Parametric 2D fits are not yet supported')
       raise

    if doUnbinned and not doParametric:
        logging.error('Unbinned only supported with parametric option')
        raise

    #############
    ### Setup ###
    #############
    sampleMap = getSampleMap()
    
    backgrounds = ['datadriven']
    data = ['data']
    
    signals = [signame.format(h=h,a=a) for h in hmasses for a in amasses]
    signalToAdd = signame.format(**signalParams)

    
    wrappers = {}
    for proc in backgrounds+signals+data:
        if proc=='datadriven': continue
        for sample in sampleMap[proc]:
            wrappers[sample] = NtupleWrapper('MuMuTauTau',sample,new=True,version='80X')
            for shift in shifts:
                wrappers[sample+shift] = NtupleWrapper('MuMuTauTau',sample,new=True,version='80X',shift=shift)
    
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
                    # TODO: unbinned, get the RooDataHist from flattenener first
                    if mode=='PP':
                        if doMatrix:
                            histMap[mode][shift][proc] = getMatrixDatadrivenHist(doUnbinned=doUnbinned,var=var,wrappers=wrappers,shift=shift,do2D=do2D,**regionArgs[mode])
                        else:
                            histMap[mode][shift][proc] = getDatadrivenHist(doUnbinned=doUnbinned,var=var,wrappers=wrappers,shift=shift,do2D=do2D,**regionArgs[mode])
                    else:
                        if doMatrix:
                            histMap[mode][shift][proc] = getMatrixHist('data',doUnbinned=doUnbinned,var=var,wrappers=wrappers,shift=shift,do2D=do2D,**regionArgs[mode])
                        else:
                            histMap[mode][shift][proc] = getHist('data',doUnbinned=doUnbinned,var=var,wrappers=wrappers,shift=shift,do2D=do2D,**regionArgs[mode])
                else:
                    if doMatrix:
                        histMap[mode][shift][proc] = getMatrixHist(proc,doUnbinned=doUnbinned,var=var,wrappers=wrappers,shift=shift,do2D=do2D,**regionArgs[mode])
                    else:
                        histMap[mode][shift][proc] = getHist(proc,doUnbinned=doUnbinned,var=var,wrappers=wrappers,shift=shift,do2D=do2D,**regionArgs[mode])
                if do2D or doUnbinned:
                    pass # TODO, figure out how to rebin 2D
                else:
                    histMap[mode][shift][proc].Rebin(rebinning[var[0]])
            if shift: continue
            logging.info('Getting observed')
            samples = backgrounds
            if addSignal: samples = backgrounds + [signalToAdd]
            hists = []
            histsNoSig = []
            for proc in samples:
                hists += [histMap[mode][shift][proc].Clone()]
                if proc!=signalToAdd: histsNoSig += [histMap[mode][shift][proc].Clone()]
            if doUnbinned:
                hist = sumDatasets('obs{}{}'.format(mode,shift),*hists)
                histNoSig = sumDatasets('obsNoSig{}{}'.format(mode,shift),*histsNoSig)
            else:
                hist = sumHists('obs{}{}'.format(mode,shift),*hists)
                histNoSig = sumHists('obsNoSig{}{}'.format(mode,shift),*histsNoSig)
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
                hist = getHist('data',doUnbinned=doUnbinned,var=var,wrappers=wrappers,do2D=do2D,**regionArgs[mode])
                histMap[mode][shift]['data'] = hist.Clone()
                histMap[mode][shift]['dataNoSig'] = histNoSig.Clone()
                if do2D or doUnbinned:
                    pass
                else:
                    histMap[mode][shift]['data'].Rebin(rebinning[var[0]])
                    histMap[mode][shift]['dataNoSig'].Rebin(rebinning[var[0]])

    if var == ['mm']:
        haaLimits = HaaLimits(histMap,'unbinned' if args.unbinned else '')
    elif var == ['h'] or var == ['hkf']:
        haaLimits = HaaLimitsHMass(histMap,'unbinned' if args.unbinned else '')
    else:
        logging.error('Unsupported fit vars: ',var)
        raise
    haaLimits.AMASSES = amasses
    haaLimits.HMASSES = hmasses
    haaLimits.initializeWorkspace()
    haaLimits.addBackgroundModels()
    haaLimits.addSignalModels()
    haaLimits.addData()
    haaLimits.setupDatacard()
    haaLimits.addSystematics()
    name = 'mmmt_{}_parametric'.format('_'.join(var))
    if args.unbinned: name += '_unbinned'
    if args.addSignal: name += '_wSig'
    haaLimits.save(name=name)


def parse_command_line(argv):
    parser = argparse.ArgumentParser(description='Create datacard')

    parser.add_argument('fitVars', type=str, nargs='*', default=[])
    parser.add_argument('--unblind', action='store_true', help='Unblind the datacards')
    parser.add_argument('--parametric', action='store_true', help='Create parametric datacards')
    parser.add_argument('--unbinned', action='store_true', help='Create unbinned datacards')
    parser.add_argument('--addSignal', action='store_true', help='Insert fake signal')
    parser.add_argument('--higgs', type=int, default=125, choices=[125,300,750])
    parser.add_argument('--pseudoscalar', type=int, default=15, choices=[5,7,9,11,13,15,17,19,21])
    parser.add_argument('--tag', type=str, default='')

    return parser.parse_args(argv)

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    args = parse_command_line(argv)

    create_datacard(args)

if __name__ == "__main__":
    status = main()
    sys.exit(status)
