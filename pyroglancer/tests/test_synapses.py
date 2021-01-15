"""Module contains test cases for synapses.py module."""

import unittest
from pyroglancer.synapses import create_synapseinfo, put_synapsefile
from pyroglancer.layers import get_ngserver, _handle_ngdimensions
from pyroglancer.localserver import startdataserver, closedataserver
from pyroglancer.ngviewer import openviewer, closeviewer
from pyroglancer.layers import create_nglayer
import os
import pandas as pd
import navis
import glob


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Testsynapses(unittest.TestCase):
    """Test pyroglancer.synapses."""

    def test_create_synapseinfo(self):
        """Check if the synapse info is stored."""
        closeviewer()
        closedataserver()
        startdataserver()  # start dataserver..
        openviewer()  # open ngviewer

        layer_serverdir, layer_host = get_ngserver()

        layer_kws = {}
        layer_kws['space'] = 'FAFB'
        dimensions = _handle_ngdimensions(layer_kws)
        create_synapseinfo(dimensions, layer_serverdir)

        status = os.path.isfile(os.path.join(
            layer_serverdir, 'precomputed/presynapses', 'info'))

        assert status

    def test_put_presynapsefile(self):
        """Check if the synapse file is stored."""
        closeviewer()
        closedataserver()
        startdataserver()  # start dataserver..
        openviewer()  # open ngviewer

        layer_serverdir, layer_host = get_ngserver()

        layer_kws = {}
        layer_kws['space'] = 'FAFB'
        dimensions = _handle_ngdimensions(layer_kws)
        synapse_path = create_synapseinfo(dimensions, layer_serverdir)

        location_data = [{'x': 5, 'y': 10, 'z': 20}, {'x': 15, 'y': 25, 'z': 30}]

        presynapses = pd.DataFrame(location_data)

        skeletonid = 123
        type = 'presynapses'

        put_synapsefile(synapse_path, type, presynapses, skeletonid)

        synapsefilepath = synapse_path + '/precomputed/' + \
            type + '/' + type + '_cell/' + str(skeletonid)

        status = os.path.isfile(synapsefilepath)

        assert status

    def test_put_postsynapsefile(self):
        """Check if the synapse file is stored."""
        closeviewer()
        closedataserver()
        startdataserver()  # start dataserver..
        openviewer()  # open ngviewer

        layer_serverdir, layer_host = get_ngserver()

        layer_kws = {}
        layer_kws['space'] = 'FAFB'
        dimensions = _handle_ngdimensions(layer_kws)
        synapse_path = create_synapseinfo(dimensions, layer_serverdir)

        location_data = [{'x': 5, 'y': 10, 'z': 20}, {'x': 15, 'y': 25, 'z': 30}]

        presynapses = pd.DataFrame(location_data)

        skeletonid = 456
        type = 'postsynapses'

        put_synapsefile(synapse_path, type, presynapses, skeletonid)

        synapsefilepath = synapse_path + '/precomputed/' + \
            type + '/' + type + '_cell/' + str(skeletonid)

        status = os.path.isfile(synapsefilepath)

        assert status

    def test_upload_synapses(self):
        """Check if synapse upload works in a neuron or neuronlist."""
        closeviewer()
        closedataserver()
        startdataserver()  # start dataserver..
        openviewer()  # open ngviewer

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
        layer_kws['space'] = 'FAFB'
        dimensions = _handle_ngdimensions(layer_kws)
        synapse_path = create_synapseinfo(dimensions, layer_serverdir)

        presynlayer_kws = {'type': 'synapses', 'space': 'FAFB',
                           'source': neuronlist}

        create_nglayer(layer_kws=presynlayer_kws)
        type = 'presynapses'
        synapsefilepath = synapse_path + '/precomputed/' +\
            type + '/' + type + '_cell/' + str(neuronlist[0].id)

        status = os.path.isfile(synapsefilepath)

        assert status


if __name__ == '__main__':
    unittest.main()
