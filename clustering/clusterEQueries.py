import os
import sys
from tools import *
from clusterTasks import *


#load the file
#load the terms queries
#cluster the patterns
#write the results

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
