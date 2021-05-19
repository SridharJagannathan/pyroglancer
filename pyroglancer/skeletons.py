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

"""Module contains functions to handle skeleton data."""

import numpy as np
import os
from cloudvolume import Skeleton, CloudVolume
from cloudvolume.datasource.precomputed.sharding import ShardingSpecification
import pandas as pd
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

    skeleton = Skeleton(segid=x.id, vertices=vertices, edges=edges)

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
    if x.soma is not None:
        this_tn.loc[x.soma, 'label'] = 1

    skeleton.vertex_types = this_tn.label

    return skeleton


def to_ngskeletons(x):
    """Generate skeleton (of cloudvolume class) for given neuron(s).

    Parameters
    ----------
     x :             CatmaidNeuron | CatmaidNeuronList or TreeNeuron | NeuronList
       neuron or neuronlist of different formats

    Returns
    -------
    skeldatasource:  list
        contains cloud volume skeletons.
    skeldatasegidlist:  list
        contains the segids(skid).
    skelsegnamelist:  list
        contains the names of segments.
    """
    if isinstance(x, pymaid.core.CatmaidNeuron):
        x = pymaid.core.CatmaidNeuronList(x)
    elif isinstance(x, navis.core.TreeNeuron):
        x = navis.core.NeuronList(x)
    elif (isinstance(x, pymaid.core.CatmaidNeuronList) or isinstance(x, navis.core.NeuronList)):
        pass
    else:
        raise TypeError(f'Expected neuron or neuronlist, got "{type(x)}"')

    skeldatasegidlist = []
    skeldatasource = []
    skelsegnamelist = []
    for neuronelement in x:
        skeldata = _generate_skeleton(neuronelement)
        skeldatasource.append(skeldata)
        skeldatasegidlist.append(skeldata.id)
        skelsegnamelist.append(neuronelement.name)

    skeldatasegidlist = list(map(str, skeldatasegidlist))
    skelsegnamelist = list(map(str, skelsegnamelist))

    return skeldatasource, skeldatasegidlist, skelsegnamelist


def uploadskeletons(skelsource, skelseglist, skelnamelist, path, layer_name):
    """Upload skeleton (of cloudvolume class) to a local server.

    Parameters
    ----------
    skeldatasource:  list
        contains cloud volume skeletons.
    skeldatasegidlist:  list
        contains the segids(skid).
    skelsegnamelist:  list
        contains the names of segments.
    path: str
        local path of the precomputed hosted layer.
    layer_name: str
        layer name.

    Returns
    -------
    cv :     CloudVolume
        object of cloudvolume class
    """
    info = {"@type": "neuroglancer_skeletons",
            "transform": skelsource[0].transform.flatten(),
            "vertex_attributes": [{"id": "radius", "data_type": "float32", "num_components": 1}],
            "scales": "um"}
    path = 'file://' + path + '/precomputed/' + layer_name
    cv = CloudVolume(path, info=info)

    # prepare for info file
    cv.skeleton.meta.info['@type'] = 'neuroglancer_skeletons'
    cv.skeleton.meta.info['transform'] = skelsource[0].transform.flatten()
    cv.skeleton.meta.info['vertex_attributes'] = [
        {'id': 'radius', 'data_type': 'float32', 'num_components': 1}]
    del cv.skeleton.meta.info['sharding']
    del cv.skeleton.meta.info['spatial_index']

    cv.skeleton.meta.info['segment_properties'] = 'seg_props'

    cv.skeleton.meta.commit_info()

    files = [os.path.join(cv.skeleton.meta.skeleton_path, str(skel.id)) for skel in skelsource]

    for fileidx in range(len(files)):
        fullfilepath = files[fileidx]
        fullfilepath = os.path.join(cv.basepath, os.path.basename(path), fullfilepath)
        uploadskel = Skeleton(
            vertices=skelsource[fileidx].vertices, edges=skelsource[fileidx].edges)
        print(fullfilepath)
        with open(fullfilepath, 'wb') as f:
            f.write(uploadskel.to_precomputed())

    segfilepath = os.path.join(cv.basepath, os.path.basename(
        path), cv.skeleton.meta.skeleton_path, 'seg_props')

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


