# -*- coding: utf-8 -*-
import ast, sys

def getQueryWithEntities(fileName):
	stats = {}
	for line in open(fileName,'r'):
		split = line.strip().split('\t')
		#query = split[0]
		spotDict = ast.literal_eval(split[-1])
		slen = len(spotDict)
		if slen > 1:
			print line.strip()
			stats[slen] = stats.setdefault(slen,0.0) + 1.0
			
	print stats

def getEntities(fileName):
	stats = {}
	for line in open(fileName,'r'):
		split = line.strip().split('\t')
		#query = split[0]
		spotDict = ast.literal_eval(split[-1])
		for entity in spotDict.keys():
			stats[entity] = stats.setdefault(entity,0.0)+ 1.0
	
	for entity, score in stats.iteritems():
		print entity, '\t', score

if __name__ == '__main__':
	argv = sys.argv
	getEntities(argv[1])