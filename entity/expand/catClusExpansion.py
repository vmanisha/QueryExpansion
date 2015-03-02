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
			clusScore = 0.0
			tDict = {}
			score, terms = scorer.score(qSet,clust)
			#if score > 0:
			#	print entry, score, terms
			clusScore+= score
			for t in terms.keys():
				if t not in tDict:
					tDict[t] = 0.0
				tDict[t]+=round(terms[t],2)
			
			rTerms = sorted(tDict.items(),reverse = True, key = lambda x : x[1])	
			order[i] = []
			for entry in rTerms:
				order[i].append(entry)
				
			clusScore/=(1.0*len(clust))
			scores[i]= clusScore
			i+=1
			
		topTerms = []
		covered = {}
		for entry in sorted(scores.items(), reverse = True, key = lambda x : x[1]):
			#print entry
			for x in order[entry[0]]:
				if x[0] not in covered:
					topTerms.append(x)
					covered[x[0]] = 1
				
				if len(topTerms) > limit:
					break
		#print query, topTerms	
		return topTerms
	
