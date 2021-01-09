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
import numpy as np
import json


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
        # segid = 0
        for volumeelement in x:
            volumedata = _generate_mesh(volumeelement)
            volumedata.segid = volumeelement.id
            volumedatasource.append(volumedata)
            volumeidlist.append(volumeelement.id)
            volumenamelist.append(volumeelement.name)
            # segid = segid+1

    return volumedatasource, volumeidlist, volumenamelist


def to_precomputed(mesh):

    vertex_index_format = [np.uint32(mesh.vertices.shape[0]),
                           mesh.vertices, mesh.faces]

    return b''.join([array.tobytes('C') for array in vertex_index_format])


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

    info = {"@type": "neuroglancer_legacy_mesh",
            'scales': [1, 1, 1],
            }
    path = 'file://' + path + '/precomputed'
    cv = CloudVolume(path, info=info)

    cv.mesh.meta.info['@type'] = 'neuroglancer_legacy_mesh'
    cv.mesh.meta.commit_info()

    files = [os.path.join(cv.mesh.meta.mesh_path, str(vol.segid)) for vol in volumedatasource]
    volumeids = [str(vol.segid) for vol in volumedatasource]

    for fileidx in range(len(files)):
        fullfilepath = str(files[fileidx])  # files[fileidx]
        fullfilepath = os.path.join(cv.basepath, os.path.basename(path), fullfilepath)
        uploadvol = Mesh(
            vertices=volumedatasource[fileidx].vertices, faces=volumedatasource[fileidx].faces,
            segid=None)
        precomputed_mesh = to_precomputed(uploadvol)
        print('Seg id is:', str(volumeids[fileidx]))
        print('Full filepath:', fullfilepath)
        with open(fullfilepath, 'wb') as f:
            f.write(precomputed_mesh)

        manifestinfo = {
            "fragments": [str(volumeids[fileidx])]}
        manifestfilepath = str(files[fileidx]) + ':' + str(0)  # files[fileidx]
        manifestfilepath = os.path.join(cv.basepath, os.path.basename(path), manifestfilepath)
        with open(manifestfilepath, 'w') as f:
            json.dump(manifestinfo, f)
