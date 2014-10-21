from queryLog import getQueryTerms
import ast
import os, sys
from utils import stopSet, ashleelString;
from nltk import stem;
#load the spot dict
#for each category
	#output this matrix
	#term entity link

def loadQueryFreq(fileName):
	queryFreq = {}
	for line in open(fileName,'r'):
		split  = line.strip().split('\t')
		queryFreq[split[0].strip()] = int (split[1])
		
	return queryFreq



def populateCategoryDistribution(fileName, queryFreq,outFolder):

	porter = stem.porter.PorterStemmer();
	if not os.path.exists(outFolder):
		os.mkdir(outFolder)
	
	categoryDist = {}	
	i = 0
	for line in open(fileName,'r'):
		split = line.split('\t')
		
		query = (split[0].decode('utf-8')).encode('ascii','ignore')
		if query not in queryFreq:
			freq = 1.0
		else:
			freq = queryFreq[query]
			
		spotDict = ast.literal_eval(split[1])
		newQuery = (split[0].decode('utf-8')).encode('ascii','ignore')
		for entity in spotDict:
			newQuery = newQuery.replace(entity,'')
		
		#get the numbers, stopWords and symbols out
		terms =getQueryTerms(newQuery)
		
		#remove the ashleel words and
		for entity in spotDict:
			catString = spotDict[entity]['cat'].replace('/','-').lower();
			for cat in catString.split():
				if cat not in categoryDist:
					categoryDist[cat] = {}
				for oentry in terms:
					entry = porter.stem(oentry);
					if len(entry) > 2 and entry not in ashleelString:
						if entry not in categoryDist[cat]:
							categoryDist[cat][entry]= {'wfreq':0.0};
						categoryDist[cat][entry]['wfreq'] += freq;
						categoryDist[cat][entry][entity] = categoryDist[cat][entry].setdefault(entity,0.0) + freq
		if i % 1000000 == 0:
			print i
		i+=1
		
	#make a file for each category				
	for cat, termDict in categoryDist.iteritems():
		if len(termDict) > 10:
			ofile = open(outFolder+'/'+cat+'_'+str(len(termDict))+'.txt','w')
			
			for term, eDict in termDict.iteritems():
				ofile.write(term + '\t'+str(eDict['wfreq'])+'\t'+ str(eDict) + '\n')
		
			ofile.close()

def loadCatFile(fileName):
	phrases = {};
	for line in open(fileName, 'r'):
			split = line.split('\t');
			term = split[0].strip();
			if len(split) > 1:
				if term not in stopSet:
					entDict = ast.literal_eval(split[1]);
					phrases[term] = sum(entDict.values());
			else:
				print line;
	return phrases;
def loadClusters(fileName):
	subClusters = {};
	for line in open(fileName,'r'):
		split = line.split('\t');
		cNum = split[0];
		subClusters[cNum] = {};
		if len(split) > 1:
			for entry in split[1].split(' '):
				entry= entry.strip();
				subClusters[cNum][entry]=0.0;
		else:
			print line;
	return subClusters;

#argv[1] = query frequency
#argv[2] = tagged queries file
#argv[3] = outFolder
def main(argv):
	'''
	iFolder = argv[1];
	cFolder = argv[2];
	oFolder = argv[3];
	
	if not os.path.exists(oFolder):
		os.mkdir(oFolder);
	
	for ifile in os.listdir(cFolder):
		phrases = loadCatFile(iFolder+'/'+ifile);
		clusters = loadClusters(cFolder+'/'+ifile);
		oFile = open(oFolder+'/'+ifile,'w');
		for cNum, words in clusters.items():
			for entry in words.keys():
				if entry in phrases:
					clusters[cNum][entry] = phrases[entry];
				else:
					print 'Not found ', entry, cNum, ifile
		
		for cNum, words in clusters.items():
			wsorted = sorted(words.items(), reverse = True, key = lambda x : x[1]);
			oFile.write(str(cNum)+'\t' + ' '.join('{0}:{1}'.format(x[0],x[1]) for x in wsorted)+'\n');
	oFile.close();
	'''
	queryFreq = loadQueryFreq(argv[1])
	populateCategoryDistribution(argv[2],queryFreq,argv[3])

if __name__ == '__main__':
	main(sys.argv)
	
	