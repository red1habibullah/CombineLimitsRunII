import os
import logging
import ROOT

ROOT.gROOT.SetBatch()

from DevTools.Utilities.utilities import python_mkdir, runCommand

logging.basicConfig(format='%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')

hdfs = '/hdfs/store/user/dntaylor'
user = os.environ['USER']
doCrab = False
version = 1
testing = False
reduced = False

jobname = '2019-10-24_MuMuTauTauLimits_HybridNew_v{v}'.format(v=version)
if doCrab:
    jobname = 'crab_' + jobname
if testing:
    jobname = 'test_' + jobname


hmasses = [750,300,125]
amasses = [x*.1 for x in range(36,210,1)] + [21.0]
lowmass_amasses = amasses
upsilon_amasses = amasses
highmass_amasses = amasses
if reduced:
    amasses = [3.6] + [x*.1 for x in range(40,210,5)] + [21.0]
    lowmass_amasses = [x*.1 for x in range(36,46,1)] + [x*.1 for x in range(50,90,5)]
    upsilon_amasses = [6,6.5,7,7.5] + [x*.1 for x in range(80,121,1)] + [12.5,13,13.5,14]
    highmass_amasses = [x*.1 for x in range(110,255,5)]
if testing:
    amasses = [7.0,10.0,15.0]


#mode = 'mmmt_mm_h_parametric_unbinned_with1DFits'
mode = 'mmmt_mm_h_parametric_unbinned_{moderange}With1DFits'
toys = 5000 # reasonable amount for all points is 100 per job, longest right now is upsilon 125, 12 hours
toys = 1000 # cut it by 5 for initial population

moderanges = ['lowmass','upsilon','highmass']
rangeMap = {
    'lowmass': [2.5,8.5],
    'upsilon': [6,14],
    'highmass': [11,25],
}

# use this for now, also support using results from asymptotic...
rMap = {
    125: [0.025,1.00],
    300: [0.050,2.00],
    750: [0.500,25.0],
}

drMap = {
    125: 0.025,
    300: 0.05,
    750: 0.5,
}

if doCrab:
    scratchdir = '/nfs_scratch/dntaylor/crab_projects'
else:
    scratchdir = '/nfs_scratch/dntaylor/condor_projects'

def submit_condor(ws,quartiles,mode,h,a):
    sample_dir = '{}/{}/{}/{}/{}'.format(scratchdir,jobname,mode,h,a)
    full_path = os.path.abspath(os.path.join(os.environ['CMSSW_BASE'],'src',ws))
    dsplit = full_path.split('/')
    srcpos = dsplit.index('src')
    drel = '/'.join(dsplit[srcpos:])
    dreldir = '/'.join(dsplit[srcpos:-1])

    # create submit dir
    submit_dir = '{}/submit'.format(sample_dir)
    if os.path.exists(submit_dir):
        logging.warning('Submission directory exists for {0}.'.format(jobname))
        return

    # setup the job parameters
    if quartiles:
        rmin = 0.5*min(quartiles)
        rmax = 1.2*max(quartiles)
    else:
        rmin = rMap[h][0]
        rmax = rMap[h][1]
    num_points = int((rmax-rmin)/drMap[h])
    points_per_job = 1
    toys_per_job = 100
    jobs_per_point = int(toys/toys_per_job)
    if jobs_per_point<1: jobs_per_point = 1

    # create dag dir
    dag_dir = '{}/dags/dag'.format(sample_dir)
    os.system('mkdir -p {0}'.format(os.path.dirname(dag_dir)))
    os.system('mkdir -p {0}'.format(dag_dir+'inputs'))

    # output dir
    output_dir = '/store/user/{}/{}/{}/{}/{}'.format(user, jobname, mode, h, a)

    # create file list
    rlist = [r*(rmax-rmin)/num_points + rmin for r in range(int(num_points/points_per_job))]
    input_name = '{}/rvalues.txt'.format(dag_dir+'inputs')
    with open(input_name,'w') as file:
        for r in rlist:
            for i in range(jobs_per_point):
                file.write('{}_{}\n'.format(r,i))

    # create bash script
    bash_name = '{}/{}.sh'.format(dag_dir+'inputs', jobname)
    bashScript = '#!/bin/bash\n'
    #bashScript += 'printenv\n'
    bashScript += 'read -d "_" -r RVAL < $INPUT\n'
    for i in range(points_per_job):
        dr = i*(rmax-rmin)/points_per_job
        bashScript += 'combine -M HybridNew -v -1 -d $CMSSW_BASE/{ws} -m {h} --setParameters MA={a} --freezeParameters=MA --LHCmode LHC-limits --singlePoint $(bc -l <<< "$RVAL+{points}") --saveToys --saveHybridResult -T {toys} -s -1 --clsAcc 0\n'.format(ws=drel,h=h,a=a,points=dr,toys=toys_per_job,jobname=jobname)
    if points_per_job>1:
        bashScript += 'hadd $OUTPUT higgsCombine*HybridNew.mH{}*.root\n'.format(h)
        bashScript += 'rm higgsCombine*.root\n'.format(h)
    else:
        bashScript += 'mv higgsCombine*.root $OUTPUT\n'.format(h)
    with open(bash_name,'w') as file:
        file.write(bashScript)
    os.system('chmod +x {}'.format(bash_name))

    # create farmout command
    farmoutString = 'farmoutAnalysisJobs --infer-cmssw-path --fwklite --input-file-list={} --assume-input-files-exist'.format(input_name)
    farmoutString += ' --submit-dir={} --output-dag-file={} --output-dir={}'.format(submit_dir, dag_dir, output_dir)
    farmoutString += ' --extra-usercode-files="{}" {} {}'.format(dreldir, jobname, bash_name)

    print farmoutString

