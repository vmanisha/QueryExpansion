from utils import text_to_vector
import sys
def reduceTaskToTerms(fileName):
	taskTermDict = {}
	for line in open(fileName, 'r'):
		split = line.split('\t')
		if len(split) > 1:
			key = split[0].strip()
			taskTermDict[key] = {}
			for entry in split[1:]:
				task = entry[:entry.rfind(',')]
				count = 0 #int(entry[entry.rfind(':')+1:])
				taskVector = text_to_vector(task)
				for entry , val in taskVector.iteritems():
					taskTermDict[key][entry]=taskTermDict[key].setdefault(entry,0.0) + val + count
			
	
	for index, tDict in taskTermDict.iteritems():
		#print index, '\t', ' '.join('{0}:{1}'.format(x,y) for x, y in tDict.iteritems())
		print index, '\t',tDict


if __name__=='__main__':
	argv = sys.argv
	reduceTaskToTerms(argv[1])