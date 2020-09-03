import logging
from array import array
import ROOT

from CombineLimitsRunII.Plotter.LimitPlotter import LimitPlotter

ROOT.gROOT.SetBatch()

logging.basicConfig(format='%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')

doSig = False
blind = True
doMatrix = False
doGrid = False #True
doDouble = False #True
doDM = False
doDM0and1 = False
autoSkip = False
strictChecking = False
isprelim = False
amasses = [5,7,9,11,13,15,17,19,21]
hmasses = [125] #[125,300,750]

#hmasses = [125,300]
#hmasses = [750] # for now since it is done
amasses_full = [x*.1 for x in range(36,210,1)] + [21.0]
#amasses_full = [x*.1 for x in range(35,210,2)] + [21.1]
#amasses_full = [x*.1 for x in range(36,210,2)] + [21.0]
#if doGrid:
#    amasses_full = [3.6] + [x*.1 for x in range(40,210,5)] + [21.0]

#hdfs_dir = '/hdfs/store/user/dntaylor/2018-05-17_MuMuTauTauLimits_v3' # added control
#hdfs_dir = '/hdfs/store/user/dntaylor/2018-06-05_MuMuTauTauLimits_v1' # added control
#hdfs_dir = '/hdfs/store/user/dntaylor/2018-06-08_MuMuTauTauLimits_v1' # added chi2 cut
#hdfs_dir = '/hdfs/store/user/dntaylor/2018-06-18_MuMuTauTauLimits_v2' # exclude < 3.5
#hdfs_dir = '/hdfs/store/user/dntaylor/2018-08-17_MuMuTauTauLimits_v1' # mm only, with separating Jpis/upsilon peaks
#hdfs_dir = '/hdfs/store/user/dntaylor/2018-08-30_MuMuTauTauLimits_v1' # mm and tt
#hdfs_dir = '/hdfs/store/user/dntaylor/2018-09-02_MuMuTauTauLimits_v1' # mm tt h
#hdfs_dir = '/hdfs/store/user/dntaylor/2018-09-02_MuMuTauTauLimits_v2' # mm tt h
#hdfs_dir = '/hdfs/store/user/dntaylor/2018-09-04_MuMuTauTauLimits_v1' # mm tt h, tt modelled by landua + upsilon=gaussian
#hdfs_dir = '/hdfs/store/user/dntaylor/2018-09-04_MuMuTauTauLimits_v2' # mm tt h, tt modelled by landua only
#hdfs_dir = '/hdfs/store/user/dntaylor/2018-09-06_MuMuTauTauLimits_v1' # mm tt h, tt modelled by landua + upsilon=gaussian, add 300 750
#hdfs_dir = '/hdfs/store/user/dntaylor/2018-09-09_MuMuTauTauLimits_v1' # mm tt h, tt sig l+g
#hdfs_dir = '/hdfs/store/user/dntaylor/2018-09-27_MuMuTauTauLimits_v1' # mm tt h, tt sig l+g, new fits, especially tt
#hdfs_dir = '/hdfs/store/user/dntaylor/2018-10-02_MuMuTauTauLimits_v1' # mm tt h, h switch to DB
#hdfs_dir = '/hdfs/store/user/dntaylor/2018-10-10_MuMuTauTauLimits_v1' # fix 2d limits
#hdfs_dir = '/hdfs/store/user/dntaylor/2018-10-15_MuMuTauTauLimits_v1' # h no err*exp
#hdfs_dir = '/hdfs/store/user/dntaylor/2018-10-22_MuMuTauTauLimits_v1' # fix to 2D again, PP only
#hdfs_dir = '/hdfs/store/user/dntaylor/2018-10-23_MuMuTauTauLimits_v1' # fix to 2D again, PP and FP
#hdfs_dir = '/hdfs/store/user/dntaylor/2018-10-25_MuMuTauTauLimits_v2' # fix to 2D again, PP and FP, binned asimov
#hdfs_dir = '/hdfs/store/user/dntaylor/2018-12-14_MuMuTauTauLimits_v1' # new fitting mode
#hdfs_dir = '/hdfs/store/user/dntaylor/2018-12-18_MuMuTauTauLimits_v1' # fix to tt/h modes
#hdfs_dir = '/hdfs/store/user/dntaylor/2019-01-02_MuMuTauTauLimits_v2' # only a few uncertainties, fix to normalization
#hdfs_dir = '/hdfs/store/user/dntaylor/2019-01-03_MuMuTauTauLimits_v1' # trying to remove binning
#hdfs_dir = '/hdfs/store/user/dntaylor/2019-01-07_MuMuTauTauLimits_v1' # switch to splines rather than fit functions in 1D fits
#hdfs_dir = '/hdfs/store/user/dntaylor/2019-01-08_MuMuTauTauLimits_v1' # remove fake rate
#hdfs_dir = '/hdfs/store/user/dntaylor/2019-01-09_MuMuTauTauLimits_v1' # remove MuonEn
#hdfs_dir = '/hdfs/store/user/dntaylor/2019-01-09_MuMuTauTauLimits_v2' # remove fake and allow lambda to float
#hdfs_dir = '/hdfs/store/user/dntaylor/2019-01-09_MuMuTauTauLimits_v3' # do binning again
#hdfs_dir = '/hdfs/store/user/dntaylor/2019-01-09_MuMuTauTauLimits_v4' # widen mm h
#hdfs_dir = '/hdfs/store/user/dntaylor/2019-01-10_MuMuTauTauLimits_v1' # back with all systs
#hdfs_dir = '/hdfs/store/user/dntaylor/2019-02-05_MuMuTauTauLimits_v1' # changing names, note, binning messed up again, rerun
#hdfs_dir = '/hdfs/store/user/dntaylor/2019-02-06_MuMuTauTauLimits_v1' # fixed binning
#hdfs_dir = '/hdfs/store/user/dntaylor/2019-02-08_MuMuTauTauLimits_v1' # fixed binning, unblinded
#hdfs_dir = '/hdfs/store/user/dntaylor/2019-02-11_MuMuTauTauLimits_v1' # fixed systs
#hdfs_dir = '/hdfs/store/user/dntaylor/2019-02-20_MuMuTauTauLimits_v1' # freely floating normalizations in FP/control
#hdfs_dir = '/hdfs/store/user/dntaylor/2019-03-06_MuMuTauTauLimits_v1' # update tau SF
#hdfs_dir = '/hdfs/store/user/dntaylor/2019-04-01_MuMuTauTauLimits_v1' # add DM
#hdfs_dir = '/hdfs/store/user/dntaylor/2019-04-03_MuMuTauTauLimits_v1' # two exp background for mm h
#hdfs_dir = '/hdfs/store/user/dntaylor/2019-05-13_MuMuTauTauLimits_v2' # add neglected uncertainty
#hdfs_dir = '/hdfs/store/user/dntaylor/2019-05-14_MuMuTauTauLimits_v1' # add regions back
#hdfs_dir = '/hdfs/store/user/dntaylor/2019-05-15_MuMuTauTauLimits_noMuonEnTauEn_v1' # no muon or tau en
#hdfs_dir = '/hdfs/store/user/dntaylor/2019-05-16_MuMuTauTauLimits_noQCD_v1' # no qcd
#hdfs_dir = '/hdfs/store/user/dntaylor/2019-05-17_MuMuTauTauLimits_v1' # back to normal 
#hdfs_dir = '/hdfs/store/user/dntaylor/2019-07-16_MuMuTauTauLimits_v1' # switch to poly
#hdfs_dir = '/hdfs/store/user/dntaylor/2019-07-17_MuMuTauTauLimits_v1' # switch to different poly for control and signal
#hdfs_dir = '/hdfs/store/user/dntaylor/2019-07-21_MuMuTauTauLimits_v1' # and try double expo again
#hdfs_dir = '/hdfs/store/user/dntaylor/2019-07-27_MuMuTauTauLimits_v1' # with new muon en and tau fake rate
#hdfs_dir = '/hdfs/store/user/dntaylor/2019-07-30_MuMuTauTauLimits_v1' # fix tau en
#hdfs_dir = '/hdfs/store/user/dntaylor/2019-08-26_MuMuTauTauLimits_v1' # back to expos, wider upsilon
#hdfs_dir = '/hdfs/store/user/dntaylor/2019-08-27_MuMuTauTauLimits_v1' # lower lowmass top edge to 8.5
#hdfs_dir = '/hdfs/store/user/dntaylor/2019-09-18_MuMuTauTauLimits_v1' # to fixed slope
#hdfs_dir='/eos/uscms/store/user/rhabibul/HtoAA/HtoAA2017/Limits/TauETauHad'
hdfs_dir='/eos/uscms/store/user/rhabibul/HtoAA/HtoAA2017Deep/TauMuTauHad/Limits/mediumDeepVSjet/'
# this is the double expo test
if doDouble:
    #hdfs_dir = '/hdfs/store/user/dntaylor/2019-10-18_MuMuTauTauLimits_DoubleExpo_v1' # test
    hdfs_dir = '/hdfs/store/user/dntaylor/2019-10-21_MuMuTauTauLimits_DoubleExpo_v1' # fixed upsilon
    #hdfs_dir = '/hdfs/store/user/dntaylor/2019-11-01_MuMuTauTauLimits_DoubleExpoNewCont_veryVerbose_v1' # combine cont1/cont2
    #hdfs_dir = '/hdfs/store/user/dntaylor/2019-11-05_MuMuTauTauLimits_DoubleExpoNewContFakeNorm_veryVerbose_v1' # combine cont1/cont2, fake as norm only

