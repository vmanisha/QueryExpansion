# -*- coding: utf-8 -*-
import sys

#from coOccurrence import CoOccurrence


class CoOcManager:

  def __init__(self, fileName, cooccur, sep):
    #self.catList  = {}
    self.coOccur = cooccur
    iFile = open(fileName, 'r')
    k = 0
    for line in iFile:
      line = line.strip()
      split = line.split(sep)
      #cat = split[0]
      i = split[0]
      j = split[1]
      #if cat not in self.catList:
      #	self.catList[cat] = CoOccurrence()
      freq = float(split[2])
      #self.catList[cat].updatStats(i,j,freq)
      self.coOccur.updateStats(i, j, freq)
      k += 1
    print 'Completed Co-occurrence ', k, ' instances'
    iFile.close()
    self.coOccur.setTermTotal()

  def getPMI(self, term1, term2, thresh):
    #if cat not in self.catList:
    #return 0.00001
    return round(self.coOccur.getPMI(term1, term2, thresh), 3)

  def getProb(self, term2, term1, thresh):
    return self.coOccur.getProb(term2, term1, thresh)

  def getUniqueTermCount(self):
    return self.coOccur.getUniqueTermCount()

  def getUniqueTerms(self):
    return self.coOccur.getUniqueTerms()

  def getCoOcCount(self, phrase1, phrase2):
    return self.coOccur.getCoOcCount(phrase1, phrase2)

  def getNeighbours(self, phrase1):
    return self.coOccur.getNeighbours(phrase1)


def main(argv):
  catM = CoOcManager(argv[1])
  print catM.getPMI('metastasi', 'renal')
  print catM.getPMI('failur', 'renal')
  print catM.getPMI('gambro', 'renal')
  print catM.getPMI('calculi', 'renal')
  print catM.getPMI('san', 'event')
  print catM.getPMI('field', 'colleg')
  print catM.getPMI('ticket', 'colleg')
  print catM.getPMI('uti', 'renal')
  print catM.getPMI('golf', 'renal')
  print catM.getPMI('xyzrr', 'abcrr')


if __name__ == '__main__':
  main(sys.argv)
