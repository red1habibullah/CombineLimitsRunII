import logging
import os
import sys
import glob
import json
import pickle


import ROOT
ROOT.gROOT.SetBatch(ROOT.kTRUE)
ROOT.gROOT.ProcessLine("gErrorIgnoreLevel = 2001;")
###### Utility to get Roodatasets ########################
def getRooDataset(f,selection='1',weight='',xRange=[],yRange=[],project='',xVar='invMassMuMu',yVar='visFourbodyMass'):
    '''Get a RooDataset'''
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
def getHisto(f,xVar='invMassMuMu',process=''):
    ''' Get 1D Histogram directly from file '''
    
    if process == "data":
        xVarnew=xVar+"3P1F1Only"
    elif process =="datadriven":
        xVarnew=xVar+"3P1F1"
    else:
        xVarnew=xVar
    file=ROOT.TFile.Open(f)
    histo=file.Get(xVarnew)
    histo.SetDirectory(ROOT.gROOT)
    #print hist
    return histo
    
