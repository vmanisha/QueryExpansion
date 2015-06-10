# -*- coding: utf-8 -*-
#Position of summary
#spread of query terms
#ari #lix #cli
#number of terms in summary
#average sentence length
#Puntuation

import sys
import os
from pattern.web import plaintext
from nltk import tokenize, sent_tokenize
import pickle
import numpy as np
#from nltk.stem.wordnet import WordNetLemmatizer

'''

stats for each document --

ARI --
Document length
Characters
Sentences

CLI --
average no of sent per 100 words
average no of letters per 100 words

LIX
No of long words -- len(word) > 6
no of periods

'''

stopSet = set (['the','an','to','and','from','for','we','you','i','so','a','at','b','be','in','of','on','was'])


def readFile(fileName, fileList,docSentences):

	iFile = open(fileName, 'r')
	append = False
	docNo = ''
	content = ''
	count = 0
	for line in iFile:
		if '<DOCNO>' in line:
			#start of new file
			docNo = line[line.find('>')+1:line.rfind('<')].strip()
			if docNo in fileList:
				append = True
		if append:
			if '</DOC>' in line:
				append = False
				count += 1
				#get the stats
				pText = plaintext(content.replace("\n"," "))
				sentences = sent_tokenize(pText)	
				fileList[docNo] = getDocMetrics(sentences)
				docSentences[docNo] = sentences
				content = ''
			else:
				content += line
	return count 			
	iFile.close()

def getQueryCount(queryText,sentences):
	metrics = {'queryFreq':0.0, 'avgTF':0.0,'minTF':0.0, 'maxTF':0.0,\
		'minWPos':0.0,'maxWPos':0.0,'avgWPos':0.0}
	
	pos = []
	qHash = {}
	for entry in queryText.split():
		if entry not in stopSet and len(entry) > 1:
			qHash[entry] = 0
			
	tid = 0
	for sent in sentences:
		if queryText in sent:
			metrics['queryFreq']+=1.0
		for token in tokenize.word_tokenize(entry):
			strToken = str(token)
				
			if strToken in qHash:
				qHash[strToken]+=1.0
				pos.append(tid)
			
			tid+=1.0
	
	for entry in qHash.keys():
		if qHash[entry] == 0:
			del qHash[entry]
	try:
		metrics['avgTF'] = np.mean(qHash.values())
		metrics['minTF'] = min(qHash.values())
		metrics['maxTF'] = max(qHash.values())
			
		metrics['avgWPos'] = np.mean(pos)
		metrics['minWPos'] = min(pos)
		metrics['maxWPos'] = max(pos)
	except:
		pass					
	return metrics
#sent #words #characters #long words len > 6 #breaks
def getDocMetrics(queryText,sentences):
	metrics = {}
	metrics['sentWithQueryTerm'] =0
	
	sent = 0.0
	word_gt_1 = 0
	word_gt_2 = 0.0
	word_gt_3 = 0.0
	diffWord = 0.0
	period = 0.0
	char = 0.0
	er = 0
	tokenCount = {}
	
	qHash = {}
	for entry in queryText.split():
		if entry not in stopSet and len(entry) > 1:
			qHash[entry] = 0
	
	for entry in sentences:
		sent+= 1
		period += 1
		char += len(entry)
		qcount = 0
		for token in tokenize.word_tokenize(entry):
			try:
				strToken = str(token)
				if strToken not in tokenCount and strToken not in stopSet:
					tokenCount[strToken]=1.0
				if strToken in qHash:
					qcount +=1
				
				if len(token) > 6:
					diffWord += 1
				elif len(token) >= 3:	
					word_gt_3 += 1
				elif len(token) >= 2:
					word_gt_2 += 1
				elif str.isalnum(strToken):
					word_gt_1 += 1
				else:
					period+= 1
			except Exception as error:
				#print error
				er+=1
		if qcount == len(qHash):
			metrics['sentWithQueryTerm']+=1
			
	totalWords = (word_gt_2+word_gt_3+diffWord)
	metrics['sent'] = sent
	metrics['char'] = char
	metrics['words'] = len(tokenCount)
	#metrics['words2'] = word_gt_2
	#metrics['words3'] = word_gt_3
	#metrics['diffWord'] = diffWord
	metrics['period'] = period
	#metrics['sent100Word'] =(sent/totalWords)*100.0
	#metrics['char100Word'] =(char/totalWords)*100.0
	metrics['ARI'] = 0 if sent == 0 or totalWords == 0 else (4.71*(char/totalWords) + 0.5*(totalWords/sent) - 21.43)
	metrics['CLI'] = 0 if sent == 0 or totalWords == 0 else (5.88*(char/totalWords) - 29.6*(sent/totalWords)  - 15.8)
	metrics['LIX'] = 0 if totalWords ==0 or period == 0 else ((totalWords/period) + (diffWord/totalWords)*100.0)
	
	return metrics


