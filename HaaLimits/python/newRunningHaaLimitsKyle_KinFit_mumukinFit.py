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

from HaaLimits2D import *

XRANGE = [2.5, 25]
YRANGE = [50,1000]
UPSILONRANGE = [8,11]
subdirectoryName='KinFit_mumukinFit_yV/'
name = 'mmmt_mm_parametric'
IFCONTROL = True

def getDataset(ds,weight='w',selection='1',xRange=[],yRange=[]):
   args = ds.get()
   if xRange: 
     args.find('x').setRange(*xRange)
   if args.find('y2'): 
     args.find('y2').SetName('y')     
   if yRange: 
     args.find('y').setRange(*yRange)
   ds = ROOT.RooDataSet(ds.GetName(),ds.GetTitle(),ds,args,selection,weight)
   return ds

def GetPPData(dictionary,xRange=[],yRange=[]):
   f_FRC = ROOT.TFile.Open("/eos/cms/store/user/ktos/ShapeDifferences/FINAL_RooDataSet_MiniAOD_SingleMu_MedIsoMu2_TauDMAntiMedIso_MAY1_AFromB_HKinFit.root")
   
   SingleMu_FakeRateCentral = f_FRC.Get("mumufourBodyKinFitmass_dataset")
   SingleMu_FakeRateCentral = getDataset(SingleMu_FakeRateCentral, selection='x <= 25 && x >= 2.5 && y>=50', xRange=xRange, yRange=yRange)
   dictionary['PP']['']['data'] = SingleMu_FakeRateCentral
   dictionary['PP']['']['dataNoSig'] = SingleMu_FakeRateCentral

def GetPPSignal(dictionary,xRange=[],yRange=[]):
  f = ROOT.TFile.Open("/eos/cms/store/user/ktos/ShapeDifferences/FINAL_AllRooDataSet_MedIsoMu2_TauDMMedIso_MAY1_HKinFit.root")

  for hMass in ["125","300","750"]:
     for aMass in ["3p6","4","5","6","7","9","11","13","15","17","19","21"]:
       if (hMass == "300" or hMass == "750") and (aMass == "3p6" or aMass == "4" or aMass == "6"): continue
       h_Central = f.Get("SIG_h" + hMass + "a" + aMass + "_MedIsoMu2_TauDMMedIso_MAY1_Central_kinFit")
       h_IDDOWN = f.Get("SIG_h" + hMass + "a" + aMass + "_MedIsoMu2_TauDMMedIso_MAY1_IDDOWN_kinFit")
       h_IDUP = f.Get("SIG_h" + hMass + "a" + aMass + "_MedIsoMu2_TauDMMedIso_MAY1_IDUP_kinFit")
       h_IsoDOWN = f.Get("SIG_h" + hMass + "a" + aMass + "_MedIsoMu2_TauDMMedIso_MAY1_IsoDOWN_kinFit")
       h_IsoUP = f.Get("SIG_h" + hMass + "a" + aMass + "_MedIsoMu2_TauDMMedIso_MAY1_IsoUP_kinFit")
       h_BTagDOWN = f.Get("SIG_h" + hMass + "a" + aMass + "_MedIsoMu2_TauDMMedIso_MAY1_BTagDOWN_kinFit")
       h_BTagUP = f.Get("SIG_h" + hMass + "a" + aMass + "_MedIsoMu2_TauDMMedIso_MAY1_BTagUP_kinFit")
       h_PileupDOWN = f.Get("SIG_h" + hMass + "a" + aMass + "_MedIsoMu2_TauDMMedIso_MAY1_PileupDOWN_kinFit")
       h_PileupUP = f.Get("SIG_h" + hMass + "a" + aMass + "_MedIsoMu2_TauDMMedIso_MAY1_PileupUP_kinFit")
     
       h_Central = getDataset(h_Central, selection='x <= 25 && x >= 2.5 && y>=50', xRange=xRange, yRange=yRange)
       h_IDDOWN = getDataset(h_IDDOWN, selection='x <= 25 && x >= 2.5 && y>=50', xRange=xRange, yRange=yRange)
       h_IDUP = getDataset(h_IDUP, selection='x <= 25 && x >= 2.5 && y>=50', xRange=xRange, yRange=yRange)
       h_IsoDOWN = getDataset(h_IsoDOWN, selection='x <= 25 && x >= 2.5 && y>=50', xRange=xRange, yRange=yRange)
       h_IsoUP = getDataset(h_IsoUP, selection='x <= 25 && x >= 2.5 && y>=50', xRange=xRange, yRange=yRange)
       h_BTagDOWN = getDataset(h_BTagDOWN, selection='x <= 25 && x >= 2.5 && y>=50', xRange=xRange, yRange=yRange)
       h_BTagUP = getDataset(h_BTagUP, selection='x <= 25 && x >= 2.5 && y>=50', xRange=xRange, yRange=yRange)
       h_PileupDOWN = getDataset(h_PileupDOWN, selection='x <= 25 && x >= 2.5 && y>=50', xRange=xRange, yRange=yRange)
       h_PileupUP = getDataset(h_PileupUP, selection='x <= 25 && x >= 2.5 && y>=50', xRange=xRange, yRange=yRange)
    
       dictionary['PP']['']["HToAAH" + hMass + "A" + aMass] = h_Central
       dictionary['PP']['IDUp']["HToAAH" + hMass + "A" + aMass] = h_IDUP
       dictionary['PP']['IDDown']["HToAAH" + hMass + "A" + aMass] = h_IDDOWN
       dictionary['PP']['IsoUp']["HToAAH" + hMass + "A" + aMass] = h_IsoUP
       dictionary['PP']['IsoDown']["HToAAH" + hMass + "A" + aMass] = h_IsoDOWN
       dictionary['PP']['BTagUp']["HToAAH" + hMass + "A" + aMass] = h_BTagUP
       dictionary['PP']['BTagDown']["HToAAH" + hMass + "A" + aMass] = h_BTagDOWN
       dictionary['PP']['PileupUp']["HToAAH" + hMass + "A" + aMass] = h_PileupUP
       dictionary['PP']['PileupDown']["HToAAH" + hMass + "A" + aMass] = h_PileupDOWN


