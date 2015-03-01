class SessionSimScore:
	
	def __init__(self,coOcMan):
		self.coMan = coOcMan
	
	
	def score(self,text1, text2):	
		return self.coMan.getCoOcCount(text1,text2)
		
			
class CoOccurSimScore:
	
	def __init__(self, coOcMan):
		self.coMan = coOcMan
	
	def score(self, text1, text2):
		terms1 = set(text1.split())
		terms2 = set(text2.split())
		score = 0.0
		termScore = {}
		for t1 in terms1:
			for t2 in terms2:
				score+= self.coMan.getCoOcCount(t1,t2)
				if t2 not in termScore:
					termScore[t2] = 0.0
				termScore[t2] += score
				
		
		return score/(1.0* len(terms1) * len(terms2)), termScore