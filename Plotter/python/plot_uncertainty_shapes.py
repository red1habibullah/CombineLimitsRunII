import os
import sys
from array import array
import ROOT

ROOT.gROOT.SetBatch(True)

import DevTools.Plotter.CMS_lumi as CMS_lumi
import DevTools.Plotter.tdrstyle as tdrstyle
from DevTools.Utilities.utilities import *

ROOT.gROOT.ProcessLine("gErrorIgnoreLevel = 2001;")
tdrstyle.setTDRStyle()



workspaces = {}
def get_workspace(name):
    global workspaces
    if name in workspaces: return workspaces[name]
    tfile = ROOT.TFile.Open('datacards_shape/MuMuTauTau/{}.root'.format(name))
    ws = tfile.Get('w')
    workspaces[name] = ws
    return ws

def get_graph(MA,func):
    xvals = [x*0.1 for x in range(30,250,5)]
    n = len(xvals)
    yvals = []
    for x in xvals:
        MA.setVal(x)
        yvals += [func.getVal()]
    graph = ROOT.TGraph(n,array('d',xvals),array('d',yvals))
    return graph

xvar = 'CMS_haa_x'
yvar = 'CMS_haa_y'
colors = [ROOT.kRed+1, ROOT.kGreen+2, ROOT.kBlue+1, ROOT.kYellow+1, ROOT.kCyan+1, ROOT.kMagenta+1, ROOT.kGreen-2, ROOT.kBlue-2]
#uncertainties = ['CMS_btag_comb','CMS_eff_t','CMS_fake_t','CMS_pu','CMS_scale_m','CMS_scale_t','QCDscale_ggH','pdf_gg']
uncertainties = ['CMS_scale_m','CMS_scale_t','CMS_eff_t','CMS_btag_comb','CMS_pu']
regions = ['PP','FP']

ws = get_workspace('mmmt_mm_h_parametric_unbinned_with1DFits')

MH = ws.var('MH')
MA = ws.var('MA')

uncs = {}
cols = {}
for u,unc in enumerate(uncertainties):
    uncs[unc] = ws.var(unc)
    uncs[unc].setVal(0)
    cols[unc] = colors[u]

plots = {
    'integral': {'label': 'Integral',               'name': 'fullIntegral_ggH_haa_{h}_{region}',},
    'xmean'   : {'label': 'm(#mu#mu) Mean',         'name': 'mean_sigx_ggH_haa_{h}_{region}',},
    'xwidth'  : {'label': 'm(#mu#mu) Width',        'name': 'width_sigx_ggH_haa_{h}_{region}',},
    'xsigma'  : {'label': 'm(#mu#mu) Sigma',        'name': 'sigma_sigx_ggH_haa_{h}_{region}',},
    'ymean'   : {'label': 'm(#mu#mu#tau#tau) Mean', 'name': 'mean_sigy_ggH_haa_{h}_{region}',},
    'ysigma1' : {'label': 'm(#mu#mu) Sigma 1',      'name': 'sigma1_sigy_ggH_haa_{h}_{region}',},
    'ysigma2' : {'label': 'm(#mu#mu) Sigma 2',      'name': 'sigma2_sigy_ggH_haa_{h}_{region}',},
}

for region in regions:
    for h in [125,300,750]:
        for plot in plots:
    
            funcName  = plots[plot]['name'].format(h=h,region=region)
            funcLabel = plots[plot]['label']
    
            MH.setVal(h)
            func = ws.function(funcName)
            graphs = {}
            graphs['central'] = get_graph(MA,func)
            for u in uncertainties:
                uncs[u].setVal(1)
                graphs['{}Up'.format(u)] = get_graph(MA,func)
                uncs[u].setVal(-1)
                graphs['{}Down'.format(u)] = get_graph(MA,func)
                uncs[u].setVal(-0)
            
            canvas = ROOT.TCanvas('c','c',800,600)
            canvas.SetRightMargin(0.2)
            
            legend = ROOT.TLegend(0.82,0.95-(1+2*len(uncertainties))*0.05,0.98,0.95)
            legend.SetTextFont(42)
            legend.SetBorderSize(0)
            legend.SetFillColor(0)
            
            graphs['central'].Draw('AC')
            graphs['central'].SetLineWidth(2)
            graphs['central'].GetXaxis().SetTitle('m_{a}')
            graphs['central'].GetYaxis().SetTitle(funcLabel)
            legend.AddEntry(graphs['central'],'Central','l')
            
            for u in uncertainties:
                graphs['{}Up'.format(u)].Draw('C same')
                graphs['{}Up'.format(u)].SetLineStyle(7)
                graphs['{}Up'.format(u)].SetLineColor(cols[u])
                legend.AddEntry(graphs['{}Up'.format(u)],'{}Up'.format(u),'l')
                graphs['{}Down'.format(u)].Draw('C same')
                graphs['{}Down'.format(u)].SetLineStyle(4)
                graphs['{}Down'.format(u)].SetLineColor(cols[u])
                legend.AddEntry(graphs['{}Down'.format(u)],'{}Down'.format(u),'l')
            
            legend.Draw()

            outdir = 'uncertainties'
            python_mkdir(outdir)
            canvas.Print('{}/{}.png'.format(outdir,funcName))
            canvas.Print('{}/{}.pdf'.format(outdir,funcName))
