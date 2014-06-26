# -*- coding: utf-8 -*-
import re
#import os
#import sys
from collections import Counter, defaultdict
import math


ashleelString = set (['sex','sexy','porn','horny','sexi','naked','pornstar','kiss','masturbation','porno','fucking','penis','shag', \
				'dick','penus','boobs','breasts','boob','orgasm','pregnant','masturbate','fuck','nude','topless',\
			'testicle','fucks','tits', 'boobies','whore','erotic', 'masturbating','nipple','nipples','cock','cocks','shagging','pussy','nudist'])

stopSet = set (['_CAT_','a','about','according','accordingly','after','all','also','am','an','and','any','anything','are','as','at','b','back','be','because','been','big','bring','bringing','but','by','both','can','cant','com','come','could','did','didnt','do','doing','dont','down','even','either','essentially','ever','every','first','for','from','four','get','give','go','going','gonna','good','got','had','has','hate','have','he','her','here','hes','hey','him','his','how','i','get','getting','gets','if','ill','im','in','into','is','it','its','ive','just','know','kind','kinds','let','life','like','little','look','love','made','make','man','many','may','maybe','me','mean','more','most','much','my','near','need','never','no','not','now','of','off','oh','ok','okay','on','one','only','or','other','our','out','over','people','please','read','really','right','said','say','see','six','seven','she','shes','should','slow','small','so','some','something','sorry','stop','since','sure','such','take','ten','than','that','thats','the','them','their','these','then','there','therefore','thereafter','themselves','theres','they','thing','think','this','thought','those','though','thus','through','throughout','three','till','time','to','too','todays','true','two','under','uh','up','us','until','upon','use','usually','very','want','was','way','we','well','were','what','whats','whose','whatever','whereby','when','where','wherein','which','who','while','whether','why','will','with','within','without','would','www','yeah','yes','you','your','youre','new'])


#SYMB = '[.!,;-*&"\'_]'
SYMB = '[^\w]+'
DIGIT = re.compile(r'\d')
WORD = re.compile(r'\w+')
WEB = re.compile("^(((ht|f)tp(s?))\://)?(www.|[a-zA-Z].)[a-zA-Z0-9\-\.]+\.([a-z]{2,4})(\:[0-9]+)*(/($|[a-zA-Z0-9\.\,\;\?\'\\\+&amp;%\$#\=~_\-]+))*")

def getDictFromSet(qset):
	d = defaultdict(int)
	for word in qset:
	    d[word] += 1
	return d

def getTuplesFromSet(qset):
	d = defaultdict(int)
	for word in qset:
	    d[word] += 1
	return [(x,d[x]) for x in d.keys()]
	
#convert list to tabbed string
def listToTabString(line):
	string = '\t'.join([str(entry) for entry in line])
	return string.strip()

	
def get_cosine(vec1, vec2):
     intersection = set(vec1.keys()) & set(vec2.keys())
     numerator = sum([vec1[x] * vec2[x] for x in intersection])

     sum1 = sum([vec1[x]**2 for x in vec1.keys()])
     sum2 = sum([vec2[x]**2 for x in vec2.keys()])
     denominator = math.sqrt(sum1) * math.sqrt(sum2)

     if not denominator:
        return 0.0
     else:
        return float(numerator) / denominator

def text_to_vector(text):
     words = WORD.findall(text)
     return Counter(words)



def getNGrams(string, length):
	split = string.split()
	#print split, len(split), length
	for i in range(0,len(split)+1):
		for j in range(i+1,length+1):
			yield ' '.join(split[i:j]), split[i:j],j-i


def removeFreqWords(fileName, rfreq):
	freq = {}
	lines = {}
	for line in open(fileName,'r'):
		count = Counter(line.strip().split())
		for entry, efreq in count.items():
			if entry not in freq:
				freq[entry] = 0
				lines[entry] = []
			freq[entry] += efreq
		lines[entry].append(line)
	
	
	for entry in sorted(freq.items(),key=lambda value : value[1]):
		#print entry
		if entry[1] < rfreq:
			#print entry
			newList = []
			for task in lines[entry[0]]:
				newList.append(task.replace(entry[0],'_RARE_'))
			lines[entry[0]] = newList
		else:
			break
	for tlist in lines.values():
		for entry in tlist:
			print entry,		


def replaceAlphaNum(fileName,replace):
	for line in open(fileName):
		split = line.strip().split()
		for entry in split:
			if DIGIT.search(entry):
				print replace,
			else:
				print entry,
		print


def loadFileInDict(fileName):
	content = {}
	for line in open(fileName,'r'):
		line = line.strip()
		tokens = line.split()
		content[tokens[0]] = tokens[1]
	return content
	
#def main(argv):
	#replaceAlphaNum(argv[1],argv[2])
	#removeFreqWords(argv[1],int(argv[2]))
	#buildLinkGraph(argv[1])
#if __name__ == "__main__":
#	main(sys.argv)
