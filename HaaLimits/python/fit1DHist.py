import ROOT, os, sys, argparse
from scipy import special

ROOT.gROOT.SetBatch()

from RunIIDatasetUtils import *


def parse_command_line(argv):
    parser = argparse.ArgumentParser(description='Create datacard')

    parser.add_argument('fitVars', type=str, nargs='*', default=[])
    parser.add_argument('--unblind', action='store_true', help='Unblind the datacards')
    parser.add_argument('--decayMode', action='store_true', help='Split by decay mode')
    parser.add_argument('--sumDecayModes', type=int, nargs='*', default=[])
    parser.add_argument('--parametric', action='store_true', help='Create parametric datacards')
    parser.add_argument('--unbinned', action='store_true', help='Create unbinned datacards')
    parser.add_argument('--addSignal', action='store_true', help='Insert fake signal')
    parser.add_argument('--addControl', action='store_true', help='Add control')
    parser.add_argument('--asimov', action='store_true', help='Use asimov dataset (if blind)')
    parser.add_argument('--project', action='store_true', help='Project to 1D')
    parser.add_argument('--do2DInterpolation', action='store_true', help='interpolate v MH and MA')
    parser.add_argument('--fitParams', action='store_true', help='fit parameters')
    parser.add_argument('--doubleExpo', action='store_true', help='Use double expo')
    parser.add_argument('--higgs', type=int, default=125, choices=[125,300,750])
    parser.add_argument('--pseudoscalar', type=int, default=7, choices=[5,7,9,11,13,15,17,19,21])
    parser.add_argument('--yFitFunc', type=str, default='', choices=['G','V','CB','DCB','DG','DV','B','G2','G3','errG','L','MB'])
    parser.add_argument('--xRange', type=float, nargs='*', default=[2.5,25])
    parser.add_argument('--yRange', type=float, nargs='*', default=[0,1000])
    parser.add_argument('--tag', type=str, default='')
    parser.add_argument('--chi2Mass', type=int, default=0)
    parser.add_argument('--selection', type=str, default='')
    parser.add_argument('--channel', type=str, nargs='*', default=['TauMuTauHad'], choices=['TauMuTauE','TauETauHad','TauMuTauHad','TauHadTauHad'])

    return parser.parse_args(argv)

def doubleCrystalBall(x, p):
    x = x[0]
    norm = p[0]
    mean = p[1]
    sigma = p[2]
    a1 = p[3]
    a2 = p[4]
    n1 = p[5]
    n2 = p[6]
    u   = (x-mean)/sigma;
    A1  = ROOT.TMath.Power(n1/ROOT.TMath.Abs(a1),n1)*ROOT.TMath.Exp(-a1*a1/2);
    A2  = ROOT.TMath.Power(n2/ROOT.TMath.Abs(a2),n2)*ROOT.TMath.Exp(-a2*a2/2);
    B1  = n1/ROOT.TMath.Abs(a1) - ROOT.TMath.Abs(a1);
    B2  = n2/ROOT.TMath.Abs(a2) - ROOT.TMath.Abs(a2);
    
    result = 1
    if u<-a1: result *= A1*ROOT.TMath.Power(B1-u,-n1);
    elif u<a2: result *= ROOT.TMath.Exp(-u*u/2);
    else: result *= A2*ROOT.TMath.Power(B2+u,-n2);
    
    return norm*result;

def doubleVoigtian(x, p):
    x = x[0]
    norm = p[0]
    mean = p[1]
    sig1 = p[2]
    sig2 = p[3]
    wid1 = p[4]
    wid2 = p[5]
    C1 = 1 / (ROOT.TMath.Sqrt(2.0)*sig1); 
    C2 = 1 / (ROOT.TMath.Sqrt(2.0)*sig2);
    A1 = 0.5*C1*wid1;
    A2 = 0.5*C2*wid2;
    U1 = C1*(x-mean);
    U2 = C2*(x-mean);
    Z1 = complex(U1, A1)
    Z2 = complex(U2, A2)
    Z1_at_mean = complex(0, A1)
    Z2_at_mean = complex(0, A2)
    voigt1_at_mean = norm * 0.5 * C1 * special.wofz(Z1_at_mean) 
    voigt2_at_mean = norm * 0.5 * C1 * special.wofz(Z2_at_mean) 
    scale_factor = voigt1_at_mean.real / voigt2_at_mean.real
    if x <= mean:
        voigt = special.wofz(Z1)
        return norm * 0.5 * C1 * voigt.real / ROOT.TMath.Power(ROOT.TMath.Pi(), 0.5)
    else:
        voigt = special.wofz(Z2)
        return norm * 0.5 * C1 * voigt.real / ROOT.TMath.Power(ROOT.TMath.Pi(), 0.5) * scale_factor
    

