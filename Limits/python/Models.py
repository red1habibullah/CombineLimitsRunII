import logging

from array import array

import ROOT


from CombineLimits.Limits.utilities import *

class Model(object):

    def __init__(self,name,**kwargs):
        self.name = name
        self.x = kwargs.pop('x','x')
        self.y = kwargs.pop('y','y')
        self.z = kwargs.pop('z','z')
        self.kwargs = kwargs

    def update(self,**kwargs):
        '''Update the floating parameters'''
        self.kwargs.update(kwargs)

    def build(self,ws,label):
        '''Dummy method to add model to workspace'''
        pass

    def fit(self,ws,hist,name,save=False,doErrors=False,saveDir=''):
        '''Fit the model to a histogram and return the fit values'''

        if isinstance(hist,ROOT.TH1):
            dhname = 'dh_{0}'.format(name)
            hist = ROOT.RooDataHist(dhname, dhname, ROOT.RooArgList(ws.var(self.x)), hist)
        self.build(ws,name)
        model = ws.pdf(name)
        fr = model.fitTo(hist,ROOT.RooFit.Save(),ROOT.RooFit.SumW2Error(True))
        pars = fr.floatParsFinal()
        vals = {}
        errs = {}
        for p in range(pars.getSize()):
            vals[pars.at(p).GetName()] = pars.at(p).getValV()
            errs[pars.at(p).GetName()] = pars.at(p).getError()

        if save:
            if saveDir: python_mkdir(saveDir)
            savename = '{}/{}_{}'.format(saveDir,self.name,name) if saveDir else '{}_{}'.format(self.name,name)
            x = ws.var(self.x)
            xFrame = x.frame()
            xFrame.SetTitle('')
            hist.plotOn(xFrame)
            model.plotOn(xFrame)
            model.paramOn(xFrame)
            canvas = ROOT.TCanvas(savename,savename,800,800)
            xFrame.Draw()
            canvas.Print('{0}.png'.format(savename))

        if doErrors:
            return vals, errs
        return vals

    def setIntegral(self,integral):
        self.integral = integral

    def getIntegral(self):
        if hasattr(self,'integral'): return self.integral
        return 1

class ModelSpline(Model):

    def __init__(self,name,**kwargs):
        self.MH = kwargs.pop('MH','MH')
        super(ModelSpline,self).__init__(name,**kwargs)

    def setIntegral(self,masses,integrals):
        self.masses = masses
        self.integrals = integrals

    def buildIntegral(self,ws,label):
        if not hasattr(self,'integrals'): return 
        integralSpline  = ROOT.RooSpline1D(label,  label,  ws.var(self.MH), len(self.masses), array('d',self.masses), array('d',self.integrals))
        # import to workspace
        getattr(ws, "import")(integralSpline, ROOT.RooFit.RecycleConflictNodes())

class SplineParam(object):

    def __init__(self,name,**kwargs):
        self.name = name
        self.kwargs = kwargs

    def build(self,ws,label):
        paramName = '{0}'.format(label) 
        ws.factory('{0}[0,-10,10]'.format(paramName))

class Spline(object):

    def __init__(self,name,**kwargs):
        self.name = name
        self.mh = kwargs.pop('MH','MH')
        self.kwargs = kwargs

    def build(self,ws,label):
        masses = self.kwargs.get('masses', [])
        values = self.kwargs.get('values', [])
        shifts = self.kwargs.get('shifts', {})
        splineName = label
        if shifts:
            centralName = '{0}_central'.format(label)
            splineCentral = ROOT.RooSpline1D(centralName,  centralName,  ws.var(self.mh), len(masses), array('d',masses), array('d',values))
            getattr(ws, "import")(splineCentral, ROOT.RooFit.RecycleConflictNodes())
            shiftFormula = '{0}'.format(centralName)
            for shift in shifts:
                up = [u-c for u,c in zip(shifts[shift]['up'],values)]
                down = [d-c for d,c in zip(shifts[shift]['down'],values)]
                upName = '{0}_{1}Up'.format(splineName,shift)
                downName = '{0}_{1}Down'.format(splineName,shift)
                splineUp   = ROOT.RooSpline1D(upName,  upName,  ws.var(self.mh), len(masses), array('d',masses), array('d',up))
                splineDown = ROOT.RooSpline1D(downName,downName,ws.var(self.mh), len(masses), array('d',masses), array('d',down))
                getattr(ws, "import")(splineUp, ROOT.RooFit.RecycleConflictNodes())
                getattr(ws, "import")(splineDown, ROOT.RooFit.RecycleConflictNodes())
                shiftFormula += ' + TMath::Max(0,{shift})*{upName} + TMath::Min(0,{shift})*{downName}'.format(shift=shift,upName=upName,downName=downName)
            spline = ROOT.RooFormulaVar(splineName, splineName, shiftFormula, ROOT.RooArgList())
        else:
            spline = ROOT.RooSpline1D(splineName,  splineName,  ws.var(self.mh), len(masses), array('d',masses), array('d',values))
        getattr(ws, "import")(spline, ROOT.RooFit.RecycleConflictNodes())

