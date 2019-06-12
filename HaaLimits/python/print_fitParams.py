import os
import json

hmasses = [125,300,750]
amasses = [3.6,4,5,6,7,9,11,13,15,17,19,21]

params = ['mean_sigx','sigma_sigx','width_sigx','mean_sigy','sigma1_sigy','sigma2_sigy']

shifts = ['CMS_btag_comb','CMS_eff_m','CMS_eff_t','CMS_pu','CMS_scale_m','CMS_scale_t']#,'QCDscale_ggH']


def a2str(a):
    return str(a).replace('.','p')

def str2a(a):
    return float(str(a).replace('p','.'))

def read(h,a,shift='central',direction=''):
    results = {}
    if h!=125 and a in [3.6,4,6,8,10,12,14,16,18,20]: return results

    fname = 'fitParams/HaaLimits2D_unbinned_h/with1DFits/{shift}/h{h}_a{a}_PP{shifttag}.json'.format(shift=shift+direction,h=h,a=a2str(a),shifttag='' if shift=='central' else '_'+shift+direction)
    with open(fname) as f:
        data = json.load(f)
    for param in params:
        results[param] = (data['vals'][param], data['errs'][param])
    results['integral'] = (data['integrals'], 0.01*data['integrals']) # hack, forgot to save, set to 10k events
    return results

results = {}
for h in hmasses:
    results[h] = {}
    for a in amasses:
        results[h][a] = {}
        results[h][a]['central'] = read(h,a)
        for shift in shifts:
            results[h][a][shift+'Up'] = read(h,a,shift=shift,direction='Up')
            results[h][a][shift+'Down'] = read(h,a,shift=shift,direction='Down')


for shift in shifts:
    print shift
    for param in params+['integral']:
        print '  ', param
        for h in hmasses:
            ds = []
            for a in amasses:
                if not results[h][a][shift+'Up']: continue
                data = results[h][a]['central']
                dataUp = results[h][a][shift+'Up']
                dataDown = results[h][a][shift+'Down']
                v,e = data[param]
                vu,eu = dataUp[param]
                vd,ed = dataDown[param]
                du = (vu-v)/v if v else 0.
                dd = (v-vd)/v if v else 0.
                d = (abs(du)+abs(dd))/2.
                ds += [d]
            if ds:
                print '    ', h, min(ds), max(ds)

        
