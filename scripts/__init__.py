# -*- coding: utf-8 -*-
from queryLog import getSessionWithQuery, hasInapWords, normalizeWithoutStem
from entity.category import getCats
from entity.category.ds import loadClusters
import sys, os, ast, random
from utils import stopSet, getNGramsAsList, ashleelString, get_cosine,\
 loadFileInDict,  loadFileInList
from dbPedia import loadCategories, loadInstancesInList
#import codecs
#import urllib
#import distance
from nltk import stem
from queryLog import normalize, filterStopWordsFromQuery
from entity.category.ds import loadClustersWithQueryFile
from features import readWeightMatrix
from features.featureManager import FeatureManager
from utils import getDictFromSet
from features.queryFeature import QueryFeature


def buildBigramSet(fileName):
  setb = set()
  for line in open(fileName, 'r'):
    split = line.strip().split('\t')
    setb.add(split[0].strip())
  return setb


def buildQueryList(catFile, catFolderDict, tagFile):
  catSet = set()
  queryDict = {}
  for line in open(catFile, 'r'):
    split = line.split('\t')
    cat = split[0].strip()
    catSet.add(cat)

  print len(catSet)

  for cat in catSet:
    if cat in catFolderDict:
      for line in open(catFolderDict[cat], 'r'):
        split = line.split('\t')
        queryDict[split[0].strip()] = 1.0

  for line in open(tagFile, 'r'):
    split = line.split('\t')
    query = split[0].strip()
    if query in queryDict:
      queryDict[query] = split[1].strip()

  print 'Loaded queries ', len(queryDict)
  return queryDict


def populateDatasetWithBigrams(logFile, bigramSet, queryFile):
  sid = 0

  queryList = buildBigramSet(queryFile)

  stemmer = stem.porter.PorterStemmer()
  for session in getSessionWithQuery(logFile):
    sessionStr = ' '.join(session)
    sessionSet = set(getNGramsAsList(sessionStr, 2))
    inter = sessionSet & bigramSet
    #print len(sessionSet), len(bigramSet), inter

    if len(inter) > 0:
      lastq = None
      for q in session:
        if q in queryList:
          q = normalize(q, stemmer)
          if lastq != q and len(q) > 1:
            print sid, '\t', q
          lastq = q
    sid += 1


def populateDataset(logFile, queryList):
  sid = 1
  sessionList = {}
  for session in getSessionWithQuery(logFile):
    prints = False
    #print len(session)
    for entry in session:
      if entry in queryList:
        #prints = True;
        if entry not in sessionList:
          sessionList[entry] = {}
        if sid not in sessionList[entry]:
          sessionList[entry][sid] = 0.0
        sessionList[entry][sid] += 1.0
      #else:

      #	print 'NOT FOUND ',entry
      #print session
    sid += 1

  for entry, sessionCount in sessionList.iteritems():
    print entry, '\t', sessionCount
    #if prints:
    #lastq = None;
    #for q in session:
    #if lastq != q:
    #if q in queryList:
    #print sid,'\t', q,'\t', queryList[q]
    #else:
    #print sid,'\t', q
    #lastq = q;


def filterSessionWithLength(fileName):
  session = []
  lastSes = None
  for line in open(fileName, 'r'):
    split = line.split('\t')
    sessNo = int(split[0])
    if lastSes != sessNo:
      sessionSet = set((' '.join(session)).split())
      inter = sessionSet & ashleelString

      if len(inter) == 0 and len(session) > 2 and len(session) < 100:
        for entry in session:
          print entry,
      session = []
    session.append(line)
    lastSes = sessNo


def filterSessionWithQuery(fileName, queryFile):
  queryList = loadFileInList(queryFile)
  for line in open(fileName, 'r'):
    split = line.split('\t')
    query = split[0].strip()
    nQuery = ''
    for entry in query.split():
      if len(entry) > 1:
        nQuery += ' ' + entry
    nQuery = nQuery.strip()
    if (nQuery in queryList) or (query in queryList):
      print line,


