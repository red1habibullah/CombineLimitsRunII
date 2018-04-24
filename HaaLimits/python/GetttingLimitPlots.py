import os
import sys
import logging
import itertools
import numpy as np
import argparse
import math
import errno

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.SetBatch()

import CombineLimits.Limits.Models as Models
from CombineLimits.Limits.Limits import Limits
from CombineLimits.Limits.utilities import *
from CombineLimits.Plotter.LimitPlotter import *
from HaaLimits import HaaLimits

Ma_list = []
quantiles = {}
for filename in os.listdir('/afs/cern.ch/work/k/ktos/public/Plotting/CMSSW_8_1_0/src/CombineLimits/HaaLimits/python/rValueFiles/'):
  print "\n", filename
  if not filename.endswith(".root"):
    continue
  print filename
  fullFileName = "/afs/cern.ch/work/k/ktos/public/Plotting/CMSSW_8_1_0/src/CombineLimits/HaaLimits/python/rValueFiles/" + filename
  f = ROOT.TFile.Open(fullFileName )
  tree = f.Get("limit")
  quants = []
  for entry in tree:
    print entry, entry.limit
    quants.append(entry.limit)
  subName = filename.split("mH", 1)[1]
  ma = subName.split(".root", 1)[0]
  Ma_list.append(float(ma) )
  quantiles[float(ma)] = quants

Ma_list = sorted(Ma_list)
#print "\n", Ma_list
#for k,v in quantiles.items():
#  print k, v
myplot = LimitPlotter()
myplot.plotLimit(xvals=Ma_list, quartiles=quantiles, savename="H125_MeanSigFracConst_BTag_50MeV_Overlap6p5to14_Calc7p8to12p3", xaxis="M(mu mu)")
