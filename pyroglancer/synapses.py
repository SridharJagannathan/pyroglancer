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

""" Module contains functions to handle synapse data.
"""

import pymaid
import navis
import neuroglancer


def annotate_synapses(ngviewer, dimensions, x):
    """

    Annotate postsynapses of a neuron/neuronlist.

    This function annotates synapses of a neuron/neuronlist

    Parameters
    ----------
    x :             CatmaidNeuron | CatmaidNeuronList or TreeNeuron | NeuronList
    ngviewer:        Neuroglancer viewer


    """
    if isinstance(x, pymaid.core.CatmaidNeuron):
        neuronlist = pymaid.core.CatmaidNeuronList(x)
    elif isinstance(x, pymaid.core.CatmaidNeuronList):
        neuronlist = x
    elif isinstance(x, navis.core.TreeNeuron):
        neuronlist = navis.core.NeuronList(x)

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
