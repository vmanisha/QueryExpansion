# -*- coding: utf-8 -*-
class Ranker:

  def __init__(self):
    self.id = 1

  def getTopK(self, terms, limit):
    total = sum([x[1] for x in terms]) * 1.0
    #tsorted = sorted (terms.items(),reverse = True , key = lambda x : x [1])
    #print 'TermSet Size',len(tsorted)
    result = []
    i = 0
    if total > 0:
      for entry in terms:
        result.append((entry[0], round(entry[1] / total, 3)))
        i += 1
        if i == limit:
          break

    return result

  def getTopKAsDict(self, terms, limit):
    total = sum([x[1] for x in terms]) * 1.0

    result = {}
    i = 0
    for entry in terms:
      result[entry[0]] = round((entry[1] + 1.0) / (total + 1.0), 3)
      i += 1
      if i == limit:
        break

    return result

  def getTopKWithFilter(self, terms, limit, limit2):
    tsorted = sorted(terms.items(), reverse=True, key=lambda x: x[1])
    filtered = []
    i = 0
    for entry in tsorted:
      if entry[1] > 0:
        filtered.append(entry)
      i += 1
      if i == limit2:
        break
    return self.getTopK(filtered, limit)  #self.getTopKAsDict(filtered, limit)
