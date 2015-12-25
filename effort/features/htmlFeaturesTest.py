import unittest
import numpy as np
import htmlFeatures

class HtmlFeaturesTest(unittest.TestCase):

	def setUp(self):
		content = '<!DOCTYPE html> \
					<html> \
					<body> \
					<h1>My First Heading</h1> \
					<p>My first paragraph.</p> \
					</body> \
					</html>'

		self.htmlFeatures = HtmlFeatures(content)

	def test_tagDistribution(self):
		gtTagDist = {'h1':1,'h2':0,'h3':0,'h4':0,'h5':0,'h6':0,'table':0, \
		'div':0,'p':1,'b':0,'i':0,'a':0,'img':0,'li':0,'input':0,'strong':0}

		self.assertEqual(self.htmlFeatures.tagDistribution(),gtTagDist)
	
if __name__ == '__main__':
	unittest.main()
