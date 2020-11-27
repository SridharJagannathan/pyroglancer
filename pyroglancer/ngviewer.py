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

import neuroglancer as ng
import webbrowser


def openviewer(ngviewer=None):
    """
    Open a neuroglancer viewing engine.



    Parameters
    ----------
    ngviewer : ng.viewer.Viewer
        object of Neuroglancer viewer class.

    Returns
    -------
    ngviewer : ng.viewer.Viewer
        object of Neuroglancer viewer class.

    Examples
    --------
    Open a neuroglancer viewer.


    >>> openviewer()
    Neuroglancer viewer created at:  http://127.0.0.1:53890/v/xxyyy/
    http://127.0.0.1:53890/v/xxyyy/
    """
    if ngviewer is None:
        ngviewer = ng.Viewer()
        print('Neuroglancer viewer created at: ', ngviewer)
        webbrowser.open(ngviewer.get_viewer_url())
    else:
        ngviewer = ngviewer

    return ngviewer
