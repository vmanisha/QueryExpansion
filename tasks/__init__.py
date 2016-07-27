import os
import sys
import re
from utils import text_to_vector, SYMB, get_cosine
import ast

from nltk.stem import porter
from queryLog import filterStopWordsFromList, hasInapWords, hasManyWords, hasAlpha, hasManyChars


def getUserVector(fileName, uIndex, qIndex):
  userVector = {}
  lastUser = None
  porter1 = porter.PorterStemmer()

  for line in open(fileName, 'r'):
    split = line.strip().split('\t')
    uId = split[uIndex]
    query = split[qIndex]

    if not lastUser:
      lastUser = uId
    raw_split = re.sub(SYMB, ' ', query.lower()).split(' ')
    query = filterStopWordsFromList(raw_split)
    #print uId, lastUser, lastUser!=uId
    if lastUser != uId:
      yield lastUser, userVector
      userVector = {}

    if (not (hasManyChars(query,raw_split,1,4,70) \
			or hasInapWords(raw_split) or hasManyWords(raw_split,15,40))) \
			and hasAlpha(query):
      qDict = text_to_vector(query)
      for entry, val in qDict.iteritems():
        entry1 = porter1.stem(entry)
        userVector[entry1] = userVector.setdefault(entry1, 0.0) + val

    lastUser = uId
  yield lastUser, userVector


def loadTasks(fileName):
  taskList = {}
  for line in open(fileName, 'r'):
    split = line.strip().split('\t')
    tid = split[0]
    task = ast.literal_eval(split[-1])
    taskList[tid] = task
  return taskList


def main(argv):
  taskList = loadTasks(argv[1])
  userVectFile = open('userVect.txt', 'w')
  userTaskSimFile = open('userTaskSim.txt', 'w')
  uSim = {}
  for uId, termVector in getUserVector(argv[2], 0, 1):
    uSim[uId] = {}
    userVectFile.write(
        str(uId) + '\t' + '\t'.join('{0}\t{1}'.format(x, y)
                                    for x, y in termVector.items()) + '\n')

    for taskid, task in taskList.iteritems():
      sim = round(get_cosine(task, termVector), 5)
      uSim[uId][taskid] = sim
    tSort = sorted(uSim[uId].items(), reverse=True, key=lambda x: x[0])
    userTaskSimFile.write(str(uId) + '\t' + '\t'.join(str(x[1])
                                                      for x in tSort) + '\n')

    #print 'Check ',uId,'\t', tSort


if __name__ == '__main__':
  main(sys.argv)
