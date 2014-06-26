# -*- coding: utf-8 -*-
from nltk.tokenize import word_tokenize
from nltk.collocations import BigramAssocMeasures, BigramCollocationFinder
from nltk import stem
from utils import stopSet
from queryLog import hasAlpha, hasWebsite
from Whoosh import loadIndex, loadCollector, loadQueryParser
from  sklearn.preprocessing import normalize
import numpy
import math
import re

from whoosh.collectors import TimeLimit

class RandomWalk:
	
	porter = stem.porter.PorterStemmer()
	biMeas = BigramAssocMeasures()
	
	def __init__(self,wikiIndexDir,queryIndexDir,rnker):
		self.network  = {}
		self.terms = set()
		self.ranker = rnker
		self.setSearcher(wikiIndexDir,queryIndexDir)		
	
	def setSearcher(self, wikiIndexDir, queryIndexDir):
		self.wIndex, self.wsearcher = loadIndex(wikiIndexDir,wikiIndexDir[wikiIndexDir.rfind('/')+1:])
		self.wtlc = loadCollector(self.wsearcher,2000,20)
		
		self.qIndex, self.qsearcher = loadIndex(queryIndexDir,queryIndexDir[queryIndexDir.rfind('/')+1:])
		self.qtlc = loadCollector(self.qsearcher,2000,20)
		
		self.qqp = loadQueryParser(self.qIndex,"session")
		self.wqp = loadQueryParser(self.wIndex,"content")
	
	def clearNetwork(self):
		self.network = {}
		self.terms = set()
		
	def updateNetwork(self,query,qp,searcher,tlc,field,ntype):
		q = qp.parse(unicode(query))
		totalText = ''
		total = 0.0
		tmin = -1000
		tmax = 1000
		
		try:
			searcher.search_with_collector(q, tlc)
		except TimeLimit:
			print '--LONG-- ',query
		
		results = tlc.results()
		for entry in results:
			totalText += entry[field] + ' '
		
		finder =  BigramCollocationFinder.from_words(word_tokenize(totalText))		
		#update the network	
		
		rList = finder.score_ngrams(self.biMeas.pmi)
		
		for rTuple in rList:
			total+= rTuple[1]
			if tmin > rTuple[1]:
				tmin = rTuple[1]
			if tmax < rTuple[1]:
				tmax = rTuple[1]
			
		for rTuple in sorted(rList,reverse = True , key = lambda x : x [1]):
			if (len(self.terms) < 3000  and finder.ngram_fd[rTuple[0]] > 2) or \
			((finder.ngram_fd[rTuple[0]] > 1.0 and rTuple[0][0] in query) or \
			 (rTuple[0][1] in query and len(self.terms) < 4000)):
			#if (len(terms) < 3000  and finder.ngram_fd[rTuple[0]] > 2) or (rTuple[0][0] in query or rTuple[0][1] in query and len(terms) < 4000):
				a = self.porter.stem(rTuple[0][0])
				if len(a) > 2 and hasAlpha(a) and a not in stopSet and not hasWebsite(a):
					if a not in self.network:
						self.network[a] = {}
						self.terms.add(a)
					b = self.porter.stem(rTuple[0][1])
					if len(b) > 2 and hasAlpha(b) and b not in stopSet and not hasWebsite(b):
						if b not in self.network[a]:
							self.network[a][b]  = {}
							self.terms.add(b)
						self.network[a][b][ntype] = self.network[a][b].setdefault(ntype,0.0) + ((rTuple[1]-tmin)/(tmax-tmin))
		
		print query, ntype, len(self.terms)		
	
	
	
	def normalizeNetworks(self):
		for i in self.network.keys():
			isum = sum(self.network[i].values())
			for j in self.network[i].keys():
				self.network[i][j]/=isum
	
	
	def combineNetwork(self,factor, rNetwork,ntype):
		for e1 , eDict in self.network.iteritems():
			if e1 not in rNetwork:
				rNetwork[e1] = {}
			for e2, tDict in eDict.iteritems():
				if e2 not in rNetwork:
					rNetwork[e2] = {}
				if ntype in tDict:
					#if ntype == 'query':
					#	print ntype, e1, e2, tDict
					rNetwork[e1][e2] = rNetwork[e1].setdefault(e2,0.0)+(factor*tDict[ntype])
					rNetwork[e2][e1] = rNetwork[e2].setdefault(e1,0.0)+(factor*tDict[ntype])
	
	
	def toMatrix(self, keySet , network):
		print 'Total Dim of Matrix ',len(keySet),'*', len(keySet)
		numArray = numpy.zeros((len(keySet),len(keySet)))
		for i in range(len(keySet)-1):
			for j in range(i+1,len(keySet)):
				try:
					numArray[i, j] = network[keySet[i]][keySet[j]]
					numArray[j, i] = network[keySet[i]][keySet[j]]
				except Exception as err:
					numArray[i,j] = 0.0
					numArray[j,i] = 0.0
	
		return normalize(numArray,norm='l2',axis=0)
			
			
	def setBackSmoothing(noTerms):
		global backSmooth
		backSmooth = 1.0/noTerms
		
	
	def walk(self,query):
	
		
		#self.updateNetwork(query,self.wqp,self.wsearcher,self.wtlc,'content','wiki')
		self.updateNetwork(query,self.qqp,self.qsearcher,self.qtlc,'session','query')	
		
		#calculate the mixtures at two stages
		#stage1 = {}
		stage2 = {}
		#self.combineNetwork(1.0,stage1,totalNetwork,'stem')
		self.combineNetwork(0.5,stage2,'query')
		#self.combineNetwork(0.5,stage2,'wiki')

		#convert into matrix for multiplication
		#totalDim = sorted(list(set(stage1.keys()) | set(stage2.keys())))
		totalDim = sorted(set(stage2.keys()))
		
		dim = len(totalDim)
		if dim > 0:
			#stage1Matrix = self.toMatrix(totalDim,stage1)
			#print 'STAGE1',stage1Matrix[0],stage1Matrix.shape
			stage2Matrix = self.toMatrix(totalDim,stage2)
			print 'STAGE2',stage2Matrix[0],stage2Matrix.shape
			
			backSmooth = 1.0/len(totalDim)
			stage3Matrix = numpy.zeros((dim,dim))
			stage3Matrix.fill(backSmooth)
			print 'STAGE3',stage3Matrix[0],stage3Matrix.shape
				
			alpha=0.80
			#matrix = ['stage2','stage2','stage2','stage2','stage2','stage2','stage2','stage2','stage3']
			matrix = ['stage2','stage2','stage2','stage2','stage3']
			totalSum = numpy.zeros((dim,dim))
			cK = numpy.ones((dim,dim))
			
			#start walk!
			for k in range(len(matrix)):
				print k, matrix[k]	
				#if matrix[k] == 'stage1':
				#	cK = numpy.dot(stage1Matrix,cK)
				if matrix[k] == 'stage2':
					cK = numpy.dot(stage2Matrix,cK)
				else:
					cK = numpy.dot(cK, stage3Matrix)
				print 'CK',cK[0]

				totalSum = totalSum + (math.pow(alpha,k)*cK)
			totalSum = totalSum * (1-alpha)
			
			#rank Terms
			qList = []
			terms = query.split()#getQueryTerms(query)
			for term in terms:
				stemed = self.porter.stem(term)
				if term in totalDim:
					qList.append(totalDim.index(term))
				elif stemed in totalDim:
					qList.append(totalDim.index(stemed))
				else:
					print 'ERROR dint find ' ,query, '\t',term, len(totalDim)
			
			termScore = {}
			for i in range(len(totalDim)):
				termScore[totalDim[i]] = 0.0
				for j in qList:
					if totalSum[i][j] > 0.0:
						termScore[totalDim[i]] += math.log(totalSum[i][j])
			
			for term in terms:
				termScore.pop(term,None)
				stemd = self.porter.stem(term)
				termScore.pop(stemd,None)
			#find the precision for different term sets
			#sortTerms = sorted(termScore.iteritems(),reverse =True , key = lambda x : x [1])
			return termScore
	
	def expandText(self,query, limit):
		self.clearNetwork()
		query = re.sub('\d+',' ',query)
		query = re.sub('\s+',' ',query).strip()
		
		terms = self.walk(query)
		scoredTerms = self.ranker.getTopKWithFilter(terms,limit,limit+10)
		print 'Query \t',query, '\t',scoredTerms
		return scoredTerms
		
	def expandTextWithStep(self,query, limit1,limit2,step):
		self.clearNetwork()
		query = re.sub('\d+',' ',query)
		query = re.sub('\s+',' ',query).strip()
		
		scoredTerms = {}
		
		terms = self.walk(query)
		if terms:
			for i in xrange(limit1,limit2,step):
				if i == 0:
					scoredTerms[i] = self.ranker.getTopKWithFilter(terms,i+1,i+50)
				else:
					scoredTerms[i] = self.ranker.getTopKWithFilter(terms,i,i+50)
		
				#print 'Query \t',query, '\t',i,'\t',scoredTerms[i]
		
		return scoredTerms
		
	