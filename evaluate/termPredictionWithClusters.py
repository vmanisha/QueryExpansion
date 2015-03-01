# -*- coding: utf-8 -*-
import sys
from entity.category.ds import loadClusters
from entity.expand.scorer import CoOccurSimScore
from utils.ds.coOccurrence import CoOccurrence
from utils.ds.coOcManager import CoOcManager
from entity.expand.catClusExpansion import ScoreClusterTerms
from queryLog import getSessionWithXML, normalize;
from evaluate import addedAndRemovedTerms
import os
from termPrediction import getPrecRecall
from plots import plotMultipleSys
from utils import stopSet

from utils import text_to_vector,loadFileInList

def toTerms(clusters):
	
	clustersWithTerms = []
	
	for clust in clusters:		
		terms = {}
		for entry in clust:
			split = entry.split()
			for st in split:
				if len(st) > 2  and st not in stopSet:
					if st not in terms:
						terms[st]= 0.0
					terms[st]+=1.0
		if len(terms) > 0:
			clustersWithTerms.append(terms)	
	return clustersWithTerms


def getTermList(queryList):
	termList = {}
	
	for entry in queryList:
		count = text_to_vector(entry)
		for w, c in count.items():
			if w not in termList:
				termList[w] = 0.0
			termList[w] += c	
	
	#print 'TermList ',len(termList), termList
	return termList.items()
	
def main(argv):
	
	#Scorer
	coSessOccur = CoOccurrence();
	coSessOcMan = CoOcManager(argv[2],coSessOccur,' ');
	tScorer = CoOccurSimScore(coSessOcMan)
	cScorer = ScoreClusterTerms()
	
	#vocab = set()
	i=0
	prec = {}
	mrr = {}
	lim = 55
	
	queryList = loadFileInList(argv[5])
	termList = getTermList(queryList)
	added = 0
	oracle_prec=0.0
	oracle_mrr = 0.0
	for tid, session, viewDocs, clickDocs, cTitle, cSummary in getSessionWithXML(argv[1]):
		query = session[0].strip();
		aTerms,rTerms = addedAndRemovedTerms(query, session[1:], None )
		if len(aTerms) > 0:
			prec1 , mrr1 = getPrecRecall(termList,aTerms)
			added+=1.0
			oracle_prec+= prec1
			oracle_mrr+= mrr1
			
	print 'Oracle prec and recall ', oracle_prec/added, oracle_mrr/added
	
	for iFile in os.listdir(argv[3]):
		qclusters = loadClusters(argv[3]+'/'+iFile)
		clusters = toTerms(qclusters)

		print iFile, len(clusters)
		prec[iFile] = {}
		mrr[iFile] = {}
		added=0.0
		for tid, session, viewDocs, clickDocs, cTitle, cSummary in getSessionWithXML(argv[1]):
			i+=1
			query = session[0].strip();
			aTerms,rTerms = addedAndRemovedTerms(query, session[1:], None )
			if len(aTerms) > 0:
				terms = cScorer.score(query, clusters,tScorer, lim)
				
				for topk in range(5,lim,5):
					prec1 , mrr1 = getPrecRecall(terms[:topk],aTerms)
					#print topk , prec1, mrr1
					if topk not in prec[iFile]:
						prec[iFile][topk] = 0.0
						mrr[iFile][topk] = 0.0
						
					prec[iFile][topk] += prec1
					mrr[iFile][topk] += mrr1
				added +=1.0
	
	for entry in prec.keys():
		for t in prec[entry].keys():
			print 'Prec',entry, t, prec[entry][t], prec[entry][t]/added
			prec[entry][t]/=added

	for entry in mrr.keys():
		for t in mrr[entry].keys():
			print 'Mrr',entry, t, mrr[entry][t], mrr[entry][t]/added
			mrr[entry][t]/=added

	print 'Plotting Precision and MRR'
	
	plotMultipleSys(prec,'No of Terms', 'Prec',argv[4]+'/prec.png','Term Prediction Prec Plot');
	plotMultipleSys(mrr,'No of Terms', 'MRR',argv[4]+'/mrr.png','Term Prediction MRR Plot');
	
	#read the file and score clusters from each of the above
	#Print the precision values and MRR values
	#Plot if necessary


if __name__ == '__main__':
	main(sys.argv)
