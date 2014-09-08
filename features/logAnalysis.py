# -*- coding: utf-8 -*-
import os, sys
import math
import ast
import re
from utils import getNGrams
from whoosh.index import create_in
from whoosh.fields import Schema, TEXT
from Whoosh import loadIndex, loadQueryParser, loadCollector
from whoosh.collectors import TimeLimit
from utils import get_cosine

linkP = re.compile('\(.+?,\d+\)')
def getQueryFreqValues(fileName):
	queryCount = {}
	for line in open(fileName,'r'):
		split = line.strip().split('\t')
		freq = int(split[-1])
		flog = round(math.log(freq),2)
 		queryCount[flog] = queryCount.setdefault(flog,0.0)+ 1.0
	
	for entry in sorted(queryCount.items(),reverse = True):
		print entry[0],'\t', math.log(entry[1])

def formatQueryFeatures(fileName):
	#oFile = open(outFile,'w')
	for line in open(fileName,'r'):
		split = line.strip().split('\t')	
		#split 1 =  spot
		spot = ast.literal_eval(split[1])
		entString = ''
		catString = ''
		catDict = {}
		for ent , catList in spot.iteritems():
			entString+= ent.replace(' ','_')+':1 '
			for cat in catList['cat'].split():
				catDict[cat]=catDict.setdefault(cat,0) + 1
			
 			catString = ' '.join('{0}:{1}'.format(x,y) for x, y in catDict.items())
 		
 		#split 2 users
 		users = ast.literal_eval(split[2])
 		userString = ' '.join('{0}:{1}'.format(x[0],str(x[1])) for x in users )
 		
 		#split 3 = links
 		links = linkP.findall(split[3])#ast.literal_eval(split[3])
 		linkString = ''
 		for tup in links:
 			entry = tup.split(',')
			entry[0] = entry[0][1:].strip()
			entry[1] = entry[1][:-1]
 			if len(entry[0]) < 3:
 				linkString += 'None:'+str(entry[1])+' '	
 			else:
 				linkString += entry[0]+':'+str(entry[1])+' '
 				
 		#biString = getNString(split[0],2)
 		triString = getNString(split[0],3).decode('utf-8')
 		triString = str(triString.encode('ascii','ignore'))
 		print split[0],'\t',entString.strip(),'\t',catString.strip(),\
 			'\t',userString.strip(),'\t',linkString.strip(), \
 			'\t',triString.strip()
 		
 		

def getNString(string, glen):
	string = string.strip()
	gram = {}
	gString = ''
	for bi, other, ind in getNGrams(string,glen):
		#print glen, string, bi, ind
 		gram[bi] = gram.setdefault(bi,0) + 1
 	gString = ' '.join('{0}:{1}'.format(x.replace(' ','_'),y) for x,y in gram.items())
 	return gString


def indexFeatures(fileName,indexLocation,indexName):
	ischema = Schema(query = TEXT(stored = True,phrase=False),
	ent = TEXT(stored = False, phrase = False),
	cat = TEXT(stored = False, phrase = False),
	user = TEXT(stored = False, phrase = False),
	links = TEXT(stored = False, phrase = False),
	ngrams = TEXT(stored = False, phrase = False))
	if not os.path.exists(indexLocation):
		os.mkdir(indexLocation)
        qindex = create_in(indexLocation,schema=ischema, indexname =indexName)
        writer = qindex.writer()
	i = 0
	for line in open(fileName,'r'):
		#load the string
		#index the features seperately
		# 1 == entity, 2 == category, 3 == users, 4 == links
		split = line.strip().split('\t')
		entString = getFeatString(split[1])
		catString = getFeatString(split[2])
		userString = getFeatString(split[3])
		linkString = getFeatString(split[4])
		ngramString = getFeatString(split[5])
		try :
			#print entString
			writer.add_document(query=unicode(split[0].decode('unicode_escape').encode('ascii','ignore')),
				ent=unicode(entString.decode('unicode_escape').encode('ascii','ignore')),
				cat=unicode(catString.decode('unicode_escape').encode('ascii','ignore')),
				user=unicode(userString.decode('unicode_escape').encode('ascii','ignore')),
				ngrams=unicode(ngramString.decode('unicode_escape').encode('ascii','ignore')),
				links=unicode(linkString.decode('unicode_escape').encode('ascii','ignore')))
		except Exception as err :
			print split[0], 'problem in indexing'
			print err, err.args
		i+=1
		if i%100000==0:
			print i

	writer.commit()
	qindex.close()
		


