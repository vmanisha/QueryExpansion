# -*- coding: utf-8 -*-

'''
Import statements go here
'''
import numpy as np
import datetime
from Utils import SYMB, WEB, ashleelString, stopSet
import re
import os

'''
		AnonID - an anonymous user ID number.
		Query  - the query issued by the user, case shifted with
				 most punctuation removed.
		QueryTime - the time at which the query was submitted for search. 2006-04-22 23:51:18
		ItemRank  - if the user clicked on a search result, the rank of the
					item on which they clicked is listed.
		ClickURL  - if the user clicked on a search result, the domain portion of
					the URL in the clicked result is listed.
'''

'''
AOL Logs indices
'''
UIND=0 #user
QIND=1 #query
TIND=2 #time
CIND=3 #click pos
CUIND=4 #click url

'''
AOL Log field names
'''
USER = 'userId'
QTIME = 'queryTime'
QUERY = 'query'
CLICKR = 'clickRank'
CLICKU = 'clickUrl'

'''
	#print the following
	# number of sessions
	# number of users
	# number of sessions per user
	# number of queries per session
	# number of words in a query
	# distributions :
		# frequency of users per session count
		# frequency of queries per session
		# frequency of words per query
		
'''


'''
Utility functions for loading logs
and processing the logs
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
	for line in open(filename,'r'):
		split = line.split('\t')
                raw_split = re.sub(SYMB, ' ', split[index].lower()).split(' ')
                query = filterStopWordsFromList(raw_split)
                if hasManyChars(query,raw_split,1,4,70) \
					and hasInapWords(raw_split) and hasManyWords(raw_split,15,40) \
					and hasAlpha(query) and hasWebsite(query):
						yield query

def parseLine(line):
	entry = {}
	split= line.strip().split('\t')
	entry[USER]=int(split[UIND])
	raw_split = re.sub(SYMB, ' ',split[QIND].lower()).split(' ')
	entry[QUERY] = filterStopWordsFromList(raw_split)
	entry[QTIME]= datetime.datetime.strptime(split[TIND], "%Y-%m-%d %H:%M:%S") #np.datetime64(split[2])
	if len(split) > 3:
		try:
			entry[CLICKR]=int(split[CIND])
		except Exception as err:
			print line, err
	entry[CLICKU]=split[CUIND].lower().strip()
	return entry


#dont need index since new line marks the session
def getSessionWithNL(fileName):
	session = []
	for line in open(fileName, 'r'):
		line = line.strip()
		if len(line) < 2:
			yield session
			session = []
		else:
			session.append(line)



#get user sessions with time difference
def getSessionWithQuery(fileName, timeCutoff):
	session = []
	lastUser = lastTime = lastQuery = None

	for line in open(fileName, 'r'):
		split = line.strip().split('\t')
		try :
			currTime = datetime.datetime.strptime(split[TIND], "%Y-%m-%d %H:%M:%S") #np.datetime64(split[2])
			query = split[QIND].lower()
			currUser = split[UIND].lower()
			raw_split = query.strip().split(' ')
			if not ((lastTime == None) or (((currTime -lastTime).total_seconds()<timeCutoff
			or subQuery(query,lastQuery,0.7)) and currUser == lastUser)):
				if len(session) > 1:
					yield session
					session = []
				
			if (lastTime != currTime or lastQuery != query) \
			and (hasManyChars(query,raw_split,1,4,70) \
			and hasInapWords(raw_split) and hasManyWords(raw_split,15,40) \
			and hasAlpha(query) and hasWebsite(query)):
				session.append(query)
				
			lastUser = currUser	
			lastTime = currTime
			lastQuery = query
		except Exception as err:
			print line, err, err.args


# get the session and related data
def getSessionWithInfo(fileName,delim,timeCutoff):
	iFile = open(fileName,'r')
	currSession = []
	iFile.readline()
	currTime = lastTime = None
	currUser=lastUser = None
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
		currUser = entry [USER]
		if not ((lastTime == None) or \
		(((currTime -lastTime).total_seconds() < timeCutoff or subQuery(query,lastQuery,0.7))\
		and currUser == lastUser)):
		#if not (lastTime == None or currUser == lastUser):
			# start a new session
			if len(currSession) > 0:
				i += 1
				yield lastUser,i-1, currSession, currSessionString #, queryVector
				currSession = []
				#queryVector = []
				currSessionString = ''
		
		if hasManyChars(query,raw_split,1,4,70) \
		and hasInapWords(raw_split) and hasManyWords(raw_split,15,40) \
		and hasAlpha(query) and hasWebsite(query):
			currSession.append(entry)
			currSessionString += str(i) +'\t' + line
		lastTime = currTime
		lastUser = currUser
		lastQuery = query
	
	iFile.close()

#check if q2 is substring of q1
def subQuery(q1, q2, thresh):
	s1 =  set(q1.split(' '))
	s2 =  set(q2.split(' '))
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
			return False;
	return True;

#for multiple word queries
#checks if too many words
#or lengthy words in query
def hasManyWords(raw_split,wordCount, wordLength):
	if len(raw_split) > wordCount:
		return False;
	for entry in raw_split:
		if len(entry) > wordLength:
			return False
	return True;

#for one word queries
def hasManyChars(query,raw_split,wmin,cmin,cmax):
	if len(raw_split) == wmin and (len(query) > cmax or len(query) < cmin):
		return False;
	return True;

#for alphabet queries
def hasAlpha(query):
	return bool(re.search('[a-zA-Z]',query))

#find if query is a website
def hasWebsite(query):
	return WEB.match(query)

#get term list from a query
def getQueryTerms(query):
	#replace symbols
	query = re.sub(SYMB,' ',query)
	
	#repace numbers
	query = re.sub('\d+','',query)
	
	#fix spaces
	query = re.sub('\s+',' ',query)

	qset = query.strip().split() 	
	qset -= stopSet		
	return list(qset)
	
#remove stop words from split
def filterStopWordsFromList(split):
	string = ''
	for entry in split:
		if entry not in stopSet:
			string += ' '+entry
	return string.strip()

#remove the stopwords from query	
def filterStopWordsFromQuery(query):
	split = query.split()
	string = ''
	for entry in split:
		if entry not in stopSet:
			string += ' '+entry
	return string.strip()

#remove symbols
def filterSymbolsFromQuery(query):
	#replace symbols
	query = re.sub(SYMB,' ',query)
	query = re.sub('\s+',' ',query)
	return query.strip()

#replace the numbers with replace string
def filterNumbersFromQuery(query,rep):
	split = query.split()
	string = ''
	for entry in split:
		string += re.sub('[0-9]+', rep ,entry)
	return string
	
#replace the numbers with replace string
def filterNumbersFromList(split,rep):
	string = ''
	for entry in split:
		string += re.sub('[0-9]+', rep ,entry)
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
              vString += entry +'^'+str(value)+' '
        return vString

def findSessionStats(folderName):
        stats = {'#queries':0,'#sessions':0,'#users':0,'#words':0}
        dist = { 'word_query': {}, 'query_session':{}}
        userQueryCountList = {}
        #iterating over logs
        for iFile in os.listdir(folderName):
                print iFile
                #logs = loadFile(folderName+'\\'+iFile, "\t")
                #iterating over sessions
                for lastUser, sessId, currSession, sessionString in getSessionWithInfo(folderName+'/'+iFile,1500):
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
							dist['word_query'][entry] = dist['word_query'].setdefault(entry,0)+len(split)
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

