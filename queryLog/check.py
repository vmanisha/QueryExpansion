# -*- coding: utf-8 -*-
import sys, os
from queryLog import getSessionWithNL, getSessionWithXML
from utils import getDocumentText
def main(argv):
	#for session in getSessionWithNL(argv[1]):
	#	print session
	#get the entries for a particular query
	#parts = int(argv[2])
	#index = int(argv[3])
	#files = os.listdir(argv[1])
	#outFolder = argv[4]
	#oFile = open(outFolder+'/'+ifile,'w')
	#strt = index*(len(files)/parts)
	#end = (index+1)*(len(files)/parts)
	#for i in range(strt,end):
		#ifile = files[i]
	queryFreq = {};
	for line in open(argv[1],'r'):
		split = line.split('\t');
		query = split[0].strip();
		freq = float(split[1]);
		queryFreq[query] = freq;
		
	toPrint = {};
	qid = 1;
	for session, doc, click in getSessionWithXML(argv[2]):
		query = session[0];
		if query in queryFreq:
			toPrint[str(qid)+'\t'+query] = queryFreq[query];
		else:
			toPrint[str(qid)+'\t'+query] = 0;
		qid+=1;
		
	sort = sorted(toPrint.items() , reverse = True , key = lambda x : x[1]);
	for entry in sort:
		print entry[0],'\t', entry[1];
		
	#print getDocumentText('clueweb12-0817wb-00-27979','/media/Data/TREC_Session_Doc/cluewebdocs12/')
	'''done = {}
	for line in open(argv[1],'r'):
		split = line.split('\t')
		if split[0] not in done:
			done[split[0].strip()] = split[1].strip()
	
	for line in open(argv[2],'r'):
		split = line.strip().split('\t')
		if split[0].strip() in done:
			print split[0]+'\t'+done[split[0]]+'\t'+'\t'.join(split[1:])
	'''
	#for entry, spot in done.iteritems():
	#	print entry, '\t', spot

#merge the features urls, users and spot
				
				
if __name__ == '__main__':
	main(sys.argv)
