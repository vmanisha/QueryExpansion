import sys
import ast

#title vectors

#abstract vectors

#co - occurance probability
#P(a | b)
def findProbMatrix(fileName):
	catCoFreq = {}
	for line in open(fileName,'r'):
		line = line.strip()
		split = line.split('\t')
		#query = split[0]
		try:
			tagDict = ast.literal_eval(split[1])
			catList = []
			for match , spotDict in tagDict.iteritems():
				catList.append(spotDict['cat'].split())
			i = 0
			j = 1
			#print catList
			while i < len(catList) and j < len(catList) :
				for entry in catList[i]:
					for entry2 in catList[j]:
						#print i, j , entry, entry2
						if entry2 not in catCoFreq:				
							catCoFreq[entry2] ={}
						if entry not in catCoFreq:				
							catCoFreq[entry] ={}
						catCoFreq[entry][entry2]= 1.0 if entry2 not in catCoFreq[entry] else catCoFreq[entry][entry2]+1
						catCoFreq[entry2][entry]= 1.0 if entry not in catCoFreq[entry2] else catCoFreq[entry2][entry]+1
				j+=1
				if j == len(catList):
					i += 1	
					j = i+1

		except Exception as err:
			print err, line
			
	return catCoFreq


def main(argv):
	catCoFreq=findProbMatrix(argv[1])
	for entry , elist in catCoFreq.iteritems():
		print entry,'\t', '\t'.join('{0}:{1}'.format(x[0],x[1]) for x in sorted( elist.iteritems(), reverse = True, key = lambda x : x[1]))
	

if __name__ == '__main__':
	main(sys.argv)
