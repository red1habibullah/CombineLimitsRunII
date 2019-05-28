import os
import json

import ROOT
ROOT.gROOT.SetBatch(ROOT.kTRUE)

import DevTools.Plotter.CMS_lumi as CMS_lumi
import DevTools.Plotter.tdrstyle as tdrstyle

ROOT.gROOT.ProcessLine("gErrorIgnoreLevel = 2001;")
tdrstyle.setTDRStyle()

yvar = 'h'
#yvar = 'tt'
h = 125
a = 8
xVar = 'CMS_haa_x'
yVar = 'CMS_haa_y'
xRange = [2.5,25]
xBinWidth = 0.25
#yRange = [30,250]
yRange = [30,750]
yBinWidth = 5
if yvar=='tt':
    yRange = [1,20]
    yBinWidth = 0.25
blind = True
br = 0.0005
doPostfit = False

amasses = ['3p6','5','9','13','17','21']
colors = [ROOT.kBlue-4, ROOT.kCyan+1, ROOT.kGreen+1, ROOT.kOrange-3, ROOT.kRed+1, ROOT.kMagenta+1]

jfile = 'fitParams/HaaLimits2D_unbinned_{}/with1DFits/background_PP.json'.format(yvar)

with open(jfile,'r') as f:
    results = json.load(f)

rfile = 'datacards_shape/MuMuTauTau/mmmt_mm_{}_parametric_unbinned_with1DFits.root'.format(yvar)
tfile = ROOT.TFile.Open(rfile)

ws = tfile.Get('w')

pdf_x = ws.pdf('bg_PP_x')
pdf_y = ws.pdf('bg_PP_y')

# override values
params = [
    # x
    'lambda_cont1_PP_x',
    'lambda_cont3_PP_x',
    'mean_jpsi1S',
    'sigma_jpsi1S',
    'width_jpsi1S',
    'mean_jpsi2S',
    'sigma_jpsi2S',
    'width_jpsi2S',
    'mean_upsilon1S',
    'sigma_upsilon1S',
    'width_upsilon1S',
    'mean_upsilon2S',
    'sigma_upsilon2S',
    'width_upsilon2S',
    'mean_upsilon3S',
    'sigma_upsilon3S',
    'width_upsilon3S',


    # y
    'lambda_conty1_PP_y',
    'erfShift_erf1_PP_y',
    'erfScale_erf1_PP_y',
]

def floatToText(x):
    s = '{:.1E}'.format(x).split('E')
    return '{} #times 10^{{{}}}'.format(float(s[0]),int(s[1]))

if doPostfit:
    jfile = 'impacts_mm_h_unbinned_with1DFits_125_7.json' # for now while the other is not working
    with open(jfile,'r') as f:
        postfit = json.load(f)
    
    postParams = {}
    for p in postfit['params']:
        postParams[p['name']] = p
    
    for p in params:
        param = ws.arg(p)
        val = postParams[p]['fit'][1]
        param.setVal(val)

data = ws.data('data_obs_PP')

mh = ws.var('MH')
mh.setVal(h)
ma = ws.var('MA')
ma.setVal(a)

sig_x = ws.pdf('ggH_haa_{}_PP_x'.format(h))
sig_y = ws.pdf('ggH_haa_{}_PP_y'.format(h))

integral = results['integral']
sigintegral = ws.function('fullIntegral_ggH_haa_{}_PP'.format(h)).getVal() * br/0.001

# x
x = ws.var(xVar)
x.setUnit('GeV')
x.setPlotLabel('m(#mu#mu)')
x.SetTitle('m(#mu#mu)')

#x.setRange('fullrange',2.5,25)
#x.setRange('range',*xRange)

canvas = ROOT.TCanvas('c','c',800,600)

xFrame = x.frame()

pdf_x.plotOn(xFrame,ROOT.RooFit.Normalization(integral),ROOT.RooFit.LineColor(ROOT.kBlue))#,ROOT.RooFit.NormRange("fullrange"),ROOT.RooFit.Range("range"))
sig_x.plotOn(xFrame,ROOT.RooFit.Normalization(sigintegral),ROOT.RooFit.LineColor(ROOT.kRed))#,ROOT.RooFit.NormRange("fullrange"),ROOT.RooFit.Range("range"))
data.plotOn(xFrame,ROOT.RooFit.Binning(int((xRange[1]-xRange[0])/xBinWidth)))


xFrame.Draw()
xFrame.GetYaxis().SetTitle('Events / {} GeV'.format(xBinWidth))
xFrame.SetMaximum(600) # for PP
xFrame.SetMinimum(0.1)

