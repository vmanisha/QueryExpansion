import ast
import sys
def readGraphFromFile(fileName):
	graph = {}
	for line in open(fileName,'r'):
		node, edges = parseGraphLine(line)
		if node not in graph:
			graph[node] = edges
		
	return graph

def parseGraphLine(line):
	split = line.split('{')
	node = split[0].strip()
	edges = '{'+split[1].strip()
	#print node, edges
	return node, ast.literal_eval(edges)
		

def sparseMultWithMatInFile(fileName,graph):
	power = {}
	for line in open(fileName, 'r'):
		x, neigh = parseGraphLine(line)
		power = {}
		#if x not in power:
		#	power[x] = {}
		for y,value in neigh.iteritems():
				for z,value2 in graph[y].iteritems():
					#power[x][z] = power[x].setdefault(z,0.0) + (value*value2)
					power[z] = power.setdefault(z,0.0) + (value*value2)
		print x,'\t', power
		
	#return power;
	
def main(argv):
	graph = readGraphFromFile(argv[1])
	sparseMultWithMatInFile(argv[2], graph)
	
	#for entry, elist in power.iteritems():
	#	print entry, '\t', elist	
	
if __name__ == '__main__':
	main(sys.argv)		
