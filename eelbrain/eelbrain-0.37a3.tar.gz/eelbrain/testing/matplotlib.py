# Author: Christian Brodbeck <christianbrodbeck@nyu.edu>
from ..plot._base import EelFigure


def assert_contains(bbox, artist):
    a_bbox = artist.get_window_extent()
    assert bbox.containsx(a_bbox.xmin)
    assert bbox.containsx(a_bbox.xmax)
    assert bbox.containsy(a_bbox.ymin)
    assert bbox.containsy(a_bbox.ymax)


def assert_titles_visible(p: EelFigure):
    bbox = p.figure.get_window_extent()
    if p.figure._suptitle:
        assert_contains(bbox, p.figure._suptitle)
    for ax in p.figure.axes:
        if ax.title:
            assert_contains(bbox, ax.title)
