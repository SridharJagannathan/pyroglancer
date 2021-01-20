"""Module contains test cases for spaces.py module."""

import unittest
from pyroglancer.spaces import create_ngspace
from pyroglancer.layers import get_ngserver
from pyroglancer.localserver import startdataserver, closedataserver
from pyroglancer.ngviewer import openviewer, closeviewer
from pyroglancer.createconfig import createconfig
import sys


# create configuration file..
createconfig()

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
    """Test pyroglancer.spaces."""

    # def setUp(self):
    #     """Perform set up."""
    #     super(Testsynapses, self).setUp()
    #
    # def tearDown(self):
    #     """Perform tearing down."""
    #     super(Testsynapses, self).tearDown()

    def test_create_fafbspace(self):
        """Check if the fafb space is created."""
        layer_serverdir, layer_host = get_ngserver()

        create_ngspace(space='FAFB')

        space = sys.modules['ngspace']

        assert space == 'FAFB'

    def test_create_fancspace(self):
        """Check if the hemibrain space is created."""
        layer_serverdir, layer_host = get_ngserver()

        create_ngspace(space='hemibrain')

        space = sys.modules['ngspace']

        assert space == 'hemibrain'


if __name__ == '__main__':

    unittest.main()
