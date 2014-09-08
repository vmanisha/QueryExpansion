# -*- coding: utf-8 -*-
class CatStats:
	
	def __init__(self, cat1):
		self.freq = 0.0
		self.ent = {}
		self.coOcc = {}
		#self.clickQ = 0.0
		self.isEnt = 0.0
		self.category = cat1
	
	def updateEnt(self,entity, score):
		self.ent[entity] = self.ent.setdefault(entity, 0.0) + score
		
	def updateCoOcc(self,word):
		self.ent[word] = self.ent.setdefault(word, 0.0) + 1.0
		
	#def updateClick(self):
	#	self.clickQ+=1.0
		
	def updateIsEnt(self):
		self.isEnt= 1
	
	def updateFreq(self):
		self.freq += 1.0
		
	def getStats(self):
		return self.freq, self.clickQ, self.isEnt, self.ent, self.coOcc
		
	def string(self):
		return (self.freq, self.ent,self.coOcc, self.isEnt)
		
class Word:
	
	def __init__(self,w):
		self.catStats = {}
		self.word = w
		self.clickQ = 0.0
		
	def updateClick(self):
		self.clickQ = 1.0
		
	def updateStats(self, cats, isEnt, entities, terms, click):
		
		if click:
			self.updateClick()
		
		for cat in cats:
			if cat not in self.catStats:
				self.catStats[cat] = CatStats(cat)
			catObj = self.catStats[cat]
		
			if isEnt:
				catObj.updateIsEnt()
		
			catObj.updateFreq()
		
			for entity,score in entities.iteritems():
				catObj.updateEnt(entity,score)
		
			for term in terms:
				catObj.updateCoOcc(term)
		
	
	'''def getOtherStats(self,cat):
		"""Get avg and max stats from other categories"""
	'''
	
	def getCatStats(self,cat):
		if cat in self.catStats:
			return self.catStats[cat].getStats()
		else:
			return None
			
	def string(self):
		catString  = {}
		for cat, catObj in self.catStats.iteritems():
			catString [cat] = catObj.string()
		
		return str(self.clickQ)+'\t'+str(catString)
		
		