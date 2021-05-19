"""Module contains test cases for synapses.py module."""

import unittest
from pyroglancer.synapses import create_synapseinfo, put_synapsefile, annotate_synapses
from pyroglancer.layers import get_ngserver, _handle_ngdimensions
from pyroglancer.localserver import startdataserver, closedataserver
from pyroglancer.ngviewer import openviewer, closeviewer
from pyroglancer.layers import create_nglayer
import os
import pandas as pd
import navis
import pymaid
import glob
import pytest


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add a common viewer, dataserver(specific port for travis) for each test module..
closeviewer()
closedataserver()
startdataserver(port=8001)  # start dataserver..
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


class Testsynapses(unittest.TestCase):
    """Test pyroglancer.synapses."""

    # def setUp(self):
    #     """Perform set up."""
    #     super(Testsynapses, self).setUp()
    #
    # def tearDown(self):
    #     """Perform tearing down."""
    #     super(Testsynapses, self).tearDown()

    def test_create_synapseinfo(self):
        """Check if the synapse info is stored."""
        layer_serverdir, layer_host = get_ngserver()

        layer_kws = {}
        layer_kws['ngspace'] = 'FAFB'
        dimensions = _handle_ngdimensions(layer_kws)
        create_synapseinfo(dimensions, layer_serverdir)

        status = os.path.isfile(os.path.join(
            layer_serverdir, 'presynapses', 'info'))

        assert status

    def test_put_presynapsefile(self):
        """Check if the synapse file is stored."""
        layer_serverdir, layer_host = get_ngserver()

        layer_kws = {}
        layer_kws['ngspace'] = 'FAFB'
        dimensions = _handle_ngdimensions(layer_kws)
        synapse_path = create_synapseinfo(dimensions, layer_serverdir)

        location_data = [{'x': 5, 'y': 10, 'z': 20}, {'x': 15, 'y': 25, 'z': 30}]

        presynapses = pd.DataFrame(location_data)

        skeletonid = 123
        type = 'presynapses'

        put_synapsefile(synapse_path, type, presynapses, skeletonid)

        synapsefilepath = synapse_path + '/' + type + '/' + type + '_cell/' + str(skeletonid)

        status = os.path.isfile(synapsefilepath)

        assert status

    def test_put_postsynapsefile(self):
        """Check if the synapse file is stored."""
        layer_serverdir, layer_host = get_ngserver()

        layer_kws = {}
        layer_kws['ngspace'] = 'FAFB'
        dimensions = _handle_ngdimensions(layer_kws)
        synapse_path = create_synapseinfo(dimensions, layer_serverdir)

        location_data = [{'x': 5, 'y': 10, 'z': 20}, {'x': 15, 'y': 25, 'z': 30}]

        presynapses = pd.DataFrame(location_data)

        skeletonid = 456
        type = 'postsynapses'

        put_synapsefile(synapse_path, type, presynapses, skeletonid)

        synapsefilepath = synapse_path + '/' + type + '/' + type + '_cell/' + str(skeletonid)

        status = os.path.isfile(synapsefilepath)

        assert status

    def test_upload_synapsestreeneuronlist(self):
        """Check if synapse upload works in a tree neuronlist."""
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

        layer_kws = {}
        layer_kws['ngspace'] = 'FAFB'
        dimensions = _handle_ngdimensions(layer_kws)
        synapse_path = create_synapseinfo(dimensions, layer_serverdir)

        presynlayer_kws = {'type': 'synapses', 'ngspace': 'FAFB',
                           'linked_layername': 'test_neurons',
                           'source': neuronlist}

        create_nglayer(layer_kws=presynlayer_kws)
        type = 'presynapses'
        synapsefilepath = synapse_path + '/precomputed/' + 'test_neurons/' + \
            type + '/' + type + '_cell/' + str(neuronlist[0].id)

        status = os.path.isfile(synapsefilepath)

        assert status

    def test_upload_synapsestreeneuron(self):
        """Check if synapse upload works in a tree neuron."""
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

        layer_kws = {}
        layer_kws['ngspace'] = 'FAFB'
        dimensions = _handle_ngdimensions(layer_kws)
        synapse_path = create_synapseinfo(dimensions, layer_serverdir)

        presynlayer_kws = {'type': 'synapses', 'ngspace': 'FAFB',
                           'linked_layername': 'test_neurons',
                           'source': neuronlist[0]}

        create_nglayer(layer_kws=presynlayer_kws)
        type = 'presynapses'
        synapsefilepath = synapse_path + '/precomputed/' + 'test_neurons/' + \
            type + '/' + type + '_cell/' + str(neuronlist[0].id)

        status = os.path.isfile(synapsefilepath)

        assert status

    def test_upload_synapsesexception(self):
        """Check if exception occurs."""
        neuronlist = (1, 2, 3)

        layer_serverdir, layer_host = get_ngserver()

        presynlayer_kws = {'type': 'synapses', 'ngspace': 'FAFB',
                           'source': neuronlist}

        with pytest.raises(Exception):
            create_nglayer(layer_kws=presynlayer_kws)

    def test_upload_synapsescatmaidneuronlist(self):
        """Check if synapse upload works in a tree neuronlist."""
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

        layer_kws = {}
        layer_kws['ngspace'] = 'FAFB'
        dimensions = _handle_ngdimensions(layer_kws)
        synapse_path = create_synapseinfo(dimensions, layer_serverdir)

        presynlayer_kws = {'type': 'synapses', 'ngspace': 'FAFB',
                           'linked_layername': 'test_neurons',
                           'source': neuronlist}

        create_nglayer(layer_kws=presynlayer_kws)
        type = 'presynapses'
        synapsefilepath = synapse_path + '/precomputed/' + 'test_neurons/' + \
            type + '/' + type + '_cell/' + str(neuronlist[0].id)

        status = os.path.isfile(synapsefilepath)

        assert status

    def test_upload_synapsescatmaidneuron(self):
        """Check if synapse upload works in a tree neuronlist."""
        # load some example neurons..
        swc_path = os.path.join(BASE_DIR, 'data/swc')
        # print('swc_path: ', swc_path)
        swc_files = glob.glob(os.path.join(swc_path, '*.swc'))
        # print('swc_file: ', swc_files)

        neuronlist = []
        neuronlist += [navis.read_swc(f, units='8 nm', connector_labels={'presynapse': 7, 'postsynapse': 8},
                                      id=int(os.path.splitext(os.path.basename(f))[0])) for f in swc_files]

        catmaidneuron = pymaid.core.CatmaidNeuron(neuronlist[0])

        layer_serverdir, layer_host = get_ngserver()

        layer_kws = {}
        layer_kws['ngspace'] = 'FAFB'
        dimensions = _handle_ngdimensions(layer_kws)
        synapse_path = create_synapseinfo(dimensions, layer_serverdir)

        presynlayer_kws = {'type': 'synapses', 'ngspace': 'FAFB',
                           'linked_layername': 'test_neurons',
                           'source': catmaidneuron}

        create_nglayer(layer_kws=presynlayer_kws)
        type = 'presynapses'
        synapsefilepath = synapse_path + '/precomputed/' + 'test_neurons/' + \
            type + '/' + type + '_cell/' + str(catmaidneuron.id)

        status = os.path.isfile(synapsefilepath)

        assert status

    def test_annotate_synapsestreeneuronlist(self):
        """Check if individual annotation works."""
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
        layer_kws = {}
        layer_kws['ngspace'] = 'FAFB'
        dimensions = _handle_ngdimensions(layer_kws)

        status = annotate_synapses(ngviewer, dimensions, neuronlist)

        assert status

    def test_annotate_synapsestreeneuron(self):
        """Check if individual annotation works."""
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
        layer_kws = {}
        layer_kws['ngspace'] = 'FAFB'
        dimensions = _handle_ngdimensions(layer_kws)

        status = annotate_synapses(ngviewer, dimensions, neuronlist[0])

        assert status

    def test_annotate_synapsescatmaidneuron(self):
        """Check if individual annotation works."""
        # load some example neurons..
        swc_path = os.path.join(BASE_DIR, 'data/swc')
        # print('swc_path: ', swc_path)
        swc_files = glob.glob(os.path.join(swc_path, '*.swc'))
        # print('swc_file: ', swc_files)

        neuronlist = []
        neuronlist += [navis.read_swc(f, units='8 nm', connector_labels={'presynapse': 7, 'postsynapse': 8},
                                      id=int(os.path.splitext(os.path.basename(f))[0])) for f in swc_files]

        catmaidneuron = pymaid.core.CatmaidNeuron(neuronlist[0])

        ngviewer = openviewer(None)
        layer_kws = {}
        layer_kws['ngspace'] = 'FAFB'
        dimensions = _handle_ngdimensions(layer_kws)

        status = annotate_synapses(ngviewer, dimensions, catmaidneuron)

        assert status

    def test_annotate_synapsesexception(self):
        """Check if exception occurs."""
        neuronlist = (1, 2, 3)

        layer_serverdir, layer_host = get_ngserver()

        ngviewer = openviewer(None)
        layer_kws = {}
        layer_kws['ngspace'] = 'FAFB'
        dimensions = _handle_ngdimensions(layer_kws)

        with pytest.raises(Exception):
            annotate_synapses(ngviewer, dimensions, neuronlist)


if __name__ == '__main__':

    unittest.main()
