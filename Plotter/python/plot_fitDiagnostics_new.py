import ROOT

ROOT.gROOT.SetBatch(ROOT.kTRUE)


import DevTools.Plotter.CMS_lumi as CMS_lumi
import DevTools.Plotter.tdrstyle as tdrstyle

ROOT.gROOT.ProcessLine("gErrorIgnoreLevel = 2001;")
tdrstyle.setTDRStyle()


isprelim = False
br = 0.0005
doUnc = False
doRatio = True

def floatToText(x):
    s = '{:.1E}'.format(x).split('E')
    return '{} #times 10^{{{}}}'.format(int(float(s[0])),int(s[1]))

def argsetToList(argset):
    arglist = []
    if not argset: return arglist
    argiter = argset.createIterator()
    ax = argiter.Next()
    while ax:
        arglist += [ax]
        ax = argiter.Next()
    return arglist

def getPoissonError(hist):
    # adapted from rootpy to get asymmetric poisson errors
    graph = ROOT.TGraphAsymmErrors(hist.GetNbinsX())
    chisqr = ROOT.TMath.ChisquareQuantile
    npoints = 0
    for bin in range(hist.GetNbinsX()):
        val = hist.GetBinContent(bin+1)
        err2 = hist.GetBinError(bin+1)**2
        width = hist.GetBinWidth(bin+1)
        varbin = val-err2>0.001
        entries = val*width if varbin else val
        if entries <= 0:
            #continue
            entries = 0
        ey_low = entries - 0.5 * chisqr(0.1586555, 2. * entries)
        ey_high = 0.5 * chisqr(1. - 0.1586555, 2. * (entries + 1)) - entries

        if varbin:
            ey_low = val - (entries-ey_low) / width
            ey_high = (entries+ey_high) / width - val

        ex = width / 2.
        graph.SetPoint(npoints, hist.GetBinCenter(bin+1), val)
        graph.SetPointEXlow(npoints, 0)
        graph.SetPointEXhigh(npoints, 0)
        graph.SetPointEYlow(npoints, ey_low)
        graph.SetPointEYhigh(npoints, ey_high)
        npoints += 1
    graph.Set(npoints)
    return graph

def getRatioError(num,denom):
    # get ratio between two hists with poisson errors
    if isinstance(num,ROOT.TH1):
        num_graph = getPoissonError(num)
    else:
        num_graph = num
    graph = ROOT.TGraphAsymmErrors(num_graph.GetN())
    npoints = 0
    xval = ROOT.Double()
    yval = ROOT.Double()
    for bin in range(num_graph.GetN()):
        num_graph.GetPoint(bin,xval,yval)
        nval = float(yval)
        dval = denom.GetBinContent(bin+1)
        ey_low = num_graph.GetErrorYlow(bin)
        ey_high = num_graph.GetErrorYhigh(bin)
        if dval > 0:
            graph.SetPoint(npoints, xval, nval/dval)
            graph.SetPointEXlow(npoints, 0)
            graph.SetPointEXhigh(npoints, 0)
            graph.SetPointEYlow(npoints, ey_low/dval)
            graph.SetPointEYhigh(npoints, ey_high/dval)
        else:
            graph.SetPoint(npoints, xval, 0)
            graph.SetPointEXlow(npoints, 0)
            graph.SetPointEXhigh(npoints, 0)
            graph.SetPointEYlow(npoints, 0)
            graph.SetPointEYhigh(npoints, 0)
        npoints += 1
    graph.Set(npoints)
    return graph

