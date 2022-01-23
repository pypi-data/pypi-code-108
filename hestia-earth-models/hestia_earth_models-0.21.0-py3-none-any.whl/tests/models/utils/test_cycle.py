from hestia_earth.schema import SiteSiteType

from hestia_earth.models.utils.cycle import valid_site_type


def test_valid_site_type():
    site = {'siteType': SiteSiteType.CROPLAND.value}
    cycle = {'site': site}
    assert valid_site_type(cycle) is True

    cycle['site']['siteType'] = SiteSiteType.PERMANENT_PASTURE.value
    assert not valid_site_type(cycle)
    assert not valid_site_type(site, True) is True
