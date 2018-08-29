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

from HaaLimitsNewRegionCorD import *

XRANGE = [2.5,30]
UPSILONRANGE = [8,11]
subdirectoryName='KinFit_mumu_RegionC/'
name = 'mmmt_mm_parametric'
IFCONTROL = True

def getDataset(ds,weight='w',selection='1',xRange=[],yRange=[]):
   args = ds.get()
   if xRange: 
     args.find('x').setRange(*xRange)
   ds = ROOT.RooDataSet(ds.GetName(),ds.GetTitle(),ds,args,selection,weight)
   return ds

def getTH1F(hist, dic, xMin=0, xMax=30, shift='', name='', region='PP'):
   width = hist.GetBinWidth(3)
   binedge = 0
   newHist = ROOT.TH1F(hist.GetName(), hist.GetTitle(), hist.GetNbinsX(), hist.GetXaxis().GetXmin(), hist.GetXaxis().GetXmax())
   newHist.SetDirectory(0)
   newHist.AddDirectory(False)
   for i in range(hist.GetNbinsX() ):
      upperEdge = hist.GetBinCenter(i) + width/2
      lowerEdge = hist.GetBinCenter(i) - width/2
      if upperEdge > xMin and lowerEdge < xMax: 
         newHist.SetBinContent(i, hist.GetBinContent(i) )
         newHist.SetBinError(i,   hist.GetBinError(i) )
      else:
         newHist.SetBinContent(i,0)
         newHist.SetBinError(i, 0)
   dic[region][shift][name] = newHist
     	


def GetFPData(dictionary,xRange=[],yRange=[], rooDataSet=False):

   f_FakeRateRegionB = ROOT.TFile.Open("/eos/cms/store/user/ktos/ShapeDifferences/FINAL_RooDataSet_MiniAOD_SingleMu_AntiMedIsoMu2_TauDMMedIso_AUG19_CItself_Plots.root")
   if rooDataSet:
      SingleMu_RegionB = f_FakeRateRegionB.Get("mumumass_dataset")
      SingleMu_RegionB = getDataset(SingleMu_RegionB, selection='x <= ' + str(XRANGE[1]) + ' && x >= ' + str(XRANGE[0]), xRange=xRange, yRange=yRange)
      dictionary['FP']['']['data']         = SingleMu_RegionB
      dictionary['FP']['']['dataNoSig']         = SingleMu_RegionB
   else:
      SingleMu_RegionB = f_FakeRateRegionB.Get("mumu_Mass")
      getTH1F(SingleMu_RegionB, xMin=XRANGE[0], xMax=XRANGE[1], shift='',         name='data', dic=dictionary, region='FP')
      getTH1F(SingleMu_RegionB, xMin=XRANGE[0], xMax=XRANGE[1], shift='',         name='dataNoSig', dic=dictionary, region='FP')

if not IFCONTROL:
  dictionary = {'PP' : { '' : {},  },
                'FP' : { '' : {},  }
               }
else:
  dictionary = {'PP' : { '' : {},  },
                'FP' : { '' : {},  },
                'control': {'' :{} }
               }
  
  f = ROOT.TFile.Open("/eos/cms/store/user/ktos/ShapeDifferences/control.root")
  control = f.Get("mmMass")
  dictionary['control']['']['data'] = control
  dictionary['control']['']['dataNoSig'] = control




GetFPData(dictionary, rooDataSet=True)


LimitsClass = HaaLimits(dictionary, tag='KinFit_mumu_RegionC')
LimitsClass.XRANGE = XRANGE
LimitsClass.UPSILONRANGE = UPSILONRANGE
LimitsClass.REGIONS = ['FP']
LimitsClass.initializeWorkspace()
print "self.binned=" , LimitsClass.binned

####################################
# Devin's code
####################################
LimitsClass.addControlModels(voigtian=True)
LimitsClass.addBackgroundModels(voigtian=True,logy=True,fixAfterControl=True)
