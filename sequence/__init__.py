# -*- coding: utf-8 -*-
from queryLog import getSessionWithInfo, QUERY
from distance import levenshtein
import sys

#load the log
def mineSequence(fileName):
	
	wordVariants = []
	for user, sesId, session, sesString in getSessionWithInfo(fileName):
		sesSeq = createSequence(session)
		for entry in sesSeq:
			if len(entry)  > 1 :
				ind = findWordVariants(entry,wordVariants)
				if ind > -1:
					#print ind, entry, wordVariants[ind]
					wordVariants[ind].union(entry)
				else:
					wordVariants.append(entry)
					
	for entry in wordVariants:					
		print entry;
		
def findWordVariants(tset,wordVariants):
	dist = 0
	for ind in range(len(wordVariants)):
		#its a set
		entry = wordVariants[ind]
		dist = 0
		for cand in tset:
			if cand not in entry:
				for toCheck in entry:
					dist+=levenshtein(cand,toCheck)
				dist /=(len(tset)*len(entry)*1.0)
				if dist < 1.3:
					#print dist, len(tset), len(entry)
					return ind
			else:
				return ind
			 	
	return -1						

def createSequence(session):
	sequence = [];
	#print session
	for entry in session:
		if QUERY in entry:
			mind = getMinSequence(entry[QUERY], sequence)		
			if mind > -1:
				#print 'adding ',sequence[mind], entry[QUERY]
				sequence[mind].add(entry[QUERY])
			else:
				sequence.append(set([entry[QUERY]]))
	return sequence
				
def getMinSequence(string, slist):
	mind = None
	mdist = None
	i = 0
	for tup in slist:
		tdist = 0;
		for entry in tup:
			tdist += levenshtein(string, entry)
		
		dist = tdist/(len(tup)	*1.0)
		if dist < mdist or mdist == None:
			mdist = dist
			mind = i
		i+=1
	
	if mdist < 3:
		return mind
	else:
		return None	
		
def main(argv):
	mineSequence(argv[1])


if __name__ == '__main__':
	main(sys.argv)				
#create a graph with each session

#treat each query as a node
#Find the edit distance between the nodes
#Write the sequence to the disk

#Post process the sequence
#Merge the sequences where possible
