from RunIISampleMaps import *
from RunIIDatasetUtils import *

import glob,os

SampleMap2017=getSampleMap2017()

#print SampleMap2017['HToAAH125A9']
#print len(SampleMap2017['HToAAH125A9'])

signame = 'HToAAH{h}A{a}'
hamap = {
    125 : [4,5,7,8,9,10,11,12,13,14,15,17,18,19,20,21],
    200 : [5,9,15],
    250 : [5,9,15],
    300 : [5,7,9,11,13,15,17,19,21],
    400 : [5,9,15],
    500 : [5,9,15],
    750 : [5,7,9,11,13,15,17,19,21],
    1000: [5,9,15],
}
hmasses = [125,200,250,300,400,500,750,1000]
amasses = [4,5,7,8,9,10,11,12,13,14,15,17,18,19,20,21]

#2017MCSignal_RooDataSets_CorrectWeight/
xRange = [2.5,25] # with jpsi                                                                                                                                                                                                                                                  
xRangeFull = [2.5,25]

yRange = [0,1000] # h, hkf                                                                                                                                                                                                                                                     
xVar='invMassMuMu'
yVar='visFourbodyMass'
selDatasets = {
    'invMassMuMu' : '{0}>{1} && {0}<{2}'.format(xVar,*xRange),
    'visFourbodyMass' : '{0}>{1} && {0}<{2}'.format(yVar,*yRange),
    }


#signals = [signame.format(h=h,a=a) for h in '125' and a in hamap[h]]
#h=

signal=[signame.format(h='125',a=a) for a in hamap[125]]

#f='/eos/uscms/store/user/rhabibul/HtoAA/HtoAA2017/LimitDataSets/2017MCSignal_RooDataSets_CorrectWeight/TauMuTauHad_HaaMC_am21_B.root'


#hist=getHist2D(f,selection=' && '.join([selDatasets['invMassMuMu'],selDatasets['visFourbodyMass']]))
#hist=getHistControl(f,selection=selDatasets['invMassMuMu'])
#print type(hist)
# print signal
# for s in signal:
#     print s
    #print SampleMap2017[s]
    
#list=[a for a in SampleMap2017[signal[0]] if '_' +'A' in a and 'TauMuTauHad' in a]
# list=[a for a in SampleMap2017['control']]
# print list

#def getRooDataset(f,selection='1',weight='w',xRange=[],yRange=[],project='',xVar='invMassMuMu',yVar='visFourbodyMass'):
#getRooDataset(f,selection='1',weight='w',xRange=xRange,yRange=yRange,project='',xVar='invMassMuMu',yVar='visFourbodyMass')

# hists=[getDataset(s,'data') for s in SampleMap2017['data'] if '_A' in s]
# region='A'
# for proc in signal:
#     hists=[getDataset(s,proc) for s in SampleMap2017[proc] if '_'+region in s]
  
# def getControlHist(proc,**kwargs):
#     wrappers = kwargs.pop('wrappers',{})
#     doUnbinned = kwargs.pop('doUnbinned',False)
#     #plot = 'invMassMuMu'                                                                                                             
#     #plotname = 'deltaR_iso/default/{}'.format(plot)                                                                                  
#     #if doUnbinned:                                                                                                                   
#     #    plotname += '_dataset'                                                                                                       
#     if doUnbinned:
#         hists = [getControlDataset(s) for s in SampleMap2017[proc]]
#         if len(hists) >1:
#             hist = sumDatasets(proc,*hists)
#         else:
#             hist = hists[0].Clone(proc)

#     #else:                                                                                                                            
#     # Takes far too long to do this unbinned                                                                                          
#     #hists = [wrappers[s].getHist(plotname) for s in sampleMap[proc]]                                                                 
#     #hist = sumHists(proc+'control',*hists)                                                                                           
#     #hist.Rebin(2)                                                                                                                    
#     return hist






# histMap={}
# backgrounds=['datadriven']
# for mode in ['control']:
#     histMap[mode] = {}
#     for shift in ['']:
#             #shiftLabel = systLabels.get(shift,shift)                                                                                 
#         histMap[mode][shift] = {}
#         for proc in backgrounds:
#             logging.info('Getting {} {}'.format(proc,shift))
#             if proc=='datadriven':
#                 hist = getControlHist('datadriven-control',doUnbinned=True)

# file=ROOT.TFile.Open(f)
# ds=file.Get('dataColl')
# ds.Print("v")
# args=ds.get()

filedir='/eos/uscms/store/user/rhabibul/HtoAA/HtoAA2017/LimitDataSets/2017MCSignal_RooDataSets_CorrectScale/'
os.chdir(filedir)


for file in glob.glob('TauMuTauHad*.root'):
    print file
    f=ROOT.TFile.Open(file)
    ds=f.Get('dataColl')
    ds.Print("v")
    args=ds.get()
    

