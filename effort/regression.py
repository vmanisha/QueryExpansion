# -*- coding: utf-8 -*-
from scipy import stats
import statsmodels.api as sm
import pylab, sys
import pandas as pd
import numpy as np
from effort import findPreference
import matplotlib.pyplot as plt
import math


def fitRegressionModel(data, ostr):
  logitModel = sm.OLS.from_formula(ostr, data)
  mlogit_res = logitModel.fit()
  print mlogit_res.summary()
  data['predict_easy_find'] = mlogit_res.predict(data)

  #ofile = open('Est_easy_find','w')
  #for entry in mlogit_res.predict(data):
  #    ofile.write(str(entry)+'\n')
  #ofile.close()
  #print mlogit_res.pvalues
  return mlogit_res, data


def preprocessData(data):
  data['allHead'] = data['h1'] + data['h2'] + data['h3'] + data['h4'] + data[
      'h5'
  ] + data['h6']
  data['outLinkDomain'] = data['sameDomain'] + data['page']  #+data['diffO']
  data['spanWithQuery'] = data['spanA'] + data['spanH'] + data['spanB'
                                                         ] + data['spanO']
  data['boldItalics'] = data['b'] + data['i'] + data['strong']
  #avg_word_pos','min_word_pos','max_word_pos'
  fstr = ['aRatio','atTxtRatio','tRatio',\
        'termsInTitle','termsInURL','doc_ARI','doc_CLI','doc_LIX','doc_char',\
        'doc_period','doc_sent','doc_sentWithQueryTerm','doc_words','sum_ARI',\
        'sum_CLI','sum_LIX','sum_char','sum_period','sum_sent',\
        'sum_sentWithQueryTerm','sum_words','avgTF','avgWPos','maxTF','maxWPos',\
        'minTF','queryFreq']

  for vname in fstr:
    data[vname] = (data[vname] - data[vname].mean()) / data[vname].std()

  data.describe

  data.fillna(0)
  return data


def main(argv):
  #data = pd.DataFrame.from_csv('/home/manisha/workspace/trec_latest/query_url_pref_effort_combined_num.csv', sep=',')
  data = pd.DataFrame.from_csv(argv[1], sep=',')
  data = preprocessData(data)
  #ostr = 'Easy_find~ Understandability+Readability+Satisfaction'
  #ostr = 'ease_find ~ doc_ARI+doc_CLI+doc_LIX+doc_sent+doc_words+sum_ARI+sum_CLI+sum_LIX+sum_queryTerms+ \
  #sum_sent+sum_sentWithQueryTerm+avg_word_pos + \
  #min_word_pos+max_word_pos+a+div+img+li+p+table+aRatio +\
  #atTxtRatio+tRatio+diffDomain+page+sameDomain+ \
  #avgSpanLen +\
  #maxSpanPos+minSpanPos+noSpan+countA+meanPosA+\
  #countH+meanPosH+minPosH+\
  #allHead+spanWithQuery+boldItalics'

  #ostr = 'understand ~allHead+boldItalics+ min_word_pos+ a+ div+\
  #img+ li+ p+ table+ aRatio+ diffDomain+ page+ \
  #sameDomain+ spanH+ avgSpanPos+ maxSpanPos+ minSpanPos+ \
  #minPosA+ minPosH+ \
  #termsInURL+ doc_ARI+ doc_CLI+ doc_char+ doc_sent+\
  #doc_sentWithQueryTerm+ sum_char+ sum_period+ \
  #sum_sent+ sum_sentWithQueryTerm+queryFreq'
  #BEST
  ostr = 'ease_find ~allHead+boldItalics+ a+ div+\
img+ li+ p+ table+ aRatio+ atTxtRatio+ tRatio+ diffDomain+ page+ \
sameDomain+ spanH+ avgSpanLen+ avgSpanPos+ maxSpanPos+ minSpanPos+ \
countA+ maxPosA+ meanPosA+ minPosA+ maxPosH+ meanPosH+  \
termsInTitle+ doc_ARI+ doc_CLI+ doc_LIX+ doc_char+ doc_sent+\
doc_sentWithQueryTerm+ doc_words+ sum_char+ sum_period+ \
sum_sent+ sum_sentWithQueryTerm+ sum_words+queryFreq'

  model, newData = fitRegressionModel(data, ostr)
  effortPrefVal = {}

  mse = 0
  for index, row in newData.iterrows():
    key = row[0].strip() + '\t' + row[1].strip()
    if key not in effortPrefVal:
      effortPrefVal[key] = []
    effortPrefVal[key] = [row[-10], row[-1], row[-11]]  #easy_find
    #effortPrefVal[key]=[row[-6],row[-1],row[-11]] #understand
    #effortPrefVal[key]=[row[-8],row[-1],row[-11]] #readability
    #effortPrefVal[key]=[row[-7],row[-1],row[-11]] #relevance
    #effortPrefVal[key]=[row[-9],row[-1],row[-11]] #satisfaction

    #print row[-1]-row[-10], math.pow(row[-1]-row[-10],2)
    mse += math.pow(effortPrefVal[key][1] - effortPrefVal[key][0], 2)

  print newData.shape, mse, newData.shape[0], mse / newData.shape[0]
  print 'RMSE', math.sqrt((mse / newData.shape[0]))
  #prefGrade = {'old':{'low':0.0,'high':0.0},'new':{'low':0.0,'high':0.0}}
  #print argv[2]
  data2 = pd.DataFrame.from_csv(argv[2], sep=',')
  data2 = preprocessData(data2)

  queryId = {}
  for line in open(argv[3], 'r'):
    split = line.split('\t')
    queryId[split[1].strip()] = split[0].strip()
  #for r in data2.iterrows():
  #	print r
  data2['predict_effort'] = model.predict(data2)
  print data2.describe()
  oFile = open('predict_' + argv[2], 'w')
  for index, row in data2.iterrows():
    key = row[0].strip() + '\t' + row[1].strip()
    oFile.write(queryId[row[0].strip()] + ' ' + row[1].strip() + ' ' + str(int(
        math.ceil(row[-1]))) + '\n')


if __name__ == '__main__':
  main(sys.argv)
