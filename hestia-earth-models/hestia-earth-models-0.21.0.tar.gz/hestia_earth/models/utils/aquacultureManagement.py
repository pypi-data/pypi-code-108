from .site import WATER_TYPES


def valid_site_type(cycle: dict): return cycle.get('site', {}).get('siteType') in WATER_TYPES
