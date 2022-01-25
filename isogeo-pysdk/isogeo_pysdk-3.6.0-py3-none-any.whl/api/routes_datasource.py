# -*- coding: UTF-8 -*-
#! python3  # noqa E265

"""
    Isogeo API v1 - API Routes for Datasources entities

    See: http://help.isogeo.com/api/complete/index.html
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import logging
from functools import lru_cache

# submodules
from isogeo_pysdk.checker import IsogeoChecker
from isogeo_pysdk.decorators import ApiDecorators
from isogeo_pysdk.models import Datasource
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
class ApiDatasource:
    """Routes as methods of Isogeo API used to manipulate datasources (CSW entry-points)."""

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
        super(ApiDatasource, self).__init__()

    @lru_cache()
    @ApiDecorators._check_bearer_validity
    def listing(
        self, workgroup_id: str = None, include: tuple = None, caching: bool = 1
    ) -> list:
        """Get workgroup datasources.

        :param str workgroup_id: identifier of the owner workgroup
        :param list include: additionnal subresource to include in the response
        :param bool caching: option to cache the response
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
        url_datasources = utils.get_request_base_url(
            route="groups/{}/data-sources".format(workgroup_id)
        )

        # request
        req_wg_datasources = self.api_client.get(
            url=url_datasources,
            headers=self.api_client.header,
            params=payload,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_wg_datasources)
        if isinstance(req_check, tuple):
            return req_check

        wg_datasources = req_wg_datasources.json()

        # if caching use or store the workgroup datasources
        if caching:
            for i in wg_datasources:
                self.api_client._wg_datasources_urls[i.get("location")] = i.get("_id")
                self.api_client._wg_datasources_names[i.get("name")] = i.get("_id")

        # end of method
        return wg_datasources

    @ApiDecorators._check_bearer_validity
    def datasource(self, workgroup_id: str, datasource_id: str) -> Datasource:
        """Get details about a specific datasource.

        :param str workgroup_id: identifier of the owner workgroup
        :param str datasource_id: datasource UUID
        """
        # check workgroup UUID
        if not checker.check_is_uuid(workgroup_id):
            raise ValueError("Workgroup ID is not a correct UUID.")
        else:
            pass
        # check datasource UUID
        if not checker.check_is_uuid(datasource_id):
            raise ValueError("Datasource ID is not a correct UUID.")
        else:
            pass

        # datasource route
        url_datasource = utils.get_request_base_url(
            route="groups/{}/data-sources/{}".format(workgroup_id, datasource_id)
        )

        # request
        req_datasource = self.api_client.get(
            url=url_datasource,
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_datasource)
        if isinstance(req_check, tuple):
            return req_check

        # end of method
        return Datasource(**req_datasource.json())

    @ApiDecorators._check_bearer_validity
    def create(
        self,
        workgroup_id: str,
        datasource: object = Datasource(),
        check_exists: int = 2,
    ) -> Datasource:
        """Add a new datasource to a workgroup.

        :param str workgroup_id: identifier of the owner workgroup
        :param int check_exists: check if a datasource already exists inot the workgroup:

        - 0 = no check
        - 1 = compare name
        - 2 = compare URL (location) [DEFAULT]

        :param class datasource: Datasource model object to create
        """
        # check workgroup UUID
        if not checker.check_is_uuid(workgroup_id):
            raise ValueError("Workgroup ID is not a correct UUID.")
        else:
            pass

        # check required datasource attributes
        if not datasource.name or not datasource.location:
            raise ValueError(
                "Datasource requires at least `name`and `location` to be created."
            )
        else:
            pass

        # check if datasource already exists in workgroup
        if check_exists == 1:  # check names
            # retrieve workgroup datasources
            if not self.api_client._wg_datasources_names:
                self.listing(workgroup_id=workgroup_id, include=())
            # check
            if datasource.name in self.api_client._wg_datasources_names:
                logger.debug(
                    "Datasource with the same name already exists: {}. Use 'datasource_update' instead.".format(
                        datasource.name
                    )
                )
                return False
        elif check_exists == 2:  # check URL (location)
            # retrieve workgroup datasources
            if not self.api_client._wg_datasources_urls:
                self.listing(workgroup_id=workgroup_id, include=())
            # check
            if datasource.location in self.api_client._wg_datasources_urls:
                logging.debug(
                    "Datasource with the same url (location) already exists: {}. Use 'datasource_update' instead.".format(
                        datasource.location
                    )
                )
                return False
        else:
            pass

        # build request url
        url_datasource_create = utils.get_request_base_url(
            route="groups/{}/data-sources".format(workgroup_id)
        )

        # request
        req_new_datasource = self.api_client.post(
            url=url_datasource_create,
            json=datasource.to_dict_creation(),
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_new_datasource)
        if isinstance(req_check, tuple):
            return req_check

        # load new datasource and save it to the cache
        new_datasource = Datasource(**req_new_datasource.json())
        self.api_client._wg_datasources_names[new_datasource.name] = new_datasource._id
        self.api_client._wg_datasources_urls[
            new_datasource.location
        ] = new_datasource._id

        # end of method
        return new_datasource

    @ApiDecorators._check_bearer_validity
    def delete(self, workgroup_id: str, datasource_id: str):
        """Delete a datasource from Isogeo database.

        :param str workgroup_id: identifier of the owner workgroup
        :param str datasource_id: identifier of the resource to delete
        """
        # check workgroup UUID
        if not checker.check_is_uuid(workgroup_id):
            raise ValueError(
                "Workgroup ID is not a correct UUID: {}".format(workgroup_id)
            )
        else:
            pass

        # check datasource UUID
        if not checker.check_is_uuid(datasource_id):
            raise ValueError(
                "Datasource ID is not a correct UUID: {}".format(datasource_id)
            )
        else:
            pass

        # request URL
        url_datasource_delete = utils.get_request_base_url(
            route="groups/{}/data-sources/{}".format(workgroup_id, datasource_id)
        )

        # request
        req_datasource_deletion = self.api_client.delete(
            url=url_datasource_delete,
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_datasource_deletion)
        if isinstance(req_check, tuple):
            return req_check

        return req_datasource_deletion

    @ApiDecorators._check_bearer_validity
    def exists(self, workgroup_id: str, datasource_id: str) -> bool:
        """Check if the specified datasource exists and is available for the authenticated user.

        :param str workgroup_id: identifier of the owner workgroup
        :param str datasource_id: identifier of the datasource to verify
        """
        # check workgroup UUID
        if not checker.check_is_uuid(workgroup_id):
            raise ValueError(
                "Workgroup ID is not a correct UUID: {}".format(workgroup_id)
            )
        else:
            pass

        # check datasource UUID
        if not checker.check_is_uuid(datasource_id):
            raise ValueError(
                "Datasource ID is not a correct UUID: {}".format(datasource_id)
            )
        else:
            pass

        # URL
        url_datasource_exists = utils.get_request_base_url(
            route="groups/{}/data-sources/{}".format(workgroup_id, datasource_id)
        )

        # request
        req_datasource_exists = self.api_client.get(
            url=url_datasource_exists,
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_datasource_exists)
        if isinstance(req_check, tuple):
            return req_check

        return req_datasource_exists

    @ApiDecorators._check_bearer_validity
    def update(
        self, workgroup_id: str, datasource: Datasource, caching: bool = 1
    ) -> Datasource:
        """Update a datasource owned by a workgroup.

        :param str workgroup_id: identifier of the owner workgroup
        :param class datasource: Datasource model object to update
        :param bool caching: option to cache the response
        """
        # check workgroup UUID
        if not checker.check_is_uuid(workgroup_id):
            raise ValueError(
                "Workgroup ID is not a correct UUID: {}".format(workgroup_id)
            )
        else:
            pass

        # check datasource UUID
        if not checker.check_is_uuid(datasource._id):
            raise ValueError(
                "Datasource ID is not a correct UUID: {}".format(datasource._id)
            )
        else:
            pass

        # URL
        url_datasource_update = utils.get_request_base_url(
            route="groups/{}/data-sources/{}".format(workgroup_id, datasource._id)
        )

        # request
        req_datasource_update = self.api_client.put(
            url=url_datasource_update,
            json=datasource.to_dict(),
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_datasource_update)
        if isinstance(req_check, tuple):
            return req_check

        # update datasource in cache
        new_datasource = Datasource(**req_datasource_update.json())
        if caching:
            self.api_client._wg_datasources_urls[
                new_datasource.location
            ] = new_datasource._id
            self.api_client._wg_datasources_names[
                new_datasource.name
            ] = new_datasource._id

        # end of method
        return new_datasource


# ##############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    """standalone execution."""
    api_datasource = ApiDatasource()
