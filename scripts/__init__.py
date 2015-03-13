# -*- coding: utf-8 -*-
from queryLog import getSessionWithQuery,hasInapWords,normalizeWithoutStem
from entity.category import getCats
import sys
from utils import getNGramsAsList, ashleelString, get_cosine, loadFileInDict, loadFileInList
import ast
import random
from dbPedia import loadCategories
#import codecs
#import urllib
#import distance
from nltk import stem
from queryLog import normalize

def buildBigramSet(fileName):
	setb = set();
	for line in open(fileName,'r'):
		split = line.strip().split('\t')
		setb.add(split[0].strip());
	return setb;
	
def buildQueryList(catFile,catFolderDict, tagFile):
	catSet = set()
	queryDict =  {}
	for line in open(catFile,'r'):
		split = line.split('\t');
		cat = split[0].strip();
		catSet.add(cat);
	
	print len(catSet);
		
	for cat in catSet:
		if cat in catFolderDict:
			for line in open(catFolderDict[cat],'r'):
				split = line.split('\t');
				queryDict[split[0].strip()] = 1.0;
				
	for line in open(tagFile,'r'):
		split = line.split('\t');
		query = split[0].strip();
		if query in queryDict:
			queryDict[query] = split[1].strip();

	print 'Loaded queries ', len(queryDict);	
	return queryDict;


def populateDatasetWithBigrams(logFile,bigramSet, queryFile):
	sid  = 0;
	
	queryList  = buildBigramSet(queryFile)
	
	stemmer =  stem.porter.PorterStemmer()
	for session in getSessionWithQuery(logFile):
		sessionStr = ' '.join(session);
		sessionSet = set(getNGramsAsList(sessionStr,2))
		inter = sessionSet & bigramSet;
		#print len(sessionSet), len(bigramSet), inter

		if len(inter) > 0:
			lastq = None;
			for q in session:
				if q in queryList:
					q = normalize(q,stemmer)
					if lastq != q and len(q) > 1:
						print sid,'\t', q
					lastq = q;
		sid+=1;
	
def populateDataset(logFile, queryList):
	sid  = 0;
	for session in getSessionWithQuery(logFile):
		prints = False;
		for entry in session:
			if entry in queryList:
				prints = True;
		if prints:
			lastq = None;
			for q in session:
				if lastq != q:
					if q in queryList:
						print sid,'\t', q,'\t', queryList[q]
					else:
						print sid,'\t', q
				lastq = q;
		sid+=1;
		
		
def filterSessionWithLength(fileName):
	session = [];
	lastSes = None;
	for line in open(fileName,'r'):
		split = line.split('\t');
		sessNo = int(split[0]);
		if lastSes != sessNo:
			sessionSet = set((' '.join(session)).split())
			inter = sessionSet & ashleelString
					
			if len(inter) == 0 and len(session) > 2 and len(session)  < 100:
				for entry in session:
					print entry,
			session = [];
		session.append(line);
		lastSes = sessNo;

def filterSessionWithQuery(fileName,queryFile):
	queryList = loadFileInList(queryFile)
	for line in open(fileName,'r'):
		split = line.split('\t');
		query = split[0].strip()
		nQuery = ''
		for entry in query.split():
			if len(entry) > 1:
				nQuery +=' '+ entry
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
	for line in open(fileName,'r'):
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
	stemmer =  stem.porter.PorterStemmer()
	
	for line in open(file2,'r'):
		split = line.split('\t')
		entry = split[index].strip()
		norm = normalize(entry, stemmer)
		if norm in toCheck and len(norm) > 3:
			print line,
	#for entry in sorted(queryList.items(), reverse = True, key = lambda x :x[1]):
	#	print entry[0],'\t', entry[1]
	
def sampleSessions(sessiontrackFile,biGramFile, freqFile, sessionFileToPrune):
	#if the session contains any session Track query
	#if it contains top 100 bigrams 20 unigrams
	# if the session average query count > 1/ session length
	#else rand number is
	
	sessionTrackQueries = {}
	#load sessionTrack queries
	for line in open(sessiontrackFile,'r'):
		query = normalizeWithoutStem(line.strip().lower())
		sessionTrackQueries[query] = 1.0
		sessionTrackQueries[line.strip().lower()] = 1.0

	biGrams = set()
	for line in open(biGramFile,'r'):
		split = line.split('\t')
		biGrams.add(split[0])
		if len(biGrams) == 2500:
			break;

	freq = {}
	for line in open(freqFile,'r'):
		split = line.split('\t')
		freq[split[0].strip()] = float(split[1])
	
	avgFreq = 0.0
	lastSes = None;
	session = []
	hasQuery = False;
	hasBigram = False;
	for line in open(sessionFileToPrune,'r'):
		split = line.split('\t');
		sessNo = int(split[0]);
		
		query = split[1].strip();
		if query in sessionTrackQueries:
			hasQuery=True;
		
		nGrams = set(getNGramsAsList(query,2));
		inter = nGrams & biGrams
		if len(inter) > 0:
			hasBigram = True;
		
		avgFreq += freq[query]
		if lastSes != sessNo:
			rnum = random.random()
			if len(session) > 0:
				avgFreq /= len(session)
			if (rnum > 0.80 or  hasQuery or hasBigram) and (len(session) > 3) and avgFreq > 90:
				for entry in session:
					print entry,
			session = [];
			hasQuery = False;
			hasBigram = False;

		session.append(line);
		lastSes = sessNo;


