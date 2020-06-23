#!/usr/bin/env python
'''
A script to retrieve the limits

Author: Devin N. Taylor, UW-Madison
'''

import os
import sys
import glob
import pwd
import argparse
import errno
import socket
import signal
import logging
import math
import ROOT
import subprocess
from multiprocessing import Pool
from socket import gethostname

#scratchDir = 'data' if 'uwlogin' in gethostname() else 'nfs_scratch'
scratchDir='/uscms_data/d3/rhabibul/CombineRun2_v2/CMSSW_8_1_0/src/CombineLimits/HaaLimits/python'
UNAME = os.environ['USER']

def python_mkdir(dir):
    '''A function to make a unix directory as well as subdirectories'''
    try:
        os.makedirs(dir)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(dir):
            pass
        else: raise

def limitsWrapper(args):
    getLimits(*args)

def runCommand(command):
    return subprocess.Popen(command,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT).communicate()[0]

def getCommands(**kwargs):
    '''
    Submit a job using farmoutAnalysisJobs --fwklite
    '''
    combineCommands = [
        'combine -M AsymptoticLimits -m {a} {datacard} -n "HToAAH{h}A{a}_{tag}"',
        #'combine -M Significance -m {a} {datacard} -n "HToAAH{h}A{a}_{tag}Observed"',
        #'combine -M Significance -m {a} {datacard} -n "HToAAH{h}A{a}_{tag}APriori" -t -1 --expectSignal=1',
        #'combine -M Significance -m {a} {datacard} -n "HToAAH{h}A{a}_{tag}APosteriori" -t -1 --expectSignal=1 --toysFreq',
    ]

    return combineCommands


def runLimit(tag,h,a,**kwargs):
    dryrun = kwargs.get('dryrun',False)
    parametric = kwargs.get('parametric',False)

    datacard = 'datacards_shape/MuMuTauTau/mmmt_{}_HToAAH{}A{}.txt'.format(tag,h,'X' if parametric else a)

    combineCommands = getCommands(**kwargs)
    for cc in combineCommands:
        command = cc.format(datacard=datacard,h=h,a=a,tag=tag)
        if dryrun:
            logging.info(command)
        else:
            out = runCommand(command)
            print out

def submitLimit(tag,h,amasses,**kwargs):
    dryrun = kwargs.get('dryrun',False)
    jobName = kwargs.get('jobName',None)
    pointsPerJob = kwargs.get('pointsPerJob',10)
    parametric = kwargs.get('parametric',False)

    a = '${A}'

    datacard = 'datacards_shape/MuMuTauTau/mmmt_{}_HToAAH{}A{}.txt'.format(tag,h,'X' if parametric else '${A}')

    combineCommands = getCommands(**kwargs)

    sample_dir = '/{}/{}/condor_projects/{}/{}/{}'.format(scratchDir, UNAME, jobName, tag, h)
    python_mkdir(sample_dir)

    # create submit dir
    submit_dir = '{}/submit'.format(sample_dir)
    if os.path.exists(submit_dir):
        logging.warning('Submission directory exists for {0}.'.format(jobName))
        return

    # make dag
    dag_dir = '{}/dags/'.format(sample_dir)
    python_mkdir(dag_dir)

    # create file list
    input_name = '{}/amasses.txt'.format(dag_dir)
    with open(input_name,'w') as f:
        for ai in amasses:
            f.write('{}\n'.format(ai))

    # output dir
    output_dir = '/store/user/{}/{}/{}/{}'.format(pwd.getpwuid(os.getuid())[0], jobName, tag, h)

    # create bash script
    bash_name = '{}/script.sh'.format(sample_dir)
    bashScript = '#!/bin/bash\n'
    bashScript += 'ls\n'
    bashScript += 'printenv\n'
    bashScript += 'cp -r $CMSSW_VERSION/src/datacards_shape .\n'
    bashScript += 'while read A; do\n'
    for cc in combineCommands:
        bashScript += cc.format(datacard=datacard,h=h,a=a,tag=tag)+'\n'
    bashScript += 'done < $INPUT\n'
    with open(bash_name,'w') as file:
        file.write(bashScript)
    os.system('chmod +x {0}'.format(bash_name))

    # create farmout command
    farmoutString = 'farmoutAnalysisJobs --infer-cmssw-path --fwklite --job-generates-output-name'
    farmoutString += ' --input-file-list={} --input-files-per-job={} --assume-input-files-exist'.format(input_name,pointsPerJob)
    farmoutString += ' --submit-dir={} --output-dag-file={}/dag --output-dir={}'.format(submit_dir, dag_dir, output_dir)
    farmoutString += ' --extra-usercode-files="src/datacards_shape/MuMuTauTau" {} {}'.format(jobName, bash_name)

    if not dryrun:
        logging.info('Submitting {}/{}/{}'.format(jobName,tag,h))
        os.system(farmoutString)
    else:
        print farmoutString


