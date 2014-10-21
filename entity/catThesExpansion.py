# -*- coding: utf-8 -*-

from utils import get_cosine, getDictFromSet,stopSet;
from queryLog import hasAlpha;

from nltk import stem;
from utils import normalize;

'''
Import the query Index
Search queries
Get categories for entities
Get the terms for each category
Rank terms
'''

class CatThesExpansion:
	
	def __init__(self,dext,categoryM,rnker, catCoM):
		self.catManager = categoryM
		self.dexter = dext
		self.ranker = rnker
		self.catCoMan = catCoM
		self.porter = stem.porter.PorterStemmer()
				
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
		terms = self.aggregateTerms(text,termSet,catList)
		#terms = self.aggregateTermsFromTopics(text,spotDict,topC)
		scoredTerms = self.ranker.getTopKWithFilter(terms,limit,limit+50)
		return scoredTerms
		
	def expandTextWithSubClusters(self, qText,cDocText, topC, limit):
		
		spotDict = self.dexter.tagText(qText);
		
		if len(spotDict) == 0:
			print 'No Entitity Found\t', qText;
		else:
			qSplit = qText.split();
			qSet = set(qSplit);
			qDict = getDictFromSet(qSplit);
			#Rank cateogories
			catList = self.scoreCategories(qSet,qDict,spotDict,topC);
			print qText,'CatList ',catList;
			#Rank subclusters
			termSet = self.aggregateTermsFromSubclusters(qSet,catList, limit+100);
			print len(termSet);
			#Rank terms
			scoredTerms = self.ranker.getTopKWithFilter(termSet,limit,limit+50)
			return scoredTerms
			#send results
		return {};
			
	def expandTextWithStepAndSubcluster(self, qText,cDocText, topC, limit1, limit2, step):
		spotDict = self.dexter.tagText(qText);
		scoredTerms = {};
		if len(spotDict) == 0:
			print 'No Entitity Found\t', qText;
		else:
			qSplit = qText.split();
			qSet = set(qSplit);
			qDict = getDictFromSet(qSplit);
			#Rank cateogories
			catList = self.scoreCategories(qSet,qDict,spotDict,topC);
			print qText,'CatList ',catList;
			#Rank subclusters
			termSet = self.aggregateTermsFromSubclusters(qSet,catList, limit2+50);
			print len(termSet);
			
			for i in xrange(limit1,limit2,step):
				if i == 0:
					scoredTerms[i] = self.ranker.getTopKWithFilter(termSet,i+1,i+50);
				else:
					scoredTerms[i] = self.ranker.getTopKWithFilter(termSet,i,i+50);
				
		return scoredTerms;
		
			#Rank terms
			
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
		terms = self.aggregateTerms(text,termSet,catList)
		#terms = self.aggregateTermsFromTopics(text,spotDict,topC)
		scoredTerms = {}
		for i in xrange(limit1,limit2,step):
			if i == 0:
				scoredTerms[i] = self.ranker.getTopKWithFilter(terms,i+1,i+50)
			else:
				scoredTerms[i] = self.ranker.getTopKWithFilter(terms,i,i+50)
				
		return scoredTerms
		
	def aggregateTermsFromTopics(self,query,spotDict,k):
		terms = {}

		for entry, eDict in spotDict.iteritems():
			catList = eDict['cat'].lower().split()
			catScore = {}
			for cat  in catList:
				topic, score = self.catManager.getSim(query,cat)
				catScore[cat] = score
				
			sortedScore = sorted(catScore.items(), reverse = True, key = lambda x : x[1])
			if k == 1000 or k > len(sortedScore):
				k = len(sortedScore)
			
			for catS in sortedScore[:k]:	
				string = self.catManager.expandSet(query, catS[0])
				print 'TOP EXP ', query, cat, string
				split = string.split(' + ')
				for wentry in split:
					try:
						wscore = float(wentry[:wentry.find('*')])
						word = wentry[wentry.find('*')+1:]
						if word not in query and wscore > 0.01:
							word = self.porter.stem(word)
							terms[word] = terms.setdefault(word, 1.0) + wscore*catS[1]
					except Exception as ex:
						print wentry, 'cant parse'
		
		return terms	
	
	def aggregateTerms(self,query,querySet,entityCatScore):
		#max -- Take the terms from max category
		termDict = {}
		for entity , catScoreList in entityCatScore.iteritems():
			for catS in catScoreList:
				#print '\n',catS
				#catTotal  = self.catManager.getTotalPhraseCount(catS[0])
				for phrase, count in  self.catManager.getPhrases(catS[0]):
					if phrase not in query:
						coOcScore = self.getCoOcScore(phrase,querySet)
						#print phrase, coOcScore, count, catS[1],catTotal
						termDict[phrase] = termDict.setdefault(phrase,0.0) + count*coOcScore
											#(0.75*(count*catS[1])+0.25*(coOcScore*catS[1]))
			
		return termDict
	
	def aggregateTermsForCategory(self,query,querySet,category):
		termDict = {}
		for phrase, count in  self.catManager.getPhrases(category):
			if phrase not in query:
				coOcScore = self.getCoOcScore(phrase,querySet)
				#print phrase, coOcScore, count, catS[1],catTotal
				termDict[phrase] = termDict.setdefault(phrase,0.0) + count*coOcScore
				#(0.75*(count*catS[1])+0.25*(coOcScore*catS[1]))
			
		return termDict
		
	
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
	
	def aggregateTermsFromSubclusters(self,querySet,entityCatScore, limit):
		sScore = {};
		sPhrases = {};
					
		for entity, catScoreList in entityCatScore.items():
			#get the subclusters
			for catS in catScoreList:
				print catS[0];
				for centry  in self.catManager.getSubclusters(catS[0]):
					cid= centry[0];
					cluster = centry[1];
					key = catS[0]+'_'+str(cid);
					phraseScore = {};
					for phrase, count in cluster.items():
						coOcScore = self.getCoOcScore(phrase,querySet)
						#print phrase, coOcScore, count, catS[1],catTotal
						phraseScore[phrase] = coOcScore;
					phraseScore = normalize(phraseScore);
					for phrase,count in cluster.items():
						phraseScore[phrase] *= count;
					sScore[key] = sum(phraseScore.values());
					sPhrases[key] = phraseScore;
					print key, sum(phraseScore.values()),phraseScore ;
				
		#sort the subclusters with scores, and combine the phrases
		sortS = sorted(sScore.items(), reverse=True, key = lambda x: x[1]);
		toReturn = {};
		for entry in sortS:
			if len(toReturn) > limit:
				break;
			for phrase, count in sPhrases[entry[0]]:
				if phrase not in toReturn:
					toReturn[phrase] = 0.0
				toReturn[phrase]+=count;
				
		return toReturn;
		
			
	def getCoOcScore(self,phrase,querySet):
		total = 0.0
		tCount = 0.0
		for entry in querySet:
			#stem the term
			qRep = self.porter.stem(entry.strip())
			#get PMI
			if len(qRep) > 2 and qRep not in stopSet and hasAlpha(qRep):
				total += self.catCoMan.getPMI(phrase, qRep,10)
				tCount += 1.0
		if tCount > 0:
			return total/tCount
		return 0
			
	
	def getTopEntityCategoryTerms(self,query,topC,limit):
		entCatTerms = {}
		spotDict = self.dexter.tagText(query)
		qsplit = query.split()
		termSet = set(qsplit)
		termDict = getDictFromSet(qsplit)
		catList = self.scoreCategories(termSet,termDict,spotDict,topC)
		for entity, cats in catList.iteritems():
			entCatTerms[entity] = {}
			for cat, score in cats:
				terms = self.aggregateTermsForCategory(query,termSet,cat)
				entCatTerms[entity][cat] = self.ranker.getTopKWithFilter(terms,limit,limit+50)
		return entCatTerms
