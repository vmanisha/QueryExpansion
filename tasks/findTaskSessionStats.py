from utils import text_to_vector
from Whoosh import loadIndex
import sys
from whoosh.query import *


def rankAndRetrieveTasks(query, qp, searcher, tlc):
  #get the terms in query
  resultSet = {}
  '''terms = query.split()
	termDict = getDictFromSet(terms)
	for term in terms:
		if term in wordTaskDict:
			for tid in wordTaskDict[term]:
				#calculate the similarity
				cosine = get_cosine(termDict, taskDict[tid])
				#print query , taskDict[tid], cosine
				if cosine > 0.05:
					resultSet[tid] = cosine
	'''
  q = qp.parse(query)
  try:
    searcher.search_with_collector(q, tlc)
  except Exception as err:
    print err, err.args

  results = tlc.results()
  for entry in results:
    resultSet[entry['task']] = entry.score
  print 'Found', len(resultSet), 'Tasks for', query

  return resultSet
  #create a term set
  #for each entry in resultSet		
  #get remaining terms
  #build the term vector with topK


  #def getTaskTermSet(rSort, taskDict, rank):
def getTaskTermSet(rSort, rank):

  termSet = {}
  index = rank
  if rank == 'all':
    index = len(rSort)
  for entry in rSort[:index]:
    #tDict = taskDict[entry[0]]
    tDict = text_to_vector(entry[0])
    for tentry, value in tDict.iteritems():
      termSet[tentry] = tDict.setdefault(tentry, 0.0) + value

  return sorted(termSet.iteritems(), reverse=True, key=lambda x: x[1])


def getPrecRecall(termSet, futTerms, rank):
  intSet = None
  tSet = set()
  if rank == 'all':
    tSet = set(x[0] for x in termSet)
  else:
    tSet = set(x[0] for x in termSet[:rank])

  #print rank, tSet

  intSet = tSet & futTerms
  if intSet:
    return (len(intSet) * 1.0) / len(futTerms), (len(intSet) * 1.0) / len(tSet)
  else:
    return 0.0, 0.0


'''
        argv[1] = dirName
        argv[2] = task type
        argv[3] = session task queries
        argv[4] = Precsion at
        argv[5] = Top K Tasks
'''


def main(argv):
  #taskDict, wordTaskDict = loadTasks(argv[1], argv[2])
  index, searcher, tlc = loadIndex(argv[1], argv[1])
  qp = QueryParser('task', schema=index.schema, group=OrGroup)

  #rank = int(argv[4]) # rank to calculate the precision
  #topK = int(argv[5]) # top K Tasks to create the term set
  precDict = {}
  recallDict = {}
  sCount = 0
  for session in getSessionWithNL(argv[3]):
    bQuery = session[0].lower()
    bQuery = re.sub(SYMB, ' ', bQuery)
    bQuery = re.sub('\s+', ' ', bQuery).strip()
    aTerms, rTerms = addedAndRemovedTerms(bQuery, session[1:])
    if aTerms:
      print bQuery, aTerms
      #resultSet = rankAndRetrieveTasks(bQuery,taskDict, wordTaskDict)
      resultSet = rankAndRetrieveTasks(bQuery, qp, searcher, tlc)
      rSort = sorted(resultSet.items(), reverse=True, key=lambda x: x[1])
      for j in [50, 100, 500, 1000, 'all']:
        if j not in precDict:
          precDict[j] = {}
          recallDict[j] = {}
        #termSet = getTaskTermSet(rSort, taskDict, j)
        termSet = getTaskTermSet(rSort, j)
        for i in [1, 3, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 'all']:
          prec, recall = getPrecRecall(termSet, aTerms, i)
          precDict[j][i] = precDict[j].setdefault(i, 0.0) + prec
          recallDict[j][i] = recallDict[j].setdefault(i, 0.0) + recall
          print j, i, bQuery, '\t', prec
      sCount += 1.0

  print 'Printing Precision Stats'
  for j, jdict in precDict.iteritems():
    for i, score in jdict.iteritems():
      print j, i, score, sCount, score / sCount

  print 'Printing Recall Stats'
  for j, jdict in recallDict.iteritems():
    for i, score in jdict.iteritems():
      print j, i, score / sCount


if __name__ == '__main__':

  main(sys.argv)
