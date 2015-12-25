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

		#sentences = ['Existing computer programs that measure readability are based largely upon subroutines which estimate number of syllables, usually by counting vowels','The shortcoming in estimating syllables is that it necessitates keypunching the prose into the computer','There is no need to estimate syllables since word length in letters is a better predictor of readability than word length in syllables','Therefore, a new readability formula was computed that has for its predictors letters per 100 words and sentences per 100 words','Both predictors can be counted by an optical scanning device, and thus the formula makes it economically feasible for an organization such as the U.S. Office of Education to calibrate the readability of all textbooks for the public school system']

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

	
if __name__ == '__main__':
	unittest.main()
