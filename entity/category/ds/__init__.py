# -*- coding: utf-8 -*-


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