def plot(h,a):
    config = {
        'CMS_haa_x': {
            'xlabel' : 'm(#mu#mu) (GeV)',
        },
        'CMS_haa_y': {
            'binning': 60,
            'xlabel' : 'm(#mu#mu#tau_{#mu}#tau_{h}) (GeV)',
            'ylabel' : 'Events / 20 GeV',
            'xrange' : [0,800]
        },
        'CMS_haa_x_control': {
            'xlabel' : 'm(#mu#mu) (GeV)',
        }
    }
    if a < 8:
        mode = 'lowmass'
        config['CMS_haa_x']['binning'] = int((8.5-2.5)/0.25)
        config['CMS_haa_x']['ylabel'] = 'Events / 0.25 GeV'
        config['CMS_haa_x_control']['binning'] = int((8.5-2.5)/0.1)
        config['CMS_haa_x_control']['ylabel'] = 'Events / 0.1 GeV'
    elif a < 11.5:
        mode = 'upsilon'
        config['CMS_haa_x']['binning'] = int((14-6)/0.2)
        config['CMS_haa_x']['ylabel'] = 'Events / 0.2 GeV'
        config['CMS_haa_x_control']['binning'] = int((14-6)/0.1)
        config['CMS_haa_x_control']['ylabel'] = 'Events / 0.1 GeV'
    else:
        mode = 'highmass'
        config['CMS_haa_x']['binning'] = int((25-11)/1)
        config['CMS_haa_x']['ylabel'] = 'Events / 1 GeV'
        config['CMS_haa_x_control']['binning'] = int((25-11)/0.2)
        config['CMS_haa_x_control']['ylabel'] = 'Events / 0.2 GeV'

    wsName = 'temp_fitDiagnostics/{h}_{a}/ws_mm_h_unbinned_{mode}With1DFits_{h}_{a}.root'.format(h=h,a=a,mode=mode)
    fdName = 'temp_fitDiagnostics/{h}_{a}/fitDiagnostics{mode}With1DFits.root'.format(h=h,a=a)

    wsFile = ROOT.TFile.Open(wsName)
    ws = wsFile.Get('w')

    ws.var('MA').setVal(a)
    ws.var('MH').setVal(h)

    sigPdfs = {x: ws.pdf('shapeSig_ggH_haa_{h}_{x}'.format(h=h,x=x)) for x in ['PP','FP']}
    sigInts = {x: ws.function('fullIntegral_ggH_haa_{h}_{x}'.format(h=h,x=x)) for x in ['PP','FP']}

    mc_s = ws.genobj('ModelConfig')
    mc_b = ws.genobj('ModelConfig_bonly')
    data = ws.data('data_obs')

    fdFile = ROOT.TFile.Open(fdName)
    fr_s = fdFile.Get('fit_s')
    fr_b = fdFile.Get('fit_b')

    mc = mc_b
    fr = fr_b

    # iterate through the fit result parameters
    pars = argsetToList(fr.floatParsFinal())
    for p in pars:
        # now set them
        mc.GetWorkspace().var(p.GetName()).setVal(p.getVal())

    sim = mc.GetPdf()
    cat = sim.indexCat()
    datasets = data.split(cat, True)

    for ds in datasets:
        dpdf = sim.getPdf(ds.GetName())
        obsset = dpdf.getObservables(ds)
        obsiter = obsset.createIterator()
        x = obsiter.Next()
        while x:
            frame = x.frame(
                ROOT.RooFit.Bins(config[x.GetName()]['binning']),
            )
            ds.plotOn(frame, 
                ROOT.RooFit.DataError(ROOT.RooAbsData.Poisson),
            )
            xargs = ROOT.RooArgSet(x)
            if doUnc:
                dpdf.plotOn(frame, 
                    ROOT.RooFit.Normalization(dpdf.expectedEvents(xargs),ROOT.RooAbsReal.NumEvent),
                    ROOT.RooFit.VisualizeError(fr,1),
                    ROOT.RooFit.Components('shapeBkg*'),
                    ROOT.RooFit.FillColor(ROOT.kOrange),
                    ROOT.RooFit.LineColor(ROOT.kOrange),
                )
            if ds.GetName() in sigPdfs:
                sigPdfs[ds.GetName()].plotOn(frame,
                    ROOT.RooFit.LineColor(ROOT.kRed),
                    ROOT.RooFit.Components('shapeSig*'),
                    ROOT.RooFit.Normalization(sigInts[ds.GetName()].getVal()*br/1e-3,ROOT.RooAbsReal.NumEvent),
                )
            dpdf.plotOn(frame,
                ROOT.RooFit.LineColor(ROOT.kBlue),
                ROOT.RooFit.Components('shapeBkg*'),
                ROOT.RooFit.Normalization(dpdf.expectedEvents(xargs),ROOT.RooAbsReal.NumEvent),
            )
            #dpdf.plotOn(frame,
            #    ROOT.RooFit.Normalization(dpdf.expectedEvents(xargs),ROOT.RooAbsReal.NumEvent),
            #)
            ds.plotOn(frame, 
                ROOT.RooFit.DataError(ROOT.RooAbsData.Poisson),
            )

            canvas = ROOT.TCanvas('c','c',50,50,600,600)

            mainpad = canvas

            if doRatio:
                plotpad = ROOT.TPad("plotpad", "top pad", 0.0, 0.21, 1.0, 1.0)
                #ROOT.SetOwnership(plotpad,False)
                plotpad.SetBottomMargin(0.04)
                plotpad.SetRightMargin(0.03)
                plotpad.SetTopMargin(0.06)
                plotpad.Draw()
                ratiopad = ROOT.TPad("ratiopad", "bottom pad", 0.0, 0.0, 1.0, 0.21)
                #ROOT.SetOwnership(ratiopad,False)
                ratiopad.SetTopMargin(0.06)
                ratiopad.SetRightMargin(0.03)
                ratiopad.SetBottomMargin(0.5)
                ratiopad.SetLeftMargin(0.16)
                ratiopad.SetTickx(1)
                ratiopad.SetTicky(1)
                ratiopad.Draw()
                if plotpad != ROOT.TVirtualPad.Pad(): plotpad.cd()
                mainpad = plotpad
            else:
                canvas.SetRightMargin(0.05)
                canvas.SetTopMargin(0.06)

            frame.Draw()
            frame.SetMinimum(0)
            frame.GetXaxis().SetTitle(config[x.GetName()]['xlabel'])
            frame.GetYaxis().SetTitle(config[x.GetName()]['ylabel'])

            if 'xrange' in config[x.GetName()]:
                frame.GetXaxis().SetRangeUser(*config[x.GetName()]['xrange'])

            ROOT.TGaxis().SetMaxDigits(5)
            if x.GetName()=='CMS_haa_x':
                if a<=8:
                    frame.SetMinimum(1)
                    frame.SetMaximum(2000)
                    mainpad.SetLogy()
                if a>8 and a<11.5:
                    frame.SetMaximum(60 if 'PP' in ds.GetName() else 120)
                if a>11.5:
                    frame.SetMaximum(50 if 'PP' in ds.GetName() else 100)
            elif x.GetName()=='CMS_haa_y':
                frame.SetMaximum(1000)
                frame.SetMinimum(0.1)
                mainpad.SetLogy()
            else:
                if a<=8:
                    frame.SetMaximum(8e5)
                    frame.SetMinimum(1e4)
                    mainpad.SetLogy()
                if a>8 and a<11.5:
                    frame.SetMaximum(1.5e5)
                if a>11.5:
                    frame.SetMaximum(2e4)
                ROOT.TGaxis().SetMaxDigits(4)

            frame.GetXaxis().SetLabelSize(0.05)
            if doRatio: frame.GetXaxis().SetLabelOffset(999)
            frame.GetYaxis().SetLabelSize(0.05)

            CMS_lumi.cmsText = 'CMS'
            CMS_lumi.writeExtraText = isprelim
            CMS_lumi.extraText = 'Preliminary'
            CMS_lumi.lumi_13TeV = "%0.1f fb^{-1}" % (35.9)
            CMS_lumi.CMS_lumi(mainpad,4,11)


            legend = ROOT.TLegend(0.4,0.65,0.92,0.92)
            legend.SetTextFont(42)
            legend.SetBorderSize(0)
            legend.SetFillColor(0)

            foundSig = False
            foundBkg = False
            foundObs = False
            toAdd = {}
            for prim in mainpad.GetListOfPrimitives():
                if 'h_{}'.format(ds.GetName()) in prim.GetName():
                    if foundObs: continue
                    foundObs = True
                    title = 'Observed'
                    toAdd['obs'] = [prim, title, 'ep']
                elif 'errorband' in prim.GetName():
                    toAdd['err'] = [prim, 'Background Uncertainty', 'f']
                elif 'Bkg' in prim.GetName():
                    if foundBkg: continue
                    foundBkg = True
                    toAdd['bkg'] = [prim, 'Background Model', 'l']
                elif 'Sig' in prim.GetName():
                    if foundSig: continue
                    foundSig = True
                    title = '#splitline{{m_{{H}} = {} GeV, m_{{a}} = {} GeV}}{{B(h #rightarrow aa #rightarrow #mu#mu#tau#tau) = {}}}'.format(h,a,floatToText(br))
                    #title = 'm_{{H}} = {} GeV, m_{{a}} = {} GeV'.format(h,a)
                    toAdd['sig'] = [prim, title, 'l']

            for l in ['obs', 'bkg', 'err', 'sig']:
                if l not in toAdd: continue
                legend.AddEntry(*toAdd[l])

            legend.Draw()

            if doRatio:
                hdata = toAdd['obs'][0]
                #hdata = ds.createHistogram('h_{}{}{}{}'.format(ds.GetName(),x.GetName(),h,a), x, ROOT.RooFit.Binning(config[x.GetName()]['binning']))
                #hdata = ds.createHistogram(x.GetName(), config[x.GetName()]['binning'])
                dp = dpdf.generateBinned(xargs,0,True)
                hpdf  = dp.createHistogram('h_{}{}{}{}'.format(ds.GetName(),x.GetName(),h,a), x, ROOT.RooFit.Binning(config[x.GetName()]['binning']))
                #hpdf  = dp.createHistogram(x.GetName(), config[x.GetName()]['binning'])
                ratio = getRatioError(hdata,hpdf)

                ratiopad.cd()
                if 'xrange' in config[x.GetName()]:
                    theRange = config[x.GetName()]['xrange']
                else:
                    theRange = [frame.GetXaxis().GetXmin(),frame.GetXaxis().GetXmax()]
                
                raxes = ROOT.TH1D('h','h',1,*theRange)
                raxes.Draw()
                raxes.GetXaxis().SetTitle(config[x.GetName()]['xlabel'])
                raxes.GetYaxis().SetTitle('Obs / Exp')
                raxes.GetXaxis().SetRangeUser(*theRange)
                raxes.GetXaxis().SetLabelSize(0.19)
                raxes.GetXaxis().SetLabelOffset(0.03)
                raxes.GetXaxis().SetTitleSize(0.21)
                raxes.GetXaxis().SetTitleOffset(1.00)
                raxes.SetMinimum(0.9 if 'control' in x.GetName() else 0.0)
                raxes.SetMaximum(1.1 if 'control' in x.GetName() else 2.0)
                raxes.GetYaxis().SetLabelSize(0.19)
                raxes.GetYaxis().SetLabelOffset(0.006)
                raxes.GetYaxis().SetTitleSize(0.21)
                raxes.GetYaxis().SetTitleOffset(0.35)
                raxes.GetYaxis().SetNdivisions(503)

                unityargs = [theRange[0],1,theRange[1],1]
                ratiounity = ROOT.TLine(*unityargs)
                ratiounity.SetLineStyle(2)
                ratiounity.Draw('same')
                
                ratio.Draw('0P same')
                canvas.cd()


            canvas.Print('rooplot_haa_{}_{}_{}_{}.png'.format(ds.GetName(),x.GetName(),h,a))
            canvas.Print('rooplot_haa_{}_{}_{}_{}.pdf'.format(ds.GetName(),x.GetName(),h,a))

            x = obsiter.Next()
            

for h in [125,300,750]:
    for a in [7,9,11,15]:
        plot(h,a)
