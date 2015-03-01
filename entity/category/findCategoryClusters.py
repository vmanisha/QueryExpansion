# -*- coding: utf-8 -*-
import sys
from features.featureManager import FeatureManager
import Pycluster as clust
import numpy as np
import random
from clustering.build.kmean import KMeans
from features import toString,readWeightMatrix

def clusterAllWithKMeans(featMan, weightMatrix):
	featMan = FeatureManager()
	featMan.readFeatures(argv[1])
	#sessCount = 0
	#lastSes = None;
	#session = []
	
	#stemmer =  stem.porter.PorterStemmer()
	weightMatrix = readWeightMatrix(argv[2])
			
	print len(weightMatrix)

	data = featMan.returnKeys()
	kmeans = KMeans(15000,data,weightMatrix,5, 0.1)
	kmeans.cluster();
	clusters = kmeans.getClusters();
	#means = kmeans.getMeans();
	noClus =kmeans.getTermInNoCluster();

	if clusters:
		oFile = open(argv[3],'w');
		for entry in clusters:
			if len(entry) > 0:
				oFile.write(toString(entry,featMan)+'\n')
		oFile.write('NO CLUST\t'+toString(noClus,featMan)+'\n');
		oFile.close()

def clusterAllWithKMediods(argv):
	featMan = FeatureManager()
	featMan.readFeatures(argv[1])
	
	data = list(featMan.returnKeys())
	#weightMatrix = readWeightMatrix(argv[2])
	weightList = getWeightMatrixForKMedFromFile(len(data),argv[2])
	#getWeightMatrixForKMed(data, weightMatrix)
	print 'Clustering'
	clusArray, error, opt = clust.kmedoids(weightList,10000, 5, None)
	clusters = {}
	for c in range(len(clusArray)):
		clusId = clusArray[c]
		if clusId not in clusters:
			clusters[clusId] = set()
			clusters[clusId].add(data[c])	
			
	oFile = open(argv[3],'w');
	for entry in clusters.values():
		qStr = toString(entry,featMan)	
		oFile.write(qStr+'\n')
	oFile.close()

def getWeightMatrixForKMedFromFile(count, fileName):
	weightList = []
	weightList.append(np.array([]))
	
	for i in range(1,count):
		i_arr = np.ones(i)
		weightList.append(i_arr)
		if i %5000 == 0:
			print i
	
	print 'Filling values'
	lbreak = False
	for line in open(fileName,'r'):
		if lbreak:
			split = line.split()
			i = int(split[0])
			j = int(split[1])
			(weightList[i])[j] = 1.0-round(float(split[-1]),2)
		if len(line) <10 and (not lbreak):
			lbreak = True
			
	print 'Finished Values'
	return weightList
	
def getWeightMatrixForKMed(data, weightMatrix):
	weightList = []
	weightList.append(np.array([]))
	for i in range(1,len(data)):
		q1 = data[i]
		i_arr = np.ones(i)
		for j in range(i-1,-1,-1):
			q2 = data[j]
			try:
				i_arr[j] = weightMatrix[q1][q2]
			except:
				try:
					i_arr[j] = weightMatrix[q2][q1]
				except:
					i_arr[j] = random.uniform(0.8,1.0)
		weightList.append(i_arr)
	
	return weightList

			

	
def clusterCatWithKMeans(featMan, weightMatrix, catQueryDist):
	noClusSet = set()
	fclusters = []

	i = 1
	#cat = 'illinois'
	#qSet = catQueryDist[cat]
	for cat, qSet in catQueryDist.items():
		if len(qSet) > 1:
			k = len(qSet)/20
			if k == 0:
				k = 1
			print cat, len(qSet), k
		
			kmeans = KMeans(k,list(qSet),weightMatrix,5, 0.1)
			kmeans.cluster();
			clusters = kmeans.getClusters();
			#means = kmeans.getMeans();
			noClus =kmeans.getTermInNoCluster();
			print 'Clust ',cat, len(clusters), len(noClus), len(qSet)
			
			
			for entry in clusters:
				if len(entry) > 0:
					cStr = toString(entry,featMan)
					fclusters.append(cStr)
					#print cat,'\t', cStr
			for entry in noClus:
				noClusSet.add(featMan.returnQuery(entry));
				
			if i % 50 == 0:
				print i
			i+=1	
	
	return fclusters, noClusSet


