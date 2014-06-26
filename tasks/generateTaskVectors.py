import ast
# -*- coding: utf-8 -*-
#for each task
	#find top K tasks
	#find cosine similarity
	#
import sys
from utils import stopSet, get_cosine, ashleelString
from queryLog import hasAlpha

from nltk.stem import porter
class TaskManager:
	
	def __init__(self, fileName,taskType):
		#self.index, self.searcher = loadIndex(indexName, indexName[indexName.rfind('/')+1:])
		#self.tlc = loadCollector(self.searcher, noTasks, 20)
		#self.qp  = loadQueryParser(self.index,'task')
		self.tClust = {}
		self.porter = porter.PorterStemmer()
		
		self.taskList = {}
		for line in open(fileName,'r'):
			split= line.strip().split('\t')
			#sId = int(split[0])
			#uId = int(split[1])
			tasks = ast.literal_eval(split[-1])
			mulTasks = tasks[taskType]['tasks'].keys()
			for entry in mulTasks:
				if entry not in self.taskList:
					self.taskList[entry] = 0.0
				self.taskList[entry] +=1.0
	
	def clusterTasks(self,thresh):
		merged = False
		for tTuple , freq in self.taskList.iteritems():
			tvector=self.getVectorFromTuple(tTuple)
			
			for word , freq in tvector.iteritems():
				self.tClust[word] = self.tClust.setdefault(word,0.0) + freq
			'''cTaskDict = self.tClust.items()
			for cid, entry in cTaskDict:
				sim = self.getSimilarity (tvector, entry)
				if sim > thresh:
					self.tClust[cid] = self.merge(entry, tvector)
					merged = True				
			if not merged:
				self.tClust[len(self.tClust)] = tvector
			'''

	def getVectorFromTuple(self,tTuple):
		tDict = {}
		#print tTuple
		
		for entry in tTuple:
			split = entry.split()
			for unstem in split:
				word = self.porter.stem(unstem)
				if word not in stopSet and hasAlpha(word) and len(word) > 2 and word not in ashleelString:
					tDict[word]=tDict.setdefault(word,0.0)+1.0
		#print tDict
		return tDict
		
	def printTaskCluster(self):
		for entry, tasks in self.tClust.iteritems():
			print entry, tasks
			#print entry , '\t','\t'.join('{0}:{1}'.format(x,y) for x,y in tasks.iteritems())
		
	def merge(self, cluster, task):
		for entry, val in task.iteritems():
			cluster[entry] = cluster.setdefault(entry,0.0) + val
			
		return cluster
	
	def getSimilarity(self, tDict, entry):
		return get_cosine(tDict,entry)


def main(argv):
	tManager = TaskManager(argv[1],argv[2])
	tManager.clusterTasks(float(argv[3]))
	tManager.printTaskCluster()


if __name__ == '__main__':
	main(sys.argv)