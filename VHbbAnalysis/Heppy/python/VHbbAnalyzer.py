from PhysicsTools.Heppy.analyzers.core.Analyzer import Analyzer
from PhysicsTools.Heppy.analyzers.core.AutoHandle import AutoHandle
from PhysicsTools.HeppyCore.utils.deltar import deltaR
from math import *
import itertools
import ROOT
class VHbbAnalyzer( Analyzer ):
    '''Analyze VH events
    '''

    def declareHandles(self):
        super(VHbbAnalyzer, self).declareHandles()
#        self.handles['pfCands'] =  AutoHandle( 'packedPFCandidates', 'std::vector<pat::PackedCandidate>' )
#        self.handles['jee'] =  AutoHandle( 'ak5PFJetsCHS', 'std::vector<reco::PFJet>' )

    def beginLoop(self,setup):
        super(VHbbAnalyzer,self).beginLoop(setup)
        if "outputfile" in setup.services :
            setup.services["outputfile"].file.cd()
            self.inputCounter = ROOT.TH1F("Count","Count",1,0,2)
 
    def makeJets(self,event):
	inputs=ROOT.std.vector(ROOT.heppy.ReclusterJets.LorentzVector)()
        event.pfCands = list(self.handles['pfCands'].product())
	for pf in event.pfCands :
	     if pf.fromPV() :
		inputs.push_back(pf.p4())
	clusterizer=ROOT.heppy.ReclusterJets(inputs,-1,0.1)
	jets = clusterizer.getGrouping(30)
        #event.jee = list(self.handles['jee'].product())
	#for j in list(jets)[0:3]:
	#	print j.pt(),
	#print " "
    def doFakeMET(self,event):
	#fake MET from Zmumu
	event.fakeMET = ROOT.reco.Particle.LorentzVector(0.,0.,0.,0.)
	event.fakeMET.sumet = 0
	if event.Vtype == 0 :
		event.fakeMET=event.met.p4() + event.V
                event.fakeMET.sumet = event.met.sumEt() - event.V.pt()

    def doHiggsHighCSV(self,event) :
        #leading csv interpretation
        event.hJetsCSV=sorted(event.jetsForHiggs,key = lambda jet : jet.btag('combinedInclusiveSecondaryVertexV2BJetTags'), reverse=True)[0:2]
        event.aJetsCSV = [x for x in event.cleanJets if x not in event.hJetsCSV]
        event.hjidxCSV=[event.cleanJets.index(x) for x in event.hJetsCSV ]
        event.ajidxCSV=[event.cleanJets.index(x) for x in event.aJetsCSV ]
        event.aJetsCSV+=event.cleanJetsFwd
        event.HCSV = event.hJetsCSV[0].p4()+event.hJetsCSV[1].p4()

    def doHiggsHighPt(self,event) :
        #highest pair interpretations
        event.hJets=list(max(itertools.combinations(event.jetsForHiggs,2), key = lambda x : (x[0].p4()+x[1].p4()).pt() ))
        event.aJets = [x for x in event.cleanJets if x not in event.hJets]
        event.hjidx=[event.cleanJets.index(x) for x in event.hJets ]
        event.ajidx=[event.cleanJets.index(x) for x in event.aJets ]
        event.aJets+=event.cleanJetsFwd
        hJetsByCSV = sorted(event.hJets , key =  lambda jet : jet.btag('combinedInclusiveSecondaryVertexV2BJetTags'), reverse=True)
        event.hjidxDiJetPtByCSV = [event.cleanJets.index(x) for x in hJetsByCSV]
        event.H = event.hJets[0].p4()+event.hJets[1].p4()


    def doHiggs3cj(self,event) :
        event.H3cj = ROOT.reco.Particle.LorentzVector(0.,0.,0.,0.)
        event.hJets3cj = []
        event.aJets3cj = []
	event.hjidx3cj = []         
	event.ajidx3cj = []         
        event.minDr3 = 0         
        #3 jets interpretations, for the closest 3 central jets
        if (len(event.jetsForHiggs) > 2 and event.jetsForHiggs[2] > 15.): 
           aJetsForHiggs = [x for x in event.jetsForHiggs if x not in event.hJets]
           j3=min(aJetsForHiggs, key = lambda x : min( deltaR( x.eta(), x.phi(), event.hJets[0].eta(), event.hJets[0].phi()),deltaR( x.eta(), x.phi(), event.hJets[1].eta(), event.hJets[1].phi() ) ) )
           event.hJets3cj=event.hJets
           event.hJets3cj.append(j3)
