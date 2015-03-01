# -*- coding: utf-8 -*-
# contains routines to build plots

import matplotlib.pyplot as plt
import sys, os;

def plotLine(data,xlabel1, ylabel1,fileDest):
	x = []
	y = []
	
	for entry in data:
		#print entry[0], entry[1];
		x.append(entry[0]);
		val = None;
		if type(entry[1]) is list:
			if len(entry[1]) > 0:
				val = (sum(entry[1])*1.0)/len(entry[1]);
		else:
			val = entry[1];
		y.append(val);
	l, = plt.plot(x, y, 'r-')
	plt.xlabel(xlabel1)	
	plt.ylabel(ylabel1)	
	plt.rcParams['xtick.major.pad']='8'
	#plt.title('C')
	plt.savefig(fileDest, bbox_inches='tight')
	#plt.shwow()

def plotScatter(data,xlabel1, ylabel1,fileDest):
	x = []
	y = []
	
	for entry in data:
		print entry[0], entry[1];
		x.append(entry[0]);
		val = entry[1];
		y.append(val);
	plt.scatter(x, y)
	plt.xlabel(xlabel1)	
	plt.ylabel(ylabel1)	
	#plt.rcParams['xtick.major.pad']='8'
	#plt.title('C')
	#plt.savefig(fileDest, bbox_inches='tight')
	plt.show()

#plot multiple line segments with fixed y, x axis
def plotMultipleSys(data,xlab, ylab,fileDest,tit):
	#print '____PLOT____';
	i = 0;
	x = [];
	y = [];
	#ppoints = ['rx','gx','bx','g+','r+','b+']
	for sys, points in data.iteritems():
		print sys,'\t', len(points)
		if len(points) > 2:
			for a, plist in sorted(points.items(), key =lambda x : x[0]) :
				val = None;
				if	type(plist) is list:
					val = (sum(plist)*1.0)/len(plist);
				else:
					val = plist;
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
	width = 0.20       # the width of the bars

	fig = plt.figure()
	ax = plt.subplot(111)
	rect = []
	colour = ['r','b','g', 'm']
	for i in range(len(data[1:])):
		print i, data[0], data[i+1], [x+(width*i) for x in range(len(data[0]))]
		rect.append(ax.bar([x+(width*i) for x in range(len(data[0]))], data[i+1], width, color=colour[i]))
		

	# add some text for labels, title and axes ticks
	ax.set_ylabel(xlab)
	ax.set_xlabel(ylab)
	#ax.set_title('')
	
	ax.set_xticks([x+(width*1.5) for x in range(len(data[0]))])
	
	xlabel = tuple(data[0])
	ax.set_xticklabels(xlabel )
	
	box = ax.get_position()
	print box.x0, box.y0;
	
	ax.set_position([box.x0, box.y0 + box.height * 0.1,
                 box.width, box.height * 0.9])

	ax.legend((rect[0], rect[1], rect[2]),('0', '1-2','3 or more'),loc='upper center',
	fancybox=True, ncol=3, bbox_to_anchor=(0.5,-0.1))
	# Put a legend below current axis
	plt.show()
	#plt.savefig('paper/images/entity-head-tail-count.png')
	
#plot the band of entity popularity
if __name__ == '__main__':
	argv = sys.argv;
	toPlot = {};
	
	for ifile in os.listdir(argv[1]):
		name = '20'+ ifile[:ifile.find('.')];
		if name not in toPlot:
			toPlot[name] = {};
		for line in open(argv[1]+'/'+ifile,'r'):
			split = line.split(' ');
			count = int(split[-1]);
			lab = None;
			if count == 0:
				lab = '0';
			elif count > 0 and count < 3:
				lab = '1-2';
			else :
				lab = '3 or more';
			
			if lab not in toPlot[name]:	
				toPlot[name][lab]=0.0;
			toPlot[name][lab]+=1.0;
	data = [[],[],[],[]];
	
	for entry,dlist in sorted(toPlot.items()):
		data[0].append(entry);
		total = sum(dlist.values());
		data[1].append(dlist['0']/total);
		data[2].append(dlist['1-2']/total);
		data[3].append(dlist['3 or more']/total);
		
	plotHist(data, '% of Queries', 'Track Year')

#plot the ratios of head:tail with respect to number of entities in query


#data = []
	#done = False;
	#for line in open(arg[1],'r'):
		#split= line.strip().split();
		#if not done:
			#for i in range(len(split)):
				#data.append([])
			#done = True
		#
		#for i in range(len(split)):
			#data[i].append(round(float(split[i]),3))
	#print data						
	##plot1(arg[1])
	
