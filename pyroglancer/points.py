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
    pointinfo :      info in json format for the points
    path:            path for the dataserver hosted locally
    pointlayername : name for the points layer
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
    path:            path for the dataserver hosted locally
    layer_name :     name for the points layer
    dimensions :     dimensions used by neuroglancer

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
    path:            path for the dataserver hosted locally
    layer_name :     name for the points layer
    points :         dataframe containing 'x', 'y', 'z' columns
    pointsscale :    scaling from voxel to native space in 'x', 'y', 'z'
    pointsname :     name for the points (not yet implemented)

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


def upload_points(points_df, path, layer_name, layer_scale):
    """Upload points from a dataframe.

    Parameters
    ----------
    points_df :      dataframe containing 'x', 'y', 'z' columns
    path:            path for the dataserver hosted locally
    layer_name :     name for the points layer
    layer_scale :    scaling from voxel to native space in 'x', 'y', 'z'

    """
    pointname = points_df['description']
    points = points_df[['x', 'y', 'z']]
    pointsscale = layer_scale
    put_pointfile(path, layer_name, points, pointsscale, pointname)


def _annotate_points(ngviewer, dimensions, points_df, layer_scale):
    """Annotate points from a dataframe (defunct do not use..).

    Parameters
    ----------
    ngviewer:        Neuroglancer viewer
    dimensions :     dimensions and units of 'x', 'y', 'z'
    points_df :      dataframe containing 'x', 'y', 'z' columns
    layer_scale :    scaling from voxel to native space in 'x', 'y', 'z'
    """
    pointlocs = points_df[['x', 'y', 'z']]

    with ngviewer.txn() as s:
        s.layers.append(
            name="points",
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
        for index, indivpoints in pointlocs.iterrows():
            s.layers['points'].annotations.append(
                neuroglancer.PointAnnotation(
                    id=str(index),
                    point=[indivpoints.x*layer_scale[0], indivpoints.y*layer_scale[1],
                           indivpoints.z*layer_scale[2]],
                    props=['#0000ff'],
                )
            )

    status = True
    return status
