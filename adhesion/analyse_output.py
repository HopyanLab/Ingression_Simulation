#!/usr/bin/env python3
import argparse
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import pylab as pl
from pathlib import Path
from parse_data import parse_data
from get_positions import get_positions

################################################################################

def cast_list(test_list, data_type):
	return list(map(data_type, test_list))

################################################################################

def compile_positions(data_dir, ten_values, time_points):
	positions = []
	for index in range(len(ten_values)):
		positions.append(None)
		positions[index] = np.zeros(0, dtype = float)
	run_dirs = (x for x in data_dir.iterdir() if x.is_dir())
	for run_dir in run_dirs:
		run_number = int(run_dir.stem.split('_')[-1])-1
		for index, parameter in enumerate(values):
			positions[index] = np.append(positions[index],
				get_positions(vertices, edges, faces)[types == 3,1])
	return positions

################################################################################

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='convert data files')
	parser.add_argument('data', type=str, nargs='?', default='./output',
						help='data file directory path')
	data_dir = Path(parser.parse_args().data)
	coarse = True
	# make list of runs
	run_values = np.zeros(0, dtype = int)
	run_dirs = (x for x in data_dir.iterdir() if x.is_dir())
	run_dirs = list(run_dirs)
	for index, run_dir in enumerate(run_dirs):
		run_values = np.append(run_values, int((run_dir.name.split('_')[-1])))
	run_values = np.sort(run_values)
	# make list of standard deviation parameters
	ten_values = np.zeros(0, dtype = float)
	ten_dirs = (x for x in run_dirs[0].iterdir() if x.is_dir())
	ten_dirs = list(ten_dirs)
	for index, ten_dir in enumerate(ten_dirs):
		ten_values = np.append(ten_values, float((ten_dir.name.split('_')[-1])))
	ten_values = np.sort(ten_values)
	# make list of time poionts
	time_values = np.zeros(0, dtype = int)
	time_files = (x for x in ten_dirs[0].iterdir() if x.suffix == '.txt')
	time_files = list(time_files)
	for index, time_file in enumerate(time_files):
		time_values = np.append(time_values,
									int((time_file.stem.split('_')[-1])))
	time_values = np.sort(time_values)
	if coarse:
		coarse_values = np.zeros(0, dtype = int)
		for time_value in time_values:
			if time_value % 10 == 0:
				coarse_values = np.append(coarse_values, time_value)
		time_values = coarse_values
	# make tracks
	tracks = np.zeros((len(ten_values), len(time_values)),
						dtype = float)
	errors = np.zeros_like(tracks)
	full_tracks = np.zeros((len(ten_values), len(time_values), len(run_values)),
							dtype = float)
	initial_positions = np.zeros((len(ten_values), len(run_values)),
									dtype = float)
	errors = np.zeros_like(tracks)
	temp_values = np.zeros(len(run_values), dtype = float)
	for ten_index, ten_value in enumerate(ten_values):
		for time_index, time_value in enumerate(time_values):
			for run_index, run_value in enumerate(run_values):
				if time_index == 0:
					continue
				vertices, edges, faces, types = parse_data(data_dir / \
							(f'run_{run_value:02d}') / \
							(f'tension_{ten_value:1.2f}') / \
							(f'time_{time_value:d}.txt'))
				positions = get_positions(vertices, edges, faces)[types == 3,1]
				temp_values[run_index] = np.mean(positions)
				if time_index == 1:
					initial_positions[ten_index, run_index] = \
													temp_values[run_index]
				full_tracks[ten_index, time_index, run_index] = \
								(temp_values[run_index] - \
									initial_positions[ten_index, run_index])**2
#				if time_index == 0:
#					pos_1 = get_positions(vertices, edges, faces)[
#																types == 1,1]
#					pos_2 = get_positions(vertices, edges, faces)[
#									np.logical_or(types == 2, types == 3),1]
#					print(np.mean(pos_1) - (np.min(pos_1) + np.max(pos_2))/2)
			tracks[ten_index, time_index] = np.mean(
						(temp_values - initial_positions[ten_index]))
			#			(temp_values - initial_positions[ten_index])**2)
			errors[ten_index, time_index] = np.std(
						(temp_values - initial_positions[ten_index])) / \
								np.sqrt(len(run_values))
	np.savetxt('./out.csv', tracks, delimiter=',')
	for run_index, run_value in enumerate(run_values):
		np.savetxt(f'./output/out_{run_index+1:02d}.csv',
					full_tracks[:,:,run_index],
						delimiter=',')
	# plot
	plt.rcParams['image.cmap'] = 'hsv'
	fig = plt.figure(figsize=(9,6))
	ax = fig.add_subplot(111)
#	ax.plot([-1,max(time_values)+1],[4.65,4.65],
#			color = 'black',
#			label= 'epi bottom')
#	ax.grid(True, ls='dotted')
	ax.set_xticks(time_values)
	ax.set_xticklabels([])
	ax.set_yticklabels([])
	for ten_index, ten_value in enumerate(ten_values):
		ax.plot(time_values[1:], tracks[ten_index,1:],
					linestyle = '-',
					color = pl.cm.hsv(1.-(ten_index+1)/(len(ten_values))),
					label = f'{int(ten_value*500):d}%',
					zorder = 8)
	#	ax.errorbar(time_values[1:], tracks[ten_index,1:], errors[ten_index,1:],
	#				linestyle = '',
	#				color = pl.cm.hsv(1.-(ten_index+1)/(len(ten_values))))
		ax.fill_between(time_values[1:],
						tracks[ten_index,1:] - errors[ten_index,1:],
						tracks[ten_index,1:] + errors[ten_index,1:],
						color = pl.cm.hsv(1.-(ten_index+1)/(len(ten_values))),
						alpha = 0.2,
						zorder = 6)
	
	plt.rcParams.update({'font.size': 16})
	ax.legend()
	plt.savefig('./{0}.svg'.format(data_dir.name))

################################################################################
# EOF
