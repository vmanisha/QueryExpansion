# -*- coding: utf-8 -*-
from queryLog import parseLine, hasAlpha, QUERY, CLICKU
from utils import stopSet, ashleelString
import sys,  ast
from utils.word import Word
from nltk.stem import porter
from features.featureManager import FeatureManager

def readWeightMatrix(fileName):
	weightMatrix = {}
	lbreak = False
	for line in open(fileName,'r'):
		if lbreak:
			split = line.split()
			i = int(split[0])
			if i not in weightMatrix:
				weightMatrix[i] = {}
			try:
				weightMatrix[i][int(split[1])] = 1.0-round(float(split[-1]),2)
			except:
				print 'Error reading ',line
		if len(line) <10 and (not lbreak):
			lbreak = True
	
	return weightMatrix
						
def toString(eset,featMan):
	string = ''
	for entry in eset:
		string+='\t'+str(featMan.returnQuery(entry))
	return string.strip()
	
def findClickQuery(fileName):
	'''load clicked queries'''
	porter1 = porter.PorterStemmer()
	clickQuery = {}
	for line in open(fileName, 'r'):
		entry = parseLine(line.strip())
		if len(entry) > 3:
			terms = entry[QUERY].split()
			for term in terms:
				nterm = porter1.stem(term)
				if len(term) > 2 and hasAlpha(term) and term not in ashleelString and \
				nterm not in stopSet and nterm not in ashleelString:
					if nterm not in clickQuery:
						clickQuery[nterm] = {}
					clickQuery[nterm][entry[CLICKU]] = clickQuery[nterm].setdefault(entry[CLICKU],0.0) + 1.0
	
	for entry, cdict in clickQuery.iteritems():
		print entry ,'\t', cdict
	
	return clickQuery

def loadClickedTerms(fileName):
	termClickDict= {}
	for line in open(fileName, 'r'):
		split = line.strip().split('\t')
		termClickDict[split[0]] = ast.literal_eval(split[-1].strip())
	return termClickDict
		
def calWordFeatures(fileName,clickQuery):
	wordStats = {}
	porter1 = porter.PorterStemmer()
	for line in open(fileName,'r'):
		split= line.strip().split('\t')
		query = split[0]
				
		#find candidate nonEntity Term
		qsplit = query.split()
		toCheck = set()
		for term in qsplit:
			term = porter1.stem(term)
			if len(term) > 2 and term not in stopSet and term not in ashleelString:
				toCheck.add(term)
		
		#find the entities
		spotDict = ast.literal_eval(split[-1])
		entities = {}
		entString = ' '.join(spotDict.keys())
		#find the categories
		categories = []
		for entity in spotDict:
			categories += spotDict[entity]['cat'].split()
			entities[entity] = spotDict[entity]['score']
			
		for term in toCheck:		
			if term not in wordStats:
				wordStats[term] = Word(term)
			
			inEnt = 1.0 if term in entString else 0
			clicked = 1.0 if term in clickQuery else 0
			print toCheck - set([term]), term, toCheck
			wordStats[term].updateStats(categories, inEnt, entities, toCheck - set([term]), clicked)
			
	for word , wObj in wordStats.iteritems():
		print word, wObj.string()


def mergeQueryCountS(file1, file2):
	counts = {}
	for line in open(file1,'r'):
		split = line.strip().split('\t')
		query = split[0].lower().strip()
		if query not in counts:
			counts[query] = int(split[1])
		else:
			counts[query] += int(split[1])
	
	for line in open(file2,'r'):
		split = line.strip().split('\t')
		query = split[0].lower().strip()
		if query not in counts:
			counts[query] = int(split[1])
		else:
			counts[query] += int(split[1])
			
	for entry, freq in counts.iteritems():
		print entry ,'\t',freq
	

def findPairwiseDistance(file1):	
	featMan = FeatureManager()
	
	featMan.readFeatures(file1)
	featDict = featMan.featureDict;
	
	ids = featDict.keys()
	keys = sorted(ids);
	print len(keys), keys[-5:]
	for i in range(49952,49954):
		qid1, qf1 = featMan.returnFeature(keys[i])
		for j in range(64006, 64080):
			qid2, qf2 = featMan.returnFeature(keys[j])
			qcos, ucos, userCos, ngramCos, entCos, catCos = qf1.findCosineDistance(qf2)
			qjac = qf1.findJacardDistance(qf2)
			#qedit = qf1.findEditDistance(qf2)
			#normalized distance
			#dist = (j - i)#*1.0/len(session)
			
			edgeScore = (.25*((qcos + qjac )/2.0) +\
			.15*ngramCos + .15*ucos + \
			.15*userCos + .15*entCos + .15*catCos)
			if edgeScore > 0.15:
				#print session[i], session[j], edgeScore, qcos, qjac, ucos, userCos, qedit
				print i, j,keys[i], keys[j], edgeScore
		
		
'''
argv[1] = Query Log
argv[2] = tagged File
'''
def main(argv):
	#clickedInfo = loadClickedTerms(argv[1])
	#calWordFeatures(argv[2], clickedInfo)
	#mergeQueryCountS(argv[1],argv[2])
	findPairwiseDistance(argv[1])
	
if __name__ == '__main__':
	main(sys.argv)		
				
					
		
'''


#In the tagged logs
for each term:
	IN CATEGORY
	#no of queries
	#no of unique entities
	#no of terms
	#no of queries with clicks
	#total entites
	#is an entity
	#max PMI
	#avg PMI
	#cat freq
	
	OUTSIDE CATEGORY
	#no of categories
	#avg Cat Freq
	#max Cat Freq
	#no of queries with clicks
	#no of entities
	#no of terms
	#no of queries
	#is an entity
	#no of unique entities
	#max PMI
	#avg PMI
	#cat freq


'''
