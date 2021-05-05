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

"""Module for creating yaml based configuration files for adding layers in the neuroglancer."""
import os
import yaml

defaultconfigdata = [
    dict(ngspace='FAFB',
         dimension=dict(
             x=1,
             y=1,
             z=1,
             units='um'),
         voxelsize=dict(
             x=4,
             y=4,
             z=40,
             units='nm'),
         layers=dict(
                fafb_v14_orig=dict(
                    type='image',
                    source='precomputed://gs://neuroglancer-fafb-data/fafb_v14/fafb_v14_orig'
                    ),
                fafb_v14_clahe=dict(
                    type='image',
                    source='precomputed://gs://neuroglancer-fafb-data/fafb_v14/fafb_v14_clahe'
                    )
            )
         ),
    dict(ngspace='hemibrain',
         dimension=dict(
            x=1,
            y=1,
            z=1,
            units='um'
            ),
         voxelsize=dict(
             x=8,
             y=8,
             z=8,
             units='nm'),
         layers=dict(
            emdata=dict(
                type='image',
                source='precomputed://gs://neuroglancer-janelia-flyem-hemibrain/emdata/clahe_yz/jpeg'
                )
            )
         )
         ]


def createconfig(configdata, configfileloc=None, overwrite=False):
    """Create config file in case it is not found.

    Parameters
    ----------
        configdata : dict
            different layers to be added in the neuroglancer instance
        configfileloc: str
            location of the configuration file
        overwrite: bool
            if set to True, then overwrites the existing configuration file
    """
    if configfileloc is None:
        configfileloc = os.environ['PYROGLANCER_CONFIG']

    if not os.path.exists(configfileloc) or overwrite:
        configfolder = os.path.dirname(configfileloc)
        if not os.path.exists(configfolder):
            print('creating default config directory..')
            os.makedirs(configfolder)
        with open(configfileloc, 'w+') as outfile:
            print('adding default config file..')
            yaml.dump(configdata, outfile, sort_keys=False, default_flow_style=False)

    print('setting default config file loc')
    os.environ["PYROGLANCER_CONFIG"] = configfileloc


def getdefaultconfigdata():
    """Get neuroglancer layer data from default configuration in case configuration fileit is not found."""
    return defaultconfigdata
