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
subdirectoryName='UpConst_SetLambda_8p5to11p0_BTag/'
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
   f_FRC = ROOT.TFile.Open("/eos/cms/store/user/ktos/ShapeDifferences/FINAL_RooDataSet_MiniAOD_SingleMu_MedIsoMu2_TauDMAntiMedIso_MAY1_AFromB.root")
#   f_FRU = ROOT.TFile.Open("/eos/cms/store/user/ktos/ShapeDifferences/FINAL_RooDataSet_MiniAOD_SingleMu_MedIsoMu2_TauDMAntiMedIso_MAY1_FakeRate_Up.root")
#   f_FRD = ROOT.TFile.Open("/eos/cms/store/user/ktos/ShapeDifferences/FINAL_RooDataSet_MiniAOD_SingleMu_MedIsoMu2_TauDMAntiMedIso_MAY1_FakeRate_Down.root")
   
   SingleMu_FakeRateCentral = f_FRC.Get("mumumass_dataset")
#   SingleMu_FakeRateDown = f_FRD.Get("mumumass_dataset")
#   SingleMu_FakeRateUp = f_FRU.Get("mumumass_dataset")

   SingleMu_FakeRateCentral = getDataset(SingleMu_FakeRateCentral, selection='x <= 25 && x >= 4', xRange=xRange)
#   SingleMu_FakeRateDown = getDataset(SingleMu_FakeRateDown, selection='x <= 25 && x >= 4', xRange=xRange)
#   SingleMu_FakeRateUp = getDataset(SingleMu_FakeRateUp, selection='x <= 25 && x >= 4', xRange=xRange)
   
   dictionary['PP']['']['data'] = SingleMu_FakeRateCentral
   dictionary['PP']['']['dataNoSig'] = SingleMu_FakeRateCentral

