# -*- coding: utf-8 -*-

TASK = 'tasks'
AND = ' AND '
OR = ' OR '

def findTaskEntity(taskDict,searcher, tlc, qp):
	for taskName, tdict in taskDict.iteritems():
		for taskVector in tdict[TASK].keys():
			#andString, orString = formulateQuery(qp,bigram_measures,trigram_measures,taskVector)
			andList = formulateQueries(taskVector)
			entityList = {}
			for andString in andList:	
				andQuery = qp.parse(unicode(andString))
				#orQuery = qp.parse(unicode(orString))
				try:
					searcher.search_with_collector(andQuery,tlc)
				except Exception as err:
					print '--LONG-- ',andString, err
				results = tlc.results()
				print taskVector, andString, andQuery
				for entry in results:
					if 'ont' in entry:
						if entry['ont'] not in entityList:
							entityList[entry['ont']] = {'match':{},'score':0}
						entityList[entry['ont']]['match'][entry['resource']]= 1
						entityList[entry['ont']]['score']+= round(entry.score,2)
			taskDict[taskName][TASK][taskVector]= entityList
			#taskDict[taskName][TASK][taskVector]['AND'][str(entry['ont'])] = round(entry.score,2)
			#taskDict[taskName][TASK][taskVector]['OR'] =searcher.search_with_collector(orquery, tlc)
			#print taskDict
					
def formulateQueries(queryList):
	#formulate and query for each entry in querylist
	andQueryList = []
	for entry in queryList:
		orList = []
		split = entry.split()
		if len(split) == 1:
			orList.append(entry)
		else:
			for i in range(len(split)):
				for j in range(i+1,len(split)+1):
					orList.append('( '+AND.join(split[i:j])+' ) ')
		andQueryList.append(OR.join(orList))
	print andQueryList
	return andQueryList
		
		

