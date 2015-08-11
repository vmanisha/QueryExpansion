import sys
from nltk import stem
import numpy
import math, re
from nltk.tokenize import word_tokenize
from nltk.collocations import BigramAssocMeasures, BigramCollocationFinder
from sklearn.preprocessing import normalize
from utils import stopSet, SYMB
from queryLog import hasAlpha, hasWebsite, getSessionWithNL
from Whoosh import loadIndex, loadCollector, loadQueryParser
from whoosh.collectors import TimeLimit
porter = stem.porter.PorterStemmer()
biMeas = BigramAssocMeasures()


def updateNetwork(query, network, qp, searcher, tlc, field, ntype):
  #find the top 50 documents
  q = qp.parse(unicode(query))
  totalText = ''
  total = 0.0
  tmin = -1000
  tmax = 1000
  terms = set()
  try:
    searcher.search_with_collector(q, tlc)
  except TimeLimit:
    print '--LONG-- ', query

  results = tlc.results()
  for entry in results:
    totalText += entry[field] + ' '

  finder = BigramCollocationFinder.from_words(word_tokenize(totalText))
  #update the network

  rList = finder.score_ngrams(biMeas.pmi)

  for rTuple in rList:
    total += rTuple[1]
    if tmin > rTuple[1]:
      tmin = rTuple[1]
    if tmax < rTuple[1]:
      tmax = rTuple[1]

  for rTuple in sorted(rList, reverse=True, key=lambda x: x[1]):
    if (len(terms) < 3000 and finder.ngram_fd[rTuple[0]] > 2
     ) or (finder.ngram_fd[rTuple[0]] > 1.0 and rTuple[0][0] in query or
           rTuple[0][1] in query and len(terms) < 4000):
      #if (len(terms) < 3000  and finder.ngram_fd[rTuple[0]] > 2) or (rTuple[0][0] in query or rTuple[0][1] in query and len(terms) < 4000):
      a = rTuple[0][0]
      if len(a) > 2 and hasAlpha(a) and a not in stopSet and not hasWebsite(a):
        if a not in network:
          network[a] = {}
          terms.add(a)
        b = rTuple[0][1]
        if len(b) > 2 and hasAlpha(b) and b not in stopSet and not hasWebsite(
            b):
          if b not in network[a]:
            network[a][b] = {}
            terms.add(b)
          network[a][b][ntype] = network[a][b].setdefault(ntype, 0.0) + (
              (rTuple[1] - tmin) / (tmax - tmin))

  print query, ntype, len(terms)

  return terms


def updateStemNetwork(queryNetwork):
  stemDict = {}
  for entry in queryNetwork.keys():
    stem = porter.stem(entry)
    if stem not in stemDict:
      stemDict[stem] = set()
    stemDict[stem].add(entry)
    for entry2 in queryNetwork[entry].keys():
      stem = porter.stem(entry2)
      if stem not in stemDict:
        stemDict[stem] = set()
      stemDict[stem].add(entry2)

  for stem, values in stemDict.iteritems():
    wl = list(values)
    for i in range(len(wl) - 1):
      if wl[i] not in queryNetwork:
        queryNetwork[wl[i]] = {}
      for j in range(i + 1, len(wl)):
        if wl[j] not in queryNetwork[wl[i]]:
          queryNetwork[wl[i]][wl[j]] = {}
        queryNetwork[wl[i]][wl[j]]['stem'] = 1.0 / len(values)


def normalizeNetworks(network):
  for i in network.keys():
    isum = sum(network[i].values())
    for j in network[i].keys():
      network[i][j] /= isum


def setBackSmoothing(noTerms):
  global backSmooth
  backSmooth = 1.0 / noTerms


def toMatrix(keySet, network):

  print 'Total Dim of Matrix ', len(keySet), '*', len(keySet)
  numArray = numpy.zeros((len(keySet), len(keySet)))
  for i in range(len(keySet) - 1):
    for j in range(i + 1, len(keySet)):
      try:
        numArray[i, j] = network[keySet[i]][keySet[j]]
        numArray[j, i] = network[keySet[i]][keySet[j]]
      except Exception as err:
        numArray[i, j] = 0.0
        numArray[j, i] = 0.0

  return normalize(numArray, norm='l2', axis=0)


def combineNetwork(factor, network, network2, ntype):
  for e1, eDict in network2.iteritems():
    if e1 not in network:
      network[e1] = {}
    for e2, tDict in eDict.iteritems():
      if e2 not in network:
        network[e2] = {}
      if ntype in tDict:
        #if ntype == 'query':
        #	print ntype, e1, e2, tDict
        network[e1][e2] = network[e1].setdefault(e2, 0.0) + (factor *
                                                             tDict[ntype])
        network[e2][e1] = network[e2].setdefault(e1, 0.0) + (factor *
                                                             tDict[ntype])


def toSparseMatrix(keySet, network):
  print 'Total Dim of Matrix ', len(keySet), '*', len(keySet)
  numArray = csr_matrix((len(keySet), len(keySet)))
  total = 0
  for i in range(len(keySet) - 1):
    for j in range(i + 1, len(keySet)):
      try:
        numArray[i, j] = network[keySet[i]][keySet[j]]
        total += 1.0
      except Exception as err:
        numArray[i, j] = 0.0

  print 'Size', numArray.shape, total
  return numArray

  #query logs
  #wikipedia


