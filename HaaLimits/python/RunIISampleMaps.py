import os
import sys
import logging
import ROOT


logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


#xsec splines
prefix='root://cmseos.fnal.gov/'
smtfilename=prefix+'/uscms/home/jingyu/nobackup/Haa/HaaLimits/CMSSW_10_2_13/src/CombineLimits/Limits/data/Higgs_YR4_SM_13TeV.root'
bsmtfilename=prefix+'/uscms/home/jingyu/nobackup/Haa/HaaLimits/CMSSW_10_2_13/src/CombineLimits/Limits/data/Higgs_YR4_SM_13TeV.root'


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

baseDir='/eos/uscms/store/user/zhangj/HaaLimits/RooDataSets/'
channelsDeep=['TauMuTauHad','TauETauHad','TauHadTauHad']
amassesDeep=[4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21]
regionsnew=['sideBand','signalRegion']

discriminators=['vvlooseDeepVSjet','vlooseDeepVSjet','looseDeepVSjet','mediumDeepVSjet','tightDeepVSjet','vtightDeepVSjet','vvtightDeepVSjet']

discriminatorsDeepDitauh=['0.3','0.4','0.5','0.6','0.7','0.8','0.9']

discriminatorsBoostedDitauh = ["vloose", "loose", "medium", "tight", "vtight", "vvtight"]

#discriminator = discriminators[3]
#discriminator = discriminatorsML[0]

#method = "boostedDitau"
method = "deepTauID"
discriminator = discriminatorsBoostedDitauh[2]

#d = discriminator

#sigSysType=['pu','fake','btag','tau','MuonEn','TauEn']#,'JetEn','UnclusteredEn']
#sigSysType=['fake']
sigSysType=['pu','fake','btag','tau','MuonEn','TauEn']
sigShifts=[u+s for u in sigSysType for s in ['Up','Down']]

bgSysType=['fake']
bgShifts=[u+s for u in bgSysType for s in ['Up','Down']]

# Control
SampleMap2017['control']=[prefix+'/eos/uscms/store/user/rhabibul/HtoAA/HtoAA2017/LimitDataSets/2017Data_RooDatasets/rooDatasets_controlRegion.root']



baseDirRooDatahists = "/eos/uscms/store/user/zhangj/HaaLimits/RooDataHists/"
channelsNew=['TauMuTauE']

SampleMapNew2017={}
SampleMapNew2017['data']=[]
SampleMapNew2017['datadriven']=[]

###################### Control and DataDriven Control############### 
SampleMapNew2017['control']=['/eos/uscms/store/user/rhabibul/HtoAA/HtoAA2017/LimitDataSets/2017Data_RooDatasets/rooDatasets_controlRegion.root']

SampleMapNew2017['datadriven-control']=['/eos/uscms/store/user/rhabibul/HtoAA/HtoAA2017/LimitDataSets/2017Data_RooDatasets/rooDatasets_controlRegion.root']

muIdList = ["loose", "medium", "tight"]
muIdLabel = ["looseMuIso", "mediumMuIso", "tightMuIso"]
eleIdList = ["loose", "medium", "tight"]
eleIdLabel = ["looseEleId", "mediumEleId", "tightEleId"]

muId = muIdList[0]
eleId = eleIdList[0]


######################## MC Samples ################################ 
#for a in amassesDeep:
#    SampleMapNew2017[signame.format(h='125',a=a)]=[]
#    for c in channelsNew:
#        for m in muIdLabel:
#            for e in eleIdLabel:
#                for r in regionsnew:
#                    SampleMapNew2017[signame.format(h='125',a=a)].append('/eos/uscms/store/user/zhangj/HaaLimits/RooDataHists/SignalMC/{c}_HaaMC_am{a}_{m}_{e}_{r}.root'.format(c=c,a=a,m=m,e=e,r=r))
                    
#########Data and DataDriven#########################################
#for c in channelsNew:
#    for m in muIdList:
#        for e in eleIdList:
#            if r in ['signalRegion']:
#                SampleMapNew2017['datadriven'].append(prefix+'/eos/uscms/store/user/zhangj/HaaLimits/RooDataHists/DataDriven/{c}_{r}_MuIso_{m}_EleId_{e}.root'.format(c=c,r=r,m=m,e=e))  

#for c in channelsNew:
#    for m in muIdList:
#        for e in eleIdList:
#            #if reg in ['signalRegion']:
#            SampleMapNew2017['data'].append(prefix+'/eos/uscms/store/user/zhangj/HaaLimits/RooDataHists/Data/{c}_{reg}_MuIso_{m}_EleId_{e}.root'.format(c=c,reg='sideBand',m=m,e=e))


####################### Calling Function ###############
#def getSampleMapNew2017():
    #print "Got SampleMapNew2017:", SampleMapNew2017
#    return SampleMapNew2017
#/eos/uscms/store/user/rhabibul/HtoAA/HtoAA2017Deep/TauMuTauE/RooDatasets/Data/TauMuTauE_sideBand_MuIso_loose_EleId_loose.root 
#TauMuTauE_sideBand_MuIso_medium_EleId_loose.root
