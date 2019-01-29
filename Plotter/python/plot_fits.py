import os
import json

import ROOT
ROOT.gROOT.SetBatch(ROOT.kTRUE)

import DevTools.Plotter.CMS_lumi as CMS_lumi
import DevTools.Plotter.tdrstyle as tdrstyle

ROOT.gROOT.ProcessLine("gErrorIgnoreLevel = 2001;")
tdrstyle.setTDRStyle()

import CombineLimits.Limits.Models as Models


yvar = 'h'


ih = 125
ia = 8
amasses = [3.6,5,9,13,17,21]
hmasses = [125,300,750]

jfile = 'fitParams/HaaLimits2D_unbinned_{}/with1DFits/central/PP.json'.format(yvar)
wfile = 'datacards_shape/MuMuTauTau/mmmt_mm_{}_parametric_unbinned_with1DFits.root'.format(yvar)

with open(jfile,'r') as f:
    results = json.load(f)

tfile = ROOT.TFile.Open(wfile)
ws = tfile.Get('w')

colors = [ROOT.kBlue-4, ROOT.kCyan+1, ROOT.kGreen+1, ROOT.kOrange-3, ROOT.kRed+1, ROOT.kMagenta+1]

def getModel(h,a):
    MH = ws.var('MH')
    MA = ws.var('MA')
    MH.setVal(h)
    MA.setVal(a)

    pdf = ws.pdf('sig{}_PP'.format(h))
    integral = ws.function('fullIntegral_sig{}_PP'.format(h))
    return pdf, integral.getVal()


x = ws.var('x')

canvas = ROOT.TCanvas('c','c',800,600)

xFrame = x.frame()

for i,a in enumerate(amasses):
    pdf, integral = getModel(ih,a)
    pdf.plotOn(xFrame,ROOT.RooFit.Normalization(integral),ROOT.RooFit.LineColor(colors[i]))

xFrame.Draw()
xFrame.GetYaxis().SetTitle('Events / GeV')
ymax = xFrame.GetMaximum()
xFrame.SetMaximum(ymax*1.2)

CMS_lumi.cmsText = 'CMS'
CMS_lumi.writeExtraText = True
CMS_lumi.extraText = 'Simulation'
CMS_lumi.lumi_13TeV = "%0.1f fb^{-1}" % (35.9)
CMS_lumi.CMS_lumi(canvas,4,11)

legend = ROOT.TLegend(0.5,0.7,0.9,0.9)
legend.SetTextFont(42)
legend.SetBorderSize(0)
legend.SetFillColor(0)
legend.SetNColumns(2)

i = 0
for prim in canvas.GetListOfPrimitives():
    if isinstance(prim,ROOT.RooCurve):
        title = 'm_{{a}} = {} GeV'.format(amasses[i])
        legend.AddEntry(prim, title, 'l')
        i += 1

legend.Draw()

canvas.RedrawAxis()

for ext in ['png','pdf','root']:
    canvas.Print('amm_pdf.{}'.format(ext))




# y variable
y = ws.var('y')

canvas = ROOT.TCanvas('c','c',800,600)

yFrame = y.frame()

if yvar=='tt':
    for i,a in enumerate(amasses):
        pdf, integral = getModel(ih,a)
        pdf.plotOn(yFrame,ROOT.RooFit.Normalization(integral),ROOT.RooFit.LineColor(colors[i]))
else:
    for i,h in enumerate(hmasses):
        pdf, integral = getModel(h,ia)
        if h==750: integral *= 10
        pdf.plotOn(yFrame,ROOT.RooFit.Normalization(integral),ROOT.RooFit.LineColor(colors[i]))

yFrame.Draw()
yFrame.GetYaxis().SetTitle('Events / GeV')
ymax = yFrame.GetMaximum()
yFrame.SetMaximum(ymax*1.2)

CMS_lumi.cmsText = 'CMS'
CMS_lumi.writeExtraText = True
CMS_lumi.extraText = 'Simulation'
CMS_lumi.lumi_13TeV = "%0.1f fb^{-1}" % (35.9)
CMS_lumi.CMS_lumi(canvas,4,11)

if yvar=='tt':
   legend = ROOT.TLegend(0.5,0.7,0.9,0.9)
else:
    legend = ROOT.TLegend(0.5,0.6,0.85,0.9)
legend.SetTextFont(42)
legend.SetBorderSize(0)
legend.SetFillColor(0)
if yvar=='tt':
    legend.SetNColumns(2)

i = 0
for prim in canvas.GetListOfPrimitives():
    if isinstance(prim,ROOT.RooCurve):
        if yvar=='tt':
            title = 'm_{{a}} = {} GeV'.format(amasses[i])
        else:
            title = 'm_{{H}} = {} GeV'.format(hmasses[i])
            if hmasses[i]==750: title += ' (x10)'
        legend.AddEntry(prim, title, 'l')
        i += 1

legend.Draw()

canvas.RedrawAxis()

for ext in ['png','pdf','root']:
    if yvar=='tt':
        canvas.Print('att_pdf.{}'.format(ext))
    else:
        canvas.Print('h_pdf.{}'.format(ext))
