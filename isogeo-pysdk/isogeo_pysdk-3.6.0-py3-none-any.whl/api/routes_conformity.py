# -*- coding: UTF-8 -*-
#! python3  # noqa E265

"""
    Isogeo API v1 - API Routes for Conformity entities

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
from isogeo_pysdk.models import Conformity, Metadata
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
class ApiConformity:
    """Routes as methods of Isogeo API used to manipulate conformity with specifications."""

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
        super(ApiConformity, self).__init__()

    @lru_cache()
    @ApiDecorators._check_bearer_validity
    def listing(self, metadata_id: str) -> list:
        """List metadata's conformity specifications with complete information.

        :param str metadata_id: metadata UUID

        :returns: the list of specifications + conformity status associated with the metadata
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
        url_metadata_conformities = utils.get_request_base_url(
            route="resources/{}/specifications/".format(metadata_id)
        )

        # request
        req_metadata_conformities = self.api_client.get(
            url=url_metadata_conformities,
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_metadata_conformities)
        if isinstance(req_check, tuple):
            return req_check

        # end of method
        return req_metadata_conformities.json()

    @ApiDecorators._check_bearer_validity
    def create(self, metadata: Metadata, conformity: Conformity) -> Conformity:
        """Add a new conformity (specification + specific conformant) to a metadata.

        :param Metadata metadata: metadata object to update
        :param Conformity conformity: conformity to create
        """
        # check metadata UUID
        if not checker.check_is_uuid(metadata._id):
            raise ValueError(
                "Metadata ID is not a correct UUID: {}".format(metadata._id)
            )
        else:
            pass

        # check specification UUID
        if not checker.check_is_uuid(conformity.specification._id):
            raise ValueError(
                "Specification ID is not a correct UUID: {}".format(
                    conformity.specification._id
                )
            )
        else:
            pass

        # URL
        url_conformity_create = utils.get_request_base_url(
            route="resources/{}/specifications/{}".format(
                metadata._id, conformity.specification._id
            )
        )

        # request
        req_conformity_create = self.api_client.put(
            url=url_conformity_create,
            json=conformity.to_dict_creation(),
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_conformity_create)
        if isinstance(req_check, tuple):
            return req_check

        # extend response with uuid of prent metadata
        conformity_returned = req_conformity_create.json()
        conformity_returned["parent_resource"] = metadata._id

        # end of method
        return Conformity(**conformity_returned)

    @ApiDecorators._check_bearer_validity
    def delete(
        self,
        metadata: Metadata,
        conformity: Conformity = None,
        specification_id: str = None,
    ) -> Response:
        """Removes a conformity from a metadata.

        :param Metadata metadata: metadata object to update
        :param Conformity conformity: specification model object to associate. If empty, the specification_id must be passed.
        :param Specification specification_id: specification model object to associate. If empty, the conformity must be passed.
        """
        # check metadata UUID
        if not checker.check_is_uuid(metadata._id):
            raise ValueError(
                "Metadata ID is not a correct UUID: {}".format(metadata._id)
            )
        else:
            pass

        # get the specification UUID from the Conformity object
        if isinstance(conformity, Conformity):
            if not checker.check_is_uuid(conformity.specification._id):
                raise ValueError(
                    "Specification ID into the Conformity is not a correct UUID: {}".format(
                        conformity.specification._id
                    )
                )
            else:
                specification_id = conformity.specification._id
                pass

        # or use the passed specification UUID
        if not checker.check_is_uuid(specification_id):
            raise ValueError(
                "Specification ID into the Conformity is not a correct UUID: {}".format(
                    conformity.specification._id
                )
            )
        else:
            pass

        # URL
        url_conformity_delete = utils.get_request_base_url(
            route="resources/{}/specifications/{}".format(
                metadata._id, specification_id
            )
        )

        # request
        req_conformity_delete = self.api_client.delete(
            url=url_conformity_delete,
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_conformity_delete)
        if isinstance(req_check, tuple):
            return req_check

        # end of method
        return req_conformity_delete


# ##############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    """standalone execution."""
    api_conformity = ApiConformity()
