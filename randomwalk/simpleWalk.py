# -*- coding: utf-8 -*-
import networkx as nx
from queryLog import getSessionWithQuery
from utils import allLetters
import sys
from utils import loadFileInList
from queryLog import stemQuery
from nltk import stem


class SimpleWalk:

  def __init__(self):
    self.graph = nx.Graph()

  def addEdge(self, word1, word2, score):
    if word1 != word2:
      if self.graph.has_edge(word1, word2):
        self.graph[word1][word2]['weight'] += score
      else:
        self.graph.add_edge(word1, word2, weight=score)

  def filter(self, thresh):
    filtered = nx.Graph([(u, v, d) for u, v, d in self.graph.edges(data=True)
                         if d['weight'] > thresh])

    self.graph = filtered

  def printAdjMatrix(self):
    for entry, neigh in self.graph.adjacency_iter():
      print entry, '\t', neigh

  def walk(self):
    #return nx.algorithms.link_analysis.pagerank(self.graph)
    #construct the adjacancy matrix
    adjMatrix = {}
    for entry, neigh in self.graph.adjacency_iter():
      adjMatrix[entry] = {}
      total = 0.0
      for neigh, eattr in neigh.items():
        adjMatrix[entry][neigh] = eattr['weight']
        total += adjMatrix[entry][neigh]
      for neigh in adjMatrix[entry].keys():
        adjMatrix[entry][neigh] = (adjMatrix[entry][neigh] / total) * 0.95
      if entry not in adjMatrix[entry]:
        adjMatrix[entry][entry] = 0.05

    for entry, elist in adjMatrix.iteritems():
      print entry, '\t', elist
    #power = sparseMult(adjMatrix, adjMatrix)
    #power = sparseMult(adjMatrix,power)

    #for entry, elist in power.iteritems():
    #	print entry, elist;

  '''
                #perform the walk#
                print self.graph.nodes()
                adj = nx.adjacency_matrix(self.graph)
                print adj
                rwalk = LA.matrix_power(adj,3)

                #find best candidates
                print rwalk
        '''


def sparseMult(mat1, mat2):
  power = {}
  for x, neigh in mat1.iteritems():
    if x not in power:
      power[x] = {}
    for y, value in neigh.iteritems():
      for z, value2 in mat2[y].iteritems():
        power[x][z] = power[x].setdefault(z, 0.0) + (value * value2)
  return power


def removeWrongEntries(session, top50):
  newSession = []
  for entry in session:
    if allLetters(entry) and entry not in top50:
      newSession.append(entry)
  return newSession


def main(argv):
  simpleWalk = SimpleWalk()
  top50 = loadFileInList(argv[2])
  porter = stem.porter.PorterStemmer()
  for rsession in getSessionWithQuery(argv[1]):
    i = 0
    j = 1
    session = removeWrongEntries(rsession, top50)
    sesLen = len(session)
    while i < sesLen and j < sesLen:
      stemI = stemQuery(session[i], porter)
      stemJ = stemQuery(session[j], porter)
      simpleWalk.addEdge(stemI, stemJ, 1.0)
      i = j
      j += 1

  simpleWalk.filter(2)

  simpleWalk.walk()


if __name__ == '__main__':
  main(sys.argv)
