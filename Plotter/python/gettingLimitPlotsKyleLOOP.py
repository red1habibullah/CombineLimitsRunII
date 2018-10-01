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
from CombineLimits.HaaLimits.HaaLimits import HaaLimits

Ma_list = []
quantiles = {}
filesToDelete = []
for filename in os.listdir('/eos/cms/store/user/ktos/rValues/DIRNAME/'):
  print "\n", filename
  if not filename.endswith(".root"):
    continue
  print filename
  fullFileName = "/eos/cms/store/user/ktos/rValues/DIRNAME/" + filename
  f = ROOT.TFile.Open(fullFileName )
  try:
    tree = f.Get("limit")
    quants = []
    for entry in tree:
      print entry, entry.limit
      quants.append(entry.limit)
    print "nEntries=", len(quants)
    if len(quants) < 6: 
      print "NOT ENOUGH ENTRIES"
      continue
    subName = filename.split("mH", 1)[1]
    ma = subName.split(".root", 1)[0]
    Ma_list.append(float(ma) )
    quantiles[float(ma)] = quants
  except TypeError:
    filesToDelete.append("/eos/cms/store/user/ktos/rValues/DIRNAME/" + filename)
    print "BAD FILE: /eos/cms/store/user/ktos/rValues/DIRNAME/" + filename
  except ReferenceError:
    filesToDelete.append("/eos/cms/store/user/ktos/rValues/DIRNAME/" + filename)
    print "BAD FILE: /eos/cms/store/user/ktos/rValues/DIRNAME/" + filename


with open('FILES_TO_DELETE_DIRNAME.txt', 'w') as f:
    for item in filesToDelete:
        f.write("%s\n" % item)


Ma_list = sorted(Ma_list)
#print "\n", Ma_list
#for k,v in quantiles.items():
#  print k, v
myplot = LimitPlotter()
myplot.plotLimit(xvals=Ma_list, quartiles=quantiles, savename="h125_100MeV_DIRNAME", xaxis="M(mu mu)", smooth=True)
