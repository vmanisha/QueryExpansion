import os
import sys

import ast

from whoosh.index import create_in
from whoosh.fields import Schema, TEXT


'''
Indexing Tasks
'''
def main(argv):
	ischema = Schema(task= TEXT(stored=True,phrase=False))
	if not os.path.exists(argv[2]):
		os.mkdir(argv[2])
	tindex = create_in(argv[2],schema=ischema, indexname =argv[2])
	writer = tindex.writer()

	i=0
	dirName = argv[1]
	ttype = argv[3]
	for tfile in os.listdir(dirName):
		for line in open(dirName+'/'+tfile,'r'):
			#load the tasks
			split = line.strip().split('\t')
			tDict = ast.literal_eval(split[-1])
			fDict = tDict[ttype]['tasks']
			for task in fDict.keys():
				try :
					writer.add_document(task=unicode(' '.join(task).decode('unicode_escape').encode('ascii','ignore')))
				except Exception as err :
					print task, 'problem in indexing task'
					print err, err.args
				i+=1
				if i%100000==0:
					print i

	writer.commit()
	tindex.close()
		
	
if __name__ == '__main__':
	main(sys.argv)
