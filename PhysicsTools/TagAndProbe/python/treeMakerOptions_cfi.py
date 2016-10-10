import FWCore.ParameterSet.Config as cms

def setModules(process, options):
    
    process.sampleInfo = cms.EDProducer("tnp::SampleInfoTree",
                                        #vertexCollection = cms.InputTag("offlineSlimmedPrimaryVertices"),
                                        genInfo = cms.InputTag("generator")
                                        )
    
    process.eleVarHelper = cms.EDProducer("PatElectronVariableHelper",
                                          probes = cms.InputTag(options['ELECTRON_COLL']),
                                          vertexCollection = cms.InputTag("offlineSlimmedPrimaryVertices")
                                          )
    
    from HLTrigger.HLTfilters.hltHighLevel_cfi import hltHighLevel
    process.hltFilter = hltHighLevel.clone()
    process.hltFilter.throw = cms.bool(True)
    process.hltFilter.HLTPaths = options['TnPPATHS']
    process.hltFilter.TriggerResultsTag = cms.InputTag("TriggerResults","",options['HLTProcessName'])
    
    from PhysicsTools.TagAndProbe.pileupConfiguration_cfi import pileupProducer
    process.pileupReweightingProducer = pileupProducer.clone()
    
###################################################################                                                                               
## Electron/Photon MODULES                                                                                                                                    
###################################################################                                    
    
    process.goodElectrons = cms.EDFilter("PATElectronRefSelector",
                                         src = cms.InputTag( options['ELECTRON_COLL'] ),
                                         cut = cms.string(   options['ELECTRON_CUTS'] )
                                         )
    process.goodPhotons =  cms.EDFilter("PATPhotonRefSelector",
                                        src = cms.InputTag( options['PHOTON_COLL'] ),
                                        cut = cms.string(   options['PHOTON_CUTS'] )
                                        )

    
###################################################################                                                                     
## SUPERCLUSTER MODULES                                                     
###################################################################         
    
    process.superClusterCands = cms.EDProducer("ConcreteEcalCandidateProducer",
                                               src = cms.InputTag(options['SUPERCLUSTER_COLL']),
                                               particleType = cms.int32(11),
                                               )
    
    process.goodSuperClusters = cms.EDFilter("RecoEcalCandidateRefSelector",
                                             src = cms.InputTag("superClusterCands"),
                                             cut = cms.string(options['SUPERCLUSTER_CUTS']),
                                             filter = cms.bool(True)
                                             )
    
    process.GsfMatchedSuperClusterCands = cms.EDProducer("PatElectronMatchedCandidateProducer",
                                                         src     = cms.InputTag("superClusterCands"),
                                                         ReferenceElectronCollection = cms.untracked.InputTag("goodElectrons"),
                                                         cut = cms.string(options['SUPERCLUSTER_CUTS'])
                                                         )
    
