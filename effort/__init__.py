# -*- coding: utf-8 -*-
import sys
from plots import plotMultipleSys
#load features
def loadFeatures(fileName, sep, fInd, labelInd):
	features = {}
	j = 0
	#if last index label
	for line in open(fileName,'r'):
		split = line.strip().split(sep);
		
		if j == 0:
			j+=1;
			if labelInd == -1:
				labelInd=len(split) - 1
			print split[fInd], fInd, labelInd
			continue;
		
		ind = split[0]+'\t'+split[1]
		if ind not in features:
			features[ind] = {'feat':[], 'label':-1}
		for i in range(fInd,len(split)):
			if i != labelInd:
				features[ind]['feat'].append(float(split[i]))
			else:
				features[ind]['label'] = int(split[i])
		
	return features

#plot the distribution of something with respect to something

def plotFeatureWithLabel(featInd, features):
	featWithLabel = {}
	urlMapping = {}
	i = 1
	for key, feat in features.iteritems():
		label = key[:key.find('\t')]+'\t'+str(feat['label'])
		if label not in featWithLabel:
			featWithLabel[label] = {}
		#if 'words' in key:
		#	print key, featInd, i,  feat['feat'][featInd]
		featWithLabel[label][i] = feat['feat'][featInd];
		urlMapping[i] = key[key.find('\t')+1:]
		i+=1
		
	plotMultipleSys(featWithLabel,'docId','featVal','featVal'+str(featInd)+'.png','Feature Values vs label' )
	return featWithLabel, urlMapping

def findPairs(featWithLabel,urlMapping):
	for key, docList in featWithLabel.iteritems():
		if len(docList) > 1:
			sdoc = sorted(docList.items(), key = lambda x : x[1])
			v1 = sdoc[0][1]
			v2 = sdoc[-1][1]
			percent = (v2-v1)/((v1+1)*1.0)
			if percent > .35:
				print key,'\t', urlMapping[sdoc[0][0]],'\t', urlMapping[sdoc[-1][0]],'\t', \
					sdoc[0][1],'\t', sdoc[-1][1],'\t', len(docList)


def main(argv):
	features = loadFeatures(argv[1],'\t',int(argv[2]),int(argv[3]))
	featWithLabel,urlMapping=plotFeatureWithLabel(int(argv[4]),features)
	#findPairs(featWithLabel,urlMapping)


if __name__ == '__main__':
	main(sys.argv)
	


