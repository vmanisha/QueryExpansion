# -*- coding: utf-8 -*-

from utils import stopSet,get_cosine, getDictFromSet
from queryLog import hasAlpha
from nltk import stem

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
		terms = self.aggregateTerms(text,spotDict,topC)
		scoredTerms = self.ranker.getTopKWithFilter(terms,limit,limit+50)
		
		return scoredTerms
		
	def expandTextWithStep(self,text,topC,limit1,limit2,step):
		
		spotDict = self.dexter.tagText(text)
		if len(spotDict) == 0:
			print 'No Entity found\t', text, spotDict
		else:
			print 'Tagged\t',text,'\t', spotDict
		qsplit = text.split()
		termSet = set(qsplit)
		termDict = getDictFromSet(qsplit)
		catList = self.scoreCategories(termSet,termDict,spotDict,topC)
		terms = self.aggregateTerms(text,spotDict,topC)
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


	def aggregateTerms(self,query,querySet,entityCatScore):
		#max -- Take the terms from max category
		termList = []
		for entity , catScoreList in entityCatScore.iteritems():
			for catS in catScoreList:
				for phrase, count in  self.catManager.getPhrases(catS[0]):
					
						