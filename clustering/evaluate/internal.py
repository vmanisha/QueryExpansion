# -*- coding: utf-8 -*-

import sys, ast
from entity.category.ds import loadClustersWithQueryFile
from features import readWeightMatrix

def DB(clusters, weightMatrix, centers=None, points=None):
	if not centers:
		avg_intra_i = []
		minpi = []
		minpd = []
		#find centers
		for i in range(len(clusters)):
			print i
			i_points = clusters[i]
			sorti = sorted(i_points)
			minpi1 = 10000
			minpd1 = 10000
			#intra cluster i
			aintra_i = 0.0
			for pi1 in sorti:
				total1 = 0.0
				for pi2 in sorti:
					try:
						aintra_i+= weightMatrix[pi1][pi2]
						total1+= weightMatrix[pi1][pi2]
					except:
						pass
				avg1 = total1/len(sorti)
				if avg1 < minpd1:
					minpd1 = avg1
					minpi1 = pi1
			
			aintra_i /= (len(sorti)*len(sorti))
			avg_intra_i.append(aintra_i)
			minpi.append(minpi1)
			minpd.append(minpd1)
			
		print 'Found centers', len(minpi), len(minpd)
		#print minpi
		#print minpd
		#exit()
		

		db_i_j = {}
		for i in range(len(clusters)):
			i_points = clusters[i]
			sorti = sorted(i_points)
			
			di = 0.0			
			for pi in sorti:
				try:
					if pi < minpi[i]:
						di+=weightMatrix[pi][minpi[i]]
					else:
						di+=weightMatrix[minpi[i]][pi]
				except:
					pass
			di/=len(sorti)
			
			
			db_i_j[i] = {}
			dc_i_j = 0
			for j in range(len(clusters)):
				
				if i!=j :
					pj = minpi[j]
					totj = 0.0
					for pi in sorti:
						try:
							if pi < pj:
								totj+=weightMatrix[pi][pj]
							else:
								totj+=weightMatrix[pj][pi]
						except:
							pass
					totj/=len(sorti)
					
					try:
						if i < j:					
							dc_i_j = weightMatrix[minpi[i]][minpi[j]]
						else:
							dc_i_j = weightMatrix[minpi[j]][minpi[i]]
					except:
						dc_i_j = 0
						pass
					
					if dc_i_j > 0:
						db_i_j[i][j] = (di + totj)/dc_i_j
					else:
						db_i_j[i][j] = -1
						#sprint 'DC i j is 0', i, j
						
						
	dbIndex = 0
	for i in range(len(clusters)):
		print 'DB i --- ',i, max(db_i_j[i].values())
		dbIndex += max(db_i_j[i].values())
	
	print 'DB Index ', len(clusters), dbIndex, dbIndex/len(clusters)
	
			
def Dunn(clusters, weightMatrix, centers=None, points=None):
	#find the mean distance between two points in cluster
	deltaList = []
	if not centers:
		diam = 0.0
		
		for clus in clusters:
			found = 0;
			nc = len(clus);
			if nc > 1:
				diam = 1.0 / (nc * (nc-1));
			dsum = 1.0;
			for i in range(len(clus)-1):
				for j in range(len(clus)):
					try:
						 dsum+=weightMatrix[clus[i]][clus[j]]
						 found+=1						
					except:
						try:
							dsum+=weightMatrix[clus[j]][clus[i]]	
							found+=1
						except:
							#print clus[i], clus[j]
							pass
						pass
			if found > 0:
				print 'Found', found
			deltaList.append(dsum*diam);
		maxDiam = max(deltaList);
		print 'Max diameter ',maxDiam
		#find center
		avg_inter_ij = {}
		
		for i in range(len(clusters)-1):
			i_points = clusters[i]
			sorti = sorted(i_points)
						
			if i not in avg_inter_ij:
				avg_inter_ij[i] = {}
			
			for j in range(i+1,len(clusters)):
				if j not in avg_inter_ij:
					avg_inter_ij[j] = {}
				
				total_i_j = 0;
				j_points = clusters[j]
				sortj = sorted(j_points)	
				for pi in sorti:
					for pj in sortj:
						try:
							total_i_j += weightMatrix[pi][pj]
						except:
							pass
							
				avg_inter_ij[i][j] = avg_inter_ij[j][i] = total_i_j/(len(sorti)*len(sortj))

		fmin_i = []
		for i, vals in avg_inter_ij.items():
			mini = min(vals.values())
			fmin_i.append(mini/maxDiam)

		print 'FMIN ', fmin_i
		print 'Dunn index ', min(fmin_i)		
	
	
if __name__ == '__main__':
	argv = sys.argv
	lbreak = False
	weightMatrix = readWeightMatrix(argv[2])
	clusters = loadClustersWithQueryFile(argv[1],argv[3])
	#load the cluster-assignments and points
	
	
	print len(clusters)
	print len(weightMatrix)
	
	#DB(clusters,weightMatrix)
	Dunn(clusters, weightMatrix)	
	#load the weight matrix
	
	#load the centers