def findUniqueQueries(fileName, file2, index):

  toCheck = {}
  #for line in open(file2,'r'):
  ##split = line.split('\t');
  ##query = split[0].strip()
  #spotDict = ast.literal_eval(line)
  #query = spotDict['text']
  #toCheck[query] = 1.0
  #
  #print len(toCheck)
  #queryList = {}
  for line in open(fileName, 'r'):
    split = line.strip().split('\t')
    query = split[0].strip()
    #if query in toCheck:
    #	print query
    toCheck[query] = 1.0

  print len(toCheck)
  #if query not in toCheck:
  #rsplit = query.split()
  #if not hasInapWords(rsplit):
  #if query not in queryList:
  #queryList[query] = 1.0
  #else:
  #queryList[query] +=1.0
  ##else:
  #print query
  stemmer = stem.porter.PorterStemmer()

  for line in open(file2, 'r'):
    split = line.split('\t')
    entry = split[index].strip()
    norm = normalize(entry, stemmer)
    if norm in toCheck and len(norm) > 3:
      print line,
  #for entry in sorted(queryList.items(), reverse = True, key = lambda x :x[1]):
  #	print entry[0],'\t', entry[1]


def sampleSessions(sessiontrackFile, biGramFile, freqFile, sessionFileToPrune):
  #if the session contains any session Track query
  #if it contains top 100 bigrams 20 unigrams
  # if the session average query count > 1/ session length
  #else rand number is

  sessionTrackQueries = {}
  #load sessionTrack queries
  for line in open(sessiontrackFile, 'r'):
    query = normalizeWithoutStem(line.strip().lower())
    sessionTrackQueries[query] = 1.0
    sessionTrackQueries[line.strip().lower()] = 1.0

  biGrams = set()
  for line in open(biGramFile, 'r'):
    split = line.split('\t')
    biGrams.add(split[0])
    if len(biGrams) == 2500:
      break

  freq = {}
  for line in open(freqFile, 'r'):
    split = line.split('\t')
    freq[split[0].strip()] = float(split[1])

  avgFreq = 0.0
  lastSes = None
  session = []
  hasQuery = False
  hasBigram = False
  for line in open(sessionFileToPrune, 'r'):
    split = line.split('\t')
    sessNo = int(split[0])

    query = split[1].strip()
    if query in sessionTrackQueries:
      hasQuery = True

    nGrams = set(getNGramsAsList(query, 2))
    inter = nGrams & biGrams
    if len(inter) > 0:
      hasBigram = True

    avgFreq += freq[query]
    if lastSes != sessNo:
      rnum = random.random()
      if len(session) > 0:
        avgFreq /= len(session)
      if (rnum > 0.80 or hasQuery or hasBigram) and (len(session) > 3
                                                  ) and avgFreq > 90:
        for entry in session:
          print entry,
      session = []
      hasQuery = False
      hasBigram = False

    session.append(line)
    lastSes = sessNo


def findEntityCategory(entFile, categoryFile, instanceFile):
  categoryList = loadCategories(categoryFile)
  instanceList = loadInstancesInList(instanceFile)
  for line in open(entFile, 'r'):
    #entry= str(line.strip().lower())
    #entry =  entry[2:-1].strip()
    #entry = unicode(entry1)

    spotDict = ast.literal_eval(line.lower())
    spots = spotDict['spots']
    i = 0
    for spot in spots:
      ename = (spot['wikiname']).encode('unicode-escape')
      if ename in categoryList:
        spotDict['spots'][i][u'cat'] = categoryList[ename]
      else:
        print 'Cat not Found ', ename
        spotDict['spots'][i][u'cat'] = []

      if ename in instanceList:
        spotDict['spots'][i][u'type'] = instanceList[ename]
      else:
        print 'Instance not Found ', ename
        spotDict['spots'][i][u'type'] = []
      i += 1
    print spotDict


