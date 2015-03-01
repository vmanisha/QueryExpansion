# -*- coding: utf-8 -*-

from utils import get_cosine, getDictFromSet,stopSet;
from queryLog import hasAlpha;

from nltk import stem;
from utils import combineDict;
import math


'''
Get categories for entities
Get the terms for each category
Rank terms
'''

class CatThesExpansion:
	
	def __init__(self,dext,categoryM,rnker, catCoM, wordM):
		self.catManager = categoryM
		self.dexter = dext
		self.ranker = rnker
		self.catCoMan = catCoM
		self.porter = stem.porter.PorterStemmer()
		self.wordMan = wordM;
		
	def expandText(self,text,clickText, topC,limit):
		entStatus = False;
		spotDict = self.dexter.tagText(text)
		if len(spotDict) == 0:
			print 'No Entity found\t', text, spotDict
		else:
			print 'Tagged\t',text,'\t', spotDict
			entStatus = True;
		qsplit = text.split()
		termSet = set(qsplit)
		termDict = getDictFromSet(qsplit)
		catList = self.scoreCategories(termSet,termDict,clickText,spotDict,topC)
		terms = self.aggregateTerms(text,termSet,catList)
		#terms = self.aggregateTermsFromTopics(text,spotDict,topC)
		scoredTerms = self.ranker.getTopKWithFilter(terms,limit,limit+50)
		return entStatus, scoredTerms
		
	def expandTextWithSubClusters(self, qText,clickText,topC, limit):
		
		spotDict = self.dexter.tagText(qText);
		entStatus = False;
		if (not spotDict) or len(spotDict) == 0:
			print 'No Entitity Found\t', qText;
		else:
			print 'Tagged ',qText, '\t', spotDict;
			entStatus = True;
			
		qSplit = qText.split();
		qSet = set(qSplit);
		qDict = getDictFromSet(qSplit);
		#Rank cateogories
		catList = self.scoreCategories(qSet,qDict,clickText, spotDict,topC);
		print qText,'CatList ',catList;
		#Rank subclusters
		termSet = self.aggregateTermsFromSubclusters(qSet,catList, limit+100);
		#print len(termSet);
		#Rank terms
		scoredTerms = self.ranker.getTopKWithFilter(termSet,limit,limit+50)
		return entStatus, scoredTerms
		#send results
	
	
	def expandTextWithStepAndSubcluster(self, qText,clickText,topC, limit1, limit2, step):
		spotDict = self.dexter.tagText(qText);
		entStatus = False;
		scoredTerms = {};
		if len(spotDict) == 0:
			print 'No Entitity Found\t', qText;
		else:
			print 'Tagged ',qText, '\t', spotDict;
			entStatus = True;
		qSplit = qText.split();
		qSet = set(qSplit);
		qDict = getDictFromSet(qSplit);
		#Rank cateogories
		print 'Click Text ', clickText;
		catList = self.scoreCategories(qSet,qDict,clickText,spotDict,topC);
		print qText,'CatList ',catList;
		#Rank subclusters
		terms= self.aggregateTermsFromSubclusters(qSet,catList, limit2+400);
		print terms;
		#print 'total term set',len(termSet);
		
		for i in xrange(limit1,limit2,step):
			if i == 0:
				scoredTerms[i] = self.ranker.getTopK(terms,i+1);#getTopKWithFilter(terms,i+1,i+50)
			else:
				scoredTerms[i] = self.ranker.getTopK(terms,i);#getTopKWithFilter(terms,i,i+50)
		
		return entStatus, scoredTerms;
		
			#Rank terms
			
	def expandTextWithStep(self,text,clickText,topC,limit1,limit2,step):
		
		spotDict = self.dexter.tagText(text)
		entStatus = False;
		if len(spotDict) == 0:
			print 'No Entity found\t', text, spotDict
		else:
			print 'Tagged\t',text,'\t', spotDict
			entStatus= True;
		qsplit = text.split()
		termSet = set(qsplit)
		termDict = getDictFromSet(qsplit)
		catList = self.scoreCategories(termSet,termDict,clickText,spotDict,topC)
		terms = self.aggregateTerms(text,termSet,catList)
		#terms = self.aggregateTermsFromTopics(text,spotDict,topC)
		scoredTerms = {}
		for i in xrange(limit1,limit2,step):
			if i == 0:
				scoredTerms[i] = self.ranker.getTopKWithFilter(terms,i+1,i+50)
			else:
				scoredTerms[i] = self.ranker.getTopKWithFilter(terms,i,i+50)
				
		return entStatus, scoredTerms
		
	
	def getTopSubclusters(self, qText, clickText,topC, limit):
		spotDict = self.dexter.tagText(qText);
		entStatus = False;
		if len(spotDict) == 0:
			print 'No Entitity Found\t', qText;
		else:
			print 'Tagged ',qText, '\t', spotDict;
			entStatus = True;
		qSplit = qText.split();
		qSet = set(qSplit);
		qDict = getDictFromSet(qSplit);
		#Rank cateogories
		#catList = self.scoreCategories(qSet,qDict,clickText,spotDict,topC);
		#print qText,'CatList ',catList;
		#Rank subclusters
		topClusters = None; #self.rankClusters(qSet,catList, limit);
		return entStatus, topClusters;
		
	def aggregateTerms(self,query,querySet,entityCatScore):
		#max -- Take the terms from max category
		stemSet = [self.porter.stem(entry.strip()) for entry in querySet];
		termDict = {}
		for entity , catScoreList in entityCatScore.iteritems():
			for catS in catScoreList:
				#print '\n',catS
				catTotal  = self.catManager.getTotalPhraseCount(catS[0])
				for phrase, count in  self.catManager.getPhrases(catS[0]):
					if phrase not in query:
						coOcScore = self.getCoOcScore(phrase,stemSet)
						#print phrase, coOcScore, count, catS[1],catTotal
						termDict[phrase] = termDict.setdefault(phrase,0.0) + (count/catTotal)\
						*(coOcScore);#+0.6*entScore)/2;
											#(0.75*(count*catS[1])+0.25*(coOcScore*catS[1]))
			
		return termDict
	
	def aggregateTermsForCategory(self,query,querySet,category):
		termDict = {}
		stemSet = [self.porter.stem(entry.strip()) for entry in querySet];
		for phrase, count in  self.catManager.getPhrases(category):
			if phrase not in query:
				coOcScore = self.getCoOcScore(phrase,stemSet);
				#print phrase, coOcScore, count, catS[1],catTotal
				termDict[phrase] = termDict.setdefault(phrase,0.0) + count*coOcScore
				#(0.75*(count*catS[1])+0.25*(coOcScore*catS[1]))
			
		return termDict
		
	
	def scoreCategories(self,querySet,queryDict,clickText,spotDict, k):
		entityCatScore = {}
		
		cDict = getDictFromSet(clickText.split());
		combDict= combineDict(cDict, queryDict);
		cSet = set(cDict.keys());
		print 'cDict ', cDict, ' combDict ', combDict;
		for entry, eDict in spotDict.iteritems():
			catList = eDict['cat'].lower().split()
			queryTerms = (querySet | cSet);
			queryTerms = queryTerms - set([entry]);
			catScore = {}
			for cat in catList:
				pset =  self.catManager.getPhraseSet(cat)	#unique phrases in cat
				if len(pset) == 0:
					print 'CAT NO PHRASE ', cat;
				qInt = pset & queryTerms	#no of query terms cat contains
				score = 0.0
				for iphrase in qInt:
					score +=  self.catManager.getPhraseProb(cat,iphrase)
				if len(queryTerms) > 0:
					score *= (1.0*len(qInt))/len(queryTerms)
				
				#cosine score
				cVector = self.catManager.getVector(cat)
				cscore = get_cosine(combDict, cVector)
			
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
		stemSet = [self.porter.stem(entry.strip()) for entry in querySet];
		#entSet = entityCatScore.keys();
		
		for entity, catScoreList in entityCatScore.items():
			#get the subclusters
			for catS in catScoreList:
				phraseCount = self.catManager.getTotalPhraseCount(catS[0]);
				for centry  in self.catManager.getSubclusters(catS[0]):
					cid= centry[0];
					cluster = centry[1];
					key = catS[0]+'_'+str(cid);
					phraseScore = {};
					for phrase, count in cluster.items():
						if phrase not in querySet:
							coOcScore = self.getCoOcScore(phrase,stemSet);
							#entScore = self.getEntScore(phrase,entSet);
							#print phrase, coOcScore, count, catS[1]
							phraseScore[phrase] = coOcScore*(count / phraseCount );
							
					#phraseScore = normalize(phraseScore);
					#for phrase,count in cluster.items():
					#	phraseScore[phrase] *= count;
					if len(phraseScore) > 0:
						sScore[key] = sum(phraseScore.values())/len(phraseScore);
						sPhrases[key] = phraseScore;
					#print key, sum(phraseScore.values()),sScore[key], len(phraseScore);
				
		#sort the subclusters with scores, and combine the phrases
		sortS = sorted(sScore.items(), reverse=True, key = lambda x: x[1]);
		toReturn = [];
		covered = {};
		i = 0;
		
		for entry in sortS:
			print entry[0],	sPhrases[entry[0]].keys(), entry[1];
			#print 'phrases to score ',len(sPhrases[entry[0]]);
			pSort = sorted(sPhrases[entry[0]].items(), reverse = True, key = lambda x:x[1]);
			for pentry in pSort:
				phrase = pentry[0];
				score = pentry[1];
				if phrase not in querySet:
					if phrase not in covered:
						covered[phrase] = score*entry[1];
					else:
						covered[phrase] += score*entry[1];
						i+=1;
					#else:						
					#	toReturn[covered[phrase]][1] += score;

					#	if score > 0:
					#		toReturn.append((phrase,score));#*entry[1] ;
					
					
		toReturn = sorted(covered.items(),reverse=True,key = lambda x : x[1]);				
		#print 'Returning terms ', len(toReturn);
		if limit > len(toReturn):
			limit = len(toReturn);
			
		return toReturn[:limit];
		
	def rankClusters(self, querySet,entityCatScore, limit):	
		sScore = {};
		sPhrases = {};
		stemSet = [self.porter.stem(entry.strip()) for entry in querySet];
		#entSet = entityCatScore.keys();
		for entity, catScoreList in entityCatScore.items():
			#get the subclusters
			for catS in catScoreList:
				phraseCount = self.catManager.getTotalPhraseCount(catS[0]);
				for centry  in self.catManager.getSubclusters(catS[0]):
					cid= centry[0];
					cluster = centry[1];
					key = catS[0]+'_'+str(cid);
					phraseScore = {};
					for phrase, count in cluster.items():
						if phrase not in querySet:
							coOcScore = self.getCoOcScore(phrase,stemSet);
							#entScore = self.getEntScore(phrase,entSet);
							#print phrase, coOcScore, count, catS[1]
							#phraseScore[phrase] = coOcScore*(count / phraseCount );
							phraseScore[phrase] = coOcScore*(count / phraseCount );
							
					#phraseScore = normalize(phraseScore);
					#for phrase,count in cluster.items():
					#	phraseScore[phrase] *= count;
					sScore[key] = sum(phraseScore.values())/len(phraseScore);
					sPhrases[key] = phraseScore;
					#print key, sum(phraseScore.values()),sScore[key], len(phraseScore);
				
		#sort the subclusters with scores, and combine the phrases
		sortS = sorted(sScore.items(), reverse=True, key = lambda x: x[1]);
		toReturn = {};
		for entry in sortS:
			if len(toReturn) > limit:
				break;
			pSort = sorted(sPhrases[entry[0]].items(), reverse = True, key = lambda x:x[1]);
			toReturn[entry[0]] = [pentry[0] for pentry in pSort];
		
		return toReturn;
			
	
	def getEntScore(self,phrase,entSet):
		#get word Manager
		total = 0.0;
		for entry in entSet:
			total+=self.wordMan.getEntProb(phrase, entry);
		
		return total/len(entSet);	
		
	def getCoOcScore(self,phrase,stemSet):
		total = 0.0
		tCount = 0.0
		for qRep in stemSet:
			#stem the term
			#get PMI
			if len(qRep) > 2 and qRep not in stopSet and hasAlpha(qRep):
				#total += self.catCoMan.getPMI(phrase, qRep,10)
				#c1, c2 = self.catCoMan.getCoOcCount(phrase, qRep);
				c1 = self.catCoMan.getProb(phrase,qRep,50);
				#if c1 != c2:
				#	print ':O CoOcc count diff ',phrase, qRep, c1, c2;
				#total+= c1;
				if c1 > 0:
					total+= c1;
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
