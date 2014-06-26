# -*- coding: utf-8 -*-
import ast
import os, sys

from whoosh.index import create_in
from whoosh.fields import Schema, TEXT

class IndexQueryEntities:
	
	def __init__(self):
		self.id = 1
		
	
	def index(self, ischema , fileName, indexPath):
		
		if not os.path.exists(indexPath):
			os.mkdir(indexPath)
	
		#open the index
		tindex = create_in(indexPath,schema=ischema, indexname =indexPath)
		writer = tindex.writer()
		i = 1
		#process each line
		for line in open(fileName,'r'):
			split = line.strip().split('\t')
			lquery = split[0]
			entityDict = ast.literal_eval(split[-1])	
			for match, catDict in entityDict.iteritems():
				try :
					writer.add_document(query = unicode(lquery.decode('unicode_escape').encode('ascii','ignore'))\
					, entity = match)
				except Exception as err:
					print err, err.args
			i+=1
			if i%100000==0:
				print i

		writer.commit()
		tindex.close()
				
				
	#def loadIndex(self, indexPath):
	
	#def searchIndex(self,field, text):
	
	
def main(argv):
	ischema = Schema(entity= TEXT(stored=True,phrase=False),\
	query = TEXT(stored=True, phrase=False))#,category=TEXT(stored=True,phrase = False))

	
	indObj = IndexQueryEntities()
	indObj.index(ischema, argv[1], argv[2])

if __name__ == '__main__':
	main(sys.argv)
		