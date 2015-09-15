import sys
import json
import urllib

import time

api_key = open('.api_key').read().strip()
service_url = 'https://www.googleapis.com/freebase/v1/search'


def getFreebaseEntities(query, limit):
  #for ngrams in getNGrams(query,query.count(' ')+1):
  #if hasAlpha(ngrams[0]):
  params = {'query': query, 'limit': limit, 'output':'(type)', 'key': api_key}
  url = service_url + '?' + urllib.urlencode(params)
  response = json.loads(urllib.urlopen(url).read())
  
  #print url, response
  #for result in response['result']:
  #	print result
  #	print result['name'] + ' (' + str(result['score']) + ')'
  yield query, response


def main(argv):
  limit = 20
  start = int(argv[2])
  i = 0
  for line in open(argv[1], 'r'):
    if i < start:
      i+=1
      continue
    else:
      line = line.strip();
      #split = line.split('\t')
      for ngram, response in getFreebaseEntities(line, limit):
        if 'error' in response:
          print response
          time.sleep(30)
          for ngram, response in getFreebaseEntities(line, limit):
            print ngram, '\t', response
          
        else:
          print ngram, '\t', response
        
    i += 1
    if i % 10 == 0:
      time.sleep(30)


if __name__ == '__main__':
  main(sys.argv)
