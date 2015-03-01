# -*- coding: utf-8 -*-

class ScoreClusterTerms:
	
	def __init__(self):
		print 'Initializing cluster expansion'
	
	def score(query, clustList, scorer, cText, limit):
		i = 0
		scores = {} #contains score of clusters
		order = {}  #contains the order of terms
		for clust in clustList:
			clusScore = 0.0
			tDict = {}
			for entry in clust:
				score, terms = scorer.score(query,entry)
				clusScore+= score
				
				for t in terms.keys():
					if t not in tDict:
						tDict[t] = 0.0
					tDict[t]+=terms[t]
			
			rTerms = sorted(tDict.items(),reverse = True, key = lambda x : x[1])	
			order[i] = []
			for entry in rTerms:
				order[i].append(entry)
				
			clusScore/=(1.0*len(clust))
			scores[i]= clusScore
			i+=1
			
		topTerms = []
		for entry in sorted(scores.items(), reverse = True, key = lambda x : x[1]):
			topTerms.append(x for x in order[entry[0]])
			if len(topTerms) > limit:
				break
		
		return topTerms
	