"""Factory functions for SitesApi."""
import typing as tp

from bambooapi_client.testing.factory import faker
from bambooapi_client.testing.factory.models import Factory, SiteFactory


def site_factory(**kwargs) -> dict:
    """Create a Site.

    Parameters
    ----------
    kwargs:
        Keyword arguments used by SiteFactory(**kwargs)

    Notes
    -----
    The return type and format matches `SitesApi:get_site`
    """
    return SiteFactory(**kwargs).to_dict()


def devices_factory(model: Factory, length: int, **kwargs) -> tp.List[dict]:
    """Create a list of model instances.

    Parameters
    ----------
    model: Factory
    length: int
        Length of the list.
    kwargs:
        Keyword arguments used by model(**kwargs)

    Notes
    -----
    The return type and format matches `SitesApi:list_devices`
    """
    return faker.list_(model, length, **kwargs)()
