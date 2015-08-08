# -*- coding: utf-8 -*-
import sys
from entity.category.ds import loadClusters
from entity.expand.scorer import CoOccurSimScore
from utils.ds.coOccurrence import CoOccurrence
from utils.ds.coOcManager import CoOcManager
from entity.expand.catClusExpansion import ScoreClusterTerms
from queryLog import getSessionWithXML, normalize
from evaluate import addedAndRemovedTerms
import os
from queryLog import getQueryTermsStemmed
from termPrediction import getPrecRecall, getTerms, getClustPrecRecall
from plots import plotMultipleSys
from utils import stopSet
from nltk import stem
from utils import text_to_vector, loadFileInList


def toTerms(clusters):

  clustersWithTerms = []

  clusterIndex = {}
  i = 0
  for clust in clusters:
    #print clust
    terms = {}
    for entry in clust:
      split = entry.strip().split()
      for st in split:
        if len(st) > 2 and st not in stopSet:
          if st not in terms:
            terms[st] = 0.0
          terms[st] += 1.0

    total = sum(terms.values())
    for entry in terms.keys():
      terms[entry] /= total
      if entry not in clusterIndex:
        clusterIndex[entry] = []
      clusterIndex[entry].append(i)

    if len(terms) > 0:
      clustersWithTerms.append(terms)
      i += 1

  return clustersWithTerms, clusterIndex


def getTermList(queryList):
  termList = {}

  for entry in queryList:
    count = text_to_vector(entry)
    for w, c in count.items():
      #w = porter.stem(w)
      if w not in termList:
        termList[w] = 0.0
      termList[w] += c

  #print 'TermList ',len(termList), termList
  return termList.items(), set(termList.keys())


def main(argv):

  #Scorer
  coSessOccur = CoOccurrence()
  coSessOcMan = CoOcManager(argv[2], coSessOccur, ' ')
  tScorer = CoOccurSimScore(coSessOcMan)
  cScorer = ScoreClusterTerms()

  #vocab = set()
  i = 0
  prec = {}
  mrr = {}
  lim = 55

  queryList = loadFileInList(argv[5])
  termList, termDict = getTermList(queryList)
  print len(termList)
  added = 0
  oracle_prec = 0.0
  oracle_mrr = 0.0
  for tid, session, viewDocs, clickDocs, cTitle, cSummary in getSessionWithXML(
      argv[1]):
    query = session[0].strip()
    aTerms, rTerms = addedAndRemovedTerms(query, session[1:], termDict)
    if len(aTerms) > 0:
      prec1, mrr1 = getPrecRecall(termList, aTerms)
      added += 1.0
      oracle_prec += prec1
      oracle_mrr += mrr1

  print 'Oracle prec and recall ', oracle_prec / added, oracle_mrr / added

  porter = stem.porter.PorterStemmer()
  ttype = argv[6]

  print ttype

  for iFile in os.listdir(argv[3]):
    qclusters = loadClusters(argv[3] + '/' + iFile)
    clusters, clusIndex = toTerms(qclusters)

    print iFile, len(clusters)
    prec[iFile] = {}
    mrr[iFile] = {}
    added = 0.0
    i = 1
    for tid, session, viewDocs, clickDocs, cTitle, cSummary in getSessionWithXML(
        argv[1]):
      i += 1
      query = session[0].strip()
      qSet = getQueryTermsStemmed(query, porter)

      print 'Query ', query, qSet
      if ttype == 'query':
        aTerms, rTerms = addedAndRemovedTerms(query, session[1:], termDict)
      elif ttype == 'title':
        aTerms = getTerms(cTitle, qSet, termDict, porter, range(
            1, len(session) - 1))
      else:
        aTerms = getTerms(cTitle, qSet, termDict, porter, range(
            1, len(session) - 1))
        bTerms = getTerms(cSummary, qSet, termDict, porter, range(
            1, len(session) - 1))
        aTerms = aTerms | bTerms
        #aTerms,rTerms = addedAndRemovedTerms(query, session[1:], None )

      if len(aTerms) > 0:
        terms = cScorer.scoreWithIndex(qSet, clusters, clusIndex, tScorer, lim)
        #terms = cScorer.scoreWithClustPos(qSet, clusters,tScorer, lim)
        print 'TERMS', '\t', i, '\t', ttype, '\t', iFile, '\t', len(
            terms), terms
        #for topk in range(1,lim,5):
        prec1, mrr1 = getClustPrecMrr(terms, aTerms)  # returns a list
        print 'METRIC', iFile, i, prec1, mrr1
        #print topk , prec1, mrr1
        for topk in prec1.keys():
          if topk not in prec[iFile]:
            prec[iFile][topk] = []
            mrr[iFile][topk] = []

          prec[iFile][topk].append(prec1[topk])
          mrr[iFile][topk].append(mrr1[topk])

          #prec[iFile][topk] += prec1
          #mrr[iFile][topk] += mrr1
        added += 1.0
      #if i == 3:
      #	break

  for fName, scoreDict in prec.items():
    for pos in scoreDict.keys():
      print 'Prec all', fName, pos, len(scoreDict[pos])
      total = sum(scoreDict[pos])
      prec[fName][pos] = total / added  #len(scoreDict[pos])
      print 'Prec', fName, pos, prec[fName][pos], total

  for fName, scoreDict in mrr.items():
    for pos in scoreDict.keys():
      print 'Mrr all', fName, pos, len(scoreDict[pos])
      total = sum(mrr[fName][pos])
      mrr[fName][pos] = total / added  #len(scoreDict[pos])
      print 'MRR', fName, pos, mrr[fName][pos], total
  #for entry in prec.keys():
  #for t in prec[entry].keys():
  #print 'Prec',entry, t, prec[entry][t], prec[entry][t]/added
  #prec[entry][t]/=added

  #for entry in mrr.keys():
  #for t in mrr[entry].keys():
  #print 'Mrr',entry, t, mrr[entry][t], mrr[entry][t]/added
  #mrr[entry][t]/=added

  print 'Plotting Precision and MRR'

  plotMultipleSys(prec, 'No of Terms', 'Prec', argv[4] + 'prec.png',
                  'Term Prediction Prec Plot')
  plotMultipleSys(mrr, 'No of Terms', 'MRR', argv[4] + 'mrr.png',
                  'Term Prediction MRR Plot')

  #read the file and score clusters from each of the above
  #Print the precision values and MRR values
  #Plot if necessary


if __name__ == '__main__':
  main(sys.argv)
