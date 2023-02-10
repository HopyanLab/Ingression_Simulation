#!/usr/bin/env python3

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.collections import LineCollection
import argparse
from pathlib import Path

################################################################################
#===============================================================================
# plot_system
#===============================================================================
################################################################################

def plot_system (vertices, edges, faces,
				 types = np.array([]),
				 savefile = Path('./system_plot.svg')):
	colors = ['white', 'tab:red', 'tab:blue', 'tab:green', 'tab:purple']
	regions = np.empty(len(faces), dtype = object)
	for face_index, face in enumerate(faces):
		region = np.zeros(len(face), dtype = int)
		for edge_index, edge in enumerate(face):
			backward = 1 if edge < 0 else 0
			region[edge_index-1] = edges[abs(edge)-1, backward]-1
			region[edge_index] = edges[abs(edge)-1, 1-backward]-1
		regions[face_index] = region
	segments = np.zeros((len(edges),2,2), dtype = float)
	segments[:,0,:] = vertices[edges[:,0]-1]
	segments[:,1,:] = vertices[edges[:,1]-1]
	line_segments = LineCollection(segments, color='black')
	fig, ax = plt.subplots()
	if len(types) == len(faces):
		for region_index, region in enumerate(regions):
			ax.fill(vertices[region,0],
					vertices[region,1],
					color = colors[types[region_index]],
					alpha = 0.5)
	ax.add_collection(line_segments)
	ax.plot(vertices[:,0],
			vertices[:,1],
			color = 'black', 
			marker = '.', markersize = 6,
			linestyle = '')
	ax.plot(vertices[:,0],
			vertices[:,1],
			color = 'white',
			marker = '.', markersize = 1,
			linestyle = '')
	ax.tick_params( left=False,
					bottom=False,
					labelleft=False,
					labelbottom=False )
	plt.savefig(savefile, format=savefile.suffix.lstrip('.'))
	plt.close()
	return

################################################################################

if __name__ == '__main__':
	# Filenames can be passed as arguements so
	#  we use argparse module to parse them.
	parser = argparse.ArgumentParser(
						description = 'Plot system')
	# outfile = sys.argv[1]
	parser.add_argument('-o', '--outfile',
						nargs = 1,
						default = ['../plots/system_plot.svg'],
						type = str,
						required = False,
						help = 'file to put plot in (svg)')
	parser.add_argument('-vf', '--vertfile',
						nargs = 1,
						default = ['../output/vertices.txt'],
						type = str,
						required = False,
						help = 'file with vertex data')
	parser.add_argument('-ef', '--edgefile',
						nargs = 1,
						default = ['../output/edges.txt'],
						type = str,
						required = False,
						help = 'file with edge data')
	parser.add_argument('-pf', '--facefile',
						nargs = 1,
						default = ['../output/faces.txt'],
						type = str,
						required = False,
						help = 'file with face data')
	args = parser.parse_args()
	vertfile = Path(args.vertfile[0])
	edgefile = Path(args.edgefile[0])
	facefile = Path(args.facefile[0])
	vertices = np.loadtxt(vertfile, delimiter='\t')
	edges = np.loadtxt(edgefile, delimiter='\t')
	faces = np.loadtxt(facefile, delimiter='\t')
	plot_system(vertices, edges, faces,
				savefile = Path(args.outfile[0])
				)

################################################################################
# EOF
