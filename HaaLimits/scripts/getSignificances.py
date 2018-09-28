import os
import sys
import logging
import itertools
import numpy as np
import argparse
import math
import errno
from significances import *

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.SetBatch()

import CombineLimits.Limits.Models as Models
from CombineLimits.Limits.Limits import Limits
from CombineLimits.Limits.utilities import *

from HaaLimits2D import *

XRANGE = [3.5, 25]
YRANGE = [0,30]
UPSILONRANGE = [8,11]
subdirectoryName='KinFit_mumutautau_3p5_GetSignificance/'
name = 'mmmt_mm_parametric'

def getDatasetAndInt(ds,weight='w',selection='1',xRange=[],yRange=[]):
  args = ds.get()
  if xRange: 
    args.find('x').setRange(*xRange)
  if args.find('y1'): 
    args.find('y1').SetName('y')    
    args.find('y1').SetTitle('y')
  if yRange: 
    args.find('y').setRange(*yRange)
  ds = ROOT.RooDataSet(ds.GetName(),ds.GetTitle(),ds,args,selection,weight)
  return ds.sumEntries(), ds, ds.numEntries()

def GetPPData(dictionary,xRange=[]):
  f_FRC = ROOT.TFile.Open("/eos/cms/store/user/ktos/ShapeDifferences/FINAL_RooDataSet_MiniAOD_SingleMu_MedIsoMu2_TauDMAntiMedIso_MAY1_AFromB_HKinFit_Plots.root")
  SingleMu_FakeRate            = f_FRC.Get("mumutautaumass_dataset")
  integral, SingleMu_FakeRate,nEntries  = getDatasetAndInt(SingleMu_FakeRate, selection='x <= 25 && x >= 2.5 && y >= 0', xRange=xRange)
  dictionary['PP']['']['data'] = (SingleMu_FakeRate, integral, nEntries)

def GetPPSignal(dictionary,xRange=[]):
  f = ROOT.TFile.Open("/eos/cms/store/user/ktos/ShapeDifferences/FINAL_AllRooDataSet_MedIsoMu2_TauDMMedIso_MAY1_HKinFit.root")
  for hMass in ["125","300","750"]:
     for aMass in ["3p6","4","5","6","7","9","11","13","15","17","19","21"]:
       if (hMass == "300" or hMass == "750") and (aMass == "3p6" or aMass == "4" or aMass == "6"): continue
       h_Central           = f.Get("SIG_h" + hMass + "a" + aMass + "_MedIsoMu2_TauDMMedIso_MAY1_Central_ditau")
       integral, h_Central, nEntries = getDatasetAndInt(h_Central, selection='x <= 25 && x >= 2.5 && y >= 0', xRange=xRange)
       dictionary['PP']['']["HToAAH" + hMass + "A" + aMass] = (h_Central, integral, nEntries)

def GetFPData(dictionary,xRange=[]):
  f_FakeRateRegionB = ROOT.TFile.Open("/eos/cms/store/user/ktos/ShapeDifferences/FINAL_RooDataSet_MiniAOD_SingleMu_MedIsoMu2_TauDMAntiMedIso_MAY1_BItself_HKinFit_Plots.root")
  SingleMu_RegionB             = f_FakeRateRegionB.Get("mumutautaumass_dataset")
  integral, SingleMu_RegionB , nEntries  = getDatasetAndInt(SingleMu_RegionB, selection='x <= 25 && x >= 2.5 && y >= 0', xRange=xRange)
  dictionary['FP']['']['data'] = (SingleMu_RegionB, integral, nEntries)

def GetFPSignal(dictionary,xRange=[]):
  f = ROOT.TFile.Open("/eos/cms/store/user/ktos/ShapeDifferences/FINAL_AllRooDataSet_MedIsoMu2_TauDMAntiMedIso_MAY1_HKinFit.root")
  for hMass in ["125","300","750"]:
     for aMass in ["3p6","4","5","6","7","9","11","13","15","17","19","21"]:
       if (hMass == "300" or hMass == "750") and (aMass == "3p6" or aMass == "4" or aMass == "6"): continue
       h_Central           = f.Get("SIG_h" + hMass + "a" + aMass + "_MedIsoMu2_TauDMAntiMedIso_MAY1_Central_ditau")
       integral, h_Central, nEntries = getDatasetAndInt(h_Central, selection='x <= 25 && x >= 2.5 && y >= 0', xRange=xRange)
       dictionary['FP']['']["HToAAH" + hMass + "A" + aMass] = (h_Central, integral, nEntries)


dictionary = {'PP' : { '' : {},  },
              'FP' : { '' : {},  }
             }



GetPPSignal(dictionary,XRANGE)
GetPPData(dictionary,XRANGE)
GetFPData(dictionary,XRANGE)
GetFPSignal(dictionary,XRANGE)

for k,v, in dictionary.items():
  for k1,v1 in dictionary[k].items():
    for k2,v2 in dictionary[k][k1].items():
      print k, k1, k2, v2