#          event.hJets3cj=list(min(itertools.combinations(event.jetsForHiggs,3), key = lambda x : ( x[2]>15 and (deltaR( x[0].eta(), x[0].phi(), x[2].eta(), x[2].phi()) +  deltaR( x[1].eta(), x[1].phi(), x[2].eta(), x[2].phi()) ) ) ))
           event.aJets3cj = [x for x in event.cleanJets if x not in event.hJets3cj]
           event.hjidx3cj=[event.cleanJets.index(x) for x in event.hJets3cj ]
           event.ajidx3cj=[event.cleanJets.index(x) for x in event.aJets3cj ]
           event.aJets3cj+=event.cleanJetsFwd
           event.H3cj = event.hJets3cj[0].p4()+event.hJets3cj[1].p4()+event.hJets3cj[2].p4()
           event.minDr3 = min(deltaR( event.hJets3cj[0].eta(), event.hJets3cj[0].phi(), event.hJets3cj[2].eta(), event.hJets3cj[2].phi()) ,  deltaR( event.hJets3cj[1].eta(), event.hJets3cj[1].phi(), event.hJets3cj[2].eta(), event.hJets3cj[2].phi()))  


    def classifyMCEvent(self,event):
        if self.cfg_comp.isMC:
		event.VtypeSim = -1
		if len(event.genvbosons) == 1:
			# ZtoLL events, same flavour leptons
			if event.genvbosons[0].pdgId()==23 and event.genvbosons[0].numberOfDaughters()>1 and abs(event.genvbosons[0].daughter(0).pdgId()) == abs(event.genvbosons[0].daughter(1).pdgId()):
				if abs(event.genvbosons[0].daughter(0).pdgId()) == 11:
 					#Ztoee
					event.VtypeSim = 1
				if abs(event.genvbosons[0].daughter(0).pdgId()) == 13:
 					#ZtoMuMu
					event.VtypeSim = 0
				if abs(event.genvbosons[0].daughter(0).pdgId()) == 15:
 					#ZtoTauTau
					event.VtypeSim = 5
				if abs(event.genvbosons[0].daughter(0).pdgId()) in [12,14,16]:
					event.VtypeSim = 4
			#WtoLNu events	
			if abs(event.genvbosons[0].pdgId())==24 and event.genvbosons[0].numberOfDaughters()==2:
				if abs(event.genvbosons[0].daughter(0).pdgId()) == 11 and abs(event.genvbosons[0].daughter(1).pdgId()) == 12:
					#WtoEleNu_e
					event.VtypeSim = 3
			if abs(event.genvbosons[0].daughter(0).pdgId()) == 13 and abs(event.genvbosons[0].daughter(1).pdgId()) == 14:
					#WtoMuNu_mu
					event.VtypeSim = 2
			#to be added: WtoTauNu

		if len(event.genvbosons)>1:
			#print 'more than one W/Zbosons?'
			event.VtypeSim = -2
#		if event.VtypeSim == -1:
#			print '===================================='
#			print ' --------- Debug VtypeSim -1 --------'
#			print '# genVbosons: ',len(event.genvbosons), '| #daughters ', event.genvbosons[0].numberOfDaughters()
#			for i in xrange (0, event.genvbosons[0].numberOfDaughters() ) :
#				print 'daughter ',i ,'| pdgId', event.genvbosons[0].daughter(i).pdgId()	

    def classifyEvent(self,event):
	#assign events to analysis (Vtype)
	#enum CandidateType{Zmumu, Zee, Wmun, Wen, Znn,  Zemu, Ztaumu, Ztaue, Wtaun, Ztautau, Zbb, UNKNOWN};
	event.Vtype=-1
        nLep=len(event.selectedLeptons)	
	event.vLeptons=[]
	#WH requires exactly one selected lepton
	wElectrons=[x for x in event.selectedElectrons if self.cfg_ana.wEleSelection(x) ]
	wMuons=[x for x in event.selectedMuons if self.cfg_ana.wMuSelection(x) ]
	zElectrons=[x for x in event.selectedElectrons if self.cfg_ana.zEleSelection(x) ]
	zMuons=[x for x in event.selectedMuons if self.cfg_ana.zMuSelection(x) ]

        zMuons.sort(key=lambda x:x.pt(),reverse=True)
        zElectrons.sort(key=lambda x:x.pt(),reverse=True)
	if len(zMuons) >=  2 :
