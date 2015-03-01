import sys
import re
import time
from entity.category import getCats, loadPhrasesWithScore, loadCategoryVector
from queryLog import getSessionWithNL
from utils import get_cosine, SYMB, stopSet, getDictFromSet
import os, ast
from evaluate import addedAndRemovedTerms

def getStatsPerQuery(argv):
	tagURL = 'http://localhost:8080/rest/annotate'
	catURL = 'http://localhost:8080/rest/graph/get-entity-categories'

	catVector = loadCategoryVector(argv[3])
	f1Dict = getCats(argv[2])
	sFound = 0.0
	sTotal = 0.0
	eTotal = set()
	eRemov = set()		
	catFoundNoTerm = set()
	catNotFound = set()
	catTermFound = set ()
	catEntity = set()
	outfile = open('match_session_dom.txt','w')
	#categoryVectors = {}
	for session in getSessionWithNL(argv[1]):
		catCount = {}
		entCount = {}
		querySpotList =  {}
		for query in session:
			#find the entities in query
			try:
				spotDict = None #tagQueryWithDexter(query, tagURL,catURL)
				querySpotList[query] = spotDict
				for text in spotDict.keys():
					for entry in spotDict[text]['cat'].split():
						catCount[entry] = catCount.setdefault(entry,1) + 1
					entCount[text] = entCount.setdefault(text,1) + 1
			except Exception as err:
				print err
				#print 'SESSION', session, 'CATCOUNT', catCount, 'ENTCOUNT',entCount
		
		found = False
		if len(catCount) > 0:
			#find the dominant entity
			maxEnt = max(entCount.values())
			#sessionQueryMapping = {}
			for query, spotList in querySpotList.iteritems():
				matchl = spotList.keys()
				for entry in matchl:
					eTotal.add(entry)
					if entCount[entry] < maxEnt:
						spotList.pop(entry,None)
						print 'Removing spot', query,  entry
						eRemov.add(entry)
					else:
						#get the categories
						#catTermMatch = {}
						rquery = query.replace(entry,'')
						queryTerms = set(rquery.split())
						for cat in spotList[entry]['cat'].lower().split():
							catEntity.add(entry+'_'+cat)
							if cat in f1Dict:
								phrase1 = loadPhrasesWithScore(argv[2]+'/'+f1Dict[cat])
								pVector = catVector[cat]
								queryDict = getDictFromSet(queryTerms)
								pTotal = sum(phrase1.values())
								pset = set(phrase1.keys())
								sint = pset & queryTerms
								score = 0.0
								cscore = get_cosine(queryDict, pVector)
								
								for iphrase in sint:
									score +=phrase1[iphrase]/pTotal
								if len(queryTerms) > 0:
									score *= (1.0*len(sint))/len(queryTerms)
								
									
								if sint:
										
									outfile.write(query+'\t'+ entry+'\t'+cat+'\t'+str(cscore)+'\t'+ ', '.join(sint)+'\n')
									found = True
									catTermFound.add(entry+'_'+cat)
								else:
									outfile.write(query+'\t'+entry+'\t'+cat+'\t0\t0\n')
									catFoundNoTerm.add(cat+'_'+entry)
							else:
								outfile.write(query+'\t'+entry+'\t'+cat+'\t0\tNOT FOUND\n')
								catNotFound.add(cat+'_'+entry)
								
						#load the terms for category
								#check if these terms match
		if found:
			sFound += 1
		sTotal += 1 		
		outfile.write('\n')
		
	print 'Total Sessions ',sTotal
	print 'Sessions with dominant entity in AOL', sFound
	print '# Unique Entities', len(eTotal)
	print '# Removed Entities (non dominant)', len(eRemov)
	print '# no of entity types', len(catEntity)
	print '# no of entity types with terms match ', len(catTermFound)
	print '# no of entity types with no term match', len(catFoundNoTerm)
	print '# no of entity types with no match in AOL', len(catNotFound)	