###################################################################
## TRIGGER MATCHING
###################################################################
    
    process.goodElectronsTagHLT = cms.EDProducer("PatElectronTriggerCandProducer",
                                                 filterNames = cms.vstring(options['TnPHLTTagFilters']),
                                                 inputs      = cms.InputTag("goodElectronsTAGCutBasedTight"),
                                                 bits        = cms.InputTag('TriggerResults::'+options['HLTProcessName']),
                                                 objects     = cms.InputTag('selectedPatTrigger'),
                                                 dR          = cms.double(0.3),
                                                 isAND       = cms.bool(True)
                                                 )
    
    process.goodElectronsProbeHLT = cms.EDProducer("PatElectronTriggerCandProducer",
                                                   filterNames = cms.vstring(options['TnPHLTProbeFilters']),
                                                   inputs      = cms.InputTag("goodElectrons"),
                                                   bits        = cms.InputTag('TriggerResults::'+options['HLTProcessName']),
                                                   objects     = cms.InputTag('selectedPatTrigger'),
                                                   dR          = cms.double(0.3),
                                                   isAND       = cms.bool(True)
                                                   )
    
    process.goodElectronsProbeMeasureHLT = cms.EDProducer("PatElectronTriggerCandProducer",
                                                          filterNames = cms.vstring(options['TnPHLTProbeFilters']),
                                                          inputs      = cms.InputTag("goodElectrons"),
                                                          bits        = cms.InputTag('TriggerResults::'+options['HLTProcessName']),
                                                          objects     = cms.InputTag('selectedPatTrigger'),
                                                          dR          = cms.double(0.3),
                                                          isAND       = cms.bool(True)
                                                          )
    
    process.goodElectronsMeasureHLT = cms.EDProducer("PatElectronTriggerCandProducer",
                                                     filterNames = cms.vstring(options['HLTFILTERTOMEASURE']),
                                                     inputs      = cms.InputTag("goodElectronsProbeMeasureHLT"),
                                                     bits        = cms.InputTag('TriggerResults::'+options['HLTProcessName']),
                                                     objects     = cms.InputTag('selectedPatTrigger'),
                                                     dR          = cms.double(0.3),
                                                     isAND       = cms.bool(False)
                                                     )
    
    process.goodPhotonsProbeHLT = cms.EDProducer("PatPhotonTriggerCandProducer",
                                                 filterNames = options['TnPHLTProbeFilters'],
                                                 inputs      = cms.InputTag("goodPhotons"),
                                                 bits        = cms.InputTag('TriggerResults::'+options['HLTProcessName']),
                                                 objects     = cms.InputTag('selectedPatTrigger'),
                                                 dR          = cms.double(0.3),
                                                 isAND       = cms.bool(True)
                                                 )


    process.goodSuperClustersHLT = cms.EDProducer("RecoEcalCandidateTriggerCandProducer",
                                                  filterNames  = cms.vstring(options['TnPHLTProbeFilters']),
                                                  inputs       = cms.InputTag("goodSuperClusters"),
                                                  bits         = cms.InputTag('TriggerResults::'+options['HLTProcessName']),
                                                  objects      = cms.InputTag('selectedPatTrigger'),
                                                  dR           = cms.double(0.3),
                                                  isAND        = cms.bool(True)
                                                  )


###################################################################
## TnP PAIRS
###################################################################
    
    process.tagTightHLT   = cms.EDProducer("CandViewShallowCloneCombiner",
                                           decay = cms.string("goodElectronsTagHLT@+ goodElectronsProbeMeasureHLT@-"), 
                                           checkCharge = cms.bool(True),
                                           cut = cms.string("60<mass<120"),
                                           )
    
    process.tagTightSC    = cms.EDProducer("CandViewShallowCloneCombiner",
                                           decay = cms.string("goodElectronsTagHLT goodSuperClustersHLT"), 
                                           checkCharge = cms.bool(False),
                                           cut = cms.string("60<mass<120"),
                                           )
    
    process.tagTightEleID = cms.EDProducer("CandViewShallowCloneCombiner",
                                           decay = cms.string("goodElectronsTagHLT@+ goodElectronsProbeHLT@-"), 
                                           checkCharge = cms.bool(True),
                                           cut = cms.string("60<mass<120"),
                                           )
    
    process.tagTightPhoID = cms.EDProducer("CandViewShallowCloneCombiner",
                                           decay = cms.string("goodElectronsTagHLT goodPhotonsProbeHLT"), 
                                           checkCharge = cms.bool(False),
                                           cut = cms.string("60<mass<120"),
                                           )
    
def setSequences(process, options):
###################################################################
## SEQUENCES
###################################################################
    process.tag_sequence = cms.Sequence(
        process.goodElectrons                    +
        process.egmGsfElectronIDSequence         +
        process.goodElectronsTAGCutBasedLoose    +
        process.goodElectronsTAGCutBasedTight    +
        process.goodElectronsTagHLT
        )

    process.ele_sequence = cms.Sequence(
        process.goodElectronsPROBECutBasedVeto   +
        process.goodElectronsPROBECutBasedLoose  +
        process.goodElectronsPROBECutBasedMedium +
        process.goodElectronsPROBECutBasedTight  +
        process.goodElectronsProbeHLT
        )

    process.hlt_sequence = cms.Sequence(
        process.goodElectronsProbeMeasureHLT     +
        process.goodElectronsMeasureHLT
        )

    process.pho_sequence = cms.Sequence(
        process.goodPhotons                    +
        process.egmPhotonIDSequence            +
        process.photonIDValueMapProducer       +
        process.goodPhotonsPROBECutBasedLoose  +
        process.goodPhotonsPROBECutBasedMedium +
        process.goodPhotonsPROBECutBasedTight  +
        process.goodPhotonsPROBEMVA            +
        process.goodPhotonsProbeHLT
        )

    process.sc_sequence = cms.Sequence( 
        process.superClusterCands +
        process.goodSuperClusters +
        process.goodSuperClustersHLT +
        process.GsfMatchedSuperClusterCands
        )
