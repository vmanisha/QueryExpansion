# -*- coding: utf-8 -*-
import sys
from search.searchIndex import SearchIndex
from entity.catThesExpansion import CatThesExpansion
from queryLog import getSessionWithXML, normalize;
from entity.category.categoryManager import CategoryManager
from entity.dexter import Dexter
from entity.ranker import Ranker
from utils.coOccurrence import CoOccurrence
from utils.coOcManager import CoOcManager
from tasks.taskExpansion import TaskExpansion
from entity.category.category import Category;
from entity.category.categorySubcluster import CategorySubcluster;
from plots import plotMultipleSys;
from measures import loadRelJudgements, findAvgPrec, findDCG;
from queryLog.coOccurExpansion import CoOccurExpansion;
from entity.category import loadCategoryVector;
from nltk import stem ;

'''
argv[1] = Session file
argv[2] = index folder
argv[3] = vector file / cat query folder / wikiIndex / (outfolder)
argv[4] = category phrase folder / topic folder / queryIndex
argv[5] = category cluster folder
argv[6] = category Co-Occurrence file / term vector file
argv[7] = dexter tagged file
argv[8] = relevance judgements
argv[9] = outFolder
'''
def main(argv):
	#open the index
	searcher = SearchIndex(argv[2])
	searcher.initializeAnalyzer()
	
	ipaddress = 'localhost'
	#dexter object
	tagURL = 'http://'+ipaddress+':8080/rest/annotate'
	catURL = 'http://'+ipaddress+':8080/rest/graph/get-entity-categories'
	dexter = Dexter(tagURL,catURL,argv[7]);
	
	
	#category vector
	catVect = loadCategoryVector(argv[3]);
	catManage1 = CategoryManager(catVect,argv[4],Category);
	catManage2 = CategoryManager(catVect,argv[5],CategorySubcluster);
	
	#load the Category co-occurrence bit
	catCoMan =	CoOcManager(argv[6],CoOccurrence(),' ')
		
	#ranker
	ranker = Ranker()
	
	#task extraction
	htcTask = TaskExpansion('Indexes/htcIndex',ranker,3000);
	qccTask = TaskExpansion('Indexes/qccIndex',ranker,3000);
	#taskK = argv[5][argv[5].rfind('/')+1:]
	
	#totalVocab = loadFileInList(argv[6]);
		
	#expansion
	entExp1 = CatThesExpansion(dexter, catManage1, ranker,catCoMan);
	entExp2 = CatThesExpansion(dexter, catManage2, ranker,catCoMan);
	#term expansion
	coOccExp = CoOccurExpansion(catCoMan,None ,ranker);
	
	rel, noRel = loadRelJudgements(argv[8]);
	
	outFolder = argv[9];
	
	#randomWalk
	#randWalk = RandomWalk(argv[3],argv[4],ranker)
	#randWalk = RandomWalk(catManage,catCoMan,entTermVect, catTermVect,ranker)
	
	#result String
	#query key terms
	#queryList = loadQueryList(argv[4]);
		
	plotMap = {'baseline':{},'ent':{}, 'entSub':{}, 'qccTask':{}, 'htcTask':{},'co':{}};
	plotNDCG = {'baseline':{},'ent':{}, 'entSub':{}, 'qccTask':{}, 'htcTask':{},'co':{}};

	#viewedFileFolder =  argv[5]
	i=0
	qMap = [];
	qNdcg = [];
	meth = 'baseline'
	oFile  = open(outFolder+'/baseline.RL1','w');
	covered = {};
	porter = stem.porter.PorterStemmer();
	for session, viewDocs, clickDocs, cTitle, cSummary in getSessionWithXML(argv[1]):
		i+=1
		query = session[0].strip();
		if i in rel and query not in covered:
			covered[query] = 1.0;
			docList = searcher.getTopDocuments(query,1000,'content','id');
			k = 1
			for dtuple  in docList:
				oFile.write(str(i)+' Q0 '+dtuple[0]+' '+str(k)+' '+str(round(dtuple[1],2))+' baseline\n');
				k +=1
			'''qmap = findAvgPrec(docList,rel[i],noRel[i]);
			dcg10, idcg10 = findDCG(docList[:10],rel[i]);
			#print dcg10, idcg10, rel[i].values();
			ndcg10 = 0.0;
			if idcg10 > 0:
				ndcg10 = dcg10/idcg10;
			qMap.append(qmap);
			qNdcg.append(ndcg10);
			oFile.write('ndcg10 '+str(i)+' '+str(ndcg10)+'\n');
			oFile.write('map '+str(i)+' '+str(qmap)+'\n');
			'''
		else:
			print 'No rel ', i, session[0];
	oFile.close();
	'''
	fmap = sum(qMap)/len(qMap);
	fnd = sum(qNdcg)/len(qNdcg);
	oFile.write('all map ' +str(fmap)+'\n');
	oFile.write('all ndcg10 '+str(fnd)+'\n');
	for val in range(0,55,5):
		plotMap[meth][val] = fmap;
		plotNDCG[meth][val] = fnd;
	oFile.close();
	'''
	
	'''
	i=0
	qMap = {};
	qNdcg = {};
	oFile = {};
	meth = 'co';
	covered = {};
	for session, viewDocs, clickDocs, cTitle, cSummary in getSessionWithXML(argv[1]):
		i+=1
		query = session[0].strip();
		
		if i in rel and query not in covered:
			covered[query] = 1.0;
			coExpTerms = coOccExp.expandTextWithStep(query,50,55,5);
			for noTerms, terms in coExpTerms.items():
				if noTerms not in qMap:
					qMap[noTerms] = [];	
					qNdcg[noTerms] = [];
				if noTerms not in oFile:
					oFile[noTerms]  = open(outFolder+'/'+meth+'_'+str(noTerms)+'.RL1','w');
				docList = searcher.getTopDocumentsWithExpansion(query,terms,1000,'content','id');
				qmap = findAvgPrec(docList,rel[i],noRel[i]);
				dcg10, idcg10 = findDCG(docList[:10],rel[i]);
				ndcg10 = 0.0;
				if idcg10 > 0:
					ndcg10 = dcg10/idcg10;
				qMap[noTerms].append(qmap);
				qNdcg[noTerms].append(ndcg10);
				oFile[noTerms].write('ndcg10 '+str(i)+' '+str(ndcg10)+' '+str(dcg10)+' '+str(idcg10)+'\n');
				oFile[noTerms].write('map '+str(i)+' '+str(qmap)+'\n');
		
	for entry, vlist in qMap.items():
		i = len(vlist);
		fmap = sum(vlist)/i;
		fnd = sum(qNdcg[entry])/i;
		print sum(vlist), len(vlist);
		oFile[entry].write('all map ' +str(fmap)+'\n');
		oFile[entry].write('all ndcg10 '+str(fnd)+'\n');
		plotMap[meth][entry] = fmap;
		plotNDCG[meth][entry] = fnd;
		oFile[entry].close();

	i=0
	qMap = {};
	qNdcg = {};
	oFile = {};
	meth = 'ent';
	covered = {};
	for session, viewDocs, clickDocs, cTitle, cSummary in getSessionWithXML(argv[1]):
		i+=1
		query = session[0].strip();
		cText = normalize(' '.join(cTitle[0]),porter);
		if i in rel and query not in covered:
			covered[query] = 1.0;
			entStatus1, entExpTerms1 = entExp1.expandTextWithStep(query,cText,1,50,55,5);
			for noTerms, terms in entExpTerms1.items():
				if noTerms not in qMap:
					qMap[noTerms] = [];	
					qNdcg[noTerms] = [];
				if noTerms not in oFile:
					oFile[noTerms]  = open(outFolder+'/'+meth+'_'+str(noTerms)+'.RL1','w');
				docList = searcher.getTopDocumentsWithExpansion(session[0],terms,1000,'content','id');
				qmap = findAvgPrec(docList,rel[i],noRel[i]);
				dcg10, idcg10 = findDCG(docList[:10],rel[i]);
				ndcg10 = 0.0;
				if idcg10 > 0:
					ndcg10 = dcg10/idcg10;
			
				qMap[noTerms].append(qmap);
				qNdcg[noTerms].append(ndcg10);
				oFile[noTerms].write('ndcg10 '+str(i)+' '+str(ndcg10)+' '+str(dcg10)+' '+str(idcg10)+'\n');
				oFile[noTerms].write('map '+str(i)+' '+str(qmap)+'\n');
		
	for entry, vlist in qMap.items():
		i = len(vlist);
		fmap = sum(qMap[entry])/i;
		fnd = sum(qNdcg[entry])/i;
		oFile[entry].write('all map ' +str(fmap)+'\n');
		oFile[entry].write('all ndcg10 '+str(fnd)+'\n');
		plotMap[meth][entry] = fmap;
		plotNDCG[meth][entry] = fnd;
		oFile[entry].close();
	
	i=0
	qMap = {};
	qNdcg = {};
	oFile = {};
	meth = 'entSub';
	covered = {};
	for session, viewDocs, clickDocs, cTitle, cSummary in getSessionWithXML(argv[1]):
		i+=1
		query = session[0].strip();
		cText = normalize(' '.join(cTitle[0]),porter);
		if i in rel and query not in covered:
			covered[query] = 1.0;
			entStatus2, entExpTerms2 = entExp2.expandTextWithStepAndSubcluster(query,cText,1,50,55,5);
			for noTerms, terms in entExpTerms2.items():
				if noTerms not in qMap:
					qMap[noTerms] = [];	
					qNdcg[noTerms] = [];
				if noTerms not in oFile:
					oFile[noTerms]  = open(outFolder+'/'+meth+'_'+str(noTerms)+'.RL1','w');
				docList = searcher.getTopDocumentsWithExpansion(session[0],terms,1000,'content','id');
				qmap = findAvgPrec(docList,rel[i],noRel[i]);
				dcg10, idcg10 = findDCG(docList[:10],rel[i]);
				ndcg10 = 0.0;
				if idcg10 > 0:
					ndcg10 = dcg10/idcg10;
				
				qMap[noTerms].append(qmap);
				qNdcg[noTerms].append(ndcg10);
				oFile[noTerms].write('ndcg10 '+str(i)+' '+str(ndcg10)+' '+str(dcg10)+' '+str(idcg10)+'\n');
				oFile[noTerms].write('map '+str(i)+' '+str(qmap)+'\n');
	
	for entry, vlist in qMap.items():
		i = len(vlist);
		fmap = sum(qMap[entry])/i;
		fnd = sum(qNdcg[entry])/i;
		oFile[entry].write('all map ' +str(fmap)+'\n');
		oFile[entry].write('all ndcg10 '+str(fnd)+'\n');
		plotMap[meth][entry] = fmap;
		plotNDCG[meth][entry] = fnd;
		oFile[entry].close();
		
	i=0
	qMap = {};
	qNdcg = {};
	oFile = {};
	meth = 'qccTask';
	covered = {};
	for session, viewDocs, clickDocs, cTitle, cSummary in getSessionWithXML(argv[1]):
		i+=1
		query = session[0].strip();

		if i in rel and query not in covered:
			covered[query] = 1.0;
			qccTaskTerms = qccTask.expandTextWithStep(query,50,55,5);
			for noTerms, terms in qccTaskTerms.items():
				if noTerms not in qMap:
					qMap[noTerms] = [];	
					qNdcg[noTerms] = [];
				if noTerms not in oFile:
					oFile[noTerms]  = open(outFolder+'/'+meth+'_'+str(noTerms)+'.RL1','w');
				docList = searcher.getTopDocumentsWithExpansion(session[0],terms,1000,'content','id');
				qmap = findAvgPrec(docList,rel[i],noRel[i]);
				dcg10, idcg10 = findDCG(docList[:10],rel[i]);
				ndcg10 = 0.0;
				if idcg10 > 0:
					ndcg10 = dcg10/idcg10;
				
				qMap[noTerms].append(qmap);
				qNdcg[noTerms].append(ndcg10);
				oFile[noTerms].write('ndcg10 '+str(i)+' '+str(ndcg10)+' '+str(dcg10)+' '+str(idcg10)+'\n');
				oFile[noTerms].write('map '+str(i)+' '+str(qmap)+'\n');
	
	for entry, vlist in qMap.items():
		i = len(vlist);
		fmap = sum(qMap[entry])/i;
		fnd = sum(qNdcg[entry])/i;
		oFile[entry].write('all map ' +str(fmap)+'\n');
		oFile[entry].write('all ndcg10 '+str(fnd)+'\n');
		plotMap[meth][entry] = fmap;
		plotNDCG[meth][entry] = fnd;
		oFile[entry].close();
		
	i=0
	qMap = {};
	qNdcg = {};
	oFile = {};
	meth = 'htcTask';
	covered = {};
	for session, viewDocs, clickDocs, cTitle, cSummary in getSessionWithXML(argv[1]):
		i+=1
		query = session[0].strip();

		if i in rel and query not in covered:
			covered[query] = 1.0;
			htcTaskTerms = htcTask.expandTextWithStep(query,50,55,5)
			for noTerms, terms in htcTaskTerms.items():
				if noTerms not in qMap:
					qMap[noTerms] = [];	
					qNdcg[noTerms] = [];
				if noTerms not in oFile:
					oFile[noTerms]  = open(outFolder+'/'+meth+'_'+str(noTerms)+'.RL1','w');
				docList = searcher.getTopDocumentsWithExpansion(session[0],terms,1000,'content','id');
				qmap = findAvgPrec(docList,rel[i],noRel[i]);
				dcg10, idcg10 = findDCG(docList[:10],rel[i]);
				ndcg10 = 0.0;
				if idcg10 > 0:
					ndcg10 = dcg10/idcg10;
				qMap[noTerms].append(qmap);
				qNdcg[noTerms].append(ndcg10);
				oFile[noTerms].write('ndcg10 '+str(i)+' '+str(ndcg10)+' '+str(dcg10)+' '+str(idcg10)+'\n');
				oFile[noTerms].write('map '+str(i)+' '+str(qmap)+'\n');
		
	for entry, vlist in qMap.items():
		i = len(vlist);
		fmap = sum(qMap[entry])/i;
		fnd = sum(qNdcg[entry])/i;
		oFile[entry].write('all map ' +str(fmap)+'\n');
		oFile[entry].write('all ndcg10 '+str(fnd)+'\n');
		plotMap[meth][entry] = fmap;
		plotNDCG[meth][entry] = fnd;
		oFile[entry].close();

	plotMultipleSys(plotMap,'No of Terms', 'MAP',outFolder+'/map.png','Retrieval MAP Plot');
	plotMultipleSys(plotNDCG,'No of Terms', 'NDCG@10',outFolder+'/ndcg10.png','Retrieval NDCG Plot');
	'''
	searcher.close();		
				

	
'''
def getWalkExpansion(query):
def getTaskExpansion(query):
'''


if __name__ == '__main__':
	main(sys.argv)
	
'''
lastQueryIndex = len(session) - 2
		
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
		
		
			
	
	for approach, docList in results.iteritems():
		app = approach[:approach.rfind('_')];
		ind = int(approach[approach.rfind('_')+1:]);
		if app not in plotMap:
			plotMap[app]={};
			plotNDCG[app] = {};
		plotMap[app][ind] = amap;
		plotNDCG[app][ind] = andcg;
'''	
	