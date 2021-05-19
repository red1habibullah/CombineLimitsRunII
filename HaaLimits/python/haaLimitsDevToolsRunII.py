import os
import sys
import logging
import itertools
import numpy as np
import argparse
import math
import glob

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
#from CombineLimitsRunII.HaaLimits.HaaLimitsNew import HaaLimits
from CombineLimitsRunII.HaaLimits.HaaLimits2DNew import HaaLimits2D

import CombineLimitsRunII.Plotter.CMS_lumi as CMS_lumi
import CombineLimitsRunII.Plotter.tdrstyle as tdrstyle

from RunIIDatasetUtils import *

tdrstyle.setTDRStyle()

#logging.basicConfig(level=logging.DEBUG, stream=sys.stderr, format='%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logging.basicConfig(level=logging.INFO, stream=sys.stdout, format='%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
ROOT.RooMsgService.instance().setGlobalKillBelow(ROOT.RooFit.WARNING)

noSigSys=True
noBgSys=True # fake rate does not allow to fluctuate within uncertainty
skipSignal = False
correlation = False
skipPlots = False

#############
### Setup ###
#############

varHists = {
    'mm' : 'invMassMuMu',
    'tt' : 'visDiTauMass',
    'h'  : 'visFourbodyMass',
    'hkf': 'hMassKinFit',
}


if noSigSys:
    sigSysType=[]

if noBgSys:
    bgSysType=[]

sysType = list(dict.fromkeys(sigSysType+bgSysType))
shifts = [u+s for u in sysType for s in ['Up','Down']]

hmasses = [125]

amasses = [4,5,7,9,10,11,12,13,14,15,17,18,19,20,21]
#amasses = [5, 7, 18, 20]
hamap = {
    125:amasses
    } 

signame = 'HToAAH{h}A{a}'
# ggsigname = 'ggHToAAH{h}A{a}'
# vbfsigname = 'vbfHToAAH{h}A{a}'

### Something that are not used up to Dec. 2020
systLabels = {
    'MuonEn': 'CMS_scale_m',
    'TauEn' : 'CMS_scale_t',
    'tau'   : 'CMS_eff_t',
    'lep'   : 'CMS_eff_m',
    'fake'  : 'CMS_fake_t',
    'btag'  : 'CMS_btag_comb',
    'pu'    : 'CMS_pu',
}
rebinning = {
    #'mm' : 5, # 10 MeV -> 50 MeV
    'mm' : 10, # 10 MeV -> 100 MeV
    #'mm' : 25, # 10 MeV -> 250 MeV
    'tt' : 1, # 100 MeV -> 100 MeV
    'h'  : 1, # 1 GeV -> 1 GeV
    'hkf': 1, # 1 GeV -> 5 GeV
}
qcdShifts = []
for muR in [0.5,1.0,2.0]:
    for muF in [0.5,1.0,2.0]:
        if muR/muF>=4 or muF/muR>=4: continue
        qcdShifts += ['muR{muR:3.1f}muF{muF:3.1f}'.format(muR=muR,muF=muF)]
qcdShifts = []

#shifts = []
#for s in shiftTypes:
#    shifts += [s+'Up', s+'Down']
#    if s in systLabels: systLabels[s+'Up'] = systLabels[s]+'Up'
#    if s in systLabels: systLabels[s+'Down'] = systLabels[s]+'Down'
#shifts += qcdShifts

def parse_command_line(argv):
    parser = argparse.ArgumentParser(description='Create datacard')

    parser.add_argument('fitVars', type=str, nargs='*', default=[])
    parser.add_argument('--unblind', action='store_true', help='Unblind the datacards')
    parser.add_argument('--decayMode', action='store_true', help='Split by decay mode')
    parser.add_argument('--sumDecayModes', type=int, nargs='*', default=[])
    parser.add_argument('--parametric', action='store_true', help='Create parametric datacards')
    parser.add_argument('--unbinned', action='store_true', help='Create unbinned datacards')
    parser.add_argument('--addSignal', action='store_true', help='Insert fake signal')
    parser.add_argument('--addControl', action='store_true', help='Add control')
    parser.add_argument('--asimov', action='store_true', help='Use asimov dataset (if blind)')
    parser.add_argument('--project', action='store_true', help='Project to 1D')
    parser.add_argument('--do2DInterpolation', action='store_true', help='interpolate v MH and MA')
    parser.add_argument('--fitParams', action='store_true', help='fit parameters')
    parser.add_argument('--doubleExpo', action='store_true', help='Use double expo')
    parser.add_argument('--higgs', type=int, default=125, choices=[125,300,750])
    parser.add_argument('--pseudoscalar', type=int, default=7, choices=[5,7,9,11,13,15,17,19,21])
    parser.add_argument('--yFitFunc', type=str, default='', choices=['G','V','CB','DCB','DG','DV','DVh','B','G2','G3','errG','L','MB'])
    parser.add_argument('--xRange', type=float, nargs='*', default=[2.5,25])
    parser.add_argument('--yRange', type=float, nargs='*', default=[0,1000])
    parser.add_argument('--tag', type=str, default='')
    parser.add_argument('--chi2Mass', type=int, default=0)
    parser.add_argument('--selection', type=str, default='')
    parser.add_argument('--channel', type=str, nargs='*', default=['TauMuTauHad'], choices=['TauMuTauE','TauETauHad','TauMuTauHad','TauHadTauHad'])

    return parser.parse_args(argv)

