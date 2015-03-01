# -*- coding: utf-8 -*-
import sys
from entity.category.ds import loadClusters
from entity.expand.scorer import CoOccurSimScore
from utils.ds.coOccurrence import CoOccurrence
from utils.ds.coOcManager import CoOcManager
from entity.expand.catClusExpansion import ScoreClusterTerms
from queryLog import getSessionWithXML, normalize;

def main(argv):
	#load the clusters
	
	#QCC
	qccClusters = loadClusters(argv[3])
	#Kmeans
	kmeansClusters = loadClusters(argv[4])
	#CatDict
	catDictClusters = loadClusters(argv[5])
	#CatDictClust
	catSubclusters = loadClusters(argv[6])
	
	#Scorer
	coSessOccur = CoOccurrence();
	coSessOcMan = CoOcManager(argv[2],coSessOccur,' ');
	tScorer = CoOccurSimScore(coSessOcMan)
	cScorer = ScoreClusterTerms()
	
	i=0
	
	for session, viewDocs, clickDocs, cTitle, cSummary in getSessionWithXML(argv[1]):
		i+=1
		query = session[0].strip();
		
		qccTerms= cScorer.score(query, qccClusters,tScorer, lim)
		catDictTerms = cScorer.score(query, catDictClusters,tScorer,lim)
		kmeansTerms = cScorer.score(query, kmeansClusters,tScorer, lim)
		catSubTerms = cScorer.score(query, catSubclusters,tScorer, lim)
	#read the file and score clusters from each of the above
	#Print the precision values and MRR values
	#Plot if necessary


if __name__ == '__main__':
	main(sys.argv)