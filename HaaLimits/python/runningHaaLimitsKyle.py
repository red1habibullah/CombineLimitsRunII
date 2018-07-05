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

from HaaLimits import *

XRANGE = [5, 25]
UPSILONRANGE = [8.5,11]
subdirectoryName='UpConst_SetLambda_8p5to11p0_TESTNEW/'
name = 'mmmt_mm_parametric'

def ScaleRooDataSets(ds, scale=1):
   x = ROOT.RooRealVar("x","x", 0, 30)
   w = ROOT.RooRealVar("w","w", 0, 30)
   dsNew = ROOT.RooDataSet(ds.GetName(),ds.GetTitle(),ROOT.RooArgSet(x,w))
   for i in range(ds.numEntries() ):
      args = ds.get(i)
      varW = args.find("w")
      varX = args.find("x")
      x.setVal(varX.getVal() )
      w.setVal(varW.getVal()*scale)
      dsNew.add(ROOT.RooArgSet(x,w) )
   print "Scaled", ds.GetName()
   return dsNew


def getDataset(ds,weight='w',selection='1',xRange=[],yRange=[]):
   args = ds.get()
   if xRange: args.find('x').setRange(*xRange)
   if yRange: args.find('w').setRange(*yRange)
   ds = ROOT.RooDataSet(ds.GetName(),ds.GetTitle(),ds,args,selection,weight)
   return ds

def GetPPData(dictionary,xRange=[]):
   f_FRC = ROOT.TFile.Open("/eos/cms/store/user/ktos/ShapeDifferences/FINAL_RooDataSet_MiniAOD_SingleMu_MedIsoMu2_TauDMAntiMedIso_APR20_DevindR_AFromB.root")
#   f_FRU = ROOT.TFile.Open("/eos/cms/store/user/ktos/ShapeDifferences/FINAL_RooDataSet_MiniAOD_SingleMu_MedIsoMu2_TauDMAntiMedIso_APR20_DevindR_FakeRate_Up.root")
#   f_FRD = ROOT.TFile.Open("/eos/cms/store/user/ktos/ShapeDifferences/FINAL_RooDataSet_MiniAOD_SingleMu_MedIsoMu2_TauDMAntiMedIso_APR20_DevindR_FakeRate_Down.root")
   
   SingleMu_FakeRateCentral = f_FRC.Get("mumumass_dataset")
#   SingleMu_FakeRateDown = f_FRD.Get("mumumass_dataset")
#   SingleMu_FakeRateUp = f_FRU.Get("mumumass_dataset")

   SingleMu_FakeRateCentral = getDataset(SingleMu_FakeRateCentral, selection='x <= 25 && x >= 4', xRange=xRange)
#   SingleMu_FakeRateDown = getDataset(SingleMu_FakeRateDown, selection='x <= 25 && x >= 4', xRange=xRange)
#   SingleMu_FakeRateUp = getDataset(SingleMu_FakeRateUp, selection='x <= 25 && x >= 4', xRange=xRange)
   
   dictionary['PP']['']['data'] = SingleMu_FakeRateCentral
   dictionary['PP']['']['dataNoSig'] = SingleMu_FakeRateCentral

def GetPPSignal(dictionary,xRange=[]):
   f = ROOT.TFile.Open("/eos/cms/store/user/ktos/ShapeDifferences/FINAL_AllRooDataSet_MedIsoMu2_TauDMMedIso_APR20_BTagSF.root")
   
   h125a11_MedIsoMu2_TauDMMedIso_Central = f.Get("SIG_h125a11_MedIsoMu2_TauDMMedIso_APR20_Central_BTagSF")
   h125a11_MedIsoMu2_TauDMMedIso_IDDOWN = f.Get("SIG_h125a11_MedIsoMu2_TauDMMedIso_APR20_IDDOWN_BTagSF")
   h125a11_MedIsoMu2_TauDMMedIso_IDUP = f.Get("SIG_h125a11_MedIsoMu2_TauDMMedIso_APR20_IDUP_BTagSF")
   h125a11_MedIsoMu2_TauDMMedIso_IsoDOWN = f.Get("SIG_h125a11_MedIsoMu2_TauDMMedIso_APR20_IsoDOWN_BTagSF")
   h125a11_MedIsoMu2_TauDMMedIso_IsoUP = f.Get("SIG_h125a11_MedIsoMu2_TauDMMedIso_APR20_IsoUP_BTagSF")
   h125a11_MedIsoMu2_TauDMMedIso_BTagDOWN = f.Get("SIG_h125a11_MedIsoMu2_TauDMMedIso_APR20_BTagDOWN_BTagSF")
   h125a11_MedIsoMu2_TauDMMedIso_BTagUP = f.Get("SIG_h125a11_MedIsoMu2_TauDMMedIso_APR20_BTagUP_BTagSF")
   h125a11_MedIsoMu2_TauDMMedIso_PileupDOWN = f.Get("SIG_h125a11_MedIsoMu2_TauDMMedIso_APR20_PileupDOWN_BTagSF")
   h125a11_MedIsoMu2_TauDMMedIso_PileupUP = f.Get("SIG_h125a11_MedIsoMu2_TauDMMedIso_APR20_PileupUP_BTagSF")
   h125a13_MedIsoMu2_TauDMMedIso_Central = f.Get("SIG_h125a13_MedIsoMu2_TauDMMedIso_APR20_Central_BTagSF")
   h125a13_MedIsoMu2_TauDMMedIso_IDDOWN = f.Get("SIG_h125a13_MedIsoMu2_TauDMMedIso_APR20_IDDOWN_BTagSF")
   h125a13_MedIsoMu2_TauDMMedIso_IDUP = f.Get("SIG_h125a13_MedIsoMu2_TauDMMedIso_APR20_IDUP_BTagSF")
   h125a13_MedIsoMu2_TauDMMedIso_IsoDOWN = f.Get("SIG_h125a13_MedIsoMu2_TauDMMedIso_APR20_IsoDOWN_BTagSF")
   h125a13_MedIsoMu2_TauDMMedIso_IsoUP = f.Get("SIG_h125a13_MedIsoMu2_TauDMMedIso_APR20_IsoUP_BTagSF")
   h125a13_MedIsoMu2_TauDMMedIso_BTagDOWN = f.Get("SIG_h125a13_MedIsoMu2_TauDMMedIso_APR20_BTagDOWN_BTagSF")
   h125a13_MedIsoMu2_TauDMMedIso_BTagUP = f.Get("SIG_h125a13_MedIsoMu2_TauDMMedIso_APR20_BTagUP_BTagSF")
   h125a13_MedIsoMu2_TauDMMedIso_PileupDOWN = f.Get("SIG_h125a13_MedIsoMu2_TauDMMedIso_APR20_PileupDOWN_BTagSF")
   h125a13_MedIsoMu2_TauDMMedIso_PileupUP = f.Get("SIG_h125a13_MedIsoMu2_TauDMMedIso_APR20_PileupUP_BTagSF")
   h125a15_MedIsoMu2_TauDMMedIso_Central = f.Get("SIG_h125a15_MedIsoMu2_TauDMMedIso_APR20_Central_BTagSF")
   h125a15_MedIsoMu2_TauDMMedIso_IDDOWN = f.Get("SIG_h125a15_MedIsoMu2_TauDMMedIso_APR20_IDDOWN_BTagSF")
   h125a15_MedIsoMu2_TauDMMedIso_IDUP = f.Get("SIG_h125a15_MedIsoMu2_TauDMMedIso_APR20_IDUP_BTagSF")
   h125a15_MedIsoMu2_TauDMMedIso_IsoDOWN = f.Get("SIG_h125a15_MedIsoMu2_TauDMMedIso_APR20_IsoDOWN_BTagSF")
   h125a15_MedIsoMu2_TauDMMedIso_IsoUP = f.Get("SIG_h125a15_MedIsoMu2_TauDMMedIso_APR20_IsoUP_BTagSF")
   h125a15_MedIsoMu2_TauDMMedIso_BTagDOWN = f.Get("SIG_h125a15_MedIsoMu2_TauDMMedIso_APR20_BTagDOWN_BTagSF")
   h125a15_MedIsoMu2_TauDMMedIso_BTagUP = f.Get("SIG_h125a15_MedIsoMu2_TauDMMedIso_APR20_BTagUP_BTagSF")
   h125a15_MedIsoMu2_TauDMMedIso_PileupDOWN = f.Get("SIG_h125a15_MedIsoMu2_TauDMMedIso_APR20_PileupDOWN_BTagSF")
   h125a15_MedIsoMu2_TauDMMedIso_PileupUP = f.Get("SIG_h125a15_MedIsoMu2_TauDMMedIso_APR20_PileupUP_BTagSF")
   h125a17_MedIsoMu2_TauDMMedIso_Central = f.Get("SIG_h125a17_MedIsoMu2_TauDMMedIso_APR20_Central_BTagSF")
   h125a17_MedIsoMu2_TauDMMedIso_IDDOWN = f.Get("SIG_h125a17_MedIsoMu2_TauDMMedIso_APR20_IDDOWN_BTagSF")
   h125a17_MedIsoMu2_TauDMMedIso_IDUP = f.Get("SIG_h125a17_MedIsoMu2_TauDMMedIso_APR20_IDUP_BTagSF")
   h125a17_MedIsoMu2_TauDMMedIso_IsoDOWN = f.Get("SIG_h125a17_MedIsoMu2_TauDMMedIso_APR20_IsoDOWN_BTagSF")
   h125a17_MedIsoMu2_TauDMMedIso_IsoUP = f.Get("SIG_h125a17_MedIsoMu2_TauDMMedIso_APR20_IsoUP_BTagSF")
   h125a17_MedIsoMu2_TauDMMedIso_BTagDOWN = f.Get("SIG_h125a17_MedIsoMu2_TauDMMedIso_APR20_BTagDOWN_BTagSF")
   h125a17_MedIsoMu2_TauDMMedIso_BTagUP = f.Get("SIG_h125a17_MedIsoMu2_TauDMMedIso_APR20_BTagUP_BTagSF")
   h125a17_MedIsoMu2_TauDMMedIso_PileupDOWN = f.Get("SIG_h125a17_MedIsoMu2_TauDMMedIso_APR20_PileupDOWN_BTagSF")
   h125a17_MedIsoMu2_TauDMMedIso_PileupUP = f.Get("SIG_h125a17_MedIsoMu2_TauDMMedIso_APR20_PileupUP_BTagSF")
   h125a19_MedIsoMu2_TauDMMedIso_Central = f.Get("SIG_h125a19_MedIsoMu2_TauDMMedIso_APR20_Central_BTagSF")
   h125a19_MedIsoMu2_TauDMMedIso_IDDOWN = f.Get("SIG_h125a19_MedIsoMu2_TauDMMedIso_APR20_IDDOWN_BTagSF")
   h125a19_MedIsoMu2_TauDMMedIso_IDUP = f.Get("SIG_h125a19_MedIsoMu2_TauDMMedIso_APR20_IDUP_BTagSF")
   h125a19_MedIsoMu2_TauDMMedIso_IsoDOWN = f.Get("SIG_h125a19_MedIsoMu2_TauDMMedIso_APR20_IsoDOWN_BTagSF")
   h125a19_MedIsoMu2_TauDMMedIso_IsoUP = f.Get("SIG_h125a19_MedIsoMu2_TauDMMedIso_APR20_IsoUP_BTagSF")
   h125a19_MedIsoMu2_TauDMMedIso_BTagDOWN = f.Get("SIG_h125a19_MedIsoMu2_TauDMMedIso_APR20_BTagDOWN_BTagSF")
   h125a19_MedIsoMu2_TauDMMedIso_BTagUP = f.Get("SIG_h125a19_MedIsoMu2_TauDMMedIso_APR20_BTagUP_BTagSF")
   h125a19_MedIsoMu2_TauDMMedIso_PileupDOWN = f.Get("SIG_h125a19_MedIsoMu2_TauDMMedIso_APR20_PileupDOWN_BTagSF")
   h125a19_MedIsoMu2_TauDMMedIso_PileupUP = f.Get("SIG_h125a19_MedIsoMu2_TauDMMedIso_APR20_PileupUP_BTagSF")
   h125a21_MedIsoMu2_TauDMMedIso_Central = f.Get("SIG_h125a21_MedIsoMu2_TauDMMedIso_APR20_Central_BTagSF")
   h125a21_MedIsoMu2_TauDMMedIso_IDDOWN = f.Get("SIG_h125a21_MedIsoMu2_TauDMMedIso_APR20_IDDOWN_BTagSF")
   h125a21_MedIsoMu2_TauDMMedIso_IDUP = f.Get("SIG_h125a21_MedIsoMu2_TauDMMedIso_APR20_IDUP_BTagSF")
   h125a21_MedIsoMu2_TauDMMedIso_IsoDOWN = f.Get("SIG_h125a21_MedIsoMu2_TauDMMedIso_APR20_IsoDOWN_BTagSF")
   h125a21_MedIsoMu2_TauDMMedIso_IsoUP = f.Get("SIG_h125a21_MedIsoMu2_TauDMMedIso_APR20_IsoUP_BTagSF")
   h125a21_MedIsoMu2_TauDMMedIso_BTagDOWN = f.Get("SIG_h125a21_MedIsoMu2_TauDMMedIso_APR20_BTagDOWN_BTagSF")
   h125a21_MedIsoMu2_TauDMMedIso_BTagUP = f.Get("SIG_h125a21_MedIsoMu2_TauDMMedIso_APR20_BTagUP_BTagSF")
   h125a21_MedIsoMu2_TauDMMedIso_PileupDOWN = f.Get("SIG_h125a21_MedIsoMu2_TauDMMedIso_APR20_PileupDOWN_BTagSF")
   h125a21_MedIsoMu2_TauDMMedIso_PileupUP = f.Get("SIG_h125a21_MedIsoMu2_TauDMMedIso_APR20_PileupUP_BTagSF")
   h125a5_MedIsoMu2_TauDMMedIso_Central = f.Get("SIG_h125a5_MedIsoMu2_TauDMMedIso_APR20_Central_BTagSF")
   h125a5_MedIsoMu2_TauDMMedIso_IDDOWN = f.Get("SIG_h125a5_MedIsoMu2_TauDMMedIso_APR20_IDDOWN_BTagSF")
   h125a5_MedIsoMu2_TauDMMedIso_IDUP = f.Get("SIG_h125a5_MedIsoMu2_TauDMMedIso_APR20_IDUP_BTagSF")
   h125a5_MedIsoMu2_TauDMMedIso_IsoDOWN = f.Get("SIG_h125a5_MedIsoMu2_TauDMMedIso_APR20_IsoDOWN_BTagSF")
   h125a5_MedIsoMu2_TauDMMedIso_IsoUP = f.Get("SIG_h125a5_MedIsoMu2_TauDMMedIso_APR20_IsoUP_BTagSF")
   h125a5_MedIsoMu2_TauDMMedIso_BTagDOWN = f.Get("SIG_h125a5_MedIsoMu2_TauDMMedIso_APR20_BTagDOWN_BTagSF")
   h125a5_MedIsoMu2_TauDMMedIso_BTagUP = f.Get("SIG_h125a5_MedIsoMu2_TauDMMedIso_APR20_BTagUP_BTagSF")
   h125a5_MedIsoMu2_TauDMMedIso_PileupDOWN = f.Get("SIG_h125a5_MedIsoMu2_TauDMMedIso_APR20_PileupDOWN_BTagSF")
   h125a5_MedIsoMu2_TauDMMedIso_PileupUP = f.Get("SIG_h125a5_MedIsoMu2_TauDMMedIso_APR20_PileupUP_BTagSF")
   h125a7_MedIsoMu2_TauDMMedIso_Central = f.Get("SIG_h125a7_MedIsoMu2_TauDMMedIso_APR20_Central_BTagSF")
   h125a7_MedIsoMu2_TauDMMedIso_IDDOWN = f.Get("SIG_h125a7_MedIsoMu2_TauDMMedIso_APR20_IDDOWN_BTagSF")
   h125a7_MedIsoMu2_TauDMMedIso_IDUP = f.Get("SIG_h125a7_MedIsoMu2_TauDMMedIso_APR20_IDUP_BTagSF")
   h125a7_MedIsoMu2_TauDMMedIso_IsoDOWN = f.Get("SIG_h125a7_MedIsoMu2_TauDMMedIso_APR20_IsoDOWN_BTagSF")
   h125a7_MedIsoMu2_TauDMMedIso_IsoUP = f.Get("SIG_h125a7_MedIsoMu2_TauDMMedIso_APR20_IsoUP_BTagSF")
   h125a7_MedIsoMu2_TauDMMedIso_BTagDOWN = f.Get("SIG_h125a7_MedIsoMu2_TauDMMedIso_APR20_BTagDOWN_BTagSF")
   h125a7_MedIsoMu2_TauDMMedIso_BTagUP = f.Get("SIG_h125a7_MedIsoMu2_TauDMMedIso_APR20_BTagUP_BTagSF")
   h125a7_MedIsoMu2_TauDMMedIso_PileupDOWN = f.Get("SIG_h125a7_MedIsoMu2_TauDMMedIso_APR20_PileupDOWN_BTagSF")
   h125a7_MedIsoMu2_TauDMMedIso_PileupUP = f.Get("SIG_h125a7_MedIsoMu2_TauDMMedIso_APR20_PileupUP_BTagSF")
   h125a9_MedIsoMu2_TauDMMedIso_Central = f.Get("SIG_h125a9_MedIsoMu2_TauDMMedIso_APR20_Central_BTagSF")
   h125a9_MedIsoMu2_TauDMMedIso_IDDOWN = f.Get("SIG_h125a9_MedIsoMu2_TauDMMedIso_APR20_IDDOWN_BTagSF")
   h125a9_MedIsoMu2_TauDMMedIso_IDUP = f.Get("SIG_h125a9_MedIsoMu2_TauDMMedIso_APR20_IDUP_BTagSF")
   h125a9_MedIsoMu2_TauDMMedIso_IsoDOWN = f.Get("SIG_h125a9_MedIsoMu2_TauDMMedIso_APR20_IsoDOWN_BTagSF")
   h125a9_MedIsoMu2_TauDMMedIso_IsoUP = f.Get("SIG_h125a9_MedIsoMu2_TauDMMedIso_APR20_IsoUP_BTagSF")
   h125a9_MedIsoMu2_TauDMMedIso_BTagDOWN = f.Get("SIG_h125a9_MedIsoMu2_TauDMMedIso_APR20_BTagDOWN_BTagSF")
   h125a9_MedIsoMu2_TauDMMedIso_BTagUP = f.Get("SIG_h125a9_MedIsoMu2_TauDMMedIso_APR20_BTagUP_BTagSF")
   h125a9_MedIsoMu2_TauDMMedIso_PileupDOWN = f.Get("SIG_h125a9_MedIsoMu2_TauDMMedIso_APR20_PileupDOWN_BTagSF")
   h125a9_MedIsoMu2_TauDMMedIso_PileupUP = f.Get("SIG_h125a9_MedIsoMu2_TauDMMedIso_APR20_PileupUP_BTagSF")
   h300a11_MedIsoMu2_TauDMMedIso_Central = f.Get("SIG_h300a11_MedIsoMu2_TauDMMedIso_APR20_Central_BTagSF")
   h300a11_MedIsoMu2_TauDMMedIso_IDDOWN = f.Get("SIG_h300a11_MedIsoMu2_TauDMMedIso_APR20_IDDOWN_BTagSF")
   h300a11_MedIsoMu2_TauDMMedIso_IDUP = f.Get("SIG_h300a11_MedIsoMu2_TauDMMedIso_APR20_IDUP_BTagSF")
   h300a11_MedIsoMu2_TauDMMedIso_IsoDOWN = f.Get("SIG_h300a11_MedIsoMu2_TauDMMedIso_APR20_IsoDOWN_BTagSF")
   h300a11_MedIsoMu2_TauDMMedIso_IsoUP = f.Get("SIG_h300a11_MedIsoMu2_TauDMMedIso_APR20_IsoUP_BTagSF")
   h300a11_MedIsoMu2_TauDMMedIso_BTagDOWN = f.Get("SIG_h300a11_MedIsoMu2_TauDMMedIso_APR20_BTagDOWN_BTagSF")
   h300a11_MedIsoMu2_TauDMMedIso_BTagUP = f.Get("SIG_h300a11_MedIsoMu2_TauDMMedIso_APR20_BTagUP_BTagSF")
   h300a11_MedIsoMu2_TauDMMedIso_PileupDOWN = f.Get("SIG_h300a11_MedIsoMu2_TauDMMedIso_APR20_PileupDOWN_BTagSF")
   h300a11_MedIsoMu2_TauDMMedIso_PileupUP = f.Get("SIG_h300a11_MedIsoMu2_TauDMMedIso_APR20_PileupUP_BTagSF")
   h300a13_MedIsoMu2_TauDMMedIso_Central = f.Get("SIG_h300a13_MedIsoMu2_TauDMMedIso_APR20_Central_BTagSF")
   h300a13_MedIsoMu2_TauDMMedIso_IDDOWN = f.Get("SIG_h300a13_MedIsoMu2_TauDMMedIso_APR20_IDDOWN_BTagSF")
   h300a13_MedIsoMu2_TauDMMedIso_IDUP = f.Get("SIG_h300a13_MedIsoMu2_TauDMMedIso_APR20_IDUP_BTagSF")
   h300a13_MedIsoMu2_TauDMMedIso_IsoDOWN = f.Get("SIG_h300a13_MedIsoMu2_TauDMMedIso_APR20_IsoDOWN_BTagSF")
   h300a13_MedIsoMu2_TauDMMedIso_IsoUP = f.Get("SIG_h300a13_MedIsoMu2_TauDMMedIso_APR20_IsoUP_BTagSF")
   h300a13_MedIsoMu2_TauDMMedIso_BTagDOWN = f.Get("SIG_h300a13_MedIsoMu2_TauDMMedIso_APR20_BTagDOWN_BTagSF")
   h300a13_MedIsoMu2_TauDMMedIso_BTagUP = f.Get("SIG_h300a13_MedIsoMu2_TauDMMedIso_APR20_BTagUP_BTagSF")
   h300a13_MedIsoMu2_TauDMMedIso_PileupDOWN = f.Get("SIG_h300a13_MedIsoMu2_TauDMMedIso_APR20_PileupDOWN_BTagSF")
   h300a13_MedIsoMu2_TauDMMedIso_PileupUP = f.Get("SIG_h300a13_MedIsoMu2_TauDMMedIso_APR20_PileupUP_BTagSF")
   h300a15_MedIsoMu2_TauDMMedIso_Central = f.Get("SIG_h300a15_MedIsoMu2_TauDMMedIso_APR20_Central_BTagSF")
   h300a15_MedIsoMu2_TauDMMedIso_IDDOWN = f.Get("SIG_h300a15_MedIsoMu2_TauDMMedIso_APR20_IDDOWN_BTagSF")
   h300a15_MedIsoMu2_TauDMMedIso_IDUP = f.Get("SIG_h300a15_MedIsoMu2_TauDMMedIso_APR20_IDUP_BTagSF")
   h300a15_MedIsoMu2_TauDMMedIso_IsoDOWN = f.Get("SIG_h300a15_MedIsoMu2_TauDMMedIso_APR20_IsoDOWN_BTagSF")
   h300a15_MedIsoMu2_TauDMMedIso_IsoUP = f.Get("SIG_h300a15_MedIsoMu2_TauDMMedIso_APR20_IsoUP_BTagSF")
   h300a15_MedIsoMu2_TauDMMedIso_BTagDOWN = f.Get("SIG_h300a15_MedIsoMu2_TauDMMedIso_APR20_BTagDOWN_BTagSF")
   h300a15_MedIsoMu2_TauDMMedIso_BTagUP = f.Get("SIG_h300a15_MedIsoMu2_TauDMMedIso_APR20_BTagUP_BTagSF")
   h300a15_MedIsoMu2_TauDMMedIso_PileupDOWN = f.Get("SIG_h300a15_MedIsoMu2_TauDMMedIso_APR20_PileupDOWN_BTagSF")
   h300a15_MedIsoMu2_TauDMMedIso_PileupUP = f.Get("SIG_h300a15_MedIsoMu2_TauDMMedIso_APR20_PileupUP_BTagSF")
   h300a17_MedIsoMu2_TauDMMedIso_Central = f.Get("SIG_h300a17_MedIsoMu2_TauDMMedIso_APR20_Central_BTagSF")
   h300a17_MedIsoMu2_TauDMMedIso_IDDOWN = f.Get("SIG_h300a17_MedIsoMu2_TauDMMedIso_APR20_IDDOWN_BTagSF")
   h300a17_MedIsoMu2_TauDMMedIso_IDUP = f.Get("SIG_h300a17_MedIsoMu2_TauDMMedIso_APR20_IDUP_BTagSF")
   h300a17_MedIsoMu2_TauDMMedIso_IsoDOWN = f.Get("SIG_h300a17_MedIsoMu2_TauDMMedIso_APR20_IsoDOWN_BTagSF")
   h300a17_MedIsoMu2_TauDMMedIso_IsoUP = f.Get("SIG_h300a17_MedIsoMu2_TauDMMedIso_APR20_IsoUP_BTagSF")
   h300a17_MedIsoMu2_TauDMMedIso_BTagDOWN = f.Get("SIG_h300a17_MedIsoMu2_TauDMMedIso_APR20_BTagDOWN_BTagSF")
   h300a17_MedIsoMu2_TauDMMedIso_BTagUP = f.Get("SIG_h300a17_MedIsoMu2_TauDMMedIso_APR20_BTagUP_BTagSF")
   h300a17_MedIsoMu2_TauDMMedIso_PileupDOWN = f.Get("SIG_h300a17_MedIsoMu2_TauDMMedIso_APR20_PileupDOWN_BTagSF")
   h300a17_MedIsoMu2_TauDMMedIso_PileupUP = f.Get("SIG_h300a17_MedIsoMu2_TauDMMedIso_APR20_PileupUP_BTagSF")
   h300a19_MedIsoMu2_TauDMMedIso_Central = f.Get("SIG_h300a19_MedIsoMu2_TauDMMedIso_APR20_Central_BTagSF")
   h300a19_MedIsoMu2_TauDMMedIso_IDDOWN = f.Get("SIG_h300a19_MedIsoMu2_TauDMMedIso_APR20_IDDOWN_BTagSF")
   h300a19_MedIsoMu2_TauDMMedIso_IDUP = f.Get("SIG_h300a19_MedIsoMu2_TauDMMedIso_APR20_IDUP_BTagSF")
   h300a19_MedIsoMu2_TauDMMedIso_IsoDOWN = f.Get("SIG_h300a19_MedIsoMu2_TauDMMedIso_APR20_IsoDOWN_BTagSF")
   h300a19_MedIsoMu2_TauDMMedIso_IsoUP = f.Get("SIG_h300a19_MedIsoMu2_TauDMMedIso_APR20_IsoUP_BTagSF")
   h300a19_MedIsoMu2_TauDMMedIso_BTagDOWN = f.Get("SIG_h300a19_MedIsoMu2_TauDMMedIso_APR20_BTagDOWN_BTagSF")
   h300a19_MedIsoMu2_TauDMMedIso_BTagUP = f.Get("SIG_h300a19_MedIsoMu2_TauDMMedIso_APR20_BTagUP_BTagSF")
   h300a19_MedIsoMu2_TauDMMedIso_PileupDOWN = f.Get("SIG_h300a19_MedIsoMu2_TauDMMedIso_APR20_PileupDOWN_BTagSF")
   h300a19_MedIsoMu2_TauDMMedIso_PileupUP = f.Get("SIG_h300a19_MedIsoMu2_TauDMMedIso_APR20_PileupUP_BTagSF")
   h300a21_MedIsoMu2_TauDMMedIso_Central = f.Get("SIG_h300a21_MedIsoMu2_TauDMMedIso_APR20_Central_BTagSF")
   h300a21_MedIsoMu2_TauDMMedIso_IDDOWN = f.Get("SIG_h300a21_MedIsoMu2_TauDMMedIso_APR20_IDDOWN_BTagSF")
   h300a21_MedIsoMu2_TauDMMedIso_IDUP = f.Get("SIG_h300a21_MedIsoMu2_TauDMMedIso_APR20_IDUP_BTagSF")
   h300a21_MedIsoMu2_TauDMMedIso_IsoDOWN = f.Get("SIG_h300a21_MedIsoMu2_TauDMMedIso_APR20_IsoDOWN_BTagSF")
   h300a21_MedIsoMu2_TauDMMedIso_IsoUP = f.Get("SIG_h300a21_MedIsoMu2_TauDMMedIso_APR20_IsoUP_BTagSF")
   h300a21_MedIsoMu2_TauDMMedIso_BTagDOWN = f.Get("SIG_h300a21_MedIsoMu2_TauDMMedIso_APR20_BTagDOWN_BTagSF")
   h300a21_MedIsoMu2_TauDMMedIso_BTagUP = f.Get("SIG_h300a21_MedIsoMu2_TauDMMedIso_APR20_BTagUP_BTagSF")
   h300a21_MedIsoMu2_TauDMMedIso_PileupDOWN = f.Get("SIG_h300a21_MedIsoMu2_TauDMMedIso_APR20_PileupDOWN_BTagSF")
   h300a21_MedIsoMu2_TauDMMedIso_PileupUP = f.Get("SIG_h300a21_MedIsoMu2_TauDMMedIso_APR20_PileupUP_BTagSF")
   h300a5_MedIsoMu2_TauDMMedIso_Central = f.Get("SIG_h300a5_MedIsoMu2_TauDMMedIso_APR20_Central_BTagSF")
   h300a5_MedIsoMu2_TauDMMedIso_IDDOWN = f.Get("SIG_h300a5_MedIsoMu2_TauDMMedIso_APR20_IDDOWN_BTagSF")
   h300a5_MedIsoMu2_TauDMMedIso_IDUP = f.Get("SIG_h300a5_MedIsoMu2_TauDMMedIso_APR20_IDUP_BTagSF")
   h300a5_MedIsoMu2_TauDMMedIso_IsoDOWN = f.Get("SIG_h300a5_MedIsoMu2_TauDMMedIso_APR20_IsoDOWN_BTagSF")
   h300a5_MedIsoMu2_TauDMMedIso_IsoUP = f.Get("SIG_h300a5_MedIsoMu2_TauDMMedIso_APR20_IsoUP_BTagSF")
   h300a5_MedIsoMu2_TauDMMedIso_BTagDOWN = f.Get("SIG_h300a5_MedIsoMu2_TauDMMedIso_APR20_BTagDOWN_BTagSF")
   h300a5_MedIsoMu2_TauDMMedIso_BTagUP = f.Get("SIG_h300a5_MedIsoMu2_TauDMMedIso_APR20_BTagUP_BTagSF")
   h300a5_MedIsoMu2_TauDMMedIso_PileupDOWN = f.Get("SIG_h300a5_MedIsoMu2_TauDMMedIso_APR20_PileupDOWN_BTagSF")
   h300a5_MedIsoMu2_TauDMMedIso_PileupUP = f.Get("SIG_h300a5_MedIsoMu2_TauDMMedIso_APR20_PileupUP_BTagSF")
   h300a7_MedIsoMu2_TauDMMedIso_Central = f.Get("SIG_h300a7_MedIsoMu2_TauDMMedIso_APR20_Central_BTagSF")
   h300a7_MedIsoMu2_TauDMMedIso_IDDOWN = f.Get("SIG_h300a7_MedIsoMu2_TauDMMedIso_APR20_IDDOWN_BTagSF")
   h300a7_MedIsoMu2_TauDMMedIso_IDUP = f.Get("SIG_h300a7_MedIsoMu2_TauDMMedIso_APR20_IDUP_BTagSF")
   h300a7_MedIsoMu2_TauDMMedIso_IsoDOWN = f.Get("SIG_h300a7_MedIsoMu2_TauDMMedIso_APR20_IsoDOWN_BTagSF")
   h300a7_MedIsoMu2_TauDMMedIso_IsoUP = f.Get("SIG_h300a7_MedIsoMu2_TauDMMedIso_APR20_IsoUP_BTagSF")
   h300a7_MedIsoMu2_TauDMMedIso_BTagDOWN = f.Get("SIG_h300a7_MedIsoMu2_TauDMMedIso_APR20_BTagDOWN_BTagSF")
   h300a7_MedIsoMu2_TauDMMedIso_BTagUP = f.Get("SIG_h300a7_MedIsoMu2_TauDMMedIso_APR20_BTagUP_BTagSF")
   h300a7_MedIsoMu2_TauDMMedIso_PileupDOWN = f.Get("SIG_h300a7_MedIsoMu2_TauDMMedIso_APR20_PileupDOWN_BTagSF")
   h300a7_MedIsoMu2_TauDMMedIso_PileupUP = f.Get("SIG_h300a7_MedIsoMu2_TauDMMedIso_APR20_PileupUP_BTagSF")
   h300a9_MedIsoMu2_TauDMMedIso_Central = f.Get("SIG_h300a9_MedIsoMu2_TauDMMedIso_APR20_Central_BTagSF")
   h300a9_MedIsoMu2_TauDMMedIso_IDDOWN = f.Get("SIG_h300a9_MedIsoMu2_TauDMMedIso_APR20_IDDOWN_BTagSF")
   h300a9_MedIsoMu2_TauDMMedIso_IDUP = f.Get("SIG_h300a9_MedIsoMu2_TauDMMedIso_APR20_IDUP_BTagSF")
   h300a9_MedIsoMu2_TauDMMedIso_IsoDOWN = f.Get("SIG_h300a9_MedIsoMu2_TauDMMedIso_APR20_IsoDOWN_BTagSF")
   h300a9_MedIsoMu2_TauDMMedIso_IsoUP = f.Get("SIG_h300a9_MedIsoMu2_TauDMMedIso_APR20_IsoUP_BTagSF")
   h300a9_MedIsoMu2_TauDMMedIso_BTagDOWN = f.Get("SIG_h300a9_MedIsoMu2_TauDMMedIso_APR20_BTagDOWN_BTagSF")
   h300a9_MedIsoMu2_TauDMMedIso_BTagUP = f.Get("SIG_h300a9_MedIsoMu2_TauDMMedIso_APR20_BTagUP_BTagSF")
   h300a9_MedIsoMu2_TauDMMedIso_PileupDOWN = f.Get("SIG_h300a9_MedIsoMu2_TauDMMedIso_APR20_PileupDOWN_BTagSF")
   h300a9_MedIsoMu2_TauDMMedIso_PileupUP = f.Get("SIG_h300a9_MedIsoMu2_TauDMMedIso_APR20_PileupUP_BTagSF")
   h750a11_MedIsoMu2_TauDMMedIso_Central = f.Get("SIG_h750a11_MedIsoMu2_TauDMMedIso_APR20_Central_BTagSF")
   h750a11_MedIsoMu2_TauDMMedIso_IDDOWN = f.Get("SIG_h750a11_MedIsoMu2_TauDMMedIso_APR20_IDDOWN_BTagSF")
   h750a11_MedIsoMu2_TauDMMedIso_IDUP = f.Get("SIG_h750a11_MedIsoMu2_TauDMMedIso_APR20_IDUP_BTagSF")
   h750a11_MedIsoMu2_TauDMMedIso_IsoDOWN = f.Get("SIG_h750a11_MedIsoMu2_TauDMMedIso_APR20_IsoDOWN_BTagSF")
   h750a11_MedIsoMu2_TauDMMedIso_IsoUP = f.Get("SIG_h750a11_MedIsoMu2_TauDMMedIso_APR20_IsoUP_BTagSF")
   h750a11_MedIsoMu2_TauDMMedIso_BTagDOWN = f.Get("SIG_h750a11_MedIsoMu2_TauDMMedIso_APR20_BTagDOWN_BTagSF")
   h750a11_MedIsoMu2_TauDMMedIso_BTagUP = f.Get("SIG_h750a11_MedIsoMu2_TauDMMedIso_APR20_BTagUP_BTagSF")
   h750a11_MedIsoMu2_TauDMMedIso_PileupDOWN = f.Get("SIG_h750a11_MedIsoMu2_TauDMMedIso_APR20_PileupDOWN_BTagSF")
   h750a11_MedIsoMu2_TauDMMedIso_PileupUP = f.Get("SIG_h750a11_MedIsoMu2_TauDMMedIso_APR20_PileupUP_BTagSF")
   h750a13_MedIsoMu2_TauDMMedIso_Central = f.Get("SIG_h750a13_MedIsoMu2_TauDMMedIso_APR20_Central_BTagSF")
   h750a13_MedIsoMu2_TauDMMedIso_IDDOWN = f.Get("SIG_h750a13_MedIsoMu2_TauDMMedIso_APR20_IDDOWN_BTagSF")
   h750a13_MedIsoMu2_TauDMMedIso_IDUP = f.Get("SIG_h750a13_MedIsoMu2_TauDMMedIso_APR20_IDUP_BTagSF")
   h750a13_MedIsoMu2_TauDMMedIso_IsoDOWN = f.Get("SIG_h750a13_MedIsoMu2_TauDMMedIso_APR20_IsoDOWN_BTagSF")
   h750a13_MedIsoMu2_TauDMMedIso_IsoUP = f.Get("SIG_h750a13_MedIsoMu2_TauDMMedIso_APR20_IsoUP_BTagSF")
   h750a13_MedIsoMu2_TauDMMedIso_BTagDOWN = f.Get("SIG_h750a13_MedIsoMu2_TauDMMedIso_APR20_BTagDOWN_BTagSF")
   h750a13_MedIsoMu2_TauDMMedIso_BTagUP = f.Get("SIG_h750a13_MedIsoMu2_TauDMMedIso_APR20_BTagUP_BTagSF")
   h750a13_MedIsoMu2_TauDMMedIso_PileupDOWN = f.Get("SIG_h750a13_MedIsoMu2_TauDMMedIso_APR20_PileupDOWN_BTagSF")
   h750a13_MedIsoMu2_TauDMMedIso_PileupUP = f.Get("SIG_h750a13_MedIsoMu2_TauDMMedIso_APR20_PileupUP_BTagSF")
   h750a15_MedIsoMu2_TauDMMedIso_Central = f.Get("SIG_h750a15_MedIsoMu2_TauDMMedIso_APR20_Central_BTagSF")
   h750a15_MedIsoMu2_TauDMMedIso_IDDOWN = f.Get("SIG_h750a15_MedIsoMu2_TauDMMedIso_APR20_IDDOWN_BTagSF")
   h750a15_MedIsoMu2_TauDMMedIso_IDUP = f.Get("SIG_h750a15_MedIsoMu2_TauDMMedIso_APR20_IDUP_BTagSF")
   h750a15_MedIsoMu2_TauDMMedIso_IsoDOWN = f.Get("SIG_h750a15_MedIsoMu2_TauDMMedIso_APR20_IsoDOWN_BTagSF")
   h750a15_MedIsoMu2_TauDMMedIso_IsoUP = f.Get("SIG_h750a15_MedIsoMu2_TauDMMedIso_APR20_IsoUP_BTagSF")
   h750a15_MedIsoMu2_TauDMMedIso_BTagDOWN = f.Get("SIG_h750a15_MedIsoMu2_TauDMMedIso_APR20_BTagDOWN_BTagSF")
   h750a15_MedIsoMu2_TauDMMedIso_BTagUP = f.Get("SIG_h750a15_MedIsoMu2_TauDMMedIso_APR20_BTagUP_BTagSF")
   h750a15_MedIsoMu2_TauDMMedIso_PileupDOWN = f.Get("SIG_h750a15_MedIsoMu2_TauDMMedIso_APR20_PileupDOWN_BTagSF")
   h750a15_MedIsoMu2_TauDMMedIso_PileupUP = f.Get("SIG_h750a15_MedIsoMu2_TauDMMedIso_APR20_PileupUP_BTagSF")
   h750a17_MedIsoMu2_TauDMMedIso_Central = f.Get("SIG_h750a17_MedIsoMu2_TauDMMedIso_APR20_Central_BTagSF")
   h750a17_MedIsoMu2_TauDMMedIso_IDDOWN = f.Get("SIG_h750a17_MedIsoMu2_TauDMMedIso_APR20_IDDOWN_BTagSF")
   h750a17_MedIsoMu2_TauDMMedIso_IDUP = f.Get("SIG_h750a17_MedIsoMu2_TauDMMedIso_APR20_IDUP_BTagSF")
   h750a17_MedIsoMu2_TauDMMedIso_IsoDOWN = f.Get("SIG_h750a17_MedIsoMu2_TauDMMedIso_APR20_IsoDOWN_BTagSF")
   h750a17_MedIsoMu2_TauDMMedIso_IsoUP = f.Get("SIG_h750a17_MedIsoMu2_TauDMMedIso_APR20_IsoUP_BTagSF")
   h750a17_MedIsoMu2_TauDMMedIso_BTagDOWN = f.Get("SIG_h750a17_MedIsoMu2_TauDMMedIso_APR20_BTagDOWN_BTagSF")
   h750a17_MedIsoMu2_TauDMMedIso_BTagUP = f.Get("SIG_h750a17_MedIsoMu2_TauDMMedIso_APR20_BTagUP_BTagSF")
   h750a17_MedIsoMu2_TauDMMedIso_PileupDOWN = f.Get("SIG_h750a17_MedIsoMu2_TauDMMedIso_APR20_PileupDOWN_BTagSF")
   h750a17_MedIsoMu2_TauDMMedIso_PileupUP = f.Get("SIG_h750a17_MedIsoMu2_TauDMMedIso_APR20_PileupUP_BTagSF")
   h750a19_MedIsoMu2_TauDMMedIso_Central = f.Get("SIG_h750a19_MedIsoMu2_TauDMMedIso_APR20_Central_BTagSF")
   h750a19_MedIsoMu2_TauDMMedIso_IDDOWN = f.Get("SIG_h750a19_MedIsoMu2_TauDMMedIso_APR20_IDDOWN_BTagSF")
   h750a19_MedIsoMu2_TauDMMedIso_IDUP = f.Get("SIG_h750a19_MedIsoMu2_TauDMMedIso_APR20_IDUP_BTagSF")
   h750a19_MedIsoMu2_TauDMMedIso_IsoDOWN = f.Get("SIG_h750a19_MedIsoMu2_TauDMMedIso_APR20_IsoDOWN_BTagSF")
   h750a19_MedIsoMu2_TauDMMedIso_IsoUP = f.Get("SIG_h750a19_MedIsoMu2_TauDMMedIso_APR20_IsoUP_BTagSF")
   h750a19_MedIsoMu2_TauDMMedIso_BTagDOWN = f.Get("SIG_h750a19_MedIsoMu2_TauDMMedIso_APR20_BTagDOWN_BTagSF")
   h750a19_MedIsoMu2_TauDMMedIso_BTagUP = f.Get("SIG_h750a19_MedIsoMu2_TauDMMedIso_APR20_BTagUP_BTagSF")
   h750a19_MedIsoMu2_TauDMMedIso_PileupDOWN = f.Get("SIG_h750a19_MedIsoMu2_TauDMMedIso_APR20_PileupDOWN_BTagSF")
   h750a19_MedIsoMu2_TauDMMedIso_PileupUP = f.Get("SIG_h750a19_MedIsoMu2_TauDMMedIso_APR20_PileupUP_BTagSF")
   h750a21_MedIsoMu2_TauDMMedIso_Central = f.Get("SIG_h750a21_MedIsoMu2_TauDMMedIso_APR20_Central_BTagSF")
   h750a21_MedIsoMu2_TauDMMedIso_IDDOWN = f.Get("SIG_h750a21_MedIsoMu2_TauDMMedIso_APR20_IDDOWN_BTagSF")
   h750a21_MedIsoMu2_TauDMMedIso_IDUP = f.Get("SIG_h750a21_MedIsoMu2_TauDMMedIso_APR20_IDUP_BTagSF")
   h750a21_MedIsoMu2_TauDMMedIso_IsoDOWN = f.Get("SIG_h750a21_MedIsoMu2_TauDMMedIso_APR20_IsoDOWN_BTagSF")
   h750a21_MedIsoMu2_TauDMMedIso_IsoUP = f.Get("SIG_h750a21_MedIsoMu2_TauDMMedIso_APR20_IsoUP_BTagSF")
   h750a21_MedIsoMu2_TauDMMedIso_BTagDOWN = f.Get("SIG_h750a21_MedIsoMu2_TauDMMedIso_APR20_BTagDOWN_BTagSF")
   h750a21_MedIsoMu2_TauDMMedIso_BTagUP = f.Get("SIG_h750a21_MedIsoMu2_TauDMMedIso_APR20_BTagUP_BTagSF")
   h750a21_MedIsoMu2_TauDMMedIso_PileupDOWN = f.Get("SIG_h750a21_MedIsoMu2_TauDMMedIso_APR20_PileupDOWN_BTagSF")
   h750a21_MedIsoMu2_TauDMMedIso_PileupUP = f.Get("SIG_h750a21_MedIsoMu2_TauDMMedIso_APR20_PileupUP_BTagSF")
   h750a5_MedIsoMu2_TauDMMedIso_Central = f.Get("SIG_h750a5_MedIsoMu2_TauDMMedIso_APR20_Central_BTagSF")
   h750a5_MedIsoMu2_TauDMMedIso_IDDOWN = f.Get("SIG_h750a5_MedIsoMu2_TauDMMedIso_APR20_IDDOWN_BTagSF")
   h750a5_MedIsoMu2_TauDMMedIso_IDUP = f.Get("SIG_h750a5_MedIsoMu2_TauDMMedIso_APR20_IDUP_BTagSF")
   h750a5_MedIsoMu2_TauDMMedIso_IsoDOWN = f.Get("SIG_h750a5_MedIsoMu2_TauDMMedIso_APR20_IsoDOWN_BTagSF")
   h750a5_MedIsoMu2_TauDMMedIso_IsoUP = f.Get("SIG_h750a5_MedIsoMu2_TauDMMedIso_APR20_IsoUP_BTagSF")
   h750a5_MedIsoMu2_TauDMMedIso_BTagDOWN = f.Get("SIG_h750a5_MedIsoMu2_TauDMMedIso_APR20_BTagDOWN_BTagSF")
   h750a5_MedIsoMu2_TauDMMedIso_BTagUP = f.Get("SIG_h750a5_MedIsoMu2_TauDMMedIso_APR20_BTagUP_BTagSF")
   h750a5_MedIsoMu2_TauDMMedIso_PileupDOWN = f.Get("SIG_h750a5_MedIsoMu2_TauDMMedIso_APR20_PileupDOWN_BTagSF")
   h750a5_MedIsoMu2_TauDMMedIso_PileupUP = f.Get("SIG_h750a5_MedIsoMu2_TauDMMedIso_APR20_PileupUP_BTagSF")
   h750a7_MedIsoMu2_TauDMMedIso_Central = f.Get("SIG_h750a7_MedIsoMu2_TauDMMedIso_APR20_Central_BTagSF")
   h750a7_MedIsoMu2_TauDMMedIso_IDDOWN = f.Get("SIG_h750a7_MedIsoMu2_TauDMMedIso_APR20_IDDOWN_BTagSF")
   h750a7_MedIsoMu2_TauDMMedIso_IDUP = f.Get("SIG_h750a7_MedIsoMu2_TauDMMedIso_APR20_IDUP_BTagSF")
   h750a7_MedIsoMu2_TauDMMedIso_IsoDOWN = f.Get("SIG_h750a7_MedIsoMu2_TauDMMedIso_APR20_IsoDOWN_BTagSF")
   h750a7_MedIsoMu2_TauDMMedIso_IsoUP = f.Get("SIG_h750a7_MedIsoMu2_TauDMMedIso_APR20_IsoUP_BTagSF")
   h750a7_MedIsoMu2_TauDMMedIso_BTagDOWN = f.Get("SIG_h750a7_MedIsoMu2_TauDMMedIso_APR20_BTagDOWN_BTagSF")
   h750a7_MedIsoMu2_TauDMMedIso_BTagUP = f.Get("SIG_h750a7_MedIsoMu2_TauDMMedIso_APR20_BTagUP_BTagSF")
   h750a7_MedIsoMu2_TauDMMedIso_PileupDOWN = f.Get("SIG_h750a7_MedIsoMu2_TauDMMedIso_APR20_PileupDOWN_BTagSF")
   h750a7_MedIsoMu2_TauDMMedIso_PileupUP = f.Get("SIG_h750a7_MedIsoMu2_TauDMMedIso_APR20_PileupUP_BTagSF")
   h750a9_MedIsoMu2_TauDMMedIso_Central = f.Get("SIG_h750a9_MedIsoMu2_TauDMMedIso_APR20_Central_BTagSF")
   h750a9_MedIsoMu2_TauDMMedIso_IDDOWN = f.Get("SIG_h750a9_MedIsoMu2_TauDMMedIso_APR20_IDDOWN_BTagSF")
   h750a9_MedIsoMu2_TauDMMedIso_IDUP = f.Get("SIG_h750a9_MedIsoMu2_TauDMMedIso_APR20_IDUP_BTagSF")
   h750a9_MedIsoMu2_TauDMMedIso_IsoDOWN = f.Get("SIG_h750a9_MedIsoMu2_TauDMMedIso_APR20_IsoDOWN_BTagSF")
   h750a9_MedIsoMu2_TauDMMedIso_IsoUP = f.Get("SIG_h750a9_MedIsoMu2_TauDMMedIso_APR20_IsoUP_BTagSF")
   h750a9_MedIsoMu2_TauDMMedIso_BTagDOWN = f.Get("SIG_h750a9_MedIsoMu2_TauDMMedIso_APR20_BTagDOWN_BTagSF")
   h750a9_MedIsoMu2_TauDMMedIso_BTagUP = f.Get("SIG_h750a9_MedIsoMu2_TauDMMedIso_APR20_BTagUP_BTagSF")
   h750a9_MedIsoMu2_TauDMMedIso_PileupDOWN = f.Get("SIG_h750a9_MedIsoMu2_TauDMMedIso_APR20_PileupDOWN_BTagSF")
   h750a9_MedIsoMu2_TauDMMedIso_PileupUP = f.Get("SIG_h750a9_MedIsoMu2_TauDMMedIso_APR20_PileupUP_BTagSF")

#   h125a11_MedIsoMu2_TauDMMedIso_Central = ScaleRooDataSets(h125a11_MedIsoMu2_TauDMMedIso_Central, scale=.001)
#   h125a11_MedIsoMu2_TauDMMedIso_IDDOWN = ScaleRooDataSets(h125a11_MedIsoMu2_TauDMMedIso_IDDOWN, scale=.001)
#   h125a11_MedIsoMu2_TauDMMedIso_IDUP = ScaleRooDataSets(h125a11_MedIsoMu2_TauDMMedIso_IDUP, scale=.001)
#   h125a11_MedIsoMu2_TauDMMedIso_IsoDOWN = ScaleRooDataSets(h125a11_MedIsoMu2_TauDMMedIso_IsoDOWN, scale=.001)
#   h125a11_MedIsoMu2_TauDMMedIso_IsoUP = ScaleRooDataSets(h125a11_MedIsoMu2_TauDMMedIso_IsoUP, scale=.001)
#   h125a11_MedIsoMu2_TauDMMedIso_BTagDOWN = ScaleRooDataSets(h125a11_MedIsoMu2_TauDMMedIso_BTagDOWN, scale=.001)
#   h125a11_MedIsoMu2_TauDMMedIso_BTagUP = ScaleRooDataSets(h125a11_MedIsoMu2_TauDMMedIso_BTagUP, scale=.001)
#   h125a11_MedIsoMu2_TauDMMedIso_PileupDOWN = ScaleRooDataSets(h125a11_MedIsoMu2_TauDMMedIso_PileupDOWN, scale=.001)
#   h125a11_MedIsoMu2_TauDMMedIso_PileupUP = ScaleRooDataSets(h125a11_MedIsoMu2_TauDMMedIso_PileupUP, scale=.001)
#   h125a13_MedIsoMu2_TauDMMedIso_Central = ScaleRooDataSets(h125a13_MedIsoMu2_TauDMMedIso_Central, scale=.001)
#   h125a13_MedIsoMu2_TauDMMedIso_IDDOWN = ScaleRooDataSets(h125a13_MedIsoMu2_TauDMMedIso_IDDOWN, scale=.001)
#   h125a13_MedIsoMu2_TauDMMedIso_IDUP = ScaleRooDataSets(h125a13_MedIsoMu2_TauDMMedIso_IDUP, scale=.001)
#   h125a13_MedIsoMu2_TauDMMedIso_IsoDOWN = ScaleRooDataSets(h125a13_MedIsoMu2_TauDMMedIso_IsoDOWN, scale=.001)
#   h125a13_MedIsoMu2_TauDMMedIso_IsoUP = ScaleRooDataSets(h125a13_MedIsoMu2_TauDMMedIso_IsoUP, scale=.001)
#   h125a13_MedIsoMu2_TauDMMedIso_BTagDOWN = ScaleRooDataSets(h125a13_MedIsoMu2_TauDMMedIso_BTagDOWN, scale=.001)
#   h125a13_MedIsoMu2_TauDMMedIso_BTagUP = ScaleRooDataSets(h125a13_MedIsoMu2_TauDMMedIso_BTagUP, scale=.001)
#   h125a13_MedIsoMu2_TauDMMedIso_PileupDOWN = ScaleRooDataSets(h125a13_MedIsoMu2_TauDMMedIso_PileupDOWN, scale=.001)
#   h125a13_MedIsoMu2_TauDMMedIso_PileupUP = ScaleRooDataSets(h125a13_MedIsoMu2_TauDMMedIso_PileupUP, scale=.001)
#   h125a15_MedIsoMu2_TauDMMedIso_Central = ScaleRooDataSets(h125a15_MedIsoMu2_TauDMMedIso_Central, scale=.001)
#   h125a15_MedIsoMu2_TauDMMedIso_IDDOWN = ScaleRooDataSets(h125a15_MedIsoMu2_TauDMMedIso_IDDOWN, scale=.001)
#   h125a15_MedIsoMu2_TauDMMedIso_IDUP = ScaleRooDataSets(h125a15_MedIsoMu2_TauDMMedIso_IDUP, scale=.001)
#   h125a15_MedIsoMu2_TauDMMedIso_IsoDOWN = ScaleRooDataSets(h125a15_MedIsoMu2_TauDMMedIso_IsoDOWN, scale=.001)
#   h125a15_MedIsoMu2_TauDMMedIso_IsoUP = ScaleRooDataSets(h125a15_MedIsoMu2_TauDMMedIso_IsoUP, scale=.001)
#   h125a15_MedIsoMu2_TauDMMedIso_BTagDOWN = ScaleRooDataSets(h125a15_MedIsoMu2_TauDMMedIso_BTagDOWN, scale=.001)
#   h125a15_MedIsoMu2_TauDMMedIso_BTagUP = ScaleRooDataSets(h125a15_MedIsoMu2_TauDMMedIso_BTagUP, scale=.001)
#   h125a15_MedIsoMu2_TauDMMedIso_PileupDOWN = ScaleRooDataSets(h125a15_MedIsoMu2_TauDMMedIso_PileupDOWN, scale=.001)
#   h125a15_MedIsoMu2_TauDMMedIso_PileupUP = ScaleRooDataSets(h125a15_MedIsoMu2_TauDMMedIso_PileupUP, scale=.001)
#   h125a17_MedIsoMu2_TauDMMedIso_Central = ScaleRooDataSets(h125a17_MedIsoMu2_TauDMMedIso_Central, scale=.001)
#   h125a17_MedIsoMu2_TauDMMedIso_IDDOWN = ScaleRooDataSets(h125a17_MedIsoMu2_TauDMMedIso_IDDOWN, scale=.001)
#   h125a17_MedIsoMu2_TauDMMedIso_IDUP = ScaleRooDataSets(h125a17_MedIsoMu2_TauDMMedIso_IDUP, scale=.001)
#   h125a17_MedIsoMu2_TauDMMedIso_IsoDOWN = ScaleRooDataSets(h125a17_MedIsoMu2_TauDMMedIso_IsoDOWN, scale=.001)
#   h125a17_MedIsoMu2_TauDMMedIso_IsoUP = ScaleRooDataSets(h125a17_MedIsoMu2_TauDMMedIso_IsoUP, scale=.001)
#   h125a17_MedIsoMu2_TauDMMedIso_BTagDOWN = ScaleRooDataSets(h125a17_MedIsoMu2_TauDMMedIso_BTagDOWN, scale=.001)
#   h125a17_MedIsoMu2_TauDMMedIso_BTagUP = ScaleRooDataSets(h125a17_MedIsoMu2_TauDMMedIso_BTagUP, scale=.001)
#   h125a17_MedIsoMu2_TauDMMedIso_PileupDOWN = ScaleRooDataSets(h125a17_MedIsoMu2_TauDMMedIso_PileupDOWN, scale=.001)
#   h125a17_MedIsoMu2_TauDMMedIso_PileupUP = ScaleRooDataSets(h125a17_MedIsoMu2_TauDMMedIso_PileupUP, scale=.001)
#   h125a19_MedIsoMu2_TauDMMedIso_Central = ScaleRooDataSets(h125a19_MedIsoMu2_TauDMMedIso_Central, scale=.001)
#   h125a19_MedIsoMu2_TauDMMedIso_IDDOWN = ScaleRooDataSets(h125a19_MedIsoMu2_TauDMMedIso_IDDOWN, scale=.001)
#   h125a19_MedIsoMu2_TauDMMedIso_IDUP = ScaleRooDataSets(h125a19_MedIsoMu2_TauDMMedIso_IDUP, scale=.001)
#   h125a19_MedIsoMu2_TauDMMedIso_IsoDOWN = ScaleRooDataSets(h125a19_MedIsoMu2_TauDMMedIso_IsoDOWN, scale=.001)
#   h125a19_MedIsoMu2_TauDMMedIso_IsoUP = ScaleRooDataSets(h125a19_MedIsoMu2_TauDMMedIso_IsoUP, scale=.001)
#   h125a19_MedIsoMu2_TauDMMedIso_BTagDOWN = ScaleRooDataSets(h125a19_MedIsoMu2_TauDMMedIso_BTagDOWN, scale=.001)
#   h125a19_MedIsoMu2_TauDMMedIso_BTagUP = ScaleRooDataSets(h125a19_MedIsoMu2_TauDMMedIso_BTagUP, scale=.001)
#   h125a19_MedIsoMu2_TauDMMedIso_PileupDOWN = ScaleRooDataSets(h125a19_MedIsoMu2_TauDMMedIso_PileupDOWN, scale=.001)
#   h125a19_MedIsoMu2_TauDMMedIso_PileupUP = ScaleRooDataSets(h125a19_MedIsoMu2_TauDMMedIso_PileupUP, scale=.001)
#   h125a21_MedIsoMu2_TauDMMedIso_Central = ScaleRooDataSets(h125a21_MedIsoMu2_TauDMMedIso_Central, scale=.001)
#   h125a21_MedIsoMu2_TauDMMedIso_IDDOWN = ScaleRooDataSets(h125a21_MedIsoMu2_TauDMMedIso_IDDOWN, scale=.001)
#   h125a21_MedIsoMu2_TauDMMedIso_IDUP = ScaleRooDataSets(h125a21_MedIsoMu2_TauDMMedIso_IDUP, scale=.001)
#   h125a21_MedIsoMu2_TauDMMedIso_IsoDOWN = ScaleRooDataSets(h125a21_MedIsoMu2_TauDMMedIso_IsoDOWN, scale=.001)
#   h125a21_MedIsoMu2_TauDMMedIso_IsoUP = ScaleRooDataSets(h125a21_MedIsoMu2_TauDMMedIso_IsoUP, scale=.001)
#   h125a21_MedIsoMu2_TauDMMedIso_BTagDOWN = ScaleRooDataSets(h125a21_MedIsoMu2_TauDMMedIso_BTagDOWN, scale=.001)
#   h125a21_MedIsoMu2_TauDMMedIso_BTagUP = ScaleRooDataSets(h125a21_MedIsoMu2_TauDMMedIso_BTagUP, scale=.001)
#   h125a21_MedIsoMu2_TauDMMedIso_PileupDOWN = ScaleRooDataSets(h125a21_MedIsoMu2_TauDMMedIso_PileupDOWN, scale=.001)
#   h125a21_MedIsoMu2_TauDMMedIso_PileupUP = ScaleRooDataSets(h125a21_MedIsoMu2_TauDMMedIso_PileupUP, scale=.001)
#   h125a5_MedIsoMu2_TauDMMedIso_Central = ScaleRooDataSets(h125a5_MedIsoMu2_TauDMMedIso_Central, scale=.001)
#   h125a5_MedIsoMu2_TauDMMedIso_IDDOWN = ScaleRooDataSets(h125a5_MedIsoMu2_TauDMMedIso_IDDOWN, scale=.001)
#   h125a5_MedIsoMu2_TauDMMedIso_IDUP = ScaleRooDataSets(h125a5_MedIsoMu2_TauDMMedIso_IDUP, scale=.001)
#   h125a5_MedIsoMu2_TauDMMedIso_IsoDOWN = ScaleRooDataSets(h125a5_MedIsoMu2_TauDMMedIso_IsoDOWN, scale=.001)
#   h125a5_MedIsoMu2_TauDMMedIso_IsoUP = ScaleRooDataSets(h125a5_MedIsoMu2_TauDMMedIso_IsoUP, scale=.001)
#   h125a5_MedIsoMu2_TauDMMedIso_BTagDOWN = ScaleRooDataSets(h125a5_MedIsoMu2_TauDMMedIso_BTagDOWN, scale=.001)
#   h125a5_MedIsoMu2_TauDMMedIso_BTagUP = ScaleRooDataSets(h125a5_MedIsoMu2_TauDMMedIso_BTagUP, scale=.001)
#   h125a5_MedIsoMu2_TauDMMedIso_PileupDOWN = ScaleRooDataSets(h125a5_MedIsoMu2_TauDMMedIso_PileupDOWN, scale=.001)
#   h125a5_MedIsoMu2_TauDMMedIso_PileupUP = ScaleRooDataSets(h125a5_MedIsoMu2_TauDMMedIso_PileupUP, scale=.001)
#   h125a7_MedIsoMu2_TauDMMedIso_Central = ScaleRooDataSets(h125a7_MedIsoMu2_TauDMMedIso_Central, scale=.001)
#   h125a7_MedIsoMu2_TauDMMedIso_IDDOWN = ScaleRooDataSets(h125a7_MedIsoMu2_TauDMMedIso_IDDOWN, scale=.001)
#   h125a7_MedIsoMu2_TauDMMedIso_IDUP = ScaleRooDataSets(h125a7_MedIsoMu2_TauDMMedIso_IDUP, scale=.001)
#   h125a7_MedIsoMu2_TauDMMedIso_IsoDOWN = ScaleRooDataSets(h125a7_MedIsoMu2_TauDMMedIso_IsoDOWN, scale=.001)
#   h125a7_MedIsoMu2_TauDMMedIso_IsoUP = ScaleRooDataSets(h125a7_MedIsoMu2_TauDMMedIso_IsoUP, scale=.001)
#   h125a7_MedIsoMu2_TauDMMedIso_BTagDOWN = ScaleRooDataSets(h125a7_MedIsoMu2_TauDMMedIso_BTagDOWN, scale=.001)
#   h125a7_MedIsoMu2_TauDMMedIso_BTagUP = ScaleRooDataSets(h125a7_MedIsoMu2_TauDMMedIso_BTagUP, scale=.001)
#   h125a7_MedIsoMu2_TauDMMedIso_PileupDOWN = ScaleRooDataSets(h125a7_MedIsoMu2_TauDMMedIso_PileupDOWN, scale=.001)
#   h125a7_MedIsoMu2_TauDMMedIso_PileupUP = ScaleRooDataSets(h125a7_MedIsoMu2_TauDMMedIso_PileupUP, scale=.001)
#   h125a9_MedIsoMu2_TauDMMedIso_Central = ScaleRooDataSets(h125a9_MedIsoMu2_TauDMMedIso_Central, scale=.001)
#   h125a9_MedIsoMu2_TauDMMedIso_IDDOWN = ScaleRooDataSets(h125a9_MedIsoMu2_TauDMMedIso_IDDOWN, scale=.001)
#   h125a9_MedIsoMu2_TauDMMedIso_IDUP = ScaleRooDataSets(h125a9_MedIsoMu2_TauDMMedIso_IDUP, scale=.001)
#   h125a9_MedIsoMu2_TauDMMedIso_IsoDOWN = ScaleRooDataSets(h125a9_MedIsoMu2_TauDMMedIso_IsoDOWN, scale=.001)
#   h125a9_MedIsoMu2_TauDMMedIso_IsoUP = ScaleRooDataSets(h125a9_MedIsoMu2_TauDMMedIso_IsoUP, scale=.001)
#   h125a9_MedIsoMu2_TauDMMedIso_BTagDOWN = ScaleRooDataSets(h125a9_MedIsoMu2_TauDMMedIso_BTagDOWN, scale=.001)
#   h125a9_MedIsoMu2_TauDMMedIso_BTagUP = ScaleRooDataSets(h125a9_MedIsoMu2_TauDMMedIso_BTagUP, scale=.001)
#   h125a9_MedIsoMu2_TauDMMedIso_PileupDOWN = ScaleRooDataSets(h125a9_MedIsoMu2_TauDMMedIso_PileupDOWN, scale=.001)
#   h125a9_MedIsoMu2_TauDMMedIso_PileupUP = ScaleRooDataSets(h125a9_MedIsoMu2_TauDMMedIso_PileupUP, scale=.001)
#   h300a11_MedIsoMu2_TauDMMedIso_Central = ScaleRooDataSets(h300a11_MedIsoMu2_TauDMMedIso_Central, scale=.001)
#   h300a11_MedIsoMu2_TauDMMedIso_IDDOWN = ScaleRooDataSets(h300a11_MedIsoMu2_TauDMMedIso_IDDOWN, scale=.001)
#   h300a11_MedIsoMu2_TauDMMedIso_IDUP = ScaleRooDataSets(h300a11_MedIsoMu2_TauDMMedIso_IDUP, scale=.001)
#   h300a11_MedIsoMu2_TauDMMedIso_IsoDOWN = ScaleRooDataSets(h300a11_MedIsoMu2_TauDMMedIso_IsoDOWN, scale=.001)
#   h300a11_MedIsoMu2_TauDMMedIso_IsoUP = ScaleRooDataSets(h300a11_MedIsoMu2_TauDMMedIso_IsoUP, scale=.001)
#   h300a11_MedIsoMu2_TauDMMedIso_BTagDOWN = ScaleRooDataSets(h300a11_MedIsoMu2_TauDMMedIso_BTagDOWN, scale=.001)
#   h300a11_MedIsoMu2_TauDMMedIso_BTagUP = ScaleRooDataSets(h300a11_MedIsoMu2_TauDMMedIso_BTagUP, scale=.001)
#   h300a11_MedIsoMu2_TauDMMedIso_PileupDOWN = ScaleRooDataSets(h300a11_MedIsoMu2_TauDMMedIso_PileupDOWN, scale=.001)
#   h300a11_MedIsoMu2_TauDMMedIso_PileupUP = ScaleRooDataSets(h300a11_MedIsoMu2_TauDMMedIso_PileupUP, scale=.001)
#   h300a13_MedIsoMu2_TauDMMedIso_Central = ScaleRooDataSets(h300a13_MedIsoMu2_TauDMMedIso_Central, scale=.001)
#   h300a13_MedIsoMu2_TauDMMedIso_IDDOWN = ScaleRooDataSets(h300a13_MedIsoMu2_TauDMMedIso_IDDOWN, scale=.001)
#   h300a13_MedIsoMu2_TauDMMedIso_IDUP = ScaleRooDataSets(h300a13_MedIsoMu2_TauDMMedIso_IDUP, scale=.001)
#   h300a13_MedIsoMu2_TauDMMedIso_IsoDOWN = ScaleRooDataSets(h300a13_MedIsoMu2_TauDMMedIso_IsoDOWN, scale=.001)
#   h300a13_MedIsoMu2_TauDMMedIso_IsoUP = ScaleRooDataSets(h300a13_MedIsoMu2_TauDMMedIso_IsoUP, scale=.001)
#   h300a13_MedIsoMu2_TauDMMedIso_BTagDOWN = ScaleRooDataSets(h300a13_MedIsoMu2_TauDMMedIso_BTagDOWN, scale=.001)
#   h300a13_MedIsoMu2_TauDMMedIso_BTagUP = ScaleRooDataSets(h300a13_MedIsoMu2_TauDMMedIso_BTagUP, scale=.001)
#   h300a13_MedIsoMu2_TauDMMedIso_PileupDOWN = ScaleRooDataSets(h300a13_MedIsoMu2_TauDMMedIso_PileupDOWN, scale=.001)
#   h300a13_MedIsoMu2_TauDMMedIso_PileupUP = ScaleRooDataSets(h300a13_MedIsoMu2_TauDMMedIso_PileupUP, scale=.001)
#   h300a15_MedIsoMu2_TauDMMedIso_Central = ScaleRooDataSets(h300a15_MedIsoMu2_TauDMMedIso_Central, scale=.001)
#   h300a15_MedIsoMu2_TauDMMedIso_IDDOWN = ScaleRooDataSets(h300a15_MedIsoMu2_TauDMMedIso_IDDOWN, scale=.001)
#   h300a15_MedIsoMu2_TauDMMedIso_IDUP = ScaleRooDataSets(h300a15_MedIsoMu2_TauDMMedIso_IDUP, scale=.001)
#   h300a15_MedIsoMu2_TauDMMedIso_IsoDOWN = ScaleRooDataSets(h300a15_MedIsoMu2_TauDMMedIso_IsoDOWN, scale=.001)
#   h300a15_MedIsoMu2_TauDMMedIso_IsoUP = ScaleRooDataSets(h300a15_MedIsoMu2_TauDMMedIso_IsoUP, scale=.001)
#   h300a15_MedIsoMu2_TauDMMedIso_BTagDOWN = ScaleRooDataSets(h300a15_MedIsoMu2_TauDMMedIso_BTagDOWN, scale=.001)
#   h300a15_MedIsoMu2_TauDMMedIso_BTagUP = ScaleRooDataSets(h300a15_MedIsoMu2_TauDMMedIso_BTagUP, scale=.001)
#   h300a15_MedIsoMu2_TauDMMedIso_PileupDOWN = ScaleRooDataSets(h300a15_MedIsoMu2_TauDMMedIso_PileupDOWN, scale=.001)
#   h300a15_MedIsoMu2_TauDMMedIso_PileupUP = ScaleRooDataSets(h300a15_MedIsoMu2_TauDMMedIso_PileupUP, scale=.001)
#   h300a17_MedIsoMu2_TauDMMedIso_Central = ScaleRooDataSets(h300a17_MedIsoMu2_TauDMMedIso_Central, scale=.001)
#   h300a17_MedIsoMu2_TauDMMedIso_IDDOWN = ScaleRooDataSets(h300a17_MedIsoMu2_TauDMMedIso_IDDOWN, scale=.001)
#   h300a17_MedIsoMu2_TauDMMedIso_IDUP = ScaleRooDataSets(h300a17_MedIsoMu2_TauDMMedIso_IDUP, scale=.001)
#   h300a17_MedIsoMu2_TauDMMedIso_IsoDOWN = ScaleRooDataSets(h300a17_MedIsoMu2_TauDMMedIso_IsoDOWN, scale=.001)
#   h300a17_MedIsoMu2_TauDMMedIso_IsoUP = ScaleRooDataSets(h300a17_MedIsoMu2_TauDMMedIso_IsoUP, scale=.001)
#   h300a17_MedIsoMu2_TauDMMedIso_BTagDOWN = ScaleRooDataSets(h300a17_MedIsoMu2_TauDMMedIso_BTagDOWN, scale=.001)
#   h300a17_MedIsoMu2_TauDMMedIso_BTagUP = ScaleRooDataSets(h300a17_MedIsoMu2_TauDMMedIso_BTagUP, scale=.001)
#   h300a17_MedIsoMu2_TauDMMedIso_PileupDOWN = ScaleRooDataSets(h300a17_MedIsoMu2_TauDMMedIso_PileupDOWN, scale=.001)
#   h300a17_MedIsoMu2_TauDMMedIso_PileupUP = ScaleRooDataSets(h300a17_MedIsoMu2_TauDMMedIso_PileupUP, scale=.001)
#   h300a19_MedIsoMu2_TauDMMedIso_Central = ScaleRooDataSets(h300a19_MedIsoMu2_TauDMMedIso_Central, scale=.001)
#   h300a19_MedIsoMu2_TauDMMedIso_IDDOWN = ScaleRooDataSets(h300a19_MedIsoMu2_TauDMMedIso_IDDOWN, scale=.001)
#   h300a19_MedIsoMu2_TauDMMedIso_IDUP = ScaleRooDataSets(h300a19_MedIsoMu2_TauDMMedIso_IDUP, scale=.001)
#   h300a19_MedIsoMu2_TauDMMedIso_IsoDOWN = ScaleRooDataSets(h300a19_MedIsoMu2_TauDMMedIso_IsoDOWN, scale=.001)
#   h300a19_MedIsoMu2_TauDMMedIso_IsoUP = ScaleRooDataSets(h300a19_MedIsoMu2_TauDMMedIso_IsoUP, scale=.001)
#   h300a19_MedIsoMu2_TauDMMedIso_BTagDOWN = ScaleRooDataSets(h300a19_MedIsoMu2_TauDMMedIso_BTagDOWN, scale=.001)
#   h300a19_MedIsoMu2_TauDMMedIso_BTagUP = ScaleRooDataSets(h300a19_MedIsoMu2_TauDMMedIso_BTagUP, scale=.001)
#   h300a19_MedIsoMu2_TauDMMedIso_PileupDOWN = ScaleRooDataSets(h300a19_MedIsoMu2_TauDMMedIso_PileupDOWN, scale=.001)
#   h300a19_MedIsoMu2_TauDMMedIso_PileupUP = ScaleRooDataSets(h300a19_MedIsoMu2_TauDMMedIso_PileupUP, scale=.001)
#   h300a21_MedIsoMu2_TauDMMedIso_Central = ScaleRooDataSets(h300a21_MedIsoMu2_TauDMMedIso_Central, scale=.001)
#   h300a21_MedIsoMu2_TauDMMedIso_IDDOWN = ScaleRooDataSets(h300a21_MedIsoMu2_TauDMMedIso_IDDOWN, scale=.001)
#   h300a21_MedIsoMu2_TauDMMedIso_IDUP = ScaleRooDataSets(h300a21_MedIsoMu2_TauDMMedIso_IDUP, scale=.001)
#   h300a21_MedIsoMu2_TauDMMedIso_IsoDOWN = ScaleRooDataSets(h300a21_MedIsoMu2_TauDMMedIso_IsoDOWN, scale=.001)
#   h300a21_MedIsoMu2_TauDMMedIso_IsoUP = ScaleRooDataSets(h300a21_MedIsoMu2_TauDMMedIso_IsoUP, scale=.001)
#   h300a21_MedIsoMu2_TauDMMedIso_BTagDOWN = ScaleRooDataSets(h300a21_MedIsoMu2_TauDMMedIso_BTagDOWN, scale=.001)
#   h300a21_MedIsoMu2_TauDMMedIso_BTagUP = ScaleRooDataSets(h300a21_MedIsoMu2_TauDMMedIso_BTagUP, scale=.001)
#   h300a21_MedIsoMu2_TauDMMedIso_PileupDOWN = ScaleRooDataSets(h300a21_MedIsoMu2_TauDMMedIso_PileupDOWN, scale=.001)
#   h300a21_MedIsoMu2_TauDMMedIso_PileupUP = ScaleRooDataSets(h300a21_MedIsoMu2_TauDMMedIso_PileupUP, scale=.001)
#   h300a5_MedIsoMu2_TauDMMedIso_Central = ScaleRooDataSets(h300a5_MedIsoMu2_TauDMMedIso_Central, scale=.001)
#   h300a5_MedIsoMu2_TauDMMedIso_IDDOWN = ScaleRooDataSets(h300a5_MedIsoMu2_TauDMMedIso_IDDOWN, scale=.001)
#   h300a5_MedIsoMu2_TauDMMedIso_IDUP = ScaleRooDataSets(h300a5_MedIsoMu2_TauDMMedIso_IDUP, scale=.001)
#   h300a5_MedIsoMu2_TauDMMedIso_IsoDOWN = ScaleRooDataSets(h300a5_MedIsoMu2_TauDMMedIso_IsoDOWN, scale=.001)
#   h300a5_MedIsoMu2_TauDMMedIso_IsoUP = ScaleRooDataSets(h300a5_MedIsoMu2_TauDMMedIso_IsoUP, scale=.001)
#   h300a5_MedIsoMu2_TauDMMedIso_BTagDOWN = ScaleRooDataSets(h300a5_MedIsoMu2_TauDMMedIso_BTagDOWN, scale=.001)
#   h300a5_MedIsoMu2_TauDMMedIso_BTagUP = ScaleRooDataSets(h300a5_MedIsoMu2_TauDMMedIso_BTagUP, scale=.001)
#   h300a5_MedIsoMu2_TauDMMedIso_PileupDOWN = ScaleRooDataSets(h300a5_MedIsoMu2_TauDMMedIso_PileupDOWN, scale=.001)
#   h300a5_MedIsoMu2_TauDMMedIso_PileupUP = ScaleRooDataSets(h300a5_MedIsoMu2_TauDMMedIso_PileupUP, scale=.001)
#   h300a7_MedIsoMu2_TauDMMedIso_Central = ScaleRooDataSets(h300a7_MedIsoMu2_TauDMMedIso_Central, scale=.001)
#   h300a7_MedIsoMu2_TauDMMedIso_IDDOWN = ScaleRooDataSets(h300a7_MedIsoMu2_TauDMMedIso_IDDOWN, scale=.001)
#   h300a7_MedIsoMu2_TauDMMedIso_IDUP = ScaleRooDataSets(h300a7_MedIsoMu2_TauDMMedIso_IDUP, scale=.001)
#   h300a7_MedIsoMu2_TauDMMedIso_IsoDOWN = ScaleRooDataSets(h300a7_MedIsoMu2_TauDMMedIso_IsoDOWN, scale=.001)
#   h300a7_MedIsoMu2_TauDMMedIso_IsoUP = ScaleRooDataSets(h300a7_MedIsoMu2_TauDMMedIso_IsoUP, scale=.001)
#   h300a7_MedIsoMu2_TauDMMedIso_BTagDOWN = ScaleRooDataSets(h300a7_MedIsoMu2_TauDMMedIso_BTagDOWN, scale=.001)
#   h300a7_MedIsoMu2_TauDMMedIso_BTagUP = ScaleRooDataSets(h300a7_MedIsoMu2_TauDMMedIso_BTagUP, scale=.001)
#   h300a7_MedIsoMu2_TauDMMedIso_PileupDOWN = ScaleRooDataSets(h300a7_MedIsoMu2_TauDMMedIso_PileupDOWN, scale=.001)
#   h300a7_MedIsoMu2_TauDMMedIso_PileupUP = ScaleRooDataSets(h300a7_MedIsoMu2_TauDMMedIso_PileupUP, scale=.001)
#   h300a9_MedIsoMu2_TauDMMedIso_Central = ScaleRooDataSets(h300a9_MedIsoMu2_TauDMMedIso_Central, scale=.001)
#   h300a9_MedIsoMu2_TauDMMedIso_IDDOWN = ScaleRooDataSets(h300a9_MedIsoMu2_TauDMMedIso_IDDOWN, scale=.001)
#   h300a9_MedIsoMu2_TauDMMedIso_IDUP = ScaleRooDataSets(h300a9_MedIsoMu2_TauDMMedIso_IDUP, scale=.001)
#   h300a9_MedIsoMu2_TauDMMedIso_IsoDOWN = ScaleRooDataSets(h300a9_MedIsoMu2_TauDMMedIso_IsoDOWN, scale=.001)
#   h300a9_MedIsoMu2_TauDMMedIso_IsoUP = ScaleRooDataSets(h300a9_MedIsoMu2_TauDMMedIso_IsoUP, scale=.001)
#   h300a9_MedIsoMu2_TauDMMedIso_BTagDOWN = ScaleRooDataSets(h300a9_MedIsoMu2_TauDMMedIso_BTagDOWN, scale=.001)
#   h300a9_MedIsoMu2_TauDMMedIso_BTagUP = ScaleRooDataSets(h300a9_MedIsoMu2_TauDMMedIso_BTagUP, scale=.001)
#   h300a9_MedIsoMu2_TauDMMedIso_PileupDOWN = ScaleRooDataSets(h300a9_MedIsoMu2_TauDMMedIso_PileupDOWN, scale=.001)
#   h300a9_MedIsoMu2_TauDMMedIso_PileupUP = ScaleRooDataSets(h300a9_MedIsoMu2_TauDMMedIso_PileupUP, scale=.001)
#   h750a11_MedIsoMu2_TauDMMedIso_Central = ScaleRooDataSets(h750a11_MedIsoMu2_TauDMMedIso_Central, scale=.001)
#   h750a11_MedIsoMu2_TauDMMedIso_IDDOWN = ScaleRooDataSets(h750a11_MedIsoMu2_TauDMMedIso_IDDOWN, scale=.001)
#   h750a11_MedIsoMu2_TauDMMedIso_IDUP = ScaleRooDataSets(h750a11_MedIsoMu2_TauDMMedIso_IDUP, scale=.001)
#   h750a11_MedIsoMu2_TauDMMedIso_IsoDOWN = ScaleRooDataSets(h750a11_MedIsoMu2_TauDMMedIso_IsoDOWN, scale=.001)
#   h750a11_MedIsoMu2_TauDMMedIso_IsoUP = ScaleRooDataSets(h750a11_MedIsoMu2_TauDMMedIso_IsoUP, scale=.001)
#   h750a11_MedIsoMu2_TauDMMedIso_BTagDOWN = ScaleRooDataSets(h750a11_MedIsoMu2_TauDMMedIso_BTagDOWN, scale=.001)
#   h750a11_MedIsoMu2_TauDMMedIso_BTagUP = ScaleRooDataSets(h750a11_MedIsoMu2_TauDMMedIso_BTagUP, scale=.001)
#   h750a11_MedIsoMu2_TauDMMedIso_PileupDOWN = ScaleRooDataSets(h750a11_MedIsoMu2_TauDMMedIso_PileupDOWN, scale=.001)
#   h750a11_MedIsoMu2_TauDMMedIso_PileupUP = ScaleRooDataSets(h750a11_MedIsoMu2_TauDMMedIso_PileupUP, scale=.001)
#   h750a13_MedIsoMu2_TauDMMedIso_Central = ScaleRooDataSets(h750a13_MedIsoMu2_TauDMMedIso_Central, scale=.001)
#   h750a13_MedIsoMu2_TauDMMedIso_IDDOWN = ScaleRooDataSets(h750a13_MedIsoMu2_TauDMMedIso_IDDOWN, scale=.001)
#   h750a13_MedIsoMu2_TauDMMedIso_IDUP = ScaleRooDataSets(h750a13_MedIsoMu2_TauDMMedIso_IDUP, scale=.001)
#   h750a13_MedIsoMu2_TauDMMedIso_IsoDOWN = ScaleRooDataSets(h750a13_MedIsoMu2_TauDMMedIso_IsoDOWN, scale=.001)
#   h750a13_MedIsoMu2_TauDMMedIso_IsoUP = ScaleRooDataSets(h750a13_MedIsoMu2_TauDMMedIso_IsoUP, scale=.001)
#   h750a13_MedIsoMu2_TauDMMedIso_BTagDOWN = ScaleRooDataSets(h750a13_MedIsoMu2_TauDMMedIso_BTagDOWN, scale=.001)
#   h750a13_MedIsoMu2_TauDMMedIso_BTagUP = ScaleRooDataSets(h750a13_MedIsoMu2_TauDMMedIso_BTagUP, scale=.001)
#   h750a13_MedIsoMu2_TauDMMedIso_PileupDOWN = ScaleRooDataSets(h750a13_MedIsoMu2_TauDMMedIso_PileupDOWN, scale=.001)
#   h750a13_MedIsoMu2_TauDMMedIso_PileupUP = ScaleRooDataSets(h750a13_MedIsoMu2_TauDMMedIso_PileupUP, scale=.001)
#   h750a15_MedIsoMu2_TauDMMedIso_Central = ScaleRooDataSets(h750a15_MedIsoMu2_TauDMMedIso_Central, scale=.001)
#   h750a15_MedIsoMu2_TauDMMedIso_IDDOWN = ScaleRooDataSets(h750a15_MedIsoMu2_TauDMMedIso_IDDOWN, scale=.001)
#   h750a15_MedIsoMu2_TauDMMedIso_IDUP = ScaleRooDataSets(h750a15_MedIsoMu2_TauDMMedIso_IDUP, scale=.001)
#   h750a15_MedIsoMu2_TauDMMedIso_IsoDOWN = ScaleRooDataSets(h750a15_MedIsoMu2_TauDMMedIso_IsoDOWN, scale=.001)
#   h750a15_MedIsoMu2_TauDMMedIso_IsoUP = ScaleRooDataSets(h750a15_MedIsoMu2_TauDMMedIso_IsoUP, scale=.001)
#   h750a15_MedIsoMu2_TauDMMedIso_BTagDOWN = ScaleRooDataSets(h750a15_MedIsoMu2_TauDMMedIso_BTagDOWN, scale=.001)
#   h750a15_MedIsoMu2_TauDMMedIso_BTagUP = ScaleRooDataSets(h750a15_MedIsoMu2_TauDMMedIso_BTagUP, scale=.001)
#   h750a15_MedIsoMu2_TauDMMedIso_PileupDOWN = ScaleRooDataSets(h750a15_MedIsoMu2_TauDMMedIso_PileupDOWN, scale=.001)
#   h750a15_MedIsoMu2_TauDMMedIso_PileupUP = ScaleRooDataSets(h750a15_MedIsoMu2_TauDMMedIso_PileupUP, scale=.001)
#   h750a17_MedIsoMu2_TauDMMedIso_Central = ScaleRooDataSets(h750a17_MedIsoMu2_TauDMMedIso_Central, scale=.001)
#   h750a17_MedIsoMu2_TauDMMedIso_IDDOWN = ScaleRooDataSets(h750a17_MedIsoMu2_TauDMMedIso_IDDOWN, scale=.001)
#   h750a17_MedIsoMu2_TauDMMedIso_IDUP = ScaleRooDataSets(h750a17_MedIsoMu2_TauDMMedIso_IDUP, scale=.001)
#   h750a17_MedIsoMu2_TauDMMedIso_IsoDOWN = ScaleRooDataSets(h750a17_MedIsoMu2_TauDMMedIso_IsoDOWN, scale=.001)
#   h750a17_MedIsoMu2_TauDMMedIso_IsoUP = ScaleRooDataSets(h750a17_MedIsoMu2_TauDMMedIso_IsoUP, scale=.001)
#   h750a17_MedIsoMu2_TauDMMedIso_BTagDOWN = ScaleRooDataSets(h750a17_MedIsoMu2_TauDMMedIso_BTagDOWN, scale=.001)
#   h750a17_MedIsoMu2_TauDMMedIso_BTagUP = ScaleRooDataSets(h750a17_MedIsoMu2_TauDMMedIso_BTagUP, scale=.001)
#   h750a17_MedIsoMu2_TauDMMedIso_PileupDOWN = ScaleRooDataSets(h750a17_MedIsoMu2_TauDMMedIso_PileupDOWN, scale=.001)
#   h750a17_MedIsoMu2_TauDMMedIso_PileupUP = ScaleRooDataSets(h750a17_MedIsoMu2_TauDMMedIso_PileupUP, scale=.001)
#   h750a19_MedIsoMu2_TauDMMedIso_Central = ScaleRooDataSets(h750a19_MedIsoMu2_TauDMMedIso_Central, scale=.001)
#   h750a19_MedIsoMu2_TauDMMedIso_IDDOWN = ScaleRooDataSets(h750a19_MedIsoMu2_TauDMMedIso_IDDOWN, scale=.001)
#   h750a19_MedIsoMu2_TauDMMedIso_IDUP = ScaleRooDataSets(h750a19_MedIsoMu2_TauDMMedIso_IDUP, scale=.001)
#   h750a19_MedIsoMu2_TauDMMedIso_IsoDOWN = ScaleRooDataSets(h750a19_MedIsoMu2_TauDMMedIso_IsoDOWN, scale=.001)
#   h750a19_MedIsoMu2_TauDMMedIso_IsoUP = ScaleRooDataSets(h750a19_MedIsoMu2_TauDMMedIso_IsoUP, scale=.001)
#   h750a19_MedIsoMu2_TauDMMedIso_BTagDOWN = ScaleRooDataSets(h750a19_MedIsoMu2_TauDMMedIso_BTagDOWN, scale=.001)
#   h750a19_MedIsoMu2_TauDMMedIso_BTagUP = ScaleRooDataSets(h750a19_MedIsoMu2_TauDMMedIso_BTagUP, scale=.001)
#   h750a19_MedIsoMu2_TauDMMedIso_PileupDOWN = ScaleRooDataSets(h750a19_MedIsoMu2_TauDMMedIso_PileupDOWN, scale=.001)
#   h750a19_MedIsoMu2_TauDMMedIso_PileupUP = ScaleRooDataSets(h750a19_MedIsoMu2_TauDMMedIso_PileupUP, scale=.001)
#   h750a21_MedIsoMu2_TauDMMedIso_Central = ScaleRooDataSets(h750a21_MedIsoMu2_TauDMMedIso_Central, scale=.001)
#   h750a21_MedIsoMu2_TauDMMedIso_IDDOWN = ScaleRooDataSets(h750a21_MedIsoMu2_TauDMMedIso_IDDOWN, scale=.001)
#   h750a21_MedIsoMu2_TauDMMedIso_IDUP = ScaleRooDataSets(h750a21_MedIsoMu2_TauDMMedIso_IDUP, scale=.001)
#   h750a21_MedIsoMu2_TauDMMedIso_IsoDOWN = ScaleRooDataSets(h750a21_MedIsoMu2_TauDMMedIso_IsoDOWN, scale=.001)
#   h750a21_MedIsoMu2_TauDMMedIso_IsoUP = ScaleRooDataSets(h750a21_MedIsoMu2_TauDMMedIso_IsoUP, scale=.001)
#   h750a21_MedIsoMu2_TauDMMedIso_BTagDOWN = ScaleRooDataSets(h750a21_MedIsoMu2_TauDMMedIso_BTagDOWN, scale=.001)
#   h750a21_MedIsoMu2_TauDMMedIso_BTagUP = ScaleRooDataSets(h750a21_MedIsoMu2_TauDMMedIso_BTagUP, scale=.001)
#   h750a21_MedIsoMu2_TauDMMedIso_PileupDOWN = ScaleRooDataSets(h750a21_MedIsoMu2_TauDMMedIso_PileupDOWN, scale=.001)
#   h750a21_MedIsoMu2_TauDMMedIso_PileupUP = ScaleRooDataSets(h750a21_MedIsoMu2_TauDMMedIso_PileupUP, scale=.001)
#   h750a5_MedIsoMu2_TauDMMedIso_Central = ScaleRooDataSets(h750a5_MedIsoMu2_TauDMMedIso_Central, scale=.001)
#   h750a5_MedIsoMu2_TauDMMedIso_IDDOWN = ScaleRooDataSets(h750a5_MedIsoMu2_TauDMMedIso_IDDOWN, scale=.001)
#   h750a5_MedIsoMu2_TauDMMedIso_IDUP = ScaleRooDataSets(h750a5_MedIsoMu2_TauDMMedIso_IDUP, scale=.001)
#   h750a5_MedIsoMu2_TauDMMedIso_IsoDOWN = ScaleRooDataSets(h750a5_MedIsoMu2_TauDMMedIso_IsoDOWN, scale=.001)
#   h750a5_MedIsoMu2_TauDMMedIso_IsoUP = ScaleRooDataSets(h750a5_MedIsoMu2_TauDMMedIso_IsoUP, scale=.001)
#   h750a5_MedIsoMu2_TauDMMedIso_BTagDOWN = ScaleRooDataSets(h750a5_MedIsoMu2_TauDMMedIso_BTagDOWN, scale=.001)
#   h750a5_MedIsoMu2_TauDMMedIso_BTagUP = ScaleRooDataSets(h750a5_MedIsoMu2_TauDMMedIso_BTagUP, scale=.001)
#   h750a5_MedIsoMu2_TauDMMedIso_PileupDOWN = ScaleRooDataSets(h750a5_MedIsoMu2_TauDMMedIso_PileupDOWN, scale=.001)
#   h750a5_MedIsoMu2_TauDMMedIso_PileupUP = ScaleRooDataSets(h750a5_MedIsoMu2_TauDMMedIso_PileupUP, scale=.001)
#   h750a7_MedIsoMu2_TauDMMedIso_Central = ScaleRooDataSets(h750a7_MedIsoMu2_TauDMMedIso_Central, scale=.001)
#   h750a7_MedIsoMu2_TauDMMedIso_IDDOWN = ScaleRooDataSets(h750a7_MedIsoMu2_TauDMMedIso_IDDOWN, scale=.001)
#   h750a7_MedIsoMu2_TauDMMedIso_IDUP = ScaleRooDataSets(h750a7_MedIsoMu2_TauDMMedIso_IDUP, scale=.001)
#   h750a7_MedIsoMu2_TauDMMedIso_IsoDOWN = ScaleRooDataSets(h750a7_MedIsoMu2_TauDMMedIso_IsoDOWN, scale=.001)
#   h750a7_MedIsoMu2_TauDMMedIso_IsoUP = ScaleRooDataSets(h750a7_MedIsoMu2_TauDMMedIso_IsoUP, scale=.001)
#   h750a7_MedIsoMu2_TauDMMedIso_BTagDOWN = ScaleRooDataSets(h750a7_MedIsoMu2_TauDMMedIso_BTagDOWN, scale=.001)
#   h750a7_MedIsoMu2_TauDMMedIso_BTagUP = ScaleRooDataSets(h750a7_MedIsoMu2_TauDMMedIso_BTagUP, scale=.001)
#   h750a7_MedIsoMu2_TauDMMedIso_PileupDOWN = ScaleRooDataSets(h750a7_MedIsoMu2_TauDMMedIso_PileupDOWN, scale=.001)
#   h750a7_MedIsoMu2_TauDMMedIso_PileupUP = ScaleRooDataSets(h750a7_MedIsoMu2_TauDMMedIso_PileupUP, scale=.001)
#   h750a9_MedIsoMu2_TauDMMedIso_Central = ScaleRooDataSets(h750a9_MedIsoMu2_TauDMMedIso_Central, scale=.001)
#   h750a9_MedIsoMu2_TauDMMedIso_IDDOWN = ScaleRooDataSets(h750a9_MedIsoMu2_TauDMMedIso_IDDOWN, scale=.001)
#   h750a9_MedIsoMu2_TauDMMedIso_IDUP = ScaleRooDataSets(h750a9_MedIsoMu2_TauDMMedIso_IDUP, scale=.001)
#   h750a9_MedIsoMu2_TauDMMedIso_IsoDOWN = ScaleRooDataSets(h750a9_MedIsoMu2_TauDMMedIso_IsoDOWN, scale=.001)
#   h750a9_MedIsoMu2_TauDMMedIso_IsoUP = ScaleRooDataSets(h750a9_MedIsoMu2_TauDMMedIso_IsoUP, scale=.001)
#   h750a9_MedIsoMu2_TauDMMedIso_BTagDOWN = ScaleRooDataSets(h750a9_MedIsoMu2_TauDMMedIso_BTagDOWN, scale=.001)
#   h750a9_MedIsoMu2_TauDMMedIso_BTagUP = ScaleRooDataSets(h750a9_MedIsoMu2_TauDMMedIso_BTagUP, scale=.001)
#   h750a9_MedIsoMu2_TauDMMedIso_PileupDOWN = ScaleRooDataSets(h750a9_MedIsoMu2_TauDMMedIso_PileupDOWN, scale=.001)
#   h750a9_MedIsoMu2_TauDMMedIso_PileupUP = ScaleRooDataSets(h750a9_MedIsoMu2_TauDMMedIso_PileupUP, scale=.001)
 
   h125a11_MedIsoMu2_TauDMMedIso_Central = getDataset(h125a11_MedIsoMu2_TauDMMedIso_Central, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a11_MedIsoMu2_TauDMMedIso_IDDOWN = getDataset(h125a11_MedIsoMu2_TauDMMedIso_IDDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a11_MedIsoMu2_TauDMMedIso_IDUP = getDataset(h125a11_MedIsoMu2_TauDMMedIso_IDUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a11_MedIsoMu2_TauDMMedIso_IsoDOWN = getDataset(h125a11_MedIsoMu2_TauDMMedIso_IsoDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a11_MedIsoMu2_TauDMMedIso_IsoUP = getDataset(h125a11_MedIsoMu2_TauDMMedIso_IsoUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a11_MedIsoMu2_TauDMMedIso_BTagDOWN = getDataset(h125a11_MedIsoMu2_TauDMMedIso_BTagDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a11_MedIsoMu2_TauDMMedIso_BTagUP = getDataset(h125a11_MedIsoMu2_TauDMMedIso_BTagUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a11_MedIsoMu2_TauDMMedIso_PileupDOWN = getDataset(h125a11_MedIsoMu2_TauDMMedIso_PileupDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a11_MedIsoMu2_TauDMMedIso_PileupUP = getDataset(h125a11_MedIsoMu2_TauDMMedIso_PileupUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a13_MedIsoMu2_TauDMMedIso_Central = getDataset(h125a13_MedIsoMu2_TauDMMedIso_Central, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a13_MedIsoMu2_TauDMMedIso_IDDOWN = getDataset(h125a13_MedIsoMu2_TauDMMedIso_IDDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a13_MedIsoMu2_TauDMMedIso_IDUP = getDataset(h125a13_MedIsoMu2_TauDMMedIso_IDUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a13_MedIsoMu2_TauDMMedIso_IsoDOWN = getDataset(h125a13_MedIsoMu2_TauDMMedIso_IsoDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a13_MedIsoMu2_TauDMMedIso_IsoUP = getDataset(h125a13_MedIsoMu2_TauDMMedIso_IsoUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a13_MedIsoMu2_TauDMMedIso_BTagDOWN = getDataset(h125a13_MedIsoMu2_TauDMMedIso_BTagDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a13_MedIsoMu2_TauDMMedIso_BTagUP = getDataset(h125a13_MedIsoMu2_TauDMMedIso_BTagUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a13_MedIsoMu2_TauDMMedIso_PileupDOWN = getDataset(h125a13_MedIsoMu2_TauDMMedIso_PileupDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a13_MedIsoMu2_TauDMMedIso_PileupUP = getDataset(h125a13_MedIsoMu2_TauDMMedIso_PileupUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a15_MedIsoMu2_TauDMMedIso_Central = getDataset(h125a15_MedIsoMu2_TauDMMedIso_Central, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a15_MedIsoMu2_TauDMMedIso_IDDOWN = getDataset(h125a15_MedIsoMu2_TauDMMedIso_IDDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a15_MedIsoMu2_TauDMMedIso_IDUP = getDataset(h125a15_MedIsoMu2_TauDMMedIso_IDUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a15_MedIsoMu2_TauDMMedIso_IsoDOWN = getDataset(h125a15_MedIsoMu2_TauDMMedIso_IsoDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a15_MedIsoMu2_TauDMMedIso_IsoUP = getDataset(h125a15_MedIsoMu2_TauDMMedIso_IsoUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a15_MedIsoMu2_TauDMMedIso_BTagDOWN = getDataset(h125a15_MedIsoMu2_TauDMMedIso_BTagDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a15_MedIsoMu2_TauDMMedIso_BTagUP = getDataset(h125a15_MedIsoMu2_TauDMMedIso_BTagUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a15_MedIsoMu2_TauDMMedIso_PileupDOWN = getDataset(h125a15_MedIsoMu2_TauDMMedIso_PileupDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a15_MedIsoMu2_TauDMMedIso_PileupUP = getDataset(h125a15_MedIsoMu2_TauDMMedIso_PileupUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a17_MedIsoMu2_TauDMMedIso_Central = getDataset(h125a17_MedIsoMu2_TauDMMedIso_Central, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a17_MedIsoMu2_TauDMMedIso_IDDOWN = getDataset(h125a17_MedIsoMu2_TauDMMedIso_IDDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a17_MedIsoMu2_TauDMMedIso_IDUP = getDataset(h125a17_MedIsoMu2_TauDMMedIso_IDUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a17_MedIsoMu2_TauDMMedIso_IsoDOWN = getDataset(h125a17_MedIsoMu2_TauDMMedIso_IsoDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a17_MedIsoMu2_TauDMMedIso_IsoUP = getDataset(h125a17_MedIsoMu2_TauDMMedIso_IsoUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a17_MedIsoMu2_TauDMMedIso_BTagDOWN = getDataset(h125a17_MedIsoMu2_TauDMMedIso_BTagDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a17_MedIsoMu2_TauDMMedIso_BTagUP = getDataset(h125a17_MedIsoMu2_TauDMMedIso_BTagUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a17_MedIsoMu2_TauDMMedIso_PileupDOWN = getDataset(h125a17_MedIsoMu2_TauDMMedIso_PileupDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a17_MedIsoMu2_TauDMMedIso_PileupUP = getDataset(h125a17_MedIsoMu2_TauDMMedIso_PileupUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a19_MedIsoMu2_TauDMMedIso_Central = getDataset(h125a19_MedIsoMu2_TauDMMedIso_Central, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a19_MedIsoMu2_TauDMMedIso_IDDOWN = getDataset(h125a19_MedIsoMu2_TauDMMedIso_IDDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a19_MedIsoMu2_TauDMMedIso_IDUP = getDataset(h125a19_MedIsoMu2_TauDMMedIso_IDUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a19_MedIsoMu2_TauDMMedIso_IsoDOWN = getDataset(h125a19_MedIsoMu2_TauDMMedIso_IsoDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a19_MedIsoMu2_TauDMMedIso_IsoUP = getDataset(h125a19_MedIsoMu2_TauDMMedIso_IsoUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a19_MedIsoMu2_TauDMMedIso_BTagDOWN = getDataset(h125a19_MedIsoMu2_TauDMMedIso_BTagDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a19_MedIsoMu2_TauDMMedIso_BTagUP = getDataset(h125a19_MedIsoMu2_TauDMMedIso_BTagUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a19_MedIsoMu2_TauDMMedIso_PileupDOWN = getDataset(h125a19_MedIsoMu2_TauDMMedIso_PileupDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a19_MedIsoMu2_TauDMMedIso_PileupUP = getDataset(h125a19_MedIsoMu2_TauDMMedIso_PileupUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a21_MedIsoMu2_TauDMMedIso_Central = getDataset(h125a21_MedIsoMu2_TauDMMedIso_Central, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a21_MedIsoMu2_TauDMMedIso_IDDOWN = getDataset(h125a21_MedIsoMu2_TauDMMedIso_IDDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a21_MedIsoMu2_TauDMMedIso_IDUP = getDataset(h125a21_MedIsoMu2_TauDMMedIso_IDUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a21_MedIsoMu2_TauDMMedIso_IsoDOWN = getDataset(h125a21_MedIsoMu2_TauDMMedIso_IsoDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a21_MedIsoMu2_TauDMMedIso_IsoUP = getDataset(h125a21_MedIsoMu2_TauDMMedIso_IsoUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a21_MedIsoMu2_TauDMMedIso_BTagDOWN = getDataset(h125a21_MedIsoMu2_TauDMMedIso_BTagDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a21_MedIsoMu2_TauDMMedIso_BTagUP = getDataset(h125a21_MedIsoMu2_TauDMMedIso_BTagUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a21_MedIsoMu2_TauDMMedIso_PileupDOWN = getDataset(h125a21_MedIsoMu2_TauDMMedIso_PileupDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a21_MedIsoMu2_TauDMMedIso_PileupUP = getDataset(h125a21_MedIsoMu2_TauDMMedIso_PileupUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a5_MedIsoMu2_TauDMMedIso_Central = getDataset(h125a5_MedIsoMu2_TauDMMedIso_Central, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a5_MedIsoMu2_TauDMMedIso_IDDOWN = getDataset(h125a5_MedIsoMu2_TauDMMedIso_IDDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a5_MedIsoMu2_TauDMMedIso_IDUP = getDataset(h125a5_MedIsoMu2_TauDMMedIso_IDUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a5_MedIsoMu2_TauDMMedIso_IsoDOWN = getDataset(h125a5_MedIsoMu2_TauDMMedIso_IsoDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a5_MedIsoMu2_TauDMMedIso_IsoUP = getDataset(h125a5_MedIsoMu2_TauDMMedIso_IsoUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a5_MedIsoMu2_TauDMMedIso_BTagDOWN = getDataset(h125a5_MedIsoMu2_TauDMMedIso_BTagDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a5_MedIsoMu2_TauDMMedIso_BTagUP = getDataset(h125a5_MedIsoMu2_TauDMMedIso_BTagUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a5_MedIsoMu2_TauDMMedIso_PileupDOWN = getDataset(h125a5_MedIsoMu2_TauDMMedIso_PileupDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a5_MedIsoMu2_TauDMMedIso_PileupUP = getDataset(h125a5_MedIsoMu2_TauDMMedIso_PileupUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a7_MedIsoMu2_TauDMMedIso_Central = getDataset(h125a7_MedIsoMu2_TauDMMedIso_Central, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a7_MedIsoMu2_TauDMMedIso_IDDOWN = getDataset(h125a7_MedIsoMu2_TauDMMedIso_IDDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a7_MedIsoMu2_TauDMMedIso_IDUP = getDataset(h125a7_MedIsoMu2_TauDMMedIso_IDUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a7_MedIsoMu2_TauDMMedIso_IsoDOWN = getDataset(h125a7_MedIsoMu2_TauDMMedIso_IsoDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a7_MedIsoMu2_TauDMMedIso_IsoUP = getDataset(h125a7_MedIsoMu2_TauDMMedIso_IsoUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a7_MedIsoMu2_TauDMMedIso_BTagDOWN = getDataset(h125a7_MedIsoMu2_TauDMMedIso_BTagDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a7_MedIsoMu2_TauDMMedIso_BTagUP = getDataset(h125a7_MedIsoMu2_TauDMMedIso_BTagUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a7_MedIsoMu2_TauDMMedIso_PileupDOWN = getDataset(h125a7_MedIsoMu2_TauDMMedIso_PileupDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a7_MedIsoMu2_TauDMMedIso_PileupUP = getDataset(h125a7_MedIsoMu2_TauDMMedIso_PileupUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a9_MedIsoMu2_TauDMMedIso_Central = getDataset(h125a9_MedIsoMu2_TauDMMedIso_Central, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a9_MedIsoMu2_TauDMMedIso_IDDOWN = getDataset(h125a9_MedIsoMu2_TauDMMedIso_IDDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a9_MedIsoMu2_TauDMMedIso_IDUP = getDataset(h125a9_MedIsoMu2_TauDMMedIso_IDUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a9_MedIsoMu2_TauDMMedIso_IsoDOWN = getDataset(h125a9_MedIsoMu2_TauDMMedIso_IsoDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a9_MedIsoMu2_TauDMMedIso_IsoUP = getDataset(h125a9_MedIsoMu2_TauDMMedIso_IsoUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a9_MedIsoMu2_TauDMMedIso_BTagDOWN = getDataset(h125a9_MedIsoMu2_TauDMMedIso_BTagDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a9_MedIsoMu2_TauDMMedIso_BTagUP = getDataset(h125a9_MedIsoMu2_TauDMMedIso_BTagUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a9_MedIsoMu2_TauDMMedIso_PileupDOWN = getDataset(h125a9_MedIsoMu2_TauDMMedIso_PileupDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a9_MedIsoMu2_TauDMMedIso_PileupUP = getDataset(h125a9_MedIsoMu2_TauDMMedIso_PileupUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a11_MedIsoMu2_TauDMMedIso_Central = getDataset(h300a11_MedIsoMu2_TauDMMedIso_Central, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a11_MedIsoMu2_TauDMMedIso_IDDOWN = getDataset(h300a11_MedIsoMu2_TauDMMedIso_IDDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a11_MedIsoMu2_TauDMMedIso_IDUP = getDataset(h300a11_MedIsoMu2_TauDMMedIso_IDUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a11_MedIsoMu2_TauDMMedIso_IsoDOWN = getDataset(h300a11_MedIsoMu2_TauDMMedIso_IsoDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a11_MedIsoMu2_TauDMMedIso_IsoUP = getDataset(h300a11_MedIsoMu2_TauDMMedIso_IsoUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a11_MedIsoMu2_TauDMMedIso_BTagDOWN = getDataset(h300a11_MedIsoMu2_TauDMMedIso_BTagDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a11_MedIsoMu2_TauDMMedIso_BTagUP = getDataset(h300a11_MedIsoMu2_TauDMMedIso_BTagUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a11_MedIsoMu2_TauDMMedIso_PileupDOWN = getDataset(h300a11_MedIsoMu2_TauDMMedIso_PileupDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a11_MedIsoMu2_TauDMMedIso_PileupUP = getDataset(h300a11_MedIsoMu2_TauDMMedIso_PileupUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a13_MedIsoMu2_TauDMMedIso_Central = getDataset(h300a13_MedIsoMu2_TauDMMedIso_Central, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a13_MedIsoMu2_TauDMMedIso_IDDOWN = getDataset(h300a13_MedIsoMu2_TauDMMedIso_IDDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a13_MedIsoMu2_TauDMMedIso_IDUP = getDataset(h300a13_MedIsoMu2_TauDMMedIso_IDUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a13_MedIsoMu2_TauDMMedIso_IsoDOWN = getDataset(h300a13_MedIsoMu2_TauDMMedIso_IsoDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a13_MedIsoMu2_TauDMMedIso_IsoUP = getDataset(h300a13_MedIsoMu2_TauDMMedIso_IsoUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a13_MedIsoMu2_TauDMMedIso_BTagDOWN = getDataset(h300a13_MedIsoMu2_TauDMMedIso_BTagDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a13_MedIsoMu2_TauDMMedIso_BTagUP = getDataset(h300a13_MedIsoMu2_TauDMMedIso_BTagUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a13_MedIsoMu2_TauDMMedIso_PileupDOWN = getDataset(h300a13_MedIsoMu2_TauDMMedIso_PileupDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a13_MedIsoMu2_TauDMMedIso_PileupUP = getDataset(h300a13_MedIsoMu2_TauDMMedIso_PileupUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a15_MedIsoMu2_TauDMMedIso_Central = getDataset(h300a15_MedIsoMu2_TauDMMedIso_Central, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a15_MedIsoMu2_TauDMMedIso_IDDOWN = getDataset(h300a15_MedIsoMu2_TauDMMedIso_IDDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a15_MedIsoMu2_TauDMMedIso_IDUP = getDataset(h300a15_MedIsoMu2_TauDMMedIso_IDUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a15_MedIsoMu2_TauDMMedIso_IsoDOWN = getDataset(h300a15_MedIsoMu2_TauDMMedIso_IsoDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a15_MedIsoMu2_TauDMMedIso_IsoUP = getDataset(h300a15_MedIsoMu2_TauDMMedIso_IsoUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a15_MedIsoMu2_TauDMMedIso_BTagDOWN = getDataset(h300a15_MedIsoMu2_TauDMMedIso_BTagDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a15_MedIsoMu2_TauDMMedIso_BTagUP = getDataset(h300a15_MedIsoMu2_TauDMMedIso_BTagUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a15_MedIsoMu2_TauDMMedIso_PileupDOWN = getDataset(h300a15_MedIsoMu2_TauDMMedIso_PileupDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a15_MedIsoMu2_TauDMMedIso_PileupUP = getDataset(h300a15_MedIsoMu2_TauDMMedIso_PileupUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a17_MedIsoMu2_TauDMMedIso_Central = getDataset(h300a17_MedIsoMu2_TauDMMedIso_Central, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a17_MedIsoMu2_TauDMMedIso_IDDOWN = getDataset(h300a17_MedIsoMu2_TauDMMedIso_IDDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a17_MedIsoMu2_TauDMMedIso_IDUP = getDataset(h300a17_MedIsoMu2_TauDMMedIso_IDUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a17_MedIsoMu2_TauDMMedIso_IsoDOWN = getDataset(h300a17_MedIsoMu2_TauDMMedIso_IsoDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a17_MedIsoMu2_TauDMMedIso_IsoUP = getDataset(h300a17_MedIsoMu2_TauDMMedIso_IsoUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a17_MedIsoMu2_TauDMMedIso_BTagDOWN = getDataset(h300a17_MedIsoMu2_TauDMMedIso_BTagDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a17_MedIsoMu2_TauDMMedIso_BTagUP = getDataset(h300a17_MedIsoMu2_TauDMMedIso_BTagUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a17_MedIsoMu2_TauDMMedIso_PileupDOWN = getDataset(h300a17_MedIsoMu2_TauDMMedIso_PileupDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a17_MedIsoMu2_TauDMMedIso_PileupUP = getDataset(h300a17_MedIsoMu2_TauDMMedIso_PileupUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a19_MedIsoMu2_TauDMMedIso_Central = getDataset(h300a19_MedIsoMu2_TauDMMedIso_Central, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a19_MedIsoMu2_TauDMMedIso_IDDOWN = getDataset(h300a19_MedIsoMu2_TauDMMedIso_IDDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a19_MedIsoMu2_TauDMMedIso_IDUP = getDataset(h300a19_MedIsoMu2_TauDMMedIso_IDUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a19_MedIsoMu2_TauDMMedIso_IsoDOWN = getDataset(h300a19_MedIsoMu2_TauDMMedIso_IsoDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a19_MedIsoMu2_TauDMMedIso_IsoUP = getDataset(h300a19_MedIsoMu2_TauDMMedIso_IsoUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a19_MedIsoMu2_TauDMMedIso_BTagDOWN = getDataset(h300a19_MedIsoMu2_TauDMMedIso_BTagDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a19_MedIsoMu2_TauDMMedIso_BTagUP = getDataset(h300a19_MedIsoMu2_TauDMMedIso_BTagUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a19_MedIsoMu2_TauDMMedIso_PileupDOWN = getDataset(h300a19_MedIsoMu2_TauDMMedIso_PileupDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a19_MedIsoMu2_TauDMMedIso_PileupUP = getDataset(h300a19_MedIsoMu2_TauDMMedIso_PileupUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a21_MedIsoMu2_TauDMMedIso_Central = getDataset(h300a21_MedIsoMu2_TauDMMedIso_Central, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a21_MedIsoMu2_TauDMMedIso_IDDOWN = getDataset(h300a21_MedIsoMu2_TauDMMedIso_IDDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a21_MedIsoMu2_TauDMMedIso_IDUP = getDataset(h300a21_MedIsoMu2_TauDMMedIso_IDUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a21_MedIsoMu2_TauDMMedIso_IsoDOWN = getDataset(h300a21_MedIsoMu2_TauDMMedIso_IsoDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a21_MedIsoMu2_TauDMMedIso_IsoUP = getDataset(h300a21_MedIsoMu2_TauDMMedIso_IsoUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a21_MedIsoMu2_TauDMMedIso_BTagDOWN = getDataset(h300a21_MedIsoMu2_TauDMMedIso_BTagDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a21_MedIsoMu2_TauDMMedIso_BTagUP = getDataset(h300a21_MedIsoMu2_TauDMMedIso_BTagUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a21_MedIsoMu2_TauDMMedIso_PileupDOWN = getDataset(h300a21_MedIsoMu2_TauDMMedIso_PileupDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a21_MedIsoMu2_TauDMMedIso_PileupUP = getDataset(h300a21_MedIsoMu2_TauDMMedIso_PileupUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a5_MedIsoMu2_TauDMMedIso_Central = getDataset(h300a5_MedIsoMu2_TauDMMedIso_Central, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a5_MedIsoMu2_TauDMMedIso_IDDOWN = getDataset(h300a5_MedIsoMu2_TauDMMedIso_IDDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a5_MedIsoMu2_TauDMMedIso_IDUP = getDataset(h300a5_MedIsoMu2_TauDMMedIso_IDUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a5_MedIsoMu2_TauDMMedIso_IsoDOWN = getDataset(h300a5_MedIsoMu2_TauDMMedIso_IsoDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a5_MedIsoMu2_TauDMMedIso_IsoUP = getDataset(h300a5_MedIsoMu2_TauDMMedIso_IsoUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a5_MedIsoMu2_TauDMMedIso_BTagDOWN = getDataset(h300a5_MedIsoMu2_TauDMMedIso_BTagDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a5_MedIsoMu2_TauDMMedIso_BTagUP = getDataset(h300a5_MedIsoMu2_TauDMMedIso_BTagUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a5_MedIsoMu2_TauDMMedIso_PileupDOWN = getDataset(h300a5_MedIsoMu2_TauDMMedIso_PileupDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a5_MedIsoMu2_TauDMMedIso_PileupUP = getDataset(h300a5_MedIsoMu2_TauDMMedIso_PileupUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a7_MedIsoMu2_TauDMMedIso_Central = getDataset(h300a7_MedIsoMu2_TauDMMedIso_Central, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a7_MedIsoMu2_TauDMMedIso_IDDOWN = getDataset(h300a7_MedIsoMu2_TauDMMedIso_IDDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a7_MedIsoMu2_TauDMMedIso_IDUP = getDataset(h300a7_MedIsoMu2_TauDMMedIso_IDUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a7_MedIsoMu2_TauDMMedIso_IsoDOWN = getDataset(h300a7_MedIsoMu2_TauDMMedIso_IsoDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a7_MedIsoMu2_TauDMMedIso_IsoUP = getDataset(h300a7_MedIsoMu2_TauDMMedIso_IsoUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a7_MedIsoMu2_TauDMMedIso_BTagDOWN = getDataset(h300a7_MedIsoMu2_TauDMMedIso_BTagDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a7_MedIsoMu2_TauDMMedIso_BTagUP = getDataset(h300a7_MedIsoMu2_TauDMMedIso_BTagUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a7_MedIsoMu2_TauDMMedIso_PileupDOWN = getDataset(h300a7_MedIsoMu2_TauDMMedIso_PileupDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a7_MedIsoMu2_TauDMMedIso_PileupUP = getDataset(h300a7_MedIsoMu2_TauDMMedIso_PileupUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a9_MedIsoMu2_TauDMMedIso_Central = getDataset(h300a9_MedIsoMu2_TauDMMedIso_Central, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a9_MedIsoMu2_TauDMMedIso_IDDOWN = getDataset(h300a9_MedIsoMu2_TauDMMedIso_IDDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a9_MedIsoMu2_TauDMMedIso_IDUP = getDataset(h300a9_MedIsoMu2_TauDMMedIso_IDUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a9_MedIsoMu2_TauDMMedIso_IsoDOWN = getDataset(h300a9_MedIsoMu2_TauDMMedIso_IsoDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a9_MedIsoMu2_TauDMMedIso_IsoUP = getDataset(h300a9_MedIsoMu2_TauDMMedIso_IsoUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a9_MedIsoMu2_TauDMMedIso_BTagDOWN = getDataset(h300a9_MedIsoMu2_TauDMMedIso_BTagDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a9_MedIsoMu2_TauDMMedIso_BTagUP = getDataset(h300a9_MedIsoMu2_TauDMMedIso_BTagUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a9_MedIsoMu2_TauDMMedIso_PileupDOWN = getDataset(h300a9_MedIsoMu2_TauDMMedIso_PileupDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a9_MedIsoMu2_TauDMMedIso_PileupUP = getDataset(h300a9_MedIsoMu2_TauDMMedIso_PileupUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a11_MedIsoMu2_TauDMMedIso_Central = getDataset(h750a11_MedIsoMu2_TauDMMedIso_Central, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a11_MedIsoMu2_TauDMMedIso_IDDOWN = getDataset(h750a11_MedIsoMu2_TauDMMedIso_IDDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a11_MedIsoMu2_TauDMMedIso_IDUP = getDataset(h750a11_MedIsoMu2_TauDMMedIso_IDUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a11_MedIsoMu2_TauDMMedIso_IsoDOWN = getDataset(h750a11_MedIsoMu2_TauDMMedIso_IsoDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a11_MedIsoMu2_TauDMMedIso_IsoUP = getDataset(h750a11_MedIsoMu2_TauDMMedIso_IsoUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a11_MedIsoMu2_TauDMMedIso_BTagDOWN = getDataset(h750a11_MedIsoMu2_TauDMMedIso_BTagDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a11_MedIsoMu2_TauDMMedIso_BTagUP = getDataset(h750a11_MedIsoMu2_TauDMMedIso_BTagUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a11_MedIsoMu2_TauDMMedIso_PileupDOWN = getDataset(h750a11_MedIsoMu2_TauDMMedIso_PileupDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a11_MedIsoMu2_TauDMMedIso_PileupUP = getDataset(h750a11_MedIsoMu2_TauDMMedIso_PileupUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a13_MedIsoMu2_TauDMMedIso_Central = getDataset(h750a13_MedIsoMu2_TauDMMedIso_Central, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a13_MedIsoMu2_TauDMMedIso_IDDOWN = getDataset(h750a13_MedIsoMu2_TauDMMedIso_IDDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a13_MedIsoMu2_TauDMMedIso_IDUP = getDataset(h750a13_MedIsoMu2_TauDMMedIso_IDUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a13_MedIsoMu2_TauDMMedIso_IsoDOWN = getDataset(h750a13_MedIsoMu2_TauDMMedIso_IsoDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a13_MedIsoMu2_TauDMMedIso_IsoUP = getDataset(h750a13_MedIsoMu2_TauDMMedIso_IsoUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a13_MedIsoMu2_TauDMMedIso_BTagDOWN = getDataset(h750a13_MedIsoMu2_TauDMMedIso_BTagDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a13_MedIsoMu2_TauDMMedIso_BTagUP = getDataset(h750a13_MedIsoMu2_TauDMMedIso_BTagUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a13_MedIsoMu2_TauDMMedIso_PileupDOWN = getDataset(h750a13_MedIsoMu2_TauDMMedIso_PileupDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a13_MedIsoMu2_TauDMMedIso_PileupUP = getDataset(h750a13_MedIsoMu2_TauDMMedIso_PileupUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a15_MedIsoMu2_TauDMMedIso_Central = getDataset(h750a15_MedIsoMu2_TauDMMedIso_Central, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a15_MedIsoMu2_TauDMMedIso_IDDOWN = getDataset(h750a15_MedIsoMu2_TauDMMedIso_IDDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a15_MedIsoMu2_TauDMMedIso_IDUP = getDataset(h750a15_MedIsoMu2_TauDMMedIso_IDUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a15_MedIsoMu2_TauDMMedIso_IsoDOWN = getDataset(h750a15_MedIsoMu2_TauDMMedIso_IsoDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a15_MedIsoMu2_TauDMMedIso_IsoUP = getDataset(h750a15_MedIsoMu2_TauDMMedIso_IsoUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a15_MedIsoMu2_TauDMMedIso_BTagDOWN = getDataset(h750a15_MedIsoMu2_TauDMMedIso_BTagDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a15_MedIsoMu2_TauDMMedIso_BTagUP = getDataset(h750a15_MedIsoMu2_TauDMMedIso_BTagUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a15_MedIsoMu2_TauDMMedIso_PileupDOWN = getDataset(h750a15_MedIsoMu2_TauDMMedIso_PileupDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a15_MedIsoMu2_TauDMMedIso_PileupUP = getDataset(h750a15_MedIsoMu2_TauDMMedIso_PileupUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a17_MedIsoMu2_TauDMMedIso_Central = getDataset(h750a17_MedIsoMu2_TauDMMedIso_Central, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a17_MedIsoMu2_TauDMMedIso_IDDOWN = getDataset(h750a17_MedIsoMu2_TauDMMedIso_IDDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a17_MedIsoMu2_TauDMMedIso_IDUP = getDataset(h750a17_MedIsoMu2_TauDMMedIso_IDUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a17_MedIsoMu2_TauDMMedIso_IsoDOWN = getDataset(h750a17_MedIsoMu2_TauDMMedIso_IsoDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a17_MedIsoMu2_TauDMMedIso_IsoUP = getDataset(h750a17_MedIsoMu2_TauDMMedIso_IsoUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a17_MedIsoMu2_TauDMMedIso_BTagDOWN = getDataset(h750a17_MedIsoMu2_TauDMMedIso_BTagDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a17_MedIsoMu2_TauDMMedIso_BTagUP = getDataset(h750a17_MedIsoMu2_TauDMMedIso_BTagUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a17_MedIsoMu2_TauDMMedIso_PileupDOWN = getDataset(h750a17_MedIsoMu2_TauDMMedIso_PileupDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a17_MedIsoMu2_TauDMMedIso_PileupUP = getDataset(h750a17_MedIsoMu2_TauDMMedIso_PileupUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a19_MedIsoMu2_TauDMMedIso_Central = getDataset(h750a19_MedIsoMu2_TauDMMedIso_Central, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a19_MedIsoMu2_TauDMMedIso_IDDOWN = getDataset(h750a19_MedIsoMu2_TauDMMedIso_IDDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a19_MedIsoMu2_TauDMMedIso_IDUP = getDataset(h750a19_MedIsoMu2_TauDMMedIso_IDUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a19_MedIsoMu2_TauDMMedIso_IsoDOWN = getDataset(h750a19_MedIsoMu2_TauDMMedIso_IsoDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a19_MedIsoMu2_TauDMMedIso_IsoUP = getDataset(h750a19_MedIsoMu2_TauDMMedIso_IsoUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a19_MedIsoMu2_TauDMMedIso_BTagDOWN = getDataset(h750a19_MedIsoMu2_TauDMMedIso_BTagDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a19_MedIsoMu2_TauDMMedIso_BTagUP = getDataset(h750a19_MedIsoMu2_TauDMMedIso_BTagUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a19_MedIsoMu2_TauDMMedIso_PileupDOWN = getDataset(h750a19_MedIsoMu2_TauDMMedIso_PileupDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a19_MedIsoMu2_TauDMMedIso_PileupUP = getDataset(h750a19_MedIsoMu2_TauDMMedIso_PileupUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a21_MedIsoMu2_TauDMMedIso_Central = getDataset(h750a21_MedIsoMu2_TauDMMedIso_Central, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a21_MedIsoMu2_TauDMMedIso_IDDOWN = getDataset(h750a21_MedIsoMu2_TauDMMedIso_IDDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a21_MedIsoMu2_TauDMMedIso_IDUP = getDataset(h750a21_MedIsoMu2_TauDMMedIso_IDUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a21_MedIsoMu2_TauDMMedIso_IsoDOWN = getDataset(h750a21_MedIsoMu2_TauDMMedIso_IsoDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a21_MedIsoMu2_TauDMMedIso_IsoUP = getDataset(h750a21_MedIsoMu2_TauDMMedIso_IsoUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a21_MedIsoMu2_TauDMMedIso_BTagDOWN = getDataset(h750a21_MedIsoMu2_TauDMMedIso_BTagDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a21_MedIsoMu2_TauDMMedIso_BTagUP = getDataset(h750a21_MedIsoMu2_TauDMMedIso_BTagUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a21_MedIsoMu2_TauDMMedIso_PileupDOWN = getDataset(h750a21_MedIsoMu2_TauDMMedIso_PileupDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a21_MedIsoMu2_TauDMMedIso_PileupUP = getDataset(h750a21_MedIsoMu2_TauDMMedIso_PileupUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a5_MedIsoMu2_TauDMMedIso_Central = getDataset(h750a5_MedIsoMu2_TauDMMedIso_Central, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a5_MedIsoMu2_TauDMMedIso_IDDOWN = getDataset(h750a5_MedIsoMu2_TauDMMedIso_IDDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a5_MedIsoMu2_TauDMMedIso_IDUP = getDataset(h750a5_MedIsoMu2_TauDMMedIso_IDUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a5_MedIsoMu2_TauDMMedIso_IsoDOWN = getDataset(h750a5_MedIsoMu2_TauDMMedIso_IsoDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a5_MedIsoMu2_TauDMMedIso_IsoUP = getDataset(h750a5_MedIsoMu2_TauDMMedIso_IsoUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a5_MedIsoMu2_TauDMMedIso_BTagDOWN = getDataset(h750a5_MedIsoMu2_TauDMMedIso_BTagDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a5_MedIsoMu2_TauDMMedIso_BTagUP = getDataset(h750a5_MedIsoMu2_TauDMMedIso_BTagUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a5_MedIsoMu2_TauDMMedIso_PileupDOWN = getDataset(h750a5_MedIsoMu2_TauDMMedIso_PileupDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a5_MedIsoMu2_TauDMMedIso_PileupUP = getDataset(h750a5_MedIsoMu2_TauDMMedIso_PileupUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a7_MedIsoMu2_TauDMMedIso_Central = getDataset(h750a7_MedIsoMu2_TauDMMedIso_Central, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a7_MedIsoMu2_TauDMMedIso_IDDOWN = getDataset(h750a7_MedIsoMu2_TauDMMedIso_IDDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a7_MedIsoMu2_TauDMMedIso_IDUP = getDataset(h750a7_MedIsoMu2_TauDMMedIso_IDUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a7_MedIsoMu2_TauDMMedIso_IsoDOWN = getDataset(h750a7_MedIsoMu2_TauDMMedIso_IsoDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a7_MedIsoMu2_TauDMMedIso_IsoUP = getDataset(h750a7_MedIsoMu2_TauDMMedIso_IsoUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a7_MedIsoMu2_TauDMMedIso_BTagDOWN = getDataset(h750a7_MedIsoMu2_TauDMMedIso_BTagDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a7_MedIsoMu2_TauDMMedIso_BTagUP = getDataset(h750a7_MedIsoMu2_TauDMMedIso_BTagUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a7_MedIsoMu2_TauDMMedIso_PileupDOWN = getDataset(h750a7_MedIsoMu2_TauDMMedIso_PileupDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a7_MedIsoMu2_TauDMMedIso_PileupUP = getDataset(h750a7_MedIsoMu2_TauDMMedIso_PileupUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a9_MedIsoMu2_TauDMMedIso_Central = getDataset(h750a9_MedIsoMu2_TauDMMedIso_Central, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a9_MedIsoMu2_TauDMMedIso_IDDOWN = getDataset(h750a9_MedIsoMu2_TauDMMedIso_IDDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a9_MedIsoMu2_TauDMMedIso_IDUP = getDataset(h750a9_MedIsoMu2_TauDMMedIso_IDUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a9_MedIsoMu2_TauDMMedIso_IsoDOWN = getDataset(h750a9_MedIsoMu2_TauDMMedIso_IsoDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a9_MedIsoMu2_TauDMMedIso_IsoUP = getDataset(h750a9_MedIsoMu2_TauDMMedIso_IsoUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a9_MedIsoMu2_TauDMMedIso_BTagDOWN = getDataset(h750a9_MedIsoMu2_TauDMMedIso_BTagDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a9_MedIsoMu2_TauDMMedIso_BTagUP = getDataset(h750a9_MedIsoMu2_TauDMMedIso_BTagUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a9_MedIsoMu2_TauDMMedIso_PileupDOWN = getDataset(h750a9_MedIsoMu2_TauDMMedIso_PileupDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a9_MedIsoMu2_TauDMMedIso_PileupUP = getDataset(h750a9_MedIsoMu2_TauDMMedIso_PileupUP, selection='x <= 25 && x >= 4', xRange=xRange)

   dictionary['PP']['']['HToAAH125A11'] = h125a11_MedIsoMu2_TauDMMedIso_Central
   dictionary['PP']['']['HToAAH125A13'] = h125a13_MedIsoMu2_TauDMMedIso_Central
   dictionary['PP']['']['HToAAH125A15'] = h125a15_MedIsoMu2_TauDMMedIso_Central
   dictionary['PP']['']['HToAAH125A17'] = h125a17_MedIsoMu2_TauDMMedIso_Central
   dictionary['PP']['']['HToAAH125A19'] = h125a19_MedIsoMu2_TauDMMedIso_Central
   dictionary['PP']['']['HToAAH125A21'] = h125a21_MedIsoMu2_TauDMMedIso_Central
   dictionary['PP']['']['HToAAH125A5'] = h125a5_MedIsoMu2_TauDMMedIso_Central
   dictionary['PP']['']['HToAAH125A7'] = h125a7_MedIsoMu2_TauDMMedIso_Central
   dictionary['PP']['']['HToAAH125A9'] = h125a9_MedIsoMu2_TauDMMedIso_Central
   dictionary['PP']['']['HToAAH300A11'] = h300a11_MedIsoMu2_TauDMMedIso_Central
   dictionary['PP']['']['HToAAH300A13'] = h300a13_MedIsoMu2_TauDMMedIso_Central
   dictionary['PP']['']['HToAAH300A15'] = h300a15_MedIsoMu2_TauDMMedIso_Central
   dictionary['PP']['']['HToAAH300A17'] = h300a17_MedIsoMu2_TauDMMedIso_Central
   dictionary['PP']['']['HToAAH300A19'] = h300a19_MedIsoMu2_TauDMMedIso_Central
   dictionary['PP']['']['HToAAH300A21'] = h300a21_MedIsoMu2_TauDMMedIso_Central
   dictionary['PP']['']['HToAAH300A5'] = h300a5_MedIsoMu2_TauDMMedIso_Central
   dictionary['PP']['']['HToAAH300A7'] = h300a7_MedIsoMu2_TauDMMedIso_Central
   dictionary['PP']['']['HToAAH300A9'] = h300a9_MedIsoMu2_TauDMMedIso_Central
   dictionary['PP']['']['HToAAH750A11'] = h750a11_MedIsoMu2_TauDMMedIso_Central
   dictionary['PP']['']['HToAAH750A13'] = h750a13_MedIsoMu2_TauDMMedIso_Central
   dictionary['PP']['']['HToAAH750A15'] = h750a15_MedIsoMu2_TauDMMedIso_Central
   dictionary['PP']['']['HToAAH750A17'] = h750a17_MedIsoMu2_TauDMMedIso_Central
   dictionary['PP']['']['HToAAH750A19'] = h750a19_MedIsoMu2_TauDMMedIso_Central
   dictionary['PP']['']['HToAAH750A21'] = h750a21_MedIsoMu2_TauDMMedIso_Central
   dictionary['PP']['']['HToAAH750A5'] = h750a5_MedIsoMu2_TauDMMedIso_Central
   dictionary['PP']['']['HToAAH750A7'] = h750a7_MedIsoMu2_TauDMMedIso_Central
   dictionary['PP']['']['HToAAH750A9'] = h750a9_MedIsoMu2_TauDMMedIso_Central
   dictionary['PP']['IDUp']['HToAAH125A11'] = h125a11_MedIsoMu2_TauDMMedIso_IDUP
   dictionary['PP']['IDUp']['HToAAH125A13'] = h125a13_MedIsoMu2_TauDMMedIso_IDUP
   dictionary['PP']['IDUp']['HToAAH125A15'] = h125a15_MedIsoMu2_TauDMMedIso_IDUP
   dictionary['PP']['IDUp']['HToAAH125A17'] = h125a17_MedIsoMu2_TauDMMedIso_IDUP
   dictionary['PP']['IDUp']['HToAAH125A19'] = h125a19_MedIsoMu2_TauDMMedIso_IDUP
   dictionary['PP']['IDUp']['HToAAH125A21'] = h125a21_MedIsoMu2_TauDMMedIso_IDUP
   dictionary['PP']['IDUp']['HToAAH125A5'] = h125a5_MedIsoMu2_TauDMMedIso_IDUP
   dictionary['PP']['IDUp']['HToAAH125A7'] = h125a7_MedIsoMu2_TauDMMedIso_IDUP
   dictionary['PP']['IDUp']['HToAAH125A9'] = h125a9_MedIsoMu2_TauDMMedIso_IDUP
   dictionary['PP']['IDUp']['HToAAH300A11'] = h300a11_MedIsoMu2_TauDMMedIso_IDUP
   dictionary['PP']['IDUp']['HToAAH300A13'] = h300a13_MedIsoMu2_TauDMMedIso_IDUP
   dictionary['PP']['IDUp']['HToAAH300A15'] = h300a15_MedIsoMu2_TauDMMedIso_IDUP
   dictionary['PP']['IDUp']['HToAAH300A17'] = h300a17_MedIsoMu2_TauDMMedIso_IDUP
   dictionary['PP']['IDUp']['HToAAH300A19'] = h300a19_MedIsoMu2_TauDMMedIso_IDUP
   dictionary['PP']['IDUp']['HToAAH300A21'] = h300a21_MedIsoMu2_TauDMMedIso_IDUP
   dictionary['PP']['IDUp']['HToAAH300A5'] = h300a5_MedIsoMu2_TauDMMedIso_IDUP
   dictionary['PP']['IDUp']['HToAAH300A7'] = h300a7_MedIsoMu2_TauDMMedIso_IDUP
   dictionary['PP']['IDUp']['HToAAH300A9'] = h300a9_MedIsoMu2_TauDMMedIso_IDUP
   dictionary['PP']['IDUp']['HToAAH750A11'] = h750a11_MedIsoMu2_TauDMMedIso_IDUP
   dictionary['PP']['IDUp']['HToAAH750A13'] = h750a13_MedIsoMu2_TauDMMedIso_IDUP
   dictionary['PP']['IDUp']['HToAAH750A15'] = h750a15_MedIsoMu2_TauDMMedIso_IDUP
   dictionary['PP']['IDUp']['HToAAH750A17'] = h750a17_MedIsoMu2_TauDMMedIso_IDUP
   dictionary['PP']['IDUp']['HToAAH750A19'] = h750a19_MedIsoMu2_TauDMMedIso_IDUP
   dictionary['PP']['IDUp']['HToAAH750A21'] = h750a21_MedIsoMu2_TauDMMedIso_IDUP
   dictionary['PP']['IDUp']['HToAAH750A5'] = h750a5_MedIsoMu2_TauDMMedIso_IDUP
   dictionary['PP']['IDUp']['HToAAH750A7'] = h750a7_MedIsoMu2_TauDMMedIso_IDUP
   dictionary['PP']['IDUp']['HToAAH750A9'] = h750a9_MedIsoMu2_TauDMMedIso_IDUP
   dictionary['PP']['IDDown']['HToAAH125A11'] = h125a11_MedIsoMu2_TauDMMedIso_IDDOWN
   dictionary['PP']['IDDown']['HToAAH125A13'] = h125a13_MedIsoMu2_TauDMMedIso_IDDOWN
   dictionary['PP']['IDDown']['HToAAH125A15'] = h125a15_MedIsoMu2_TauDMMedIso_IDDOWN
   dictionary['PP']['IDDown']['HToAAH125A17'] = h125a17_MedIsoMu2_TauDMMedIso_IDDOWN
   dictionary['PP']['IDDown']['HToAAH125A19'] = h125a19_MedIsoMu2_TauDMMedIso_IDDOWN
   dictionary['PP']['IDDown']['HToAAH125A21'] = h125a21_MedIsoMu2_TauDMMedIso_IDDOWN
   dictionary['PP']['IDDown']['HToAAH125A5'] = h125a5_MedIsoMu2_TauDMMedIso_IDDOWN
   dictionary['PP']['IDDown']['HToAAH125A7'] = h125a7_MedIsoMu2_TauDMMedIso_IDDOWN
   dictionary['PP']['IDDown']['HToAAH125A9'] = h125a9_MedIsoMu2_TauDMMedIso_IDDOWN
   dictionary['PP']['IDDown']['HToAAH300A11'] = h300a11_MedIsoMu2_TauDMMedIso_IDDOWN
   dictionary['PP']['IDDown']['HToAAH300A13'] = h300a13_MedIsoMu2_TauDMMedIso_IDDOWN
   dictionary['PP']['IDDown']['HToAAH300A15'] = h300a15_MedIsoMu2_TauDMMedIso_IDDOWN
   dictionary['PP']['IDDown']['HToAAH300A17'] = h300a17_MedIsoMu2_TauDMMedIso_IDDOWN
   dictionary['PP']['IDDown']['HToAAH300A19'] = h300a19_MedIsoMu2_TauDMMedIso_IDDOWN
   dictionary['PP']['IDDown']['HToAAH300A21'] = h300a21_MedIsoMu2_TauDMMedIso_IDDOWN
   dictionary['PP']['IDDown']['HToAAH300A5'] = h300a5_MedIsoMu2_TauDMMedIso_IDDOWN
   dictionary['PP']['IDDown']['HToAAH300A7'] = h300a7_MedIsoMu2_TauDMMedIso_IDDOWN
   dictionary['PP']['IDDown']['HToAAH300A9'] = h300a9_MedIsoMu2_TauDMMedIso_IDDOWN
   dictionary['PP']['IDDown']['HToAAH750A11'] = h750a11_MedIsoMu2_TauDMMedIso_IDDOWN
   dictionary['PP']['IDDown']['HToAAH750A13'] = h750a13_MedIsoMu2_TauDMMedIso_IDDOWN
   dictionary['PP']['IDDown']['HToAAH750A15'] = h750a15_MedIsoMu2_TauDMMedIso_IDDOWN
   dictionary['PP']['IDDown']['HToAAH750A17'] = h750a17_MedIsoMu2_TauDMMedIso_IDDOWN
   dictionary['PP']['IDDown']['HToAAH750A19'] = h750a19_MedIsoMu2_TauDMMedIso_IDDOWN
   dictionary['PP']['IDDown']['HToAAH750A21'] = h750a21_MedIsoMu2_TauDMMedIso_IDDOWN
   dictionary['PP']['IDDown']['HToAAH750A5'] = h750a5_MedIsoMu2_TauDMMedIso_IDDOWN
   dictionary['PP']['IDDown']['HToAAH750A7'] = h750a7_MedIsoMu2_TauDMMedIso_IDDOWN
   dictionary['PP']['IDDown']['HToAAH750A9'] = h750a9_MedIsoMu2_TauDMMedIso_IDDOWN
   dictionary['PP']['IsoUp']['HToAAH125A11'] = h125a11_MedIsoMu2_TauDMMedIso_IsoUP
   dictionary['PP']['IsoUp']['HToAAH125A13'] = h125a13_MedIsoMu2_TauDMMedIso_IsoUP
   dictionary['PP']['IsoUp']['HToAAH125A15'] = h125a15_MedIsoMu2_TauDMMedIso_IsoUP
   dictionary['PP']['IsoUp']['HToAAH125A17'] = h125a17_MedIsoMu2_TauDMMedIso_IsoUP
   dictionary['PP']['IsoUp']['HToAAH125A19'] = h125a19_MedIsoMu2_TauDMMedIso_IsoUP
   dictionary['PP']['IsoUp']['HToAAH125A21'] = h125a21_MedIsoMu2_TauDMMedIso_IsoUP
   dictionary['PP']['IsoUp']['HToAAH125A5'] = h125a5_MedIsoMu2_TauDMMedIso_IsoUP
   dictionary['PP']['IsoUp']['HToAAH125A7'] = h125a7_MedIsoMu2_TauDMMedIso_IsoUP
   dictionary['PP']['IsoUp']['HToAAH125A9'] = h125a9_MedIsoMu2_TauDMMedIso_IsoUP
   dictionary['PP']['IsoUp']['HToAAH300A11'] = h300a11_MedIsoMu2_TauDMMedIso_IsoUP
   dictionary['PP']['IsoUp']['HToAAH300A13'] = h300a13_MedIsoMu2_TauDMMedIso_IsoUP
   dictionary['PP']['IsoUp']['HToAAH300A15'] = h300a15_MedIsoMu2_TauDMMedIso_IsoUP
   dictionary['PP']['IsoUp']['HToAAH300A17'] = h300a17_MedIsoMu2_TauDMMedIso_IsoUP
   dictionary['PP']['IsoUp']['HToAAH300A19'] = h300a19_MedIsoMu2_TauDMMedIso_IsoUP
   dictionary['PP']['IsoUp']['HToAAH300A21'] = h300a21_MedIsoMu2_TauDMMedIso_IsoUP
   dictionary['PP']['IsoUp']['HToAAH300A5'] = h300a5_MedIsoMu2_TauDMMedIso_IsoUP
   dictionary['PP']['IsoUp']['HToAAH300A7'] = h300a7_MedIsoMu2_TauDMMedIso_IsoUP
   dictionary['PP']['IsoUp']['HToAAH300A9'] = h300a9_MedIsoMu2_TauDMMedIso_IsoUP
   dictionary['PP']['IsoUp']['HToAAH750A11'] = h750a11_MedIsoMu2_TauDMMedIso_IsoUP
   dictionary['PP']['IsoUp']['HToAAH750A13'] = h750a13_MedIsoMu2_TauDMMedIso_IsoUP
   dictionary['PP']['IsoUp']['HToAAH750A15'] = h750a15_MedIsoMu2_TauDMMedIso_IsoUP
   dictionary['PP']['IsoUp']['HToAAH750A17'] = h750a17_MedIsoMu2_TauDMMedIso_IsoUP
   dictionary['PP']['IsoUp']['HToAAH750A19'] = h750a19_MedIsoMu2_TauDMMedIso_IsoUP
   dictionary['PP']['IsoUp']['HToAAH750A21'] = h750a21_MedIsoMu2_TauDMMedIso_IsoUP
   dictionary['PP']['IsoUp']['HToAAH750A5'] = h750a5_MedIsoMu2_TauDMMedIso_IsoUP
   dictionary['PP']['IsoUp']['HToAAH750A7'] = h750a7_MedIsoMu2_TauDMMedIso_IsoUP
   dictionary['PP']['IsoUp']['HToAAH750A9'] = h750a9_MedIsoMu2_TauDMMedIso_IsoUP
   dictionary['PP']['BTagDown']['HToAAH125A11'] = h125a11_MedIsoMu2_TauDMMedIso_BTagDOWN
   dictionary['PP']['BTagDown']['HToAAH125A13'] = h125a13_MedIsoMu2_TauDMMedIso_BTagDOWN
   dictionary['PP']['BTagDown']['HToAAH125A15'] = h125a15_MedIsoMu2_TauDMMedIso_BTagDOWN
   dictionary['PP']['BTagDown']['HToAAH125A17'] = h125a17_MedIsoMu2_TauDMMedIso_BTagDOWN
   dictionary['PP']['BTagDown']['HToAAH125A19'] = h125a19_MedIsoMu2_TauDMMedIso_BTagDOWN
   dictionary['PP']['BTagDown']['HToAAH125A21'] = h125a21_MedIsoMu2_TauDMMedIso_BTagDOWN
   dictionary['PP']['BTagDown']['HToAAH125A5'] = h125a5_MedIsoMu2_TauDMMedIso_BTagDOWN
   dictionary['PP']['BTagDown']['HToAAH125A7'] = h125a7_MedIsoMu2_TauDMMedIso_BTagDOWN
   dictionary['PP']['BTagDown']['HToAAH125A9'] = h125a9_MedIsoMu2_TauDMMedIso_BTagDOWN
   dictionary['PP']['BTagDown']['HToAAH300A11'] = h300a11_MedIsoMu2_TauDMMedIso_BTagDOWN
   dictionary['PP']['BTagDown']['HToAAH300A13'] = h300a13_MedIsoMu2_TauDMMedIso_BTagDOWN
   dictionary['PP']['BTagDown']['HToAAH300A15'] = h300a15_MedIsoMu2_TauDMMedIso_BTagDOWN
   dictionary['PP']['BTagDown']['HToAAH300A17'] = h300a17_MedIsoMu2_TauDMMedIso_BTagDOWN
   dictionary['PP']['BTagDown']['HToAAH300A19'] = h300a19_MedIsoMu2_TauDMMedIso_BTagDOWN
   dictionary['PP']['BTagDown']['HToAAH300A21'] = h300a21_MedIsoMu2_TauDMMedIso_BTagDOWN
   dictionary['PP']['BTagDown']['HToAAH300A5'] = h300a5_MedIsoMu2_TauDMMedIso_BTagDOWN
   dictionary['PP']['BTagDown']['HToAAH300A7'] = h300a7_MedIsoMu2_TauDMMedIso_BTagDOWN
   dictionary['PP']['BTagDown']['HToAAH300A9'] = h300a9_MedIsoMu2_TauDMMedIso_BTagDOWN
   dictionary['PP']['BTagDown']['HToAAH750A11'] = h750a11_MedIsoMu2_TauDMMedIso_BTagDOWN
   dictionary['PP']['BTagDown']['HToAAH750A13'] = h750a13_MedIsoMu2_TauDMMedIso_BTagDOWN
   dictionary['PP']['BTagDown']['HToAAH750A15'] = h750a15_MedIsoMu2_TauDMMedIso_BTagDOWN
   dictionary['PP']['BTagDown']['HToAAH750A17'] = h750a17_MedIsoMu2_TauDMMedIso_BTagDOWN
   dictionary['PP']['BTagDown']['HToAAH750A19'] = h750a19_MedIsoMu2_TauDMMedIso_BTagDOWN
   dictionary['PP']['BTagDown']['HToAAH750A21'] = h750a21_MedIsoMu2_TauDMMedIso_BTagDOWN
   dictionary['PP']['BTagDown']['HToAAH750A5'] = h750a5_MedIsoMu2_TauDMMedIso_BTagDOWN
   dictionary['PP']['BTagDown']['HToAAH750A7'] = h750a7_MedIsoMu2_TauDMMedIso_BTagDOWN
   dictionary['PP']['BTagDown']['HToAAH750A9'] = h750a9_MedIsoMu2_TauDMMedIso_BTagDOWN
   dictionary['PP']['BTagUp']['HToAAH125A11'] = h125a11_MedIsoMu2_TauDMMedIso_BTagUP
   dictionary['PP']['BTagUp']['HToAAH125A13'] = h125a13_MedIsoMu2_TauDMMedIso_BTagUP
   dictionary['PP']['BTagUp']['HToAAH125A15'] = h125a15_MedIsoMu2_TauDMMedIso_BTagUP
   dictionary['PP']['BTagUp']['HToAAH125A17'] = h125a17_MedIsoMu2_TauDMMedIso_BTagUP
   dictionary['PP']['BTagUp']['HToAAH125A19'] = h125a19_MedIsoMu2_TauDMMedIso_BTagUP
   dictionary['PP']['BTagUp']['HToAAH125A21'] = h125a21_MedIsoMu2_TauDMMedIso_BTagUP
   dictionary['PP']['BTagUp']['HToAAH125A5'] = h125a5_MedIsoMu2_TauDMMedIso_BTagUP
   dictionary['PP']['BTagUp']['HToAAH125A7'] = h125a7_MedIsoMu2_TauDMMedIso_BTagUP
   dictionary['PP']['BTagUp']['HToAAH125A9'] = h125a9_MedIsoMu2_TauDMMedIso_BTagUP
   dictionary['PP']['BTagUp']['HToAAH300A11'] = h300a11_MedIsoMu2_TauDMMedIso_BTagUP
   dictionary['PP']['BTagUp']['HToAAH300A13'] = h300a13_MedIsoMu2_TauDMMedIso_BTagUP
   dictionary['PP']['BTagUp']['HToAAH300A15'] = h300a15_MedIsoMu2_TauDMMedIso_BTagUP
   dictionary['PP']['BTagUp']['HToAAH300A17'] = h300a17_MedIsoMu2_TauDMMedIso_BTagUP
   dictionary['PP']['BTagUp']['HToAAH300A19'] = h300a19_MedIsoMu2_TauDMMedIso_BTagUP
   dictionary['PP']['BTagUp']['HToAAH300A21'] = h300a21_MedIsoMu2_TauDMMedIso_BTagUP
   dictionary['PP']['BTagUp']['HToAAH300A5'] = h300a5_MedIsoMu2_TauDMMedIso_BTagUP
   dictionary['PP']['BTagUp']['HToAAH300A7'] = h300a7_MedIsoMu2_TauDMMedIso_BTagUP
   dictionary['PP']['BTagUp']['HToAAH300A9'] = h300a9_MedIsoMu2_TauDMMedIso_BTagUP
   dictionary['PP']['BTagUp']['HToAAH750A11'] = h750a11_MedIsoMu2_TauDMMedIso_BTagUP
   dictionary['PP']['BTagUp']['HToAAH750A13'] = h750a13_MedIsoMu2_TauDMMedIso_BTagUP
   dictionary['PP']['BTagUp']['HToAAH750A15'] = h750a15_MedIsoMu2_TauDMMedIso_BTagUP
   dictionary['PP']['BTagUp']['HToAAH750A17'] = h750a17_MedIsoMu2_TauDMMedIso_BTagUP
   dictionary['PP']['BTagUp']['HToAAH750A19'] = h750a19_MedIsoMu2_TauDMMedIso_BTagUP
   dictionary['PP']['BTagUp']['HToAAH750A21'] = h750a21_MedIsoMu2_TauDMMedIso_BTagUP
   dictionary['PP']['BTagUp']['HToAAH750A5'] = h750a5_MedIsoMu2_TauDMMedIso_BTagUP
   dictionary['PP']['BTagUp']['HToAAH750A7'] = h750a7_MedIsoMu2_TauDMMedIso_BTagUP
   dictionary['PP']['BTagUp']['HToAAH750A9'] = h750a9_MedIsoMu2_TauDMMedIso_BTagUP
   dictionary['PP']['IsoDown']['HToAAH125A11'] = h125a11_MedIsoMu2_TauDMMedIso_IsoDOWN
   dictionary['PP']['IsoDown']['HToAAH125A13'] = h125a13_MedIsoMu2_TauDMMedIso_IsoDOWN
   dictionary['PP']['IsoDown']['HToAAH125A15'] = h125a15_MedIsoMu2_TauDMMedIso_IsoDOWN
   dictionary['PP']['IsoDown']['HToAAH125A17'] = h125a17_MedIsoMu2_TauDMMedIso_IsoDOWN
   dictionary['PP']['IsoDown']['HToAAH125A19'] = h125a19_MedIsoMu2_TauDMMedIso_IsoDOWN
   dictionary['PP']['IsoDown']['HToAAH125A21'] = h125a21_MedIsoMu2_TauDMMedIso_IsoDOWN
   dictionary['PP']['IsoDown']['HToAAH125A5'] = h125a5_MedIsoMu2_TauDMMedIso_IsoDOWN
   dictionary['PP']['IsoDown']['HToAAH125A7'] = h125a7_MedIsoMu2_TauDMMedIso_IsoDOWN
   dictionary['PP']['IsoDown']['HToAAH125A9'] = h125a9_MedIsoMu2_TauDMMedIso_IsoDOWN
   dictionary['PP']['IsoDown']['HToAAH300A11'] = h300a11_MedIsoMu2_TauDMMedIso_IsoDOWN
   dictionary['PP']['IsoDown']['HToAAH300A13'] = h300a13_MedIsoMu2_TauDMMedIso_IsoDOWN
   dictionary['PP']['IsoDown']['HToAAH300A15'] = h300a15_MedIsoMu2_TauDMMedIso_IsoDOWN
   dictionary['PP']['IsoDown']['HToAAH300A17'] = h300a17_MedIsoMu2_TauDMMedIso_IsoDOWN
   dictionary['PP']['IsoDown']['HToAAH300A19'] = h300a19_MedIsoMu2_TauDMMedIso_IsoDOWN
   dictionary['PP']['IsoDown']['HToAAH300A21'] = h300a21_MedIsoMu2_TauDMMedIso_IsoDOWN
   dictionary['PP']['IsoDown']['HToAAH300A5'] = h300a5_MedIsoMu2_TauDMMedIso_IsoDOWN
   dictionary['PP']['IsoDown']['HToAAH300A7'] = h300a7_MedIsoMu2_TauDMMedIso_IsoDOWN
   dictionary['PP']['IsoDown']['HToAAH300A9'] = h300a9_MedIsoMu2_TauDMMedIso_IsoDOWN
   dictionary['PP']['IsoDown']['HToAAH750A11'] = h750a11_MedIsoMu2_TauDMMedIso_IsoDOWN
   dictionary['PP']['IsoDown']['HToAAH750A13'] = h750a13_MedIsoMu2_TauDMMedIso_IsoDOWN
   dictionary['PP']['IsoDown']['HToAAH750A15'] = h750a15_MedIsoMu2_TauDMMedIso_IsoDOWN
   dictionary['PP']['IsoDown']['HToAAH750A17'] = h750a17_MedIsoMu2_TauDMMedIso_IsoDOWN
   dictionary['PP']['IsoDown']['HToAAH750A19'] = h750a19_MedIsoMu2_TauDMMedIso_IsoDOWN
   dictionary['PP']['IsoDown']['HToAAH750A21'] = h750a21_MedIsoMu2_TauDMMedIso_IsoDOWN
   dictionary['PP']['IsoDown']['HToAAH750A5'] = h750a5_MedIsoMu2_TauDMMedIso_IsoDOWN
   dictionary['PP']['IsoDown']['HToAAH750A7'] = h750a7_MedIsoMu2_TauDMMedIso_IsoDOWN
   dictionary['PP']['IsoDown']['HToAAH750A9'] = h750a9_MedIsoMu2_TauDMMedIso_IsoDOWN
   dictionary['PP']['PileupUp']['HToAAH125A11'] = h125a11_MedIsoMu2_TauDMMedIso_PileupUP
   dictionary['PP']['PileupUp']['HToAAH125A13'] = h125a13_MedIsoMu2_TauDMMedIso_PileupUP
   dictionary['PP']['PileupUp']['HToAAH125A15'] = h125a15_MedIsoMu2_TauDMMedIso_PileupUP
   dictionary['PP']['PileupUp']['HToAAH125A17'] = h125a17_MedIsoMu2_TauDMMedIso_PileupUP
   dictionary['PP']['PileupUp']['HToAAH125A19'] = h125a19_MedIsoMu2_TauDMMedIso_PileupUP
   dictionary['PP']['PileupUp']['HToAAH125A21'] = h125a21_MedIsoMu2_TauDMMedIso_PileupUP
   dictionary['PP']['PileupUp']['HToAAH125A5'] = h125a5_MedIsoMu2_TauDMMedIso_PileupUP
   dictionary['PP']['PileupUp']['HToAAH125A7'] = h125a7_MedIsoMu2_TauDMMedIso_PileupUP
   dictionary['PP']['PileupUp']['HToAAH125A9'] = h125a9_MedIsoMu2_TauDMMedIso_PileupUP
   dictionary['PP']['PileupUp']['HToAAH300A11'] = h300a11_MedIsoMu2_TauDMMedIso_PileupUP
   dictionary['PP']['PileupUp']['HToAAH300A13'] = h300a13_MedIsoMu2_TauDMMedIso_PileupUP
   dictionary['PP']['PileupUp']['HToAAH300A15'] = h300a15_MedIsoMu2_TauDMMedIso_PileupUP
   dictionary['PP']['PileupUp']['HToAAH300A17'] = h300a17_MedIsoMu2_TauDMMedIso_PileupUP
   dictionary['PP']['PileupUp']['HToAAH300A19'] = h300a19_MedIsoMu2_TauDMMedIso_PileupUP
   dictionary['PP']['PileupUp']['HToAAH300A21'] = h300a21_MedIsoMu2_TauDMMedIso_PileupUP
   dictionary['PP']['PileupUp']['HToAAH300A5'] = h300a5_MedIsoMu2_TauDMMedIso_PileupUP
   dictionary['PP']['PileupUp']['HToAAH300A7'] = h300a7_MedIsoMu2_TauDMMedIso_PileupUP
   dictionary['PP']['PileupUp']['HToAAH300A9'] = h300a9_MedIsoMu2_TauDMMedIso_PileupUP
   dictionary['PP']['PileupUp']['HToAAH750A11'] = h750a11_MedIsoMu2_TauDMMedIso_PileupUP
   dictionary['PP']['PileupUp']['HToAAH750A13'] = h750a13_MedIsoMu2_TauDMMedIso_PileupUP
   dictionary['PP']['PileupUp']['HToAAH750A15'] = h750a15_MedIsoMu2_TauDMMedIso_PileupUP
   dictionary['PP']['PileupUp']['HToAAH750A17'] = h750a17_MedIsoMu2_TauDMMedIso_PileupUP
   dictionary['PP']['PileupUp']['HToAAH750A19'] = h750a19_MedIsoMu2_TauDMMedIso_PileupUP
   dictionary['PP']['PileupUp']['HToAAH750A21'] = h750a21_MedIsoMu2_TauDMMedIso_PileupUP
   dictionary['PP']['PileupUp']['HToAAH750A5'] = h750a5_MedIsoMu2_TauDMMedIso_PileupUP
   dictionary['PP']['PileupUp']['HToAAH750A7'] = h750a7_MedIsoMu2_TauDMMedIso_PileupUP
   dictionary['PP']['PileupUp']['HToAAH750A9'] = h750a9_MedIsoMu2_TauDMMedIso_PileupUP
   dictionary['PP']['PileupDown']['HToAAH125A11'] = h125a11_MedIsoMu2_TauDMMedIso_PileupDOWN
   dictionary['PP']['PileupDown']['HToAAH125A13'] = h125a13_MedIsoMu2_TauDMMedIso_PileupDOWN
   dictionary['PP']['PileupDown']['HToAAH125A15'] = h125a15_MedIsoMu2_TauDMMedIso_PileupDOWN
   dictionary['PP']['PileupDown']['HToAAH125A17'] = h125a17_MedIsoMu2_TauDMMedIso_PileupDOWN
   dictionary['PP']['PileupDown']['HToAAH125A19'] = h125a19_MedIsoMu2_TauDMMedIso_PileupDOWN
   dictionary['PP']['PileupDown']['HToAAH125A21'] = h125a21_MedIsoMu2_TauDMMedIso_PileupDOWN
   dictionary['PP']['PileupDown']['HToAAH125A5'] = h125a5_MedIsoMu2_TauDMMedIso_PileupDOWN
   dictionary['PP']['PileupDown']['HToAAH125A7'] = h125a7_MedIsoMu2_TauDMMedIso_PileupDOWN
   dictionary['PP']['PileupDown']['HToAAH125A9'] = h125a9_MedIsoMu2_TauDMMedIso_PileupDOWN
   dictionary['PP']['PileupDown']['HToAAH300A11'] = h300a11_MedIsoMu2_TauDMMedIso_PileupDOWN
   dictionary['PP']['PileupDown']['HToAAH300A13'] = h300a13_MedIsoMu2_TauDMMedIso_PileupDOWN
   dictionary['PP']['PileupDown']['HToAAH300A15'] = h300a15_MedIsoMu2_TauDMMedIso_PileupDOWN
   dictionary['PP']['PileupDown']['HToAAH300A17'] = h300a17_MedIsoMu2_TauDMMedIso_PileupDOWN
   dictionary['PP']['PileupDown']['HToAAH300A19'] = h300a19_MedIsoMu2_TauDMMedIso_PileupDOWN
   dictionary['PP']['PileupDown']['HToAAH300A21'] = h300a21_MedIsoMu2_TauDMMedIso_PileupDOWN
   dictionary['PP']['PileupDown']['HToAAH300A5'] = h300a5_MedIsoMu2_TauDMMedIso_PileupDOWN
   dictionary['PP']['PileupDown']['HToAAH300A7'] = h300a7_MedIsoMu2_TauDMMedIso_PileupDOWN
   dictionary['PP']['PileupDown']['HToAAH300A9'] = h300a9_MedIsoMu2_TauDMMedIso_PileupDOWN
   dictionary['PP']['PileupDown']['HToAAH750A11'] = h750a11_MedIsoMu2_TauDMMedIso_PileupDOWN
   dictionary['PP']['PileupDown']['HToAAH750A13'] = h750a13_MedIsoMu2_TauDMMedIso_PileupDOWN
   dictionary['PP']['PileupDown']['HToAAH750A15'] = h750a15_MedIsoMu2_TauDMMedIso_PileupDOWN
   dictionary['PP']['PileupDown']['HToAAH750A17'] = h750a17_MedIsoMu2_TauDMMedIso_PileupDOWN
   dictionary['PP']['PileupDown']['HToAAH750A19'] = h750a19_MedIsoMu2_TauDMMedIso_PileupDOWN
   dictionary['PP']['PileupDown']['HToAAH750A21'] = h750a21_MedIsoMu2_TauDMMedIso_PileupDOWN
   dictionary['PP']['PileupDown']['HToAAH750A5'] = h750a5_MedIsoMu2_TauDMMedIso_PileupDOWN
   dictionary['PP']['PileupDown']['HToAAH750A7'] = h750a7_MedIsoMu2_TauDMMedIso_PileupDOWN
   dictionary['PP']['PileupDown']['HToAAH750A9'] = h750a9_MedIsoMu2_TauDMMedIso_PileupDOWN


def GetFPData(dictionary,xRange=[]):

   f_FakeRateRegionB = ROOT.TFile.Open("/eos/cms/store/user/ktos/ShapeDifferences/FINAL_RooDataSet_MiniAOD_SingleMu_MedIsoMu2_TauDMAntiMedIso_APR20_DevindR.root")
   SingleMu_RegionB = f_FakeRateRegionB.Get("mumumass_dataset")
   SingleMu_RegionB = getDataset(SingleMu_RegionB, selection='x <= 25 && x >= 4', xRange=xRange)

   dictionary['FP']['']['data'] = SingleMu_RegionB
   dictionary['FP']['']['dataNoSig'] = SingleMu_RegionB

def GetFPSignal(dictionary,xRange=[]):
   f = ROOT.TFile.Open("/eos/cms/store/user/ktos/ShapeDifferences/FINAL_AllRooDataSet_MedIsoMu2_TauDMAntiMedIso_APR20_BTagSF.root")
   
   h125a11_MedIsoMu2_TauDMAntiMedIso_Central = f.Get("SIG_h125a11_MedIsoMu2_TauDMAntiMedIso_APR20_Central_BTagSF")
   h125a11_MedIsoMu2_TauDMAntiMedIso_IDDOWN = f.Get("SIG_h125a11_MedIsoMu2_TauDMAntiMedIso_APR20_IDDOWN_BTagSF")
   h125a11_MedIsoMu2_TauDMAntiMedIso_IDUP = f.Get("SIG_h125a11_MedIsoMu2_TauDMAntiMedIso_APR20_IDUP_BTagSF")
   h125a11_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = f.Get("SIG_h125a11_MedIsoMu2_TauDMAntiMedIso_APR20_IsoDOWN_BTagSF")
   h125a11_MedIsoMu2_TauDMAntiMedIso_IsoUP = f.Get("SIG_h125a11_MedIsoMu2_TauDMAntiMedIso_APR20_IsoUP_BTagSF")
   h125a11_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = f.Get("SIG_h125a11_MedIsoMu2_TauDMAntiMedIso_APR20_BTagDOWN_BTagSF")
   h125a11_MedIsoMu2_TauDMAntiMedIso_BTagUP = f.Get("SIG_h125a11_MedIsoMu2_TauDMAntiMedIso_APR20_BTagUP_BTagSF")
   h125a11_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = f.Get("SIG_h125a11_MedIsoMu2_TauDMAntiMedIso_APR20_PileupDOWN_BTagSF")
   h125a11_MedIsoMu2_TauDMAntiMedIso_PileupUP = f.Get("SIG_h125a11_MedIsoMu2_TauDMAntiMedIso_APR20_PileupUP_BTagSF")
   h125a13_MedIsoMu2_TauDMAntiMedIso_Central = f.Get("SIG_h125a13_MedIsoMu2_TauDMAntiMedIso_APR20_Central_BTagSF")
   h125a13_MedIsoMu2_TauDMAntiMedIso_IDDOWN = f.Get("SIG_h125a13_MedIsoMu2_TauDMAntiMedIso_APR20_IDDOWN_BTagSF")
   h125a13_MedIsoMu2_TauDMAntiMedIso_IDUP = f.Get("SIG_h125a13_MedIsoMu2_TauDMAntiMedIso_APR20_IDUP_BTagSF")
   h125a13_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = f.Get("SIG_h125a13_MedIsoMu2_TauDMAntiMedIso_APR20_IsoDOWN_BTagSF")
   h125a13_MedIsoMu2_TauDMAntiMedIso_IsoUP = f.Get("SIG_h125a13_MedIsoMu2_TauDMAntiMedIso_APR20_IsoUP_BTagSF")
   h125a13_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = f.Get("SIG_h125a13_MedIsoMu2_TauDMAntiMedIso_APR20_BTagDOWN_BTagSF")
   h125a13_MedIsoMu2_TauDMAntiMedIso_BTagUP = f.Get("SIG_h125a13_MedIsoMu2_TauDMAntiMedIso_APR20_BTagUP_BTagSF")
   h125a13_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = f.Get("SIG_h125a13_MedIsoMu2_TauDMAntiMedIso_APR20_PileupDOWN_BTagSF")
   h125a13_MedIsoMu2_TauDMAntiMedIso_PileupUP = f.Get("SIG_h125a13_MedIsoMu2_TauDMAntiMedIso_APR20_PileupUP_BTagSF")
   h125a15_MedIsoMu2_TauDMAntiMedIso_Central = f.Get("SIG_h125a15_MedIsoMu2_TauDMAntiMedIso_APR20_Central_BTagSF")
   h125a15_MedIsoMu2_TauDMAntiMedIso_IDDOWN = f.Get("SIG_h125a15_MedIsoMu2_TauDMAntiMedIso_APR20_IDDOWN_BTagSF")
   h125a15_MedIsoMu2_TauDMAntiMedIso_IDUP = f.Get("SIG_h125a15_MedIsoMu2_TauDMAntiMedIso_APR20_IDUP_BTagSF")
   h125a15_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = f.Get("SIG_h125a15_MedIsoMu2_TauDMAntiMedIso_APR20_IsoDOWN_BTagSF")
   h125a15_MedIsoMu2_TauDMAntiMedIso_IsoUP = f.Get("SIG_h125a15_MedIsoMu2_TauDMAntiMedIso_APR20_IsoUP_BTagSF")
   h125a15_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = f.Get("SIG_h125a15_MedIsoMu2_TauDMAntiMedIso_APR20_BTagDOWN_BTagSF")
   h125a15_MedIsoMu2_TauDMAntiMedIso_BTagUP = f.Get("SIG_h125a15_MedIsoMu2_TauDMAntiMedIso_APR20_BTagUP_BTagSF")
   h125a15_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = f.Get("SIG_h125a15_MedIsoMu2_TauDMAntiMedIso_APR20_PileupDOWN_BTagSF")
   h125a15_MedIsoMu2_TauDMAntiMedIso_PileupUP = f.Get("SIG_h125a15_MedIsoMu2_TauDMAntiMedIso_APR20_PileupUP_BTagSF")
   h125a17_MedIsoMu2_TauDMAntiMedIso_Central = f.Get("SIG_h125a17_MedIsoMu2_TauDMAntiMedIso_APR20_Central_BTagSF")
   h125a17_MedIsoMu2_TauDMAntiMedIso_IDDOWN = f.Get("SIG_h125a17_MedIsoMu2_TauDMAntiMedIso_APR20_IDDOWN_BTagSF")
   h125a17_MedIsoMu2_TauDMAntiMedIso_IDUP = f.Get("SIG_h125a17_MedIsoMu2_TauDMAntiMedIso_APR20_IDUP_BTagSF")
   h125a17_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = f.Get("SIG_h125a17_MedIsoMu2_TauDMAntiMedIso_APR20_IsoDOWN_BTagSF")
   h125a17_MedIsoMu2_TauDMAntiMedIso_IsoUP = f.Get("SIG_h125a17_MedIsoMu2_TauDMAntiMedIso_APR20_IsoUP_BTagSF")
   h125a17_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = f.Get("SIG_h125a17_MedIsoMu2_TauDMAntiMedIso_APR20_BTagDOWN_BTagSF")
   h125a17_MedIsoMu2_TauDMAntiMedIso_BTagUP = f.Get("SIG_h125a17_MedIsoMu2_TauDMAntiMedIso_APR20_BTagUP_BTagSF")
   h125a17_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = f.Get("SIG_h125a17_MedIsoMu2_TauDMAntiMedIso_APR20_PileupDOWN_BTagSF")
   h125a17_MedIsoMu2_TauDMAntiMedIso_PileupUP = f.Get("SIG_h125a17_MedIsoMu2_TauDMAntiMedIso_APR20_PileupUP_BTagSF")
   h125a19_MedIsoMu2_TauDMAntiMedIso_Central = f.Get("SIG_h125a19_MedIsoMu2_TauDMAntiMedIso_APR20_Central_BTagSF")
   h125a19_MedIsoMu2_TauDMAntiMedIso_IDDOWN = f.Get("SIG_h125a19_MedIsoMu2_TauDMAntiMedIso_APR20_IDDOWN_BTagSF")
   h125a19_MedIsoMu2_TauDMAntiMedIso_IDUP = f.Get("SIG_h125a19_MedIsoMu2_TauDMAntiMedIso_APR20_IDUP_BTagSF")
   h125a19_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = f.Get("SIG_h125a19_MedIsoMu2_TauDMAntiMedIso_APR20_IsoDOWN_BTagSF")
   h125a19_MedIsoMu2_TauDMAntiMedIso_IsoUP = f.Get("SIG_h125a19_MedIsoMu2_TauDMAntiMedIso_APR20_IsoUP_BTagSF")
   h125a19_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = f.Get("SIG_h125a19_MedIsoMu2_TauDMAntiMedIso_APR20_BTagDOWN_BTagSF")
   h125a19_MedIsoMu2_TauDMAntiMedIso_BTagUP = f.Get("SIG_h125a19_MedIsoMu2_TauDMAntiMedIso_APR20_BTagUP_BTagSF")
   h125a19_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = f.Get("SIG_h125a19_MedIsoMu2_TauDMAntiMedIso_APR20_PileupDOWN_BTagSF")
   h125a19_MedIsoMu2_TauDMAntiMedIso_PileupUP = f.Get("SIG_h125a19_MedIsoMu2_TauDMAntiMedIso_APR20_PileupUP_BTagSF")
   h125a21_MedIsoMu2_TauDMAntiMedIso_Central = f.Get("SIG_h125a21_MedIsoMu2_TauDMAntiMedIso_APR20_Central_BTagSF")
   h125a21_MedIsoMu2_TauDMAntiMedIso_IDDOWN = f.Get("SIG_h125a21_MedIsoMu2_TauDMAntiMedIso_APR20_IDDOWN_BTagSF")
   h125a21_MedIsoMu2_TauDMAntiMedIso_IDUP = f.Get("SIG_h125a21_MedIsoMu2_TauDMAntiMedIso_APR20_IDUP_BTagSF")
   h125a21_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = f.Get("SIG_h125a21_MedIsoMu2_TauDMAntiMedIso_APR20_IsoDOWN_BTagSF")
   h125a21_MedIsoMu2_TauDMAntiMedIso_IsoUP = f.Get("SIG_h125a21_MedIsoMu2_TauDMAntiMedIso_APR20_IsoUP_BTagSF")
   h125a21_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = f.Get("SIG_h125a21_MedIsoMu2_TauDMAntiMedIso_APR20_BTagDOWN_BTagSF")
   h125a21_MedIsoMu2_TauDMAntiMedIso_BTagUP = f.Get("SIG_h125a21_MedIsoMu2_TauDMAntiMedIso_APR20_BTagUP_BTagSF")
   h125a21_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = f.Get("SIG_h125a21_MedIsoMu2_TauDMAntiMedIso_APR20_PileupDOWN_BTagSF")
   h125a21_MedIsoMu2_TauDMAntiMedIso_PileupUP = f.Get("SIG_h125a21_MedIsoMu2_TauDMAntiMedIso_APR20_PileupUP_BTagSF")
   h125a5_MedIsoMu2_TauDMAntiMedIso_Central = f.Get("SIG_h125a5_MedIsoMu2_TauDMAntiMedIso_APR20_Central_BTagSF")
   h125a5_MedIsoMu2_TauDMAntiMedIso_IDDOWN = f.Get("SIG_h125a5_MedIsoMu2_TauDMAntiMedIso_APR20_IDDOWN_BTagSF")
   h125a5_MedIsoMu2_TauDMAntiMedIso_IDUP = f.Get("SIG_h125a5_MedIsoMu2_TauDMAntiMedIso_APR20_IDUP_BTagSF")
   h125a5_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = f.Get("SIG_h125a5_MedIsoMu2_TauDMAntiMedIso_APR20_IsoDOWN_BTagSF")
   h125a5_MedIsoMu2_TauDMAntiMedIso_IsoUP = f.Get("SIG_h125a5_MedIsoMu2_TauDMAntiMedIso_APR20_IsoUP_BTagSF")
   h125a5_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = f.Get("SIG_h125a5_MedIsoMu2_TauDMAntiMedIso_APR20_BTagDOWN_BTagSF")
   h125a5_MedIsoMu2_TauDMAntiMedIso_BTagUP = f.Get("SIG_h125a5_MedIsoMu2_TauDMAntiMedIso_APR20_BTagUP_BTagSF")
   h125a5_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = f.Get("SIG_h125a5_MedIsoMu2_TauDMAntiMedIso_APR20_PileupDOWN_BTagSF")
   h125a5_MedIsoMu2_TauDMAntiMedIso_PileupUP = f.Get("SIG_h125a5_MedIsoMu2_TauDMAntiMedIso_APR20_PileupUP_BTagSF")
   h125a7_MedIsoMu2_TauDMAntiMedIso_Central = f.Get("SIG_h125a7_MedIsoMu2_TauDMAntiMedIso_APR20_Central_BTagSF")
   h125a7_MedIsoMu2_TauDMAntiMedIso_IDDOWN = f.Get("SIG_h125a7_MedIsoMu2_TauDMAntiMedIso_APR20_IDDOWN_BTagSF")
   h125a7_MedIsoMu2_TauDMAntiMedIso_IDUP = f.Get("SIG_h125a7_MedIsoMu2_TauDMAntiMedIso_APR20_IDUP_BTagSF")
   h125a7_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = f.Get("SIG_h125a7_MedIsoMu2_TauDMAntiMedIso_APR20_IsoDOWN_BTagSF")
   h125a7_MedIsoMu2_TauDMAntiMedIso_IsoUP = f.Get("SIG_h125a7_MedIsoMu2_TauDMAntiMedIso_APR20_IsoUP_BTagSF")
   h125a7_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = f.Get("SIG_h125a7_MedIsoMu2_TauDMAntiMedIso_APR20_BTagDOWN_BTagSF")
   h125a7_MedIsoMu2_TauDMAntiMedIso_BTagUP = f.Get("SIG_h125a7_MedIsoMu2_TauDMAntiMedIso_APR20_BTagUP_BTagSF")
   h125a7_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = f.Get("SIG_h125a7_MedIsoMu2_TauDMAntiMedIso_APR20_PileupDOWN_BTagSF")
   h125a7_MedIsoMu2_TauDMAntiMedIso_PileupUP = f.Get("SIG_h125a7_MedIsoMu2_TauDMAntiMedIso_APR20_PileupUP_BTagSF")
   h125a9_MedIsoMu2_TauDMAntiMedIso_Central = f.Get("SIG_h125a9_MedIsoMu2_TauDMAntiMedIso_APR20_Central_BTagSF")
   h125a9_MedIsoMu2_TauDMAntiMedIso_IDDOWN = f.Get("SIG_h125a9_MedIsoMu2_TauDMAntiMedIso_APR20_IDDOWN_BTagSF")
   h125a9_MedIsoMu2_TauDMAntiMedIso_IDUP = f.Get("SIG_h125a9_MedIsoMu2_TauDMAntiMedIso_APR20_IDUP_BTagSF")
   h125a9_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = f.Get("SIG_h125a9_MedIsoMu2_TauDMAntiMedIso_APR20_IsoDOWN_BTagSF")
   h125a9_MedIsoMu2_TauDMAntiMedIso_IsoUP = f.Get("SIG_h125a9_MedIsoMu2_TauDMAntiMedIso_APR20_IsoUP_BTagSF")
   h125a9_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = f.Get("SIG_h125a9_MedIsoMu2_TauDMAntiMedIso_APR20_BTagDOWN_BTagSF")
   h125a9_MedIsoMu2_TauDMAntiMedIso_BTagUP = f.Get("SIG_h125a9_MedIsoMu2_TauDMAntiMedIso_APR20_BTagUP_BTagSF")
   h125a9_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = f.Get("SIG_h125a9_MedIsoMu2_TauDMAntiMedIso_APR20_PileupDOWN_BTagSF")
   h125a9_MedIsoMu2_TauDMAntiMedIso_PileupUP = f.Get("SIG_h125a9_MedIsoMu2_TauDMAntiMedIso_APR20_PileupUP_BTagSF")
   h300a11_MedIsoMu2_TauDMAntiMedIso_Central = f.Get("SIG_h300a11_MedIsoMu2_TauDMAntiMedIso_APR20_Central_BTagSF")
   h300a11_MedIsoMu2_TauDMAntiMedIso_IDDOWN = f.Get("SIG_h300a11_MedIsoMu2_TauDMAntiMedIso_APR20_IDDOWN_BTagSF")
   h300a11_MedIsoMu2_TauDMAntiMedIso_IDUP = f.Get("SIG_h300a11_MedIsoMu2_TauDMAntiMedIso_APR20_IDUP_BTagSF")
   h300a11_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = f.Get("SIG_h300a11_MedIsoMu2_TauDMAntiMedIso_APR20_IsoDOWN_BTagSF")
   h300a11_MedIsoMu2_TauDMAntiMedIso_IsoUP = f.Get("SIG_h300a11_MedIsoMu2_TauDMAntiMedIso_APR20_IsoUP_BTagSF")
   h300a11_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = f.Get("SIG_h300a11_MedIsoMu2_TauDMAntiMedIso_APR20_BTagDOWN_BTagSF")
   h300a11_MedIsoMu2_TauDMAntiMedIso_BTagUP = f.Get("SIG_h300a11_MedIsoMu2_TauDMAntiMedIso_APR20_BTagUP_BTagSF")
   h300a11_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = f.Get("SIG_h300a11_MedIsoMu2_TauDMAntiMedIso_APR20_PileupDOWN_BTagSF")
   h300a11_MedIsoMu2_TauDMAntiMedIso_PileupUP = f.Get("SIG_h300a11_MedIsoMu2_TauDMAntiMedIso_APR20_PileupUP_BTagSF")
   h300a13_MedIsoMu2_TauDMAntiMedIso_Central = f.Get("SIG_h300a13_MedIsoMu2_TauDMAntiMedIso_APR20_Central_BTagSF")
   h300a13_MedIsoMu2_TauDMAntiMedIso_IDDOWN = f.Get("SIG_h300a13_MedIsoMu2_TauDMAntiMedIso_APR20_IDDOWN_BTagSF")
   h300a13_MedIsoMu2_TauDMAntiMedIso_IDUP = f.Get("SIG_h300a13_MedIsoMu2_TauDMAntiMedIso_APR20_IDUP_BTagSF")
   h300a13_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = f.Get("SIG_h300a13_MedIsoMu2_TauDMAntiMedIso_APR20_IsoDOWN_BTagSF")
   h300a13_MedIsoMu2_TauDMAntiMedIso_IsoUP = f.Get("SIG_h300a13_MedIsoMu2_TauDMAntiMedIso_APR20_IsoUP_BTagSF")
   h300a13_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = f.Get("SIG_h300a13_MedIsoMu2_TauDMAntiMedIso_APR20_BTagDOWN_BTagSF")
   h300a13_MedIsoMu2_TauDMAntiMedIso_BTagUP = f.Get("SIG_h300a13_MedIsoMu2_TauDMAntiMedIso_APR20_BTagUP_BTagSF")
   h300a13_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = f.Get("SIG_h300a13_MedIsoMu2_TauDMAntiMedIso_APR20_PileupDOWN_BTagSF")
   h300a13_MedIsoMu2_TauDMAntiMedIso_PileupUP = f.Get("SIG_h300a13_MedIsoMu2_TauDMAntiMedIso_APR20_PileupUP_BTagSF")
   h300a15_MedIsoMu2_TauDMAntiMedIso_Central = f.Get("SIG_h300a15_MedIsoMu2_TauDMAntiMedIso_APR20_Central_BTagSF")
   h300a15_MedIsoMu2_TauDMAntiMedIso_IDDOWN = f.Get("SIG_h300a15_MedIsoMu2_TauDMAntiMedIso_APR20_IDDOWN_BTagSF")
   h300a15_MedIsoMu2_TauDMAntiMedIso_IDUP = f.Get("SIG_h300a15_MedIsoMu2_TauDMAntiMedIso_APR20_IDUP_BTagSF")
   h300a15_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = f.Get("SIG_h300a15_MedIsoMu2_TauDMAntiMedIso_APR20_IsoDOWN_BTagSF")
   h300a15_MedIsoMu2_TauDMAntiMedIso_IsoUP = f.Get("SIG_h300a15_MedIsoMu2_TauDMAntiMedIso_APR20_IsoUP_BTagSF")
   h300a15_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = f.Get("SIG_h300a15_MedIsoMu2_TauDMAntiMedIso_APR20_BTagDOWN_BTagSF")
   h300a15_MedIsoMu2_TauDMAntiMedIso_BTagUP = f.Get("SIG_h300a15_MedIsoMu2_TauDMAntiMedIso_APR20_BTagUP_BTagSF")
   h300a15_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = f.Get("SIG_h300a15_MedIsoMu2_TauDMAntiMedIso_APR20_PileupDOWN_BTagSF")
   h300a15_MedIsoMu2_TauDMAntiMedIso_PileupUP = f.Get("SIG_h300a15_MedIsoMu2_TauDMAntiMedIso_APR20_PileupUP_BTagSF")
   h300a17_MedIsoMu2_TauDMAntiMedIso_Central = f.Get("SIG_h300a17_MedIsoMu2_TauDMAntiMedIso_APR20_Central_BTagSF")
   h300a17_MedIsoMu2_TauDMAntiMedIso_IDDOWN = f.Get("SIG_h300a17_MedIsoMu2_TauDMAntiMedIso_APR20_IDDOWN_BTagSF")
   h300a17_MedIsoMu2_TauDMAntiMedIso_IDUP = f.Get("SIG_h300a17_MedIsoMu2_TauDMAntiMedIso_APR20_IDUP_BTagSF")
   h300a17_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = f.Get("SIG_h300a17_MedIsoMu2_TauDMAntiMedIso_APR20_IsoDOWN_BTagSF")
   h300a17_MedIsoMu2_TauDMAntiMedIso_IsoUP = f.Get("SIG_h300a17_MedIsoMu2_TauDMAntiMedIso_APR20_IsoUP_BTagSF")
   h300a17_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = f.Get("SIG_h300a17_MedIsoMu2_TauDMAntiMedIso_APR20_BTagDOWN_BTagSF")
   h300a17_MedIsoMu2_TauDMAntiMedIso_BTagUP = f.Get("SIG_h300a17_MedIsoMu2_TauDMAntiMedIso_APR20_BTagUP_BTagSF")
   h300a17_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = f.Get("SIG_h300a17_MedIsoMu2_TauDMAntiMedIso_APR20_PileupDOWN_BTagSF")
   h300a17_MedIsoMu2_TauDMAntiMedIso_PileupUP = f.Get("SIG_h300a17_MedIsoMu2_TauDMAntiMedIso_APR20_PileupUP_BTagSF")
   h300a19_MedIsoMu2_TauDMAntiMedIso_Central = f.Get("SIG_h300a19_MedIsoMu2_TauDMAntiMedIso_APR20_Central_BTagSF")
   h300a19_MedIsoMu2_TauDMAntiMedIso_IDDOWN = f.Get("SIG_h300a19_MedIsoMu2_TauDMAntiMedIso_APR20_IDDOWN_BTagSF")
   h300a19_MedIsoMu2_TauDMAntiMedIso_IDUP = f.Get("SIG_h300a19_MedIsoMu2_TauDMAntiMedIso_APR20_IDUP_BTagSF")
   h300a19_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = f.Get("SIG_h300a19_MedIsoMu2_TauDMAntiMedIso_APR20_IsoDOWN_BTagSF")
   h300a19_MedIsoMu2_TauDMAntiMedIso_IsoUP = f.Get("SIG_h300a19_MedIsoMu2_TauDMAntiMedIso_APR20_IsoUP_BTagSF")
   h300a19_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = f.Get("SIG_h300a19_MedIsoMu2_TauDMAntiMedIso_APR20_BTagDOWN_BTagSF")
   h300a19_MedIsoMu2_TauDMAntiMedIso_BTagUP = f.Get("SIG_h300a19_MedIsoMu2_TauDMAntiMedIso_APR20_BTagUP_BTagSF")
   h300a19_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = f.Get("SIG_h300a19_MedIsoMu2_TauDMAntiMedIso_APR20_PileupDOWN_BTagSF")
   h300a19_MedIsoMu2_TauDMAntiMedIso_PileupUP = f.Get("SIG_h300a19_MedIsoMu2_TauDMAntiMedIso_APR20_PileupUP_BTagSF")
   h300a21_MedIsoMu2_TauDMAntiMedIso_Central = f.Get("SIG_h300a21_MedIsoMu2_TauDMAntiMedIso_APR20_Central_BTagSF")
   h300a21_MedIsoMu2_TauDMAntiMedIso_IDDOWN = f.Get("SIG_h300a21_MedIsoMu2_TauDMAntiMedIso_APR20_IDDOWN_BTagSF")
   h300a21_MedIsoMu2_TauDMAntiMedIso_IDUP = f.Get("SIG_h300a21_MedIsoMu2_TauDMAntiMedIso_APR20_IDUP_BTagSF")
   h300a21_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = f.Get("SIG_h300a21_MedIsoMu2_TauDMAntiMedIso_APR20_IsoDOWN_BTagSF")
   h300a21_MedIsoMu2_TauDMAntiMedIso_IsoUP = f.Get("SIG_h300a21_MedIsoMu2_TauDMAntiMedIso_APR20_IsoUP_BTagSF")
   h300a21_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = f.Get("SIG_h300a21_MedIsoMu2_TauDMAntiMedIso_APR20_BTagDOWN_BTagSF")
   h300a21_MedIsoMu2_TauDMAntiMedIso_BTagUP = f.Get("SIG_h300a21_MedIsoMu2_TauDMAntiMedIso_APR20_BTagUP_BTagSF")
   h300a21_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = f.Get("SIG_h300a21_MedIsoMu2_TauDMAntiMedIso_APR20_PileupDOWN_BTagSF")
   h300a21_MedIsoMu2_TauDMAntiMedIso_PileupUP = f.Get("SIG_h300a21_MedIsoMu2_TauDMAntiMedIso_APR20_PileupUP_BTagSF")
   h300a5_MedIsoMu2_TauDMAntiMedIso_Central = f.Get("SIG_h300a5_MedIsoMu2_TauDMAntiMedIso_APR20_Central_BTagSF")
   h300a5_MedIsoMu2_TauDMAntiMedIso_IDDOWN = f.Get("SIG_h300a5_MedIsoMu2_TauDMAntiMedIso_APR20_IDDOWN_BTagSF")
   h300a5_MedIsoMu2_TauDMAntiMedIso_IDUP = f.Get("SIG_h300a5_MedIsoMu2_TauDMAntiMedIso_APR20_IDUP_BTagSF")
   h300a5_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = f.Get("SIG_h300a5_MedIsoMu2_TauDMAntiMedIso_APR20_IsoDOWN_BTagSF")
   h300a5_MedIsoMu2_TauDMAntiMedIso_IsoUP = f.Get("SIG_h300a5_MedIsoMu2_TauDMAntiMedIso_APR20_IsoUP_BTagSF")
   h300a5_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = f.Get("SIG_h300a5_MedIsoMu2_TauDMAntiMedIso_APR20_BTagDOWN_BTagSF")
   h300a5_MedIsoMu2_TauDMAntiMedIso_BTagUP = f.Get("SIG_h300a5_MedIsoMu2_TauDMAntiMedIso_APR20_BTagUP_BTagSF")
   h300a5_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = f.Get("SIG_h300a5_MedIsoMu2_TauDMAntiMedIso_APR20_PileupDOWN_BTagSF")
   h300a5_MedIsoMu2_TauDMAntiMedIso_PileupUP = f.Get("SIG_h300a5_MedIsoMu2_TauDMAntiMedIso_APR20_PileupUP_BTagSF")
   h300a7_MedIsoMu2_TauDMAntiMedIso_Central = f.Get("SIG_h300a7_MedIsoMu2_TauDMAntiMedIso_APR20_Central_BTagSF")
   h300a7_MedIsoMu2_TauDMAntiMedIso_IDDOWN = f.Get("SIG_h300a7_MedIsoMu2_TauDMAntiMedIso_APR20_IDDOWN_BTagSF")
   h300a7_MedIsoMu2_TauDMAntiMedIso_IDUP = f.Get("SIG_h300a7_MedIsoMu2_TauDMAntiMedIso_APR20_IDUP_BTagSF")
   h300a7_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = f.Get("SIG_h300a7_MedIsoMu2_TauDMAntiMedIso_APR20_IsoDOWN_BTagSF")
   h300a7_MedIsoMu2_TauDMAntiMedIso_IsoUP = f.Get("SIG_h300a7_MedIsoMu2_TauDMAntiMedIso_APR20_IsoUP_BTagSF")
   h300a7_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = f.Get("SIG_h300a7_MedIsoMu2_TauDMAntiMedIso_APR20_BTagDOWN_BTagSF")
   h300a7_MedIsoMu2_TauDMAntiMedIso_BTagUP = f.Get("SIG_h300a7_MedIsoMu2_TauDMAntiMedIso_APR20_BTagUP_BTagSF")
   h300a7_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = f.Get("SIG_h300a7_MedIsoMu2_TauDMAntiMedIso_APR20_PileupDOWN_BTagSF")
   h300a7_MedIsoMu2_TauDMAntiMedIso_PileupUP = f.Get("SIG_h300a7_MedIsoMu2_TauDMAntiMedIso_APR20_PileupUP_BTagSF")
   h300a9_MedIsoMu2_TauDMAntiMedIso_Central = f.Get("SIG_h300a9_MedIsoMu2_TauDMAntiMedIso_APR20_Central_BTagSF")
   h300a9_MedIsoMu2_TauDMAntiMedIso_IDDOWN = f.Get("SIG_h300a9_MedIsoMu2_TauDMAntiMedIso_APR20_IDDOWN_BTagSF")
   h300a9_MedIsoMu2_TauDMAntiMedIso_IDUP = f.Get("SIG_h300a9_MedIsoMu2_TauDMAntiMedIso_APR20_IDUP_BTagSF")
   h300a9_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = f.Get("SIG_h300a9_MedIsoMu2_TauDMAntiMedIso_APR20_IsoDOWN_BTagSF")
   h300a9_MedIsoMu2_TauDMAntiMedIso_IsoUP = f.Get("SIG_h300a9_MedIsoMu2_TauDMAntiMedIso_APR20_IsoUP_BTagSF")
   h300a9_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = f.Get("SIG_h300a9_MedIsoMu2_TauDMAntiMedIso_APR20_BTagDOWN_BTagSF")
   h300a9_MedIsoMu2_TauDMAntiMedIso_BTagUP = f.Get("SIG_h300a9_MedIsoMu2_TauDMAntiMedIso_APR20_BTagUP_BTagSF")
   h300a9_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = f.Get("SIG_h300a9_MedIsoMu2_TauDMAntiMedIso_APR20_PileupDOWN_BTagSF")
   h300a9_MedIsoMu2_TauDMAntiMedIso_PileupUP = f.Get("SIG_h300a9_MedIsoMu2_TauDMAntiMedIso_APR20_PileupUP_BTagSF")
   h750a11_MedIsoMu2_TauDMAntiMedIso_Central = f.Get("SIG_h750a11_MedIsoMu2_TauDMAntiMedIso_APR20_Central_BTagSF")
   h750a11_MedIsoMu2_TauDMAntiMedIso_IDDOWN = f.Get("SIG_h750a11_MedIsoMu2_TauDMAntiMedIso_APR20_IDDOWN_BTagSF")
   h750a11_MedIsoMu2_TauDMAntiMedIso_IDUP = f.Get("SIG_h750a11_MedIsoMu2_TauDMAntiMedIso_APR20_IDUP_BTagSF")
   h750a11_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = f.Get("SIG_h750a11_MedIsoMu2_TauDMAntiMedIso_APR20_IsoDOWN_BTagSF")
   h750a11_MedIsoMu2_TauDMAntiMedIso_IsoUP = f.Get("SIG_h750a11_MedIsoMu2_TauDMAntiMedIso_APR20_IsoUP_BTagSF")
   h750a11_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = f.Get("SIG_h750a11_MedIsoMu2_TauDMAntiMedIso_APR20_BTagDOWN_BTagSF")
   h750a11_MedIsoMu2_TauDMAntiMedIso_BTagUP = f.Get("SIG_h750a11_MedIsoMu2_TauDMAntiMedIso_APR20_BTagUP_BTagSF")
   h750a11_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = f.Get("SIG_h750a11_MedIsoMu2_TauDMAntiMedIso_APR20_PileupDOWN_BTagSF")
   h750a11_MedIsoMu2_TauDMAntiMedIso_PileupUP = f.Get("SIG_h750a11_MedIsoMu2_TauDMAntiMedIso_APR20_PileupUP_BTagSF")
   h750a13_MedIsoMu2_TauDMAntiMedIso_Central = f.Get("SIG_h750a13_MedIsoMu2_TauDMAntiMedIso_APR20_Central_BTagSF")
   h750a13_MedIsoMu2_TauDMAntiMedIso_IDDOWN = f.Get("SIG_h750a13_MedIsoMu2_TauDMAntiMedIso_APR20_IDDOWN_BTagSF")
   h750a13_MedIsoMu2_TauDMAntiMedIso_IDUP = f.Get("SIG_h750a13_MedIsoMu2_TauDMAntiMedIso_APR20_IDUP_BTagSF")
   h750a13_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = f.Get("SIG_h750a13_MedIsoMu2_TauDMAntiMedIso_APR20_IsoDOWN_BTagSF")
   h750a13_MedIsoMu2_TauDMAntiMedIso_IsoUP = f.Get("SIG_h750a13_MedIsoMu2_TauDMAntiMedIso_APR20_IsoUP_BTagSF")
   h750a13_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = f.Get("SIG_h750a13_MedIsoMu2_TauDMAntiMedIso_APR20_BTagDOWN_BTagSF")
   h750a13_MedIsoMu2_TauDMAntiMedIso_BTagUP = f.Get("SIG_h750a13_MedIsoMu2_TauDMAntiMedIso_APR20_BTagUP_BTagSF")
   h750a13_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = f.Get("SIG_h750a13_MedIsoMu2_TauDMAntiMedIso_APR20_PileupDOWN_BTagSF")
   h750a13_MedIsoMu2_TauDMAntiMedIso_PileupUP = f.Get("SIG_h750a13_MedIsoMu2_TauDMAntiMedIso_APR20_PileupUP_BTagSF")
   h750a15_MedIsoMu2_TauDMAntiMedIso_Central = f.Get("SIG_h750a15_MedIsoMu2_TauDMAntiMedIso_APR20_Central_BTagSF")
   h750a15_MedIsoMu2_TauDMAntiMedIso_IDDOWN = f.Get("SIG_h750a15_MedIsoMu2_TauDMAntiMedIso_APR20_IDDOWN_BTagSF")
   h750a15_MedIsoMu2_TauDMAntiMedIso_IDUP = f.Get("SIG_h750a15_MedIsoMu2_TauDMAntiMedIso_APR20_IDUP_BTagSF")
   h750a15_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = f.Get("SIG_h750a15_MedIsoMu2_TauDMAntiMedIso_APR20_IsoDOWN_BTagSF")
   h750a15_MedIsoMu2_TauDMAntiMedIso_IsoUP = f.Get("SIG_h750a15_MedIsoMu2_TauDMAntiMedIso_APR20_IsoUP_BTagSF")
   h750a15_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = f.Get("SIG_h750a15_MedIsoMu2_TauDMAntiMedIso_APR20_BTagDOWN_BTagSF")
   h750a15_MedIsoMu2_TauDMAntiMedIso_BTagUP = f.Get("SIG_h750a15_MedIsoMu2_TauDMAntiMedIso_APR20_BTagUP_BTagSF")
   h750a15_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = f.Get("SIG_h750a15_MedIsoMu2_TauDMAntiMedIso_APR20_PileupDOWN_BTagSF")
   h750a15_MedIsoMu2_TauDMAntiMedIso_PileupUP = f.Get("SIG_h750a15_MedIsoMu2_TauDMAntiMedIso_APR20_PileupUP_BTagSF")
   h750a17_MedIsoMu2_TauDMAntiMedIso_Central = f.Get("SIG_h750a17_MedIsoMu2_TauDMAntiMedIso_APR20_Central_BTagSF")
   h750a17_MedIsoMu2_TauDMAntiMedIso_IDDOWN = f.Get("SIG_h750a17_MedIsoMu2_TauDMAntiMedIso_APR20_IDDOWN_BTagSF")
   h750a17_MedIsoMu2_TauDMAntiMedIso_IDUP = f.Get("SIG_h750a17_MedIsoMu2_TauDMAntiMedIso_APR20_IDUP_BTagSF")
   h750a17_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = f.Get("SIG_h750a17_MedIsoMu2_TauDMAntiMedIso_APR20_IsoDOWN_BTagSF")
   h750a17_MedIsoMu2_TauDMAntiMedIso_IsoUP = f.Get("SIG_h750a17_MedIsoMu2_TauDMAntiMedIso_APR20_IsoUP_BTagSF")
   h750a17_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = f.Get("SIG_h750a17_MedIsoMu2_TauDMAntiMedIso_APR20_BTagDOWN_BTagSF")
   h750a17_MedIsoMu2_TauDMAntiMedIso_BTagUP = f.Get("SIG_h750a17_MedIsoMu2_TauDMAntiMedIso_APR20_BTagUP_BTagSF")
   h750a17_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = f.Get("SIG_h750a17_MedIsoMu2_TauDMAntiMedIso_APR20_PileupDOWN_BTagSF")
   h750a17_MedIsoMu2_TauDMAntiMedIso_PileupUP = f.Get("SIG_h750a17_MedIsoMu2_TauDMAntiMedIso_APR20_PileupUP_BTagSF")
   h750a19_MedIsoMu2_TauDMAntiMedIso_Central = f.Get("SIG_h750a19_MedIsoMu2_TauDMAntiMedIso_APR20_Central_BTagSF")
   h750a19_MedIsoMu2_TauDMAntiMedIso_IDDOWN = f.Get("SIG_h750a19_MedIsoMu2_TauDMAntiMedIso_APR20_IDDOWN_BTagSF")
   h750a19_MedIsoMu2_TauDMAntiMedIso_IDUP = f.Get("SIG_h750a19_MedIsoMu2_TauDMAntiMedIso_APR20_IDUP_BTagSF")
   h750a19_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = f.Get("SIG_h750a19_MedIsoMu2_TauDMAntiMedIso_APR20_IsoDOWN_BTagSF")
   h750a19_MedIsoMu2_TauDMAntiMedIso_IsoUP = f.Get("SIG_h750a19_MedIsoMu2_TauDMAntiMedIso_APR20_IsoUP_BTagSF")
   h750a19_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = f.Get("SIG_h750a19_MedIsoMu2_TauDMAntiMedIso_APR20_BTagDOWN_BTagSF")
   h750a19_MedIsoMu2_TauDMAntiMedIso_BTagUP = f.Get("SIG_h750a19_MedIsoMu2_TauDMAntiMedIso_APR20_BTagUP_BTagSF")
   h750a19_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = f.Get("SIG_h750a19_MedIsoMu2_TauDMAntiMedIso_APR20_PileupDOWN_BTagSF")
   h750a19_MedIsoMu2_TauDMAntiMedIso_PileupUP = f.Get("SIG_h750a19_MedIsoMu2_TauDMAntiMedIso_APR20_PileupUP_BTagSF")
   h750a21_MedIsoMu2_TauDMAntiMedIso_Central = f.Get("SIG_h750a21_MedIsoMu2_TauDMAntiMedIso_APR20_Central_BTagSF")
   h750a21_MedIsoMu2_TauDMAntiMedIso_IDDOWN = f.Get("SIG_h750a21_MedIsoMu2_TauDMAntiMedIso_APR20_IDDOWN_BTagSF")
   h750a21_MedIsoMu2_TauDMAntiMedIso_IDUP = f.Get("SIG_h750a21_MedIsoMu2_TauDMAntiMedIso_APR20_IDUP_BTagSF")
   h750a21_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = f.Get("SIG_h750a21_MedIsoMu2_TauDMAntiMedIso_APR20_IsoDOWN_BTagSF")
   h750a21_MedIsoMu2_TauDMAntiMedIso_IsoUP = f.Get("SIG_h750a21_MedIsoMu2_TauDMAntiMedIso_APR20_IsoUP_BTagSF")
   h750a21_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = f.Get("SIG_h750a21_MedIsoMu2_TauDMAntiMedIso_APR20_BTagDOWN_BTagSF")
   h750a21_MedIsoMu2_TauDMAntiMedIso_BTagUP = f.Get("SIG_h750a21_MedIsoMu2_TauDMAntiMedIso_APR20_BTagUP_BTagSF")
   h750a21_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = f.Get("SIG_h750a21_MedIsoMu2_TauDMAntiMedIso_APR20_PileupDOWN_BTagSF")
   h750a21_MedIsoMu2_TauDMAntiMedIso_PileupUP = f.Get("SIG_h750a21_MedIsoMu2_TauDMAntiMedIso_APR20_PileupUP_BTagSF")
   h750a5_MedIsoMu2_TauDMAntiMedIso_Central = f.Get("SIG_h750a5_MedIsoMu2_TauDMAntiMedIso_APR20_Central_BTagSF")
   h750a5_MedIsoMu2_TauDMAntiMedIso_IDDOWN = f.Get("SIG_h750a5_MedIsoMu2_TauDMAntiMedIso_APR20_IDDOWN_BTagSF")
   h750a5_MedIsoMu2_TauDMAntiMedIso_IDUP = f.Get("SIG_h750a5_MedIsoMu2_TauDMAntiMedIso_APR20_IDUP_BTagSF")
   h750a5_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = f.Get("SIG_h750a5_MedIsoMu2_TauDMAntiMedIso_APR20_IsoDOWN_BTagSF")
   h750a5_MedIsoMu2_TauDMAntiMedIso_IsoUP = f.Get("SIG_h750a5_MedIsoMu2_TauDMAntiMedIso_APR20_IsoUP_BTagSF")
   h750a5_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = f.Get("SIG_h750a5_MedIsoMu2_TauDMAntiMedIso_APR20_BTagDOWN_BTagSF")
   h750a5_MedIsoMu2_TauDMAntiMedIso_BTagUP = f.Get("SIG_h750a5_MedIsoMu2_TauDMAntiMedIso_APR20_BTagUP_BTagSF")
   h750a5_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = f.Get("SIG_h750a5_MedIsoMu2_TauDMAntiMedIso_APR20_PileupDOWN_BTagSF")
   h750a5_MedIsoMu2_TauDMAntiMedIso_PileupUP = f.Get("SIG_h750a5_MedIsoMu2_TauDMAntiMedIso_APR20_PileupUP_BTagSF")
   h750a7_MedIsoMu2_TauDMAntiMedIso_Central = f.Get("SIG_h750a7_MedIsoMu2_TauDMAntiMedIso_APR20_Central_BTagSF")
   h750a7_MedIsoMu2_TauDMAntiMedIso_IDDOWN = f.Get("SIG_h750a7_MedIsoMu2_TauDMAntiMedIso_APR20_IDDOWN_BTagSF")
   h750a7_MedIsoMu2_TauDMAntiMedIso_IDUP = f.Get("SIG_h750a7_MedIsoMu2_TauDMAntiMedIso_APR20_IDUP_BTagSF")
   h750a7_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = f.Get("SIG_h750a7_MedIsoMu2_TauDMAntiMedIso_APR20_IsoDOWN_BTagSF")
   h750a7_MedIsoMu2_TauDMAntiMedIso_IsoUP = f.Get("SIG_h750a7_MedIsoMu2_TauDMAntiMedIso_APR20_IsoUP_BTagSF")
   h750a7_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = f.Get("SIG_h750a7_MedIsoMu2_TauDMAntiMedIso_APR20_BTagDOWN_BTagSF")
   h750a7_MedIsoMu2_TauDMAntiMedIso_BTagUP = f.Get("SIG_h750a7_MedIsoMu2_TauDMAntiMedIso_APR20_BTagUP_BTagSF")
   h750a7_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = f.Get("SIG_h750a7_MedIsoMu2_TauDMAntiMedIso_APR20_PileupDOWN_BTagSF")
   h750a7_MedIsoMu2_TauDMAntiMedIso_PileupUP = f.Get("SIG_h750a7_MedIsoMu2_TauDMAntiMedIso_APR20_PileupUP_BTagSF")
   h750a9_MedIsoMu2_TauDMAntiMedIso_Central = f.Get("SIG_h750a9_MedIsoMu2_TauDMAntiMedIso_APR20_Central_BTagSF")
   h750a9_MedIsoMu2_TauDMAntiMedIso_IDDOWN = f.Get("SIG_h750a9_MedIsoMu2_TauDMAntiMedIso_APR20_IDDOWN_BTagSF")
   h750a9_MedIsoMu2_TauDMAntiMedIso_IDUP = f.Get("SIG_h750a9_MedIsoMu2_TauDMAntiMedIso_APR20_IDUP_BTagSF")
   h750a9_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = f.Get("SIG_h750a9_MedIsoMu2_TauDMAntiMedIso_APR20_IsoDOWN_BTagSF")
   h750a9_MedIsoMu2_TauDMAntiMedIso_IsoUP = f.Get("SIG_h750a9_MedIsoMu2_TauDMAntiMedIso_APR20_IsoUP_BTagSF")
   h750a9_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = f.Get("SIG_h750a9_MedIsoMu2_TauDMAntiMedIso_APR20_BTagDOWN_BTagSF")
   h750a9_MedIsoMu2_TauDMAntiMedIso_BTagUP = f.Get("SIG_h750a9_MedIsoMu2_TauDMAntiMedIso_APR20_BTagUP_BTagSF")
   h750a9_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = f.Get("SIG_h750a9_MedIsoMu2_TauDMAntiMedIso_APR20_PileupDOWN_BTagSF")
   h750a9_MedIsoMu2_TauDMAntiMedIso_PileupUP = f.Get("SIG_h750a9_MedIsoMu2_TauDMAntiMedIso_APR20_PileupUP_BTagSF")

#   h125a11_MedIsoMu2_TauDMAntiMedIso_Central = ScaleRooDataSets(h125a11_MedIsoMu2_TauDMAntiMedIso_Central, scale=.001)
#   h125a11_MedIsoMu2_TauDMAntiMedIso_IDDOWN = ScaleRooDataSets(h125a11_MedIsoMu2_TauDMAntiMedIso_IDDOWN, scale=.001)
#   h125a11_MedIsoMu2_TauDMAntiMedIso_IDUP = ScaleRooDataSets(h125a11_MedIsoMu2_TauDMAntiMedIso_IDUP, scale=.001)
#   h125a11_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = ScaleRooDataSets(h125a11_MedIsoMu2_TauDMAntiMedIso_IsoDOWN, scale=.001)
#   h125a11_MedIsoMu2_TauDMAntiMedIso_IsoUP = ScaleRooDataSets(h125a11_MedIsoMu2_TauDMAntiMedIso_IsoUP, scale=.001)
#   h125a11_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = ScaleRooDataSets(h125a11_MedIsoMu2_TauDMAntiMedIso_BTagDOWN, scale=.001)
#   h125a11_MedIsoMu2_TauDMAntiMedIso_BTagUP = ScaleRooDataSets(h125a11_MedIsoMu2_TauDMAntiMedIso_BTagUP, scale=.001)
#   h125a11_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = ScaleRooDataSets(h125a11_MedIsoMu2_TauDMAntiMedIso_PileupDOWN, scale=.001)
#   h125a11_MedIsoMu2_TauDMAntiMedIso_PileupUP = ScaleRooDataSets(h125a11_MedIsoMu2_TauDMAntiMedIso_PileupUP, scale=.001)
#   h125a13_MedIsoMu2_TauDMAntiMedIso_Central = ScaleRooDataSets(h125a13_MedIsoMu2_TauDMAntiMedIso_Central, scale=.001)
#   h125a13_MedIsoMu2_TauDMAntiMedIso_IDDOWN = ScaleRooDataSets(h125a13_MedIsoMu2_TauDMAntiMedIso_IDDOWN, scale=.001)
#   h125a13_MedIsoMu2_TauDMAntiMedIso_IDUP = ScaleRooDataSets(h125a13_MedIsoMu2_TauDMAntiMedIso_IDUP, scale=.001)
#   h125a13_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = ScaleRooDataSets(h125a13_MedIsoMu2_TauDMAntiMedIso_IsoDOWN, scale=.001)
#   h125a13_MedIsoMu2_TauDMAntiMedIso_IsoUP = ScaleRooDataSets(h125a13_MedIsoMu2_TauDMAntiMedIso_IsoUP, scale=.001)
#   h125a13_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = ScaleRooDataSets(h125a13_MedIsoMu2_TauDMAntiMedIso_BTagDOWN, scale=.001)
#   h125a13_MedIsoMu2_TauDMAntiMedIso_BTagUP = ScaleRooDataSets(h125a13_MedIsoMu2_TauDMAntiMedIso_BTagUP, scale=.001)
#   h125a13_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = ScaleRooDataSets(h125a13_MedIsoMu2_TauDMAntiMedIso_PileupDOWN, scale=.001)
#   h125a13_MedIsoMu2_TauDMAntiMedIso_PileupUP = ScaleRooDataSets(h125a13_MedIsoMu2_TauDMAntiMedIso_PileupUP, scale=.001)
#   h125a15_MedIsoMu2_TauDMAntiMedIso_Central = ScaleRooDataSets(h125a15_MedIsoMu2_TauDMAntiMedIso_Central, scale=.001)
#   h125a15_MedIsoMu2_TauDMAntiMedIso_IDDOWN = ScaleRooDataSets(h125a15_MedIsoMu2_TauDMAntiMedIso_IDDOWN, scale=.001)
#   h125a15_MedIsoMu2_TauDMAntiMedIso_IDUP = ScaleRooDataSets(h125a15_MedIsoMu2_TauDMAntiMedIso_IDUP, scale=.001)
#   h125a15_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = ScaleRooDataSets(h125a15_MedIsoMu2_TauDMAntiMedIso_IsoDOWN, scale=.001)
#   h125a15_MedIsoMu2_TauDMAntiMedIso_IsoUP = ScaleRooDataSets(h125a15_MedIsoMu2_TauDMAntiMedIso_IsoUP, scale=.001)
#   h125a15_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = ScaleRooDataSets(h125a15_MedIsoMu2_TauDMAntiMedIso_BTagDOWN, scale=.001)
#   h125a15_MedIsoMu2_TauDMAntiMedIso_BTagUP = ScaleRooDataSets(h125a15_MedIsoMu2_TauDMAntiMedIso_BTagUP, scale=.001)
#   h125a15_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = ScaleRooDataSets(h125a15_MedIsoMu2_TauDMAntiMedIso_PileupDOWN, scale=.001)
#   h125a15_MedIsoMu2_TauDMAntiMedIso_PileupUP = ScaleRooDataSets(h125a15_MedIsoMu2_TauDMAntiMedIso_PileupUP, scale=.001)
#   h125a17_MedIsoMu2_TauDMAntiMedIso_Central = ScaleRooDataSets(h125a17_MedIsoMu2_TauDMAntiMedIso_Central, scale=.001)
#   h125a17_MedIsoMu2_TauDMAntiMedIso_IDDOWN = ScaleRooDataSets(h125a17_MedIsoMu2_TauDMAntiMedIso_IDDOWN, scale=.001)
#   h125a17_MedIsoMu2_TauDMAntiMedIso_IDUP = ScaleRooDataSets(h125a17_MedIsoMu2_TauDMAntiMedIso_IDUP, scale=.001)
#   h125a17_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = ScaleRooDataSets(h125a17_MedIsoMu2_TauDMAntiMedIso_IsoDOWN, scale=.001)
#   h125a17_MedIsoMu2_TauDMAntiMedIso_IsoUP = ScaleRooDataSets(h125a17_MedIsoMu2_TauDMAntiMedIso_IsoUP, scale=.001)
#   h125a17_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = ScaleRooDataSets(h125a17_MedIsoMu2_TauDMAntiMedIso_BTagDOWN, scale=.001)
#   h125a17_MedIsoMu2_TauDMAntiMedIso_BTagUP = ScaleRooDataSets(h125a17_MedIsoMu2_TauDMAntiMedIso_BTagUP, scale=.001)
#   h125a17_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = ScaleRooDataSets(h125a17_MedIsoMu2_TauDMAntiMedIso_PileupDOWN, scale=.001)
#   h125a17_MedIsoMu2_TauDMAntiMedIso_PileupUP = ScaleRooDataSets(h125a17_MedIsoMu2_TauDMAntiMedIso_PileupUP, scale=.001)
#   h125a19_MedIsoMu2_TauDMAntiMedIso_Central = ScaleRooDataSets(h125a19_MedIsoMu2_TauDMAntiMedIso_Central, scale=.001)
#   h125a19_MedIsoMu2_TauDMAntiMedIso_IDDOWN = ScaleRooDataSets(h125a19_MedIsoMu2_TauDMAntiMedIso_IDDOWN, scale=.001)
#   h125a19_MedIsoMu2_TauDMAntiMedIso_IDUP = ScaleRooDataSets(h125a19_MedIsoMu2_TauDMAntiMedIso_IDUP, scale=.001)
#   h125a19_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = ScaleRooDataSets(h125a19_MedIsoMu2_TauDMAntiMedIso_IsoDOWN, scale=.001)
#   h125a19_MedIsoMu2_TauDMAntiMedIso_IsoUP = ScaleRooDataSets(h125a19_MedIsoMu2_TauDMAntiMedIso_IsoUP, scale=.001)
#   h125a19_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = ScaleRooDataSets(h125a19_MedIsoMu2_TauDMAntiMedIso_BTagDOWN, scale=.001)
#   h125a19_MedIsoMu2_TauDMAntiMedIso_BTagUP = ScaleRooDataSets(h125a19_MedIsoMu2_TauDMAntiMedIso_BTagUP, scale=.001)
#   h125a19_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = ScaleRooDataSets(h125a19_MedIsoMu2_TauDMAntiMedIso_PileupDOWN, scale=.001)
#   h125a19_MedIsoMu2_TauDMAntiMedIso_PileupUP = ScaleRooDataSets(h125a19_MedIsoMu2_TauDMAntiMedIso_PileupUP, scale=.001)
#   h125a21_MedIsoMu2_TauDMAntiMedIso_Central = ScaleRooDataSets(h125a21_MedIsoMu2_TauDMAntiMedIso_Central, scale=.001)
#   h125a21_MedIsoMu2_TauDMAntiMedIso_IDDOWN = ScaleRooDataSets(h125a21_MedIsoMu2_TauDMAntiMedIso_IDDOWN, scale=.001)
#   h125a21_MedIsoMu2_TauDMAntiMedIso_IDUP = ScaleRooDataSets(h125a21_MedIsoMu2_TauDMAntiMedIso_IDUP, scale=.001)
#   h125a21_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = ScaleRooDataSets(h125a21_MedIsoMu2_TauDMAntiMedIso_IsoDOWN, scale=.001)
#   h125a21_MedIsoMu2_TauDMAntiMedIso_IsoUP = ScaleRooDataSets(h125a21_MedIsoMu2_TauDMAntiMedIso_IsoUP, scale=.001)
#   h125a21_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = ScaleRooDataSets(h125a21_MedIsoMu2_TauDMAntiMedIso_BTagDOWN, scale=.001)
#   h125a21_MedIsoMu2_TauDMAntiMedIso_BTagUP = ScaleRooDataSets(h125a21_MedIsoMu2_TauDMAntiMedIso_BTagUP, scale=.001)
#   h125a21_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = ScaleRooDataSets(h125a21_MedIsoMu2_TauDMAntiMedIso_PileupDOWN, scale=.001)
#   h125a21_MedIsoMu2_TauDMAntiMedIso_PileupUP = ScaleRooDataSets(h125a21_MedIsoMu2_TauDMAntiMedIso_PileupUP, scale=.001)
#   h125a5_MedIsoMu2_TauDMAntiMedIso_Central = ScaleRooDataSets(h125a5_MedIsoMu2_TauDMAntiMedIso_Central, scale=.001)
#   h125a5_MedIsoMu2_TauDMAntiMedIso_IDDOWN = ScaleRooDataSets(h125a5_MedIsoMu2_TauDMAntiMedIso_IDDOWN, scale=.001)
#   h125a5_MedIsoMu2_TauDMAntiMedIso_IDUP = ScaleRooDataSets(h125a5_MedIsoMu2_TauDMAntiMedIso_IDUP, scale=.001)
#   h125a5_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = ScaleRooDataSets(h125a5_MedIsoMu2_TauDMAntiMedIso_IsoDOWN, scale=.001)
#   h125a5_MedIsoMu2_TauDMAntiMedIso_IsoUP = ScaleRooDataSets(h125a5_MedIsoMu2_TauDMAntiMedIso_IsoUP, scale=.001)
#   h125a5_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = ScaleRooDataSets(h125a5_MedIsoMu2_TauDMAntiMedIso_BTagDOWN, scale=.001)
#   h125a5_MedIsoMu2_TauDMAntiMedIso_BTagUP = ScaleRooDataSets(h125a5_MedIsoMu2_TauDMAntiMedIso_BTagUP, scale=.001)
#   h125a5_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = ScaleRooDataSets(h125a5_MedIsoMu2_TauDMAntiMedIso_PileupDOWN, scale=.001)
#   h125a5_MedIsoMu2_TauDMAntiMedIso_PileupUP = ScaleRooDataSets(h125a5_MedIsoMu2_TauDMAntiMedIso_PileupUP, scale=.001)
#   h125a7_MedIsoMu2_TauDMAntiMedIso_Central = ScaleRooDataSets(h125a7_MedIsoMu2_TauDMAntiMedIso_Central, scale=.001)
#   h125a7_MedIsoMu2_TauDMAntiMedIso_IDDOWN = ScaleRooDataSets(h125a7_MedIsoMu2_TauDMAntiMedIso_IDDOWN, scale=.001)
#   h125a7_MedIsoMu2_TauDMAntiMedIso_IDUP = ScaleRooDataSets(h125a7_MedIsoMu2_TauDMAntiMedIso_IDUP, scale=.001)
#   h125a7_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = ScaleRooDataSets(h125a7_MedIsoMu2_TauDMAntiMedIso_IsoDOWN, scale=.001)
#   h125a7_MedIsoMu2_TauDMAntiMedIso_IsoUP = ScaleRooDataSets(h125a7_MedIsoMu2_TauDMAntiMedIso_IsoUP, scale=.001)
#   h125a7_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = ScaleRooDataSets(h125a7_MedIsoMu2_TauDMAntiMedIso_BTagDOWN, scale=.001)
#   h125a7_MedIsoMu2_TauDMAntiMedIso_BTagUP = ScaleRooDataSets(h125a7_MedIsoMu2_TauDMAntiMedIso_BTagUP, scale=.001)
#   h125a7_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = ScaleRooDataSets(h125a7_MedIsoMu2_TauDMAntiMedIso_PileupDOWN, scale=.001)
#   h125a7_MedIsoMu2_TauDMAntiMedIso_PileupUP = ScaleRooDataSets(h125a7_MedIsoMu2_TauDMAntiMedIso_PileupUP, scale=.001)
#   h125a9_MedIsoMu2_TauDMAntiMedIso_Central = ScaleRooDataSets(h125a9_MedIsoMu2_TauDMAntiMedIso_Central, scale=.001)
#   h125a9_MedIsoMu2_TauDMAntiMedIso_IDDOWN = ScaleRooDataSets(h125a9_MedIsoMu2_TauDMAntiMedIso_IDDOWN, scale=.001)
#   h125a9_MedIsoMu2_TauDMAntiMedIso_IDUP = ScaleRooDataSets(h125a9_MedIsoMu2_TauDMAntiMedIso_IDUP, scale=.001)
#   h125a9_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = ScaleRooDataSets(h125a9_MedIsoMu2_TauDMAntiMedIso_IsoDOWN, scale=.001)
#   h125a9_MedIsoMu2_TauDMAntiMedIso_IsoUP = ScaleRooDataSets(h125a9_MedIsoMu2_TauDMAntiMedIso_IsoUP, scale=.001)
#   h125a9_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = ScaleRooDataSets(h125a9_MedIsoMu2_TauDMAntiMedIso_BTagDOWN, scale=.001)
#   h125a9_MedIsoMu2_TauDMAntiMedIso_BTagUP = ScaleRooDataSets(h125a9_MedIsoMu2_TauDMAntiMedIso_BTagUP, scale=.001)
#   h125a9_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = ScaleRooDataSets(h125a9_MedIsoMu2_TauDMAntiMedIso_PileupDOWN, scale=.001)
#   h125a9_MedIsoMu2_TauDMAntiMedIso_PileupUP = ScaleRooDataSets(h125a9_MedIsoMu2_TauDMAntiMedIso_PileupUP, scale=.001)
#   h300a11_MedIsoMu2_TauDMAntiMedIso_Central = ScaleRooDataSets(h300a11_MedIsoMu2_TauDMAntiMedIso_Central, scale=.001)
#   h300a11_MedIsoMu2_TauDMAntiMedIso_IDDOWN = ScaleRooDataSets(h300a11_MedIsoMu2_TauDMAntiMedIso_IDDOWN, scale=.001)
#   h300a11_MedIsoMu2_TauDMAntiMedIso_IDUP = ScaleRooDataSets(h300a11_MedIsoMu2_TauDMAntiMedIso_IDUP, scale=.001)
#   h300a11_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = ScaleRooDataSets(h300a11_MedIsoMu2_TauDMAntiMedIso_IsoDOWN, scale=.001)
#   h300a11_MedIsoMu2_TauDMAntiMedIso_IsoUP = ScaleRooDataSets(h300a11_MedIsoMu2_TauDMAntiMedIso_IsoUP, scale=.001)
#   h300a11_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = ScaleRooDataSets(h300a11_MedIsoMu2_TauDMAntiMedIso_BTagDOWN, scale=.001)
#   h300a11_MedIsoMu2_TauDMAntiMedIso_BTagUP = ScaleRooDataSets(h300a11_MedIsoMu2_TauDMAntiMedIso_BTagUP, scale=.001)
#   h300a11_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = ScaleRooDataSets(h300a11_MedIsoMu2_TauDMAntiMedIso_PileupDOWN, scale=.001)
#   h300a11_MedIsoMu2_TauDMAntiMedIso_PileupUP = ScaleRooDataSets(h300a11_MedIsoMu2_TauDMAntiMedIso_PileupUP, scale=.001)
#   h300a13_MedIsoMu2_TauDMAntiMedIso_Central = ScaleRooDataSets(h300a13_MedIsoMu2_TauDMAntiMedIso_Central, scale=.001)
#   h300a13_MedIsoMu2_TauDMAntiMedIso_IDDOWN = ScaleRooDataSets(h300a13_MedIsoMu2_TauDMAntiMedIso_IDDOWN, scale=.001)
#   h300a13_MedIsoMu2_TauDMAntiMedIso_IDUP = ScaleRooDataSets(h300a13_MedIsoMu2_TauDMAntiMedIso_IDUP, scale=.001)
#   h300a13_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = ScaleRooDataSets(h300a13_MedIsoMu2_TauDMAntiMedIso_IsoDOWN, scale=.001)
#   h300a13_MedIsoMu2_TauDMAntiMedIso_IsoUP = ScaleRooDataSets(h300a13_MedIsoMu2_TauDMAntiMedIso_IsoUP, scale=.001)
#   h300a13_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = ScaleRooDataSets(h300a13_MedIsoMu2_TauDMAntiMedIso_BTagDOWN, scale=.001)
#   h300a13_MedIsoMu2_TauDMAntiMedIso_BTagUP = ScaleRooDataSets(h300a13_MedIsoMu2_TauDMAntiMedIso_BTagUP, scale=.001)
#   h300a13_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = ScaleRooDataSets(h300a13_MedIsoMu2_TauDMAntiMedIso_PileupDOWN, scale=.001)
#   h300a13_MedIsoMu2_TauDMAntiMedIso_PileupUP = ScaleRooDataSets(h300a13_MedIsoMu2_TauDMAntiMedIso_PileupUP, scale=.001)
#   h300a15_MedIsoMu2_TauDMAntiMedIso_Central = ScaleRooDataSets(h300a15_MedIsoMu2_TauDMAntiMedIso_Central, scale=.001)
#   h300a15_MedIsoMu2_TauDMAntiMedIso_IDDOWN = ScaleRooDataSets(h300a15_MedIsoMu2_TauDMAntiMedIso_IDDOWN, scale=.001)
#   h300a15_MedIsoMu2_TauDMAntiMedIso_IDUP = ScaleRooDataSets(h300a15_MedIsoMu2_TauDMAntiMedIso_IDUP, scale=.001)
#   h300a15_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = ScaleRooDataSets(h300a15_MedIsoMu2_TauDMAntiMedIso_IsoDOWN, scale=.001)
#   h300a15_MedIsoMu2_TauDMAntiMedIso_IsoUP = ScaleRooDataSets(h300a15_MedIsoMu2_TauDMAntiMedIso_IsoUP, scale=.001)
#   h300a15_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = ScaleRooDataSets(h300a15_MedIsoMu2_TauDMAntiMedIso_BTagDOWN, scale=.001)
#   h300a15_MedIsoMu2_TauDMAntiMedIso_BTagUP = ScaleRooDataSets(h300a15_MedIsoMu2_TauDMAntiMedIso_BTagUP, scale=.001)
#   h300a15_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = ScaleRooDataSets(h300a15_MedIsoMu2_TauDMAntiMedIso_PileupDOWN, scale=.001)
#   h300a15_MedIsoMu2_TauDMAntiMedIso_PileupUP = ScaleRooDataSets(h300a15_MedIsoMu2_TauDMAntiMedIso_PileupUP, scale=.001)
#   h300a17_MedIsoMu2_TauDMAntiMedIso_Central = ScaleRooDataSets(h300a17_MedIsoMu2_TauDMAntiMedIso_Central, scale=.001)
#   h300a17_MedIsoMu2_TauDMAntiMedIso_IDDOWN = ScaleRooDataSets(h300a17_MedIsoMu2_TauDMAntiMedIso_IDDOWN, scale=.001)
#   h300a17_MedIsoMu2_TauDMAntiMedIso_IDUP = ScaleRooDataSets(h300a17_MedIsoMu2_TauDMAntiMedIso_IDUP, scale=.001)
#   h300a17_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = ScaleRooDataSets(h300a17_MedIsoMu2_TauDMAntiMedIso_IsoDOWN, scale=.001)
#   h300a17_MedIsoMu2_TauDMAntiMedIso_IsoUP = ScaleRooDataSets(h300a17_MedIsoMu2_TauDMAntiMedIso_IsoUP, scale=.001)
#   h300a17_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = ScaleRooDataSets(h300a17_MedIsoMu2_TauDMAntiMedIso_BTagDOWN, scale=.001)
#   h300a17_MedIsoMu2_TauDMAntiMedIso_BTagUP = ScaleRooDataSets(h300a17_MedIsoMu2_TauDMAntiMedIso_BTagUP, scale=.001)
#   h300a17_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = ScaleRooDataSets(h300a17_MedIsoMu2_TauDMAntiMedIso_PileupDOWN, scale=.001)
#   h300a17_MedIsoMu2_TauDMAntiMedIso_PileupUP = ScaleRooDataSets(h300a17_MedIsoMu2_TauDMAntiMedIso_PileupUP, scale=.001)
#   h300a19_MedIsoMu2_TauDMAntiMedIso_Central = ScaleRooDataSets(h300a19_MedIsoMu2_TauDMAntiMedIso_Central, scale=.001)
#   h300a19_MedIsoMu2_TauDMAntiMedIso_IDDOWN = ScaleRooDataSets(h300a19_MedIsoMu2_TauDMAntiMedIso_IDDOWN, scale=.001)
#   h300a19_MedIsoMu2_TauDMAntiMedIso_IDUP = ScaleRooDataSets(h300a19_MedIsoMu2_TauDMAntiMedIso_IDUP, scale=.001)
#   h300a19_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = ScaleRooDataSets(h300a19_MedIsoMu2_TauDMAntiMedIso_IsoDOWN, scale=.001)
#   h300a19_MedIsoMu2_TauDMAntiMedIso_IsoUP = ScaleRooDataSets(h300a19_MedIsoMu2_TauDMAntiMedIso_IsoUP, scale=.001)
#   h300a19_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = ScaleRooDataSets(h300a19_MedIsoMu2_TauDMAntiMedIso_BTagDOWN, scale=.001)
#   h300a19_MedIsoMu2_TauDMAntiMedIso_BTagUP = ScaleRooDataSets(h300a19_MedIsoMu2_TauDMAntiMedIso_BTagUP, scale=.001)
#   h300a19_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = ScaleRooDataSets(h300a19_MedIsoMu2_TauDMAntiMedIso_PileupDOWN, scale=.001)
#   h300a19_MedIsoMu2_TauDMAntiMedIso_PileupUP = ScaleRooDataSets(h300a19_MedIsoMu2_TauDMAntiMedIso_PileupUP, scale=.001)
#   h300a21_MedIsoMu2_TauDMAntiMedIso_Central = ScaleRooDataSets(h300a21_MedIsoMu2_TauDMAntiMedIso_Central, scale=.001)
#   h300a21_MedIsoMu2_TauDMAntiMedIso_IDDOWN = ScaleRooDataSets(h300a21_MedIsoMu2_TauDMAntiMedIso_IDDOWN, scale=.001)
#   h300a21_MedIsoMu2_TauDMAntiMedIso_IDUP = ScaleRooDataSets(h300a21_MedIsoMu2_TauDMAntiMedIso_IDUP, scale=.001)
#   h300a21_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = ScaleRooDataSets(h300a21_MedIsoMu2_TauDMAntiMedIso_IsoDOWN, scale=.001)
#   h300a21_MedIsoMu2_TauDMAntiMedIso_IsoUP = ScaleRooDataSets(h300a21_MedIsoMu2_TauDMAntiMedIso_IsoUP, scale=.001)
#   h300a21_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = ScaleRooDataSets(h300a21_MedIsoMu2_TauDMAntiMedIso_BTagDOWN, scale=.001)
#   h300a21_MedIsoMu2_TauDMAntiMedIso_BTagUP = ScaleRooDataSets(h300a21_MedIsoMu2_TauDMAntiMedIso_BTagUP, scale=.001)
#   h300a21_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = ScaleRooDataSets(h300a21_MedIsoMu2_TauDMAntiMedIso_PileupDOWN, scale=.001)
#   h300a21_MedIsoMu2_TauDMAntiMedIso_PileupUP = ScaleRooDataSets(h300a21_MedIsoMu2_TauDMAntiMedIso_PileupUP, scale=.001)
#   h300a5_MedIsoMu2_TauDMAntiMedIso_Central = ScaleRooDataSets(h300a5_MedIsoMu2_TauDMAntiMedIso_Central, scale=.001)
#   h300a5_MedIsoMu2_TauDMAntiMedIso_IDDOWN = ScaleRooDataSets(h300a5_MedIsoMu2_TauDMAntiMedIso_IDDOWN, scale=.001)
#   h300a5_MedIsoMu2_TauDMAntiMedIso_IDUP = ScaleRooDataSets(h300a5_MedIsoMu2_TauDMAntiMedIso_IDUP, scale=.001)
#   h300a5_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = ScaleRooDataSets(h300a5_MedIsoMu2_TauDMAntiMedIso_IsoDOWN, scale=.001)
#   h300a5_MedIsoMu2_TauDMAntiMedIso_IsoUP = ScaleRooDataSets(h300a5_MedIsoMu2_TauDMAntiMedIso_IsoUP, scale=.001)
#   h300a5_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = ScaleRooDataSets(h300a5_MedIsoMu2_TauDMAntiMedIso_BTagDOWN, scale=.001)
#   h300a5_MedIsoMu2_TauDMAntiMedIso_BTagUP = ScaleRooDataSets(h300a5_MedIsoMu2_TauDMAntiMedIso_BTagUP, scale=.001)
#   h300a5_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = ScaleRooDataSets(h300a5_MedIsoMu2_TauDMAntiMedIso_PileupDOWN, scale=.001)
#   h300a5_MedIsoMu2_TauDMAntiMedIso_PileupUP = ScaleRooDataSets(h300a5_MedIsoMu2_TauDMAntiMedIso_PileupUP, scale=.001)
#   h300a7_MedIsoMu2_TauDMAntiMedIso_Central = ScaleRooDataSets(h300a7_MedIsoMu2_TauDMAntiMedIso_Central, scale=.001)
#   h300a7_MedIsoMu2_TauDMAntiMedIso_IDDOWN = ScaleRooDataSets(h300a7_MedIsoMu2_TauDMAntiMedIso_IDDOWN, scale=.001)
#   h300a7_MedIsoMu2_TauDMAntiMedIso_IDUP = ScaleRooDataSets(h300a7_MedIsoMu2_TauDMAntiMedIso_IDUP, scale=.001)
#   h300a7_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = ScaleRooDataSets(h300a7_MedIsoMu2_TauDMAntiMedIso_IsoDOWN, scale=.001)
#   h300a7_MedIsoMu2_TauDMAntiMedIso_IsoUP = ScaleRooDataSets(h300a7_MedIsoMu2_TauDMAntiMedIso_IsoUP, scale=.001)
#   h300a7_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = ScaleRooDataSets(h300a7_MedIsoMu2_TauDMAntiMedIso_BTagDOWN, scale=.001)
#   h300a7_MedIsoMu2_TauDMAntiMedIso_BTagUP = ScaleRooDataSets(h300a7_MedIsoMu2_TauDMAntiMedIso_BTagUP, scale=.001)
#   h300a7_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = ScaleRooDataSets(h300a7_MedIsoMu2_TauDMAntiMedIso_PileupDOWN, scale=.001)
#   h300a7_MedIsoMu2_TauDMAntiMedIso_PileupUP = ScaleRooDataSets(h300a7_MedIsoMu2_TauDMAntiMedIso_PileupUP, scale=.001)
#   h300a9_MedIsoMu2_TauDMAntiMedIso_Central = ScaleRooDataSets(h300a9_MedIsoMu2_TauDMAntiMedIso_Central, scale=.001)
#   h300a9_MedIsoMu2_TauDMAntiMedIso_IDDOWN = ScaleRooDataSets(h300a9_MedIsoMu2_TauDMAntiMedIso_IDDOWN, scale=.001)
#   h300a9_MedIsoMu2_TauDMAntiMedIso_IDUP = ScaleRooDataSets(h300a9_MedIsoMu2_TauDMAntiMedIso_IDUP, scale=.001)
#   h300a9_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = ScaleRooDataSets(h300a9_MedIsoMu2_TauDMAntiMedIso_IsoDOWN, scale=.001)
#   h300a9_MedIsoMu2_TauDMAntiMedIso_IsoUP = ScaleRooDataSets(h300a9_MedIsoMu2_TauDMAntiMedIso_IsoUP, scale=.001)
#   h300a9_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = ScaleRooDataSets(h300a9_MedIsoMu2_TauDMAntiMedIso_BTagDOWN, scale=.001)
#   h300a9_MedIsoMu2_TauDMAntiMedIso_BTagUP = ScaleRooDataSets(h300a9_MedIsoMu2_TauDMAntiMedIso_BTagUP, scale=.001)
#   h300a9_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = ScaleRooDataSets(h300a9_MedIsoMu2_TauDMAntiMedIso_PileupDOWN, scale=.001)
#   h300a9_MedIsoMu2_TauDMAntiMedIso_PileupUP = ScaleRooDataSets(h300a9_MedIsoMu2_TauDMAntiMedIso_PileupUP, scale=.001)
#   h750a11_MedIsoMu2_TauDMAntiMedIso_Central = ScaleRooDataSets(h750a11_MedIsoMu2_TauDMAntiMedIso_Central, scale=.001)
#   h750a11_MedIsoMu2_TauDMAntiMedIso_IDDOWN = ScaleRooDataSets(h750a11_MedIsoMu2_TauDMAntiMedIso_IDDOWN, scale=.001)
#   h750a11_MedIsoMu2_TauDMAntiMedIso_IDUP = ScaleRooDataSets(h750a11_MedIsoMu2_TauDMAntiMedIso_IDUP, scale=.001)
#   h750a11_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = ScaleRooDataSets(h750a11_MedIsoMu2_TauDMAntiMedIso_IsoDOWN, scale=.001)
#   h750a11_MedIsoMu2_TauDMAntiMedIso_IsoUP = ScaleRooDataSets(h750a11_MedIsoMu2_TauDMAntiMedIso_IsoUP, scale=.001)
#   h750a11_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = ScaleRooDataSets(h750a11_MedIsoMu2_TauDMAntiMedIso_BTagDOWN, scale=.001)
#   h750a11_MedIsoMu2_TauDMAntiMedIso_BTagUP = ScaleRooDataSets(h750a11_MedIsoMu2_TauDMAntiMedIso_BTagUP, scale=.001)
#   h750a11_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = ScaleRooDataSets(h750a11_MedIsoMu2_TauDMAntiMedIso_PileupDOWN, scale=.001)
#   h750a11_MedIsoMu2_TauDMAntiMedIso_PileupUP = ScaleRooDataSets(h750a11_MedIsoMu2_TauDMAntiMedIso_PileupUP, scale=.001)
#   h750a13_MedIsoMu2_TauDMAntiMedIso_Central = ScaleRooDataSets(h750a13_MedIsoMu2_TauDMAntiMedIso_Central, scale=.001)
#   h750a13_MedIsoMu2_TauDMAntiMedIso_IDDOWN = ScaleRooDataSets(h750a13_MedIsoMu2_TauDMAntiMedIso_IDDOWN, scale=.001)
#   h750a13_MedIsoMu2_TauDMAntiMedIso_IDUP = ScaleRooDataSets(h750a13_MedIsoMu2_TauDMAntiMedIso_IDUP, scale=.001)
#   h750a13_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = ScaleRooDataSets(h750a13_MedIsoMu2_TauDMAntiMedIso_IsoDOWN, scale=.001)
#   h750a13_MedIsoMu2_TauDMAntiMedIso_IsoUP = ScaleRooDataSets(h750a13_MedIsoMu2_TauDMAntiMedIso_IsoUP, scale=.001)
#   h750a13_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = ScaleRooDataSets(h750a13_MedIsoMu2_TauDMAntiMedIso_BTagDOWN, scale=.001)
#   h750a13_MedIsoMu2_TauDMAntiMedIso_BTagUP = ScaleRooDataSets(h750a13_MedIsoMu2_TauDMAntiMedIso_BTagUP, scale=.001)
#   h750a13_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = ScaleRooDataSets(h750a13_MedIsoMu2_TauDMAntiMedIso_PileupDOWN, scale=.001)
#   h750a13_MedIsoMu2_TauDMAntiMedIso_PileupUP = ScaleRooDataSets(h750a13_MedIsoMu2_TauDMAntiMedIso_PileupUP, scale=.001)
#   h750a15_MedIsoMu2_TauDMAntiMedIso_Central = ScaleRooDataSets(h750a15_MedIsoMu2_TauDMAntiMedIso_Central, scale=.001)
#   h750a15_MedIsoMu2_TauDMAntiMedIso_IDDOWN = ScaleRooDataSets(h750a15_MedIsoMu2_TauDMAntiMedIso_IDDOWN, scale=.001)
#   h750a15_MedIsoMu2_TauDMAntiMedIso_IDUP = ScaleRooDataSets(h750a15_MedIsoMu2_TauDMAntiMedIso_IDUP, scale=.001)
#   h750a15_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = ScaleRooDataSets(h750a15_MedIsoMu2_TauDMAntiMedIso_IsoDOWN, scale=.001)
#   h750a15_MedIsoMu2_TauDMAntiMedIso_IsoUP = ScaleRooDataSets(h750a15_MedIsoMu2_TauDMAntiMedIso_IsoUP, scale=.001)
#   h750a15_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = ScaleRooDataSets(h750a15_MedIsoMu2_TauDMAntiMedIso_BTagDOWN, scale=.001)
#   h750a15_MedIsoMu2_TauDMAntiMedIso_BTagUP = ScaleRooDataSets(h750a15_MedIsoMu2_TauDMAntiMedIso_BTagUP, scale=.001)
#   h750a15_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = ScaleRooDataSets(h750a15_MedIsoMu2_TauDMAntiMedIso_PileupDOWN, scale=.001)
#   h750a15_MedIsoMu2_TauDMAntiMedIso_PileupUP = ScaleRooDataSets(h750a15_MedIsoMu2_TauDMAntiMedIso_PileupUP, scale=.001)
#   h750a17_MedIsoMu2_TauDMAntiMedIso_Central = ScaleRooDataSets(h750a17_MedIsoMu2_TauDMAntiMedIso_Central, scale=.001)
#   h750a17_MedIsoMu2_TauDMAntiMedIso_IDDOWN = ScaleRooDataSets(h750a17_MedIsoMu2_TauDMAntiMedIso_IDDOWN, scale=.001)
#   h750a17_MedIsoMu2_TauDMAntiMedIso_IDUP = ScaleRooDataSets(h750a17_MedIsoMu2_TauDMAntiMedIso_IDUP, scale=.001)
#   h750a17_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = ScaleRooDataSets(h750a17_MedIsoMu2_TauDMAntiMedIso_IsoDOWN, scale=.001)
#   h750a17_MedIsoMu2_TauDMAntiMedIso_IsoUP = ScaleRooDataSets(h750a17_MedIsoMu2_TauDMAntiMedIso_IsoUP, scale=.001)
#   h750a17_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = ScaleRooDataSets(h750a17_MedIsoMu2_TauDMAntiMedIso_BTagDOWN, scale=.001)
#   h750a17_MedIsoMu2_TauDMAntiMedIso_BTagUP = ScaleRooDataSets(h750a17_MedIsoMu2_TauDMAntiMedIso_BTagUP, scale=.001)
#   h750a17_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = ScaleRooDataSets(h750a17_MedIsoMu2_TauDMAntiMedIso_PileupDOWN, scale=.001)
#   h750a17_MedIsoMu2_TauDMAntiMedIso_PileupUP = ScaleRooDataSets(h750a17_MedIsoMu2_TauDMAntiMedIso_PileupUP, scale=.001)
#   h750a19_MedIsoMu2_TauDMAntiMedIso_Central = ScaleRooDataSets(h750a19_MedIsoMu2_TauDMAntiMedIso_Central, scale=.001)
#   h750a19_MedIsoMu2_TauDMAntiMedIso_IDDOWN = ScaleRooDataSets(h750a19_MedIsoMu2_TauDMAntiMedIso_IDDOWN, scale=.001)
#   h750a19_MedIsoMu2_TauDMAntiMedIso_IDUP = ScaleRooDataSets(h750a19_MedIsoMu2_TauDMAntiMedIso_IDUP, scale=.001)
#   h750a19_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = ScaleRooDataSets(h750a19_MedIsoMu2_TauDMAntiMedIso_IsoDOWN, scale=.001)
#   h750a19_MedIsoMu2_TauDMAntiMedIso_IsoUP = ScaleRooDataSets(h750a19_MedIsoMu2_TauDMAntiMedIso_IsoUP, scale=.001)
#   h750a19_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = ScaleRooDataSets(h750a19_MedIsoMu2_TauDMAntiMedIso_BTagDOWN, scale=.001)
#   h750a19_MedIsoMu2_TauDMAntiMedIso_BTagUP = ScaleRooDataSets(h750a19_MedIsoMu2_TauDMAntiMedIso_BTagUP, scale=.001)
#   h750a19_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = ScaleRooDataSets(h750a19_MedIsoMu2_TauDMAntiMedIso_PileupDOWN, scale=.001)
#   h750a19_MedIsoMu2_TauDMAntiMedIso_PileupUP = ScaleRooDataSets(h750a19_MedIsoMu2_TauDMAntiMedIso_PileupUP, scale=.001)
#   h750a21_MedIsoMu2_TauDMAntiMedIso_Central = ScaleRooDataSets(h750a21_MedIsoMu2_TauDMAntiMedIso_Central, scale=.001)
#   h750a21_MedIsoMu2_TauDMAntiMedIso_IDDOWN = ScaleRooDataSets(h750a21_MedIsoMu2_TauDMAntiMedIso_IDDOWN, scale=.001)
#   h750a21_MedIsoMu2_TauDMAntiMedIso_IDUP = ScaleRooDataSets(h750a21_MedIsoMu2_TauDMAntiMedIso_IDUP, scale=.001)
#   h750a21_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = ScaleRooDataSets(h750a21_MedIsoMu2_TauDMAntiMedIso_IsoDOWN, scale=.001)
#   h750a21_MedIsoMu2_TauDMAntiMedIso_IsoUP = ScaleRooDataSets(h750a21_MedIsoMu2_TauDMAntiMedIso_IsoUP, scale=.001)
#   h750a21_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = ScaleRooDataSets(h750a21_MedIsoMu2_TauDMAntiMedIso_BTagDOWN, scale=.001)
#   h750a21_MedIsoMu2_TauDMAntiMedIso_BTagUP = ScaleRooDataSets(h750a21_MedIsoMu2_TauDMAntiMedIso_BTagUP, scale=.001)
#   h750a21_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = ScaleRooDataSets(h750a21_MedIsoMu2_TauDMAntiMedIso_PileupDOWN, scale=.001)
#   h750a21_MedIsoMu2_TauDMAntiMedIso_PileupUP = ScaleRooDataSets(h750a21_MedIsoMu2_TauDMAntiMedIso_PileupUP, scale=.001)
#   h750a5_MedIsoMu2_TauDMAntiMedIso_Central = ScaleRooDataSets(h750a5_MedIsoMu2_TauDMAntiMedIso_Central, scale=.001)
#   h750a5_MedIsoMu2_TauDMAntiMedIso_IDDOWN = ScaleRooDataSets(h750a5_MedIsoMu2_TauDMAntiMedIso_IDDOWN, scale=.001)
#   h750a5_MedIsoMu2_TauDMAntiMedIso_IDUP = ScaleRooDataSets(h750a5_MedIsoMu2_TauDMAntiMedIso_IDUP, scale=.001)
#   h750a5_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = ScaleRooDataSets(h750a5_MedIsoMu2_TauDMAntiMedIso_IsoDOWN, scale=.001)
#   h750a5_MedIsoMu2_TauDMAntiMedIso_IsoUP = ScaleRooDataSets(h750a5_MedIsoMu2_TauDMAntiMedIso_IsoUP, scale=.001)
#   h750a5_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = ScaleRooDataSets(h750a5_MedIsoMu2_TauDMAntiMedIso_BTagDOWN, scale=.001)
#   h750a5_MedIsoMu2_TauDMAntiMedIso_BTagUP = ScaleRooDataSets(h750a5_MedIsoMu2_TauDMAntiMedIso_BTagUP, scale=.001)
#   h750a5_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = ScaleRooDataSets(h750a5_MedIsoMu2_TauDMAntiMedIso_PileupDOWN, scale=.001)
#   h750a5_MedIsoMu2_TauDMAntiMedIso_PileupUP = ScaleRooDataSets(h750a5_MedIsoMu2_TauDMAntiMedIso_PileupUP, scale=.001)
#   h750a7_MedIsoMu2_TauDMAntiMedIso_Central = ScaleRooDataSets(h750a7_MedIsoMu2_TauDMAntiMedIso_Central, scale=.001)
#   h750a7_MedIsoMu2_TauDMAntiMedIso_IDDOWN = ScaleRooDataSets(h750a7_MedIsoMu2_TauDMAntiMedIso_IDDOWN, scale=.001)
#   h750a7_MedIsoMu2_TauDMAntiMedIso_IDUP = ScaleRooDataSets(h750a7_MedIsoMu2_TauDMAntiMedIso_IDUP, scale=.001)
#   h750a7_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = ScaleRooDataSets(h750a7_MedIsoMu2_TauDMAntiMedIso_IsoDOWN, scale=.001)
#   h750a7_MedIsoMu2_TauDMAntiMedIso_IsoUP = ScaleRooDataSets(h750a7_MedIsoMu2_TauDMAntiMedIso_IsoUP, scale=.001)
#   h750a7_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = ScaleRooDataSets(h750a7_MedIsoMu2_TauDMAntiMedIso_BTagDOWN, scale=.001)
#   h750a7_MedIsoMu2_TauDMAntiMedIso_BTagUP = ScaleRooDataSets(h750a7_MedIsoMu2_TauDMAntiMedIso_BTagUP, scale=.001)
#   h750a7_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = ScaleRooDataSets(h750a7_MedIsoMu2_TauDMAntiMedIso_PileupDOWN, scale=.001)
#   h750a7_MedIsoMu2_TauDMAntiMedIso_PileupUP = ScaleRooDataSets(h750a7_MedIsoMu2_TauDMAntiMedIso_PileupUP, scale=.001)
#   h750a9_MedIsoMu2_TauDMAntiMedIso_Central = ScaleRooDataSets(h750a9_MedIsoMu2_TauDMAntiMedIso_Central, scale=.001)
#   h750a9_MedIsoMu2_TauDMAntiMedIso_IDDOWN = ScaleRooDataSets(h750a9_MedIsoMu2_TauDMAntiMedIso_IDDOWN, scale=.001)
#   h750a9_MedIsoMu2_TauDMAntiMedIso_IDUP = ScaleRooDataSets(h750a9_MedIsoMu2_TauDMAntiMedIso_IDUP, scale=.001)
#   h750a9_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = ScaleRooDataSets(h750a9_MedIsoMu2_TauDMAntiMedIso_IsoDOWN, scale=.001)
#   h750a9_MedIsoMu2_TauDMAntiMedIso_IsoUP = ScaleRooDataSets(h750a9_MedIsoMu2_TauDMAntiMedIso_IsoUP, scale=.001)
#   h750a9_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = ScaleRooDataSets(h750a9_MedIsoMu2_TauDMAntiMedIso_BTagDOWN, scale=.001)
#   h750a9_MedIsoMu2_TauDMAntiMedIso_BTagUP = ScaleRooDataSets(h750a9_MedIsoMu2_TauDMAntiMedIso_BTagUP, scale=.001)
#   h750a9_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = ScaleRooDataSets(h750a9_MedIsoMu2_TauDMAntiMedIso_PileupDOWN, scale=.001)
#   h750a9_MedIsoMu2_TauDMAntiMedIso_PileupUP = ScaleRooDataSets(h750a9_MedIsoMu2_TauDMAntiMedIso_PileupUP, scale=.001)
   
   h125a11_MedIsoMu2_TauDMAntiMedIso_Central = getDataset(h125a11_MedIsoMu2_TauDMAntiMedIso_Central, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a11_MedIsoMu2_TauDMAntiMedIso_IDDOWN = getDataset(h125a11_MedIsoMu2_TauDMAntiMedIso_IDDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a11_MedIsoMu2_TauDMAntiMedIso_IDUP = getDataset(h125a11_MedIsoMu2_TauDMAntiMedIso_IDUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a11_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = getDataset(h125a11_MedIsoMu2_TauDMAntiMedIso_IsoDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a11_MedIsoMu2_TauDMAntiMedIso_IsoUP = getDataset(h125a11_MedIsoMu2_TauDMAntiMedIso_IsoUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a11_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = getDataset(h125a11_MedIsoMu2_TauDMAntiMedIso_BTagDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a11_MedIsoMu2_TauDMAntiMedIso_BTagUP = getDataset(h125a11_MedIsoMu2_TauDMAntiMedIso_BTagUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a11_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = getDataset(h125a11_MedIsoMu2_TauDMAntiMedIso_PileupDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a11_MedIsoMu2_TauDMAntiMedIso_PileupUP = getDataset(h125a11_MedIsoMu2_TauDMAntiMedIso_PileupUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a13_MedIsoMu2_TauDMAntiMedIso_Central = getDataset(h125a13_MedIsoMu2_TauDMAntiMedIso_Central, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a13_MedIsoMu2_TauDMAntiMedIso_IDDOWN = getDataset(h125a13_MedIsoMu2_TauDMAntiMedIso_IDDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a13_MedIsoMu2_TauDMAntiMedIso_IDUP = getDataset(h125a13_MedIsoMu2_TauDMAntiMedIso_IDUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a13_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = getDataset(h125a13_MedIsoMu2_TauDMAntiMedIso_IsoDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a13_MedIsoMu2_TauDMAntiMedIso_IsoUP = getDataset(h125a13_MedIsoMu2_TauDMAntiMedIso_IsoUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a13_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = getDataset(h125a13_MedIsoMu2_TauDMAntiMedIso_BTagDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a13_MedIsoMu2_TauDMAntiMedIso_BTagUP = getDataset(h125a13_MedIsoMu2_TauDMAntiMedIso_BTagUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a13_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = getDataset(h125a13_MedIsoMu2_TauDMAntiMedIso_PileupDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a13_MedIsoMu2_TauDMAntiMedIso_PileupUP = getDataset(h125a13_MedIsoMu2_TauDMAntiMedIso_PileupUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a15_MedIsoMu2_TauDMAntiMedIso_Central = getDataset(h125a15_MedIsoMu2_TauDMAntiMedIso_Central, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a15_MedIsoMu2_TauDMAntiMedIso_IDDOWN = getDataset(h125a15_MedIsoMu2_TauDMAntiMedIso_IDDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a15_MedIsoMu2_TauDMAntiMedIso_IDUP = getDataset(h125a15_MedIsoMu2_TauDMAntiMedIso_IDUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a15_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = getDataset(h125a15_MedIsoMu2_TauDMAntiMedIso_IsoDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a15_MedIsoMu2_TauDMAntiMedIso_IsoUP = getDataset(h125a15_MedIsoMu2_TauDMAntiMedIso_IsoUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a15_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = getDataset(h125a15_MedIsoMu2_TauDMAntiMedIso_BTagDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a15_MedIsoMu2_TauDMAntiMedIso_BTagUP = getDataset(h125a15_MedIsoMu2_TauDMAntiMedIso_BTagUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a15_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = getDataset(h125a15_MedIsoMu2_TauDMAntiMedIso_PileupDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a15_MedIsoMu2_TauDMAntiMedIso_PileupUP = getDataset(h125a15_MedIsoMu2_TauDMAntiMedIso_PileupUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a17_MedIsoMu2_TauDMAntiMedIso_Central = getDataset(h125a17_MedIsoMu2_TauDMAntiMedIso_Central, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a17_MedIsoMu2_TauDMAntiMedIso_IDDOWN = getDataset(h125a17_MedIsoMu2_TauDMAntiMedIso_IDDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a17_MedIsoMu2_TauDMAntiMedIso_IDUP = getDataset(h125a17_MedIsoMu2_TauDMAntiMedIso_IDUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a17_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = getDataset(h125a17_MedIsoMu2_TauDMAntiMedIso_IsoDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a17_MedIsoMu2_TauDMAntiMedIso_IsoUP = getDataset(h125a17_MedIsoMu2_TauDMAntiMedIso_IsoUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a17_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = getDataset(h125a17_MedIsoMu2_TauDMAntiMedIso_BTagDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a17_MedIsoMu2_TauDMAntiMedIso_BTagUP = getDataset(h125a17_MedIsoMu2_TauDMAntiMedIso_BTagUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a17_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = getDataset(h125a17_MedIsoMu2_TauDMAntiMedIso_PileupDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a17_MedIsoMu2_TauDMAntiMedIso_PileupUP = getDataset(h125a17_MedIsoMu2_TauDMAntiMedIso_PileupUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a19_MedIsoMu2_TauDMAntiMedIso_Central = getDataset(h125a19_MedIsoMu2_TauDMAntiMedIso_Central, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a19_MedIsoMu2_TauDMAntiMedIso_IDDOWN = getDataset(h125a19_MedIsoMu2_TauDMAntiMedIso_IDDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a19_MedIsoMu2_TauDMAntiMedIso_IDUP = getDataset(h125a19_MedIsoMu2_TauDMAntiMedIso_IDUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a19_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = getDataset(h125a19_MedIsoMu2_TauDMAntiMedIso_IsoDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a19_MedIsoMu2_TauDMAntiMedIso_IsoUP = getDataset(h125a19_MedIsoMu2_TauDMAntiMedIso_IsoUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a19_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = getDataset(h125a19_MedIsoMu2_TauDMAntiMedIso_BTagDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a19_MedIsoMu2_TauDMAntiMedIso_BTagUP = getDataset(h125a19_MedIsoMu2_TauDMAntiMedIso_BTagUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a19_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = getDataset(h125a19_MedIsoMu2_TauDMAntiMedIso_PileupDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a19_MedIsoMu2_TauDMAntiMedIso_PileupUP = getDataset(h125a19_MedIsoMu2_TauDMAntiMedIso_PileupUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a21_MedIsoMu2_TauDMAntiMedIso_Central = getDataset(h125a21_MedIsoMu2_TauDMAntiMedIso_Central, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a21_MedIsoMu2_TauDMAntiMedIso_IDDOWN = getDataset(h125a21_MedIsoMu2_TauDMAntiMedIso_IDDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a21_MedIsoMu2_TauDMAntiMedIso_IDUP = getDataset(h125a21_MedIsoMu2_TauDMAntiMedIso_IDUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a21_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = getDataset(h125a21_MedIsoMu2_TauDMAntiMedIso_IsoDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a21_MedIsoMu2_TauDMAntiMedIso_IsoUP = getDataset(h125a21_MedIsoMu2_TauDMAntiMedIso_IsoUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a21_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = getDataset(h125a21_MedIsoMu2_TauDMAntiMedIso_BTagDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a21_MedIsoMu2_TauDMAntiMedIso_BTagUP = getDataset(h125a21_MedIsoMu2_TauDMAntiMedIso_BTagUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a21_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = getDataset(h125a21_MedIsoMu2_TauDMAntiMedIso_PileupDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a21_MedIsoMu2_TauDMAntiMedIso_PileupUP = getDataset(h125a21_MedIsoMu2_TauDMAntiMedIso_PileupUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a5_MedIsoMu2_TauDMAntiMedIso_Central = getDataset(h125a5_MedIsoMu2_TauDMAntiMedIso_Central, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a5_MedIsoMu2_TauDMAntiMedIso_IDDOWN = getDataset(h125a5_MedIsoMu2_TauDMAntiMedIso_IDDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a5_MedIsoMu2_TauDMAntiMedIso_IDUP = getDataset(h125a5_MedIsoMu2_TauDMAntiMedIso_IDUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a5_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = getDataset(h125a5_MedIsoMu2_TauDMAntiMedIso_IsoDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a5_MedIsoMu2_TauDMAntiMedIso_IsoUP = getDataset(h125a5_MedIsoMu2_TauDMAntiMedIso_IsoUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a5_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = getDataset(h125a5_MedIsoMu2_TauDMAntiMedIso_BTagDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a5_MedIsoMu2_TauDMAntiMedIso_BTagUP = getDataset(h125a5_MedIsoMu2_TauDMAntiMedIso_BTagUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a5_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = getDataset(h125a5_MedIsoMu2_TauDMAntiMedIso_PileupDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a5_MedIsoMu2_TauDMAntiMedIso_PileupUP = getDataset(h125a5_MedIsoMu2_TauDMAntiMedIso_PileupUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a7_MedIsoMu2_TauDMAntiMedIso_Central = getDataset(h125a7_MedIsoMu2_TauDMAntiMedIso_Central, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a7_MedIsoMu2_TauDMAntiMedIso_IDDOWN = getDataset(h125a7_MedIsoMu2_TauDMAntiMedIso_IDDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a7_MedIsoMu2_TauDMAntiMedIso_IDUP = getDataset(h125a7_MedIsoMu2_TauDMAntiMedIso_IDUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a7_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = getDataset(h125a7_MedIsoMu2_TauDMAntiMedIso_IsoDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a7_MedIsoMu2_TauDMAntiMedIso_IsoUP = getDataset(h125a7_MedIsoMu2_TauDMAntiMedIso_IsoUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a7_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = getDataset(h125a7_MedIsoMu2_TauDMAntiMedIso_BTagDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a7_MedIsoMu2_TauDMAntiMedIso_BTagUP = getDataset(h125a7_MedIsoMu2_TauDMAntiMedIso_BTagUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a7_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = getDataset(h125a7_MedIsoMu2_TauDMAntiMedIso_PileupDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a7_MedIsoMu2_TauDMAntiMedIso_PileupUP = getDataset(h125a7_MedIsoMu2_TauDMAntiMedIso_PileupUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a9_MedIsoMu2_TauDMAntiMedIso_Central = getDataset(h125a9_MedIsoMu2_TauDMAntiMedIso_Central, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a9_MedIsoMu2_TauDMAntiMedIso_IDDOWN = getDataset(h125a9_MedIsoMu2_TauDMAntiMedIso_IDDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a9_MedIsoMu2_TauDMAntiMedIso_IDUP = getDataset(h125a9_MedIsoMu2_TauDMAntiMedIso_IDUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a9_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = getDataset(h125a9_MedIsoMu2_TauDMAntiMedIso_IsoDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a9_MedIsoMu2_TauDMAntiMedIso_IsoUP = getDataset(h125a9_MedIsoMu2_TauDMAntiMedIso_IsoUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a9_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = getDataset(h125a9_MedIsoMu2_TauDMAntiMedIso_BTagDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a9_MedIsoMu2_TauDMAntiMedIso_BTagUP = getDataset(h125a9_MedIsoMu2_TauDMAntiMedIso_BTagUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a9_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = getDataset(h125a9_MedIsoMu2_TauDMAntiMedIso_PileupDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h125a9_MedIsoMu2_TauDMAntiMedIso_PileupUP = getDataset(h125a9_MedIsoMu2_TauDMAntiMedIso_PileupUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a11_MedIsoMu2_TauDMAntiMedIso_Central = getDataset(h300a11_MedIsoMu2_TauDMAntiMedIso_Central, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a11_MedIsoMu2_TauDMAntiMedIso_IDDOWN = getDataset(h300a11_MedIsoMu2_TauDMAntiMedIso_IDDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a11_MedIsoMu2_TauDMAntiMedIso_IDUP = getDataset(h300a11_MedIsoMu2_TauDMAntiMedIso_IDUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a11_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = getDataset(h300a11_MedIsoMu2_TauDMAntiMedIso_IsoDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a11_MedIsoMu2_TauDMAntiMedIso_IsoUP = getDataset(h300a11_MedIsoMu2_TauDMAntiMedIso_IsoUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a11_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = getDataset(h300a11_MedIsoMu2_TauDMAntiMedIso_BTagDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a11_MedIsoMu2_TauDMAntiMedIso_BTagUP = getDataset(h300a11_MedIsoMu2_TauDMAntiMedIso_BTagUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a11_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = getDataset(h300a11_MedIsoMu2_TauDMAntiMedIso_PileupDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a11_MedIsoMu2_TauDMAntiMedIso_PileupUP = getDataset(h300a11_MedIsoMu2_TauDMAntiMedIso_PileupUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a13_MedIsoMu2_TauDMAntiMedIso_Central = getDataset(h300a13_MedIsoMu2_TauDMAntiMedIso_Central, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a13_MedIsoMu2_TauDMAntiMedIso_IDDOWN = getDataset(h300a13_MedIsoMu2_TauDMAntiMedIso_IDDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a13_MedIsoMu2_TauDMAntiMedIso_IDUP = getDataset(h300a13_MedIsoMu2_TauDMAntiMedIso_IDUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a13_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = getDataset(h300a13_MedIsoMu2_TauDMAntiMedIso_IsoDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a13_MedIsoMu2_TauDMAntiMedIso_IsoUP = getDataset(h300a13_MedIsoMu2_TauDMAntiMedIso_IsoUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a13_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = getDataset(h300a13_MedIsoMu2_TauDMAntiMedIso_BTagDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a13_MedIsoMu2_TauDMAntiMedIso_BTagUP = getDataset(h300a13_MedIsoMu2_TauDMAntiMedIso_BTagUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a13_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = getDataset(h300a13_MedIsoMu2_TauDMAntiMedIso_PileupDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a13_MedIsoMu2_TauDMAntiMedIso_PileupUP = getDataset(h300a13_MedIsoMu2_TauDMAntiMedIso_PileupUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a15_MedIsoMu2_TauDMAntiMedIso_Central = getDataset(h300a15_MedIsoMu2_TauDMAntiMedIso_Central, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a15_MedIsoMu2_TauDMAntiMedIso_IDDOWN = getDataset(h300a15_MedIsoMu2_TauDMAntiMedIso_IDDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a15_MedIsoMu2_TauDMAntiMedIso_IDUP = getDataset(h300a15_MedIsoMu2_TauDMAntiMedIso_IDUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a15_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = getDataset(h300a15_MedIsoMu2_TauDMAntiMedIso_IsoDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a15_MedIsoMu2_TauDMAntiMedIso_IsoUP = getDataset(h300a15_MedIsoMu2_TauDMAntiMedIso_IsoUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a15_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = getDataset(h300a15_MedIsoMu2_TauDMAntiMedIso_BTagDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a15_MedIsoMu2_TauDMAntiMedIso_BTagUP = getDataset(h300a15_MedIsoMu2_TauDMAntiMedIso_BTagUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a15_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = getDataset(h300a15_MedIsoMu2_TauDMAntiMedIso_PileupDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a15_MedIsoMu2_TauDMAntiMedIso_PileupUP = getDataset(h300a15_MedIsoMu2_TauDMAntiMedIso_PileupUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a17_MedIsoMu2_TauDMAntiMedIso_Central = getDataset(h300a17_MedIsoMu2_TauDMAntiMedIso_Central, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a17_MedIsoMu2_TauDMAntiMedIso_IDDOWN = getDataset(h300a17_MedIsoMu2_TauDMAntiMedIso_IDDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a17_MedIsoMu2_TauDMAntiMedIso_IDUP = getDataset(h300a17_MedIsoMu2_TauDMAntiMedIso_IDUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a17_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = getDataset(h300a17_MedIsoMu2_TauDMAntiMedIso_IsoDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a17_MedIsoMu2_TauDMAntiMedIso_IsoUP = getDataset(h300a17_MedIsoMu2_TauDMAntiMedIso_IsoUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a17_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = getDataset(h300a17_MedIsoMu2_TauDMAntiMedIso_BTagDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a17_MedIsoMu2_TauDMAntiMedIso_BTagUP = getDataset(h300a17_MedIsoMu2_TauDMAntiMedIso_BTagUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a17_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = getDataset(h300a17_MedIsoMu2_TauDMAntiMedIso_PileupDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a17_MedIsoMu2_TauDMAntiMedIso_PileupUP = getDataset(h300a17_MedIsoMu2_TauDMAntiMedIso_PileupUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a19_MedIsoMu2_TauDMAntiMedIso_Central = getDataset(h300a19_MedIsoMu2_TauDMAntiMedIso_Central, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a19_MedIsoMu2_TauDMAntiMedIso_IDDOWN = getDataset(h300a19_MedIsoMu2_TauDMAntiMedIso_IDDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a19_MedIsoMu2_TauDMAntiMedIso_IDUP = getDataset(h300a19_MedIsoMu2_TauDMAntiMedIso_IDUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a19_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = getDataset(h300a19_MedIsoMu2_TauDMAntiMedIso_IsoDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a19_MedIsoMu2_TauDMAntiMedIso_IsoUP = getDataset(h300a19_MedIsoMu2_TauDMAntiMedIso_IsoUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a19_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = getDataset(h300a19_MedIsoMu2_TauDMAntiMedIso_BTagDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a19_MedIsoMu2_TauDMAntiMedIso_BTagUP = getDataset(h300a19_MedIsoMu2_TauDMAntiMedIso_BTagUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a19_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = getDataset(h300a19_MedIsoMu2_TauDMAntiMedIso_PileupDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a19_MedIsoMu2_TauDMAntiMedIso_PileupUP = getDataset(h300a19_MedIsoMu2_TauDMAntiMedIso_PileupUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a21_MedIsoMu2_TauDMAntiMedIso_Central = getDataset(h300a21_MedIsoMu2_TauDMAntiMedIso_Central, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a21_MedIsoMu2_TauDMAntiMedIso_IDDOWN = getDataset(h300a21_MedIsoMu2_TauDMAntiMedIso_IDDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a21_MedIsoMu2_TauDMAntiMedIso_IDUP = getDataset(h300a21_MedIsoMu2_TauDMAntiMedIso_IDUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a21_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = getDataset(h300a21_MedIsoMu2_TauDMAntiMedIso_IsoDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a21_MedIsoMu2_TauDMAntiMedIso_IsoUP = getDataset(h300a21_MedIsoMu2_TauDMAntiMedIso_IsoUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a21_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = getDataset(h300a21_MedIsoMu2_TauDMAntiMedIso_BTagDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a21_MedIsoMu2_TauDMAntiMedIso_BTagUP = getDataset(h300a21_MedIsoMu2_TauDMAntiMedIso_BTagUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a21_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = getDataset(h300a21_MedIsoMu2_TauDMAntiMedIso_PileupDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a21_MedIsoMu2_TauDMAntiMedIso_PileupUP = getDataset(h300a21_MedIsoMu2_TauDMAntiMedIso_PileupUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a5_MedIsoMu2_TauDMAntiMedIso_Central = getDataset(h300a5_MedIsoMu2_TauDMAntiMedIso_Central, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a5_MedIsoMu2_TauDMAntiMedIso_IDDOWN = getDataset(h300a5_MedIsoMu2_TauDMAntiMedIso_IDDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a5_MedIsoMu2_TauDMAntiMedIso_IDUP = getDataset(h300a5_MedIsoMu2_TauDMAntiMedIso_IDUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a5_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = getDataset(h300a5_MedIsoMu2_TauDMAntiMedIso_IsoDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a5_MedIsoMu2_TauDMAntiMedIso_IsoUP = getDataset(h300a5_MedIsoMu2_TauDMAntiMedIso_IsoUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a5_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = getDataset(h300a5_MedIsoMu2_TauDMAntiMedIso_BTagDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a5_MedIsoMu2_TauDMAntiMedIso_BTagUP = getDataset(h300a5_MedIsoMu2_TauDMAntiMedIso_BTagUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a5_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = getDataset(h300a5_MedIsoMu2_TauDMAntiMedIso_PileupDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a5_MedIsoMu2_TauDMAntiMedIso_PileupUP = getDataset(h300a5_MedIsoMu2_TauDMAntiMedIso_PileupUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a7_MedIsoMu2_TauDMAntiMedIso_Central = getDataset(h300a7_MedIsoMu2_TauDMAntiMedIso_Central, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a7_MedIsoMu2_TauDMAntiMedIso_IDDOWN = getDataset(h300a7_MedIsoMu2_TauDMAntiMedIso_IDDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a7_MedIsoMu2_TauDMAntiMedIso_IDUP = getDataset(h300a7_MedIsoMu2_TauDMAntiMedIso_IDUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a7_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = getDataset(h300a7_MedIsoMu2_TauDMAntiMedIso_IsoDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a7_MedIsoMu2_TauDMAntiMedIso_IsoUP = getDataset(h300a7_MedIsoMu2_TauDMAntiMedIso_IsoUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a7_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = getDataset(h300a7_MedIsoMu2_TauDMAntiMedIso_BTagDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a7_MedIsoMu2_TauDMAntiMedIso_BTagUP = getDataset(h300a7_MedIsoMu2_TauDMAntiMedIso_BTagUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a7_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = getDataset(h300a7_MedIsoMu2_TauDMAntiMedIso_PileupDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a7_MedIsoMu2_TauDMAntiMedIso_PileupUP = getDataset(h300a7_MedIsoMu2_TauDMAntiMedIso_PileupUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a9_MedIsoMu2_TauDMAntiMedIso_Central = getDataset(h300a9_MedIsoMu2_TauDMAntiMedIso_Central, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a9_MedIsoMu2_TauDMAntiMedIso_IDDOWN = getDataset(h300a9_MedIsoMu2_TauDMAntiMedIso_IDDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a9_MedIsoMu2_TauDMAntiMedIso_IDUP = getDataset(h300a9_MedIsoMu2_TauDMAntiMedIso_IDUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a9_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = getDataset(h300a9_MedIsoMu2_TauDMAntiMedIso_IsoDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a9_MedIsoMu2_TauDMAntiMedIso_IsoUP = getDataset(h300a9_MedIsoMu2_TauDMAntiMedIso_IsoUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a9_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = getDataset(h300a9_MedIsoMu2_TauDMAntiMedIso_BTagDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a9_MedIsoMu2_TauDMAntiMedIso_BTagUP = getDataset(h300a9_MedIsoMu2_TauDMAntiMedIso_BTagUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a9_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = getDataset(h300a9_MedIsoMu2_TauDMAntiMedIso_PileupDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h300a9_MedIsoMu2_TauDMAntiMedIso_PileupUP = getDataset(h300a9_MedIsoMu2_TauDMAntiMedIso_PileupUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a11_MedIsoMu2_TauDMAntiMedIso_Central = getDataset(h750a11_MedIsoMu2_TauDMAntiMedIso_Central, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a11_MedIsoMu2_TauDMAntiMedIso_IDDOWN = getDataset(h750a11_MedIsoMu2_TauDMAntiMedIso_IDDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a11_MedIsoMu2_TauDMAntiMedIso_IDUP = getDataset(h750a11_MedIsoMu2_TauDMAntiMedIso_IDUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a11_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = getDataset(h750a11_MedIsoMu2_TauDMAntiMedIso_IsoDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a11_MedIsoMu2_TauDMAntiMedIso_IsoUP = getDataset(h750a11_MedIsoMu2_TauDMAntiMedIso_IsoUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a11_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = getDataset(h750a11_MedIsoMu2_TauDMAntiMedIso_BTagDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a11_MedIsoMu2_TauDMAntiMedIso_BTagUP = getDataset(h750a11_MedIsoMu2_TauDMAntiMedIso_BTagUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a11_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = getDataset(h750a11_MedIsoMu2_TauDMAntiMedIso_PileupDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a11_MedIsoMu2_TauDMAntiMedIso_PileupUP = getDataset(h750a11_MedIsoMu2_TauDMAntiMedIso_PileupUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a13_MedIsoMu2_TauDMAntiMedIso_Central = getDataset(h750a13_MedIsoMu2_TauDMAntiMedIso_Central, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a13_MedIsoMu2_TauDMAntiMedIso_IDDOWN = getDataset(h750a13_MedIsoMu2_TauDMAntiMedIso_IDDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a13_MedIsoMu2_TauDMAntiMedIso_IDUP = getDataset(h750a13_MedIsoMu2_TauDMAntiMedIso_IDUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a13_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = getDataset(h750a13_MedIsoMu2_TauDMAntiMedIso_IsoDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a13_MedIsoMu2_TauDMAntiMedIso_IsoUP = getDataset(h750a13_MedIsoMu2_TauDMAntiMedIso_IsoUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a13_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = getDataset(h750a13_MedIsoMu2_TauDMAntiMedIso_BTagDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a13_MedIsoMu2_TauDMAntiMedIso_BTagUP = getDataset(h750a13_MedIsoMu2_TauDMAntiMedIso_BTagUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a13_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = getDataset(h750a13_MedIsoMu2_TauDMAntiMedIso_PileupDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a13_MedIsoMu2_TauDMAntiMedIso_PileupUP = getDataset(h750a13_MedIsoMu2_TauDMAntiMedIso_PileupUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a15_MedIsoMu2_TauDMAntiMedIso_Central = getDataset(h750a15_MedIsoMu2_TauDMAntiMedIso_Central, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a15_MedIsoMu2_TauDMAntiMedIso_IDDOWN = getDataset(h750a15_MedIsoMu2_TauDMAntiMedIso_IDDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a15_MedIsoMu2_TauDMAntiMedIso_IDUP = getDataset(h750a15_MedIsoMu2_TauDMAntiMedIso_IDUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a15_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = getDataset(h750a15_MedIsoMu2_TauDMAntiMedIso_IsoDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a15_MedIsoMu2_TauDMAntiMedIso_IsoUP = getDataset(h750a15_MedIsoMu2_TauDMAntiMedIso_IsoUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a15_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = getDataset(h750a15_MedIsoMu2_TauDMAntiMedIso_BTagDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a15_MedIsoMu2_TauDMAntiMedIso_BTagUP = getDataset(h750a15_MedIsoMu2_TauDMAntiMedIso_BTagUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a15_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = getDataset(h750a15_MedIsoMu2_TauDMAntiMedIso_PileupDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a15_MedIsoMu2_TauDMAntiMedIso_PileupUP = getDataset(h750a15_MedIsoMu2_TauDMAntiMedIso_PileupUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a17_MedIsoMu2_TauDMAntiMedIso_Central = getDataset(h750a17_MedIsoMu2_TauDMAntiMedIso_Central, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a17_MedIsoMu2_TauDMAntiMedIso_IDDOWN = getDataset(h750a17_MedIsoMu2_TauDMAntiMedIso_IDDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a17_MedIsoMu2_TauDMAntiMedIso_IDUP = getDataset(h750a17_MedIsoMu2_TauDMAntiMedIso_IDUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a17_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = getDataset(h750a17_MedIsoMu2_TauDMAntiMedIso_IsoDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a17_MedIsoMu2_TauDMAntiMedIso_IsoUP = getDataset(h750a17_MedIsoMu2_TauDMAntiMedIso_IsoUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a17_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = getDataset(h750a17_MedIsoMu2_TauDMAntiMedIso_BTagDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a17_MedIsoMu2_TauDMAntiMedIso_BTagUP = getDataset(h750a17_MedIsoMu2_TauDMAntiMedIso_BTagUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a17_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = getDataset(h750a17_MedIsoMu2_TauDMAntiMedIso_PileupDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a17_MedIsoMu2_TauDMAntiMedIso_PileupUP = getDataset(h750a17_MedIsoMu2_TauDMAntiMedIso_PileupUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a19_MedIsoMu2_TauDMAntiMedIso_Central = getDataset(h750a19_MedIsoMu2_TauDMAntiMedIso_Central, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a19_MedIsoMu2_TauDMAntiMedIso_IDDOWN = getDataset(h750a19_MedIsoMu2_TauDMAntiMedIso_IDDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a19_MedIsoMu2_TauDMAntiMedIso_IDUP = getDataset(h750a19_MedIsoMu2_TauDMAntiMedIso_IDUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a19_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = getDataset(h750a19_MedIsoMu2_TauDMAntiMedIso_IsoDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a19_MedIsoMu2_TauDMAntiMedIso_IsoUP = getDataset(h750a19_MedIsoMu2_TauDMAntiMedIso_IsoUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a19_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = getDataset(h750a19_MedIsoMu2_TauDMAntiMedIso_BTagDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a19_MedIsoMu2_TauDMAntiMedIso_BTagUP = getDataset(h750a19_MedIsoMu2_TauDMAntiMedIso_BTagUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a19_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = getDataset(h750a19_MedIsoMu2_TauDMAntiMedIso_PileupDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a19_MedIsoMu2_TauDMAntiMedIso_PileupUP = getDataset(h750a19_MedIsoMu2_TauDMAntiMedIso_PileupUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a21_MedIsoMu2_TauDMAntiMedIso_Central = getDataset(h750a21_MedIsoMu2_TauDMAntiMedIso_Central, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a21_MedIsoMu2_TauDMAntiMedIso_IDDOWN = getDataset(h750a21_MedIsoMu2_TauDMAntiMedIso_IDDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a21_MedIsoMu2_TauDMAntiMedIso_IDUP = getDataset(h750a21_MedIsoMu2_TauDMAntiMedIso_IDUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a21_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = getDataset(h750a21_MedIsoMu2_TauDMAntiMedIso_IsoDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a21_MedIsoMu2_TauDMAntiMedIso_IsoUP = getDataset(h750a21_MedIsoMu2_TauDMAntiMedIso_IsoUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a21_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = getDataset(h750a21_MedIsoMu2_TauDMAntiMedIso_BTagDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a21_MedIsoMu2_TauDMAntiMedIso_BTagUP = getDataset(h750a21_MedIsoMu2_TauDMAntiMedIso_BTagUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a21_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = getDataset(h750a21_MedIsoMu2_TauDMAntiMedIso_PileupDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a21_MedIsoMu2_TauDMAntiMedIso_PileupUP = getDataset(h750a21_MedIsoMu2_TauDMAntiMedIso_PileupUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a5_MedIsoMu2_TauDMAntiMedIso_Central = getDataset(h750a5_MedIsoMu2_TauDMAntiMedIso_Central, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a5_MedIsoMu2_TauDMAntiMedIso_IDDOWN = getDataset(h750a5_MedIsoMu2_TauDMAntiMedIso_IDDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a5_MedIsoMu2_TauDMAntiMedIso_IDUP = getDataset(h750a5_MedIsoMu2_TauDMAntiMedIso_IDUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a5_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = getDataset(h750a5_MedIsoMu2_TauDMAntiMedIso_IsoDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a5_MedIsoMu2_TauDMAntiMedIso_IsoUP = getDataset(h750a5_MedIsoMu2_TauDMAntiMedIso_IsoUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a5_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = getDataset(h750a5_MedIsoMu2_TauDMAntiMedIso_BTagDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a5_MedIsoMu2_TauDMAntiMedIso_BTagUP = getDataset(h750a5_MedIsoMu2_TauDMAntiMedIso_BTagUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a5_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = getDataset(h750a5_MedIsoMu2_TauDMAntiMedIso_PileupDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a5_MedIsoMu2_TauDMAntiMedIso_PileupUP = getDataset(h750a5_MedIsoMu2_TauDMAntiMedIso_PileupUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a7_MedIsoMu2_TauDMAntiMedIso_Central = getDataset(h750a7_MedIsoMu2_TauDMAntiMedIso_Central, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a7_MedIsoMu2_TauDMAntiMedIso_IDDOWN = getDataset(h750a7_MedIsoMu2_TauDMAntiMedIso_IDDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a7_MedIsoMu2_TauDMAntiMedIso_IDUP = getDataset(h750a7_MedIsoMu2_TauDMAntiMedIso_IDUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a7_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = getDataset(h750a7_MedIsoMu2_TauDMAntiMedIso_IsoDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a7_MedIsoMu2_TauDMAntiMedIso_IsoUP = getDataset(h750a7_MedIsoMu2_TauDMAntiMedIso_IsoUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a7_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = getDataset(h750a7_MedIsoMu2_TauDMAntiMedIso_BTagDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a7_MedIsoMu2_TauDMAntiMedIso_BTagUP = getDataset(h750a7_MedIsoMu2_TauDMAntiMedIso_BTagUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a7_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = getDataset(h750a7_MedIsoMu2_TauDMAntiMedIso_PileupDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a7_MedIsoMu2_TauDMAntiMedIso_PileupUP = getDataset(h750a7_MedIsoMu2_TauDMAntiMedIso_PileupUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a9_MedIsoMu2_TauDMAntiMedIso_Central = getDataset(h750a9_MedIsoMu2_TauDMAntiMedIso_Central, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a9_MedIsoMu2_TauDMAntiMedIso_IDDOWN = getDataset(h750a9_MedIsoMu2_TauDMAntiMedIso_IDDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a9_MedIsoMu2_TauDMAntiMedIso_IDUP = getDataset(h750a9_MedIsoMu2_TauDMAntiMedIso_IDUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a9_MedIsoMu2_TauDMAntiMedIso_IsoDOWN = getDataset(h750a9_MedIsoMu2_TauDMAntiMedIso_IsoDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a9_MedIsoMu2_TauDMAntiMedIso_IsoUP = getDataset(h750a9_MedIsoMu2_TauDMAntiMedIso_IsoUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a9_MedIsoMu2_TauDMAntiMedIso_BTagDOWN = getDataset(h750a9_MedIsoMu2_TauDMAntiMedIso_BTagDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a9_MedIsoMu2_TauDMAntiMedIso_BTagUP = getDataset(h750a9_MedIsoMu2_TauDMAntiMedIso_BTagUP, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a9_MedIsoMu2_TauDMAntiMedIso_PileupDOWN = getDataset(h750a9_MedIsoMu2_TauDMAntiMedIso_PileupDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
   h750a9_MedIsoMu2_TauDMAntiMedIso_PileupUP = getDataset(h750a9_MedIsoMu2_TauDMAntiMedIso_PileupUP, selection='x <= 25 && x >= 4', xRange=xRange)

   dictionary['FP']['']['HToAAH125A11'] = h125a11_MedIsoMu2_TauDMAntiMedIso_Central
   dictionary['FP']['']['HToAAH125A13'] = h125a13_MedIsoMu2_TauDMAntiMedIso_Central
   dictionary['FP']['']['HToAAH125A15'] = h125a15_MedIsoMu2_TauDMAntiMedIso_Central
   dictionary['FP']['']['HToAAH125A17'] = h125a17_MedIsoMu2_TauDMAntiMedIso_Central
   dictionary['FP']['']['HToAAH125A19'] = h125a19_MedIsoMu2_TauDMAntiMedIso_Central
   dictionary['FP']['']['HToAAH125A21'] = h125a21_MedIsoMu2_TauDMAntiMedIso_Central
   dictionary['FP']['']['HToAAH125A5'] = h125a5_MedIsoMu2_TauDMAntiMedIso_Central
   dictionary['FP']['']['HToAAH125A7'] = h125a7_MedIsoMu2_TauDMAntiMedIso_Central
   dictionary['FP']['']['HToAAH125A9'] = h125a9_MedIsoMu2_TauDMAntiMedIso_Central
   dictionary['FP']['']['HToAAH300A11'] = h300a11_MedIsoMu2_TauDMAntiMedIso_Central
   dictionary['FP']['']['HToAAH300A13'] = h300a13_MedIsoMu2_TauDMAntiMedIso_Central
   dictionary['FP']['']['HToAAH300A15'] = h300a15_MedIsoMu2_TauDMAntiMedIso_Central
   dictionary['FP']['']['HToAAH300A17'] = h300a17_MedIsoMu2_TauDMAntiMedIso_Central
   dictionary['FP']['']['HToAAH300A19'] = h300a19_MedIsoMu2_TauDMAntiMedIso_Central
   dictionary['FP']['']['HToAAH300A21'] = h300a21_MedIsoMu2_TauDMAntiMedIso_Central
   dictionary['FP']['']['HToAAH300A5'] = h300a5_MedIsoMu2_TauDMAntiMedIso_Central
   dictionary['FP']['']['HToAAH300A7'] = h300a7_MedIsoMu2_TauDMAntiMedIso_Central
   dictionary['FP']['']['HToAAH300A9'] = h300a9_MedIsoMu2_TauDMAntiMedIso_Central
   dictionary['FP']['']['HToAAH750A11'] = h750a11_MedIsoMu2_TauDMAntiMedIso_Central
   dictionary['FP']['']['HToAAH750A13'] = h750a13_MedIsoMu2_TauDMAntiMedIso_Central
   dictionary['FP']['']['HToAAH750A15'] = h750a15_MedIsoMu2_TauDMAntiMedIso_Central
   dictionary['FP']['']['HToAAH750A17'] = h750a17_MedIsoMu2_TauDMAntiMedIso_Central
   dictionary['FP']['']['HToAAH750A19'] = h750a19_MedIsoMu2_TauDMAntiMedIso_Central
   dictionary['FP']['']['HToAAH750A21'] = h750a21_MedIsoMu2_TauDMAntiMedIso_Central
   dictionary['FP']['']['HToAAH750A5'] = h750a5_MedIsoMu2_TauDMAntiMedIso_Central
   dictionary['FP']['']['HToAAH750A7'] = h750a7_MedIsoMu2_TauDMAntiMedIso_Central
   dictionary['FP']['']['HToAAH750A9'] = h750a9_MedIsoMu2_TauDMAntiMedIso_Central
   dictionary['FP']['IDUp']['HToAAH125A11'] = h125a11_MedIsoMu2_TauDMAntiMedIso_IDUP
   dictionary['FP']['IDUp']['HToAAH125A13'] = h125a13_MedIsoMu2_TauDMAntiMedIso_IDUP
   dictionary['FP']['IDUp']['HToAAH125A15'] = h125a15_MedIsoMu2_TauDMAntiMedIso_IDUP
   dictionary['FP']['IDUp']['HToAAH125A17'] = h125a17_MedIsoMu2_TauDMAntiMedIso_IDUP
   dictionary['FP']['IDUp']['HToAAH125A19'] = h125a19_MedIsoMu2_TauDMAntiMedIso_IDUP
   dictionary['FP']['IDUp']['HToAAH125A21'] = h125a21_MedIsoMu2_TauDMAntiMedIso_IDUP
   dictionary['FP']['IDUp']['HToAAH125A5'] = h125a5_MedIsoMu2_TauDMAntiMedIso_IDUP
   dictionary['FP']['IDUp']['HToAAH125A7'] = h125a7_MedIsoMu2_TauDMAntiMedIso_IDUP
   dictionary['FP']['IDUp']['HToAAH125A9'] = h125a9_MedIsoMu2_TauDMAntiMedIso_IDUP
   dictionary['FP']['IDUp']['HToAAH300A11'] = h300a11_MedIsoMu2_TauDMAntiMedIso_IDUP
   dictionary['FP']['IDUp']['HToAAH300A13'] = h300a13_MedIsoMu2_TauDMAntiMedIso_IDUP
   dictionary['FP']['IDUp']['HToAAH300A15'] = h300a15_MedIsoMu2_TauDMAntiMedIso_IDUP
   dictionary['FP']['IDUp']['HToAAH300A17'] = h300a17_MedIsoMu2_TauDMAntiMedIso_IDUP
   dictionary['FP']['IDUp']['HToAAH300A19'] = h300a19_MedIsoMu2_TauDMAntiMedIso_IDUP
   dictionary['FP']['IDUp']['HToAAH300A21'] = h300a21_MedIsoMu2_TauDMAntiMedIso_IDUP
   dictionary['FP']['IDUp']['HToAAH300A5'] = h300a5_MedIsoMu2_TauDMAntiMedIso_IDUP
   dictionary['FP']['IDUp']['HToAAH300A7'] = h300a7_MedIsoMu2_TauDMAntiMedIso_IDUP
   dictionary['FP']['IDUp']['HToAAH300A9'] = h300a9_MedIsoMu2_TauDMAntiMedIso_IDUP
   dictionary['FP']['IDUp']['HToAAH750A11'] = h750a11_MedIsoMu2_TauDMAntiMedIso_IDUP
   dictionary['FP']['IDUp']['HToAAH750A13'] = h750a13_MedIsoMu2_TauDMAntiMedIso_IDUP
   dictionary['FP']['IDUp']['HToAAH750A15'] = h750a15_MedIsoMu2_TauDMAntiMedIso_IDUP
   dictionary['FP']['IDUp']['HToAAH750A17'] = h750a17_MedIsoMu2_TauDMAntiMedIso_IDUP
   dictionary['FP']['IDUp']['HToAAH750A19'] = h750a19_MedIsoMu2_TauDMAntiMedIso_IDUP
   dictionary['FP']['IDUp']['HToAAH750A21'] = h750a21_MedIsoMu2_TauDMAntiMedIso_IDUP
   dictionary['FP']['IDUp']['HToAAH750A5'] = h750a5_MedIsoMu2_TauDMAntiMedIso_IDUP
   dictionary['FP']['IDUp']['HToAAH750A7'] = h750a7_MedIsoMu2_TauDMAntiMedIso_IDUP
   dictionary['FP']['IDUp']['HToAAH750A9'] = h750a9_MedIsoMu2_TauDMAntiMedIso_IDUP
   dictionary['FP']['IDDown']['HToAAH125A11'] = h125a11_MedIsoMu2_TauDMAntiMedIso_IDDOWN
   dictionary['FP']['IDDown']['HToAAH125A13'] = h125a13_MedIsoMu2_TauDMAntiMedIso_IDDOWN
   dictionary['FP']['IDDown']['HToAAH125A15'] = h125a15_MedIsoMu2_TauDMAntiMedIso_IDDOWN
   dictionary['FP']['IDDown']['HToAAH125A17'] = h125a17_MedIsoMu2_TauDMAntiMedIso_IDDOWN
   dictionary['FP']['IDDown']['HToAAH125A19'] = h125a19_MedIsoMu2_TauDMAntiMedIso_IDDOWN
   dictionary['FP']['IDDown']['HToAAH125A21'] = h125a21_MedIsoMu2_TauDMAntiMedIso_IDDOWN
   dictionary['FP']['IDDown']['HToAAH125A5'] = h125a5_MedIsoMu2_TauDMAntiMedIso_IDDOWN
   dictionary['FP']['IDDown']['HToAAH125A7'] = h125a7_MedIsoMu2_TauDMAntiMedIso_IDDOWN
   dictionary['FP']['IDDown']['HToAAH125A9'] = h125a9_MedIsoMu2_TauDMAntiMedIso_IDDOWN
   dictionary['FP']['IDDown']['HToAAH300A11'] = h300a11_MedIsoMu2_TauDMAntiMedIso_IDDOWN
   dictionary['FP']['IDDown']['HToAAH300A13'] = h300a13_MedIsoMu2_TauDMAntiMedIso_IDDOWN
   dictionary['FP']['IDDown']['HToAAH300A15'] = h300a15_MedIsoMu2_TauDMAntiMedIso_IDDOWN
   dictionary['FP']['IDDown']['HToAAH300A17'] = h300a17_MedIsoMu2_TauDMAntiMedIso_IDDOWN
   dictionary['FP']['IDDown']['HToAAH300A19'] = h300a19_MedIsoMu2_TauDMAntiMedIso_IDDOWN
   dictionary['FP']['IDDown']['HToAAH300A21'] = h300a21_MedIsoMu2_TauDMAntiMedIso_IDDOWN
   dictionary['FP']['IDDown']['HToAAH300A5'] = h300a5_MedIsoMu2_TauDMAntiMedIso_IDDOWN
   dictionary['FP']['IDDown']['HToAAH300A7'] = h300a7_MedIsoMu2_TauDMAntiMedIso_IDDOWN
   dictionary['FP']['IDDown']['HToAAH300A9'] = h300a9_MedIsoMu2_TauDMAntiMedIso_IDDOWN
   dictionary['FP']['IDDown']['HToAAH750A11'] = h750a11_MedIsoMu2_TauDMAntiMedIso_IDDOWN
   dictionary['FP']['IDDown']['HToAAH750A13'] = h750a13_MedIsoMu2_TauDMAntiMedIso_IDDOWN
   dictionary['FP']['IDDown']['HToAAH750A15'] = h750a15_MedIsoMu2_TauDMAntiMedIso_IDDOWN
   dictionary['FP']['IDDown']['HToAAH750A17'] = h750a17_MedIsoMu2_TauDMAntiMedIso_IDDOWN
   dictionary['FP']['IDDown']['HToAAH750A19'] = h750a19_MedIsoMu2_TauDMAntiMedIso_IDDOWN
   dictionary['FP']['IDDown']['HToAAH750A21'] = h750a21_MedIsoMu2_TauDMAntiMedIso_IDDOWN
   dictionary['FP']['IDDown']['HToAAH750A5'] = h750a5_MedIsoMu2_TauDMAntiMedIso_IDDOWN
   dictionary['FP']['IDDown']['HToAAH750A7'] = h750a7_MedIsoMu2_TauDMAntiMedIso_IDDOWN
   dictionary['FP']['IDDown']['HToAAH750A9'] = h750a9_MedIsoMu2_TauDMAntiMedIso_IDDOWN
   dictionary['FP']['IsoUp']['HToAAH125A11'] = h125a11_MedIsoMu2_TauDMAntiMedIso_IsoUP
   dictionary['FP']['IsoUp']['HToAAH125A13'] = h125a13_MedIsoMu2_TauDMAntiMedIso_IsoUP
   dictionary['FP']['IsoUp']['HToAAH125A15'] = h125a15_MedIsoMu2_TauDMAntiMedIso_IsoUP
   dictionary['FP']['IsoUp']['HToAAH125A17'] = h125a17_MedIsoMu2_TauDMAntiMedIso_IsoUP
   dictionary['FP']['IsoUp']['HToAAH125A19'] = h125a19_MedIsoMu2_TauDMAntiMedIso_IsoUP
   dictionary['FP']['IsoUp']['HToAAH125A21'] = h125a21_MedIsoMu2_TauDMAntiMedIso_IsoUP
   dictionary['FP']['IsoUp']['HToAAH125A5'] = h125a5_MedIsoMu2_TauDMAntiMedIso_IsoUP
   dictionary['FP']['IsoUp']['HToAAH125A7'] = h125a7_MedIsoMu2_TauDMAntiMedIso_IsoUP
   dictionary['FP']['IsoUp']['HToAAH125A9'] = h125a9_MedIsoMu2_TauDMAntiMedIso_IsoUP
   dictionary['FP']['IsoUp']['HToAAH300A11'] = h300a11_MedIsoMu2_TauDMAntiMedIso_IsoUP
   dictionary['FP']['IsoUp']['HToAAH300A13'] = h300a13_MedIsoMu2_TauDMAntiMedIso_IsoUP
   dictionary['FP']['IsoUp']['HToAAH300A15'] = h300a15_MedIsoMu2_TauDMAntiMedIso_IsoUP
   dictionary['FP']['IsoUp']['HToAAH300A17'] = h300a17_MedIsoMu2_TauDMAntiMedIso_IsoUP
   dictionary['FP']['IsoUp']['HToAAH300A19'] = h300a19_MedIsoMu2_TauDMAntiMedIso_IsoUP
   dictionary['FP']['IsoUp']['HToAAH300A21'] = h300a21_MedIsoMu2_TauDMAntiMedIso_IsoUP
   dictionary['FP']['IsoUp']['HToAAH300A5'] = h300a5_MedIsoMu2_TauDMAntiMedIso_IsoUP
   dictionary['FP']['IsoUp']['HToAAH300A7'] = h300a7_MedIsoMu2_TauDMAntiMedIso_IsoUP
   dictionary['FP']['IsoUp']['HToAAH300A9'] = h300a9_MedIsoMu2_TauDMAntiMedIso_IsoUP
   dictionary['FP']['IsoUp']['HToAAH750A11'] = h750a11_MedIsoMu2_TauDMAntiMedIso_IsoUP
   dictionary['FP']['IsoUp']['HToAAH750A13'] = h750a13_MedIsoMu2_TauDMAntiMedIso_IsoUP
   dictionary['FP']['IsoUp']['HToAAH750A15'] = h750a15_MedIsoMu2_TauDMAntiMedIso_IsoUP
   dictionary['FP']['IsoUp']['HToAAH750A17'] = h750a17_MedIsoMu2_TauDMAntiMedIso_IsoUP
   dictionary['FP']['IsoUp']['HToAAH750A19'] = h750a19_MedIsoMu2_TauDMAntiMedIso_IsoUP
   dictionary['FP']['IsoUp']['HToAAH750A21'] = h750a21_MedIsoMu2_TauDMAntiMedIso_IsoUP
   dictionary['FP']['IsoUp']['HToAAH750A5'] = h750a5_MedIsoMu2_TauDMAntiMedIso_IsoUP
   dictionary['FP']['IsoUp']['HToAAH750A7'] = h750a7_MedIsoMu2_TauDMAntiMedIso_IsoUP
   dictionary['FP']['IsoUp']['HToAAH750A9'] = h750a9_MedIsoMu2_TauDMAntiMedIso_IsoUP
   dictionary['FP']['BTagDown']['HToAAH125A11'] = h125a11_MedIsoMu2_TauDMAntiMedIso_BTagDOWN
   dictionary['FP']['BTagDown']['HToAAH125A13'] = h125a13_MedIsoMu2_TauDMAntiMedIso_BTagDOWN
   dictionary['FP']['BTagDown']['HToAAH125A15'] = h125a15_MedIsoMu2_TauDMAntiMedIso_BTagDOWN
   dictionary['FP']['BTagDown']['HToAAH125A17'] = h125a17_MedIsoMu2_TauDMAntiMedIso_BTagDOWN
   dictionary['FP']['BTagDown']['HToAAH125A19'] = h125a19_MedIsoMu2_TauDMAntiMedIso_BTagDOWN
   dictionary['FP']['BTagDown']['HToAAH125A21'] = h125a21_MedIsoMu2_TauDMAntiMedIso_BTagDOWN
   dictionary['FP']['BTagDown']['HToAAH125A5'] = h125a5_MedIsoMu2_TauDMAntiMedIso_BTagDOWN
   dictionary['FP']['BTagDown']['HToAAH125A7'] = h125a7_MedIsoMu2_TauDMAntiMedIso_BTagDOWN
   dictionary['FP']['BTagDown']['HToAAH125A9'] = h125a9_MedIsoMu2_TauDMAntiMedIso_BTagDOWN
   dictionary['FP']['BTagDown']['HToAAH300A11'] = h300a11_MedIsoMu2_TauDMAntiMedIso_BTagDOWN
   dictionary['FP']['BTagDown']['HToAAH300A13'] = h300a13_MedIsoMu2_TauDMAntiMedIso_BTagDOWN
   dictionary['FP']['BTagDown']['HToAAH300A15'] = h300a15_MedIsoMu2_TauDMAntiMedIso_BTagDOWN
   dictionary['FP']['BTagDown']['HToAAH300A17'] = h300a17_MedIsoMu2_TauDMAntiMedIso_BTagDOWN
   dictionary['FP']['BTagDown']['HToAAH300A19'] = h300a19_MedIsoMu2_TauDMAntiMedIso_BTagDOWN
   dictionary['FP']['BTagDown']['HToAAH300A21'] = h300a21_MedIsoMu2_TauDMAntiMedIso_BTagDOWN
   dictionary['FP']['BTagDown']['HToAAH300A5'] = h300a5_MedIsoMu2_TauDMAntiMedIso_BTagDOWN
   dictionary['FP']['BTagDown']['HToAAH300A7'] = h300a7_MedIsoMu2_TauDMAntiMedIso_BTagDOWN
   dictionary['FP']['BTagDown']['HToAAH300A9'] = h300a9_MedIsoMu2_TauDMAntiMedIso_BTagDOWN
   dictionary['FP']['BTagDown']['HToAAH750A11'] = h750a11_MedIsoMu2_TauDMAntiMedIso_BTagDOWN
   dictionary['FP']['BTagDown']['HToAAH750A13'] = h750a13_MedIsoMu2_TauDMAntiMedIso_BTagDOWN
   dictionary['FP']['BTagDown']['HToAAH750A15'] = h750a15_MedIsoMu2_TauDMAntiMedIso_BTagDOWN
   dictionary['FP']['BTagDown']['HToAAH750A17'] = h750a17_MedIsoMu2_TauDMAntiMedIso_BTagDOWN
   dictionary['FP']['BTagDown']['HToAAH750A19'] = h750a19_MedIsoMu2_TauDMAntiMedIso_BTagDOWN
   dictionary['FP']['BTagDown']['HToAAH750A21'] = h750a21_MedIsoMu2_TauDMAntiMedIso_BTagDOWN
   dictionary['FP']['BTagDown']['HToAAH750A5'] = h750a5_MedIsoMu2_TauDMAntiMedIso_BTagDOWN
   dictionary['FP']['BTagDown']['HToAAH750A7'] = h750a7_MedIsoMu2_TauDMAntiMedIso_BTagDOWN
   dictionary['FP']['BTagDown']['HToAAH750A9'] = h750a9_MedIsoMu2_TauDMAntiMedIso_BTagDOWN
   dictionary['FP']['BTagUp']['HToAAH125A11'] = h125a11_MedIsoMu2_TauDMAntiMedIso_BTagUP
   dictionary['FP']['BTagUp']['HToAAH125A13'] = h125a13_MedIsoMu2_TauDMAntiMedIso_BTagUP
   dictionary['FP']['BTagUp']['HToAAH125A15'] = h125a15_MedIsoMu2_TauDMAntiMedIso_BTagUP
   dictionary['FP']['BTagUp']['HToAAH125A17'] = h125a17_MedIsoMu2_TauDMAntiMedIso_BTagUP
   dictionary['FP']['BTagUp']['HToAAH125A19'] = h125a19_MedIsoMu2_TauDMAntiMedIso_BTagUP
   dictionary['FP']['BTagUp']['HToAAH125A21'] = h125a21_MedIsoMu2_TauDMAntiMedIso_BTagUP
   dictionary['FP']['BTagUp']['HToAAH125A5'] = h125a5_MedIsoMu2_TauDMAntiMedIso_BTagUP
   dictionary['FP']['BTagUp']['HToAAH125A7'] = h125a7_MedIsoMu2_TauDMAntiMedIso_BTagUP
   dictionary['FP']['BTagUp']['HToAAH125A9'] = h125a9_MedIsoMu2_TauDMAntiMedIso_BTagUP
   dictionary['FP']['BTagUp']['HToAAH300A11'] = h300a11_MedIsoMu2_TauDMAntiMedIso_BTagUP
   dictionary['FP']['BTagUp']['HToAAH300A13'] = h300a13_MedIsoMu2_TauDMAntiMedIso_BTagUP
   dictionary['FP']['BTagUp']['HToAAH300A15'] = h300a15_MedIsoMu2_TauDMAntiMedIso_BTagUP
   dictionary['FP']['BTagUp']['HToAAH300A17'] = h300a17_MedIsoMu2_TauDMAntiMedIso_BTagUP
   dictionary['FP']['BTagUp']['HToAAH300A19'] = h300a19_MedIsoMu2_TauDMAntiMedIso_BTagUP
   dictionary['FP']['BTagUp']['HToAAH300A21'] = h300a21_MedIsoMu2_TauDMAntiMedIso_BTagUP
   dictionary['FP']['BTagUp']['HToAAH300A5'] = h300a5_MedIsoMu2_TauDMAntiMedIso_BTagUP
   dictionary['FP']['BTagUp']['HToAAH300A7'] = h300a7_MedIsoMu2_TauDMAntiMedIso_BTagUP
   dictionary['FP']['BTagUp']['HToAAH300A9'] = h300a9_MedIsoMu2_TauDMAntiMedIso_BTagUP
   dictionary['FP']['BTagUp']['HToAAH750A11'] = h750a11_MedIsoMu2_TauDMAntiMedIso_BTagUP
   dictionary['FP']['BTagUp']['HToAAH750A13'] = h750a13_MedIsoMu2_TauDMAntiMedIso_BTagUP
   dictionary['FP']['BTagUp']['HToAAH750A15'] = h750a15_MedIsoMu2_TauDMAntiMedIso_BTagUP
   dictionary['FP']['BTagUp']['HToAAH750A17'] = h750a17_MedIsoMu2_TauDMAntiMedIso_BTagUP
   dictionary['FP']['BTagUp']['HToAAH750A19'] = h750a19_MedIsoMu2_TauDMAntiMedIso_BTagUP
   dictionary['FP']['BTagUp']['HToAAH750A21'] = h750a21_MedIsoMu2_TauDMAntiMedIso_BTagUP
   dictionary['FP']['BTagUp']['HToAAH750A5'] = h750a5_MedIsoMu2_TauDMAntiMedIso_BTagUP
   dictionary['FP']['BTagUp']['HToAAH750A7'] = h750a7_MedIsoMu2_TauDMAntiMedIso_BTagUP
   dictionary['FP']['BTagUp']['HToAAH750A9'] = h750a9_MedIsoMu2_TauDMAntiMedIso_BTagUP
   dictionary['FP']['IsoDown']['HToAAH125A11'] = h125a11_MedIsoMu2_TauDMAntiMedIso_IsoDOWN
   dictionary['FP']['IsoDown']['HToAAH125A13'] = h125a13_MedIsoMu2_TauDMAntiMedIso_IsoDOWN
   dictionary['FP']['IsoDown']['HToAAH125A15'] = h125a15_MedIsoMu2_TauDMAntiMedIso_IsoDOWN
   dictionary['FP']['IsoDown']['HToAAH125A17'] = h125a17_MedIsoMu2_TauDMAntiMedIso_IsoDOWN
   dictionary['FP']['IsoDown']['HToAAH125A19'] = h125a19_MedIsoMu2_TauDMAntiMedIso_IsoDOWN
   dictionary['FP']['IsoDown']['HToAAH125A21'] = h125a21_MedIsoMu2_TauDMAntiMedIso_IsoDOWN
   dictionary['FP']['IsoDown']['HToAAH125A5'] = h125a5_MedIsoMu2_TauDMAntiMedIso_IsoDOWN
   dictionary['FP']['IsoDown']['HToAAH125A7'] = h125a7_MedIsoMu2_TauDMAntiMedIso_IsoDOWN
   dictionary['FP']['IsoDown']['HToAAH125A9'] = h125a9_MedIsoMu2_TauDMAntiMedIso_IsoDOWN
   dictionary['FP']['IsoDown']['HToAAH300A11'] = h300a11_MedIsoMu2_TauDMAntiMedIso_IsoDOWN
   dictionary['FP']['IsoDown']['HToAAH300A13'] = h300a13_MedIsoMu2_TauDMAntiMedIso_IsoDOWN
   dictionary['FP']['IsoDown']['HToAAH300A15'] = h300a15_MedIsoMu2_TauDMAntiMedIso_IsoDOWN
   dictionary['FP']['IsoDown']['HToAAH300A17'] = h300a17_MedIsoMu2_TauDMAntiMedIso_IsoDOWN
   dictionary['FP']['IsoDown']['HToAAH300A19'] = h300a19_MedIsoMu2_TauDMAntiMedIso_IsoDOWN
   dictionary['FP']['IsoDown']['HToAAH300A21'] = h300a21_MedIsoMu2_TauDMAntiMedIso_IsoDOWN
   dictionary['FP']['IsoDown']['HToAAH300A5'] = h300a5_MedIsoMu2_TauDMAntiMedIso_IsoDOWN
   dictionary['FP']['IsoDown']['HToAAH300A7'] = h300a7_MedIsoMu2_TauDMAntiMedIso_IsoDOWN
   dictionary['FP']['IsoDown']['HToAAH300A9'] = h300a9_MedIsoMu2_TauDMAntiMedIso_IsoDOWN
   dictionary['FP']['IsoDown']['HToAAH750A11'] = h750a11_MedIsoMu2_TauDMAntiMedIso_IsoDOWN
   dictionary['FP']['IsoDown']['HToAAH750A13'] = h750a13_MedIsoMu2_TauDMAntiMedIso_IsoDOWN
   dictionary['FP']['IsoDown']['HToAAH750A15'] = h750a15_MedIsoMu2_TauDMAntiMedIso_IsoDOWN
   dictionary['FP']['IsoDown']['HToAAH750A17'] = h750a17_MedIsoMu2_TauDMAntiMedIso_IsoDOWN
   dictionary['FP']['IsoDown']['HToAAH750A19'] = h750a19_MedIsoMu2_TauDMAntiMedIso_IsoDOWN
   dictionary['FP']['IsoDown']['HToAAH750A21'] = h750a21_MedIsoMu2_TauDMAntiMedIso_IsoDOWN
   dictionary['FP']['IsoDown']['HToAAH750A5'] = h750a5_MedIsoMu2_TauDMAntiMedIso_IsoDOWN
   dictionary['FP']['IsoDown']['HToAAH750A7'] = h750a7_MedIsoMu2_TauDMAntiMedIso_IsoDOWN
   dictionary['FP']['IsoDown']['HToAAH750A9'] = h750a9_MedIsoMu2_TauDMAntiMedIso_IsoDOWN
   dictionary['FP']['PileupUp']['HToAAH125A11'] = h125a11_MedIsoMu2_TauDMAntiMedIso_PileupUP
   dictionary['FP']['PileupUp']['HToAAH125A13'] = h125a13_MedIsoMu2_TauDMAntiMedIso_PileupUP
   dictionary['FP']['PileupUp']['HToAAH125A15'] = h125a15_MedIsoMu2_TauDMAntiMedIso_PileupUP
   dictionary['FP']['PileupUp']['HToAAH125A17'] = h125a17_MedIsoMu2_TauDMAntiMedIso_PileupUP
   dictionary['FP']['PileupUp']['HToAAH125A19'] = h125a19_MedIsoMu2_TauDMAntiMedIso_PileupUP
   dictionary['FP']['PileupUp']['HToAAH125A21'] = h125a21_MedIsoMu2_TauDMAntiMedIso_PileupUP
   dictionary['FP']['PileupUp']['HToAAH125A5'] = h125a5_MedIsoMu2_TauDMAntiMedIso_PileupUP
   dictionary['FP']['PileupUp']['HToAAH125A7'] = h125a7_MedIsoMu2_TauDMAntiMedIso_PileupUP
   dictionary['FP']['PileupUp']['HToAAH125A9'] = h125a9_MedIsoMu2_TauDMAntiMedIso_PileupUP
   dictionary['FP']['PileupUp']['HToAAH300A11'] = h300a11_MedIsoMu2_TauDMAntiMedIso_PileupUP
   dictionary['FP']['PileupUp']['HToAAH300A13'] = h300a13_MedIsoMu2_TauDMAntiMedIso_PileupUP
   dictionary['FP']['PileupUp']['HToAAH300A15'] = h300a15_MedIsoMu2_TauDMAntiMedIso_PileupUP
   dictionary['FP']['PileupUp']['HToAAH300A17'] = h300a17_MedIsoMu2_TauDMAntiMedIso_PileupUP
   dictionary['FP']['PileupUp']['HToAAH300A19'] = h300a19_MedIsoMu2_TauDMAntiMedIso_PileupUP
   dictionary['FP']['PileupUp']['HToAAH300A21'] = h300a21_MedIsoMu2_TauDMAntiMedIso_PileupUP
   dictionary['FP']['PileupUp']['HToAAH300A5'] = h300a5_MedIsoMu2_TauDMAntiMedIso_PileupUP
   dictionary['FP']['PileupUp']['HToAAH300A7'] = h300a7_MedIsoMu2_TauDMAntiMedIso_PileupUP
   dictionary['FP']['PileupUp']['HToAAH300A9'] = h300a9_MedIsoMu2_TauDMAntiMedIso_PileupUP
   dictionary['FP']['PileupUp']['HToAAH750A11'] = h750a11_MedIsoMu2_TauDMAntiMedIso_PileupUP
   dictionary['FP']['PileupUp']['HToAAH750A13'] = h750a13_MedIsoMu2_TauDMAntiMedIso_PileupUP
   dictionary['FP']['PileupUp']['HToAAH750A15'] = h750a15_MedIsoMu2_TauDMAntiMedIso_PileupUP
   dictionary['FP']['PileupUp']['HToAAH750A17'] = h750a17_MedIsoMu2_TauDMAntiMedIso_PileupUP
   dictionary['FP']['PileupUp']['HToAAH750A19'] = h750a19_MedIsoMu2_TauDMAntiMedIso_PileupUP
   dictionary['FP']['PileupUp']['HToAAH750A21'] = h750a21_MedIsoMu2_TauDMAntiMedIso_PileupUP
   dictionary['FP']['PileupUp']['HToAAH750A5'] = h750a5_MedIsoMu2_TauDMAntiMedIso_PileupUP
   dictionary['FP']['PileupUp']['HToAAH750A7'] = h750a7_MedIsoMu2_TauDMAntiMedIso_PileupUP
   dictionary['FP']['PileupUp']['HToAAH750A9'] = h750a9_MedIsoMu2_TauDMAntiMedIso_PileupUP
   dictionary['FP']['PileupDown']['HToAAH125A11'] = h125a11_MedIsoMu2_TauDMAntiMedIso_PileupDOWN
   dictionary['FP']['PileupDown']['HToAAH125A13'] = h125a13_MedIsoMu2_TauDMAntiMedIso_PileupDOWN
   dictionary['FP']['PileupDown']['HToAAH125A15'] = h125a15_MedIsoMu2_TauDMAntiMedIso_PileupDOWN
   dictionary['FP']['PileupDown']['HToAAH125A17'] = h125a17_MedIsoMu2_TauDMAntiMedIso_PileupDOWN
   dictionary['FP']['PileupDown']['HToAAH125A19'] = h125a19_MedIsoMu2_TauDMAntiMedIso_PileupDOWN
   dictionary['FP']['PileupDown']['HToAAH125A21'] = h125a21_MedIsoMu2_TauDMAntiMedIso_PileupDOWN
   dictionary['FP']['PileupDown']['HToAAH125A5'] = h125a5_MedIsoMu2_TauDMAntiMedIso_PileupDOWN
   dictionary['FP']['PileupDown']['HToAAH125A7'] = h125a7_MedIsoMu2_TauDMAntiMedIso_PileupDOWN
   dictionary['FP']['PileupDown']['HToAAH125A9'] = h125a9_MedIsoMu2_TauDMAntiMedIso_PileupDOWN
   dictionary['FP']['PileupDown']['HToAAH300A11'] = h300a11_MedIsoMu2_TauDMAntiMedIso_PileupDOWN
   dictionary['FP']['PileupDown']['HToAAH300A13'] = h300a13_MedIsoMu2_TauDMAntiMedIso_PileupDOWN
   dictionary['FP']['PileupDown']['HToAAH300A15'] = h300a15_MedIsoMu2_TauDMAntiMedIso_PileupDOWN
   dictionary['FP']['PileupDown']['HToAAH300A17'] = h300a17_MedIsoMu2_TauDMAntiMedIso_PileupDOWN
   dictionary['FP']['PileupDown']['HToAAH300A19'] = h300a19_MedIsoMu2_TauDMAntiMedIso_PileupDOWN
   dictionary['FP']['PileupDown']['HToAAH300A21'] = h300a21_MedIsoMu2_TauDMAntiMedIso_PileupDOWN
   dictionary['FP']['PileupDown']['HToAAH300A5'] = h300a5_MedIsoMu2_TauDMAntiMedIso_PileupDOWN
   dictionary['FP']['PileupDown']['HToAAH300A7'] = h300a7_MedIsoMu2_TauDMAntiMedIso_PileupDOWN
   dictionary['FP']['PileupDown']['HToAAH300A9'] = h300a9_MedIsoMu2_TauDMAntiMedIso_PileupDOWN
   dictionary['FP']['PileupDown']['HToAAH750A11'] = h750a11_MedIsoMu2_TauDMAntiMedIso_PileupDOWN
   dictionary['FP']['PileupDown']['HToAAH750A13'] = h750a13_MedIsoMu2_TauDMAntiMedIso_PileupDOWN
   dictionary['FP']['PileupDown']['HToAAH750A15'] = h750a15_MedIsoMu2_TauDMAntiMedIso_PileupDOWN
   dictionary['FP']['PileupDown']['HToAAH750A17'] = h750a17_MedIsoMu2_TauDMAntiMedIso_PileupDOWN
   dictionary['FP']['PileupDown']['HToAAH750A19'] = h750a19_MedIsoMu2_TauDMAntiMedIso_PileupDOWN
   dictionary['FP']['PileupDown']['HToAAH750A21'] = h750a21_MedIsoMu2_TauDMAntiMedIso_PileupDOWN
   dictionary['FP']['PileupDown']['HToAAH750A5'] = h750a5_MedIsoMu2_TauDMAntiMedIso_PileupDOWN
   dictionary['FP']['PileupDown']['HToAAH750A7'] = h750a7_MedIsoMu2_TauDMAntiMedIso_PileupDOWN
   dictionary['FP']['PileupDown']['HToAAH750A9'] = h750a9_MedIsoMu2_TauDMAntiMedIso_PileupDOWN


dictionary = {'PP' : {
                 '' : {},
                 'IDUp' : {},
                 'IDDown' : {},
                 'PileupUp' : {},
                 'PileupDown' : {},
                 'IsoUp' : {},
                 'IsoDown' : {},
                 'BTagUp' : {},
                 'BTagDown' : {}
                     },
              'FP' : {
                 '' : {},
                 'IDUp' : {},
                 'IDDown' : {},
                 'PileupUp' : {},
                 'PileupDown' : {},
                 'IsoUp' : {},
                 'IsoDown' : {},
                 'BTagUp' : {},
                 'BTagDown' : {}
                     }
             }

GetPPSignal(dictionary,XRANGE)
GetPPData(dictionary,XRANGE)
GetFPData(dictionary,XRANGE)
GetFPSignal(dictionary,XRANGE)

LimitsClass = HaaLimits(dictionary)
LimitsClass.XRANGE = XRANGE
LimitsClass.UPSILONRANGE = UPSILONRANGE
LimitsClass.SHIFTS = ['Pileup', 'ID','Iso', 'BTag']
LimitsClass.REGIONS = ['FP','PP']
LimitsClass.initializeWorkspace()

####################################
# Devin's code
####################################
LimitsClass.addBackgroundModels(fixAfterFP=False, addUpsilon=False, setUpsilonLambda=None)

LAMBDA = LimitsClass.GetWorkspaceValue("lambda_cont1_FP")
print "\n\n\n\n\n\n\n\n\n\n\n\n\nHELLOO", LAMBDA
LimitsClass.initializeWorkspace()
LimitsClass.addBackgroundModels(fixAfterFP=True, addUpsilon=True,  setUpsilonLambda=LAMBDA)

LimitsClass.addSignalModels()
LimitsClass.addData(asimov=True)#,addSignal=True)

LimitsClass.setupDatacard()
LimitsClass.addSystematics()
LimitsClass.save(name=name, subdirectory=subdirectoryName)
