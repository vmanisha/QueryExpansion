import unittest
import numpy as np
from htmlFeatures import HtmlFeatures
from utils import encodeUTF

class HtmlFeaturesTest(unittest.TestCase):

	def setUp(self):
		self.page = open('../../clueweb_docs/test.html', 'r').read()
		self.content = encodeUTF(self.page).lower()
		self.url = 'http://www.xperiencetech.com/forum/topic.asp?TOPIC_ID=8254'
		self.qTerms = ['altitude' ,'sickness']
		self.qLen = 2

		self.pageForSpan = open('../../clueweb_docs/test_span.html','r').read()
		self.contentForSpan = encodeUTF(self.pageForSpan).lower()
		
		self.pageForOutlinkToTextRatio = \
                        open('../../clueweb_docs/test_aratio.html','r').read()
		self.contentForOutlinkToTextRatio = \
                        encodeUTF(self.pageForOutlinkToTextRatio).lower()

		self.htmlFeatures = HtmlFeatures(self.content)
		self.htmlFeaturesForSpan = HtmlFeatures(self.contentForSpan)
		self.htmlFeaturesForOutlinkToTextRatio =\
                        HtmlFeatures(self.contentForOutlinkToTextRatio)
	
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
		gtOutlinkFeat = {'aRatio': 2.5, 'tRatio': 2.333, 'atTxtRatio':0.714}
		gtOutlinkFeatStr = ','.join([str(round(x[1], 3))
                          for x in sorted(gtOutlinkFeat.items())])

	   	self.assertEqual(self.htmlFeaturesForOutlinkToTextRatio.outlinksToTextRatio(),gtOutlinkFeatStr)

	def test_summaryTagSpan(self):
		qTermsForSpan = ['altitude' ,'and','sickness']
		
		gtMinTag = {'spanA': 0.5, 'spanH': 0.5, 'spanB': 0.0, 'others': 0.0}
	    	gtSpanFeat = {'noSpan':2.0, 'avgSpanLen':3.5,'minSpanPos':0.6,\
		'maxSpanPos':0.8,'meanSpanPos':0.7}
		gtMinTagStr = ','.join([str(round(gtMinTag[y], 3))
                           for y in sorted(gtMinTag.keys())])
		gtSpanFeatStr = ','.join([str(round(gtSpanFeat[y], 3))
                           for y in sorted(gtSpanFeat.keys())])

    		gtResultString = gtMinTagStr + ',' + gtSpanFeatStr
    		self.assertEqual(self.htmlFeaturesForSpan.summaryTagSpan(qTermsForSpan),gtResultString)

	def test_tagCountAndPosition(self):
		gtHTagFeat = {'count': 2.0, 'minPos': 0.286, 'maxPos': 0.714,\
                        'meanPos': 0.5}
		gtHTagFeatStr = ','.join([str(round(y[1], 3)) for y in sorted(gtHTagFeat.items())])
		self.assertEqual(self.htmlFeaturesForOutlinkToTextRatio.tagCountAndPosition('h',set(self.qTerms)),gtHTagFeatStr)

		gtATagFeat = {'count': 2.0, 'minPos': 0.429, 'maxPos': 0.5,\
                        'meanPos': 0.464}
		gtATagFeatStr = ','.join([str(round(y[1], 3)) for y in sorted(gtATagFeat.items())])
		self.assertEqual(self.htmlFeaturesForOutlinkToTextRatio.tagCountAndPosition('a',set(self.qTerms)),gtATagFeatStr)

	def test_getTextFeature(self):
		gtMetrics = {'termsInTitle': 0.0, 'termsInURL': 0.0}
		gtMetricsStr = ','.join([str(round(gtMetrics[y], 3))
                        for y in sorted(gtMetrics.keys())])
                self.assertEqual(self.htmlFeatures.getTextFeature(self.qTerms,self.url),gtMetricsStr)

		qTermsMatch = ['SERVER']
		gtMetrics = {'termsInTitle': 1.0, 'termsInURL': 0.0}
		gtMetricsStr = ','.join([str(round(y[1], 3)) for y in\
                    sorted(gtMetrics.items())])
                self.assertEqual(self.htmlFeatures.getTextFeature(qTermsMatch,self.url),gtMetricsStr)
		
                qTermsMatch = ['topic']
		gtMetrics = {'termsInTitle': 0.0, 'termsInURL': 1.0}
		gtMetricsStr = ','.join([str(round(y[1], 3)) for y in\
                    sorted(gtMetrics.items())])
                self.assertEqual(self.htmlFeatures.getTextFeature(qTermsMatch,self.url),gtMetricsStr)

if __name__ == '__main__':
	unittest.main()
