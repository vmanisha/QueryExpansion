import networkx as nx
import os, sys
import numpy as np
from utils import get_cosine, text_to_vector

from sklearn.cluster import DBSCAN
from sklearn import metrics
from queryLog import QUERY, QTIME, CLICKU, USER, getSessionWithInfo

import argparse

import distance
'''Algo Names
'''
QCC = 'qcc'
HTC = 'htc'
DBS = 'dbscan'
'''#features :

        Queries
        #Jaccard
        #Cosine
        #time diff
        #dist
        #url match count
        #prev query jac
        #next query jac
        #edit distance

'''


def getPairFeatures(session):

  totalTime = 1.0 + (session[-1][QTIME] - session[0][QTIME]).total_seconds()
  for i in range(len(session) - 1):
    for j in range(i + 1, len(session)):
      e1 = session[i]
      e2 = session[j]
      jaccard = 1.0 - distance.jaccard(e1[QUERY].split(), e2[QUERY].split())
      edit = 1.0 - distance.nlevenshtein(e1[QUERY].split(), e2[QUERY].split())
      timeDiff = ((e2[QTIME] - e1[QTIME]).total_seconds()) / totalTime * 1.0
      #normalized distance
      dist = (j - i) * 1.0 / len(session)
      urlMatch = -1
      if CLICKU in e1 and CLICKU in e2:
        urlMatch = 1.0 - distance.nlevenshtein(e1[CLICKU], e2[CLICKU])
      cosine = get_cosine(text_to_vector(e1[QUERY]), text_to_vector(e2[QUERY]))
      edgeScore = .20 * cosine + .20 * jaccard + .20 * edit + .15 * dist + .15 * timeDiff + .10 * urlMatch
      yield i, j, edgeScore, cosine, jaccard, edit, dist, timeDiff, urlMatch


def getSessionFeatures(session, sId, user):
  #print sessionString

  jScore = None
  wxScore = None
  featList = []
  featString = ''
  jScore = np.zeros((len(session), len(session)))
  wxScore = np.zeros((len(session), len(session)))

  for i, j, score, cosine, jaccard, edit, dist, timeDiff, urlMatch in getPairFeatures(
      session):
    featList.append([cosine, jaccard, edit, dist, timeDiff, urlMatch, score])
    jScore[i][j] = jaccard
    wxScore[i][j] = wxScore[j][i] = score
    featString += str(sId)+'\t'+str(user)+'\t'+str(i) +'\t'+ str(j) +'\t'+ str(cosine) \
			+'\t'+str(jaccard)+'\t'+ str(edit) +'\t'+ str(timeDiff) \
			+'\t'+ str(dist) +'\t'+ str(urlMatch) +'\n'

  return jScore, wxScore, featList, featString


  #HTC -- Lucchese
def getHTC(jScore, wxScore, tscore, lsession):
  i = 0
  j = 1
  cluster = []
  while i < lsession and j < lsession:
    if jScore[i][j] < 0.75:
      cluster.append(tuple(range(i, j)))
      i = j
      j = i + 1
    else:
      j += 1
  cluster.append(tuple(range(i, j)))

  i = 0
  j = 1
  #print 'before clustering' , cluster
  while i < len(cluster) - 1:
    if len(cluster[i]) > 0 and len(cluster[j]) > 0:
      h1 = min(cluster[i])
      h2 = min(cluster[j])
      t1 = max(cluster[i])
      t2 = max(cluster[j])
      sim = min(wxScore[h1][h2], wxScore[h1][t2], wxScore[t1][h2],
                wxScore[t1][t2])
      if sim > tscore:
        #merge the clusters
        setc = sorted(cluster[i] + cluster[j])
        cluster[i] = (tuple(set(setc)))
        cluster[j] = ()
      j += 1
    elif len(cluster[j]) == 0:
      j += 1
    else:
      i += 1
      j = i + 1

    if j >= len(cluster):
      i += 1
      j = i + 1

  labels = getClusterFormat(cluster, lsession)
  #print HTC,cluster, labels
  return labels
  #print 'after clustering' , cluster


  #DBSCAN - Lucchese
def getDbScan(wxScore, eps, tscore):
  dbscan = DBSCAN(eps, min_samples=5, metric='precomputed').fit(wxScore)
  #return the clusters
  #print  'DBSCAN', dbscan.labels_
  return dbscan.labels_