class Polynomial(Model):

    def __init__(self,name,**kwargs):
        super(Chebychev,self).__init__(name,**kwargs)

    def build(self,ws,label):
        order = self.kwargs.get('order',1)
        params = ['p{}_{}'.format(o,label) for o in range(order)]
        ranges = [self.kwargs.get('p{}'.format(o),[0,-1,1]) for o in range(order)]
        ws.factory('Polynomial::{}({}, {{ {} }})'.format(label, self.x, ', '.join(['{}[{}]'.format(p,','.join([str(r) for r in rs])) for p,rs in zip(params,ranges)])))
        self.params = params

class PolynomialSpline(ModelSpline):

    def __init__(self,name,**kwargs):
        super(ChebychevSpline,self).__init__(name,**kwargs)

    def build(self,ws,label):
        order = self.kwargs.get('order',1)
        masses = self.kwargs.get('masses',[])
        paramSplines = {}
        params = []
        for o in range(order):
            ps = self.kwargs.get('p{}'.format(o), [])
            paramName = 'p{}_{}'.format(o,label)
            paramSplines[o] = ROOT.RooSpline1D(paramName, paramName, ws.var('MH'), len(masses), array('d',masses), array('d',ps))
            getattr(ws, "import")(paramSplines[o], ROOT.RooFit.RecycleConflictNodes())
            params += [paramName]
        ws.factory('Polynomial::{}({}, {{ {} }})'.format(label, self.x, ', '.join(['{}[0, -10, 10]'.format(p) for p in params])))
        self.params = params

class Chebychev(Model):

    def __init__(self,name,**kwargs):
        super(Chebychev,self).__init__(name,**kwargs)

    def build(self,ws,label):
        order = self.kwargs.get('order',1)
        params = ['p{}_{}'.format(o,label) for o in range(order)]
        ranges = [self.kwargs.get('p{}'.format(o),[0,-1,1]) for o in range(order)]
        ws.factory('Chebychev::{}({}, {{ {} }})'.format(label, self.x, ', '.join(['{}[{}]'.format(p,','.join([str(r) for r in rs])) for p,rs in zip(params,ranges)])))
        self.params = params

class ChebychevSpline(ModelSpline):

    def __init__(self,name,**kwargs):
        super(ChebychevSpline,self).__init__(name,**kwargs)

    def build(self,ws,label):
        order = self.kwargs.get('order',1)
        masses = self.kwargs.get('masses',[])
        paramSplines = {}
        params = []
        for o in range(order):
            ps = self.kwargs.get('p{}'.format(o), [])
            paramName = 'p{}_{}'.format(o,label)
            paramSplines[o] = ROOT.RooSpline1D(paramName, paramName, ws.var('MH'), len(masses), array('d',masses), array('d',ps))
            getattr(ws, "import")(paramSplines[o], ROOT.RooFit.RecycleConflictNodes())
            params += [paramName]
        ws.factory('Chebychev::{}({}, {{ {} }})'.format(label, self.x, ', '.join(['{}[0, -10, 10]'.format(p) for p in params])))
        self.params = params

class Gaussian(Model):

    def __init__(self,name,**kwargs):
        super(Gaussian,self).__init__(name,**kwargs)

    def build(self,ws,label):
        meanName = 'mean_{0}'.format(label)
        sigmaName = 'sigma_{0}'.format(label)
        mean = self.kwargs.get('mean',[1,0,1000])
        sigma = self.kwargs.get('sigma',[1,0,100])
        # variables
        ws.factory('{0}[{1}, {2}, {3}]'.format(meanName,*mean))
        ws.factory('{0}[{1}, {2}, {3}]'.format(sigmaName,*sigma))
        # build model
        ws.factory("Gaussian::{0}({1}, {2}, {3})".format(label,self.x,meanName,sigmaName))
        self.params = [meanName,sigmaName]

