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

"""Module contains functions to handle synapse data."""

import pymaid
import navis
import neuroglancer
import json
import os
import struct


def commit_info(synapseinfo, path, synapsetype):
    """
    Commit the info file created for the synapses based on precomputed format.

    Parameters
    ----------
    synapseinfo : info in json format for the synapses
    path:         path for the dataserver hosted locally
    synapsetype : pre or postsynapses
    """
    synapsefilepath = path + '/precomputed/' + synapsetype
    if not os.path.exists(synapsefilepath):
        os.makedirs(synapsefilepath)
        print('creating:', synapsefilepath)
    infofile = os.path.join(synapsefilepath, 'info')
    with open(infofile, 'w') as f:
        json.dump(synapseinfo, f)


def create_synapseinfo(dimensions, path):
    """
    Create info file for the synapse based precomputed format.

    Parameters
    ----------
    path:            path for the dataserver hosted locally
    dimensions :     dimensions used by neuroglancer

    """
    synapseinfo = {
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
                "chunk_size": [34422, 37820, 41362],
                "grid_shape": [1, 1, 1],
                "key": "spatial0",
                "limit": 10000
            }
        ],
        "upper_bound": [34422, 37820, 41362]
    }
    synapseinfo["relationships"] = [{"id": "presynapses_cell",
                                     "key": "presynapses_cell"}]
    commit_info(synapseinfo, path, synapsetype='presynapses')
    synapseinfo["relationships"] = [{"id": "postsynapses_cell",
                                     "key": "postsynapses_cell"}]
    commit_info(synapseinfo, path, synapsetype='postsynapses')
    return path


def put_synapsefile(path, synapsetype, synapses, skeletonid):
    """
    Put synapse in the local dataserver.

    Parameters
    ----------
    path:            path for the dataserver hosted locally
    synapsetype :    pre or post synapse
    synapses :       dataframe containing 'x', 'y', 'z' columns
    skeletonid :     skeleton id to be associated with the corresponding synapse
    pointsname :     name for the points (not yet implemented)

    """
    synapsefilepath = path + '/precomputed/' + synapsetype + '/' + synapsetype + '_cell/'
    if not os.path.exists(synapsefilepath):
        os.makedirs(synapsefilepath)
        # print('creating:', synapsefilepath)
    synapsefile = os.path.join(synapsefilepath, str(skeletonid))
    print('making:', synapsefile)
    synapselocs = synapses[['x', 'y', 'z']].values/1000

    # implementation based on logic suggested by https://github.com/google/neuroglancer/issues/227
    with open(synapsefile, 'wb') as outputbytefile:
        total_synapses = len(synapselocs)  # coordinates is a list of tuples (x,y,z)
        buffer = struct.pack('<Q', total_synapses)
        for (x, y, z) in synapselocs:
            synapsepoint = struct.pack('<3f', x, y, z)
            buffer += synapsepoint
        # write the ids of the individual points at the very end..
        synapseid_buffer = struct.pack('<%sQ' % len(synapselocs), *range(len(synapselocs)))
        buffer += synapseid_buffer
        outputbytefile.write(buffer)


def upload_synapses(x, path):
    """
    Upload synpases from a neuron or neuronlist.

    Parameters
    ----------
    x :   neuron or neuronlist
    path: path for the dataserver hosted locally

    """
    if isinstance(x, pymaid.core.CatmaidNeuron):
        neuronlist = pymaid.core.CatmaidNeuronList(x)
    elif isinstance(x, navis.core.TreeNeuron):
        neuronlist = navis.core.NeuronList(x)
    elif (isinstance(x, pymaid.core.CatmaidNeuronList) or isinstance(x, navis.core.NeuronList)):
        neuronlist = x
    else:
        raise TypeError(f'Expected neuron or neuronlist, got "{type(x)}"')

    for neuronidx in range(len(neuronlist)):
        neuronelement = neuronlist[neuronidx]
        presynapses = neuronelement.presynapses
        postsynapses = neuronelement.postsynapses
        print('Adding neuron: ', neuronelement.id)
        put_synapsefile(path, 'presynapses', presynapses, neuronelement.id)
        put_synapsefile(path, 'postsynapses', postsynapses, neuronelement.id)


def annotate_synapses(ngviewer, dimensions, x):
    """
    Annotate postsynapses of a neuron/neuronlist. (defunct do not use..).

    This function annotates synapses of a neuron/neuronlist

    Parameters
    ----------
    x :             CatmaidNeuron | CatmaidNeuronList or TreeNeuron | NeuronList
    ngviewer:        Neuroglancer viewer


    """
    if isinstance(x, pymaid.core.CatmaidNeuron):
        neuronlist = pymaid.core.CatmaidNeuronList(x)
    elif isinstance(x, navis.core.TreeNeuron):
        neuronlist = navis.core.NeuronList(x)
    elif (isinstance(x, pymaid.core.CatmaidNeuronList) or isinstance(x, navis.core.NeuronList)):
        neuronlist = x
    else:
        raise TypeError(f'Expected neuron or neuronlist, got "{type(x)}"')

    skeldatasegidlist = []
    for neuron in neuronlist:
        skeldatasegidlist.append(neuron.id)

    # postsynapses first..
    with ngviewer.txn() as s:
        s.layers.append(
            name="post_synapses",
            layer=neuroglancer.LocalAnnotationLayer(
                dimensions=dimensions,
                annotation_relationships=['post_synapses'],
                linked_segmentation_layer={'post_synapses': 'skeletons'},
                filter_by_segmentation=['post_synapses'],
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

    with ngviewer.txn() as s:
        for neuronidx in range(len(neuronlist)):
            neuronelement = neuronlist[neuronidx]
            postsynapses = neuronelement.postsynapses
            postsynapses = postsynapses.reset_index()

            for index, postsyn in postsynapses.iterrows():
                s.layers['post_synapses'].annotations.append(
                    neuroglancer.PointAnnotation(
                        id=str(index),
                        point=[postsyn.x/1000, postsyn.y/1000, postsyn.z/1000],
                        segments=[[skeldatasegidlist[neuronidx]]],
                        props=['#0000ff'],
                    )
                )

    # presynapses next..
    with ngviewer.txn() as s:
        s.layers.append(
            name="pre_synapses",
            layer=neuroglancer.LocalAnnotationLayer(
                dimensions=dimensions,
                annotation_relationships=['pre_synapses'],
                linked_segmentation_layer={'pre_synapses': 'skeletons'},
                filter_by_segmentation=['pre_synapses'],
                ignore_null_segment_filter=False,
                annotation_properties=[
                    neuroglancer.AnnotationPropertySpec(
                        id='color',
                        type='rgb',
                        default='red',
                    )
                ],
                shader='''
                        void main() {
                          setColor(prop_color());
                          setPointMarkerSize(5.0);
                        }
                        ''',
            ))

    with ngviewer.txn() as s:
        for neuronidx in range(len(neuronlist)):
            neuronelement = neuronlist[neuronidx]
            presynapses = neuronelement.presynapses
            presynapses = presynapses.reset_index()

            for index, presyn in presynapses.iterrows():
                s.layers['pre_synapses'].annotations.append(
                    neuroglancer.PointAnnotation(
                        id=str(index),
                        point=[presyn.x/1000, presyn.y/1000, presyn.z/1000],
                        segments=[[skeldatasegidlist[neuronidx]]],
                        props=['#ff0000'],
                    )
                )
