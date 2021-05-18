import logging
import os
import sys
import glob
import json
import pickle


import ROOT
ROOT.gROOT.SetBatch(ROOT.kTRUE)
ROOT.gROOT.ProcessLine("gErrorIgnoreLevel = 2001;")

from RunIISampleMaps import *

#selHists = {
#    'invMassMuMu' : '{0}>{1} && {0}<{2}'.format(xVar,*xRange),
#    'visFourbodyMass' : '{0}>{1} && {0}<{2}'.format(yVar,*yRange),
#}

def initUtils(args):
    global xRange
    global yRange
    global project
    yRange = args.yRange
    xRange = args.xRange
    project = args.project

###### Utility to get Roodatasets ########################
def getRooDataset(f,selection='1',weight='',xRange=[],yRange=[],project='',xVar='invMassMuMu',yVar='visFourbodyMass',shift=''):
    '''Get a RooDataset'''
    file=ROOT.TFile.Open(f)
    dsname='dataColl'
    ds=file.Get(dsname)
    #print ds
    args=ds.get()
    "Getting RooDataset"
    #print f, xRange, yRange, selection, project
    if xRange: args.find('invMassMuMu').setRange(*xRange)
    if yRange: args.find('visFourbodyMass').setRange(*yRange)
    if xVar!='invMassMuMu': args.find('invMassMuMu').SetName(xVar)
    if yVar!='visFourbodyMass':args.find('visFourbodyMass').SetName(yVar)
    ds = ROOT.RooDataSet(ds.GetName(),ds.GetTitle(),ds,args,selection,weight)
    if project: ds = getattr(ds,'reduce')(ROOT.RooArgSet(ds.get().find(project)))
    #print ds.sumEntries('invMassMuMu>0 && invMassMuMu<30 && visFourbodyMass>0 && visFourbodyMass<1000')
    return ds


def getRooDatasetFake(f,selection='1',weight='fakeRateEfficiency',xRange=[],yRange=[],project='',xVar='invMassMuMu',yVar='visFourbodyMass'):
    '''Get a DataDriven RooDataset'''
    file=ROOT.TFile.Open(f)
    ds=file.Get('dataColl')
    args=ds.get()
    if xRange: args.find('invMassMuMu').setRange(*xRange)
    if yRange: args.find('visFourbodyMass').setRange(*yRange)
    if xVar!='invMassMuMu': args.find('invMassMuMu').SetName(xVar)
    if yVar!='visFourbodyMass':args.find('visFourbodyMass').SetName(yVar)
    ds = ROOT.RooDataSet(ds.GetName(),ds.GetTitle(),ds,args,selection,weight)
    if project: ds = getattr(ds,'reduce')(ROOT.RooArgSet(ds.get().find(project)))
    return ds

###### Utility to get Histos ########################  
def getHist2D(f,selection='1',xVar='invMassMuMu',yVar='visFourbodyMass',xBinning='',yBinning=''):
    '''Get a 2D Histogram from RooDataset'''
    file=ROOT.TFile.Open(f)
    ds=file.Get('dataColl')
    hist=ROOT.TH2F()
    hist=ds.createHistogram(ds.get().find(xVar),ds.get().find(yVar),int(xBinning),int(yBinning),selection,ds.GetName())
    hist.SetDirectory(ROOT.gROOT) 
    return hist

def getHistControl(f,selection='1',xVar='invMassMuMu',Binning='1'):
    ''' Get a 1D Control Histogram from RooDataset'''
    file=ROOT.TFile.Open(f)
    ds=file.Get('dataColl')
    args=ds.get()
    ds = ROOT.RooDataSet(ds.GetName(),ds.GetTitle(),ds,args,selection)
    hist=ROOT.TH1F()
    hist=ROOT.RooAbsData.createHistogram(ds,ds.GetName(),ds.get().find(xVar),ROOT.RooFit.Binning(int(Binning[0]),float(Binning[1]),float(Binning[2])))
    hist.SetDirectory(ROOT.gROOT)
    return hist

def getHisto(f,do2D,channel,xVar='invMassMuMu',process=''):
    ''' Get Histogram directly from file '''
    if do2D: xVar='invMassMuMuVisMassMuMuTauTau'
    
    if process == "data":
        xVarnew=xVar+"3P1F1Only"
    elif process =="datadriven":
        if channel == "TauMuTauE":
            xVarnew=xVar+"3P1F1"
        else:
            xVarnew=xVar+"3P1F"
    else:
        xVarnew=xVar
    file=ROOT.TFile.Open(f)
    #print f, xVarnew
    histo=file.Get(xVarnew)
    #print histo
    histo.SetDirectory(ROOT.gROOT)
    #print hist
    return histo
    

