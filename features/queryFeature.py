# -*- coding: utf-8 -*-
from utils import get_cosine
import distance
from queryLog import filterStopWordsFromQuery
class QueryFeature:
	
	def __init__(self, query1, ngrams1, qVect, urlDict1, \
	userDict1, sessionDict1, entDict1 = {}, \
	catDict1 = {},typeDict1 = {}):
		self.query = query1
		self.ngrams = ngrams1;
		self.filterNgrams()
		self.queryVector = qVect;
		self.filterQVector()
		self.urlDict = urlDict1;
		self.userDict = userDict1;
		self.sessionDict = sessionDict1;
		self.catDict = catDict1;
		self.entDict = entDict1;
		self.typeDict = typeDict1;
	
	def filterNgrams(self):
		for entry in self.ngrams.keys():
			nentry = filterStopWordsFromQuery(entry)
			if len(nentry) < 3:
				del self.ngrams[entry]
	
	def filterQVector(self):
		for entry in self.queryVector.keys():
			if len(entry) < 3:
				del self.queryVector[entry]
				
	def returnEntities(self):
		return self.entDict;
	
	def returnUsers(self):
		return self.userDict;
		
	def returnCategories(self):
		return self.catDict;

	def returnSessions(self):
		return self.sessionDict;

	def returnType(self):
		return self.typeDict;
		
	def returnUrl(self):
		return self.urlDict;


	def mergeFeature(self, feat):
		self.updateDict(feat.urlDict, self.urlDict)
		self.updateDict(feat.userDict,self.userDict)
		self.updateDict(feat.sessionDict,self.userDict)
		self.updateDict(feat.entDict,self.entDict)
		self.updateDict(feat.catDict,self.catDict)
		self.updateDict(feat.typeDict,self.typeDict)
				
	def updateDict(self, urlDict1,tdict):
		for entry, val in urlDict1.iteritems():
			if entry not in tdict:
				tdict[entry]= 0;
			
			tdict[entry] += val;

	def findCosineDistance(self, qFeat):
		qCos = get_cosine(self.queryVector, qFeat.queryVector);
		uCos = get_cosine(self.urlDict, qFeat.urlDict);
		userCos = get_cosine(self.userDict, qFeat.userDict);
		sessionCos = get_cosine(self.sessionDict, qFeat.sessionDict);
		ngramsCos = get_cosine(self.ngrams, qFeat.ngrams);
		entCos = get_cosine(self.entDict, qFeat.entDict);
		catCos = get_cosine(self.catDict, qFeat.catDict);
		typeCos = get_cosine(self.typeDict, qFeat.typeDict);
		return (qCos,uCos, userCos, sessionCos, ngramsCos,entCos,catCos,typeCos);
		
	def findEditDistance(self, qFeat):
		#print self.query, qFeat.query, distance.nlevenshtein(self.query, qFeat.query,method=1), distance.nlevenshtein(self.query, qFeat.query,method=2)
		edit = 1.0-distance.nlevenshtein(self.query, qFeat.query,method=1)
		return edit	
		
	def findJacardDistance(self, qFeat):
		#print self.query, qFeat.query, distance.jaccard(self.query, qFeat.query)
		qJac = 1.0-distance.jaccard(self.query, qFeat.query);
		#uJac = 1.0-distance.jaccard(self.urlDict.keys(), qFeat.urlDict.keys());
		#userJac = 1.0-distance.jaccard(self.userDict.keys(), qFeat.userDict.keys());
		return qJac#, uJac, userJac);
	
	def toString(self):
		return str(self.ngrams)+'\t'+str(self.queryVector)+\
		'\t'+str(self.urlDict)+'\t'+str(self.userDict)+\
		'\t'+str(self.catDict)+'\t'+str(self.entDict)+'\t'+str(self.typeDict)+\
		'\t'+str(self.sessionDict)
		
	
	def keepFeatKey(self,feat, toKeep):
		for entry in feat.keys():
			if entry not in toKeep:
				del feat[entry]
		
	def filterFeat(self, toKeepFeat):
		self.keepFeatKey(self.ngrams, toKeepFeat)
		self.keepFeatKey(self.queryVector, toKeepFeat)
		self.keepFeatKey(self.urlDict, toKeepFeat)
		self.keepFeatKey(self.userDict, toKeepFeat)
		self.keepFeatKey(self.catDict, toKeepFeat)
		self.keepFeatKey(self.entDict, toKeepFeat)
		
		