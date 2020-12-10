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
from cloudvolume import CloudVolume, Mesh
import os


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
    if not isinstance(x, list):
        x = [x]

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


def uploadmeshes(volumedatasource, volumeidlist, volumenamelist, path):
    """Upload mesh (of cloudvolume class) to a local server.



    Parameters
    ----------
    volumedatasource :     List containing cloud volume meshes
    volumeidlist :    List containing the segids(volume id)
    volumenamelist :   List containing the names of volumes
    path :           path to the local data server

    Returns
    -------
    cv :     cloudvolume class object
    """
    # info = {"@type": "neuroglancer_multilod_draco",
    #         "spatial_index": None,
    #         'scales': [1, 1, 1],
    #         'lod_scale_multiplier': 1.0}
    info = {"@type": "neuroglancer_legacy_mesh",
            'scales': [1, 1, 1],
            }
    path = 'file://' + path + '/precomputed'
    cv = CloudVolume(path, info=info)

    # # prepare for info file
    # cv.mesh.meta.info['@type'] = 'neuroglancer_multilod_draco'
    # cv.mesh.meta.info['vertex_quantization_bits'] = 16
    # cv.mesh.meta.info['scales'] = [1, 1, 1]
    # cv.mesh.meta.info['lod_scale_multiplier'] = 1.0

    cv.mesh.meta.info['@type'] = 'neuroglancer_legacy_mesh'
    cv.mesh.meta.commit_info()

    files = [os.path.join(cv.mesh.meta.mesh_path, str(vol.segid)) for vol in volumedatasource]

    for fileidx in range(len(files)):
        fullfilepath = files[fileidx]
        fullfilepath = os.path.join(cv.basepath, os.path.basename(path), fullfilepath)
        uploadvol = Mesh(
            vertices=volumedatasource[fileidx].vertices/1000, faces=volumedatasource[fileidx].faces)
        # ,segid=volumedatasource[fileidx].segid)
        print(fullfilepath)
        with open(fullfilepath, 'wb') as f:
            f.write(uploadvol.to_precomputed())
