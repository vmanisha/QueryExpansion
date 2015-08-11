# -*- coding: utf-8 -*-
from Whoosh import loadCollector, loadQueryParser, loadIndex, closeIndex
from utils import text_to_vector, stopSet
from queryLog import hasAlpha
from nltk import stem
from queryLog import getQueryTerms


class TaskExpansion:

  def __init__(self, indexName, rnker, noTasks, wordList):
    self.ranker = rnker
    #load the index
    self.index, self.searcher = loadIndex(indexName,
                                          indexName[indexName.rfind('/') + 1:])
    self.tlc = loadCollector(self.searcher, noTasks, 20)
    self.qp = loadQueryParser(self.index, 'task')
    self.porter = stem.porter.PorterStemmer()
    self.vocab = wordList

  def expandText(self, text, limit):
    #search the index
    resultSet = self.rankAndRetrieveTasks(text)
    rSort = sorted(resultSet.items(), reverse=True, key=lambda x: x[1])
    #score the terms
    termSet = self.getTaskTermSet(rSort, text)
    #print termSet
    return self.ranker.getTopKWithFilter(termSet, limit, 25)

    #return top

  def expandTextWithStep(self, text, limit1, limit2, step):
    #search the index

    resultSet = self.rankAndRetrieveTasks(text)
    rSort = sorted(resultSet.items(), reverse=True, key=lambda x: x[1])
    #score the terms
    termSet = self.getTaskTermSet(rSort, text)
    #print termSet
    scoredTerms = {}
    for i in xrange(limit1, limit2, step):
      if i == 0:
        scoredTerms[i] = self.ranker.getTopKWithFilter(termSet, i + 1, i + 50)
      else:
        scoredTerms[i] = self.ranker.getTopKWithFilter(termSet, i, i + 50)

    return scoredTerms

  def rankAndRetrieveTasks(self, query):
    #get the terms in query
    resultSet = {}

    q = self.qp.parse(query)
    try:
      self.searcher.search_with_collector(q, self.tlc)
    except Exception as err:
      print err, err.args

    results = self.tlc.results()
    for entry in results:
      resultSet[entry['task']] = entry.score
    #print 'Found', len(resultSet), 'Tasks for', query

    return resultSet

  def getTaskTermSet(self, rSort, text):

    termSet = {}
    #qterms = getQueryTerms(text);
    for entry in rSort:
      #tDict = taskDict[entry[0]]
      tDict = text_to_vector(entry[0])
      for tentry, value in tDict.iteritems():
        stem = self.porter.stem(tentry)
        if tentry not in stopSet and len(tentry) >2 and hasAlpha(tentry) \
				and (tentry not in text and stem not in text) and tentry in self.vocab:
          termSet[stem] = termSet.setdefault(stem, 0.0) + value
    #for term in termSet.keys():
    #	for qterm in qTerms:
    #		termSet[term] *=
    return termSet
    #sorted(termSet.iteritems(),reverse = True, key = lambda x : x [1])

  def closeIndex(self):
    closeIndex(self.searcher, self.index)
