# -*- coding: utf-8 -*-

from evaluate.termPredictionWithClusters import toTerms,getTermList
import sys
from features.featureManager import FeatureManager
from entity.category import findCatQueryDist
from queryLog import getSessionWithQuery
import random
import numpy as np
import Pycluster as clust
from termPrediction import getPrecRecall,getTerms, getClustPrecRecall
from tasks.qccTasks import QCCTasks
from queryLog import getQueryTermsStemmed,getQueryTerms
from evaluate import addedAndRemovedTerms
from entity.expand.catClusExpansion import ScoreClusterTerms
from entity.category.findCategoryClusters import \
getWeightMatrixForKMedFromFile,getWeightMatrixForKMed
from nltk import stem
from features import toString,readWeightMatrix
from entity.category.buildCategoryNetwork import returnFilteredNetwork
#load sessions
def loadSessions(sessFile):
	sessions = []
	count = 0.0
	clen = 0
	for session in getSessionWithQuery(sessFile):
		if len(session) > 0:
			sessions.append(session)
			count+=1
			clen+=len(session)
	print count, clen/count
			
	return sessions
	
def sampleSessions(sessions, percent):
	x = []
	y = []
	tos = int(percent*len(sessions))
	ls = range(len(sessions))
	xs = random.sample(ls,tos)
	
	uniquex = set()
	uniquey = set()
	for i in range(len(sessions)):
		if i in xs:
			x.append(sessions[i])	
			for entry in sessions[i]:
				uniquex.add(entry)
		else:
			y.append(sessions[i])	
			for entry in sessions[i]:
				uniquey.add(entry)

	print 'Sampling stats: sessions:',len(sessions),'percent:',\
	 percent,'x:', len(x), 'y:',len(y), 'uniqx:',len(uniquex), 'uniquey:',len(uniquey)
	
	return x, y, uniquex, uniquey
	

def clusterSessionsKmed(featMan, weightFile):
	
	data = featMan.returnKeys()
	weightList = getWeightMatrixForKMedFromFile(featMan.returnLastId(),weightFile,data)
	cnt = 0
	kclusters = {}
	for k in range(4,5,2):
		i = (len(weightList)+1)/k
		if i == 0:
			i = 1
		clusArray, error, opt = clust.kmedoids(weightList,i, 10, None)
		print error, len(clusArray)
		clusters = {}
		for c in range(len(clusArray)):
			clusId = clusArray[c]
			q = featMan.returnQuery(c)
			if len(q) > 1:
				if clusId not in clusters:
					clusters[clusId] = set()
				clusters[clusId].add(q)	
				cnt+=1
				
		kclusters[k] = clusters.values()
	
		print 'Cluster with kmed ',len(clusters),cnt,' queries'
	return kclusters[4]


def clusterSessionsQcc(x,featMan, weightMatrix):
	
	tclusters = {}
	for threshold in np.arange(0.24,0.25,0.05):
		qcc = QCCTasks();
		tclusters[threshold] = []
		for session in x:
			if len(session) > 2:
				newSession = []
				for i in range(len(session)-1):
					qid1, qf1 = featMan.returnFeature(session[i])
					if qf1:
						newSession.append(session[i])
				
				session = newSession
				#calculate the score
				for i in range(len(session)-1):
					qid1, qf1 = featMan.returnFeature(session[i])
					if qf1:
						for j in range(i+1,len(session)):
							qid2, qf2 = featMan.returnFeature(session[j])
							if qf2:
								try:
									#print qid1, qid2
									if qid1 < qid2 :
										edgeScore = 1.0-weightMatrix[qid1][qid2]
									else:
										edgeScore = 1.0-weightMatrix[qid2][qid1]
										
									if edgeScore > threshold:
										#print session[i], session[j], edgeScore, qcos, qjac, ucos, userCos, qedit
										qcc.addEdge(qid1, qid2, edgeScore)
								except:
									pass
		labels = qcc.getTaskComponents()
		
		for entry in labels:
			nc = []
			for qid in entry:
				qc = featMan.returnQuery(qid)
				if len(qc) > 1:
					nc.append(qc)
			if len(nc) > 0:	
				tclusters[threshold].append(nc)

		
	return tclusters[0.24]

#def clusterSessionsPost(x,features):
#	return clusters

def clusterSessionsPre(catQueryDist,featMan,weightMatrix):
	
	tclusters = {}
	print len(catQueryDist)
	for termCount in range(4,5):
		tclusters[termCount] = []
		for cat, qSet in catQueryDist.items():
			if len(qSet) > 1: # and cat in pairs:
				k = len(qSet)/termCount
				if k == 0:
					k = 1
				#print cat, len(qSet), k
				qList = list(qSet)
				catDist = getWeightMatrixForKMed(qList, weightMatrix)
							
				clusArray, error, opt = clust.kmedoids(catDist,k, 5, None)
				#print 'Queries', qList
				clusters = {}
				for c in range(len(clusArray)):
					clusId = clusArray[c]
					if clusId not in clusters:
						clusters[clusId] = []
					qc = featMan.returnQuery(qList[c])
					if len(qc) > 1:
						clusters[clusId].append(qc)
				#print cat, len(clusters)
				for entry in clusters.values():
					tclusters[termCount].append(entry)
		
	print len(tclusters[4])
	return tclusters[4]


