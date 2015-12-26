import unittest
import numpy as np
from textFeatures import *

class textFeaturesTest(unittest.TestCase):

	def test_getQueryCount(self):
		queryText = 'Mansi verma'
		# check when query terms appear consecutively in the document.
		sentences = ['mansi Mansi verma is very beautiful','mansi','verma','is this true?']
		gtMetrics = {'queryFreq':1.0, 'avgTF':2.5,'minTF':2.0, 'maxTF':3.0,\
		'minQTermPos':1.0,'maxQTermPos':8.0,'avgQTermPos':4.2}
		self.assertEqual(getQueryCount(queryText,sentences),gtMetrics)
		
		# check when query terms do not appear consecutively in document. 
		sentences = ['is very beautiful','mansi','verma','is this true?']
		gtMetrics = {'queryFreq':0.0, 'avgTF':1.0,'minTF':1.0, 'maxTF':1.0,\
		'minQTermPos':4.0,'maxQTermPos':5.0,'avgQTermPos':4.5}
		
		self.assertEqual(getQueryCount(queryText,sentences),gtMetrics)

	def test_getDocMetrics(self):
		queryText = 'tiger Woods'
		sentences = ['Tiger woods is not a real tiger','tiger','woods','is tiger, woods true']
		gtMetrics = {'sentWithQueryTerm': 2, \
					'sent': 4.0, \
					'char': 51.0, \
					'words': 5, \
					'period': 5.0, \
					'ARI': -1.33, \
					'CLI': -1.84, \
					'LIX': 2.6 \
					}

		self.assertEqual(getDocMetrics(queryText,sentences),gtMetrics)

	def test_getQueryDocMetrics(self):
		queryText = 'altitude sickness'
		sentences = ['Altitude sickness is a ordinary physiological','Tibet common bed',\
			'can of a doctor','alti','doctor','Tibet','sickness','new alit']
		gtMetrics = {'sentWithQueryTerm': 1, \
				'sent': 5.0, \
				'char': 74.0, \
				'words': 9, \
				'period': 5.0, \
				'ARI': 6.68, \
				'CLI': 6.29, \
				'LIX': 41.06 \
				}
		self.assertEqual(getQueryDocMetrics(queryText,sentences),gtMetrics)			

if __name__ == '__main__':
	unittest.main()
