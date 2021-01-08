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

""" Module contains functions to wrap neuroglancer spaces.
"""

from .layers import create_nglayer
import sys


def create_ngspace(space='fafb_v14'):

    if space == 'MANC':
        ngviewer = create_nglayer(layer_kws={'type': 'emdataset', 'space': space,
                                             'name': 'manc_v3'})
        ngviewer = create_nglayer(layer_kws={'type': 'meshes', 'space': space,
                                             'name': 'MANC.surf'})
        ngviewer = create_nglayer(layer_kws={'type': 'segdataset', 'space': space,
                                             'name': 'seg_mancv3'})

    elif space == 'FANC':
        ngviewer = create_nglayer(layer_kws={'type': 'emdataset', 'space': space,
                                             'name': 'fanc_v1'})
        ngviewer = create_nglayer(layer_kws={'type': 'meshes', 'space': space,
                                             'name': 'FANC.surf'})
        ngviewer = create_nglayer(layer_kws={'type': 'segdataset', 'space': space,
                                             'name': 'seg_fancv1'})

    elif space == 'FAFB':
        ngviewer = create_nglayer(layer_kws={'type': 'emdataset', 'space': space,
                                             'name': 'fafb_v14'})
        ngviewer = create_nglayer(layer_kws={'type': 'meshes', 'space': space,
                                             'name': 'FAFB.surf'})
        ngviewer = create_nglayer(layer_kws={'type': 'segdataset', 'space': space,
                                             'name': 'seg_20200412'})

    print(ngviewer)
    sys.modules['ngspace'] = space