#QCC - Lucchese
def getComponents(wxScore, tscore):
  G = nx.Graph()
  entries = len(wxScore)
  for i in range(entries - 1):
    for j in range(i + 1, entries):
      if wxScore[i][j] > tscore:
        # build the graph
        G.add_edge(i, j, weight=wxScore[i][j])
      else:
        G.add_node(i)
        G.add_node(j)
  entries = len(G.nodes())
  if entries > 1:
    #find connected components
    #t = 1
    taskList = nx.connected_components(G)
    #for nlist in taskList:
    #	taskFile.write( str(sId)+'\t'+ str(user) +'\t'+  str(t) +'\t'+', '.join(nlist)+'\n')
    #	t += 1

    #convert to clustering measure format
    labels = getClusterFormat(taskList, entries)
    #print 'Connected Components' , taskList, labels
    return labels
  return []


def getTaskFeatures(session, cTask, sc1):
  taskList = {}
  for j in range(len(cTask) + 1):
    i = int(cTask[j])
    if i not in taskList:
      taskList[i] = {'query': {}, 'url': {}, 'user': 0.0, 'score': 0.0}
    uquery = session[j][QUERY]
    taskList[i]['query'][uquery] = 1 if uquery not in taskList[
        i
    ] else taskList[i][uquery] + 1
    if CLICKU in session[j]:
      curl = session[j][CLICKU]
      taskList[i]['url'][curl] = taskList[i]['url'].setdefault(curl, 0.0) + 1.0
    taskList[i]['user'] = session[j][USER]
    taskList[i]['score'] = sc1
    return taskList


def formatResults(session, jsonObject, label, cTask, sc1):
  jsonObject[label] = {'score': sc1, 'tasks': {}}
  taskList = {}
  for j in range(len(cTask)):
    i = int(cTask[j])
    if i not in taskList:
      taskList[i] = {}
    uquery = session[j][QUERY]
    taskList[i][uquery] = 1 if uquery not in taskList[i] else taskList[i][uquery
                                                                        ] + 1

  for i, task in taskList.iteritems():
    #print task.keys()
    jsonObject[label]['tasks'][tuple(task.keys())] = {}
  '''for entry1, entry2 in cTask, hTask:
		string += str(sId)+'\t'+str(t)+'\t'\
		+(','.join([session[x][QUERY] for x in entry1])) + '\t' \
		+(','.join([session[x][QUERY] for x in entry2])) + '\n'
	print 'Json Object', jsonObject

	'''


def getClusterFormat(taskList, lsession):

  labels = {}
  k = 1
  for cluster in taskList:
    for entry in cluster:
      labels[entry] = k
    k += 1

  return labels


def compareAlgos(task1, task2, wxScore):
  #formats maybe different !!
  #ways to compare -- use the highest score ?
  #average of all -- if have a good average send that
  sc1 = sc2 = sc3 = -2
  try:
    if np.any(task1[0] != task1):
      sc1 = metrics.silhouette_score(wxScore, task1, metric='precomputed')
    if np.any(task2[0] != task2):
      sc2 = metrics.silhouette_score(wxScore, task2, metric='precomputed')
  except ValueError:
    print 'Number of clusters == Number of samples'
  sc3 = 0.0
  #if np.any(dbScan[0]!=dbScan):
  #	sc3 = metrics.silhouette_score(wxScore, dbScan, metric='precomputed')
  #print sc1, sc2, sc3
  return sc1, sc2, sc3


def getHTCTasks(session, thresh, sId=1, userId=1):
  wxScore, jScore, featList, featString = getSessionFeatures(session, sId,
                                                             userId)
  htc = getHTC(jScore, wxScore, thresh, len(session))
  sc2 = -2
  taskDict = {}
  if np.any(htc[0] != htc):
    sc2 = metrics.silhouette_score(wxScore, htc, metric='precomputed')
  formatResults(session, taskDict, HTC, htc, sc2)
  return taskDict


def getQCCTasks(session, thresh, sId=1, userId=1):
  wxScore, jScore, featList, featString = getSessionFeatures(session, sId,
                                                             userId)
  qcc = getComponents(wxScore, thresh)
  sc2 = -2
  taskDict = {}
  if np.any(qcc[0] != qcc):
    sc2 = metrics.silhouette_score(wxScore, qcc, metric='precomputed')
  formatResults(session, taskDict, QCC, qcc, sc2)
  return taskDict


