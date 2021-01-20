"""Module contains test cases for utils.py module."""

import unittest
from pyroglancer.utils import get_hexcolor, get_alphavalue


class Testutils(unittest.TestCase):
    """Test pyroglancer.utils."""

    def test_hexcolor(self):
        """Check if the hex colors are returned."""
        layer_kws = {}
        layer_kws['color'] = 'yellow'
        hexcolor = get_hexcolor(layer_kws)

        assert hexcolor[0] == '#ffff00'

    def test_defaulthexcolor(self):
        """Check if the hex colors are returned."""
        layer_kws = {}
        hexcolor = get_hexcolor(layer_kws)

        assert hexcolor[0] == '#ffff00'

    def test_customhexcolor(self):
        """Check if the hex colors are returned."""
        layer_kws = {}
        layer_kws['color'] = 'red'
        hexcolor = get_hexcolor(layer_kws)

        assert hexcolor[0] == '#ff0000'

    def test_alphavalue(self):
        """Check if the alpha values are returned."""
        layer_kws = {}
        layer_kws['alpha'] = 0.9
        alphavalue = get_alphavalue(layer_kws)

        assert alphavalue == 0.9

    def test_defaultalphavalue(self):
        """Check if the alpha values are returned."""
        layer_kws = {}
        alphavalue = get_alphavalue(layer_kws)

        assert alphavalue == 1.0


if __name__ == '__main__':
    unittest.main()
