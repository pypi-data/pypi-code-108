from hestia_earth.schema import SchemaType, SiteSiteType
from hestia_earth.utils.api import download_hestia, find_related

WATER_TYPES = [
    SiteSiteType.POND.value,
    SiteSiteType.RIVER_OR_STREAM.value,
    SiteSiteType.LAKE.value,
    SiteSiteType.SEA_OR_OCEAN.value
]
FRESH_WATER_TYPES = [
    SiteSiteType.RIVER_OR_STREAM.value,
    SiteSiteType.LAKE.value
]


def related_cycles(site_id: str):
    """
    Get the list of `Cycle` related to the `Site`.

    In Hestia, a `Cycle` must have a link to a `Site`, therefore a `Site` can be related to many `Cycle`s.

    Parameters
    ----------
    site_id : str
        The `@id` of the `Site`.

    Returns
    -------
    list[dict]
        The related `Cycle`s as `dict`.
    """
    nodes = find_related(SchemaType.SITE, site_id, SchemaType.CYCLE)
    return [] if nodes is None else list(map(lambda node: download_hestia(node.get('@id'), SchemaType.CYCLE), nodes))


def valid_site_type(site: dict, site_types=[SiteSiteType.CROPLAND.value, SiteSiteType.PERMANENT_PASTURE.value]):
    """
    Check if the site `siteType` is allowed.

    Parameters
    ----------
    site : dict
        The `Site`.
    site_types : list[string]
        List of valid site types. Defaults to `['cropland', 'permanent pasture']`.
        Full list available on https://hestia.earth/schema/Site#siteType.

    Returns
    -------
    bool
        `True` if `siteType` matches the allowed values, `False` otherwise.
    """
    site_type = site.get('siteType') if site is not None else None
    return site_type in site_types
