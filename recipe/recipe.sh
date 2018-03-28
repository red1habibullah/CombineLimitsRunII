#!/bin/bash
pushd $CMSSW_BASE/src

# setup Higgs Combine
git clone https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit
pushd HiggsAnalysis/CombinedLimit

git fetch origin
git checkout v7.0.6

popd

# setup CombineHarvester
git clone https://github.com/cms-analysis/CombineHarvester.git CombineHarvester

popd
