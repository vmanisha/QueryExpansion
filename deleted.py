
def loadLinks(linksFile, RSTR='resource/'):
	inlinks = {}
	outlinks = {}

	idDict = {}
	nameIdDict = {}

	lid = 0
	for line in open(linksFile,'r'):
		split = line.lower().strip().split(' ')
		res1 = split[0][split[0].rfind(RSTR)+9:-1]
		res2 = split[-1][split[-1].rfind(RSTR)+9:-1]
		
		id1 = id2 = None
		if res1 not in idDict:
			lid += 1
			idDict[lid] = res1
			nameIdDict[res1] = id1
		
		if res2 not in idDict:
			lid += 1
			idDict[lid] = res2
			nameIdDict[res2] = id2
		
		id1 = nameIdDict[res1]
		id2 = nameIdDict[res2]

		if id1 not in outlinks:
			outlinks[id1] = set()
			
		if id2 not in inlinks:
			inlinks[id2] = set()

		outlinks[id1].add(id2)
		inlinks[id2].add(id1)
		
	return idDict, inlinks, outlinks

def buildLinkGraph(linksFile, RSTR = 'resource/'):
	g = Graph(directed = True)
	vertexList = set ()
	i = 0
	ifile = open(linksFile,'r')
	ifile.readline()
	for line in ifile:
		i+=1
		#split = line.lower().strip().split(' ')
		split = line.strip().split(' ')
		res1 = split[0]
		res2 = split[1]
		#print split[0], split[1]
		#res1 = split[0][split[0].rfind(RSTR)+9:-1]
		#res2 = split[-1][split[-1].rfind(RSTR)+9:-1]
		#if res1 in validRes and res2 in validRes:
		#print res1, res2
		if res1 not in vertexList:
			vertexList.add(res1)
			g.add_vertex(name = res1)

		if res2 not in vertexList:
			vertexList.add(res2)
			g.add_vertex(name = res2)
		
		g.add_edge(res1, res2)
		#else:
		#	print 'one', res1,'two', res2
		if i % 50000==0:
			print i
	ifile.close()
	g.save('linkGraph.txt')

'''def formulateQuery(parser,bigram_measures,trigram_measures,queryList):
	#and queries
	#make the collocations
	words = []
	for entry in queryList:
		 words += entry.split()
	
	wordDict = {}
	for entry in queryList:
		for x in entry.split():
			wordDict[x] = 1 if x not in wordDict else wordDict[x]+1

	andString =''
	if len(words) > 1:
		finder = BigramCollocationFinder.from_words(words)
		#finder3 = TrigramCollocationFinder.from_documents(queryList)
		andString = OR.join(['( '+AND.join([x +'^'+str(round(qt[1],2)) for x in qt[0]])+' )' for qt in aboveScore(finder.score_ngrams(bigram_measures.pmi))])
	else:
		andString = words[0]
		return andString, orString
	
	wordDictString = AND.join(['{0}^{1}'.format(entry, str(score)) for entry, score in wordDict.iteritems()])
	andString += ' OR ( '+ wordDictString + ' )'
	
	#print queryList , 'ANDSTRING', andString , 'ORSTRING', orString
	
	return andString	
'''


#updates the stem network
#stem set([words])
def updateStemNetwork(queryTerms,network,porter,termIdDict,idTermDict):
	
	for term in queryTerms :
		words = len(termDict)
		stemmed = porter(term)
		
		if term not in idTermDict:
			idTermDict[words] = term
			termIdDict[term] = words
		else:
			words = termIdDict[term]
	
		if stemmed not in network:
			network[stemmed] = set()
		
		network[stemmed].add(words)
	

#return the probabilities of stems	
def getStemProb(network):
	sProb = {}
		
	for i in sProb.keys():
		for j in sProb[i].keys():
			sProb[i][j]/=(1.0*len(sProb[i]))
	
	return sProb				
#load the index
	#index, searcher, tlc = loadIndex(args.indexPath,args.indexName)
	#print 'Doc count ',index.doc_count()
	#make the parser
	#qp = QueryParser("resource", schema=index.schema,group=OrGroup )