def GetPPSignal(dictionary,xRange=[]):
  f = ROOT.TFile.Open("/eos/cms/store/user/ktos/ShapeDifferences/FINAL_AllRooDataSet_MedIsoMu2_TauDMMedIso_MAY1.root")

  for hMass in ["125","300","750"]:
     for aMass in ["3p6","4","5","6","7","9","11","13","15","17","19","21"]:
       if (hMass == "300" or hMass == "750") and (aMass == "3p6" or aMass == "4" or aMass == "6"): continue
       h_Central = f.Get("SIG_h" + hMass + "a" + aMass + "_MedIsoMu2_TauDMMedIso_MAY1_Central")
       h_IDDOWN = f.Get("SIG_h" + hMass + "a" + aMass + "_MedIsoMu2_TauDMMedIso_MAY1_IDDOWN")
       h_IDUP = f.Get("SIG_h" + hMass + "a" + aMass + "_MedIsoMu2_TauDMMedIso_MAY1_IDUP")
       h_IsoDOWN = f.Get("SIG_h" + hMass + "a" + aMass + "_MedIsoMu2_TauDMMedIso_MAY1_IsoDOWN")
       h_IsoUP = f.Get("SIG_h" + hMass + "a" + aMass + "_MedIsoMu2_TauDMMedIso_MAY1_IsoUP")
       h_BTagDOWN = f.Get("SIG_h" + hMass + "a" + aMass + "_MedIsoMu2_TauDMMedIso_MAY1_BTagDOWN")
       h_BTagUP = f.Get("SIG_h" + hMass + "a" + aMass + "_MedIsoMu2_TauDMMedIso_MAY1_BTagUP")
       h_PileupDOWN = f.Get("SIG_h" + hMass + "a" + aMass + "_MedIsoMu2_TauDMMedIso_MAY1_PileupDOWN")
       h_PileupUP = f.Get("SIG_h" + hMass + "a" + aMass + "_MedIsoMu2_TauDMMedIso_MAY1_PileupUP")
     
       h_Central = getDataset(h_Central, selection='x <= 25 && x >= 4', xRange=xRange)
       h_IDDOWN = getDataset(h_IDDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
       h_IDUP = getDataset(h_IDUP, selection='x <= 25 && x >= 4', xRange=xRange)
       h_IsoDOWN = getDataset(h_IsoDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
       h_IsoUP = getDataset(h_IsoUP, selection='x <= 25 && x >= 4', xRange=xRange)
       h_BTagDOWN = getDataset(h_BTagDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
       h_BTagUP = getDataset(h_BTagUP, selection='x <= 25 && x >= 4', xRange=xRange)
       h_PileupDOWN = getDataset(h_PileupDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
       h_PileupUP = getDataset(h_PileupUP, selection='x <= 25 && x >= 4', xRange=xRange)
    
       dictionary['PP']['']["HToAAH" + hMass + "A" + aMass] = h_Central
       dictionary['PP']['IDUp']["HToAAH" + hMass + "A" + aMass] = h_IDUP
       dictionary['PP']['IDDown']["HToAAH" + hMass + "A" + aMass] = h_IDDOWN
       dictionary['PP']['IsoUp']["HToAAH" + hMass + "A" + aMass] = h_IsoUP
       dictionary['PP']['IsoDown']["HToAAH" + hMass + "A" + aMass] = h_IsoDOWN
       dictionary['PP']['BTagUp']["HToAAH" + hMass + "A" + aMass] = h_BTagUP
       dictionary['PP']['BTagDown']["HToAAH" + hMass + "A" + aMass] = h_BTagDOWN
       dictionary['PP']['PileupUp']["HToAAH" + hMass + "A" + aMass] = h_PileupUP
       dictionary['PP']['PileupDown']["HToAAH" + hMass + "A" + aMass] = h_PileupDOWN


def GetFPData(dictionary,xRange=[]):

   f_FakeRateRegionB = ROOT.TFile.Open("/eos/cms/store/user/ktos/ShapeDifferences/FINAL_RooDataSet_MiniAOD_SingleMu_MedIsoMu2_TauDMAntiMedIso_MAY1_BItself.root")
   SingleMu_RegionB = f_FakeRateRegionB.Get("mumumass_dataset")
   SingleMu_RegionB = getDataset(SingleMu_RegionB, selection='x <= 25 && x >= 4', xRange=xRange)

   dictionary['FP']['']['data'] = SingleMu_RegionB
   dictionary['FP']['']['dataNoSig'] = SingleMu_RegionB

def GetFPSignal(dictionary,xRange=[]):
  f = ROOT.TFile.Open("/eos/cms/store/user/ktos/ShapeDifferences/FINAL_AllRooDataSet_MedIsoMu2_TauDMAntiMedIso_MAY1.root")
   
  for hMass in ["125","300","750"]:
     for aMass in ["3p6","4","5","6","7","9","11","13","15","17","19","21"]:
       if (hMass == "300" or hMass == "750") and (aMass == "3p6" or aMass == "4" or aMass == "6"): continue
       h_Central = f.Get("SIG_h" + hMass + "a" + aMass + "_MedIsoMu2_TauDMAntiMedIso_MAY1_Central")
       h_IDDOWN = f.Get("SIG_h" + hMass + "a" + aMass + "_MedIsoMu2_TauDMAntiMedIso_MAY1_IDDOWN")
       h_IDUP = f.Get("SIG_h" + hMass + "a" + aMass + "_MedIsoMu2_TauDMAntiMedIso_MAY1_IDUP")
       h_IsoDOWN = f.Get("SIG_h" + hMass + "a" + aMass + "_MedIsoMu2_TauDMAntiMedIso_MAY1_IsoDOWN")
       h_IsoUP = f.Get("SIG_h" + hMass + "a" + aMass + "_MedIsoMu2_TauDMAntiMedIso_MAY1_IsoUP")
       h_BTagDOWN = f.Get("SIG_h" + hMass + "a" + aMass + "_MedIsoMu2_TauDMAntiMedIso_MAY1_BTagDOWN")
       h_BTagUP = f.Get("SIG_h" + hMass + "a" + aMass + "_MedIsoMu2_TauDMAntiMedIso_MAY1_BTagUP")
       h_PileupDOWN = f.Get("SIG_h" + hMass + "a" + aMass + "_MedIsoMu2_TauDMAntiMedIso_MAY1_PileupDOWN")
       h_PileupUP = f.Get("SIG_h" + hMass + "a" + aMass + "_MedIsoMu2_TauDMAntiMedIso_MAY1_PileupUP")

       h_Central = getDataset(h_Central, selection='x <= 25 && x >= 4', xRange=xRange)
       h_IDDOWN = getDataset(h_IDDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
       h_IDUP = getDataset(h_IDUP, selection='x <= 25 && x >= 4', xRange=xRange)
       h_IsoDOWN = getDataset(h_IsoDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
       h_IsoUP = getDataset(h_IsoUP, selection='x <= 25 && x >= 4', xRange=xRange)
       h_BTagDOWN = getDataset(h_BTagDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
       h_BTagUP = getDataset(h_BTagUP, selection='x <= 25 && x >= 4', xRange=xRange)
       h_PileupDOWN = getDataset(h_PileupDOWN, selection='x <= 25 && x >= 4', xRange=xRange)
       h_PileupUP = getDataset(h_PileupUP, selection='x <= 25 && x >= 4', xRange=xRange)
 
       dictionary['FP']['']["HToAAH" + hMass + "A" + aMass] = h_Central
       dictionary['FP']['IDUp']["HToAAH" + hMass + "A" + aMass] = h_IDUP
       dictionary['FP']['IDDown']["HToAAH" + hMass + "A" + aMass] = h_IDDOWN
       dictionary['FP']['IsoUp']["HToAAH" + hMass + "A" + aMass] = h_IsoUP
       dictionary['FP']['IsoDown']["HToAAH" + hMass + "A" + aMass] = h_IsoDOWN
       dictionary['FP']['BTagUp']["HToAAH" + hMass + "A" + aMass] = h_BTagUP
       dictionary['FP']['BTagDown']["HToAAH" + hMass + "A" + aMass] = h_BTagDOWN
       dictionary['FP']['PileupUp']["HToAAH" + hMass + "A" + aMass] = h_PileupUP
       dictionary['FP']['PileupDown']["HToAAH" + hMass + "A" + aMass] = h_PileupDOWN


dictionary = {'PP' : {
                 '' : {},
                 'BTagUp' : {},
                 'BTagDown' : {},
                 'IDUp' : {},
                 'IDDown' : {},
                 'PileupUp' : {},
                 'PileupDown' : {},
                 'IsoUp' : {},
                 'IsoDown' : {}
                     },
              'FP' : {
                 '' : {},
                 'BTagUp' : {},
                 'BTagDown' : {},
                 'IDUp' : {},
                 'IDDown' : {},
                 'PileupUp' : {},
                 'PileupDown' : {},
                 'IsoUp' : {},
                 'IsoDown' : {}
                     }
             }


GetPPSignal(dictionary,XRANGE)
GetPPData(dictionary,XRANGE)
GetFPData(dictionary,XRANGE)
GetFPSignal(dictionary,XRANGE)
for k,v, in dictionary['PP'][''].items():
  print k,v

LimitsClass = HaaLimits(dictionary)
LimitsClass.XRANGE = XRANGE
LimitsClass.UPSILONRANGE = UPSILONRANGE
LimitsClass.SHIFTS = ['Pileup',rID','Iso','BTag']
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
