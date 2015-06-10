# -*- coding: utf-8 -*-
from sklearn import svm
import sys
from scipy import stats
import statsmodels.api as sm
from sklearn.multiclass import OneVsRestClassifier
import pylab
import pandas as pd
import numpy as np
import random
import matplotlib.pyplot as plt
from sklearn.cross_validation import train_test_split,cross_val_score
from sklearn.ensemble import RandomForestClassifier,AdaBoostClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.feature_selection import f_classif
from sklearn.feature_selection import SelectKBest
from scipy import stats
from sklearn import cross_validation


def loadLabels(fileName,indexA):
	labels = {}
	li = 0
	for line in open(fileName,'r'):
		split = line.lower().strip().split(',')
		#key = split[2]+'\t'+ split[3]
		key = split[3].strip()+'\t'+ split[4].strip()+'\t'+split[5].strip()
		if key not in labels:
			labels[key] = []
		if li == 0:
			print split[indexA]
			li+=1
		try:
			if 'left' in split[indexA]:
				labels[key].append(1)
			if 'right' in split[indexA]:
				labels[key].append(-1)
			#labels[key].append(split[indexA]) #gradeMap[split[indexA]])
		except:
			print split[indexA]
	return labels


def crossValidation(argv):
	data = pd.DataFrame.from_csv(argv[1], sep=',')
	column = argv[2]
	target = data[column]
	print data.columns.values
	
	#target.loc[target == 1] = 0
	#target.loc[target > 1] = 1
	
	#for c in ['ease_find','satisfaction','readability',\
	#'relevance','understand']:
	#	co = c+'_Diff'
		#c1 = data[c+'_P1']
		#c2 = data[c+'_P2']
		##
		##c1.loc[c1 < 1] = 0
		##c1.loc[c1 == 1] = 0
		##c1.loc[c1 > 1] = 1

		##c2.loc[c2 < 1] = 0
		##c2.loc[c2 == 1] = 0
		##c2.loc[c2 > 1] = 1

		#data[co] = c1 - c2

		#data=data.drop([c+'_P1',c+'_P2'],axis=1)
	#	data=data.drop([co],axis=1)
		
	#tdata = data.drop([' judgement_P1',' judgement_P2',' judgement_Diff',\
	#'effort_P1','effort_P2','effort_Diff','Preference'],axis=1)
	#clf = OneVsRestClassifier(svm.SVC(class_weight='auto',gamma=1, C=8))#
	
	#clf = LogisticRegression(multi_class='ovr')
	
	clf = AdaBoostClassifier(n_estimators=10)
	#tdata = data.drop(['URL','Query','judgement','Preference',column], axis=1)
	#tdata = data.drop([column,'q','u1','u2'],axis=1)
	#tdata = data.drop([column],axis=1)
	#tdata = data[['ease_find_Diff','readability_Diff','understand_Diff']]
	tdata = data[['ease_find']]
	
	#tdata = tdata[['ease_find_Diff','satisfaction_Diff','readability_Diff',\
	#'relevance_Diff','understand_Diff']]
	print tdata.columns.values
	
	#for vname in list(tdata.columns.values):
	#	tdata[vname] = (tdata[vname] - tdata[vname].mean()) / tdata[vname].std()
	#tdata=tdata.replace([np.inf, -np.inf], np.nan)
	tdata = tdata.fillna(0)
	#target = target.fillna(0)
	#kf = cross_validation.KFold(tdata.shape[0], n_folds=10)
	##print tdata.columns.values, tdata.shape
	tdata= tdata.reset_index()
	#
	#for train, test in kf:
		##print train, test
		#tr = tdata.loc[train,:]
		##print target.shape
		#tst = target[train]
		##target[0] = -1
		##print tst	
		##tr.fillna(0,inplace=True)
		##print tdata.loc[[8,9,10],:]
		#prob = clf.fit(tr, tst)
		##predict_proba(tdata.loc[test])
		#scores = clf.score(tdata.loc[test],target[test])
		#print scores
		#print clf.coef_
		##print prob
		##results.append( myEvaluationFunc(target[testcv], [x[1] for x in probas]) )
	#clf = LogisticRegression(multi_class='ovr')
	tdata= tdata.reset_index()
	
	scores = cross_val_score(clf,tdata,target,cv = 15)
	
	print column, scores.mean(), scores.std()
	