def GetFPData(dictionary,xRange=[],yRange=[]):

   f_FakeRateRegionB = ROOT.TFile.Open("/eos/cms/store/user/ktos/ShapeDifferences/FINAL_RooDataSet_MiniAOD_SingleMu_MedIsoMu2_TauDMAntiMedIso_MAY1_BItself_HKinFit.root")
   SingleMu_RegionB = f_FakeRateRegionB.Get("mumufourBodyKinFitmass_dataset")
   SingleMu_RegionB = getDataset(SingleMu_RegionB, selection='x <= 25 && x >= 2.5 && y>=50', xRange=xRange, yRange=yRange)

   dictionary['FP']['']['data'] = SingleMu_RegionB
   dictionary['FP']['']['dataNoSig'] = SingleMu_RegionB

def GetFPSignal(dictionary,xRange=[],yRange=[]):
  f = ROOT.TFile.Open("/eos/cms/store/user/ktos/ShapeDifferences/FINAL_AllRooDataSet_MedIsoMu2_TauDMAntiMedIso_MAY1_HKinFit.root")
   
  for hMass in ["125","300","750"]:
     for aMass in ["3p6","4","5","6","7","9","11","13","15","17","19","21"]:
       if (hMass == "300" or hMass == "750") and (aMass == "3p6" or aMass == "4" or aMass == "6"): continue
       h_Central = f.Get("SIG_h" + hMass + "a" + aMass + "_MedIsoMu2_TauDMAntiMedIso_MAY1_Central_kinFit")
       h_IDDOWN = f.Get("SIG_h" + hMass + "a" + aMass + "_MedIsoMu2_TauDMAntiMedIso_MAY1_IDDOWN_kinFit")
       h_IDUP = f.Get("SIG_h" + hMass + "a" + aMass + "_MedIsoMu2_TauDMAntiMedIso_MAY1_IDUP_kinFit")
       h_IsoDOWN = f.Get("SIG_h" + hMass + "a" + aMass + "_MedIsoMu2_TauDMAntiMedIso_MAY1_IsoDOWN_kinFit")
       h_IsoUP = f.Get("SIG_h" + hMass + "a" + aMass + "_MedIsoMu2_TauDMAntiMedIso_MAY1_IsoUP_kinFit")
       h_BTagDOWN = f.Get("SIG_h" + hMass + "a" + aMass + "_MedIsoMu2_TauDMAntiMedIso_MAY1_BTagDOWN_kinFit")
       h_BTagUP = f.Get("SIG_h" + hMass + "a" + aMass + "_MedIsoMu2_TauDMAntiMedIso_MAY1_BTagUP_kinFit")
       h_PileupDOWN = f.Get("SIG_h" + hMass + "a" + aMass + "_MedIsoMu2_TauDMAntiMedIso_MAY1_PileupDOWN_kinFit")
       h_PileupUP = f.Get("SIG_h" + hMass + "a" + aMass + "_MedIsoMu2_TauDMAntiMedIso_MAY1_PileupUP_kinFit")

       h_Central = getDataset(h_Central, selection='x <= 25 && x >= 2.5 && y>=50', xRange=xRange, yRange=yRange)
       h_IDDOWN = getDataset(h_IDDOWN, selection='x <= 25 && x >= 2.5 && y>=50', xRange=xRange, yRange=yRange)
       h_IDUP = getDataset(h_IDUP, selection='x <= 25 && x >= 2.5 && y>=50', xRange=xRange, yRange=yRange)
       h_IsoDOWN = getDataset(h_IsoDOWN, selection='x <= 25 && x >= 2.5 && y>=50', xRange=xRange, yRange=yRange)
       h_IsoUP = getDataset(h_IsoUP, selection='x <= 25 && x >= 2.5 && y>=50', xRange=xRange, yRange=yRange)
       h_BTagDOWN = getDataset(h_BTagDOWN, selection='x <= 25 && x >= 2.5 && y>=50', xRange=xRange, yRange=yRange)
       h_BTagUP = getDataset(h_BTagUP, selection='x <= 25 && x >= 2.5 && y>=50', xRange=xRange, yRange=yRange)
       h_PileupDOWN = getDataset(h_PileupDOWN, selection='x <= 25 && x >= 2.5 && y>=50', xRange=xRange, yRange=yRange)
       h_PileupUP = getDataset(h_PileupUP, selection='x <= 25 && x >= 2.5 && y>=50', xRange=xRange, yRange=yRange)
 
       dictionary['FP']['']["HToAAH" + hMass + "A" + aMass] = h_Central
       dictionary['FP']['IDUp']["HToAAH" + hMass + "A" + aMass] = h_IDUP
       dictionary['FP']['IDDown']["HToAAH" + hMass + "A" + aMass] = h_IDDOWN
       dictionary['FP']['IsoUp']["HToAAH" + hMass + "A" + aMass] = h_IsoUP
       dictionary['FP']['IsoDown']["HToAAH" + hMass + "A" + aMass] = h_IsoDOWN
       dictionary['FP']['BTagUp']["HToAAH" + hMass + "A" + aMass] = h_BTagUP
       dictionary['FP']['BTagDown']["HToAAH" + hMass + "A" + aMass] = h_BTagDOWN
       dictionary['FP']['PileupUp']["HToAAH" + hMass + "A" + aMass] = h_PileupUP
       dictionary['FP']['PileupDown']["HToAAH" + hMass + "A" + aMass] = h_PileupDOWN


