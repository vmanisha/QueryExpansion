import sys
import json
import urllib
from Utils import getNGrams
from QueryLog import hasAlpha, getQuery

api_key = open(".api_key").read().strip()
service_url = 'https://www.googleapis.com/freebase/v1/search'

def getFreebaseEntities(query,limit):
	for ngrams in getNGrams(query,query.count(' ')+1):
		if hasAlpha(ngrams[0]):
			params = {
				'query': ngrams[0],
				'key': api_key,
				'limit':limit
			}
			url = service_url + '?' + urllib.urlencode(params)
			response = json.loads(urllib.urlopen(url).read())
			#print url, response
			#for result in response['result']:
			#	print result
			#	print result['name'] + ' (' + str(result['score']) + ')'
			yield ngrams[0], response

def main(argv):
	limit = 20
	for query in getQuery(argv[1],int(argv[2])):
		for ngram, response in getFreebaseEntities(query, limit):
			print query ,'\t', ngram,'\t',  response

if __name__ == "__main__":
	main(sys.argv)
