import os
import sys
import re
import math
import ast
from utils import SYMB, stopSet
from queryLog import hasAlpha
#import nltk
from nltk.collocations import TrigramCollocationFinder
from nltk.collocations import BigramCollocationFinder
from nltk import stem


def getPhrases(fileName, biMeasure, triMeasure):
	i = 0
	for line in open(fileName,'r'):
		split = line.strip().split('\t')
		taskDict = ast.literal_eval(split[-1])
		taskTokenList = [x.split() for x in taskDict.keys()]
		#print taskTokenList
		finder = BigramCollocationFinder.from_documents(taskTokenList)
		finder.apply_freq_filter(3)
		finder3 = TrigramCollocationFinder.from_documents(taskTokenList)
		finder3.apply_freq_filter(3)
		#print len(taskDict), len(taskTokenList)
		string1 = ''
		for entry in finder.nbest(biMeasure.pmi,20):
			string1 += ' '.join(entry) + ',\t'
		string2 = ''	
		for entry in finder3.nbest(triMeasure.pmi,20):
			string1 += ' '.join(entry) + ',\t'
		
		print i,'\t',string1, '\t',string2
		i+=1
		
	

def getTfIdfWords(fileName):
	wordCatDict = {}
	catSet = set()
	for line in open(fileName,'r'):
		split = line.lower().strip().split('\t')
		split[-1] = split[-1].strip()
		try:
			entityDict = ast.literal_eval(split[-1])
			query = re.sub(SYMB, ' ',split[0]).strip()
			#get the query
			for match, entDict in entityDict.iteritems():
				cats = entDict["cat"]
				if len(cats) > 2:
					categories = cats.split()
					#rho = entDict["score"]
					qrep = query.replace(match,"_CAT_")
					qsplit = qrep.strip().split()
					for entry in qsplit:
						if entry not in wordCatDict:
							wordCatDict[entry] = {}
						for centry in categories:
							wordCatDict[entry][centry] = wordCatDict[entry].setdefault(centry,1) + 1.0
							catSet.add(centry)
		except Exception as err:
			print err, err.args

	totCat = len(catSet)
	print 'Word QueryLog tfIdf'
	#this will give the importance of word for the query corpus
	for entry , catDict in wordCatDict.iteritems():
		cidf =math.log(totCat/len(catDict)*1.0)
		tf = sum(catDict.values())
		tfIdf = tf*cidf
		print entry,tf, cidf, tfIdf

		
def getProtEntityPhrases(fileName,outDir):
	i = 0
	catQueries = {}
	string = ""
	catTotal = {}
	catMatch = {}
	i = 0
	
	
	porter = stem.porter.PorterStemmer()
	for line in open(fileName,'r'):
		split = line.lower().strip().split('\t')
		split[-1] = split[-1].strip()
		try:
			entityDict = ast.literal_eval(split[-1])
			query = re.sub(SYMB, ' ',split[0]).strip()
			#get the query
			nquery = query
			for match in entityDict.keys():
				nquery = nquery.replace(match,' ')
				
			for match, entDict in entityDict.iteritems():
				cats = entDict["cat"]
				if len(cats) > 2:
					categories = cats.split()
					#rho = entDict["score"]
					#qrep = query.replace(match," _CAT_ ")
					for cat in categories:
						if cat not in catQueries:
							catQueries[cat] = {}
							catTotal[cat] = 0.0
							catMatch[cat] = {}
						#if rho > 0.00001:
							#qsplit = qrep.strip().split('_CAT_')
						#qsplit = qrep.strip().split()
						qsplit = nquery.split()
						for qRep in qsplit:
							if len(qRep) > 2 and qRep not in stopSet and hasAlpha(qRep):
								qRep = porter.stem(qRep.strip())
							
								if qRep not in catQueries[cat]:
									catQueries[cat][qRep] = 0.0 #{"score":0.0 }
								#catQueries[cat][qRep]["score"] += 1.0
								catQueries[cat][qRep] += 1.0
								catMatch[cat][match] = 1.0 if match not in catMatch[cat] else catMatch[cat][match] + 1.0
								#catQueries[cat][qRep]["query"][query] = 1.0
								
								if catTotal[cat] < catQueries[cat][qRep]:
									catTotal[cat] = catQueries[cat][qRep]
								#if catTotal[cat] < catQueries[cat][qRep]["score"]:
								#	catTotal[cat] = catQueries[cat][qRep]["score"]
								
							
			i += 1
			if i % 100000 ==0:
				print i
		except Exception as err:
			print 'ERROR', line, err


			
	#for cat, queryDict in catQueries.iteritems():
	#	print queryDict["_TOTAL_"],"\t",cat, '\t', queryDict
	
	if not os.path.exists(outDir):
		os.mkdir(outDir)
	
	cqn = 0 #no of queries/phrase per category
	qn = 2	 #no of times query/phrase occurs in cat
	uqn = 2 #no of unique queries/phrase with occurance > qn
	mn = 15  #no of times this phrase match occured
	catPhraseTotal = {}
	catEntityTotal = {}

	for cat, queryDict in catQueries.iteritems():
		#match = {}
		if catTotal[cat] > cqn:
			#newCat = cat.replace(' ','_')
			string = ""
			cnt = 0
			catEntityTotal [cat] = 0.0
			catPhraseTotal [cat] = 0.0
			
			for entry in sorted(queryDict.items(), reverse = True,key = lambda x : x[1]):#x[1]['score']):
				#if entry[1]['score'] >= qn:
				if entry[1] >= qn:
					string+= entry[0]+'\t'+str(entry[1])+'\n'#+ '\t'+ str(entry[1]['query']) +'\n'
					catPhraseTotal[cat] +=1.0
					cnt += 1
			if cnt >= uqn:
				newCat = cat.replace('/','_')
				oFile = open(outDir+'/'+newCat+'_'+str(len(queryDict))+'.txt','w')
					
				for entry in sorted(catMatch[cat].items(),reverse=True, key = lambda x : x[1]):
					if entry[1] > mn:
						oFile.write(entry[0] +'\t'+str(entry[1])+'\n')
						catEntityTotal[cat]+=1.0
				oFile.write('\n')
				oFile.write(string)
				oFile.close()
			

		else:
			print 'Ignoring category', cat, catTotal[cat]
	
	print 'Entities per category'
	for entry, val in catEntityTotal.iteritems():
		print entry,'\t',val

	print '\nPhrases per category'
	for entry, val in catPhraseTotal.iteritems():
		print entry,'\t',val

	
