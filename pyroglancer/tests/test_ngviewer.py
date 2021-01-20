"""Module contains test cases for ngviewer.py module."""

import neuroglancer as ng
from pyroglancer.ngviewer import openviewer
import unittest


class Testngviewer(unittest.TestCase):
    """Test pyroglancer.ngviewer."""

    def test_newviewer(self):
        """Check if the viewer opens when no object is passed."""
        viewer = openviewer(None)

        assert isinstance(viewer, ng.viewer.Viewer)

    def test_reuseoldviewer(self):
        """Check if old viewer is reused incase of new opening request."""
        viewer1 = openviewer(None)
        viewer2 = openviewer(viewer1)

        assert viewer1 == viewer2


if __name__ == '__main__':
    unittest.main()
