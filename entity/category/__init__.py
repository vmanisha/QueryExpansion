# -*- coding: utf-8 -*-
'''
Imports
'''
import ast
import os
from utils import stopSet
from features.featureManager import FeatureManager
'''
Function
'''

def findCatQueryDist(fileName,featMan):
	catQueryCount = {}
	for line in open(fileName,'r'):
		split = line.strip().split('\t')
		query = split[0].strip()
		qid = featMan.returnId(query)
		catList = ast.literal_eval(split[6])
		for entry in catList:
			if entry not in catQueryCount:
				catQueryCount[entry] = set()
			catQueryCount[entry].add(qid)
	
	#for entry  in sorted(catQueryCount.items(), reverse=True, key = lambda x: len(x[1])):
	#	print entry[0], len(entry[1])
	return catQueryCount	
	

def loadCategoryVector(fileName):
	catVector = {}
	for line in open(fileName,'r'):
		split = line.strip().split('\t')
		catName = split[0]
		vector = ast.literal_eval(split[1])
		catVector[catName] = vector

	return catVector	


def getCats(directory):
	f1Dict = {}
	for line in os.listdir(directory):
		line = line.strip().lower();
		f1Dict[line[:line.rfind('_')]] = directory+'/'+line
	
	return f1Dict	

def getCatsWithType(directory,ttype):
	f1Dict = {}
	for line in os.listdir(directory):
		line = line.strip()
		if line.endswith(ttype):
			f1Dict[line[:line.rfind('_')]] = directory+'/'+line
	
	return f1Dict	


'''def loadPhrases(fileName):
	phrases = set()
	phrase = False
	for line in open(fileName , 'r'):
		split = line.strip().split('\t')
		if phrase and len(split[0]) > 2 and split[0] not in stopSet:
			phrases.add(split[0])
		if len(split) != 2 :
			phrase = True

	return phrases
'''
def loadPhrases(fileName):
	phrases = set();
	for line in open(fileName, 'r'):
		split = line.split('\t');
		term = split[0];
		#entDict = ast.literal_eval(split[1]);
		phrases.add(term);
	return phrases;
	
		
def loadPhrasesWithScore(fileName):
	phrases = {}
	phrase = False
	for line in open(fileName , 'r'):
		split = line.strip().split('\t')
		if phrase and len(split[0]) > 2 and split[0] not in stopSet:
			phrases[split[0]]= float(split[1])
		if len(split) != 2 :
			phrase = True

	return phrases
	