def getEntityPhrases(fileName,outDir):
	#i = 0
	catQueries = {}
	string = ""
	catTotal = {}

	for line in open(fileName,'r'):
		split = line.lower().strip().split('\t')
		taskDict = ast.literal_eval(split[-1])
		query = split[2].strip()
		print split	
		#get the query
		for entry in taskDict["annotations"]:
			if "dbpedia_categories" in entry:
				categories = entry["dbpedia_categories"];
				match = entry["spot"].replace('+',' ')
				rho = float(entry["rho"])
				#print query, categories, match
				if len(categories) > 0:
					for cat in categories:
						if cat not in catQueries:
							catQueries[cat] = {}
							catTotal[cat] = 0.0
						if rho > 0.05:
							qRep = query.replace(match,"_CAT_")
							if qRep not in catQueries[cat]:
								catQueries[cat][qRep] = {"match":[], "score":0.0}
							qRep = qRep.strip()
							catQueries[cat][qRep]["score"] += 1.0
							catQueries[cat][qRep]["match"].append(match)
							if catTotal[cat] < catQueries[cat][qRep]["score"]:
								catTotal[cat] = catQueries[cat][qRep]["score"]

			else:
		
				string += str(entry)+"\n"
				
			
	#for cat, queryDict in catQueries.iteritems():
	#	print queryDict["_TOTAL_"],"\t",cat, '\t', queryDict
	
	if not os.path.exists(outDir):
		os.mkdir(outDir)
	
	for cat, queryDict in catQueries.iteritems():
		match = {}
		if catTotal[cat] > 10:
			newCat = cat.replace(' ','_')
			newCat = newCat.replace('/','_')
			oFile = open(outDir+'/'+newCat+'_'+str(len(queryDict))+'.txt','w')
			string = ""
			for entry in sorted(queryDict.items(), reverse = True,key = lambda x : x[1]["score"]):
				string+= entry[0]+'\t'+str( entry[1]["score"])+'\n'
				for mtype in entry[1]["match"]:
					matchStr = mtype
					if matchStr not in match:
						match[matchStr] = 0.0
					match[matchStr]+= 1.0
			for entry in sorted(match.items(),reverse=True, key = lambda x : x[1]):
				if entry[1] > 10.0:
					oFile.write(entry[0] +'\t'+str(entry[1])+'\n')
			oFile.write('\n')
			oFile.write(string)
			oFile.close()
			
	
	#print string
		
'''
#argv[1] = input file
#argv[2] = output dir
'''
def main(argv):
	#biMeasure = nltk.collocations.BigramAssocMeasures()
	#triMeasure = nltk.collocations.TrigramAssocMeasures()
	#getPhrases(argv[1],biMeasure,triMeasure)
	getProtEntityPhrases(argv[1],argv[2])
	#getTfIdfWords(argv[1])

if __name__ == '__main__':
	main(sys.argv)
