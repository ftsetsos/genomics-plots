import matplotlib
from matplotlib.text import TextPath
import brewer2mpl
import numpy as np
import sys
import subprocess
matplotlib.use('Agg')
import matplotlib.pyplot as plt

#########         To use Arial fonts
from matplotlib import rc
rc('font',**{'family':'sans-serif','sans-serif':['Arial']})


if len(sys.argv) < 2:
	print '''	PCA 2D plotting script.
	Usage: python pca-2d-plot_v2.py [evec file] #,#[the PCs to plot] -highlight=[name of samples to highlight - optional] -eval[optional] -points=[size of points]
	
	'''
	sys.exit()

print 'Plotting', sys.argv[1], 'with', ' '.join(sys.argv[2:])

with open(sys.argv[1], 'r') as f:
	data=f.readlines()

populations = []
names = []

pcs=[int(i) for i in sys.argv[2].split(':')]
pc = [ [] for i in range(max(pcs))]
status=-1

letters=0
evaldat=0
highlight=[]
highlightdat=[]
size=30

for i in sys.argv:
	if '-letters' in i:
		letters=1
	if '-eval' in i:
		evaldat=1
	if '-highlight=' in i:
		with open(i.split('=')[1], 'r') as f:
			highlight = [ j.rstrip() for j in f]
	if '-points=' in i:
		size=int(i.split('=')[1])

#####     Separate into populations
for i in data[:]:
	k = i.split()
	if k[0][0] == '#':
		continue
	if k[0] in highlight:
		highlightdat.append([k[0]]+[k[j] for j in pcs]+[k[status]])
		continue
	if k[status] not in populations:
		populations.append(k[status])
		for j in pcs:
			pc[j-1].append([])
		names.append([])
	for j in pcs:
		pc[j-1][populations.index(k[status])].append(float(k[j]))
	names[populations.index(k[status])].append(k[status])

#####     Set  the colors
colorset = ['blue', 'green','red', 'magenta', 'black', 'Olive',
			'HotPink', 'DimGray', 'DarkViolet', 'Orange', 'SaddleBrown',
			'Teal', 'Tan', 'cyan']
markers = [ "o", "v", "^", ">", "<" , "s",
			"p", "*", "H", "D", "h", "d"] #,'+', 'x', '_', '|'
almost_black = '#262626'
if len(highlight) == 0:
	popcolors = {j: colorset[i%len(colorset)] for (i,j) in enumerate(set([i.split(',')[0] for i in populations]))}
	popmarkers = {j: markers[i%len(markers)] for (i,j) in enumerate(set([i.split(',')[-1] for i in populations]))}
elif len(highlight) >= 1:
	popcolors = {j: 'gray' for (i,j) in enumerate(set([i.split(',')[0] for i in populations]))}
	popmarkers = {j: '.' for (i,j) in enumerate(set([i.split(',')[-1] for i in populations]))}


#####    Start plotting
fig = plt.figure()
pcaplot = fig.add_subplot(111, facecolor='white')
fig.set_facecolor('none')
fig.set_figheight(6)
fig.set_figwidth(8)

for i in xrange(len(populations)):
	color = popcolors[populations[i].split(',')[0]]
	marker = popmarkers[populations[i].split(',')[-1]]
	
	if letters==1:
		pcaplot.scatter(pc[pcs[0]-1][i],
						pc[pcs[1]-1][i],
						marker=TextPath((0, 0), populations[i][:], size=size),
						facecolor=color,
						edgecolor=almost_black,
						s=size,
						linewidths=0.1,
						alpha=1,
						label=populations[i]+'-'+str(len(pc[pcs[0]-1][i])))
	elif letters==0:
		if populations[i]=='none':
			pcaplot.scatter(pc[pcs[0]-1][i],
							pc[pcs[1]-1][i],
							marker='o',
							facecolor='grey',
							edgecolor='none',
							s=10,
							linewidths=1,
							alpha=0.5,
							label=populations[i]+'-'+str(len(pc[pcs[0]-1][i])))
		else:
			pcaplot.scatter(pc[pcs[0]-1][i],
							pc[pcs[1]-1][i],
							marker=marker,
							facecolor='none',
							edgecolor=color,
							s=size,
							linewidths=1,
							alpha=1,
							label=populations[i]+'-'+str(len(pc[pcs[0]-1][i])))

if len(highlight) >= 1:
	for j,i in enumerate(highlightdat):
		color=colorset[j%len(colorset)]
		marker=markers[j%len(markers)]
		pcaplot.scatter(i[1],
						i[2],
						marker=marker,
						facecolor='none',
						edgecolor=color,
						s=10,
						label=i[0])

pcaplot.grid(	color=almost_black,
				linestyle='--',
				alpha=0.5,
				dashes=(50,50),
				linewidth=0.1,
				which='both')
plt.tick_params(axis='both',
				labelsize=8,
				direction='out',
				colors='#1a1a1a')

pcaplot.spines["top"].set_visible(False)
pcaplot.spines["right"].set_visible(False)
pcaplot.spines["bottom"].set_visible(False)
pcaplot.spines["left"].set_visible(False)
fig.subplots_adjust(left=0.06,
					bottom=0.06,
					right=0.99,
					top=0.95,
					wspace=0.2,
					hspace=0.2)

pcaplot.set_title("PC"+str(pcs[0])+" vs PC"+str(pcs[1])+" plot\n")


######           Calculate variance explained
if evaldat==1:
	with open('.'.join(sys.argv[1].split('.')[:-1])+'.eval', 'r') as f:
		evaldata = [float(i) for i in f.readlines()]
		plt.xlabel("PC"+str(pcs[0])+ \
					" - "+str(100*evaldata[pcs[0]-1]/sum(evaldata))[:5]+ \
					'% of total variance explained')
		plt.ylabel("PC"+str(pcs[1])+ \
					" - "+str(100*evaldata[pcs[1]-1]/sum(evaldata))[:5]+ \
					'% of total variance explained')
else:
	plt.xlabel("$PC"+str(pcs[0])+"$")
	plt.ylabel("$PC"+str(pcs[1])+"$")

######...........Calculate number of columns for legend (works only if legend is horizontal)
numcol=6
if 15 < max([len(i) for i in populations]) < 20:
	numcol=5
elif 20 < max([len(i) for i in populations]):
	numcol=4


legend = pcaplot.legend(scatterpoints=1,
						fontsize=9,
						ncol=numcol,
						fancybox=True,
						bbox_to_anchor=(-0.05, -0.1),
						loc=2,
						borderaxespad=0.,
						numpoints=1,
						facecolor='none',
						edgecolor='black')

savename='pca-plot-'+ \
			'.'.join(sys.argv[1].split('/')[-1].split('.')[:-1])+ \
			'-'+sys.argv[2]+'-2d'

if letters==1:
	savename=savename+'-letters'

plt.savefig(savename+'.pdf',
			bbox_inches='tight',
			facecolor=fig.get_facecolor(),
			dpi=150,
			edgecolor='none')
