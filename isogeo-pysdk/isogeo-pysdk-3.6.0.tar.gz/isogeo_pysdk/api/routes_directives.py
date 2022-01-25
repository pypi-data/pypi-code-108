# -*- coding: UTF-8 -*-
#! python3  # noqa E265

"""
    Isogeo API v1 - API Routes to retrieve EU environment code Directives used as INSPIRE limitations

    See: http://help.isogeo.com/api/complete/index.html
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import logging

# submodules
from isogeo_pysdk.checker import IsogeoChecker
from isogeo_pysdk.decorators import ApiDecorators
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
class ApiDirective:
    """Routes as methods of Isogeo API used to manipulate directives (Europe Environment code for
    INSPIRE limitations)."""

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
        super(ApiDirective, self).__init__()

    @ApiDecorators._check_bearer_validity
    def listing(self, caching: bool = 1) -> list:
        """Get directives.

        :param bool caching: option to cache the response
        """
        # request URL
        url_directives = utils.get_request_base_url(route="directives")

        # request
        req_directives = self.api_client.get(
            url=url_directives,
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_directives)
        if isinstance(req_check, tuple):
            return req_check

        directives = req_directives.json()

        # if caching use or store the workgroup directives
        if caching and not self.api_client._directives:
            self.api_client._directives = directives

        # end of method
        return directives


# ##############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    """standalone execution."""
    api_directive = ApiDirective()
