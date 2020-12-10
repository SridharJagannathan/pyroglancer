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

""" Module contains functions to handle mesh data.
"""
import navis
from cloudvolume import Mesh


def _generate_mesh(x):
    """

    Generate mesh (of cloudvolume class) for given navis volume.

    Parameters
    ----------
    x :             Navis Volume

    Returns
    -------
    mesh :      Cloud volume mesh
    """

    mesh = Mesh(segid=x.id, vertices=x.vertices, faces=x.faces)

    return mesh


def to_ngmesh(x):
    """

    Generate mesh (of cloudvolume class) for given volume.

    Parameters
    ----------
    volume :             Navis Volume | List

    Returns
    -------
    mesh :      Cloud volume mesh
    """
    if isinstance(x, list):
        if all(isinstance(volume, navis.core.volumes.Volume) for volume in x):
            volumeidlist = []
            volumedatasource = []
            volumenamelist = []
            for volumeelement in x:
                volumedata = _generate_mesh(volumeelement)
                volumedatasource.append(volumedata)
                volumeidlist.append(volumeelement.id)
                volumenamelist.append(volumeelement.name)

    return volumedatasource, volumeidlist, volumenamelist
