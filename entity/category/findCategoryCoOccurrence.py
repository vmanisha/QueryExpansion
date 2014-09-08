# -*- coding: utf-8 -*-
#from coOccurrence import CoOccurrence
#from utils import SYMB, stopSet, loadFileInDict
#from queryLog import hasAlpha
import sys,re
import ast
from nltk import stem
#from bayes.objCoOccurrence import ObjCoOccurrence

def main(argv):
	#catCoOcc = {}
	#porter = stem.porter.PorterStemmer()
	i = 0
	#toCount = []
	#toKeep = loadFileInDict(argv[2])
	#print len(toKeep)
	#toCount = {}
	
	#cooccur = CoOccurrence()
	#entTermCo = ObjCoOccurrence()
	#entCatCo = ObjCoOccurrence()
	catEntVector = {}
	#entEntCo = ObjCoOccurrence()
	
	for line in open(argv[1],'r'):
		split = line.lower().strip().split('\t')
		split[-1] = split[-1].strip()
		try:
			entityDict = ast.literal_eval(split[-1])
			#query = re.sub(SYMB, ' ',split[0]).strip()
			#query = re.sub('\s+',' ',query)
			#qsplit = query.strip().split()
			#toCount = []
			#for qRep in qsplit:
			#	qRep = porter.stem(qRep.strip())
			#	if len(qRep) > 2 and qRep not in stopSet and hasAlpha(qRep):
			#		toCount.append(qRep)
			#if len(toCount) > 1.0:
				#cooccur.updateStatsFromList(toCount,toKeep)

			entSet = entityDict.keys()
			for entry, attDict in entityDict.iteritems():
				cat = attDict['cat']
				for category in cat.split():
					if category not in catEntVector:
						catEntVector[category] = {}
					for entity in entSet:
						catEntVector[category][entity] = catEntVector[category].setdefault(entity,0.0)+ 1.0
					
			'''for entity, pDict in entityDict.iteritems():
				if 'cat' in pDict:
					for cat in pDict['cat'].split():
						entCatCo.updateStats(cat, entity,1.0)
				newQuery = query.replace(entity,' ')
				newQuery = re.sub('\s+', ' ', newQuery)
				if len(newQuery) > 2:
					for term in newQuery.split():
						if len(term) > 2 and term not in stopSet and hasAlpha(term):
							entTermCo.updateStats(entity, term,1.0)
			'''		
			#get the query
			'''for match, entDict in entityDict.iteritems():
				cats = entDict["cat"]
				if len(cats) > 2:
					categories = cats.split()
					#rho = entDict["score"]
					qrep = query.replace(match," _CAT_ ")
					qsplit = qrep.strip().split()
					toCount = []
					for qRep in qsplit:
						qRep = porter.stem(qRep.strip())
						if len(qRep) > 2 and qRep not in stopSet and hasAlpha(qRep):
							toCount.append(qRep)
					if len(toCount) > 1.0:
						for cat in categories:
							#print cat, toCount
							if cat not in catCoOcc:
								catCoOcc[cat] = CoOccurrence()
							catObj = catCoOcc[cat]
							catObj.updateStatsFromList(toCount,toKeep)
						
						#print catCoOcc[cat].toStringList()
			'''		
			i +=1
			if i % 100000 == 0:
				print i
			
		except Exception as err:
			print err, err.args
	
	#write co-occurrence bit
	#cFile = open('EntCatCoOccurrence.txt','w')
	#for entry in entCatCo.toStringList():
	#	cFile.write(entry+'\n')
	#cFile.close()
	
	#cFile = open('EntTermCoOccurrence.txt','w')
	#for entry in entTermCo.toStringList():
	#	cFile.write(entry+'\n')
	#cFile.close()
	
	cFile = open('EntCatVector.txt','w')
	for entry, vector in catEntVector.iteritems():
		cFile.write(entry+'\t'+str(vector)+'\n')
	cFile.close()
	
	
	'''for cat in catCoOcc.keys():
		for entry in catCoOcc[cat].toStringList():
			cFile.write(cat+' '+entry+'\n')
	cFile.close()
	'''
	'''
	for entry, freq in toCount.iteritems():
		if freq > 2:
			print entry, freq
	'''
if __name__ == '__main__':
	main(sys.argv)
