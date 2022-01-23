from unittest.mock import patch
from hestia_earth.schema import SiteSiteType

from hestia_earth.models.utils.site import related_cycles, valid_site_type

class_path = 'hestia_earth.models.utils.site'
CYCLE = {'@id': 'id'}


@patch(f"{class_path}.find_related", return_value=[CYCLE])
@patch(f"{class_path}.download_hestia", return_value=CYCLE)
def test_related_cycles(*args):
    assert related_cycles('id') == [CYCLE]


def test_valid_site_type():
    site = {'siteType': SiteSiteType.CROPLAND.value}
    assert valid_site_type(site) is True

    site = {'siteType': SiteSiteType.CROPLAND.value}
    assert not valid_site_type(site, [SiteSiteType.OTHER_NATURAL_VEGETATION.value])
