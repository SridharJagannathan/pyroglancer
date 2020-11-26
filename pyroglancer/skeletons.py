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

""" Module contains functions to handle skeleton data.
"""

import numpy as np
import os
from cloudvolume import Skeleton, CloudVolume
import pymaid
import navis
import json


def _generate_skeleton(x, min_radius=0):
    """Generate skeleton (of cloudvolume class) for given neuron.



    Parameters
    ----------
    x :             CatmaidNeuron | TreeNeuron

    Returns
    -------
    skeleton :      Cloud volume skeleton
    """

    # flatten the list of the segments (sub-trees)..
    nodes_ordered = [n for seg in x.segments for n in seg[::-1]]
    # arrange the nodes in the order of segments..
    this_tn = x.nodes.set_index('node_id').loc[nodes_ordered]
    # remove the first occurance of duplicated elements (as seglist stuff is repeated for different segments)..
    this_tn = this_tn[~this_tn.index.duplicated(keep='first')]
    this_tn['index'] = list(range(1, this_tn.shape[0] + 1))

    # treenode to index..
    tn2ix = this_tn['index'].to_dict()

    # set the rootnodes as 0..
    this_tn['parent_ix'] = this_tn.parent_id.map(lambda x: tn2ix.get(x, -1))

    # get the vertices now..
    vertices = np.array(this_tn[['x', 'y', 'z']].values.tolist(), dtype="float32")

    # get the edges now..
    edges = np.array(this_tn[['index', 'parent_ix']].values[1:] - 1, dtype="uint32")

    skeleton = Skeleton(segid=x.skeleton_id, vertices=vertices, edges=edges)

    # set the min_radius
    min_radius = 0
    if not isinstance(min_radius, type(None)):
        this_tn.loc[this_tn.radius < min_radius, 'radius'] = min_radius

    skeleton.radius = np.array(this_tn['radius'].values, dtype="float32")

    # Set Label column to 0 (undefined)
    this_tn['label'] = 0
    # Add end/branch labels
    this_tn.loc[this_tn.type == 'branch', 'label'] = 5
    this_tn.loc[this_tn.type == 'end', 'label'] = 6
    # Add soma label
    this_tn.loc[x.soma, 'label'] = 1

    skeleton.vertex_types = this_tn.label

    return skeleton


def to_ngskeletons(x):
    """Generate skeleton (of cloudvolume class) for given neuron(s).



    Parameters
    ----------
    x :             CatmaidNeuron | CatmaidNeuronList or TreeNeuron | NeuronList

    Returns
    -------
    skeldatasource :     List containing cloud volume skeletons
    skeldatasegidlist :  List containing the segids(skid)
    """

    if isinstance(x, pymaid.core.CatmaidNeuron):
        x = pymaid.core.CatmaidNeuronList(x)
    elif isinstance(x, navis.core.TreeNeuron):
        x = navis.core.NeuronList(x)

    skeldatasegidlist = []
    skeldatasource = []
    for neuronelement in x:
        skeldata = _generate_skeleton(neuronelement)
        skeldatasource.append(skeldata)
        skeldatasegidlist.append(skeldata.id)

    return skeldatasource, skeldatasegidlist


def uploadskeletons(skelsource, skelseglist, skelnamelist, path):
    """Upload skeleton (of cloudvolume class) to a local server.



    Parameters
    ----------
    skelsource :     List containing cloud volume skeletons
    skelseglist :    List containing the segids(skid)
    skelnamelist :   List containing the names of skeletons
    path :           path to the local data server

    Returns
    -------
    cv :     cloudvolume class object
    """

    info = {"@type": "neuroglancer_skeletons",
            "transform": skelsource[0].transform.flatten(),
            "vertex_attributes": [{"id": "radius", "data_type": "float32", "num_components": 1}],
            "scales": "um"}
    path = 'file://' + path + '/precomputed'
    cv = CloudVolume(path, info=info)

    # prepare for info file
    cv.skeleton.meta.info['@type'] = 'neuroglancer_skeletons'
    cv.skeleton.meta.info['transform'] = skelsource[0].transform.flatten()
    cv.skeleton.meta.info['vertex_attributes'] = [{'id': 'radius', 'data_type': 'float32', 'num_components': 1}]
    del cv.skeleton.meta.info['sharding']
    del cv.skeleton.meta.info['spatial_index']

    cv.skeleton.meta.info['segment_properties'] = 'seg_props'

    cv.skeleton.meta.commit_info()

    files = [os.path.join(cv.skeleton.meta.skeleton_path, str(skel.id)) for skel in skelsource]

    for fileidx in range(len(files)):
        fullfilepath = files[fileidx]
        fullfilepath = os.path.join(cv.basepath, os.path.basename(path), fullfilepath)
        uploadskel = Skeleton(vertices=skelsource[fileidx].vertices, edges=skelsource[fileidx].edges)
        print(fullfilepath)
        with open(fullfilepath, 'wb') as f:
            f.write(uploadskel.to_precomputed())

    segfilepath = os.path.join(cv.basepath, os.path.basename(path), cv.skeleton.meta.skeleton_path, 'seg_props')

    if not os.path.exists(segfilepath):
        os.makedirs(segfilepath)
        print('creating:', segfilepath)

    allsegproplist = []
    for segid in skelseglist:
        segpropdict = {}
        segpropdict['id'] = segid
        segpropdict['type'] = 'label'
        segpropdict['values'] = skelnamelist
        allsegproplist.append(segpropdict)

    seginfo = {"@type": "neuroglancer_segment_properties",
               "inline": {"ids": skelseglist,
                          "properties": allsegproplist}}

    segfile = os.path.join(segfilepath, 'info')
    with open(segfile, 'w') as segfile:
        json.dump(seginfo, segfile)

    return cv
