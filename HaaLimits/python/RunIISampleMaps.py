import os
import sys
import logging


logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
#######################################################################
################################ Sample Map 2017 ######################
SampleMap2017={}
channels=['TauETauHad','TauMuTauHad']
amasses=[4,5,7,8,9,10,11,12,13,14,15,17,18,19,20,21]
regions=['A','B','C','D']
signame = 'HToAAH{h}A{a}'

#########Data and DataDriven##########################################
SampleMap2017['data']=[]
for c in channels:
    for r in regions:
        SampleMap2017['data'].append('/eos/uscms/store/user/rhabibul/HtoAA/HtoAA2017/LimitDataSets/2017Data_RooDatasets/{c}_{r}.root'.format(c=c,r=r))

SampleMap2017['datadriven']=[]
for c in channels:
    for r in regions:
        SampleMap2017['datadriven'].append('/eos/uscms/store/user/rhabibul/HtoAA/HtoAA2017/LimitDataSets/2017DataDriven_RooDatasets/{c}_{r}.root'.format(c=c,r=r))

###################### Control and DataDriven Control################
SampleMap2017['control']=['/eos/uscms/store/user/rhabibul/HtoAA/HtoAA2017/LimitDataSets/2017Data_RooDatasets/rooDatasets_controlRegion.root']

SampleMap2017['datadriven-control']=['/eos/uscms/store/user/rhabibul/HtoAA/HtoAA2017/LimitDataSets/2017Data_RooDatasets/rooDatasets_controlRegion.root']


####################### MC Samples #################################
for a in amasses:
    SampleMap2017[signame.format(h='125',a=a)]=[]
    for c in channels:
        for r in regions:
            SampleMap2017[signame.format(h='125',a=a)].append('/eos/uscms/store/user/rhabibul/HtoAA/HtoAA2017/LimitDataSets/2017MCSignal_RooDataSets_CorrectWeight/{c}_HaaMC_am{a}_{r}.root'.format(c=c,a=a,r=r))

################### Calling Function ################################
def getSampleMap2017():
    return SampleMap2017
#####################Sample Map 2017 ################################
#####################################################################