def createJointDatasetForEntities(queryList, onlyId, tagged2, catList,
                                  entityTitle, outFile):

  #2 entity files -- one with wiki names and not_wiki ==> Merge them into one
  #Categories are listed with entity name
  # file with entity id and name for not_wiki
  #load id-> title mapping
  idNameDict = {}
  for line in open(entityTitle, 'r'):
    idDict = ast.literal_eval(line.lower())
    idNameDict[idDict['code']] = idDict['title']
  #load title-> cat mapping
  nameCatDict = {}
  for line in open(catList, 'r'):
    split = line.split('\t')
    nameCatDict[split[0].strip()] = split[1].strip()

  #load queries
  queryDict = {}
  for line in open(queryList, 'r'):
    queryDict[line.strip()] = 1.0

  print len(queryDict), len(nameCatDict), len(idNameDict)
  out = open(outFile, 'w')

  #file with id info no name and category
  for line in open(onlyId, 'r'):
    spot = ast.literal_eval(line)
    if spot['text'] in queryDict:
      spots = spot['spots']
      i = 0
      for entry in spots:
        eid = entry['entity']

        #get the wikiname
        if eid in idNameDict:
          spot['spots'][i][u'wikiname'] = idNameDict[eid]
          #get the category
          uniName = idNameDict[eid].encode('unicode-escape')
          if uniName in nameCatDict:
            spot['spots'][i][u'cat'] = nameCatDict[uniName]
          else:
            print 'Cat not Found ', uniName
            spot['spots'][i][u'cat'] = '[]'
        else:
          spot['spots'][i][u'wikiname'] = ''
          spot['spots'][i][u'cat'] = '[]'

          print 'Entity not Found! ', eid
        i += 1

      out.write(str(spot) + '\n')

  for line in open(tagged2, 'r'):
    spot = ast.literal_eval(line.lower())
    spot['text'] = spot['text'].strip()
    if spot['text'] in queryDict:
      spots = spot['spots']
      i = 0
      for entry in spots:
        ename = str(entry['wikiname']).encode('unicode-escape')
        #get the wikiname
        if ename in nameCatDict:
          spot['spots'][i][u'cat'] = nameCatDict[ename]
        else:
          print 'Cat not Found ', ename
          spot['spots'][i][u'cat'] = '[]'
        i += 1
      out.write(str(spot) + '\n')

  out.close()


def mergeFeatures(featFile, taggedFile, newFile):
  entFeatDict = {}
  stemmer = stem.porter.PorterStemmer()
  for line in open(taggedFile, 'r'):
    spotDict = ast.literal_eval(line.strip())
    normQuery = normalize(spotDict['text'], stemmer)
    if normQuery not in entFeatDict:
      entFeatDict[normQuery] = []
    #convert ent stuff into a dictionary
    entVect = {}
    catVect = {}
    for entry in spotDict['spots']:
      entVect[entry['wikiname']] = 1.0
      cats = ast.literal_eval(entry['cat'])
      for cat in cats:
        if cat not in catVect:
          catVect[cat] = 0.0
        catVect[cat] += 1.0
    entFeatDict[normQuery].append(entVect)
    entFeatDict[normQuery].append(catVect)

  print len(entFeatDict)

  featDict = {}

  outF = open(newFile, 'w')

  for line in open(featFile, 'r'):
    split = line.split('\t')
    query = split[0].strip()
    featDict[query] = []
    for entry in split[1:]:
      featDict[query].append(entry.strip())
    if query in entFeatDict:
      featDict[query] = featDict[query] + entFeatDict[query]
    else:
      featDict[query] = featDict[query] + [{}, {}]
      print 'Query not tagged! ', query

    outF.write(query)
    for entry in featDict[query]:
      outF.write('\t' + str(entry))
    outF.write('\n')
    #convert cat stuff into a dictionary

  outF.close()


