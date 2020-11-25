# pyroglancer/ngviewer.py

import neuroglancer as ng


def openviewer(ngviewer = None):
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
    else:
        ngviewer = ngviewer

    return ngviewer
