import re
from utils import SYMB, stopSet
from nltk import stem

porter = stem.porter.PorterStemmer()

def addedAndRemovedTerms(bQuery, session,termVocab):
	bset = set()
	tset = set()
	for entry in bQuery.split():
		bset.add(porter.stem(entry))
		
	for query in session:
		#print query
		query = re.sub(SYMB,' ',query.lower())
		query = re.sub('\s+',' ',query)
		for entry in query.strip().split():
			stemd = porter.stem(entry);
			if len(entry) > 2 and entry not in stopSet and stemd not in stopSet \
			and entry not in termVocab:
				tset.add(stemd)

	#print 'bSet', bset, 'Tset ', tset, 'Add', tset - bset, 'Remove', bset - tset
	return  tset - bset, bset - tset