# -*- coding: utf-8 -*-
def findWeightMatrix(featMan,coSessOcMan,coQueryOcMan, p1,p2=None ):
	weightMatrix = {};
	words1 = sorted(p1);
	words2 = None;
	if p2:
		words2 = sorted(p2);
	else:
		words2 = words1	
	
	for i in range(len(words1)):
		word1 = words1[i];
		
		if word1 not in weightMatrix:
			weightMatrix[word1] = {};
		
		if p2:
			st = 0; # different list
		else:
			st = i+1; #same list
			
		for j in range(st,len(words2)):
			word2= words2[j];
		
			if word2 not in weightMatrix:
				weightMatrix[word2]= {};
				
			if word1 != word2:
				eScore = featMan.getEntCosine(word1,word2);
				cScore = featMan.getCatCosine(word1,word2);
				uScore = featMan.getUrlCosine(word1,word2);
				weightMatrix[word1][word2] =0.18*(1.0-uScore)+\
					0.16*(1.0-cScore)+0.16*(1.0-eScore);
				weightMatrix[word2][word1] = weightMatrix[word1][word2];
		
	weightMatrix=findScore('session-co-occur',weightMatrix,\
		findSessionDistance,coSessOcMan,3.0,0.25);
	weightMatrix=findScore('query-co-occur',weightMatrix,\
		findQueryDistance,coQueryOcMan,3.0,0.25);
			
	return weightMatrix;
	


def findCatIndexes(catObj,featMan,coSessOcMan,coQueryOcMan):
	
	subClustDiam = {};
	clustList = catObj.getSubclusters();
	#for each cluster get the diameter
	for clusPair in clustList :
		entry = clusPair[0];
		phraseDict = clusPair[1];
		weightMatrix = findWeightMatrix(featMan,coSessOcMan,coQueryOcMan,phraseDict.keys());
		diam = findDiameter(weightMatrix);
		subClustDiam[entry] = diam;
	
	maxDiam = max(subClustDiam.values());
	
	if maxDiam  > 0:
		clustDistMatrix = {};
		#build clustDist matrix
		for i in range(len(clustList)):
			p1 = clustList[i][1].keys();
			for j in range(i+1, len(clustList)):
				p2 = clustList[j][1].keys();
				weightMatrix = findWeightMatrix(featMan,coSessOcMan,coQueryOcMan,p1,p2);
				dist = findMinInDict(weightMatrix);
				
				key = str(clustList[i][0]) +'_'+str(clustList[j][0]);
				clustDistMatrix[key] = dist;
		if len(clustDistMatrix.values()) > 0:
			minClusDist = min(clustDistMatrix.values());
			return minClusDist/maxDiam;
	
	return -1000;
	

def loadCatQueries(fileName):
	
	iFile = open(fileName, 'r')
	wordDict = {}
	corpus = [[],[]]
	#pattern frequency
	while True:
		line = iFile.readline()
		split = line.strip().split('\t')	
		if len(split)== 2:
			wordDict[split[0]] = float(split[1])
		else:
			break
	# remaining lines in file	
	for line in iFile:
		line = line.strip()
		split = line.split('\t')
		#patternDict[split[0]] = split[1]
		corpus[0].append(line)
		taskTokenDict = text_to_vector(split[0].replace('_CAT_',''))
		corpus[1].append(taskTokenDict)
	print len(corpus[0]), len(corpus[1])
	return wordDict, corpus

def main(argv):
	
	out = argv[3]
	os.mkdir(out)
	for ifile in os.listdir(argv[1]):
		try:
			k = int(ifile[ifile.rfind('_')+1:ifile.rfind('.')])/30
			print ifile, k
			if k > 0:
				phraseDict, corpus = loadCatQueries(argv[1]+'/'+ifile)
				X1,X2 = transformCorpus([],corpus[1])
				clusterBaseline1 = clusterTasksAgglomerative(X2,k)
				labels = clusterBaseline1.labels_
				labelResult = {}
				#scores = metrics.silhouette_score(X2, labels, metric='cosine')
				#print ifile, scores	
				for i in range(len(corpus[0])):
					if labels[i] not in labelResult:
						labelResult[labels[i]] = {}
					pattern = corpus[0][i][:corpus[0][i].find('\t')]
					freq = float(corpus[0][i][corpus[0][i].find('\t'):])
					labelResult[labels[i]][pattern] = freq
	
				writeDict(labelResult,out+'/'+ifile[:ifile.rfind('.')]+'_'+str(k)+'.txt')
		except Exception as err:
			print err
	
	

if __name__ == "__main__":	
	main(sys.argv)
