# -*- coding: utf-8 -*-
import ast
import os, sys
class listIntersection:
	
	def __init__(self):
		self.id = 1
		
	def intersect(self,l1, l2):
		return len(l1 & l2), l1 & l2

def loadQueries(fileName, termCount):
	queryExpTermList  = {}
	for line in open(fileName, 'r'):
		split = line.strip().split('\t')
		tCount = int(split[-1])
		termset = set()
		if tCount == termCount:
			terms = ast.literal_eval(split[3])
			for entry in terms:
				termset.add(entry[0])
			queryExpTermList[split[1]+'_'+split[2]] = termset
		
	return queryExpTermList
	
def main(argv):
	listInt = listIntersection()
	set1 = loadQueries(argv[1],50)
	for iFile in os.listdir(argv[2]):
		print argv[1][argv[1].find('/')+1:], iFile
		set2 = loadQueries(argv[2]+'/'+iFile,50)
		num = 0.0
		den = 0.0
		for entry, tlist in set1.iteritems():
			#print entry, tlist, set2[entry]
			if entry in set2:
				count, intSet  = listInt.intersect(tlist,set2[entry])
				print iFile, entry, count, intSet
				num+= count
				den+= len(tlist)
		print 'Stat ',iFile, num, den, num/den
		
		
if __name__ == '__main__':
	main(sys.argv)