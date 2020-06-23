import ROOT
ROOT.gROOT.SetBatch()
ROOT.gStyle.SetOptStat(1101)
C=ROOT.TCanvas("C","C",600,600)

ARANGE=[0,25]
h='125'
tag='test'
func=ROOT.TF1('integral_h{}_{}'.format(h,tag),  '[0]+TMath::Erf([1]+[2]*x)*TMath::Erfc([3]+[4]*x)', *ARANGE)
func.SetParameter(1,-0.2)#.005
func.SetParameter(2,0.032) #.02
func.SetParameter(3,-0.9)
func.SetParameter(4,0.06)#.08
func.Draw()
C.SaveAs("plot.png")

