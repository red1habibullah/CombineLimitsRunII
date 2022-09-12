import logging
import os
import sys
import glob
import json
import pickle
import array


import ROOT
ROOT.gROOT.SetBatch(ROOT.kTRUE)
ROOT.gROOT.ProcessLine("gErrorIgnoreLevel = 2001;")

#from RunIISampleMaps import *

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

    global maxyRange
    maxyRange = [0, 2000]

    global baseDir
    #global desc
    baseDir = '/eos/user/z/zhangj/HaaAnalysis/RooDatasets/'
    #baseDir = '/eos/cms/store/user/rhabibul/BoostedRooDatasets/'
    #desc = 'MVAMedium'

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
    #print "DEBUG:", yRange
    if yRange: args.find('visFourbodyMass').setRange(*yRange)
    print "yRange:", args.find('visFourbodyMass').getMax()
    if xVar!='invMassMuMu': args.find('invMassMuMu').SetName(xVar)
    if yVar!='visFourbodyMass':args.find('visFourbodyMass').SetName(yVar)
    ds = ROOT.RooDataSet(ds.GetName(),ds.GetTitle(),ds,args,selection,weight)
    if project: ds = getattr(ds,'reduce')(ROOT.RooArgSet(ds.get().find(project)))
    #print selection
    #print ds.sumEntries('invMassMuMu>0 && invMassMuMu<30 && visFourbodyMass>0 && visFourbodyMass<1000')
    return ds


def getRooDatasetFake(f,selection='1',weight='fakeRateEfficiency',xRange=[],yRange=[],project='',xVar='invMassMuMu',yVar='visFourbodyMass'):
    '''Get a DataDriven RooDataset'''
    file=ROOT.TFile.Open(f)
    ds=file.Get('dataColl')
    args=ds.get()
    if xRange: args.find('invMassMuMu').setRange(*xRange)
    if yRange: args.find('visFourbodyMass').setRange(*yRange)
    print "yRange:", args.find('visFourbodyMass').getMax()
    if xVar!='invMassMuMu': args.find('invMassMuMu').SetName(xVar)
    if yVar!='visFourbodyMass':args.find('visFourbodyMass').SetName(yVar)
    ds = ROOT.RooDataSet(ds.GetName(),ds.GetTitle(),ds,args,selection,weight)
    if project: ds = getattr(ds,'reduce')(ROOT.RooArgSet(ds.get().find(project)))
    print "dsIntegral:", ds.sumEntries()
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
    #print f
    file=ROOT.TFile.Open(f)
    ds=file.Get('dataColl')
    args=ds.get()
    ds = ROOT.RooDataSet(ds.GetName(),ds.GetTitle(),ds,args,selection)
    hist=ROOT.TH1F()
    hist=ROOT.RooAbsData.createHistogram(ds,ds.GetName(),ds.get().find(xVar),ROOT.RooFit.Binning(int(Binning[0]),float(Binning[1]),float(Binning[2])))
    hist.SetDirectory(ROOT.gROOT)
    return hist

def getHisto(f,do2D,channel,xVar='invMassMuMu',xRange=[],process=''):
    ''' Get Histogram directly from file '''
    if do2D:
        xVar='invMassMuMuVisMassMuMuTauTau'
        if process == "data":
            xVarnew=xVar+"3P1F1Only"
        elif process =="datadriven":
            xVarnew = xVar+"3P1F1"
        else:
            xVarnew=xVar
    
    if process == "data":
        #xVarnew=xVar+"3P1F1Only"
        xVarnew=xVar+"3P1F1"
    elif process =="datadriven":
        xVarnew = xVar+"3P1F1"
    else:
        xVarnew=xVar

    file=ROOT.TFile.Open(f)
    #print f, xVarnew
    #histo=file.Get(xVarnew, str(xRange[0])+"<"+xVarnew+"<"+str(xRange[1]))
    histo=file.Get(xVarnew)
    histo.SetDirectory(ROOT.gROOT)
    
    #if not do2D and (process=="datadriven" or process == "data"):
        #if xRange:
            #print "xRange: ", xRange
            #histo.GetXaxis().SetRangeUser(*xRange)
            #binning = array.array('d',[histo.GetXaxis().GetXmin(), 2.5, 2.75, 3., 3.25, 3.5, 3.75, 4., 5, 6, 7, 8.5, histo.GetXaxis().GetXmax()])
            #histo.Rebin(12, "rebin", binning)
            #print "nBins",histo, histo.GetNbinsX()
        
    if do2D:
        if process == "datadriven" or process == "data": histo.RebinY(4)
    return histo
    

