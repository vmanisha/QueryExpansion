# -*- coding: utf-8 -*-
import os, sys
from nltk.corpus import wordnet as wn;
from utils.coOcManager import CoOcManager;
from utils.coOccurrence import CoOccurrence;
from itertools import product;
from clustering.cluster import KMeans;
from clustering.clusterTasks import transformWeightMatrix,clusterTasksAgglomerative
from utils.wordManager import WordManager;
from utils import stopSet, loadFileInList;
#load the session co-occurrence
#calculate wordNet similarity
#find Kmean clusters
#re-write the clusters


def compare(word1, word2):
    ss1 = wn.synsets(word1,wn.NOUN);
    ss2 = wn.synsets(word2,wn.NOUN);

    if len(ss1)>0 and len(ss2)>0:
    	maxv = min(s1.path_similarity(s2) for (s1, s2) in product(ss1, ss2));
    	if maxv:
    		result = 1.0 - maxv;
    		return result;
	
def findWordNetDistance(word1, word2):
	return compare(word1, word2);

def findSessionDistance(word1, word2, coOcMan,thresh=0.0):
	return coOcMan.getPMI(word1, word2,thresh);

def findQueryDistance(word1, word2, coOcMan, thresh=0.0):
	return coOcMan.getPMI(word1, word2,thresh);

def findClustersWithKMeans(weightMatrix,outFile):
	wordList = weightMatrix.keys();
	n = len(wordList)/5;
	
	if n > 0:
		X1, X2 = transformWeightMatrix(weightMatrix);
		clusters = clusterTasksAgglomerative(X2,n);
		
		labelResult = {}
		labels = clusters.labels_
		
		for i in range(len(X1)):
			if labels[i] not in labelResult:
				labelResult[labels[i]] = []
		
			labelResult[labels[i]].append(X1[i]);
			
		for ind, entries in  labelResult.iteritems():
				outFile.write(str(ind)+'\t'+' '.join(entries)+'\n');
				i+=1;
		
	
def findClusters(weightMatrix, wordList,n):
	#wordList = weightMatrix.keys();
	
	print n, len(wordList);
	
	if n > 1:
		kmeans = KMeans(n, wordList, weightMatrix,10, 0.01);
		kmeans.cluster();
		clusters = kmeans.getClusters();
		means = kmeans.getMeans();
		noClus =kmeans.getTermInNoCluster();
		return clusters, means, noClus;
		
	return None, None,None;
		

def writeClusters(outFile, means, distance, words, entities, noClus):
	#print len(means),means;
	clen = len(means);
	for i in range(clen):
		if len(words[i]) > 1:
			maxDist = str(round(max(distance[i]),3)) if len(distance[i]) > 0 else 'NA';
			minDist = str(round(min(distance[i]),3)) if len(distance[i]) > 0 else 'NA';
			medDist = str(round(distance[i][len(distance[i])/2],3)) if len(distance[i]) > 0 else 'NA';
			meanDist = 'NA';
			if len(distance[i]) > 0:
				meanDist = str(round(sum(distance[i])/len(distance[i]),3));
			center = means[i];
			wsort = sorted(words[i].items(),reverse = True, key = lambda x : x[1]);
			wString = ' '.join('{0}:{1}'.format(x[0],x[1]) for x in wsort);
			esort = sorted(entities[i].items(),reverse = True, key = lambda x : x[1]);
			eString = None;
			if len(esort) > 10:
				eString = ' '.join('{0}:{1}'.format(x[0],x[1]) for x in esort[:10]);
			else:
				eString = ' '.join('{0}:{1}'.format(x[0],x[1]) for x in esort);
			
			outFile.write(str(i)+'\t'+center+'\t'+eString+'\t'+wString+
			'\t'+meanDist+'\t'+minDist+'\t'+maxDist+'\t'+medDist+'\n');
		i+=1;
	outFile.write('NA\t'+' '.join(noClus)+'\n');
	
	
def findClusterMetaData(clusters,means,featMan,weightMatrix, termFreq):
	entities = {};
	distance = {};
	words = {};
	i = 0;
	for cluster in clusters:
		entities[i] = {};
		distance[i] = [];
		words[i] = {};
		for word in cluster:
			words[i][word] = termFreq[word];
			for ent in featMan.getEntities(word):
				if ent not in entities[i]:
					entities[i][ent] = 0.0;
				entities[i][ent] += 1.0;
			
			if word in weightMatrix and means[i] in weightMatrix[word] and \
			weightMatrix[word][means[i]] > 0.0:
				distance[i].append(weightMatrix[word][means[i]]);
		
		for ent in entities[i].keys():
			if entities[i][ent] < 3:
				del(entities[i][ent]);
		
				
		i+=1;	
	return words, distance, entities;
		

def normalize(matrix):
	for t1 in matrix.keys():
		total = sum(matrix[t1].values());
		for t2 in matrix[t1].keys():
			matrix[t1][t2]=1.0-(matrix[t1][t2]/total);
	return matrix;

def filterFiles(fileList, ffilter, words):
	for ifile in fileList:
		if ifile not in ffilter and words not in ifile:
			yield ifile;
			
def findScore(featName, weightMatrix, func, man, thresh, weight):
	score = {};
	smin = None;
	smax = None;
	for entry in weightMatrix.keys():
		for entry2 in weightMatrix[entry].keys():
			s = func(entry, entry2, man, thresh);
			score[entry+' '+entry2] = s;
			if (not smin) or smin > s:
				smin = s;
			if (not smax) or smax < s:
				smax = s;
	
	#print featName, smin, smax;	
	diff = smax - smin;
	#normalize the scores;
	for entry in score.keys():
		space = entry.find(' ');
		entry1 = entry[0:space];
		entry2 = entry[space+1:];
		if diff > 0:
			weightMatrix[entry1][entry2]+= weight*(1.0-((score[entry] - smin)/diff));
			
				
	return weightMatrix;
		
