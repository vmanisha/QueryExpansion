# -*- coding: utf-8 -*-
import os
import json
import urllib
import time
import sys
import ast
from dbPedia import loadCategories,loadInstancesInList
def tagQueryWithDexter(query, tagURL):
	
	tagParam = {'text':'', 'n':'5', 'dsb':'tagme','min-conf':'0.2','wn':'true' }
	tagParam['text'] = query
	url = tagURL + '?' + urllib.urlencode(tagParam)
	#print url
	response = json.loads(urllib.urlopen(url).read())
	spots = response['spots']
	spotDict = {'text' : None, 'spots':None}
	spotDict['text'] = query
	spotDict['spots'] = spots;
	#for spot in spots:
		##find the entity url and Name
		#catParam['id'] = spot['entity']
		#curl = self.catURL + '?' + urllib.urlencode(catParam)
		#cresponse = json.loads(urllib.urlopen(curl).read())
		#spotDict['spotLinks'][spot['entity']] = (' '.join([x[x.rfind(':')+1:] for x in cresponse])).lower()
		##
		
	if len(spotDict['spots']) > 0:
		return spotDict	
	return {}
	

def tagEntityWithDexter(code, entURL):
	entParam = {'id':'', 'title-only':'true', 'description':'false' }
	entParam['id'] = code
	url = entURL + '?' + urllib.urlencode(entParam)
	try:
		response = json.loads(urllib.urlopen(url).read())
	except:
		print url
		return None,None
	return response['title'], response['url']
	
def getEntityLinkWithDexter(spotFile, filterList=None):
	ipList = ['localhost']	
	ipaddress = ipList[0] #if random.random() > 0.5 else ipList[0]
	entURL = 'http://'+ipaddress+':8080/dexter-webapp/api/rest/get-desc'
	print 'Using ' + entURL
	
	outFile = open(spotFile[spotFile.rfind('/')+1:spotFile.rfind('.')]+'_ent_info.txt','w')
	i = 1
	entityList = {}
	for line in open(spotFile,'r'):
		spotDict = ast.literal_eval(line);
		query = spotDict['text']
		#print query, query in filterList
		if filterList and query in filterList:
			for entry in spotDict['spots']:
				code=entry['entity']
				if code not in entityList:
					name, url = tagEntityWithDexter(code, entURL)
					if name:
						entityList[code] = {'code':code,'title':name, 'url':url, 'count':1.0 }
					i+=1;	
					if i%10000 == 0:
						print i	
				else:
					entityList[code]['count'] += 1.0;
	
	for entry in sorted(entityList.items(), reverse = True, key = lambda x : x[1]['count']):		
		outFile.write(str(entry[1])+'\n');
	outFile.close();
	
'''
	args[1] = Logfile
	args[2] = line to read queries from file
	args[3] = index of query on each line (esp when format is ID QUERY TIME CLICK etc
	argv[4] = category list file
	argv[5] = instance type file
'''
def getEntitiesWithDexter(argv):
	#find the entities with dexter
	index = int(argv[3])
	#if hosted on multiple ips
	ipList = ['localhost']	
	ipaddress = ipList[0] #if random.random() > 0.5 else ipList[0]
	tagURL = 'http://'+ipaddress+':8080/dexter-webapp/api/rest/annotate'
	#catURL = 'http://'+ipaddress+':8080/dexter-webapp/api/rest/get-desc'
	print 'Using ' + tagURL

	start = int(argv[2])
	outFile = open(argv[1][argv[1].rfind('/')+1:argv[1].rfind('.')]+str(start)+'_out.txt','w')

	i = 0
	e = 0
	
	categoryList = loadCategories(argv[4])
	instanceList = loadInstancesInList(argv[5])
	
	for line in open(argv[1],'r'):
		#if already tagged
		if i < start:
			pass;
		split = line.strip().split('\t')
		query = split[index].lower()	#get the result with url
		try:
			spotDict = tagQueryWithDexter(query, tagURL)
			spotDict = getCatAndTypeInfo(spotDict, categoryList, instanceList)
			if len(spotDict) > 0:
				outFile.write(str(spotDict)+'\n')
			
		except Exception as err:
			print i, query
			errStr = ''.join(str(err.args))
			print err, err.args, errStr
			if e == 300:
				break
			if 'Connection' in errStr:
				time.sleep(15)
				outFile.close()
				outFile = open(argv[1][argv[1].rfind('/')+1:argv[1].rfind('.')]+str(i)+'_out.txt','w')
				e+=1
				#try starting the server again
				os.system("nohup java -Xmx4000m -jar ~/libraries/dexter2/dexter-2.1.0.jar &> java.log &")
				time.sleep(15)
			else :
				print err, err.args
		i+= 1
		if i%50000 == 0:
			if i > start:
				time.sleep(15)
				print i
		
		'''if len(domCat) > 0:
			avgCatFrq = sum(domCat.values()) / len(domCat)
			avgEnityFrq = sum(domEnt.values()) / len(domEnt)
			toRemoveCat = [k for k,v in domCat.iteritems() if v < avgCatFrq]
			
			print session, domEnt, domCat, avgCatFrq, avgEnityFrq	
			print 'To Remove Cat List', toRemoveCat
			for query, spotList in querySpotList.iteritems():
				matchl = spotList.keys()
				for entry in matchl:
					if domEnt[entry] < avgEnityFrq:
						spotList.pop(entry,None)
						print 'Removing spot', entry
					else:
						for cat in toRemoveCat:
							spotList[entry]['cat']= spotList[entry]['cat'].replace(cat,'').strip()
				outFile.write( query +'\t'+ str(spotList)+'\n')
		'''	
	outFile.close()


def getCatAndTypeInfo(spotDict,categoryList, instanceList):
	spots = spotDict['spots']
	i = 0
	for spot in spots:
		ename = (spot['wikiname']).encode('unicode-escape')
		if ename in categoryList:
			spotDict['spots'][i][u'cat'] = categoryList[ename]
		else:
			print 'Cat not Found ', ename
			spotDict['spots'][i][u'cat'] = []
		
		if ename in instanceList:
			spotDict['spots'][i][u'type'] = instanceList[ename]
		else:
			print 'Instance not Found ', ename
			spotDict['spots'][i][u'type'] = []
		i+=1
	print spotDict


if __name__ == '__main__':
	argv = sys.argv
	getEntitiesWithDexter(argv)
	#load queries
	#queryList = {}
	#for line in open(argv[1],'r'):
		#split = line.strip();
		#queryList[split] = 1
		#
	#print len(queryList)
	#
	##send tagged file
	#getEntityLinkWithDexter(argv[2], queryList)