#################
### Utilities ###
#################
def getDataset(File,channel,type,shift,do2D,xVar='invMassMuMu',yVar='visFourbodyMass'):
    thisxrange = xRange
    thisyrange = yRange
    maxyrange = maxyRange
    selDatasets = {
        'invMassMuMu' : '{0}>{1} && {0}<{2}'.format(xVar,*thisxrange),
        'visFourbodyMass' : '{0}>{1} && {0}<{2}'.format(yVar,*thisyrange),
    }

    print "getDataset:", type
    print File
    if "TauMuTauHad" in channel or "TauETauHad" in channel or "TauHadTauHad" in channel:
        if project and 'datadriven' in type:
            dataset =getRooDatasetFake(File,selection=selDatasets['invMassMuMu'],xRange=thisxrange,weight='fakeRateEfficiency',yRange=maxyrange,project=xVar,xVar=xVar,yVar=yVar)
        elif not project and 'datadriven' in type:
            dataset =getRooDatasetFake(File,selection=selDatasets['invMassMuMu'],xRange=thisxrange,weight='fakeRateEfficiency',yRange=maxyrange,project='',xVar=xVar,yVar=yVar)
        elif not project and 'data' in type:
            dataset =getRooDataset(File,selection=selDatasets['invMassMuMu'],xRange=thisxrange,weight='',yRange=maxyrange,project='',xVar=xVar,yVar=yVar)
        else:
            weightname='eventWeight'
            # For signal dataset, use a different xRange, yRange, and selection
            dataset =getRooDataset(File,selection=selDatasets['visFourbodyMass'],xRange=[0,50],weight=weightname,yRange=maxyrange,project='',xVar=xVar,yVar=yVar,shift=shift)
    
    elif "TauMuTauE" in channel or "TauMuTauMu" in channel or "TauETauE" in channel:
        print File
        if 'datadriven' in type:
            print type
            dataset=getHisto(File,do2D,channel,xRange=thisxrange,process='datadriven')
        elif 'data' in type:
            dataset= getHisto(File,do2D,channel,xRange=thisxrange,process='data')
        else:
            dataset=getHisto(File,do2D,channel,xRange=thisxrange,process='signal')
    else:
        raise ValueError('Channel Unknown in getDataset')

    #print dataset
    #global j
    #j+=1
    #return dataset.Clone('hist'+str(j))
    #print "DEBUG!!!", dataset.Print()
    return dataset

def getXsec(proc,mode):
    #prefix='root://cmseos.fnal.gov/'
    prefix = ''
    smtfilename=prefix+'/afs/cern.ch/work/z/zhangj/private/RunIILimits/CMSSW_10_2_13/src/CombineLimits/Limits/data/Higgs_YR4_SM_13TeV.root'
    bsmtfilename=prefix+'/afs/cern.ch/work/z/zhangj/private/RunIILimits/CMSSW_10_2_13/src/CombineLimits/Limits/data/Higgs_YR4_BSM_13TeV.root'

    smtfile=ROOT.TFile(smtfilename)
    bsmtfile=ROOT.TFile(bsmtfilename)

    smws = smtfile.Get('YR4_SM_13TeV')
    bsmws = bsmtfile.Get('YR4_BSM_13TeV')

    h = int(proc.split('_')[0].replace('hm', ''))
    a = float(proc.split('_')[-1].replace('am','').replace('p',''))
    # this was input as SM for 125 and BSM for others
    ws = smws if h==125 else bsmws
    #ws = bsmws
    #print ws, bsmws
    names = {
        'gg' : 'xsec_ggF_N3LO',
        'vbf': 'xsec_VBF',
    }
    spline = ws.function(names[mode])
    ws.var('MH').setVal(h)
    return spline.getVal()

