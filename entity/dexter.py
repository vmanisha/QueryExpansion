# -*- coding: utf-8 -*-
import urllib
import json,os
import time
from queryLog import getSessionWithNL
import sys;
import ast;

class Dexter:
	
	def __init__(self,tURL, cURL,spotFile = None):
		self.tagURL = tURL;
		self.catURL = cURL;
		self.e = 0;
		self.spots = {};
		if spotFile:
			self.loadSpotFile(spotFile);
		
		
	def loadSpotFile(self, spotFile):
		for line in open(spotFile,'r'):
			split = line.split('\t');
			query = split[0].strip();
			spotDict = ast.literal_eval(split[1].strip());
			if query not in self.spots:
				self.spots[query] = spotDict;
	
	def tagText(self, query):
		
		if self.spots and query in self.spots:
			return self.spots[query];
		else:
			return {};
		
		try:
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
			
		except Exception as err:
			errStr = ''.join(str(err.args))
			print err, err.args, errStr
			if self.e == 900:
				exit()
			if 'Connection' in errStr:
				time.sleep(15)
				self.e+=1
				#try starting the server again
				os.system("nohup java -Xmx4000m -jar ~/Downloads/dexter/dexter-1.0.0.jar &> java.log &")
				time.sleep(15)
			else :
				print err, err.args
			return {}
		
	
def main(argv):
	ipaddress = 'localhost'
	#dexter object
	tagURL = 'http://'+ipaddress+':8080/rest/annotate'
	catURL = 'http://'+ipaddress+':8080/rest/graph/get-entity-categories'
	dexter = Dexter(tagURL,catURL)
	
	
	#for i, session in getSessionWithNL(argv[1]):
	#	query = session[0]
	#	print i , query, dexter.tagText(query)
	done = {};
	allCats = [];

	sFile = open('spotFile','w');
	cFile = open('catFile','w');
	for line in open(argv[1],'r'):
		#split = line.split('\t');
		query = line.strip();
		if query not in done:
			done[query] = 1.0;
			spotDict = dexter.tagText(query);
			if len(spotDict) > 0:
				sFile.write(query+'\t'+ str(spotDict)+'\n');
				for entry,sDict in spotDict.items():
					catList = sDict['cat'].split();
					for entry1 in catList:
						if entry1 not in allCats:
							allCats.append(entry1);
							
				
	for entry in allCats:
		cFile.write(entry+'\n');
	
	cFile.close();
	
	sFile.close();
			
		
if __name__ == '__main__':
	main(sys.argv)