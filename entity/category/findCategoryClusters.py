# -*- coding: utf-8 -*-
import sys
from features.featureManager import FeatureManager
import Pycluster as clust
import numpy as np
import random
from entity.category import findCatQueryDist
from clustering.build.kmean import KMeans
from features import toString,readWeightMatrix
from buildCategoryNetwork import returnFilteredNetwork
from clustering.evaluate.external import getRecallPrecision
import argparse
def clusterAllWithKMeans(argv):
	featMan = FeatureManager()
	featMan.readFeatures(argv[1])
	#sessCount = 0
	#lastSes = None;
	#session = []
	
	#stemmer =  stem.porter.PorterStemmer()
	weightMatrix = readWeightMatrix(argv[2])
	metrics = {}
	print len(weightMatrix)

	data = featMan.returnKeys()
	for k in range(4,50,2):
		i = len(data)/k
		if i == 0:
			i = 1
		kmeans = KMeans(i,data,weightMatrix,5, 0.1)
		kmeans.cluster();
		clusters = kmeans.getClusters();
		#means = kmeans.getMeans();
		noClus =kmeans.getTermInNoCluster();
	
		if clusters:
			fname = argv[5]+'_'+str(i)+'.txt'
			oFile = open(fname,'w');
			for entry in clusters:
				if len(entry) > 0:
					oFile.write(toString(entry,featMan)+'\n')
			oFile.write('NO CLUST\t'+toString(noClus,featMan)+'\n');
			oFile.close()
			metrics[k] = getRecallPrecision(argv[6],argv[7],fname,argv[1])
	for tcount, met in metrics.items():
		print tcount, met

def clusterAllWithKMediods(argv):
	featMan = FeatureManager()
	featMan.readFeatures(argv[1])
	
	data = featMan.returnKeys()
	#weightMatrix = readWeightMatrix(argv[2])
	weightList = getWeightMatrixForKMedFromFile(featMan.returnLastId(),argv[2],data)
	#getWeightMatrixForKMed(data, weightMatrix)
	print len(weightList)
	metrics = {}
	print 'Clustering'
	for k in range(4,50,2):
		i = (len(weightList)+1)/k
		if i == 0:
			i = 1
		clusArray, error, opt = clust.kmedoids(weightList,i, 10, None)
		print error, len(clusArray)
		clusters = {}
		for c in range(len(clusArray)):
			clusId = clusArray[c]
			if clusId not in clusters:
				clusters[clusId] = set()
			try:
				clusters[clusId].add(c)	
			except:
				print c #len(data)
		fname = argv[5]+'_'+str(i)+'.txt'
		oFile = open(fname,'w');
		for entry in clusters.values():
			#print len(entry)
			qStr = toString(entry,featMan)	
			oFile.write(qStr+'\n')
		oFile.close()
		metrics[k] = getRecallPrecision(argv[6],argv[7],fname,argv[1])
	
	for tcount, met in metrics.items():
		print tcount, met

		
def getWeightMatrixForKMedFromFile(count, fileName,data):
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
		if len(line) <20 and (not lbreak):
			lbreak = True
		if lbreak:
			split = line.split()
			i = int(split[0])
			j = int(split[1])
			if i and j in data:
				try:
					score = float(split[-1])/100.0
					#if score  > 0.80:
					#	print featMan.returnQuery(i),  featMan.returnQuery(j), split[-1]
					if i > j:
						(weightList[i])[j] = 1.0-round(score,2)
					else:
						(weightList[j])[i] = 1.0-round(score,2)
				except:
					print i, j, split[-1]
					
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
					i_arr[j] = random.uniform(0.75,1.0)
		weightList.append(i_arr)
	
	return weightList


def clusterCatWithKMeans(termCount, featMan, weightMatrix, catQueryDist,outFile = 'cat-clusters-with-mean.txt'):
	noClusSet = set()
	fclusters = []

	i = 1
	#cat = 'illinois'
	#qSet = catQueryDist[cat]
	oFile = open(outFile,'w')
	
	for cat, qSet in catQueryDist.items():
		if len(qSet) > 1:
			k = len(qSet)/termCount
			if k == 0:
				k = 1
			print cat, len(qSet), k
			
			if k > 1:
				kmeans = KMeans(k,list(qSet),weightMatrix,5, 0.1)
				kmeans.cluster();
				clusters = kmeans.getClusters();
				#means = kmeans.getMeans();
				noClus =kmeans.getTermInNoCluster();
				#print 'Clust ',cat, len(clusters), len(noClus), len(qSet)
			
			
				for entry in clusters:
					if len(entry) > 0:
						cStr = toString(entry,featMan)
						fclusters.append(cStr)
						oFile.write(cat+'\t'+cStr+'\n');
						#print cat,'\t', cStr
				for entry in noClus:
					noClusSet.add(featMan.returnQuery(entry));
			else:
				cStr = toString(qSet,featMan)
				oFile.write(cat+'\t'+cStr+'\n');	
			if i % 50 == 0:
				print i
			i+=1	
	oFile.close()
	return fclusters, noClusSet

