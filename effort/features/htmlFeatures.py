# -*- coding: utf-8 -*-
#tag distribution
#no of ads
#word to tag ratio
#outlinks
#outlink to text ratio
#No of headings
#size of font
#headings with query terms
#summary tag span

import sys
import lxml.html as lh
import urllib2
from lxml.html.clean import clean_html
from nltk.tokenize import word_tokenize
from nltk import sent_tokenize
import tldextract
from collections import Counter
import numpy as np
from utils import encodeUTF
from effort.features.textFeatures import getDocMetrics, getQueryDocMetrics, getQueryCount
from pattern.web import plaintext, URL


class HtmlFeatures:

  def __init__(self, content):

    #print len(content), type(content)
    self.pObj = lh.fromstring(content)
    self.toAvoidTags = set(['comment','noscript','style','meta',\
		'script','html','body','head','form','title'])
    self.toKeepTags = set(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'table', 'div',
                           'p', 'b', 'i', 'a', 'img', 'li', 'input', 'strong'])

  def tagDistribution(self):
    tagDist = {'h1':0,'h2':0,'h3':0,'h4':0,'h5':0,'h6':0,'table':0,\
		'div':0,'p':0,'b':0,'i':0,'a':0,'img':0,'li':0,'input':0,'strong':0}
    #textTags = 0.0
    totalTags = 0.0
    for ele in self.pObj.iter():
      if ele.tag in self.toKeepTags:
        #print ele.tag, 'Text',ele.text,'end'
        if ele.tag not in tagDist:
          tagDist[ele.tag] = 0.0
        tagDist[ele.tag] += 1.0
        totalTags += 1.0
    print totalTags
    print tagDist
    try:
      for entry in tagDist.keys():
        tagDist[entry] /= totalTags
    except:
      pass

    #print 'Tag dist' , tagDist
    #print 'Total tags', totalTags
    #tagDistStr = '\t'.join(['{0}:{1}'.format(x[0],str(x[1])) for x in sorted(tagDist.items())])
    #return tagDistStr+'\ttotalTags:'+str(totalTags)  #textTags/totalTags
    tagDistStr = ','.join([str(round(x[1], 3))
                           for x in sorted(tagDist.items())])
    return tagDistStr

  def outlinksWithDiffDomain(self, url):

    outlinkDist = {'page': 0.0, 'same-domain': 0.0, 'diff-domain': 0.0}
    for out in self.pObj.iterlinks():
      #ignore links other than <a>
      if out[1] != 'href':
        continue

      if out[2].startswith('htt'):
          if tldextract.extract(out[2]).domain in url:
            outlinkDist['same-domain'] += 1.0
          else:
            outlinkDist['diff-domain'] += 1.0
      elif out[2].startswith('#'):
          outlinkDist['page'] += 1.0
      else:
          outlinkDist['same-domain'] += 1.0

    try:
      total = sum(outlinkDist.values())

      for entry in outlinkDist.keys():
        # print entry, total, outlinkDist[entry], outlinkDist[entry]/total
        outlinkDist[entry] /= total
    except:
      pass
    #print 'Outlink domain dist ',outlinkDist
    outLinkStr = ','.join([str(round(x[1], 3))
                           for x in sorted(outlinkDist.items())])
    return outLinkStr

  def outlinksToTextRatio(self):
    #find all the words
    txt, atxt, txtCount, aCount = self.aToTextRatio(self.pObj)
    #print txt, atxt, txtCount, aCount

    splitt = word_tokenize(txt)
    splita = word_tokenize(atxt)

    wordt = Counter(splitt)
    worda = Counter(splita)

    outlinkFeat = {'aRatio': 0.0, 'tRatio': 0.0, 'atTxtRatio': 0.0}
    try:
      outlinkFeat['aRatio'] = len(worda) / aCount
      outlinkFeat['tRatio'] = len(wordt) / txtCount
      outlinkFeat['atTxtRatio'] = len(worda) / (len(wordt) * 1.0)
    except:
      pass
    retString = ','.join([str(round(x[1], 3))
                          for x in sorted(outlinkFeat.items())])
    return retString

    #aCount, txtCount, len(splita), len(worda), len(splitt), len(wordt)
    #aCount/txtCount , len(splita)/(len(splitt)*1.0), len(worda)/(len(wordt)*1.0)

  def aToTextRatio(self, node):
    #for this node calculate the following:
    txt = ''  #text itself
    atxt = ''  #a text
    txtCount = 0  #text nodes
    aCount = 0  #a nodes
    #print 'In',node.tag
    for child in node.iterchildren():
      #print 'Child',child.tag
      if child.tag == 'a':
        aCount += 1.0
        if child.text:
          ntxt = child.text.strip()
          if len(ntxt) > 1:
            atxt += ntxt + ' '

      else:
        if child.text:
          ntxt = child.text.strip()
          if len(ntxt) > 1:
            txt += ntxt + ' '
            txtCount += 1.0

        #get all the childrenlen stats
      ctxt, catxt, ctxtCount, caCount = self.aToTextRatio(child)
      #update current stats
      txt += ' ' + ctxt
      atxt += ' ' + catxt
      txtCount += ctxtCount
      aCount += caCount

      #print node.tag, txt, atxt, txtCount, aCount
    return txt, atxt, txtCount, aCount

    #def outlinksToTagRatio(self):

  def summaryTagSpan(self, queryTerms, qLen):
    #if you know the sentence structure and tag structure
    #sentences = 0.0
    tagPos = 0.0
    minTagPos = []
    minTag = {'spanA': 0.0, 'spanH': 0.0, 'spanB': 0.0, 'others': 0.0}
    spanFeat = {'noSpan':0.0, 'avgSpanLen':0.0,'minSpanPos':0.0,\
		'maxSpanPos':0.0,'meanSpanPos':0.0}

    currWord = 0.0
    allTuples = []
    for ele in self.pObj.iter():
      tagPos += 1.0
      toFind = {}
      hasFound = {}

      minBegin = -1.0
      minEnd = -1.0
      minWind = None

      for entry in queryTerms:
        toFind[entry] = 1.0
        hasFound[entry] = 0.0

      if ele.text and ele.tag not in self.toAvoidTags:
        begin = 0
        end = 0

        content = word_tokenize(ele.text)
        tlen = len(content)
        found = 0.0
        #print content, tlen
        if len(ele.text.strip()) > qLen:
          #print content
          while end < tlen:
            #print found, begin, end, toFind, hasFound
            eword = content[end]
            if eword not in toFind:
              end += 1
              continue
            hasFound[eword] += 1.0
            if hasFound[eword] <= toFind[eword]:
              found += 1.0
            #print found, begin, end, toFind, hasFound

            if found == len(queryTerms):  #found all
              bword = content[begin]
              while (bword not in toFind) or (hasFound[bword] > toFind[bword]):
                if bword in hasFound and hasFound[bword] > toFind[bword]:
                  hasFound[bword] -= 1.0
                begin += 1
                bword = content[begin]
              wind = end - begin + 1
              if minWind > wind or not minWind:
                minWind = wind
                minBegin = begin
                minEnd = end
                minTagPos.append(tagPos)
                if str(ele.tag).startswith('a'):
                  minTag['spanA'] += 1.0
                if str(ele.tag).startswith('h'):
                  minTag['spanH'] += 1.0
                if str(ele.tag).startswith('b'):
                  minTag['spanB'] += 1.0
                else:
                  minTag['others'] += 1.0

          currWord += tlen
          if minWind:
            allTuples.append(minWind)
            #print minWind, minBegin, minEnd , content[minBegin:minEnd+1]#, minTag, minTagPos		
            #print allTuples, minTag, minTagPos

    try:
      #print minTag, len(allTuples), queryTerms
      if sum(minTag.values()) > 0:
        for entry in minTag.keys():
          minTag[entry] /= sum(minTag.values())

      if len(allTuples) > 0:
        spanFeat['noSpan'] = len(allTuples)
        spanFeat['avgSpanLen'] = round(np.mean(allTuples), 2)

      if len(minTagPos) > 0:
        spanFeat['minSpanPos'] = min(minTagPos) / tagPos
        spanFeat['maxSpanPos'] = max(minTagPos) / tagPos
        spanFeat['meanSpanPos'] = round(np.mean(minTagPos) / tagPos, 3)
    except Exception as ex:
      print ex
      pass
    retString1 = ','.join([str(round(minTag[y], 3))
                           for y in sorted(minTag.keys())])
    retString2 = ','.join([str(round(spanFeat[y], 3))
                           for y in sorted(spanFeat.keys())])

    return retString1 + ',' + retString2  #allTuples, minTag, minTagPos

  def tagCountAndPosition(self, tagPrefix, queryTerms):
    tagCount = {}
    tagPos = []
    tagFeat = {'count': 0.0, 'minPos': 0.0, 'maxPos': 0.0, 'meanPos': 0.0}
    pos = 0.0
    for ele in self.pObj.iter():
      pos += 1
      if str(ele.tag).startswith(tagPrefix):
        if ele.text:
          split = set(word_tokenize(ele.text.lower().strip()))
          if len(queryTerms & split) > 0:
            if ele.tag not in tagCount:
              tagCount[ele.tag] = 0.0
            tagPos.append(pos)
            tagCount[ele.tag] += 1.0

    try:
      tagFeat['count'] = sum(tagCount.values())
      if len(tagPos) > 0:
        tagFeat['minPos'] = round(min(tagPos) / pos, 3)
        tagFeat['maxPos'] = round(max(tagPos) / pos, 3)
        tagFeat['meanPos'] = round(np.median(tagPos) / pos, 3)
    except:
      pass

    retString = ','.join([str(round(y[1], 3)) for y in sorted(tagFeat.items())])
    return retString

  def getTextFeature(self, qTerms, url):
    metrics = {'termsInTitle': 0.0, 'termsInURL': 0.0}

    for term in qTerms:
      if term in url:
        metrics['termsInURL'] += 1.0

    for ele in self.pObj.iter():
      if str(ele.tag).startswith('title'):
        if ele.text:
          for term in qTerms:
            if term in ele.text:
              metrics['termsInTitle'] += 1.0
    retString = ','.join([str(round(metrics[y], 3))
                          for y in sorted(metrics.keys())])
    return retString

  def getAllFeatures(self, url, qTerms, qLen):
    return self.tagDistribution()+','+self.outlinksToTextRatio()+','+\
		self.outlinksWithDiffDomain(url)+','+self.summaryTagSpan(qTerms, qLen)+\
		','+self.tagCountAndPosition('h',set(qTerms))+','+\
		self.tagCountAndPosition('a',set(qTerms))+','+\
		self.getTextFeature(qTerms,url)

