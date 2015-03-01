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
		#print terms1, len(terms2)
		for t1 in terms1:
			if len(t1) > 2:
				for t2 in terms2:
					if len(t2) > 2:
						sc = self.coMan.getCoOcCount(t1,t2)[0]
						#if sc > 0:
						#	print t1, t2, sc 
						score+= sc 
						if t2 not in termScore:
							termScore[t2] = 0.0
						termScore[t2] += score
				
		for entry in termScore.keys():
			termScore[entry]/= len(terms1)
	
		return score/(1.0* len(terms1) * len(terms2)), termScore
