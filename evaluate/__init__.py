import re
from utils import SYMB, stopSet
from nltk import stem

porter = stem.porter.PorterStemmer()

def addedAndRemovedTerms(bQuery, session):
	bset = set()
	tset = set()
	for entry in bQuery.split():
		bset.add(porter.stem(entry))
		
	for query in session:
		#print query
		query = re.sub(SYMB,' ',query.lower())
		query = re.sub('\s+',' ',query)
		for entry in query.strip().split():
			if len(entry) > 2 and entry not in stopSet:
				tset.add(porter.stem(entry))

	#print 'bSet', bset, 'Tset ', tset, 'Add', tset - bset, 'Remove', bset - tset
	return  tset - bset, bset - tset