def prepareTrainingDataset(sameTaskFile, dataSubsetFile, taskQueryFile):
  #select only those pairs which have both queries in queryFile
  tQueryList = {}
  #queryKey = {}
  keyQuery = {}
  for line in open(taskQueryFile, 'r'):
    tQueryList[line.strip()] = 1.0

  print len(tQueryList)

  for line in open(sameTaskFile, 'r'):
    split = line.split('\t')
    query = split[4].strip()
    key = '_'.join(split[:3])
    if query in tQueryList:
      if key not in keyQuery:
        keyQuery[key] = {}
      keyQuery[key][query] = 1.0

  keys = keyQuery.keys()
  newDict = {}
  skip = {}
  for i in range(len(keys)):
    if i not in skip:
      newDict[i] = keyQuery[keys[i]]
      for j in range(i + 1, len(keys) - 1):
        if j not in skip:
          cos = get_cosine(keyQuery[keys[i]], keyQuery[keys[j]])
          if cos > 0.70:
            newDict[i].update(keyQuery[keys[j]])
            skip[j] = True

  for entry, queries in newDict.items():
    if len(queries) > 1:
      print '\t'.join(queries.keys())
  #	if len(qlist) > 1:
  #print '\t'.join(qlist)

  #for line in open(dataSubsetFile,'r'):
  #split = line.strip().split('\t')
  #key = split[0]+'_'+split[1]
  #keyQuery[key] = split[-1]
  ##queryKey[split[-1]] = key

  #for line in open(sameTaskFile,'r'):
  #split = line.strip().split('\t')
  #key1 = split[1]+'_'+split[2]
  #key2 = split[1]+'_'+split[3]
  #if key1 in keyQuery and key2 in keyQuery:
  #q1 = keyQuery[key1]
  #q2 = keyQuery[key2]
  #
  #if q1 in tQueryList and q2 in tQueryList:
  #print split[1]+'\t'+q1+'\t'+q2+'\t'+split[-1]


def combineHenry(fileName):
  cluster = {}
  for line in open(fileName, 'r'):
    split = line.split('\t')
    if split[0] not in cluster:
      cluster[split[0]] = set()
    trim = split[1].strip()
    if trim != split[0]:
      cluster[split[0]].add(trim)

  for entry, sets in cluster.items():
    print entry + '\t' + '\t'.join(sets)


def filterQueries(queryCountFile, queryFile, trainFile, sessionFile):
  queryCount = loadFileInDict(queryCountFile)

  #print len(queryCount)
  toPrint = set()
  toFilter = loadFileInList(queryFile)
  training = loadFileInList(trainFile)
  session = loadFileInList(sessionFile)
  stemmer = stem.porter.PorterStemmer()
  for entry in toFilter:

    if (entry in queryCount) and ((queryCount[entry] > 15) or \
		 (entry in training) or (entry in session)):
      entry1 = normalize(entry, stemmer)
      toPrint.add(entry1)
      #print entry, '\t', queryCount[entry]
  for entry in toPrint:
    print entry


def sampleEntities(fileName, number):
  entities = {}
  queries = {}
  for line in open(fileName, 'r'):
    split = line.split('\t')
    entityDict = ast.literal_eval(split[5])
    for entry, count in entityDict.items():
      if entry not in entities:
        entities[entry] = 0.0
        queries[entry] = set()
      entities[entry] += count
      qsplit = split[0].split()
      if len(qsplit) < 4:
        queries[entry].add(split[0].strip())
  sent = sorted(entities.items(), reverse=True, key=lambda x: x[1])

  sampled = random.sample(sent[:100], min(number, 100))

  for entry in sampled:
    ent = entry[0].replace('_', ' ')
    for query in queries[entry[0]]:
      if query != ent:
        print ent + '\t' + query


