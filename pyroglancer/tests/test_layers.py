"""Module contains test cases for layers.py module."""

import glob
import os
import unittest

import navis
import neuroglancer as ng
import pandas as pd
from pyroglancer.layers import _handle_ngdimensions
from pyroglancer.layers import create_nglayer
from pyroglancer.layers import get_ngserver
from pyroglancer.localserver import closedataserver
from pyroglancer.localserver import startdataserver
from pyroglancer.ngviewer import closeviewer
from pyroglancer.ngviewer import openviewer
import pytest


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add a common viewer, dataserver(specific port for travis) for each test module..
closeviewer()
closedataserver()
startdataserver(port=8007)  # start dataserver..
openviewer(headless=True)  # open ngviewer


# def setup_module(module):
#     """Start all servers."""
#     # Add a common viewer, dataserver for the whole serie of test..
#     startdataserver()  # start dataserver..
#     openviewer(headless=True)  # open ngviewer
#
#
# def teardown_module(module):
#     """Stop all servers."""
#     # Stop all viewers..
#     closedataserver()
#     closeviewer()


class Testlayers(unittest.TestCase):
    """Test pyroglancer.layers."""

    # def setUp(self):
    #     """Perform set up."""
    #     super(Testsynapses, self).setUp()
    #
    # def tearDown(self):
    #     """Perform tearing down."""
    #     super(Testsynapses, self).tearDown()

    def test_create_ngsegmentlayer(self):
        """Check if the segdataset seg_20190805 is created."""
        layer_serverdir, layer_host = get_ngserver()

        ngviewer = openviewer(None)

        ngviewer2 = create_nglayer(ngviewer=ngviewer,
                                   layer_kws={'type': 'segdataset', 'ngspace': 'FAFB', 'name': 'seg_20190805'})

        assert ngviewer2 == ngviewer

    def test_create_ngbuhmannsynapselayer(self):
        """Check if the buhmann synapse layer is created."""
        layer_serverdir, layer_host = get_ngserver()

        ngviewer = openviewer(None)

        ngviewer2 = create_nglayer(ngviewer=ngviewer,
                                   layer_kws={'type': 'synapticlayer', 'ngspace': 'FAFB',
                                              'name': 'synapses_buhmann2019'})

        assert ngviewer2 == ngviewer

    def test_create_ngsynapticcleftslayer(self):
        """Check if the synaptic clefts layer is created."""
        layer_serverdir, layer_host = get_ngserver()

        ngviewer = openviewer(None)

        ngviewer2 = create_nglayer(ngviewer=ngviewer,
                                   layer_kws={'type': 'synapticclefts', 'ngspace': 'FAFB',
                                              'name': 'clefts_Heinrich_etal'})

        assert ngviewer2 == ngviewer

    def test_create_ngtreeneuronlist(self):
        """Check if create layer works in a tree neuronlist."""
        # load some example neurons..
        swc_path = os.path.join(BASE_DIR, 'data/swc')
        # print('swc_path: ', swc_path)
        swc_files = glob.glob(os.path.join(swc_path, '*.swc'))
        # print('swc_file: ', swc_files)

        neuronlist = []
        neuronlist += [navis.read_swc(f, units='8 nm', connector_labels={'presynapse': 7, 'postsynapse': 8},
                                      id=int(os.path.splitext(os.path.basename(f))[0])) for f in swc_files]

        neuronlist = navis.core.NeuronList(neuronlist)

        ngviewer = openviewer(None)

        ngviewer2 = create_nglayer(layer_kws={'type': 'skeletons', 'source': neuronlist, 'ngspace': 'FAFB',
                                              'color': ['white', 'green', 'grey', 'yellow', 'magenta'],
                                              'alpha': 0.9})

        assert ngviewer2 == ngviewer

    def test_create_ngpointslayer(self):
        """Check if the points layer is created."""
        layer_serverdir, layer_host = get_ngserver()

        ngviewer = openviewer(None)

        location_data = [{'x': 5, 'y': 10, 'z': 20}, {'x': 15, 'y': 25, 'z': 30}]

        points = pd.DataFrame(location_data)
        points['description'] = 'dummy data'

        ngviewer2 = create_nglayer(layer_kws={'type': 'points', 'name': 'points1', 'ngspace': 'FAFB',
                                              'source': points, 'scale': [8, 8, 8], 'color': 'yellow'})

        assert ngviewer2 == ngviewer

    def test_create_ngexceptionspacelayer(self):
        """Check exception is dimensions is not set."""
        layer_serverdir, layer_host = get_ngserver()

        location_data = [{'x': 5, 'y': 10, 'z': 20}, {'x': 15, 'y': 25, 'z': 30}]

        points = pd.DataFrame(location_data)
        points['description'] = 'dummy data'

        with pytest.raises(Exception):
            create_nglayer(layer_kws={'type': 'points', 'name': 'points1',
                                      'source': points, 'scale': [8, 8, 8], 'color': 'yellow'})

    def test_create_ngexceptionlayoutlayer(self):
        """Check exception is layout is not set."""
        layer_serverdir, layer_host = get_ngserver()

        location_data = [{'x': 5, 'y': 10, 'z': 20}, {'x': 15, 'y': 25, 'z': 30}]

        points = pd.DataFrame(location_data)
        points['description'] = 'dummy data'

        with pytest.raises(Exception):
            create_nglayer(layout='xy-nd', layer_kws={'type': 'points', 'name': 'points1',
                                                      'source': points, 'scale': [8, 8, 8], 'color': 'yellow'})

    def test_create_nghandledimensionslayer(self):
        """Check if the dimensions are handled."""
        dimensions = ng.CoordinateSpace(names=['x', 'y', 'z'], units='um', scales=[1, 1, 1])

        dimensions2 = _handle_ngdimensions(layer_kws={'dimensions': dimensions})

        assert dimensions2 == dimensions

    def test_create_ngvolumelayer(self):
        """Check if the volume layer is created."""
        layer_serverdir, layer_host = get_ngserver()

        ngviewer = openviewer(None)

        segid = 10
        vertices = [(0, 0, 0), (0, 1, 0), (0, 2, 0)]
        faces = [(0, 1, 2)]
        testvolume = navis.Volume(vertices=vertices, faces=faces, name='test', id=segid)

        ngviewer2 = create_nglayer(layer_kws={'type': 'volumes', 'source': testvolume, 'ngspace': 'FAFB',
                                              'color': 'white', 'alpha': 0.3})

        assert ngviewer2 == ngviewer


if __name__ == '__main__':

    unittest.main()
