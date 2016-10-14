# -*- coding: utf-8 -*-
import re
import os
import sys
from collections import Counter, defaultdict
import math
import html2text
from nltk import stem
import ast


ashleelString = set (['sex','sexy','porn','horny','sexi','naked','pornstar','kiss','masturbation','porno','fucking','penis','shag', 'viagra','sexual'\
				'dicks','dick','penus','boobs','breasts','boob','orgasm','pregnant','masturbate','fuck','nude','topless','boobs','nudes','vagina','xxx'\
			'testicle','fucks','tits', 'boobies','whore','erotic', 'masturbating','nipple','nipples','cock','cocks','shagging','pussy','nudist'])

stopSet = set (['_CAT_','a','above','about','according','accordingly','after','all','also','am','an','and','any','anything','are','as',\
'at','always','b','back','be','being','because','before','been','big','bring','bringing','but','by','both','can',\
'cant','called','com','comn','comhttp','come','could','doe','did','didnt','do','doing','dont','down','during','does','even','either',\
'essentially','ever','every','first','for','from','four','get','give','go','going','gonna',\
'good','got','had','has','hate','have','he','her','here','hes','hey','him','his','how','http',\
'i','get','getting','gets','great','if','ill','im','in','into','is','it','its','ive','just','know',\
'kind','kinds','knows','keep','let','like','little','look','looking','love','made','make','making','man','many','may',\
'maybe','me','mean','more','most','mostly','much','my','near','need','never','no','not','now','of',\
'off','oh','ok','okay','on','one','only','or','other','our','out','over','put','people','please',\
'read','really','regarding','relate','related','right','said','say','see','six','seven','she','shes','should','slow',\
'small','s','so','some','something','sorry','still','stop','since','sure','such','take','ten','than',\
'that','thats','the','them','their','these','then','there','therefore','thereafter',\
'themselves','theres','they','thing','think','this','thought','those','though','thus',\
'through','throughout','three','till','to','too','todays','true','two','under',\
'uh','up','us','until','upon','use','using','usually','very','want','was','way','we','well',\
'were','what','whats','whose','whatever','whereby','when','where','wherein','which',\
'who','whi','while','whether','why','will','with','within','without','would','www','wwww','yeah',\
'yes','you','your','youre','new','clueweb12','same'])

#SYMB = '[.!,;-*&"\'_]'
SYMB = '[^\w]+'
SYMBreg = re.compile('[^\w]+')
SYMB2 = re.compile('[\.\!\,\;\-\*\&\"\'\_\%\^\@\~\#\<\>\/\:\=\`\?\~\|]+')
SYMB2_string = '[\.\!\,\;\-\*\&\"\'\_\%\^\@\~\#\<\>\/\:\=\`\?\~\|]+'
DIGIT = re.compile(r'\d')
WORD = re.compile(r'\w+')
WEB = re.compile(
    "^(((ht|f)tp(s?))\://)?(www.|[a-zA-Z].)[a-zA-Z0-9\-\.]+\.([a-z]{2,4})(\:[0-9]+)*(/($|[a-zA-Z0-9\.\,\;\?\'\\\+&amp;%\$#\=~_\-]+))*")
HTML = re.compile('<html')
LEMR = re.compile('the lemur project')


def filterWords(query, wlen=1):
  nQuery = ''
  for entry in query.split():
    if len(entry) > wlen:
      nQuery += ' ' + entry
  nQuery = nQuery.strip()
  return nQuery


def getDictFromSet(qset):
  d = {}  #defaultdict(int)
  for word in qset:
    if word not in stopSet:
      if word not in d:
        d[word] = 0
      d[word] += 1
  return d


def getTuplesFromSet(qset):
  d = defaultdict(int)
  for word in qset:
    d[word] += 1
  return [(x, d[x]) for x in d.keys()]


  #convert list to tabbed string
def listToTabString(line):
  string = '\t'.join([str(entry) for entry in line])
  return string.strip()


def get_cosine(vec1, vec2):
  intersection = set(vec1.keys()) & set(vec2.keys())
  numerator = sum([vec1[x] * vec2[x] for x in intersection])

  sum1 = sum([vec1[x] ** 2 for x in vec1.keys()])
  sum2 = sum([vec2[x] ** 2 for x in vec2.keys()])
  denominator = math.sqrt(sum1) * math.sqrt(sum2)

  if not denominator:
    return 0.0
  else:
    return float(numerator) / denominator


def text_to_vector(text):
  words = WORD.findall(text)
  return Counter(words)


def getNGramsAsList(string, length):
  split = string.split()
  result = {}
  #print split, len(split), length
  for i in range(0, len(split)):
    for j in range(i + 1, i + length + 1):
      #print i, j , length
      if j <= len(split):
        gram = '_'.join(split[i:j])
        if gram not in stopSet and '_' in gram:
          if gram not in result:
            result[gram] = 0.0
          result[gram] += 1.0
  return result


def getNGrams(string, length):
  split = string.split()
  #print split, len(split), length
  for i in range(0, len(split)):
    for j in range(i + 1, i + length + 1):
      #print i, j , length
      if j <= len(split):
        yield ' '.join(split[i:j]), split[i:j], j - i


def removeFreqWords(fileName, rfreq):
  freq = {}
  lines = {}
  for line in open(fileName, 'r'):
    count = Counter(line.strip().split())
    for entry, efreq in count.items():
      if entry not in freq:
        freq[entry] = 0
        lines[entry] = []
      freq[entry] += efreq
    lines[entry].append(line)

  for entry in sorted(freq.items(), key=lambda value: value[1]):
    #print entry
    if entry[1] < rfreq:
      #print entry
      newList = []
      for task in lines[entry[0]]:
        newList.append(task.replace(entry[0], '_RARE_'))
      lines[entry[0]] = newList
    else:
      break
  for tlist in lines.values():
    for entry in tlist:
      print entry,


