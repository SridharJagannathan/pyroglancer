"""Module contains test cases for skeleton.py module."""

import unittest
from pyroglancer.skeletons import to_ngskeletons, uploadskeletons
from pyroglancer.layers import get_ngserver
from pyroglancer.localserver import startdataserver, closedataserver
from pyroglancer.ngviewer import openviewer, closeviewer
import os
import navis
import pymaid
import glob
import pytest


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add a common viewer, dataserver(specific port for travis) for each test module..
closeviewer()
closedataserver()
startdataserver(port=8003)  # start dataserver..
ngviewer = openviewer(headless=True)  # open ngviewer


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


class Testskeleton(unittest.TestCase):
    """Test pyroglancer.skeleton."""

    # def setUp(self):
    #     """Perform set up."""
    #     super(Testsynapses, self).setUp()
    #
    # def tearDown(self):
    #     """Perform tearing down."""
    #     super(Testsynapses, self).tearDown()

    def test_upload_skeletontreeneuronlist(self):
        """Check if skeleton upload works in a tree neuronlist."""
        # load some example neurons..
        swc_path = os.path.join(BASE_DIR, 'data/swc')
        # print('swc_path: ', swc_path)
        swc_files = glob.glob(os.path.join(swc_path, '*.swc'))
        # print('swc_file: ', swc_files)

        neuronlist = []
        neuronlist += [navis.read_swc(f, units='8 nm', connector_labels={'presynapse': 7, 'postsynapse': 8},
                                      id=int(os.path.splitext(os.path.basename(f))[0])) for f in swc_files]

        neuronlist = navis.core.NeuronList(neuronlist)

        layer_serverdir, layer_host = get_ngserver()

        skelsource, skelseglist, skelsegnamelist = to_ngskeletons(neuronlist)
        uploadskeletons(skelsource, skelseglist, skelsegnamelist, layer_serverdir, 'catmaid_test')

        skeleton_path = os.path.join(
            layer_serverdir, 'precomputed/catmaid_test/skeletons/', str(neuronlist[0].id))
        # print('skel path: ', skeleton_path)

        status = os.path.isfile(skeleton_path)

        assert status

    def test_upload_skeletontreeneuron(self):
        """Check if skeleton upload works in a tree neuron."""
        # load some example neurons..
        swc_path = os.path.join(BASE_DIR, 'data/swc')
        # print('swc_path: ', swc_path)
        swc_files = glob.glob(os.path.join(swc_path, '*.swc'))
        # print('swc_file: ', swc_files)

        neuronlist = []
        neuronlist += [navis.read_swc(f, units='8 nm', connector_labels={'presynapse': 7, 'postsynapse': 8},
                                      id=int(os.path.splitext(os.path.basename(f))[0])) for f in swc_files]

        neuronlist = navis.core.NeuronList(neuronlist)
        treeneuron = neuronlist[0]

        layer_serverdir, layer_host = get_ngserver()

        skelsource, skelseglist, skelsegnamelist = to_ngskeletons(treeneuron)
        uploadskeletons(skelsource, skelseglist, skelsegnamelist, layer_serverdir, 'catmaid_test')

        skeleton_path = os.path.join(
            layer_serverdir, 'precomputed/catmaid_test/skeletons/', str(treeneuron.id))

        status = os.path.isfile(skeleton_path)

        assert status

    def test_upload_skeletoncatmaidneuronlist(self):
        """Check if skeleton upload works in a catmaid neuronlist."""
        # load some example neurons..
        swc_path = os.path.join(BASE_DIR, 'data/swc')
        # print('swc_path: ', swc_path)
        swc_files = glob.glob(os.path.join(swc_path, '*.swc'))
        # print('swc_file: ', swc_files)

        neuronlist = []
        neuronlist += [navis.read_swc(f, units='8 nm', connector_labels={'presynapse': 7, 'postsynapse': 8},
                                      id=int(os.path.splitext(os.path.basename(f))[0])) for f in swc_files]

        neuronlist = pymaid.core.CatmaidNeuronList(neuronlist)

        layer_serverdir, layer_host = get_ngserver()

        skelsource, skelseglist, skelsegnamelist = to_ngskeletons(neuronlist)
        uploadskeletons(skelsource, skelseglist, skelsegnamelist, layer_serverdir, 'catmaid_test')

        skeleton_path = os.path.join(
            layer_serverdir, 'precomputed/catmaid_test/skeletons/', str(neuronlist[0].id))

        status = os.path.isfile(skeleton_path)

        assert status

    def test_upload_skeletoncatmaidneuron(self):
        """Check if skeleton upload works in a catmaid neuron."""
        # load some example neurons..
        swc_path = os.path.join(BASE_DIR, 'data/swc')
        # print('swc_path: ', swc_path)
        swc_files = glob.glob(os.path.join(swc_path, '*.swc'))
        # print('swc_file: ', swc_files)

        neuronlist = []
        neuronlist += [navis.read_swc(f, units='8 nm', connector_labels={'presynapse': 7, 'postsynapse': 8},
                                      id=int(os.path.splitext(os.path.basename(f))[0])) for f in swc_files]

        catmaidneuron = pymaid.core.CatmaidNeuron(neuronlist[0])
        catmaidneuron.soma = None  # set this so you don't have to fetch from remote instance

        layer_serverdir, layer_host = get_ngserver()

        skelsource, skelseglist, skelsegnamelist = to_ngskeletons(catmaidneuron)
        uploadskeletons(skelsource, skelseglist, skelsegnamelist, layer_serverdir, 'catmaid_test')

        skeleton_path = os.path.join(
            layer_serverdir, 'precomputed/catmaid_test/skeletons/', str(catmaidneuron.id))

        status = os.path.isfile(skeleton_path)

        assert status

    def test_upload_skeletonexception(self):
        """Check if exception occurs."""
        neuronlist = (1, 2, 3)

        layer_serverdir, layer_host = get_ngserver()

        with pytest.raises(Exception):
            skelsource, skelseglist, skelsegnamelist = to_ngskeletons(neuronlist)


if __name__ == '__main__':

    unittest.main()
