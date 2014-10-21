# -*- coding: utf-8 -*-
from queryLog import getSessionWithQuery;
from entity.spotDict import SpotDict;
from utils.coOccurrence import CoOccurrence;
from utils import getNGramsAsList, stopSet;
import sys,os;
from queryLog import getQueryTerms;
from utils import loadFileInList;
import shutil;
from nltk import stem;
#read the spotDict
def loadNonEntityTerms(fileName):
	queryTermDict = {};
	terms = 0.0;
	sDict = None;
	#for each query store the terms
	for line in open(fileName,'r'):
		split = line.split('\t');
		query = (split[0].strip().decode('utf-8')).encode('ascii','ignore');
		spotDict1 = split[1].strip();
		#create the dict object
		sDict = SpotDict(spotDict1, query);
		if len(sDict.getNonEntityTerms()) > 0 and query not in queryTermDict:
			queryTermDict[query] = sDict;
			terms += sDict.getNonEntTermsLen();
			
	print len(queryTermDict), terms;
	return queryTermDict;


def findQueryCounts(queryFile):
	#coOccur = CoOccurrence();
	pairs = {};
	porter =  stem.porter.PorterStemmer();
	qTerms = '';
	for line in open(queryFile, 'r'):
		split = line.strip().lower().split('\t');
		query = split[0].strip();
		freq = float(split[1]);
		#for each query get nonEntTerms and update co-occurrence stats
		qTerms = '';
		qTerms = ' '.join(getQueryTerms(query));
		if len(qTerms) > 3:
			ngrams = sorted(getNGramsAsList(qTerms.strip(),1));
			lngrams = len(ngrams);
			if lngrams > 1:
				for i in range(lngrams-1):
					if ngrams[i] not in stopSet and len(ngrams[i]) > 2:
						for j in range(i+1,lngrams):
							if ngrams[j] not in stopSet and len(ngrams[j]) > 2:
								stemd1 = porter.stem(ngrams[i]);
								stemd2 = porter.stem(ngrams[j]);
								key = stemd1 +' '+stemd2;
								if key not in pairs:
									pairs[key] = 0.0;
								pairs[key]+= freq;
								#coOccur.updateStats(stemd1, stemd2, freq);
	#coOccur.setTermTotal();
	#coOccur.writeTermCo(outFile);
	return pairs;

def findSessionCounts(queryFile,outFile,wordSet):
	coOccur = {};#CoOccurrence();
	
	qTerms = '';
	sess = 0;
	qid = 0.0;
	qSet = set();
	for session in getSessionWithQuery(queryFile):
		qSet.clear();
		for query in session:
			qid +=1;
			terms = getQueryTerms(query);
			if len(terms) > 0:
				qSet|=getQueryTerms(query);
			if qid %1000000 == 0:
				print qid;
				print len(coOccur);
				
		#print len(session)	, len(qSet);
		#for each query get nonEntTerms and update co-occurrence stats
		qTerms = '';
		qTerms=' '.join(qSet);
		if len(qTerms) > 3 and len(qSet) > 1:
			#print qSet;
			ngrams = sorted(getNGramsAsList(qTerms.strip(),1));
			lngrams = len(ngrams);
			if lngrams > 1:
				for i in range(lngrams-1):
					if ngrams[i] not in stopSet and len(ngrams[i]) > 2 and ngrams[i] in wordSet:
						for j in range(i+1,lngrams):
							if ngrams[j] not in stopSet and len(ngrams[j]) > 2 and ngrams[j] in wordSet:
									#coOccur.updateStats(ngrams[i],ngrams[j],1.0);
									key = ngrams[i]+' '+ngrams[j];
									if key not in coOccur:
										coOccur[key] = 0.0;
									coOccur[key] += 1.0;
									if len(coOccur) >= 9000000:
										writeDictToFile(outFile,coOccur,sess);
										coOccur.clear();
										coOccur = {};
										sess+=1;

	#coOccur.setTermTotal();
	#coOccur.writeTermCo(outFile);
	

def writeDictToFile(outFile, coOccur,i):
	oFile = open(outFile+'_'+str(i)+'.txt','w');
	sort = sorted(coOccur.items(), key = lambda x : x[0]);
	for entry in sort:
		oFile.write(entry[0]+' '+str(entry[1])+'\n');
	oFile.close();	


