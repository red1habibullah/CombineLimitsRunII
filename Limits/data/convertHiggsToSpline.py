import pandas as pd
import numpy as np
from array import array

import ROOT
ROOT.gROOT.SetBatch(True)

def dumpSpline(worksheet):
    
    #xlsxname = 'HiggsAnalysis/CombinedLimit/data/lhc-hxswg/Higgs_XSBR_YR4_update.xlsx'
    xlsxname = 'Higgs_XSBR_YR4_update.xlsx'
    outname = 'Higgs_{}.root'.format(worksheet.replace(' ','_'))
    
    old = False
    
    df = pd.read_excel(xlsxname, sheetname=worksheet, skiprows=5, header=None, startcol=0)
    
    arrays = {}
    
    groups = ['ggF_N3LO','ggF_NNLONNLL','VBF','WH','ZH','ttH','bbH','tH_tch','tH_sch']#,'WplusH','WminusH']
    if old:
        groups = groups[1:]
        df = df.iloc[:,:78]
    else:
        df = df.iloc[:,:85]
    
    col = 0
    labels = []
    for group in groups:
        if group=='WplusH':
            labels += ['total']
            labels += [None]
            labels += [None]
            labels += [None]
        if group == 'ggF_N3LO':
            labels += ['mh_{}'.format(group)]
            labels += ['xsec_{}'.format(group)]
            labels += ['theory_up_{}'.format(group)]
            labels += ['theory_down_{}'.format(group)]
            labels += ['theory_err_{}'.format(group)]
            labels += ['pdfalpha_err_{}'.format(group)]
        else:
            labels += ['mh_{}'.format(group)]
            labels += ['xsec_{}'.format(group)]
            labels += ['scale_up_{}'.format(group)]
            labels += ['scale_down_{}'.format(group)]
            labels += ['pdfalpha_err_{}'.format(group)]
            labels += ['pdf_err_{}'.format(group)]
            labels += ['alpha_err_{}'.format(group)]
            labels += ['deltaEW_{}'.format(group)]
        if group=='WH':
            labels += ['xsec_Wplus_{}'.format(group)]
            labels += ['xsec_Wminus_{}'.format(group)]
        if group=='ZH':
            labels += ['ggZH_box_{}'.format(group)]
        if group in ['tH_tch','tH_sch']:
            labels += ['xsec_tH_{}'.format(group)]
            labels += ['xsec_tbarH_{}'.format(group)]
        labels += [None]
    
    labels = labels[:-1]
    df.columns = labels
    
    
    ws = ROOT.RooWorkspace(worksheet.replace(' ','_'))
    splines = []
    mhlabel = ''
    for label in labels:
        if label==None: continue
        if label.startswith('mh'): 
            mhlabel = label
            continue
    
        print label
    
        mhs = df[pd.notnull(df[label])][mhlabel]
        vals = df[pd.notnull(df[label])][label]
    
        print vals.dtype
        if vals.dtype!='float64':
            continue
            vals = pd.to_numeric(vals.astype(basestring).str.replace('?',''))
    
        if len(vals.index):
            ws.factory('MH[{},{}]'.format(min(mhs),max(mhs)))
            ws.var('MH').setUnit('GeV')
            spline = ROOT.RooSpline1D(label,label,ws.var('MH'), len(mhs.index), array('d',mhs), array('d',vals))
            getattr(ws,'import')(spline)
    
    ws.SaveAs(outname)

worksheets = ['YR4 BSM 13TeV','YR4 SM 13TeV']

for worksheet in worksheets:
    dumpSpline(worksheet)
