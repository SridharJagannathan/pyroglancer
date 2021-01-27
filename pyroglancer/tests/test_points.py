"""Module contains test cases for points.py module."""

import unittest
from pyroglancer.points import create_pointinfo, upload_points, annotate_points
from pyroglancer.layers import get_ngserver, _handle_ngdimensions
from pyroglancer.localserver import startdataserver, closedataserver
from pyroglancer.ngviewer import openviewer, closeviewer
import os
import pandas as pd


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add a common viewer, dataserver(specific port for travis) for each test module..
closeviewer()
closedataserver()
startdataserver(port=8004)  # start dataserver..
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


class Testpoints(unittest.TestCase):
    """Test pyroglancer.points."""

    # def setUp(self):
    #     """Perform set up."""
    #     super(Testsynapses, self).setUp()
    #
    # def tearDown(self):
    #     """Perform tearing down."""
    #     super(Testsynapses, self).tearDown()

    def test_create_pointinfo(self):
        """Check if the point info is stored."""
        layer_serverdir, layer_host = get_ngserver()

        layer_kws = {}
        layer_kws['ngspace'] = 'FAFB'
        dimensions = _handle_ngdimensions(layer_kws)
        create_pointinfo(dimensions, layer_serverdir, 'points')

        status = os.path.isfile(os.path.join(
            layer_serverdir, 'precomputed/points', 'info'))

        assert status

    def test_put_pointfile(self):
        """Check if the point file is stored."""
        layer_serverdir, layer_host = get_ngserver()

        layer_kws = {}
        layer_kws['ngspace'] = 'FAFB'
        dimensions = _handle_ngdimensions(layer_kws)
        layer_name = 'points'
        points_path = create_pointinfo(dimensions, layer_serverdir, layer_name)

        location_data = [{'x': 5, 'y': 10, 'z': 20}, {'x': 15, 'y': 25, 'z': 30}]

        points = pd.DataFrame(location_data)
        points['description'] = 'dummy data'

        upload_points(points, points_path, 'points', [1, 1, 1])

        pointfilepath = points_path + '/precomputed/' + layer_name + '/spatial0/0_0_0'

        status = os.path.isfile(pointfilepath)

        assert status

    def test_annotate_annotate_points(self):
        """Check if individual annotation works."""
        layer_serverdir, layer_host = get_ngserver()

        layer_kws = {}
        layer_kws['ngspace'] = 'FAFB'
        dimensions = _handle_ngdimensions(layer_kws)

        location_data = [{'x': 5, 'y': 10, 'z': 20}, {'x': 15, 'y': 25, 'z': 30}]

        points = pd.DataFrame(location_data)
        points['description'] = 'dummy data'

        ngviewer = openviewer(None)
        layer_scale = (1, 1, 1)
        annot_colors = '#ff0000'

        status = annotate_points(ngviewer, dimensions, annot_colors, points, 'points', layer_scale)

        assert status


if __name__ == '__main__':

    unittest.main()
