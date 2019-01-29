import os
import sys
import logging

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.SetBatch()

from CombineLimits.Limits.Limits import Limits
from DevTools.Plotter.NtupleWrapper import NtupleWrapper

logging.basicConfig(level=logging.DEBUG, stream=sys.stderr, format='%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

class MonoHZZLimits(Limits):


    BACKGROUNDS = ['ZX','ggZZ','qqZZ','H']
    BINNAME = 'hzz4l'

    def __init__(self,histMap):
        super(MonoHZZLimits,self).__init__()

        self.histMap = histMap


    def setup(self):
        self.addBin(self.BINNAME)
        for bg in self.BACKGROUNDS:
            self.addProcess(bg)

        for bg in self.BACKGROUNDS:
            self.setExpected(bg,self.BINNAME,self.histMap[bg])

        self.setObserved(self.BINNAME,self.histMap['data'])

        mcProc = tuple([bg for bg in self.BACKGROUNDS if bg not in ['ZX']])

        # lumi: 2.5% 2016
        lumisyst = {
            (mcProc,tuple([self.BINNAME])) : 1.025,
        }
        self.addSystematic('lumi','lnN',systematics=lumisyst)

            

    def save(self,name='datacard',subdirectory=''):
        self.printCard('datacards_shape/MonoHZZ/{}'.format('{}/{}'.format(subdirectory,name) if subdirectory else name), processes=self.BACKGROUNDS, blind=False)


sigMap = {
    'ZX'  : [
            'DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8',
            'DYJetsToLL_M-10to50_TuneCP5_13TeV-amcatnloFXFX-pythia8',
            'ttWJets_TuneCP5_13TeV_madgraphMLM_pythia8',
            'ttZJets_TuneCP5_13TeV_madgraphMLM_pythia8',
            'TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8',
            'WWW_4F_TuneCP5_13TeV-amcatnlo-pythia8',
            'WWZ_4F_TuneCP5_13TeV-amcatnlo-pythia8',
            'WZG_TuneCP5_13TeV-amcatnlo-pythia8',
            'WZZ_TuneCP5_13TeV-amcatnlo-pythia8',
            'ZZZ_TuneCP5_13TeV-amcatnlo-pythia8',
            'WZTo3LNu_TuneCP5_13TeV-amcatnloFXFX-pythia8',
            #'WZTo3LNu_13TeV-powheg-pythia8',
            'WZTo2L2Q_13TeV_amcatnloFXFX_madspin_pythia8',
            'WWTo2L2Nu_NNPDF31_TuneCP5_13TeV-powheg-pythia8',
            ],
    'Z'   : [
            'DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8',
            'DYJetsToLL_M-10to50_TuneCP5_13TeV-amcatnloFXFX-pythia8',
            ],
    'TT'  : [
            #'TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8',
            #'TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8',
            #'TT_DiLept_TuneCP5_13TeV-amcatnlo-pythia8',
            'TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8',
            ],
    'WW' : [
            'WWTo2L2Nu_NNPDF31_TuneCP5_13TeV-powheg-pythia8',
            ],
    'WZ' : [
            'WZTo3LNu_TuneCP5_13TeV-amcatnloFXFX-pythia8',
            #'WZTo3LNu_13TeV-powheg-pythia8',
            'WZTo2L2Q_13TeV_amcatnloFXFX_madspin_pythia8',
            ],
    'ZZ' : [
            'ZZTo4L_13TeV_powheg_pythia8',
            'ZZTo2L2Nu_13TeV_powheg_pythia8',
            #'ZZTo2L2Q_13TeV_powheg_pythia8',
            'ZZTo2L2Q_13TeV_amcatnloFXFX_madspin_pythia8',
            'GluGluToContinToZZTo2e2mu_13TeV_MCFM701_pythia8',
            'GluGluToContinToZZTo2mu2tau_13TeV_MCFM701_pythia8',
            'GluGluToContinToZZTo2e2tau_13TeV_MCFM701_pythia8',
            'GluGluToContinToZZTo4e_13TeV_MCFM701_pythia8',
            'GluGluToContinToZZTo4mu_13TeV_MCFM701_pythia8',
            'GluGluToContinToZZTo4tau_13TeV_MCFM701_pythia8',
            ],
    'qqZZ' : [
            'ZZTo4L_13TeV_powheg_pythia8',
            'ZZTo2L2Nu_13TeV_powheg_pythia8',
            #'ZZTo2L2Q_13TeV_powheg_pythia8',
            'ZZTo2L2Q_13TeV_amcatnloFXFX_madspin_pythia8',
            ],
    'ggZZ' : [
            'GluGluToContinToZZTo2e2mu_13TeV_MCFM701_pythia8',
            'GluGluToContinToZZTo2mu2tau_13TeV_MCFM701_pythia8',
            'GluGluToContinToZZTo2e2tau_13TeV_MCFM701_pythia8',
            'GluGluToContinToZZTo4e_13TeV_MCFM701_pythia8',
            'GluGluToContinToZZTo4mu_13TeV_MCFM701_pythia8',
            'GluGluToContinToZZTo4tau_13TeV_MCFM701_pythia8',
            ],
    'TTV' : [
            'ttWJets_TuneCP5_13TeV_madgraphMLM_pythia8',
            'ttZJets_TuneCP5_13TeV_madgraphMLM_pythia8',
            ],
    'VVV' : [
            'WWW_4F_TuneCP5_13TeV-amcatnlo-pythia8',
            'WWZ_4F_TuneCP5_13TeV-amcatnlo-pythia8',
            'WZG_TuneCP5_13TeV-amcatnlo-pythia8',
            'WZZ_TuneCP5_13TeV-amcatnlo-pythia8',
            'ZZZ_TuneCP5_13TeV-amcatnlo-pythia8',
            ],
    'H'   : [
            'GluGluHToZZTo4L_M125_13TeV_powheg2_JHUGenV7011_pythia8',
            'VBF_HToZZTo4L_M125_13TeV_powheg2_JHUGenV7011_pythia8',
            'WminusH_HToZZTo4L_M125_13TeV_powheg2-minlo-HWJ_JHUGenV7011_pythia8',
            'WplusH_HToZZTo4L_M125_13TeV_powheg2-minlo-HWJ_JHUGenV7011_pythia8',
            'ttH_HToZZ_4LFilter_M125_13TeV_powheg2_JHUGenV7011_pythia8',
            'ZH_HToZZ_4LFilter_M125_13TeV_powheg2-minlo-HZJ_JHUGenV7011_pythia8',
            ],
    'data' : [
            'DoubleMuon',
            'DoubleEG',
            'MuonEG',
            'SingleMuon',
            'SingleElectron',
            ],
}

def sumHists(name,*hists):
    histlist = ROOT.TList()
    for hist in hists:
        histlist.Add(hist)
    hist = histlist[0].Clone(name)
    hist.Reset()
    hist.Merge(histlist)
    return hist

def getHist(proc,plotname,**kwargs):
    wrappers = kwargs.pop('wrappers',{})
    hists = [wrappers[s].getHist(plotname) for s in sigMap[proc]]
    hist = sumHists(proc+plotname,*hists)
    return hist

def getDatadrivenHists(plotname,**kwargs):
    wrappers = kwargs.pop('wrappers',{})
    histMap = getDatadrivenHistMap(plotname)
    hists = {}
    for proc in histMap:
        hs = [getHist(proc,p,wrappers=wrappers) for p in histMap[proc]]
        hists[proc] = sumHists(proc,*hs)
    return hists

def getDatadrivenHistMap(*plotnames):
    histMap = {}
    for s in samples + ['data','ZX']: histMap[s] = []
    for plot in plotnames:
        plotdirs = plot.split('/')
        for s in samples + ['data']: histMap[s] += ['/'.join(['4P0F']+plotdirs)]
        histMap['ZX'] += ['/'.join(['for4P0F',reg]+plotdirs) for reg in ['3P1F','2P2F']]
    return histMap


samples = ['ggZZ','qqZZ','H']
allsamples = ['TT','TTV','Z','WZ','VVV','ggZZ','qqZZ','H']
ddsamples = ['data'] + samples
sigMap['ZX'] = []
for s in ddsamples: sigMap['ZX'] += sigMap[s]

wrappers = {}
for proc in samples+['data']:
    for sample in sigMap[proc]:
        wrappers[sample] = NtupleWrapper('MonoHZZ',sample,new=True,version='94X',baseDirFlat='newflat_94X',baseDirProj='newflat_94X')


hists = getDatadrivenHists('hzz4l/met',wrappers=wrappers)

limits = MonoHZZLimits(hists)
limits.setup()
limits.save()
