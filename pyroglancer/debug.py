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
# from pyroglancer.localserver import startdataserver, closedataserver
# from pyroglancer.ngviewer import openviewer
# import neuroglancer as ng
# import pandas as pd
# from pyroglancer.layers import create_nglayer, add_precomputed
# from pyroglancer.flywire import flywireurl2dict, add_flywirelayer
# import os
# import glob
# import navis
# import flybrains
# import fafbseg

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

# startdataserver()
# create_ngspace(ngspace='FAFB')
# temp_pts = pd.DataFrame([[123072, 47001, 3375], [120000, 17001, 3000]], columns=['x', 'y', 'z'])
# temp_pts['description'] = 'temp_pts'
# tmpviewer = create_nglayer(layer_kws={'type': 'points', 'name': 'landmarks',
#                                       'source': temp_pts, 'color': 'magenta'})

# temp_pts = []

# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# shorturl = 'https://ngl.flywire.ai/?json_url=https://globalv1.flywire-daf.com/nglstate/5692426366746624'
# ngdict = flywireurl2dict(shorturl)

# swc_path = os.path.join(BASE_DIR, 'pyroglancer/data/swc')
# swc_files = glob.glob(os.path.join(swc_path, '57323.swc'))

# neuronlist = []
# neuronlist += [navis.read_swc(f, units='8 nm', connector_labels={'presynapse': 7, 'postsynapse': 8},
#                               id=int(os.path.splitext(os.path.basename(f))[0])) for f in swc_files]

# neuronlist = navis.core.NeuronList(neuronlist)
# neuronlist = None
# startdataserver()
# layer_kws = {'type': 'skeletons', 'source': neuronlist}
# add_flywirelayer(ngdict, layer_kws)
# #add_precomputed('skeletons', layer_kws)

# closedataserver()

# neuronlist = []
# neuronlist += [navis.read_swc(f, units='8 nm', connector_labels={'presynapse': 7, 'postsynapse': 8},
#                               id=int(os.path.splitext(os.path.basename(f))[0])) for f in swc_files]
# neuronlist = navis.core.NeuronList(neuronlist)

# flybrains.download_jefferislab_transforms()
# flybrains.download_saalfeldlab_transforms()
# flybrains.register_transforms()

# startdataserver()

# pre_syn_df2 = pd.read_hdf('/Users/sri/Downloads/test_data.h5', 'presyn').head(5)
# flywire_neuron = navis.xform_brain(neuronlist, source='FAFB14', target='FLYWIRE')
# flywire_neuron = navis.resample_neuron(flywire_neuron, resample_to=1000*8, inplace=False)
# layer_kws = {'type': 'synapses', 'source': flywire_neuron, 'annotationstatetype': 'in-json',
#              'color': ['red', 'blue'],
#               "scale": [4,4,40]}
# flywireurl = add_flywirelayer(ngdict, layer_kws)

# tempval = []

# scale = layer_kws.get("scale", 0)