#grid_dir = '/hdfs/store/user/dntaylor/2019-08-14_MuMuTauTauLimits_MergedGridPacks_v1'
#grid_dir = '/hdfs/store/user/dntaylor/2019-10-20_MuMuTauTauLimits_MergedGridPacks_v1'
#grid_dir = '/hdfs/store/user/dntaylor/2019-10-27_MuMuTauTauLimits_MergedGridPacks_v1'
#grid_dir = '/hdfs/store/user/dntaylor/2019-10-28_MuMuTauTauLimits_MergedGridPacks_v2' # modify rRelAcc/rAbsAcc
#grid_dir = '/hdfs/store/user/dntaylor/2019-11-03_MuMuTauTauLimits_MergedGridPacks_v1' # first pass with double expo and everyone submitting
#grid_dir = '/hdfs/store/user/dntaylor/2019-11-10_MuMuTauTauLimits_MergedGridPacks_v1' # current status
#grid_dir = '/hdfs/store/user/dntaylor/2019-11-14_MuMuTauTauLimits_MergedGridPacks_v1' # current status
#grid_dir = '/hdfs/store/user/dntaylor/2019-11-24_MuMuTauTauLimits_MergedGridPacks_v1' # current status
#grid_dir = '/hdfs/store/user/dntaylor/2019-11-26_MuMuTauTauLimits_MergedGridPacks_v2' # current status --fullGrid
#grid_dir = '/hdfs/store/user/dntaylor/2019-11-27_MuMuTauTauLimits_MergedGridPacks_v1' # current status --fullGrid, rMax
#prev_grid_dir = '/hdfs/store/user/dntaylor/2019-11-27_MuMuTauTauLimits_MergedGridPacks_v1' # current status --fullGrid, rMax
#grid_dir = '/hdfs/store/user/dntaylor/2019-11-29_MuMuTauTauLimits_MergedGridPacks_v1' # current status --fullGrid, rMax
#grid_dir = '/hdfs/store/user/dntaylor/2019-12-09_MuMuTauTauLimits_MergedGridPacks_v1' # current status --fullGrid, rMax
grid_dir = '/hdfs/store/user/dntaylor/2019-12-10_MuMuTauTauLimits_MergedGridPacks_v2' # current status --fullGrid, rMax

#hs_grid_dir = '/hdfs/store/user/dntaylor/2019-11-26_MuMuTauTauLimits_MergedGridPacks_HighStat_v1' # current high stat for better sigma bands
#hs_grid_dir = '/hdfs/store/user/dntaylor/2019-11-26_MuMuTauTauLimits_MergedGridPacks_HighStat_v2' # current high stat for better sigma bands --fullGrid
hs_grid_dir = '/hdfs/store/user/dntaylor/2019-11-27_MuMuTauTauLimits_MergedGridPacks_HighStat_v1' # current high stat for better sigma bands --fullGrid, rMax
#higgsCombineHtoAAH125A20_mm_h_parametric_highmassWith1DFitsDVteth.AsymptoticLimits.mH125.root 

#tag = 'with1DFits'
tag = 'REGIONWith1DFits1ExpoDVmediumDeepVSjet'
if doDouble: tag = 'REGIONWith1DFitsDoubleExpoDVmediumDeepVSjet'
if doDM: 
    tag += 'DM'
elif doDM0and1:
    tag += 'DM0and1'

pdir = 'haa-grid' if doGrid else 'haa'
if doDM: 
    pdir += 'DM'
elif doDM0and1:
    pdir += 'DM0and1'


modelstrings = ['','I','II','III','IV']


modes = []
#mmmt_mm_h_parametric_unbinned_highmassWith1DFits1ExpoDV.root
#modes += ['mmmt_mm_parametric_unbinned_{}'.format(tag)]
#for var in ['tt','h']:
for var in ['h']:
    modes += ['mmmt_mm_{}_parametric_unbinned_{}'.format(var,tag)]

if doGrid:
    modes = ['mmmt_mm_h_parametric_unbinned_{}'.format(tag)]

allModes = []
for mode in modes:
    allModes += [mode]
    if doSig: allModes += [mode+'_wSig']

quartiles = {}
quartilesbr = {}
quartilesxsec = {}
quartilesxsecsm = {}
quartilesmodels = {}
tanbmodels = {}
goodas = {}
goodqs = {}

plotter = LimitPlotter()

br = 0.001 # input was 0.1% h xsec
hxsec = {}
hxsec_sm = {
    125: 48.52+3.779,
}

toSkip = {
    'mmmt_mm_h_parametric_unbinned_{}'.format(tag): {
        # expected
        #125: [],
        #300: [],
        #750: [],
        # observed
        125: [],
        300: [9.8,12.3],
        750: [],
    }
}

if doDouble:
    toSkip = {
        'mmmt_mm_h_parametric_unbinned_{}'.format(tag): {
            125: [18.4],
            300: [9.8],
            750: [],
        }
    }

if doGrid:
    toSkip = {
        'mmmt_mm_h_parametric_unbinned_{}'.format(tag): {
            125: [],
            300: [9.3,10.8,15.8],
            750: [7.8,9.9],
        }
    }


