# -*- coding: utf-8 -*-
import os, sys, ast
from utils import getDictFromSet, getNGramsAsList
import networkx as nx
from queryLog import normalize, getSessionWithQuery
from features.logAnalysis import extractFeatureTuple
from features.queryFeature import *
from features.featureManager import FeatureManager
import math
from nltk import stem
import numpy as np
from features import toString, readWeightMatrix
from clustering.evaluate.external import getRecallPrecision
import argparse as ap
from entity.category.findCategoryClusters import loadPairsFromFile, getPairLabelsFromClusters, mergeMetrics, computeAverageAndVarianceOfMetrics

'''#load features #load session #find connected components
'''


def sortPair(id1, id2):
  if id1 < id2:
    return id1, id2
  else:
    return id2, id1


class QCCTasks:

  def __init__(self):
    self.G = nx.Graph()
    self.pairCount = {}

  def addEdge(self, q1, q2, score):
    #print q1, q2, score;
    self.G.add_edge(q1, q2, weight=score)

    a, b = sortPair(q1, q2)
    if a in self.pairCount:
      if b not in self.pairCount[a]:
        self.pairCount[a][b] = 1.0
      else:
        self.pairCount[a][b] += 1.0
    else:
      self.pairCount[a] = {}
      self.pairCount[a][b] = 1.0

  def normalizeScores(self):
    edgeList = self.G.edges()
    for entry in edgeList:
      print entry

  def getTaskComponents(self):
    entries = len(self.G.nodes())
    print entries
    if entries > 1:
      taskList = nx.connected_components(self.G)
      #print taskList
      #convert to clustering measure format
      #labels = getClusterFormat(taskList,entries)
      #print 'Connected Components' , taskList, labels
      return taskList
    return []

  def writeWeights(self, labels, fileName):
    #for each edge write the weights
    outFile = open(fileName, 'w')
    for line in labels:
      outFile.write(str(line) + '\n')

    outFile.write('\n')
    for n, nbrs in self.G.adjacency_iter():
      for nbr, eattr in nbrs.items():
        data = eattr['weight']
        outFile.write(str(n) + ' ' + str(nbr) + ' ' + str(data) + '\n')
    outFile.close()


if __name__ == '__main__':

  parser = ap.ArgumentParser(description = 'Generate clusters of'+ \
                        'Lucchesse QCC tasks')
  parser.add_argument('-f', '--featFile', help='Feature file', required=True)
  parser.add_argument('-d', '--distFile', help='Pairwise Similarity file',\
                    required=True)
  parser.add_argument('-o', '--outDir', help='Output Directory', \
                    required=True)
  parser.add_argument('-a', '--algo', help='qcc', \
                    required=True)
  parser.add_argument('-l', '--lowerLimit', help='min limit on #terms in '+\
                    'cluster', required=True,type=float)
  parser.add_argument('-u', '--upperLimit', help='upper limit on #terms in'+\
                    ' cluster', required=True,type=float)
  parser.add_argument('-s', '--sessionFile', help='Session file containing'+\
                    ' queries', required=True)
  parser.add_argument('-p', '--pairLabelFile', help='Task labels for a'+\
                    ' pair of queries, same_task and different_task',\
                     required=False)

  args = parser.parse_args()

  qcc = QCCTasks()
  featMan = FeatureManager()

  #stemmer = stem.porter.PorterStemmer()
  featMan.readFeatures(args.featFile)
  # Loads the distance between two queries (i.e. 1-similarity)
  weightMatrix = readWeightMatrix(args.distFile)
  print len(weightMatrix)
  samePairsSet = differentPairsSet = None
  if args.pairLabelFile:
    samePairsSet , differentPairsSet =   loadPairsFromFile(args.pairLabelFile)

  total_metrics_dict = {}
  for threshold in np.arange(args.lowerLimit, args.upperLimit, 0.02):
    sessCount = 0
    lastSes = None
    session = []
    metrics = {}
    qcc = QCCTasks()
    for session in getSessionWithQuery(args.sessionFile):
      #calculate the score
      for i in range(len(session) - 1):
        qid1, qf1 = featMan.returnFeature(session[i])
        if qf1:
          for j in range(i + 1, len(session)):
            qid2, qf2 = featMan.returnFeature(session[j])
            if qf2:
              try:
                if qid1 < qid2:
                  edgeScore = 1.0 - weightMatrix[qid1][qid2]
                else:
                  edgeScore = 1.0 - weightMatrix[qid2][qid1]
                if edgeScore > threshold:
                  qcc.addEdge(qid1, qid2, edgeScore)
              except:
                pass
        else:
            print 'Query feature error ', session[i]
      sessCount += 1
    labels = qcc.getTaskComponents()
    fname = args.outDir + '_'+args.algo+'_' + str(threshold) + '.txt'
    outFile = open(fname, 'w')

    for entry in labels:
      string = ''
      for qid in entry:
        string += featMan.returnQuery(qid) + '\t'
      outFile.write(string.strip() + '\n')
    outFile.close()
    predicted_same_pairs, predicted_different_pairs=\
     getPairLabelsFromClusters(labels,featMan)
    metrics[threshold] = getRecallPrecision(samePairsSet, differentPairsSet, predicted_same_pairs, predicted_different_pairs)
    for tcount, met in metrics.items():
      print tcount, met
    mergeMetrics(total_metrics_dict, metrics)
  computeAverageAndVarianceOfMetrics(args.algo, total_metrics_dict)

  #qcos, ucos, userCos, sessionCos, ngramCos, entCos, \
  #catCos,typeCos = qf1.findCosineDistance(qf2)
  #qjac = qf1.findJacardDistance(qf2)
  ##qedit = qf1.findEditDistance(qf2)
  ##normalized distance
  ##dist = (j - i)#*1.0/len(session)
  ##oFile.write(str(qid1)+'\t'+str(qid2)+'\t'+\
  ##str(round(qcos,2))+'\t'+str(round(qjac,2))+'\t'+\
  ##str(round(ngramCos,2))+'\t'+str(round(userCos,2))+'\t' + \
  ##str(round(entCos,2))+'\t'+ str(round(catCos,2))+\
  ##'\t'+ str(round(sessionCos,2))+'\t'+ str(round(typeCos,2))+'\n')
  #edgeScore = (15*((qcos + qjac )/2.0) +\
  #12.5*ngramCos + 12.5*ucos + 15*sessionCos +\
  #15*userCos + 10*entCos + 10*catCos+ 10*typeCos)
