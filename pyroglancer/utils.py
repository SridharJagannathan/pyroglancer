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

"""Module contains utility functions."""
from .loadconfig import getconfigdata
import webcolors


def get_hexcolor(layer_kws):
    """Convert text based color to hex value."""
    # This function converts css color text to hex based.
    if 'color' in layer_kws:
        layer_color = layer_kws['color']
    else:
        layer_color = 'yellow'
    rawcolorlist = layer_color

    if not isinstance(rawcolorlist, list):
        rawcolorlist = (rawcolorlist,)

    hexcolorlist = []
    for hexcolor in rawcolorlist:
        if not hexcolor.startswith("#"):
            hexcolor = webcolors.name_to_hex(hexcolor)
        hexcolorlist.append(hexcolor)
    return hexcolorlist


def get_alphavalue(layer_kws):
    """Get alpha values from the interface APIs."""
    # This function gets alpha/transparency values.
    layer_alpha = layer_kws.get("alpha", 1.0)
    return layer_alpha


def get_annotationstatetype(layer_kws):
    """Get alpha values from the interface APIs."""
    # This function gets alpha/transparency values.
    layer_statetype = layer_kws.get("annotationstatetype", 'in-json')
    return layer_statetype


def _get_configvox2physical(layer_kws):
    scale = layer_kws.get("scale", None)
    if scale is None:
        layer_kws['configfileloc'] = layer_kws.get('configfileloc', None)
        configdata = getconfigdata(layer_kws['configfileloc'])
        ngspaceconfig = next(filter(lambda ngspace: ngspace['ngspace'] == layer_kws['ngspace'], configdata))
        scale = [ngspaceconfig['voxelsize'].get(key) for key in ['x', 'y', 'z']]
    return scale


def get_scalevalue(layer_kws):
    """Get scale values from the interface APIs."""
    # This function gets scale values for annotations.
    space = layer_kws.get("space", "voxel")
    if space == "voxel":
        scale = _get_configvox2physical(layer_kws)
    else:
        scale = [1, 1, 1]
    print('using ', space, 'space', 'with scale: ', scale)

    return scale
