# -*- coding: utf-8 -*-
from twitter import *
import json
import time
# XXX: Go to http://dev.twitter.com/apps/new to create an app and get values
# for these credentials, which you'll need to provide in place of these
# empty string values that are defined as placeholders.
# See https://dev.twitter.com/docs/auth/oauth for more information
# on Twitter's OAuth implementation.

CONSUMER_KEY = 't0Zomb2Fyerok8xetDdKYRdqX'
CONSUMER_SECRET ='J1obfw1Mltw3OcWolimFoo1qPXTgOjqNkLMnR9sicpUjUE6wGM'
OAUTH_TOKEN = '154412671-R3J9O4gyqdfpUi2oiNIJlakESCP8fW8DrrbB9cdn'
OAUTH_TOKEN_SECRET = 'jrlTFpC58hsxEkO7BvUgamTxvjAmYD6z21OtAf2hdisa4'

#auth = twitter.oauth.OAuth(OAUTH_TOKEN, OAUTH_TOKEN_SECRET,
#                           CONSUMER_KEY, CONSUMER_SECRET)

#twitter_api = twitter.Twitter(auth=auth)

# Nothing to see by displaying twitter_api except that it's now a
# defined variable

hashTags = ['#tvdebates','#TVDebates','#UKelection','#GeneralElection2015',\
'#ukelection2015','#UKelection2015','#DavidCameron','#Edmiliband', \
'#GE2015','#generalelections2015', '#labour', '#GE15'\
'#election2015', '#conservatives', '#tvdebates2015']
count = 100


t = Twitter(auth=OAuth(OAUTH_TOKEN, OAUTH_TOKEN_SECRET, CONSUMER_KEY, CONSUMER_SECRET))

# Get your "home" timeline
for query in hashTags:
	# See https://dev.twitter.com/docs/api/1.1/get/search/tweets
	search_results = t.search.tweets(q=query, count=count)
	statuses = search_results['statuses']
	print len(statuses), json.dumps(statuses)
	i=0
	# Iterate through 5 more batches of results by following the cursor
	for _ in range(49):
	    #print "Length of statuses", len(statuses)
		try:
			next_results = search_results['search_metadata']['next_results']
		except KeyError, e: # No more results when next_results doesn't exist
			#print e, search_results['search_metadata']
			break

		kwargs = dict([ kv.split('=') for kv in next_results[1:].split("&") ])
		search_results = t.search.tweets(**kwargs)
		statuses = search_results['statuses']
		print len(statuses), json.dumps(statuses)
		if i % 10 == 0:
			#sleep
			time.sleep(300)
		i+=1
		#break
		# Show one sample search result by slicing the list...	
	#break
	#print len(statuses), json.dumps(statuses)
