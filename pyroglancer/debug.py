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

"""Test file for debugging purposes."""

# from pyroglancer.layers import handle_emdata, handle_segmentdata, handle_synapticdata
# from pyroglancer.layers import handle_synapticclefts, handle_meshes
# from pyroglancer.ngspaces import create_ngspace
# from pyroglancer.ngviewer import openviewer
# import neuroglancer as ng

import pandas as pd
from pyroglancer.layers import create_nglayer

# ngviewer = openviewer(ngviewer = None)


# layer_kws = {}
# layer_kws['ngspace'] = "FAFB"
# layer_kws['name'] = "fafb_v14_orig"
# handle_emdata(ngviewer, layer_kws)

# layer_kws = {}
# layer_kws['ngspace'] = "FAFB"
# layer_kws['name'] = "seg_20200412"
# handle_segmentdata(ngviewer, layer_kws)

# layer_kws = {}
# layer_kws['ngspace'] = "FAFB"
# layer_kws['name'] = "synapses_buhmann2019"
# handle_synapticdata(ngviewer, layer_kws)

# layer_kws = {}
# layer_kws['ngspace'] = "FAFB"
# layer_kws['name'] = "clefts_Heinrich_etal"
# handle_synapticclefts(ngviewer, layer_kws)

# layer_kws = {}
# layer_kws['ngspace'] = "FAFB"
# layer_kws['name'] = "FAFB.surf"
# handle_meshes(ngviewer, layer_kws)

# create_ngspace(ngspace='FAFB')
# create_ngspace(ngspace='FANC')
# create_ngspace(ngspace='MANC')
# create_ngspace(ngspace='hemibrain')

location_data = [{'x': 5, 'y': 10, 'z': 20}, {'x': 15, 'y': 25, 'z': 30}]
points = pd.DataFrame(location_data)
tmpviewer = create_nglayer(layer_kws={'type': 'points', 'name': 'landmarks', 'ngspace': 'MANC',
                                      'source': points, 'color': 'yellow'})
