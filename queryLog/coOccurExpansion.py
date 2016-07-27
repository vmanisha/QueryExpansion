# -*- coding: utf-8 -*-
from utils import loadFileInDict, stopSet, ashleelString
from queryLog import hasAlpha
from nltk import stem


class CoOccurExpansion:

  def __init__(self, coOcManager, termFile, rank):
    self.coMan = coOcManager
    #self.termList = loadFileInDict(termFile);
    self.ranker = rank
    self.porter = stem.porter.PorterStemmer()

  def expandText(self, query, limit):
    qsplit = query.split()
    querySet = set(qsplit)
    stemSet = [self.porter.stem(entry.strip()) for entry in querySet]
    neigbhours = self.getCoOccuringTerms(stemSet)

    termScore = {}
    for entry in neigbhours:
      if entry not in querySet and entry not in stemSet:
        termScore[entry] = self.getCoOcScore(stemSet, entry)

    scoredTerms = self.ranker.getTopKWithFilter(termScore, limit, limit + 50)
    return scoredTerms

  def expandTextWithStep(self, query, limit1, limit2, step):
    qsplit = query.split()
    querySet = set(qsplit)
    stemSet = [self.porter.stem(entry.strip()) for entry in querySet]
    neigbhours = self.getCoOccuringTerms(stemSet)
    termScore = {}
    for entry in neigbhours:
      if entry not in querySet and entry not in stemSet:
        termScore[entry] = self.getCoOcScore(stemSet, entry)
    scoredTerms = {}
    for i in xrange(limit1, limit2, step):
      if i == 0:
        scoredTerms[i] = self.ranker.getTopKWithFilter(termScore, i + 1, i + 50)
      else:
        scoredTerms[i] = self.ranker.getTopKWithFilter(termScore, i, i + 50)

    return scoredTerms

  def getCoOccuringTerms(self, stemSet):
    neighbours = set()
    for entry in stemSet:
      for n in self.coMan.getNeighbours(entry):
        if n not in neighbours and len(n) > 2 and n not in ashleelString:
          neighbours.add(n)
    return neighbours

  def getCoOcScore(self, stemSet, phrase):
    total = 0.0
    tCount = 0.0
    for qRep in stemSet:
      #stem the term
      #get PMI
      if len(qRep) > 2 and qRep not in stopSet and hasAlpha(qRep):
        #total += self.coMan.getPMI(phrase, qRep,50)
        c1, c2 = self.coMan.getCoOcCount(phrase, qRep)
        if c1 != c2:
          print ':O CoOcc count diff ', phrase, qRep, c1, c2
        total += c1
        tCount += 1.0
    if tCount > 0:
      return total / tCount
    return 0
