# -*- coding: utf-8 -*-
import sys
import os
from entity.catThesExpansion import CatThesExpansion
from queryLog import getSessionWithXML

from entity.category.categoryManager import CategoryManager
from entity.dexter import Dexter
from entity.ranker import Ranker
from utils.coOcManager import CoOcManager;
from utils.coOccurrence import CoOccurrence;
from utils import loadFileInList;
from tasks.taskExpansion import TaskExpansion
from evaluate import addedAndRemovedTerms
from randomwalk.randomWalk import RandomWalk
from entity.category import loadCategoryVector;
from  entity.category.category import Category;
from entity.category.categorySubcluster import CategorySubcluster;
from queryLog.coOccurExpansion import CoOccurExpansion;
from plots import plotMultipleSys;
'''
argv[1] = Session file
argv[2] = vector file / cat query folder / wikiIndex
argv[3] = category phrase folder / topic folder / queryIndex
argv[4] = category Co-Occurrence file
argv[5] = spotFile  / Task Index
argv[6] = File containing vocabulary (log dictionary/word counts);
argv[7] = category clusterFolder
'''#

def main(argv):
	ipaddress = 'localhost'
	#dexter object
	tagURL = 'http://'+ipaddress+':8080/rest/annotate'
	catURL = 'http://'+ipaddress+':8080/rest/graph/get-entity-categories'
	dexter = Dexter(tagURL,catURL,argv[5]);
	
	
	#load the Category co-occurrence bit
	catCoMan =	CoOcManager(argv[4],CoOccurrence(),' ')

	#category vector
	catVect = loadCategoryVector(argv[2]);
	catManage1 = CategoryManager(catVect,argv[3],Category);
	catManage2 = CategoryManager(catVect,argv[7],CategorySubcluster);
	
	
	
	#ranker
	ranker = Ranker()
	
	#task extraction
	htcTask = TaskExpansion('Indexes/htcIndex',ranker,3000);
	qccTask = TaskExpansion('Indexes/qccIndex',ranker,3000);
	#taskK = argv[5][argv[5].rfind('/')+1:]
	
	totalVocab = loadFileInList(argv[6]);
		
	#expansion
	entExp1 = CatThesExpansion(dexter, catManage1, ranker,catCoMan);
	entExp2 = CatThesExpansion(dexter, catManage2, ranker,catCoMan);
	#term expansion
	coOccExp = CoOccurExpansion(catCoMan,None ,ranker );
	#randomWalk
	#randWalk = RandomWalk(argv[2],argv[3],ranker)
	prec = {'ent':{}, 'qccTask':{}, 'htcTask':{}, 'co':{} ,'entSub':{}};
	mrr = {'ent':{}, 'qccTask':{}, 'htcTask':{}, 'co':{} , 'entSub':{}};
	
	ent_prec = {'ent':{}, 'qccTask':{}, 'htcTask':{}, 'co':{} , 'entSub':{}};
	ent_mrr = {'ent':{}, 'qccTask':{}, 'htcTask':{}, 'co':{} , 'entSub':{}};
	'''
	sess_prec = {};
	sess_mrr = {};
	'''
	covered = {};
	
	i = 0;
	for session, doc, click in getSessionWithXML(argv[1]):
		query = session[0]
		aTerms,rTerms = addedAndRemovedTerms(query, session[1:], totalVocab)
		print i, 'Query' ,query, aTerms, rTerms, len(aTerms);
		
		if len(aTerms) > 0 and query not in covered:
			covered[query] = 1;
			coExpTerms = coOccExp.expandTextWithStep(query,0,55,5);
			entStatus1, entExpTerms1 = entExp1.expandTextWithStep(query,1,0,55,5);
			entStatus2, entExpTerms2 = entExp2.expandTextWithStepAndSubcluster(query,'',1,0,55,5);
			
			qccTaskTerms = qccTask.expandTextWithStep(query,0,55,5)
			htcTaskTerms = htcTask.expandTextWithStep(query,0,55,5)
			#print entExpTerms, taskExpTerms50, taskExpTerms100
			#randExpTerms = randWalk.expandTextWithStep(query,55,105,5)
			if not entStatus1:
				print i, 'Ent False' ,query;
				
			#addLen = getBand(len(aTerms));
			#if addLen not in sess_prec:
			#	sess_prec[addLen] = {'ent':{}};#, 'qccTask':{}, 'htcTask':{}, 'co':{} };
			#	sess_mrr[addLen] = {'ent':{}};#, 'qccTask':{}, 'htcTask':{}, 'co':{} };
			
			for noTerms in entExpTerms1.keys():
				print 'ETerms\t',i,'\t',query,'\t',entExpTerms1[noTerms],'\t',noTerms
				prec1 , mrr1 = getPrecRecall(entExpTerms1[noTerms],aTerms)
				prec = updateStats(noTerms, 'ent',prec1, prec)
				mrr = updateStats(noTerms, 'ent',mrr1, mrr);
				if entStatus1:
					ent_prec = updateStats(noTerms, 'ent',prec1, ent_prec)
					ent_mrr = updateStats(noTerms, 'ent',mrr1, ent_mrr);
				#sess_prec[addLen] = updateStats(noTerms, 'ent',prec1, sess_prec[addLen])
				#sess_mrr[addLen] = updateStats(noTerms, 'ent',mrr1, sess_mrr[addLen]);
				
				print 'EMetrics ',i,'\t',noTerms,'\t', len(aTerms), '\t', aTerms, '\t',prec1, '\t',mrr1;
						
			for noTerms in entExpTerms2.keys():
				print 'ESubTerms\t',i,'\t',query,'\t',entExpTerms2[noTerms],'\t',noTerms
				prec1 , mrr1 = getPrecRecall(entExpTerms2[noTerms],aTerms)
				prec = updateStats(noTerms, 'entSub',prec1, prec)
				mrr = updateStats(noTerms, 'entSub',mrr1, mrr);
				if entStatus1:
					ent_prec = updateStats(noTerms, 'entSub',prec1, ent_prec)
					ent_mrr = updateStats(noTerms, 'entSub',mrr1, ent_mrr);
				#sess_prec[addLen] = updateStats(noTerms, 'ent',prec1, sess_prec[addLen])
				#sess_mrr[addLen] = updateStats(noTerms, 'ent',mrr1, sess_mrr[addLen]);
				print 'ESubMetrics ',i,'\t',noTerms,'\t', len(aTerms), '\t', aTerms, '\t',prec1, '\t',mrr1;
			
			for noTerms in qccTaskTerms.keys():
				print 'qccTaskTerms\t',i,'\t',query,'\t',qccTaskTerms[noTerms],'\t',noTerms
				prec1 , mrr1 = getPrecRecall(qccTaskTerms[noTerms],aTerms)
				prec = updateStats(noTerms, 'qccTask',prec1, prec)
				mrr = updateStats(noTerms, 'qccTask',mrr1, mrr);
				if entStatus1:
					ent_prec = updateStats(noTerms, 'qccTask',prec1, ent_prec)
					ent_mrr = updateStats(noTerms, 'qccTask',mrr1, ent_mrr);
				'''
				sess_prec[addLen] = updateStats(noTerms, 'qccTask',prec1, sess_prec[addLen])
				sess_mrr[addLen] = updateStats(noTerms, 'qccTask',mrr1, sess_mrr[addLen]);
				'''
				print 'qccTaskMetrics ',i,'\t',noTerms,'\t', len(aTerms), '\t', aTerms, '\t',prec1, '\t',mrr1
			
			
			for noTerms in htcTaskTerms.keys():
				print 'htcTaskTerms\t',i,'\t',query,'\t',htcTaskTerms[noTerms],'\t',noTerms
				prec1 , mrr1 = getPrecRecall(htcTaskTerms[noTerms],aTerms)
				prec = updateStats(noTerms, 'htcTask',prec1, prec)
				mrr = updateStats(noTerms, 'htcTask',mrr1, mrr);
				if entStatus1:
					ent_prec = updateStats(noTerms, 'htcTask',prec1, ent_prec)
					ent_mrr = updateStats(noTerms, 'htcTask',mrr1, ent_mrr);
				'''
				sess_prec[addLen] = updateStats(noTerms, 'htcTask',prec1, sess_prec[addLen])
				sess_mrr[addLen] = updateStats(noTerms, 'htcTask',mrr1, sess_mrr[addLen]);
				'''
				print 'htcTaskMetrics ',i,'\t',noTerms,'\t', len(aTerms), '\t', aTerms, '\t',prec1, '\t',mrr1
			
			
			for noTerms in coExpTerms.keys():
				print 'CoTerms\t',i,'\t',query,'\t',coExpTerms[noTerms],'\t',noTerms
				prec1 , mrr1 = getPrecRecall(coExpTerms[noTerms],aTerms)
				prec = updateStats(noTerms, 'co',prec1, prec)
				mrr = updateStats(noTerms, 'co',mrr1, mrr);
				if entStatus1:
					ent_prec = updateStats(noTerms,'co',prec1, ent_prec)
					ent_mrr = updateStats(noTerms, 'co',mrr1, ent_mrr);
				'''
				sess_prec[addLen] = updateStats(noTerms, 'co',prec1, sess_prec[addLen])
				sess_mrr[addLen] = updateStats(noTerms, 'co' ,mrr1, sess_mrr[addLen]);
				'''
				print 'CoMetrics ',i,'\t',noTerms,'\t', len(aTerms), '\t', aTerms, '\t',prec1, '\t',mrr1
			
		else:
			pass;
			#print 'NO ADDED TERMS in', i;
		i+=1;	
	
	printMetric(prec,'entSub','Prec');
	printMetric(mrr,'entSub','Mrr');
		
	printMetric(prec,'ent','Prec');
	printMetric(mrr,'ent','Mrr');
	
	printMetric(prec,'htcTask','Prec');
	printMetric(mrr,'htcTask','Mrr');
	
	printMetric(prec,'qccTask','Prec');
	printMetric(mrr,'qccTask','Mrr');
	
	printMetric(prec,'co','Prec');
	printMetric(mrr,'co','Mrr');
	
	printMetric(ent_prec,'entSub','EntPrec');
	printMetric(ent_mrr,'entSub','EntMrr');
	
	printMetric(ent_prec,'ent','EntPrec');
	printMetric(ent_mrr,'ent','EntMrr');
	
	printMetric(ent_prec,'htcTask','EntPrec');
	printMetric(ent_mrr,'htcTask','EntMrr');
	
	printMetric(ent_prec,'qccTask','EntPrec');
	printMetric(ent_mrr,'qccTask','EntMrr');
	
	printMetric(ent_prec,'co','EntPrec');
	printMetric(ent_mrr,'co','EntMrr');
	
	plotMultipleSys(prec,'No of Terms', 'Prec',argv[1][:-4]+'_'+'prec.png','Term Prediction Prec Plot');
	plotMultipleSys(mrr,'No of Terms', 'MRR',argv[1][:-4]+'_'+'mrr.png','Term Prediction MRR Plot');
	plotMultipleSys(ent_prec,'No of Terms', 'Prec',argv[1][:-4]+'_'+'_ent_prec.png','Term Prediction Prec Plot (Ent queries)');
	plotMultipleSys(ent_mrr,'No of Terms', 'MRR',argv[1][:-4]+'_'+'_ent_mrr.png','Term Prediction MRR Plot (Ent queries)');
	
	'''
	for aLen, sprec in sess_prec.items():
		printMetric(sprec,'ent','SPrec'+str(aLen));
		printMetric(sprec,'htcTask','SPrec'+str(aLen));
		printMetric(sprec,'qccTask','SPrec'+str(aLen));
		printMetric(sprec,'co','SPrec'+str(aLen));

	for aLen, smrr in sess_prec.items():
		printMetric(smrr,'ent','SMrr'+str(aLen));
		printMetric(smrr,'htcTask','SMrr'+str(aLen));
		printMetric(smrr,'qccTask','SMrr'+str(aLen));
		printMetric(smrr,'co','SMrr'+str(aLen));

	for aLen, sprec in sess_prec.items():
		printMetric(sprec,'ent','SubSPrec'+str(aLen));
	
	for aLen, smrr in sess_prec.items():
		printMetric(smrr,'ent','SubSMrr'+str(aLen));
	
	
	'''

def printMetric(var, method,key):
	nkey = method + key;
	for i, plist in var[method].iteritems():
		print i , plist
		print nkey,i,'\t', sum(plist), len(plist), (sum(plist)*1.0)/len(plist)	

def updateStats(pos, method, val, var):
	if pos not in var[method]:
		var[method][pos] = [];
	var[method][pos].append(val);			
	return var;

def getPrecRecall(run, toCompare ):			
	apset = set(x[0] for x in run)	
	apList = [x[0] for x in run];
	#print 'pSet ',apset
	aInt =  toCompare & apset
	#print 'EXPANSION SET ',apset, 'ADDED SET ',toCompare, 'INTSCN ',aInt

	prec = (1.0*len(aInt))/len(toCompare)	
	mrr = 0;
	for i in range(len(apList)):
		if apList[i] in toCompare:
			mrr = max((1.0/(i+1.0)),mrr);
	#if len(apList) > 0:
	#	mrr /= len(apList);
	
	return prec, mrr;		
	'''if len(apset) > 0:
		recall = (1.0*len(aInt))/len(apset)
	else:
		recall = 0.0
	
	'''

def getBand(num):
	if num < 6:
		return num;
	else:
		return '>5';
		
if __name__ == '__main__':
	main(sys.argv)