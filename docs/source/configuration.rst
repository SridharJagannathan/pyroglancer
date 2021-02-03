Configure ngspaces
******************

After installation, you need to configure ngspaces (neuroglancer spaces), a shorthand convention for different configurations 
like electron microscopy images, segmentation, synapse predictions etc per dataset.

#. An example `config.yml` file for the `FAFB` dataset looks like below::

    - ngspace: FAFB
    dimension:
        x: 1
        y: 1
        z: 1
        units: um
    voxelsize:
        x: 4
        y: 4
        z: 40
        units: nm
    layers:
        fafb_v14_orig:
        type: image
        source: precomputed://gs://neuroglancer-fafb-data/fafb_v14/fafb_v14_orig
        fafb_v14_clahe:
        type: image
        source: precomputed://gs://neuroglancer-fafb-data/fafb_v14/fafb_v14_clahe
        FAFB.surf:
        type: surfacemesh
        source: vtk://https://storage.googleapis.com/neuroglancer-fafb-data/elmr-data/FAFB.surf.vtk.gz
        seg_20190805:
        type: segmentation
        source: precomputed://gs://fafb-ffn1-20190805/segmentation
        synapses_buhmann2019:
        type: synapsepred
        source: precomputed://gs://neuroglancer-20191211_fafbv14_buhmann2019_li20190805
        linkedseg: seg_20190805
        clefts_Heinrich_etal:
        type: synapticcleft
        source: n5://gs://fafb-v14-synaptic-clefts-heinrich-et-al-2018-n5/synapses_dt_reblocked

#. Save the above `config.yml` file in a directory like `~./pyroglancer/config.yml`

#. Set an environment variable in your bash profile like below ::

    export PYROGLANCER_CONFIG='~/.pyroglancer/config.yml'

.. note:: If you are having trouble in configuring, please don't hesitate to ask