#modelfile = 'brato30mumutautau_alltypes_temp.root'
#modeltfile = ROOT.TFile.Open(modelfile)
mfile = 'braa2mmtt.root'
mtfile = ROOT.TFile.Open(mfile)

modeltypes = [1,2,3,4]
tanbs = [1,1.5,2,3,20,50]
goodtanbs = [x*0.01 for x in range(5,505,5)]
goodtanbsfull = [x*0.01 for x in range(50,5050,50)]
modelbrname = 'Model Type=   {}/tanB={}'

def getModels2D():
    models = {}
    for m in modeltypes:
        models[m] = mtfile.Get('model_type{}'.format(m))
    return models

def getModels(scale=1):

    models = {}
    for m in modeltypes:
        models[m] = {}
        for t in tanbs:
            graph = modeltfile.Get(modelbrname.format(m,t))
            xs = []
            ys = []
            x, y = ROOT.Double(0), ROOT.Double(0)
            for i in range(graph.GetN()):
                graph.GetPoint(i,x,y)
                xs += [float(x)]
                ys += [float(y)*scale]
            graph = ROOT.TGraph(len(xs),array('d',xs),array('d',ys))
            models[m][t] = graph
    return models

dm = 0.1
dt = 0.1
allmasses = [x*dm for x in range(int(1/dm),int(35/dm)+1,1)]
alltanbs  = [x*dt for x in range(int(1/dt),int(50/dt)+1,1)]

#models2D = getModels2D()

def getModelsAlt(scale=1):
    models = {}
    for m in modeltypes:
        models[m] = {}
        hist = models2D[m]
        for t in alltanbs:
            xs = allmasses
            ys = []
            for ma in xs:
                ys += [hist.GetBinContent(hist.FindBin(ma,t))*scale]
            graph = ROOT.TGraph(len(xs),array('d',xs),array('d',ys))
            models[m][t] = graph
    return models

# Load the "BR" one with the fixed quarkonia content
mtmap = {1:'I',2:'II',3:'III',4:'IV'}
def load_br_graph(m,tb):
    if m==1:
        fname = 'haa_br_data/BR/BR_I.dat'
    else:
        fname = 'haa_br_data/BR/BR_{}_{:.1f}.dat'.format(mtmap[m],tb)
    xs = []
    ys = []
    with open(fname) as f:
        for line in f.readlines():
            vals = line.split()
            ma = float(vals[1])
            amm = float(vals[6])
            att = float(vals[5])
            aammtt = 2*amm*att
            xs += [ma]
            ys += [aammtt]
    return ROOT.TGraph(len(xs),array('d',xs),array('d',ys))

tanbsq = [0.5,0.6,0.7,0.8,0.9,1.0,1.5,2.0,2.5,3.0,3.5,4.0,4.5,5.0,5.5,6.0,6.5,7.0,7.5,8.0,8.5,9.0,9.5,10.0]
def load_br():
    models = {}
    for m in modeltypes:
        models[m] = {}
        for t in tanbsq:
            models[m][t] = load_br_graph(m,t)
    return models
    


#models = getModels()
#modelsAlt = getModelsAlt()
#modelsQ = load_br()

# overwrite tanbs for use with quarkonia
tanbs = tanbsq

label = 'H #rightarrow aa #rightarrow #mu#mu#tau#tau (pb)'
labelbr = '#frac{#sigma_{H}}{#sigma_{SM}}B(H #rightarrow aa #rightarrow #mu#mu#tau#tau)'
labelbrbsm = '#frac{#sigma_{H}}{#sigma_{SM}}B(H #rightarrow aa #rightarrow #mu#mu#tau#tau)'


def get_model_br(a,model,tanb):
    #graph = models[model][tanb]
    #graph = modelsAlt[model][tanb]
    graph = modelsQ[model][tanb]
    return graph.Eval(a)

def get_model_scale(a,model,tanb):
    y = get_model_br(a,model,tanb)
    return br/y if y else 0

def get_tanb_graph(a,model):
    scales = []
    #for t in tanbs:
    #for t in alltanbs:
    for t in tanbsq:
        scales += [get_model_scale(a,model,t)]
    #graph = ROOT.TGraph(len(scales),array('d',tanbs),array('d',scales))
    #graph = ROOT.TGraph(len(scales),array('d',alltanbs),array('d',scales))
    graph = ROOT.TGraph(len(scales),array('d',tanbsq),array('d',scales))
    return graph


# high stat
hs_amasses = [3.6,3.8,4.0,4.5,5.0,5.5,6.0,6.5,7.0,7.5,8.0,8.5,
              8.0,8.2,8.4,8.6,8.8,9.0,9.2,9.4,9.6,9.8,10.0,10.2,10.4,10.6,10.8,11.0,11.2,11.4,
              11.0,11.5,12.0,13.0,14.0,15.0,16.0,17.0,18.0,19.0,20.0,21.0]

def readQs(mode,h,a):
    if a % 1 < 1e-10: astr = '{0:.0f}'.format(a)
    elif (10*a) % 1 < 1e-10: astr = '{0:.1f}'.format(a)
    elif (100*a) % 1 < 1e-10: astr = '{0:.2f}'.format(a)
    else: astr = 'HELP'

    good = []

    if doGrid:

        #this_grid_dir = hs_grid_dir if a in hs_amasses else grid_dir
        # TODO: temp
        this_grid_dir = grid_dir

        # check if grid is populated
        tfile = ROOT.TFile.Open('{working}/{m}/{h}/{a}/merged.root'.format(working=this_grid_dir,h=h,a=a,m=mode))
        try:
            keys = tfile.Get('toys').GetListOfKeys()
            rs = [[r for r  in key.GetName().split('_') if r.startswith('r')] for key  in keys]
            rs = [r[0] for r in rs if r]
            rs = set(rs)
            njobs = tfile.Get('limit').GetEntries()
            if njobs<10 or len(rs)<5:
                logging.warning('Insufficient grid {} {} {}'.format(mode,h,a))
                return [], []
        except:
            logging.warning('Failed to get grid {} {} {}'.format(mode,h,a))



        qs = []
        for q in ['0.025','0.160','0.500','0.840','0.975','']:
            if q:
                if 'parametric' in mode:
                    tfile = ROOT.TFile.Open('{working}/{m}/{h}/{a}/higgsCombineTest.HybridNew.mH{h}.quant{q}.root'.format(working=this_grid_dir,h=h,a=a,m=mode,q=q))
                else:
                    tfile = ROOT.TFile.Open('{working}/{m}/{h}/{a}/higgsCombineTest.HybridNew.mH{h}.quant{q}.root'.format(working=this_grid_dir,h=h,a=a,m=mode,q=q))
            else:
                if 'parametric' in mode:
                    tfile = ROOT.TFile.Open('{working}/{m}/{h}/{a}/higgsCombineTest.HybridNew.mH{h}.root'.format(working=this_grid_dir,h=h,a=a,m=mode,q=q))
                else:
                    tfile = ROOT.TFile.Open('{working}/{m}/{h}/{a}/higgsCombineTest.HybridNew.mH{h}.root'.format(working=this_grid_dir,h=h,a=a,m=mode,q=q))
            try:
                tree = tfile.Get("limit")
            except:
                logging.error('Failed to open {} {} {}'.format(mode,h,a))
                return [], []
            for row in tree:
                qs += [row.limit]


        for i,q in enumerate(qs):
            if i in [2,5]: # say expected and observed always good for now
                good += [True]
            #elif i in [0,1,3,4] and h==750: # always use high stat sigma bands
            #    good += [a in hs_amasses]
            elif i<2:
                good += [q<qs[i+1]]
            elif i>2:
                good += [q>qs[i-1]]
            else:
                good += [False]

    else:

        if 'parametric' in mode:
            #tfile = ROOT.TFile.Open('{hdfs}/{m}/{h}/higgsCombineHToAAH{h}A{a:.1f}_{m}.AsymptoticLimits.mH{h}.root'.format(hdfs=hdfs_dir,h=h,a=a,m=mode,astr=astr))
            #/eos/uscms/store/user/rhabibul/HtoAA/HtoAA2017/Limits/TauMuTauHad/highmass/125/
            tfile = ROOT.TFile.Open('{hdfs}/{m}/{h}/{a}/higgsCombineHtoAAH125AX_mm_h_parametric_{m}With1DFits1ExpoDVmediumDeepVSjet.AsymptoticLimits.mH{h}.root'.format(hdfs=hdfs_dir,h=h,a=a,m=mode.split('_')[-1].split('W')[0]))
            
        else:
            tfile = ROOT.TFile.Open('{hdfs}/{m}/{h}/higgsCombineHToAAH{h}A{a}_{m}.AsymptoticLimits.mH{h}.root'.format(hdfs=hdfs_dir,h=h,a=a,m=mode))
        try:
            tree = tfile.Get("limit")
        except:
            logging.error('Failed to open {} {} {}'.format(mode,h,a))
            return [], []
        qs = []
        for i, row in enumerate(tree):
            qs += [row.limit]
            good += [True]

    return qs, good
    #higgsCombineHtoAAH125AX_mm_h_parametric_upsilonWith1DFits1ExpoDV.AsymptoticLimits.mH125.root 
    #/eos/uscms/store/user/rhabibul/HtoAA/HtoAA2017/Limits/TauMuTauHad/highmass/125/

