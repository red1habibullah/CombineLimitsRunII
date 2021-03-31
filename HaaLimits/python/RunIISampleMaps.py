import os
import sys
import logging
import ROOT


logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


#xsec splines
prefix='root://cmseos.fnal.gov/'
smtfilename=prefix+'/uscms/home/jingyu/nobackup/Haa/HaaLimits/CMSSW_10_2_13/src/CombineLimits/Limits/data/Higgs_YR4_SM_13TeV.root'
bsmtfilename=prefix+'/uscms/home/jingyu/nobackup/Haa/HaaLimits/CMSSW_10_2_13/src/CombineLimits/Limits/data/Higgs_YR4_SM_13TeV.root'
#smtfile  = ROOT.TFile.Open('/uscms/home/jingyu/nobackup/Haa/HaaLimits/CMSSW_10_2_13/src/CombineLimits/Limits/data/Higgs_YR4_SM_13TeV.root')
#bsmtfile = ROOT.TFile.Open('/uscms/home/jingyu/nobackup/Haa/HaaLimits/CMSSW_10_2_13/src/CombineLimits/Limits/data/Higgs_YR4_BSM_13TeV.root')

#smws = smtfile.Get('YR4_SM_13TeV')
#bsmws = bsmtfile.Get('YR4_BSM_13TeV')

#######################################################################
################################ Sample Map 2017 ######################
SampleMap2017MVA={}
channels=['TauETauHad','TauMuTauHad','TauETauMu']
amasses=[4,5,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21]
regions=['A','B','C','D']
signame = 'HToAAH{h}A{a}'

#########Data and DataDriven##########################################
SampleMap2017MVA['data']=[]
for c in channels:
    for r in regions:
        SampleMap2017MVA['data'].append(prefix+'/eos/uscms/store/user/rhabibul/HtoAA/HtoAA2017/LimitDataSets/2017Data_RooDatasets/{c}_{r}.root'.format(c=c,r=r))

SampleMap2017MVA['datadriven']=[]
for c in channels:
    for r in regions:
        SampleMap2017MVA['datadriven'].append(prefix+'/eos/uscms/store/user/rhabibul/HtoAA/HtoAA2017/LimitDataSets/2017DataDriven_RooDatasets/{c}_{r}.root'.format(c=c,r=r))

###################### Control and DataDriven Control################
SampleMap2017MVA['control']=['/eos/uscms/store/user/rhabibul/HtoAA/HtoAA2017/LimitDataSets/2017Data_RooDatasets/rooDatasets_controlRegion.root']

SampleMap2017MVA['datadriven-control']=['/eos/uscms/store/user/rhabibul/HtoAA/HtoAA2017/LimitDataSets/2017Data_RooDatasets/rooDatasets_controlRegion.root']


####################### MC Samples #################################
for a in amasses:
    SampleMap2017MVA[signame.format(h='125',a=a)]=[]
    for c in channels:
        for r in regions:
            SampleMap2017MVA[signame.format(h='125',a=a)].append(prefix+'/eos/uscms/store/user/rhabibul/HtoAA/HtoAA2017/LimitDataSets/2017MCSignal_RooDataSets_CorrectScale/{c}_HaaMC_am{a}_{r}.root'.format(c=c,a=a,r=r))

################### Calling Function ################################
def getSampleMap2017MVA():
    #print "Got SampleMap2017MVA:", SampleMap2017MVA
    return SampleMap2017MVA
#####################Sample Map 2017 ################################
#####################################################################




#####################################################################
#################### Sample Map Deep 2017 ###########################
SampleMap2017={}

baseDir='/eos/uscms/store/user/rhabibul/HtoAA/HtoAA2017Deep/'
channelsDeep=['TauMuTauHad','TauETauHad','TauHadTauHad']
amassesDeep=[4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21]
regionsnew=['sideBand','signalRegion']

muIdList = ["loose", "medium", "tight"]
muIdLabel = ["looseMuIso", "mediumMuIso", "tightMuIso"]
eleIdList = ["loose", "medium", "tight"]
eleIdLabel = ["looseEleId", "mediumEleId", "tightEleId"]
discriminators=['vvlooseDeepVSjet','vlooseDeepVSjet','looseDeepVSjet','mediumDeepVSjet','tightDeepVSjet','vtightDeepVSjet','vvtightDeepVSjet']
discriminatorsML=['0.3','0.4','0.5','0.6','0.7','0.8','0.9']

discriminator = discriminators[3]
#discriminator = discriminatorsML[0]

#d = discriminator

#sigSysType=['pu','fake','btag','tau','MuonEn','TauEn']#,'JetEn','UnclusteredEn']
#sigSysType=['fake']
sigSysType=['pu','fake','btag','tau','MuonEn','TauEn']
sigShifts=[u+s for u in sigSysType for s in ['Up','Down']]

bgSysType=['fake']
bgShifts=[u+s for u in bgSysType for s in ['Up','Down']]

