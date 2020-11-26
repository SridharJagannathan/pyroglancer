import neuroglancer as ng
from ..ngviewer import openviewer


def test_newviewer():
    # check if the viewer opens when no object is passed....

    viewer = openviewer(None)

    assert isinstance(viewer, ng.viewer.Viewer)


def test_reuseoldviewer():
    # check if old viewer is reused incase of new opening request....

    viewer1 = openviewer(None)
    viewer2 = openviewer(viewer1)

    assert viewer1 == viewer2