def getControlHist(proc,channel,**kwargs):
    wrappers = kwargs.pop('wrappers',{})
    doUnbinned = kwargs.pop('doUnbinned',False)
    xbnwdth=0.001   ### very fine binning for start
    xBins=[int((xRange[1]-xRange[0])/xbnwdth),xRange[0],xRange[1]]
    # Takes far too long to do this unbinned

    year = channel.split('_')[-1]
    
    sampleDir = baseDir+'control/'+year
    filename = sampleDir + '/control_RooDataset_{}.root'.format(year)
    hists = [getHistControl(filename, Binning=xBins)]
    hist = hists[0].Clone(proc)
    return hist

def getSignalHist(proc,channel,**kwargs):
    print "-----getSignalHist..."
    scale = kwargs.pop('scale',1)
    shift = kwargs.pop('shift','')
    region = kwargs.pop('region','A')
    do2D = kwargs.pop('do2D',False)
    chi2Mass = kwargs.pop('chi2Mass',0)
    doUnbinned = kwargs.pop('doUnbinned',False)
    var = kwargs.pop('var',['mm'])
    name = proc+region+shift
    print "name:", name

    yeartext = channel.split('_')[-1]
    channeltext = channel.replace('_'+yeartext, '')

    if 'TauMuTauE' in channel:
        desc = 'looseMuIso_tightEleId'
    elif 'TauMuTauMu' in channel:
        desc = 'looseMuIso_looseMuIso'
    else:
        desc = 'MVAMedium'
    
    sampleDir = baseDir+channeltext+'/'+yeartext+'/SignalMC/'
    filename = sampleDir + 'Haa_MC_{}_{}_{}_{}_{}_{}.root'.format(proc, channeltext, yeartext, desc, region, shift)
    hists = [getDataset(filename,channel,proc,shift, do2D)]
    hist = hists[0].Clone(name)
    return hist

def getDatadrivenHist(proc,channel,**kwargs):
    print "-----getDatadrivenHist..."
    shift = kwargs.pop('shift','')
    source = kwargs.pop('source','B')
    region = kwargs.pop('region','A')
    do2D = kwargs.pop('do2D',False)
    chi2Mass = kwargs.pop('chi2Mass',0)
    doUnbinned = kwargs.pop('doUnbinned',False)
    var = kwargs.pop('var',['mm'])
    name = proc+region+shift
    print "name", name

    yeartext = channel.split('_')[-1]
    channeltext = channel.replace('_'+yeartext, '')

    if 'TauMuTauE' in channel:
        desc = 'looseMuIso_tightEleId'
    elif 'TauMuTauMu' in channel:
        desc = 'looseMuIso_looseMuIso'
    else:
        desc = 'MVAMedium'
    
    sampleDir = baseDir+channeltext+'/'+yeartext+'/DataDriven/'
    filename = sampleDir + '{}_{}_{}_{}_{}.root'.format(channeltext, yeartext, desc, region, shift)
    #if proc == 'data' and region == 'signalRegion' and not 'TauMuTauE' in channel:
    if proc == 'data' and region == 'signalRegion':
        filename=filename.replace('signalRegion', 'signalRegionUnblind')
    hists = [getDataset(filename,channel,proc,shift, do2D)]
    hist = hists[0].Clone(name)
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
