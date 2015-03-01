# -*- coding: utf-8 -*-
from utils import get_cosine
import distance
from queryLog import filterStopWordsFromQuery
class QueryFeature:
	
	def __init__(self, query1, ngrams1, qVect, urlDict1, userDict1, entDict1 = None, catDict1 = None):
		self.query = query1
		self.ngrams = ngrams1;
		self.filterNgrams()
		self.queryVector = qVect;
		self.filterQVector()
		self.urlDict = urlDict1;
		self.userDict = userDict1;
		self.catDict = catDict1;
		self.entDict = entDict1;
	
	
	def filterNgrams(self):
		for entry in self.ngrams.keys():
			nentry = filterStopWordsFromQuery(entry)
			if len(nentry) < 3:
				del self.ngrams[entry]
	
	def filterQVector(self):
		for entry in self.queryVector.keys():
			if len(entry) < 3:
				del self.queryVector[entry]
				
	def returnFeature(self,name):
		if name == 'cat':
			return self.catDict;
			
	def mergeFeature(self, feat):
		self.updateURLDict(feat.urlDict)
		self.updateUserDict(feat.userDict)
		
	def updateURLDict(self, urlDict1):
		for entry, val in urlDict1.iteritems():
			self.addURL(entry, val);
	
	def updateUserDict(self, userDict1):
		for entry, val in userDict1.iteritems():
			self.addUser(entry, val);
	
	def addURL(self, url, count):
		if url not in self.urlDict:
			self.urlDict[url] = 0;
		
		self.urlDict[url] += count;
	
	def addUser(self, user, count):
		if user not in self.userDict:
			self.userDict[user] = 0;
			
		self.userDict[user] += count;

	def findCosineDistance(self, qFeat):
		qCos = get_cosine(self.queryVector, qFeat.queryVector);
		uCos = get_cosine(self.urlDict, qFeat.urlDict);
		userCos = get_cosine(self.userDict, qFeat.userDict);
		ngramsCos = get_cosine(self.ngrams, qFeat.ngrams);
		entCos = get_cosine(self.entDict, qFeat.entDict);
		catCos = get_cosine(self.catDict, qFeat.catDict);
		
		return (qCos,uCos, userCos, ngramsCos,entCos,catCos);
		
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
		'\t'+str(self.catDict)+'\t'+str(self.entDict)
		
	
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
		
		