def updateStats(taskDict, stats, ctype):

  score = round(taskDict[ctype]['score'], 2)
  if score not in stats[ctype]['sc']:
    stats[ctype]['sc'][score] = 0
  stats[ctype]['sc'][score] += 1
  stats[ctype]['scTotal'] += score
  stats[ctype]['scCount'] += 1

  for tasks, entityVect in taskDict[ctype]['tasks'].iteritems():
    stats[ctype]['ttotal'] += 1
    for entity, eMatchScore in entityVect.iteritems():
      #print entity
      if entity not in stats[ctype]:
        stats[ctype][entity] = 1
      else:
        stats[ctype][entity] += 1
      stats[ctype]['etotal'] += 1


def loadOptions(fileName):
  print fileName
  argparser = argparse.ArgumentParser(fromfile_prefix_chars='@')
  #load the variables too
  ifile = open(fileName[1:], 'r')
  for line in ifile:
    if '--' in line:
      line = line.strip()
      argparser.add_argument(line)
  ifile.close()
  return argparser


'''--inputDir --taskDir --featDir --sessDir --inputDelim --htcFile --qccFile --dbScanFile --qccThresh --htcThresh --dbScanThresh --indexPath --indexName
'''


def main(argv):
  argParser = loadOptions(argv[1])
  args = argParser.parse_args([argv[1]])
  print args
  tscore = {
      QCC: float(args.qccThresh),
      HTC: float(args.htcThresh),
      DBS: float(args.dbScanThresh)
  }

  stats = {
      QCC: {'ttotal': 0,
            'etotal': 0,
            'sc': {},
            'scTotal': 0,
            'scCount': 0},
      HTC: {'ttotal': 0,
            'etotal': 0,
            'sc': {},
            'scTotal': 0,
            'scCount': 0}
  }
  '''if not os.path.exists(featDir):
		os.mkdir(featDir)

	if not os.path.exists(args.sessDir):
		os.mkdir(args.sessDir)
	'''

  if not os.path.exists(args.taskDir):
    os.mkdir(args.taskDir)

  i = 0
  for fileName in os.listdir(args.inputDir):
    #featFile = open(args.featDir+'//'+fileName,'w')
    #sessionFile = open(args.sessDir + '//'+fileName,'w')
    taskFile = open(args.taskDir + '//' + fileName, 'w')
    taskFeatures1 = open(args.taskDir + '//Feat1' + fileName, 'w')
    taskFeatures2 = open(args.taskDir + '//Feat2' + fileName, 'w')

    #get the session features
    for user, sId, session, sessionString in getSessionWithInfo(
        args.inputDir + '//' + fileName, args.inputDelim, 1500):
      if len(session) > 5:
        wxScore, jScore, featList, featString = getSessionFeatures(session, sId,
                                                                   user)
        #qcc
        qcc = getComponents(wxScore, tscore[QCC])  #array of array of queries
        #htc
        htc = getHTC(jScore, wxScore, tscore[HTC], len(session))
        #dbscan
        #if len(featList) > 0:
        #	dbTask = getDbScan(wxScore, 0.4, tscore[DBSCAN])
        sc1, sc2, sc3 = compareAlgos(qcc, htc, wxScore)

        #write Tasks to file
        taskDict = {}
        formatResults(session, taskDict, QCC, qcc, sc1)
        formatResults(session, taskDict, HTC, htc, sc2)
        updateStats(taskDict, stats, HTC)
        updateStats(taskDict, stats, QCC)
        taskFile.write(str(sId) + '\t' + str(session[0][USER]) + '\t' +
                       str(taskDict) + '\n')

        taskFeatures1.write(
            str(sId) + '\t' + str(getTaskFeatures(session, taskDict, qcc, sc1)))
        #featFile.write(featString+'\n')
        #sessionFile.write(sessionString+'\n')

      if i % 10000 == 0:
        print 'STATS', i
        print stats

      i += 1
    sessionFile.close()
    #featFile.close()
    taskFile.close()


if __name__ == '__main__':

  main(sys.argv)
