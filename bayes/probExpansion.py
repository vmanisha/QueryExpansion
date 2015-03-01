# -*- coding: utf-8 -*-
from entity.category.coOcManager import CoOcManager
from entity.category.coOccurrence import CoOccurrence
from bayes.objCoOccurrence import ObjCoOccurrence
from entity.ranker import Ranker
from entity.dexter import Dexter
from queryLog import hasAlpha, getSessionWithNL
from utils import stopSet
import sys
import math

class ProbExpansion:
	
	#term-term co-occurence
	#term - entity co-occurence
	#entity - category co-occurence
	
	def __init__(self,ttMan,teMan,ecMan, dextr,rnker):
		self.termTermManager = ttMan
		self.termEntityManager = teMan
		self.entityCatManager = ecMan
		self.ranker = rnker
		self.dexter = dextr
		
	def updateTermEntFreq(self, entity,query):
		self.termEntityManager.updateStats(entity,query)
	
	def updateEntityCatFreq(self,entity, catList):
		self.entityCatManager.updateStats(entity, catList)
	
	def writeStats(self,fileName1, fileName2):
		self.termEntityManager.writeStats(fileName1)
		self.entityCatManager.writeStats(fileName2)
	
	def expandText(self, query, limit):
		#get the entities
		spotDict = self.dexter.tagText(query)
		#P(c)
		pC = 1.0/self.entityCatManager.getUniqueTermCount()
	
		termList = self.termTermManager.getUniqueTerms()
		
		pEC = {}
		for entity, edict in spotDict.iteritems():
			catList = edict['cat'].split()
			#SUM(P(e|c)P(c))
			pEC[entity] = 0.0
			for cat in catList:
				#SUM(P(e|c)P(c))
				#print entity, cat, self.entityCatManager.getProb(cat, entity)
				pEC[entity] += pC * self.entityCatManager.getProb(cat, entity)
			#print entity, 'pEC', pEC[entity]
		
		termScore = {}
		
		for	term in termList:		
			pTE = 0.0
			termScore[term] = 0.0
			#P(t|e)
			for entity, score in pEC.iteritems():
				repQuery = query.replace(entity,'')
				pTT = 0.0000001
				qsplit = repQuery.split()
				for entry in qsplit:
					if len(entry) > 2 and entry not in stopSet and hasAlpha(entry):
						pTT += self.termTermManager.getProb(term, entry)
						#print term, entry, self.termTermManager.getProb(term, entry)
				pTE = self.termEntityManager.getProb(entity, term)
				if pTE == 0.0:
					pTE = 0.0000001
				#print term, entity, pTE, score, pTT
				termScore[term]+= pTE*score*pTT
			if termScore[term] < 0.0 or termScore[term] > 0.0:
				termScore[term] = math.log(termScore[term])
			
		resultSet = {}
		for ttuple in sorted(termScore.items(),reverse=True, key = lambda x : x[1]):
			#print ttuple,
			resultSet[ttuple[0]] = ttuple[1]
			if len(resultSet) == limit+10:	
				break
		#print
		#print query, '\t', resultSet
		return resultSet
		

def main(argv):
	
	ttCoOc = CoOccurrence()
	teCoOc = ObjCoOccurrence()
	ecCoOc = ObjCoOccurrence()
	
	termEntMan = CoOcManager(argv[1],teCoOc,'\t')
	entCatMan = CoOcManager(argv[2],ecCoOc,'\t' )
	termTermMan = CoOcManager(argv[3], ttCoOc, ' ')
	
	ipaddress = 'localhost'
	#dexter object
	tagURL = 'http://'+ipaddress+':8080/rest/annotate'
	catURL = 'http://'+ipaddress+':8080/rest/graph/get-entity-categories'
	dexter = Dexter(tagURL,catURL)
	et = ProbExpansion(termTermMan, termEntMan, entCatMan, dexter, Ranker())
	
	for i, session in getSessionWithNL(argv[4]):
		query = session[0]
		terms = et.expandText(query,50)
		print i, '\t',query,'\t', terms

if __name__ == '__main__':
	main(sys.argv)