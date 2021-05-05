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
    headless : bool
        if True, then operating in servers or testcase mode.

    Returns
    -------
    ngviewer : ng.viewer.Viewer
        object of Neuroglancer viewer class.

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
    """
    if 'ngviewerinst' in sys.modules:
        print('closing already existing ng viewer')
        del sys.modules['ngviewerinst']
        try:
            ng.stop()
        except Exception:
            print('exception occurred while stopping')


def setviewerstate(ngviewer=None, axis_lines=True, bounding_box=True, layout=None):
    """Set state of neuroglancer viewing engine.

    Parameters
    ----------
    ngviewer : ng.viewer.Viewer
        object of Neuroglancer viewer class.
    axis_lines : bool
        if False, then disable the axis lines.
    bounding_box : bool
        if False, then disable the default annotations like bounding box.
    layout:  string | dict
        possible layout options.

    Returns
    -------
    ngviewer : ng.viewer.Viewer
        object of Neuroglancer viewer class.

    """
    if ngviewer is None:
        if 'ngviewerinst' in sys.modules:
            ngviewer = sys.modules['ngviewerinst']
        else:
            raise RuntimeError("no known neuroglancer instances were set already")
    else:
        ngviewer = ngviewer

    with ngviewer.txn() as s:
        s.show_axis_lines = axis_lines
        s.show_default_annotations = bounding_box

    if layout is not None:
        with ngviewer.txn() as s:
            s.layout = layout

    return ngviewer
