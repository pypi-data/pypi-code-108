from nose.tools import nottest, assert_equals, with_setup
from vpv.model.coordinate_mapper import Coordinate_mapper
from vpv.common import Orientation

def _get_views():
    """
    Get a dummpy views object. This is a list that contains the SliceViewWidgets. Coordinate mapper only needs a few
    attributes from each view, so we can add those to the dummy views
    """
    view = [] # Currently only tesitng function that does not access views


def _get_flips():
    """
    Flips is a dict that contains the flips status of each orientation
    Returns
    -------

    """
    flips = {
        'axial': {'x': False, 'y': False, 'z': False},
        'coronal': {'x': False, 'y': False, 'z': False},
        'impc_view': False,
        'sagittal': {'x': False, 'y': False, 'z': False}
    }

    return flips


def _get_mapper():
    return Coordinate_mapper(_get_views(), _get_flips())


def test_view_to_volume():

    mapper = _get_mapper()

    dims_xyz = (100, 200, 400)

    x = 10
    y = 20
    z = 30

    # going from axial to axial coordinates should stay unchanged
    res = mapper.view_to_volume(x, y, z, Orientation.axial, dims_xyz)
    assert res == (x, y, z)

    # Going from coronal to axial
    res = mapper.view_to_volume(x, y, z, Orientation.coronal, dims_xyz)
    assert res == (x, z, y)

    # Going from sagittal to axial
    res = mapper.view_to_volume(x, y, z, Orientation.sagittal, dims_xyz)
    assert res == (y, z, x)


    # Now try with flips
    mapper.flips['axial'] = True
    res = mapper.view_to_volume(x, y, z, Orientation.axial, dims_xyz)
    assert res == (x, y, z)




if __name__ == '__main__':
    test_view_to_volume()