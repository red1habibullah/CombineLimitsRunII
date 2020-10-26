import os
import json
import pickle

def read(fname):
    pfile = '{}.pkl'.format(fname)
    if os.path.exists(pfile):
        with open(pfile,'rb') as f:
            results = pickle.load(f)
    else:
        results = {}
    return results

doSignal = True
doBackground = True
h = 125
region = 'PP'
shifts = ['lep','tau','trig','pu','btag','MuonEn','TauEn','qcd']
shifts = ['MuonEn']

amasses = ['3p6',4,5,6,7,9,11,13,15,17,19,21]

sigfname = 'fitParams/HaaLimits2D_unbinned_h/fullWithControl/central/h{h}_{region}'
shiftsigfname = 'fitParams/HaaLimits2D_unbinned_h/fullWithControl/{shift}/h{h}_{region}_{shift}'
bgfname = 'fitParams/HaaLimits2D_unbinned_h/fullWithControl/background_{region}'
shiftbgfname = 'fitParams/HaaLimits2D_unbinned_h/fullWithControl/background_{region}_{shift}'
compfname = 'fitParams/HaaLimits2D_unbinned_h/fullWithControl/components_{region}'
shiftcompfname = 'fitParams/HaaLimits2D_unbinned_h/fullWithControl/components_{region}_{shift}'

if doSignal:
    central = read(sigfname.format(h=h,region=region))
    for shift in shifts:
        up = read(shiftsigfname.format(shift=shift+'Up',h=h,region=region))
        down = read(shiftsigfname.format(shift=shift+'Down',h=h,region=region))
    
        print h, region, shift, 'integral'
        for a in amasses:
            integral = [
                central['integrals'][h][a],
                up[     'integrals'][h][a],
                down[   'integrals'][h][a],
            ]
            relup   = (integral[1]-integral[0]) / integral[0]
            reldown = (integral[2]-integral[0]) / integral[0]
            print '    {:3}: {:6.2f} {:+4.1f}% {:+4.1f}% '.format(a, integral[0], relup*100, reldown*100)
    
        print ''
        for param in ['mean_sigx','sigma_sigx','width_sigx', 'mean_sigy', 'sigma1_sigy','sigma2_sigy']:
            print h, region, shift, param
            for a in amasses:
                params = [
                    central['vals'][h][a][param],
                    up[     'vals'][h][a][param],
                    down[   'vals'][h][a][param],
                ]
                relup   = (params[1]-params[0]) / params[0]
                reldown = (params[2]-params[0]) / params[0]
                print '    {:3}: {:6.2f} {:+4.1f}% {:+4.1f}% '.format(a, params[0], relup*100, reldown*100)
    
            print ''

if doBackground: 
    central = read(bgfname.format(region=region))
    for shift in ['fake']:
        up = read(shiftbgfname.format(shift=shift+'Up',region=region))
        down = read(shiftbgfname.format(shift=shift+'Down',region=region))
    
        print 'background', region, shift, 'integral'
        integral = [
            central['integral'],
            up[     'integral'],
            down[   'integral'],
        ]
        relup   = (integral[1]-integral[0]) / integral[0]
        reldown = (integral[2]-integral[0]) / integral[0]
        print '    {:20}: {:6.2f} {:+4.1f}% {:+4.1f}% '.format('integral',integral[0], relup*100, reldown*100)

        for param in ['lambda_cont1_PP_x','lambda_cont3_PP_x','mu_bg_PP_y','sigma_bg_PP_y']:
            params = [
                central['vals'][param],
                up[     'vals'][param],
                down[   'vals'][param],
            ]
            relup   = (params[1]-params[0]) / params[0]
            reldown = (params[2]-params[0]) / params[0]
            print '    {:20}: {:6.2f} {:+4.1f}% {:+4.1f}% '.format(param, params[0], relup*100, reldown*100)

        print ''
