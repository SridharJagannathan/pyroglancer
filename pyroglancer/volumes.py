#    This script is part of pyroglancer (https://github.com/SridharJagannathan/pyroglancer).
#    The code for multi-resolution meshes was adapted using the solutions provided in the discussion at
#    https://github.com/google/neuroglancer/issues/272
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
import struct
import trimesh
from pyroglancer.meshgenerator import decompose_meshes
from io import BytesIO
from cloudvolume.datasource.precomputed.sharding import ShardingSpecification


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
    volume :  Navis Volume | Navis mesh neuron | List
      volume or volumelist of different formats

    Returns
    -------
    volumedatasource:  list
        contains volumes of cloud volume class.
    volumeidlist:  list
        contains the volume ids.
    volumenamelist:  list
        contains the names of volumes.
    """
    volumeidlist, volumedatasource, volumenamelist = ([] for i in range(3))

    if isinstance(x, navis.core.volumes.Volume):
        x = [x]  # if a simple volume, convert to list..

    if all(isinstance(meshneuron, navis.core.MeshNeuron) for meshneuron in x):
        for neuronelement in x:
            volumedata = _generate_mesh(neuronelement)
            volumedata.segid = neuronelement.id
            volumedatasource.append(volumedata)
            volumeidlist.append(neuronelement.id)
            volumenamelist.append(neuronelement.name)
    if all(isinstance(volume, navis.core.volumes.Volume) for volume in x):
        for volumeelement in x:
            volumedata = _generate_mesh(volumeelement)
            volumedata.segid = volumeelement.id
            volumedatasource.append(volumedata)
            volumeidlist.append(volumeelement.id)
            volumenamelist.append(volumeelement.name)

    volumeidlist = list(map(str, volumeidlist))
    volumenamelist = list(map(str, volumenamelist))

    return volumedatasource, volumeidlist, volumenamelist


def _to_precomputed(mesh):
    """Convert mesh to precomputed format."""
    vertex_index_format = [np.uint32(mesh.vertices.shape[0]),
                           mesh.vertices, mesh.faces]

    return b''.join([array.tobytes('C') for array in vertex_index_format])


def _to_multires_precomputed(vertices, faces, quant_bits, meshpath):
    """Convert mesh to multi resolution precomputed format and save them."""

    # start with some settings..
    quantization_bits = quant_bits
    lods = np.array([0, 1, 2])  # number of level of details, keep 3 for now..
    # set the chunk shape, grid origin acc to vertex data, so there is no need for offsets later on..
    chunk_shape = (vertices.max(axis=0) - vertices.min(axis=0))/2**lods.max()
    grid_origin = vertices.min(axis=0)
    lod_scales = np.array([2**lod for lod in lods])
    num_lods = len(lod_scales)
    vertex_offsets = np.array([[0., 0., 0.] for _ in range(num_lods)])

    fragment_offsets = []
    fragment_positions = []

    # write the mesh fragment data file first..
    with open(meshpath, 'wb') as f:
        # for each level now decompose the mesh into submeshes with lower resolution..
        for scale in lod_scales[::-1]:
            # start with lod-0, which is the highest resolution possible..
            lod_offsets = []
            nodes, submeshes = decompose_meshes(vertices.copy(), faces.copy(), scale, quantization_bits)
            # convert each submesh into google draco format and append them..
            for mesh in submeshes:
                draco = trimesh.exchange.ply.export_draco(mesh, bits=quant_bits)
                f.write(draco)
                lod_offsets.append(len(draco))

            fragment_positions.append(np.array(nodes))
            fragment_offsets.append(np.array(lod_offsets))

    num_fragments_per_lod = np.array([len(nodes) for nodes in fragment_positions])

    # write the mesh manifest file now..
    manifestfilepath = meshpath + '.index'
    with open(manifestfilepath, 'wb') as f:
        f.write(chunk_shape.astype('<f').tobytes())
        f.write(grid_origin.astype('<f').tobytes())
        f.write(struct.pack('<I', num_lods))
        f.write(lod_scales.astype('<f').tobytes())
        f.write(vertex_offsets.astype('<f').tobytes(order='C'))
        f.write(num_fragments_per_lod.astype('<I').tobytes())
        for frag_pos, frag_offset in zip(fragment_positions, fragment_offsets):
            f.write(frag_pos.T.astype('<I').tobytes(order='C'))
            f.write(frag_offset.astype('<I').tobytes(order='C'))


def _to_multires_shardedprecomputed(vertices, faces, quant_bits):
    """Convert mesh to multi resolution precomputed format and return them for shards."""

    # start with some settings..
    quantization_bits = quant_bits
    lods = np.array([0, 1, 2])  # number of level of details, keep 3 for now..
    # set the chunk shape, grid origin acc to vertex data, so there is no need for offsets later on..
    chunk_shape = (vertices.max(axis=0) - vertices.min(axis=0))/2**lods.max()
    grid_origin = vertices.min(axis=0)
    lod_scales = np.array([2**lod for lod in lods])
    num_lods = len(lod_scales)
    vertex_offsets = np.array([[0., 0., 0.] for _ in range(num_lods)])

    fragment_offsets = []
    fragment_positions = []

    manifestdata = BytesIO()
    fragmentdata = BytesIO()
    combineddata = BytesIO()

    # write the mesh fragment data file first..
    # for each level now decompose the mesh into submeshes with lower resolution..
    for scale in lod_scales[::-1]:
        # start with lod-0, which is the highest resolution possible..
        lod_offsets = []
        nodes, submeshes = decompose_meshes(vertices.copy(), faces.copy(), scale, quantization_bits)
        # convert each submesh into google draco format and append them..
        for mesh in submeshes:
            draco = trimesh.exchange.ply.export_draco(mesh, bits=quant_bits)
            fragmentdata.write(draco)
            lod_offsets.append(len(draco))

        fragment_positions.append(np.array(nodes))
        fragment_offsets.append(np.array(lod_offsets))

    num_fragments_per_lod = np.array([len(nodes) for nodes in fragment_positions])

    # write the mesh manifest file now..
    manifestdata.write(chunk_shape.astype('<f').tobytes())
    manifestdata.write(grid_origin.astype('<f').tobytes())
    manifestdata.write(struct.pack('<I', num_lods))
    manifestdata.write(lod_scales.astype('<f').tobytes())
    manifestdata.write(vertex_offsets.astype('<f').tobytes(order='C'))
    manifestdata.write(num_fragments_per_lod.astype('<I').tobytes())
    for frag_pos, frag_offset in zip(fragment_positions, fragment_offsets):
        manifestdata.write(frag_pos.T.astype('<I').tobytes(order='C'))
        manifestdata.write(frag_offset.astype('<I').tobytes(order='C'))

    combineddata.write(fragmentdata.getvalue())
    combineddata.write(manifestdata.getvalue())
    offset = len(fragmentdata.getvalue())

    return combineddata.getvalue(), offset


def uploadsingleresmeshes(volumedatasource, volumeidlist, volumenamelist, path, layer_name):
    """Upload mesh (of cloudvolume class) to a local server.

    Parameters
    ----------
    volumedatasource:  list
        contains volumes of cloud volume class.
    volumeidlist:  list
        contains the volume ids.
    volumenamelist:  list
        contains the names of volumes.
    path: str
        local path of the precomputed hosted layer.
    layer_name: str
        layer name.

    Returns
    -------
    cv :     cloudvolume class object
    """
    info = {"@type": "neuroglancer_legacy_mesh",
            'scales': [1, 1, 1],
            }
    path = 'file://' + path + '/precomputed/' + layer_name
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


def to_precomputedsingleresmeshes(volumedatasource, path, layer_name):
    """Upload mesh (of cloudvolume class) to a local server.

    Parameters
    ----------
    volumedatasource:  list
        contains cloud volume meshes.
    path: str
        local path of the precomputed hosted layer.
    layer_name: str
        layer name.

    """
    info = {"@type": "neuroglancer_legacy_mesh",
            'scales': [1, 1, 1],
            }
    path = 'file://' + path + '/precomputed/' + layer_name
    cv = CloudVolume(path, info=info)

    cv.mesh.meta.info['@type'] = 'neuroglancer_legacy_mesh'
    cv.mesh.meta.info['segment_name_map'] = 'segment_names'
    cv.mesh.meta.info['segment_properties'] = 'segment_properties'
    cv.mesh.meta.commit_info()

    files = [os.path.join(cv.mesh.meta.mesh_path, str(vol.segid)) for vol in volumedatasource]
    volumeids = [str(vol.segid) for vol in volumedatasource]

    for fileidx in range(len(files)):
        fullfilepath = str(files[fileidx])  # files[fileidx]
        # print(files[fileidx])
        fullfilepath = os.path.join(cv.basepath, os.path.basename(path), fullfilepath)
        uploadvol = Mesh(
            vertices=volumedatasource[fileidx].vertices, faces=volumedatasource[fileidx].faces,
            segid=None)
        precomputed_mesh = _to_precomputed(uploadvol)
        # print('Seg id is:', str(volumeids[fileidx]))
        # print('Full filepath:', fullfilepath)
        with open(fullfilepath, 'wb') as f:
            f.write(precomputed_mesh)

        manifestinfo = {
            "fragments": [str(volumeids[fileidx])]}
        manifestfilepath = str(files[fileidx]) + ':' + str(0)  # files[fileidx]
        manifestfilepath = os.path.join(cv.basepath, os.path.basename(path), manifestfilepath)
        with open(manifestfilepath, 'w') as f:
            json.dump(manifestinfo, f)

    # delete the info file path, as they will be updated seperately..
    info_file = os.path.join(cv.basepath, os.path.basename(path), cv.mesh.meta.mesh_path, 'info')
    os.remove(info_file)


def to_precomputedsingleresmeshesinfo(volumeidlist, volumenamelist, path, layer_name):
    """Upload mesh (of cloudvolume class) info to a local server.

    Parameters
    ----------
    volumeidlist:  list
        contains the volume ids.
    volumenamelist:  list
        contains the names of volumes.
    path: str
        local path of the precomputed hosted layer.
    layer_name: str
        layer name.

    Returns
    -------
    cv :     CloudVolume
        object of cloudvolume class
    """
    info = {"@type": "neuroglancer_legacy_mesh",
            'scales': [1, 1, 1],
            }
    path = 'file://' + path + '/precomputed/' + layer_name
    cv = CloudVolume(path, info=info)

    cv.mesh.meta.info['@type'] = 'neuroglancer_legacy_mesh'
    cv.mesh.meta.info['segment_name_map'] = 'segment_names'
    cv.mesh.meta.info['segment_properties'] = 'segment_properties'
    cv.mesh.meta.commit_info()

    # create the file for segment_properties
    allvolproplist = {"id": "label",
                      "type": "label",
                      "values": volumenamelist}

    volinfo = {"@type": "neuroglancer_segment_properties",
               "inline": {"ids": volumeidlist,
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
    volumenamedict = dict(zip(volumeidlist, volumenamelist))
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


def uploadmultiresmeshes(volumedatasource, volumeidlist, volumenamelist, path, layer_name):
    """Upload multi-res mesh to a local server.

    Parameters
    ----------
    volumedatasource:  list
        contains cloud volume meshes.
    volumeidlist:  list
        contains the volume ids.
    volumenamelist:  list
        contains the names of volumes.
    path: str
        local path of the precomputed hosted layer.
    layer_name: str
        layer name.

    Returns
    -------
    cv :     cloudvolume class object
    """
    info = {"@type": "neuroglancer_multilod_draco",
            'scales': [1, 1, 1],
            }
    path = 'file://' + path + '/precomputed/' + layer_name
    cv = CloudVolume(path, info=info)

    quant_bits = 16  # number of bits needed to encode for each vertex position

    cv.mesh.meta.info['@type'] = 'neuroglancer_multilod_draco'
    cv.mesh.meta.info['vertex_quantization_bits'] = quant_bits
    cv.mesh.meta.info['transform'] = [1, 0, 0, 0,
                                      0, 1, 0, 0,
                                      0, 0, 1, 0]
    cv.mesh.meta.info['lod_scale_multiplier'] = 1

    cv.mesh.meta.info['segment_name_map'] = 'segment_names'
    cv.mesh.meta.info['segment_properties'] = 'segment_properties'
    cv.mesh.meta.commit_info()

    files = [os.path.join(cv.mesh.meta.mesh_path, str(vol.segid)) for vol in volumedatasource]
    volumeids = [str(vol.segid) for vol in volumedatasource]

    for fileidx in range(len(files)):
        fullfilepath = str(files[fileidx])  # files[fileidx]
        print(files[fileidx])
        fullfilepath = os.path.join(cv.basepath, os.path.basename(path), fullfilepath)
        vertices = volumedatasource[fileidx].vertices
        faces = volumedatasource[fileidx].faces
        print('Seg id is:', str(volumeids[fileidx]))
        print('Full filepath:', fullfilepath)
        _to_multires_precomputed(vertices, faces, quant_bits, fullfilepath)

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


def uploadshardedmultiresmeshes(volumedatasource, volumeidlist, volumenamelist, path, layer_name, shardprogress):
    """Upload sharded multi-res mesh to a local server.

    Parameters
    ----------
    volumedatasource:  list
        contains cloud volume meshes.
    volumeidlist:  list
        contains the volume ids.
    volumenamelist:  list
        contains the names of volumes.
    path: str
        local path of the precomputed hosted layer.
    layer_name: str
        layer name.
    shardprogress:   bool
        progress bar for sharding operation

    Returns
    -------
    cv :     cloudvolume class object
    """
    info = {"@type": "neuroglancer_multilod_draco",
            'scales': [1, 1, 1],
            }
    path = 'file://' + path + '/precomputed/' + layer_name
    cv = CloudVolume(path, info=info)

    quant_bits = 16  # number of bits needed to encode for each vertex position

    cv.mesh.meta.info['@type'] = 'neuroglancer_multilod_draco'
    cv.mesh.meta.info['scales'] = [1, 1, 1]
    cv.mesh.meta.info['vertex_quantization_bits'] = quant_bits
    cv.mesh.meta.info['transform'] = [1, 0, 0, 0,
                                      0, 1, 0, 0,
                                      0, 0, 1, 0]
    cv.mesh.meta.info['lod_scale_multiplier'] = 1

    cv.mesh.meta.info['segment_name_map'] = 'segment_names'
    cv.mesh.meta.info['segment_properties'] = 'segment_properties'

    # prepare sharding info
    spec = ShardingSpecification('neuroglancer_uint64_sharded_v1',
                                 preshift_bits=9,
                                 hash='murmurhash3_x86_128',
                                 minishard_bits=6,
                                 shard_bits=15,
                                 minishard_index_encoding='raw',
                                 data_encoding='raw',)
    cv.mesh.meta.info['sharding'] = spec.to_dict()

    cv.mesh.meta.commit_info()

    files = [os.path.join(cv.mesh.meta.mesh_path, str(vol.segid)) for vol in volumedatasource]
    volumeids = [str(vol.segid) for vol in volumedatasource]

    precomp_data = {}
    offset = {}
    for fileidx in range(len(files)):
        fullfilepath = str(files[fileidx])  # files[fileidx]
        print(files[fileidx])
        fullfilepath = os.path.join(cv.basepath, os.path.basename(path), fullfilepath)
        vertices = volumedatasource[fileidx].vertices
        faces = volumedatasource[fileidx].faces
        print('Seg id is:', str(volumeids[fileidx]))
        print('Full filepath:', fullfilepath)
        volumeid = int(volumeids[fileidx])
        print('Vol id is:', str(volumeid))
        precomp_data[volumeid], offset[volumeid] = _to_multires_shardedprecomputed(vertices, faces, quant_bits)

    shardfiles = spec.synthesize_shards(precomp_data, offset, progress=shardprogress)
    shardedfilepath = os.path.join(cv.basepath, os.path.basename(path), cv.mesh.meta.mesh_path)

    for fname in shardfiles.keys():
        with open(shardedfilepath + '/' + fname, 'wb') as f:
            f.write(shardfiles[fname])

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
