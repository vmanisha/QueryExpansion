class SessionSimScore:
	
	def __init__(self,coOcMan):
		self.coMan = coOcMan
	
	
	def score(self,text1, text2):	
		return self.coMan.getCoOcCount(text1,text2)
		
			
class CoOccurSimScore:
	
	def __init__(self, coOcMan):
		self.coMan = coOcMan
	
	def score(self, terms1, terms2):
		score = 0.0
		termScore = {}
		total = sum(terms2.values())
		#print terms1, len(terms2)
		for t1 in terms1:
			for t2 in terms2:
				sc = self.coMan.getCoOcCount(t1,t2)[0]
				#if sc > 0:
				#	print t1, t2, sc
				score+= (sc*(terms2[t2]/total))
				if t2 not in termScore:
					termScore[t2] = 0.0
				termScore[t2] += score
				
		for entry in termScore.keys():
			termScore[entry]/= len(terms1)
		if len(terms2) > 0 and len(terms1) > 0:
			return score/(1.0* len(terms1) * len(terms2)), termScore
		return 0.0, termScore