def sampleQueryPairs(fileName, weightFile, featFile):
  weightMatrix = readWeightMatrix(weightFile)
  featMan = FeatureManager()
  featMan.loadQueries(featFile)
  idDict = featMan.returnIdDict()
  qDict = featMan.returnQueryDict()

  clusters = loadClustersWithQueryFile(fileName, idDict)
  done = {}
  for entry in clusters:
    minPair = None
    maxPair = None
    minDist = 1000
    maxDist = 0
    #print entry
    if len(entry) > 3:
      sentry = sorted(entry)
      for i in range(len(sentry) - 1):
        for j in range(i + 1, len(sentry)):
          try:
            if weightMatrix[sentry[i]][sentry[j]] < minDist:
              minDist = weightMatrix[sentry[i]][sentry[j]]
              minPair = (qDict[sentry[i]], qDict[sentry[j]])
            if weightMatrix[sentry[i]][sentry[j]] > maxDist:
              maxDist = weightMatrix[sentry[i]][sentry[j]]
              maxPair = (qDict[sentry[i]], qDict[sentry[j]])
          except:
            dist = random.uniform(0.8, 1.0)
            if dist < minDist:
              minDist = dist
              minPair = (qDict[sentry[i]], qDict[sentry[j]])
            if dist > maxDist:
              maxDist = dist
              maxPair = (qDict[sentry[i]], qDict[sentry[j]])

    if minPair and minPair[0] not in done and minPair[1] not in done:
      print 'Min\t' + minPair[0] + '\t' + minPair[1]

    if maxPair and maxPair[0] not in done and maxPair[1] not in done:
      print 'Max\t' + maxPair[0] + '\t' + maxPair[1]

    if minPair:
      done[minPair[0]] = 1
      done[minPair[1]] = 1
    if maxPair:
      done[maxPair[0]] = 1
      done[maxPair[1]] = 1


def sampleEntityQueries(featFile, clusterFile):
  queries = {}
  for line in open(featFile, 'r'):
    split = line.split('\t')
    entityDict = ast.literal_eval(split[5])
    qsplit = split[0].split()

    if len(qsplit) > 2:
      queries[split[0].strip()] = entityDict

  outFile = open('EntityQueries.sample', 'w')
  globalEnt = {}
  entTerms = {}
  for cluster in loadClusters(clusterFile):
    if len(cluster) > 4:
      cent = {}
      for query in cluster:
        if query in queries:
          for entry, value in queries[query].items():
            if entry not in cent:
              cent[entry] = 0.0
            cent[entry] += value
      entSort = sorted(cent.items(), reverse=True, key=lambda x: x[1])
      toPrint = {}
      if len(entSort) > 0:
        bestEnt = entSort[0][0]
        if bestEnt not in globalEnt:
          globalEnt[bestEnt] = []
          entTerms[bestEnt] = set([])
        for query in cluster:
          if query in queries and bestEnt in queries[query]:
            qsplit = query.split()  #getNGramsAsList(query,2) #
            for entry in qsplit:
              if len(entry) > 2  and entry not in stopSet \
							and entry not in bestEnt and entry not in ashleelString:
                if entry not in toPrint:
                  toPrint[entry] = 0.0
                toPrint[entry] += 1.0
        sortP = sorted(toPrint.items(), reverse=True, key=lambda x: x[1])
        fset = set([])
        if len(sortP) > 3:
          for entry in sortP:
            if entry[1] > 1:
              fset.add(entry[0])
            if len(fset) > 7:
              break
          covered = 0
          for entry in fset:
            if entry not in entTerms[bestEnt]:
              entTerms[bestEnt].add(entry)
            else:
              covered += 1.0
          if len(fset) > 3 and covered / len(fset) < .20:
            globalEnt[bestEnt].append(fset)
          #else:
          #	print covered, len(fset)
  for bestEnt, sList in globalEnt.items():
    if len(sList) > 1:
      for sortP in sList:
        outFile.write(bestEnt.encode('utf-8') + '\t' + '\t'.join(sortP) + '\n')
  outFile.close()


