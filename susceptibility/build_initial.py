#!/usr/bin/env /usr/bin/python3
import numpy as np
from build_voronoi import build_voronoi

################################################################################
#===============================================================================
# build_initial
#===============================================================================
################################################################################

def build_initial (Nx = 16, Ny = 8):
	vertices, edges, faces, boundary_edges = build_voronoi(Nx, Ny)
	boundary_vertices = np.unique((edges[boundary_edges]-1).flatten())
	# need to figure out which edges are on which boundary.
	lower_boundary = np.zeros_like(boundary_edges, dtype = bool)
	upper_boundary = np.zeros_like(boundary_edges, dtype = bool)
	left_boundary = np.zeros_like(boundary_edges, dtype = bool)
	right_boundary = np.zeros_like(boundary_edges, dtype = bool)
	for edge_index, edge in enumerate(edges):
		if not boundary_edges[edge_index]:
			continue
		delta_x, delta_y = np.abs(vertices[edge[0]-1] - vertices[edge[1]-1])
		if delta_x > delta_y: # horizontal
			if vertices[edge[0]-1,1] > Ny/2:
				upper_boundary[edge_index] = True
			else:
				lower_boundary[edge_index] = True
		else: # vertical
			if vertices[edge[0]-1,0] > Nx/2:
				right_boundary[edge_index] = True
			else:
				left_boundary[edge_index] = True
	############################################################################
	# need to build a new face out of the top boundary and some new edges
	# first order the top edge left to right
	new_face = np.nonzero(upper_boundary)[0] + 1
	first_x = np.zeros_like(new_face, dtype = float)
	for face_index, edge_index in enumerate(new_face):
		if vertices[edges[edge_index-1,0]-1, 0] > \
		   vertices[edges[edge_index-1,1]-1, 0]:
			new_face[face_index] *= -1
			first_x[face_index] = vertices[edges[edge_index-1,1]-1, 0]
		else:
			first_x[face_index] = vertices[edges[edge_index-1,0]-1, 0]
	new_face = new_face[np.argsort(first_x)]
	left_corner = edges[np.abs(new_face[0])-1,0 if new_face[0]>0 else 1]
	right_corner = edges[np.abs(new_face[-1])-1,1 if new_face[-1]>0 else 0]
	vertices = np.append(vertices, [[0, Nx], [Nx, Nx]], axis = 0)
	edges = np.append(edges, [[left_corner, len(vertices)-1],
							  [len(vertices)-1, len(vertices)],
							  [right_corner, len(vertices)]],
						axis = 0)
	new_face = np.append(new_face, [len(edges), -len(edges)+1, -len(edges)+2])
	faces = np.append(faces, [None])
	faces[-1] = new_face.tolist()
	faces = np.roll(faces, 1, axis=0)
	# fix the boundaries
	left_boundary = np.append(left_boundary, [True, False, False])
	right_boundary = np.append(right_boundary, [False, False, True])
	lower_boundary = np.append(lower_boundary, [False, False, False])
	upper_boundary = np.zeros_like(right_boundary, dtype = bool)
	upper_boundary[-2] = True
	############################################################################
	# need three extra faces for edge effects in model #
	####################################################
	# left extra face
	left_face = np.nonzero(left_boundary)[0] + 1
	first_y = np.zeros_like(left_face, dtype = float)
	for face_index, edge_index in enumerate(left_face):
		if vertices[edges[edge_index-1,0]-1, 1] > \
		   vertices[edges[edge_index-1,1]-1, 1]:
			left_face[face_index] *= -1
			first_y[face_index] = vertices[edges[edge_index-1,1]-1, 1]
		else:
			first_y[face_index] = vertices[edges[edge_index-1,0]-1, 1]
	left_face = left_face[np.argsort(first_y)]
	lower_left_corner = edges[np.abs(left_face[0])-1,
								0 if left_face[0]>0 else 1]
	upper_left_corner = edges[np.abs(left_face[-1])-1,
								1 if left_face[-1]>0 else 0]
	# right extra face
	right_face = np.nonzero(right_boundary)[0] + 1
	first_y = np.zeros_like(right_face, dtype = float)
	for face_index, edge_index in enumerate(right_face):
		if vertices[edges[edge_index-1,0]-1, 1] > \
		   vertices[edges[edge_index-1,1]-1, 1]:
			right_face[face_index] *= -1
			first_y[face_index] = vertices[edges[edge_index-1,1]-1, 1]
		else:
			first_y[face_index] = vertices[edges[edge_index-1,0]-1, 1]
	right_face = right_face[np.argsort(first_y)]
	lower_right_corner = edges[np.abs(right_face[0])-1,
								0 if right_face[0]>0 else 1]
	upper_right_corner = edges[np.abs(right_face[-1])-1,
								1 if right_face[-1]>0 else 0]
	# lower extra face
	lower_face = np.nonzero(lower_boundary)[0] + 1
	first_x = np.zeros_like(lower_face, dtype = float)
	for face_index, edge_index in enumerate(lower_face):
		if vertices[edges[edge_index-1,0]-1, 0] > \
		   vertices[edges[edge_index-1,1]-1, 0]:
			lower_face[face_index] *= -1
			first_x[face_index] = vertices[edges[edge_index-1,1]-1, 0]
		else:
			first_x[face_index] = vertices[edges[edge_index-1,0]-1, 0]
	lower_face = lower_face[np.argsort(first_x)]
	# add new elements
	vertices = np.append(vertices, [[-1, -1], [Nx+1, -1]], axis = 0)
	edges = np.append(edges, [[upper_left_corner, len(vertices)-1],
							  [lower_left_corner, len(vertices)-1],
							  [len(vertices)-1, len(vertices)],
							  [lower_right_corner, len(vertices)],
							  [upper_right_corner, len(vertices)]],
						axis = 0)
	left_face = np.append(left_face,
							[len(edges)-4, -len(edges)+3])
	faces = np.append(faces, [None])
	faces[-1] = left_face.tolist()
	lower_face = np.append(-1*lower_face[::-1],
							[len(edges)-3, len(edges)-2, -len(edges)+1])
	faces = np.append(faces, [None])
	faces[-1] = lower_face.tolist()
	right_face = np.append(-1*right_face[::-1],
							[len(edges)-1, -len(edges)])
	faces = np.append(faces, [None])
	faces[-1] = right_face.tolist()
	faces = np.roll(faces, 3, axis=0)
	# add some extra entries in edge boundary arrays
	left_boundary = np.append(left_boundary,
								[False, False, False, False, False])
	right_boundary = np.append(right_boundary,
								[False, False, False, False, False])
	lower_boundary = np.append(lower_boundary,
								[False, False, False, False, False])
	upper_boundary = np.append(upper_boundary,
								[False, False, False, False, False])
	############################################################################
	left_vertices = np.zeros(len(vertices), dtype = bool)
	left_vertices[np.unique((edges[left_boundary]-1).flatten())] = True
	lower_vertices = np.zeros(len(vertices), dtype = bool)
	lower_vertices[np.unique((edges[lower_boundary]-1).flatten())] = True
	right_vertices = np.zeros(len(vertices), dtype = bool)
	right_vertices[np.unique((edges[right_boundary]-1).flatten())] = True
	upper_vertices = np.zeros(len(vertices), dtype = bool)
	upper_vertices[np.unique((edges[upper_boundary]-1).flatten())] = True
	boundaries = np.vstack([left_vertices, lower_vertices,
							right_vertices, upper_vertices]).T
	return vertices, edges, faces, boundaries

################################################################################

if __name__ == '__main__':
	pass

################################################################################
# EOF