'''
argv[1] = file containing queries. Each line has query id and query.
argv[2] = file containing query and url. Each line has query id and url.
argv[3] = folder containing the html dump of urls.
argv[4] = Output file containing the features.
'''
def main(argv):
  queryUrlFeatures = None  #{}
  pid = 0

  #user_agent = 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_4; en-US) AppleWebKit/534.3 (KHTML, like Gecko) Chrome/6.0.472.63 Safari/534.3'
  #headers = { 'User-Agent' : user_agent }

  #oFile = open('url_pid_mapping.txt','w')
  fFile = open(argv[4], 'w')  #open('all_features_combined.txt','w')
  k = -1

  qMap = {}
  for line in open(argv[1], 'r'):
    split = line.strip().split('\t')
    qMap[split[0]] = split[1]

  #print string
  for line in open(argv[2], 'r'):
    split = line.split()
    query = qMap[split[0].strip()]

    qTerms = []
    for t in query.split():
      if len(t.strip()) > 1:
        qTerms.append(t)
    link = split[1].strip()
    key = query + '\t' + link

    if pid == 0:
      #print line.strip(),
      tagDist = {'h1':0,'h2':0,'h3':0,'h4':0,'h5':0,'h6':0,'table':0,\
			'div':0,'p':0,'b':0,'i':0,'a':0,'img':0,'li':0,'input':0,'strong':0}
      outlinkDist = {'page': 0.0, 'same-domain': 0.0, 'diff-domain': 0.0}
      outlinkFeat = {'aRatio': 0.0, 'tRatio': 0.0, 'atTxtRatio': 0.0}
      minTag = {'spanA': 0.0, 'spanH': 0.0, 'spanB': 0.0, 'others': 0.0}
      spanFeat = {'noSpan':0.0, 'avgSpanLen':0.0,'minSpanPos':0.0,\
			'maxSpanPos':0.0,'avgSpanPos':0.0}
      metrics = {'queryFreq':0.0, 'avgTF':0.0,'minTF':0.0, 'maxTF':0.0,\
			'minWPos':0.0,'maxWPos':0.0,'avgWPos':0.0}
      metricsT = {'termsInTitle': 0.0, 'termsInURL': 0.0}

      print ','.join([x for x in sorted(tagDist.keys())]) + ',',
      print ','.join([x for x in sorted(outlinkFeat.keys())]) + ',',
      print ','.join([x for x in sorted(outlinkDist.keys())]) + ',',
      print ','.join([x for x in sorted(minTag.keys())]) + ',',
      print ','.join([x for x in sorted(spanFeat.keys())]) + ',',
      for pre in ['A', 'H']:
        tagFeat = {'count': 0.0, 'minPos': 0.0, 'maxPos': 0.0, 'meanPos': 0.0}
        print ','.join([x + pre for x in sorted(tagFeat.keys())]) + ',',
      print ','.join([x for x in sorted(metricsT.keys())]) + ',',

      for pre in ['doc_', 'sum_']:
        textMetrics = {'sent':0.0, 'char':0.0,'words':0.0,'period':0.0,\
				'ARI':0.0,'CLI':0.0, 'LIX':0.0,'sentWithQueryTerm':0.0}
        print ','.join([pre + x for x in sorted(textMetrics.keys())]) + ',',
      print ','.join([x for x in sorted(metrics.keys())]) + ',',

      print
      pid += 1
      continue

    #TODO: check for cases of sentences and query terms everywhere
    if pid > k:
      try:
        #fetch the content

        #req = urllib2.Request(link,  None, headers)
        #response = urllib2.urlopen(req)
        #page = response.read()
        #page = encodeUTF(page)
        page = open(argv[3] + '/' + link + '.txt', 'r').read()  #response.read()
        page = encodeUTF(page).lower()

        #open(argv[2]+'/'+str(pid)+'.txt','w').write(page)
        #oFile.write(query+','+link+','+argv[2]+str(pid)+'.txt\n')

        #page = open(link.strip(),'r').read()
        queryUrlFeatures = HtmlFeatures(page.lower())

        toWrite = qMap[split[0]]+','+split[1]+','+ \
				queryUrlFeatures.getAllFeatures(link,qTerms,len(query))

        pageText = plaintext(page)
        sentences = sent_tokenize(pageText)
        #print link, len(pageText), len(sentences)
        metrics = getDocMetrics(query.lower(), sentences)
        queryDocMetrics = getQueryDocMetrics(query.lower(), sentences)
        textMetrics = getQueryCount(query, sentences) #TODO: query.lower()?

        #print metrics, queryDocMetrics
        string = ','.join(str(round(val[1], 3))
                          for val in sorted(metrics.items()))
        string += ','
        string += ','.join(str(round(val[1], 3))
                           for val in sorted(queryDocMetrics.items()))
        string += ','
        string += ','.join(str(round(val[1], 3))
                           for val in sorted(textMetrics.items()))

        fFile.write(toWrite + ',' + string + '\n')

        #print toWrite+','+string
      except Exception as ex:
        print ex, '\tERROR\t', line
    pid += 1
  #writeFeatures(argv[2],queryUrlFeatures)
  #oFile.close()


if __name__ == '__main__':
  main(sys.argv)

  #print splitt, splita, wordt, worda, len(splita),len(splitt), len(worda),len(wordt)
  #print aCount/txtCount, len(splita)/(len(splitt)*1.0), len(worda)/(len(wordt)*1.0)
  #retString = 'aCount:'+str(aCount)+'\ttxtCount:'+str(txtCount)+'\tuniqueA:'+\
  #str(len(worda))+'\tallA:'+str(len(splita))+'\tuniqueT:'+ str(len(wordt))+\
  #'\tallT:'+str(len(splitt))

  #retString+= '\tminSpanPos:'+str(minT)+'\tmaxSpanPos:'+str(maxT)+\
  #			'\tmeanSpanPos:'+str(round(np.mean(minTagPos),2))+\
  #			'\tmedSpanPos:'+str(round(np.median(minTagPos),2))
