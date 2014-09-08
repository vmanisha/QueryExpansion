# -*- coding: utf-8 -*-
import networkx as nx

class SimpleWalk:
	
	def __init__(self):
		self.graph = nx.Graph()
	
	def addEdge(self, word1, word2, score):
		self.graph.add_edge(word1, word2, weight= score)
	
	def walk(self):
		return nx.algorithms.link_analysis.pagerank(self.graph)
	

	