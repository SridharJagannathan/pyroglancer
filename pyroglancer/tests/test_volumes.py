"""Module contains test cases for volumes.py module."""

import unittest
from pyroglancer.volumes import uploadsingleresmeshes, to_ngmesh
from pyroglancer.layers import get_ngserver
from pyroglancer.localserver import startdataserver, closedataserver
from pyroglancer.ngviewer import openviewer, closeviewer
import navis
import os

# Add a common viewer, dataserver(specific port for travis) for each test module..
closeviewer()
closedataserver()
startdataserver(port=8002)  # start dataserver..
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


class Testvolumes(unittest.TestCase):
    """Test pyroglancer.volumes."""

    # def setUp(self):
    #     """Perform set up."""
    #     super(Testvolumes, self).setUp()
    #
    # def tearDown(self):
    #     """Perform tearing down."""
    #     super(Testvolumes, self).tearDown()

    def test_convertmesh(self):
        """Check if the meshconversion is done."""
        segid = 10
        vertices = [(0, 0, 0), (0, 1, 0), (0, 2, 0)]
        faces = [(0, 1, 2)]
        testvolume = navis.Volume(vertices=vertices, faces=faces, name='test', id=segid)

        volumedatasource, volumeidlist, volumenamelist = to_ngmesh(testvolume)

        assert volumeidlist[0] == '10'

    def test_meshupload(self):
        """Check if the meshupload is done."""
        segid = 10
        vertices = [(0, 0, 0), (0, 1, 0), (0, 2, 0)]
        faces = [(0, 1, 2)]
        testvolume = navis.Volume(vertices=vertices, faces=faces, name='test', id=segid)

        volumedatasource, volumeidlist, volumenamelist = to_ngmesh(testvolume)
        # segmentColors = dict(zip(volumeidlist, '#ffff00'))

        layer_serverdir, layer_host = get_ngserver()
        uploadsingleresmeshes(volumedatasource, volumeidlist, volumenamelist, layer_serverdir, 'testvolume')

        status = os.path.exists(os.path.join(layer_serverdir, 'precomputed/testvolume/mesh', str(segid)))

        assert status


if __name__ == '__main__':

    unittest.main()
