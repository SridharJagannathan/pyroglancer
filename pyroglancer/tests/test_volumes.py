"""Module contains test cases for volumes.py module."""

import unittest
from pyroglancer.volumes import uploadmeshes, to_ngmesh
import navis


class Testvolumes(unittest.TestCase):
    """Test pyroglancer.volumes."""

    def test_meshupload(self):
        """Check if the meshupload is done."""
        segid = 10
        vertices = [(0, 0, 0), (0, 1, 0), (0, 2, 0)]
        faces = [(0, 1, 2)]
        testvolume = navis.Volume(vertices=vertices, faces=faces, name='test', id=segid)

        volumedatasource, volumeidlist, volumenamelist = to_ngmesh(testvolume)

        assert volumeidlist[0] == 10


if __name__ == '__main__':
    unittest.main()
