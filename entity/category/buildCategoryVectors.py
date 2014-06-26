
import sys
from sklearn.feature_extraction.text import CountVectorizer
from dbPedia import loadAbstracts, loadCategoryTitles

	
def getVectorsFromTitles(catTitleDict,analyzer,vlen):
	catVector = textToVector(catTitleDict,analyzer)
	#trim dimensions
	j = 0
	for cat in catVector.keys():
		vector = catVector[cat]
		sortedD = sorted(vector.iteritems(), key = lambda x : x[1], reverse = True)
		if len(sortedD) > vlen:
			for i in range(vlen,len(sortedD)):
				#print 'Deleting', sortedD[i], 'for cat', cat
				vector.pop(sortedD[i][0])
		if j < 20:
			print cat, vector	
		 	j+=1
				
		#print cat,'\t', '\t'.join('{0}:{1}'.format(e[0],e[1]) for e in sorted(vector.iteritems(), key = lambda x : x[1], reverse = True))
	return catVector

def textToVector(tDict, analyzer):
	textVector = {}
	for tid, textList in tDict.iteritems():
		textVector[tid] = {}
		for text in textList:
			vector = analyzer(text)	
			for entry in vector:
				textVector[tid][entry] = textVector[tid].setdefault(entry,0) + 1

	return textVector


def getVectorsFromAbstracts(catTitleDict, abstractDict, analyzer,vlen):
	
	#convert the abstract to vector
	catVectors = {}
	j = 0
	for cat, titleList in catTitleDict.iteritems():
		catVectors[cat] = {}
		for title in titleList:
			text = ''
			if title in abstractDict:
				text = abstractDict.pop(title)	
			text = title+' '+text
			#print 'Merging',text,catVectors[cat]
			mergeDictWithList(catVectors[cat],analyzer(text))
		#cut the vectors
		sortedD = sorted(catVectors[cat].iteritems(), key = lambda x : x[1], reverse = True)
		if len(sortedD) > vlen:
			for i in range(vlen,len(sortedD)):
				catVectors[cat].pop(sortedD[i][0])
		if j < 20:
			print cat, catVectors[cat]
		 	j+=1
	
	return catVectors

def mergeDictWithList(dict1, dlist):
	for entry in dlist:
		dict1[entry] = dict1.setdefault(entry, 1.0) + 1.0

def indexVectors(categoryVector,fileName):
	outFile = open(fileName,'w')
	for cat, vector in categoryVector.iteritems():
		outFile.write(cat+'\t'+str(vector)+'\n')
	outFile.close()	


def main(argv):
	vlen = int(argv[4])
	abstractDict = loadAbstracts(argv[2])
	catTitleDict = loadCategoryTitles(argv[1])
	
	vectorizer = CountVectorizer(stop_words='english')
	analyzer = vectorizer.build_analyzer()
	
	#catVectors = getVectorsFromTitles(catTitleDict, analyzer, vlen)
	catVectors = getVectorsFromAbstracts(catTitleDict, abstractDict, analyzer, vlen)
	print len(catVectors)
	indexVectors(catVectors,argv[3])	
	

if __name__ == '__main__':
	main(sys.argv)
