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

"""Module contains functions to wrap neuroglancer spaces."""

from .layers import _get_ngspace
from .layers import create_nglayer
import sys


def create_ngspace(layer_kws):
    """Create a neuroglancer space (EM layers, segmentation, neuropil surfaces).

    Parameters
    ----------
    layer_kws: dict
        containing details about different neuroglancer layers
    """
    ngspace = layer_kws.get('ngspace', 'FAFB')
    ngspaceconfig = _get_ngspace(layer_kws)
    for layername in ngspaceconfig['layers']:
        create_nglayer(layer_kws={'type': ngspaceconfig['layers'][layername]['type'],
                                  'ngspace': ngspace, 'name': layername})

    # print(ngviewer)
    sys.modules['ngspace'] = ngspace