def getQueryDocMetrics(queryText, sentences):
	#find the occurance of query terms in the document
	#features -- % of terms present
	#	     % of document all terms are present
	#	     readability of snippet
	#	     number of terms in snippet
	#	     number of sent in snippet
	#	     position of first query term
	#	     position of last query term
	#	     % sent containing query terms
	qSplit = queryText.split(' ')
	#stem the query string
	qHash = {}
	firstOcc = -1.0
	lastOcc  = -1.0
	
	firstSent = -1.0
	lastSent = -1.0
	for entry in qSplit:
		if entry not in stopSet and len(entry) > 1:
			qHash[entry] = 0
	#print qHash		
	
	sInd = 0
	tInd = 0
	er = 0
	sCount = 0.0
	tCount = 0.0
	lastInd = -1.0
	
	summary = {}
	noSent = len(sentences)
	for sInd in range(noSent):
		entry = sentences[sInd]
		for token in tokenize.word_tokenize(entry.lower()): #.encode('utf-8').lower()):
			if len(token) > 1:
				tInd += 1
			try:
				sToken = str (token)
				if sToken in qHash:
					tCount += 1.0
					if lastInd != sInd:
						lastInd = sInd
						sCount += 1.0
						if sInd > 1:
							summary[sInd-1] = sentences[sInd-1]
						summary[sInd] = entry
						if sInd < noSent -1 :
							summary[sInd+1] = sentences[sInd+1]
					if firstOcc < 0.0:
						firstOcc = lastOcc = tInd
						firstSent = lastSent = sInd
					else:
						lastOcc = tInd
						lastSent = sInd
				
			except Exception as err:
				#print err
				er += 1
	#print qSplit, qHash, tInd, sInd, firstOcc, lastOcc, firstSent, lastSent
	
	metrics = {}
	metrics['sentWithQueryTerm'] = sCount
	#metrics['queryTerms'] = len(qHash)
	#print len(summary), summary
	metrics.update(getDocMetrics(queryText,summary.values()))
	
	'''if sCount > 0:
		metrics['%termInSummary'] = tCount/(lastOcc-firstOcc+ 1.0)
		metrics['%sentInDoc'] = sCount/sInd
		metrics['%termsInDoc'] = tCount/tInd
		metrics['firstQueryTermInd'] = firstOcc
		metrics['lastQueryTermInd'] = lastOcc
		metrics['firstQuerySentInd'] = firstSent
		metrics['lastQuerySentInd'] = lastSent
		metrics['%doc'] = (lastSent+1.0 - firstSent)/sInd
		metrics['%token'] = (lastOcc+1.0 - firstOcc)/tInd
		metrics['%sentInSummary'] = sCount / (lastSent- firstSent + 1.0)'''
	
	return metrics
			

	
def writeMetrics(fileName, metricList):
	pickle.dump(metricList,open(fileName,'wb'))
		
	string = ''
	
	for entry, stats in metricList.iteritems():
		string += entry
		string +='\t'+str(stats['sent'])
		string +='\t'+str(stats['words'])
		#string +='\t'+str(stats['words2'])
		#string +='\t'+str(stats['words3'])
		#string +='\t'+str(stats['diffWord'])
		string +='\t'+str(stats['char'])
		string +='\t'+str(stats['period'])
		#string +='\t'+str(stats['sent100Word'])
		#string +='\t'+str(stats['char100Word'])
		string +='\t'+str(stats['LIX'])
		string +='\t'+str(stats['CLI'])
		string +='\t'+str(stats['ARI'])
		string +='\n'
	ofile = open(fileName+'txt','w')
	ofile.write(string)
	ofile.close()
	

def getFileList(folderName):
	fileList = []
	if os.path.isdir(folderName):
		for ifile in os.listdir(folderName):
			if os.path.isfile(ifile):
				fileList.append(folderName+'/'+ifile)
			else:
				fileList+=(getFileList(folderName+'/'+ifile))
	else:
		fileList.append(folderName)

	#print fileList
	return fileList;

def loadFileInHash(fileName):
	array = {}
	ifile = open(fileName, 'r')
	for line in ifile:
		array[line.strip()] = {}
	ifile.close()
	return array

def main(argv):
	#List files
	collection = getFileList(argv[1])
	docMetrics = loadFileInHash(argv[2])
	count = 0
	docSentences = {}
	for entry in collection:
		count += readFile(entry, docMetrics,docSentences)
	print count
	print 'no of doc with sent ', len(docSentences)	
	pickle.dump(docSentences,open('docSentence.p','wb'))
	writeMetrics('DocMetrics.p',docMetrics)	
	#print collection
	

if __name__ == '__main__':
	main(sys.argv)
	
#get the doc
#check whether docno in list
#get content if match
#get the metrics