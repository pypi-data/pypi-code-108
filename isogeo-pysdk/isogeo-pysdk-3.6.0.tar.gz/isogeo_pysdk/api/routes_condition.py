# -*- coding: UTF-8 -*-
#! python3  # noqa E265

"""
    Isogeo API v1 - API Routes for Conditions entities

    See: http://help.isogeo.com/api/complete/index.html
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import logging
from functools import lru_cache

# 3rd party
from requests import Response

# submodules
from isogeo_pysdk.checker import IsogeoChecker
from isogeo_pysdk.decorators import ApiDecorators
from isogeo_pysdk.models import Condition, License, Metadata
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
class ApiCondition:
    """Routes as methods of Isogeo API used to manipulate conditions."""

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
        super(ApiCondition, self).__init__()

    @lru_cache()
    @ApiDecorators._check_bearer_validity
    def listing(self, metadata_id: str) -> list:
        """List metadata's conditions with complete information.

        :param str metadata_id: metadata UUID

        :returns: the list of conditions associated with the metadata
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
        url_metadata_conditions = utils.get_request_base_url(
            route="resources/{}/conditions/".format(metadata_id)
        )

        # request
        req_metadata_conditions = self.api_client.get(
            url=url_metadata_conditions,
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_metadata_conditions)
        if isinstance(req_check, tuple):
            return req_check

        # end of method
        return req_metadata_conditions.json()

    @lru_cache()
    @ApiDecorators._check_bearer_validity
    def get(self, metadata_id: str, condition_id: str) -> Condition:
        """Get details about a specific condition.

        :param str metadata_id: identifier of the owner workgroup
        :param str condition_id: condition UUID
        """
        # check workgroup UUID
        if not checker.check_is_uuid(metadata_id):
            raise ValueError(
                "Metadata ID is not a correct UUID: {}".format(metadata_id)
            )
        else:
            pass
        # check condition UUID
        if not checker.check_is_uuid(condition_id):
            raise ValueError(
                "Condition ID is not a correct UUID: {}".format(condition_id)
            )
        else:
            pass

        # condition route
        url_condition = utils.get_request_base_url(
            route="resources/{}/conditions/{}".format(metadata_id, condition_id)
        )

        # request
        req_condition = self.api_client.get(
            url=url_condition,
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_condition)
        if isinstance(req_check, tuple):
            return req_check

        # extend response with uuid of prent metadata
        condition_returned = req_condition.json()
        condition_returned["parent_resource"] = metadata_id

        # end of method
        return Condition(**condition_returned)

    @ApiDecorators._check_bearer_validity
    def create(self, metadata: Metadata, condition: Condition) -> Condition:
        """Add a new condition (license + specific description) to a metadata.

        :param Metadata metadata: metadata object to update
        :param Condition condition: condition to create
        """
        # check metadata UUID
        if not checker.check_is_uuid(metadata._id):
            raise ValueError(
                "Metadata ID is not a correct UUID: {}".format(metadata._id)
            )
        else:
            pass

        # check license UUID
        if isinstance(condition.license, License) and not checker.check_is_uuid(
            condition.license._id
        ):
            raise ValueError(
                "License ID is not a correct UUID: {}".format(condition.license._id)
            )
        elif condition.license is None:
            logger.debug("Creating a condition without associated license.")
        else:
            pass

        # URL
        url_condition_create = utils.get_request_base_url(
            route="resources/{}/conditions".format(metadata._id)
        )

        # request
        req_condition_create = self.api_client.post(
            url=url_condition_create,
            json=condition.to_dict_creation(),
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_condition_create)
        if isinstance(req_check, tuple):
            return req_check

        # extend response with uuid of prent metadata
        condition_returned = req_condition_create.json()
        condition_returned["parent_resource"] = metadata._id

        # end of method
        return Condition(**condition_returned)

    @ApiDecorators._check_bearer_validity
    def delete(self, metadata: Metadata, condition: Condition) -> Response:
        """Removes a condition from a metadata.

        :param Metadata metadata: metadata object to update
        :param Condition condition: license model object to associate
        """
        # check metadata UUID
        if not checker.check_is_uuid(metadata._id):
            raise ValueError(
                "Metadata ID is not a correct UUID: {}".format(metadata._id)
            )
        else:
            pass

        # check license UUID
        if not checker.check_is_uuid(condition._id):
            raise ValueError(
                "Condition ID is not a correct UUID: {}".format(condition._id)
            )
        else:
            pass

        # URL
        url_condition_delete = utils.get_request_base_url(
            route="resources/{}/conditions/{}".format(metadata._id, condition._id)
        )

        # request
        req_condition_delete = self.api_client.delete(
            url=url_condition_delete,
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_condition_delete)
        if isinstance(req_check, tuple):
            return req_check

        # end of method
        return req_condition_delete


# ##############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    """standalone execution."""
    api_condition = ApiCondition()
