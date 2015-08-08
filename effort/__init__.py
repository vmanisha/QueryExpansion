# -*- coding: utf-8 -*-
import sys, os
#from plots import plotMultipleSys,plotOneHist,plotHist
from collections import Counter
import numpy as np
import itertools
from stats import computeKappa
import random
import urllib2
from scipy.stats import chisquare


#load features
def loadFeatures(dirName, sep, fInd, labelInd):
  features = {}
  j = 0
  queryDoc = {}
  #if last index label
  for fileName in os.listdir(dirName):
    for line in open(dirName + '/' + fileName, 'r'):
      split = line.strip().split(sep)
      if j == 0:
        j += 1
        if labelInd == -1:
          labelInd = len(split) - 1
        #print split[fInd], fInd, labelInd
        continue
      q = split[0].strip()
      doc = split[1].strip()
      label = split[labelInd]
      ind = q + '\t' + doc
      if ' ' in q and (int(label) > 0):

        if q + label not in queryDoc:
          queryDoc[q + label] = []
        if doc not in queryDoc[q + label]:
          queryDoc[q + label].append(doc)

      if ind not in features:
        features[ind] = {'feat': [], 'label': -1}
        try:
          for i in range(fInd, len(split)):
            if i != labelInd:
              features[ind]['feat'].append(float(split[i]))
            else:
              features[ind]['label'] = int(label)
        except:
          pass
          print line
      else:
        pass
        #print 'Found line'
        #print 'Query in features', ind, features[ind]
        #print 'Line  in features', ind, split

  return features, queryDoc

#plot the distribution of something with respect to something


def plotFeatureWithLabel(featInd, features):
  featWithLabel = {}
  urlMapping = {}
  i = 1
  for key, feat in features.iteritems():
    label = key[:key.find('\t')] + '\t' + str(feat['label'])
    #print key, feat, 'LABEL',label

    if label not in featWithLabel:
      featWithLabel[label] = {}
    #if 'words' in key:
    #	print key, featInd, i,  feat['feat'][featInd]
    featWithLabel[label][i] = feat['feat'][featInd]
    urlMapping[i] = key[key.find('\t') + 1:]
    i += 1
  #print featWithLabel
  plotMultipleSys(featWithLabel, 'docId', 'featVal',
                  'featVal' + str(featInd) + '.png', 'Feature Values vs label')
  return featWithLabel, urlMapping


def findPairs(featWithLabel, queryDoc, label_pref, toComplete):
  toCompare = [0, 2, 4, 5, 7]
  done = {}
  result = []
  for entry, docList in queryDoc.items():
    #print entry, docList

    entry = entry[:-1]
    for pair in itertools.combinations(docList, 2):
      feat1 = featWithLabel[entry + '\t' + pair[0]]['feat']
      feat2 = featWithLabel[entry + '\t' + pair[1]]['feat']
      count = {1: 0.0, 2: 0.0}
      for ind in toCompare:
        #print entry, pair, ind, feat1[ind], feat2[ind]
        if feat1[ind] > 0.0 and feat2[ind] > 0.0:
          percent = (feat1[ind] - feat2[ind]) / feat1[ind]
          if percent > 0.0:
            count[1] += 1.0
          if percent < 0.0:
            count[2] += 1.0
          #print entry, pair, ind, percent
      if count[1] != count[2] and (count[1] - count[2] > 2 or
                                   count[2] - count[1] > 2):
        if pair[0] not in done and pair[1] not in done:
          #print entry, pair, count
          result.append((entry, pair[0], pair[1]))
          done[pair[0]] = 1.0
          done[pair[1]] = 1.0

  for entry in toComplete:
    for triple in result:
      if entry[0] in triple and entry[1] in triple and \
			entry[0] not in done and entry[1] not in done:
        done[entry[0]] = 1.0
        done[entry[1]] = 1.0
        result.append(entry)

  for entry in result:
    found = False
    for triple in label_pref.keys():
      if entry[0] in triple and entry[1] in triple:
        found = True
        break

    for triple in toComplete:
      if entry[0] in triple and entry[1] in triple:
        found = False
        break

    if not found and (entry[1] not in entry[2] and entry[2] not in entry[1]):
      print entry[0], '\t', entry[1], '\t', entry[2]
      #else:
      #	print entry, pair, count


