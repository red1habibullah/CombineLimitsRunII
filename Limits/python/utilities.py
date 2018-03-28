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
