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

"""Module contains functions to handle neuroglancer layers."""

from .ngviewer import openviewer
from .skeletons import to_ngskeletons, uploadskeletons
from .synapses import create_synapseinfo, upload_synapses
from .points import create_pointinfo, upload_points  # , annotate_points
from .volumes import to_ngmesh, uploadmeshes
from .utils import get_hexcolor, get_alphavalue
from .loadconfig import getconfigdata

import neuroglancer
import os
import shutil
import sys


def _get_ngspace(layer_kws):
    space = layer_kws['space']
    if 'configfileloc' not in layer_kws:
        layer_kws['configfileloc'] = None
    configdata = getconfigdata(layer_kws['configfileloc'])

    try:
        ngspace = next(filter(lambda ngspace: ngspace['space'] == space, configdata))
    except:
        ValueError("exception has occured, perhaps the requested space is not present in the yml file??")
        return None

    return ngspace


def _handle_ngdimensions(layer_kws):
    """Return the dimensions of different neuroglancer spaces."""
    # return dimensions either based on already set ngspace or a string 'space'.
    dimensions = None
    if 'ngspace' in sys.modules:
        layer_kws['space'] = sys.modules['ngspace']

    if 'dimensions' in layer_kws:
        dimensions = layer_kws['dimensions']
    if 'space' in layer_kws:
        ngspace = _get_ngspace(layer_kws)

        print('Dimensions are in :', ngspace['space'])
        dimensions = neuroglancer.CoordinateSpace(
                     names=['x', 'y', 'z'], units=ngspace['dimension']['units'],
                     scales=[ngspace['dimension']['x'],
                             ngspace['dimension']['y'],
                             ngspace['dimension']['z']])

    if dimensions is None:
        raise ValueError("dimensions is not set already: either use 'space' or 'dimensions'")

    return dimensions


def flush_precomputed(path, subdir):
    """Delete/Flush a subfolder inside the precomputed folder that is hosted via http."""
    # This function is for deleting the subfolders, usually for cleaning up.

    path = os.path.join(path, 'precomputed', subdir)
    if os.path.exists(path):
        print('deleting..', path)
        shutil.rmtree(path)


def get_ngserver():
    """Return the local folder hosted via http and its corresponding port."""
    # This function fetches: a)the already set neuroglancer local folder(hosted via http).
    # b)the port number of the http host

    layer_serverdir = sys.modules['ngserverdir']
    layer_host = str(sys.modules['ngserver'].socket.getsockname()[1])
    layer_host = 'http://localhost:' + layer_host

    return layer_serverdir, layer_host


def handle_emdata(ngviewer, layer_kws):
    """Add the electron microscopy layer as a neuroglancer layer."""
    # This function adds EM layer to a neuroglancer instance.
    # The EM layers are usually corresponding to spaces like 'FAFB', etc
    ngspace = _get_ngspace(layer_kws)

    for layername in ngspace['layers']:
        if ngspace['layers'][layername]['type'] == 'image':
            with ngviewer.txn() as s:
                s.layers[layername] = neuroglancer.ImageLayer(
                        source=ngspace['layers'][layername]['source'],)

    return ngviewer


def handle_segmentdata(ngviewer, layer_kws):
    """Add the different neuron segmentation datasets as a neuroglancer layer."""
    # This function adds segmentation of EM layer to a neuroglancer instance.
    # The EM segmentations usually correspond to autosegs from google for datasets like 'FAFB' etc
    ngspace = _get_ngspace(layer_kws)

    for layername in ngspace['layers']:
        if ngspace['layers'][layername]['type'] == 'segmentation':
            with ngviewer.txn() as s:
                s.layers[layername] = neuroglancer.SegmentationLayer(
                        source=ngspace['layers'][layername]['source'],)

    return ngviewer


def handle_synapticdata(ngviewer, layer_kws):
    """Add the synapse predictions for the em datasets as a neuroglancer layer."""
    # This function adds synapse predictions to a neuroglancer instance.

    ngspace = _get_ngspace(layer_kws)

    for layername in ngspace['layers']:
        if ngspace['layers'][layername]['type'] == 'synapsepred':
            with ngviewer.txn() as s:
                s.layers[layername] = neuroglancer.AnnotationLayer(
                        source=ngspace['layers'][layername]['source'],
                        linked_segmentation_layer={'pre_segment': ngspace['layers'][layername]['linkedseg'],
                                                   'post_segment': ngspace['layers'][layername]['linkedseg']},
                        filter_by_segmentation=['post_segment', 'pre_segment'],
                        shader='''#uicontrol vec3 preColor color(default=\"blue\")
                                  # uicontrol vec3 postColor color(default=\"red\")
                                  # uicontrol float scorethr slider(min=0, max=1000)
                                  # uicontrol int showautapse slider(min=0, max=1)

                                  void main() {
                                  setColor(defaultColor());
                                  setEndpointMarkerColor(
                                  vec4(preColor, 0.5),
                                  vec4(postColor, 0.5));
                                  setEndpointMarkerSize(5.0, 5.0);
                                  setLineWidth(2.0);
                                  if (int(prop_autapse()) > showautapse) discard;
                                  if (prop_score()<scorethr) discard;
                                  }''',
                        shaderControls={"scorethr": 80},
                                           )

    return ngviewer


