# -*- coding: utf-8 -*-
import sys, os
from queryLog import getSessionWithNL, getSessionWithXML
from utils import getDocumentText
from queryLog import normalize
from nltk.stem import porter
from evaluate.termPrediction import updateStats, printMetric
from plots import plotMultipleSys


def main(argv):

  rare_prec = {'ent': {}, 'qccTask': {}, 'htcTask': {}, 'co': {}, 'entSub': {}}
  rare_mrr = {'ent': {}, 'qccTask': {}, 'htcTask': {}, 'co': {}, 'entSub': {}}

  freq_prec = {'ent': {}, 'qccTask': {}, 'htcTask': {}, 'co': {}, 'entSub': {}}
  freq_mrr = {'ent': {}, 'qccTask': {}, 'htcTask': {}, 'co': {}, 'entSub': {}}

  freqList = set()
  rareList = set()

  for line in open(argv[1], 'r'):
    split = line.split('\t')
    qid = int(split[0])
    freq = float(split[-1])
    if freq > 0:
      freqList.add(qid)
    else:
      rareList.add(qid)

  entFalse = set()
  for line in open(argv[2], 'r'):

    if 'Ent False' in line:
      entFalse.add(int(line[:line.find(' ')]))
      print entFalse
    if 'Metrics' in line:
      osplit = line.split('\t')
      split = osplit[0].split()
      approach = split[0][:split[0].rfind('Metrics')].lower()

      if approach == 'e':
        approach = 'ent'
      if approach == 'esub':
        approach = 'entSub'
      if approach == 'qcctask':
        approach = 'qccTask'
      if approach == 'htctask':
        approach = 'htcTask'

      qid = int(split[1])
      noTerms = int(osplit[1])
      prec = float(osplit[-2])
      mrr = float(osplit[-1])

      if qid not in entFalse:
        #print qid;
        if qid in freqList:
          freq_prec = updateStats(noTerms, approach, prec, freq_prec)
          freq_mrr = updateStats(noTerms, approach, mrr, freq_mrr)

        else:
          rare_prec = updateStats(noTerms, approach, prec, rare_prec)
          rare_mrr = updateStats(noTerms, approach, mrr, rare_mrr)

  printMetric(freq_prec, 'entSub', 'FreqPrec')
  printMetric(freq_mrr, 'entSub', 'FreqMrr')

  printMetric(freq_prec, 'ent', 'FreqPrec')
  printMetric(freq_mrr, 'ent', 'FreqMrr')

  printMetric(freq_prec, 'htcTask', 'FreqPrec')
  printMetric(freq_mrr, 'htcTask', 'FreqMrr')

  printMetric(freq_prec, 'qccTask', 'FreqPrec')
  printMetric(freq_mrr, 'qccTask', 'FreqMrr')

  printMetric(freq_prec, 'co', 'FreqPrec')
  printMetric(freq_mrr, 'co', 'FreqMrr')

  printMetric(rare_prec, 'entSub', 'RarePrec')
  printMetric(rare_mrr, 'entSub', 'RareMrr')

  printMetric(rare_prec, 'ent', 'RarePrec')
  printMetric(rare_mrr, 'ent', 'RareMrr')

  printMetric(rare_prec, 'htcTask', 'RarePrec')
  printMetric(rare_mrr, 'htcTask', 'RareMrr')

  printMetric(rare_prec, 'qccTask', 'RarePrec')
  printMetric(rare_mrr, 'qccTask', 'RareMrr')

  printMetric(rare_prec, 'co', 'RarePrec')
  printMetric(rare_mrr, 'co', 'RareMrr')

  plotMultipleSys(freq_prec, 'No of Terms', 'Prec', argv[3] + '_freq_prec.png',
                  'Term Prediction Prec Plot')
  plotMultipleSys(freq_mrr, 'No of Terms', 'MRR', argv[3] + '_freq_mrr.png',
                  'Term Prediction MRR Plot')
  plotMultipleSys(rare_prec, 'No of Terms', 'Prec', argv[3] + '_rare_prec.png',
                  'Term Prediction Prec Plot ')
  plotMultipleSys(rare_mrr, 'No of Terms', 'MRR', argv[3] + '_rare_mrr.png',
                  'Term Prediction MRR Plot ')

  #completedDocs = {};
  #for session, docs, clicks in getSessionWithXML(argv[1]):
  #for i , docList in docs.items():
  #for docId in docList:
  #if docId not in completedDocs:
  #completedDocs[docId] = 1.0;
  #
  #
  #for entry in completedDocs.keys():
  #print entry;
  #
  #	print session

  #get the entries for a particular query
  #parts = int(argv[2])
  #index = int(argv[3])
  #files = os.listdir(argv[1])
  #outFolder = argv[4]
  #oFile = open(outFolder+'/'+ifile,'w')
  #strt = index*(len(files)/parts)
  #end = (index+1)*(len(files)/parts)
  #for i in range(strt,end):
  #ifile = files[i]
  '''stemmer = porter.PorterStemmer();


        queryFreq = {};
        for line in open(argv[1],'r'):
                split = line.split('\t');
                query = split[0].strip();

                sQuery = normalize(query, stemmer);

                freq = float(split[1]);
                queryFreq[sQuery] = freq;

        toPrint = {};
        qid = 1;
        for session, doc, click, cTitle, cSummary in getSessionWithXML(argv[2]):
                oquery = session[0];
                query = normalize(oquery, stemmer);
                if query in queryFreq:
                        toPrint[str(qid)+'\t'+query] = queryFreq[query];
                else:
                        toPrint[str(qid)+'\t'+query] = 0;
                qid+=1;

        sort = sorted(toPrint.items() , reverse = True , key = lambda x : x[1]);
        for entry in sort:
                print entry[0],'\t', entry[1];
                #
        ##print
        getDocumentText('clueweb12-0817wb-00-27979','/media/Data/TREC_Session_Doc/cluewebdocs12/')
        '''
  '''done = {}

        for line in open(argv[1],'r'):
                split = line.split('\t')
                if split[0] not in done:
                        done[split[0].strip()] = split[1].strip()

        for line in open(argv[2],'r'):
                split = line.strip().split('\t')
                if split[0].strip() in done:
                        print
                        split[0]+'\t'+done[split[0]]+'\t'+'\t'.join(split[1:])
        '''
  #for entry, spot in done.iteritems():
  #	print entry, '\t', spot

  #merge the features urls, users and spot


if __name__ == '__main__':
  main(sys.argv)