def featureSelection(argv):
	data = pd.DataFrame.from_csv(argv[1], sep=',')
	column = argv[2]
	target = data[column]
	
	#for c in ['ease_find','satisfaction','readability',\
	#'relevance','understand']:
		#co = c+'_Diff'
		#c1 = data[c+'_P1']
		#c2 = data[c+'_P2']
		##
		##c1.loc[c1 < 1] = 0
		##c1.loc[c1 == 1] = 0
		##c1.loc[c1 > 1] = 1

		##c2.loc[c2 < 1] = 0
		##c2.loc[c2 == 1] = 0
		##c2.loc[c2 > 1] = 1

		#data[co] = c1 - c2
		#data=data.drop([c+'_P1',c+'_P2'],axis=1)

	#print data.columns.values
	
	#target.loc[target == 1] = 0
	#target.loc[target > 1] = 1
	
	#tdata = data.drop([' judgement_P1',' judgement_P2',' judgement_Diff',\
	#'effort_P1','effort_P2','effort_Diff','Preference'],axis=1)
	
	#tdata = data.drop(['URL','judgement','Readability','Satisfaction',\
	#'Preference','Understandability','Relevance','Easy_find'], axis=1)

	#tdata1 = data[['Readability','Satisfaction','Understandability','Relevance','Easy_find']]
	#tdata = data.drop([column,'q','u1','u2'],axis=1)
	#tdata = data[['ease_find_Diff','readability_Diff','understand_Diff']]
	
	tdata = data.drop([column],axis=1)
	
	#for vname in list(tdata.columns.values):
		#tdata[vname] = (tdata[vname] - tdata[vname].mean()) / tdata[vname].std()

	
	clf = ExtraTreesClassifier()
	X_new = clf.fit(tdata, target).transform(tdata)
	imp =clf.feature_importances_
	print imp
	print X_new.shape
	for i in range(len(imp)):
		if imp[i] > 0.02:
			print tdata.columns.values[i]+':'+str(round(imp[i],3))
	
	result = f_classif(tdata,target)
	print '\n'.join([tdata.columns.values[i]+' '+str(round(result[0][i],3))\
	+' '+str(round(result[1][i],3)) for i in range(len(result[0]))])
	#normalize
	#for vname in list(tdata.columns.values):
	#    tdata[vname] = (tdata[vname] - tdata[vname].mean()) / tdata[vname].std()
	
	
	
	
def main(argv):
	
	clf = svm.SVC(class_weight='auto',probability=True,C=0.9, gamma = 0.02)
	#clf = RandomForestClassifier(n_estimators=10, max_depth=None,\
	#min_samples_split=1, random_state=0)
	#clf = AdaBoostClassifier(n_estimators=100)
	
	#load features nd prepare data
	data = pd.DataFrame.from_csv(argv[1], sep=',')
	target = data['Preference']
	#print data
	print data.columns.values
	
	tdata = data.drop([' judgement_P1',' judgement_P2',' judgement_Diff',\
	'effort_P1','effort_P2','effort_Diff','Preference'],axis=1)
	#normalize
	for vname in list(tdata.columns.values):
	    tdata[vname] = (tdata[vname] - tdata[vname].mean()) / tdata[vname].std()

	#X_train, X_test, y_train, y_test = train_test_split(tdata, target, \
	#test_size=0.25, random_state=33)
	#clf.fit(X_train,X_test)
	scores = cross_val_score(clf,tdata,target,cv = 30)
	
	print scores.mean(), scores.std()
	labelPref = loadLabels(argv[2],int(argv[3]))
	
	ran = range(1000)
	mall = []
	mrall  = []
	for j in range(1000):
		matchA = []
		matchR = []
		st = random.choice(ran)
		X_train, X_test, y_train, y_test = train_test_split(tdata, target, \
			test_size=0.20, random_state=st)
		clf.fit(X_train,y_train)
		print 'Iter ',j, 'Train Accuracy ',clf.score(X_train,y_train),\
			'Test Accuracy ',clf.score(X_test,y_test)
		
		rMatch = 0.0
		count = 0.0
		match = 0.0
				
		for i in range(48):
			st = random.choice(ran)
			#X_train, X_test, y_train, y_test = train_test_split(tdata, target, \
			#test_size=0.20, random_state=st)
			#print st
			#randomly choose one of the labelers
			predicted = clf.predict(X_test)
			
			#randomA = []
			r = 0
			for row in X_test.iterrows():
				key =row[0].strip()
				if key in labelPref and len(labelPref[key]) > 1:
					
					r_c = random.choice(labelPref[key])
					if r_c==predicted[r]:
						match +=1.0
						
					rs = random.sample(labelPref[key],2)
					#binarize
					if rs[0] == rs[1]:
						rMatch+=1.0
					count+=1
				r+=1
				#else:
					#randomA.append(0)
					
			#print predicted
			#print randomA
			
			#for x, y in zip(predicted, randomA):
				#if x == y:
					#match+=1.0
				#count+=1.0
		matchA.append(match/count)
		matchR.append(rMatch/count)
		
		#print 'Iter',j, matchA
		print 'Iter',j, np.mean(matchA), np.std(matchA)
		print 'Iter',j, np.mean(matchR), np.std(matchR)
		
		mall.append(np.mean(matchA))
		mrall.append(np.mean(matchR))
	print mall
	print mrall
	
	print 'All ',j, np.mean(mall), np.std(mall)
	print 'All ',j, np.mean(mrall), np.std(mrall)

	#m, v, s, k = stats.t.stats(10, moments='mvsk')
	print 't-statistic = %6.3f pvalue = %6.4f' %  stats.mannwhitneyu(mall,mrall)
	
	#print 't-statistic = %6.3f pvalue = %6.4f' %  stats.ttest_ind(mrall,0)
	
		
if __name__ == '__main__':
	#main(sys.argv)
	#featureSelection(sys.argv)
	crossValidation(sys.argv)