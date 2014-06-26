# -*- coding: utf-8 -*-
import urllib
import json
from queryLog import getSessionWithNL
import sys

class Dexter:
	
	def __init__(self,tURL, cURL):
		self.tagURL = tURL
		self.catURL = cURL
	
	def tagText(self, query):
		tagParam = {'text':''}
		catParam = {'asWikiNames':'true', 'wid' : ''}
		tagParam['text'] = query
		url = self.tagURL + '?' + urllib.urlencode(tagParam)
		#print url
		response = json.loads(urllib.urlopen(url).read())
		spots = response['spots']
		spotDict = {}
		for spot in spots:
			text = spot['mention']
			spotDict[text] = {}
			spotDict[text]['score'] = spot['score']
			#find the category
			catParam['wid'] = spot['entity']
			curl = self.catURL + '?' + urllib.urlencode(catParam)
			cresponse = json.loads(urllib.urlopen(curl).read())
			spotDict[text]['cat'] = (' '.join([x[x.rfind(':')+1:] for x in cresponse])).lower()
			
		return spotDict	


def main(argv):
	ipaddress = 'localhost'
	#dexter object
	tagURL = 'http://'+ipaddress+':8080/rest/annotate'
	catURL = 'http://'+ipaddress+':8080/rest/graph/get-entity-categories'
	dexter = Dexter(tagURL,catURL)
	
	
	for i, session in getSessionWithNL(argv[1]):
		query = session[0]
		print i , query, dexter.tagText(query)
		
		
if __name__ == '__main__':
	main(sys.argv)