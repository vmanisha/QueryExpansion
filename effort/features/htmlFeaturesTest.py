import unittest
import numpy as np
from htmlFeatures import HtmlFeatures
from utils import encodeUTF

class HtmlFeaturesTest(unittest.TestCase):

	def setUp(self):
		# page = open(argv[1], 'r').read()
		# content = encodeUTF(page).lower()
		url = 'test'
		qTerms = 'test'
		qLen = 10
		content = '<!DOCTYPE html> \
					<html> \
					<body> \
					<h1>My First Heading</h1> \
					<p>My first paragraph.</p> \
					</body> \
					</html>'

		self.htmlFeatures = HtmlFeatures(content)

	def test_tagDistribution(self):
		gtTagDist = {'h1':0.5,'h2':0,'h3':0,'h4':0,'h5':0,'h6':0,'table':0, \
		'div':0,'p':0.5,'b':0,'i':0,'a':0,'img':0,'li':0,'input':0,'strong':0}

		gtTagDistStr = ','.join([str(round(x[1], 3))
                           for x in sorted(gtTagDist.items())])

		self.assertEqual(self.htmlFeatures.tagDistribution(),gtTagDistStr)

	def test_outlinksWithDiffDomain(self):
		gtOutlinkDist = {'page': 0.0, 'same-domain': 0.0, 'diff-domain': 0.0}
	    gtOutLinkStr = ','.join([str(round(x[1], 3))
                           for x in sorted(gtOutlinkDist.items())])

		self.assertEqual(self.htmlFeatures.outlinksWithDiffDomain(self.url),gtOutLinkStr)

	def test_outlinksToTextRatio(self):
		gtOutlinkFeat = {'aRatio': 0.0, 'tRatio': 0.0, 'atTxtRatio': 0.0}
	    gtOutlinkFeatStr = ','.join([str(round(x[1], 3))
                          for x in sorted(gtOutlinkFeat.items())])

	   	self.assertEqual(self.htmlFeatures.outlinksToTextRatio(),gtOutlinkFeatStr)

	def test_summaryTagSpan(self):
		gtMinTag = {'spanA': 0.0, 'spanH': 0.0, 'spanB': 0.0, 'others': 0.0}
	    gtSpanFeat = {'noSpan':0.0, 'avgSpanLen':0.0,'minSpanPos':0.0,\
		'maxSpanPos':0.0,'meanSpanPos':0.0}

	    gtMinTagStr = ','.join([str(round(gtMinTag[y], 3))
                           for y in sorted(gtMinTag.keys())])
    	gtSpanFeatStr = ','.join([str(round(gtSpanFeat[y], 3))
                           for y in sorted(gtSpanFeat.keys())])

    	gtResultString = gtMinTagStr + ',' + gtSpanFeatStr
    	self.assertEqual(self.htmlFeatures.summaryTagSpan(self.qTerms,self.qLen),gtResultString)

    def test_tagCountAndPosition(self):
        gtHTagFeat = {'count': 0.0, 'minPos': 0.0, 'maxPos': 0.0, 'meanPos': 0.0}
	    gtHTagFeatStr = ','.join([str(round(y[1], 3)) for y in sorted(gtHTagFeat.items())])
	    #TODO: check why set?
		self.assertEqual(self.htmlFeatures.tagCountAndPosition('h',set(self.qTerms)),gtHTagFeatStr)	

        gtATagFeat = {'count': 0.0, 'minPos': 0.0, 'maxPos': 0.0, 'meanPos': 0.0}
	    gtATagFeatStr = ','.join([str(round(y[1], 3)) for y in sorted(gtATagFeat.items())])
	    self.assertEqual(self.htmlFeatures.tagCountAndPosition('a',set(self.qTerms)),gtATagFeatStr)	

	def test_getTextFeature(self):
		gtMetrics = {'termsInTitle': 0.0, 'termsInURL': 0.0}
	    gtMetricsStr = ','.join([str(round(gtMetrics[y], 3))
                        for y in sorted(gtMetrics.keys())])

    	self.assertEqual(self.htmlFeatures.getTextFeature(self.qTerms,self.url),gtMetricsStr)

if __name__ == '__main__':
	unittest.main()