def getQuerySimilarity(featFile, indexName, indexLocation, parts , pindex):
	# load the queries in the dictionary
	featDict = {}
	for line in open(featFile,'r'):
		split = line.strip().split('\t')
		query = split[0]
		entDict = getFeatDict(split[1])
		catDict = getFeatDict(split[2])
		userDict = getFeatDict(split[3])
		linkDict = getFeatDict(split[4])
		ngramDict = getFeatDict(split[5])
		featDict[query] = {'ent':entDict , 'cat':catDict, 'user':userDict,
							'link':linkDict, 'ngram':ngramDict}			
	
	total = len(featDict)
	i = 0
	length = total / (parts * 1.0)
	strt = 	pindex * length
	end = (pindex+1) * length
	
	print pindex, strt, end
	#load the index
	fIndex, fsearcher = loadIndex(indexLocation, indexName)
	ftlc = loadCollector(fsearcher,1000000,100)
	eqp = loadQueryParser(fIndex,"ent")	
	cqp = loadQueryParser(fIndex,"cat")	
	uqp = loadQueryParser(fIndex,"user")	
	lqp = loadQueryParser(fIndex,"links")	
	nqp = loadQueryParser(fIndex,"ngrams")	
	qqp = None
	#for every query find all queries
	#that have overlapping feature values
	#calculate 5 similariies seperately
	
	querySimilarity = {}
	
	for query, features in featDict.iteritems():
		queryBucket = {}
		if i > strt and i < end:
			for ftype,fdict in features.iteritems():
				if ftype == 'ent':
					qqp = eqp
				elif ftype == 'cat':
					qqp = cqp
				elif ftype == 'user':
					qqp = uqp
				elif ftype == 'link':
					qqp = lqp
				else:
					qqp = nqp
				
				keys = fdict.keys()
				for entry in keys:
					q = qqp.parse(unicode(entry))
					try:
						fsearcher.search_with_collector(q, ftlc)
					except TimeLimit :
						print '--LONG-- ', entry
					results = ftlc.results()
					
					for row in results:
						toAdd =row['query']
						if toAdd not in queryBucket:
							queryBucket[toAdd] = 1
				print query, ftype, len(queryBucket)
						
			for entry in queryBucket.keys():
				key = entry+'\t'+query
				key1 = query +'\t' + entry
				if entry in featDict and key not in querySimilarity and key1 not in querySimilarity:
					querySimilarity[key] = getFeatureSimilarity(features,featDict[entry])
		i+=1
		if i%100000==0:
			print i
	
	for entry, simValues in querySimilarity.iteritems():
		print entry, str(simValues)


def generatePairs(fileName, parts , pindex, leave):
	oFile = open('similarity'+str(pindex)+'.txt','w')
	i = 0
	length = 3659819.0/ parts
	strt = 	(pindex * length) + leave
	end = (pindex+1) * length
	query = entDict = catDict = userDict = linkDict = ngramDict = None	
	query1 = entDict1 = catDict1 = userDict1 = linkDict1 = ngramDict1 = None	
	for line1 in open(fileName,'r'):
		if i >= strt and i < end:
			print i	
			split = line1.strip().split('\t')
			query = split[0]
			entDict = getFeatDict(split[1])
			catDict = getFeatDict(split[2])
			userDict = getFeatDict(split[3])
			linkDict = getFeatDict(split[4])
			ngramDict = getFeatDict(split[5])
			j = 0
			for line2 in open(fileName,'r'):
				if j > i:
					split = line2.strip().split('\t')
					query1 = split[0]
					entDict1 = getFeatDict(split[1])
					catDict1 = getFeatDict(split[2])
					userDict1 = getFeatDict(split[3])
					linkDict1 = getFeatDict(split[4])
					ngramDict1 = getFeatDict(split[5])
					ec = get_cosine(entDict,entDict1)
					cc = get_cosine(catDict,catDict1)
					uc = get_cosine(userDict,userDict1)
					lc = get_cosine(linkDict,linkDict1)
					nc = get_cosine(ngramDict,ngramDict1)
					total = ec + cc + uc + lc + nc
					if total > 0:
						oFile.write(query+ '\t'+ query1 +'\t'+ str(ec)+'\t'\
						+ str(cc)+'\t'+ str(uc)+'\t'+ str(lc)+'\t'+ str(nc)+'\n')
				j+=1
		i+=1
	oFile.close()

		
			
		
def getFeatString(featString):
		retString = ''
		featString = featString.strip()
		if len(featString) > 1:
			for entry in featString.split(' '):
				retString += entry[:entry.rfind(':')]+' '
		
		return retString.strip()	

def getFeatDict(featString):
	#converts string to dict		
	retDict = {}
	i = 0
	featString = featString.strip()
	if len(featString) > 1:
		for entry in featString.split(' '):
			try:
				retDict[entry[:entry.rfind(':')]] = int(entry[entry.rfind(':')+1:])
			except:
				i+=1
			#print featString
			
	return retDict;
	

def getFeatureSimilarity(feat1 , feat2):
	simDict = {}
	for ftype, fdict1 in feat1.iteritems():
		if ftype in feat2:
			fdict2 = feat2[ftype]
			cos = get_cosine(fdict1,fdict2)
			simDict[ftype+'_cos'] = cos	

	return str(simDict)

def printNonEmptyRows(fileName):
	for line in open(fileName,'r'):
		try:
			split = line.strip().split('\t')
			ec =round( float(split[2]),3)
			cc =round( float(split[3]),3)
			uc =round( float(split[4]),3)
			lc =round( float(split[5]),3)
			nc =round( float(split[6]),3)
			total = ec + cc + uc + lc + nc
			if total > 0:
				print line,
		except:
			pass

		
def main(argv):
	#getQueryFreqValues(argv[1])	
	#formatQueryFeatures(argv[1])
	#indexFeatures(argv[1],argv[2],argv[3])
	#featFile, indexName, indexLocation, parts , pindex
	#getQuerySimilarity(argv[1], argv[2], argv[3], int(argv[4]) , int(argv[5]))
	#generatePairs(argv[1],int(argv[2]),int(argv[3]), int(argv[4]))
	printNonEmptyRows(argv[1])
	
if __name__=='__main__':
	main(sys.argv)
