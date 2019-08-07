import os
import json

import ROOT
ROOT.gROOT.SetBatch(ROOT.kTRUE)

import DevTools.Plotter.CMS_lumi as CMS_lumi
import DevTools.Plotter.tdrstyle as tdrstyle

ROOT.gROOT.ProcessLine("gErrorIgnoreLevel = 2001;")
tdrstyle.setTDRStyle()

isprelim = False
br = 0.0005

def floatToText(x):
    s = '{:.1E}'.format(x).split('E')
    return '{} #times 10^{{{}}}'.format(int(float(s[0])),int(s[1]))

def get_rooplot(tfile,name,doUnc):
    # get the postfit result
    rooplot = tfile.Get(name)
    fittree = tfile.Get('tree_fit_sb')
    fittree.GetEntry(0)
    
    # remove things we dont want
    # rooplot.remove("name")
    objToRemove = []
    objs = []
    for i in range(7):
        obj = rooplot.nameOf(i)
        o = rooplot.getObject(i)
        objs += [obj]
        if 'pdf' in obj and not ('Comp' in obj or 'errorband' in obj):
            objToRemove += [obj]
        if not doUnc and 'errorband' in obj:
            objToRemove += [obj]
        # scale the signal to desired br
        if 'Sig' in obj:
            for j in range(o.GetN()):
                if fittree.r: o.GetY()[j] *= br/(fittree.r * 0.001)
    for obj in objToRemove:
        rooplot.remove(obj)

    return rooplot
    

def plot(h,a,dim,region,mode,doUnc):
    var = 'CMS_haa_{}'.format(dim)
    if region=='control': var += '_control'
    fname = 'temp_fitDiagnostics/{h}_{a}/fitDiagnostics.Test.root'.format(h=h,a=a)

    tfile = ROOT.TFile.Open(fname)

    rooplot = get_rooplot(tfile,'{}_{}_{}'.format(region,var,mode),doUnc)
    
    canvas = ROOT.TCanvas('c','c',50,50,800,600)
    canvas.SetRightMargin(0.05)
    
    rooplot.Draw()
    mi = rooplot.GetMinimum()
    if mi<0:
        rooplot.SetMinimum(0.1)
    
    if 'x' in var:
        rooplot.GetXaxis().SetTitle('m(#mu#mu) (GeV)')
        rooplot.GetYaxis().SetTitle('Events / 0.2 GeV')
        if a<8.5: 
            rooplot.GetXaxis().SetRangeUser(2.5,8.9)
            canvas.SetLogy()
            rooplot.SetMaximum(2000)
        if a>8.5 and a<11.5:
            rooplot.SetMaximum(60)
        if a>11.5:
            rooplot.SetMaximum(15)
        if region=='control': rooplot.GetYaxis().SetTitle('Events / 0.02 GeV')
    else:
        rooplot.GetXaxis().SetTitle('m(#mu#mu#tau_{#mu}#tau_{h}) (GeV)')
        rooplot.GetYaxis().SetTitle('Events / 20 GeV')
        rooplot.GetXaxis().SetRangeUser(0,800)
        canvas.SetLogy()
        rooplot.SetMaximum(2000)
        if region=='control':
            rooplot.SetMaximum(1e6)
            rooplot.SetMinimum(100)
    
    
    CMS_lumi.cmsText = 'CMS'
    CMS_lumi.writeExtraText = isprelim
    CMS_lumi.extraText = 'Preliminary'
    CMS_lumi.lumi_13TeV = "%0.1f fb^{-1}" % (35.9)
    CMS_lumi.CMS_lumi(canvas,4,11)
    
    
    legend = ROOT.TLegend(0.4,0.6,0.92,0.92)
    legend.SetTextFont(42)
    legend.SetBorderSize(0)
    legend.SetFillColor(0)
    #legend.SetNColumns(2)
    
    foundSig = False
    foundObs = False
    for prim in canvas.GetListOfPrimitives():
        if 'h_{}'.format(region) in prim.GetName():
            if foundObs: continue
            foundObs = True
            title = 'Observed'
            legend.AddEntry(prim, title, 'ep')
        elif 'Bkg' in prim.GetName():
            prim.SetLineColor(ROOT.kBlue)
            legend.AddEntry(prim, 'Background Model', 'l')
        elif 'errorband' in prim.GetName():
            prim.SetLineColor(ROOT.kOrange)
            legend.AddEntry(prim, 'Uncertainty', 'f')
        elif 'Sig' in prim.GetName():
            prim.SetLineColor(ROOT.kRed)
            if foundSig: continue
            foundSig = True
            title = '#splitline{{m_{{H}} = {} GeV, m_{{a}} = {} GeV}}{{B(h #rightarrow aa #rightarrow #mu#mu#tau#tau) = {}}}'.format(h,a,floatToText(br))
            #title = 'm_{{H}} = {} GeV, m_{{a}} = {} GeV'.format(h,a)
            legend.AddEntry(prim, title, 'l')
    
    legend.Draw()
    
    canvas.Print('haa_mm_h_{}_{}_{}_{}_{}{}.png'.format(region,var,mode,h,a,'' if doUnc else '_noUnc'))
    canvas.Print('haa_mm_h_{}_{}_{}_{}_{}{}.pdf'.format(region,var,mode,h,a,'' if doUnc else '_noUnc'))

for doUnc in [True,False]:
    for mode in ['fit_s','fit_b']:
        for h in [125,300,750]:
            for a in [7,9,15]:
                for region in ['PP','FP','control']:
                    plot(h,a,'x',region,mode,doUnc)
                    if region!='control': plot(h,a,'y',region,mode,doUnc)