def findPreference(features, labelFile):

  label_pref = {}
  for line in open(labelFile, 'r'):
    split = line.lower().strip().split(',')
    #try:
    #featString1 = ','.join([str(round(x,2)) for x in features[split[0]+'\t'+split[2]]['feat']])
    #featString2 = ','.join([str(round(x,2)) for x in features[split[0]+'\t'+split[3]]['feat']])
    ##print line.strip()+','+featString1+','+ featString2
    #except:
    #pass
    #key = (split[0],split[2],split[3])#+'\t'+split[1]
    #key = (split[2],split[3],split[4])
    key = (split[3], split[4], split[5])
    #print key, split[-1]
    if key not in label_pref:
      label_pref[key] = {0: 0.0, 1: 0.0, -1: 0.0}
    if 'left' in split[-1]:
      #print 'left', split[2], split[3]
      label_pref[key][0] += 1.0
    elif 'right' in split[-1]:
      #print 'right', split[2], split[3]
      label_pref[key][1] += 1.0
      #elif 'both' in split[-1]:
      #	label_pref[key][-1]+=1.0

      pass
      #print line
      #doc = None

  print 'Pref pairs ', len(label_pref)

  docPref = {}
  for triple, pref in label_pref.items():
    #print triple, pref
    q = triple[0].strip()
    doc1 = triple[1].strip()
    doc2 = triple[2].strip()
    if pref[0] > pref[1]:  # and pref[0] > pref[-1]:
      docPref[triple] = 'left'
      #if pref[0] == 3 and ' ' in q:
      #	print triple, pref
      #docPref[triple]= [1,0]
      #docPref[q+'\t'+doc1] = 'pref'
      #docPref[q+'\t'+doc2] = 'not-pref'
    elif pref[1] > pref[0]:  #and pref[1] > pref[-1]:
      docPref[triple] = 'right'  #[0,1]
      #if pref[1] == 3 and ' ' in q:
      #	print triple, pref

      #docPref[triple]= [0,1]

      #elif pref[-1] > pref[0] : #and pref[-1] > pref[1]:
      #		docPref[triple]='none'
      #docPref[triple]= [-1,-1]

    else:
      print 'No majority ', triple, pref

    #if triple in docPref:	
    #	print docPref[triple], pref
    #docPref[q+'\t'+doc2] = 'pref'
    #docPref[q+'\t'+doc1] = 'not-pref'
    #else:
    #docPref[q+'\t'+doc2] = 'cant-judge'
    #docPref[q+'\t'+doc1] = 'cant-judge'
  print len(docPref)
  effort_pref = {'high': 0.0, 'low': 0.0}
  docType = {}
  #for triple, pref in label_pref.items():
  #q = triple[0].strip()
  #doc1 = triple[1].strip()
  #doc2 = triple[2].strip()
  #fcount = {0:0, 1:0} #how many times 0 or 1 is high effort

  #for find in [0,2,4,5,7]:
  #try :
  #d1v1 = features[triple[0]+'\t'+doc1]['feat'][find]
  #d2v1 = features[triple[0]+'\t'+doc2]['feat'][find]
  #if d1v1 > d2v1:
  #fcount[0]+=1.0
  #else:
  #fcount[1]+=1.0
  #
  #except:
  #
  #pass

  #if fcount[0] > fcount[1]:
  #docType[q+'\t'+doc1]='high'
  #docType[q+'\t'+doc2]='low'
  #
  #elif fcount[1] > fcount[0]:
  #docType[q+'\t'+doc1]='low'
  #docType[q+'\t'+doc2]='high'
  #else:
  #docType[q+'\t'+doc1]='cant-judge'
  #docType[q+'\t'+doc2]='cant-judge'

  ##for entry, count in docType.items():
  #	print entry, count
  return label_pref, docType, docPref


def findPairsWithMissingLabels(fileName):
  count = {}
  for line in open(fileName, 'r'):
    split = line.split(',')
    key = split[1] + '\t' + split[2]
    if key not in count:
      count[key] = 0

    count[key] += 1

  for entry in sorted(count.items(), reverse=True, key=lambda x: x[1]):
    if entry[1] < 3:
      print entry[1], '\t', entry[0]


def mapLabels(fileName):
  gradeMap = {'easy':1, 'v-easy':1, 'some-diff':0, 'v-diff':0, 'yes':1, \
	'no':0, 'somewhat':0, 'high-rel':1, 'rel':1, 'non-rel':0, 'some-rel':1}

  queryUrlLabels = {}

  #find the majority
  for line in open(fileName, 'r'):
    split = line.strip().split(',')
    key = split[1] + '\t' + split[2]
    if key not in queryUrlLabels:
      queryUrlLabels[key] = {}

    for i in range(3, len(split)):
      split[i] = split[i].strip()
      if len(split[i]) > 0:
        if i not in queryUrlLabels[key]:
          queryUrlLabels[key][i] = []
        if split[i] in gradeMap:
          queryUrlLabels[key][i].append(gradeMap[split[i]])
        else:
          print 'Did not find ', split[i], key

  maxQULabels = {}

  for entry, llist in queryUrlLabels.items():
    print entry, '\t', llist

    try:
      maxQULabels[entry] = {}

      for ind in llist.keys():
        maxQULabels[entry][ind] = Counter(llist[ind]).most_common(1)[0][0]
    except:

      pass

  toReturn = {}
  for entry, fval in maxQULabels.items():
    fstr = '\t'.join(['{0}:{1}'.format(x[0], x[1]) for x in fval.items()])
    #print entry,'\t'
    toReturn[entry] = fstr
  return toReturn


