# -*- coding: utf-8 -*-
'''Imports
'''

import os
from whoosh import scoring
import whoosh.index as index
from whoosh.collectors import TimeLimitCollector
from whoosh.qparser import QueryParser, OrGroup
'''Utility Functions
'''


def loadIndex(indexPath, indexName):

  print 'IndexPath ', indexPath, 'IndexName ', indexName
  if not os.path.exists(indexPath):
    exit()
  ontIndex = index.open_dir(indexPath, indexname=indexName)
  #create the searcher object on ontIndex
  searcher = ontIndex.searcher(weighting=scoring.TF_IDF())
  return ontIndex, searcher


def loadCollector(searcher, dlim, tlim):
  c = searcher.collector(limit=dlim)
  # Wrap it in a TimeLimitedCollector and set the time limit to 10 seconds
  tlc = TimeLimitCollector(c, timelimit=tlim)
  return tlc


def loadQueryParser(index, field):
  return QueryParser(field, schema=index.schema, group=OrGroup)


def closeIndex(searcher, index):
  try:
    searcher.close()
    index.close()
  except Exception as ex:
    print ex


def filterResults(results, score):
  for qt in results:
    if qt[1] > score:
      yield qt
