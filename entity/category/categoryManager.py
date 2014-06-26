# -*- coding: utf-8 -*-
from entity.category import getCats, loadCategoryVector
from entity.category import Category

class CategoryManager:
	
	def __init__(self, vectFile, catDir):
		self.catFileDict = getCats(catDir)
		self.catVectors = loadCategoryVector(vectFile)
		self.catObjDict = {}
	
	def getCategoryObject(self, cat):
		if self.loadCategoryObject(cat):
			return self.catObjDict[cat]
	
		return None
	
	def loadCategoryObject(self,cat):
		if cat not in self.catObjDict:
			if cat in self.catFileDict:
				self.catObjDict[cat] = Category.Category(self.catFileDict[cat])
				return True
			else:
				return False
		return True
		
	def getPhrases(self, cat):
		if self.loadCategoryObject(cat):
			return self.catObjDict[cat].getPhrases()
		
		return {}
			
	def getTotalPhraseCount(self,cat):
		if self.loadCategoryObject(cat):
			return self.catObjDict[cat].getTotalPhraseCount()
		return 0
	
	def getPhraseSet(self, cat):
		if self.loadCategoryObject(cat):
			return self.catObjDict[cat].getPhraseSet()
		return set('')
		
	def getPhraseProb(self,cat,iphrase):
		if self.loadCategoryObject(cat):
			return self.catObjDict[cat].getPhraseProb(iphrase)
		return 0.0001
		
	def getVector(self,cat):
		if cat in self.catVectors:
			return self.catVectors[cat]
		return {}
		