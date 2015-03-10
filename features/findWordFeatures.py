# -*- coding: utf-8 -*-
from entity.spotDict import SpotDict;
from features.word import Word;
from entity.category.findCategoryPhrases import loadQueryFreq;
from queryLog import getQueryTerms;
from utils import loadFileInList;
import re;
from logAnalysis import filterWords
import os,sys;
from entity.category.findCategorySubclusters import findClustersWithKMeans;
from nltk import stem;
linkP = re.compile('\(.+?,\d+\)');
porter = stem.porter.PorterStemmer();

def getEntCatFeatures(fileName,queryFreq):
	wordFeat = {}
	
	for line in open(fileName,'r'):
		split = line.split('\t')
		query = (split[0].strip().decode('utf-8')).encode('ascii','ignore');
		freq = 1.0;
		if query in queryFreq:
			freq = queryFreq[query]
			
		spotDict = split[1].strip();
		sDict = SpotDict(spotDict,query);
		nEntTerms = sDict.getNonEntityTerms();
		for oentry in nEntTerms:
			entry = porter.stem(oentry);
			if len(entry) > 2:
				if entry not in wordFeat:
					wordFeat[entry] = Word(entry,'');
				for entity in sDict.getEntities():
					wordFeat[entry].updateEntStats(entity, freq);
					
					for cat in sDict.getEntCategories(entity):
						if 'redirect' not in cat:
							wordFeat[entry].updateCatStats(cat, freq);
	return wordFeat ;
	
	
def getURLFeatures(fileName, wordFeat):
	for line in open(fileName,'r'):
		split = line.split('\t');
		queryTerms = getQueryTerms(split[0]);
		links = linkP.findall(split[1])#ast.literal_eval(split[3])
		urlFeatures = [];
 		for tup in links:
 			try:
 				entry = tup.rsplit(',');
				entry[0] = entry[0][1:].strip();
				entry[1] = int(entry[1][:-1]);
				urlFeatures.append((entry[0],entry[1]));
			except:
				pass;
		#print split[0], len(urlFeatures);
		for oentry in queryTerms:
			entry = porter.stem(oentry);
			if len(entry) >2 and entry in wordFeat:
				for urlPair in urlFeatures:
					wordFeat[entry].updateURLStats(urlPair[0],urlPair[1]);
			

def loadFeatures(fileName,wfilter=None):
	wordFeat = {};
	for line in open(fileName,'r'):
		line = line.strip().lower();
		split = line.split('\t');
		term = split[0];
		if (not wfilter) or (term in wfilter):
			if term not in wordFeat:
				wordFeat[term] = Word(term,'');#line.strip().lower());
				
			for entry in split[1:]:
				try:
					fsplit = entry.rsplit(':',1);
					name = fsplit[0];
					freq = round(float(fsplit[-1]),4);
					if name[0] == 'e':
						wordFeat[term].updateEntStats(name[2:],freq);
					elif name[0] == 'c':
						wordFeat[term].updateCatStats(name[2:],freq);
					elif name[0] == 'u':
						#name=name.replace('https://','').strip();
						#name=name.replace('http://','').strip();
						wordFeat[term].updateURLStats(name[2:],freq);
				except:
					if len(entry) > 1 :
						print 'ERROR',entry;
		
	return wordFeat;


def normalizeFeatures(wordFeat):
	#normalize the vectors
	#remove the features with certain threshold
	for entry in wordFeat.keys():
		wordFeat[entry].normalizeAll();
	return wordFeat;


def cleanFeatures(wordFeat):
	#normalize the vectors
	#remove the features with certain threshold
	for entry in wordFeat.keys():
		wordFeat[entry].reduceDim(40);
		#minF = wordFeat[entry].minFreq();
		#if minF > 0.5 :
		#	del wordFeat[entry];
			
	return wordFeat;

def writeCatFiles(outFolder,wordFeat,clist):
	if not os.path.exists(outFolder):
		os.mkdir(outFolder);
		
 	catWords = loadCatWords(wordFeat,clist);
 	
	print len(catWords);
	for cat , wordList in catWords.items():
		cat = cat.replace('/','_');
		if len(wordList) > 10:
			oFile = open(outFolder+'/'+cat+'_'+str(len(wordList))+'.txt','w');
			for word in wordList:
				#toWrite = word+'\t'+wordFeat[word].getVector()+'\n';
				oFile.write(wordFeat[word].toString()+'\n');
			oFile.close();

def loadCatWords(wordFeat,clist = None):
	catWords = {};
	#wordList = {};
 	clen = len(clist);
 	print clen;
 	for word, wObj in wordFeat.items():
		categories = wObj.getCats();
		for cat in categories:
			cat = cat.replace('/','_');
			if clen > 0 and cat in clist and cat not in catWords:
				#print 'found', cat;
				catWords[cat]= [];
			if cat in catWords:	
				catWords[cat].append(word);
				#wordList[word] = wordList.setdefault(word,0.0)+ 1.0;
	return catWords;

