# -*- coding: UTF-8 -*-
#! python3  # noqa E265

"""
    Isogeo API v1 - API Routes for Thesaurus entities

    See: http://help.isogeo.com/api/complete/index.html
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import logging
from uuid import UUID

# submodules
from isogeo_pysdk.checker import IsogeoChecker
from isogeo_pysdk.decorators import ApiDecorators
from isogeo_pysdk.models import Thesaurus
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
class ApiThesaurus:
    """Routes as methods of Isogeo API used to manipulate thesaurus."""

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
        super(ApiThesaurus, self).__init__()

    @ApiDecorators._check_bearer_validity
    def thesauri(self, caching: bool = 1) -> list:
        """Get all thesauri."""
        # URL builder
        url_thesauri = utils.get_request_base_url(route="thesauri")

        # request
        req_thesauri = self.api_client.get(
            url=url_thesauri,
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_thesauri)
        if isinstance(req_check, tuple):
            return req_check

        thesauri = req_thesauri.json()

        # if caching use or store the workgroup specifications
        if caching and not self.api_client._thesauri_codes:
            self.api_client._wg_specifications_names = {
                i.get("code"): i.get("_id") for i in thesauri
            }

        # end of method
        return thesauri

    @ApiDecorators._check_bearer_validity
    def thesaurus(
        self,
        thesaurus_id: UUID = "1616597fbc4348c8b11ef9d59cf594c8",
        include: tuple = ("_abilities",),
    ) -> Thesaurus:
        """Get a thesaurus.

        :param str thesaurus_id: thesaurus UUID
        :param list include: subresources that should be returned. Available values:

          * '_abilities'
          * 'count'
        """
        # check thesaurus UUID
        if not checker.check_is_uuid(thesaurus_id):
            raise ValueError("Thesaurus ID is not a correct UUID.")
        else:
            pass

        # handling request parameters
        if isinstance(include, (tuple, list)):
            payload = {"_include": ",".join(include)}
        else:
            payload = None

        # URL builder
        url_thesaurus = utils.get_request_base_url(
            route="thesauri/{}".format(thesaurus_id)
        )

        # request
        req_thesaurus = self.api_client.get(
            url=url_thesaurus,
            headers=self.api_client.header,
            params=payload,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_thesaurus)
        if isinstance(req_check, tuple):
            return req_check

        # end of method
        return Thesaurus(**req_thesaurus.json())


# ##############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    """standalone execution."""
    api_thesaurus = ApiThesaurus()
