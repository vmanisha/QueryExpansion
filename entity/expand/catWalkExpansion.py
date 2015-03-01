# -*- coding: utf-8 -*-

from utils import get_cosine, getDictFromSet, stopSet

from nltk import stem
from randomwalk.simpleWalk import SimpleWalk
class CatWalkExpansion:
	
	def __init__(self,dext,categoryM,rnker,vectMan):
		self.catManager = categoryM
		self.dexter = dext
		self.ranker = rnker
		self.porter = stem.porter.PorterStemmer()
		self.vectManager = vectMan
	
	def expandText(self,text,topC,limit):
		spotDict = self.dexter.tagText(text)
		if len(spotDict) == 0:
			print 'No Entity found\t', text, spotDict
		else:
			print 'Tagged\t',text,'\t', spotDict
		qsplit = text.split()
		termSet = set(qsplit)
		termDict = getDictFromSet(qsplit)
		catList = self.scoreCategories(termSet,termDict,spotDict,topC)
		terms = self.aggregateTerms(text,catList)
		scoredTerms = self.ranker.getTopKWithFilter(terms,limit,limit+50)
		return scoredTerms
		
	def expandTextWithStep(self,text,topC,limit1,limit2,step, spotDict = None):
		if not spotDict:
			spotDict = self.dexter.tagText(text)
		if len(spotDict) == 0:
			print 'No Entity found\t', text, spotDict
		else:
			print 'Tagged\t',text,'\t', spotDict
		qsplit = text.split()
		termSet = set(qsplit)
		termDict = getDictFromSet(qsplit)
		catList = self.scoreCategories(termSet,termDict,spotDict,topC)
		terms = self.aggregateTerms(text,catList)
		scoredTerms = {}
		for i in xrange(limit1,limit2,step):
			if i == 0:
				scoredTerms[i] = self.ranker.getTopKWithFilter(terms,i+1,i+50)
			else:
				scoredTerms[i] = self.ranker.getTopKWithFilter(terms,i,i+50)
				
		return scoredTerms
		
	def scoreCategories(self,querySet,queryDict,spotDict, k):
		entityCatScore = {}
		for entry, eDict in spotDict.iteritems():
			catList = eDict['cat'].lower().split()
			queryTerms = querySet - set([entry])
			catScore = {}
			for cat in catList:
				pset =  self.catManager.getPhraseSet(cat)	#unique phrases in cat
				qInt = pset & queryTerms	#no of query terms cat contains
				score = 0.0
				for iphrase in qInt:
					score +=  self.catManager.getPhraseProb(cat,iphrase)
				if len(queryTerms) > 0:
					score *= (1.0*len(qInt))/len(queryTerms)
				
				#cosine score
				cVector = self.catManager.getVector(cat)
				cscore = get_cosine(queryDict, cVector)
			
				#total score
				catScore[cat] = (cscore + score)/2.0
			sortedScore = sorted(catScore.items(), reverse = True, key = lambda x : x[1])
			
			#get terms from all categories
			if k == 1000 or k > len(sortedScore):
				k = len(sortedScore)
			
			entityCatScore[entry] = sortedScore[0:k]
			
			print 'Query\t',querySet, ' Entity\t', entry, entityCatScore[entry]
		return entityCatScore


	def aggregateTerms(self,query,entityCatScore):
		#max -- Take the terms from max category
		#weight = {}
		tList = {}
		for entity , catScoreList in entityCatScore.iteritems():
			for catS in catScoreList:
				pList =  self.catManager.getPhrases(catS[0])
				for x in pList:
					if x[0] not in stopSet and x[0] not in query:
						tList[x[0]] = tList.setdefault(x[0],0.0) + x[1]
		
		
		#termList = list(tList.keys())		
		print 'Term size', len(tList)
		
		
		sTerm = sorted(tList.items(), reverse= True, key = lambda x : x[1])
		sw = SimpleWalk()
		k = len(sTerm) if len(sTerm) < 1000 else 1000
		for i in range(0,k):
			ivect = self.vectManager.getVector(sTerm[i][0])
			if ivect:
				#weight[termList[i]] = {}
				for j in range(i+1,k):
					jvect = self.vectManager.getVector(sTerm[j][0])
					if jvect:
						#print sTerm[i][0], ivect
						#print sTerm[j][0], jvect
						sim = get_cosine(ivect, jvect)
						if sim > 0.001:
							#weight[termList[i]][termList[j]] = sim
							sw.addEdge(sTerm[i][0], sTerm[j][0], sim)		
		
		print 'Done graph, starting walk'
		#return tList
		try :
			results = sw.walk()
			return results
		except :
			return {}
		
