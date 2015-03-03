# -*- coding: utf-8 -*-
from nltk.stem import porter
from queryLog import normalize
class ScoreClusterTerms:
	
	def __init__(self):
		print 'Initializing cluster expansion'
		self.stemmer = porter.PorterStemmer()

	def score(self,qSet, clustList, scorer, limit):
		i = 0
		scores = {} #contains score of clusters
		order = {}  #contains the order of terms
		
		
		for clust in clustList:
			
			score, terms = scorer.score(qSet,clust)
			
			#if score > 0 and len(terms) < 15:
			#	print qSet, score, terms
			sTerms = sorted(terms.items(),reverse = True, key = lambda x : x[1])	
			#print qSet, score, clust, sTerms
			order[i] = []
			for entry in sTerms:
				if entry[0] not in qSet and entry[1] > 0.0:
					order[i].append(entry)
					if len(order[i]) > limit:
						break
					
			#score/=(1.0*len(clust))
			scores[i]= score
			i+=1
			
		topTerms = []
		covered = {}
		for entry in sorted(scores.items(), reverse = True, key = lambda x : x[1]):
			#print entry
			#if entry[1] > 0.0 and len(order[entry[0]]) < 15:
			#	print qSet, entry, order[entry[0]]
				
			for x in order[entry[0]]:
				if x[0] not in covered:
					#if x[1] > 0.0:
					topTerms.append(x)
					covered[x[0]] = 1
				
				if len(topTerms) > limit:
					break
			if len(topTerms) > limit:
				break
		#print query, topTerms	
		return topTerms
	
