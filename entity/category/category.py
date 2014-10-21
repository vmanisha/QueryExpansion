# -*- coding: utf-8 -*-
from utils import stopSet
import ast;
class Category:
	
	def __init__(self,fileName):
		self.phrases = {}
		'''phrase = False
		for line in open(fileName , 'r'):
			split = line.strip().split('\t')
			if phrase and len(split[0]) > 2 and split[0] not in stopSet:
				self.phrases[split[0]]= float(split[1])
			if len(split) != 2 :
				phrase = True
		self.phraseCount = 1.0*sum(self.phrases.values())
		'''
		for line in open(fileName, 'r'):
			split = line.split('\t');
			term = split[0];
			if term not in stopSet:
				entDict = ast.literal_eval(split[1]);
				self.phrases[term] = sum(entDict.values());
		self.phraseCount = 1.0*sum(self.phrases.values());
				
	#returns the phrases as a set
	def getPhraseSet(self):
		return set(self.phrases.keys())
		
	#returns total phrase count
	def getTotalPhraseCount(self):
		return self.phraseCount
	
	#probability of input phrase
	def getPhraseProb (self,iphrase):
		return self.phrases[iphrase]/self.phraseCount

	def getPhrases(self):
		return self.phrases.items()
	
	'''def rankPhrases(self):
	
	def returnTopK(self,k):
	'''