def findEntityCategory(entFile, categoryFile):
	categoryList = loadCategories(categoryFile)
	for line in open(entFile,'r'):
		entry= str(line.strip().lower())
		#entry =  entry[2:-1].strip()
		#entry = unicode(entry1)
		#print entry, type(entry),
		if entry in categoryList:
			print entry, '\t', categoryList[entry]
			
		else:
			#for tit in categoryList.keys():
				#if tit.startswith(entry):
					#print entry, '\t', tit, '\t', categoryList[tit]
					#break	
			print 'Not in Cat ', entry
		
def createJointDatasetForEntities(queryList, onlyId , tagged2, catList , entityTitle, outFile):	

#2 entity files -- one with wiki names and not_wiki ==> Merge them into one
#Categories are listed with entity name
# file with entity id and name for not_wiki
	#load id-> title mapping
	idNameDict = {}
	for line in open(entityTitle,'r'):
		idDict = ast.literal_eval(line.lower())
		idNameDict[idDict['code']] = idDict['title']
	#load title-> cat mapping
	nameCatDict = {}
	for line in open(catList,'r'):
		split = line.split('\t')
		nameCatDict[split[0].strip()] = split[1].strip()

	#load queries
	queryDict = {}
	for line in open(queryList,'r'):
		queryDict[line.strip()] = 1.0
	
	print len(queryDict), len(nameCatDict), len(idNameDict)
	out = open(outFile,'w')
	
	#file with id info no name and category
	for line in open(onlyId,'r'):
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
					
					print 'Entity not Found! ',eid
				i+=1
			
			out.write(str(spot)+'\n')
	
	for line in open(tagged2,'r'):
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
				i+=1
			out.write(str(spot)+'\n')
	
	
	out.close()	
	

def mergeFeatures(featFile, taggedFile, newFile):
	entFeatDict = {}
	stemmer =  stem.porter.PorterStemmer()
	for line in open(taggedFile,'r'):
		spotDict = ast.literal_eval(line.strip());
		normQuery = normalize(spotDict['text'], stemmer);
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
				catVect[cat] +=1.0
		entFeatDict[normQuery].append(entVect)
		entFeatDict[normQuery].append(catVect)
	
	print len(entFeatDict)
	
	featDict = {}
	
	outF = open(newFile,'w')
	
	for line in open(featFile,'r'):
		split = line.split('\t')
		query = split[0].strip()
		featDict[query] = []
		for entry in split[1:]:
			featDict[query].append(entry.strip())
		if query in entFeatDict:
			featDict[query] = featDict[query] + entFeatDict[query]
		else:
			featDict[query] = featDict[query] + [{},{}]
			print 'Query not tagged! ', query
		
		outF.write(query);
		for entry in featDict[query]:
			outF.write('\t'+str(entry));
		outF.write('\n')
			#convert cat stuff into a dictionary
		
			
	
	outF.close()

def prepareTrainingDataset(sameTaskFile, dataSubsetFile, taskQueryFile):
	#select only those pairs which have both queries in queryFile
	tQueryList = {}
	#queryKey = {}
	keyQuery = {}
	for line in open(taskQueryFile,'r'):
		tQueryList[line.strip()] = 1.0

	print len(tQueryList)
	
	for line in open(sameTaskFile,'r'):
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
			for j in range(i+1,len(keys)-1):
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
	for line in open(fileName,'r'):
		split = line.split('\t')
		if split[0] not in cluster:
			cluster[split[0]] = set()
		trim = split[1].strip()
		if trim != split[0]:
			cluster[split[0]].add(trim)
		
	for entry, sets in cluster.items():
		print entry+'\t'+'\t'.join(sets)

def filterQueries(queryCountFile, queryFile, trainFile, sessionFile):
	queryCount = loadFileInDict(queryCountFile)
	
	#print len(queryCount)
	toPrint = set ()
	toFilter = loadFileInList(queryFile)
	training = loadFileInList(trainFile)
	session = loadFileInList(sessionFile)
	stemmer =  stem.porter.PorterStemmer()
	for entry in toFilter:
	
		if (entry in queryCount) and ((queryCount[entry] > 15) or \
		 (entry in training) or (entry in session)):
			entry1 = normalize(entry, stemmer)
			toPrint.add(entry1)
			#print entry, '\t', queryCount[entry]
	for entry in toPrint:
		print entry

def findDBPediaTypeIntersection(dbFile, entFile):
	for line in open(entFile,'r')
#argv[1] = catFile / bigram file
#argv[2] = catFolder
#argv[3] = tagged query file
#argv[4] = logFile
if __name__ == '__main__':
	argv =sys.argv
	#catFiles = getCats(argv[2])
	#queryDict = buildQueryList(argv[1], catFiles, argv[3])
	#populateDataset(argv[4], queryDict)
	#filterSessionWithLength(argv[1])
	#bigramSet = buildBigramSet(argv[1])
	#populateDatasetWithBigrams(argv[2],bigramSet,argv[3])
	
	#findUniqueQueries(argv[2], argv[1], 1)
	#sampleSessions(argv[1],argv[2],argv[3], argv[4])
	#findEntityCategory(argv[1],argv[2])
	#1 = query list, 2 = all Aol tagged (new dexter), 3 = aol tagged with wikiName
	#4 = cat list , 5= entity title mapping, 6 = out file
	#createJointDatasetForEntities(argv[1], argv[2],argv[3],argv[4],argv[5], argv[6])
	#mergeFeatures(argv[1],argv[2],argv[3])
	#findCatQueryDist(argv[1])
	#prepareTrainingDataset(argv[1],argv[2],argv[3])
	#prepareTrainingDataset(argv[1],None,argv[2])
	#combineHenry(argv[1])
	
	#filterQueries(argv[1],argv[2],argv[3],argv[4])
	filterSessionWithQuery(argv[1],argv[2])