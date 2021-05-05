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

"""Module contains functions to handle configuratio data fron YAML files."""
from .createconfig import getdefaultconfigdata
import os
import yaml


def getconfigdata(configfileloc=None):
    """Get the YAML config data from the default location.

    Parameters
    ----------
    configfileloc :  str
        override the default location if configfileloc is present

    Returns
    -------
    configdata : dict
        different layers to be added in the neuroglancer instance
    """
    if configfileloc is not None:
        print('using custom location at: ', configfileloc)
    else:
        configfileloc = os.environ['PYROGLANCER_CONFIG']
        print('using default location at: ', configfileloc)

    configfileloc = os.path.expanduser(configfileloc)
    if os.path.isfile(configfileloc):
        with open(configfileloc, "r") as fh:
            configdata = yaml.load(fh, Loader=yaml.SafeLoader)
    else:
        print('using default config data..')
        configdata = getdefaultconfigdata()
    return configdata