if __name__ == "__main__":
    argv = sys.argv[1:]
    args = parse_command_line(argv)

    initUtils(args)

    xVar=varHists[sys.argv[1]]
    yVar=varHists[sys.argv[2]]
    
    do2D = len(args.fitVars)==2
    var = args.fitVars
    
    xBinWidth = 0.05
    if do2D:
        yBinWidth = 0.25 if var[1]=='tt' else 10

    if do2D and var[1]=='tt': yRange = [0.75,30]
    if args.yRange: yRange = args.yRange
    xRange = args.xRange

    project = args.project
    doMatrix = False
    doParametric = args.parametric
    doUnbinned = args.unbinned
    chi2Mass = args.chi2Mass
    blind = not args.unblind
    addSignal = args.addSignal
    signalParams = {'h': args.higgs, 'a': args.pseudoscalar}
    wsname = 'w'
    channels=args.channel
    if doUnbinned and not doParametric:
        logging.error('Unbinned only supported with parametric option')
        raise

    if chi2Mass and 'hkf' not in var:
        logging.error('Trying to use non-kinematic fit with chi2 cut')
        raise

    if var[1]=='tt':
        print "Program will not run!"
        sys.exit()

    #global hmasses
    if not args.do2DInterpolation:
        hmasses = [h for h in hmasses if h in [125, 300, 750]]

    backgrounds = ['datadriven']
    
    signals=[signame.format(h='125',a=a) for a in hamap[125]]
    #signals = [signame.format(h=h,a=a) for h in hmasses[0] for a in amasses if a in hamap[h]]
    #ggsignals = [ggsigname.format(h=h,a=a) for h in hmasses for a in amasses if a in hamap[h]]
    #vbfsignals = [vbfsigname.format(h=h,a=a) for h in vbfhmasses for a in vbfamasses]
    signalToAdd = signame.format(**signalParams)

    
    ##############################
    ### Create/read histograms ###
    ##############################
    
    histMap = {}
    # The definitons of which regions match to which arguments
    # PP can take a fake rate datadriven estimate from FP, but FP can only take the observed values
    regionArgs = {
        'PP': {'region':'signalRegion','fakeRegion':'B','source':'B','sources':['A','C'],'fakeSources':['B','D'],},
        'FP': {'region':'sideBand','sources':['B','D'],},
    }
    modes = ['PP','FP']
    thesesamples = backgrounds
    if not skipSignal: thesesamples = backgrounds + signals
    print "thesesamples:", thesesamples, "modes:", modes, "shifts:", shifts, "var", var, "**regionArgs[PP]", regionArgs["PP"]

    j=0
    for channel in channels:
        for mode in modes:
            modeTag=mode
            mode=channel+'_'+mode
            histMap[mode] = {}
            for shift in ['']+shifts:
                histMap[mode][shift] = {}
                for proc in thesesamples:
                    logging.info('Getting {} {} {}'.format(mode,shift,proc))
                    if proc=='datadriven':
                        if 'PP' in mode:
                            histMap[mode][shift][proc] = getDatadrivenHist(proc,channel,doUnbinned=True,var=var,shift=shift,do2D=do2D,**regionArgs[modeTag])
                        #print histMap[mode][shift][proc]
                        else:
                            ### As datadriven so try to load appropriate RooDatasets ###
                            histMap[mode][shift][proc] = getDatadrivenHist('data',channel,doUnbinned=True,var=var,shift=shift,do2D=do2D,**regionArgs[modeTag])
                        #    print histMap[mode][shift][proc]
                    else:
                        if proc in signals:
                            oldXRange = xRange
                            xRange = [0,30]
                            histMap[mode][shift][proc] = getSignalHist(proc,channel,doUnbinned=True,var=var,shift=shift,do2D=do2D,**regionArgs[modeTag])

                        #print "histMap", mode, shift, proc, histMap[mode][shift][proc], histMap[mode][shift][proc].sumEntries('invMassMuMu>0 && invMassMuMu<30 && visFourbodyMass>0 && visFourbodyMass<1000')
                            
                        xRange = oldXRange
                    #print proc

                logging.info('Getting {} observed {}'.format(mode, shift))
                samples = backgrounds
                if addSignal: samples = backgrounds + [signalToAdd]
                hists = []
                histsNoSig = []
                #print "observed:",samples, blind
                for proc in samples:
                    j+=1
                    hists += [histMap[mode][shift][proc].Clone('hist'+str(j))]
                    j+=1
                    if proc!=signalToAdd:
                        histsNoSig += [histMap[mode][shift][proc].Clone('hist'+str(j))]
                #if doUnbinned:
                hist = sumDatasets('obs{}{}'.format(mode,shift),*hists)
                histNoSig = sumDatasets('obsNoSig{}{}'.format(mode,shift),*histsNoSig)
                
                j+=1
                histMap[mode][shift]['data'] = hist.Clone('hist'+str(j))
                j+=1
                histMap[mode][shift]['dataNoSig'] = histNoSig.Clone('hist'+str(j))


    for mode in ['control']:
        histMap[mode] = {}
        for shift in ['']:
            #shiftLabel = systLabels.get(shift,shift)
            histMap[mode][shift] = {}
            if shift: continue
            
            logging.info('Getting {} observed'.format(mode))
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
    #elif do2D and project:
    #    haaLimits = HaaLimits(histMap,name,do2DInterpolation=args.do2DInterpolation,doParamFit=args.fitParams)
    elif : #do2D:
        #print "JINGYU1", args.do2DInterpolation, args.fitParams
        haaLimits = HaaLimits2D(histMap,name,do2DInterpolation=args.do2DInterpolation,doParamFit=args.fitParams)
    else:
        logging.error('Unsupported fit vars: ',var)
        raise
    
    #print name -> unbinned_h/lowmassWith1DFits_TauETauHad
    if args.decayMode: haaLimits.REGIONS = modes
    if 'h' in var:
        haaLimits.YCORRELATION = correlation
    haaLimits.SKIPPLOTS = skipPlots
    haaLimits.SHIFTS = bgSysType
    haaLimits.SIGNALSHIFTS = sigSysType
    haaLimits.BACKGROUNDSHIFTS = bgSysType
    haaLimits.QCDSHIFTS = [systLabels.get(shift,shift) for shift in qcdShifts]
    haaLimits.AMASSES = amasses
    haaLimits.HMASSES = [chi2Mass] if chi2Mass else hmasses
    haaLimits.HAMAP = hamap
    haaLimits.XRANGE = xRange
    haaLimits.XBINNING = int((xRange[1]-xRange[0])/xBinWidth)
    haaLimits.XVAR = xVar
    haaLimits.CHANNELS = channels
    if do2D: 
        haaLimits.YVAR = yVar
        haaLimits.YRANGE = yRange
        haaLimits.YBINNING = int((yRange[1]-yRange[0])/yBinWidth)
        haaLimits.DOUBLEEXPO = args.doubleExpo
    print "xVar:", xVar, "xRange:", xRange, "yVar:", yVar, "yRange:", yRange
    if 'tt' in var: haaLimits.YLABEL = 'm_{#tau_{#mu}#tau_{h}}'
    if 'h' in var or 'hkf' in var: haaLimits.YLABEL = 'm_{#mu#mu#tau_{#mu}#tau_{h}}'
    haaLimits.initializeWorkspace()
    haaLimits.addControlModels()
    haaLimits.addBackgroundModels(fixAfterControl=True)
    #sys.exit()
    if not skipSignal:
        haaLimits.XRANGE = [0,30] # override for signal splines
        if project:
            haaLimits.addSignalModels(scale=scales)
        elif 'tt' in var:
            if args.yFitFunc:
                haaLimits.addSignalModels(scale=scales,yFitFuncFP=args.yFitFunc,yFitFuncPP=args.yFitFunc) # cutOffFP=0.0,cutOffPP=0.0)
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
    #sys.exit()
    if args.addControl: haaLimits.addControlData()
    haaLimits.addData(blind=blind,asimov=args.asimov,addSignal=args.addSignal,doBinned=not doUnbinned,**signalParams) # this will generate a dataset based on the fitted model
    haaLimits.setupDatacard(addControl=args.addControl,doBinned=not doUnbinned)
    haaLimits.addSystematics(addControl=args.addControl,doBinned=not doUnbinned)
    name = 'mmmt_{}_parametric'.format('_'.join(var))
    if args.unbinned: name += '_unbinned'
    if args.tag: name += '_{}'.format(args.tag)
    if args.addSignal: name += '_wSig'
    haaLimits.save(name=name)
    print "DONE!!!"
    
    #status = main()
    #sys.exit(status)
#/eos/uscms/store/user/rhabibul/HtoAA/HtoAA2017Deep/TauMuTauE/RooDatasets/Data/TauMuTauE_sideBand_MuIso_loose_EleId_loose.root
#/eos/uscms/store/user/rhabibul/HtoAA/HtoAA2017Deep/TauMuTauE/RooDatasets/DataDriven/TauMuTauE_signalRegion_MuIso_loose_EleId_loose.root
#/eos/uscms/store/user/rhabibul/HtoAA/HtoAA2017Deep/TauMuTauE/RooDatasets/SignalMC/TauMuTauE_HaaMC_am9_tightMuIso_tightEleId_signalRegion.root 
