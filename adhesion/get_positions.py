#!/usr/bin/env python3
import numpy as np

################################################################################
#===============================================================================
# get_positions
#===============================================================================
################################################################################

def get_positions (vertices, edges, faces):
	positions = np.zeros((len(faces),2), dtype = float)
	for face_index, face in enumerate(faces):
		face_vertices = np.zeros((len(face),2), dtype = float)
		face_vertices = vertices[np.unique(edges[np.abs(np.array(face))-1]-1)]
		positions[face_index] = np.mean(face_vertices, axis=0)
	return positions

################################################################################

if __name__ == '__main__':
	pass

################################################################################
# EOF