def findMarkovStats(argv):

  i = 0

  wikiIndexDir = argv[2]
  queryIndexDir = argv[3]

  iFile = argv[1]

  wIndex, wsearcher = loadIndex(wikiIndexDir, wikiIndexDir)
  qIndex, qsearcher = loadIndex(queryIndexDir, queryIndexDir)

  wtlc = loadCollector(wsearcher, 2000, 20)
  qtlc = loadCollector(qsearcher, 2000, 20)

  qqp = loadQueryParser(qIndex, 'session')
  wqp = loadQueryParser(wIndex, 'content')

  prec = {}
  recall = {}

  count = 0.0
  for session in getSessionWithNL(iFile):
    #get the query
    query = session[0].lower()
    query = re.sub(SYMB, ' ', query)
    query = re.sub('\d+', ' ', query)
    query = re.sub('\s+', ' ', query).strip()

    aTerms, bTerms = addedAndRemovedTerms(query, session)

    if aTerms:
      count += 1.0
      totalNetwork = {}
      #stemNetwork = {}
      #queryNetwork = {}
      #wikiNetwork = {}
      terms = updateNetwork(query, totalNetwork, wqp, wsearcher, wtlc,
                            'content', 'wiki')
      terms2 = updateNetwork(query, totalNetwork, qqp, qsearcher, qtlc,
                             'session', 'query')
      print len(terms), len(terms2)
      #updateStemNetwork(queryNetwork,stemNetwork, porter)	
      #updateStemNetwork(wikiNetwork,stemNetwork, porter)
      updateStemNetwork(totalNetwork)
      #normalizeNetworks(queryNetwork)			
      #normalizeNetworks(stemNetwork)			
      #normalizeNetworks(wikiNetwork)

      #calculate the mixtures at two stages
      stage1 = {}
      stage2 = {}
      combineNetwork(1.0, stage1, totalNetwork, 'stem')
      combineNetwork(0.5, stage2, totalNetwork, 'query')
      combineNetwork(0.5, stage2, totalNetwork, 'wiki')

      #convert into matrix for multiplication
      totalDim = sorted(list(set(stage1.keys()) | set(stage2.keys())))

      dim = len(totalDim)
      if dim > 0:
        stage1Matrix = toMatrix(totalDim, stage1)
        print 'STAGE1', stage1Matrix[0], stage1Matrix.shape
        stage2Matrix = toMatrix(totalDim, stage2)
        print 'STAGE2', stage2Matrix[0], stage2Matrix.shape

        backSmooth = 1.0 / len(totalDim)
        stage3Matrix = numpy.zeros((dim, dim))
        stage3Matrix.fill(backSmooth)
        print 'STAGE3', stage3Matrix[0], stage3Matrix.shape

        alpha = 0.80
        #matrix = ['stage2','stage2','stage2','stage2','stage2','stage2','stage2','stage2','stage3']
        matrix = ['stage1', 'stage2', 'stage2', 'stage2', 'stage3']
        totalSum = numpy.zeros((dim, dim))
        cK = numpy.ones((dim, dim))

        #start walk!
        for k in range(len(matrix)):
          print k, matrix[k]
          if matrix[k] == 'stage1':
            cK = numpy.dot(stage1Matrix, cK)
          elif matrix[k] == 'stage2':
            cK = numpy.dot(stage2Matrix, cK)
          else:
            cK = numpy.dot(cK, stage3Matrix)
          print 'CK', cK[0]

          totalSum = totalSum + (math.pow(alpha, k) * cK)
        totalSum = totalSum * (1 - alpha)

        #rank Terms
        qList = []
        terms = query.split()  #getQueryTerms(query)
        for term in terms:
          if term in totalDim:
            qList.append(totalDim.index(term))
          else:
            print 'ERROR dint find ', query, '\t', term, len(totalDim)

        termScore = {}
        for i in range(len(totalDim)):
          termScore[totalDim[i]] = 0.0
          for j in qList:
            if totalSum[i][j] > 0.0:
              termScore[totalDim[i]] += math.log(totalSum[i][j])

        #find the precision for different term sets
        sortTerms = sorted(termScore.iteritems(),
                           reverse=True,
                           key=lambda x: x[1])
        for i in [1, 3, 5, 10, 20, 30, 40, 50, 60, 100, '10000']:
          try:
            cTerms = set([x[0] for x in sortTerms[:i]])
            print 'CTERMS ', sortTerms[0:10], len(cTerms), 'ATERMS', aTerms
            p = len(aTerms & cTerms) / (len(aTerms) * 1.0)
            r = len(aTerms & cTerms) / (len(cTerms) * 1.0)
            prec[i] = prec.setdefault(i, 0.0) + p
            recall[i] = recall.setdefault(i, 0.0) + r
            print 'Prec', i, '\t', query, '\t', p
          except Exception as err:
            cTerms = set([x[0] for x in sortTerms])
            p = len(aTerms & cTerms) / (len(aTerms) * 1.0)
            r = len(aTerms & cTerms) / (len(cTerms) * 1.0)
            prec[i] = prec.setdefault(i, 0.0) + p
            recall[i] = recall.setdefault(i, 0.0) + r
            print 'Prec', i, '\t', query, '\t', p

      else:
        for i in [1, 3, 5, 10, 20, 30, 40, 50, 60, 100, '10000']:
          print 'Prec', i, '\t', query, '\t', 0.0

    #average the prec & recall
    #print prec and recall
  print 'Printing Precison'
  for entry, value in prec.iteritems():
    print entry, value / count

  print 'Printing Precison'
  for entry, value in recall.iteritems():
    print entry, value / count

  wIndex.close()
  qIndex.close()


'''
        argv[1] = sessionTrack file
        argv[2] = query  file
        argv[3] = wiki Index folder


'''


def main(argv):

  #stemNetwork = loadStemNetwork(argv[2])
  findMarkovStats(argv)


if __name__ == '__main__':
  main(sys.argv)
