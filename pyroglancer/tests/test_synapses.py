"""Module contains test cases for synapses.py module."""

import unittest
from pyroglancer.synapses import create_synapseinfo, put_synapsefile
from pyroglancer.layers import get_ngserver, _handle_ngdimensions
from pyroglancer.localserver import startdataserver, closedataserver
from pyroglancer.ngviewer import openviewer, closeviewer
import os
import pandas as pd


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


if __name__ == '__main__':
    unittest.main()
