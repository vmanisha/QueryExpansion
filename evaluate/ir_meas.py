# -*- coding: utf-8 -*-
import math


def loadRelJudgements(fileName):
  #query : 	{document : label}
  labels = {}
  noRel = {}
  for line in open(fileName, 'r'):
    split = line.strip().split(' ')
    q = int(split[0])

    d = split[2]
    st = int(split[-1])

    if q not in labels:
      labels[q] = {}
      noRel[q] = 0.0
      #print q;

    if d not in labels[q]:
      labels[q][d] = st
      if st > 0:
        noRel[q] += 1.0

  return labels, noRel


def findMAP(results, rel, noRel, oFile=None):
  MAP = 0.0
  qCount = 0.0
  for qid, docs in results.items():
    qmap = findAvgPrec(docs, rel[qid], noRel)
    print qid, len(docs), qmap

    if oFile:
      oFile.write('map ' + str(qid) + ' ' + str(qmap) + '\n')
    MAP += qmap
    qCount += 1
  return MAP / qCount


#results = docList for a query
#rel = relevance labels for that query
def findAvgPrec(results, rel, noRel):
  pTotK = 0.0
  avpTotal = 0.0
  for k in range(len(results)):
    lab = 0
    try:
      lab = rel[results[k]]
      lab = min(1, lab)
    except:
      pass

    pTotK += lab
    pK = pTotK / ((k + 1) * 1.0)
    if lab > 0:
      print lab, k, noRel, pK, pTotK
    avpTotal += pK * lab

  if noRel > 0:
    return avpTotal / noRel

  return 0.0


def findNDCG10(results, rel, oFile=None):
  #return NDCG and NDCG at 10
  totNdcg = 0.0
  qCount = 0.0
  for query, documents in results.items():
    dcg10, idcg10 = findDCG(documents[:10], rel[query])
    if oFile:
      oFile.write('ndcg10 ' + str(query) + ' ' + str(dcg10 / idcg10) + '\n')
    totNdcg += dcg10 / idcg10
    qCount += 1
  return totNdcg / qCount


def findDCG(results, rel):
  DCG = 0.0
  IDCG = 0.0
  idcgOrder = sorted(rel.values(), reverse=True)
  for k in range(len(results)):
    lab = 0.0
    try:
      lab = rel[results[k]]
    except:
      pass
    logK = math.log(k + 1, 2)

    ilab = idcgOrder[k]
    if logK > 0:
      DCG += lab / logK
      IDCG += ilab / logK
    else:
      DCG += lab
      IDCG += ilab

  return DCG, IDCG
