#! python3  # noqa E265

"""Module to easily get versions about Isogeo platform components."""

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import logging
from functools import lru_cache

# 3rd party
from requests import Session

# submodules
from isogeo_pysdk.checker import IsogeoChecker
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
class ApiAbout:
    """Routes as methods of Isogeo API used to get platform informations."""

    def __init__(
        self, platform: str = "prod", proxies: dict = None, protocol: str = "https"
    ):
        self.proxies = proxies
        self.protocol = protocol

        # ensure platform and others params to request
        (
            self.platform,
            self.api_url,
            self.app_url,
            self.csw_url,
            self.mng_url,
            self.oc_url,
            self.ssl,
        ) = utils.set_base_url(platform)
        # initialize
        super(ApiAbout, self).__init__()

    @lru_cache()
    def api(self) -> str:
        """Get API version."""
        with Session() as req_session:
            req_session.proxies = self.proxies
            # request URL
            url_account = utils.get_request_base_url(route="about", prot=self.protocol)

            # request
            req_api_version = req_session.get(
                url=url_account, proxies=self.proxies, verify=self.ssl
            )

        # checking response
        req_check = checker.check_api_response(req_api_version)
        if isinstance(req_check, tuple):
            return req_check

        # end of method
        return req_api_version.json().get("version")

    @lru_cache()
    def database(self) -> str:
        """Get database version."""
        with Session() as req_session:
            req_session.proxies = self.proxies
            # request URL
            url_account = utils.get_request_base_url(
                route="about/{}".format("database"), prot=self.protocol
            )

            # request
            req_api_version = req_session.get(
                url=url_account, proxies=self.proxies, verify=self.ssl
            )

        # checking response
        req_check = checker.check_api_response(req_api_version)
        if isinstance(req_check, tuple):
            return req_check

        # end of method
        return req_api_version.json().get("version")

    @lru_cache()
    def authentication(self) -> str:
        """Get authentication server (ID) version."""
        with Session() as req_session:
            req_session.proxies = self.proxies
            # request
            req_api_version = req_session.get(
                url="{}://id.{}.isogeo.com/about".format(self.protocol, self.api_url),
                proxies=self.proxies,
                verify=self.ssl,
            )

        # checking response
        req_check = checker.check_api_response(req_api_version)
        if isinstance(req_check, tuple):
            return req_check

        # end of method
        return req_api_version.json().get("version")

    @lru_cache()
    def scan(self) -> str:
        """Get daemon version."""
        with Session() as req_session:
            req_session.proxies = self.proxies
            # request
            req_api_version = req_session.get(
                url="{}://daemons.isogeo.com/about".format(self.protocol),
                proxies=self.proxies,
                verify=self.ssl,
            )

        # checking response
        req_check = checker.check_api_response(req_api_version)
        if isinstance(req_check, tuple):
            return req_check

        # end of method
        return req_api_version.json().get("version")

    @lru_cache()
    def services(self) -> str:
        """Get services.api version."""
        with Session() as req_session:
            req_session.proxies = self.proxies
            # request
            req_api_version = req_session.get(
                url="{}://services.{}.isogeo.com/about".format(
                    self.protocol, self.api_url
                ),
                proxies=self.proxies,
                verify=self.ssl,
            )

        # checking response
        req_check = checker.check_api_response(req_api_version)
        if isinstance(req_check, tuple):
            return req_check

        # end of method
        return req_api_version.json().get("version")


# ##############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    """standalone execution."""
    # PROD
    isogeo_about = ApiAbout()
    print(isogeo_about.api())
    print(isogeo_about.database())
    print(isogeo_about.authentication())
    print(isogeo_about.scan())
    print(isogeo_about.services())

    # QA
    isogeo_about = ApiAbout("qa")
    print(isogeo_about.api())
    print(isogeo_about.database())
    print(isogeo_about.authentication())
    print(isogeo_about.scan())
    print(isogeo_about.services())