# Control
SampleMap2017['control']=[prefix+'/eos/uscms/store/user/rhabibul/HtoAA/HtoAA2017/LimitDataSets/2017Data_RooDatasets/rooDatasets_controlRegion.root']

# Data Driven
## SampleMap2017['datadriven']=[]
## for c in channelsDeep:
##     for r in regionsnew:
##         SampleMap2017['datadriven'].append(prefix+baseDir+'{c}/RooDataSets/DataDrivenSystematics/{c}_{r}_{d}.root'.format(c=c,r=r,d=d))
##         for s in bgShifts:
##             SampleMap2017['datadriven'].append(prefix+baseDir+'{c}/RooDataSets/DataDrivenSystematics/{c}_{r}_{d}_{s}.root'.format(c=c,r=r,d=d,s=s))
##

# Signal MC
## for a in amassesDeep:
##     SampleMap2017[signame.format(h='125',a=a)]=[]
##     for c in channelsDeep:
##         for r in regionsnew:
##             SampleMap2017[signame.format(h='125',a=a)].append(prefix+baseDir+'{c}/RooDataSets/SignalMC/{c}_HaaMC_am{a}_{d}_{r}.root'.format(c=c,a=a,d=d,r=r))
##             for s in sigShifts:
##                 SampleMap2017[signame.format(h='125',a=a)].append(prefix+baseDir+'{c}/RooDataSets/SignalMC/{c}_HaaMC_am{a}_{d}_{r}_{s}.root'.format(c=c,a=a,d=d,r=r,s=s))
##                 
## def getSampleMap2017():
##     #print "Got SampleMap2017:",SampleMap2017
##     return SampleMap2017




########################## Sample Map Deep 2017 #####################
#####################################################################
#/eos/uscms/store/user/rhabibul/HtoAA/HtoAA2017Deep/TauMuTauE/RooDatasets/Data/TauMuTauE_sideBand_MuIso_loose_EleId_loose.root 
#/eos/uscms/store/user/rhabibul/HtoAA/HtoAA2017Deep/TauMuTauE/RooDatasets/DataDriven/TauMuTauE_signalRegion_MuIso_loose_EleId_loose.root
#/eos/uscms/store/user/rhabibul/HtoAA/HtoAA2017Deep/TauMuTauE/RooDatasets/SignalMC/TauMuTauE_HaaMC_am9_tightMuIso_tightEleId_signalRegion.root
channelsNew=['TauMuTauE']

SampleMapNew2017={}
SampleMapNew2017['data']=[]
SampleMapNew2017['datadriven']=[]

###################### Control and DataDriven Control############### 
SampleMapNew2017['control']=['/eos/uscms/store/user/rhabibul/HtoAA/HtoAA2017/LimitDataSets/2017Data_RooDatasets/rooDatasets_controlRegion.root']

SampleMapNew2017['datadriven-control']=['/eos/uscms/store/user/rhabibul/HtoAA/HtoAA2017/LimitDataSets/2017Data_RooDatasets/rooDatasets_controlRegion.root']

######################## MC Samples ################################ 
for a in amassesDeep:
    SampleMapNew2017[signame.format(h='125',a=a)]=[]
    for c in channelsNew:
        for m in muIdLabel:
            for e in eleIdLabel:
                for r in regionsnew:
                    SampleMapNew2017[signame.format(h='125',a=a)].append('/eos/uscms/store/user/rhabibul/HtoAA/HtoAA2017Deep/{c}/RooDatasets/SignalMC/{c}_HaaMC_am{a}_{m}_{e}_{r}.root'.format(c=c,a=a,m=m,e=e,r=r))

#########Data and DataDriven#########################################
for c in channelsNew:
    for m in muIdList:
        for e in eleIdList:
            if r in ['signalRegion']:
                SampleMapNew2017['datadriven'].append('/eos/uscms/store/user/rhabibul/HtoAA/HtoAA2017Deep/{c}/RooDatasets/DataDriven/{c}_{r}_MuIso_{m}_EleId_{e}.root'.format(c=c,r=r,m=m,e=e))  

for c in channelsNew:
    for m in muIdList:
        for e in eleIdList:
            #if reg in ['signalRegion']:
            SampleMapNew2017['data'].append('/eos/uscms/store/user/rhabibul/HtoAA/HtoAA2017Deep/{c}/RooDatasets/Data/{c}_{reg}_MuIso_{m}_EleId_{e}.root'.format(c=c,reg='sideBand',m=m,e=e))


####################### Calling Function ###############
def getSampleMapNew2017():
    #print "Got SampleMapNew2017:", SampleMapNew2017
    return SampleMapNew2017
#/eos/uscms/store/user/rhabibul/HtoAA/HtoAA2017Deep/TauMuTauE/RooDatasets/Data/TauMuTauE_sideBand_MuIso_loose_EleId_loose.root 
#TauMuTauE_sideBand_MuIso_medium_EleId_loose.root
