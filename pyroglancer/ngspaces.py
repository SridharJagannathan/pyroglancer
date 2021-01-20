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

from .layers import create_nglayer, _get_ngspace
import sys


def create_ngspace(ngspace='FAFB'):
    """Create a neuroglancer space (EM layers, segmentation, neuropil surfaces).

    Parameters
    ----------
    ngspace : dataset to be used for e.g. : FAFB etc

    Returns
    -------
    None
    """
    layer_kws = {}
    layer_kws['ngspace'] = ngspace
    ngspaceconfig = _get_ngspace(layer_kws)
    for layername in ngspaceconfig['layers']:
        create_nglayer(layer_kws={'type': ngspaceconfig['layers'][layername]['type'],
                                  'ngspace': ngspace, 'name': layername})

    # print(ngviewer)
    sys.modules['ngspace'] = ngspace
