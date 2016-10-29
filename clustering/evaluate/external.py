# -*- coding: utf-8 -*-
#load the pairs labelled together in one task

# Calculate Precision, Recall, F Measure, Rand Index

from queryLog import normalize
from nltk import stem
import sys, math
from utils import loadFileInTuples
from utils import filterWords
import ast
stemmer = stem.porter.PorterStemmer()


def Precision(tp, fp):
  return tp / (1.0 * (tp + fp))


def Recall(tp, fn):
  return tp / (1.0 * (tp + fn))



def fMeasure(prec, recall):
  #beta = 5
  #pow2 = math.pow(beta, 2)
  #return ((pow2+1.0)*( prec* recall))/(pow2*prec+recall)
  return 2.0 * ((prec * recall) / (prec + recall))


def RandIndex(tp, tn, totalPairs):
  return (tp + tn) / (totalPairs * 1.0)


def loadPairs(queryId, fileName, labeledPoints, pairLabels):

  for line in open(fileName, 'r'):
    split = line.split('\t')
    cpoints = set()
    for entry in split:
      normQuery = filterWords(entry.strip())
      #normQuery = entry.strip()#normalize(entry,stemmer)
      if normQuery in queryId:
        qid = queryId[normQuery]
        labeledPoints.add(qid)
        cpoints.add(qid)
      #else:
      #if len(normQuery) > 0:
      #	print normQuery
      #		pass
      #print 'True same ',normQuery
      pairs = generatePairsFromList(sorted(cpoints))

    for pair in pairs:
      pairLabels.add(pair)

			
	
# each pair in these sets is sorted by alphabetical order.	
# format : same_pairs_set = set(query1+'\t'+query2)
# format : different_pairs_set = set(query1+'\t'+query2)
# format : predicted_same_pairs_set = set(query1+'\t'+query2)
# format : predicted_different_pairs_set = set(query1+'\t'+query2)
def calculateIndicesFromSets(same_pairs_set, different_pairs_set,
					predicted_same_pairs_set,
					predicted_different_pairs_set):
	true_positives = 0.0
	true_negatives = 0.0
	false_negatives = 0.0
	false_positives = 0.0
	covered_pairs_set = set()
	
	for predicted_pair in predicted_same_pairs_set:
		if predicted_pair not in covered_pairs_set:
			if predicted_pair in same_pairs_set:
				true_positives+=1.0
			if predicted_pair in different_pairs_set:
				false_positives+=1.0
			covered_pairs_set.add(predicted_pair)
	for predicted_pair in predicted_different_pairs_set:
		if predicted_pair not in covered_pairs_set:
			if predicted_pair in same_pairs_set:
				false_negatives+=1.0
			if predicted_pair in different_pairs_set:
				true_negatives+=1.0
			covered_pairs_set.add(predicted_pair)
	print true_positives, false_positives, false_negatives , true_negatives,\
	len(same_pairs_set)+ len(different_pairs_set)

	return true_positives, false_positives, false_negatives, \
	true_negatives, len(same_pairs_set)+ len(different_pairs_set)
	
	
def calculateIndiciesFromFiles(trueLabelFile, differentPairFile, predictedLabelFile,
                      queryList):

  queryId = {}
  idQuery = {}
  i = 1
  for line in open(queryList, 'r'):
    split = line.split('\t')
    typeList = ast.literal_eval(split[7])
    if len(typeList) > 0:
      query = filterWords(split[0].strip())
      if query not in queryId:
        queryId[query] = str(i)
        idQuery[str(i)] = query
    i += 1

  l_samePairs = set()
  l_points = set()
  l_diffPairs = set()
  p_samePairs = set()

  #load true label file
  #Same cluster

  loadPairs(queryId, trueLabelFile, l_points, l_samePairs)
  loadPairs(queryId, differentPairFile, l_points, l_diffPairs)

  total_pairs = len(l_samePairs) + len(l_diffPairs)  #(len(l_points)*(len(l_points)-1))/2
  #filter predicted label file
  for line in open(predictedLabelFile, 'r'):
    line = line.strip()
    cpoints = set()
    if len(line) > 0 and 'NO CLUST' not in line:
      split = line.split('\t')
      for entry in split:
        try:
          entry = filterWords(entry.strip())
          qid = queryId[entry]
          if qid in l_points:
            cpoints.add(qid)
        except:
          #print entry
          pass
      pairs = generatePairsFromList(sorted(cpoints))
      for pair in pairs:
        if pair in l_samePairs or pair in l_diffPairs:
          #if pair in l_diffPairs:
          #	s = pair.split()
          #	print pair, idQuery[s[0]], idQuery[s[1]]
          p_samePairs.add(pair)  #
          if pair in l_diffPairs:
            p1 = pair[0:pair.find(' ')]
            p2 = pair[pair.find(' ') + 1:]
            #if p1 in idQuery and p2 in idQuery:
            #	print idQuery[p1], idQuery[p2]
            #else:
            #	print p1, 'sec', p2

  print len(l_samePairs), len(p_samePairs), total_pairs
  #print l_samePairs
  tp = len(l_samePairs & p_samePairs)
  fp = len(p_samePairs & l_diffPairs)  #len(p_samePairs) - tp ;
  fn = len(l_samePairs) - tp
  tn = len(l_diffPairs) - fp  #total_pairs - (tp+fp+fn)
  print tp, fp, fn, tn, total_pairs

  return tp, fp, fn, tn, total_pairs


