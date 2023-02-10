#!/usr/bin/env /usr/bin/python3
import numpy as np
import argparse
from pathlib import Path
from numpy.random import Generator, PCG64
from build_initial import *

################################################################################
#===============================================================================
# make_system
#===============================================================================
################################################################################

def make_system (Nx = 16, Ny = 8,
					suevfile = Path('./initial_state.fe'),
					shape_index = 3.6,
					perimeter_modulus = 1.0,
					length_threshold = 5.e-2,
					energy_threshold = 1.e-8,
					force_coefficent = 1.e-3,
					length_tolerance = 1.e-6 ):
	vertices, edges, faces, boundaries = build_initial(Nx, Ny)
	# Write surface evolver script
	with open(suevfile, 'w+') as outfile:
		outfile.write('// Bounded Voronoi Tesselation\n')
		outfile.write('\nSTRING')
		outfile.write('\nSURFACE_DIMENSION 1')
		outfile.write('\nSPACE_DIMENSION   2')
		outfile.write('\nDEFINE facet ATTRIBUTE type integer\n')
		outfile.write('\nPARAMETER Nx = {0:d}'.format(Nx))
		outfile.write('\nPARAMETER Ny = {0:d}'.format(Ny))
		outfile.write('\nPARAMETER length_threshold = {0:1.9f}'.format(
															length_threshold))
		outfile.write('\nPARAMETER energy_threshold = {0:1.9f}\n'.format(
															energy_threshold))
		outfile.write('\nPARAMETER force_coefficent = {0:1.9f}\n'.format(
															force_coefficent))
		outfile.write('\nPARAMETER length_tolerance = {0:1.9f}\n'.format(
															length_tolerance))
		outfile.write('\nCONSTRAINT 1')
		outfile.write('\n\tformula: x = 0\n')
		outfile.write('\nCONSTRAINT 2')
		outfile.write('\n\tformula: y = 0\n')
		outfile.write('\nCONSTRAINT 3')
		outfile.write('\n\tformula: x = {0:d}\n'.format(Nx))
		outfile.write('\nCONSTRAINT 4')
		outfile.write('\n\tformula: y = {0:d}\n'.format(Nx))
		outfile.write('\nQUANTITY fixed_edge INFO_ONLY METHOD edge_length\n')
		outfile.write('\nQUANTITY downward_force ENERGY METHOD')
		outfile.write(' vertex_scalar_integral\n')
		outfile.write('\tscalar_integrand: force_coefficent * y\n')
		for face_index, face in enumerate(faces):
			outfile.write('\nMETHOD_INSTANCE cell_{0:d}'.format(face_index+1))
			outfile.write('_peri METHOD edge_length\n')
			outfile.write('METHOD_INSTANCE cell_{0:d}'.format(face_index+1))
			outfile.write('_area_pos METHOD edge_area\n')
			outfile.write('METHOD_INSTANCE cell_{0:d}'.format(face_index+1))
			outfile.write('_area_neg METHOD edge_area\n')
			outfile.write('PARAMETER cell_{0:d}_p0 = {1:1.9f}\n'.format(
											face_index+1, shape_index))
			outfile.write('PARAMETER cell_{0:d}_r = {1:1.9f}\n'.format(
											face_index+1, perimeter_modulus))
			outfile.write('QUANTITY cell_{0:d}'.format(face_index+1))
			outfile.write('_energy ENERGY FUNCTION\n')
			if face_index in [0,1,2,3]:
				outfile.write('\t0\n\n')
			else:
				outfile.write('\t(cell_{0:d}'.format(face_index+1))
				outfile.write('_area_pos.value - ')
				outfile.write('cell_{0:d}'.format(face_index+1))
				outfile.write('_area_neg.value - 1)^2 +\n')
				outfile.write('\t(cell_{0:d}_peri.value'.format(face_index+1))
				outfile.write(' - cell_{0:d}_p0)^2'.format(face_index+1))
				outfile.write('/cell_{0:d}_r\n\n'.format(face_index+1))
		outfile.write('\nvertices\n')
		for vertex_index, vertex in enumerate(vertices):
			outfile.write('{0:d}\t{1:1.10f}\t{2:1.10f}'.format(
														vertex_index+1,
														vertex[0],
														vertex[1]))
			if vertex_index in [len(vertices)-2, len(vertices)-1]:
				outfile.write('\tfixed')
			if boundaries[vertex_index,0]:
				outfile.write('\tconstraint 1')
			if boundaries[vertex_index,1]:
				outfile.write('\tconstraint 2')
			if boundaries[vertex_index,2]:
				outfile.write('\tconstraint 3')
			if boundaries[vertex_index,3]:
				outfile.write('\tconstraint 4')
			outfile.write('\n')
		outfile.write('\nedges\n')
		for edge_index, edge in enumerate(edges):
			outfile.write('{0:d}\t{1:d}\t{2:d}'.format(
										edge_index+1, edge[0], edge[1]))
			outfile.write('\ttension\t0')
			for face_index, face in enumerate(faces):
				for edge_check in face:
					if edge_check == edge_index+1:
						outfile.write('\tcell_{0:d}_peri'.format(face_index+1))
						outfile.write('\tcell_{0:d}'.format(face_index+1))
						outfile.write('_area_pos')
					elif -edge_check == edge_index+1:
						outfile.write('\tcell_{0:d}_peri'.format(face_index+1))
						outfile.write('\tcell_{0:d}'.format(face_index+1))
						outfile.write('_area_neg')
			outfile.write('\n')
		outfile.write('\nfaces\n')
		for face_index, face in enumerate(faces):
			outfile.write('{0:d}'.format(face_index+1))
			for index in face:
				outfile.write('\t{0:d}'.format(index))
			outfile.write('\n')
		outfile.write('\nbodies\n')
		for face_index, face in enumerate(faces):
			outfile.write('{0:d}\t{0:d}\n'.format(face_index+1))
		outfile.write('\nread\n')
		outfile.write('\nconj_grad on') # Much faster convergence!
		outfile.write('\nautorecalc on\n')
		rg = Generator(PCG64())
		outfile.write('\nrandom_seed := {0:d}\n'.format(
										rg.integers(0,1000)))
		# Procedures in seperate file.
		with open(Path(__file__).resolve().parent / \
					'procedures.fe','r') as commandfile:
			for line in commandfile.read():
				outfile.write(line)
		# Graphics and command sequences.
	#	outfile.write('\nshow\nq\n')
	#	outfile.write('\nsetup\nrelax\nreset\ngiver\n')
	#	outfile.write('\n')

