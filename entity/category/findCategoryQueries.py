# -*- coding: utf-8 -*-
import os
import sys
import ast
import re
from utils import SYMB
def main(argv):
	catQueryDict = {}
	for line in open(argv[1],'r'):
		split = line.lower().strip().split('\t')
		split[-1] = split[-1].strip()
		try:
			entityDict = ast.literal_eval(split[-1])
			query = re.sub(SYMB, ' ',split[0]).strip()
			query = re.sub('\s+',' ',query)
			
			#get the query
			for match, entDict in entityDict.iteritems():
				cats = entDict["cat"]
				if len(cats) > 2:
					categories = cats.split()
					for cat in categories:
						if cat not in catQueryDict:
							catQueryDict[cat] = []
						catQueryDict[cat].append(query)
		except Exception as err:
			print err, err.argv
	
	if not os.path.exists(argv[2]):
		os.mkdir(argv[2])
	
	for cat, qlist in catQueryDict.iteritems():
		cat = cat.replace('/','_')
		ofile = open(argv[2]+'/'+cat+'_'+str(len(qlist))+'.txt','w')
		for query in qlist:
			ofile.write(query+'\n')
		ofile.close()	
		
if __name__ == '__main__':
	main(sys.argv)