def clusterCatWithMediods(featMan, weightMatrix, catQueryDist,pairs):
	
	noClusSet = set()
	fclusters = []
	subsets = {}
	i = 0;
	for cat, qSet in catQueryDist.items():
		if len(qSet) > 1: # and cat in pairs:
			k = len(qSet)/5
			if k == 0:
				k = 1
			#print cat, len(qSet), k
			qList = list(qSet)
			catDist = getWeightMatrixForKMed(qList, weightMatrix)
						
			clusArray, error, opt = clust.kmedoids(catDist,k, 5, None)
			#print 'Queries', qList
			clusters = {}
			for c in range(len(clusArray)):
				clusId = clusArray[c]
				if clusId not in clusters:
					clusters[clusId] = set()
				clusters[clusId].add(qList[c])
				
			if cat in pairs:
				subsets[cat] = []
			for entry in clusters.values():
				qStr = toString(entry,featMan)
				fclusters.append(qStr)
				if cat in pairs:
					subsets[cat].append(qStr)
							
			print 'Clust ',cat, len(clusters), error, opt
			#if i % 5 == 0:
			#	print i
				#break
			i+=1	
			
			#for entry in clusters:
				#if len(entry) > 0:
					#cStr = toString(entry,featMan)
					#fclusters.append(cStr)
					##print cat,'\t', cStr
				
			
	return fclusters, noClusSet, subsets


def printCategoryQueryDictionary(fileName, clusFile, weightFile):
	
	featMan = FeatureManager()
	
	featMan.readFeatures(fileName)
	categoryDictionary = {}
	for query, feat in featMan.iterFeatures():
		catDict = feat.returnFeature('cat')
		for entry in catDict:
			if entry not in categoryDictionary:
				categoryDictionary[entry] = set()
			categoryDictionary[entry].add(query)
		
	outC = open(clusFile,'w')
	outW = open(weightFile,'w')
	for entry, qlist in categoryDictionary.items():
		outC.write(toString(qlist,featMan)+'\n')
		outW.write(str(qlist)+'\n')
	outC.close()
	
			
	weightMatrix = {}
	cc = 0
	#calculate the weight matrix
	for entry, qlist in categoryDictionary.items():
		sort = sorted(qlist)
		for i in range(len(sort)-1):
			qid1, qf1 = featMan.returnFeature(sort[i])
			if qf1:
				if sort[i]  not in weightMatrix:
					weightMatrix[sort[i]] = {}
				for j in range(i+1,len(sort)):
					qid2, qf2 = featMan.returnFeature(sort[j])
					if qf2:
						if sort[j] not in weightMatrix[sort[i]]:
							qcos, ucos, userCos, ngramCos, entCos, catCos = qf1.findCosineDistance(qf2)
							qjac = qf1.findJacardDistance(qf2)
							#qedit = qf1.findEditDistance(qf2)
							#normalized distance
							#dist = (j - i)#*1.0/len(session)
							
							edgeScore = (.25*((qcos + qjac )/2.0) +\
							.15*ngramCos + .15*ucos + \
							.15*userCos + .15*entCos + .15*catCos)
					
							if edgeScore > 0.05:
								weightMatrix[sort[i]][sort[j]] = edgeScore
		if cc % 10000==0:
			print cc
		cc+=1
		
	outW.write('\n')
	
	
	for entry1, scoreList in weightMatrix.items():
		for entry2, score in scoreList.items():
			outW.write(str(entry1)+' '+str(entry2)+' '+str(score)+'\n');
	outW.close();
						


if __name__ == '__main__':
	argv = sys.argv
	clusterAllWithKMediods(argv)
	
	#printCategoryQueryDictionary(argv[1],argv[2],argv[3])