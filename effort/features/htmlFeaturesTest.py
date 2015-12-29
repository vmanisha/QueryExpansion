import unittest
import numpy as np
from htmlFeatures import HtmlFeatures
from utils import encodeUTF

class HtmlFeaturesTest(unittest.TestCase):

	def setUp(self):
		self.page = open('../../clueweb_docs/test_aratio.html', 'r').read()
		self.content = encodeUTF(self.page).lower()
		self.url = 'http://www.xperiencetech.com/forum/topic.asp?TOPIC_ID=8254'
		self.qTerms = ['altitude' ,'sickness']
		self.qLen = 2

		self.pageForSpan = open('../../clueweb_docs/test_span.html','r').read()
		self.contentForSpan = encodeUTF(self.pageForSpan).lower()
		
		#content = '<!DOCTYPE html> \
		#			<html> \
		#			<body> \
		#			<h1>My First Heading</h1> \
		#			<p>My first paragraph.</p> \
		#			</body> \
		#			</html>'

		self.htmlFeatures = HtmlFeatures(self.content)
		self.htmlFeaturesForSpan = HtmlFeatures(self.contentForSpan)
	
	def test_tagDistribution(self):
		gtTagDist = {'h1':0.032,'h2':0.0,'h3':0.0,'h4':0.0,'h5':0.0,'h6':0.0,'table':0.097, \
		'div':0.0,'p':0.065,'b':0.129,'i':0.0,'a':0.387,'img':0.032,'li':0.0,'input':0.258,'strong':0.0}

		gtTagDistStr = ','.join([str(round(x[1], 3))
                           for x in sorted(gtTagDist.items())])

		self.assertEqual(self.htmlFeatures.tagDistribution(),gtTagDistStr)

	def test_outlinksWithDiffDomain(self):
		gtOutlinkDist = {'page': 0.083, 'same-domain': 0.583, 'diff-domain': 0.333}
		gtOutLinkStr = ','.join([str(round(x[1], 3))
                           for x in sorted(gtOutlinkDist.items())])

		self.assertEqual(self.htmlFeatures.outlinksWithDiffDomain(self.url),gtOutLinkStr)

	def test_outlinksToTextRatio(self):
		gtOutlinkFeat = {'aRatio': 2.0, 'tRatio': 2.667, 'atTxtRatio': 0.5}
		gtOutlinkFeatStr = ','.join([str(round(x[1], 3))
                          for x in sorted(gtOutlinkFeat.items())])

	   	self.assertEqual(self.htmlFeatures.outlinksToTextRatio(),gtOutlinkFeatStr)

	def test_summaryTagSpan(self):
		self.qTermsForSpan = ['altitude' ,'and','sickness']
		
		gtMinTag = {'spanA': 0.0, 'spanH': 0.0, 'spanB': 0.0, 'others': 0.0}
	    	gtSpanFeat = {'noSpan':0.0, 'avgSpanLen':0.0,'minSpanPos':0.0,\
		'maxSpanPos':0.0,'meanSpanPos':0.0}
		gtMinTagStr = ','.join([str(round(gtMinTag[y], 3))
                           for y in sorted(gtMinTag.keys())])
		gtSpanFeatStr = ','.join([str(round(gtSpanFeat[y], 3))
                           for y in sorted(gtSpanFeat.keys())])

    		gtResultString = gtMinTagStr + ',' + gtSpanFeatStr
    		self.assertEqual(self.htmlFeaturesForSpan.summaryTagSpan(self.qTermsForSpan,self.qLen),gtResultString)

	'''
	def test_tagCountAndPosition(self):
		gtHTagFeat = {'count': 2.0, 'minPos': 0.364, 'maxPos': 0.909, 'meanPos': 0.636}
		gtHTagFeatStr = ','.join([str(round(y[1], 3)) for y in sorted(gtHTagFeat.items())])
		self.assertEqual(self.htmlFeatures.tagCountAndPosition('h',set(self.qTerms)),gtHTagFeatStr)	

		gtATagFeat = {'count': 1.0, 'minPos': 2.0, 'maxPos': 3.0, 'meanPos': 4.0}
		gtATagFeatStr = ','.join([str(round(y[1], 3)) for y in sorted(gtATagFeat.items())])
		self.assertEqual(self.htmlFeatures.tagCountAndPosition('a',set(self.qTerms)),gtATagFeatStr)	

	def test_getTextFeature(self):
		gtMetrics = {'termsInTitle': 0.0, 'termsInURL': 0.0}
		gtMetricsStr = ','.join([str(round(gtMetrics[y], 3))
                        for y in sorted(gtMetrics.keys())])

    		self.assertEqual(self.htmlFeatures.getTextFeature(self.qTerms,self.url),gtMetricsStr)
	'''

if __name__ == '__main__':
	unittest.main()