def maxLabels(fileName):
  queryUrlLabels = {}
  k = 0
  head = None
  #find the majority
  for line in open(fileName, 'r'):
    split = line.strip().split(',')
    #key = split[1]+'\t'+ split[2]
    key = split[2].strip() + '\t' + split[3].strip()  #if worker id and time is present too
    #print key
    if key not in queryUrlLabels:
      queryUrlLabels[key] = {}

    for i in range(4, len(split)):
      split[i] = split[i].strip()
      if len(split[i]) > 0:
        if i not in queryUrlLabels[key]:
          queryUrlLabels[key][i] = []
        queryUrlLabels[key][i].append(split[i])
    if k == 0:
      head = split[5:]
      k += 1

  maxQULabels = {}

  for entry, llist in queryUrlLabels.items():
    #print entry,'\t', llist

    try:
      maxQULabels[entry] = {}

      for ind in llist.keys():
        mcom = Counter(llist[ind]).most_common(1)
        if mcom[0][1] > 0:
          maxQULabels[entry][ind] = mcom[0][0]
        else:
          maxQULabels[entry][ind] = 'cant-judge'
    except:

      pass
  i = 0
  for entry, fval in maxQULabels.items():
    if i == 0:
      print 'Query,URL,', ','.join([head[x[0] - 5] for x in sorted(fval.items())
                                   ])
      i += 1
    print entry, ',', ','.join([x[1] for x in sorted(fval.items())])

  return maxQULabels


def pairwiseEffort(fileName, docPref):
  data = {}
  gradeMap = {'easy':2, 'v-easy':3, 'some-diff':1, 'v-diff':0, 'yes':2, \
	'no':0, 'somewhat':1, 'high-rel':3, 'rel':2, 'non-rel':0, 'some-rel':1}

  #gradeMap = {'easy':1, 'v-easy':1, 'some-diff':0, 'v-diff':0, 'yes':1, \
  #'no':0, 'somewhat':0, 'high-rel':1, 'rel':1, 'non-rel':0, 'some-rel':1}

  #dpairs = [(0,1),(0,2),(0,4),(1,2),(1,4),(2,4),(1,3	)]
  head = None
  i = 1
  #filename == effort values file
  for line in open(fileName, 'r'):
    split = line.strip().lower().split(',')
    key = split[0].strip() + '\t' + split[1].strip()
    q = split[0].strip()
    doc = split[1].strip()

    #print key, line
    #if key in docType and key in features:
    #	print 'FEAT '+line.strip()+','+str(features[key]['label'])+','+ ','.join([str(x) for x in features[key]['feat']])+','+docType[key]
    if 'query' in key:
      head = split[2:]
      print 'HEAD in pair ', head
    else:
      if 'cant-judge' not in split[2:]:
        data[q + '\t' + doc] = []
        for entry in split[2:]:
          data[q + '\t' + doc].append(gradeMap[entry.strip()])
      else:
        print 'Cant judge ', line.strip()
    i += 1

  prefGrade = {}
  samePref = {}
  nonePref = {}
  count = 0.0
  found = {}
  effortLabel = {}

  for triple, pref in docPref.items():
    k1 = triple[0].strip() + '\t' + triple[1].strip()
    k2 = triple[0].strip() + '\t' + triple[2].strip()
    if k1 in data and k2 in data:
      found[triple] = 1.0  #, pref
      #for i in range(len(head)):
      #	if i not in effortLabel:
      #		effortLabel[i] = {'same':0.0, 'diff':0.0}
      #		prefGrade[i] = {'low':0.0, 'high':0.0, 'none':0.0, 'same':0.0}
      #if pref == 'left':
      #if data[k1][i] < data[k2][i]:
      #prefGrade[i]['low']+=1.0
      #elif data[k1][i] > data[k2][i]:
      #prefGrade[i]['high']+=1.0
      #else:
      #prefGrade[i]['same']+=1.0
      #elif pref == 'right':
      #if data[k1][i] > data[k2][i]:
      #prefGrade[i]['low']+=1.0
      #elif data[k1][i] < data[k2][i]:
      #prefGrade[i]['high']+=1.0
      #else:
      #prefGrade[i]['same']+=1.0

      #elif pref == 'none':
      #prefGrade[i]['none']+=1.0
      for i in range(len(head)):
        if i not in effortLabel:
          effortLabel[i] = {'same': 0.0, 'diff': 0.0}
          prefGrade[i] = {'low': 0.0, 'high': 0.0, 'none': 0.0, 'same': 0.0}

        if data[k1][i] == data[k2][i]:
          effortLabel[i]['same'] += 1.0
          prefGrade[i]['same'] = effortLabel[i]['same']

        else:
          effortLabel[i]['diff'] += 1.0
          #print triple, pref
          #samePref[i] = {}
          #nonePref[i] = {'left':0.0, 'right':0.0, 'same':0.0}
          if pref == 'left':
            if data[k1][i] < data[k2][i]:
              prefGrade[i]['low'] += 1.0
            elif data[k1][i] > data[k2][i]:
              prefGrade[i]['high'] += 1.0
          elif pref == 'right':
            if data[k1][i] > data[k2][i]:
              prefGrade[i]['low'] += 1.0
            elif data[k1][i] < data[k2][i]:
              prefGrade[i]['high'] += 1.0
          elif pref == 'none':
            prefGrade[i]['none'] += 1.0

      count += 1.0
    else:
      #print triple
      if ' ' in triple[0] and (k1 in data or k2 in data):
        print triple, k1 in data, k2 in data
      #toComplete.append(triple)

  print effortLabel

  for ind, values in prefGrade.items():
    for entry, val in values.items():
      print head[ind], entry, val, count  #, val/(values['high']+values['low'])# +values['none'])

    #if entry == 'same':
    #	print head[ind], samePref[ind]
    #if entry == 'none':
    #	print head[ind], nonePref[ind]
  return prefGrade, head, count


