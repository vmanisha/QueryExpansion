# -*- coding: utf-8 -*-
import os
import json
import urllib
import time
from QueryLog import getQuery


'''
	args[1] = Logfile
	args[2] = line to read queries from file
	args[3] = index of query on each line (esp when format is ID QUERY TIME CLICK etc
'''
def getEntitiesWithDexter(argv):
	#find the entities with dexter
	index = int(argv[3])
	#if hosted on multiple ips
	ipList = ['localhost']	
	ipaddress = ipList[0] #if random.random() > 0.5 else ipList[0]
	tagURL = 'http://'+ipaddress+':8080/rest/annotate'
	catURL = 'http://'+ipaddress+':8080/rest/graph/get-entity-categories'
	print 'Using ' + tagURL

	start = int(argv[2])
	outFile = open(argv[1][argv[1].rfind('/')+1:argv[1].rfind('.')]+str(start)+'_out.txt','w')

	i = 0
	e = 0
	prev = None
	for query in getQuery(argv[1], index):
		if prev!=query and i > start:
			#get the result with url
			try:
					
				spotDict = tagQueryWithDexter(query, tagURL, catURL)
				if len(spotDict) > 0:
					outFile.write( query +'\t'+ str(spotDict)+'\n')
				prev = query
					
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
					os.system("nohup java -Xmx4000m -jar ~/Downloads/dexter/dexter-1.0.0.jar &> java.log &")
					time.sleep(15)
				else :
					print err, err.args
		i+= 1
		if i%3000 == 0:
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
