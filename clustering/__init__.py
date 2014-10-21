from utils import text_to_vector
import sys
import os, random
from subprocess import call
import json
from utils import stopSet
def reduceTaskToTerms(fileName):
	taskTermDict = {}
	for line in open(fileName, 'r'):
		split = line.split('\t')
		if len(split) > 1:
			key = split[0].strip()
			taskTermDict[key] = {}
			for entry in split[1:]:
				task = entry[:entry.rfind(',')]
				count = 0 #int(entry[entry.rfind(':')+1:])
				taskVector = text_to_vector(task)
				for entry , val in taskVector.iteritems():
					taskTermDict[key][entry]=taskTermDict[key].setdefault(entry,0.0) + val + count
			
	out = open('taskVectors.txt','w')
	for index, tDict in taskTermDict.iteritems():
		out.write(str(index)+ '\t'+ ' '.join('{0}:{1}'.format(x,y) for x, y in tDict.iteritems())+'\n')
		print index, '\t',tDict
		
		
def findQueryFeaturesFromList(featFile, directory, outDir):
	queries = {}
	finalFiles = {}
	os.mkdir(outDir)
	for ifile in os.listdir(directory):
		#toss a coin
		toSelect = random.random()
		try:
			noQueries = int(ifile[ifile.rfind('_')+1:ifile.rfind('.')])
			if toSelect > 0.5 and len(queries) < 100000 and noQueries > 100:
				for line in open(directory+'/'+ifile,'r'):
					query = line.strip()
					if query not in queries:
						queries[query] = []
					if ifile not in queries[query]:
						queries[query].append(ifile)
		except:
			pass
		
	for line in open(featFile,'r'):
		split = line.split('\t')
		split[0] = split[0].strip()
		if split[0] in queries:
			print split[0]
			for entry in queries[split[0]]:
				if entry not in finalFiles:
					finalFiles[entry] = open(outDir+'/'+entry,'w')
				finalFiles[entry].write(line)
	
	for entry in finalFiles.keys():
		finalFiles[entry].close()			
				

def standardizeFeatures(directory, outDir):
	if not os.path.exists(outDir):
		os.mkdir(outDir)
	for ifile in os.listdir(directory):
		featList = {}
		qfeatures = {}
		for line in open(directory+'/'+ifile,'r'):
			query, featDict = getFeatDict(line)
			#print query, featDict
			#print featDict.keys()
			for entry,val in featDict.items():
				entry = entry.lower()
				try:
					featList[entry] = featList.setdefault(entry,0) + 1#int(val)
				except:
					print entry, val
			qfeatures[query] = featDict
		ofile = open(outDir+'/'+ifile,'w')
		for query,features in qfeatures.iteritems():
			ofile.write(query.replace(' ','_'))
			for entry, val in featList.iteritems():
				if val > 3:
					if entry in features:
						ofile.write(' '+str(features[entry]))
					else:
						ofile.write(' 0.0')
			ofile.write('\n')
		ofile.close()
		
def getFeatDict(line):
	split = line.strip().split('\t')
	query = split[0].strip()
	featDict = {}
	k = 1
	for entry in split[1:]:
		featDict[k] = {}
		split2 = entry.split(' ')
		for featString in split2:
			featName = featString[:featString.rfind(':')].replace(' ','').strip()
			val = featString[featString.rfind(':')+1:]
			try:
				featVal = int(val)
				if len(featName) > 2:
					featDict[k][featName] = featVal
			except:
				pass
		k+=1
	return query, featDict	

def toFeat(entry):
	feat = {}
	split2 = entry.split(' ')
	for featString in split2:
			featName = featString[:featString.rfind(':')].replace(' ','').strip()
			featName = featName.replace('_',' ')
			val = featString[featString.rfind(':')+1:]
			try:
				featVal = int(val)
				if len(featName) > 2:
					feat[featName] = featVal
			except:
				pass
	return feat
			
def runCommand(inputDir, outDir):
	if not os.path.exists(outDir):
		os.mkdir(outDir)
	for ifile in os.listdir(inputDir):
			call(['mcl',inputDir+'/'+ifile,'--abc','-o',outDir+'/'+ifile])


def convertToJson(allFeatures, directory):
	# category -- {cluster_index:{[terms],[ent]}, clusterIndex:{[terms],[ent]}}
	allQueries = {}
	clusters = {}
	for ifile in os.listdir(directory):
		k = 1
		clusters[ifile] = {}
		for line in open(directory+'/'+ifile,'r'):
			clusters[ifile][k] = {'query':{}, 'ent':{}, 'terms': {}}
			queries = line.strip().split('\t')
			for entry in queries:
				query = (entry.replace('_',' ')).strip()
				clusters[ifile][k]['query'][query] = 0
				allQueries[query] = None
			k+=1
	for line in open(allFeatures,'r'):
		split = line.split('\t')
		query = split[0].strip()
		if query in allQueries:
			allQueries[query]={'ent': toFeat(split[1]).keys() ,
				 'count' : sum(toFeat(split[3]).values())}
			
	
	for fileName in clusters.keys():
		clusterInfo = clusters[fileName]
		for index in clusterInfo.keys():
			feat = clusterInfo[index]
			#print index, feat
			for query in feat['query'].keys():
				info = allQueries[query]
				#print query
				feat['query'][query] += info['count']
				terms = query.split(' ')
				entString = ''
				for ent in info['ent']:
					feat['ent'][ent] = feat['ent'].setdefault(ent, 0.0) + info['count']
					entString += ent + ' '
				for term in terms:
					if term not in entString and term not in stopSet and len(term) > 2:
						feat['terms'][term] = feat['terms'].setdefault(term, 0.0) + info['count']
	
	for entry, clustInfo in clusters.items():
		print entry, '\t', json.dumps(clustInfo)
		
				
if __name__=='__main__':
	argv = sys.argv
	#reduceTaskToTerms(argv[1])
	#findQueryFeaturesFromList(argv[1],argv[2], argv[3])
	#standardizeFeatures(argv[1],argv[2])
	#runCommand(argv[1],argv[2])
	convertToJson(argv[1],argv[2])