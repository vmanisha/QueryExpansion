# -*- coding: utf-8 -*-
from utils import getDictFromSet
import sys
from search.searchIndex import SearchIndex
from queryLog import getSessionWithXML, normalize
from nltk import stem
from entity.ranker import Ranker
#1. query
#2. query + session terms
#3. query + click summary terms
#4. query + click summary others
#5. query + random walk summary
#6. query + random walk summary+aol
#7. query + random walk other summary+aol
#8. query + task aol
#9. query + task aol session
#10. query + task aol other


def convertListToDict(iList):
	tSet = {}
	for entry in iList:
		for word, count in getDictFromSet(entry.split()).items():
			try:
				tSet[word] += count
			except:
				tSet[word] = count
	return tSet
	
def removeSameKeys(dict1, dict2):
	for entry in dict1.keys():
		if entry in dict2:
			del dict2[entry]
	return dict2
	
def getSessionTerms(session,porter):
	lSet = getDictFromSet(session[-1].split())
	nlSet = normalizeDict(lSet, porter)
	
	tSet = convertListToDict(session)
	ntSet = normalizeDict(tSet, porter)
	
	tSet = removeSameKeys(nlSet, ntSet)
	
	return tSet
		
def getClickedSummaryTerms(session, cSummary, cTitle, porter):
	tSet = {}
	sSet = {}
	
	qSet = getDictFromSet(session[-1].split())
	nqSet = normalizeDict(qSet,porter)
	
	#print cTitle, cSummary
	
	tSet = convertListToDict(cTitle)
	sSet = convertListToDict(cSummary)
	
	ntSet = normalizeDict(tSet,porter)
	nsSet = normalizeDict(sSet,porter)

	tSet = removeSameKeys(nqSet, ntSet)
	sSet = removeSameKeys(nqSet, nsSet)
	
	return tSet, sSet
	
def getOtherSessionTerms(session, topicInfoMapping):
	
	sSet = convertListToDict(session)
	
	oSet = {}
	for session in topicInfoMapping:
		tSet = convertListToDict(session)
		for entry, count in tSet.items():
			try:
				oSet[entry] += count
			except:
				oSet[entry] = count
			
	oSet = removeSameKeys(sSet, oSet)
	
	return oSet
	

def getOtherClickedSummaryTerms(cSummary, cTitle, topicTitle, topicSummary):
	
	tSet = convertListToDict(cTitle)
	sSet = convertListToDict(cSummary)
	
	
	oTitle = {}
	for title in topicTitle:
		ttset = convertListToDict(title)
		for entry, count in ttset.items():
			try:
				oTitle[entry] += count
			except:
				oTitle[entry] = count
	
	oSummary = {}
	for summ in topicSummary:
		ttset = convertListToDict(summ)
		for entry, count in ttset.items():
			try:
				oSummary[entry] += count
			except:
				oSummary[entry] = count
	
	fTitle = removeSameKeys(tSet, oTitle)
	fSumm = removeSameKeys(sSet, oSummary)
	
	return fTitle, fSumm

def normalizeDict(idict, stemmer):
	returnDict = {}
	#tSum = sum(idict.values())*1.0
	
	for entry, count in idict.items():
		entry = normalize(entry, stemmer)
		if len(entry) > 2:
		 	try:
		 		returnDict[entry]+= count#/tSum
		 	except:
		 		returnDict[entry] = count#/tSum
	 		
	return returnDict

def mergeDicts(dict1, dict2):
	
	returnDict = {}
	
	for entry in dict1.keys():
		try:
			returnDict[entry]+= dict1[entry]
		except:
			returnDict[entry]= dict1[entry]

	for entry in dict2.keys():
		try:
			returnDict[entry]+= dict2[entry]
		except:
			returnDict[entry]= dict2[entry]

	return returnDict

def joinLists(ilist):
	retList = []
	for entry in ilist:
		joined = ' '.join(entry)
		if len(joined) > 2:
			retList.append(joined)
	return retList
	
def main(argv):
	
	#load the session
	#find the terms
	porter = stem.porter.PorterStemmer();
	searcher = SearchIndex(argv[2])
	searcher.initializeAnalyzer()
	#oSession = open('session-words.all','w')
	#oClicked = open('clicked-words.all','w')
	oOtherSession = open('other-session-words.all','w')
	oOtherClicked = open('other-clicked-words.all','w')
	
	otherSessions = {}
	otherClicked = {}
	
	ranker = Ranker()
	qId = 1
	for topicId, session, doc, click, cTitle, cSummary in getSessionWithXML(argv[1]):

		if topicId not in otherSessions:
			otherSessions[topicId] = {}
			otherClicked[topicId] = {}
			
		#add session terms
		sessionTerms = getSessionTerms(session,porter)
		
		otherSessions[topicId] = mergeDicts(otherSessions[topicId], sessionTerms)
		
		#eTerms = ranker.getTopKWithFilter(sessionTerms,10,15)
		#print session[-1], sessionTerms, eTerms		

		#k = 0
		#for entry in searcher.getTopDocumentsWithExpansion(session[-1],eTerms, 1000, 'content','id'):
			#oSession.write(str(qId)+' Q0 '+entry[0]+' '+str(k)+' '+str(round(entry[1],2))+' session\n')
			#k+=1
		
		
		#add clicked terms
		
		cTTerms, cSTerms = getClickedSummaryTerms(session, joinLists(cSummary.values()), joinLists(cTitle.values()),porter)
		nTerms = mergeDicts(cTTerms, cSTerms)
		otherClicked[topicId] = mergeDicts(otherClicked[topicId],nTerms)
		
		
		#fTerms = normalizeDict(nTerms, porter)
		#eTerms = ranker.getTopKWithFilter(nTerms,10,15)
		##
		#k = 0
		#for entry in searcher.getTopDocumentsWithExpansion(session[-1],eTerms, 1000, 'content','id'):
			#oClicked.write(str(qId)+' Q0 '+entry[0]+' '+str(k)+' '+str(round(entry[1],2))+' click\n')
			#k+=1

		
		qId+=1
		
	oSession.close()
	oClicked.close()
	searcher.close()
	
if __name__ == '__main__':
	main(sys.argv)