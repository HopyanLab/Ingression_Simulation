#!/usr/bin/env /usr/bin/python3
import numpy as np
from scipy.spatial import Voronoi
from numpy.random import Generator, PCG64, default_rng
from functools import reduce
from operator import concat

################################################################################
#===============================================================================
# build_voronoi
#===============================================================================
################################################################################

def build_voronoi (Nx = 16, Ny = 12):
	x = np.arange(0,Nx)+0.5
	y = np.arange(0,Ny)+0.5
	xx, yy = np.meshgrid(x, y)
	points = np.vstack([xx.flatten(), yy.flatten()]).T
	# for testing can use fixed sequence
	# rg = np.random.default_rng(42)
	rg = Generator(PCG64()) # PCG64 is the default bit generator.
	gaussian_noise = np.reshape(rg.normal(0,0.3,2*Nx*Ny), (Nx*Ny,2))
	points = points + gaussian_noise
	# Make sure all points are in the region
	for point in points:
		if point[0] < 0:
			point[0] = -point[0]
		if point[0] > Nx:
			point[0] = 2*Nx - point[0]
		if point[1] < 0:
			point[1] = -point[1]
		if point[1] > Ny:
			point[1] = 2*Ny - point[1]
	# Reflect points across boundary to make edges.
	extra_points = np.zeros((4*Nx*Ny, 2))
	# Lower
	extra_points[:Nx*Ny,0] = points[:,0]
	extra_points[:Nx*Ny,1] = -points[:,1]
	# Upper
	extra_points[Nx*Ny:2*Nx*Ny,0] = points[:,0]
	extra_points[Nx*Ny:2*Nx*Ny,1] = 2*Ny-points[:,1]
	# Left
	extra_points[2*Nx*Ny:3*Nx*Ny,0] = -points[:,0]
	extra_points[2*Nx*Ny:3*Nx*Ny,1] = points[:,1]
	# Right
	extra_points[3*Nx*Ny:,0] = 2*Nx-points[:,0]
	extra_points[3*Nx*Ny:,1] = points[:,1]
	# Put together
	input_points = np.concatenate((points,extra_points),axis=0)
	# Make Voronoi diagram
	vor = Voronoi(input_points)
	# We only want the regions inside the boundary
	good_region_indices = vor.point_region[:Nx*Ny]
	regions = np.array(vor.regions, dtype=object)[good_region_indices]
	# Easy to make a backward map. We need to reverse it.
	used_vertices = np.unique(reduce(concat, regions))
	vertices = vor.vertices[used_vertices]
	vertex_map = np.ones(len(vor.vertices), dtype=int) * -1
	vertex_map[used_vertices] = np.arange(len(used_vertices), dtype=int)
	# Use this map to renumber regions.
	remapped_regions = np.empty(len(regions), dtype=object)
	for index,region in enumerate(regions):
		remapped_regions[index] = vertex_map[region]
	regions = remapped_regions
	# make sure they are all counterclockwise
	counter = 0
	for region_index, region in enumerate(regions):
		if is_clockwise(vertices, region):
			regions[region_index] = region[::-1]
			counter += 1
	# Build edge and face lists in Surface Evolver notation.
	edges = np.empty((0,2), dtype = int)
	boundary_edges = np.empty(0, dtype = bool)
	faces = np.empty(0, dtype = object)
	for region in regions:
		face = []
		for i in range(len(region)):
			edge = np.array([region[i-1]+1, region[i]+1])
			orientation = 1
			if region[i] < region[i-1]:
				edge = edge[::-1]
				orientation = -1
			edge_search = np.where((edges[:,0] == edge[0]) & \
								   (edges[:,1] == edge[1]))[0]
			if len(edge_search) == 0:
				edge_index = len(edges)
				edges = np.append(edges, edge[np.newaxis,:], axis=0)
				boundary_edges = np.append(boundary_edges, True)
			else:
				edge_index = edge_search[0]
				boundary_edges[edge_index] = not(boundary_edges[edge_index])
			face.append(orientation * (edge_index + 1))
		faces = np.append(faces, [None])
		faces[-1] = face
#	with open('./faces.txt', 'w') as outfile:
#		for face in faces:
#			for edge in face:
#				outfile.write(str(edge))
#				outfile.write('\t')
#			outfile.write('\n')
	return vertices, edges, faces, boundary_edges

################################################################################

def is_clockwise (vertices, region):
	points = vertices[region]
	edge_sum = 0
	for index, point in enumerate(points):
		edge_sum += (point[0] - points[index-1,0]) * \
					(point[1] + points[index-1,1])
	if edge_sum > 0:
		return True
	else:
		return False

################################################################################

if __name__ == '__main__':
	pass

################################################################################
# EOF
