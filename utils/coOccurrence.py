# -*- coding: utf-8 -*-
import math

class CoOccurrence:

	termId = {}
	idTerm = {}
	
	def __init__(self):
		self.termTermTotal = 0.0	
		self.termTotal = 0.0
		self.termFreq = {}
		self.termTermFreq = {}
		
	def updateTermStats(self,term,val):
		self.termFreq[term] = self.termFreq.setdefault(term,0.0) + val
	
	
	def updateStatsFromList(self, tlist, toKeep):
		#print tlist
		for i in range(len(tlist)-1):
			for j in range(i+1,len(tlist)):
				if tlist[i] in toKeep and tlist[j] in toKeep:
					self.updateStats(tlist[i],tlist[j],1.0)
		#print tlist, self.termFreq
	
	def getUniqueTermCount(self):
		return len(self.termTotal)
		
	def updateStats(self,term1, term2,val):
		i, j = self.orderTerms(term1,term2)	
		#i = term1
		#j = term2
		
		self.updateTermStats(i,val)
		self.updateTermStats(j,val)
		if i not in self.termTermFreq:
			self.termTermFreq[i] = {}
		
		if j not in self.termTermFreq:
			self.termTermFreq[j] = {}
		
		self.termTermFreq[i][j] = self.termTermFreq[i].setdefault(j,0.0) + val
		self.termTermFreq[j][i] = self.termTermFreq[j].setdefault(i,0.0) + val
		self.termTermTotal += val
			
	def orderTerms(self,term1,term2):
		i = term1
		j = term2
		
		if term1 > term2:
			i = term2
			j = term1
			
		m = n = -1
		try:
			m = self.termId[i]
		except:
			m = len(self.termId)
			self.termId[i] = len(self.termId)
			self.idTerm[len(self.idTerm)] = i
			
			
		try:
			n = self.termId[j]
		except:
			n = len(self.termId)
			self.termId[j] = len(self.termId)
			self.idTerm[len(self.idTerm)] = j
			
			
		#print term1, term2, m, n, self.termId, self.idTerm
		return m, n
	
	def getUniqueTerms(self):
		return self.termId.keys()
		
	def setTermTotal(self):
		self.termTotal = sum(self.termFreq.values())
		
	def getPMI(self,term1, term2,thresh):
		#dont know the
		i , j = self.orderTerms(term1,term2)
		hasi = i in self.termTermFreq
		hasj = j in self.termTermFreq
		num=den=0.0
		#print term1, term2,
		if hasi:
			if j in self.termTermFreq[i]:
				if self.termTermFreq[i][j] < thresh:
					return 0.0
				num = self.termTermFreq[i][j]/self.termTermTotal
				den = (self.termFreq[i]/self.termTotal)*(self.termFreq[j]/self.termTotal)
				#print 'Num ij ',self.termTermFreq[i][j],self.termTermTotal,
				#print 'Den ij ',self.termFreq[i], self.termFreq[j], self.termTotal
			else:
				return 0.0	
		elif hasj:
			return 0.0
		else:
			#print 'Num ',self.termTermTotal, 'Den ',self.termTotal
			return 0.0#math.log((1.0/self.termTermTotal)/math.pow((1.0/self.termTotal),2))
		
		return math.log(num/den)
		
	#P(term2|term1)
	def getProb(self,term2, term1):
		
		i = term1
		j = term2
		
		if i in self.termTermFreq:
			if j in self.termTermFreq[i]:
				return self.termTermFreq[i][j]/sum(self.termTermFreq[i].values())
			else:
				return 0.0#1.0/sum(self.termTermFreq[i].values())
		else:
			return 0.0 # 1.0/ self.termTotal
			
	def writeTermCo(self,fileName):	
		#write the totals first
		oFile = open(fileName, 'w')
		for i, eDict in self.termTermFreq.iteritems():
			word1 = self.idTerm[i]
			for j,freq in eDict.iteritems():
				word2 = self.idTerm[j]
				oFile.write(word1+' '+word2+' '+str(freq)+'\n')
		oFile.close()

	def toStringList(self):	
		#write the totals first
		sList = []
		for i, eDict in self.termTermFreq.iteritems():
			word1 = self.idTerm[i]
			for j,freq in eDict.iteritems():
				word2 = self.idTerm[j]
				sList.append(word1+' '+word2+' '+str(freq))
		return sList
	
	
	def getNeighbours(self, term):
		tid = None
		if term in self.termId:
			tid = self.termId[term]
		
		if tid in self.termTermFreq:
			neigh = self.termTermFreq[tid]
			toReturn = []
			for entry in neigh:
				toReturn.append(self.idTerm[entry])
			return toReturn;
		
		return None;
	
	#def loadTermCo(self,fileName):
	
		
		