def predictTerms(queryList, y,qclusters):
	termList, termDict = getTermList(queryList)
	oracle_prec=0.0
	oracle_mrr = 0.0
	added=0
	cScorer = ScoreClusterTerms()
	for session in y:
		query = session[0]
		aTerms,rTerms = addedAndRemovedTerms(query, session[1:], termDict)
		if len(aTerms) > 0:
			prec1 , mrr1 = getPrecRecall(termList,aTerms)
			added+=1.0
			oracle_prec+= prec1
			oracle_mrr+= mrr1
	print 'Oracle prec and recall ', oracle_prec/added, oracle_mrr/added, added
	#porter = stem.porter.PorterStemmer();
	clusters, clusIndex = toTerms(qclusters)
	lim=5
	i =0
	prec = {}
	mrr = {}
	pf = 0.0
	pr = 0.0
	for session in y:
		query = session[0].strip();
		qSet = getQueryTerms(query) #getQueryTermsStemmed(query, porter);
		aTerms,rTerms = addedAndRemovedTerms(query, session[1:], termDict)
		if len(aTerms) > 0:
			terms = cScorer.scoreWithCosine(qSet, clusters,clusIndex, lim)
			
			if len(terms) > 0:
				#print len(aTerms), len(terms)
				prec1 , mrr1 = getClustPrecRecall(terms,aTerms) # returns a list
				#print 'METRIC',i, prec1, mrr1
					#print topk , prec1, mrr1
				if sum(prec1) > 0:
					pf +=1.0

				if sum(mrr1) > 0:
					pr +=1.0
				
				for topk in range(len(prec1)):	
					if topk not in prec:
						prec[topk] = []
						mrr[topk] = []
					
					prec[topk].append(prec1[topk])
					mrr[topk].append(mrr1[topk])
			i+=1

	retPrec = {}
	retRecall = {}
	
	for entry, ls in prec.items():
		print 'Prec @',entry, np.mean(ls)
		retPrec[entry] = np.mean(ls)
	
	for entry , ls in mrr.items():
		print 'Recall @',entry, np.mean(ls)
		retRecall[entry] = np.mean(ls)
		
	
	print 'Percentage ', pf/i, pr/i	
	
	return retPrec, retRecall
def kFoldEvaluation(k,sessFile, featFile,weightFile,percent,typeFile):
	sessions = loadSessions(sessFile)
	#weightMatrix = readWeightMatrix(weightFile)
	#
	#p1 = {}
	#r1 = {}
	#p2 = {}
	#r2 = {}
	#p3 = {}
	#r3 = {}
	#p4 = {}
	#r4 = {}

	#
	amean = []
	ymean = []
	for i in range(k):
		x,y , uniqx, uniqy = sampleSessions(sessions,percent)
		acount = 0.0
		ylen = 0.0
		termList, termDict = getTermList(uniqx)
		for session in y:
			aTerms,rTerms = addedAndRemovedTerms(session[0], session[1:], termDict)
			acount+=len(aTerms)
			ylen += len(session)
		print acount, ylen , acount/len(y), ylen/len(y)
		amean.append(acount/len(y))
		ymean.append(ylen/len(y))
	
	print np.mean(amean), np.mean(ymean)
		#print len(x), len(y), len(uniqx), len(uniqy)
		#featMan = FeatureManager()
		#featMan.readFeatures(featFile,uniqx)
		#clust = clusterSessionsKmed(featMan,weightFile)
		#p, r =predictTerms(uniqx, y,clust)
		#p1, r1 =updateStats(p1,r1,p,r)

		#clust = clusterSessionsQcc(x,featMan,weightMatrix)
		#p, r =predictTerms(uniqx, y,clust)
		#p2, r2 =updateStats(p2,r2,p,r)

		#catQueryDist = findCatQueryDist(featFile,featMan)
		#clust = clusterSessionsPre(catQueryDist,featMan,weightMatrix)
		#p, r =predictTerms(uniqx, y,clust)
		#p3, r3 =updateStats(p3,r3,p,r)

		#catNetwork, catQueryDist = returnFilteredNetwork(featFile, typeFile, featMan,\
		#weightMatrix)
		#clust = clusterSessionsPre(catQueryDist,featMan,weightMatrix)
		#p, r =predictTerms(uniqx, y,clust)
		#p4, r4 =updateStats(p4,r4,p,r)

	#print 'Precision Cluster all '
	#printDict(p1)
	#print 'Recall Cluster all '
	#printDict(r1)

	#print 'Precision QCC '
	#printDict(p2)
	#print 'Recall QCC '
	#printDict(r2)

	#print 'Precision Pre '
	#printDict(p3)
	#print 'Recall Pre '
	#printDict(r3)

	#print 'Precision Post '
	#printDict(p4)
	#print 'Recall Post '
	#printDict(r4)

def printDict(dic):
	for entry, val in dic.items():
		print entry, np.mean(val), np.std(val)

def updateStats(prec, recall, nprec, nrecall):
	
	for entry, val in nprec.items():
		if entry not in prec:
			prec[entry] = []
		prec[entry].append(val)
	
	for entry, val in nrecall.items():
		if entry not in recall:
			recall[entry] = []
		recall[entry].append(val)
	
	return prec, recall
	
def main(argv):
	kFoldEvaluation(int(argv[5]),argv[1],argv[2],argv[3],float(argv[4]),argv[6])

if __name__ == '__main__':
	main(sys.argv)