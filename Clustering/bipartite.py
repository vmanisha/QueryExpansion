import sys
import os
import numpy as np
import ast
import igraph
from igraph import Graph


'''
Bipartite clustering of two node types with edges
'''
def loadTasks(fileName,ttype):
	taskEntityScore = {}
	idTaskDict = {}
	idEntityDict = {}
	taskIdDict = {}
	entityIdDict = {}

	tId = 0
	eId = 0
	for line in open(fileName,'r'):
		split = line.strip().split('\t')
		taskDict = ast.literal_eval(split[-1])
		#load the tasks and entity vector
		for task, entityList in taskDict[ttype]['tasks'].iteritems():
			#format task : {entity : {score: , match : }, entity : {score: , match :}}
			taskString = '\t'.join(task)
			if taskString not in taskIdDict:
				ntId = 't'+str(tId)
				taskEntityScore[ntId] = {}
				taskIdDict[taskString]=ntId
				idTaskDict[ntId] = taskString
				tId += 1
			for entity in entityList.keys():
				entityString = str(entity)
				if entityString not in entityIdDict:
					neId = 'e'+str(eId)
					entityIdDict[entityString] = neId
					idEntityDict[neId] = entityString
					eId += 1
				
				taskEntityScore[taskIdDict[taskString]][entityIdDict[entityString]]= entityList[entity]['score']
			#print taskString, entityString, taskIdDict[taskString], entityIdDict[entityString], taskEntityScore[taskIdDict[taskString]]
	print tId, eId, len(idTaskDict), len(idEntityDict)
	return taskEntityScore, idTaskDict, idEntityDict

#for the TagMe tagged queries
def loadQueries(fileName):
	taskIdDict = {}
	entityIdDict = {}
	idTaskDict = {}
	idEntityDict = {}
	taskEntityScore = {}
	tId = 0
	eId = 0

	for line in open(fileName,'r'):
		split = line.strip().split('\t')
		query = split[2]
		#print query
		if query not in taskIdDict:
			ntId = 'q'+str(tId)
			taskIdDict[query] = ntId
			idTaskDict[ntId] = query
			taskEntityScore[ntId] = {}
			tId += 1

		taggedResults = ast.literal_eval(split[-1])
		for annotation in taggedResults["annotations"]:
			score = float(annotation["rho"])
			if 'dbpedia_categories' in annotation:
				for category in annotation["dbpedia_categories"]:
					if category not in entityIdDict:
						neId = 'c'+str(eId)
						idEntityDict[neId] = category
						entityIdDict[category] = neId
						eId += 1
					
					neId = entityIdDict[category]	
					ntId = taskIdDict[query]
					if category not in taskEntityScore[ntId]:
						taskEntityScore[ntId][neId] = 0.0
					
					taskEntityScore[ntId][neId] += score
					#print taskIdDict[query], entityIdDict[category], score, taskEntityScore[taskIdDict[query]][entityIdDict[category]]
				#print taskIdDict[query], entityIdDict[category], score , taskEntityScore[taskIdDict[query]]

	return taskEntityScore, idTaskDict, idEntityDict

def buildTransitionMatrix(taskList):
	#converting it into probability
	
	for task in taskList.keys():
		esum = sum(taskList[task].values())
		for entry in taskList[task].keys():
			entityScore[entity] /= esum

		
#Initially thought of random walk but
#def runBackwardRandomWalk(transMatrix, steps, selfProb):
#def clusterWalkResults(finalMatrix):

def buildGraph(taskList,tsize,eList):
	
	G = Graph(tsize+len(eList), directed=False)
	G.vs['name'] = taskList.keys() + eList
	G.vs["type"] = 0
	G.vs[tsize:]["type"] = 1
	for task,entityList in taskList.iteritems():
		for entity, score in entityList.iteritems():
			#a dict -- entity: score
			#print task, entity
			G[task,entity] = score
	#print G	
	#print G.is_bipartite()
	return G		
	
def clusterGraph(biGraph):
	#comm = biGraph.community_leading_eigenvector(clusters=5000)
	comm = biGraph.community_walktrap(steps=4)
	#for entry in comm:
	#	print entry
	#biGraph.community_leading_eigenvector(clusters=1000)
	return comm


def writeClusters(biGraph,comm,taskDict, entityDict,fileName):
	oFile = open(fileName,'w')
	i = 0
	print 'CLUSTERING'
	for entry in comm:
		oFile.write(str(i)+'\t')
		for k in range(len(entry)):
			taskId = biGraph.vs[entry[k]]['name']
			if taskId in taskDict:
				print i, k, entry[k], taskId, taskDict[taskId]
				oFile.write(taskDict[taskId]+',\t')
			#else:
			#	oFile.write(entityDict[taskId]+'\t')
		i+= 1
		oFile.write('\n')
		
	oFile.close()
				
		
def main(argv):
	#taskEntityScore, taskDict, entityDict = loadTasks(argv[1],argv[2])
	taskEntityScore, taskDict, entityDict = loadQueries(argv[1])
	biGraph  =  buildGraph(taskEntityScore,len(taskDict),entityDict.keys())
	#finalMatrix = runBackwardRandomWalk(transMatrix,steps, selfProb)	
	clusters =  clusterGraph(biGraph)
	#clusters = clusterWalkResults(finalMatrix)
	writeClusters(biGraph,clusters,taskDict, entityDict, 'Bi-PartiteClustering_tagMe'+'.txt')
	
if __name__ == "__main__":
	main(sys.argv)
