# -*- coding: utf-8 -*-
import sys
import os
def main(argv):
	toKeep = []
	for line in open(argv[1],'r'):
		qNo = int(line.strip())
		toKeep.append(qNo)	
		
	for fileName in os.listdir(argv[2]):
		if not os.path.isdir(argv[2]+'/'+fileName):
			outF = open(argv[2]+'/'+fileName[: fileName.rfind('.')]+'_filter.RL1','w')
			for line in open(argv[2]+'/'+fileName,'r'):
				split = line.split()
				qNo = int(split[0])
				if qNo in toKeep:
					outF.write(line)
			outF.close()
	
	
if __name__ == '__main__':
	main(sys.argv)