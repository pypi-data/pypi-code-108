"""
Unit tests for the _utils.dkist_location module
"""
from astropy.coordinates import EarthLocation

from dkist_processing_common._util.dkist_location import location_of_dkist


def test_location_of_dkist():
    """
    Given: function for retrieving the dkist location on earth
    When: Call function
    Then: receive an earth location and not astropy.coordinates.UnknownSiteException
    """
    itrs = location_of_dkist()
    assert isinstance(itrs, EarthLocation)
