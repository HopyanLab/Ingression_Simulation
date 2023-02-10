#!/usr/bin/env python3
import numpy as np
import argparse
import pickle
from pathlib import Path
from cell_tracks import cell_tracks
from parse_data import parse_data
from get_positions import get_positions

################################################################################
#===============================================================================
# compile_tracks
#===============================================================================
################################################################################

def add_time_point (cell_data, data_filepath):
	time = int(data_filepath.stem.split('_')[-1])
	vertices, edges, faces, types = parse_data(data_filepath)
	positions = get_positions(vertices, edges, faces)
	if cell_data.number_cells < len(positions):
		cell_data.resize_cells(len(positions))
		cell_data.types = types
	cell_data.add_time_point(time, positions)

################################################################################

def compile_tracks (dir_path):
	cell_data = cell_tracks(len(dir_path.glob('*.txt')),0)
	for data_filepath in dir_path.glob('*.txt'):
		add_time_point(cell_data ,data_filepath)
	with open(dir_path/'tracks.pkl', 'wb') as outstream:
		pickle.dump(cell_data, outstream)

################################################################################

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='convert data files')
	parser.add_argument('data', type=str, nargs='*', default='./output/',
						help='data file directory path')
	args = parser.parse_args()
	datapaths = list(map(Path, args.data))
	dirs_to_process = np.array([])
	for datapath in datapaths:
		if datapath.exists():
			if datapath.is_dir():
				for datafilepath in datapath.rglob('*.txt'):
					if datafilepath.parent.resolve() not in dirs_to_process:
						dirs_to_process = np.append(dirs_to_process,
											datafilepath.parent.resolve())
			else:
				pass #TODO: What to do here?
	for dir_path in dirs_to_process:
		compile_tracks(dir_path)

