from Whoosh import loadIndex, loadCollector, loadQueryParser
from math import log, factorial
from Utils import AND, getNGrams
from QueryLog import getQuery
W = log(16599813)


def getEntities(ngram, searcher, tlc, qp):
  #generate ngrams
  #query = AND.join('resource:'+x for x in ngram.split())
  query = AND.join(ngram.split())
  #query+= OR + AND.join('redirect:'+x for x in ngram.split())
  try:
    andQuery = qp.parse(unicode(query))
    print query, andQuery
    #search ngrams
    rTuple = []
    try:
      results = searcher.search(andQuery, terms=True)
    except Exception as err:
      print 'ERROR', query, err, type(err), err.args

    #results = tlc.results()
    for entry in results:
      result = {}
      if 'ont' in entry:
        result['ont'] = entry['ont']

      if 'inlink' in entry:
        result['in'] = entry['inlink']

      result['cat'] = entry['category']
      result['page'] = entry['resource']
      result['score'] = entry.score
      print ngram, result['page'], entry.score, entry.matched_terms()
      rTuple.append(result)
    return (rTuple, results.estimated_length())
  except Exception as err:
    print 'ERROR PARSE', ngram, err, err.args
  return ([], 0)


def score(seta, setb, ina, inb):
  lint = len(seta & setb)
  lmin = min(ina, inb)
  lmax = max(ina, inb)

  lint = log(lint) if lint > 0 else lint
  lmax = log(lmax) if lmax > 0 else lmax
  lmin = log(lmin) if lmin > 0 else lmin

  return (lmax - lint) / (W - lmin)


def filterEntities(result):
  rel = {}
  spots = result.keys()
  for i in range(len(spots)):
    a = spots[i]
    aTuple = result[a]
    maxk = 0
    maxTotal = -float('inf')
    index = 0
    for maDict in aTuple[0]:
      pa = maDict['page']
      pra = 1.0 / factorial(pa.count(' ') + 1)
      inlinka = maDict['in'] if 'in' in maDict else None
      seta = set(inlinka.split(' ')) if inlinka else set()
      ina = len(seta)
      keya = a + '_' + pa
      #print a, pa, ina, pra, pra*ina
      if keya not in rel:
        rel[keya] = {}
      for j in range(i + 1, len(spots)):
        b = spots[j]
        bTuple = result[b]
        for mbDict in bTuple[0]:
          pb = mbDict['page']
          prb = 1.0 / factorial(pb.count(' ') + 1)
          inlinkb = mbDict['in'] if 'in' in mbDict else None
          setb = set(inlinkb.split(' ')) if inlinkb else set()
          inb = len(setb)
          keyb = b + '_' + pb
          if keyb not in rel:
            rel[keyb] = {}
          #print b, pb, inb, prb
          rel[keya][keyb] = rel[keyb][keya] = score(seta, setb, ina, inb)
          rel[keya][keyb] *= (prb / bTuple[1])
          rel[keyb][keya] *= (pra / aTuple[1])
          #if rel[keya][keyb] > 0.1 or rel[keyb][keya] > 0.1:
          #	print 'A',keya, ina, pra, aTuple[1] , 'B',keyb, inb,prb, bTuple[1], 'INT',len(seta & setb), 'SCORE',rel[keya][keyb], rel[keyb][keya],score(seta,setb,ina,inb)

      if len(rel[keya]) > 0:
        #print rel[keya]
        if ina > 0:
          total = sum(rel[keya].values()) * (ina * pra)
        else:
          total = sum(rel[keya].values()) * pra

          #print 'TOTAL',keya, total, rel[keya]
      else:
        if ina > 0:
          total = ina * pra
        else:
          total = pra

      if total > maxTotal:
        maxTotal = total
        maxk = index
      index += 1
    #found the maximum		
    #print a, aTuple[0][maxk]['page']

    result[a] = {
        'page': aTuple[0][maxk]['page'],
        'cat': aTuple[0][maxk]['cat'],
        'ont': (aTuple[0][maxk]['ont'] if 'ont' in aTuple[0][maxk] else ''),
        'score': aTuple[0][maxk]['score'],
        'max': maxTotal
    }
  return result


'''args[0] = folder args[1] = indexName args[2] = indexPath
'''


def getEntitiesWithEIndex(args):

  #oFile = open(args[3],'w')
  index, searcher = loadIndex(args[2], args[3])
  tlc = loadCollector(searcher, 50, 20)
  qp = loadQueryParser(index)
  querySet = set()

  fileName = args[1]
  for query in getQuery(fileName, 1):
    if query not in querySet:
      print query, findTextEntities(query, searcher, tlc, qp)
      querySet.add(query)


def findTextEntities(query, searcher, tlc, qp):
  prev = None
  pCount = None
  result = {}
  for ngram, count in getNGrams(query, query.count(' ') + 1):
    rTuple = getEntities(ngram, searcher, tlc, qp)
    if len(rTuple[0]) > 0:
      if prev == None:
        prev = ngram
        result[ngram] = rTuple
        pCount = count
      elif (count > pCount and prev in ngram):
        result.pop(prev)
        result[ngram] = rTuple
        prev = ngram
        pCount = count
      elif (count <= pCount and ngram not in prev):
        result[ngram] = rTuple
        prev = ngram
        pCount = count

    #print 'QUERY', query, 'SPOTS ', result.keys()
  if len(result) > 0:
    finalList = filterEntities(result)
    print query, '\t', finalList
    return query, finalList

  return query, {}

#def main(argv):

#if __name__ == '__main__':
#	main(sys.argv)