if __name__ == "__main__":
    signame = 'hm{h}_am{a}'
    
    #whichFunc = "DCB"
    whichFunc = "DV"

    channels = ['TauHadTauHad_2018']

    modes = ['signalRegion', 'sideBand']

    amasses = [5,7,9,10,11,12,13,14,15,17,18,19,20,21]
    hamap = {
        125:amasses
    } 
    signals=[signame.format(h='125',a=a) for a in hamap[125]]

    argv = sys.argv[1:]
    args = parse_command_line(argv)
    initUtils(args)

    initialValues={}
    initialValues['signalRegion']={}
    initialValues['sideBand']={}
    initialValues['signalRegion']['5']={}
    initialValues['sideBand']['5']={}
    initialValues['signalRegion']['18']={}
    initialValues['sideBand']['18']={}

    if whichFunc == "DCB":
        
        initialValues['signalRegion']['5']['p'] =    [1.5, 110, 18, 0.5, 1.5, 100, 0.001]
        initialValues['signalRegion']['5']['low'] =  [1.2, 100, 10, 0.1,   1, 50,     0]
        initialValues['signalRegion']['5']['high'] = [1.8, 120, 20, 1.5,  10, 200,  0.01]
        initialValues['sideBand']['5']['p'] =        [0.16, 110,  15, 0.5, 1.5, 100, 0.01]
        initialValues['sideBand']['5']['low'] =      [0.1,  90,  10, 0.1,  1, 1,    0]
        initialValues['sideBand']['5']['high'] =     [0.25, 120, 30, 2,    5, 200,  0.5]
    
        initialValues['signalRegion']['18']['p'] =    [1.5, 95,  18, 7.5, 0.5, 0.001, 100]
        initialValues['signalRegion']['18']['low'] =  [1.2, 90,  10, 1,   0.1, 0,     50]
        initialValues['signalRegion']['18']['high'] = [1.8, 100, 20, 10,  1.5, 0.01,  200]
        initialValues['sideBand']['18']['p'] =        [0.16, 92,  15, 4,  0.5, 0.01, 10]
        initialValues['sideBand']['18']['low'] =      [0.1,  80,  10, 1,  0.1, 0,    0]
        initialValues['sideBand']['18']['high'] =     [0.25, 110, 30, 10, 1.5, 10,  100]
        
    elif whichFunc == "DV":

        initialValues['signalRegion']['5']['p'] =    [100., 110, 18, 15, 8.0, 5.0]
        initialValues['signalRegion']['5']['low'] =  [1.,   100, 10,  5, 0.1, 0.1]
        initialValues['signalRegion']['5']['high'] = [200,  120, 25, 25,  50,  50]
        initialValues['sideBand']['5']['p'] =        [1.,   110, 15, 15, 8.0, 5.0]
        initialValues['sideBand']['5']['low'] =      [0.,   80,  10,0.1, 0.1, 0.1]
        initialValues['sideBand']['5']['high'] =     [10,   120, 30, 30,  50,  100]
    
        initialValues['signalRegion']['18']['p'] =    [1.,  95,  15, 18, 0.5, 8.0]
        initialValues['signalRegion']['18']['low'] =  [0.,  80,  10,  5, 0.1, 0.1]
        initialValues['signalRegion']['18']['high'] = [10,  100, 30, 50,  10,  50]
        initialValues['sideBand']['18']['p'] =        [1.,  92,  15, 18, 0.5, 8.0]
        initialValues['sideBand']['18']['low'] =      [0.,  80,   1, 0., 0.1, 0.1]
        initialValues['sideBand']['18']['high'] =     [10,  110, 20, 30,  50,  100]

    histMap={}
    for channel in channels:
        for mode in modes:
            modeTag=mode
            mode=channel+'_'+mode
            histMap[mode] = {}
            for proc in signals:
                #histMap[mode][proc] = getSignalHist(proc,channel,doUnbinned=True,region=modeTag)
                histMap[mode][proc] = getSignalHist(proc,channel,doUnbinned=True,var='visFourbodyMass',shift='nominal',region=modeTag)
    

    for channel in channels:
        for mode in modes:
            modeTag=mode
            mode=channel+'_'+mode
            for proc in signals:
                #print "debug", mode, proc
                region = mode.split("_")[-1]
                amass = proc.split("_")[-1].replace('am','')
                if not "am5" in proc and not "am18" in proc: continue
                args = histMap[mode][proc].get()
                xVar = args.find('invMassMuMu')
                yVar = args.find('visFourbodyMass')
                name = histMap[mode][proc].GetName()
                h_2d =  histMap[mode][proc].createHistogram(xVar, yVar, 100, 500, '', name+'_hist')
                h_y = h_2d.ProjectionY()

                print h_y, h_y.Integral()

                

                if whichFunc == "DCB":
                    if region == "signalRegion": y = 300
                    else: y = 300
                    fitter = ROOT.TF1('fitter', doubleCrystalBall, 0, y, 7)
                    fitter.SetParNames("norm", "mean", "sigma", "a1", "a2", "n1", "n2")
                    fitter.SetParameters(initialValues[region][amass]['p'][0],
                                         initialValues[region][amass]['p'][1],
                                         initialValues[region][amass]['p'][2],
                                         initialValues[region][amass]['p'][3],
                                         initialValues[region][amass]['p'][4],
                                         initialValues[region][amass]['p'][5],
                                         initialValues[region][amass]['p'][6])
                                
                    fitter.SetParLimits(1, initialValues[region][amass]['low'][1], initialValues[region][amass]['high'][1])
                    fitter.SetParLimits(2, initialValues[region][amass]['low'][2], initialValues[region][amass]['high'][2])
                    fitter.SetParLimits(3, initialValues[region][amass]['low'][3], initialValues[region][amass]['high'][3])
                    fitter.SetParLimits(4, initialValues[region][amass]['low'][4], initialValues[region][amass]['high'][4])
                    fitter.SetParLimits(5, initialValues[region][amass]['low'][5], initialValues[region][amass]['high'][5])
                    fitter.SetParLimits(6, initialValues[region][amass]['low'][6], initialValues[region][amass]['high'][6])

                elif whichFunc == "DV":
                    y = 300
                    fitter = ROOT.TF1('fitter', doubleVoigtian, 0, y, 6)
                    fitter.SetParNames("norm", "mean", "sigma1", "sigma2", "width1", "width2")
                    fitter.SetParameters(initialValues[region][amass]['p'][0],
                                         initialValues[region][amass]['p'][1],
                                         initialValues[region][amass]['p'][2],
                                         initialValues[region][amass]['p'][3],
                                         initialValues[region][amass]['p'][4],
                                         initialValues[region][amass]['p'][5])
                                
                    fitter.SetParLimits(1, initialValues[region][amass]['low'][1], initialValues[region][amass]['high'][1])
                    fitter.SetParLimits(2, initialValues[region][amass]['low'][2], initialValues[region][amass]['high'][2])
                    fitter.SetParLimits(3, initialValues[region][amass]['low'][3], initialValues[region][amass]['high'][3])
                    fitter.SetParLimits(4, initialValues[region][amass]['low'][4], initialValues[region][amass]['high'][4])
                    fitter.SetParLimits(5, initialValues[region][amass]['low'][5], initialValues[region][amass]['high'][5])
                    
                    
                else:
                    fitter = ROOT.TF1('fitter', 'gaus', 80, 200)
                
                h_y.Fit("fitter", '')

                c=ROOT.TCanvas("myCanvas", "myCanvas")
                h_y.Draw()
                h_y.GetXaxis().SetRangeUser(0,300)
                fitter.SetLineColor(2)
                fitter.Draw('same')

                c.SaveAs('./figures/signalFitsTunning/'+name+whichFunc+".pdf")
    
    
