import FWCore.ParameterSet.Config as cms

process = cms.Process("CrabDummy")

process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring()
)