def submit_crab(ws,quartiles,mode,h,a):
    if quartiles:
        low = min(quartiles[:5])*0.5
        high = max(quartiles[:5])*1.2
        exp = quartiles[2]
        obs = quartiles[5]
    else:
        low = rMap[h][0]
        high = rMap[h][1]
        exp = (high-low)/2
    pointsString = '{:.2}:{:.2}:{:.2},{:.2}:{:.2}:{:.2}'.format(low,exp,(exp-low)/50,exp,high,(high-exp)/30)

    crab = 'custom_crab_{h}_{a}.py'.format(h=h,a=a)

    crabString = '''
def custom_crab(config):
    config.General.workArea = '/nfs_scratch/{user}/crab_projects/{jobname}/{tag}/{h}/{a}'
    config.Data.outLFNDirBase = '/store/user/{user}/{jobname}/{tag}/{h}/{a}'
    config.Site.storageSite = 'T2_US_Wisconsin'
'''.format(user=user, jobname=jobname, tag=mode, h=h, a=a)

    with open('{temp}/custom_crab_{h}_{a}.py'.format(temp=temp,h=h,a=a),'w') as f:
        f.write(crabString)

    command = 'combineTool.py -M HybridNew -v -1 -d {ws} -m {h} --setParameters MA={a} --freezeParameters=MA --LHCmode LHC-limits --singlePoint {points} --saveToys --saveHybridResult -T {toys} -s -1 --clsAcc 0 --job-mode crab3 --task-name {jobname} --custom-crab custom_crab_{h}_{a}.py'.format(ws=ws,h=h,a=a,points=pointsString,toys=toys,jobname=jobname)
    print command



for moderange in moderanges:
    for h in hmasses:
        thismode = mode.format(moderange=moderange)
        datacard = 'datacards_shape/MuMuTauTau/{mode}_HToAAH{h}AX.txt'.format(mode=thismode,h=h)
        ws = '{mode}_{h}.root'.format(mode=thismode,h=h)
        temp = 'temp_HybridNew_{h}'.format(h=h)
        python_mkdir(temp)
        print 'text2workspace.py {datacard} -m {h} -o {temp}/{ws}'.format(datacard=datacard,h=h,temp=temp,ws=ws)
        if doCrab: print 'pushd {temp}'.format(temp=temp)
        prev_qs = []
        thisamasses = amasses
        if moderange=='lowmass':
            thisamasses = lowmass_amasses
        if moderange=='upsilon':
            thisamasses = upsilon_amasses
        if moderange=='highmass':
            thisamasses = highmass_amasses
        for a in thisamasses:
            if a<rangeMap[moderange][0]: continue
            if a>rangeMap[moderange][1]: continue
            if a % 1 < 1e-10: astr = '{0:.0f}'.format(a)
            elif (10*a) % 1 < 1e-10: astr = '{0:.1f}'.format(a)
            elif (100*a) % 1 < 1e-10: astr = '{0:.2f}'.format(a)
            else: astr = 'HELP'

            qs = []
            # turn off for now
            #tfile = ROOT.TFile.Open('{hdfs}/{m}/{h}/higgsCombineHToAAH{h}A{a:.1f}_{m}.AsymptoticLimits.mH{h}.root'.format(hdfs=hdfs,h=h,a=a,m=thismode,astr=astr))
            #try:
            #    tree = tfile.Get("limit")
            #except:
            #    logging.error('Failed to open {} {} {}'.format(thismode,h,a))
            #    continue
            #for i, row in enumerate(tree):
            #    qs += [row.limit]
            #outline = ' '.join([str(x) for x in qs])
            #logging.info('{0}:{1}: Limits: {2}'.format(h,a,outline))

            #if not prev_qs: prev_qs = qs

            #if abs(qs[2]-prev_qs[2])/qs[2]>0.3:
            #    logging.info('{}:{}: Large jump in AsymptoticLimit, will use previous a mass limits for bounds'.format(h,a))
            #    qs = prev_qs

            #prev_qs = qs

            #if len(qs)<6:
            #    logging.info('{}:{}: Too few limits, will not sumbit'.format(h,a))
            #    continue

            if doCrab:
                submit_crab(ws,qs,thismode,h,a)
            else:
                submit_condor('{temp}/{ws}'.format(temp=temp,ws=ws),qs,thismode,h,a)

        if doCrab: print 'popd'

