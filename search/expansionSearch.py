# -*- coding: utf-8 -*-
import sys
from search.searchIndex import SearchIndex
from entity.catThesExpansion import CatThesExpansion
from entity.catWalkExpansion import CatWalkExpansion
from entity.termVector import TermVector
from queryLog import getSessionWithNL, getSessionWithXML
from entity.category.categoryManager import CategoryManager
from entity.dexter import Dexter
from entity.ranker import Ranker
from utils.coOccurrence import CoOccurrence
from utils.coOcManager import CoOcManager
from tasks.taskExpansion import TaskExpansion
#from entity.category.catSubManager import CategorySubtopicManager
from randomwalk.randomWalk import RandomWalk
from utils import getDocumentText, loadQueryList
import ast
#from nltk.stem import porter
'''
argv[1] = Session file
argv[2] = index folder
argv[3] = vector file / cat query folder / wikiIndex / (outfolder)
argv[4] = category phrase folder / topic folder / queryIndex
argv[5] = category Co-Occurrence file / term vector file
arg[6] = Task index
'''
def main(argv):
	#open the index
	searcher = SearchIndex(argv[2])
	searcher.initializeAnalyzer()
	outFolder = argv[3];
	#output file
	oFile1 = open(outFolder+'/baseline_11.RL1','w')
	oFiles = {};
	
	
	#category vector
	#catManage = CategoryManager(argv[3],argv[4])
	#catManage = CategorySubtopicManager(argv[3],argv[4])
	
	#ipaddress = 'localhost'
	#dexter object
	#tagURL = 'http://'+ipaddress+':8080/rest/annotate'
	#catURL = 'http://'+ipaddress+':8080/rest/graph/get-entity-categories'
	#dexter = Dexter(tagURL,catURL)
	
	#ranker
	#ranker = Ranker()
	
	#load the Category co-occurrence bit
	#catCoMan =	CoOcManager(argv[5],CoOccurrence(),' ')

	
	#expansion
	#entExp = CatThesExpansion(dexter, catManage, ranker,catCoMan)
	#entTermVect = TermVector(argv[6])
	#catTermVect = TermVector(argv[7])
	#dexter  = None
	#entExp = CatWalkExpansion(dexter, catManage, ranker,termVect)
	
	#taskExpansion
	#taskExp = TaskExpansion(argv[6],ranker, 50)
	#taskExp50 = TaskExpansion(argv[5],ranker,50)
	#taskExp100 = TaskExpansion(argv[6],ranker,100)
	#taskInd = argv[6][argv[6].rfind('/')+1:]
	#randomWalk
	#randWalk = RandomWalk(argv[3],argv[4],ranker)
	#randWalk = RandomWalk(catManage,catCoMan,entTermVect, catTermVect,ranker)
	
	#result String
	#entFile = {}
	#randFile = {}
	#task50File = {}
	#task100File = {}
	#porter1 = porter.PorterStemmer()
	#resStringAll = {}
	
	
	
	#query key terms
	queryList = loadQueryList(argv[4]);
	
	#viewedFileFolder =  argv[5]
	i=0
	for session, viewDocs, clickDocs in getSessionWithXML(argv[1]):
		i+=1
		query = session[0].strip();
		if query in queryList:
			for entry , terms in queryList[query].items():
				if entry not in oFiles:
					oFiles[entry] = open(outFolder+'/'+entry+'.RL1','w');
				docList = searcher.getTopDocumentsWithExpansion(session[0],terms,1000,'content','id')
				'''k = 1
				for dtuple  in docList:
					oFiles[entry].write(str(i)+' Q0 '+dtuple[0]+' '+str(k)+' '+str(round(dtuple[1],2))+' '+entry+'\n')
					k +=1
				'''
			
			docList = searcher.getTopDocuments(query,1000,'content','id');
			k =1;
			for dtuple  in docList:
				oFile1.write(str(i)+' Q0 '+dtuple[0]+' '+str(k)+' '+str(round(dtuple[1],2))+' baseline\n')
				k+=1;
		
		
		##get max cat terms
		#randExpTerms = randWalk.expandText(query,50)
		'''lastQueryIndex = len(session) - 2
		
		if lastQueryIndex > -1:
			docText = ''
			#print viewDocs[lastQueryIndex]
			for entry in viewDocs[lastQueryIndex][:5]:
				#print session[lastQueryIndex], 'docs',entry, len(docText)
				docText += getDocumentText(entry, viewedFileFolder).lower()+' '
			
			#print clickDocs[lastQueryIndex]
			clickText = ''
			for entry in clickDocs.values():
				#print session[lastQueryIndex], 'click',entry,  len(docText)
				for doc in entry:
					clickText += getDocumentText(doc,viewedFileFolder).lower()+' '
			
			#print
			randTerms = randWalk.expandLastWithSession(session,docText, clickText,50 );
			#docList = searcher.getTopDocumentsWithExpansion(query,entExpTerms,1100,'content','id')
			for qtype, terms in randTerms.iteritems():
				if qtype not in randFile:
					randFile[qtype] = open(argv[6]+str(qtype)+'.RL2','w')
				#k=1
				docList = searcher.getTopDocumentsWithExpansion(session[-1],terms,1100,'content','id')
				k = 1
				for dtuple  in docList:
					randFile[qtype].write(str(i)+' Q0 '+dtuple[0]+' '+str(k)+' '+str(round(dtuple[1],2))+' rand\n')
					k +=1
		'''	
			
		'''
		#if query in querySpotDict:
		#entExpTerms = entExp.expandText(query,1, 50) #,querySpotDict[query])
			#randExpTerms = randWalk.expandTextWithStep(query,25,55,25,querySpotDict[query])
			#for noT , entry in randExpTerms.iteritems():
			#	if noT not in randFile:
			#		randFile[noT] = open(argv[9]+str(noT)+'.RL1','a')
		#k=1
			#	print 'RWQuery\t',i,'\t',noT,'\t',query,'\t',entry
		#docList = searcher.getTopDocumentsWithExpansion(query,entExpTerms,1100,'content','id')
		#for dtuple  in docList:
		#	oFile2.write(str(i)+' Q0 '+dtuple[0]+' '+str(k)+' '+str(round(dtuple[1],2))+' ent\n')
			#randFile[noT].write(str(i)+' Q0 '+dtuple[0]+' '+str(k)+' '+str(round(dtuple[1],2))+' ent\n')
			
		#	k+=1
		#entExpTerms = entExp.expandText(query,1,1)
		#k=0
		#docList = searcher.getTopDocumentsWithExpansion(query,entExpTerms,2000,'content','id')
		#for dtuple  in docList:
		#	oFile2.write(str(i)+' Q0 '+dtuple[0]+' '+str(k)+' '+str(round(dtuple[1],2))+' eexpansion_1_5\n')
			#resStringAll[noT]+=str(i)+' Q0 '+dtuple[0]+' '+str(k)+' '+str(round(dtuple[1],2))+' probExpansion_1_'+str(noT)+'\n'
		#	k+=1
			
		
		#taskExpTerms = taskExp100.expandText(query,50)
		#for noT , entry in taskExpTerms50.iteritems():
		#	if noT not in entFile:
		#		task50File[noT] = open('task50_11_'+str(noT)+'.RL1','w')
		#k=1
		#docList = searcher.getTopDocumentsWithExpansion(query,taskExpTerms,1100,'content','id')
		#for dtuple  in docList:
			#entFile[noT].write(str(i)+' Q0 '+dtuple[0]+' '+str(k)+' '+str(round(dtuple[1],2))+' task1\n')
		#	oFile3.write(str(i)+' Q0 '+dtuple[0]+' '+str(k)+' '+str(round(dtuple[1],2))+' task1\n')
		#	k+=1
		
		
		taskExpTerms100 = taskExp100.expandTextWithStep(query,25,55,25)
		for noT , entry in taskExpTerms100.iteritems():
			if noT not in task100File:
				task100File[noT] = open(taskInd+'_100_11_'+str(noT)+'.RL1','w')
			k=1
			print 'TQuery\t',i,'\t',noT,'\t',query,'\t',entry
			docList = searcher.getTopDocumentsWithExpansion(query,entry,2000,'content','id')
			for dtuple  in docList:
				task100File[noT].write(str(i)+' Q0 '+dtuple[0]+' '+str(k)+' '+str(round(dtuple[1],2))+' task2\n')
				k+=1
		'''	
		#taskExpTerms = taskExp.expandText(query,5)
		#k=0
		#docList = searcher.getTopDocumentsWithExpansion(query,taskExpTerms,2000,'content','id')
		#for dtuple  in docList:
			#oFile3.write(str(i)+' Q0 '+dtuple[0]+' '+str(k)+' '+str(round(dtuple[1],2))+' texpansion_1_5\n')
			#k+=1
		
		#randExpTerms = randWalk.expandText(query,5)
		
		
		#k=0
		#docList = searcher.getTopDocumentsWithExpansion(query,randExpTerms,2000,'content','id')
		#for dtuple  in docList:
		#	resString4+=str(i)+' Q0 '+dtuple[0]+' '+str(k)+' '+str(round(dtuple[1],2))+' texpansion_1_5\n'
		#	k+=1
		#get top 3 cat terms
		#expansionTerms = entExp.expandText(query,3,5)
	#for entry, string in resStringAll.iteritems():
	#	oFile2 = open('probExp_11_'+str(entry)+'.RL1','w')
	#	oFile2.write(string)
	#oFile1.close()
	#for entry, fileP in randFile.iteritems():
	#	fileP.close()
	
	#for entry, fileP in task100File.iteritems():
	#	fileP.close()
	
	#oFile1.close()	
	#oFile2.close()	
	#oFile3.close()
	#load the queries
	#oFile1.write(resString1)
	#oFile4.write(resString4)
	#oFile4.close()
	for entry, oFile in oFiles.iteritems():
		oFile.close()
	searcher.close()
	
'''
def getWalkExpansion(query):
def getTaskExpansion(query):
'''


if __name__ == '__main__':
	main(sys.argv)
