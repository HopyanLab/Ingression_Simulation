#!/usr/bin/env python3
import numpy as np
from matplotlib import pyplot as plt
from pathlib import Path
import subprocess

################################################################################
#===============================================================================
# run_sims
#===============================================================================
################################################################################

if __name__ == '__main__':
	for index in range(1,97):
		current_dir = Path('./')
		out_dir = current_dir / 'output'
		Path.mkdir(out_dir, exist_ok = True)
		with open('./sim.fe', 'w') as outstream:
			outstream.write('ready\nJ\n0.005\nrelax\nJ\nrelax\n')
			outstream.write('ing_std := 0.16;\ndo_oscillations := 1;\n')
			outstream.write('nonlocal_counter := 1;\n random_seed := ')
			random_int = np.random.randint(1,1000)
			outstream.write(f'{random_int:d};\nrun_system(125);\nq\nq\n')
		subprocess.check_call(['evolver','-fsim.fe','-x',
							   './initial_state_paper.fe'])
		out_dir.rename(current_dir / f'output_{index:02d}')

################################################################################
# EOF