if not IFCONTROL:
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
else:
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
                       },
                'control': {'' :{} }
               }
  
  f = ROOT.TFile.Open("/eos/cms/store/user/ktos/ShapeDifferences/control.root")
  control = f.Get("mmMass")
  dictionary['control']['']['data'] = control
  dictionary['control']['']['dataNoSig'] = control




GetPPSignal(dictionary,XRANGE,YRANGE)
GetPPData(dictionary,XRANGE,YRANGE)
GetFPData(dictionary,XRANGE,YRANGE)
GetFPSignal(dictionary,XRANGE,YRANGE)

LimitsClass = HaaLimits2D(dictionary, tag='KinFit_mumukinFit_yV')
LimitsClass.XRANGE = XRANGE
LimitsClass.YRANGE = YRANGE
LimitsClass.UPSILONRANGE = UPSILONRANGE
LimitsClass.SHIFTS = ['Pileup','ID','Iso','BTag']
LimitsClass.REGIONS = ['FP','PP']
LimitsClass.initializeWorkspace()

####################################
# Devin's code
####################################
LimitsClass.addControlModels(voigtian=True)
LimitsClass.addBackgroundModels(voigtian=True,logy=False,fixAfterControl=IFCONTROL)

LimitsClass.addSignalModels(fit=False, yFitFunc="V")
LimitsClass.addData(asimov=True)

LimitsClass.setupDatacard()
LimitsClass.addSystematics()
LimitsClass.save(name=name, subdirectory=subdirectoryName)
