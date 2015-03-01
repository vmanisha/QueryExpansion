# -*- coding: utf-8 -*-

class ClusterExpansion:
	
	def __init__(self):
		
	
	def expandText(query, clustList, scorer, cText, limit):
		i = 0
		scores = {} #contains score of clusters
		order = {}  #contains the order of terms
		for clust in clustList:
			scores[i], order[i]=scorer.score(query,clust)
			i+=1
			
		topTerms = []
		for entry in sorted(scores.items(), reverse = True, key = lambda x : x[1]):
			topTerms.append(x for x in order[entry[0]])
			if len(topTerms) > limit:
				break
		
		return topTerms
	