def plotValues(fileName, docType, docPref, features):
  data = {}

  #dpairs = [(0,1),(0,2),(0,4),(1,2),(1,4),(2,4),(1,3	)]
  head = None
  i = 1
  for line in open(fileName, 'r'):
    split = line.strip().split(',')
    key = split[0].strip() + '\t' + split[1].strip()
    #print key, line
    #if key in docType and key in features:
    #	print 'FEAT '+line.strip()+','+str(features[key]['label'])+','+ ','.join([str(x) for x in features[key]['feat']])+','+docType[key]
    if 'Query' in key:
      head = split[2:]
      print 'HEAD ', head
    else:
      data[split[0].strip() + '\t' + split[1].strip()] = split[2:]
    i += 1

  #print tables
  returnProb(head, data, docType, {})  #,{'high':{},'low':{}})
  returnProb(head, data, docPref, {})  #,{'pref':{},'not-pref':{}})


def returnProb(head, data, docType, prob1={}):
  fcount = {}
  print 'FINDING PROB !!!', prob1
  for entry, val in data.items():
    if entry in docType:
      dtype = docType[entry]

      #high and low counts
      if dtype not in fcount:
        fcount[dtype] = 0.0
      fcount[dtype] += 1
      #p(feat=1,0| effort = high,low)
      for i in range(len(val)):
        if i not in prob1:
          prob1[i] = {}
        if val[i] not in prob1[i]:
          prob1[i][val[i]] = {}
        if dtype not in prob1[i][val[i]]:
          prob1[i][val[i]][dtype] = 0.0
        prob1[i][val[i]][dtype] += 1.0

      #calculates (effort|feature)
      #for i in range(len(val)):
      #if i not in prob1[dtype]:
      #prob1[dtype][i] = {0:0.0,1:0.0}
      #prob1[dtype][i][int(val[i])]+= 1
      #
      #if i not in fcount:
      #fcount[i]={0:0.0,1:0.0}
      #fcount[i][int(val[i])]+=1.0	
      #else:
      #print 'Nahi hai', entry
  print fcount
  print prob1
  #for entry, value in docType.items():	
  #	print entry, value

  for entry, vdict in prob1.items():
    #print entry, vdict
    print head[entry], vdict
    for feat, fdict in vdict.items():
      for val, count in fdict.items():
        #print entry, head[feat], val, count, fcount[feat][val], count/fcount[feat][val]
        print head[entry], feat, val, count, fcount[val], count / fcount[val]


def fromPairsToList(fileName):
  for line in open(fileName):
    split = line.split('\t')
    print split[0].strip() + ',' + split[1].strip()
    print split[0].strip() + ',' + split[2].strip()