def generatePairsFromList(elist, sep=' '):
  pairList = set([])
  for i in range(len(elist) - 1):
    for j in range(i + 1, len(elist)):
      if elist[i] != elist[j]:
        if elist[i] > elist[j]:
          temp = elist[i]
          elist[i] = elist[j]
          elist[j]= temp
        pairList.add(elist[i] + sep + elist[j])
  return list(pairList)


def printIndices(argv1, argv2, argv3):
  tp, fp, fn, tn, totalPairs = calculateIndiciesFromFiles(argv1, argv2, argv3)
  print 'Rand-Index ', RandIndex(tp, tn, totalPairs)
  recall = Recall(tp, fn)
  print 'Recall', recall
  prec = Precision(tp, fp)
  print 'Precision', prec
  print 'fMeasure', fMeasure(prec, recall)


def getRecallPrecision(true, diff, predicted_same, predicted_diff):
  tp, fp, fn, tn, totalPairs = calculateIndicesFromSets(true, diff, \
  				    predicted_same, predicted_diff)
  if tp > 0 and fp > 0 and fn > 0:
    rand = RandIndex(tp, tn, totalPairs)
    print 'Rand-Index ', rand
    recall = Recall(tp, fn)
    print 'Recall', recall
    prec = Precision(tp, fp)
    print 'Precision', prec
    print 'fMeasure', fMeasure(prec, recall)

    return {'Rand-Index':rand, 'Recall':recall, 'Precision':prec,\
        'FMeasure:':fMeasure(prec, recall)}

  return {'Rand-Index':0, 'Recall':0, 'Precision':0,'FMeasure:':0}

  #trueLabelFile,differentPairFile, predictedLabelFile, queryList

'''
Calculate Metrics: Precision, Recall and Precision on pair of queries marked on
same task in ground truth and predicted by algorithm
'''
def getSamePairPrecisionRecallF1Calculator(ground_truth_same_pairs, predicted_same_pairs):
    
    print 'GT length and predict length', len(ground_truth_same_pairs), len(predicted_same_pairs)
    
    #print 'Predicted', predicted_same_pairs
  
    #print 'Ground truth', ground_truth_same_pairs
    
    precision = recall = f1_meas = 0
    if len(predicted_same_pairs) > 0 and len(ground_truth_same_pairs) > 0:
        precision = len(predicted_same_pairs & ground_truth_same_pairs) / \
            (len(predicted_same_pairs)* 1.0)
        recall = len(predicted_same_pairs & ground_truth_same_pairs) / \
            (len(ground_truth_same_pairs)* 1.0)

    if precision + recall > 0:
        f1_meas = ((2* precision* recall) / (precision + recall))
 
    return {'Rand-Index':0, 'Recall':recall, 'Precision': precision,'FMeasure:':f1_meas}

if __name__ == '__main__':
  argv = sys.argv

  tp, fp, fn, tn, totalPairs = calculateIndiciesFromFiles(argv[1], argv[2], argv[3],
                                                 argv[4])
  print 'Rand-Index ', RandIndex(tp, tn, totalPairs)
  recall = Recall(tp, fn)
  print 'Recall', recall
  prec = Precision(tp, fp)
  print 'Precision', prec
  print 'fMeasure', fMeasure(prec, recall)


  
'''
all_tasks_ground_truth : A dictionary containing task-label-i : set(query1i, query2i .. query_{ni})
predicted_task : A set of queries (query1, query2 ...) considered to be on same task.

'''
def F1SetCalculator(all_tasks_ground_truth, predicted_task):
    all_task_fmeas = [0.0]
   
    # Should always be an array
    predicted_set = set(predicted_task)
 
    # Iterate over each task to find out the F-measure. 
    for task, query_set in all_tasks_ground_truth.items():
        # TP / (TP+FP)
        
        true_positives = len(query_set & predicted_set)
        precision = 0
        if len(predicted_set) > 0:
           precision  = true_positives / (len(predicted_set) * 1.0)

        # TP / (TP+FN)
        recall =0
        if len(query_set) > 0:
            recall =  true_positives / (len(query_set) * 1.0)
        prec_recall_sum = (precision + recall)

        f_meas = 0
        if prec_recall_sum > 0:
          f_meas = ( 2.0 * precision * recall ) / prec_recall_sum

        #print len(query_set), len(predicted_set), precision, recall, f_meas
        all_task_fmeas.append(round(f_meas,4))
    
    return max(all_task_fmeas)

