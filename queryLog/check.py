# -*- coding: utf-8 -*-
import sys
from queryLog import getSessionWithNL
def main(argv):
	for session in getSessionWithNL(argv[1]):
		print session
	
if __name__ == '__main__':
	main(sys.argv)