def getStatsPerSession(catVector, f1Dict, argv):
	
	tagURL = 'http://localhost:8080/rest/annotate'
	catURL = 'http://localhost:8080/rest/graph/get-entity-categories'

	
	print 'Cats ',len(f1Dict)	
	#stats
	sStat = {'ef':0,'total':0,'aTerms':0 }
	#eStat = {'total':set(), 'remov':set()}
	catStat = {'nfTerm':set(), 'nf':set(), 'tf':set(), 'total':set()}
	outfile = open('match_session_'+str(argv[4])+'.txt','w')
	#categoryVectors = {}
	#load the session
	arTotal = 0.0
	apTotal = 0.0
	for session in getSessionWithNL(argv[1]):
		bQuery = session[0].lower()
		bQuery = re.sub(SYMB,' ',bQuery)
		bQuery = re.sub('\s+',' ',bQuery).strip()
		aTerms,rTerms = addedAndRemovedTerms(bQuery, session[1:])	
		arMax = 0.0
		apMax = 0.0
		try:
			spotDict = None#tagQueryWithDexter(bQuery, tagURL,catURL)
			time.sleep(1)
			if aTerms:
				sStat['aTerms'] +=1.0
				if len(spotDict) > 0:
					sStat['ef'] +=1.0
					print 'Found Entity \t', '\t'.join(session)
				for entry in spotDict.keys():
					rquery = bQuery.replace(entry,'')
					queryTerms = set(rquery.split())
					catList = spotDict[entry]['cat'].lower().split()
					#notFound, maxCat, rDict = getPrecRecall('avg',catList,f1Dict,catVector, queryTerms, argv[2])
					#print 'Avg', notFound, rDict
					notFound, maxCat ,rDict = getPrecRecall('max',catList,f1Dict,catVector, queryTerms, aTerms,int(argv[4]))
					print 'Max',bQuery, 'Ent',entry, 'Cat',maxCat, 'NFC',notFound, rDict
					nf=0
					for centry in catList:
						catStat['total'].add(centry+'_'+entry)
						if centry in notFound:
							catStat['nf'].add(centry+'_'+entry)
							nf+=1.0
						else:
							if rDict and len(rDict['qInt']) == 0 :	
								catStat['nfTerm'].add(centry+'_'+entry)
					if nf==len(catList):
						print 'For Query',bQuery,'With ent list',spotDict.keys(),'for ENT',entry,'No cat found'
				
					if rDict:
						#to choose the type with max values
						if arMax < rDict['aR']:
							arMax = rDict['aR']
						if apMax < rDict['aP']:
							apMax = rDict['aP']

						outfile.write(bQuery+'\t'+ entry+'\t'+str(rDict['qS'])+'\t'+ ', '.join(rDict['qInt'])+'\t'+', '.join(rDict['aInt'])+'\t'+str(rDict['aR'])+'\t'+str(rDict['aP'])+'\n')
			#else:
			#	outfile.write(bQuery+'\tNOT\tNOT\tNOT\tNO TERMS\n')
		except Exception as err:
			print 'SESSION WITH ERR',session, err, err.args
		if aTerms:
			print 'Prec ',argv[4], bQuery,'\t' , apMax
			for query in session[1:]:
				 outfile.write(query+'\tNIL\t0.0\tNIL\tNIL\t0.0\t0.0\n')
		
		sStat['total'] += 1 		
		outfile.write('\n')
		apTotal += apMax
		arTotal += arMax

	print 'Total Sessions ',sStat['total']
	print 'Sessions with entity in AOL', sStat['ef']
	print '# no of entity types', len(catStat['total'])
	#print '# no of entity types with terms match ', len(catStat['tf'])
	print '# no of entity types present but no qterm match', len(catStat['nfTerm'])
	print '# no of entity types not present in AOL', len(catStat['nf'])	
	if sStat['ef'] > 0:
		print  argv[4],'\t', 'Prec',apTotal/sStat['ef'],'Recall', arTotal/sStat['ef']
		print  argv[4],'\t', 'Prec',apTotal/sStat['aTerms'],'Recall', arTotal/sStat['aTerms']
	#tag the entity for first query
	#find the category -- with catVector and termScore
	#for each query find added terms, removed terms
	#count how many terms added are present in cat
	#count how many terms absent are present in cat