def handle_synapticclefts(ngviewer, layer_kws):
    """Add the synapse cleft predictions for the em dataset as a neuroglancer layer."""
    # This function adds synapse cleft predictions to a neuroglancer instance.

    ngspace = _get_ngspace(layer_kws)

    for layername in ngspace['layers']:
        if ngspace['layers'][layername]['type'] == 'synapticcleft':
            with ngviewer.txn() as s:
                s.layers[layername] = neuroglancer.ImageLayer(
                        source=ngspace['layers'][layername]['source'],
                        shader='void main() {emitRGBA(vec4(0.0,0.0,1.0,toNormalized(getDataValue())));}',
                        opacity=0.73)

    return ngviewer


def handle_meshes(ngviewer, layer_kws):
    """Add the different surface meshes as a neuroglancer layer."""
    # This function adds meshes usually based on neuropil boundaries to a neuroglancer instance.

    ngspace = _get_ngspace(layer_kws)

    # for meshes as a mesh layer
    for layername in ngspace['layers']:
        if ngspace['layers'][layername]['type'] == 'surfacemesh':
            with ngviewer.txn() as s:
                s.layers[layername] = neuroglancer.SingleMeshLayer(
                        source=ngspace['layers'][layername]['source'],
                        shader='void main() {emitRGBA(vec4(0.859, 0.859, 0.859, 0.3));}')

    # for meshes as a segment layer
    for layername in ngspace['layers']:
        if ngspace['layers'][layername]['type'] == 'segmentmesh':
            with ngviewer.txn() as s:
                s.layers[layername] = neuroglancer.SegmentationLayer(
                        source=ngspace['layers'][layername]['source'],
                        segmentQuery='/',
                        objectAlpha=0.3)

    return ngviewer


def handle_skels(ngviewer, path, segmentColors, alpha):
    """Add skeletons hosted via http as a neuroglancer layer."""
    # This function adds skeletons in the precomputed format hosted locally via http to a neuroglancer instance.

    precomputepath = 'precomputed://' + path + '/precomputed/skeletons'
    with ngviewer.txn() as s:
        s.layers['skeleton'] = neuroglancer.SegmentationLayer(
            source=precomputepath,
            segmentQuery='/',
            segmentColors=segmentColors,
            objectAlpha=alpha)

    return ngviewer


def handle_vols(ngviewer, path, segmentColors, alpha):
    """Add volumes hosted via http as a neuroglancer layer."""
    # This function adds volumes in the precomputed format hosted locally via http to a neuroglancer instance.

    precomputepath = 'precomputed://' + path + '/precomputed/mesh#type=mesh'
    with ngviewer.txn() as s:
        s.layers['volume'] = neuroglancer.SegmentationLayer(
            source=precomputepath,
            segmentQuery='/',
            segmentColors=segmentColors,
            objectAlpha=alpha)

    return ngviewer


def handle_synapses(ngviewer, path):
    """Add pre/post-synapses hosted via http as a neuroglancer layer."""
    # This function adds synapses in the precomputed format hosted remotely via http to a neuroglancer instance.
    presynapsepath = 'precomputed://' + path + '/precomputed/presynapses'
    postsynapsepath = 'precomputed://' + path + '/precomputed/postsynapses'
    with ngviewer.txn() as s:
        s.layers['presynapses'] = neuroglancer.AnnotationLayer(
            source=presynapsepath,
            annotationColor='#ff0000',
            linked_segmentation_layer={'presynapses_cell': 'skeleton'},
            filter_by_segmentation=['presynapses_cell'])
        s.layers['postsynapses'] = neuroglancer.AnnotationLayer(
            source=postsynapsepath,
            annotationColor='#0000ff',
            linked_segmentation_layer={'postsynapses_cell': 'skeleton'},
            filter_by_segmentation=['postsynapses_cell'])

    return ngviewer