def to_precomputedskels(skelsource, path):
    """Upload skeleton (of cloudvolume class) to a local path.

    Parameters
    ----------
    skelsource:  list
        contains the cloud volume skeletons.
    path: str
        local path of the precomputed hosted layer.

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
    cv.skeleton.meta.info['vertex_attributes'] = [
        {'id': 'radius', 'data_type': 'float32', 'num_components': 1}]
    del cv.skeleton.meta.info['sharding']
    del cv.skeleton.meta.info['spatial_index']

    cv.skeleton.meta.info['segment_properties'] = 'seg_props'

    cv.skeleton.meta.commit_info()

    files = [os.path.join(cv.skeleton.meta.skeleton_path, str(skel.id)) for skel in skelsource]

    for fileidx in range(len(files)):
        fullfilepath = files[fileidx]
        fullfilepath = os.path.join(cv.basepath, os.path.basename(path), fullfilepath)
        uploadskel = Skeleton(
            vertices=skelsource[fileidx].vertices, edges=skelsource[fileidx].edges)
        # print(fullfilepath)
        with open(fullfilepath, 'wb') as f:
            f.write(uploadskel.to_precomputed())

    # delete the info file path, as they will be updated seperately..
    info_file = os.path.join(cv.basepath, os.path.basename(path), 'skeletons', 'info')
    os.remove(info_file)


def to_precomputedskelsinfo(skelseglist, skelnamelist, path):
    """Upload skeleton info to a local path.

    Parameters
    ----------
    skelseglist:  list
        contains the segids(skid).
    skelnamelist:  list
        contains the names of skeletons.
    path: str
        local path of the precomputed hosted layer.
    """

    info = {"@type": "neuroglancer_skeletons",
            "transform": [1, 0, 0, 0,
                          0, 1, 0, 0,
                          0, 0, 1, 0],
            "vertex_attributes": [{"id": "radius", "data_type": "float32", "num_components": 1}],
            "scales": "um"}
    path = 'file://' + path + '/precomputed'
    cv = CloudVolume(path, info=info)

    # prepare for info file
    cv.skeleton.meta.info['@type'] = 'neuroglancer_skeletons'
    cv.skeleton.meta.info['vertex_attributes'] = [
        {'id': 'radius', 'data_type': 'float32', 'num_components': 1}]
    del cv.skeleton.meta.info['sharding']
    del cv.skeleton.meta.info['spatial_index']

    cv.skeleton.meta.info['segment_properties'] = 'seg_props'

    cv.skeleton.meta.commit_info()

    segfilepath = os.path.join(cv.basepath, os.path.basename(
        path), cv.skeleton.meta.skeleton_path, 'seg_props')

    if not os.path.exists(segfilepath):
        os.makedirs(segfilepath)
        print('creating:', segfilepath)

    allsegproplist = {}
    allsegproplist['id'] = 'label'
    allsegproplist['type'] = 'label'
    allsegproplist['values'] = skelnamelist

    seginfo = {"@type": "neuroglancer_segment_properties",
               "inline": {"ids": skelseglist,
                          "properties": [allsegproplist]}}

    segfile = os.path.join(segfilepath, 'info')
    with open(segfile, 'w') as segfile:
        json.dump(seginfo, segfile)


def uploadshardedskeletons(skelsource, skelseglist, skelnamelist, path, layer_name, shardprogress=False):
    """Upload sharded skeletons to a local server.

    Parameters
    ----------
    skelsource:  list
        contains cloud volume skeletons.
    skelseglist:  list
        contains the segids(skid).
    skelnamelist:  list
        contains the names of segments.
    path: str
        local path of the precomputed hosted layer.
    layer_name: str
        layer name.
    shardprogress:   bool
        progress bar for sharding operation

    Returns
    -------
    cv :     CloudVolume
        object of cloudvolume class
    """
    info = {"@type": "neuroglancer_skeletons",
            "transform": skelsource[0].transform.flatten(),
            "vertex_attributes": [{"id": "radius", "data_type": "float32", "num_components": 1}],
            "scales": "um"}
    path = 'file://' + path + '/precomputed/' + layer_name
    cv = CloudVolume(path, info=info)

    # prepare for info file
    cv.skeleton.meta.info['@type'] = 'neuroglancer_skeletons'
    cv.skeleton.meta.info['transform'] = skelsource[0].transform.flatten()
    cv.skeleton.meta.info['vertex_attributes'] = [
        {'id': 'radius', 'data_type': 'float32', 'num_components': 1}]

    # prepare sharding info
    spec = ShardingSpecification('neuroglancer_uint64_sharded_v1',
                                 preshift_bits=9,
                                 hash='murmurhash3_x86_128',
                                 minishard_bits=6,
                                 shard_bits=15,
                                 minishard_index_encoding='raw',
                                 data_encoding='raw',)
    cv.skeleton.meta.info['sharding'] = spec.to_dict()

    cv.skeleton.meta.info['segment_properties'] = 'seg_props'

    cv.skeleton.meta.commit_info()

    precomputedskels = {}
    for skelidx in range(len(skelsource)):
        skelid = int(skelsource[skelidx].id)
        skel = Skeleton(skelsource[skelidx].vertices,
                        edges=skelsource[skelidx].edges,
                        segid=skelid,
                        extra_attributes=[{"id": "radius",
                                           "data_type": "float32",
                                           "num_components": 1, }]
                        ).physical_space()
        precomputedskels[skelid] = skel.to_precomputed()

    shardfiles = spec.synthesize_shards(precomputedskels, progress=shardprogress)
    shardedfilepath = os.path.join(cv.basepath, os.path.basename(path), cv.skeleton.meta.skeleton_path)

    for fname in shardfiles.keys():
        with open(shardedfilepath + '/' + fname, 'wb') as f:
            f.write(shardfiles[fname])

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


def skeletons2nodepoints(x, layer_scale):
    """Generate nodepoints (point A, point B) from skeletons for given neuron(s).

    Parameters
    ----------
    x :             CatmaidNeuron | CatmaidNeuronList or TreeNeuron | NeuronList
       neuron or neuronlist of different formats
    layer_scale : int | float
        scaling from voxel to native space in 'x', 'y', 'z'

    Returns
    -------
    nodepointscollec_df : dataframe
     contains node points in point A - point B format used in flywire annotations.
    """
    if isinstance(x, pymaid.core.CatmaidNeuron):
        x = pymaid.core.CatmaidNeuronList(x)
    elif isinstance(x, navis.core.TreeNeuron):
        x = navis.core.NeuronList(x)
    elif (isinstance(x, pymaid.core.CatmaidNeuronList) or isinstance(x, navis.core.NeuronList)):
        pass
    else:
        raise TypeError(f'Expected neuron or neuronlist, got "{type(x)}"')

    nodepointscollec_df = []
    for neuronelement in x:
        nodes = neuronelement.nodes
        nonrootnodes = nodes[nodes.parent_id >= 0]
        ptA = nonrootnodes[['x', 'y', 'z']].values
        ptB = nodes.set_index('node_id').loc[nonrootnodes.parent_id.values, ['x', 'y', 'z']].values

        # scale the points incase it is in voxel coordinates..
        ptA = ptA / layer_scale
        ptB = ptB / layer_scale

        pts_df = pd.DataFrame(pd.Series(ptA.tolist()), columns=['pointA'])
        pts_df['pointB'] = pd.Series(ptB.tolist())

        nodepointscollec_df.append([neuronelement.id, pts_df])
    nodepointscollec_df = pd.DataFrame(nodepointscollec_df, columns=['id', 'points_df'])

    return nodepointscollec_df