def loadEffortLabels(fileName):
  gradeMap = {'easy':2, 'v-easy':3, 'some-diff':1, 'v-diff':0, 'yes':2, \
'no':0, 'somewhat':1, 'high-rel':3, 'rel':2, 'non-rel':0, 'some-rel':1, 'cant-judge':-1}

  effortLabels = {}
  for line in open(fileName):
    split = line.strip().split(',')
    try:
      effortLabels[split[0].strip()+'\t'+split[1].strip()] = \
			'\t'.join([ str(gradeMap[x.strip()]) for x in split[2:]])
    except:
      pass
      #effortLabels[split[0].strip()+'\t'+split[1].strip()] = '\t'.join(split[2:])

  return effortLabels


def combineAll(features, docPref, docTypes, effortLabels):

  for entry, eDict in features.items():
    featString = entry + '\t' + str(eDict['label']) + '\t' + '\t'.join([str(
        round(x, 2)) for x in eDict['feat']])
    if entry in docTypes and entry in docPref and entry in effortLabels:
      print featString + '\t' + docTypes[entry] + '\t' + docPref[
          entry
      ] + '\t' + effortLabels[entry]
    #else:
    #if ' ' in entry and (entry in docTypes or entry in docPref or entry in effortLabels):
    #	print 'ERROR ',entry,entry in docTypes ,entry in docPref , entry in effortLabels


def prepareFeaturesPairwise(docPref, featFile):
  featList = {}
  gradeMap = {'easy':2, 'v-easy':3, 'some-diff':1, 'v-diff':0, 'yes':2, \
	'no':0, 'somewhat':1, 'high-rel':3, 'rel':2, 'non-rel':0, 'some-rel':1, \
	'cant-judge':-1, 'not-pref':0, 'pref':1}

  head = None
  for line in open(featFile, 'r'):
    split = line.lower().strip().split(',')
    if 'query' in split:
      head = split[2:]
    else:
      if 'cant' not in line:
        query = split[0]
        url = split[1]
        key = query + '\t' + url
        featList[key] = []
        for entry in split[2:]:
          try:
            featList[key].append(float(entry))
          except:
            featList[key].append(gradeMap[entry])
      #pri
      #featList[key]	 = split[2:]

      #print 'q-u1-u2,', ','.join([ x.strip()+'_P1' for x in head	])\
      #,',',','.join([ x.strip()+'_P2' for x in head]),',',','.join([ x.strip()+'_Diff' for x in head])


  print 'q-u1-u2,'+ ','.join([ x.strip()+'_P1' for x in head ])\
	+','+','.join([ x.strip()+'_P2' for x in head]),',',','.join([ x.strip()+'_Diff' for x in head])

  for triple, pref in docPref.items():
    k1 = triple[0] + '\t' + triple[1]
    k2 = triple[0] + '\t' + triple[2]
    if k1 in featList and k2 in featList:
      f1 = featList[k1]
      f2 = featList[k2]
      print '\t'.join(triple),
      for i in range(len(f1)):
        print ',', f1[i],
        #try:
        #print ',',float(f1[i]),
        #except:
        #print ',',gradeMap[f1[i]],
        #print ',',pref[0],

      for i in range(len(f2)):
        print ',', f2[i],
        #try:
        #print ',',float(f2[i]),
        #except:
        #print ',',gradeMap[f2[i]],
        #print ',',pref[1],

      for i in range(len(f1)):
        print ',', float(f1[i]) - float(f2[i]),

      #print pref
      print ',', pref[0] - pref[1]


