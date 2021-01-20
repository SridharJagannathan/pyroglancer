"""Module contains test cases for ngspaces.py module."""

import unittest
from pyroglancer.ngspaces import create_ngspace
from pyroglancer.layers import get_ngserver
from pyroglancer.localserver import startdataserver, closedataserver
from pyroglancer.ngviewer import openviewer, closeviewer
import sys


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

        create_ngspace(ngspace='FAFB')

        ngspace = sys.modules['ngspace']

        assert ngspace == 'FAFB'

    def test_create_fancspace(self):
        """Check if the hemibrain space is created."""
        layer_serverdir, layer_host = get_ngserver()

        create_ngspace(ngspace='hemibrain')

        ngspace = sys.modules['ngspace']

        assert ngspace == 'hemibrain'


if __name__ == '__main__':

    unittest.main()
