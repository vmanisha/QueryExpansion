# -*- coding: utf-8 -*-
from features.featureManager import FeatureManager
import Pycluster as clust
import numpy as np
import random
from entity.category import findCatQueryDist
from clustering.build.kmeans import KMeans
from features import toString,readWeightMatrix
from buildCategoryNetwork import returnFilteredNetwork
from clustering.evaluate.external import getRecallPrecision
import argparse as ap


def getPairLabelsFromClusters(cluster_list, featMan):
	samePairsSet = set()
	differentPairsSet = set()
	for cluster in cluster_list:
		# for each cluster get all pairs and label
		# them on same task.
		generatePairs(cluster, cluster, featMan, samePairsSet)
	for i in range(len(cluster_list)-1):
		for j in range(i+1, len(cluster_list)):
			generatePairs(cluster_list[i], cluster_list[j], \
			featMan, differentPairsSet)
	return samePairsSet, differentPairsSet
	
def generatePairs(item_list1, item_list2, featMan, output_list):
	for i in range(len(item_list1)):
		query_i = featMan.returnQuery(item_list1[i])
		for j in range(len(item_list2)):
			query_j = featMan.returnQuery(item_list2[j])
			if query_j < query_i:
				temp = query_j
				query_j = query_i
				query_i = temp
			if query_i != query_j:
				output_list.add(query_i +'\t'+query_j)

def clusterAllWithKMeans(lowerLimit, upperLimit, featMan, weightMatrix,\
					samePairsSet, differentPairsSet, outDir):
	metrics = {}
	print len(weightMatrix)

	data = featMan.returnKeys()
	for k in range(lowerLimit,upperLimit,2):
		i = len(data)/k
		if i == 0:
			i = 1
		kmeans = KMeans(i,data,weightMatrix,5, 0.1)
		kmeans.cluster();
		clusters = kmeans.getClusters();
		noClus =kmeans.getTermInNoCluster();
		
		if clusters:
			predicted_same_pairs, predicted_different_pairs = \
				getPairLabelsFromClusters(clusters,featMan)
			fname = outDir+'_'+str(i)+'.txt'
			oFile = open(fname,'w');
			for entry in clusters:
				if len(entry) > 0:
					oFile.write(toString(entry,featMan)+'\n')
			oFile.write('NO CLUST\t'+toString(noClus,featMan)+'\n');
			oFile.close()
			metrics[k] = getRecallPrecision(samePairsSet, \
			differentPairsSet, predicted_same_pairs, predicted_different_pairs)
	for tcount, met in metrics.items():
		print tcount, met
	return metrics

def clusterCatWithKMeans(lowerLimit, upperLimit, featMan, \
						weightMatrix, samePairsSet, \
						differentPairsSet, catQueryDist,\
						outFile = 'cat-clusters-with-mean.txt'):
	metrics = {}
	for termCount in range(lowerLimit, upperLimit):
		i = 1
		fclusters = []
		allCatClusters = []
		oFile = open(outFile+'_'+str(termCount)+'.txt','w')
		for cat, qIdSet in catQueryDist.items():
			if len(qIdSet) > 1:
				k = len(qIdSet)/termCount
				if k == 0:
					k = 1
				print cat, len(qIdSet), k
				if k > 1:
					kmeans = KMeans(k,list(qIdSet),weightMatrix,5, 0.1)
					kmeans.cluster();
					clusters = kmeans.getClusters();
					noClus =kmeans.getTermInNoCluster();
					for entry in clusters:
						if len(entry) > 1:
							allCatClusters.append(entry)
						if len(entry) > 0:
							cStr = toString(entry,featMan)
							fclusters.append(cStr)
							oFile.write(cat+'\t'+cStr+'\n');
					oFile.write(cat+'\t'+'NO CLUST\t'+\
								toString(noClus,featMan)+'\n');
				else:
					cStr = toString(qIdSet,featMan)
					oFile.write(cat+'\t'+cStr+'\n');
					allCatClusters.append(list(qIdSet))
				
				if i % 50 == 0:
					print i
				i+=1	
		predicted_same_pairs, predicted_different_pairs = \
						getPairLabelsFromClusters(allCatClusters,featMan)
		print 'COUNTS ',termCount, len(allCatClusters), \
		len(predicted_same_pairs), len(catQueryDist)
		metrics[termCount] = getRecallPrecision(samePairsSet, \
										differentPairsSet,\
										predicted_same_pairs,\
										predicted_different_pairs)	
		oFile.close()
	for tcount, met in metrics.items():
		print tcount, met
	return metrics

