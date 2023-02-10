#!/usr/bin/env python3
import numpy as np
from matplotlib import pyplot as plt
from pathlib import Path
import argparse
from plot_system import plot_system
from parse_data import parse_data

################################################################################
#===============================================================================
# plot_data
#===============================================================================
################################################################################

def plot_data (data_filepath):
	vertices, edges, faces, types = parse_data(data_filepath)
	if len(vertices) > 0:
		plot_system(vertices, edges, faces, types,
					savefile = data_filepath.with_suffix('.png'))

################################################################################

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='plot txt data files')
	parser.add_argument('data', type=str, nargs='*', default='./output',
						help='data file directory path')
	args = parser.parse_args()
	datapaths = list(map(Path,args.data))
	files_to_process = np.array([])
	for datapath in datapaths:
		if datapath.exists():
			if datapath.is_dir():
				for datafilepath in datapath.rglob('*.txt'):
					if datafilepath.resolve() not in files_to_process:
						files_to_process = np.append(files_to_process,
													 datafilepath.resolve())
			else:
				if datapath.resolve() not in files_to_process:
					files_to_process = np.append(files_to_process,
												 datapath.resolve())
	for data_filepath in files_to_process:
		plot_data(data_filepath)

################################################################################
# EOF
