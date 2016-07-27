# -*- coding: utf-8 -*-
from utils import filterWords

def loadClusters(fileName):
	clusters = []
	for line in open(fileName,'r'):
		line = line.strip()
		cpoints = []
		if len(line) > 0:
			split = line.split('\t')
			for entry in split:
				try:
					cpoints.append(entry.strip())
				except:
					pass
		clusters.append(cpoints)
	return clusters
	

def loadClustersWithQueryFile(fileName, idDict):
	
	clusters = []
	for line in open(fileName,'r'):
		line = line.strip()
		cpoints = []
		if len(line) > 0:
			split = line.split('\t')
			for entry in split:
				try:
					#print entry, queryId[entry.strip()]
					if len(entry.strip()) > 0:
						cpoints.append(idDict[entry.strip()])
				except:
					#print 'Cant find', entry
					pass
		clusters.append(cpoints)
	return clusters
