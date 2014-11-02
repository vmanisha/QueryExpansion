# -*- coding: utf-8 -*-
import math;

def loadRelJudgements(fileName):
	#query : 	{document : label}
	labels = {}
	for line in open(fileName,'r'):
		split = line.strip().split(' ');
		q = int(split[0]);
		d = split[2]
		st = int(split[-1])
		
		if q not in labels:
			labels[q] = {};
		if d not in labels[q]:
			labels[q][d] = st;
	return labels;
	

def findMAP(results, rel):
	MAP =0.0;
	qCount = 0.0;
	for qid, docs in results.items():
		MAP+= findAvgPrec(docs, rel[qid]);
		qCount+=1;
	return MAP/qCount;

#results = docList for a query
#rel = relevance labels for that query
def findAvgPrec(results, rel):
	noRel = len(rel);
	pTotK = 0.0;
	avpTotal = 0.0;
	for k in range(len(results)):
		lab = 0;
		if results[k] in rel:
			lab=rel[results[k]];
			lab = min(1,lab);
		pTotK += lab;	
		pK  = pTotK/(k*1.0);
		avpTotal+= pK*lab;

	return avpTotal/noRel;
	
def findNDCG10(results, rel):
	#return NDCG and NDCG at 10
	totNdcg=0.0;
	qCount = 0.0;
	for query, documents in results.items():
		dcg10, idcg10 = findDCG(documents[:10],rel[query]);
		totNdcg+= dcg10/idcg10;
		qCount+=1;
	return totNdcg/qCount;
	
def findDCG(results, rel):
	DCG = 0.0;
	IDCG = 0.0;
	idcgOrder = sorted(rel.values(), reverse = True);
	for k in range(len(results)):
		lab = 0.0;
		if results[k] in rel:
			lab = rel[results[k]];
		logK = math.log(k+1);

		ilab = idcgOrder[k];
		if logK > 0:
			DCG+= lab/logK;	
			IDCG += ilab/logK;
		else:
			DCG+=lab;
			IDCG+=ilab;
		
	return DCG, IDCG;