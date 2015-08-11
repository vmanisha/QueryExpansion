import sys
from utils.coOccurrence import CoOccurrence
from utils import getNGramsAsList
from nltk import stem
from queryLog import normalize
from utils import stopSet


def main(argv):
  #for each query
  #get bi-grams, unigrams and update frequency

  coOccur = CoOccurrence()
  stemmer = stem.porter.PorterStemmer()
  for line in open(argv[1], 'r'):
    split = line.strip().split('\t')

    query = normalize(split[0].strip(), stemmer)
    freq = int(split[1].strip())
    #generate ngrams
    ngrams = getNGramsAsList(query, 1)
    #if it has more than one term
    lngrams = len(ngrams)
    if lngrams > 1:

      for i in range(lngrams - 1):
        if ngrams[i] not in stopSet and len(ngrams[i]) > 2:
          for j in range(i + 1, lngrams):
            if ngrams[j] not in stopSet and len(ngrams[j]) > 2:
              coOccur.updateStats(ngrams[i], ngrams[j], freq)
  coOccur.setTermTotal()
  #for each query find the terms highly co-occured wth
  for line in open(argv[2], 'r'):
    split = line.split('\t')
    query = normalize(split[1].lower().strip(), stemmer)
    nGrams = getNGramsAsList(query, 1)
    toScore = set()
    result = {}

    for entry in nGrams:
      elist = coOccur.getNeighbours(entry)
      if elist:
        toScore |= set(elist)

    for term1 in toScore:
      if term1 not in query:
        result[term1] = 0.0
        for term2 in nGrams:
          pmi = coOccur.getPMI(term1, term2, 50)
          result[term1] += pmi
        result[term1] /= len(nGrams)

    for entry in result.keys():
      if result[entry] == 0:
        del result[entry]

    sort = sorted(result.items(), reverse=True, key=lambda x: x[1])
    print query, '\t', '\t'.join('{0}:{1}'.format(x[0], round(x[1], 3))
                                 for x in sort[:50])


def getTop50(fileName):
  for line in open(fileName, 'r'):
    split = line.split('\t')
    toWrite = '\t'.join(split[:51])
    print toWrite


if __name__ == '__main__':
  main(sys.argv)
  #argv = sys.argv
  #getTop50(argv[1])
