# -*- coding: utf-8 -*-
import sys
'''Import statements go here
'''
import numpy as np
import datetime
from utils import SYMB, SYMB2, WEB, ashleelString, stopSet
import re
import os
from lxml import etree
'''
                AnonID - an anonymous user ID number.
                Query  - the query issued by the user, case shifted with
                                 most punctuation removed.
                QueryTime - the time at which the query was submitted for
                search. 2006-04-22 23:51:18
                ItemRank  - if the user clicked on a search result, the rank of
                the
                                        item on which they clicked is listed.
                ClickURL  - if the user clicked on a search result, the domain
                portion of
                                        the URL in the clicked result is listed.
'''
'''AOL Logs indices
'''
UIND = 0  #user
QIND = 1  #query
TIND = 2  #time
CIND = 3  #click pos
CUIND = 4  #click url
'''AOL Log field names
'''
USER = 'userId'
QTIME = 'queryTime'
QUERY = 'query'
CLICKR = 'clickRank'
CLICKU = 'clickUrl'
'''Utility functions for loading logs and processing the logs
'''


#Load the whole log in the memory, for small files
def getAllAOLQueries(fileName, sep):
  data = np.genfromtxt(fileName, delimiter = sep, skip_header = 1 , \
	names = (USER,QUERY,QTIME,CLICKR, CLICKU), \
	converters = { USER: lambda s: int(s.strip()), QUERY : lambda s : s.strip(), \
	QTIME: np.datetime64,  CLICKR: lambda s : int(s), CLICKU: lambda s : s.strip()})

  return data


#Load only query from file
def getQuery(filename, index):
  for line in open(filename, 'r'):
    split = line.split('\t')
    query1 = normalizeWithoutStem(split[index])
    query = filterStopWordsFromQuery(query1)
    raw_split = query.split()
    if (not hasManyChars(query,raw_split,1,4,70)) and (not hasInapWords(raw_split)) \
        and (not hasManyWords(raw_split,15,40)) and hasAlpha(query) \
        and (not hasWebsite(query)) and ('.com' not in query) and ('www.' not in query):
      print line,


def parseLine(line, sep='\t'):
  entry = {}
  split = line.strip().split(sep)
  try:
    entry[USER] = split[UIND]
    raw_split = re.sub(SYMB, ' ', split[QIND].lower()).split(' ')
    entry[QUERY] = filterStopWordsFromList(raw_split)
    if ('T' in split[TIND]) and ('.' in split[TIND]):
        entry[QTIME] = datetime.datetime.strptime(split[TIND],"%Y-%m-%dT%H:%M:%S.%f")  #np.datetime64(split[2])
    elif 'T' in split[TIND]:
        entry[QTIME] = datetime.datetime.strptime(split[TIND].split('.')[0],"%Y-%m-%dT%H:%M:%S")  #np.datetime64(split[2])
    else: 
        entry[QTIME] = datetime.datetime.strptime(split[TIND], '%Y-%m-%d %H:%M:%S')  #np.datetime64(split[2])
    if len(split) > 4:
      try:
        entry[CLICKR] = int(split[CIND])
      except Exception as err:
        print line, err
      entry[CLICKU] = split[CUIND].lower().strip()
    return entry
  except Exception as err:
    print line, err
    return {}


def stemQuery(string, stemmer):
  split = string.split(' ')
  return ' '.join(stemmer.stem(x) for x in split)


def getUserQueryAsString(entry):
  string = str(entry[USER]) + '\t' + entry[QUERY] + '\t' + str(entry[QTIME])
  if CLICKU in entry:
    return string + '\t' + entry[CLICKU]
  return string


def getSessionsByUsers(filename, queries_to_ignore, timeCutoff=1500):
  users = {}
  lastTime = lastQuery = None
  lastUser = currUser = None
  session = []
  i = 0
  for line in open(filename, 'r'):
    try:
      entry = parseLine(line)
      currTime = entry[QTIME]
      query = entry[QUERY]
      raw_split = query.split()
      currUser = entry[USER]
      if not ((lastTime == None) or \
         (((currTime-lastTime).total_seconds() < timeCutoff \
         or subQuery(query,lastQuery,0.7))\
         and currUser == lastUser)):
        if len(session) > 1:
          if lastUser not in users:
            users[lastUser] = []
          users[lastUser].append(session)
          session = []
          if len(users) % 1000 == 0:
            print 'Finished ', len(users)
      if (lastTime != currTime and lastQuery != query) \
      and hasAlpha(query) \
      and not(hasManyChars(query,raw_split,1,4,70) \
              or hasInapWords(raw_split) \
              or hasManyWords(raw_split,15,40)\
              or hasWebsite(query) or (query in queries_to_ignore)):
        session.append(entry)

      lastTime = currTime
      lastQuery = query
      lastUser = currUser
      i += 1
    except Exception as err:
      print err
      if i > 1:
        break

  if lastUser not in users:
    users[lastUser] = []
  users[lastUser].append(session)
  session = []
  return users