#initialize bigram and trigram collocations
	#biMeasure = nltk.collocations.BigramAssocMeasures()
	#triMeasure = nltk.collocations.TrigramAssocMeasures()
	#stats = {QCC:{'total':0},HTC:{'total':0}}
#searchIndex(searcher,tlc,qp, biMeasure, triMeasure,taskDict)
						#closeIndex(searcher,index)
						
							#read the file
	'''args = sys.argv
	iFile = open(args[1],'r')
	stats = {QCC:{'ttotal':0,'etotal':0, 'sc':{}, 'scTotal':0, 'scCount':0},
		 HTC:{'ttotal':0,'etotal':0, 'sc':{}, 'scTotal':0, 'scCount':0}}
	i = 0
	for line in iFile:
		split = line.split('\t')
		taskDict = ast.literal_eval(split[2])
		updateStats(taskDict,stats)
		i+= 1
		if i % 10000==0:
			print i

	iFile.close()
	print stats	
	'''	
	
	
def loadTasks(dirName,ttype):
	taskDict = {}
	wordTaskDict = {}
	i = 0
	for tfile in os.listdir(dirName):
		for line in open(dirName+'/'+tfile,'r'):
			#load the tasks
			split = line.strip().split('\t')
			tDict = ast.literal_eval(split[-1])
			fDict = tDict[ttype]['tasks']
			for task in fDict.keys():
				text = re.sub(SYMB,' ',' '.join(task))
				text = re.sub('\s+',' ',text)
				tokens = text.split()
				#tokenize the dict
				taskDict[i] = getDictFromSet(tokens)

				for token in tokens:
					if len(token) > 2 and queryAlphabetFilter(token) and token not in stopSet:
						if token not in wordTaskDict:
							wordTaskDict[token] = set ()	
						wordTaskDict[token].add(i)
				i+=1
				if i % 100000==0:
					print 'Loaded', i ,'Tasks'
					
	print 'Done Loading Task dictionary'	
	return taskDict,wordTaskDict

