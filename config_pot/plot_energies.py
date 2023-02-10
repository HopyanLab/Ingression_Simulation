#!/usr/bin/env python3
import numpy as np
from matplotlib import pyplot as plt
from parse_data import parse_data

################################################################################
#===============================================================================
# plot_energies
#===============================================================================
################################################################################

N = 96
T = 125

if __name__ == '__main__':
	time_points = np.arange(1,125)
	energy = np.zeros((N,T))
	ing_time = np.zeros(N, dtype = int)
	for file_index in range(N):
		for time_index in range(T):
			file_name = f'./output_{file_index+1:02d}/time_{time_index:d}.txt'
			with open(file_name) as instream:
				for line_index, line in enumerate(instream):
					if line_index > 1:
						break
					elif line_index == 1:
						energy[file_index, time_index] = float(line)
			if ing_time[file_index] == 0:
				double_break = False
				vertices, edges, faces, types = parse_data(file_name)
				for edge_number in faces[types == 3][0]:
					for face in faces[types == 1]:
						if edge_number in face or -edge_number in face:
							ing_time[file_index] = time_index
							double_break = True
							break
					if double_break:
						break
	mask = np.logical_and(ing_time > 10, ing_time < (T - 20))
	energy = energy[mask]
	ing_time = ing_time[mask]
	good_sims = len(ing_time)
	shifted_energy = np.zeros((good_sims,30))
	for sim_index in range(good_sims):
		t_0 = ing_time[sim_index]
		shifted_energy[sim_index] = energy[sim_index, t_0-10:t_0+20]
	mean_energy = np.mean(shifted_energy, axis=0)
	mean_energy = mean_energy - mean_energy[-1]
	spread = np.std(shifted_energy, axis=0)
	time_points = np.arange(1,25)
	mean_energy = mean_energy[3:27]
	spread = spread[3:27]
	plt.plot(time_points,
			 mean_energy,
			 linestyle = '-',
			 marker = '',
			 color = 'tab:red')
	plt.fill_between(time_points,
					 mean_energy - spread,
					 mean_energy + spread,
					 color = 'tab:red',
					 alpha = 0.2)
	plt.show()

################################################################################
# EOF