'''
[1] = category folder
[2] = queryCoOccurence
[3] = sessionCoOccurence
[4] = features
[5] = outFolder
[6] = files to filter
'''
def main(argv):
	#load the co-occurrance values
	
	inFolder = argv[1];
	weightMatrix={};
	
	coQueryOccur = CoOccurrence();
	coQueryOcMan = CoOcManager(argv[2],coQueryOccur,' ');
	
	coSessOccur = CoOccurrence();
	coSessOcMan = CoOcManager(argv[3],coSessOccur,' ');
	
	featureFolder = argv[4];
	featMan = WordManager(featureFolder,False);
	
	outFolder = argv[5];
	if not os.path.exists(outFolder):
		os.mkdir(outFolder);
	
	ffilter = [];#loadFileInList(argv[6]);
	termList = [];
	
	#sFile = open('score-output.txt','w');
	fileList = os.listdir(inFolder);
	
	termFreq = {};
	
	for ifile in filterFiles(fileList,ffilter, 'redirect'):
		print ifile;
		termList = [];	
		termFreq.clear();
		for line in open(inFolder+'/'+ifile,'r'):
			split = line.split('\t');
			term = split[0].strip();
			freq = float(split[1]);
			if term not in stopSet and featMan.hasWord(term) and freq > 5:
				termList.append(term);
				termFreq[term] = freq;
		termList = sorted(termList);
			
		tlen = len(termList);
		if tlen >= 10 and tlen < 5000:
			for i in range(tlen):
				word1 = termList[i];
				if word1 not in weightMatrix:
						weightMatrix[word1] = {};
					
				for j in range(i+1, tlen):
					word2 = termList[j];
					if word2 not in weightMatrix:
						weightMatrix[word2] = {};
					eScore = featMan.getEntCosine(word1,termList[j]);
					cScore = featMan.getCatCosine(word1,termList[j]);
					uScore = featMan.getUrlCosine(word1,termList[j]);
					weightMatrix[word1][word2] =0.18*(1.0-uScore)+\
					0.16*(1.0-cScore)+0.16*(1.0-eScore);
					weightMatrix[word2][word1] = weightMatrix[word1][word2];
			
			
			weightMatrix=findScore('session-co-occur',weightMatrix,\
			findSessionDistance,coSessOcMan,3.0,0.25);
			weightMatrix=findScore('query-co-occur',weightMatrix,\
			findQueryDistance,coQueryOcMan,3.0,0.25);
					
			#wScore = 0.0
			#wScore = findWordNetDistance(termList[i], termList[j]);
			#if not wScore:
			#	wScore = 0.0;
			#print termList[i], termList[j], cScore, wScore;
			#if totalS > 0.0:
			#	sFile.write(termList[i]+' '+termList[j]+' '+str(sScore)
			#	+' '+str(qScore)+' '+str(uScore)+' '+str(cScore)+\
			#' '+str(eScore)+'\n');
			sTerm = sorted(termFreq.items()	, reverse=True, \
			key = lambda x : x[1]);
			wordList = [x[0] for x in sTerm];
			gt10 = 0;
			for x in sTerm:
				gt10 += 1 if x[1] > 15 else 0;
			if gt10 <3 or (gt10 > (len(sTerm)/7)):
				gt10 = len(sTerm)/7;
				
			clusters, means, noClus = findClusters(weightMatrix,wordList,gt10);
			print 'CLUSTER ',clusters;
			'''print 'CLUSTER ',clusters;
			print 'Mean ',means;
			print 'noCluster ',noClus;
			'''
			
			if clusters:
				oFile = open(outFolder+'/'+ifile,'w');
				
				word, distance, entities = findClusterMetaData(clusters,\
				means,featMan,weightMatrix,termFreq);
				'''print 'sortedWords ',word;
				print 'Distances ',distance;
				print 'Entities ',entities;
				'''
				writeClusters(oFile, means, \
				distance, word, entities, noClus);
				#findClustersWithKMeans(weightMatrix,oFile);
				#print '\n';
				#oFile.write(clusterString);
				oFile.close();
			else:
				print 'NO CLUSTERS FOR ',ifile, gt10, ;
			weightMatrix.clear();
					
	#sFile.close();



if __name__ == '__main__':
	main(sys.argv);	
	
	
'''
2 types of clustering
	--network based
	--feature based

For each category:
	find the words that occur more than 2 times
	For feature based:
		Occurrence in cat C --
		entities--
		top 5 categories--
		links--
		users (not consistant!)
	write to file
	-- Tried Kmeans (doesnt work) -- sklearn
	-- Try my implementation
	-- Agglomerative clustering
	
	
	For network based:
		no of sessions together
		no of immediate queries together
		no of queries together
		no of users together
		no of entities
		no of links
		wordnet distance
	write to file
---------------------------------------

Clustering algorithms -- work on the graph and features
Report the cluster numbers
(Still have to figure out which one!!!)
----------------------------------------

Mapping to subclusters
	for a given query:
		find entities
		find the category
		find the cluster as follows:
			word vect sim b/w cluster terms and query
			word vect sim b/w cluster terms and qdoc
			Avg Pmi b/w query and cluster terms
			Max Pmi b/w query and cluster terms
			min Pmi b/w query and cluster terms
			Rank terms using comb of above
		get the terms and report accuracy of :
			term prediction
			retrieval
					

Properties of each cluster
	- top entities
	- dist distribution (round off to 2 places)
	- sorted words

The features were not normalized correctly. So normalizing them.
'''