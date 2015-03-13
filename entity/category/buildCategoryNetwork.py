# -*- coding: utf-8 -*-
import sys
import os
from dbPedia.ntriples import NTriplesParser
from dbPedia.triple import MySink, Triple
from dbPedia import loadSkosCategories
import networkx as nx
import matplotlib.pyplot as plt
from features.featureManager import FeatureManager
from features import toString
from entity.category import findCatQueryDist
import random
#from findCategoryClusters import clusterCatWithMediods

def buildNetwork(queryFile, skosFile,featMan):
	catQueryDist = findCatQueryDist(queryFile, featMan)
	catQueryDist['dow_jones_transportation_average'] = set()
	
	
	total = set(catQueryDist.keys())
	#found = set()
	#i = 0
	#for line in open(argv[2],'r'):

	print len(catQueryDist)

	found , related , broad = loadSkosCategories(skosFile, catQueryDist)
	
	notFound = total.difference(found)
	categoryNetwork=nx.DiGraph()
	#B parent of A
	for entry in broad:
		categoryNetwork.add_edge(entry[1],entry[0])
	print len(notFound), len(related), len(broad)
	
	return categoryNetwork, catQueryDist

def mergeCategories(categoryNetwork,catQueryDist):
	
	avoid = set()
	for i in range(15):
		for entry in categoryNetwork.nodes():
			toDel = False
			if entry in catQueryDist  and len(catQueryDist[entry]) < 60 and entry not in avoid:
				#send the queries to inedges
				merge = 0
				parents = []
			
				for in_tup in categoryNetwork.in_edges_iter(entry):
					parent = in_tup[0]
					parents.append(parent)
					if parent not in catQueryDist:
						catQueryDist[parent] = set()
					merge+=1
					catQueryDist[parent].update(catQueryDist[entry])
				
				if merge == 0:
					#print 'Lonely Node', entry, categoryNetwork.in_edges(entry)
					avoid.add(entry)
				else:
					#add the outgoing to incoming
					for out_tup in categoryNetwork.out_edges_iter(entry):
						child = out_tup[1]
						for par in parents:
							if par != child:
								categoryNetwork.add_edge(par,child)	
					
					categoryNetwork.remove_node(entry)
					toDel = True
	
			if toDel:
				#print 'Deleting ', entry, len(catQueryDist[entry])
				del catQueryDist[entry]
	
	return categoryNetwork, catQueryDist

def returnFilteredNetwork(queryFile, skosFile,featMan):
	
	catNetwork, catQueryDist=buildNetwork(queryFile, skosFile,featMan)
	catNetwork , catQueryDist= mergeCategories(catNetwork,catQueryDist)
	
	return catNetwork, catQueryDist
	
	
def main(argv):	
	
	featMan = FeatureManager()
	featMan.readFeatures(argv[3])
	
	catQueryDist = findCatQueryDist(argv[1], featMan)
	catQueryDist['dow_jones_transportation_average'] = set()
	
	
	total = set(catQueryDist.keys())

	print len(catQueryDist)

	found , related , broad = loadSkosCategories(argv[2], catQueryDist)
	
	notFound = total.difference(found)
	
	
	#build the category network
	categoryNetwork=nx.DiGraph()
	#B parent of A
	for entry in broad:
		if 'illinois' == entry[1] or 'illinois' == entry[0]:
			print 'BROAD', entry
		
		categoryNetwork.add_edge(entry[1],entry[0])
		
	print len(notFound), len(related), len(broad)
	
	avoid = set()
	#nx.write_adjlist(categoryNetwork,"catNetwork.adjlist")
	for i in range(15):
		for entry in categoryNetwork.nodes():
			toDel = False
			if entry in catQueryDist  and len(catQueryDist[entry]) < 60 and entry not in avoid:
				#send the queries to inedges
				merge = 0
				parents = []
			
				for in_tup in categoryNetwork.in_edges_iter(entry):
					parent = in_tup[0]
					parents.append(parent)
					if parent not in catQueryDist:
						catQueryDist[parent] = set()
					merge+=1
					catQueryDist[parent].update(catQueryDist[entry])
				
				if merge == 0:
					#print 'Lonely Node', entry, categoryNetwork.in_edges(entry)
					avoid.add(entry)
				else:
					#add the outgoing to incoming
					for out_tup in categoryNetwork.out_edges_iter(entry):
						child = out_tup[1]
						for par in parents:
							if par != child:
								categoryNetwork.add_edge(par,child)	
					
					categoryNetwork.remove_node(entry)
					toDel = True
	
			if toDel:
				#print 'Deleting ', entry, len(catQueryDist[entry])
				del catQueryDist[entry]
				#print entry,'PARENT', pList
			
	both = 0;
	single = 0;
	pairs = set()
	edgeSet = set()
	for edge in categoryNetwork.edges_iter():
		#print edge,
		if edge[0] in catQueryDist and edge[1] in catQueryDist:
			if len(catQueryDist[edge[0]]) < 70 and len(catQueryDist[edge[1]]) < 70:
				#print edge,  len(catQueryDist[edge[0]]), len(catQueryDist[edge[1]])
				if random.randint(0,10) > 8 and len(catQueryDist[edge[0]]) > 50:
					pairs.add(edge[0])
					pairs.add(edge[1])
					if edge[0]!= edge[1]:
						edgeSet.add(edge)
			both+=1;
		else:
			single+=1
			#if edge[0] in catQueryDist:
			#	print '\t', len(catQueryDist[edge[0]]),
		
		#print
	print both, single, len(catQueryDist)
	
	#take the queries of these nodes, cluster them using kmeans
	weightMatrix = {}
	lbreak = False
	for line in open(argv[4],'r'):
		if lbreak:
			split = line.split()
			i = int(split[0])
			if i not in weightMatrix:
				weightMatrix[i] = {}
				
			try:
				weightMatrix[i][int(split[1])] = 1.0-round(float(split[-1]),2)
			except:
				print line
		if len(line) <10 and (not lbreak):
			lbreak = True
	
	oFile = open(argv[5][:argv[5].find('.')]+'cat_dist.combined','w')
	
	for cat, qList in catQueryDist.items():
		oFile.write(toString(qList,featMan)+'\n')
	
	oFile.close()
	
	
	oFile = open(argv[5],'w')
	
	
	clusters, noClus, subset = clusterCatWithMediods(featMan, weightMatrix, catQueryDist, pairs)
	#clusters, noClus = clusterEachCategory(featMan, weightMatrix, catQueryDist)
	for entry in clusters:
		oFile.write(entry+'\n')
	#oFile.write('\t'.join(noClus)+'\n')
	oFile.close()
	
	#for edge in edgeSet:
		#print '\n'+edge[0]+'\t ----- \t'+ edge[1]
		#clusA = subset[edge[0]]
		#clusB = subset[edge[1]]
		#
		#mi = max(len(clusA),len(clusB))
		#for i in range(mi):
			#try:
				#print clusA[i] +'\t ----- \t'+ clusB[i]
			#except:
				#try:
					#print clusA[i] +'\t ----- \t'
				#except:
					#print clusB[i] +'\t ----- \t'
		#
		
	
	

if __name__ =='__main__':
	main(sys.argv)
