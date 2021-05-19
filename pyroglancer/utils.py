#    This script is part of pyroglancer (https://github.com/SridharJagannathan/pyroglancer).
#    Copyright (C) 2020 Sridhar Jagannathan
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

"""Module contains utility functions."""
from .loadconfig import getconfigdata
import navis
import numpy as np
import open3d as o3d
from scipy import ndimage
from skimage import measure
import trimesh as tm
import webcolors


def get_hexcolor(layer_kws):
    """Convert text based color to hex value."""
    # This function converts css color text to hex based.
    if 'color' in layer_kws:
        layer_color = layer_kws['color']
    else:
        layer_color = 'yellow'
    rawcolorlist = layer_color

    if not isinstance(rawcolorlist, list):
        rawcolorlist = (rawcolorlist,)

    hexcolorlist = []
    for hexcolor in rawcolorlist:
        if not hexcolor.startswith("#"):
            hexcolor = webcolors.name_to_hex(hexcolor)
        hexcolorlist.append(hexcolor)
    return hexcolorlist


def get_alphavalue(layer_kws):
    """Get alpha values from the interface APIs.
    """
    # This function gets alpha/transparency values.
    layer_alpha = layer_kws.get("alpha", 1.0)
    return layer_alpha


def get_annotationstatetype(layer_kws):
    """Get alpha values from the interface APIs."""
    # This function gets alpha/transparency values.
    layer_statetype = layer_kws.get("annotationstatetype", 'precomputed')
    return layer_statetype


def _get_configvox2physical(layer_kws):
    scale = layer_kws.get("scale", None)
    if scale is None:
        layer_kws['configfileloc'] = layer_kws.get('configfileloc', None)
        configdata = getconfigdata(layer_kws['configfileloc'])
        ngspaceconfig = next(filter(lambda ngspace: ngspace['ngspace'] == layer_kws['ngspace'], configdata))
        scale = [ngspaceconfig['voxelsize'].get(key) for key in ['x', 'y', 'z']]
    return scale


def get_scalevalue(layer_kws):
    """Get scale values from the interface APIs."""
    # This function gets scale values for annotations.
    space = layer_kws.get("space", "voxel")
    if space == "voxel":
        scale = _get_configvox2physical(layer_kws)
    else:
        scale = [1, 1, 1]
    print('using ', space, 'space', 'with scale: ', scale)

    return scale


def obj2pointcloud(objurl=None):
    """Convert object url to point cloud data in open3d format.

    Parameters
    ----------
    objurl : str
        url containing the obj file.

    Returns
    -------
    pcd : o3d.geometry.PointCloud
        point cloud object of open3d PointCloud class.

    """

    tm_mesh = tm.load_remote(objurl)
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(tm_mesh.vertices)

    return pcd


def pointcloud2meshes(pcd_data, algorithm='rollingball', **kwargs):
    """Convert point cloud files to volumetric meshes.

    Parameters
    ----------
    pcd_data : o3d.geometry.PointCloud or str
        pointcloud object or file location in polygon file format.
    algorithm : str
        algorithm of either 'rollingball' or 'marchingcubes' to convert points to meshes.

    Returns
    -------
    ret_mesh : navis.Volume
        mesh object of navis volume class.

    """
    # read point cloud data and compute normals
    if isinstance(pcd_data, o3d.geometry.PointCloud):
        pcd = pcd_data
    else:
        pcd = o3d.io.read_point_cloud(pcd_data)
    pcd.estimate_normals()

    if algorithm == 'rollingball':

        # estimate radius for rolling ball
        distances = pcd.compute_nearest_neighbor_distance()
        avg_dist = np.mean(distances)
        radius_scale = kwargs.get('radius_scale', 3)
        radius = radius_scale * avg_dist

        # compute mesh
        mesh = o3d.geometry.TriangleMesh.create_from_point_cloud_ball_pivoting(pcd, o3d.utility.DoubleVector(
                            [radius, radius * 2]))

        # create the triangular mesh with the vertices and faces from open3d
        tri_mesh = tm.Trimesh(np.asarray(mesh.vertices), np.asarray(mesh.triangles),
                              vertex_normals=np.asarray(mesh.vertex_normals))

    elif algorithm == 'marchingcubes':
        point_vals = np.asarray(pcd.points)
        x_coords = point_vals[:, 2]
        y_coords = point_vals[:, 1]
        z_coords = point_vals[:, 0]

        # input: z_coords, y_coords, x_coords
        zint, yint, xint = [np.floor(coords).astype(int) for coords in [z_coords, y_coords, x_coords]]
        shape = tuple([np.max(intcoords) + 1 for intcoords in [zint, yint, xint]])
        mat = np.zeros(shape)
        mat[zint, yint, xint] += 1

        # Remove binary holes
        mat = ndimage.binary_fill_holes(mat)

        # We need one round of erodes
        mat = ndimage.binary_erosion(mat)

        step_size = kwargs.get('step_size', 1)

        verts, faces, normals, values = measure.marching_cubes_lewiner(mat.astype(float),
                                                                       level=0,
                                                                       allow_degenerate=False, step_size=step_size)

        # create the triangular mesh with the vertices and faces from open3d
        tri_mesh = tm.Trimesh(vertices=verts, faces=faces, normals=normals)

    if tm.convex.is_convex(tri_mesh):
        print('The mesh is convex')
    else:
        print('The mesh is not convex')

    ret_mesh = navis.Volume(tri_mesh)

    return ret_mesh
