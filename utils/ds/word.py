from utils import get_cosine


class Word:

  def __init__(self, w, line1=''):
    self.word = w
    self.cat = {}
    self.ent = {}
    self.url = {}
    self.entTotal = 0.0
    self.line = line1

  def updateURLStats(self, u, count):

    #u = u.replace(' ','');
    #if len(u) < 2:
    #	u = 'None';

    u = u.replace('http://', '')
    u = u.replace('https://', '')
    if len(u) > 2:
      if u not in self.url:
        self.url[u] = 0.0

      self.url[u] += count

  def updateCatStats(self, c, count):

    if c not in self.cat:
      self.cat[c] = 0.0

    self.cat[c] += count

  def updateEntStats(self, e, count):

    e = e.replace(' ', '_')

    if e not in self.ent:
      self.ent[e] = 0.0

    self.ent[e] += count
    self.entTotal += count

  def getCats(self):
    return self.cat.keys()

  def getCatFreq(self, cat):
    if cat in self.catEnt:
      return self.cat[cat].values()

    return 0.0

  def getEntFreq(self, ent):
    if ent in self.ent:
      return self.ent[ent]

    return 0.0

  def getEntProb(self, ent):
    if ent in self.ent:
      return self.ent[ent]

    return 0.0

  def getEntities(self):
    return self.ent

  def toString(self):
    return self.line

  def getFeatDict(self):
    toSend = {}
    toSend.update(self.ent)
    toSend.update(self.cat)
    toSend.update(self.url)
    return toSend

  def normalize(self, vect):
    total = sum(vect.values()) + 0.0
    for entry in vect.keys():
      vect[entry] /= total
      vect[entry] = round(vect[entry], 3)

  def normalizeAll(self):
    self.normalize(self.ent)
    self.normalize(self.cat)
    self.normalize(self.url)

  def filterFeat(self, vect, thresh1, thresh2):
    for entry in vect.keys():
      if vect[entry] < thresh1 or vect[entry] > thresh2:
        del (vect[entry])

  def filterAll(self, thresh1, thresh2):
    self.filterFeat(self.ent, thresh1, thresh2)
    self.filterFeat(self.cat, thresh1, thresh2)
    self.filterFeat(self.url, thresh1, thresh2)

  def minFreq(self):
    c1 = max(self.ent.values())
    #c2 = sum(self.cat.values());
    c3 = max(self.url.values())

    max1 = max(c1, c3)
    return max1

  def reduceVectDim(self, dim, vect):
    print 'In reduce'
    sort_ent = sorted(vect.items(), reverse=True, key=lambda x: x[1])

    vect.clear()
    if len(sort_ent) < dim:
      dim = len(sort_ent)

    for entry in sort_ent[:dim]:
      vect[entry[0]] = entry[1]
    return vect

  def reduceDim(self, dim):
    self.ent = self.reduceVectDim(dim, self.ent)
    self.cat = self.reduceVectDim(dim, self.cat)
    self.url = self.reduceVectDim(dim, self.url)

  def getCosine(self, word2):
    eCos = round(get_cosine(self.ent, word2.ent), 3)
    cCos = round(get_cosine(self.cat, word2.cat), 3)
    uCos = round(get_cosine(self.url, word2.url), 3)
    return eCos, cCos, uCos

  def getEntCosine(self, word2):
    return round(get_cosine(self.ent, word2.ent), 3)

  def getCatCosine(self, word2):
    return round(get_cosine(self.cat, word2.cat), 3)

  def getUrlCosine(self, word2):
    return round(get_cosine(self.url, word2.url), 3)

  def getVector(self):

    if len(self.line) < 2:
      sort_ent = sorted(self.ent.items(), reverse=True, key=lambda x: x[1])
      sort_cat = sorted(self.cat.items(), reverse=True, key=lambda x: x[1])
      sort_url = sorted(self.url.items(), reverse=True, key=lambda x: x[1])
      entV = '\t'.join('e_{0}:{1}'.format(x[0], x[1]) for x in sort_ent)
      catV = '\t'.join('c_{0}:{1}'.format(x[0], x[1]) for x in sort_cat)
      urlV = '\t'.join('u_{0}:{1}'.format(x[0], x[1]) for x in sort_url)
      print urlV
      string = entV + '\t' + catV + '\t' + urlV
      self.line = (string.decode('utf-8')).encode('ascii', 'ignore')

    return self.line
