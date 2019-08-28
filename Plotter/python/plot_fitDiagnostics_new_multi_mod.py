import ROOT

ROOT.gROOT.SetBatch(ROOT.kTRUE)


import DevTools.Plotter.CMS_lumi as CMS_lumi
import DevTools.Plotter.tdrstyle as tdrstyle

ROOT.gROOT.ProcessLine("gErrorIgnoreLevel = 2001;")
tdrstyle.setTDRStyle()


isprelim = False
br = 0.0005
doUnc = False

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

def load(h,a,mode=''):
    result = {}

    if mode=='lowmass':
        a = 7
    elif mode=='upsilon':
        a = 9
    elif mode=='highmass':
        a = 15

    wsName = 'temp_fitDiagnostics/{h}_{a}/ws_mm_h_unbinned_{mode}_{h}_{a}.root'.format(h=h,a=a,mode=mode+'With1DFits' if mode else 'with1DFits')
    fdName = 'temp_fitDiagnostics/{h}_{a}/fitDiagnostics{mode}.root'.format(h=h,a=a,mode=mode+'With1DFits' if mode else 'with1DFits')


    wsFile = ROOT.TFile.Open(wsName)
    fdFile = ROOT.TFile.Open(fdName)
    ws = wsFile.Get('w')

    result['wsFile'] = wsFile
    result['fdFile'] = fdFile
    result['ws'] = ws

    ws.var('MA').setVal(a)
    ws.var('MH').setVal(h)

    sigPdfs = {x: ws.pdf('shapeSig_ggH_haa_{h}_{x}'.format(h=h,x=x)) for x in ['PP','FP']}
    sigInts = {x: ws.function('fullIntegral_ggH_haa_{h}_{x}'.format(h=h,x=x)) for x in ['PP','FP']}

    result['sigPdfs'] = sigPdfs
    result['sigInts'] = sigInts

    mc_s = ws.genobj('ModelConfig')
    mc_b = ws.genobj('ModelConfig_bonly')
    data = ws.data('data_obs')

    fr_s = fdFile.Get('fit_s')
    fr_b = fdFile.Get('fit_b')

    mc = mc_b
    fr = fr_b

    result['mc'] = mc
    result['fr'] = fr
    result['data'] = data

    # iterate through the fit result parameters
    pars = argsetToList(fr.floatParsFinal())
    for p in pars:
        # now set them
        mc.GetWorkspace().var(p.GetName()).setVal(p.getVal())

    sim = mc.GetPdf()
    cat = sim.indexCat()
    datasets = data.split(cat, True)

    result['sim'] = sim
    result['cat'] = cat
    result['datasets'] = datasets

    for ds in datasets:
        dpdf = sim.getPdf(ds.GetName())

        result[ds.GetName()] = {}
        result[ds.GetName()]['dpdf'] = dpdf
        result[ds.GetName()]['dataset'] = ds

        obsset = dpdf.getObservables(ds)
        obsiter = obsset.createIterator()
        x = obsiter.Next()
        result[ds.GetName()]['obsset'] = obsset
        while x:
            result[ds.GetName()][x.GetName()] = x
            x = obsiter.Next()

    return result

