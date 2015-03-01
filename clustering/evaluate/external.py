# -*- coding: utf-8 -*-
#load the pairs labelled together in one task

# Calculate Precision, Recall, F Measure, Rand Index

from queryLog import normalize
from nltk import stem
import sys, math
from utils import loadFileInTuples

from utils import filterWords
def Precision(tp, fp):
	return tp/(1.0*(tp+fp))
	
def Recall(tp,fn):
	return tp/(1.0*(tp+fn))

def fMeasure(prec, recall):
	beta = 5
	pow2 = math.pow(beta,2)
	#return ((pow2+1.0)*( prec* recall))/(pow2*prec+recall)
	return 2.0*(( prec* recall)/(prec+recall))
	
def RandIndex(tp,tn,totalPairs):
	return (tp+tn)/(totalPairs*1.0)
	
def calculateIndicies(trueLabelFile,differentPairFile, predictedLabelFile, queryList):
	stemmer = stem.porter.PorterStemmer()
	queryId={}
	idQuery = {}
	i = 1
	for line in open(queryList,'r'):
		split = line.split('\t')
		query = filterWords(split[0].strip())
		queryId[query] = str(i)
		idQuery[str(i)] = query
		i+=1
		
	c = 1
	l_samePairs = set()
	l_points = set()
	l_diffPairs = set()
	p_samePairs = set()
	
	#load true label file
	#Same cluster
	for line in open(trueLabelFile,'r'):
		split = line.split('\t')
		cpoints = set()
		for entry in split:
			normQuery = normalize(entry,stemmer)
			if normQuery in queryId:
				qid = queryId[normQuery]
				l_points.add(qid)
				cpoints.add(qid)
			else:
				if len(normQuery) > 0:
					pass
					#print 'True same ',normQuery
			pairs = generatePairs(sorted(cpoints))
		
		for pair in pairs:
			l_samePairs.add(pair)
		c+1
	
	#load differentPairs
	for line in open(differentPairFile,'r'):
		split = line.split('\t')
		cpoints = set()
		for entry in split:
			normQuery = normalize(entry,stemmer)
			if normQuery in queryId:
				qid = queryId[normQuery]
				cpoints.add(qid)
			else:
				if len(normQuery) > 0:
					pass
					#print 'True Diff ',normQuery
			pairs = generatePairs(sorted(cpoints))
		
		for pair in pairs:
			l_diffPairs.add(pair)
		
		
	total_pairs = len(l_samePairs) + len(l_diffPairs) #(len(l_points)*(len(l_points)-1))/2
	#filter predicted label file
	for line in open(predictedLabelFile,'r'):
		line = line.strip()
		cpoints = set()
		if len(line) > 0:
			split = line.split('\t')
			for entry in split:
				try:
					qid = queryId[entry]
					if qid in l_points:
						cpoints.add(qid)
				except:
					pass
			pairs = generatePairs(sorted(cpoints))
			for pair in pairs:
				if pair in l_samePairs or pair in l_diffPairs:
					#if pair in l_diffPairs:
					#	s = pair.split()
					#	print pair, idQuery[s[0]], idQuery[s[1]]
					p_samePairs.add(pair)#
	
	print len(l_samePairs), len(p_samePairs), total_pairs
	tp = len(l_samePairs & p_samePairs);
	fp = len(p_samePairs & l_diffPairs)#len(p_samePairs) - tp ;
	fn = len(l_samePairs) - tp ;
	tn = len(l_diffPairs) - fp #total_pairs - (tp+fp+fn)
	print tp, fp, fn, tn, total_pairs
	
	return tp, fp, fn, tn, total_pairs

def generatePairs(elist):
	pairList = []
	for i in range(len(elist)-1):
		for j in range(i+1, len(elist)):
			pairList.append(elist[i]+' '+elist[j])
	return pairList


def printIndices(argv1,argv2,argv3):
	tp, fp, fn, tn, totalPairs = calculateIndicies(argv1,argv2,argv3)
	print 'Rand-Index ', RandIndex(tp,tn,totalPairs)
	recall = Recall(tp,fn)
	print 'Recall', recall
	prec = Precision(tp, fp)
	print 'Precision', prec
	print 'fMeasure', fMeasure(prec, recall)
	


#trueLabelFile,differentPairFile, predictedLabelFile, queryList
if __name__ == '__main__':
	argv = sys.argv

	
	tp, fp, fn, tn, totalPairs = calculateIndicies(argv[1],argv[2],argv[3],argv[4])
	print 'Rand-Index ', RandIndex(tp,tn,totalPairs)
	recall = Recall(tp,fn)
	print 'Recall', recall
	prec = Precision(tp, fp)
	print 'Precision', prec
	print 'fMeasure', fMeasure(prec, recall)