def clusterAllWithKMediods(lowerLimit, upperLimit,\
				 featMan, weightFile, samePairsSet, \
				 differentPairsSet, outDir):
	
	data = featMan.returnKeys()
	weightList = getWeightMatrixForKMedFromFile(featMan.returnLastId(),\
                weightFile,data)
	#getWeightMatrixForKMed(data, weightMatrix)
	print len(weightList)
	metrics = {}
	
	for k in range(lowerLimit,upperLimit,2):
		print 'Clustering with terms ', k
		cluster_list = []
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
		fname = outDir+'_'+str(i)+'.txt'
		oFile = open(fname,'w');
		for entry in clusters.values():
			cluster_list.append(list(entry))
			qStr = toString(entry,featMan)	
			oFile.write(qStr+'\n')
		oFile.close()
		predicted_same_pairs, predicted_different_pairs = \
						getPairLabelsFromClusters(cluster_list,featMan)
		metrics[k] = getRecallPrecision(samePairsSet, \
										differentPairsSet,\
										predicted_same_pairs,\
										predicted_different_pairs)	
	
	for tcount, met in metrics.items():
		print tcount, met
		
	return metrics

def clusterCatWithMediods(lowerLimit, upperLimit,featMan, weightMatrix, \
						 samePairsSet, differentPairsSet, catQueryDist, \
						outFile = 'cat-clusters-with-med.txt'):
	
	oFile = open(outFile,'w')
	metrics = {}
	for noTerms in range(lowerLimit, upperLimit):
		#fclusters = []
		cluster_list = []
		i = 0
		oFile = open(outFile+str(noTerms)+'.txt','w')
		for cat, qSet in catQueryDist.items():
			if len(qSet) > 1: # and cat in pairs:
				k = len(qSet)/noTerms
				if k == 0:
					k = 1
			
				qList = list(qSet)
				catDist = getWeightMatrixForKMed(qList, weightMatrix)
							
				clusArray, error, opt = clust.kmedoids(catDist,k, 5, None)
				clusters = {}
				for c in range(len(clusArray)):
					clusId = clusArray[c]
					if clusId not in clusters:
						clusters[clusId] = set()
					clusters[clusId].add(qList[c])
				
				for entry in clusters.values():
					cluster_list.append(list(entry))
					qStr = toString(entry,featMan)
					#fclusters.append(qStr)
					oFile.write(cat+'\t'+qStr+'\n');
				print 'Clust ',cat, len(clusters), error, opt
				if i % 5 == 0:
					print i
				i+=1	
		predicted_same_pairs, predicted_different_pairs = \
						getPairLabelsFromClusters(cluster_list,featMan)
		metrics[noTerms] = getRecallPrecision(samePairsSet, \
					differentPairsSet,\
					predicted_same_pairs,\
					predicted_different_pairs)	

		oFile.close()
	for tcount, met in metrics.items():
		print tcount, met
	return metrics

def clusterCatWithMediodsAndNetwork(threshold, \
				    lowerLimit, upperLimit, featMan, \
				    weightMatrix, samePairsSet, \
				    differentPairsSet, catQueryDist, \
				    catNetwork, \
				    outFile = 'cat-clusters-with-med.txt'):
	#cluster each cat find the outliers
	#move them to parents
	metrics = {}
	for noTerms in range(lowerLimit, upperLimit, 2):
		cluster_list = []
		#fclusters = []
		i = 0
		oFile = open(outFile+str(noTerms)+'.txt','w')
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
				#outliers = getOutliers(qList,catDist)
				for entry in clusters.values():
					cluster_list.append(list(entry))
					qStr = toString(entry,featMan)
					oFile.write(cat+'\t'+qStr+'\n');
					#fclusters.append(qStr)
				print 'Clust ',cat, len(clusters), error, opt
				if i % 50 == 0:
					print i
				i+=1
		predicted_same_pairs, predicted_different_pairs = \
						getPairLabelsFromClusters(cluster_list,featMan)
		key = str(threshold)+'_'+str(noTerms)
		metrics[key] = getRecallPrecision(samePairsSet, differentPairsSet,\
			     		            predicted_same_pairs,\
			     		            predicted_different_pairs)
		oFile.close()
	for tcount, met in metrics.items():
		print tcount, met
	return metrics

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
						

# Returns two sets one with pairs labeled on same task
# and one with pairs labeled on different task.
def loadPairsFromFile(file_name):
	same_task_set = set()
	different_task_set = set()
	
	for line in open(file_name):
		split = line.split('\t')
		query1 = split[0]
		query2 = split[1]
		label = split[-1].strip()
		# swap the queries if query2 precedes query1 alphabetically
		if query2 < query1:
			temp = query2
			query2 = query1
			query1 = temp
		
		if query1 != query2:
			if 'same' in label:
				same_task_set.add(query1+'\t'+query2)
			if 'different' in label:
				different_task_set.add(query1+'\t'+query2)
	return same_task_set, different_task_set	