def findValByWorker(fileName):
  head = None
  data = {}
  kapData = {}
  #gradeMap = {'easy':1, 'v-easy':1, 'some-diff':0, 'v-diff':0, 'yes':1, \
  #'no':0, 'somewhat':0, 'high-rel':1, 'rel':1, 'non-rel':0, 'some-rel':1}

  gradeMap = {
      'Prefer Right': 1,
      'Prefer Left': 0,
      'Both Irrelevant': 2
  }  #,'Skip':3}
  for line in open(fileName, 'r'):
    split = line.strip().split(',')
    if 'Input.query' in line:
      head = split
      for i in range(4, len(split)):
        print split[i],
        head[i] = split[i][split[i].find('.') + 1:].strip()

    if split[1] not in data:
      data[split[1]] = {}
    #key = split[2]+'\t'+split[3]
    #key = split[3]+'\t'+split[4]+'\t'+split[5]
    key = split[2] + '\t' + split[3] + '\t' + split[4]
    if 'Skip' not in line:  # and 'Both' not in line:
      for i in range(5, len(split)):
        if key not in kapData:
          kapData[key] = {}

        if head[i] not in data[split[1]]:
          #data[split[1]][head[i]] = {'easy':0, 'v-easy':0, 'some-diff':0, \
          #'v-diff':0, 'yes':0, 'no':0, 'somewhat':0, 'high-rel':0, \
          #'rel':0, 'non-rel':0, 'some-rel':0, 'cant-judge':0}
          data[split[1]][head[i]] = {1: 0.0, 0: 0.0, 2: 0.0}  #, 3:0.0}
        try:
          val = gradeMap[split[i]]
          if val not in data[split[1]][head[i]]:
            data[split[1]][head[i]][val] = 0.0
          data[split[1]][head[i]][val] += 1.0
        except:
          print 'Error', split
          pass

        if head[i] not in kapData[key]:
          #kapData[key][head[i]] = {'easy':0, 'v-easy':0, 'some-diff':0, \
          #'v-diff':0, 'yes':0, 'no':0, 'somewhat':0, 'high-rel':0, \
          #'rel':0, 'non-rel':0, 'some-rel':0, 'cant-judge':0}
          kapData[key][head[i]] = {1: 0.0, 0: 0.0, 2: 0.0}  #, 3:0.0}
        try:
          val = gradeMap[split[i]]
          if val not in kapData[key][head[i]]:
            kapData[key][head[i]][val] = 0.0
          kapData[key][head[i]][val] += 1.0
        except:
          print 'Error ', split
          pass

  #valsHead = {'relevance':{'rel':0, 'non-rel':0, 'some-rel':0,'high-rel':0},\
  #'happy':{'yes':0, 'no':0, 'somewhat':0, 'cant-judge':0},\
  #'find':{'easy':0, 'v-easy':0, 'some-diff':0,'v-diff':0},\
  #'understand':{'easy':0, 'v-easy':0, 'some-diff':0,'v-diff':0},\
  #'read':{'easy':0, 'v-easy':0, 'some-diff':0,'v-diff':0}}
  print head
  valsHead = {'preference': {1: 0.0, 0: 0.0, 2: 0.0}}  #,3:0.0}}
  #'relevance':{1:0.0, 0:0.0},
  #'happy':{1:0.0, 0:0.0},
  #'find':{1:0.0, 0:0.0},
  #'understand':{1:0.0, 0:0.0},
  #'read':{1:0.0, 0:0.0}}

  for head in ['preference']:  #'relevance','happy','find','read','understand']:
    print '-------------------' + head + '-------------------'
    print
    #print 'url', '\t'.join([x for x in sorted(vals.keys())]);
    i = 0
    mat = []

    for entry, headStats in kapData.items():
      print entry, headStats

      m = [headStats[head][val] for val in sorted(valsHead[head].keys())]
      if sum(m) != 3:
        continue
      mat.append(m)

      #print mat
    print computeKappa(mat)

    #for val in sorted(vals.keys()):
    #	print '\t', headStats[head][val],
    #print


def randomComparison(fileName, indexA):
  #load labels
  #gradeMap = {'easy':1, 'v-easy':1, 'some-diff':0, 'v-diff':0, 'yes':1, \
  #'no':0, 'somewhat':0, 'high-rel':1, 'rel':1, 'non-rel':0, 'some-rel':1,\
  # 'cant-judge':-1}

  gradeMap = {'easy':2, 'v-easy':3, 'some-diff':1, 'v-diff':0, 'yes':2, \
	'no':0, 'somewhat':1, 'high-rel':3, 'rel':2, 'non-rel':0, 'some-rel':1,\
	 'cant-judge':-1,'prefer left':0,'prefer right':1}

  labels = {}
  li = 0
  for line in open(fileName, 'r'):
    if 'cant-judge' not in line:
      split = line.lower().strip().split(',')
      #key = split[0]+'\t'+split[1]
      #print key
      #key = split[2]+'\t'+ split[3]
      #print key
      #key = split[2]+'\t'+ split[3]+'\t'+ split[4]
      key = split[3] + '\t' + split[4] + '\t' + split[5]
      if key not in labels:
        labels[key] = []
      if li == 0:
        print split[indexA]
        li += 1
      try:
        labels[key].append(gradeMap[split[indexA]])  #gradeMap[split[indexA]])
      except:
        print split[indexA]
  matchA = []
  mismatchA = []
  count = 0.0
  for i in range(100):
    match = 0
    mismatch = 0
    count = 0.0
    for key in labels.keys():
      #print labels[key]
      if len(labels[key]) > 2:
        r = random.sample(labels[key], 2)
        #print r
        #binarize
        if r[0] == r[1]:
          match += 1
        else:
          mismatch += 1

        #print 'left' not in r[0] and 'right' not in r[0],
        #if ('left' not in r[0] and 'right' not in r[0]) or \
        #('left' not in r[1] and 'right' not in r[1]):
        #	continue

        count += 1
      #else
      #	print key, labels[key]

    matchA.append(match / count)
    mismatchA.append(mismatch / count)

  avgMatch = sum(matchA) / (1.0 * 100)
  avgMisMatch = sum(mismatchA) / (1.0 * 100)

  print matchA, mismatchA
  print avgMatch, avgMisMatch, len(labels), count
  #print avgMatch/count,avgMisMatch/count


