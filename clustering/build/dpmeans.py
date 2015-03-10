# -*- coding: utf-8 -*-
#given the data and weight matrix and \lambda, send the clusters
import sys
from features import readWeightMatrix
from features import toString
from features.featureManager import FeatureManager
import random
from entity.category.buildCategoryNetwork import returnFilteredNetwork
class DPMeans:
	
	def __init__(self):
		pass
	
	def cluster(self, data, weightMatrix, clambda, idiff ):
		cIndex = {}
		for entry in data:
			cIndex[entry] = 1

		mean = []
		minv = -1
		mind = 1000
		print len(data)
		
		for v1 in weightMatrix.keys():
			vtotal = sum(weightMatrix[v1].values())
			vavg =  vtotal/len(weightMatrix[v1])
			#print 'Avg',v1, vavg
			if mind > vavg:	
				mind = vavg
				minv = v1
	
		mean.append(minv)
			
		print 'Starting with ', len(mean)
		for iteration in range(5):
			print 'Means', len(mean),
			#find the cluster assignments
			for xi in data:
				mind = 1000
				cIndex[xi] = -1
				isMean = False
				for mi in range(len(mean)):
					ci = mean[mi]
					if ci == xi:
						isMean = True
						if cIndex[xi] == -1:
							cIndex[xi] = mi	
						continue
					try:
						if weightMatrix[xi][ci] < mind:
							mind=weightMatrix[xi][ci]
							cIndex[xi] = mi
					except:
						try:
							if weightMatrix[ci][xi] < mind:
								mind=weightMatrix[ci][xi]
								cIndex[xi] = mi		
						except:
							
							pass
				#print 'C for',xi, mind, minc, cIndex[xi], (mind > clambda)
				#check with \lambda and create a new cluster
				if cIndex[xi] == -1 and mind > clambda and not isMean:
					cIndex[xi] = len(mean)
					mean.append(xi)
				
				if cIndex[xi] == -1:
					print xi, mind, isMean, clambda
					
			#recompute the means
			newMeans = []
			clusAssignments = {}
			for xi, ci in cIndex.items():
				if ci not in clusAssignments:
					clusAssignments[ci] = []
				clusAssignments[ci].append(xi)
			
			print 'Assignments', len(clusAssignments) , len(cIndex)#, clusAssignments
			for ci, xList in clusAssignments.items():
				newd = 1000
				newc = -1
				for xi in xList:
					avg = 0.0
					for xj in xList:
						try:
							avg+= weightMatrix[xi][xj]
						except:
							try:
								avg+= weightMatrix[xj][xi]
							except:
								avg+= random.uniform(0.8,1.0)
								pass
					avg/=len(xList)
					if avg < newd:
						newd = avg
						newc = xi
				newMeans.append(newc)
			
			diff = 1.0 - (len(set(newMeans) & set(mean))/(len(mean)*1.0))
			print 'Similar', diff, len(newMeans), len(mean)

			if diff < idiff:
				print iteration
				break
			
			print 'Means', len(mean), len(newMeans)
			mean = newMeans
			
		#print iteration
		
		#merge one item cluster
		merged = 0
		for ci, cList in clusAssignments.items():
			if len(cList) == 1:
				xi = cList[0]
				minA = 1000
				minC = -1
				for cj, scList in clusAssignments.items():
					cAvg = 0.0
					for entry in scList:
						try:
							cAvg+= weightMatrix[xi][entry]
						except:
							try:
								cAvg+= weightMatrix[entry][xi]
							except:
								pass
					cAvg/=len(scList)
					if cAvg > 0 and cAvg < minA:
						minA = cAvg
						minC = cj
				if minA < clambda:
					cIndex[xi] = minC
					merged+=1
		print 'Merged', len(cIndex), merged, len(mean) - merged
			
		return cIndex, mean

	#def reassignClusters(self, ccIndex, weightMatrix, cNetworkm , clambda ):
		
	#	for
	
	
	def clusterWithNetwork(self,featMan,weightMatrix, cNetwork, cDist, clambda, cdiff):
		#for each category cluster
		oFile = open('DPClusters-cat-dist.combined_'+str(clambda)+'.txt','w')
		clusterPointDist = {}
		cati = 1
		for cat, queryList in cDist.items():
			#print cat, len(queryList)
			if len(queryList) > 3:
				cluster, mean = self.cluster(queryList, weightMatrix, clambda, cdiff)
				toWriteClus = {}
				print 'Cat',cat, len(cluster), len(queryList)
				for d, c in cluster.items():
					if c not in toWriteClus:
						toWriteClus[c] = []
					toWriteClus[c].append(d)
				for c, entry in toWriteClus.items():
					le = len(entry)
					if le > 0:
						cStr = toString(entry,featMan).strip()
						if len(cStr) > 0:
							oFile.write(cat+'\t'+cStr+'\n')
					if le not in clusterPointDist:
						clusterPointDist[le] =0
					clusterPointDist[le]+=1
		
			cati+=1
			if cati%5000==0:
				print cati
				#break;
			
		oFile.close()
		for entry in sorted(clusterPointDist.items(), reverse=True, key = lambda x : x[1]):
			print entry
		
		#output it to a file
		
		#count the number of clusters with one query
		#write that distribution
		#Move the points around with the following :
			#If parent 	
		

#argv[1] = feature file
#argv[2] = weight file
#argv[3] = query file
#argv[4] = skos file

def main(argv):
	featMan = FeatureManager()
	featMan.readFeatures(argv[1])
	
	data = featMan.returnKeys() #random.sample(list(featMan.returnKeys()),40)
	print 'To cluster', data
	#weightMatrix = readWeightMatrix(argv[2])
	weightList = readWeightMatrix(argv[2])
	
	catNetwork, catQueryDist = returnFilteredNetwork(argv[3], argv[4], featMan)
	dp = DPMeans()
	x = float(argv[5])
	while x < 0.85:
		dp.clusterWithNetwork(featMan,weightList,catNetwork, catQueryDist,x,0.01)
		x+=0.10
	
	

if __name__ == '__main__':
	main(sys.argv)