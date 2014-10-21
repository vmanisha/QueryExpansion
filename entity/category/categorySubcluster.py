# -*- coding: utf-8 -*-
class CategorySubcluster:
	
	def __init__(self,fileName):
		self.subClusters = {};
		self.phraseCount = 0.0;
		self.uniquePhrases = 0.0;
		self.centers = {};
		# id : {p:count},
		for line in open(fileName, 'r'):
			split = line.split('\t');
			try:
				cid = int(split[0].strip());
				if cid not in self.subClusters:
					self.subClusters[cid] = {};
					
				self.centers[cid] = split[1].strip();
				
				words = split[3].strip().split(' ');
				for entry in words:
					wsplit = entry.split(':');
					count = float(wsplit[1]);
					self.subClusters[cid][wsplit[0]] = count;
					self.phraseCount+= count;
					self.uniquePhrases+= 1.0;
					
			except:
				if 'NA' not in line:
					print 'ERROR parsing ',line;
	
	def getPhrases(self):
		toSend = [];
		for phraseDict in self.subClusters.values():
			toSend.append(phraseDict.items());
		return toSend;

	def getPhraseSet(self):
		toSend = set();
		for phraseDict in self.subClusters.values():
			for entry in phraseDict.keys():
				toSend.add(entry);
		return toSend;

	def getPhraseProb(self,phrase):
		#2 types one in subcluster
		for cid in self.subClusters.keys():
			if phrase in self.subClusters[cid]:
				#print self.subClusters[cid];
				total = sum(self.subClusters[cid].values());
				return self.subClusters[cid][phrase]/total;
		#the other in whole file

	def getSubclusters(self):
		return self.subClusters.items();
			