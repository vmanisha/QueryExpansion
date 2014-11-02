# -*- coding: utf-8 -*-
# contains routines to build plots

import matplotlib.pyplot as plt
import sys

def plot1(file1,xlabel1, ylabel1,fileDest):
	x = []
	y = []
	
	for line in open(file1,'r'):
		split = line.split('\t')
		x.append(float(split[0]))
		y.append(round(float(split[1]),3))
	l, = plt.plot(x, y, 'r-')
	plt.xlabel(xlabel1)	
	plt.ylabel(ylabel1)	
	plt.rcParams['xtick.major.pad']='8'
	#plt.title('C')
	plt.savefig(fileDest, bbox_inches='tight')
	#plt.shwow()


#plot multiple line segments with fixed y, x axis
def plotMultipleSys(data,xlab, ylab,fileDest,tit):
	#print '____PLOT____';
	i = 0;
	x = [];
	y = [];
	for sys, points in data.iteritems():
		
		for a, plist in sorted(points.items(), key =lambda x : x[0]) :
			val = (sum(plist)*1.0)/len(plist);
			
			x.append(a);
			y.append(val);
			
		if len(x) > 0 and len(y) > 0:
			l, = plt.plot(x, y,label=sys);
		
		i+=1;
		x = [];
		y = [];
		
	plt.xlabel(xlab);	
	plt.ylabel(ylab);	
	#plt.xscale('log')
	#plt.yscale('log')
	#plt.rcParams['xtick.major.pad']='4';
	plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0., title = tit);
	plt.savefig(fileDest, bbox_inches='tight');
	plt.close();

def plotHist(data,xlab, ylab):
	width = 0.24       # the width of the bars

	fig = plt.figure()
	ax = plt.subplot(111)
	rect = []
	colour = ['r','b','g', 'y']
	for i in range(len(data[1:])):
		#print i, data[0], data[i+1], [x+(width*i) for x in data[0]]
		rect.append(ax.bar([x+(width*i) for x in data[0]], data[i+1], width, color=colour[i]))
		

	# add some text for labels, title and axes ticks
	ax.set_ylabel(xlab)
	ax.set_xlabel(ylab)
	#ax.set_title('')
	ax.set_xticks([x+(width*1.5) for x in data[0]])
	
	data[0][-1] = '>6'
	xlabel = tuple(data[0])
	ax.set_xticklabels(xlabel )
	
	box = ax.get_position()
	ax.set_position([box.x0, box.y0 + box.height * 0.1,
                 box.width, box.height * 0.9])

	ax.legend((rect[0], rect[1], rect[2]),('All-Head', 'All-Tail','Head and Tail'),loc='upper center',
	fancybox=True, ncol=4, bbox_to_anchor=(0.5,-0.1))
	# Put a legend below current axis
	plt.show()
	#plt.savefig('paper/images/entity-head-tail-count.png')
	
#plot the band of entity popularity
if __name__ == '__main__':
	arg = sys.argv
	data = []
	done = False;
	for line in open(arg[1],'r'):
		split= line.strip().split();
		if not done:
			for i in range(len(split)):
				data.append([])
			done = True
		
		for i in range(len(split)):
			data[i].append(round(float(split[i]),3))
	print data						
	#plot1(arg[1])
	plotHist(data)
#plot the ratios of head:tail with respect to number of entities in query


