# -*- coding: utf-8 -*-
from nltk.stem import porter
from queryLog import normalize
class ScoreClusterTerms:
	
	def __init__(self):
		print 'Initializing cluster expansion'
		self.stemmer = porter.PorterStemmer()


	def scoreWithIndex(self,qSet, clustList,cIndex, scorer, limit):
		toEvaluate=[]
		for entry in qSet:
			try:
				clusters = cIndex[entry]
				for cind in clusters:
					toEvaluate.append(clustList[cind])
			except:
				pass
		
		if len(toEvaluate) > 0:
			return self.score(qSet,toEvaluate,scorer, limit)
		
		return []
				
	def score(self,qSet, clustList, scorer, limit):
		i = 0
		scores = {} #contains score of clusters
		order = {}  #contains the order of terms
		
		terms = {}
		
		for clust in clustList:
			
			score, cterms = scorer.score(qSet,clust)
			
			#if score > 0 and len(terms) < 15:
			#	print qSet, score, terms
			sTerms = sorted(cterms.items(),reverse = True, key = lambda x : x[1])	
			#print qSet, score, clust, sTerms
			#order[i] = []
			#for entry in sTerms:
				#if entry[0] not in qSet and entry[1] > 0.0:
					#order[i].append(entry)
					#if len(order[i]) > limit:
						#break
					
			#score/=(1.0*len(clust))
			#scores[i]= score
			for entry in sTerms:
				if entry[0] not in qSet and entry[1] > 0.0:
					if entry[0] not in terms:
						terms[entry[0]]= 0.0
					terms[entry[0]]+= round(score*entry[1],2)
				
			i+=1
			
		topTerms = []
		covered = {}
		for entry in sorted(terms.items(), reverse = True, key = lambda x : x[1]):
			if entry[0] not in covered:
				if entry[1] > 0.0:
					topTerms.append(entry)
					covered[entry[0]] = 1
			
			if len(topTerms) > limit:
				break	
		#for entry in sorted(scores.items(), reverse = True, key = lambda x : x[1]):
			##print entry
			##if entry[1] > 0.0 and len(order[entry[0]]) < 15:
			##	print qSet, entry, order[entry[0]]
				#
			#for x in order[entry[0]]:
				#if x[0] not in covered:
					##if x[1] > 0.0:
					#topTerms.append(x)
					#covered[x[0]] = 1
				#
				#if len(topTerms) > limit:
					#break
			#if len(topTerms) > limit:
				#break
		#print query, topTerms	
		return topTerms
	
