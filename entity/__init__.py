# -*- coding: utf-8 -*-
import ast, sys
from queryLog import getSessionWithXML;
from utils.coOcManager import CoOcManager;
from utils.coOccurrence import CoOccurrence;
from entity.category.categoryManager import CategoryManager;
from entity.dexter import Dexter;
from entity.ranker import Ranker;
from entity.category import loadCategoryVector;
from entity.catThesExpansion import CatThesExpansion;
from  entity.category.category import Category;
from entity.category.categorySubcluster import CategorySubcluster;
from nltk import stem;
from queryLog import normalize;

def getQueryWithEntities(fileName):
	stats = {}
	for line in open(fileName,'r'):
		split = line.strip().split('\t')
		#query = split[0]
		spotDict = ast.literal_eval(split[-1])
		slen = len(spotDict)
		if slen > 1:
			print line.strip()
			stats[slen] = stats.setdefault(slen,0.0) + 1.0
			
	print stats

def getEntities(fileName):
	stats = {}
	for line in open(fileName,'r'):
		split = line.strip().split('\t')
		#query = split[0]
		spotDict = ast.literal_eval(split[-1])
		for entity in spotDict.keys():
			stats[entity] = stats.setdefault(entity,0.0)+ 1.0
	
	for entity, score in stats.iteritems():
		print entity, '\t', score

def toTag(file1, file2):
	tagged = {};
	for line in open(file1,'r'):
		split = line.split('\t');
		query = split[0].strip();
		if query not in tagged:
			tagged[query] = 1.0;
	
	for line in open(file2,'r'):
		split= line.split('\t');
		query = split[0].strip();
		if query not in tagged:
			print query;
	

if __name__ == '__main__':
	argv = sys.argv
	#getEntities(argv[1])
	#toTag(argv[1],argv[2]);
	
	dexter = Dexter('tagURL','catURL',argv[6]);
	#load the Category co-occurrence bit
	catCoMan =	CoOcManager(argv[4],CoOccurrence(),' ')

	#category vector
	catVect = loadCategoryVector(argv[2]);
	catManage1 = CategoryManager(catVect,argv[3],Category);
	catManage2 = CategoryManager(catVect,argv[5],CategorySubcluster);
	
	#ranker
	ranker = Ranker()
	entExp1 = CatThesExpansion(dexter, catManage1, ranker,catCoMan);
	entExp2 = CatThesExpansion(dexter, catManage2, ranker,catCoMan);
	
	oFile1 = open(argv[1][:argv[1].rfind('.')]+'_ent.txt','w');
	oFile2 = open(argv[1][:argv[1].rfind('.')]+'_entSub.txt','w');
	i= 0;
	
	porter = stem.porter.PorterStemmer();
	
	for session, documents, clicks, cTitle, scontents in getSessionWithXML(argv[1]):
		query = session[0];
		cText = normalize(' '.join(cTitle[0]),porter);
		i+=1
		entStatus2, entExpTerms2 = entExp2.getTopSubclusters(query,cText,1,5);
		for entry, wlist in entExpTerms2.items():
			oFile2.write(str(i)+'\t'+query+'\t'+entry+'\t'+str(wlist)+'\n');
		
		noTerms = sum([len(entry) for entry in entExpTerms2.values()]);
		entStatus1, entExpTerms1 = entExp1.expandText(query,cText,1,noTerms);
		
		oFile1.write(str(i)+'\t'+query);	
		k=0;
		num = noTerms/5;
		for entry in entExpTerms1:
			oFile1.write('\t'+entry[0]);
			k+=1;
			if (num > 0 and k%num == 0) and k < noTerms:
				oFile1.write('\n'+str(i)+'\t'+query);
		oFile1.write('\n');	
	
	oFile1.close();
	oFile2.close();
	
