#    This script is part of pyroglancer (https://github.com/SridharJagannathan/pyroglancer).
#    This code was adapted using the solutions provided in the discussion at
#    https://github.com/google/neuroglancer/issues/272
#    Copyright (C) 2021 Sridhar Jagannathan
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

"""Module contains functions to generate multi-resolution meshes."""

import numpy as np
import trimesh
import functools


class Quantize():
    # class for quanitising the location of the octree nodes that will be computed..
    def __init__(self, fragment_origin, fragment_shape, input_origin, quantization_bits):
        self.upper_bound = np.iinfo(np.uint32).max >> (np.dtype(np.uint32).itemsize*8 - quantization_bits)
        self.scale = self.upper_bound / fragment_shape
        self.offset = input_origin - fragment_origin + 0.5/self.scale

    def __call__(self, v_pos):
        output = np.minimum(self.upper_bound, np.maximum(0, self.scale*(v_pos + self.offset))).astype(np.uint32)
        return output


def cmp_zorder(lhs, rhs) -> bool:
    def less_msb(x: int, y: int) -> bool:
        return x < y and x < (x ^ y)

    # Assume lhs and rhs array-like objects of indices.
    assert len(lhs) == len(rhs)
    # Will contain the most significant dimension.
    msd = 2
    # Loop over the other dimensions.
    for dim in [1, 0]:
        # Check if the current dimension is more significant
        # by comparing the most significant bits.
        if less_msb(lhs[msd] ^ rhs[msd], lhs[dim] ^ rhs[dim]):
            msd = dim
    return lhs[msd] - rhs[msd]


def decompose_meshes(verts, faces, nodes_per_dim, bits):
    # Scale our coordinates.
    scale = nodes_per_dim/(verts.max(axis=0) - verts.min(axis=0))
    verts_scaled = scale*(verts - verts.min(axis=0))

    # Define plane normals and create a trimesh object.
    nyz, nxz, nxy = np.eye(3)
    mesh = trimesh.Trimesh(vertices=verts_scaled, faces=faces)

    # create submeshes by slicing the orignal mesh to produce smaller chunks,
    # by slicing them from x,y,z dimensions..
    submeshes = []
    nodes = []
    for x in range(0, nodes_per_dim):
        mesh_x = trimesh.intersections.slice_mesh_plane(mesh, plane_normal=nyz, plane_origin=nyz*x)
        mesh_x = trimesh.intersections.slice_mesh_plane(mesh_x, plane_normal=-nyz, plane_origin=nyz*(x+1))
        for y in range(0, nodes_per_dim):
            mesh_y = trimesh.intersections.slice_mesh_plane(mesh_x, plane_normal=nxz, plane_origin=nxz*y)
            mesh_y = trimesh.intersections.slice_mesh_plane(mesh_y, plane_normal=-nxz, plane_origin=nxz*(y+1))
            for z in range(0, nodes_per_dim):
                mesh_z = trimesh.intersections.slice_mesh_plane(mesh_y, plane_normal=nxy, plane_origin=nxy*z)
                mesh_z = trimesh.intersections.slice_mesh_plane(mesh_z, plane_normal=-nxy, plane_origin=nxy*(z+1))

                # Initialize Quantizer.
                quantize = Quantize(
                    fragment_origin=np.array([x, y, z]),
                    fragment_shape=np.array([1, 1, 1]),
                    input_origin=np.array([0, 0, 0]),
                    quantization_bits=bits
                )

                if len(mesh_z.vertices) > 0:
                    mesh_z.vertices = quantize(mesh_z.vertices)

                    submeshes.append(mesh_z)
                    nodes.append([x, y, z])

    # Sort in Z-curve order
    submeshes, nodes = zip(*sorted(zip(submeshes, nodes),
                                   key=functools.cmp_to_key(lambda x, y: cmp_zorder(x[1], y[1]))))

    return nodes, submeshes