#import nltk
#import nltk.collocations
#from nltk.collocations import TrigramCollocationFinder
#from nltk.collocations import BigramCollocationFinder
def getUserSessionsWithTime(fileName, delim, timeCutoff):
	# iterate the queries if the time difference
	# between 2 queries is greater than the cutoff
	# put them in different sessions
	lastTime = lastUser = lastQuery = currTime = currUser = None
	wordCount = 0
	currSession = {}
	wordQueryDict = {}
	sessionVector = {}
	clickedURL = {}
	iFile = open(fileName,'r')
	iFile.readline()
	i =0
	for line in iFile:
		entry = parseLine(line)
		query = entry[QUERY].lower()
		raw_split = entry[QUERY].split(' ')
		currTime = entry[QTIME]
		currUser = entry [USER]
		if not ((lastTime == None) or (((currTime -lastTime).total_seconds() < timeCutoff or subQuery(query,lastQuery)) and currUser == lastUser)):
			# start a new session
			if len(currSession) > 0:
				i += 1
				yield lastUser, currSession, wordCount, wordQueryDict, sessionVector, clickedURL
				currSession = {}
				wordQueryDict = {}
				sessionVector = {}
				clickedURL = {}
				
			if i % 100000 == 0:
				print i
			if hasManyChars(query,raw_split,1,4,70) and hasInapWords(raw_split) \
			and hasManyWords(raw_split,15,40) and hasAlpha(query) and hasWebsite(query):
				rLen = len(raw_split)
				wordCount+= rLen
				wordQueryDict[rLen] = 1 if rLen not in wordQueryDict else wordQueryDict[rLen] + 1
				updateVector(query,sessionVector)
				if query not in currSession:
					currSession[query] = [currTime]
				else:
					currSession[query].append(currTime)
				if 'clickUrl' in entry:
					pUrl = entry['clickUrl']
					clickedURL[pUrl] = 1 if pUrl not in clickedURL else clickedURL[pUrl] + 1
					lastTime = currTime
					lastUser = currUser
					lastQuery = query
	iFile.close()
	def writeSessions(folderName, outFolderName):
        stats = {'#queries':0,'#sessions':0,'#users':0,'#words':0}
        dist = { 'word_query': {}, 'query_session':{}}
        userQueryCountList = {}
        i = 1
	if not os.path.exists(outFolderName):
		os.mkdir(outFolderName)
		
        #iterating over logs
        for iFile in os.listdir(folderName):
                print iFile
		outFile = open(outFolderName+'//'+iFile,'w')
                #logs = loadFile(folderName+'//'+iFile, "\t")
                #iterating over sessions
                for lastUser, currSession, wordCount, wordQueryDict, sessionVector,clickedURL in getUserSessionsWithTime(folderName+'/'+iFile,1500): #np.timedelta64(1500)):
                        noQueries = len(currSession)
                        if lastUser not in userQueryCountList:
                                userQueryCountList[lastUser] = 0
                                stats['#users'] += 1
                        userQueryCountList[lastUser] += noQueries
                        if noQueries not in dist['query_session']:
                                dist['query_session'][noQueries] = 0
                        dist['query_session'][noQueries] += 1
                        stats['#queries'] += noQueries
                        stats['#sessions'] += 1
                        stats['#words'] += wordCount
                        for entry, value in wordQueryDict.iteritems():
                                if entry not in dist['word_query']:
                                        dist['word_query'][entry] = 0
                                dist['word_query'][entry] += value
			#print the sessions
			writeStr= str(lastUser)+'\t'
			writeStr += ', '.join('{0}:{1}'.format(x, str(len(y))) for x, y in currSession.iteritems()) + '\t'
			#writeStr += ', '.join( for x in currSession.values()) + '\t'
			writeStr += ' '.join('{0}:{1}'.format(x,str(y)) for x, y in clickedURL.iteritems())
			outFile.write(writeStr+'\n')
		outFile.close()

        print '\nPrinting Stats'
        for entry, value in stats.iteritems():
                print entry, value

        print '\nPrinting Dist'
        for entry, dist in dist.iteritems():
                print entry
                for key, value in dist.iteritems():
                        print key, value

        print '\nPrinting User Session info'
        for uId, count in userQueryCountList.iteritems():
                print uId, count


total = 0
	aT = 0
	for session in getSessionWithNL(argv[1]):
		
		bQuery = session[0].lower()
		bQuery = re.sub(SYMB,' ',bQuery)
		bQuery = re.sub('\s+',' ',bQuery)
		aTerms, rTerms = addedAndRemovedTerms(bQuery, session)	
		print len(session), len(aTerms), aTerms, '\t'.join(session)
		total+= len(session)
		aT += len(aTerms)
<<<<<<< HEAD
	print total	, aT
	
	'''num = 1.0/sum(self.termTermFreq[i].values())
				print 'Num i ',sum(self.termTermFreq[i].values()),
				if j in self.termFreq:
					den = self.termFreq[j]/self.termTotal
					print 'Den i+j ' ,self.termFreq[j], self.termTotal
				else:
					den = 1.0/self.termTotal
					print 'Den i-j ' , self.termTotal
				'''
				
				'''num = 1.0/sum(self.termTermFreq[j].values())
			print 'Num j ',sum(self.termTermFreq[j].values()),
			if i in self.termFreq:
				den = self.termFreq[i]/self.termTotal
				print 'Den j+i ' ,self.termFreq[i], self.termTotal
			else:
				den = 1.0/self.termTotal
				print 'Den j-i ' , self.termTotal
			'''
			
			'''num = 1.0/self.termTermTotal
				if j in self.termFreq:
					den = (self.termFreq[j]*self.termFreq[i])/math.pow(self.termTotal,2)
				else:
					den = self.termFreq[i]/math.pow(self.termTotal,2)
				'''
				
				'''num = 1.0/self.termTermTotal
			#i isnt in db
			if i in self.termFreq:
				den = (self.termFreq[j]*self.termFreq[i])/math.pow(self.termTotal,2)
			else:
				den = self.termFreq[j]/math.pow(self.termTotal,2)
			'''
=======
	print total	, aT
>>>>>>> origin/master
