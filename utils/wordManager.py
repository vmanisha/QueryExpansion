# -*- coding: utf-8 -*-#
from word import Word;
class WordManager:
	
	
	def __init__(self,fileName,isIndex):
		self.wordFeat = {};
		if not isIndex:
			self.loadFeatures(fileName);
		else:
			self.loadFeaturesFromIndex(fileName);
	
	def loadFeatures(self,fileName,wfilter=None):
		for line in open(fileName,'r'):
			line = line.strip().lower();
			split = line.split('\t');
			term = split[0].strip();
			if (not wfilter) or (term in wfilter):
				if term not in self.wordFeat:
					self.wordFeat[term] = Word(term,'');#line.strip().lower());
					
				for entry in split[1:]:
					#entry = entry.replace('https:','').strip();
					try:
						fsplit = entry.rsplit(':',1);
						name = fsplit[0];
						freq = round(float(fsplit[-1]),4);
						if name[0] == 'e':
							self.wordFeat[term].updateEntStats(name[2:],freq);
						elif name[0] == 'c':
							self.wordFeat[term].updateCatStats(name[2:],freq);
						else:
							self.wordFeat[term].updateURLStats(name[2:],freq);
					except:
						if len(entry) > 1 :
							print entry;
		print len(self.wordFeat);
	
	#def loadFeaturesFromIndex(self,indexPath):
		
	#def getEntCatScore(self, ent, cat, term):
	
	
	def hasWord(self, word):
		if word in self.wordFeat:
			return True;
		return False;
		
	def getWordFeat(self, word):
		if word in self.wordFeat:
			return self.wordFeat[word];
		else:
			return {};
			
	def getCosine(self, word1, word2):
		
		if word1 in self.wordFeat and word2 in self.wordFeat:
			return self.wordFeat[word1].getCosine(self.wordFeat[word2]);
		else:
			return 0.0, 0.0, 0.0;
	
	def getEntCosine(self, word1, word2):
		if word1 in self.wordFeat and word2 in self.wordFeat:
			return self.wordFeat[word1].getEntCosine(self.wordFeat[word2]);
		else:
			return 0.0;
	
	def getCatCosine(self, word1, word2):
		if word1 in self.wordFeat and word2 in self.wordFeat:
			return self.wordFeat[word1].getCatCosine(self.wordFeat[word2]);
		else:
			return 0.0;
	
	def getUrlCosine(self, word1, word2):
		if word1 in self.wordFeat and word2 in self.wordFeat:
			return self.wordFeat[word1].getUrlCosine(self.wordFeat[word2]);
		else:
			return 0.0;
	
	def getEntities(self, word):
		if word in self.wordFeat:
			return self.wordFeat[word].getEntities();
		
		else:
			return {};
