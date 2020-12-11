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

""" Module contains functions to handle point data.
"""

import pymaid
import navis
import neuroglancer
import json
import os
import struct


def commit_info(pointinfo, path, pointlayername):
    pointfilepath = path + '/precomputed/' + pointlayername
    if not os.path.exists(pointfilepath):
        os.makedirs(pointfilepath)
        print('creating:', pointfilepath)
    infofile = os.path.join(pointfilepath, 'info')
    with open(infofile, 'w') as f:
        json.dump(pointinfo, f)


def create_pointinfo(dimensions, path, layer_name):
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
                "chunk_size": [137216,  264192, 4400],
                "grid_shape": [1, 1, 1],
                "key": "spatial0",
                "limit": 1000
            }
        ],
        "upper_bound": [137216,  264192, 4400]
    }
    commit_info(pointinfo, path, pointlayername=layer_name)

    return path


def put_pointfile(path, layer_name, points, pointname):

    pointfilepath = path + '/precomputed/' + layer_name + '/'
    if not os.path.exists(pointfilepath):
        os.makedirs(pointfilepath)
        #print('creating:', pointfilepath)
    pointfile = os.path.join(pointfilepath, str(layer_name))
    #print('making:', pointfile)
    pointlocs = points[['x', 'y', 'z']]

    # implementation based on logic suggested by https://github.com/google/neuroglancer/issues/227
    with open(pointfile, 'wb') as outputbytefile:
        total_points = len(pointlocs)  # coordinates is a list of tuples (x,y,z)
        buffer = struct.pack('<Q', total_points)
        print(total_points)
        for index, row in pointlocs.iterrows():
            x = row['x']
            y = row['y']
            z = row['z']
            print(x)
            print(y)
            print(z)
            annotpoint = struct.pack('<3f', x, y, z)
            buffer += annotpoint
        # write the ids of the individual points at the very end..
        pointid_buffer = struct.pack('<%sQ' % len(pointlocs), *range(len(pointlocs)))
        buffer += pointid_buffer
        outputbytefile.write(buffer)


def upload_points(points_df, path, layer_name):

    pointname = points_df['description']
    points = points_df[['x', 'y', 'z']]
    #print('Adding neuron: ', neuronelement.id)
    put_pointfile(path, layer_name, points, pointname)


def annotate_points(ngviewer, dimensions, points_df, layer_scale):
    """

    Annotate points from a dataframe.

    This function annotates points based on a dataframe

    Parameters
    ----------
    points_df :      dataframe containing 'x', 'y', 'z' columns
    layer_scale :    scaling from voxel to native space in 'x', 'y', 'z'
    dimensions :     dimensions and units of 'x', 'y', 'z'
    ngviewer:        Neuroglancer viewer


    """

    #pointname = points_df['description']
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