def getSessionWithXML(fileName, storeTitle=False):
  #content = open(fileName,'r').read()
  root = etree.parse(fileName)
  session = []
  docs = {}
  clicks = {}
  title = {}
  summary = {}
  ctitle = {}
  csummary = {}
  k = 0

  for sess in root.iter('session'):
    session = []
    docs = {}
    clicks = {}
    title = {}
    summary = {}
    ctitle = {}
    csummary = {}

    i = 0
    k += 1
    topicId = sess[0].get('num')
    #print k,topicId;
    for entry in sess.iter('interaction'):
      for query in entry.iter('query'):
        line = (query.text).lower()
        #line = re.sub(SYMB, ' ', line)
        #line = re.sub('\s+', ' ', line)
        session.append(line.strip())
        docs[i] = []
        clicks[i] = []
        title[i] = []
        summary[i] = []
        ctitle[i] = []
        csummary[i] = []
        #print i,'query', line

      for result in entry.iter('clueweb12id'):
        docs[i].append(result.text)

      for result in entry.iter('clueweb09id'):
        docs[i].append(result.text)

      for tit in entry.iter('title'):
        txt = tit.text
        if txt:
          title[i].append(txt.lower())

      for content in entry.iter('snippet'):
        txt = content.text
        if txt:
          summary[i].append(txt.lower())

      #print i,'result',result.text
      for clicked in entry.iter('click'):
        for rank in clicked.iter('rank'):
          index = int(rank.text)
          #print i,'click', index, docs[i][index-1]
          try:
            clicks[i].append(docs[i][index - 1])
            ctitle[i].append(title[i][index - 1])
            csummary[i].append(summary[i][index - 1])
          except:
            #print 'ERROR IN CLICK', index, i, docs[i]
            pass
      i += 1
    for curr in sess.iter('currentquery'):
      for query in curr.iter('query'):
        line = query.text.lower()
        #line = re.sub(SYMB, ' ', query.text.lower())
        #line = re.sub('\s+', ' ', line)
        session.append(line)
        #print k, i, query.text
    yield topicId, session, docs, clicks, ctitle, csummary
  yield topicId, session, docs, clicks, ctitle, csummary


  #dont need index since new line marks the session
def getSessionWithNL(fileName):
  session = []
  for line in open(fileName, 'r'):
    line = line.strip().lower()
    line = re.sub(SYMB, ' ', line)
    line = re.sub('\s+', ' ', line)
    if len(line) < 2:
      sid = int(session[0][0:session[0].find(' ')])
      session[0] = session[0][session[0].find(' ') + 1:].strip()
      yield sid, session
      session = []
    else:
      session.append(line.strip())

  sid = int(session[0][0:session[0].find(' ')])
  session[0] = session[0][session[0].find(' ') + 1:].strip()
  yield sid, session


def getSessionTuples(fileName, sep, timeCutoff=1500):
  session = []
  lastTime = lastQuery = None

  for line in open(fileName, 'r'):
    split = line.strip().split(sep)
    try:
      entry = parseLine(line,sep)
      currTime = entry[QTIME] #np.datetime64(split[2])
      query = entry[QUERY]
      raw_split = entry[QUERY].split(' ')
      if not ((lastTime == None) or \
			((currTime -lastTime).total_seconds()<timeCutoff)):
        #if len(session) > 1:
        #print currTime, lastTime, (currTime - lastTime).total_seconds(), lastUser, currUser
        yield session
        session = []

      if (lastTime != currTime or lastQuery != query) \
			and (not hasManyChars(query,raw_split,1,4,70) \
			and not hasInapWords(raw_split) and not hasManyWords(raw_split,15,40) \
			and hasAlpha(query)):  # hasWebsite(query)):
        session.append(entry)

      lastTime = currTime
      lastQuery = query
    except Exception as err:
      #	print line.strip(), query, err, err.args
      pass
  yield session


