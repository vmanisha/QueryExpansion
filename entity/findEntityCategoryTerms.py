# -*- coding: utf-8 -*-
import sys
from utils import loadDictFromFile
from entity.category.categoryManager import CategoryManager
from utils.coOccurrence import CoOccurrence
from utils.coOcManager import CoOcManager
from entity.dexter import Dexter
from entity.ranker import Ranker
from entity.catThesExpansion import CatThesExpansion
from queryLog import normalize
import json
from nltk import stem
#find the entities in the query
#for each entity find the right category
#fetch the top terms of that category through rules of expansion
'''argv[1] = file containing the queries argv[2] = file containing the topTerms argv[3] = cat vector file / cat query folder / wikiIndex argv[4] = category phrase folder / topic folder / queryIndex argv[5] = category Co-Occurrence file / term vector file
'''


def main(argv):

  #load the co-occurrence terms
  coOccurTermList = loadDictFromFile(argv[2], '\t', ':')
  #for each query find the entities
  #score the cats

  ipaddress = 'localhost'
  #dexter object
  tagURL = 'http://' + ipaddress + ':8080/rest/annotate'
  catURL = 'http://' + ipaddress + ':8080/rest/graph/get-entity-categories'
  dexter = Dexter(tagURL, catURL)
  catManage = CategoryManager(argv[3], argv[4])
  catCoMan = CoOcManager(argv[5], CoOccurrence(), ' ')

  ranker = Ranker()
  entExp = CatThesExpansion(dexter, catManage, ranker, catCoMan)
  stemmer = stem.porter.PorterStemmer()
  result = {}
  done = set()
  noEnt = 0
  oFile = open(argv[6], 'w')
  for line in open(argv[1], 'r'):
    split = line.strip().split('\t')
    oquery = split[0].strip()
    query = normalize(oquery, stemmer)

    if query not in done and len(query) > 2:
      result = {}
      result = {'coTerms': {}, 'catTerms': None, 'freq': 0.0}
      result['freq'] = int(split[1])
      #print query, query in coOccurTermList
      if query in coOccurTermList:
        result['coTerms'] = coOccurTermList[query]
        entCatTermDict = entExp.getTopEntityCategoryTerms(oquery, 1, 40)
        result['catTerms'] = entCatTermDict
        if len(result['catTerms']) > 0:
          oFile.write(query + '\t' + json.dumps(result) + '\n')
        else:
          noEnt += 1.0
      done.add(query)

  print 'No of queries with no Ent ', noEnt
  oFile.close()


if __name__ == '__main__':
  main(sys.argv)
