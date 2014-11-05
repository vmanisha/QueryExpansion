# -*- coding: utf-8 -*-
from entity.category.categorySubcluster import CategorySubcluster;
from entity.category.findCategorySubclusters import findScore;
from entity.category.findCategorySubclusters import findSessionDistance;
from entity.category.findCategorySubclusters import findQueryDistance;
from plots import plotLine;
from utils.coOcManager import CoOcManager;
from utils.coOccurrence import CoOccurrence;
from utils.wordManager import WordManager;
import os,sys;

def findDiameter(weightMatrix):
	keys = weightMatrix.keys();
	nc = len(keys);
	diam = 1.0 / (nc * (nc-1));
	dsum = 0;
	for i in range(nc):
		for j in range(i+1, nc):
			dsum+= weightMatrix[keys[i]][keys[j]];
	return (dsum*diam);
		

def findWeightMatrix(featMan,coSessOcMan,coQueryOcMan, p1,p2=None ):
	weightMatrix = {};
	words1 = sorted(p1);
	words2 = None;
	if p2:
		words2 = sorted(p2);
	else:
		words2 = words1	
	
	for i in range(len(words1)):
		word1 = words1[i];
		
		if word1 not in weightMatrix:
			weightMatrix[word1] = {};
		
		if p2:
			st = 0; # different list
		else:
			st = i+1; #same list
			
		for j in range(st,len(words2)):
			word2= words2[j];
		
			if word2 not in weightMatrix:
				weightMatrix[word2]= {};
				
			if word1 != word2:
				eScore = featMan.getEntCosine(word1,word2);
				cScore = featMan.getCatCosine(word1,word2);
				uScore = featMan.getUrlCosine(word1,word2);
				weightMatrix[word1][word2] =0.18*(1.0-uScore)+\
					0.16*(1.0-cScore)+0.16*(1.0-eScore);
				weightMatrix[word2][word1] = weightMatrix[word1][word2];
		
	weightMatrix=findScore('session-co-occur',weightMatrix,\
		findSessionDistance,coSessOcMan,3.0,0.25);
	weightMatrix=findScore('query-co-occur',weightMatrix,\
		findQueryDistance,coQueryOcMan,3.0,0.25);
			
	return weightMatrix;

def findCatIndexes(catObj,featMan,coSessOcMan,coQueryOcMan):
	
	subClustDiam = {};
	clustList = catObj.getSubclusters();
	#for each cluster get the diameter
	for clusPair in clustList :
		entry = clusPair[0];
		phraseDict = clusPair[1];
		weightMatrix = findWeightMatrix(featMan,coSessOcMan,coQueryOcMan,phraseDict.keys());
		diam = findDiameter(weightMatrix);
		subClustDiam[entry] = diam;
	
	maxDiam = max(subClustDiam.values());
	
	if maxDiam  > 0:
		clustDistMatrix = {};
		#build clustDist matrix
		for i in range(len(clustList)):
			p1 = clustList[i][1].keys();
			for j in range(i+1, len(clustList)):
				p2 = clustList[j][1].keys();
				weightMatrix = findWeightMatrix(featMan,coSessOcMan,coQueryOcMan,p1,p2);
				dist = findMinInDict(weightMatrix);
				
				key = str(clustList[i][0]) +'_'+str(clustList[j][0]);
				clustDistMatrix[key] = dist;
		if len(clustDistMatrix.values()) > 0:
			minClusDist = min(clustDistMatrix.values());
			return minClusDist/maxDiam;
	
	return -1000;

def findMinInDict(weightMatrix):
	gmin = None;
	for i , wordDict in weightMatrix.iteritems():
		if not gmin:
			gmin = min(wordDict.values());
		else:
			gmin = min(gmin, wordDict.values());
	return gmin;

def plotValues(indexList, fileName,xlabel, ylabel):

	esorted = sorted(indexList.items(), key = lambda x : x[0]);
	plotLine(esorted, xlabel,ylabel,fileName);
	
'''
argv[1] = input directory of clusters
argv[2] = query co-occurence file
argv[3] = session co-occurence file
argv[4] = features words
argv[5] = outFolder;

'''
def main(argv):
	
	coQueryOccur = CoOccurrence();
	coQueryOcMan = CoOcManager(argv[2],coQueryOccur,' ');
	
	coSessOccur = CoOccurrence();
	coSessOcMan = CoOcManager(argv[3],coSessOccur,' ');
	
	featureFolder = argv[4];
	featMan = WordManager(featureFolder,False);
	
	outFolder = argv[5];
	
	dindex = {};
	#scindex = {};
	#load the clusters
	for ifile in os.listdir(argv[1]):
		catClusters = CategorySubcluster(argv[1]+'/'+ifile);
		dind = findCatIndexes(catClusters, featMan,coSessOcMan,coQueryOcMan);
		
		#sc = 0;
		totalPhrases = catClusters.uniquePhrases;
		
		print 'CoEff', ifile, totalPhrases, dind;
		
		if totalPhrases not in dindex:
			dindex[totalPhrases]= [];
			#scindex[totalPhrases] = [];
		dindex[totalPhrases].append(dind);
		#scindex[totalPhrases].append(sc);
	
	
	plotValues(dindex, outFolder+'/'+'dindex.png','# terms in Cat file','Dunn Index');
	#plotValues(scindex, 'scindex.png');
		

if __name__ == '__main__':
	main(sys.argv);