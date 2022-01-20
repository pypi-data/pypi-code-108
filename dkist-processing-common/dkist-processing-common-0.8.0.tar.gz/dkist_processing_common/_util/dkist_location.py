"""
Fault tolerant retrieval of the dkist earth location
"""
from astropy.coordinates import EarthLocation
from astropy.coordinates import UnknownSiteException
from retry import retry


@retry(UnknownSiteException, tries=5, delay=1, backoff=2)
def location_of_dkist() -> EarthLocation:
    """
    Cartesian geocentric coordinates of DKIST on Earth
    """
    return EarthLocation.of_site("dkist")
