[![Build Status](https://github.com/SridharJagannathan/pyroglancer/workflows/Tests/badge.svg)](https://github.com/SridharJagannathan/pyroglancer/actions)
[![codecov](https://codecov.io/gh/SridharJagannathan/pyroglancer/branch/master/graph/badge.svg?token=HuY5pVjAMm)](https://codecov.io/gh/SridharJagannathan/pyroglancer) [![PyPI version](https://badge.fury.io/py/pyroglancer.svg)](https://badge.fury.io/py/pyroglancer) [![Downloads](https://pepy.tech/badge/pyroglancer)](https://pepy.tech/project/pyroglancer)

![image](https://github.com/SridharJagannathan/pyroglancer/raw/master/docs/_static/pyroglancer_logo.png)

Pythonic interface to neuroglancer for displaying neuronal data like
neurons, synapses, meshes (surfaces, volumes), annotations (points) in
the precomputed format.

Installation
============

The easiest way to install the package is via `pip`:

    $ pip3 install pyroglancer

The easiest way to install the latest developments from `GitHub` is:

    $ pip3 install git+git://github.com/SridharJagannathan/pyroglancer@master

Documentation
=============

<https://SridharJagannathan.github.io/pyroglancer>

Features
========

-   Fetch and display neurons/neuropil meshes from electron microscopy (EM) datasets like hemibrain, FAFB etc and light microscopy (LM) 
    neurons in mesh format.
-   Display locally modified neurons or neuropil meshes.
-   Display synapse annotations etc

| Elements | Format |  Source |  Datasets |
| --- | --- | --- | --- |
| `neuron` | skeletons (swc) or volumetric meshes | `CATMAID`, `neuprint`, `vritualflybrain` or other locally modified data | EM datasets like FAFB, hemibrain or any other LM dataset like lineage clones etc |
| `neuropils` | volumetric meshes | `CATMAID`, `neuprint` or other locally modified data | FAFB, hemibrain |
| `synapses` | point annotations or precomputed format | neuroglancer layers or other locally modified data | FAFB, hemibrain |


Acknowledgements
================

Thanks to [Jeremy Maitin-Shepard](https://github.com/jbms) from google
for inventing the precomputed format and answering many of my queries. The pyroglancer
logo was inspired from [PyPy](https://www.pypy.org/). The pyroglancer critically depends on
packages like [NAVis](https://github.com/schlegelp/navis) for interfacing with neuron data.

Copyright & License
===================

Copyright (c) 2021, [Sridhar Jagannathan](https://github.com/SridharJagannathan).
3-clause BSD License.
