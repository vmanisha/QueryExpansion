from ast import literal_eval
import sys
import math
from utils import text_to_vector,get_cosine
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction import DictVectorizer
#from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import Normalizer
from sklearn import metrics
from sklearn.cluster import AgglomerativeClustering
from sklearn.cluster import KMeans, MiniBatchKMeans
from sklearn import metrics
from sklearn.metrics import pairwise_distances
import numpy
SPACE = '  '


#convert each task into text vector
#maintain a list of task indexes for each token
def indexTaskVectors(taskTuple,entityList,tid,tokenDict,taskVectorDict):
	#tokenDict = {}
	#taskVectorDict = {}
	for entry in taskTuple:
		split = entry.split(' ')
		taskTokenDict = {}
		for token in split:
			if token not in tokenDict:
				tokenDict[token] = {}
			tokenDict[token][tid] = 1
			if token not in taskTokenDict:
				taskTokenDict[token] = 0
			taskTokenDict[token]+=1
		taskVectorDict[tid]=taskTokenDict
	
	#for entity, score in entityList.iteritems():
		
	return taskVectorDict, tokenDict

def calculateSimilarityMatrix(taskVectorDict, tokenDict):
	print 'In similarity'
	nTasks = len(taskVectorDict)
	print nTasks
	sim =numpy.zeros(shape=(nTasks,nTasks))
	for entry,vector in taskVectorDict.iteritems():
		print entry, vector
		taskIndexList = {}
		for token in vector.keys():
			for ntid in tokenDict[token].keys():
				if ntid > entry:
					taskIndexList[ntid] = 1
		print entry, len(taskIndexList)
		for i in taskIndexList.values():
			print entry, i, sim
			sim[entry][i]=sim[i][entry]=get_cosine(vector, taskVectorDict[i])
			print 'sim', entry, i, vector, taskVectorDict[i], sim[entry][i]
	return sim


#tasks have been written into a file
def loadTasks(fileName,ttype):
	iFile = open(fileName,'r')
	corpus = [[],[]]
	tokenDict = {}
	taskVectorDict = {}
	tid = 0
	for line in iFile:
		split = line.strip().split('\t')
		taskDict = literal_eval(split[-1])
		for entry, entDict in taskDict[ttype]['tasks'].iteritems():
			#indexTaskVectors(entry,None,tid,tokenDict,taskVectorDict)
			ttext =SPACE.join(entry)
			tid += 1
			corpus[0].append(ttext)
			#print corpus[0], ttext, entry
			taskTokenDict = text_to_vector(ttext)
			#etDict =  {}
			#for entity in entDict['AND']:
			#etDict[str(entity)] = entDict['AND'][entity]['score']
			#etDict.update(taskTokenDict)
			corpus[1].append(taskTokenDict)
			#print etDict, corpus[1][-1]
			#print tsDict, corpus[0][-1]
	iFile.close()
	return corpus,tokenDict,taskVectorDict


def loadTasksFromTxt(fileName):
	corpus = [[],[]]
	tokenDict = {}
	taskVectorDict = {}
	tid = 0	
	for line in open(fileName,'r'):
		line = line.strip()
		#indexTaskVectors(line,None,tid,tokenDict,taskVectorDict)
		tid += 1
		corpus[0].append(line)
		taskTokenDict = text_to_vector(line)
		corpus[1].append(taskTokenDict)
	return corpus, tokenDict, taskVectorDict


#transform the corpus into
#set of features
def transformCorpus(tdocuments, tentities):
	X1 = None
	#treat the tasks as documents and calculate the tfIdf vector
	'''hasher = HashingVectorizer(stop_words='english', non_negative=True,
								 norm=None, binary=False)
	vectorizer = Pipeline((
		('hasher', hasher),
		('tf_idf', TfidfTransformer())
	))

	'''
	'''lsa = TruncatedSVD(1000)
	X = lsa.fit_transform( vectorizer.fit_transform(tdocuments) )
	X1 = Normalizer(copy=False).fit_transform(X)
	'''
	#X1 = vectorizer.fit_transform(tdocuments)
	#print("n_samples: %d, n_features: %d" % X1.shape)
	#print()
	vec = Pipeline((('dictText',DictVectorizer()), ('tfIdf',TfidfTransformer())))
	X2 = vec.fit_transform(tentities)
	lsa = TruncatedSVD(1000)
	X = lsa.fit_transform(X2 )
	X1 = Normalizer(copy=False).fit_transform(X)
	#X2 = Normalizer(copy=False).fit_transform(X)
	print("n_samples: %d, n_features: %d" % X.shape)
	print()

	return X1, X2

