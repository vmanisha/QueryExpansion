# -*- coding: utf-8 -*-
#given the data and weight matrix and \lambda, send the clusters
import sys
from features import readWeightMatrix
from features.featureManager import FeatureManager
import random
class DPMeans:
	
	def __init__(self):
		pass
	
	def cluster(self, data, weightMatrix, clambda, idiff ):
		cIndex = {}
		for entry in data:
			cIndex[entry] = 1
		
		mean = []
		total = 0
		c = 0
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
		for iteration in range(7):
			print len(mean), 'Means'
			#find the cluster assignments
			for xi in data:
				minc = -1
				mind = 1000
				isMean = False
				for mi in range(len(mean)):
					ci = mean[mi]
					if ci == xi:
						isMean = True
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
				if mind > clambda and not isMean:
					cIndex[xi] = len(mean)
					mean.append(xi)
				
			#recompute the means
			newMeans = []
			clusAssignments = {}
			for xi, ci in cIndex.items():
				if ci not in clusAssignments:
					clusAssignments[ci] = []
				clusAssignments[ci].append(xi)
			
			print 'Assignments', len(clusAssignments), clusAssignments
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
			
			print 'Means', mean, newMeans
			mean = newMeans
			
		print iteration
		return cIndex, mean

	def clusterWithNetwork(weightMatrix, cNetwork, cDist, clambda, cdiff):
		#for each category cluster
		for cat, queryList in cDist.items():
			print cat, len(queryList)
			cluster, mean = self.cluster(queryList, weightMatrix, clambda, cdiff)
			
			
			
		#output it to a file
		
		#count the number of clusters with one query
		#write that distribution
		#Move the points around with the following :
			#If parent 	
		
	
def main(argv):
	featMan = FeatureManager()
	featMan.readFeatures(argv[1])
	
	data = featMan.returnKeys() #random.sample(list(featMan.returnKeys()),40)
	print 'To cluster', data
	#weightMatrix = readWeightMatrix(argv[2])
	weightList = readWeightMatrix(argv[2])
	
	dp = DPMeans()
	dp.cluster(data,weightList, 0.60,0.1)
	
	

if __name__ == '__main__':
	main(sys.argv)