def effortPrefInt(file1, file2):
  #load the effort labels
  maxLabel = maxLabels(file1)

  #load the the pref labels
  label_pref, docType, docPref = findPreference({'features': 0.0}, file2)

  user_agent = ('Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_4; en-US) '
                'AppleWebKit/534.3 (KHTML, like Gecko) Chrome/6.0.472.63 '
                'Safari/534.3')
  headers = {'User-Agent': user_agent}

  #find intersection of two

  for triple, pref in docPref.items():
    k1 = triple[0] + '\t' + triple[1]
    k2 = triple[0] + '\t' + triple[2]
    try:

      req = urllib2.Request(triple[1], None, headers)
      response = urllib2.urlopen(req)
      page = response.read()

      req = urllib2.Request(triple[2], None, headers)
      response = urllib2.urlopen(req)
      page = response.read()
      if k1 in maxLabel and k2 in maxLabel:
        if 'cant-judge' not in maxLabel[k1].values() and \
				'cant-judge' not in maxLabel[k2].values():
          print 'PAIR', '\t'.join(triple)
        else:
          print 'CANT JUDGE ', maxLabel[k1], maxLabel[k2]
      else:
        print 'NO MAX', triple, k1 in maxLabel, k2 in maxLabel
    except Exception as ex:
      print 'Exception ', ex
      print 'ERROR DOWNLOAD ', triple


def significance(prefGrade, head, count):

  prob = {'same': 4.0 / 16, 'high': 6.0 / 16, 'low': 6.0 / 16}

  expCounts = {
      'same': count * prob['same'],
      'low': count * prob['low'],
      'high': count * prob['high']
  }

  #print prob
  for ind, values in prefGrade.items():
    print values, count - values['same']
    expCounts = {
        'low': (count - values['same']) * 0.5,
        'high': (count - values['same']) * 0.5
    }

    #clist =  np.random.choice(['high','low'], count-values['same'],\
    # p=[0.5,0.5])
    #expCounts =  {'same':0,'low':0,'high':0}
    #print clist
    #for entry in countclist:
    #	expCounts[entry]+=1.0

    print head[ind], chisquare([values['high'],values['low']], \
		f_exp=[expCounts['high'],expCounts['low']])


def loadPrefAndEffort(fileName, docPref):
  quPref = {}
  quEffort = {}
  i = 0
  gradeMap = {'easy':2, 'v-easy':3, 'some-diff':1, 'v-diff':0, 'yes':2, \
'no':0, 'somewhat':1, 'high-rel':3, 'rel':2, 'non-rel':0, 'some-rel':1, 'cant-judge':-1}

  for line in open(fileName, 'r'):
    if 'cant-judge' not in line:
      split = line.strip().split(',')
      if i == 0:
        head = split[-5:]
        i += 1
      else:
        pref = split[-6]
        effort = split[-5:]
        key = split[0] + '\t' + split[1]
        quPref[key] = pref
        quEffort[key] = []

        for entry in effort:
          quEffort[key].append(gradeMap[entry])
  #	else:
  #		print 'Ignoring ', line.strip()
  prefGrade = {}
  count = 0.0
  effortLabel = {}
  pref = None
  for triple in docPref.keys():
    k1 = triple[0].strip() + '\t' + triple[1].strip()
    k2 = triple[0].strip() + '\t' + triple[2].strip()
    if k1 in quPref and k2 in quPref:
      pref1 = quPref[k1]
      pref2 = quPref[k2]

      if pref1 == 'pref' and pref2 == 'not-pref':
        pref = 'left'

      if pref1 == 'not-pref' and pref2 == 'pref':
        pref = 'right'

      if pref:
        #print triple, quPref[k1], quPref[k2]
        for i in range(len(head)):
          if i not in effortLabel:
            effortLabel[i] = {'same': 0.0, 'diff': 0.0}
            prefGrade[i] = {'low': 0.0, 'high': 0.0, 'none': 0.0, 'same': 0.0}

          if quEffort[k1][i] == quEffort[k2][i]:
            effortLabel[i]['same'] += 1.0
            prefGrade[i]['same'] = effortLabel[i]['same']

          else:
            effortLabel[i]['diff'] += 1.0
            if pref == 'left':
              if quEffort[k1][i] < quEffort[k2][i]:
                prefGrade[i]['low'] += 1.0
              elif quEffort[k1][i] > quEffort[k2][i]:
                prefGrade[i]['high'] += 1.0
            elif pref == 'right':
              if quEffort[k1][i] > quEffort[k2][i]:
                prefGrade[i]['low'] += 1.0
              elif quEffort[k1][i] < quEffort[k2][i]:
                prefGrade[i]['high'] += 1.0
            elif pref == 'none':
              prefGrade[i]['none'] += 1.0

        count += 1.0
    else:
      #print triple
      if ' ' in triple[0] and (k1 in quEffort or k2 in quEffort):
        print triple, k1 in quEffort, k2 in quEffort
      #toComplete.append(triple)

  print effortLabel

  for ind, values in prefGrade.items():
    for entry, val in values.items():
      print head[ind], entry, val, count, val / (values['high'] + values['low'])

  return prefGrade, head, count


