# -*- coding: utf-8 -*-

class ScoreClusterTerms:
	
	def __init__(self):
		print 'Initializing cluster expansion'
	
	def getTerms(self, clust):
		terms = {}
		for entry in clust:
			split = entry.split()
			for st in split:
				if len(st) > 2:
					if st not in terms:
						terms[st]= 0.0
					terms[st]+=1.0
		return terms;

	def score(self,query, clustList, scorer, limit):
		i = 0
		scores = {} #contains score of clusters
		order = {}  #contains the order of terms
		qSet = query.split()

		for clust in clustList:
			clusScore = 0.0
			tDict = {}
			cTerms = self.getTerms(clust)
			if i % 5000 == 0:
				print i,len(clust), len(cTerms)
			score, terms = scorer.score(qSet,cTerms)
			#if score > 0:
			#	print entry, score, terms
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
	
