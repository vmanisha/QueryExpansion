# -*- coding: utf-8 -*-
import ast, os
from utils import stopSet, get_cosine
from queryLog import hasAlpha
import sys
from nltk import stem

from whoosh.index import create_in
from whoosh.fields import Schema, TEXT
from whoosh.collectors import TimeLimit
from Whoosh import loadIndex, loadCollector, loadQueryParser


class TermVector:

  featDict = {}

  def __init__(self, fileName=None):
    self.vector = {}
    '''if not os.path.isdir(fileName):
			self.vector = {}
			self.loadVector(fileName)
		else:
		'''
    if fileName:
      self.vIndex, self.vsearcher = loadIndex(
          fileName, fileName[fileName.rfind('/') + 1:])
      self.vtlc = loadCollector(self.vsearcher, 1, 20)
      self.qqp = loadQueryParser(self.vIndex, 'term')

  def clear(self):
    self.vector.clear()
    self.featDict.clear()

  def createVector(self, fileName):
    porter = stem.porter.PorterStemmer()
    word_catVector = {}
    word_entVector = {}
    for line in open(fileName, 'r'):
      split = line.strip().split('\t')
      query = split[0]
      qsplit = query.split()
      spotDict = ast.literal_eval(split[1])
      for entity, elist in spotDict.iteritems():
        for oword in qsplit:
          oword = oword.replace('\'', '')
          word = porter.stem(oword)
          if len(word) > 2 and hasAlpha(word) and word not in stopSet:
            if word not in word_entVector:
              word_catVector[word] = {}
              word_entVector[word] = {}
            for cat in elist['cat'].split():
              word_catVector[word][cat] = word_catVector[word].setdefault(
                  cat, 0.0) + 1.0
            word_entVector[word][entity] = word_entVector[word].setdefault(
                entity, 0.0) + 1.0

    self.writeVector('ont/Word_catCount.txt', word_catVector)
    self.writeVector('ont/Word_entCount.txt', word_entVector)

  def indexVector(self, indexLoc, indName):
    """Indexes the vectors"""
    ischema = Schema(term=TEXT(stored=True,
                               phrase=False),
                     vector=TEXT(stored=True,
                                 phrase=False))
    if not os.path.exists(indexLoc):
      os.mkdir(indexLoc)

  #open the index
    tindex = create_in(indexLoc, schema=ischema, indexname=indName)
    writer = tindex.writer()
    i = 1
    #process each line
    for word, wvector in self.vector.iteritems():
      if len(wvector) > 0:
        try:
          writer.add_document(term = unicode(word.decode('unicode_escape').encode('ascii','ignore'))\
						, vector = unicode(str(wvector)))
        except Exception as err:
          print word, wvector
          print err, err.args
          exit()
        i += 1
        if i % 100000 == 0:
          print i

    writer.commit()
    tindex.close()

  def indexSimilarity(self, indexLoc, indName, simFile):
    """Indexes the similarity"""
    ischema = Schema(word=TEXT(stored=True,
                               phrase=False),
                     score=TEXT(stored=True,
                                phrase=False))
    if not os.path.exists(indexLoc):
      os.mkdir(indexLoc)

  #open the index
    tindex = create_in(indexLoc, schema=ischema, indexname=indName)
    writer = tindex.writer()
    i = 1
    for line in open(simFile, 'r'):
      split = line.strip().split()
      if split[0] != split[1]:
        try:
          word = unicode((split[1] + '_' + split[2]).decode(
              'unicode_escape').encode('ascii', 'ignore'))
          writer.add_document(word=word, score=unicode(str(split[2])))
        except Exception as err:
          print line
          print err, err.args
          exit()
        i += 1
        if i % 100000 == 0:
          print i

  def writeVector(self, fileName, vector):
    ofile = open(fileName, 'w')
    for word, catList in vector.iteritems():
      ofile.write(word + '\t' + str(catList) + '\n')
    ofile.close()

  def loadVector(self, fileName, delim='\t'):
    for line in open(fileName, 'r'):
      split = line.strip().split(delim)
      tempFeatDict = ast.literal_eval(split[1])
      newFeatDict = {}
      for entry, value in tempFeatDict.iteritems():
        if entry not in self.featDict:
          self.featDict[entry] = len(self.featDict)
        if value > 5:
          newFeatDict[self.featDict[entry]] = value
      if len(newFeatDict) > 0:
        self.vector[split[0]] = newFeatDict
    print 'Total entities ', len(self.featDict)

  def truncateDim(self, fileName, k, delim='\t'):
    for line in open(fileName, 'r'):
      split = line.strip().split(delim)
      tempFeatDict = ast.literal_eval(split[1])
      featVect = sorted(tempFeatDict.items(), reverse=True, key=lambda x: x[1])

      i = 0
      newFeat = {}
      for entry in featVect:
        newFeat[entry[0]] = entry[1]
        i += 1
        if i == k:
          break

      if len(newFeat) > 0:
        print split[0], '\t', newFeat

  def getSimilarity(self):
    keys = self.vector.keys()
    for i in range(len(keys)):
      v1 = self.vector[keys[i]]
      for j in range(i, len(keys)):
        v2 = self.vector[keys[j]]
        sim = get_cosine(v1, v2)
        if sim > 0:
          print keys[i], keys[j], sim

  def getVector(self, word):

    if word in self.vector:
      return self.vector[word]
    else:
      q = self.qqp.parse(unicode(word))
      try:
        self.vsearcher.search_with_collector(q, self.vtlc)
      except TimeLimit:
        print '--LONG-- ', word

      results = self.vtlc.results()

      newFeatDict = {}
      for entry in results:
        newFeatDict = ast.literal_eval(entry['vector'])
      if word not in self.vector:
        self.vector[word] = newFeatDict
      return newFeatDict


def main(argv):
  termVector = TermVector()
  #termVector.truncateDim(argv[1],int(argv[2]))
  termVector.loadVector(argv[1])
  termVector.indexVector(argv[2], argv[3])
  #termVector.getSimilarity()
  #termVector.indexSimilarity(argv[1],argv[2],argv[3])
  #termVector.getVector('pictures')
  #termVector.getVector('dawn')
  #termVector.getVector('greenland')


if __name__ == '__main__':
  main(sys.argv)
