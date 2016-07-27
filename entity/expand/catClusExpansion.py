# -*- coding: utf-8 -*-
from nltk.stem import porter
from queryLog import normalize
from utils import getDictFromSet, get_cosine


class ScoreClusterTerms:

  def __init__(self):
    print 'Initializing cluster expansion'
    self.stemmer = porter.PorterStemmer()

  def scoreWithCosine(self, qSet, clustList, cIndex, limit):
    toEvaluate = []
    done = set()
    for entry in qSet:
      try:
        clusters = cIndex[entry]
        #print 'CLUSTERS',entry, clusters
        for cind in clusters:
          if cind not in done:
            toEvaluate.append(clustList[cind])
            done.add(cind)
      except:
        pass

    #for each cluster find cosine similarity
    clustScore = {}
    i = 0
    qDict = getDictFromSet(qSet)
    for clust in toEvaluate:
      cos = get_cosine(qDict, clust)
      if cos > 0:
        clustScore[i] = cos
      i += 1

    toReturn = []
    for entry in sorted(clustScore.items(), reverse=True, key=lambda x: x[1]):
      toReturn.append(toEvaluate[entry[0]].keys())

    return toReturn

  def scoreWithIndex(self, qSet, clustList, cIndex, scorer, limit):
    toEvaluate = []
    done = set()
    for entry in qSet:
      try:
        clusters = cIndex[entry]
        #print 'CLUSTERS',entry, clusters
        for cind in clusters:
          if cind not in done:
            toEvaluate.append(clustList[cind])
            done.add(cind)
      except:
        pass

    if len(toEvaluate) > 0:
      #return self.score(qSet,toEvaluate,scorer, limit)
      return self.scoreWithClustPos(qSet, toEvaluate, scorer, limit)
    return []

  def scoreWithClustPos(self, qSet, clustList, scorer, limit):
    i = 0
    scores = {}  #contains score of clusters
    order = {}  #contains the order of terms

    for clust in clustList:

      count = len(qSet & set(clust.keys()))

      score, cterms = scorer.score(qSet, clust)

      sTerms = sorted(cterms.items(), reverse=True, key=lambda x: x[1])
      #print qSet, score, clust, sTerms
      #for entry in sTerms:
      #if entry[0] not in qSet and entry[1] > 0.0:
      #if entry[0] not in terms:
      #terms[entry[0]]= 0.0
      #terms[entry[0]]+= round(score*entry[1],2)

      order[i] = []
      for entry in sTerms:
        if entry[0] not in qSet and entry[1] > 0.0:
          order[i].append(entry)
          if len(order[i]) > limit:
            break
      scores[i] = score * count
      i += 1

    topTerms = []
    covered = {}
    k = 0
    prevKeys = set()
    for entry in sorted(scores.items(), reverse=True, key=lambda x: x[1]):
      ##print entry
      if entry[1] > 1.0:
        #currKeys = set([x[0] for x in order[entry[0]]])
        #if len(currKeys - prevKeys) > 0:
        #print 'SCORE ',entry , len(order[entry[0]]),order[entry[0]][:min(5,len(order[entry[0]]))]
        for x in order[entry[0]]:
          if x[0] not in covered and x[1] > 0.05:
            covered[x[0]] = 0.0
            topTerms.append(x[0])
            if len(topTerms) >= limit:
              break
            #covered[x[0]]+=entry[1] * x[1]
        k += 1
        #prevKeys = currKeys
      if k == 1:
        break

      #for entry in sorted(covered.items(),reverse = True, key = lambda x : x[1]):
      #topTerms.append(entry[0])
      #if len(topTerms) > limit:
      #break

    print 'SENDING ', qSet, len(topTerms), topTerms
    return topTerms

  def score(self, qSet, clustList, scorer, limit):
    i = 0
    scores = {}  #contains score of clusters
    order = {}  #contains the order of terms

    terms = {}

    for clust in clustList:
      score, cterms = scorer.score(qSet, clust)
      #if score > 0 and len(terms) < 15:
      #	print qSet, score, terms
      sTerms = sorted(cterms.items(), reverse=True, key=lambda x: x[1])
      #print qSet, score, clust, sTerms
      #order[i] = []
      #for entry in sTerms:
      #if entry[0] not in qSet and entry[1] > 0.0:
      #order[i].append(entry)
      #if len(order[i]) > limit:
      #break

      #score/=(1.0*len(clust))
      #scores[i]= score
      for entry in sTerms:
        if entry[0] not in qSet and entry[1] > 0.0:
          if entry[0] not in terms:
            terms[entry[0]] = 0.0
          terms[entry[0]] += round(score * entry[1], 2)
      i += 1

    topTerms = []
    covered = {}
    for entry in sorted(terms.items(), reverse=True, key=lambda x: x[1]):
      if entry[0] not in covered:
        if entry[1] > 0.0:
          topTerms.append(entry)
          covered[entry[0]] = 1

      if len(topTerms) > limit:
        break
    #for entry in sorted(scores.items(), reverse = True, key = lambda x : x[1]):
    ##print entry
    ##if entry[1] > 0.0 and len(order[entry[0]]) < 15:
    ##	print qSet, entry, order[entry[0]]
    #
    #for x in order[entry[0]]:
    #if x[0] not in covered:
    ##if x[1] > 0.0:
    #topTerms.append(x)
    #covered[x[0]] = 1
    #
    #if len(topTerms) > limit:
    #break
    #if len(topTerms) > limit:
    #break
    #print query, topTerms
    return topTerms
