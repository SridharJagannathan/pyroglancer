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

"""Module contains functions to handle neuroglancer layers for flywire tracing."""

import cloudvolume
import json
from pyroglancer.layers import add_precomputed
import requests
from urllib.parse import parse_qs
from urllib.parse import urlparse

FLYWIRESTATE_URL = 'https://globalv1.flywire-daf.com/nglstate'
FLYWIREHOST_URL = 'https://ngl.flywire.ai'


def flywireurl2dict(flywireurl):
    """Return dict from a flywire based short or long url.

    Parameters
    ----------
    flywireurl: short or long url of the flywire instance

    Returns
    -------
    ngdict: dict containing different layers of the flywire instance
    """
    assert isinstance(flywireurl, (str, dict))

    # get the query string..
    queryurl = urlparse(flywireurl).query
    # convert query to string..
    querystring = parse_qs(queryurl, keep_blank_values=True)

    if 'json_url' in querystring:
        # Get the layers from the json file as query
        token = cloudvolume.secrets.chunkedgraph_credentials['token']
        response = requests.get(querystring['json_url'][0], headers={'Authorization': f"Bearer {token}"})
        response.raise_for_status()

        ngdict = response.json()
    else:
        ngdict = querystring

    return ngdict


def flywiredict2url(ngdict):
    """Return a flywire based short url.

    Parameters
    ----------
    ngdict: dict containing different layers of the flywire instance

    Returns
    -------
    flywireurl: short url of the flywire instance
    """
    token = cloudvolume.secrets.chunkedgraph_credentials['token']
    jsonbaseurl = FLYWIRESTATE_URL
    flywirebaseurl = FLYWIREHOST_URL
    session = requests.Session()

    requesturl = f'{jsonbaseurl}/post'
    response = session.post(requesturl, data=json.dumps(ngdict),
                            headers={'Authorization': f"Bearer {token}"})
    response.raise_for_status()

    jsonqueryurl = response.json()
    flywireurl = f'{flywirebaseurl}/?json_url={jsonqueryurl}'

    return flywireurl


def add_flywirelayer(ngdict, layer_kws):
    """Return dict from a flywire based short or long url.

    Parameters
    ----------
    ngdict: a dict containing different layers of the flywire instance
    layer_kws: a dict containing different parameters about the layer to add

    Returns
    -------
    flywireurl: url containing the updated flywire instance
    """
    layer_type = layer_kws['type']
    if layer_type == 'skeletons':
        skelseglist, layer_host = add_precomputed(layer_kws)
        skeleton_layer = {"type": "segmentation",
                          "skeletons": "precomputed://" + layer_host + "/precomputed/skeletons",
                          "skeletonRendering": {"mode2d": "lines_and_points", "mode3d": "lines"},
                          "segments": skelseglist,
                          "name": "skeleton"}
        ngdict['layers'].append(skeleton_layer)
        flywireurl = flywiredict2url(ngdict)
        print('flywire url at:', flywireurl)

    elif layer_type == 'volumes':
        volumeidlist, layer_host = add_precomputed(layer_kws)
        layer_name = layer_kws.get('name', 'volumes')
        volume_layer = {"type": "segmentation",
                        "mesh": "precomputed://" + layer_host + "/precomputed/" + layer_name + "/mesh",
                        "skeletonRendering": {"mode2d": "lines_and_points", "mode3d": "lines"},
                        "segments": volumeidlist,
                        "name": "volumes"}
        ngdict['layers'].append(volume_layer)
        flywireurl = flywiredict2url(ngdict)
        print('flywire url at:', flywireurl)

    elif layer_type == 'synapses':
        layer_host = add_precomputed(layer_kws)
        presynapsepath = 'precomputed://' + layer_host + '/precomputed/presynapses'
        postsynapsepath = 'precomputed://' + layer_host + '/precomputed/postsynapses'
        presynapse_layer = {"type": "annotation",
                            "source": presynapsepath,
                            "annotationColor": "#ff0000",
                            "linkedSegmentationLayer": {"presynapses_cell": "skeleton"},
                            "filterBySegmentation": ["postsynapses_cell"],
                            "name": "presynapses"}
        postsynapse_layer = {"type": "annotation",
                             "source": postsynapsepath,
                             "annotationColor": "#0000ff",
                             "linkedSegmentationLayer": {"postsynapses_cell": "skeleton"},
                             "filterBySegmentation": ["postsynapses_cell"],
                             "name": "postsynapses"}

        ngdict['layers'].append(presynapse_layer)
        ngdict['layers'].append(postsynapse_layer)

        flywireurl = flywiredict2url(ngdict)
        print('flywire url at:', flywireurl)
    elif layer_type == 'points':
        layer_host, layer_name = add_precomputed(layer_kws)
        pointpath = 'precomputed://' + layer_host + '/precomputed/' + layer_name
        point_layer = {"type": "annotation",
                       "source": pointpath,
                       "annotationColor": "#ff0000",
                       "name": layer_name}
        ngdict['layers'].append(point_layer)
        flywireurl = flywiredict2url(ngdict)
        print('flywire url at:', flywireurl)

    else:
        flywireurl = None

    return flywireurl