def replaceAlphaNum(fileName, replace):
  for line in open(fileName):
    split = line.strip().split()
    for entry in split:
      if DIGIT.search(entry):
        print replace,
      else:
        print entry,
    print


def loadFileInDict(fileName, sep='\t'):
  content = {}
  for line in open(fileName, 'r'):
    line = line.strip()
    tokens = line.split(sep)
    content[tokens[0].strip()] = int(tokens[1])
  return content


def loadFileInTuples(fileName, sep='\t'):
  content = []
  for line in open(fileName, 'r'):
    line = line.strip()
    tokens = line.split(sep)
    content.append[(tokens[0].strip(), tokens[1].strip())]
  return content


def plain_text(html):
  try:
    return html2text.html2text(html)
  except:
    print 'Cant parse Html'
    return ''


def getDocumentText(fileName, dirPath):
  if os.path.exists(dirPath + '/' + fileName):
    dtext = open(dirPath + '/' + fileName, 'r').read()
    dec = dtext.decode('utf-8', 'ignore').lower()
    #assuming the the content is in html
    end = len(dec)
    for content in LEMR.finditer(dec):
      end = content.start()
    strt = 50
    for content in HTML.finditer(dec):
      strt = content.start()
    print fileName, strt, end, len(dec)
    return plain_text(dec[strt:end - 14].encode('ascii', 'ignore'))
  else:
    return ''


def loadFileInList(fileName, index, sep='\t'):
  eset = set()
  for line in open(fileName, 'r'):
    split = line.strip().split(sep)
    eset.add(split[index].strip())
  return eset


def allLetters(entry):
  if DIGIT.search(entry):
    return False
  if SYMB2.search(entry):
    return False
  return True


#load the pattern query \t entry1:value \t entry2:value
def loadDictFromFile(filename, delimit1, delimit2):
  entryDict = {}
  for line in open(filename, 'r'):
    split = line.strip().split(delimit1)
    if len(split) > 1:
      key = split[0].strip()
      entryDict[key] = {}
      for entry in split[1:]:
        fsplit = entry.split(delimit2)
        entryDict[key][fsplit[0]] = fsplit[1]
  return entryDict


def normalize(idict):
  dmin = min(idict.values())
  diff = max(idict.values()) - (dmin * 1.0)
  for entry in idict.keys():
    idict[entry] = (idict[entry] - dmin) / diff if diff > 0 else 0.0
  return idict


def stemFileContents(fileName):
  porter = stem.porter.PorterStemmer()
  toPrint = {}
  for line in open(fileName, 'r'):
    split = line.split(' ')
    #print split;
    '''if len(split) > 2:
			w1 = split[0];
			w2 = split[1];
			freq = float(split[-1]);
			key = porter.stem(w1) + ' '+ porter.stem(w2);
			#print key;
			if key not in toPrint:
				toPrint[key] =0.0;
			toPrint[key] += freq;
		'''
    if len(split) > 1:
      w1 = split[0]
      freq = float(split[-1])
      key = porter.stem(w1)
      if key not in toPrint:
        toPrint[key] = 0.0
      toPrint[key] += freq

  for entry, val in toPrint.items():
    print entry, val


def loadQueryList(fileName):
  queryList = {}
  for line in open(fileName, 'r'):
    split = line.split('\t')
    terms = []
    allTerms = ast.literal_eval(split[3].strip())
    for entry in allTerms:
      if entry[1] > 0.01:
        terms.append(entry)

    if len(terms) > 0:
      key = split[0].strip() + '_' + split[4].strip()
      query = split[2].strip()
      if query not in queryList:
        queryList[query] = {}
      if key not in queryList[query]:
        queryList[query][key] = terms
  return queryList


def combineDict(d1, d2):
  return dict(d1.items() + d2.items() + [(k, d1[k] + d2[k])
                                         for k in set(d1) & set(d2)])


def findInfo(file1, file2, index1, index2):
  toSearch = []
  for line in open(file1, 'r'):
    split = line.split('\t')
    #print split[index1]
    toSearch.append(split[index1])

  for line in open(file2, 'r'):
    split = line.split(' ')
    #print split
    if split[index2] in toSearch:
      print line.strip()


def encodeUTF(string):
  newString = ''
  for ch in string:
    try:
      nch = ch.encode('ascii', 'ignore')
    except UnicodeDecodeError, error:
      #print error.args, error.start, error.end, ch
      nch = ''
    newString += nch
  return newString


def main(argv):
  #replaceAlphaNum(argv[1],argv[2])
  #removeFreqWords(argv[1],int(argv[2]))
  #stemFileContents(argv[1]);
  #ngramDict = {}
  #for line in open(argv[1],'r'):
  #line = line.strip().lower()
  ##line = normalizeWithoutStem(line);
  #for ngram in getNGramsAsList(line,2):
  #if ngram not in stopSet:
  #if ngram not in ngramDict:
  #ngramDict[ngram] = 1.0
  #else:
  #ngramDict[ngram] +=1.0
  #
  #for entry in sorted(ngramDict.items(),reverse=True,key = lambda x:x[1]):
  #print entry[0] , '\t', entry[1]
  findInfo(argv[1], argv[2], int(argv[3]), int(argv[4]))


if __name__ == "__main__":
  main(sys.argv)
