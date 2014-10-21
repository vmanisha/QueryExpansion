# -*- coding: utf-8 -*-
import os
import sys
from utils import get_cosine
import numpy
from clusterTasks import clusterWithSimMatrix, writeDict
from __init__ import getFeatDict
'''	
#1 = directory
#2 = out directory
#3 = num
'''
def main(argv):
	
	
	num = int(argv[3])
	outDir = argv[2]+argv[3]
	if not os.path.exists(outDir):
		os.mkdir(outDir)
	slambda = [0,0.10,0.20,0.20,0.20,0.30]
	data = {}
	for ifile in os.listdir(argv[1]):
		data ={}
		for line in open(argv[1]+'/'+ifile,'r'):
			query, feat = getFeatDict(line.lower())
			data[query] = feat
		

		#find similarity between all points
		keys = data.keys()
		if len(keys) > num:
			ofile = open(outDir+'/'+ifile,'w')
			sim =numpy.zeros(shape=(len(keys),len(keys)))
			#similarity = {}
			for k in range(len(keys)-1):
				v1 =keys[k]
				sim[k][k]=1
				#if v1 not in similarity:
					#similarity[v1] = {}
				for j in range(k+1, len(keys)):
					v2 = keys[j]
					sim[j][j]=1
					f1 = data[v1]
					f2 = data[v2]
					
					#similarity[v1][v2] = 0.0
					similarity=0.0
					for index, features in f1.items():
						#print index, features
						#similarity[v1][v2] += (get_cosine(features, f2[index])*slambda[index]
						similarity = (get_cosine(features, f2[index])*slambda[index])
					if similarity > 0:
						sim[k][j]=sim[j][k] = similarity
						ofile.write(keys[k].replace(' ','_')+' '+ keys[j].replace(' ','_')+' '+ str(round(similarity,3))+'\n')
			ofile.close()
			'''clusters = clusterWithSimMatrix(sim,num)
			labelResult = {}
			labels = clusters.labels_
			for i in range(len(keys)):
				if labels[i] not in labelResult:
					labelResult[labels[i]] = {}
				labelResult[labels[i]][keys[i]] = 1
	
			writeDict(labelResult,outDir+'/'+ifile)
			'''
if __name__ == '__main__':
	main(sys.argv)	