#get user sessions with only user queries.
def getSessionWithQuery(fileName, timeCutoff=1500, sep='\t'):
  session = []
  lastUser = lastTime = lastQuery = None

  for line in open(fileName, 'r'):
    try:
      entry = parseLine(line,sep)
      currTime = entry[QTIME] #datetime.datetime.strptime(split[TIND], '%Y-%m-%d %H:%M:%S')  #np.datetime64(split[2])
      query = entry[QUERY]
      currUser = entry[USER]
      raw_split = query.split(' ')
      if not ((lastTime == None) or \
			((currTime -lastTime).total_seconds()<timeCutoff \
			 and currUser == lastUser)):
        #if len(session) > 1:
        #print currTime, lastTime, (currTime - lastTime).total_seconds(), lastUser, currUser
        yield session
        session = []

      if (lastTime != currTime or lastQuery != query) \
			and (not hasManyChars(query,raw_split,1,4,70) \
			and not hasInapWords(raw_split) and not hasManyWords(raw_split,15,40) \
			and hasAlpha(query)):  # hasWebsite(query)):
        session.append(query)

      lastUser = currUser
      lastTime = currTime
      lastQuery = query
    except Exception as err:
      print line.strip(), err, err.args
      pass

  yield session


  # get the session and related data
def getSessionWithInfo(fileName, timeCutoff=1500):
  iFile = open(fileName, 'r')
  currSession = []
  iFile.readline()
  currTime = lastTime = None
  currUser = lastUser = None
  lastQuery = None
  currSessionString = ''
  #queryVector = []
  i = 1
  for line in iFile:
    entry = parseLine(line)
    query = entry[QUERY]
    raw_split = query.split(' ')
    #queryVector.append(raw_split)
    currTime = entry[QTIME]
    currUser = entry[USER]
    if not ((lastTime == None) or \
		(((currTime -lastTime).total_seconds() < timeCutoff or subQuery(query,lastQuery,0.7))\
		and currUser == lastUser)):
      #if not (lastTime == None or currUser == lastUser):
      # start a new session
      if len(currSession) > 0:
        i += 1
        yield lastUser, i - 1, currSession, currSessionString  #, queryVector
        currSession = []
        #queryVector = []
        currSessionString = ''

    if not hasManyChars(query,raw_split,1,4,70) \
		and not hasInapWords(raw_split) and not hasManyWords(raw_split,15,40) \
		and hasAlpha(query) and not hasWebsite(query):
      currSession.append(entry)
      currSessionString += str(i) + '\t' + line
    lastTime = currTime
    lastUser = currUser
    lastQuery = query

  yield lastUser, i - 1, currSession, currSessionString  #, queryVector

  iFile.close()


#check if q2 is substring of q1
def subQuery(q1, q2, thresh):
  s1 = set(q1.split(' '))
  s2 = set(q2.split(' '))
  n = len(s1.intersection(s2)) * 1.0
  jIndex = n / (len(s1) + len(s2) - n)
  #print q1 in q2, q2 in q1, q1 == q2,s1, s2, n, jIndex
  if (q1 == q2) or (q1 in q2) or (q2 in q1) or jIndex > thresh:
    return True
  return False


#for queries with unacceptable words
def hasInapWords(raw_split):
  for entry in raw_split:
    if entry in ashleelString:
      return True
  return False


#for multiple word queries
#checks if too many words
#or lengthy words in query
def hasManyWords(raw_split, wordCount, wordLength):
  if len(raw_split) > wordCount:
    return True
  for entry in raw_split:
    if len(entry) > wordLength:
      return True
  return False


#for one word queries
def hasManyChars(query, raw_split, wmin, cmin, cmax):
  if len(raw_split) == wmin and (len(query) > cmax or len(query) < cmin):
    return True
  return False


#for alphabet queries
def hasAlpha(query):
  return bool(re.search('[a-zA-Z]', query))


#find if query is a website
def hasWebsite(query):
  return WEB.match(query)


#clear symbols, numbers and stem
def normalize(query, stemmer):

  split = query.split()
  if hasWebsite(query) or hasInapWords(split):
    return ''
  #replace symbols
  query = re.sub(SYMB, ' ', query)

  #remove numbers
  query = re.sub('\d+', '', query)

  #remove spaces
  query = re.sub('\s+', ' ', query)

  nQuery = ''
  #remove words less than 2 letters
  for entry in query.split():
    stemmed = stemmer.stem(entry)
    if len(stemmed) > 1 and stemmed not in stopSet:
      nQuery += stemmed + ' '

  return nQuery.strip()


