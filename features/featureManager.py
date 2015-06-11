# -*- coding: utf-8 -*-
import ast
import sys
from features.queryFeature import QueryFeature
from utils import loadFileInList
class FeatureManager:
	
	def __init__(self):
		#id--> queryfeature
		self.featureDict = {}
		#query --> id mapping
		self.idDict = {}
		#id --> query mapping
		self.qDict = {}
		self.featGCount = {}
		self.lastId = None;
		
	def addFeature(self, query, qid, feat):
		#merge Features

		if len(query) > 0:
			if query in self.idDict:
				key = self.idDict[query]
				#ngrams and query terms will remain the same
				self.featureDict[key].mergeFeature(feat)
			#print 'Mergin query ', query
		#add new query
			else:	
				self.idDict[query] = qid;
				#self.qDict[qid] = query;
				
				if qid not in self.featureDict:
					self.featureDict[qid] = feat;
		
				if len(self.featureDict) % 100000==0:
					print len(self.featureDict)	
		
	def deleteFeature(self, key):
		key = self.idDict[key];
		if key in self.featureDict:
			del self.featureDict[key]
	
	def returnFeature(self, key1):
		#print key1, key1 in self.idDict
		if key1 in self.idDict:
			key = self.idDict[key1];
			if key in self.featureDict:
				return key, self.featureDict[key]
		else:
			#print 'key ', key1
			if key1 in self.featureDict:
				return key1, self.featureDict[key1]
		return None, None
		
	
	def returnId(self, query):
		if query in self.idDict:
			return self.idDict[query]
		
		return None
		
	def returnQuery(self,qid):
		if qid in self.featureDict:
			return self.featureDict[qid].query
		
		return ''
	
	def iterFeatures(self):
		for entry, queryFeat in self.featureDict.items():
			#query = self.qDict[entry]
			yield entry, queryFeat
	
	def writeFeatures(self, fileName):
		outFile = open(fileName,'w')
		for qid, feat in self.featureDict.items():
			query = feat.query
			if len(query) > 1:
				outFile.write(query+'\t'+feat.toString()+'\n')
		outFile.close()
	
	def returnKeys(self):
		return self.featureDict.keys();

	def buildFeatCounts(self, i,featD):
		
		for entry, count in featD.items():
			if entry not in self.featGCount:
				self.featGCount[entry]  = set()
			self.featGCount[entry].add(i)
	
	def filterFeatures(self, count):
		count+=0
		for entry in self.featGCount.keys():
			if len(self.featGCount[entry]) < count:
				del self.featGCount[entry]
		
			
	def filterWords(self,query, wlen=1):
		nQuery = ''
		for entry in query.split():
			if len(entry) > wlen:
				nQuery +=' '+ entry
		nQuery = nQuery.strip()
		return nQuery
	
	def loadQueries(self, fileName):
		i = 1
		for line in open(fileName,'r'):
			split = line.strip().split('\t')
			query = self.filterWords(split[0])
			if len(query) > 0 and query not in self.idDict:
				self.idDict[query] = i;
				self.qDict[i] = query
				
			i+=1;
	
	def returnIdDict(self):
		return self.idDict;
	
	def returnQueryDict(self):
		return self.qDict;			
		
	def readFeatures(self, fileName,queryFilter = None):
		
		#if queryFilterFile:
		#	toFilter = loadFileInList(queryFilterFile)
			
		i = 1
		for line in open(fileName,'r'):
			split = line.strip().split('\t')
			query = self.filterWords(split[0])
			typeList = 	ast.literal_eval(split[7])
			#if toFilter and query in toFilter:
			#query1, ngrams1, qVect, urlDict1, userDict1, sessionDict1 = 8, entDict1 = 5  \
	        #catDict1 = 6,typeDict1 = 7
			queryFeat = QueryFeature(query, ast.literal_eval(split[1]),ast.literal_eval(split[2]),\
			ast.literal_eval(split[3]),ast.literal_eval(split[4]),\
			ast.literal_eval(split[8]),	ast.literal_eval(split[5]),\
			ast.literal_eval(split[6]),	typeList)
			if len(typeList) > 0:
			#if queryFilter and query in queryFilter and len(typeList) > 0:
				self.addFeature(query, i, queryFeat);
			
			#self.buildFeatCounts(i,queryFeat.userDict)
			#self.buildFeatCounts(i,queryFeat.catDict)
			#self.buildFeatCounts(i,queryFeat.entDict)
			
			i+=1
			self.lastId = i
		
		print 'Loading features ',len(self.featureDict);
		
		#print len(self.featGCount)
		#self.filterFeatures(2);
		#print len(self.featGCount)
		#
		#for entry in self.featureDict.keys():
			#self.featureDict[entry].filterFeat(self.featGCount);
		#
		#self.writeFeatures('aol-session-filtered-features.all');

	def returnLastId(self):
		return self.lastId
		
def mergeSets(sets):
	setDict =  sets.keys()
	for i in range(len(setDict)):
		if setDict[i] in sets:
			for j in range(i+1,len(setDict)):
				if setDict[j] in sets and sets[setDict[j]].issubset(sets[setDict[i]]):
					del sets[setDict[j]]
	
	for entry, items in sets.items():
		print len(items),'\t', str(items)
		
if __name__ == "__main__":
	argv = sys.argv
	featMan = FeatureManager()
	featMan.readFeatures(argv[1],argv[2])
	#globSet = featMan.featGCount
	#mergeSets(globSet)