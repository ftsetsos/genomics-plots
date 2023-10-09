import matplotlib
import numpy as np
import sys
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import scipy.stats

qfiles=[]
listofk=[]
order_of_pops=[]
orderpops=0
cvvalues=[]
colororder=[]
show=0
save=0
autocolors=0

for i in sys.argv:
	if '.Q' in i:
		qfiles.append(i)
		listofk.append(int(i.split('.')[-2]))
	if '-poporder=' in i:
		with open(i.split('=')[1], 'r') as f:
			data=f.readlines()
			order_of_pops=data[0].rstrip().split(',')
		orderpops=1
	if '-colors=' in i:
		colororder=i.split('=')[1].split(',')
	if '-cv=' in i:
		with open(i.split('=')[1], 'r') as f:
			data=f.readlines()
			cvvalues=[j.split()[-1] for j in data]
	if '-autocolors' in i:
		autocolors=1

if len(qfiles) == 0:
	sys.exit('''No Q files loaded - At least one q file is needed
	Usage: python [path]/admixture-plot.py qfile1 qfile2 ... ''')

#######      SET COLORS
#######      The amount of colors listed here limit the number of Ks that can be plotted.
#######      Increment the list if you want to plot more than 12 Ks. Color codes are from
#######      the brewer2mpl 12-color colorset
colors=['#a6cee3','#1f78b4','#b2df8a','#33a02c','#fb9a99','#e31a1c','#fdbf6f','#ff7f00','#ffff99','#b15928','#cab2d6','#6a3d9a']

#######   Default colors
colorset=[colors[:i] for i in range(1,len(colors)+1)]

#######   If autocolors is turned on to guess the color assignments
if autocolors==1:
	autodata=[]
	for filename in qfiles:
		with open(filename, 'r') as f:
			tempdata=map(list, zip(*[map(float, i.split()[6:]) for i in f]))
			autodata.append(tempdata)

	colororder.append('01')
	
	rvalues=[]
	for numi, i in enumerate(autodata[1:]):
		for numj, j in enumerate(i):
			rvalues1=[]
			try:
				for k in autodata[numi+1:]:
					for l in k:
						rvalues1.append(scipy.stats.linregress(j,l)[2])
					print max(rvalues1),rvalues1.index(max(rvalues1)), numi,numj
			
			except:
				pass
	for i in rvalues:
		print i

#######   if using a color command to manually specify the colors.
if colororder!=[]:
	colorset=[[colors[0]]]
	if len(colororder)>10:
		for j in colororder:
			colorset.append([])
			colorword = [j[ik:ik+2] for ik in range(0, len(j), 2)]
			for ij in colorword:
				colorset[-1].append(colors[int(ij)])
	else:
		for j in colororder:
			colorset.append([])
			for ij in j:
				colorset[-1].append(colors[int(ij)])


#######   Start of the data categorizing by population and starting plotting

fig = plt.figure(facecolor='none')
fig.set_figheight(len(qfiles))

print 'Plotting admixture plot for', sys.argv[1].split('/')[-1].split('.')[0]

for number, filename in enumerate(qfiles):
	with open(filename, 'r') as f:
		data=f.readlines()

	populations = []
	pops=[]
	poplabels=[]
	numk=int(filename.split('.')[-2])
	
	for i in data:
		k = i.rstrip().split()
		if k[0][0] == '#':
			continue
		if k[0] not in [j[0] for j in populations]:
			populations.append([k[0]])
			pops.append(k[0])
		populations[pops.index(k[0])].append(k[1:6]+[0.0]+[float(i) for i in k[6:]])
	
	####SORT THE POPULATIONS
	
	if orderpops==1:
		populations.sort(key=lambda a: (order_of_pops.index(a[0])))

	####MAKE THE FINAL LIST TO PLOT
	
	if cvvalues==[]:
		admixplot = fig.add_subplot(len(qfiles),1,number+1, facecolor='white')
	if cvvalues!=[]:
		admixplot = fig.add_subplot(len(qfiles),2,2*number+1, facecolor='white')
	if len(data)<15:
		figlength=1
	else:
		figlength=3*np.log10(len(data))
	fig.set_figwidth(figlength)
	
	start=0
	for i in populations:
		barwidth=1
		indwidth=1
#		ind=np.arange(start,start+len(i[1:]),1.01)
		ind=np.linspace(start,start+len(i[1:])-1,len(i[1:]))*indwidth
		plotdata=[j[5:] for j in i[1:]]
		bottom=np.cumsum(plotdata, axis=1)
		for k in range(numk):
			color = colorset[numk-1][k%len(colorset)]
			plt.bar(ind, [p[k+1] for p in plotdata], bottom=[p[k] for p in bottom], width=indwidth, color=color,linewidth=0)
		poplabels.append([i[0],start+(float(len(i[1:]))/2)])
		plt.bar(ind[-1]+1*indwidth, 1, width=barwidth, color='white', edgecolor='none')
		start+=len(i[1:])+barwidth

	plt.xlim(0, ind[-1]+1)
	plt.ylim(0, 1)
	for spine in plt.gca().spines.values():
		spine.set_visible(False)
	plt.tick_params(axis='y', which='both', right='off',left='off')
	
	if numk!=max(listofk):
		plt.tick_params(axis='x',
		which='both',
		bottom='off',
		top='off',
		labelbottom='off',
		direction='out')
		
	if numk==max(listofk):
		plt.tick_params(axis='x',
						which='both',
						bottom='off',
						top='off',
						direction='out',
						pad=-5)
		plt.xticks([i[1] for i in poplabels],
					[i[0] for i in poplabels],
					ha='right',
					rotation=45,
					fontsize=8)
	
	plt.yticks([0.5], 
				['K='+str(numk)], 
				rotation=45, 
				fontsize=10)
	fig.subplots_adjust(left=0.02,
						bottom=0.20,
						right=0.97,
						top=0.85,
						wspace=0.2,
						hspace=0.2)
#	if numk==min(listofk):
#		plt.title('Plot of admixture results for K='+','.join([str(i) for i in listofk])+'\n', fontsize=12)
	
	if cvvalues!=[]:
		plt.yticks([0.5],
					['K='+str(numk)+'\nCV:'+cvvalues[number]],
					rotation=45,
					fontsize=10)


if orderpops==0:
	plt.savefig( 'admix-plot-' \
					+ sys.argv[1].split('/')[-1].split('.')[0] \
					+ '_'.join([str(i) for i in listofk]) \
					+'.pdf', 
					bbox_inches='tight', 
					facecolor=fig.get_facecolor(), 
					dpi=150 )
elif orderpops==1:
	plt.savefig( 'admix-plot-' \
					+ sys.argv[1].split('/')[-1].split('.')[0] \
					+'_'.join([str(i) for i in listofk]) \
					+'-ordered.pdf', 
					bbox_inches='tight', 
					facecolor=fig.get_facecolor(), 
					dpi=150 )
