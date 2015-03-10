# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-

class ObjCoOccurrence:

	
	def __init__(self):
		self.termTotal = 0.0
		self.termFreq = {}
		self.termTermFreq = {}
		self.termTermTotal = 0.0
		
	def updateTermStats(self,term,val):
		self.termFreq[term] = self.termFreq.setdefault(term,0.0) + val
	
	
	def updateStatsFromList(self, obj, toKeep):
		for entry in toKeep:
			self.updateStats(obj,entry,1.0)
		
	
	def getUniqueTermCount(self):
		return len(self.termFreq)
					
	def updateStats(self,obj, term,val):
		self.updateTermStats(obj,val)
		if obj not in self.termTermFreq:
			self.termTermFreq[obj] = {}
		self.termTermFreq[obj][term] = self.termTermFreq[obj].setdefault(term,0.0) + val
		self.termTermTotal += val
			

	def setTermTotal(self):
		self.termTotal = sum(self.termFreq.values())
		
	#P(term2|term1)
	def getProb(self,i, j):
			
		if i in self.termTermFreq:
			if j in self.termTermFreq[i]:
				return self.termTermFreq[i][j]/sum(self.termTermFreq[i].values())
			else:
				return 0.0#1.0/sum(self.termTermFreq[i].values())
		else:
			return 0.0 #1.0/ self.termTotal
			
	def writeTermCo(self,fileName):	
		#write the totals first
		oFile = open(fileName, 'w')
		for i, eDict in self.termTermFreq.iteritems():
			
			for j,freq in eDict.iteritems():
				oFile.write(i+'\t'+j+'\t'+str(freq))
		oFile.close()

	def toStringList(self):	
		#write the totals first
		sList = []
		for i, eDict in self.termTermFreq.iteritems():
			for j,freq in eDict.iteritems():
				sList.append(i+'\t'+j+'\t'+str(freq))
		return sList
		
	#def loadTermCo(self,fileName):
	
		
		