def handle_points(ngviewer, path, layer_name, annotationColor):
    """Add points hosted via http as a neuroglancer layer."""
    # This function adds points in the precomputed format hosted locally via http to a neuroglancer instance.
    pointpath = 'precomputed://' + path + '/precomputed/' + layer_name
    with ngviewer.txn() as s:
        s.layers[layer_name] = neuroglancer.AnnotationLayer(
            source=pointpath,
            annotationColor=annotationColor)

    return ngviewer


def create_nglayer(ngviewer=None, layout='xy-3d', **kwargs):
    """Create a neuroglancer layer and print the url as output.

    Parameters
    ----------
    ngviewer :  ng.viewer.Viewer
        object of Neuroglancer viewer class.
    layout :   layout of neuroglancer window

    Returns
    -------
    ngviewer :  ng.viewer.Viewer
        object of Neuroglancer viewer class.
    """
    _LAYOUT_OPTIONS = ['xy', 'yz', 'xz', 'xy-3d', 'yz-3d', 'xz-3d', '4panel', '3d']
    if layout not in _LAYOUT_OPTIONS:
        raise ValueError('Unknown method "{0}". Please use either: {1}'.format(
            layout, _LAYOUT_OPTIONS))

    layer_kws = kwargs.get('layer_kws', {})

    ngviewer = openviewer(ngviewer)

    if layer_kws:

        dimensions = _handle_ngdimensions(layer_kws)
        layer_type = layer_kws['type']
        print('Layer created: ', layer_type)

        if layer_type == 'image':
            handle_emdata(ngviewer, layer_kws)

        if layer_type == 'segmentation':
            handle_segmentdata(ngviewer, layer_kws)

        if layer_type == 'synapsepred':
            handle_synapticdata(ngviewer, layer_kws)

        if layer_type == 'synapticcleft':
            handle_synapticclefts(ngviewer, layer_kws)

        if (layer_type == 'surfacemesh') or (layer_type == 'segmentmesh'):
            handle_meshes(ngviewer, layer_kws)

        if layer_type == 'skeletons':
            layer_source = layer_kws['source']
            layer_serverdir, layer_host = get_ngserver()
            hexcolor = get_hexcolor(layer_kws)
            flush_precomputed(layer_serverdir, 'skeletons')
            alpha = get_alphavalue(layer_kws)

            skelsource, skelseglist, skelsegnamelist = to_ngskeletons(layer_source)
            print(hexcolor)
            segmentColors = dict(zip(skelseglist, hexcolor))
            print(segmentColors)
            uploadskeletons(skelsource, skelseglist, skelsegnamelist, layer_serverdir)
            ngviewer = handle_skels(ngviewer, layer_host, segmentColors, alpha)

        if layer_type == 'volumes':
            layer_source = layer_kws['source']
            layer_serverdir, layer_host = get_ngserver()
            hexcolor = get_hexcolor(layer_kws)
            flush_precomputed(layer_serverdir, 'mesh')
            alpha = get_alphavalue(layer_kws)

            volumedatasource, volumeidlist, volumenamelist = to_ngmesh(layer_source)
            print(hexcolor)
            segmentColors = dict(zip(volumeidlist, hexcolor))
            print(segmentColors)
            uploadmeshes(volumedatasource, volumeidlist, volumenamelist, layer_serverdir)
            ngviewer = handle_vols(ngviewer, layer_host, segmentColors, alpha)

        if layer_type == 'synapses':
            layer_source = layer_kws['source']
            layer_serverdir, layer_host = get_ngserver()

            flush_precomputed(layer_serverdir, 'presynapses')
            flush_precomputed(layer_serverdir, 'postsynapses')

            synapse_path = create_synapseinfo(dimensions, layer_serverdir)
            upload_synapses(layer_source, synapse_path)
            ngviewer = handle_synapses(ngviewer, layer_host)

        if layer_type == 'points':
            layer_source = layer_kws['source']
            layer_name = layer_kws['name']
            hexcolor = get_hexcolor(layer_kws)
            layer_scale = layer_kws['scale']
            print(layer_scale)

            annotationColors = hexcolor[0]
            # alpha = get_alphavalue(layer_kws)

            layer_serverdir, layer_host = get_ngserver()

            flush_precomputed(layer_serverdir, layer_name)

            points_path = create_pointinfo(dimensions, layer_serverdir, layer_name)
            upload_points(layer_source, points_path, layer_name, layer_scale)
            ngviewer = handle_points(ngviewer, layer_host, layer_name, annotationColors)

            # annotate_points(ngviewer, dimensions, layer_source, layer_scale)

    if layout:
        with ngviewer.txn() as s:
            print('Using layout :', layout)
            s.layout = neuroglancer.layout_specification = layout

    # setup some stuff at the end..
    with ngviewer.txn() as s:
        s.show_slices = False

    return(ngviewer)