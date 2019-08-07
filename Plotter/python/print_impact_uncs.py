import os
import json
import numpy as np
from array import array

import ROOT
ROOT.gROOT.SetBatch(ROOT.kTRUE)

import DevTools.Plotter.CMS_lumi as CMS_lumi
import DevTools.Plotter.tdrstyle as tdrstyle

ROOT.gROOT.ProcessLine("gErrorIgnoreLevel = 2001;")
tdrstyle.setTDRStyle()

CMS_lumi.cmsText = 'CMS'
CMS_lumi.writeExtraText = True
CMS_lumi.extraText = 'Preliminary'
CMS_lumi.lumi_13TeV = "%0.1f fb^{-1}" % (35.9)

hmasses = [125,300,750]
#amasses = [5,7,9,11,13,15,17]
amasses = [3.6, 4, 4.5, 5, 5.5, 6, 6.5, 7, 7.5, 8, 8.5, 9, 9.5, 10, 10.5, 11, 11.5, 12, 13, 14, 15, 16, 17, 18, 19, 20]
colors = {125: ROOT.kBlack, 300: ROOT.kBlue, 750: ROOT.kGreen+2}

toSkip = {
    125: [10],
    300: [13,19],
    750: [],
}

data = {}
for h in hmasses:
    data[h] = {}
    for a in amasses:
        if a<9:
            tag = 'lowmassWith1DFits'
        elif a<12:
            tag = 'upsilonWith1DFits'
        else:
            tag = 'highmassWith1DFits'
        fname = 'temp_impacts_unconstrained_{h}_{a}/impacts_mm_h_unbinned_{tag}_{h}_{a}.json'.format(h=h,a=a,tag=tag)
        if not os.path.exists(fname): continue
        with open(fname) as f:
            data[h][a] = json.load(f)

pdata = {}
for h in hmasses:
    for a in amasses:
        if a not in data[h]: continue
        for d in data[h][a]['params']:
            name = str(d['name'])
            if name not in pdata:
                pdata[name] = {}
            if h not in pdata[name]:
                pdata[name][h] = {}
            pdata[name][h][a] = d

for name in sorted(pdata):
    name = str(name)

    if name.startswith('mean') or name.startswith('sigma') or name.startswith('width'):
        doPrint = False
    elif any([name.startswith('p{}'.format(i)) for i in range(10)]):
        doPrint = False
    elif name.startswith('lambda') or name.startswith('integral') or name.startswith('erf') or name.endswith('frac'):
        doPrint = False
    elif name == 'MA':
        doPrint = False
    else:
        doPrint = True

    if doPrint: print name
    graphs = {'avg':{},'med':{}}
    mg = ROOT.TMultiGraph()
    for i,h in enumerate(hmasses):
        runcs = []
        runcMap = {}
        ups = []
        downs = []
        for a in amasses:
            if a in toSkip[h]: continue
            try:
                d = pdata[name][h][a]
            except:
                continue
            r = d['r']
            if any([abs(ri)<0.005 for ri in r]): continue
            up = (r[2]-r[1])/r[1]
            down = (r[1]-r[0])/r[1]
            avg = (abs(up)+abs(down))/2
            runcs += [avg]
            runcMap[a] = {'avg': avg, 'up': up, 'down': down, 'r': r[1], 'rup': r[2], 'rdown': r[0]}
            ups += [up]
            downs += [down]
            #print h, a, r, up, down
        if runcs:
            min_r = min(runcs)
            max_r = max(runcs)
            avg_r = sum(runcs)/len(runcs)
            med_r = np.median(runcs)
            min_u = min(ups)
            max_u = max(ups)
            avg_u = sum(ups)/len(ups)
            med_u = np.median(ups)
            min_d = min(downs)
            max_d = max(downs)
            avg_d = sum(downs)/len(downs)
            med_d = np.median(downs)
            if doPrint:
                print '   ', h, min(runcs), max(runcs)
                print '       ', ', '.join(['{:2f}'.format(ri) for ri in runcs])
                for a in sorted(runcMap):
                    if runcMap[a]['avg']>2*med_r:
                        print '           ', 'outlier', a, ', '.join(['{}: {:2f}'.format(k,v) for k,v in sorted(runcMap[a].iteritems())])
                    

            graphs['med'][h] = ROOT.TGraphAsymmErrors(1,array('d',[med_r*100]),array('d',[h]),array('d',[(med_r-min_r)*100]),array('d',[(max_r-med_r)*100]))
            graphs['avg'][h] = ROOT.TGraph(1,array('d',[avg_r*100]),array('d',[h]))
        else:
            graphs['med'][h] = ROOT.TGraphAsymmErrors(1,array('d',[0]),array('d',[0]))
            graphs['avg'][h] = ROOT.TGraphAsymmErrors(1,array('d',[0]),array('d',[0]))
        graphs['med'][h].SetMarkerColor(colors[h])
        graphs['med'][h].SetLineColor(colors[h])
        graphs['med'][h].SetMarkerStyle(25)
        graphs['avg'][h].SetMarkerColor(colors[h])
        mg.Add(graphs['med'][h])
        mg.Add(graphs['avg'][h])

    canvas = ROOT.TCanvas('c','c',600,800)
    mg.Draw('AP')
    mg.GetXaxis().SetTitle('Uncertainty from {} (%)'.format(name))
    mg.GetYaxis().SetTitle('m_{H} (GeV)')
    mg.GetYaxis().SetRangeUser(100,1000)
    CMS_lumi.CMS_lumi(canvas,4,11)
    legend = ROOT.TLegend(0.35,0.4,0.85,0.55)
    legend.SetTextFont(42)
    legend.SetBorderSize(0)
    legend.SetFillColor(0)
    legend.AddEntry(graphs['med'][125],'Median (with low and high)','lep')
    legend.AddEntry(graphs['avg'][125],'Average','p')
    legend.Draw()
    canvas.Print('impact_uncs/{}.png'.format(name))
    canvas.Print('impact_uncs/{}.pdf'.format(name))

    if doPrint: print ''


