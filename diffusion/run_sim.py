#!/usr/bin/env /usr/bin/python3
import numpy as np
import os
import subprocess as sp
import multiprocessing as mp
from pathlib import Path
from timer import timer
from make_system import *

################################################################################
#===============================================================================
# run_sim.py
#===============================================================================
################################################################################

base_dir = Path(__file__).resolve().parent
out_dir = base_dir/'output'
out_dir.mkdir(parents=True, exist_ok=True)
cores_to_use = mp.cpu_count() - 4 # = 12
number_runs = cores_to_use * 4 # * 2
std_values = np.linspace(0.06, 0.20, 8, endpoint=True)
number_sims = number_runs * len(std_values)

def run_sim (run_number):
	run_dir = out_dir/'run_{0:02d}'.format(run_number)
	Path.mkdir(run_dir, exist_ok = True)
	os.chdir(str(run_dir))
	# Generate an initial state.
	if (run_dir/'initial_state.fe').exists():
		pass
	else:
		make_system( Nx = 16, Ny = 8,
					 suevfile = Path('./initial_state.fe'),
					 shape_index = 3.6,
					 perimeter_modulus = 1.0,
					 length_threshold = 5.e-2,
					 energy_threshold = 1.e-8,
					 force_coefficent = 0.0 )
	# Run through the parameter values.
	for std_param in std_values:
		sim_dir = run_dir/('std_{0:1.2f}'.format(std_param))
		if (sim_dir).exists():
			pass
		else:
			Path.mkdir(run_dir/"output", exist_ok = True)
			# Make a simulation script.
			with open(run_dir/'sim.fe','w') as sim_script:
				sim_script.write('ing_std := {0:1.2f};\n'.format(std_param))
				sim_script.write('giver;\n')
				sim_script.write('dump "./output/final_state')
				sim_script.write('_{0:1.2f}.fe"\n'.format(std_param))
				sim_script.write('quit 1\n')
			# Run simulation.
			with open(os.devnull, 'w') as nowhere:
				sim = sp.Popen(['evolver','-fsim.fe','-x','initial_state.fe'],
								stdout=nowhere)
				sim.wait()
			(run_dir/'output').rename(sim_dir)
			(run_dir/'sim.fe').unlink()

################################################################################

if __name__ == '__main__':
	code_timer = timer()
	code_timer.start()
	Path.mkdir(out_dir, exist_ok = True)
	with mp.Pool(processes = cores_to_use) as pool:
		pool.map(run_sim, range(1,number_runs+1))
	code_timer.stop()

################################################################################
# EOF
