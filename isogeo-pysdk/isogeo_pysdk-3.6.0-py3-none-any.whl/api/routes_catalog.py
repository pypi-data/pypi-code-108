# -*- coding: UTF-8 -*-
#! python3  # noqa E265

"""
    Isogeo API v1 - API Routes for Catalogs entities

    See: http://help.isogeo.com/api/complete/index.html
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import logging
from functools import lru_cache
from typing import Tuple, Union

# 3rd party
from requests.exceptions import Timeout
from requests.models import Response

# submodules
from isogeo_pysdk.checker import IsogeoChecker
from isogeo_pysdk.decorators import ApiDecorators
from isogeo_pysdk.enums import CatalogStatisticsTags
from isogeo_pysdk.models import Catalog, Metadata
from isogeo_pysdk.utils import IsogeoUtils

# #############################################################################
# ########## Global #############
# ##################################

logger = logging.getLogger(__name__)
checker = IsogeoChecker()
utils = IsogeoUtils()


# #############################################################################
# ########## Classes ###############
# ##################################
class ApiCatalog:
    """Routes as methods of Isogeo API used to manipulate catalogs."""

    def __init__(self, api_client=None):
        if api_client is not None:
            self.api_client = api_client

        # store API client (Request [Oauthlib] Session) and pass it to the decorators
        self.api_client = api_client
        ApiDecorators.api_client = api_client

        # ensure platform and others params to request
        (
            self.platform,
            self.api_url,
            self.app_url,
            self.csw_url,
            self.mng_url,
            self.oc_url,
            self.ssl,
        ) = utils.set_base_url(self.api_client.platform)
        # initialize
        super(ApiCatalog, self).__init__()

    @lru_cache()
    @ApiDecorators._check_bearer_validity
    def listing(
        self,
        workgroup_id: str = None,
        include: tuple = ("_abilities", "count"),
        caching: bool = 1,
    ) -> list:
        """Get workgroup catalogs.

        :param str workgroup_id: identifier of the owner workgroup
        :param tuple include: additionnal subresource to include in the response
        :param bool caching: option to cache the response

        :rtype: list

        :Example:

            .. code-block:: python

                # retrieve the catalogs of workgroup
                wg_catalogs = isogeo.catalog.listing(
                    workgroup_id=isogeo_workgroup._id,
                    include=None
                )
                # filter on catalogs with the Sacn checked
                for cat in wg_catalogs:
                    if cat.get("$scan", False):
                        print(cat.get("name"))
        """
        # check workgroup UUID
        if not checker.check_is_uuid(workgroup_id):
            raise ValueError("Workgroup ID is not a correct UUID.")
        else:
            pass

        # handling request parameters
        if isinstance(include, (tuple, list)):
            payload = {"_include": ",".join(include)}
        else:
            payload = None

        # request URL
        url_catalogs = utils.get_request_base_url(
            route="groups/{}/catalogs".format(workgroup_id)
        )

        # request
        req_wg_catalogs = self.api_client.get(
            url_catalogs,
            headers=self.api_client.header,
            params=payload,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_wg_catalogs)
        if isinstance(req_check, tuple):
            return req_check

        wg_catalogs = req_wg_catalogs.json()

        # if caching use or store the workgroup catalogs
        if caching and not self.api_client._wg_catalogs_names:
            self.api_client._wg_catalogs_names = {
                i.get("name"): i.get("_id") for i in wg_catalogs
            }

        # end of method
        return wg_catalogs

    @lru_cache()
    @ApiDecorators._check_bearer_validity
    def metadata(self, metadata_id: str) -> list:
        """List metadata's catalogs with complete information.

        :param str metadata_id: metadata UUID

        :returns: the list of catalogs associated with the metadata
        :rtype: list
        """
        # check metadata UUID
        if not checker.check_is_uuid(metadata_id):
            raise ValueError(
                "Metadata ID is not a correct UUID: {}".format(metadata_id)
            )
        else:
            pass

        # URL
        url_metadata_catalogs = utils.get_request_base_url(
            route="resources/{}/catalogs/".format(metadata_id)
        )

        # request
        req_metadata_catalogs = self.api_client.get(
            url=url_metadata_catalogs,
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_metadata_catalogs)
        if isinstance(req_check, tuple):
            return req_check

        # end of method
        return req_metadata_catalogs.json()

    @lru_cache()
    @ApiDecorators._check_bearer_validity
    def get(
        self,
        workgroup_id: str,
        catalog_id: str,
        include: tuple = ("_abilities", "count"),
    ) -> Catalog:
        """Get details about a specific catalog.

        :param str workgroup_id: identifier of the owner workgroup
        :param str catalog_id: catalog UUID
        :param list include: additionnal subresource to include in the response
        """
        # check workgroup UUID
        if not checker.check_is_uuid(workgroup_id):
            raise ValueError(
                "Workgroup ID is not a correct UUID: {}".format(workgroup_id)
            )
        else:
            pass
        # check catalog UUID
        if not checker.check_is_uuid(catalog_id):
            raise ValueError("Catalog ID is not a correct UUID: {}".format(catalog_id))
        else:
            pass

        # request parameter
        if isinstance(include, (tuple, list)):
            payload = {"_include": ",".join(include)}
        else:
            payload = None

        # catalog route
        url_catalog = utils.get_request_base_url(
            route="groups/{}/catalogs/{}".format(workgroup_id, catalog_id)
        )

        # request
        req_catalog = self.api_client.get(
            url=url_catalog,
            headers=self.api_client.header,
            params=payload,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_catalog)
        if isinstance(req_check, tuple):
            return req_check

        # end of method
        return Catalog.clean_attributes(req_catalog.json())

    @ApiDecorators._check_bearer_validity
    def create(
        self, workgroup_id: str, catalog: Catalog, check_exists: bool = 1
    ) -> Catalog:
        """Add a new catalog to a workgroup.

        :param str workgroup_id: identifier of the owner workgroup
        :param class catalog: Catalog model object to create
        :param bool check_exists: check if a catalog already exists into the workgroup:

            - 0 = no check
            - 1 = compare name [DEFAULT]

        :returns: the created catalog or False if a similar cataog already exists or a tuple with response error code
        :rtype: Catalog
        """
        # check workgroup UUID
        if not checker.check_is_uuid(workgroup_id):
            raise ValueError(
                "Workgroup ID is not a correct UUID: {}".format(workgroup_id)
            )
        else:
            pass

        # check if catalog already exists in workgroup
        if check_exists == 1:
            # retrieve workgroup catalogs
            if not self.api_client._wg_catalogs_names:
                self.listing(workgroup_id=workgroup_id, include=())
            # check
            if catalog.name in self.api_client._wg_catalogs_names:
                logger.debug(
                    "Catalog with the same name already exists: {}. Use 'catalog_update' instead.".format(
                        catalog.name
                    )
                )
                return False
        else:
            pass

        # build request url
        url_catalog_create = utils.get_request_base_url(
            route="groups/{}/catalogs".format(workgroup_id)
        )

        # request
        req_new_catalog = self.api_client.post(
            url_catalog_create,
            data=catalog.to_dict_creation(),
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_new_catalog)
        if isinstance(req_check, tuple):
            return req_check

        # handle bad JSON attribute
        new_catalog = req_new_catalog.json()
        new_catalog["scan"] = new_catalog.pop("$scan")

        # load new catalog and save it to the cache
        new_catalog = Catalog(**new_catalog)
        self.api_client._wg_catalogs_names[new_catalog.name] = new_catalog._id

        # end of method
        return new_catalog

    @ApiDecorators._check_bearer_validity
    def delete(self, workgroup_id: str, catalog_id: str):
        """Delete a catalog from Isogeo database.

        :param str workgroup_id: identifier of the owner workgroup
        :param str catalog_id: identifier of the resource to delete
        """
        # check workgroup UUID
        if not checker.check_is_uuid(workgroup_id):
            raise ValueError(
                "Workgroup ID is not a correct UUID: {}".format(workgroup_id)
            )
        else:
            pass

        # check catalog UUID
        if not checker.check_is_uuid(catalog_id):
            raise ValueError("Catalog ID is not a correct UUID: {}".format(catalog_id))
        else:
            pass

        # request URL
        url_catalog_delete = utils.get_request_base_url(
            route="groups/{}/catalogs/{}".format(workgroup_id, catalog_id)
        )

        # request
        req_catalog_deletion = self.api_client.delete(
            url_catalog_delete,
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_catalog_deletion)
        if isinstance(req_check, tuple):
            return req_check

        return req_catalog_deletion

    @ApiDecorators._check_bearer_validity
    def exists(self, workgroup_id: str, catalog_id: str) -> bool:
        """Check if the specified catalog exists and is available for the authenticated user.

        :param str workgroup_id: identifier of the owner workgroup
        :param str catalog_id: identifier of the catalog to verify
        """
        # check workgroup UUID
        if not checker.check_is_uuid(workgroup_id):
            raise ValueError(
                "Workgroup ID is not a correct UUID: {}".format(workgroup_id)
            )
        else:
            pass
        # check catalog UUID
        if not checker.check_is_uuid(catalog_id):
            raise ValueError("Catalog ID is not a correct UUID: {}".format(catalog_id))
        else:
            pass

        # URL builder
        url_catalog_exists = utils.get_request_base_url(
            route="groups/{}/catalogs/{}".format(workgroup_id, catalog_id)
        )

        # request
        req_catalog_exists = self.api_client.get(
            url=url_catalog_exists,
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_catalog_exists)
        if isinstance(req_check, tuple):
            return req_check

        return req_catalog_exists

    @ApiDecorators._check_bearer_validity
    def update(self, catalog: Catalog, caching: bool = 1) -> Catalog:
        """Update a catalog owned by a workgroup.

        :param class catalog: Catalog model object to update
        :param bool caching: option to cache the response
        """
        # check catalog UUID
        if not checker.check_is_uuid(catalog._id):
            raise ValueError("Catalog ID is not a correct UUID: {}".format(catalog._id))
        else:
            pass

        # URL
        url_catalog_update = utils.get_request_base_url(
            route="groups/{}/catalogs/{}".format(catalog.owner.get("_id"), catalog._id)
        )

        # request
        req_catalog_update = self.api_client.put(
            url=url_catalog_update,
            json=catalog.to_dict_creation(),
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_catalog_update)
        if isinstance(req_check, tuple):
            return req_check

        # handle bad JSON attribute
        new_catalog = req_catalog_update.json()
        new_catalog["scan"] = new_catalog.pop("$scan")

        # load new catalog and save it to the cache
        new_catalog = Catalog(**new_catalog)
        if caching:
            self.api_client._wg_catalogs_names[new_catalog.name] = new_catalog._id

        # end of method
        return new_catalog

    # -- Routes to manage the related objects ------------------------------------------
    @ApiDecorators._check_bearer_validity
    def associate_metadata(
        self, metadata: Union[Metadata, Tuple[Metadata, ...]], catalog: Catalog
    ) -> Response:
        """Associate a metadata with a catalog.

        If the specified catalog is already associated, the response is still 204.

        :param metadata: metadata object to update
        :param Catalog catalog: catalog model object to associate

        :Example:

        .. code-block:: python

            isogeo.catalog.associate_metadata(
                isogeo.metadata.get(METADATA_UUID),
                isogeo.catalog.get(WORKGROUP_UUID, CATALOG_UUID)
                )

            <Response [204]>
        """
        # check metadata UUID
        if isinstance(metadata, Metadata) and not checker.check_is_uuid(metadata._id):
            raise ValueError(
                "Metadata ID is not a correct UUID: {}".format(metadata._id)
            )
        elif isinstance(metadata, (list, tuple)):
            logger.info("Multiple association detected: using bulk instead...")
            # prepare request
            self.api_client.metadata.bulk.prepare(
                metadatas=tuple([md._id for md in metadata]),
                action="add",
                target="catalogs",
                models=(catalog,),
            )
            # send it
            return self.api_client.metadata.bulk.send()
        else:
            pass

        # check catalog UUID
        if not checker.check_is_uuid(catalog._id):
            raise ValueError("Catalog ID is not a correct UUID: {}".format(catalog._id))
        else:
            pass

        # URL
        url_catalog_association = utils.get_request_base_url(
            route="catalogs/{}/resources/{}".format(catalog._id, metadata._id)
        )

        # request
        req_catalog_association = self.api_client.put(
            url=url_catalog_association,
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_catalog_association)
        if isinstance(req_check, tuple):
            return req_check

        # end of method
        return req_catalog_association

    @ApiDecorators._check_bearer_validity
    def dissociate_metadata(self, metadata: Metadata, catalog: Catalog) -> Response:
        """Removes the association between a metadata and a catalog.

        If the specified catalog is not associated, the response is 404.

        :param Metadata metadata: metadata object to update
        :param Catalog catalog: catalog model object to associate
        """
        # check metadata UUID
        if not checker.check_is_uuid(metadata._id):
            raise ValueError(
                "Metadata ID is not a correct UUID: {}".format(metadata._id)
            )
        else:
            pass

        # check catalog UUID
        if not checker.check_is_uuid(catalog._id):
            raise ValueError("Catalog ID is not a correct UUID: {}".format(catalog._id))
        else:
            pass

        # URL
        url_catalog_dissociation = utils.get_request_base_url(
            route="catalogs/{}/resources/{}".format(catalog._id, metadata._id)
        )

        # request
        req_catalog_dissociation = self.api_client.delete(
            url=url_catalog_dissociation,
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_catalog_dissociation)
        if isinstance(req_check, tuple):
            return req_check

        # end of method
        return req_catalog_dissociation

    @lru_cache()
    @ApiDecorators._check_bearer_validity
    def shares(self, catalog_id: str) -> list:
        """Returns shares for the specified catalog.

        :param str catalog_id: catalog UUID

        :return: list of Shares containing the catalog
        :rtype: list
        """
        # check catalog UUID
        if not checker.check_is_uuid(catalog_id):
            raise ValueError("Catalog ID is not a correct UUID: {}".format(catalog_id))
        else:
            pass

        # URL builder
        url_catalog_shares = utils.get_request_base_url(
            route="catalogs/{}/shares".format(catalog_id)
        )

        # request
        req_catalog_shares = self.api_client.get(
            url=url_catalog_shares,
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_catalog_shares)
        if isinstance(req_check, tuple):
            return req_check

        return req_catalog_shares.json()

    @lru_cache()
    @ApiDecorators._check_bearer_validity
    def statistics(self, catalog_id: str) -> dict:
        """Returns statistics for the specified catalog.

        :param str catalog_id: catalog UUID
        """
        # check catalog UUID
        if not checker.check_is_uuid(catalog_id):
            raise ValueError("Catalog ID is not a correct UUID: {}".format(catalog_id))
        else:
            pass

        # URL builder
        url_catalog_statistics = utils.get_request_base_url(
            route="catalogs/{}/statistics".format(catalog_id)
        )

        # request
        req_catalog_statistics = self.api_client.get(
            url=url_catalog_statistics,
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_catalog_statistics)
        if isinstance(req_check, tuple):
            return req_check

        return req_catalog_statistics.json()

    @lru_cache()
    @ApiDecorators._check_bearer_validity
    def statistics_by_tag(self, catalog_id: str, tag: str) -> dict:
        """Returns statistics on a specific tag for the specified catalog.

        Be careful: if an invalid character is present into the response (e.g. contact.name = 'bureau GF-3A'), a ConnectionError / ReadTimeout will be raised.

        :param str catalog_id: catalog UUID
        :param str tag: tag name. Must be one of: catalog, coordinate-system, format, keyword:inspire-theme, keyword, owner
        """
        # check catalog UUID
        if not checker.check_is_uuid(catalog_id):
            raise ValueError("Catalog ID is not a correct UUID: {}".format(catalog_id))
        else:
            pass

        # check tag
        if not CatalogStatisticsTags.has_value(tag) or tag == "catalog":
            raise ValueError(
                "Tag name '{}' is not one of accepted values: {} (except 'catalog')".format(
                    tag, CatalogStatisticsTags
                )
            )

        # URL builder
        url_catalog_statistics = utils.get_request_base_url(
            route="catalogs/{}/statistics/tag/{}".format(catalog_id, tag)
        )

        # request
        try:
            req_catalog_statistics = self.api_client.get(
                url=url_catalog_statistics,
                headers=self.api_client.header,
                proxies=self.api_client.proxies,
                verify=self.api_client.ssl,
                timeout=self.api_client.timeout,
            )
        except Timeout as e:
            logger.error(
                "Request failed (timeout) but maybe (probably) it occurred because of a special "
                "character in an entity string. Exception: {}".format(e)
            )
            return False, 500

        # checking response
        req_check = checker.check_api_response(req_catalog_statistics)
        if isinstance(req_check, tuple):
            return req_check

        return req_catalog_statistics.json()


# ##############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    """standalone execution."""
    api_catalog = ApiCatalog()
