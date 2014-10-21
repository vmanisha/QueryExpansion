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

def toTag(file1, file2):
	tagged = {};
	for line in open(file1,'r'):
		split = line.split('\t');
		query = split[0].strip();
		if query not in tagged:
			tagged[query] = 1.0;
	
	for line in open(file2,'r'):
		split= line.split('\t');
		query = split[0].strip();
		if query not in tagged:
			print query;
	

if __name__ == '__main__':
	argv = sys.argv
	#getEntities(argv[1])
	toTag(argv[1],argv[2]);
	