def submitLimitCrab(tag,h,amasses,**kwargs):
    dryrun = kwargs.get('dryrun',False)
    jobName = kwargs.get('jobName',None)
    pointsPerJob = kwargs.get('pointsPerJob',10)
    parametric = kwargs.get('parametric',False)

    a = '${A}'

    datacard = 'datacards_shape/MuMuTauTau/mmmt_{}_HToAAH{}A{}.txt'.format(tag,h,'X' if parametric else '${A}')

    combineCommands = getCommands(**kwargs)

    sample_dir = '/{}/{}/crab_projects/{}/{}/{}'.format(scratchDir,pwd.getpwuid(os.getuid())[0], jobName, tag, h)
    python_mkdir(sample_dir)

    # create submit dir
    submit_dir = '{}/crab'.format(sample_dir)
    if os.path.exists(submit_dir):
        logging.warning('Submission directory exists for {0}.'.format(jobName))
        return

    # create bash script
    bash_name = '{}/script.sh'.format(sample_dir)
    bashScript = '#!/bin/bash\n'
    bashScript += 'eval `scramv1 runtime -sh`\n'
    bashScript += 'ls\n'
    bashScript += 'printenv\n'
    bashScript += 'mkdir datacards_shape\n'
    bashScript += 'mv MuMuTauTau datacards_shape/MuMuTauTau\n'
    bashScript += 'files=`python -c "import PSet; print \' \'.join(list(PSet.process.source.fileNames))"`\n'
    bashScript += 'echo $files\n'
    bashScript += 'for A in $files; do\n'
    for cc in combineCommands:
        bashScript += cc.format(datacard=datacard,h=h,a=a,tag=tag)+'\n'
    bashScript += 'done\n'
    bashScript += """echo '''<FrameworkJobReport>\
<ReadBranches>\n
</ReadBranches>\n
<PerformanceReport>\n
  <PerformanceSummary Metric="StorageStatistics">\n
    <Metric Name="Parameter-untracked-bool-enabled" Value="true"/>\n
    <Metric Name="Parameter-untracked-bool-stats" Value="true"/>\n
    <Metric Name="Parameter-untracked-string-cacheHint" Value="application-only"/>\n
    <Metric Name="Parameter-untracked-string-readHint" Value="auto-detect"/>\n
    <Metric Name="ROOT-tfile-read-totalMegabytes" Value="0"/>\n
    <Metric Name="ROOT-tfile-write-totalMegabytes" Value="0"/>\n
  </PerformanceSummary>\n
</PerformanceReport>\n
<GeneratorInfo>\n
</GeneratorInfo>\n
</FrameworkJobReport>''' > FrameworkJobReport.xml\n"""
    with open(bash_name,'w') as file:
        file.write(bashScript)
    os.system('chmod +x {0}'.format(bash_name))

    # setup crab config
    from CRABClient.UserUtilities import config

    config = config()

    config.General.workArea         = submit_dir
    config.General.transferOutputs  = True

    config.JobType.pluginName       = 'Analysis'
    #config.JobType.psetName         = '{0}/src/DevTools/Utilities/test/PSet.py'.format(os.environ['CMSSW_BASE'])
    config.JobType.psetName         = 'PSet.py' 
    config.JobType.scriptExe        = bash_name
    #config.JobType.outputFiles      = []
    config.JobType.inputFiles       = ['datacards_shape/MuMuTauTau']

    config.Data.outLFNDirBase       = '/store/user/{}/{}/{}/{}'.format(UNAME, jobName, tag, h)
    config.Data.outputDatasetTag    = jobName
    config.Data.userInputFiles      = [str(a) for a in amasses]
    config.Data.splitting           = 'FileBased'
    config.Data.unitsPerJob         = pointsPerJob
    config.Data.outputPrimaryDataset= 'Limits'

    config.Site.storageSite         = 'T3_US_FNALLPC'

    # submit
    submitArgs = ['--config',config]
    if dryrun: submitArgs += ['--dryrun']

    from CRABClient.ClientExceptions import ClientException
    from CRABClient.ClientUtilities import initLoggers
    from httplib import HTTPException
    import CRABClient.Commands.submit as crabClientSubmit

    tblogger, logger, memhandler = initLoggers()
    tblogger.setLevel(logging.INFO)
    logger.setLevel(logging.INFO)
    memhandler.setLevel(logging.INFO)

    try:
        logging.info('Submitting {}/{}/{}'.format(jobName,tag,h))
        crabClientSubmit.submit(logger,submitArgs)()
    except HTTPException as hte:
        logging.info("Submission failed: {}".format(hte.headers))
    except ClientException as cle:
        logging.info("Submission failed: {}".format(cle))


