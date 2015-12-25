import unittest
import numpy as np
from textFeatures import *

class textFeaturesTest(unittest.TestCase):

	def test_getQueryCount(self):
		queryText = 'Mansi verma'
		sentences = ['mansi Mansi verma is very beautiful','mansi','verma','is this true?']
		gtMetrics = {'queryFreq':1.0, 'avgTF':2.5,'minTF':2.0, 'maxTF':3.0,\
		'minQTermPos':1.0,'maxQTermPos':8.0,'avgQTermPos':4.2}

		metrics = getQueryCount(queryText,sentences)

		self.assertEqual(metrics,gtMetrics)


if __name__ == '__main__':
  unittest.main()
