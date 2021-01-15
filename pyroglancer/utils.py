#    This script is part of pyroglancer (https://github.com/SridharJagannathan/pyroglancer).
#    Copyright (C) 2020 Sridhar Jagannathan
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

"""Module contains utility functions."""
import webcolors


def get_hexcolor(layer_kws):
    """Convert text based color to hex value."""
    # This function converts css color text to hex based.
    if 'color' in layer_kws:
        layer_color = layer_kws['color']
    else:
        layer_color = 'yellow'
    rawcolorlist = layer_color

    if not isinstance(rawcolorlist, list):
        rawcolorlist = (rawcolorlist,)

    hexcolorlist = []
    for hexcolor in rawcolorlist:
        if not hexcolor.startswith("#"):
            hexcolor = webcolors.name_to_hex(hexcolor)
        hexcolorlist.append(hexcolor)
    return hexcolorlist


def get_alphavalue(layer_kws):
    """Get alpha values from the interface APIs."""
    # This function gets alpha/transparency values.
    if 'alpha' in layer_kws:
        layer_alpha = layer_kws['alpha']
    else:
        layer_alpha = 1.0
    return layer_alpha
