#!/usr/bin/env python
import os
import sys
import argparse
from array import array
import ROOT

class TopPlot(object):

    def __init__(self,lines):
        self.lines = lines

    def convert(self,tfile):
        self.graph_names = []
        self.graph_styles = []
        self.graph_values = []
        inLabel = False
        inValues = False
        values = []
        for line in self.lines:
            if 'SET' in line.upper():
                # TODO: convert plot options
                pass
            elif 'CASE' in line.upper():
                continue
            elif 'TITLE TOP' in line.upper():
                self.title = line.strip().split("'")[1]
            elif 'TITLE BOTTOM' in line.upper():
                self.xlabel = line.strip().split("'")[1]
            elif 'TITLE LEFT' in line.upper():
                self.ylabel = line.strip().split("'")[1]
            elif 'TITLE' in line.upper():
                self.graph_names += [line.strip().split("'")[1]]
                inLabel = True
            elif 'JOIN' in line.upper() and inLabel:
                self.graph_styles += [' '.join(line.strip().split()[1:])]
                inLabel = False
            elif inLabel:
                continue
            elif 'JOIN' in line.upper() and inValues:
                inValues = False
                self.graph_values += [values]
                values = []
            else:
                inValues = True
                try:
                    values += [[float(v) for v in line.strip().split()]]
                except:
                    print line

        print self.title
        folder = tfile.mkdir(self.title)
        folder.cd()
        for i in range(len(self.graph_names)):
            print self.graph_names[i], len(self.graph_values[i])
            graph = self.getTGraph(self.graph_values[i])
            graph.SetName(self.graph_names[i])
            graph.SetTitle(self.graph_names[i])
            graph.Write(self.graph_names[i])
        tfile.cd()


    def getTGraph(self,values):
        xvals = [v[0] for v in values]
        yvals = [v[1] for v in values]
        graph = ROOT.TGraph(len(xvals),array('d',xvals),array('d',yvals))
        return graph


class TopFile(object):

    def __init__(self,fname):
        self.fname = fname

    def convert(self):

        rname = self.fname.replace('.top','.root')
        tfile = ROOT.TFile.Open(rname,'RECREATE')
        
        plots = []
        with open(self.fname,'r') as f:
            lines = []
            for line in f.readlines():
                if 'NEW FRAME' in line.upper():
                    plots += [TopPlot(lines)]
                    lines = []
                    continue
                lines += [line]
            if lines:
                plots += [TopPlot(lines)]

        for plot in plots:
            plot.convert(tfile)

        tfile.Close()


def parse_command_line(argv):
    parser = argparse.ArgumentParser(description='Convert topdrawer files to root')

    parser.add_argument('fname', type=str, help='Topdrawer file')

    return parser.parse_args(argv)


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    args = parse_command_line(argv)

    top = TopFile(args.fname)
    top.convert()

    return 0

if __name__ == "__main__":
    status = main()
    sys.exit(status)