#              print  zMuons[0].pt()
              if zMuons[0].pt() > self.cfg_ana.zLeadingMuPt :
		    for i in xrange(1,len(zMuons)):
			if zMuons[0].charge()*zMuons[i].charge()<0 :
	                      event.Vtype = 0
			      event.vLeptons =[zMuons[0],zMuons[i]]
			      break
	elif len(zElectrons) >=  2 :
#	    for i in zElectrons[0].electronIDs()  :
#			print i.first,i.second
              if zElectrons[0].pt() > self.cfg_ana.zLeadingElePt :
		    for i in xrange(1,len(zElectrons)):
			if zElectrons[0].charge()*zElectrons[i].charge()<0 :
	                      event.Vtype = 1
			      event.vLeptons =[zElectrons[0],zElectrons[i]]
			      break
	elif len(wElectrons) + len(wMuons) == 1: 
		if abs(event.selectedLeptons[0].pdgId())==13 :
			event.Vtype = 2
			event.vLeptons =event.selectedLeptons
		if abs(event.selectedLeptons[0].pdgId())==11 :
			event.Vtype = 3
			event.vLeptons =event.selectedLeptons
	else :
		event.Vtype = 4	
		#apply MET cut
		if  event.met.pt() < 50 :
			 return False


	event.V=sum(map(lambda x:x.p4(), event.vLeptons),ROOT.reco.Particle.LorentzVector(0.,0.,0.,0.))
	if event.Vtype > 1 :	
		event.V+=ROOT.reco.Particle.LorentzVector(event.met.p4().x(),event.met.p4().y(),0,event.met.p4().pt())
        if event.V.Et() > event.V.pt() :
           event.V.goodMt = sqrt(event.V.Et()**2-event.V.pt()**2)
        else :
           event.V.goodMt = -sqrt(-event.V.Et()**2+event.V.pt()**2)

	event.aLeptons = [x for x in event.inclusiveLeptons if x not in event.vLeptons]

	return True
    def initOutputs (self,event) : 
        event.hJets = []
        event.aJets = []
        event.hjidx = []
        event.ajidx = []
        event.hJetsCSV = []
        event.aJetsCSV = []
        event.hjidxCSV = []
        event.ajidxCSV = []
        event.hJets3cj = []
        event.aJets3cj = []
        event.hjidx3cj = []
        event.ajidx3cj = []
        event.aLeptons = []
        event.vLeptons = []
        event.H = ROOT.reco.Particle.LorentzVector(0.,0.,0.,0.)
        event.HCSV = ROOT.reco.Particle.LorentzVector(0.,0.,0.,0.)
        event.H3cj = ROOT.reco.Particle.LorentzVector(0.,0.,0.,0.)
        event.V = ROOT.reco.Particle.LorentzVector(0.,0.,0.,0.)
        event.minDr3=-1
        event.V.goodMt=0
        event.hjidxDiJetPtByCSV = []

    def process(self, event):
        self.readCollections( event.input )
        self.inputCounter.Fill(1)
        self.initOutputs(event)
#	event.pfCands = self.handles['pfCands'].product()
# 	met = event.met
	
   	self.classifyMCEvent(event)
	passClassify = self.classifyEvent(event) 
	self.doFakeMET(event)

	#substructure threshold, make configurable
	ssTrheshold = 200.
	# filter events with less than 2 jets with pt 20
        event.jetsForHiggs = [x for x in event.cleanJets if self.cfg_ana.higgsJetsPreSelection(x) ]
	if not   len(event.jetsForHiggs) >= 2 : # and event.jetsForHiggs[1] > 20.) : # or(len(event.cleanJets) == 1 and event.cleanJets[0] > ssThreshold ) ) :
		return self.cfg_ana.passall
        if not passClassify:
                return self.cfg_ana.passall

	self.doHiggsHighCSV(event)
	self.doHiggsHighPt(event)
        self.doHiggs3cj(event)



    #    event.jee = list(self.handles['jee'].product())
	#for j in list(jets)[0:3]:
	#	print j.pt(),
	#print " "
	
	#to implement
	#if some threshold: 
	#   self.computeSubStructuresStuff()  
   	
	#self.doIVFHiggs()
	#self.computePullAngle()
	#

	#perhaps in different producers:	
	# LHE weights
	# Trigger weights
	# gen level VH specific info
	# add soft jet info to jets
	# PU weights
	# SIM B hadrons information
	# MET corrections (in MET analyzer)
  	# trigger flags
		

#	self.makeJets(event)
        return True




