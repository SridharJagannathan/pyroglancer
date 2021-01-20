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

"""Module contains code to open a neuroglancer viewer."""

import neuroglancer as ng
import sys
import webbrowser


def openviewer(ngviewer=None, headless=False):
    """Open a neuroglancer viewing engine.

    Parameters
    ----------
    ngviewer : ng.viewer.Viewer
        object of Neuroglancer viewer class.
    headless : if True, then operating in servers or testcase mode.

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
        if 'ngviewerinst' in sys.modules:
            ngviewer = sys.modules['ngviewerinst']
        else:
            ngviewer = ng.Viewer()
            print('Neuroglancer viewer created at: ', ngviewer)
            sys.modules['ngviewerinst'] = ngviewer
            if not headless:
                webbrowser.open(ngviewer.get_viewer_url())
    else:
        ngviewer = ngviewer

    return ngviewer


def closeviewer():
    """Close a already started ngviewer.

    Parameters
    ----------
    None

    Returns
    -------
    None
    """
    if 'ngviewerinst' in sys.modules:
        print('closing already existing ng viewer')
        del sys.modules['ngviewerinst']
        try:
            ng.stop()
        except Exception:
            print('exception occurred while stopping')