def sampleEntityTerms(folderName, oFile):
  globalEnt = {}
  entTerms = {}
  for fileName in os.listdir(folderName):

    for line in open(folderName + '/' + fileName, 'r'):
      split = line.split('\t')
      #try:
      entSet = set([])
      wordSet = set([])

      if 'NA' not in line and len(split) > 3:
        entList = split[2].strip().split(' ')
        for entry in entList:
          if len(entry) > 2:
            wsplit = entry.split(':')
            count = float(wsplit[1])
            if count > 10:
              entSet.add(wsplit[0])
              if len(entSet) > 1:
                break

        if len(entSet) > 1:
          entT = tuple(sorted(entSet))
          if entT not in globalEnt:
            globalEnt[entT] = []
            entTerms[entT] = {}
          wordList = split[3].strip().split(' ')
          for entry in wordList:
            wsplit = entry.split(':')
            count = float(wsplit[1])
            if count > 10:
              wordSet.add(wsplit[0])

          if len(wordSet) > 4:
            covered = 0.0
            for entry in wordSet:
              if entry in entTerms[entT]:
                covered += 1.0
            for entry in wordSet:
              entTerms[entT][entry] = 1.0
            if covered / len(wordSet) < 0.10:
              globalEnt[entT].append([fileName, sorted(wordSet)])
      #except Exception as ex:
      #print ex
      #print line
      #if 'NA' not in line:
      #print 'ERROR parsing ',line;

  outFile = open(oFile, 'w')
  for bestEnt, sList in globalEnt.items():
    if len(sList) > 1 and 'lyrics' not in bestEnt:
      for arr in sList:
        #cat = arr[0][:arr[0].rfind('_')]+cat+'\t'
        sortP = arr[1]
        outFile.write(' '.join(bestEnt) + '\t' + '\t'.join(sortP) + '\n')
  outFile.close()


def mergeFeatures(file1, file2):
  f2 = {}
  for line in open(file2, 'r'):
    split = line.split('\t')
    if split[0].strip() not in f2:
      f2[split[0].strip()] = ast.literal_eval(split[1])

  for line in open(file1, 'r'):
    split = line.split('\t')
    if split[0].strip() in f2:
      print line.strip() + '\t' + str(f2[split[0].strip()])
    else:
      print line.strip() + '\t{}'


def mergeWithrel(relFile, outFile):
  key = {}
  for line in open(relFile, 'r'):
    split = line.strip().split(' ')
    key[split[0] + ' ' + split[1]] = split[2]
  for line in open(outFile, 'r'):
    split = line.split(',')
    k = split[0] + ' ' + split[2]
    if k in key:
      print ' '.join(split[0:3]), key[k], split[4].strip()


def generatePhraseFeatures(featureFile, spotFile, outFile):
  #load features for queries
  qfeatMan = FeatureManager()
  qfeatMan.readFeatures(featureFile)

  pid = 0
  pfeatMan = FeatureManager()

  #generate features for phrases
  for query, pList in generatePhrases(spotFile):
    qkey, qfeat = qfeatMan.returnFeature(query)
    #print query, qkey
    if qkey:
      #print query, pList
      for phrase in pList:
        qVect = getDictFromSet(phrase.split())
        ngrams = getNGramsAsList(phrase, 2)
        url = qfeat.returnUrl()
        user = qfeat.returnUsers()
        ent = qfeat.returnEntities()
        cat = qfeat.returnCategories()
        typ = qfeat.returnType()
        sess = qfeat.returnSessions()
        if 'tournament' in phrase:
          print query, phrase
          print sess
          print typ
          print ent
        nFeature = QueryFeature(phrase, ngrams, qVect, url, user, sess, ent,
                                cat, typ)
        pfeatMan.addFeature(phrase, pid, nFeature)
        pid += 1

  pfeatMan.writeFeatures(outFile)


def generatePhrases(labelFile):
  stemmer = stem.porter.PorterStemmer()
  for line in open(labelFile, 'r'):
    pList = []
    spotDict = ast.literal_eval(line)
    query = spotDict['text']
    text = spotDict['text']
    for entry in spotDict['spots']:
      mention = entry['mention']
      text = text.replace(mention, '<entity>').strip()

    if len(text) > 2:
      split = text.split('<entity>')
      for entry in split:
        entry = normalize(entry, stemmer).strip()
        if len(entry) > 1:
          pList.append(entry)
      yield query, pList


