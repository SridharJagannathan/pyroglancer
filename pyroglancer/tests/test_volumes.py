"""Module contains test cases for volumes.py module."""

import unittest
from pyroglancer.volumes import uploadmeshes, to_ngmesh
from pyroglancer.layers import get_ngserver
from pyroglancer.localserver import startdataserver, closedataserver
from pyroglancer.ngviewer import openviewer, closeviewer
import navis
import os
import sys


class Testvolumes(unittest.TestCase):
    """Test pyroglancer.volumes."""

    def test_convertmesh(self):
        """Check if the meshconversion is done."""
        segid = 10
        vertices = [(0, 0, 0), (0, 1, 0), (0, 2, 0)]
        faces = [(0, 1, 2)]
        testvolume = navis.Volume(vertices=vertices, faces=faces, name='test', id=segid)

        volumedatasource, volumeidlist, volumenamelist = to_ngmesh(testvolume)

        assert volumeidlist[0] == 10

    def test_meshupload(self):
        """Check if the meshupload is done."""
        segid = 10
        vertices = [(0, 0, 0), (0, 1, 0), (0, 2, 0)]
        faces = [(0, 1, 2)]
        testvolume = navis.Volume(vertices=vertices, faces=faces, name='test', id=segid)

        volumedatasource, volumeidlist, volumenamelist = to_ngmesh(testvolume)
        # segmentColors = dict(zip(volumeidlist, '#ffff00'))
        closeviewer()
        closedataserver()
        startdataserver()  # start dataserver..
        openviewer()  # open ngviewer

        layer_serverdir, layer_host = get_ngserver()
        uploadmeshes(volumedatasource, volumeidlist, volumenamelist, layer_serverdir)

        status = os.path.exists(os.path.join(layer_serverdir, 'precomputed/mesh', str(segid)))

        assert status


if __name__ == '__main__':
    unittest.main()
