# -*- coding: utf-8 -*-
from queryLog import parseLine, hasAlpha, QUERY, CLICKU
from utils import stopSet, ashleelString
import sys, ast
from utils.ds.word import Word
from nltk.stem import porter
from features.featureManager import FeatureManager
import argparse as ap

def readWeightMatrix(fileName):
  weightMatrix = {}
  lbreak = False
  for line in open(fileName, 'r'):
    if len(line) < 20 and (not lbreak):
      lbreak = True

    if lbreak:
      split = line.split()
      i = int(split[0])
      if i not in weightMatrix:
        weightMatrix[i] = {}
      try:
        weightMatrix[i][int(split[1])] = 1.0 - round(float(split[-1]) / 100, 2)
      except:
        print 'Error reading ', line

  return weightMatrix


def toString(eset, featMan):
  string = ''
  for entry in eset:
    string += '\t' + str(featMan.returnQuery(entry))
  return string.strip()


def toList(eset, featMan):
  elist = []
  for entry in eset:
    elist.append(str(featMan.returnQuery(entry)))

  return elist


def findClickQuery(fileName):
  """load clicked queries"""
  porter1 = porter.PorterStemmer()
  clickQuery = {}
  for line in open(fileName, 'r'):
    entry = parseLine(line.strip())
    if len(entry) > 3:
      terms = entry[QUERY].split()
      for term in terms:
        nterm = porter1.stem(term)
        if len(term) > 2 and hasAlpha(term) and term not in ashleelString and \
				nterm not in stopSet and nterm not in ashleelString:
          if nterm not in clickQuery:
            clickQuery[nterm] = {}
          clickQuery[nterm][entry[CLICKU]] = clickQuery[nterm].setdefault(
              entry[CLICKU], 0.0) + 1.0

  for entry, cdict in clickQuery.iteritems():
    print entry, '\t', cdict

  return clickQuery


def loadClickedTerms(fileName):
  termClickDict = {}
  for line in open(fileName, 'r'):
    split = line.strip().split('\t')
    termClickDict[split[0]] = ast.literal_eval(split[-1].strip())
  return termClickDict


def calWordFeatures(fileName, clickQuery):
  wordStats = {}
  porter1 = porter.PorterStemmer()
  for line in open(fileName, 'r'):
    split = line.strip().split('\t')
    query = split[0]

    #find candidate nonEntity Term
    qsplit = query.split()
    toCheck = set()
    for term in qsplit:
      term = porter1.stem(term)
      if len(term) > 2 and term not in stopSet and term not in ashleelString:
        toCheck.add(term)

    #find the entities
    spotDict = ast.literal_eval(split[-1])
    entities = {}
    entString = ' '.join(spotDict.keys())
    #find the categories
    categories = []
    for entity in spotDict:
      categories += spotDict[entity]['cat'].split()
      entities[entity] = spotDict[entity]['score']

    for term in toCheck:
      if term not in wordStats:
        wordStats[term] = Word(term)

      inEnt = 1.0 if term in entString else 0
      clicked = 1.0 if term in clickQuery else 0
      print toCheck - set([term]), term, toCheck
      wordStats[term].updateStats(categories, inEnt, entities,
                                  toCheck - set([term]), clicked)

  for word, wObj in wordStats.iteritems():
    print word, wObj.string()


def mergeQueryCountS(file1, file2):
  counts = {}
  for line in open(file1, 'r'):
    split = line.strip().split('\t')
    query = split[0].lower().strip()
    if query not in counts:
      counts[query] = int(split[1])
    else:
      counts[query] += int(split[1])

  for line in open(file2, 'r'):
    split = line.strip().split('\t')
    query = split[0].lower().strip()
    if query not in counts:
      counts[query] = int(split[1])
    else:
      counts[query] += int(split[1])

  for entry, freq in counts.iteritems():
    print entry, '\t', freq


def findPairwiseDistance(featureFile, outFile):
  featMan = FeatureManager()

  featMan.readFeatures(featureFile)
  featDict = featMan.featureDict

  oFile = open(outFile, 'w')
  #oFile1 = open('feature-wise-similarity.txt','w')

  ids = featDict.keys()
  keys = sorted(ids)
  print len(keys), keys[-5:]
  for i in range(0, len(keys) - 1):
    qid1, qf1 = featMan.returnFeature(keys[i])
    for j in range(i + 1, len(keys)):
      qid2, qf2 = featMan.returnFeature(keys[j])
      qcos, ucos, userCos, sessionCos, ngramCos, entCos, \
			catCos,typeCos = qf1.findCosineDistance(qf2)
      qjac = qf1.findJacardDistance(qf2)
      #qedit = qf1.findEditDistance(qf2)
      #normalized distance
      #dist = (j - i)#*1.0/len(session)
      #oFile1.write(str(qid1)+'\t'+str(qid2)+'\t'+\
      #str(round(qcos,2))+'\t'+str(round(qjac,2))+'\t'+\
      #str(round(ngramCos,2))+'\t'+str(round(userCos,2))+'\t' + \
      #str(round(entCos,2))+'\t'+ str(round(catCos,2))+\
      #'\t'+ str(round(sessionCos,2))+'\t'+ str(round(typeCos,2))+'\n')
      edgeScore = (15*((qcos + qjac )/2.0) +\
			12.5*ngramCos + 12.5*ucos + 15*sessionCos +\
			15*userCos + 10*entCos + 10*catCos+ 10*typeCos)
      if edgeScore > 25:
        #print session[i], session[j], edgeScore, qcos, qjac, ucos, userCos, qedit
        #print qid1, qid2, round(edgeScore,3)
        oFile.write(
            str(qid1) + ' ' + str(qid2) + ' ' + str(round(edgeScore, 3)) + '\n')
  oFile.close()


def main(argv):
  parser = ap.ArgumentParser(description = 'Generate word level features and\
          compute pairwise distance between two queries.')
  parser.add_argument('-o', '--oFile', help='Output feature file', required=True)
  parser.add_argument('-f', '--featureFile', help='File containing features', required=True)

  args = parser.parse_args()
  #clickedInfo = loadClickedTerms(argv[1])
  #calWordFeatures(argv[2], clickedInfo)
  #mergeQueryCountS(argv[1],argv[2])
  findPairwiseDistance(args.featureFile, args.oFile)


if __name__ == '__main__':
  main(sys.argv)
