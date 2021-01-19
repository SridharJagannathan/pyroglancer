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

"""Module contains test data to create a sample yaml config file."""
import yaml

data = [
    dict(space='FAFB',
         dimension=dict(
             x=1,
             y=1,
             z=1,
             units='um'),
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
    dict(space='hemibrain',
         dimension=dict(
            x=1,
            y=1,
            z=1,
            units='um'
            ),
         layers=dict(
            emdata=dict(
                type='image',
                source='precomputed://gs://neuroglancer-janelia-flyem-hemibrain/emdata/clahe_yz/jpeg'
                )
            )
         )
         ]
with open('config.yml', 'w') as outfile:
    yaml.dump(data, outfile, sort_keys=False, default_flow_style=False)