def submitGridCrab(tag,h,amasses,**kwargs):
    dryrun = kwargs.get('dryrun',False)
    jobName = kwargs.get('jobName',None)
    parametric = kwargs.get('parametric',False)
    pointsPerJob = kwargs.get('pointsPerJob',1)
    toys = 5000
    rMin = 0.01
    rMax = 1.00
    rStep = 0.01

    a = '${A}'

    datacard = 'datacards_shape/MuMuTauTau/mmmt_{}_HToAAH{}A{}.txt'.format(tag,h,'X' if parametric else '${A}')

    for a in amasses:
        sample_dir = '/{}/{}/crab_projects/{}/{}/{}/{}'.format(scratchDir,pwd.getpwuid(os.getuid())[0], jobName, tag, h, a)
        python_mkdir(sample_dir)


        # create submit dir
        submit_dir = '{}/crab'.format(sample_dir)
        if os.path.exists(submit_dir):
            logging.warning('Submission directory exists for {} {} {} {}.'.format(jobName,tag,h,a))
            continue

        workspace = '{}/workspace.root'.format(sample_dir)

        # create workspace
        command = 'text2workspace.py {datacard} -m {a} -o {workspace}'.format(datacard=datacard,a=a,workspace=workspace)
        os.system(command)

        # setup crab customization
        custom = '{}/custom_crab.py'.format(sample_dir)
        customString = ''
        customString += "def custom_crab(config):\n"
        customString += "    print 'Customizing crab config'\n"
        customString += "    config.General.workArea = '{}'\n".format(submit_dir)
        customString += "    config.Data.outLFNDirBase = '/store/user/{}/{}/{}/{}/{}'\n".format(pwd.getpwuid(os.getuid())[0], jobName, tag, h, a)
        customString += "    config.Site.storageSite = 'T2_US_Wisconsin'\n"
        with open(custom,'w') as f:
            f.write(customString)

        # get combine command
        command = 'combineTool.py -d {workspace} -M HybridNew'\
                  +' --freq --LHCmode LHC-limits --clsAcc 0 -T {toys} -s -1'\
                  +' --singlePoint 0.5:1.0:0.05,0.1:0.5:0.01,0.005:0.1:0.005 --saveToys --fullBToys --saveHybridResult'\
                  +' -m {a} --job-mode crab3 --task-name {jobName} --custom-crab {custom} --merge {n}'
        command = command.format(workspace=workspace,toys=toys,a=a,jobName=jobName,custom=custom,n=pointsPerJob)

        # submit job
        os.system(command)



def parse_command_line(argv):
    parser = argparse.ArgumentParser(description='Process limits')

    # limit information
    parser.add_argument('tag', nargs='?',type=str,default='',help='MuMuTauTau tag')
    parser.add_argument('--mh', nargs='?',type=int,default=125,help='Higgs mass')
    parser.add_argument('--ma', nargs='?',type=int,default=15,help='Pseudoscalar mass')
    parser.add_argument('--parametric',action='store_true',help='Use extended a masses')
    # job submission
    parser.add_argument('--jobName', nargs='?',type=str,default='',help='Jobname for submission')
    parser.add_argument('--submit',action='store_true',help='Submit Full CLs')
    parser.add_argument('--dryrun',action='store_true',help='Dryrun for submission')
    parser.add_argument('--crab',action='store_true',help='Submit using crab')
    parser.add_argument('--grid',action='store_true',help='Submit using crab')
    parser.add_argument('--pointsPerJob', nargs='?',type=int,default=10,help='Number of mass points per job')
    # logging
    parser.add_argument('-j',type=int,default=1,help='Number of cores')
    parser.add_argument('-l','--log',nargs='?',type=str,const='INFO',default='INFO',choices=['INFO','DEBUG','WARNING','ERROR','CRITICAL'],help='Log level for logger')

    args = parser.parse_args(argv)

    return args

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    args = parse_command_line(argv)

    loglevel = getattr(logging,args.log)
    logging.basicConfig(format='%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s', level=loglevel, datefmt='%Y-%m-%d %H:%M:%S')

    if args.submit:
        amasses = range(5,23,2)
        if args.parametric: amasses = [x*0.1 for x in range(36,211,1)]
        command = submitLimitCrab if args.crab else submitLimit
        if args.grid: command = submitGridCrab
        command(args.tag,args.mh,amasses,dryrun=args.dryrun,jobName=args.jobName,parametric=args.parametric,pointsPerJob=args.pointsPerJob)
    else:
        runLimit(args.tag,args.mh,args.ma,dryrun=args.dryrun,parametric=args.parametric)

    return 0


if __name__ == "__main__":
    status = main()
    sys.exit(status)

