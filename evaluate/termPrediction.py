# -*- coding: utf-8 -*-
import sys
import os
from entity.catThesExpansion import CatThesExpansion
from queryLog import getSessionWithNL

from entity.category.categoryManager import CategoryManager
from entity.dexter import Dexter
from entity.ranker import Ranker
from entity.category.coOccurrence import CoOccurrence
from entity.category.coOcManager import CoOcManager
from tasks.taskExpansion import TaskExpansion
from evaluate import addedAndRemovedTerms
from randomwalk.randomWalk import RandomWalk

'''
argv[1] = Session file
argv[2] = vector file / cat query folder / wikiIndex
argv[3] = category phrase folder / topic folder / queryIndex
argv[4] = category Co-Occurrence file
arg[5] = Task index
'''#

def main(argv):
	ipaddress = 'localhost'
	#dexter object
	tagURL = 'http://'+ipaddress+':8080/rest/annotate'
	catURL = 'http://'+ipaddress+':8080/rest/graph/get-entity-categories'
	dexter = Dexter(tagURL,catURL)
	
	#load the Category co-occurrence bit
	catCoMan =	CoOcManager(argv[4],CoOccurrence(),' ')

	#category vector
	catManage = CategoryManager(argv[2],argv[3])
	
	
	'''
	#taskExpansion
	#taskExp50 = TaskExpansion(argv[5],ranker,50)
	#taskExp100 = TaskExpansion(argv[5],ranker,100)
	'''
	#ranker
	ranker = Ranker()
	
	#expansion
	entExp = CatThesExpansion(dexter, catManage, ranker,catCoMan)
	
	#randomWalk
	#randWalk = RandomWalk(argv[2],argv[3],ranker)
	prec = {}
	recall = {}
	
	for i, session in getSessionWithNL(argv[1]):
		query = session[0]
		
		aTerms,rTerms = addedAndRemovedTerms(query, session[1:])
		if len(aTerms) > 0:
			entExpTerms = entExp.expandTextWithStep(query,1,50,55,5)
			#randExpTerms = randWalk.expandTextWithStep(query,55,105,5)
			#taskExpTerms50 = taskExp50.expandTextWithStep(query,0,55,5)
			#taskExpTerms100 = taskExp100.expandTextWithStep(query,0,55,5)
			#print entExpTerms, taskExpTerms50, taskExpTerms100
			for noTerms in entExpTerms.keys():
				print 'Terms\t',i,'\t',query,'\t',entExpTerms[noTerms],'\t',noTerms
				prec1 , recall1 = getPrecRecall(entExpTerms[noTerms],aTerms)
				if noTerms not in prec:
					prec[noTerms] = []
					recall[noTerms] = []
				prec[noTerms].append(prec1)
				recall[noTerms].append(recall1)
				#prec2 , recall2 = getPrecRecall(taskExpTerms50[noTerms],aTerms)
				#prec3 , recall3 = getPrecRecall(taskExpTerms100[noTerms],aTerms)
				#print 'Metrics ',i,'\t',noTerms, '\t',prec1, '\t',prec2,'\t',prec3, \
				#'\t',recall1, '\t', recall2, '\t',recall3
			
				print 'Metrics ',i,'\t',noTerms, '\t',prec1, '\t',recall1
	for i, plist in prec.iteritems():
		print 'Prec@',i,'\t', sum(plist), len(plist), (sum(plist)*1.0)/len(plist)	
		
	for i, rlist in recall.iteritems():
		print 'Recall@',i,'\t', sum(rlist), len(rlist), (sum(rlist)*1.0)/len(rlist)	
	
			
def getPrecRecall(run, toCompare ):			
	apset = set(x[0] for x in run)	
	#print 'pSet ',apset
	print apset , len(apset), toCompare
	aInt =  toCompare & apset
	prec = (1.0*len(aInt))/len(toCompare)	
	if len(apset) > 0:
		recall = (1.0*len(aInt))/len(apset)
	else:
		recall = 0.0
	return prec, recall
	
if __name__ == '__main__':
	main(sys.argv)