def pairwisePrefFeatures(fileName, docPref):
  #gradeMap = {'easy':2, 'v-easy':3, 'some-diff':1, 'v-diff':0, 'yes':2, \
  #'no':0, 'somewhat':1, 'high-rel':3, 'rel':2, 'non-rel':0, 'some-rel':1, 'cant-judge':-1}
  i = 0
  #quPref={}
  quEffort = {}

  head = {}
  for line in open(fileName, 'r'):
    if 'cant-judge' not in line:
      split = line.strip().split(',')
      if i == 0:
        k = 0
        for entry in split[-5:]:
          head[entry] = k
          k += 1
        i += 1
      else:
        #pref = split[-6]
        effort = split[-5:]
        key = split[1].strip() + '\t' + split[2].strip()
        #quPref[key] = pref
        quEffort[key] = []
        for entry in effort:
          quEffort[key].append(entry)  #(gradeMap[entry])
  #	else:
  #		print 'Ignoring ', line.strip()
  pref = None
  print 'query-url,ease_find,readability,understand,Preference'
  for triple in docPref.keys():
    k1 = triple[0].strip() + '\t' + triple[1].strip()
    k2 = triple[0].strip() + '\t' + triple[2].strip()
    if k1 in quEffort and k2 in quEffort:  #quPref and k2 in quPref:
      #pref1 = docPref[triple][0]#quPref[k1]
      #pref2 = docPref[triple][1]#quPref[k2]
      #print pref1, pref2
      #if pref1 == 'pref' and pref2 == 'not-pref':
      #pref = [1,0]
      #
      #if pref1 == 'not-pref' and pref2 == 'pref':
      #pref = [0,1]
      pref = docPref[triple]
      if pref:
        featDiff = []
        for entry in ['ease_find', 'readability', 'understand']:
          v1 = int(quEffort[k1][head[entry]])
          v2 = int(quEffort[k2][head[entry]])
          featDiff.append(v1 - v2)
        #if not (all(x == featDiff[0] for x in featDiff)):
        #not all equal
        if pref[0] >= 0 and pref[1] >= 0:
          print '\t'.join(triple)+','+\
					','.join([str(x) for x in featDiff])+','+str(pref[0]-pref[1])
        #else:
        #	print 'SAME', featDiff

    else:
      pass
      #print triple
      #if ' ' in triple[0] and (k1 in quEffort or k2 in quEffort):
      #	print triple, k1 in quEffort, k2 in quEffort
      #toComplete.append(triple)


def main(argv):
  #features, queryDoc = loadFeatures(argv[1],'\t',int(argv[2]),int(argv[3]))
  #featWithLabel,urlMapping=plotFeatureWithLabel(int(argv[4]),features)
  label_pref, docType, docPref = findPreference({'features': 0.0}, argv[1])
  #label_pref1 , docType1, docPref1 = findPreference({'features':0.0}, argv[3])

  pairwisePrefFeatures(argv[2], docPref)
  #prepareFeaturesPairwise(docPref,argv[2])
  #findValByWorker(argv[1])
  #print len(label_pref)
  #prefGrade, head, count  = pairwiseEffort(argv[2],docPref)
  #found2 = pairwiseEffort(argv[2],docPref1)
  #significance(prefGrade, head, count)
  #for entry in found2:
  #	if entry not in found1:
  #		print entry
  #findPairs(features,queryDoc, label_pref,toComplete)
  #findPairsWithMissingLabels(argv[1])
  #mapLabels(argv[1])
  #plotValues(argv[5],docType,docPref,features)
  #maxLabels(argv[1])
  #effortLabels = loadEffortLabels(argv[5])
  #fromPairsToList(argv[1])
  #combineAll(features, docPref, docType, effortLabels)
  #randomComparison(argv[1],int(argv[2]))
  #effortPrefInt(argv[1], argv[2])


if __name__ == '__main__':
  main(sys.argv)
