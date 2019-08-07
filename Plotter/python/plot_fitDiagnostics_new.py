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

def argsetToList(argset):
    arglist = []
    if not argset: return arglist
    argiter = argset.createIterator()
    ax = argiter.Next()
    while ax:
        arglist += [ax]
        ax = argiter.Next()
    return arglist

def plot(h,a):
    config = {
        'CMS_haa_x': {
            'xlabel' : 'm(#mu#mu) (GeV)',
        },
        'CMS_haa_y': {
            'binning': 60,
            'xlabel' : 'm(#mu#mu#tau_{#mu}#tau_{h}) (GeV)',
            'ylabel' : 'Events / 20 GeV',
        },
        'CMS_haa_x_control': {
            'xlabel' : 'm(#mu#mu) (GeV)',
        }
    }
    if a < 8.5:
        mode = 'lowmass'
        config['CMS_haa_x']['binning'] = 52
        config['CMS_haa_x']['ylabel'] = 'Events / 0.1 GeV'
        config['CMS_haa_x_control']['binning'] = 65
        config['CMS_haa_x_control']['ylabel'] = 'Events / 0.1 GeV'
    elif a < 11.5:
        mode = 'upsilon'
        config['CMS_haa_x']['binning'] = 20
        config['CMS_haa_x']['ylabel'] = 'Events / 0.2 GeV'
        config['CMS_haa_x_control']['binning'] = 40
        config['CMS_haa_x_control']['ylabel'] = 'Events / 0.1 GeV'
    else:
        mode = 'highmass'
        config['CMS_haa_x']['binning'] = 14
        config['CMS_haa_x']['ylabel'] = 'Events / 1 GeV'
        config['CMS_haa_x_control']['binning'] = 140
        config['CMS_haa_x_control']['ylabel'] = 'Events / 0.1 GeV'

    wsName = 'temp_fitDiagnostics/{h}_{a}/ws_mm_h_unbinned_{mode}With1DFits_{h}_{a}.root'.format(h=h,a=a,mode=mode)
    fdName = 'temp_fitDiagnostics/{h}_{a}/fitDiagnostics.Test.root'.format(h=h,a=a)

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

            canvas = ROOT.TCanvas('c','c',50,50,800,600)
            canvas.SetRightMargin(0.05)
            canvas.SetTopMargin(0.06)

            frame.Draw()
            mi = frame.GetMinimum()
            if mi<0: frame.SetMinimum(0.1)
            frame.GetXaxis().SetTitle(config[x.GetName()]['xlabel'])
            frame.GetYaxis().SetTitle(config[x.GetName()]['ylabel'])

            if x.GetName()=='CMS_haa_x':
                if a<8.5:
                    canvas.SetLogy()
                    frame.SetMaximum(2000)
                if a>8.5 and a<11.5:
                    frame.SetMaximum(60 if 'PP' in ds.GetName() else 120)
                if a>11.5:
                    frame.SetMaximum(50 if 'PP' in ds.GetName() else 100)
            elif x.GetName()=='CMS_haa_y':
                frame.GetXaxis().SetRangeUser(0,800)
                canvas.SetLogy()
                frame.SetMaximum(1000)
            else:
                if a<8.5:
                    canvas.SetLogy()
                    frame.SetMaximum(2e6)
                    frame.SetMinimum(1e4)
                if a>8.5 and a<11.5:
                    frame.SetMaximum(1.5e5)
                if a>11.5:
                    frame.SetMaximum(2e4)

            frame.GetXaxis().SetLabelSize(0.05)
            frame.GetYaxis().SetLabelSize(0.05)

            CMS_lumi.cmsText = 'CMS'
            CMS_lumi.writeExtraText = isprelim
            CMS_lumi.extraText = 'Preliminary'
            CMS_lumi.lumi_13TeV = "%0.1f fb^{-1}" % (35.9)
            CMS_lumi.CMS_lumi(canvas,4,11)


            legend = ROOT.TLegend(0.4,0.6,0.92,0.92)
            legend.SetTextFont(42)
            legend.SetBorderSize(0)
            legend.SetFillColor(0)

            foundSig = False
            foundBkg = False
            foundObs = False
            toAdd = {}
            for prim in canvas.GetListOfPrimitives():
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

            canvas.Print('rooplot_haa_{}_{}_{}_{}.png'.format(ds.GetName(),x.GetName(),h,a))
            canvas.Print('rooplot_haa_{}_{}_{}_{}.pdf'.format(ds.GetName(),x.GetName(),h,a))

            x = obsiter.Next()
            

for h in [125,300,750]:
    for a in [7,11,15]:
        plot(h,a)
