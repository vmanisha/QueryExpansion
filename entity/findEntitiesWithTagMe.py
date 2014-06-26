import sys
import requests
import ast
URL = "http://tagme.di.unipi.it/tag"
KEY = "verma2014"

def getEntities(query):
	query = query.replace(' ','+')
	data = {"key":KEY,"text":query,"include_categories":"true"}
	response = requests.get(URL,params=data)
	return response.text

def main(argv):
	#load taskVector
	done = set()
	for line in open(argv[1],'r'):
		split = line.strip().split('\t')
		taskDict = ast.literal_eval(split[-1])
		#load the tasks and entity vector
		for task in taskDict[argv[2]]['tasks'].keys():
		#format task : {entity : {score: , match : }, entity : {score: , match :}}
 			for entry in task:
				if entry not in done:
					jString = getEntities(entry)
					print split[0],"\t",split[1],"\t",entry,"\t", jString.encode('ascii','ignore')
					#eJson = ast.literal_eval(jString)
					done.add(entry)
	#for each query
		#get the entity vector from tagme
		

if __name__ == '__main__':
	main(sys.argv)