def mergeMetrics(total_metrics_dict, metrics_dict ):
	for entry, metric_name_value_dict in metrics_dict.iteritems():
		if entry not in total_metrics_dict:
			total_metrics_dict[entry] = {}
		for metric_name, metric_value in metric_name_value_dict.iteritems():
			if metric_name not in total_metrics_dict[entry]:
				total_metrics_dict[entry][metric_name] = []
			total_metrics_dict[entry][metric_name].append(metric_value)

def computeAverageAndVarianceOfMetrics(system_name, total_metrics_dict):
	for no_of_terms , metric_dict in total_metrics_dict.iteritems():
		for metric_name, metric_values_list in metric_dict.iteritems():
			print system_name,'\t', metric_name, '\t',no_of_terms,'\t',\
			np.mean(metric_values_list), '\t', np.std(metric_values_list)
			
			
		
if __name__ == '__main__':
	parser = ap.ArgumentParser(description = 'Generate clusters of'+ \
							'entity tagged queries')
	parser.add_argument('-f', '--featFile', help='Feature file', required=True)
	parser.add_argument('-d', '--distFile', help='Pairwise Similarity file',\
						required=True)
	parser.add_argument('-o', '--outDir', help='Output Directory', \
						required=True)
	parser.add_argument('-a', '--algo', help='kmeans or kmediods or'+ \
						'cat_kmediods or cat_kmeans', \
						required=True)
	parser.add_argument('-l', '--lowerLimit', help='min limit on #terms in '+\
						'cluster', required=True,type=int)
	parser.add_argument('-u', '--upperLimit', help='upper limit on #terms in'+\
						' cluster', required=True,type=int)
	parser.add_argument('-p', '--pairLabelFile', help='Task labels for a'+\
						' pair of queries, same_task and different_task',\
						 required=False)
	parser.add_argument('-t', '--ontFile', help='DBpedia ontology file', required=False)
	
	#argv = sys.argv
	args = parser.parse_args()
	
	
	featMan = FeatureManager()
	featMan.readFeatures(args.featFile)
	weightMatrix = readWeightMatrix(args.distFile)
		
	##stemmer =  stem.porter.PorterStemmer()
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
	samePairsSet = differentPairsSet = None
	if args.pairLabelFile:
		samePairsSet , differentPairsSet =\
					loadPairsFromFile(args.pairLabelFile)
	
	total_metrics_dict = {}
	for i in range(3):
		if args.algo == 'kmediods':
			outSuff = args.outDir+'/kmeds_'
			metrics = clusterAllWithKMediods(args.lowerLimit, args.upperLimit,\
								featMan, args.distFile, samePairsSet,\
								differentPairsSet, args.outDir)
			mergeMetrics(total_metrics_dict, metrics)
		else:
			weightMatrix = readWeightMatrix(args.distFile)
			if args.algo == 'kmeans':
				outSuff = args.outDir+'/kmeans_'
				metrics = clusterAllWithKMeans(args.lowerLimit, args.upperLimit,\
									featMan, weightMatrix, \
									samePairsSet,
									differentPairsSet,\
									args.outDir)
				mergeMetrics(total_metrics_dict, metrics)
			elif args.algo == 'cat_kmeans':
				catQueryDist = findCatQueryDist(args.featFile,featMan)
				outSuff = args.outDir+'/cat_kmeans_'
				metrics = clusterCatWithKMeans(args.lowerLimit, args.upperLimit,\
									featMan, weightMatrix, samePairsSet,\
									differentPairsSet, catQueryDist, \
									outSuff)
				mergeMetrics(total_metrics_dict, metrics)
			elif args.algo == 'cat_kmediods':
				catQueryDist = findCatQueryDist(args.featFile,featMan)
				outSuff = args.outDir+'/cat_kmeds_'
				metrics = clusterCatWithMediods(args.lowerLimit, args.upperLimit,\
									featMan, weightMatrix, samePairsSet,\
									differentPairsSet,catQueryDist,\
									outSuff)
				mergeMetrics(total_metrics_dict, metrics)
			elif args.algo == 'cat_merge':
				for threshold in np.arange(0.5, 0.95, 0.1):
					catNetwork, catQueryDist = returnFilteredNetwork(\
												args.featFile, \
												args.ontFile, \
												featMan,weightMatrix, threshold)
					outSuff = args.outDir+'/cat_merge_kmeds_'+str(threshold)+'_'
					metrics = clusterCatWithMediodsAndNetwork(threshold,\
										args.lowerLimit,\
										args.upperLimit,featMan, weightMatrix,\
										samePairsSet, differentPairsSet, \
										catQueryDist, catNetwork, outSuff)
					mergeMetrics(total_metrics_dict, metrics)
	computeAverageAndVarianceOfMetrics(args.algo, total_metrics_dict)		                    	
		
	#for tcount, met in metrics.items():
	#	print tcount, met
	#printCategoryQueryDictionary(argv[1],argv[2],argv[3])
	
	
	
	
