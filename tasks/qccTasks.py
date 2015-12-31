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


    #argv[1] = feature file
    #argv[2] = session file
    #argv[3] = outFile
    #argv[4] = weight file
    #Test normalize
    #
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
  weightMatrix = readWeightMatrix(args.distFile)

  samePairsSet = differentPairsSet = None
  if args.pairLabelFile:
    samePairsSet , differentPairsSet =   loadPairsFromFile(args.pairLabelFile)

  total_metrics_dict = {}
  for threshold in np.arange(args.lowerLimit, args.upperLimit, 0.05):
    sessCount = 0
    lastSes = None
    session = []
    metrics = {}
    qcc = QCCTasks()
    for session in getSessionWithQuery(args.sessionFile):
      newSession = []
      if len(session) > 2:
        newSession = []
      for i in range(len(session) - 1):
        qid1, qf1 = featMan.returnFeature(session[i])
        if qf1:
          newSession.append(session[i])
      session = newSession
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
              print 'Query feature error ', session[j]
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
  #qcc.writeWeights(labels,argv[4])

  #reading and creating features
  #load the features of queries
  #for line in open(argv[1], 'r'):
  #split = line.strip().split('\t')
  #query = split[0].strip()
  #nquery = normalize(query, stemmer);
  #qVect = getDictFromSet(nquery.split())
  #if len(qVect) > 0:
  #ngrams = getNGramsAsList(nquery,2)
  ##if len(ngrams) > 0:
  ##    print query, ngrams
  #userDict = extractFeatureTuple(split[1])
  #urlDict = extractFeatureTuple(split[2],True)
  #newDict = {}
  #for entry, count in urlDict.items():
  #if entry not in gurlDict:
  #gurlDict[entry] = uid
  #uid+=1
  #newDict[gurlDict[entry]] = count;
  #
  #queryFeat = QueryFeature(ngrams, qVect, newDict, userDict)
  #featMan.addFeature(nquery,qid, queryFeat)
  #qid +=1
  ##    else:
  ##        print query
  #featMan.writeFeatures(argv[4])
  #
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

