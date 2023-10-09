import matplotlib
from matplotlib.text import TextPath
import brewer2mpl
import numpy as np
import sys
import subprocess
import gzip
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import argparse

parser = argparse.ArgumentParser(description='Manhattan plot for GWAS p-values.')
parser.add_argument('-f','--file',
					help='P-value file',
					required=True)
parser.add_argument('-s','--specs',
					help='Columns for p-values, chromosome, position and snpid. ' +
							'Space-separated values eg. 9 0 2 1',
					type=int,
					nargs='+',
					default=[0,0,0,0])
parser.add_argument('-l','--lines',
					help='Number of lines in header',
					type=int,
					required=True)
parser.add_argument('-t', '--threshold',
					help='Threshold of p-values under which to plot.',
					default=0.05,
					type=float)
args = parser.parse_args()

colors= ['black','grey']
header=args.lines
pval,chrom,position,snp=args.specs
threshold=args.threshold

#highlight=0
#hsnps=[]
#for i in sys.argv:
#	if '-highlight' in i:
#		highlight=1
#		with open(i.split('=')[1]) as f:
#			hsnps = [j.rstrip() for j in f]

if args.file.split('.')[-1] == 'gz':
	with gzip.open(args.file, 'rb') as f:
		data=f.readlines()
else:
	with open(args.file, 'r') as f:
		data=f.readlines()

chroms=list(set(i.split()[chrom] for i in data[header:]))
chroms.sort(key=int)
plotdata=[]
chromindices=[]
for i in chroms:
	plotdata.append([])
	chromindices.append([])

for j,i in enumerate(data):
	k=i.split()
	try:
		if float(k[pval]) < threshold:
			plotdata[chroms.index(k[chrom])].append([k[pval],k[chrom],k[position],k[snp],j])
	except ValueError:
		continue

fig = plt.figure()
manhattanplot = fig.add_subplot(111)
fig.set_facecolor('none')
fig.set_figheight(6)
fig.set_figwidth(12)

indexmax=0
for j,i in enumerate(plotdata):
	if len(i)==0:
		chromindices[j].append(0)
		chromindices[j].append(0)
		continue
	pvalues=np.absolute(np.log10([float(k[0]) for k in i]))
	indices=[k[-1] for k in i]
	color = colors[j%len(colors)]
	chromindices[j].append(np.min(indices))
	chromindices[j].append(np.max(indices))
	indexmax=np.max(indices+[indexmax])
	manhattanplot.scatter(indices, pvalues, marker='o',s=1, color=color)

#if highlight==1:
#	

plt.axhline(y=5.,color='blue', alpha=0.5)
plt.axhline(y=7.3,color='red', alpha=0.5)

plt.xlim(0, indexmax+1)
plt.ylim(abs(np.log10(threshold)))

plt.tick_params(axis='x', which='both',top=False, direction='out')
plt.tick_params(axis='y', which='both', direction='out')
plt.xticks([i[0]+(i[1]-i[0])/2 for i in chromindices], chroms, fontsize=8, rotation=0)

plt.title('Manhattan plot of GWAS p-values')
plt.xlabel('Chromosomes')
plt.ylabel('$-log_{10}(P)$')

plt.savefig('manhattan-plot-'+args.file.split('/')[-1]+'.png', bbox_inches='tight', facecolor=fig.get_facecolor(), dpi=150, edgecolor='none')

