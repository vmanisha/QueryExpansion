class SessionSimScore:
	
	def __init__(self):
		self.id = 1
	
	
	def score(self,text1, text2):	
		return self.coMan.getCoOcCount(text1,text2)
		
			
class CoOccurSimScore:
	
	def __init__(self, coOcMan):
		self.coMan = coOcMan
	
	def score(self, terms1, terms2):
		
		t2Set = set(terms2.keys())
		t2Final = t2Set - terms1
		#print terms1, t2Set & terms1
		#print 'After subracting ',len(terms2), len(t2Final) , len(terms1)
		score = 0.0
		termScore = {}
		posTerms = 0
		total = sum([terms2[entry] for entry in t2Final] )
		t1len = len(terms1)
		t2len = len(t2Final)
		#print terms1, len(terms2)
		for t2 in t2Final:
			if t2 not in termScore:
				termScore[t2] = 0.0
			for t1 in terms1:
				termScore[t2] += self.coMan.getCoOcCount(t1,t2)[0]
			termScore[t2]*= (terms2[t2])
			termScore[t2]/= t1len
			termScore[t2] = round(termScore[t2],2)
			score+= termScore[t2]
			#if termScore[t2] > 0:
			#	posTerms+=1
		
		#if len(terms2) < 15:
		#	print terms1, terms2, score, termScore
		if t2len > 0:
			return score/t2len, termScore
		return 0.0, termScore