def normalizeWithoutStem(query):
  if hasWebsite(query):
    return ''
  #replace symbols
  query = re.sub(SYMB, ' ', query)

  #remove numbers
  query = re.sub('\d+', '', query)

  #remove spaces
  query = re.sub('\s+', ' ', query)
  return query


def normalizeWithStopWordRemoval(query):
  if hasWebsite(query):
    return ''
  #replace symbols
  query = re.sub(SYMB, ' ', query)

  #remove numbers
  query = re.sub('\d+', '', query)

  #remove spaces
  query = re.sub('\s+', ' ', query)

  qset = set(query.strip().split())
  qset -= stopSet

  return ' '.join(qset)


#get term list from a query
def getQueryTerms(query):

  if hasWebsite(query):
    return []
  #replace symbols
  query = re.sub(SYMB, ' ', query)

  #repace numbers
  query = re.sub('\d+', '', query)

  #fix spaces
  query = re.sub('\s+', ' ', query)

  qset = set(query.strip().split())
  qset -= stopSet
  return qset
  #list(qset)


  #get term list from a query
def getQueryTermsStemmed(query, stemmer):

  if hasWebsite(query):
    return set()
  #replace symbols
  query = re.sub(SYMB, ' ', query)

  #repace numbers
  query = re.sub('\d+', '', query)

  #fix spaces
  query = re.sub('\s+', ' ', query)

  qset = set()
  for entry in query.strip().split(' '):
    if len(entry) > 2:
      qset.add(stemmer.stem(entry))

  qset -= stopSet

  return qset
  #list(qset)


  #remove stop words from split
def filterStopWordsFromList(split):
  string = ''
  for entry in split:
    if entry not in stopSet:
      string += ' ' + entry
  return string.strip()


#remove the stopwords from query
def filterStopWordsFromQuery(query):
  split = query.split()
  string = ''
  for entry in split:
    if entry not in stopSet and len(entry) > 1:
      string += ' ' + entry
  return string.strip()


#remove symbols
def filterSymbolsFromQuery(query):
  #replace symbols
  query = re.sub(SYMB, ' ', query)
  query = re.sub('\s+', ' ', query)
  return query.strip()


#replace the numbers with replace string
def filterNumbersFromQuery(query, rep):
  split = query.split()
  string = ''
  for entry in split:
    string += re.sub('[0-9]+', rep, entry)
  return string


  #replace the numbers with replace string
def filterNumbersFromList(split, rep):
  string = ''
  for entry in split:
    string += re.sub('[0-9]+', rep, entry)
  return string


def updateVector(query, sessionVector):
  split = query.split(' ')
  for word in split:
    if word not in stopSet and len(word) > 1:
      if word not in sessionVector:
        sessionVector[word] = 0
      sessionVector[word] += 1


def getQueryString(sessionVector):
  vString = ''
  for entry, value in sessionVector.iteritems():
    vString += entry + '^' + str(value) + ' '
  return vString


def findSessionStats(folderName):
  stats = {'#queries': 0, '#sessions': 0, '#users': 0, '#words': 0}
  dist = {'word_query': {}, 'query_session': {}}
  userQueryCountList = {}
  #iterating over logs
  for iFile in os.listdir(folderName):
    print iFile
    #logs = loadFile(folderName+'\\'+iFile, "\t")
    #iterating over sessions
    for lastUser, sessId, currSession, sessionString in getSessionWithInfo(
        folderName + '/' + iFile, 1500):
      noQueries = len(currSession)
      if lastUser not in userQueryCountList:
        userQueryCountList[lastUser] = 0
        stats['#users'] += 1
      userQueryCountList[lastUser] += noQueries
      if noQueries not in dist['query_session']:
        dist['query_session'][noQueries] = 0
      dist['query_session'][noQueries] += 1
      stats['#queries'] += noQueries
      stats['#sessions'] += 1
      for entry in currSession:
        split = entry[QUERY].split()
        dist['word_query'][entry] = dist['word_query'].setdefault(
            entry, 0) + len(split)
        stats['#words'] += len(split)

    print '\nPrinting Stats'
  for entry, value in stats.iteritems():
    print entry, value

  print '\nPrinting Dist'
  for entry, dist in dist.iteritems():
    print entry
    for key, value in dist.iteritems():
      print key, value

  print '\nPrinting User Session info'
  for uId, count in userQueryCountList.iteritems():
    print uId, count


if __name__ == '__main__':
  arg = sys.argv
  getQuery(arg[1], 0)