CMS_lumi.cmsText = 'CMS'
CMS_lumi.writeExtraText = True
CMS_lumi.extraText = 'Preliminary'
CMS_lumi.lumi_13TeV = "%0.1f fb^{-1}" % (35.9)
CMS_lumi.CMS_lumi(canvas,4,11)

xFrame.SetAxisRange(*xRange)

legend = ROOT.TLegend(0.5,0.6,0.9,0.9)
legend.SetTextFont(42)
legend.SetBorderSize(0)
legend.SetFillColor(0)
#legend.SetNColumns(2)

for prim in canvas.GetListOfPrimitives():
    #print prim
    if 'data_obs' in prim.GetTitle():
        title = 'Pseudodata' if blind else 'Observed'
        legend.AddEntry(prim, title, 'ep')
    elif 'bg' in prim.GetTitle():
        legend.AddEntry(prim, 'Background Model', 'l')
    elif 'ggH' in prim.GetTitle():
        title = '#splitline{{m_{{H}} = {} GeV, m_{{a}} = {} GeV}}{{BR(h #rightarrow aa #rightarrow #mu#mu#tau#tau) = {}}}'.format(h,a,floatToText(br))
        legend.AddEntry(prim, title, 'l')

legend.Draw()

canvas.SetLogy()
canvas.RedrawAxis()

for ext in ['png','pdf','root']:
    canvas.Print('bg_mm_pdf.{}'.format(ext))

# y
y = ws.var(yVar)
y.setUnit('GeV')
if yvar=='h':
    y.setPlotLabel('m(#mu#mu#tau_{#mu}#tau_{h})')
    y.SetTitle('m(#mu#mu#tau_{#mu}#tau_{h})')
else:
    y.setPlotLabel('m(#tau_{#mu}#tau_{h})')
    y.SetTitle('m(#tau_{#mu}#tau_{h})')

canvas = ROOT.TCanvas('c','c',800,600)

yFrame = y.frame()

pdf_y.plotOn(yFrame,ROOT.RooFit.Normalization(integral),ROOT.RooFit.LineColor(ROOT.kBlue))#,ROOT.RooFit.NormRange("fullrange"),ROOT.RooFit.Range("range"))
sig_y.plotOn(yFrame,ROOT.RooFit.Normalization(sigintegral),ROOT.RooFit.LineColor(ROOT.kRed))#,ROOT.RooFit.NormRange("fullrange"),ROOT.RooFit.Range("range"))
data.plotOn(yFrame,ROOT.RooFit.Binning(int((yRange[1]-yRange[0])/yBinWidth)))


yFrame.Draw()
yFrame.GetYaxis().SetTitle('Events / {} GeV'.format(yBinWidth))
if yvar=='tt':
    yFrame.SetMaximum(100) # for PP
else:
    yFrame.SetMaximum(140) # for PP

CMS_lumi.cmsText = 'CMS'
CMS_lumi.writeExtraText = True
CMS_lumi.extraText = 'Preliminary'
CMS_lumi.lumi_13TeV = "%0.1f fb^{-1}" % (35.9)
CMS_lumi.CMS_lumi(canvas,4,11)

yFrame.SetAxisRange(*yRange)
ymax = yFrame.GetMaximum()
yFrame.SetMaximum(ymax*5)
xFrame.SetMinimum(0.1)

legend = ROOT.TLegend(0.5,0.6,0.9,0.9)
legend.SetTextFont(42)
legend.SetBorderSize(0)
legend.SetFillColor(0)
#legend.SetNColumns(2)

for prim in canvas.GetListOfPrimitives():
    #print prim
    if 'data_obs' in prim.GetTitle():
        title = 'Pseudodata' if blind else 'Observed'
        legend.AddEntry(prim, title, 'ep')
    elif 'bg' in prim.GetTitle():
        legend.AddEntry(prim, 'Background Model', 'l')
    elif 'ggH' in prim.GetTitle():
        title = '#splitline{{m_{{H}} = {} GeV, m_{{a}} = {} GeV}}{{BR(h #rightarrow aa #rightarrow #mu#mu#tau#tau) = {}}}'.format(h,a,floatToText(br))
        legend.AddEntry(prim, title, 'l')

legend.Draw()

canvas.RedrawAxis()
canvas.SetLogy()

for ext in ['png','pdf','root']:
    canvas.Print('bg_{}_pdf.{}'.format(yvar,ext))