regionXs = {
    'lowmass' : [3.6,8],
    'upsilon' : [8,11.5],
    'highmass': [11.5,21],
}

for m in allModes:
    if 'REGION' in m:
        mlow = m.replace('REGION','lowmass')
        dfile = ROOT.TFile.Open('datacards_shape/MuMuTauTau/{m}.root'.format(m=mlow))
        regionModes = [m.replace('REGION',x) for x in ['lowmass','upsilon','highmass']]
    else:
        dfile = ROOT.TFile.Open('datacards_shape/MuMuTauTau/{m}.root'.format(m=m))
        regionModes = [m]
    ws = dfile.Get('w')

    quartiles[m] = {}
    quartilesbr[m] = {}
    quartilesxsec[m] = {}
    quartilesxsecsm[m] = {}
    quartilesmodels[m] = {}
    tanbmodels[m] = {}
    goodas[m] = {}
    goodqs[m] = {}

    for rm in regionModes:

        quartiles[rm] = {}
        quartilesbr[rm] = {}
        quartilesxsec[rm] = {}
        quartilesxsecsm[rm] = {}
        quartilesmodels[rm] = {}
        tanbmodels[rm] = {}
        goodas[rm] = {}
        goodqs[rm] = {}
        for h in hmasses:
            # in the workspace, these are BSM (ggF N3LO)
            # alternatively, for h(125), there is SM (ggF N3LO + NLO EW)
            # note, there is also a difference in the VBF between the two
            ws.var('MH').setVal(h)
            gg = ws.function('xsec_ggF_N3LO').getVal()
            vbf = ws.function('xsec_VBF').getVal()
            hxsec[h] = gg+vbf

            #if h == 750 and 'mm_para' not in m: continue
            goodas[rm][h] = []
            quartiles[rm][h] = {}
            quartilesbr[rm][h] = {}
            quartilesxsec[rm][h] = {}
            quartilesxsecsm[rm][h] = {}
            quartilesmodels[rm][h] = {}
            tanbmodels[rm][h] = {}
            goodqs[rm][h] = {}

            thisas = amasses_full if 'parametric' in rm else amasses

            for rmk, rmx in regionXs.iteritems():
                if rmk in rm:
                    thisas = [ta for ta in thisas if ta>=rmx[0] and ta<=rmx[1]]

            prev = 0
            for a in thisas:
                thisMode = rm

                #if 'hkf' in thisMode:
                #    thisMode = thisMode + '_chi2H{}'.format(h)

                qs, goodqs[rm][h][a] = readQs(thisMode,h,a)
                if a==thisas[0] or a==thisas[-1]: # override
                    goodqs[rm][h][a] = [True]*6
                if not qs: continue
                outline = ':'.join(['{:.3f}'.format(x) for x in qs])
                logging.info('{0}:{1}: Limits: {2}'.format(h,a,outline))

                good = True
                if m in toSkip:
                    if h in toSkip[m]:
                        if any([abs(ia-a)<0.01 for ia in toSkip[m][h]]):
                            good = False
                            logging.info('Will manually skip {} {}'.format(h,a))

                strictGood = True
                pq = 0
                for iq in qs[:5]:
                    if iq<pq:
                        strictGood = False
                        break
                    pq = iq

                if strictChecking:
                    good = good and strictGood
                    if not strictGood:
                        logging.info('Strict checking skip {} {}'.format(h,a))
        
                if len(qs)==6 and good:
                    curr = qs
                    if prev:
                        if abs(prev[2]-curr[2])/prev[2]<0.3 or not autoSkip: # exclude "jumps"
                        #if abs(prev[2]-curr[2])/prev[2]<5 or not autoSkip: # exclude "jumps"
                            goodas[rm][h] += [a]
                            prev = curr
                        else:
                            logging.warning('Skipping a mass')
                    else:
                        goodas[rm][h] += [a]
                        prev = curr
                    if curr[-1] > prev[5] or curr[-1] < prev[0]:
                        logging.warning('More than 2 sigma difference in observed')

                quartiles[rm][h][a] = qs
                quartilesxsec[rm][h][a] = [q * hxsec[h] * br for q in qs]
                quartilesbr[rm][h][a] = [q * br for q in qs]
                quartilesmodels[rm][h][a] = {}
                if h==125:
                    quartiles[rm][h][a] = [q * hxsec[h]/hxsec_sm[h] for q in qs]
                    quartilesxsecsm[rm][h][a] = [q * hxsec_sm[h] * br for q in qs]
                    quartilesbr[rm][h][a] = [q * br * hxsec[h]/hxsec_sm[h] for q in qs]
                    tanbmodels[rm][h][a] = {}
                    # for model in modeltypes:
                    #     quartilesmodels[rm][h][a][model] = {}
                    #     for tanb in tanbs:
                    #         s = get_model_scale(a,model,tanb)
                    #         quartilesmodels[rm][h][a][model][tanb] = [q * s * hxsec[h]/hxsec_sm[h] for q in qs]
                    #     tanbmodels[rm][h][a][model] = get_tanb_graph(a,model)
                

    
    if 'REGION' in m:
        for h in hmasses:
            quartiles[m][h] = [quartiles[rm][h] for rm in regionModes]
            quartilesbr[m][h] = [quartilesbr[rm][h] for rm in regionModes]
            quartilesxsec[m][h] = [quartilesxsec[rm][h] for rm in regionModes]
            quartilesmodels[m][h] = [quartilesmodels[rm][h] for rm in regionModes]
            if h==125:
                quartilesxsecsm[m][h] = [quartilesxsecsm[rm][h] for rm in regionModes]
               # tanbmodels[m][h] = [tanbmodels[rm][h] for rm in regionModes]
            goodas[m][h] = [goodas[rm][h] for rm in regionModes]
            goodqs[m][h] = [goodqs[rm][h] for rm in regionModes]
        plotMethod = plotter.plotLimitMulti
        plotMethod2D = plotter.plotLimit2DMulti
        plotMethod2DProjection = plotter.plotLimit2DProjectionMulti
    else:
        plotMethod = plotter.plotLimit
        plotMethod2D = plotter.plotLimit2D
        plotMethod2DProjection = plotter.plotLimit2DProjection


    b = blind
    if 'wSig' in m: b = False

    # dump values
    # from DevTools.Utilities.utilities import dumpResults
    # dumpResults({'goodas': goodas[m], 'quartiles': quartiles[m]}, 'HAA', m)
    # continue

  
    for h in hmasses:
        #if h == 750 and 'mm_para' not in m: continue
        thisbr = labelbr if h==125 else labelbrbsm
        lpos = 34 if 'mm_para' in m else 24

        #legendtitle = '#splitline{{m_{{H}} = {h} GeV}}{{95% CL upper limits}}'.format(h=h)
        legendtitle = '95% CL upper limits'
        additionaltext = 'm_{{H}} = {h} GeV'.format(h=h)

        ymin = 0
        ymax = 1
        if h==300: ymax = 2
        if h==750: ymax = 5
        plotMethod(       goodas[m][h], quartiles[m][h],    '{pdir}/{m}-limits/{h}'.format(pdir=pdir,h=h,m=m),                  goodqs=goodqs[m][h], xaxis='m_{a} (GeV)',              blind=b,logy=0,ymin=ymin,ymax=ymax,legendpos=lpos,numcol=1,legendtitle=legendtitle,additionaltext=additionaltext,isprelim=isprelim)
        plotMethod(       goodas[m][h], quartiles[m][h],    '{pdir}/{m}-limits/{h}_smooth'.format(pdir=pdir,h=h,m=m),           goodqs=goodqs[m][h], xaxis='m_{a} (GeV)', smooth=True, blind=b,logy=0,ymin=ymin,ymax=ymax,legendpos=lpos,numcol=1,legendtitle=legendtitle,additionaltext=additionaltext,isprelim=isprelim)

        ymin = 1e-3
        ymax = 2
        if h==300: ymax = 5
        if h==750: ymax = 5e1
        if h==750: ymin = 1e-1
        plotMethod(       goodas[m][h], quartiles[m][h],    '{pdir}/{m}-limits/{h}_log'.format(pdir=pdir,h=h,m=m),              goodqs=goodqs[m][h], xaxis='m_{a} (GeV)',              blind=b,logy=1,ymin=ymin,ymax=ymax,legendpos=lpos,numcol=1,legendtitle=legendtitle,additionaltext=additionaltext,isprelim=isprelim)
        plotMethod(       goodas[m][h], quartiles[m][h],    '{pdir}/{m}-limits/{h}_log_smooth'.format(pdir=pdir,h=h,m=m),       goodqs=goodqs[m][h], xaxis='m_{a} (GeV)', smooth=True, blind=b,logy=1,ymin=ymin,ymax=ymax,legendpos=lpos,numcol=1,legendtitle=legendtitle,additionaltext=additionaltext,isprelim=isprelim)

        ymin = 0
        ymax = 1e-1
        if h==300: ymax = 2e-1
        if h==750: ymax = 1e-2
        plotMethod(       goodas[m][h], quartilesxsec[m][h],'{pdir}/{m}-limits/{h}_xsec'.format(pdir=pdir,h=h,m=m),             goodqs=goodqs[m][h], xaxis='m_{a} (GeV)',              yaxis=label,blind=b,logy=0,ymin=ymin,ymax=ymax,legendpos=lpos,numcol=1,plotunity=False,leftmargin=0.20,legendtitle=legendtitle,additionaltext=additionaltext,isprelim=isprelim)
        plotMethod(       goodas[m][h], quartilesxsec[m][h],'{pdir}/{m}-limits/{h}_xsec_smooth'.format(pdir=pdir,h=h,m=m),      goodqs=goodqs[m][h], xaxis='m_{a} (GeV)', smooth=True, yaxis=label,blind=b,logy=0,ymin=ymin,ymax=ymax,legendpos=lpos,numcol=1,plotunity=False,leftmargin=0.20,legendtitle=legendtitle,additionaltext=additionaltext,isprelim=isprelim)

        ymin = 1e-4
        ymax = 1e-1
        #if h==750: ymax = 1e3
        plotMethod(       goodas[m][h], quartilesxsec[m][h],'{pdir}/{m}-limits/{h}_xsec_log'.format(pdir=pdir,h=h,m=m),         goodqs=goodqs[m][h], xaxis='m_{a} (GeV)',              yaxis=label,blind=b,logy=1,ymin=ymin,ymax=ymax,legendpos=lpos,numcol=1,plotunity=False,leftmargin=0.20,legendtitle=legendtitle,additionaltext=additionaltext,isprelim=isprelim)
        plotMethod(       goodas[m][h], quartilesxsec[m][h],'{pdir}/{m}-limits/{h}_xsec_log_smooth'.format(pdir=pdir,h=h,m=m),  goodqs=goodqs[m][h], xaxis='m_{a} (GeV)', smooth=True, yaxis=label,blind=b,logy=1,ymin=ymin,ymax=ymax,legendpos=lpos,numcol=1,plotunity=False,leftmargin=0.20,legendtitle=legendtitle,additionaltext=additionaltext,isprelim=isprelim)

        if h==125:
            ymin = 0
            ymax = 1e-1
            plotMethod(       goodas[m][h], quartilesxsecsm[m][h],'{pdir}/{m}-limits/{h}_xsec_sm'.format(pdir=pdir,h=h,m=m),             goodqs=goodqs[m][h], xaxis='m_{a} (GeV)',              yaxis=label,blind=b,logy=0,ymin=ymin,ymax=ymax,legendpos=lpos,numcol=1,plotunity=False,leftmargin=0.20,legendtitle=legendtitle,additionaltext=additionaltext,isprelim=isprelim)
            plotMethod(       goodas[m][h], quartilesxsecsm[m][h],'{pdir}/{m}-limits/{h}_xsec_sm_smooth'.format(pdir=pdir,h=h,m=m),      goodqs=goodqs[m][h], xaxis='m_{a} (GeV)', smooth=True, yaxis=label,blind=b,logy=0,ymin=ymin,ymax=ymax,legendpos=lpos,numcol=1,plotunity=False,leftmargin=0.20,legendtitle=legendtitle,additionaltext=additionaltext,isprelim=isprelim)

            ymin = 1e-4
            ymax = 1e-1
            plotMethod(       goodas[m][h], quartilesxsecsm[m][h],'{pdir}/{m}-limits/{h}_xsec_sm_log'.format(pdir=pdir,h=h,m=m),         goodqs=goodqs[m][h], xaxis='m_{a} (GeV)',              yaxis=label,blind=b,logy=1,ymin=ymin,ymax=ymax,legendpos=lpos,numcol=1,plotunity=False,leftmargin=0.20,legendtitle=legendtitle,additionaltext=additionaltext,isprelim=isprelim)
            plotMethod(       goodas[m][h], quartilesxsecsm[m][h],'{pdir}/{m}-limits/{h}_xsec_sm_log_smooth'.format(pdir=pdir,h=h,m=m),  goodqs=goodqs[m][h], xaxis='m_{a} (GeV)', smooth=True, yaxis=label,blind=b,logy=1,ymin=ymin,ymax=ymax,legendpos=lpos,numcol=1,plotunity=False,leftmargin=0.20,legendtitle=legendtitle,additionaltext=additionaltext,isprelim=isprelim)

        ymin = 0
        ymax = 2e-3
        if h==300: ymax = 2e-3
        if h==750: ymax = 2e-2
        plotMethod(       goodas[m][h], quartilesbr[m][h],  '{pdir}/{m}-limits/{h}_br'.format(pdir=pdir,h=h,m=m),               goodqs=goodqs[m][h], xaxis='m_{a} (GeV)',              yaxis=thisbr,blind=b,logy=0,ymin=ymin,ymax=ymax,legendpos=lpos,numcol=1,plotunity=False,leftmargin=0.20,legendtitle=legendtitle,additionaltext=additionaltext,isprelim=isprelim)
        plotMethod(       goodas[m][h], quartilesbr[m][h],  '{pdir}/{m}-limits/{h}_br_smooth'.format(pdir=pdir,h=h,m=m),        goodqs=goodqs[m][h], xaxis='m_{a} (GeV)', smooth=True, yaxis=thisbr,blind=b,logy=0,ymin=ymin,ymax=ymax,legendpos=lpos,numcol=1,plotunity=False,leftmargin=0.20,legendtitle=legendtitle,additionaltext=additionaltext,isprelim=isprelim)
        if h==125:
            plotMethod(   goodas[m][h], quartilesbr[m][h],  '{pdir}/{m}-limits/comp_{h}_br'.format(pdir=pdir,h=h,m=m),          goodqs=goodqs[m][h], xaxis='m_{a} (GeV)',              yaxis=thisbr,blind=b,logy=0,ymin=ymin,ymax=ymax,legendpos=lpos,numcol=1,plotunity=False,leftmargin=0.20,legendtitle=legendtitle,additionaltext=additionaltext,isprelim=isprelim,addResolved=True)
            plotMethod(   goodas[m][h], quartilesbr[m][h],  '{pdir}/{m}-limits/comp_{h}_br_smooth'.format(pdir=pdir,h=h,m=m),   goodqs=goodqs[m][h], xaxis='m_{a} (GeV)', smooth=True, yaxis=thisbr,blind=b,logy=0,ymin=ymin,ymax=ymax,legendpos=lpos,numcol=1,plotunity=False,leftmargin=0.20,legendtitle=legendtitle,additionaltext=additionaltext,isprelim=isprelim,addResolved=True)

        ymin = 5e-6
        ymax = 2e-3
        if h==300: ymax = 5e-3
        if h==750: ymax = 5e-2
        plotMethod(       goodas[m][h], quartilesbr[m][h],  '{pdir}/{m}-limits/{h}_br_log'.format(pdir=pdir,h=h,m=m),           goodqs=goodqs[m][h], xaxis='m_{a} (GeV)',              yaxis=thisbr,blind=b,logy=1,ymin=ymin,ymax=ymax,legendpos=lpos,numcol=1,plotunity=False,leftmargin=0.20,legendtitle=legendtitle,additionaltext=additionaltext,isprelim=isprelim)
        plotMethod(       goodas[m][h], quartilesbr[m][h],  '{pdir}/{m}-limits/{h}_br_log_smooth'.format(pdir=pdir,h=h,m=m),    goodqs=goodqs[m][h], xaxis='m_{a} (GeV)', smooth=True, yaxis=thisbr,blind=b,logy=1,ymin=ymin,ymax=ymax,legendpos=lpos,numcol=1,plotunity=False,leftmargin=0.20,legendtitle=legendtitle,additionaltext=additionaltext,isprelim=isprelim)


        if h != 125: continue

        # scale = 0.2
        # modelsScale = getModelsAlt(scale)
        # for model in modelsScale:
        #     tbs = [1,2,3]
        #     overlay = []
        #     overlayLabels = []
        #     for tb in tbs:
        #         overlay += [
        #             modelsScale[model][tb],
        #         ]
        #         overlayLabels += [
        #             '#splitline{{2HDM+S Type-{}}}{{tan #beta = {} B(H#rightarrow a_{{1}}a_{{1}}) = {}}}'.format(modelstrings[model],tb,scale)
        #         ]

        #     legendtitle = '#splitline{{2HDM+S Type-{model}, m_{{H}} = {h} GeV}}{{95% CL upper limits}}'.format(model=model,h=h)
        #     plotMethod(       goodas[m][h], quartilesbr[m][h],  '{pdir}/{m}-limits/{h}_br_log_overlay_type{model}'.format(pdir=pdir,h=h,m=m,model=model),       goodqs=goodqs[m][h], xaxis='m_{a} (GeV)', overlay=overlay,overlayLabels=overlayLabels, yaxis=thisbr,blind=b,logy=1,ymin=5e-6,ymax=2e-3,legendpos=31,numcol=1,plotunity=False,leftmargin=0.20,legendtitle=legendtitle,isprelim=isprelim)
        #     plotMethod(       goodas[m][h], quartilesbr[m][h],  '{pdir}/{m}-limits/{h}_br_overlay_type{model}'.format(pdir=pdir,h=h,m=m,model=model),           goodqs=goodqs[m][h], xaxis='m_{a} (GeV)', overlay=overlay,overlayLabels=overlayLabels, yaxis=thisbr,blind=b,logy=0,ymin=0,ymax=1e-3,legendpos=34,numcol=1,plotunity=False,leftmargin=0.20,legendtitle=legendtitle,isprelim=isprelim)
        #     plotMethod(       goodas[m][h], quartilesbr[m][h],  '{pdir}/{m}-limits/{h}_br_log_overlay_smooth_type{model}'.format(pdir=pdir,h=h,m=m,model=model),goodqs=goodqs[m][h], xaxis='m_{a} (GeV)', smooth=True, overlay=overlay,overlayLabels=overlayLabels, yaxis=thisbr,blind=b,logy=1,ymin=5e-6,ymax=2e-3,legendpos=31,numcol=1,plotunity=False,leftmargin=0.20,legendtitle=legendtitle,isprelim=isprelim)
        #     plotMethod(       goodas[m][h], quartilesbr[m][h],  '{pdir}/{m}-limits/{h}_br_overlay_smooth_type{model}'.format(pdir=pdir,h=h,m=m,model=model),    goodqs=goodqs[m][h], xaxis='m_{a} (GeV)', smooth=True, overlay=overlay,overlayLabels=overlayLabels, yaxis=thisbr,blind=b,logy=0,ymin=0,ymax=1e-3,legendpos=34,numcol=1,plotunity=False,leftmargin=0.20,legendtitle=legendtitle,isprelim=isprelim)

    # do 2D last to speed things up
    # for h in [125]:
    #     zaxis = '#frac{#sigma_{H}}{#sigma_{SM}}B(H #rightarrow aa)'

    #     expectedBands = [1.0,0.47]

        # for model in modeltypes:
        #     #legendtitle = '#splitline{{2HDM+S Type-{model}, m_{{H}} = {h} GeV}}{{95% CL upper limits}}'.format(model=modelstrings[model],h=h)
        #     legendtitle = '95% CL upper limits'
        #     additionaltext = ['2HDM+S Type-{model}'.format(model=modelstrings[model]),'m_{{H}} = {h} GeV'.format(h=h)]
        #     #try:
        #     plotMethod2D( goodas[m][h], goodtanbs,     quartiles[m][h], tanbmodels[m][h],  '{pdir}/{m}-limits2D/{h}-2HDM-Type{model}'.format(pdir=pdir,h=h,m=m,model=model),                         goodqs=goodqs[m][h], modelkey=model, expectedBands=expectedBands, xaxis='m_{a} (GeV)', yaxis='tan #beta', zaxis=zaxis,                                blind=b,logy=0,legendpos=34,numcol=1,plotunity=False,leftmargin=0.20,zmin=1e-3,legendtitle=legendtitle,additionaltext=additionaltext,isprelim=isprelim)
        #     plotMethod2D( goodas[m][h], goodtanbs,     quartiles[m][h], tanbmodels[m][h],  '{pdir}/{m}-limits2D/{h}-2HDM-Type{model}_smooth'.format(pdir=pdir,h=h,m=m,model=model),                  goodqs=goodqs[m][h], modelkey=model, expectedBands=expectedBands, xaxis='m_{a} (GeV)', yaxis='tan #beta', zaxis=zaxis,                   smooth=True, blind=b,logy=0,legendpos=34,numcol=1,plotunity=False,leftmargin=0.20,zmin=1e-3,legendtitle=legendtitle,additionaltext=additionaltext,isprelim=isprelim)
        #     plotMethod2D( goodas[m][h], goodtanbsfull, quartiles[m][h], tanbmodels[m][h],  '{pdir}/{m}-limits2D/{h}-2HDM-Type{model}_smooth_full'.format(pdir=pdir,h=h,m=m,model=model),             goodqs=goodqs[m][h], modelkey=model, expectedBands=expectedBands, xaxis='m_{a} (GeV)', yaxis='tan #beta', zaxis=zaxis,                   smooth=True, blind=b,logy=0,legendpos=34,numcol=1,plotunity=False,leftmargin=0.20,zmin=1e-3,legendtitle=legendtitle,additionaltext=additionaltext,isprelim=isprelim)
        #     plotMethod2D( goodas[m][h], goodtanbs,     quartiles[m][h], tanbmodels[m][h],  '{pdir}/{m}-limits2D/{h}-2HDM-Type{model}_simple'.format(pdir=pdir,h=h,m=m,model=model),                  goodqs=goodqs[m][h], modelkey=model, expectedBands=expectedBands, xaxis='m_{a} (GeV)', yaxis='tan #beta', plotcolz=False,                             blind=b,logy=0,legendpos=34,numcol=1,plotunity=False,leftmargin=0.20,zmin=1e-3,legendtitle=legendtitle,additionaltext=additionaltext,isprelim=isprelim)
        #     plotMethod2D( goodas[m][h], goodtanbs,     quartiles[m][h], tanbmodels[m][h],  '{pdir}/{m}-limits2D/{h}-2HDM-Type{model}_simple_smooth'.format(pdir=pdir,h=h,m=m,model=model),           goodqs=goodqs[m][h], modelkey=model, expectedBands=expectedBands, xaxis='m_{a} (GeV)', yaxis='tan #beta', plotcolz=False,                smooth=True, blind=b,logy=0,legendpos=34,numcol=1,plotunity=False,leftmargin=0.20,zmin=1e-3,legendtitle=legendtitle,additionaltext=additionaltext,isprelim=isprelim)
        #     plotMethod2D( goodas[m][h], goodtanbsfull, quartiles[m][h], tanbmodels[m][h],  '{pdir}/{m}-limits2D/{h}-2HDM-Type{model}_simple_smooth_full'.format(pdir=pdir,h=h,m=m,model=model),      goodqs=goodqs[m][h], modelkey=model, expectedBands=expectedBands, xaxis='m_{a} (GeV)', yaxis='tan #beta', plotcolz=False,                smooth=True, blind=b,logy=0,legendpos=34,numcol=1,plotunity=False,leftmargin=0.20,zmin=1e-3,legendtitle=legendtitle,additionaltext=additionaltext,isprelim=isprelim)
        #     plotMethod2D( goodas[m][h], goodtanbs,     quartiles[m][h], tanbmodels[m][h],  '{pdir}/{m}-limits2D/{h}-2HDM-Type{model}_simple_fill'.format(pdir=pdir,h=h,m=m,model=model),             goodqs=goodqs[m][h], modelkey=model, expectedBands=expectedBands, xaxis='m_{a} (GeV)', yaxis='tan #beta', plotcolz=False, plotfill=True,              blind=b,logy=0,legendpos=34,numcol=1,plotunity=False,leftmargin=0.20,zmin=1e-3,legendtitle=legendtitle,additionaltext=additionaltext,isprelim=isprelim)
        #     plotMethod2D( goodas[m][h], goodtanbs,     quartiles[m][h], tanbmodels[m][h],  '{pdir}/{m}-limits2D/{h}-2HDM-Type{model}_simple_fill_smooth'.format(pdir=pdir,h=h,m=m,model=model),      goodqs=goodqs[m][h], modelkey=model, expectedBands=expectedBands, xaxis='m_{a} (GeV)', yaxis='tan #beta', plotcolz=False, plotfill=True, smooth=True, blind=b,logy=0,legendpos=34,numcol=1,plotunity=False,leftmargin=0.20,zmin=1e-3,legendtitle=legendtitle,additionaltext=additionaltext,isprelim=isprelim)
        #     plotMethod2D( goodas[m][h], goodtanbsfull, quartiles[m][h], tanbmodels[m][h],  '{pdir}/{m}-limits2D/{h}-2HDM-Type{model}_simple_fill_smooth_full'.format(pdir=pdir,h=h,m=m,model=model), goodqs=goodqs[m][h], modelkey=model, expectedBands=expectedBands, xaxis='m_{a} (GeV)', yaxis='tan #beta', plotcolz=False, plotfill=True, smooth=True, blind=b,logy=0,legendpos=34,numcol=1,plotunity=False,leftmargin=0.20,zmin=1e-3,legendtitle=legendtitle,additionaltext=additionaltext,isprelim=isprelim)
        #     for tanb in [0.5,1.0,1.5,2.0]:
        #         #legendtitle = '#splitline{{2HDM+S Type-{model}, m_{{H}} = {h} GeV, tan#beta = {tanb}}}{{95% CL upper limits}}'.format(model=modelstrings[model],h=h,tanb=tanb)
        #         legendtitle = '95% CL upper limits'
        #         if model==1:
        #             additionaltext = ['2HDM+S Type-{model}'.format(model=modelstrings[model]),'m_{{H}} = {h} GeV'.format(h=h)]
        #         else:
        #             additionaltext = ['2HDM+S Type-{model}'.format(model=modelstrings[model]),'m_{{H}} = {h} GeV'.format(h=h),'tan#beta = {tanb}'.format(tanb=tanb)]
        #         plotMethod2DProjection( goodas[m][h], tanb, quartiles[m][h], tanbmodels[m][h],  '{pdir}/{m}-limits2D/{h}-2HDM-Type{model}_tanB{tanb}'.format(pdir=pdir,h=h,m=m,model=model,tanb=tanb),        goodqs=goodqs[m][h], modelkey=model, expectedBands=expectedBands, xaxis='m_{a} (GeV)', yaxis=zaxis,                                              blind=b,logy=1,legendpos=34,numcol=1,plotunity=False,leftmargin=0.20,ymax=100,ymin=1e-3,legendtitle=legendtitle,additionaltext=additionaltext,isprelim=isprelim)
        #         plotMethod2DProjection( goodas[m][h], tanb, quartiles[m][h], tanbmodels[m][h],  '{pdir}/{m}-limits2D/{h}-2HDM-Type{model}_tanB{tanb}_smooth'.format(pdir=pdir,h=h,m=m,model=model,tanb=tanb), goodqs=goodqs[m][h], modelkey=model, expectedBands=expectedBands, xaxis='m_{a} (GeV)', yaxis=zaxis,                                 smooth=True, blind=b,logy=1,legendpos=34,numcol=1,plotunity=False,leftmargin=0.20,ymax=100,ymin=1e-3,legendtitle=legendtitle,additionaltext=additionaltext,isprelim=isprelim)
        #     #except:
            #    logging.error('caught exception')