def main(argv):
	corpus,tokenDict,taskVectorDict = loadTasks(argv[1],argv[2])
	
	#simMatrix = calculateSimilarityMatrix(taskVectorDict,tokenDict)

	X1,X2 = transformCorpus(corpus[0],corpus[1])
	print X2.ndim
	
	numC= int(argv[3])
	#lucchese agglomerative clustering
	clusterBaseline1 = clusterTasksAgglomerative(X2,numC)
	#clusterBaseline1 = clusterTasksWithSimMatrix(simMatrix,numC)
	labelResult = {}
	labels = clusterBaseline1.labels_
	#scores = metrics.silhouette_score(X2, labels, metric='cosine')
	
	for entry in labels:
		print entry,
	#print scores

	for i in range(len(corpus[0])):
		if labels[i] not in labelResult:
			labelResult[labels[i]] = {}
		#split = corpus[0][i].split(SPACE)
		#for entry in split:	
		#	labelResult[labels[i]][entry] = 1 if entry not in labelResult[labels[i]] else labelResult[labels[i]][entry] + 1
		labelResult[labels[i]][corpus[0][i]] = 1

	writeDict(labelResult,'Task_Text_Agg__Cluster_userIds'+str(numC)+'.txt')
	
	'''		
	clusterBaseline2 = clusterTasksAgglomerative(X2,int(argv[3]))
	labelResult = {}
	labels = clusterBaseline2.labels_
	for i in range(len(corpus[0])):
		if labels[i] not in labelResult:
			labelResult[labels[i]] = {}
		split = corpus[0][i].split(SPACE)
		for entry in split:	
			labelResult[labels[i]][entry] = 1 if entry not in labelResult[labels[i]] else labelResult[labels[i]][entry] + 1
	writeDict(labelResult,'Task_Ent_Agg_Cluster'+str(numC)+'.txt')
	'''

	'''#clustering on entities agglomerative
	clusterBaseline2 =
	#clustering combining both agglomerative
	clusterBaseline3 =
	#
	'''

def writeDict(result, fileName):
	oFile = open(fileName, 'w')
	for entry, eDict in result.iteritems():
		dst = '\t'.join(["{0} : {1}".format(x,y) for x, y in eDict.iteritems()])
		oFile.write(str(entry)+'\t' + dst + '\n')
		#oFile.write(str(entry)+'\t' + str(eDict) + '\n')
	oFile.close()
 	
#Lucchesse Tasks clustered
#on text vectors
def clusterTasksAgglomerative(features,num):
	#clustering = AgglomerativeClustering(n_clusters = num, affinity='cosine',linkage='average')
	#clustering = MiniBatchKMeans(n_clusters=num, init='k-means++', n_init=1,
	#					 init_size=5000, batch_size=10000, verbose=True)
	clustering = KMeans(n_clusters=num, init='k-means++', max_iter=100, n_init=1,
                verbose=True)
	clustering.fit(features)
	return clustering

def clusterTasksWithSimMatrix(simMatrix,num):
	clustering = AgglomerativeClustering(n_clusters = num, affinity='precomputed',linkage='average')
	#clustering = MiniBatchKMeans(n_clusters=num, init='k-means++', n_init=1,
		#				 init_size=1000, batch_size=1000, verbose=opts.verbose)
	clustering.fit(simMatrix)
	return clustering


if __name__ == '__main__':
	main(sys.argv)


'''
#try clustering
	#merge Text vector and entities
	#Random Walks
def clusterTasks(taskList):


#task clustered
#on entities
def clusterTasksBase2(taskList):


'''
