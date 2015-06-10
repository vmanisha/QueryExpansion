import re,os,sys
from utils import SYMB, stopSet
from nltk import stem
from plots import plotScatter;
porter = stem.porter.PorterStemmer()

def addedAndRemovedTerms(bQuery, session,termVocab):
	bset = set()
	tset = set()
	for entry in bQuery.split():
		bset.add(entry)#porter.stem(entry))
		
	for query in session:
		#print query
		query = re.sub(SYMB,' ',query.lower())
		query = re.sub('\s+',' ',query)
		for entry in query.strip().split():
			stemd = porter.stem(entry);
			if len(entry) > 2 and (entry not in stopSet or stemd not in stopSet) \
			and (entry in termVocab or stemd in termVocab) :
				if entry in termVocab:
					tset.add(entry)
				tset.add(stemd)

	#print 'bSet', bset, 'Tset ', tset, 'Add', tset - bset, 'Remove', bset - tset
	return  tset - bset, bset - tset
	
def populateTerms(folder):
	wordList = set();
	for ifile in os.listdir(folder):
		for line in open(folder+'/'+ifile,'r'):
			split = line.split('\t');
			word = split[0].strip();
			wordList.add(word);
	for entry in wordList:
		print entry;

def plotCoeff(files):
	names = set();
	coeffList = {};
	count =0;
	ktotal=0;
	total=0;
	for ifile in files:
		for line in open(ifile,'r'):
			split = line.split(' ');
			if len(split) == 4:
				name = split[1].strip();
				key = float(split[-2]);
				val = float(split[-1]);
				if name not in names:
					names.add(name);
					if key < 2500:
						if key not in coeffList:
							coeffList[key] = [];
						if val != -1000 and val > -2:
							coeffList[key].append(val);
						
					else:
						count+=1;
					total+= val;
					ktotal+= 1.0;
						
		#plotValues();
	#plotValues(scindex, 'scindex.png');
	print 'Count',count, (total/ktotal), total, ktotal;
	esorted = sorted(coeffList.items(), key = lambda x : x[0]);
	toPlot = [];
	for entry in esorted:
		for val in entry[1]:
			toPlot.append((entry[0],val));
	plotScatter(toPlot, '# terms on Cat node','Dunn Index','dindex.png');		
	
if __name__ == '__main__':
	argv = sys.argv;	
	#populateTerms(argv[1]);
	plotCoeff(argv[1:]);
