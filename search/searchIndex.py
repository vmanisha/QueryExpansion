# -*- coding: utf-8 -*-
import sys
import ast
import lucene
from java.io import File
#from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.analysis.en import EnglishAnalyzer
from org.apache.lucene.analysis.util import CharArraySet
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.index import IndexReader
from org.apache.lucene.search.similarities import BM25Similarity
from org.apache.lucene.util import Version
#from lucene.collections import JavaSet
from utils import stopSet
from entity.ranker import Ranker

class SearchIndex:
	
	def __init__(self, indexPath):
		lucene.initVM(vmargs=['-Djava.awt.headless=true'])
		print  'lucene', lucene.VERSION

		#initialize the index
		self.INDEX_DIR =  indexPath #"Clue_Index"
		self.results = None
		self.searcher = IndexSearcher(DirectoryReader.open(SimpleFSDirectory(File(self.INDEX_DIR))
))
		
		self.searcher.setSimilarity(BM25Similarity())
	
    	
	def initializeAnalyzer(self):
		#self.analyzer = StandardAnalyzer(Version.LUCENE_CURRENT,JavaSet(stopSet))
		sSet = CharArraySet(Version.LUCENE_CURRENT, 0, True)
		for entry in stopSet:
			sSet.add(entry)
		self.stopSet = sSet
		#self.analyzer = EnglishAnalyzer(Version.LUCENE_CURRENT,sSet)
		self.analyzer = EnglishAnalyzer(Version.LUCENE_CURRENT)
	
	def getTopDocuments(self,query,limit,sfield,dfield):
		queryObj = QueryParser(Version.LUCENE_CURRENT,sfield,
                            self.analyzer).parse(query)
		print queryObj
		scoreDocs = self.searcher.search(queryObj, limit).scoreDocs
		print "%s total matching documents." % len(scoreDocs)
		self.results = scoreDocs
		rresults = []
		i = 0
		#reader = self.searcher.getIndexReader();
		#print type(reader)
		for scoreDoc in scoreDocs:
			doc = self.searcher.doc(scoreDoc.doc)
			rresults.append((doc.get(dfield),scoreDoc.score));
			#rresults.append(doc.get(dfield));#,scoreDoc.score))
			i+=1
			if i == limit:
				break
		return rresults
		#print 'path:', doc.get("URL"), 'name:', doc.get("id"), 'title:', doc.get("title")

	def getTopDocumentsWithExpansion(self,query,expTerms, limit,sfield,dfield):
		print expTerms
		query = query + ' '+' '.join('{0}^{1}'.format(x[0],round(x[1],2)) for x in expTerms)
		sSet = CharArraySet(Version.LUCENE_CURRENT, 0, True)
		for entry in expTerms:
			sSet.add(entry[0])
		
		analyzer = EnglishAnalyzer(Version.LUCENE_CURRENT,self.stopSet,sSet)
		
		queryObj = QueryParser(Version.LUCENE_CURRENT,sfield,
                            analyzer).parse(query)
		scoreDocs = self.searcher.search(queryObj, limit).scoreDocs
		print "%s total matching documents." % len(scoreDocs), queryObj
		self.results = scoreDocs
		rresults = []
		i = 0
		
		for scoreDoc in scoreDocs:
			doc = self.searcher.doc(scoreDoc.doc)
			rresults.append(doc.get(dfield));#,scoreDoc.score))
			i+=1
			if i == limit:
				break
		return rresults
		
	def getField(self,dfield, name,limit):
		toReturn = []
		i = 0
		for scoreDoc in self.results:
			doc = self.searcher.doc(scoreDoc.doc)
			toReturn.append((doc.get(dfield), doc.get(name)))
			i+=1
			if i == limit:
				break
		return toReturn
			
	def close(self):
		 del self. searcher


def main(argv):
	searcher = SearchIndex(argv[2])
	searcher.initializeAnalyzer()
	#oFile = {}
	for line in open(argv[1],'r'):
		split = line.strip().split(' ')
		did = split[2]
		print did
		for entry in searcher.getTopDocuments(did, 10, 'id','title'):
			print entry
		break;
		#qId = split[0]
		#lenth = int(split[1])
		#query = split[2]
		#terms = ast.literal_eval(split[-1])
		#rankr = Ranker()
		#sortedTerms = rankr.getTopK(terms, 50)
		#lenth = int(split[-1])
		'''for step in xrange(0,55,5):
			lenth = step
			if step == 0:
				lenth = 1
		'''
		'''if lenth > 0 and lenth < 60:
			if lenth not in oFile:
				oFile[lenth] = open(argv[3]+'_'+str(lenth)+'.RL1','w')
			docList = searcher.getTopDocumentsWithExpansion(query,terms[:lenth],2000,'content','id')
			k = 1
			for dtuple  in docList:
				oFile[lenth].write(qId+' Q0 '+dtuple[0]+' '+str(k)+' '+str(round(dtuple[1],2))+' prob\n')
				k+=1
		
	for i in oFile.keys():
		oFile[i].close()
	'''
	searcher.close()

if __name__ == '__main__':
	main(sys.argv)