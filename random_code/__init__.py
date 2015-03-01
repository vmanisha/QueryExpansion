# -*- coding: utf-8 -*-
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
	
	#clusterWithKMeans(argv)
	clusterWithKMediods(argv)
	#reduceTaskToTerms(argv[1])
	#findQueryFeaturesFromList(argv[1],argv[2], argv[3])
	#standardizeFeatures(argv[1],argv[2])
	#runCommand(argv[1],argv[2])
	#convertToJson(argv[1],argv[2])
