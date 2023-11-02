import os
import sys
import errno
import operator
import subprocess
import logging
import math
import json
import pickle

# common definitions
ZMASS = 91.1876

# helper functions
def python_mkdir(dir):
    '''A function to make a unix directory as well as subdirectories'''
    try:
        os.makedirs(dir)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(dir):
            pass
        else: raise

def which(program):
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None

def getLumi():
    #return 36330.060 # full 2016
    return 41480 # full 2017 
    #return 59830 # full 2018
    #return 137640 # full run 2

def runCommand(command):
    return subprocess.Popen(command,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT).communicate()[0]


def getCMSSWMajorVersion():
    return os.environ['CMSSW_VERSION'].split('_')[1]

def getCMSSWMinorVersion():
    return os.environ['CMSSW_VERSION'].split('_')[2]

def getCMSSWVersion():
    return ''.join([getCMSSWMajorVersion(),getCMSSWMinorVersion(),'X'])

def sumWithError(*args):
    val = sum([x[0] for x in args])
    err = (sum([x[1]**2 for x in args]))**0.5
    return (val,err)

def diffWithError(a,b):
    val = a[0]-b[0]
    err = (a[1]**2 + b[1]**2)**0.5
    return (val,err)

def prod(iterable):
    return reduce(operator.mul, iterable, 1)

def prodWithError(*args):
    val = prod([x[0] for x in args])
    err = abs(val) * (sum([(x[1]/x[0])**2 for x in args if x[0]]))**0.5
    return (val,err)

def divWithError(num,denom):
    val = num[0]/denom[0] if denom[0] else 0.
    err = abs(val) * ((num[1]/num[0])**2 + (denom[1]/denom[0])**2)**0.5 if num[0] and denom[0] else 0.
    return (val, err)

def sqrtWithError(a):
    val = a[0]**0.5
    err = 0.5*a[1]
    return (val,err)

def sOverB(s,b):
    return s[0]/b[0] if b[0] else 0.

def poissonSignificance(s,b):
    return s[0]/b[0]**0.5 if b[0] else 0.

def poissonSignificanceWithError(s,b):
    return s[0]/(b[0]+b[1]**2)**0.5 if b[0] or b[1] else 0.

def asimovSignificance(s,b):
    if b[1]>b[0]: b = (b[1],b[1]) # avoid negative stuff
    if not b[0]: return 0.
    sPlusB = s[0]+b[0]
    sOverB = s[0]/b[0]
    if sOverB<1e-5: return poissonSignificance(s,b) # avoid floating point problems with small s
    #return (2*(sPlusB*math.log(1+sOverB)-1))**0.5
    return (2*(sPlusB*math.log(1+sOverB)-s[0]))**0.5 # another source

def asimovSignificanceWithError(s,b):
    if b[1]>b[0]: b = (b[1],b[1]) # avoid negative stuff
    if not b[0]: return 0.
    if not b[1]: return asimovSignificance(s,b) # no error on background
    sPlusB = s[0]+b[0]
    sOverB = s[0]/b[0]
    bOverE = b[0]/b[1]
    if sOverB<1e-5: return poissonSignificanceWithError(s,b) # avoid floating point problems with small s
    return (2*(sPlusB*math.log(sPlusB*(b[0]+b[1]**2)/(b[0]**2+sPlusB*b[1]**2))-bOverE**2*math.log(1+b[1]**2*s[0]/(b[0]*(b[0]+b[1]**2)))))**0.5

def dumpData(name,data):
    jfile = 'jsons/{0}.json'.format(name)
    pfile = 'pickles/{0}.pkl'.format(name)
    python_mkdir(os.path.dirname(jfile))
    python_mkdir(os.path.dirname(pfile))
    with open(jfile,'w') as f:
        f.write(json.dumps(data, indent=4, sort_keys=True))
    with open(pfile,'wb') as f:
        pickle.dump(data,f)
