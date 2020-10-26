import os
import json
import pickle
from array import array

import ROOT
ROOT.gROOT.SetBatch(ROOT.kTRUE)


import CombineLimitsRunII.Plotter.CMS_lumi as CMS_lumi
import CombineLimitsRunII.Plotter.tdrstyle as tdrstyle
from CombineLimitsRunII.Utilities.utilities import *

ROOT.gROOT.ProcessLine("gErrorIgnoreLevel = 2001;")
tdrstyle.setTDRStyle()



h = '125'
region = ['PP','FP']

#amasses = [4,5,6,7,9,11,13,15,17,19,21]
amasses=[4,5,7,8,10,11,12,13,14,15,17,19,20,21]

jfile = '/uscms_data/d3/rhabibul/CombineRunII/CMSSW_10_2_13/src/CombineLimitsRunII/HaaLimits/python/fitParams/HaaLimits_unbinned/lowmasswith1DFitsmediumDeepVSjetmm/central/PP.json'
disc='lowmasswith1DFitsmediumDeepVSjetmm'


with open(jfile) as f:
    data=json.load(f)
    
xvals=amasses
xerrs=[0]* len(amasses)
#yvals=[data['integrals'][h][str(m)] for m in amasses]
#yerrs=[data['integralerrs'][h][str(m)] for m in amasses]
yvals=[data['vals'][h][str(m)]['width_h125_a'+str(m)+'_PP'] for m in amasses]
yerrs=[data['errs'][h][str(m)]['width_h125_a'+str(m)+'_PP'] for m in amasses]

canvas = ROOT.TCanvas('c','c',800,600)

canvas.SetRightMargin(0.2)
#canvas.Clear()
canvas.cd()
canvas.SetGrid()


pad = ROOT.TPad("pad1", "pad1", 0.02, 0.02, 1.0, 1.0)
ROOT.gStyle.SetOptStat(0)
pad.SetTickx()
pad.SetTicky()
pad.Draw()
pad.cd()


legend = ROOT.TLegend(0.82,0.83,0.98,0.95)
legend.SetTextFont(42)
legend.SetBorderSize(0)
legend.SetFillColor(0)

graph = ROOT.TGraphErrors(len(amasses), array('d', xvals), array('d', yvals),array('d',xerrs),array('d', yerrs))
graph.SetLineWidth(1)
graph.GetXaxis().SetTitle('m_{a}')
graph.GetYaxis().SetTitle('Width')
graph.SetTitle("Uncertainity in integral for {d} in region {r}".format(d=disc,r=region[1]))
graph.Draw("ALP")
ROOT.gPad.Modified()
ROOT.gPad.Update()

legend.AddEntry(graph,'Central','l')
legend.Draw()

ROOT.gPad.Modified()
ROOT.gPad.Update()
ROOT.gPad.RedrawAxis()
#canvas.RedrawAxis()
outdir='uncertainties'
python_mkdir(outdir)
canvas.Print('{}/{}_{}_width.png'.format(outdir,disc,region[0]))
canvas.Print('{}/{}_{}_width.pdf'.format(outdir,disc,region[0]))


