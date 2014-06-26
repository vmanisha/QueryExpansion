# -*- coding: utf-8 -*-
class Ranker:
	
	def __init__(self):
		self.id = 1
	
	def getTopK(self,terms, limit):
		total = sum(terms.values())*1.0
		tsorted = sorted (terms.items(),reverse = True , key = lambda x : x [1])
		#print 'TermSet Size',len(tsorted)
		
		result = []
		i = 0
		for entry in tsorted:
			result.append((entry[0],(entry[1]+1)/(total+1)))
			i +=1
			if i == limit:
				break
				
		return result	
	
	def getTopKWithFilter(self, terms, limit, limit2):
		tsorted = sorted (terms.items(),reverse = True , key = lambda x : x [1])
		result = {}
		i = 0
		for entry in tsorted:
			if entry[1] > 0:
				result[entry[0]]=entry[1]
			i +=1
			if i == limit2:
				break
				
		return self.getTopK(result,limit)