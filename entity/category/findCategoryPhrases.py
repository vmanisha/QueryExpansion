from queryLog import getQueryTerms, normalize
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

def loadCategories(fileName):
	catDict = {}
	for line in open(fileName):
		tup = line.strip().split('\t');
		catDict[tup[0]] = tup[1]
	return catDict;
	
def loadTaggedQueries(fileName):
	taggedQueries = {};
	for line in open(fileName,'r'):
		split = line.split('\t');
		query = split[0].strip();
		spotDict = ast.literal_eval(split[1]);
		taggedQueries[query] = spotDict;

#def populateSessionCategoryDistribution(logFile, taggedDict, outFolder):
	#load session
	#for each session find dominant entity
	

def filterSpotDict(spotDict):
	newDict = {};
	#print spotDict.keys();
	
	for ent in spotDict.keys():
		if ent in stopSet:
			#print 'deleting ', ent;
			del spotDict[ent];
	
	#keep the entities above median for more than 2 entities
	if len(spotDict) > 2:
		scores = {};
		for entry in spotDict.keys():
			scores[entry] = spotDict[entry]['score'];
		sorteds = sorted(scores.items(), key = lambda x : x[1]);
		#print sorteds
		for entry in sorteds[0:len(sorteds)/2]:
			#print 'deleting ', entry
			del spotDict[entry[0]];
				
	
	spots = spotDict.keys();
	overlapped = {};
	for i in range(len(spots)):
		if i not in overlapped:
			overlapped[i] = False;
		for j in range(i+1, len(spots)):
			ints = set(spots[i].split()) & set(spots[j].split())
			
			if len(ints) > 0:
				#keep the largest
				#print 'overlap ', spots[i], spots[j], spotDict[spots[i]]['score'], spotDict[spots[j]]['score']
				if spotDict[spots[i]]['score'] > spotDict[spots[j]]['score']:
					newDict[spots[i]] = spotDict[spots[i]]
					overlapped[j] = True;
				else:
					newDict[spots[j]] = spotDict[spots[j]]
					overlapped[i] = True;
		if not overlapped[i]:
			newDict[spots[i]] = spotDict[spots[i]]
	#print 'Returning ', newDict;
	
	return newDict;
	
def populateCategoryDistribution(fileName, queryFreq,outFolder,catDict = None):

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
		try :
			spotDict = ast.literal_eval(split[1])
			#keeps the highest entity if overlapping entities
			spotDict = filterSpotDict(spotDict);
			
			newQuery = (split[0].decode('utf-8')).encode('ascii','ignore')
			#for entity in spotDict:
			#	newQuery = newQuery.replace(entity,'')
			
			#get the numbers, stopWords and symbols out
			terms = [newQuery];  #getQueryTerms(newQuery)
			
			#remove the ashleel words and
			for entity in spotDict:
				catString = spotDict[entity]['cat'].replace('/','-').lower();
				for cat in catString.split():
					if catDict and cat in catDict:
						if cat not in categoryDist:
							categoryDist[cat] = {}
						for oentry in terms:
							entry = oentry#porter.stem(oentry);
							if len(entry) > 2 and entry not in ashleelString and entry not in stopSet:
								if entry not in categoryDist[cat]:
									categoryDist[cat][entry]= {'wfreq':0.0};
								categoryDist[cat][entry]['wfreq'] += freq;
								categoryDist[cat][entry][entity] = categoryDist[cat][entry].setdefault(entity,0.0) + freq
			if i % 1000000 == 0 and i >0:
				print i
				
			i+=1
		except:
			print line;
			pass;
	#make a file for each category				
	for cat, termDict in categoryDist.iteritems():
		if len(termDict) > 10:
			ofile = open(outFolder+'/'+cat+'_'+str(len(termDict))+'.txt','w')
			
			for term, eDict in sorted(termDict.items(), reverse=True, key = lambda x: x[1]['wfreq']):
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
	catDict = loadCategories(argv[4])
	populateCategoryDistribution(argv[2],queryFreq,argv[3],catDict)

if __name__ == '__main__':
	main(sys.argv)
	
	