def generatePhraseStats(labelFile):
  phrases = {}
  stemmer = stem.porter.PorterStemmer()
  entQuery = 0.0
  for line in open(labelFile, 'r'):

    try:
      entList = []
      spotDict = ast.literal_eval(line)
      text = spotDict['text']
      for entry in spotDict['spots']:
        mention = entry['mention']
        text = text.replace(mention, '<entity>').strip()
        entList.append(entry['wikiname'])

      if len(text) > 2:
        split = text.split('<entity>')
        if len(split) == 1:
          entQuery += 1.0
        for entry in split:
          entry = normalize(entry, stemmer).strip()

          if entry not in phrases:
            phrases[entry] = {}

          for entity in entList:
            if entity not in phrases[entry]:
              phrases[entry][entity] = 0.0
            phrases[entry][entity] += 1.0
          #phrases[entry]+=1.0
    except:
      pass
      #print line
  print entQuery

  words = {}
  for entry in sorted(phrases.items(), reverse=True, key=lambda x: len(x[1])):
    split = entry[0].split()
    wlen = len(split)
    if wlen not in words:
      words[wlen] = 0.0
    words[wlen] += 1.0
    print entry
  for entry, count in words.items():
    print entry, count


def getLabels(phrase, labelFile):
  phraseList = {}
  for line in open(phrase, 'r'):
    split = line.split('\t')
    phraseList[split[0]] = 1.0
  for line in open(labelFile, 'r'):
    split = line.split('\t')
    q1 = set(split[1].split())
    q2 = set(split[2].split())
    label = split[3].strip()
    fq1 = False
    fq2 = False
    p1 = None
    p2 = None
    for entry in phraseList.keys():
      esplit = set(entry.split())

      int1 = len(esplit - q1)
      int2 = len(esplit - q2)
      if int1 == 0:
        fq1 = True
        p1 = entry
      if int2 == 0:
        fq2 = True
        p2 = entry

    if fq1 and fq2 and p1 != p2:
      print p1, '\t', p2, '\t', label

      #argv[1] = catFile / bigram file
      #argv[2] = catFolder
      #argv[3] = tagged query file
      #argv[4] = logFile


if __name__ == '__main__':
  argv = sys.argv
  #catFiles = getCats(argv[2])
  #queryDict = buildQueryList(argv[1], catFiles, argv[3])
  #populateDataset(argv[4], queryDict)
  #filterSessionWithLength(argv[1])
  #bigramSet = buildBigramSet(argv[1])
  #populateDatasetWithBigrams(argv[2],bigramSet,argv[3])

  #findUniqueQueries(argv[2], argv[1], 1)
  #sampleSessions(argv[1],argv[2],argv[3], argv[4])
  #findEntityCategory(argv[1],argv[2],argv[3])
  #1 = query list, 2 = all Aol tagged (new dexter), 3 = aol tagged with wikiName
  #4 = cat list , 5= entity title mapping, 6 = out file
  #createJointDatasetForEntities(argv[1], argv[2],argv[3],argv[4],argv[5], argv[6])
  #mergeFeatures(argv[1],argv[2],argv[3])
  #findCatQueryDist(argv[1])
  #prepareTrainingDataset(argv[1],argv[2],argv[3])
  #prepareTrainingDataset(argv[1],None,argv[2])
  #combineHenry(argv[1])

  #filterQueries(argv[1],argv[2],argv[3],argv[4])
  #filterSessionWithQuery(argv[1],argv[2])
  #sampleEntities(argv[1],int(argv[2]))
  #sampleQueryPairs(argv[1],argv[2],argv[3])
  #sampleEntityQueries(argv[1],argv[2])
  #sampleEntityTerms(argv[1],argv[2])
  #queryList =  loadFileInList(argv[1])
  #populateDataset(argv[2],queryList)
  #mergeFeatures(argv[1],argv[2])
  #mergeWithrel(argv[1],argv[2])
  #generatePhraseLabels(argv[1])
  #generatePhraseFeatures(argv[1],argv[2],argv[3])
  getLabels(argv[1], argv[2])
