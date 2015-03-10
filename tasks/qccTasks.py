# -*- coding: utf-8 -*-
import os,sys, ast
from utils import getDictFromSet, getNGramsAsList
import networkx as nx
from queryLog import normalize
from features.logAnalysis import extractFeatureTuple
from features.queryFeature import *
from features.featureManager import FeatureManager
import math
from nltk import stem
'''
#load features
#load session
#find connected components
'''

def sortPair(id1, id2):
	if id1 < id2:
		return id1, id2
	else:
		return id2, id1
	
class QCCTasks:
	
	def __init__(self):
		self.G=nx.Graph()
		self.pairCount = {}
		
	def addEdge(self, q1, q2, score):
		#print q1, q2, score;
		self.G.add_edge(q1,q2,weight=score);
		
		a, b = sortPair(q1, q2);
		if a in self.pairCount:
			if b not in self.pairCount[a]:
				self.pairCount[a][b]=1.0
			else:
				self.pairCount[a][b]+=1.0
		else:
			self.pairCount[a]={}
			self.pairCount[a][b]= 1.0
			
	
	def normalizeScores(self):
		edgeList = self.G.edges()
		for entry in edgeList:
			print entry
	
	
	def getTaskComponents(self):
		entries = len(self.G.nodes())
		print entries
		if entries> 1:
			taskList = nx.connected_components(self.G)
			#print taskList
			#convert to clustering measure format
			#labels = getClusterFormat(taskList,entries)
			#print 'Connected Components' , taskList, labels
			return taskList
		return []

	def writeWeights(self,labels, fileName):
		#for each edge write the weights
		outFile = open(fileName,'w')
		for line in labels:
			outFile.write(str(line)+'\n')
		
		outFile.write('\n')
		for n,nbrs in self.G.adjacency_iter():
		    for nbr,eattr in nbrs.items():
		    	data=eattr['weight']
		    	outFile.write(str(n)+' '+str(nbr)+' '+str(data)+'\n')
		outFile.close()
			
#argv[1] = feature file
#argv[2] = session file
#argv[3] = outFile
#argv[4] = weight file
#Test normalize
#
def main(argv):

	qcc = QCCTasks();
	featMan = FeatureManager()
	#gurlDict = {}
	
	stemmer =  stem.porter.PorterStemmer()
	#qid = 1
	#uid = 1
	
	featMan.readFeatures(argv[1])
	
	sessCount = 0
	lastSes = None;
	session = []
	#parse sessions	
	for line in open(argv[2],'r'):
		split = line.split('\t');
		sessNo = int(split[0]);
		
		if lastSes != sessNo:
			newSession = []
			for i in range(len(session)-1):
				qid1, qf1 = featMan.returnFeature(session[i])
				if qf1:
					newSession.append(session[i])
			
			session = newSession
			#calculate the score
			for i in range(len(session)-1):
				qid1, qf1 = featMan.returnFeature(session[i])
				if qf1:
					for j in range(i+1,len(session)):
						#if (j - i) < 10:
						qid2, qf2 = featMan.returnFeature(session[j])
						if qf2:
							qcos, ucos, userCos, ngramCos, entCos, catCos = qf1.findCosineDistance(qf2)
							qjac = qf1.findJacardDistance(qf2)
							#qedit = qf1.findEditDistance(qf2)
							#normalized distance
							#dist = (j - i)#*1.0/len(session)
							
							edgeScore = (.25*((qcos + qjac)/2.0) +\
							.15*ngramCos + .15*ucos + \
							.15*userCos + .15*entCos + .15*catCos)
							if edgeScore > 0.40:
								#print session[i], session[j], edgeScore, qcos, qjac, ucos, userCos, qedit
								qcc.addEdge(qid1, qid2, edgeScore)
						else:
							print 'Query feature error ', session[j]
				else:
					print 'Query feature error ', session[i]
			#update the graph			
			session = [];
			sessCount+=1
			#if sessCount == 30:
			#	break
			
	#	session.append(normalize(split[1].strip(),stemmer));
		session.append(split[1].strip());
		lastSes = sessNo;

			
	labels = qcc.getTaskComponents()
	
	outFile = open(argv[3],'w');
	
	for entry in labels:
		string = ''
		for qid in entry:
			string+=featMan.returnQuery(qid) + '\t'
		outFile.write(string.strip()+'\n')
	
	outFile.close()	
			

	qcc.writeWeights(labels,argv[4])
if __name__ == '__main__':
	main(sys.argv)
	
	


#reading and creating features
	#load the features of queries
	#for line in open(argv[1], 'r'):
		#split = line.strip().split('\t')
		#query = split[0].strip()
		#nquery = normalize(query, stemmer);
		#qVect = getDictFromSet(nquery.split())
		#if len(qVect) > 0:
			#ngrams = getNGramsAsList(nquery,2)
			##if len(ngrams) > 0:
			##	print query, ngrams
			#userDict = extractFeatureTuple(split[1])
			#urlDict = extractFeatureTuple(split[2],True)
			#newDict = {}
			#for entry, count in urlDict.items():
				#if entry not in gurlDict:
					#gurlDict[entry] = uid
					#uid+=1
				#newDict[gurlDict[entry]] = count;
				#
			#queryFeat = QueryFeature(ngrams, qVect, newDict, userDict)
			#featMan.addFeature(nquery,qid, queryFeat)
			#qid +=1
	##	else:
	##		print query
	#featMan.writeFeatures(argv[4])
	#
	