# -*- coding: utf-8 -*-
import ast
from utils import stopSet
from queryLog import hasAlpha
import sys
from nltk import stem
class TermVector:
	
	def __init__(self):
		self.vector = {}
	
	def createVector(self, fileName):	
		porter = stem.porter.PorterStemmer()
		word_catVector = {}
		word_entVector = {}
		for line in open(fileName,'r'):
			split = line.strip().split('\t')
			query = split[0]
			qsplit = query.split()
			spotDict = ast.literal_eval(split[1])
			for entity, elist in spotDict.iteritems():
					for oword in qsplit:
						word = porter.stem(oword)
						if len(word) > 2 and hasAlpha(word) and word not in stopSet:
							if word not in word_entVector:
								word_catVector[word] = {}
								word_entVector[word] = {}
							for cat in elist['cat'].split():
								word_catVector[word][cat] = word_catVector[word].setdefault(cat,0.0)+1.0
							word_entVector[word][entity] = word_entVector[word].setdefault(entity,0.0)+1.0
		
		self.writeVector('ont/Word_catCount.txt',word_catVector)
		self.writeVector('ont/Word_entCount.txt',word_entVector)		
	
	def writeVector(self,fileName, vector):
		ofile = open(fileName,'w')
		for word, catList in vector.iteritems():
			ofile.write(word+'\t'+str(catList)+'\n')
		ofile.close()	
		

	def loadVector(self, fileName,delim='\t'):
			
		for line in open(fileName, 'r'):
			split = line.strip().split(delim)
			self.vector[split[0]] = ast.literal_eval(split[1])
	
	def returnVector(self, word):			
		if word in self.vector:
			return self.vector[word]
		else:
			return None
			
def main(argv):
	termVector = TermVector()
	termVector.createVector(argv[1])
	
	
if __name__ == '__main__':
	main(sys.argv)