# -*- coding: utf-8 -*-
from entity.category import getCats, getCatsWithType
from entity.category.categorySubtopics import CatSubtopic
import sys

class CategorySubtopicManager:
	
	catQueryFileDict = {}
	catTopicFileDict = {}
	catDictFileDict = {}
	
	catSubtopicObjDict = {}
	
	topicDir = 'topics/'
	dictDir = 'corpus/'
	
	tFolder = None
	def __init__(self,queryFolder,topicFolder):
		#make list of cat - query file
		self.catQueryFileDict = getCats(queryFolder)
		#make the list of topic files
		self.tFolder = topicFolder
		self.catTopicFileDict = getCatsWithType(topicFolder+'/'+self.topicDir,'.tp')
		self.catDictFileDict = getCats(topicFolder+'/'+self.dictDir)
		#print len(self.tFolder)
		#print len(self.catTopicFileDict)
		#print len(self.catDictFileDict)
	
	def loadCatTopics(self, category):
		
		print category, category not in self.catSubtopicObjDict, len(self.catSubtopicObjDict)
		print category, category not in self.catDictFileDict, len(self.catDictFileDict)
		if category not in self.catSubtopicObjDict:
			if category not in self.catTopicFileDict:
				#find the topics using Query file dict
				catSub = CatSubtopic()
				catSub.findTopics(self.catQueryFileDict[category])
				if catSub.hasModel():
					fName = self.catQueryFileDict[category]
					fName = fName[fName.find('/')+1:fName.rfind('.')]
					self.catTopicFileDict[category]=self.tFolder+'/'+self.topicDir+'/'+fName+'.tp'
					self.catDictFileDict[category]= self.tFolder+'/'+self.dictDir+'/'+fName+'.mm'
					catSub.writeTopics(self.catTopicFileDict[category])
					catSub.writeCorpus(self.catDictFileDict[category])
				
					self.catSubtopicObjDict[category] = catSub
			else:
				catSub = CatSubtopic()
				catSub.loadCorpus(self.catDictFileDict[category])
				catSub.loadTopics(self.catTopicFileDict[category])
				self.catSubtopicObjDict[category] = catSub
	
				
	def expandSet(self,text,category):
		self.loadCatTopics(category)
		if category in self.catSubtopicObjDict:
			catSub = self.catSubtopicObjDict[category]
			if catSub.hasModel():
				topId, score =  catSub.getSim(text)
				string = catSub.getTopWords(topId,15)
				return string
		return ''
	
	def getSim(self, text, category):
		self.loadCatTopics(category)
		if category in self.catSubtopicObjDict:
			catSub = self.catSubtopicObjDict[category]
			if catSub.hasModel():
				topId, score =  catSub.getSim(text)
				return topId, score
		return 0,0.0

def main(argv):
	catMan = CategorySubtopicManager(argv[1],argv[2])
	print catMan.catDictFileDict.keys()
	catMan.loadCatTopics('conventions_(meetings)')
	catMan.loadCatTopics('entertainment_events')
	catMan.loadCatTopics('conventions_(meetings)')

if __name__ == '__main__':
	main(sys.argv)
