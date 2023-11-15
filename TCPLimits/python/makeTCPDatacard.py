import os
import sys
import logging

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.SetBatch()

from CombineLimitsRunII.Limits.TCPLimits import Limits

class TCPLimits(Limits):

    BACKGROUNDS = ['']
    BINS = ['']
    SIGMASSES = ['']
    FFUNCERT = ['']

    SIGNALS = ['']
    SIGNALTXT = ''

    ffUncert = [u+s for u in FFUNCERT for s in ['Up','Down']]

    def __init__(self,histMap):
        super(TCPLimits,self).__init__()

        self.histMap = histMap
        '''
        Required arguments:
            histMap = histogram map. the structure should be:
                histMap[region][process][shift] = ROOT.TH1()
                where:
                    region  : 'MuTau_SR_2017' or 'MuMu_Control_2017' for signal and control regions, respectively
                    shift   : '', 'shiftName', 'shiftNameUp', or 'shiftNameDown'
                        ''                   : central value
                        'shiftName'          : a symmetric shift (ie, jet resolution)
                        'shiftName[Up,Down]' : an asymmetric shift (ie, fake rate, lepton efficiencies, etc)
                        shiftName            : the name the uncertainty will be given in the datacard
                    process : the name of the process
                        signal must be of the form 'ALP_Ntuple_m_{mass}_htj_100to400'
                        data = 'data'
                        background = 'datadriven'
        '''

    def setup(self):
        for b in self.BINS:
            self.addBin(b)
        for bg in self.BACKGROUNDS:
            self.addProcess(bg)
        self.addProcess(self.SIGNALTXT, True)

        for b in self.BINS:
            ## Backgrounds
            for bg in self.BACKGROUNDS:
                self.setExpected(bg,b,self.histMap[b][bg][''])
            ##  Signals
            if not 'Control' in b:
                self.setExpected(self.SIGNALTXT, b, -1)
                self.addShape(b,self.SIGNALTXT,'{}$MASS_htj_100to400_{}'.format(self.SIGNALTXT,b))
                    
        for b in self.BINS:
            self.setObserved(b,-1)

        mcProc = tuple([bg for bg in self.BACKGROUNDS+[self.SIGNALTXT] if bg not in ['QCD']])
        lumisyst = {
            (mcProc,tuple(self.BINS)) : 1.025,
        }
        self.addSystematic('lumi_2017','lnN',systematics=lumisyst)

        ffsyst = {}
        basename = FFUNCERT[0]
        ffsyst[(('QCD',),('MuTau_SR_2017_OS_Boost_Mass',))] = (basename+'Up', basename+'Down')
        self.addSystematic('ff2017','shape',systematics=ffsyst)

        for b in self.BINS:
            self.addRateParam('rateDY',b,'DYJetsToLL')

    def save(self,name='datacard',subdirectory=''):
        self.printCard('datacards_shape/TCP/{}'.format('{}/{}'.format(subdirectory,name) if subdirectory else name), processes=self.BACKGROUNDS+[self.SIGNALTXT], blind=True, addSignal=False, saveWorkspace=False)


if __name__ == "__main__":

    BACKGROUNDS = ['WJetsToLNu','ST','TT','Diboson','DYJetsToLL','QCD']
    BINNAMES = ['MuTau_SR_2017_OS_Boost_Mass', 'MuMu_Control_2017_OS_Boost_Mass']
    SIGMASSES = ['15','20','30','40','50','60']
    SIGNALS = ['ALP_Ntuple_m_{}_htj_100to400'.format(m) for m in SIGMASSES]
    FFUNCERT = ['ff2017']

    ffUncert = [u+s for u in FFUNCERT for s in ['Up','Down']]

    filename = "TCP_2017_datacard"

    filesave = ROOT.TFile(filename+'.root','RECREATE')
    
    histmap={}

    for b in BINNAMES:
        histmap[b] = {}
        
        for process in BACKGROUNDS + SIGNALS:
            histmap[b][process] = {}

    for b in BINNAMES:
        fin = ROOT.TFile('h_{}_studyCRwSVFit_v7.root'.format(b),'r')
        ## Backgrounds
        for process in BACKGROUNDS:
            ## ff uncertainty 
            if 'SR' in b and 'QCD' in process:
                for uncert in ['']+ffUncert:
                    if uncert == '': uncertTxt = ''
                    else: uncertTxt = '_'+uncert
                    finname = '{}_{}{}'.format(process,b,uncertTxt)
                    histmap[b][process][uncert] = fin.Get(finname)
                    histmap[b][process][uncert].SetDirectory(0)
            ## everything else
            else:
                for uncert in ['']:
                    if uncert == '': uncertTxt = ''
                    else: uncertTxt = '_'+uncert
                    finname = '{}_{}{}'.format(process,b,uncertTxt)
                    histmap[b][process][uncert] = fin.Get(finname)
                    histmap[b][process][uncert].SetDirectory(0)
        ## Signals
        if 'SR' in b:
            for process in SIGNALS:
                for uncert in ['']:
                    if uncert == '': uncertTxt = ''
                    else: uncertTxt = '_'+uncert
                    histmap[b][process][''] = fin.Get('{}_{}'.format(process,b))
                    histmap[b][process][''].SetDirectory(0)
        fin.Close()
        
            
    limits = TCPLimits(histmap)
    limits.BACKGROUNDS = BACKGROUNDS
    limits.BINS = BINNAMES
    limits.SIGMASSES = SIGMASSES
    limits.SIGNALS = SIGNALS
    limits.SIGNALTXT = 'ALP_Ntuple_m_'
    limits.setup()
    limits.save(filename)

    filesave = ROOT.TFile('datacards_shape/TCP/{}.root'.format(filename),'UPDATE')
    for b in histmap.keys():
        for process in histmap[b].keys():
            for uncert in histmap[b][process].keys():
                if not uncert == '' or 'ALP' in process:
                    histmap[b][process][uncert].Write()
    filesave.Close()
            
            
                

