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

"""Module contains functions to handle mesh data."""

from cloudvolume import CloudVolume
from cloudvolume import Mesh
import json
import navis
import numpy as np
import os


def _generate_mesh(x):
    """Generate mesh (of cloudvolume class) for given navis volume.

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
    """Generate mesh (of cloudvolume class) for given volume.

    Parameters
    ----------
    volume :             Navis Volume | List

    Returns
    -------
    mesh :      Cloud volume mesh
    """
    volumeidlist, volumedatasource, volumenamelist = []

    if not isinstance(x, list):
        x = [x]

    if all(isinstance(volume, navis.core.volumes.Volume) for volume in x):
        for volumeelement in x:
            volumedata = _generate_mesh(volumeelement)
            volumedata.segid = volumeelement.id
            volumedatasource.append(volumedata)
            volumeidlist.append(volumeelement.id)
            volumenamelist.append(volumeelement.name)

    return volumedatasource, volumeidlist, volumenamelist


def _to_precomputed(mesh):
    """Convert mesh to precomputed format."""
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
    cv.mesh.meta.info['segment_name_map'] = 'segment_names'
    cv.mesh.meta.info['segment_properties'] = 'segment_properties'
    cv.mesh.meta.commit_info()

    files = [os.path.join(cv.mesh.meta.mesh_path, str(vol.segid)) for vol in volumedatasource]
    volumeids = [str(vol.segid) for vol in volumedatasource]

    for fileidx in range(len(files)):
        fullfilepath = str(files[fileidx])  # files[fileidx]
        print(files[fileidx])
        fullfilepath = os.path.join(cv.basepath, os.path.basename(path), fullfilepath)
        uploadvol = Mesh(
            vertices=volumedatasource[fileidx].vertices, faces=volumedatasource[fileidx].faces,
            segid=None)
        precomputed_mesh = _to_precomputed(uploadvol)
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

    # create the file for segment_properties
    allvolproplist = {"id": "label",
                      "type": "label",
                      "values": volumenamelist}

    volinfo = {"@type": "neuroglancer_segment_properties",
               "inline": {"ids": list(map(str, volumeidlist)),
                          "properties": [allvolproplist]}}
    volfilepath = os.path.join(cv.basepath, os.path.basename(path), os.path.join(cv.mesh.meta.mesh_path),
                               'segment_properties')
    if not os.path.exists(volfilepath):
        os.makedirs(volfilepath)
        print('creating:', volfilepath)
    volinfofile = os.path.join(volfilepath, 'info')
    with open(volinfofile, 'w') as volinfofile:
        json.dump(volinfo, volinfofile)

    # create the file for segment_names
    volumenamedict = dict(zip(map(str, volumeidlist), volumenamelist))
    volnamemap = {"@type": "neuroglancer_segment_name_map",
                  "map": volumenamedict}
    volnamefilepath = os.path.join(cv.basepath, os.path.basename(path), os.path.join(cv.mesh.meta.mesh_path),
                                   'segment_names')
    if not os.path.exists(volnamefilepath):
        os.makedirs(volnamefilepath)
        print('creating:', volnamefilepath)
    volnamemapfile = os.path.join(volnamefilepath, 'info')
    with open(volnamemapfile, 'w') as volnamemapfile:
        json.dump(volnamemap, volnamemapfile)
