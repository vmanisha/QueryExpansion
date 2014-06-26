
# -*- coding: utf-8 -*-
from nltk import stem
import ast
import sys
import re
from utils import SYMB
class TermFeat:
	
	def __init__(self):
		#for every term
			# category Count
			# entity count
		self.id = 1
		self.tdict = {}
		self.porter = stem.porter.PorterStemmer()
	
	#def getCatFreq(self,term,cat):
		
	#def getEntityFreq(self,term, entity):
	
		
	def findStats(self,fileName):
		for line in open(fileName,'r'):
			split = line.lower().strip().split('\t')
			split[-1] = split[-1].strip()
			try:
				entityDict = ast.literal_eval(split[-1])
				query = re.sub(SYMB, ' ',split[0]).strip()
				replaced = query
				#get the query
				for match in entityDict.keys():
					replaced = replaced.replace(match,' ')
			
				rsplit = replaced.split()
				for match, entDict in entityDict.iteritems():
					cats = entDict["cat"]		
					if len(cats) > 2:
						categories = cats.split()
						for cat in categories:
							for entry in rsplit:
								if len(entry) > 2:
									entry = self.porter.stem(entry.strip())
									if entry not in self.tdict:
										self.tdict[entry] = {}
									if cat not in self.tdict[entry]:
										self.tdict[entry][cat] = {}
									self.tdict[entry][cat][match] = self.tdict[entry][cat].setdefault(match,0.0)+1.0
			except Exception as err:
				print err , err.args
		
	
	def loadStats(self,fileName):
		for line in open(fileName,'r'):
			split = line.strip().split()
			self.tDict[split[0]] = ast.literal_eval(split[1])
			
		
	def writeStats(self,fileName):
		oFile = open(fileName, 'w')
		for term, catStats in self.tdict.iteritems():
			oFile.write(term+'\t'+str(catStats)+'\n')
		oFile.close()
				


def main(args):
	termFeat = TermFeat()
	termFeat.findStats(args[1])
	termFeat.writeStats(args[2])


if __name__ == '__main__':
	main(sys.argv)