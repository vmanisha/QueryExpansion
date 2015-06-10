# -*- coding: utf-8 -*-
import argparse as ap
from q
from features.featureManager import FeatureManager
#for each query in log do the following
	#store the clicked document
	#store the user if present
	#store the session
	#store entities


def main():

	parser = ap.ArguementParser(description = 'Generate features for entity tagged queries')
	parser.add_argument('-i', '--iFile', help='Query log file', required=True)
	parser.add_argument('-o', '--oFile', help='Output feature file', required=True)
	parser.add_argument('-t', '--typeFile', help='DBPedia type file', required=True)
	parser.add_argument('-c', '--catFile', help='DBPedia cat file', required=True)
	parser.add_argument('-u', '--uid', help='User id present or not', required=True,type=bool)
	parser.add_argument('-w', '--wtype', help='Words, Phrase or query features', required=True)
	
	args = parser.parse_args()
	
	
	#load the category list
	catList = {}

	#load the type list
	typeList = {}

	#query list
	queryList = {}
	
	#feature manager
	fMan = FeatureManager()

	if args.uid:
		getSession = 	
	for session in getSession

