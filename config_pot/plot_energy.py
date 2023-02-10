#!/usr/bin/env python3
import numpy as np
from matplotlib import pyplot as plt

################################################################################
#===============================================================================
# plot_energies
#===============================================================================
################################################################################

file_index = 15
T = 125

if __name__ == '__main__':
	energy = np.zeros(T)
	for time_index in range(T):
		with open(f'./output_{file_index+1:02d}' + \
				  f'/time_{time_index:d}.txt') as instream:
			for line_index, line in enumerate(instream):
				if line_index > 1:
					break
				elif line_index == 1:
					energy[time_index] = float(line)

	plt.plot(np.arange(T),
			 energy,
			 linestyle = '-',
			 marker = '',
			 color = 'tab:red')
	plt.show()

################################################################################
# EOF
