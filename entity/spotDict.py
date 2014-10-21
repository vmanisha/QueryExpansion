# -*- coding: utf-8 -*-
import ast;
from queryLog import getQueryTerms;

class SpotDict:
	
	
	def __init__(self,string, query):
		sdict = ast.literal_eval(string);
		self.entities = sdict.keys();
		self.nonEntTerms = [];
		
		for entry in self.findNonEntTerms(query,sdict):
			if len(entry) > 2:
				self.nonEntTerms.append(entry);
		
		self.cats = {};
		
		for entity in sdict:
			self.cats[entity] =  sdict[entity]['cat'].split();
 	
	def findNonEntTerms(self,query,sdict):
		newQuery = query
		for entity in sdict:
			newQuery = newQuery.replace(entity,'')
		terms = getQueryTerms(newQuery);
		return terms	;
			
	def getEntities(self):
		return self.entities;
		
	def getEntCategories(self,entity):
		return self.cats[entity];
	
	
	def getNonEntityTerms(self):
		return self.nonEntTerms;
	
	def getNonEntTermsLen(self):
		return len(self.nonEntTerms);
	