import sys
import os
import numpy as np
import ast
import igraph
from igraph import Graph
'''Bipartite clustering of two node types with edges
'''


def buildGraph(taskList, tsize, eList):

  G = Graph(tsize + len(eList), directed=False)
  G.vs['name'] = taskList.keys() + eList
  G.vs['type'] = 0
  G.vs[tsize:]['type'] = 1
  for task, entityList in taskList.iteritems():
    for entity, score in entityList.iteritems():
      #a dict -- entity: score
      #print task, entity
      G[task, entity] = score
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


def writeClusters(biGraph, comm, taskDict, entityDict, fileName):
  oFile = open(fileName, 'w')
  i = 0
  print 'CLUSTERING'
  for entry in comm:
    oFile.write(str(i) + '\t')
    for k in range(len(entry)):
      taskId = biGraph.vs[entry[k]]['name']
      if taskId in taskDict:
        print i, k, entry[k], taskId, taskDict[taskId]
        oFile.write(taskDict[taskId] + ',\t')
      #else:
      #	oFile.write(entityDict[taskId]+'\t')
    i += 1
    oFile.write('\n')

  oFile.close()


def main(argv):
  #taskEntityScore, taskDict, entityDict = loadTasks(argv[1],argv[2])

  biGraph = buildGraph(taskEntityScore, len(taskDict), entityDict.keys())
  #finalMatrix = runBackwardRandomWalk(transMatrix,steps, selfProb)
  clusters = clusterGraph(biGraph)
  #clusters = clusterWalkResults(finalMatrix)
  writeClusters(biGraph, clusters, taskDict, entityDict,
                'Bi-PartiteClustering_tagMe' + '.txt')


if __name__ == "__main__":
  main(sys.argv)