class GaussianSpline(ModelSpline):

    def __init__(self,name,**kwargs):
        super(GaussianSpline,self).__init__(name,**kwargs)

    def build(self,ws,label):
        meanName = 'mean_{0}'.format(label)
        sigmaName = 'sigma_{0}'.format(label)
        masses = self.kwargs.get('masses', [])
        means  = self.kwargs.get('means',  [])
        sigmas = self.kwargs.get('sigmas', [])
        # splines
        meanSpline  = ROOT.RooSpline1D(meanName,  meanName,  ws.var('MH'), len(masses), array('d',masses), array('d',means))
        sigmaSpline = ROOT.RooSpline1D(sigmaName, sigmaName, ws.var('MH'), len(masses), array('d',masses), array('d',sigmas))
        # import
        getattr(ws, "import")(meanSpline, ROOT.RooFit.RecycleConflictNodes())
        getattr(ws, "import")(sigmaSpline, ROOT.RooFit.RecycleConflictNodes())
        # build model
        ws.factory("Gaussian::{0}({1}, {2}, {3})".format(label,self.x,meanName,sigmaName))
        self.params = [meanName,sigmaName]

class BreitWigner(Model):

    def __init__(self,name,**kwargs):
        super(BreitWigner,self).__init__(name,**kwargs)

    def build(self,ws,label):
        meanName = 'mean_{0}'.format(label)
        widthName = 'width_{0}'.format(label)
        mean  = self.kwargs.get('mean',  [1,0,1000])
        width = self.kwargs.get('width', [1,0,100])
        # variables
        ws.factory('{0}[{1}, {2}, {3}]'.format(meanName,*mean))
        ws.factory('{0}[{1}, {2}, {3}]'.format(widthName,*width))
        # build model
        ws.factory("BreitWigner::{0}({1}, {2}, {3})".format(label,self.x,meanName,widthName))
        self.params = [meanName,widthName]

class BreitWignerSpline(ModelSpline):

    def __init__(self,name,**kwargs):
        super(BreitWignerSpline,self).__init__(name,**kwargs)

    def build(self,ws,label):
        meanName = 'mean_{0}'.format(label)
        widthName = 'width_{0}'.format(label)
        masses = self.kwargs.get('masses', [])
        means  = self.kwargs.get('means',  [])
        widths = self.kwargs.get('widths', [])
        # splines
        meanSpline  = ROOT.RooSpline1D(meanName,  meanName,  ws.var('MH'), len(masses), array('d',masses), array('d',means))
        widthSpline = ROOT.RooSpline1D(widthName, widthName, ws.var('MH'), len(masses), array('d',masses), array('d',widths))
        # import
        getattr(ws, "import")(meanSpline, ROOT.RooFit.RecycleConflictNodes())
        getattr(ws, "import")(widthSpline, ROOT.RooFit.RecycleConflictNodes())
        # build model
        ws.factory("BreitWigner::{0}({1}, {2}, {3})".format(label,self.x,meanName,widthName))
        self.params = [meanName,widthName]

class Voigtian(Model):

    def __init__(self,name,**kwargs):
        super(Voigtian,self).__init__(name,**kwargs)

    def build(self,ws,label):
        meanName = 'mean_{0}'.format(label)
        widthName = 'width_{0}'.format(label)
        sigmaName = 'sigma_{0}'.format(label)
        mean  = self.kwargs.get('mean',  [1,0,1000])
        width = self.kwargs.get('width', [1,0,100])
        sigma = self.kwargs.get('sigma', [1,0,100])
        # variables
        ws.factory('{0}[{1}, {2}, {3}]'.format(meanName,*mean))
        ws.factory('{0}[{1}, {2}, {3}]'.format(widthName,*width))
        ws.factory('{0}[{1}, {2}, {3}]'.format(sigmaName,*sigma))
        # build model
        ws.factory("Voigtian::{0}({1}, {2}, {3}, {4})".format(label,self.x,meanName,widthName,sigmaName))
        self.params = [meanName,widthName,sigmaName]