# TODO
# multi expected on same plot
#for h in hmasses:
#    if doGrid: continue
#    #if h == 750: continue
#    thisbr = labelbr if h==125 else labelbrbsm
#    allas = []
#    qs = []
#    qxs = []
#    qbrs = []
#    labels = ['m(#mu#mu)','m(#mu#mu) v m(#tau#tau)','m(#mu#mu) v m^{vis}(#mu#mu#tau#tau)','m(#mu#mu) v m^{kf}(#mu#mu#tau#tau)']
#    colors = [ROOT.kBlack, ROOT.kBlue, ROOT.kGreen+2, ROOT.kRed+2]
#    #for var in ['mm','mm_tt','mm_h','mm_hkf']:
#    for var in ['mm','mm_tt','mm_h']:
#        mode = 'mmmt_{}_parametric_unbinned_{}'.format(var,tag)
#        allas += [goodas[mode][h]]
#        qs   += [quartiles[mode][h]]
#        qxs  += [quartilesxsec[mode][h]]
#        qbrs += [quartilesbr[mode][h]]
#        #labels += [var]
#    legendtitle = '#splitline{{m_{{H}} = {h} GeV}}{{95% CL upper limits}}'.format(h=h)
#    b = True
#    plotter.plotMultiExpected(allas, qs,  labels, '{pdir}/limits_{tag}/{h}_log'.format(pdir=pdir,h=h,tag=tag),              xaxis='m_{a} (GeV)',              colors=colors, blind=b,logy=1,ymin=1e-3,ymax=2,legendpos=31,numcol=1,legendtitle=legendtitle)
#    plotter.plotMultiExpected(allas, qxs, labels, '{pdir}/limits_{tag}/{h}_xsec_log'.format(pdir=pdir,h=h,tag=tag),         xaxis='m_{a} (GeV)',              colors=colors, yaxis=label,blind=b,logy=1,ymin=1e-4,ymax=1e-1,legendpos=31,numcol=1,plotunity=False,leftmargin=0.20,legendtitle=legendtitle)
#    plotter.plotMultiExpected(allas, qbrs,labels, '{pdir}/limits_{tag}/{h}_br_log'.format(pdir=pdir,h=h,tag=tag),           xaxis='m_{a} (GeV)',              colors=colors, yaxis=thisbr,blind=b,logy=1,ymin=5e-6,ymax=2e-3,legendpos=31,numcol=1,plotunity=False,leftmargin=0.20,legendtitle=legendtitle)
#    plotter.plotMultiExpected(allas, qs,  labels, '{pdir}/limits_{tag}/{h}'.format(pdir=pdir,h=h,tag=tag),                  xaxis='m_{a} (GeV)',              colors=colors, blind=b,logy=0,ymin=0,ymax=10 if h==750 else 1,legendpos=34,numcol=1,legendtitle=legendtitle)
#    plotter.plotMultiExpected(allas, qxs, labels, '{pdir}/limits_{tag}/{h}_xsec'.format(pdir=pdir,h=h,tag=tag),             xaxis='m_{a} (GeV)',              colors=colors, yaxis=label,blind=b,logy=0,ymin=0,ymax=5e-2,legendpos=34,numcol=1,plotunity=False,leftmargin=0.20,legendtitle=legendtitle)
#    plotter.plotMultiExpected(allas, qbrs,labels, '{pdir}/limits_{tag}/{h}_br'.format(pdir=pdir,h=h,tag=tag),               xaxis='m_{a} (GeV)',              colors=colors, yaxis=thisbr,blind=b,logy=0,ymin=0,ymax=1e-2 if h==750 else 1e-3,legendpos=34,numcol=1,plotunity=False,leftmargin=0.20,legendtitle=legendtitle)
#    plotter.plotMultiExpected(allas, qs,  labels, '{pdir}/limits_{tag}/{h}_log_smooth'.format(pdir=pdir,h=h,tag=tag),       xaxis='m_{a} (GeV)', smooth=True, colors=colors, blind=b,logy=1,ymin=1e-3,ymax=2,legendpos=31,numcol=1,legendtitle=legendtitle)
#    plotter.plotMultiExpected(allas, qxs, labels, '{pdir}/limits_{tag}/{h}_xsec_log_smooth'.format(pdir=pdir,h=h,tag=tag),  xaxis='m_{a} (GeV)', smooth=True, colors=colors, yaxis=label,blind=b,logy=1,ymin=1e-4,ymax=1e-1,legendpos=31,numcol=1,plotunity=False,leftmargin=0.20,legendtitle=legendtitle)
#    plotter.plotMultiExpected(allas, qbrs,labels, '{pdir}/limits_{tag}/{h}_br_log_smooth'.format(pdir=pdir,h=h,tag=tag),    xaxis='m_{a} (GeV)', smooth=True, colors=colors, yaxis=thisbr,blind=b,logy=1,ymin=5e-6,ymax=2e-3,legendpos=31,numcol=1,plotunity=False,leftmargin=0.20,legendtitle=legendtitle)
#    plotter.plotMultiExpected(allas, qs,  labels, '{pdir}/limits_{tag}/{h}_smooth'.format(pdir=pdir,h=h,tag=tag),           xaxis='m_{a} (GeV)', smooth=True, colors=colors, blind=b,logy=0,ymin=0,ymax=10 if h==750 else 1,legendpos=34,numcol=1,legendtitle=legendtitle)
#    plotter.plotMultiExpected(allas, qxs, labels, '{pdir}/limits_{tag}/{h}_xsec_smooth'.format(pdir=pdir,h=h,tag=tag),      xaxis='m_{a} (GeV)', smooth=True, colors=colors, yaxis=label,blind=b,logy=0,ymin=0,ymax=5e-2,legendpos=34,numcol=1,plotunity=False,leftmargin=0.20,legendtitle=legendtitle)
#    plotter.plotMultiExpected(allas, qbrs,labels, '{pdir}/limits_{tag}/{h}_br_smooth'.format(pdir=pdir,h=h,tag=tag),        xaxis='m_{a} (GeV)', smooth=True, colors=colors, yaxis=thisbr,blind=b,logy=0,ymin=0,ymax=1e-2 if h==750 else 1e-3,legendpos=34,numcol=1,plotunity=False,leftmargin=0.20,legendtitle=legendtitle)
#