def getPrecRecall(opt,catList,f1Dict,catVector,queryTerms,aTerms,index):

	catScore = {}	
	maxQs = -1000
	maxCat = ''
	
	notFound = set()
	for cat in catList:
		if cat in f1Dict:
			catScore[cat] = {'aP':0.0,'aR':0.0,'qS':0.0,'qInt':set(),'aInt':set() }
			#phrase cat score	
			phrase1 = loadPhrasesWithScore(f1Dict[cat])
			pTotal = sum(phrase1.values())  #total no of terms in cat
			pset = set(phrase1.keys())	#unique phrases in cat
			qInt = pset & queryTerms	#no of query terms cat contains
			score = 0.0
			for iphrase in qInt:
				score +=phrase1[iphrase]/pTotal
			if len(queryTerms) > 0:
				score *= (1.0*len(qInt))/len(queryTerms)

			#cosine score
			queryDict = getDictFromSet(queryTerms)
			cVector = catVector[cat]
			cscore = get_cosine(queryDict, cVector)
			
			#total score
			catScore[cat]['qs'] = cscore + score	
			if maxQs < catScore[cat]['qs']:
				maxQs = catScore[cat]['qs']
				maxCat = cat
			
			sortP = sorted(phrase1.items(), reverse= True, key=lambda x :x[1])
			#print 'sorted' , sortP[0],sortP[1]
			apset = set(x[0] for x in sortP[0:index])	
			#print 'pSet ',apset
			
			aInt =  aTerms & apset
			catScore[cat]['aP'] = (1.0*len(aInt))/len(aTerms)	
			catScore[cat]['aR'] = (1.0*len(aInt))/len(apset)
			catScore[cat]['aInt'] = aInt
			catScore[cat]['qInt'] = qInt
		else:
			notFound.add(cat)

	if opt == 'max':
		if maxCat in catScore:
			return notFound, maxCat, catScore[maxCat]
		else:
			return notFound, None, {'aP':0.0,'aR':0.0,'qS':0.0,'qInt':set(),'aInt':set()}
			
	else:
		avgScore = {'aP':0.0,'aR':0.0,'qS':0.0,'qInt':set(),'aInt':set()}
		for entry, cdict in catScore.iteritems():
			avgScore['aP'] += cdict['aP']
			avgScore['aR'] += cdict['aR']
			avgScore['qS'] += cdict['qS']
			avgScore['qInt'] |= cdict['qInt']
			avgScore['aInt'] |= cdict['aInt']
		
		
		avgScore['aP'] /= len(catScore)
		avgScore['aR'] /= len(catScore)
		avgScore['qS'] /= len(catScore)
		
		return notFound, None, avgScore

	return notFound, None, None




#t = set (a , b , c , d , e)
#b = set (a, b) 	

def getCategoryCount(dirName):
	catCount = {}
	for fileName in os.listdir(dirName):
		for line in open(dirName+'/'+fileName, 'r'):
			split = line.split('\t');
			spotDict = ast.literal_eval(split[1]);
			for entity, edict in spotDict.items():
				catList = edict['cat'].split();
				for cat in catList:
					catCount[cat] = catCount.setdefault(cat,0.0)+ 1.0;
			
	for entry in sorted(catCount.items(), reverse = True, key = lambda x : x[1]):
		print entry;


def main(argv):
	
	#catVector = loadCategoryVector(argv[3])
	#f1Dict = getCats(argv[2]+'/list.txt')
	#for k in [1,3,5,10,20,30,40,50,60,100]:
		#argv[-1]=  str(k)
		#getStatsPerSession(catVector, f1Dict,argv)
	getCategoryCount(argv[1])

if __name__ == '__main__':
	main(sys.argv)
