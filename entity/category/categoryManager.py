# -*- coding: utf-8 -*-
from entity.category import getCats, loadCategoryVector;
from entity.category.category import Category;
from entity.category.categorySubcluster import CategorySubcluster;
import sys;

class CategoryManager:
	
	def __init__(self, vectFile, catDir, cclass):
		self.catFileDict = getCats(catDir)
		self.catVectors = loadCategoryVector(vectFile)
		self.catObjDict = {}
		self.catClass = cclass;
	
	def getCategoryObject(self, cat):
		if self.loadCategoryObject(cat):
			return self.catObjDict[cat]
	
		return None
	
	def loadCategoryObject(self,cat):
		if cat not in self.catObjDict:
			if cat in self.catFileDict:
				self.catObjDict[cat] = self.catClass(self.catFileDict[cat]);
				#Category(self.catFileDict[cat])
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
	
	def getSubclusters(self, cat):
		#dictionary of lists. With inner lists containing (phrase, count) pair
		return self.catObjDict[cat].getSubclusters();

'''
catVector = vectFile
catPhraseDir = catDir
'''
def main(argv):
	#test the subclusters
	catMan = CategoryManager(argv[1],argv[2],CategorySubcluster);
	phrases = catMan.getPhrases('wine');
	print 'PHRASES ', len(phrases) ,phrases;
	phraseSet = catMan.getPhraseSet('workwear');
	print 'PHRASESET ', len(phraseSet), phraseSet;
	prob = catMan.getPhraseProb('wine','buy');
	print 'buy in wine',prob;
	
if __name__ == '__main__':
	main(sys.argv);