def findSessionCountsOfNonEnt(netDict, queryFile,outFile):
	
	coOccur = CoOccurrence();
	
	qTerms = '';
	for session in getSessionWithQuery(queryFile):
		#for each query get nonEntTerms and update co-occurrence stats
		qTerms = '';
		for query in session:
			query = (query.decode('utf-8')).encode('ascii','ignore');
			if query in netDict:
				for entry in netDict[query].getNonEntityTerms():
					if entry not in qTerms:
						qTerms+= ' '+entry;
		qTerms = qTerms.strip();
		if len(qTerms) > 2:
			ngrams = getNGramsAsList(qTerms.strip(),1);
			lngrams = len(ngrams);
			if lngrams > 1:
				for i in range(lngrams-1):
					if ngrams[i] not in stopSet and len(ngrams[i]) > 2:
						for j in range(i+1,lngrams):
							if ngrams[j] not in stopSet and len(ngrams[j]) > 2:
								coOccur.updateStats(ngrams[i],ngrams[j],1.0);
	coOccur.setTermTotal();
	coOccur.writeTermCo(outFile);


def mergeCounts(file1, file2, out):
	print file1, file2;
	
	outFile = open(out,'w');
	'''
	c1 = loadCoOccurFile(file1);
	c2 = loadCoOccurFile(file2);
	
	
	
	for key,value in c1.items():
		if key in c2:
			outFile.write(key+' '+ str(value+c2[key])+'\n');
		else:
			outFile.write(key+' '+ str(value)+'\n');
	
	for key, value in c2.items():
		if key not in c1:
			outFile.write(key+' '+ str(value)+'\n');
	'''	
	f1 = open(file1, 'r') ;
	f2 = open(file2, 'r') ;

	line1 = f1.readline();
	line2 = f2.readline();
	while True:
		if len(line1) >0  and len(line2) > 0:
			split1 = line1.split(' ');
			split2 = line2.split(' ');
			key1 = split1[0]+' '+split1[1];
			key2 = split2[0]+' '+split2[1];
				
			val1 = float(split1[-1]);
			val2 = float(split2[-1]);
			if key1 == key2:
				outFile.write(key1+' '+str(val1+val2)+'\n');
				line1 = f1.readline();
				line2 = f2.readline();
			elif key1 < key2:
				outFile.write(key1+' '+str(val1)+'\n');
				line1 = f1.readline();
			else :
				outFile.write(key2+' '+str(val2)+'\n');
				line2 = f2.readline();
		else:
			break;
	
	if len(line1) > 0:
		outFile.write(line1);
	if len(line2) > 0:
		outFile.write(line2);				
	for line in f1:
		outFile.write(line);
	
	for line in f2:
		outFile.write(line);
	
	outFile.close();

	
def loadCoOccurFile(file1):
	wdict = {};
	for line in open(file1,'r'):
		split = line.strip().split();
		key = split[0]+' '+split[1];
		value = float(split[-1]);
		wdict[key]  = value;
	return wdict;

def mergeFile(inDir,outDir,stage):
	fileList = os.listdir(inDir);
	files = len(fileList);
	if files > 1:
		if not os.path.exists(outDir):
			os.mkdir(outDir);

		for i in range(0,files,2):
			if files == i+1:
				print '1',i , fileList[i];
				shutil.copy(inDir+'/'+fileList[i],outDir+'/'+str(i));				
			else:
				print '2',i , fileList[i], fileList[i+1];
				mergeCounts(inDir+'/'+fileList[i],inDir+'/'+fileList[i+1],outDir+'/'+str(i));
		stage+=1;
		
		mergeFile(outDir,outDir+'_'+str(stage), stage);
		
def main(argv):
	#netDict = loadNonEntityTerms(argv[1])
	#findSessionCounts(netDict, argv[2], argv[3]);
	#wordSet = loadFileInList(argv[1]);
	#findSessionCounts(argv[2], argv[3],wordSet);
	#mergeFile(argv[1],argv[2],0);
	pairs = findQueryCounts(argv[1]);
	writeDictToFile(argv[2],pairs,0);
		
if __name__== '__main__':
	main(sys.argv);
