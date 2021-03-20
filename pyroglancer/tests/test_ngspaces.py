"""Module contains test cases for ngspaces.py module."""

import sys
import unittest

from pyroglancer.layers import get_ngserver
from pyroglancer.localserver import closedataserver
from pyroglancer.localserver import startdataserver
from pyroglancer.ngspaces import create_ngspace
from pyroglancer.ngviewer import closeviewer
from pyroglancer.ngviewer import openviewer

# Add a common viewer, dataserver(specific port for travis) for each test module..
closeviewer()
closedataserver()
startdataserver(port=8005)  # start dataserver..
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


class Testspaces(unittest.TestCase):
    """Test pyroglancer.ngspaces."""

    # def setUp(self):
    #     """Perform set up."""
    #     super(Testsynapses, self).setUp()
    #
    # def tearDown(self):
    #     """Perform tearing down."""
    #     super(Testsynapses, self).tearDown()

    def test_create_fafbspace(self):
        """Check if the fafb ngspace is created."""
        layer_serverdir, layer_host = get_ngserver()
        layer_kws = {'ngspace': 'FAFB'}
        create_ngspace(layer_kws)

        ngspace = sys.modules['ngspace']

        assert ngspace == 'FAFB'

    def test_create_fancspace(self):
        """Check if the hemibrain space is created."""
        layer_serverdir, layer_host = get_ngserver()
        layer_kws = {'ngspace': 'hemibrain'}
        create_ngspace(layer_kws)

        ngspace = sys.modules['ngspace']

        assert ngspace == 'hemibrain'


if __name__ == '__main__':

    unittest.main()
