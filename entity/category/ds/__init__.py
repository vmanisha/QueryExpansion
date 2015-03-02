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
	

def loadClustersWithQueryFile(fileName, queryFile):
	queryId = {}
	
	i=1
	
	for line in open(queryFile,'r'):
		split = line.split('\t')
		query = filterWords(split[0].strip())
		if query in queryId:
			print 'Found query ',query
		else:
			queryId[query] = str(i)
		i+=1
	
	keys = sorted(queryId.keys())
	print len(keys), keys[-5:]
	clusters = []
	for line in open(fileName,'r'):
		line = line.strip()
		cpoints = []
		if len(line) > 0:
			split = line.split('\t')
			for entry in split:
				try:
					print entry, queryId[entry.strip()]
					cpoints.append(queryId[entry.strip()])
				except:
					print 'Cant find', entry
					pass
		clusters.append(cpoints)
	return clusters