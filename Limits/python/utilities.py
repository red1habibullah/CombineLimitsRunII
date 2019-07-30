import os
import sys
import errno
import operator
import subprocess
import logging
import math
import json
import pickle
import glob

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.SetBatch()

# common definitions
ZMASS = 91.1876

# helper functions
def python_mkdir(dir):
    '''A function to make a unix directory as well as subdirectories'''
    try:
        os.makedirs(dir)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(dir):
            pass
        else: raise

def which(program):
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None

def runCommand(command):
    return subprocess.Popen(command,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT).communicate()[0]


def getCMSSWMajorVersion():
    return os.environ['CMSSW_VERSION'].split('_')[1]

def getCMSSWMinorVersion():
    return os.environ['CMSSW_VERSION'].split('_')[2]

def getCMSSWVersion():
    return ''.join([getCMSSWMajorVersion(),getCMSSWMinorVersion(),'X'])


def sumHists(name,*hists):
    histlist = ROOT.TList()
    for hist in hists:
        histlist.Add(hist)
    hist = histlist[0].Clone(name)
    hist.Reset()
    hist.Merge(histlist)
    return hist

def getDatasetIntegralError(dataset, cutSpec=''):
    
    select = ROOT.RooFormula()
    if cutSpec:
        select = ROOT.RooFormula("select",cutSpec,ROOT.RooArgList(dataset.get()))
    
    if not cutSpec and not dataset.isWeighted():
        return dataset.numEntries()**0.5
    
    sumw2 = 0
    for i in xrange(dataset.numEntries()):
        dataset.get(i)
        if (cutSpec and select.eval()==0.): continue
        sumw2 += dataset.weight()**2
    
    return sumw2**0.5


def getHistogramIntegralError(hist,binlow=1,binhigh=-1):
    if binhigh<0: binhigh = hist.GetNbinsX()
    integralerr = ROOT.Double(0)
    hist.IntegralAndError(binlow,binhigh,integralerr,"")
    return float(integralerr)

def getHistogram2DIntegralError(hist,binxlow=1,binxhigh=-1,binylow=1,binyhigh=-1):
    if binxhigh<0: binxhigh = hist.GetNbinsX()
    if binyhigh<0: binyhigh = hist.GetNbinsY()
    integralerr = ROOT.Double(0)
    hist.IntegralAndError(binxlow,binxhigh,binylow,binyhigh,integralerr,"")
    return float(integralerr)