#################
### Utilities ###
#################
def getDataset(File,channel,type,shift,do2D,xVar='invMassMuMu',yVar='visFourbodyMass'):
    thisxrange = xRange
    thisyrange = yRange
    selDatasets = {
        'invMassMuMu' : '{0}>{1} && {0}<{2}'.format(xVar,*thisxrange),
        'visFourbodyMass' : '{0}>{1} && {0}<{2}'.format(yVar,*thisyrange),
    }

    print "getDataset:", type
    print File
    if channel=="TauMuTauHad" or channel=="TauETauHad" or channel=="TauHadTauHad" or channel == "TauHadTauHad_2017" or channel == "TauHadTauHad_2016" or channel == "TauHadTauHad_2018" or channel == "TauMuTauHad_2017" or channel == "TauMuTauHad_2017Cut" or channel == "TauMuTauHad_2017CutV2":
        if project and 'datadriven' in type:
            dataset =getRooDatasetFake(File,selection=' && '.join([selDatasets['invMassMuMu'],selDatasets['visFourbodyMass']]),xRange=thisxrange,weight='fakeRateEfficiency',yRange=thisyrange,project=xVar,xVar=xVar,yVar=yVar)
        # For FP region
        elif not project and 'datadriven' in type:
            dataset =getRooDatasetFake(File,selection=' && '.join([selDatasets['invMassMuMu'],selDatasets['visFourbodyMass']]),xRange=thisxrange,weight='fakeRateEfficiency',yRange=thisyrange,project='',xVar=xVar,yVar=yVar)
        # For PP region
        elif not project and 'data' in type:
            dataset =getRooDataset(File,selection=' && '.join([selDatasets['invMassMuMu'],selDatasets['visFourbodyMass']]),xRange=thisxrange,weight='',yRange=thisyrange,project='',xVar=xVar,yVar=yVar)
        else:
            weightname='eventWeight'
            # For signal dataset, use a different xRange and selection
            dataset =getRooDataset(File,selection='',xRange=[0,30],weight=weightname,yRange=thisyrange,project='',xVar=xVar,yVar=yVar,shift=shift)
    
    elif channel =="TauMuTauE" or channel == "TauMuTauMu":
        print File
        if 'datadriven' in type:
            print type
            dataset=getHisto(File,do2D,channel,process='datadriven')
        elif 'data' in type:
            dataset= getHisto(File,do2D,channel,process='data')
        else:
            dataset=getHisto(File,do2D,channel,process='signal')
    else:
        raise ValueError('Channel Unknown in getDataset')

    #print dataset
    #global j
    #j+=1
    #return dataset.Clone('hist'+str(j))
    return dataset

def getXsec(proc,mode):

    smtfile=ROOT.TFile(smtfilename)
    bsmtfile=ROOT.TFile(bsmtfilename)

    smws = smtfile.Get('YR4_SM_13TeV')
    bsmws = bsmtfile.Get('YR4_BSM_13TeV')
    
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

def getControlHist(proc,**kwargs):
    wrappers = kwargs.pop('wrappers',{})
    doUnbinned = kwargs.pop('doUnbinned',False)
    xbnwdth=0.001   ### very fine binning for start
    xBins=[int((xRange[1]-xRange[0])/xbnwdth),xRange[0],xRange[1]]
    # Takes far too long to do this unbinned
    hists = [getHistControl(s,Binning=xBins) for s in SampleMap2017[proc]]
    if len(hists) >1:
        hist = sumHists(proc,*hists)
    else:
        hist = hists[0].Clone(proc)
    return hist

