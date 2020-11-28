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


def omit_nones(seg_list):
    if seg_list is None:
        return []

    seg_list = list(filter(lambda x: x is not None, seg_list))
    if len(seg_list) == 0:
        return []
    else:
        return seg_list


def annotate_postsynapses(x, nglayer):
    """

    Annotate postsynapses of a neuron/neuronlist.

    This function annotates synapses of a neuron/neuronlist

    Parameters
    ----------
    x :             CatmaidNeuron | CatmaidNeuronList or TreeNeuron | NeuronList
    nglayer:        Neuroglancer layer


    """
    if isinstance(x, pymaid.core.CatmaidNeuron):
        neuronlist = pymaid.core.CatmaidNeuronList(x)
    elif isinstance(x, pymaid.core.CatmaidNeuronList):
        neuronlist = x
    elif isinstance(x, navis.core.TreeNeuron):
        neuronlist = navis.core.NeuronList(x)

    for neuronidx in range(len(neuronlist)):
        neuronelement = neuronlist[neuronidx]
        annotations = nglayer.layers['post_synapses'].annotations
        postsynapses = neuronelement.postsynapses
        postsynapses = postsynapses.reset_index()
        # segmentlist = [[] for i in range(len(postsynapses))]
        # segmentlist = [[]] * 1
        for index, postsyn in postsynapses.iterrows():
            annotations.append(neuroglancer.PointAnnotation(
                id=str(postsyn.connector_id),
                # segments=segmentlist,
                # segments=omit_nones(linked_segmentation)),
                point=[postsyn.x/1000, postsyn.y/1000, postsyn.z/1000],
                props=['#01FE01', 10]))  # 0000ff