class VoigtianSpline(ModelSpline):

    def __init__(self,name,**kwargs):
        super(VoigtianSpline,self).__init__(name,**kwargs)

    def build(self,ws,label):
        meanName = 'mean_{0}'.format(label)
        widthName = 'width_{0}'.format(label)
        sigmaName = 'sigma_{0}'.format(label)
        masses = self.kwargs.get('masses', [])
        means  = self.kwargs.get('means',  [])
        widths = self.kwargs.get('widths', [])
        sigmas = self.kwargs.get('sigmas', [])
        # splines
        meanSpline  = ROOT.RooSpline1D(meanName,  meanName,  ws.var('MH'), len(masses), array('d',masses), array('d',means))
        widthSpline = ROOT.RooSpline1D(widthName, widthName, ws.var('MH'), len(masses), array('d',masses), array('d',widths))
        sigmaSpline = ROOT.RooSpline1D(sigmaName, sigmaName, ws.var('MH'), len(masses), array('d',masses), array('d',sigmas))
        # import
        getattr(ws, "import")(meanSpline, ROOT.RooFit.RecycleConflictNodes())
        getattr(ws, "import")(widthSpline, ROOT.RooFit.RecycleConflictNodes())
        getattr(ws, "import")(sigmaSpline, ROOT.RooFit.RecycleConflictNodes())
        # build model
        ws.factory("Voigtian::{0}({1}, {2}, {3}, {4})".format(label,self.x,meanName,widthName,sigmaName))
        self.params = [meanName,widthName,sigmaName]

class Exponential(Model):

    def __init__(self,name,**kwargs):
        super(Exponential,self).__init__(name,**kwargs)

    def build(self,ws,label):
        lambdaName = 'lambda_{0}'.format(label)
        lamb = self.kwargs.get('lamb',  [-1,-5,0])
        # variables
        ws.factory('{0}[{1}, {2}, {3}]'.format(lambdaName,*lamb))
        # build model
        ws.factory("Exponential::{0}({1}, {2})".format(label,self.x,lambdaName))
        self.params = [lambdaName]

class Sum(Model):

    def __init__(self,name,**kwargs):
        self.doRecursive = kwargs.pop('recursive',False)
        self.doExtended = kwargs.pop('extended',False)
        super(Sum,self).__init__(name,**kwargs)

    #def recurse(self,curr,remaining):
    #    if len(remaining):
    #        return '{0}_frac*{0} + (1-{0}_frac)*({2})'.format(curr,self.recurse(remaining[0],remaining[1:]))
    #    else:
    #        return '{0}_frac*{0}'.format(curr)

    def build(self,ws,label):
        pdfs = []
        sumpdfs = []
        for n, (pdf, r) in enumerate(sorted(self.kwargs.iteritems())):
            if len(r)==2:
                ws.factory('{0}_frac[{1},{2}]'.format(pdf,*r))
                sumpdfs += [pdf]
            elif len(r)==3:
                ws.factory('{0}_frac[{1},{2},{3}]'.format(pdf,*r))
                sumpdfs += [pdf]
            pdfs += [pdf]
        pdf = sorted(pdfs)
        # build model
        if self.doRecursive:
            sumargs = ['{0}_frac*{0}'.format(pdf) for pdf in pdfs[:-1]] + [pdfs[-1]]
            ws.factory("RSUM::{0}({1})".format(label, ', '.join(sumargs)))
        elif self.doExtended:
            sumargs = ['{0}_frac*{0}'.format(pdf) for pdf in pdfs]
            ws.factory("sum::{0}({1})".format(label, ', '.join(sumargs)))
        else: # Don't do this if you have more than 2 pdfs ...
            if len(sumpdfs)>1: logging.warning('This sum is not guaranteed to be positive because there are more than two arguments. Better to use the option recursive=True.')
            sumargs = ['{0}_frac*{0}'.format(pdf) for pdf in sumpdfs] + ['{0}'.format(pdf) for pdf in pdfs if pdf not in sumpdfs]
            ws.factory("SUM::{0}({1})".format(label, ', '.join(sumargs)))
        self.params = ['{}_frac'.format(pdf) for pdf in pdfs]

class Prod(Model):

    def __init__(self,name,*args,**kwargs):
        super(Prod,self).__init__(name,**kwargs)
        self.args = args

    def build(self,ws,label):
        ws.factory("PROD::{0}({1})".format(label, ', '.join(self.args)))
        self.params = []
