# -*- coding: utf-8 -*-

from utils import stopSet
from queryLog import hasAlpha
import gensim.utils
from gensim import models,corpora


import os
import sys
import logging

class CatSubtopic:
	
	def __init__(self):
		self.model = None
		self.dictionary = None
		
	def findTopics(self, fileName):
		document = []
		for line in open(fileName,'r'):
			line = line.strip()
			#treat it as a document
			split = line.split()
			document.append([entry for entry in split if entry not in stopSet \
			 and len(entry) > 2 and hasAlpha(entry) ])
		all_tokens = sum(document, [])
		tokens_once = set(word for word in set(all_tokens) \
			if all_tokens.count(word) == 1)
		texts = [[word for word in text if word not in tokens_once]	for text in document]
		if len(texts) > 30:
			self.dictionary = corpora.Dictionary(texts)		
			corpus = [self.dictionary.doc2bow(text) for text in texts]
			toUse = fileName.replace('(','')
			toUse = toUse.replace(')','')
			toUse = toUse.replace('\'','')
			toUse = toUse[toUse.rfind('/')+1:-4]
			
			#self.model = models.ldamallet.LdaMallet('/home/manisha/libraries/mallet-2.0.7/bin/mallet',\
			# corpus, num_topics=30, id2word=self.dictionary,\
			# prefix='/home/manisha/proj_workspace/Aol-Logs/catDexterTopics/tmp/'+toUse)
			
			self.model = models.ldamodel.LdaModel(corpus, id2word=self.dictionary, num_topics=30)
			
			#print 'Topics : '
			#print self.model.show_topics(topics = 30,topn = 50)


	def hasModel(self):
		if self.model:
			return True
		return False	
	def writeTopics(self, fileName):
		if self.model:
			self.model.save(fileName)
	
	def writeCorpus(self, fileName):
		#corpora.MmCorpus.serialize(fileName, self.corpus)
		if self.dictionary:
			self.dictionary.save(fileName)
		
	def loadTopics(self,fileName):
		#self.model = models.ldamallet.LdaMallet.load(fileName)
		self.model = models.ldamodel.LdaModel.load(fileName)
	
	def loadCorpus(self,fileName):
		self.dictionary = corpora.Dictionary.load(fileName)
		
	def getSim(self,text):
		maxId = -1
		maxScore = -1
		bow = None
		#print text
		if self.dictionary:
			bow = self.dictionary.doc2bow(gensim.utils.simple_preprocess(text))
		
		for stuple in self.model[bow]:
			if stuple[1] > maxScore:
				maxScore = stuple[1]
				maxId = stuple[0]
		return maxId, maxScore
	
	def getTopWords(self,topicId,num):
		return self.model.print_topic(topicId, topn=num)
		

def main(argv):
	#load the file
	#find the subtopics
	#write the file
	if not os.path.exists(argv[2]):
		os.mkdir(argv[2])
		os.mkdir(argv[2]+'/topics')
		os.mkdir(argv[2]+'/corpus')
		
	for ifile in os.listdir(argv[1]):
		catSub = CatSubtopic()
		#catSub.findTopics(argv[1]+'/'+ifile)
		#catSub.writeTopics(argv[2]+'/topics/'+ifile[:ifile.rfind('.')]+'.tp')
		#catSub.writeCorpus(argv[2]+'/corpus/'+ifile[:ifile.rfind('.')]+'.mm')
		
		#print catSub.getSim('world war two')
		catSub.loadCorpus(argv[2]+'/corpus/'+ifile[:ifile.rfind('.')]+'.mm')
		catSub.loadTopics(argv[2]+'/topics/'+ifile[:ifile.rfind('.')]+'.tp')
		topId, score =  catSub.getSim('world war two')
		print 'Topic ::::', topId, 'SCORE ::: ',score
		string = catSub.getTopWords(topId,5)
		print 'WHAT! ', string
		
		
if __name__ == '__main__':
	logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
	main(sys.argv)
		
	