################################################################################

if __name__ == '__main__':
	# Use argparse to get arguements from commandline call
	parser = argparse.ArgumentParser(
							description = 'Generate initial condition')
	# N = int(sys.argv[1])
	parser.add_argument('-nx', '--number_x',
						nargs = 1,
						default = [16],
						type = int,
						required = False,
						help = 'number of cells in x')
	parser.add_argument('-ny', '--number_y',
						nargs = 1,
						default = [8],
						type = int,
						required = False,
						help = 'number of cells in y')
	parser.add_argument('-s', '--suevfile',
						nargs = 1,
						default = ['./initial_state.fe'],
						type = str,
						required = False,
						help = 'file to put surface evolver script in')
	parser.add_argument('-p', '--p0_param',
						nargs = 1,
						default = [3.6],
						type = float,
						required = False,
						help = 'shape index parameter')
	parser.add_argument('-r', '--r_param',
						nargs = 1,
						default = [1.0],
						type = float,
						required = False,
						help = 'inverse perimeter modulus')
	args = parser.parse_args()
	suevfile = Path(args.suevfile[0])
	suevfile.parent.mkdir(exist_ok = True)
	make_system(Nx = args.number_x[0],
				Ny = args.number_y[0],
				suevfile = suevfile,
				shape_index = args.p0_param[0],
				perimeter_modulus = args.r_param[0])

################################################################################
# EOF