def clusterCatWithMediodsAndNetwork(featMan, weightMatrix, catQueryDist,network):
	#cluster each cat find the outliers
	#move them to parents
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
			outliers = getOutliers(qList,catDist)
			for entry in clusters.values():
				qStr = toString(entry,featMan)
				fclusters.append(qStr)
							
			print 'Clust ',cat, len(clusters), error, opt
			if i % 50 == 0:
				print i
				break
			i+=1	
		
def getOutliers(queries, weightMatrix):
	qdist = {}
	for i in range(len(weightMatrix)):
		qdist[queries[i]] = 0.0
		for j in range(len(weightMatrix[i])):
			qdist[queries[i]] += weightMatrix[i][j]
			qdist[queries[j]] += weightMatrix[i][j]
	qlen = len(qdist)
	
	avgDist = 0.0
	for entry in qdist:
		qdist[entry]/=qlen
		avgDist+= qdist[entry]
	avgDist/=len(qdist)
	
	print 'AvgDist' ,avgDist
	outliers = []
	
	#sortd = sorted(qdist.items() , key = lambda x : x[1])
	for query, entry in qdist.items():
		ratio = 1.0 - (avgDist/entry)
		if ratio > 0 and ratio > 0.21 :
			outliers.append((query, entry))
			print query, entry, ratio
		
		if ratio < 0 and ratio < -0.30:
			outliers.append((query,entry))
			print query, entry, ratio
		
	print 'Outlier ',len(qdist), len(outliers)
	
	return outliers
			
def clusterCatWithMediods(noTerms,featMan, weightMatrix, catQueryDist, outFile = 'cat-clusters-with-med.txt'):
	
	noClusSet = set()
	fclusters = []
	subsets = {}
	i = 0;
	oFile = open(outFile,'w')
	for cat, qSet in catQueryDist.items():
		if len(qSet) > 1: # and cat in pairs:
			k = len(qSet)/noTerms
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
			
			#outliers = getOutliers(qList, catDist)
			#if cat in pairs:
			#	subsets[cat] = []
			for entry in clusters.values():
				qStr = toString(entry,featMan)
				fclusters.append(qStr)
				oFile.write(cat+'\t'+qStr+'\n');
				#if cat in pairs:
				#	subsets[cat].append(qStr)
							
			print 'Clust ',cat, len(clusters), error, opt
			if i % 5 == 0:
				print i
				#break
			i+=1	
			
			#for entry in clusters:
				#if len(entry) > 0:
					#cStr = toString(entry,featMan)
					#fclusters.append(cStr)
					##print cat,'\t', cStr
				
	oFile.close()
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
	parser = ap.ArguementParser(description = 'Generate clusters of entity tagged queries')
	parser.add_argument('-f', '--featFile', help='Feature file', required=True)
	parser.add_argument('-d', '--distFile', help='Pairwise Similarity file', required=True)
	parser.add_argument('-o', '--outDir', help='Output Directory', required=True)
	parser.add_argument('-a', '--algo', help='kmeans or kmediods', required=True)
	parser.add_argument('-l', '--lowerLimit', help='min limit on #terms in cluster', required=True,type=int)
	parser.add_argument('-u', '--upperLimit', help='upper limit on #terms in cluster', required=True,type=int)
	
	#argv = sys.argv
	args = parser.parse_args()
	
	#clusterAllWithKMediods(argv)
	featMan = FeatureManager()
	featMan.readFeatures(args.featFile)
	weightMatrix = readWeightMatrix(args.distFile)
	#clusterAllWithKMeans(argv)
	catQueryDist = findCatQueryDist(args.featFile,featMan)
	
	##stemmer =  stem.porter.PorterStemmer()
	#catNetwork, catQueryDist = returnFilteredNetwork(argv[1], argv[3], featMan,\
	#weightMatrix)
	#print len(catQueryDist)
	#
	##PRE-MERGE  WRITE
	#oFile = open(argv[4],'w')
	#for cat, entry in catQueryDist.items():
	#	qStr = toString(entry,featMan)
	#	oFile.write(cat +'\t'+qStr+'\n')
	#oFile.close()

	##CLUSTER PRE-MERGE
	#metrics = {}
	#metrics['pre-merge'] = getRecallPrecision(argv[6],argv[7],argv[4],argv[1])
	
	for termCount in range(args.lowerLimit,args.upperLimit):

		if args.algo == 'kmeans':
		    outSuff = args.outDir+'/kmeans_'
		    clusterCatWithKMeans(termCount,featMan, weightMatrix, catQueryDist, outSuff)
		elif args.alog == 'kmediods':
                      outSuff = args.outDir+'/kmeds_'
                      clusterCatWithMediods(termCount,featMan, weightMatrix, catQueryDist,outSuff)
                    	
		#metrics[termCount] = getRecallPrecision(argv[6],argv[7],argv[5],argv[1])
	
	#for tcount, met in metrics.items():
	#	print tcount, met
	#printCategoryQueryDictionary(argv[1],argv[2],argv[3])
	
	
	
	