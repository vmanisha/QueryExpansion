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
	
	for iFile in os.listdir(argv[3]):
		clusters = loadClusters(argv[3]+'/'+iFile)
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
