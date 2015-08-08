import random


class KMeans:

  def __init__(self, k1, data1, distMatrix, iteration, threshold):
    self.k = k1
    self.data = data1
    #list
    self.distance = distMatrix
    self.mean = []
    self.meanDist = []
    #stores the avg distance from mean
    self.clusters = [[] for i in range(k1)]
    self.noClass = []
    self.maxDist = []
    self.itertn = iteration
    self.thresh = threshold
    self.wasCenter = {}
    print 'To Initialize ', k1, len(data1), len(self.clusters)

  def initializeMean(self):
    while len(self.mean) < self.k:
      #print len(self.mean), self.k
      #index = random.randint(0,self.k);
      index = random.randint(0, len(self.data) - 1)
      if self.data[index] not in self.mean:
        self.mean.append(self.data[index])
        self.wasCenter[self.data[index]] = self.wasCenter.setdefault(
            self.data[index], 0.0) + 1.0
        self.meanDist.append(0.0)
        self.maxDist.append(None)

    print 'Done with initialization'

  def findCenters(self):
    self.mean = []
    self.meanDist = []
    self.maxDist = []
    tdist = {}

    for entry in self.clusters:
      #find the new mean
      minDist = None
      minEntry = None
      tdist.clear()
      clen = len(entry)
      self.maxDist.append(None)

      for term in entry:
        tdist[term] = 0.0

      noClus = len(self.noClass)
      if clen == 1 and noClus > 0:
        #randomly select another entry
        index = random.randint(0, noClus - 1)
        #print index , noClus;
        minEntry = self.noClass[index]
        self.wasCenter[minEntry] = self.wasCenter.setdefault(minEntry,
                                                             0.0) + 1.0
        self.mean.append(minEntry)
        self.meanDist.append(0.0)
        self.noClass.remove(minEntry)
        noClus -= 1
      else:
        for i in range(clen):
          t1 = entry[i]
          for j in range(i + 1, clen):
            t2 = entry[j]
            try:
              a, b = self.order(t1, t2)
              tdist[t1] += self.distance[a][b]
              tdist[t2] += self.distance[a][b]
            except:
              pass

          if clen > 1.0:
            tdist[t1] /= (clen - 1.0)
          if not minDist or minDist > tdist[t1]:
            minDist = tdist[t1]
            minEntry = t1
        #print i, t1, minDist;
        #print entry, minDist, minEntry;
        self.wasCenter[minEntry] = self.wasCenter.setdefault(minEntry,
                                                             0.0) + 1.0
        self.mean.append(minEntry)
        self.meanDist.append(minDist)

  def getEntryWithMinDist(self, word, check):
    minDist = None
    minEntry = None
    minInd = None
    i = 0
    #print word, self.distance[word];
    #print check;
    for entry in check:
      try:
        a, b = self.order(word, entry)
        dist = self.distance[a][b]
        if (not minDist) or (minDist > dist) and dist < self.maxDist[i]:
          minDist = dist
          minEntry = entry
          minInd = i
      except:
        pass
      i += 1
    return minDist, minEntry, minInd

  def assignLabel(self):
    self.noClass = []

    for i in range(len(self.clusters)):
      self.clusters[i] = [self.mean[i]]
    i = 1
    for entry in self.data:
      if entry not in self.mean:
        minDist, minEntry, minInd = self.getEntryWithMinDist(entry, self.mean)
        #print 'Assigning ', entry, minDist, minEntry, minInd
        if minInd:
          self.clusters[minInd].append(entry)
          if (not self.maxDist[minInd]) or (self.maxDist[minInd] < minDist):
            self.maxDist[minInd] = minDist
        else:
          if entry not in self.noClass:
            self.noClass.append(entry)
      i += 1
      if i % 10000 == 1:
        print i

  def cluster(self):

    oldMaxDist = None
    self.initializeMean()

    for i in range(self.itertn):
      print 'Assigning Labels'
      self.assignLabel()
      print 'Assigned Labels'
      print 'Iteration ', i
      #print self.clusters;
      oldCenters = self.meanDist
      oldMaxDist = self.maxDist
      self.findCenters()
      newCenters = self.meanDist
      #print 'old means', oldCenters;
      #print 'new means', newCenters;

      if self.findCenterDiff(oldCenters, newCenters) < self.thresh:
        break
    self.maxDist = oldMaxDist
    self.cleanClusters()

  def cleanClusters(self):
    clen = len(self.clusters)
    #for each cluster if only one term
    #check if these terms can be moved to one cluster
    #else move to NA
    '''print self.maxDist;
		print self.mean;
		print len(self.distance);
		print self.distance.keys();
		'''
    for i in range(clen):
      if len(self.clusters[i]) < 2:
        cInd = self.findMostLikelyCluster(i)
        #print cInd, self.clusters[i];
        if cInd == -1:
          self.noClass.append(self.clusters[i][0])
        else:
          print 'Merging with', cInd, self.clusters[i]
          self.clusters[cInd].append(self.clusters[i][0])
        self.clusters[i] = []

    #aggregate cluster labels
    #store cluster
    #find max clustering
    # merge small clusters

  def findMostLikelyCluster(self, i):
    clus = self.clusters[i]
    clen = len(self.clusters)
    minDist = 100
    minIndex = -1
    for j in range(i + 1, clen):
      for entry in clus:
        a, b = self.order(entry, self.mean[j])
        try:
          if self.distance[a][b] < self.maxDist[j] and self.distance[a][b
                                                                  ] < minDist:
            minIndex = j
            minDist = self.distance[a][b]
        except:
          pass
        #if entry in self.distance and self.mean[j] in self.distance[entry] and \
        #self.distance[entry][self.mean[j]] < self.maxDist[j]:
        #	return j;

    return minIndex

  def findCenterDiff(self, v1, v2):
    diff = 0.0
    vec1 = v1
    vec2 = v2
    if len(v2) < len(v1):
      vec1 = v2
      vec2 = v1
    #print vec1;
    #print vec2;
    for i in range(len(vec1)):
      diff += abs(vec1[i] - vec2[i])
    diff /= len(vec1)
    return diff

  def getClusters(self):
    return self.clusters

  def getMeans(self):
    return self.mean

  def getTermInNoCluster(self):
    return self.noClass

  def order(self, a, b):
    if a > b:
      return b, a
    return a, b
