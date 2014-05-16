import sys
from Category import getCats, loadPhrases

def main(argv):
	f1Dict = getCats(argv[1])
	f2Dict = getCats(argv[2])
	mcount = 0.0	
	ctotal = 0.0
	total = 0.0
	for entry in f2Dict.keys():
		if entry in f1Dict:
			phrase1 = loadPhrases(f1Dict[entry])
			phrase2 = loadPhrases(f2Dict[entry])
			ints = phrase1 & phrase2
			if len(ints) > 1:
				#print 'Phrase1 ', f1Dict[entry], phrase1
				#print 'Phrase2 ', f2Dict[entry], phrase2
				score = len(ints)/(len(phrase2)*1.0)
				if score > 0.2:
					print entry, '\t', ', '.join(ints),'\t', len(ints),'\t',score
				total+= score
			
			mcount +=1
		
		ctotal +=1

	print 'total types in sessions ', ctotal
	print 'matched types in AOL Logs', mcount
	print 'average % match', total/mcount


if __name__ == "__main__":
	main(sys.argv)