def clusterCategoryTerms(outFolder,wordFeat,clist,catWords):
	if not os.path.exists(outFolder):
		os.mkdir(outFolder);
			
 	toCluster = {};
 	print len(catWords);
 	for cat , wordList in catWords.items():
		if len(wordList) > 20 and len(wordList) < 1500:
			#get the feature vector
			#store and cluster
			print cat, len(wordList);
			toCluster.clear();
			for word in wordList:
				toCluster[word] = wordFeat[word].getFeatDict();
				
			#cluster
			oFile = open(outFolder+'/'+cat+'_'+str(len(toCluster))+'.txt','w');
			findClustersWithKMeans(toCluster,oFile);
			oFile.close();
			
 	
def writeFeatures(out,wordFeat):
	oFile = open(out+'/wordFeatures_reduce.txt','w');
			
	for word, wObj in wordFeat.items():
		toWrite = word+'\t'+wordFeat[word].getVector()+'\n';
		oFile.write(toWrite);
	oFile.close();

def getSimilarity(wordFeat, clist,oFile):
	similarity = {};
	toWrite = {};
	for cat, wordList in clist.items():
		print cat, len(wordList);
		wsort = sorted(wordList);
		wlen = len(wordList);
		for k in range(wlen-1):
			w1 = wsort[k];
			for j in range(k+1, wlen):
				w2 = wsort[j];
				key = w1+'\t'+w2;
				if key not in similarity:
					ecos, ccos, ucos = wordFeat[w1].getCosine(wordFeat[w2]);
					similarity[key] = 1.0; #
					toWrite.clear();
					if ecos > 0.03:
						toWrite ['e']=ecos;
					if ccos > 0.03:
						toWrite ['c']=ccos;	
					if ucos > 0.03:
						toWrite['u']= ucos;
					if len(toWrite) > 0:
						oFile.write(key+'\t'+ '\t'.join('{0}:{1}'.format(x,y) for x, y in toWrite.items())+'\n');
	return similarity;

def writeFeaturesFromDict(wordFeat,outFile):
	oFile = open(outFile,'w');
	
	for entry, featDict in wordFeat.items():
		oFile.write(entry+'\t'+ '\t'.join('{0}:{1}'.format(x,y) for x, y in featDict.items())+'\n');
	oFile.close();
			
def indexFeatures(fileName, indexPath, indexName):
	
'''
[1] = query freq
[2] = dexter tagged
[3] = url feat
[4] = output file
'''
def main(argv):
	#wfilter = loadFileInList(argv[2]);
	wfilter = filterWords(argv[1],50);
	#print len(wfilter);
	#wfilter = [];
	wordFeat = loadFeatures(argv[2],wfilter);
	#print len(wordFeat);
	#wordFeat = cleanFeatures(wordFeat);
	
	#clist = loadFileInList(argv[3]);
	#catWords = loadCatWords(wordFeat,clist);
	#oFile = open(argv[4],'w');
	#similarity = getSimilarity(wordFeat,catWords,oFile);
	
	#writeFeaturesFromDict(similarity);
	#oFile.close();
	
	oFile = open(argv[3]+'/filtered-word-feat.txt','w')
	for entry in wordFeat.keys():
		
		toWrite = entry+'\t'+wordFeat[entry].getVector()+'\n';
		oFile.write(toWrite);
	oFile.close();
	
	#wordFeat = cleanFeatures(wordFeat);
	#writeFeatures(argv[2],wordFeat);
	#writeCatFiles(argv[3],wordFeat,clist);
	#clusterCategoryTerms(argv[4],wordFeat,clist,catWords);
	#print len(wordFeat);
	#writeCatFiles(argv[2],wordFeat);	
'''
	queryFreq = loadQueryFreq(argv[1]);
	print len(queryFreq);
	wordFeat = getEntCatFeatures(argv[2],queryFreq);
	print len(wordFeat);
	getURLFeatures(argv[3],wordFeat);
	
	wordFeat = normalizeFeatures(wordFeat);
	
	if not os.path.exists(argv[4]):
		os.mkdir(argv[4]);
		
	#catWords = {};
	oFile = open(argv[4]+'/wordFeatures.txt','w');
			
	for word, wObj in wordFeat.items():
		toWrite = word+'\t'+wordFeat[word].getVector()+'\n';
		oFile.write(toWrite);
'''

 	
if __name__ == '__main__':
	main(sys.argv);		
	
				
'''
#for each query :
	#get non entity terms
		#make entity vector
		#freq
		#cat vector
	
	
	#get the terms
	#get the links
	
'''