def plot(h,a):
    result = {}

    config = {
        'CMS_haa_x': {
            'binning': int((25-2.5)/0.25),
            'lowmassbinning': int((8.5-2.5)/0.25),
            'upsilonbinning': int((14-6)/0.25),
            'highmassbinning': int((25-11)/0.25),
            'xlabel' : 'm(#mu#mu) (GeV)',
            'ylabel' : 'Events / 0.25 GeV',
            'xrange' : [2.5,25]
        },
        'CMS_haa_y': {
            'binning': int((800-0)/20),
            'xlabel' : 'm(#mu#mu#tau_{#mu}#tau_{h}) (GeV)',
            'ylabel' : 'Events / 20 GeV',
            'xrange' : [0,800]
        },
        'CMS_haa_x_control': {
            'binning': int((25-2.5)/0.1),
            'lowmassbinning': int((8.5-2.5)/0.1),
            'upsilonbinning': int((14-6)/0.1),
            'highmassbinning': int((25-11)/0.1),
            'xlabel' : 'm(#mu#mu) (GeV)',
            'ylabel' : 'Events / 0.1 GeV',
            'xrange' : [2.5,25]
        }
    }

    ranges = {
        'lowmass': [2.5,8.5],
        'upsilon': [6,14],
        'highmass': [11,25],
        '' : [2.5,25],
    }
    limitranges = {
        'lowmass': [2.5,8],
        'upsilon': [8,11.5],
        'highmass': [11.5,25],
        '' : [2.5,25],
    }

    result[h] = {}
    result[h][''] = load(h,a,'')

    # we will now iterate over the mode='' and grab the ds/x names to iterate through again
    names = []
    sim = result[h]['']['sim']
    for ds in result[h]['']['datasets']:
        dpdf = sim.getPdf(ds.GetName())
        obsset = dpdf.getObservables(ds)
        obsiter = obsset.createIterator()
        x = obsiter.Next()
        while x:
            names += [(ds.GetName(),x.GetName())]

            x = obsiter.Next()

    # then iterate over those names
    for dsName, xName in names:
        # create a canvas with 3 pads, one for each region
        canvas = ROOT.TCanvas('c','c',50,50,600,600)
        canvas.SetLogy()

        mainpad = canvas

        left = 0.16
        right = 0.04
        top = 0.05
        bottom = 0.13
        width = 1-left-right
        height = 1-top-bottom
        xwidth = ranges[''][1] - ranges[''][0]
        lowmasswidth = float(limitranges['lowmass'][1] - limitranges['lowmass'][0])/xwidth * width
        upsilonwidth = float(limitranges['upsilon'][1] - limitranges['upsilon'][0])/xwidth * width
        highmasswidth = float(limitranges['highmass'][1] - limitranges['highmass'][0])/xwidth * width


        lowmasspad = ROOT.TPad('lowmasspad','lowmasspad',0,0,left+lowmasswidth,1)
        lowmasspad.SetBottomMargin(bottom)
        lowmasspad.SetLeftMargin(left/(left+lowmasswidth))
        lowmasspad.SetRightMargin(0)
        lowmasspad.SetTopMargin(top)
        lowmasspad.Draw()

        upsilonpad = ROOT.TPad('upsilonpad','upsilonpad',left+lowmasswidth,0,left+lowmasswidth+upsilonwidth,1)
        upsilonpad.SetBottomMargin(bottom)
        upsilonpad.SetLeftMargin(0)
        upsilonpad.SetRightMargin(0)
        upsilonpad.SetTopMargin(top)
        upsilonpad.Draw()

        highmasspad = ROOT.TPad('highmasspad','highmasspad',left+lowmasswidth+upsilonwidth,0,1,1)
        highmasspad.SetBottomMargin(bottom)
        highmasspad.SetLeftMargin(0)
        highmasspad.SetRightMargin(right/(right+highmasswidth))
        highmasspad.SetTopMargin(top)
        highmasspad.Draw()



        for mode in ['lowmass','upsilon','highmass']:
            thepad = canvas
            if mode=='lowmass':
                thepad = lowmasspad
            elif mode=='upsilon':
                thepad = upsilonpad
            elif mode=='highmass':
                thepad = highmasspad
            thepad.cd()

            result[h][mode] = load(h,a,mode)

            sim = result[h][mode]['sim']
            for ds in result[h][mode]['datasets']:
                if ds.GetName()!=dsName: continue
                dpdf = sim.getPdf(ds.GetName())
                obsset = dpdf.getObservables(ds)
                obsiter = obsset.createIterator()
                x = obsiter.Next()
                while x:
                    if x.GetName()!=xName or '_x' not in xName:
                        x = obsiter.Next()
                        continue

                    x.setRange(mode+'Range',*ranges[mode])
                    x.setRange(mode+'LimitRange',*limitranges[mode])


                    frame = x.frame(
                        ROOT.RooFit.Bins(config[x.GetName()][mode+'binning']),
                    )
                    ds.plotOn(frame, 
                        ROOT.RooFit.DataError(ROOT.RooAbsData.Poisson),
                    )
                    # now loop over each mode
                    xargs = ROOT.RooArgSet(x)
                    fr = result[h][mode]['fr']
                    sigInts = result[h][mode]['sigInts']
                    sigPdfs = result[h][mode]['sigPdfs']
                    addSig = ds.GetName() in sigPdfs
                    if mode=='lowmass' and a>8: addSig=False
                    if mode=='upsilon' and (a<8 or a>11.5): addSig=False
                    if mode=='highmass' and a<11.5: addSig=False
                    if doUnc:
                        dpdf.plotOn(frame, 
                            ROOT.RooFit.Normalization(dpdf.expectedEvents(xargs),ROOT.RooAbsReal.NumEvent),
                            ROOT.RooFit.VisualizeError(fr,1),
                            ROOT.RooFit.Components('shapeBkg*'),
                            ROOT.RooFit.FillColor(ROOT.kOrange),
                            ROOT.RooFit.LineColor(ROOT.kOrange),
                            ROOT.RooFit.Range(mode+'LimitRange'),
                            ROOT.RooFit.NormRange(mode+'Range'),
                        )
                    if addSig:
                        mainpad = thepad
                        sigPdfs[ds.GetName()].plotOn(frame,
                            ROOT.RooFit.LineColor(ROOT.kRed),
                            ROOT.RooFit.Components('shapeSig*'),
                            ROOT.RooFit.Normalization(sigInts[ds.GetName()].getVal()*br/1e-3,ROOT.RooAbsReal.NumEvent),
                        )
                    dpdf.plotOn(frame,
                        ROOT.RooFit.LineColor(ROOT.kBlue),
                        ROOT.RooFit.Components('shapeBkg*'),
                        ROOT.RooFit.Normalization(dpdf.expectedEvents(xargs),ROOT.RooAbsReal.NumEvent),
                        ROOT.RooFit.Range(mode+'LimitRange'),
                        ROOT.RooFit.NormRange(mode+'Range'),
                    )
                    ds.plotOn(frame, 
                        ROOT.RooFit.DataError(ROOT.RooAbsData.Poisson),
                    )


                    frame.Draw()
                    frame.SetMinimum(0)
                    #frame.GetXaxis().SetTitle(config[x.GetName()]['xlabel'] if mode=='highmass' else '')
                    #frame.GetYaxis().SetTitle(config[x.GetName()]['ylabel'] if mode=='lowmass' else '')
                    frame.GetXaxis().SetTitle('')
                    frame.GetYaxis().SetTitle('')

                    frame.GetXaxis().SetRangeUser(*limitranges[mode])

                    if x.GetName()=='CMS_haa_x':
                        frame.SetMinimum(0.1 if 'PP' in ds.GetName() else 1)
                        frame.SetMaximum(2000)
                        thepad.SetLogy()
                        #frame.SetMinimum(0)
                        #frame.SetMaximum(500)
                    elif x.GetName()=='CMS_haa_y':
                        frame.SetMaximum(1000)
                        frame.SetMinimum(0.1)
                        thepad.SetLogy()
                        #frame.SetMaximum(1000)
                        #frame.SetMinimum(0)
                    else:
                        frame.SetMaximum(1e7)
                        frame.SetMinimum(5e2)
                        thepad.SetLogy()
                        #frame.SetMaximum(8e5)
                        #frame.SetMinimum(0)

                    frame.GetXaxis().SetTickLength(0)
                    frame.GetXaxis().SetLabelOffset(999)

                    frame.GetYaxis().SetTickLength(0)
                    frame.GetYaxis().SetLabelOffset(999)

                    x = obsiter.Next()

        canvas.cd()
        apad = ROOT.TPad('apad','apad',0,0,1,1)
        apad.SetFillStyle(4000)
        apad.SetLogy()
        apad.SetBottomMargin(bottom)
        apad.SetTopMargin(top)
        apad.SetLeftMargin(left)
        apad.SetRightMargin(right)
        apad.Draw('same')
        apad.cd()

        ahist = ROOT.TH1D('h','h',1,2.5,25)
        ahist.Draw('axis same')
        ahist.GetXaxis().SetTitle(config[xName]['xlabel'])
        ahist.GetYaxis().SetTitle(config[xName]['ylabel'])
        if xName=='CMS_haa_x':
            ahist.SetMinimum(0.1 if 'PP' in dsName else 1)
            ahist.SetMaximum(2000)
        elif xName=='CMS_haa_y':
            ahist.SetMaximum(1000)
            ahist.SetMinimum(0.1)
        else:
            ahist.SetMaximum(1e7)
            ahist.SetMinimum(5e2)

        CMS_lumi.cmsText = 'CMS'
        CMS_lumi.writeExtraText = isprelim
        CMS_lumi.extraText = 'Preliminary'
        CMS_lumi.lumi_13TeV = "%0.1f fb^{-1}" % (35.9)
        CMS_lumi.CMS_lumi(canvas,4,11)


        legend = ROOT.TLegend(0.4,0.65,0.92,0.92)
        legend.SetTextFont(42)
        legend.SetBorderSize(0)
        legend.SetFillColor(0)

        foundSig = False
        foundBkg = False
        foundObs = False
        toAdd = {}
        for prim in lowmasspad.GetListOfPrimitives():
            if 'h_{}'.format(dsName) in prim.GetName():
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


        canvas.Print('new_mod_rooplot_haa_{}_{}_{}_{}.png'.format(dsName,xName,h,a))
        canvas.Print('new_mod_rooplot_haa_{}_{}_{}_{}.pdf'.format(dsName,xName,h,a))

            

for h in [125]:
    for a in [7]:
        plot(h,a)