def getSignalHist(proc,channel,**kwargs):
    #print "getSignalHist..."
    scale = kwargs.pop('scale',1)
    shift = kwargs.pop('shift','')
    region = kwargs.pop('region','A')
    do2D = kwargs.pop('do2D',False)
    chi2Mass = kwargs.pop('chi2Mass',0)
    doUnbinned = kwargs.pop('doUnbinned',False)
    var = kwargs.pop('var',['mm'])
    name = proc+region+shift
    print "name:", name

    if proc[-2]=='A': aMass=proc[-1]
    elif proc[-3]=='A': aMass=proc[-2]+proc[-1]
        
    if channel=="TauMuTauHad" or channel=="TauETauHad" or channel=="TauHadTauHad":
        if doUnbinned:
            hists = []
            sampleDir = baseDir+channel+'/RooDataSets/SignalMCSystematics/'
            if channel == "TauHadTauHad":
                sampleDir = baseDir+channel+'/RooDatasets/SignalMCSystematics/'
            if shift=='':
                filename = sampleDir+channel+'_HaaMC_am'+aMass+'_'+region+'_'+discriminator+'.root'
            else:
                filename = sampleDir+channel+'_HaaMC_am'+aMass+'_'+region+'_'+discriminator+'_'+shift+'.root'
            print filename
            hists=[getDataset(filename,channel,proc,shift,do2D)]
            hist = hists[0].Clone(name)

    elif channel=='TauMuTauE':
        sampleDir = prefix+baseDirRooDatahists+"SignalMC/"
        filename = sampleDir+channel+"_HaaMC_am"+aMass+"_"+muId+"MuIso_"+eleId+"EleId_signalRegion.root"
        hists=[getDataset(filename,channel,proc,shift,do2D)]
        hist = hists[0].Clone(name)
    elif channel=='TauMuTauMu':
        sampleDir = prefix+baseDirRooDatahists+"SignalMC/"
        filename = sampleDir+channel+"_HaaMC_am"+aMass+"_"+muId+"MuIso_signalRegion.root"
        hists=[getDataset(filename,channel,proc,shift,do2D)]
        hist = hists[0].Clone(name)
    elif channel == "TauHadTauHad_2017" or channel == "TauHadTauHad_2016" or channel == "TauHadTauHad_2018" or channel == "TauMuTauHad_2017" or channel == "TauMuTauHad_2017Cut" or channel == "TauMuTauHad_2017CutV2":
        sampleDir = baseDir
        if doUnbinned:
            if shift=='':
                filename = sampleDir+'HaaMC_am'+aMass+'_'+channel+'_'+method+'_'+discriminator+'_'+region+'.root'
            else:
                filename = sampleDir+'HaaMC_am'+aMass+'_'+channel+'_'+method+'_'+discriminator+'_'+region+'_'+shift+'.root'
            hists=[getDataset(filename,channel,proc,shift,do2D)]
            hist = hists[0].Clone(name)
    else:
        raise ValueError('Channel Unknown in getHist')
    return hist

def getDatadrivenHist(proc,channel,**kwargs):
    print "getDatadrivenHist..."
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
    print "name", name
    
    if channel=='TauMuTauHad' or channel=='TauETauHad' or channel=='TauHadTauHad':
        sampleDir = baseDir+channel+'/RooDataSets/DataDrivenSystematics/'
        if channel == 'TauHadTauHad':
            sampleDir = baseDir+channel+'/RooDatasets/DataDrivenSystematics/'

        if doUnbinned:
            hists = []
            ### Loading with fakaRate?? ###
            #print SampleMap2017['datadriven']
            if shift=='':
                filename = sampleDir+channel+'_'+region+'_'+discriminator+'.root'
            else:
                filename = sampleDir+channel+'_'+region+'_'+discriminator+'_'+shift+'.root'
            hists=[getDataset(filename,channel,proc,shift, do2D)]

            hist = hists[0].Clone(name)
        else:
            hists = []
            print "Doing binned, cannot get datadriven hist!"
            sys.exit()
    elif channel=='TauMuTauE':
        sampleDir = prefix+baseDirRooDatahists+"DataDriven/"
        filename = sampleDir+channel+'_'+region+'_MuIso_'+muId+'_EleId_'+eleId+'.root'
        hists = [getDataset(filename,channel,proc,'', do2D)]
        hist = hists[0].Clone(name)
    elif channel=='TauMuTauMu':
        sampleDir = prefix+baseDirRooDatahists+"DataDriven/"
        filename = sampleDir+channel+'_'+region+'_MuIso_'+muId+".root"
        hists = [getDataset(filename,channel,proc,'', do2D)]
        hist = hists[0].Clone(name)
        
    elif channel == "TauHadTauHad_2017" or channel == "TauHadTauHad_2016" or channel == "TauHadTauHad_2018" or channel == "TauMuTauHad_2017" or channel == "TauMuTauHad_2017Cut" or channel == "TauMuTauHad_2017CutV2":
        sampleDir = baseDir
        if doUnbinned:
            if shift=='':
                filename = sampleDir+channel+'_'+method+'_'+discriminator+'_'+region+'.root'
            else:
                filename = sampleDir+channel+'_'+method+'_'+discriminator+'_'+region+'_'+shift+'.root'
            hists=[getDataset(filename,channel,proc,shift, do2D)]
            hist = hists[0].Clone(name)
    else:
        raise ValueError('Channel Unknown in getDatadrivenHist')

    #print hist
    
    return hist



def sumHists(name,*hists):
    #global j
    #j += 1
    histlist = ROOT.TList()
    for hist in hists:
        histlist.Add(hist)
    #hist = histlist[0].Clone(name+str(j))
    hist = histlist[0].Clone(name+'_clone')
    hist.Reset()
    hist.Merge(histlist)
    return hist

def sumDatasets(name,*datasets):
    #global j
    #j += 1
    #dataset = datasets[0].Clone(name+str(j))
    dataset = datasets[0].Clone(name+'_clone')
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
