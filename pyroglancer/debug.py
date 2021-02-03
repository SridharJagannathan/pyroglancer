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

# shorturl = 'https://ngl.flywire.ai/?json_url=https://globalv1.flywire-daf.com/nglstate/5571829238333440'
# longurl = 'https://ngl.flywire.ai/#!%7B%22layers%22:%5B%7B%22source%22:%22precomputed://gs://microns-seunglab/drosophila_v0/alignment/image_rechunked%22%2C%22type%22:%22image%22%2C%22blend%22:%22default%22%2C%22shaderControls%22:%7B%7D%2C%22name%22:%22Production-image%22%7D%2C%7B%22source%22:%22graphene://https://prodv1.flywire-daf.com/segmentation/1.0/fly_v31%22%2C%22type%22:%22segmentation_with_graph%22%2C%22colorSeed%22:3742675410%2C%22segments%22:%5B%22720575940577944770%22%2C%22720575940606347531%22%2C%22720575940617089669%22%2C%22720575940645185924%22%5D%2C%22hiddenSegments%22:%5B%22720575940606750165%22%2C%22720575940607328373%22%2C%22720575940610232037%22%2C%22720575940613090114%22%2C%22720575940618381295%22%2C%22720575940619773473%22%2C%22720575940622610919%22%2C%22720575940628278748%22%2C%22720575940628869391%22%2C%22720575940629056018%22%2C%22720575940630464595%22%2C%22720575940634160247%22%2C%22720575940637478744%22%2C%22720575940645228921%22%5D%2C%22skeletonRendering%22:%7B%22mode2d%22:%22lines_and_points%22%2C%22mode3d%22:%22lines%22%7D%2C%22graphOperationMarker%22:%5B%7B%22annotations%22:%5B%5D%2C%22tags%22:%5B%5D%7D%2C%7B%22annotations%22:%5B%5D%2C%22tags%22:%5B%5D%7D%5D%2C%22pathFinder%22:%7B%22color%22:%22#ffff00%22%2C%22pathObject%22:%7B%22annotationPath%22:%7B%22annotations%22:%5B%5D%2C%22tags%22:%5B%5D%7D%2C%22hasPath%22:false%7D%7D%2C%22name%22:%22Production-segmentation_with_graph%22%7D%5D%2C%22navigation%22:%7B%22pose%22:%7B%22position%22:%7B%22voxelSize%22:%5B4%2C4%2C40%5D%2C%22voxelCoordinates%22:%5B125724.1640625%2C53187.34765625%2C3593.458251953125%5D%7D%7D%2C%22zoomFactor%22:4.489367582399096%7D%2C%22perspectiveOrientation%22:%5B0.05597979575395584%2C0.1316245198249817%2C0.04441007226705551%2C0.9887208938598633%5D%2C%22perspectiveZoom%22:174.97949571792066%2C%22jsonStateServer%22:%22https://globalv1.flywire-daf.com/nglstate/post%22%2C%22selectedLayer%22:%7B%22layer%22:%22Production-segmentation_with_graph%22%2C%22visible%22:true%7D%2C%22layout%22:%22xy-3d%22%7D'
# ngdict = flywireurl2dict(shorturl)

# swc_path = os.path.join(BASE_DIR, 'pyroglancer/data/swc')
# swc_files = glob.glob(os.path.join(swc_path, '40637.swc'))

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
# tempval = []
