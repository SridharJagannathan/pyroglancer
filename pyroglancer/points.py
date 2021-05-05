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

"""Module contains functions to handle point data."""

import json
import neuroglancer
import os
import struct


def commit_info(pointinfo, path, pointlayername):
    """Commit the info file created for the points based precomputed format.

    Parameters
    ----------
    pointinfo : dict
        info in json format for the points
    path: str
        local path of the precomputed hosted layer.
    pointlayername : str
      name for the points layer
    """
    pointfilepath = path + '/precomputed/' + pointlayername
    if not os.path.exists(pointfilepath):
        os.makedirs(pointfilepath)
        print('creating:', pointfilepath)
    infofile = os.path.join(pointfilepath, 'info')
    with open(infofile, 'w') as f:
        json.dump(pointinfo, f)


def create_pointinfo(dimensions, path, layer_name):
    """Create info file for the points based precomputed format.

    Parameters
    ----------
    path: str
        local path of the precomputed hosted layer.
    layer_name : str
      name for the points layer
    dimensions:  neuroglancer.CoordinateSpace
        object of neuroglancer coordinate space class.

    Returns
    -------
    path: str
        local path of the precomputed hosted layer.
    """
    pointinfo = {
        '@type': 'neuroglancer_annotations_v1',
        "annotation_type": "POINT",
        "by_id": {
            "key": "by_id"
        },
        "dimensions": {
            "x": [dimensions['x'].scale, dimensions['x'].unit],
            "y": [dimensions['y'].scale, dimensions['y'].unit],
            "z": [dimensions['z'].scale, dimensions['z'].unit]
        },
        "lower_bound": [0, 0, 0],
        "properties": [],
        "relationships": [],
        "spatial": [
            {
                "chunk_size": [137216, 264192, 4400],
                "grid_shape": [1, 1, 1],
                "key": "spatial0",
                "limit": 10000
            }
        ],
        "upper_bound": [137216, 264192, 4400]
    }
    commit_info(pointinfo, path, pointlayername=layer_name)

    return path


def put_pointfile(path, layer_name, points, pointsscale, pointname):
    """Put pointfile in the local dataserver.

    Parameters
    ----------
    path: str
        local path of the precomputed hosted layer.
    layer_name : str
      name for the points layer
    points :  dataframe
        should contain 'x', 'y', 'z' columns
    pointsscale : int | float
        scaling from voxel to native space in 'x', 'y', 'z'
    pointsname :  str
        name for the points (not yet implemented)

    """
    pointsfilepath = path + '/precomputed/' + layer_name + '/spatial0'
    if not os.path.exists(pointsfilepath):
        os.makedirs(pointsfilepath)

    pointsfile = os.path.join(pointsfilepath, '0_0_0')
    print(pointsfile)
    pointlocs = points[['x', 'y', 'z']].values/1000

    # implementation based on logic suggested by https://github.com/google/neuroglancer/issues/227
    with open(pointsfile, 'wb') as outputbytefile:
        total_points = len(pointlocs)
        buffer = struct.pack('<Q', total_points)
        for (x, y, z) in pointlocs:
            x = x*pointsscale[0]
            y = y*pointsscale[1]
            z = z*pointsscale[2]
            annotpoint = struct.pack('<3f', x, y, z)
            buffer += annotpoint
        pointid_buffer = struct.pack('<%sQ' % len(pointlocs), *range(len(pointlocs)))
        buffer += pointid_buffer
        outputbytefile.write(buffer)

    idfilepath = path + '/precomputed/' + layer_name + '/by_id'
    if not os.path.exists(idfilepath):
        os.makedirs(idfilepath)

    for idfileidx in range(len(pointlocs)):
        filename = str(idfileidx)
        idfile = os.path.join(idfilepath, filename)
        print(idfile)
        with open(idfile, 'wb') as outputbytefile:
            x = pointlocs[idfileidx][0]*pointsscale[0]
            y = pointlocs[idfileidx][1]*pointsscale[1]
            z = pointlocs[idfileidx][2]*pointsscale[2]
            annotpoint = struct.pack('<3f', x, y, z)
            outputbytefile.write(annotpoint)


def upload_points(points_df, path, layer_name, layer_scale):
    """Upload points from a dataframe.

    Parameters
    ----------
    points_df :  dataframe
        should contain 'x', 'y', 'z' columns
    path: str
        local path of the precomputed hosted layer.
    layer_name : str
      name for the points layer
    layer_scale : int | float
        scaling from voxel to native space in 'x', 'y', 'z'

    """
    pointname = points_df['description']
    points = points_df[['x', 'y', 'z']]
    pointsscale = layer_scale
    put_pointfile(path, layer_name, points, pointsscale, pointname)


def annotate_points(ngviewer, dimensions, pointscolor, points_df, layer_name, layer_scale):
    """Annotate points from a dataframe (defunct do not use..).

    Parameters
    ----------
    ngviewer : ng.viewer.Viewer
        object of Neuroglancer viewer class.
    dimensions:  neuroglancer.CoordinateSpace
        object of neuroglancer coordinate space class.
    points_df :  dataframe
        should contain 'x', 'y', 'z' columns
    layer_scale : int | float
        scaling from voxel to native space in 'x', 'y', 'z'
    """
    pointname = points_df['description']
    points_df.loc[:, ['x', 'y', 'z']] = points_df.loc[:, ['x', 'y', 'z']].values/1000

    with ngviewer.txn() as s:
        s.layers.append(
            name=layer_name,
            layer=neuroglancer.LocalAnnotationLayer(
                dimensions=dimensions,
                ignore_null_segment_filter=False,
                annotation_properties=[
                    neuroglancer.AnnotationPropertySpec(
                        id='color',
                        type='rgb',
                        default='blue',
                    )
                ],
                shader='''
                        void main() {
                          setColor(prop_color());
                          setPointMarkerSize(5.0);
                        }
                        ''',
            ))
        for index, indivpoints in points_df.iterrows():
            s.layers[layer_name].annotations.append(
                neuroglancer.PointAnnotation(
                    id=str(index),
                    point=[indivpoints.x*layer_scale[0], indivpoints.y*layer_scale[1],
                           indivpoints.z*layer_scale[2]],
                    props=[pointscolor],
                    description=pointname[index]
                )
            )

    status = True
    return status
