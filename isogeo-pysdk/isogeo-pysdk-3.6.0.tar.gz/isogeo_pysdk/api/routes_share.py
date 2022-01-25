# -*- coding: UTF-8 -*-
#! python3  # noqa E265

"""
    Isogeo API v1 - API Routes for Shares entities

    See: http://help.isogeo.com/api/complete/index.html
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import logging
from functools import lru_cache

# 3rd party
from requests.models import Response

# submodules
from isogeo_pysdk.checker import IsogeoChecker
from isogeo_pysdk.decorators import ApiDecorators
from isogeo_pysdk.models import Application, Catalog, Share, Workgroup
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
class ApiShare:
    """Routes as methods of Isogeo API used to manipulate shares."""

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
        super(ApiShare, self).__init__()

    # -- Routes to manage the object ---------------------------------------------------
    @lru_cache()
    @ApiDecorators._check_bearer_validity
    def listing(self, workgroup_id: str = None, caching: bool = 1) -> list:
        """Get all shares which are accessible by the authenticated user OR shares for a workgroup.

        :param str workgroup_id: identifier of the owner workgroup. If `None`, then list shares for the autenticated user
        :param bool caching: option to cache the response
        """
        # URL
        if workgroup_id is not None:
            logger.debug("Listing shares for a workgroup: {}".format(workgroup_id))
            if not checker.check_is_uuid(workgroup_id):
                raise ValueError("Workgroup ID is not a correct UUID.")
            else:
                url_shares = utils.get_request_base_url(
                    route="groups/{}/shares".format(workgroup_id)
                )
        else:
            logger.debug("Listing shares for the authenticated application/user")
            url_shares = utils.get_request_base_url(route="shares")

        # request
        req_shares = self.api_client.get(
            url=url_shares,
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=(5, 200),
        )

        # checking response
        req_check = checker.check_api_response(req_shares)
        if isinstance(req_check, tuple):
            return req_check

        shares = req_shares.json()

        # if caching use or store the workgroup shares
        if caching and workgroup_id is None:
            self.api_client._shares = shares
        elif caching:
            self.api_client._wg_shares = shares
        else:
            pass

        # end of method
        return shares

    @ApiDecorators._check_bearer_validity
    def get(self, share_id: str, include: tuple = ("_abilities", "groups")) -> Share:
        """Returns details about a specific share.

        :param str share_id: share UUID
        :param tuple inlude: additionnal subresource to include in the response
        """
        # check share UUID
        if not checker.check_is_uuid(share_id):
            raise ValueError("Share ID is not a correct UUID.")
        else:
            pass

        # handling request parameters
        if isinstance(include, (tuple, list)):
            payload = {"_include": ",".join(include)}
        else:
            payload = None

        # URL
        url_share = utils.get_request_base_url(route="shares/{}".format(share_id))

        # request
        req_share = self.api_client.get(
            url=url_share,
            headers=self.api_client.header,
            params=payload,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_share)
        if isinstance(req_check, tuple):
            return req_check

        # end of method
        return Share(**req_share.json())

    @ApiDecorators._check_bearer_validity
    def create(
        self, workgroup_id: str, share: object = Share(), check_exists: int = 1
    ) -> Share:
        """Add a new share to Isogeo.

        :param str workgroup_id: identifier of the owner workgroup
        :param Share share: Share model object to create
        :param int check_exists: check if a share already exists into the workgroup:

        - 0 = no check
        - 1 = compare name [DEFAULT]
        """
        # check if share already exists in workgroup
        if check_exists == 1:
            # retrieve workgroup shares
            if not self.api_client._wg_shares:
                share.listing()
            # check
            if share.name in self.api_client._wg_shares:
                logger.debug(
                    "Share with the same name already exists: {}. Use 'share_update' instead.".format(
                        share.name
                    )
                )
                return False
        else:
            pass

        # URL
        url_share_create = utils.get_request_base_url(
            route="groups/{}/shares".format(workgroup_id)
        )

        # request
        req_new_share = self.api_client.post(
            url=url_share_create,
            json=share.to_dict_creation(),
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_new_share)
        if isinstance(req_check, tuple):
            return req_check

        # load new share and save it to the cache
        new_share = Share(**req_new_share.json())
        self.api_client._shares[new_share.name] = new_share._id

        # end of method
        return new_share

    @ApiDecorators._check_bearer_validity
    def delete(self, share_id: str) -> Response:
        """Delete a share from Isogeo database.

        :param str share_id: identifier of the resource to delete
        """
        # check share UUID
        if not checker.check_is_uuid(share_id):
            raise ValueError("Share ID is not a correct UUID: {}".format(share_id))
        else:
            pass

        # request URL
        url_share_delete = utils.get_request_base_url(
            route="shares/{}".format(share_id)
        )

        # request
        req_share_deletion = self.api_client.delete(
            url=url_share_delete,
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_share_deletion)
        if isinstance(req_check, tuple):
            return req_check

        return req_share_deletion

    @ApiDecorators._check_bearer_validity
    def exists(self, share_id: str) -> bool:
        """Check if the specified share exists and is available for the authenticated user.

        :param str share_id: identifier of the share to verify
        """
        # check share UUID
        if not checker.check_is_uuid(share_id):
            raise ValueError("Share ID is not a correct UUID: {}".format(share_id))
        else:
            pass

        # URL
        url_share_exists = utils.get_request_base_url(
            route="shares/{}".format(share_id)
        )

        # request
        req_share_exists = self.api_client.get(
            url=url_share_exists,
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_share_exists)
        if isinstance(req_check, tuple):
            return req_check

        return req_share_exists

    @ApiDecorators._check_bearer_validity
    def update(self, share: Share, caching: bool = 1) -> Share:
        """Update a share owned by a workgroup.

        :param Share share: Share model object to update
        :param bool caching: option to cache the response
        """
        # check share UUID
        if not checker.check_is_uuid(share._id):
            raise ValueError("Share ID is not a correct UUID: {}".format(share._id))
        else:
            pass

        # URL
        url_share_update = utils.get_request_base_url(
            route="shares/{}".format(share._id)
        )

        # request
        req_share_update = self.api_client.put(
            url=url_share_update,
            json=share.to_dict_creation(),
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_share_update)
        if isinstance(req_check, tuple):
            return req_check

        # update share in cache
        new_share = Share(**req_share_update.json())
        if caching:
            self.api_client._shares[new_share.name] = new_share._id

        # end of method
        return new_share

    # -- Routes which are really specific ----------------------------------------------
    @ApiDecorators._check_bearer_validity
    def reshare(self, share: Share, reshare: bool = 1) -> Share:
        """Enable/disable the reshare option for the given share.

        Only available for shares of type 'group'.

        :param Share share: Share model object to update
        :param bool reshare: set option to allow recipients groups
        """
        # check share UUID
        if not checker.check_is_uuid(share._id):
            raise ValueError("Share ID is not a correct UUID: {}".format(share._id))
        else:
            pass

        # check share type
        if share.type != "group":
            raise TypeError(
                "Bad share type. Must be 'group', found {}".format(share.type)
            )
        else:
            pass

        # determine if a request is required or can be avoided
        if reshare and share.rights == ["reshare"]:
            logger.info("Share has already reshare right enabled.")
            return share
        elif not reshare and not share.rights:
            logger.info("Share has already reshare right disabled.")
            return share
        else:
            pass

        # set new state
        if reshare:
            share.rights = ["reshare"]
        else:
            share.rights = []

        # URL
        url_share_refresh = utils.get_request_base_url(
            route="shares/{}".format(share._id)
        )

        # request
        req_share_refresh = self.api_client.put(
            url=url_share_refresh,
            json=share.to_dict_creation(),
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_share_refresh)
        if isinstance(req_check, tuple):
            return req_check

        # end of method
        return Share(**req_share_refresh.json())

    @ApiDecorators._check_bearer_validity
    def refresh_token(self, share: Share) -> Share:
        """Refresh the URL token of a share, used by Cartotheque, CSW, OpenCatalog.

        :param Share share: Share model object to update
        """
        # check share UUID
        if not checker.check_is_uuid(share._id):
            raise ValueError("Share ID is not a correct UUID: {}".format(share._id))
        else:
            pass

        # URL
        url_share_refresh = utils.get_request_base_url(
            route="shares/{}/refresh-token".format(share._id)
        )

        # request
        req_share_refresh = self.api_client.post(
            url=url_share_refresh,
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_share_refresh)
        if isinstance(req_check, tuple):
            return req_check

        # end of method
        return Share(**req_share_refresh.json())

    # -- Routes to manage the related objects ------------------------------------------
    @ApiDecorators._check_bearer_validity
    def associate_application(self, share: Share, application: Application) -> tuple:
        """Associate a share with an application.

        :param Share share: share model object to update
        :param Application application: application object to associate
        """
        # check share UUID
        if not checker.check_is_uuid(share._id):
            raise ValueError("Share ID is not a correct UUID: {}".format(share._id))
        else:
            pass

        # check application UUID
        if not checker.check_is_uuid(application._id):
            raise ValueError(
                "Application ID is not a correct UUID: {}".format(application._id)
            )
        else:
            pass

        # check share type
        if share.type != "application":
            raise TypeError(
                "Bad share type. Must be 'application', found {}".format(share.type)
            )
        else:
            pass

        # URL
        url_share_association = utils.get_request_base_url(
            route="shares/{}/applications/{}".format(share._id, application._id)
        )

        # request
        req_share_association = self.api_client.put(
            url=url_share_association,
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_share_association)
        if isinstance(req_check, tuple):
            return req_check

        # end of method
        return req_share_association

    @ApiDecorators._check_bearer_validity
    def dissociate_application(self, share: Share, application: Application) -> tuple:
        """Removes the association between the specified share and the specified application.

        :param Share share: share model object to update
        :param Application application: object to associate
        """
        # check share UUID
        if not checker.check_is_uuid(share._id):
            raise ValueError("Share ID is not a correct UUID: {}".format(share._id))
        else:
            pass

        # check application UUID
        if not checker.check_is_uuid(application._id):
            raise ValueError(
                "Application ID is not a correct UUID: {}".format(application._id)
            )
        else:
            pass

        # check share type
        if share.type != "application":
            raise TypeError(
                "Bad share type. Must be 'application', found {}".format(share.type)
            )
        else:
            pass

        # URL
        url_share_dissociation = utils.get_request_base_url(
            route="shares/{}/applications/{}".format(share._id, application._id)
        )

        # request
        req_share_dissociation = self.api_client.delete(
            url=url_share_dissociation,
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_share_dissociation)
        if isinstance(req_check, tuple):
            return req_check

        # end of method
        return req_share_dissociation

    @ApiDecorators._check_bearer_validity
    def associate_catalog(self, share: Share, catalog: Catalog) -> tuple:
        """Associate a share with a catalog.

        :param Share share: share model object to update
        :param Catalog catalog: object to associate
        """
        # check share UUID
        if not checker.check_is_uuid(share._id):
            raise ValueError("Share ID is not a correct UUID: {}".format(share._id))
        else:
            pass

        # check catalog UUID
        if not checker.check_is_uuid(catalog._id):
            raise ValueError("Catalog ID is not a correct UUID: {}".format(catalog._id))
        else:
            pass

        # URL
        url_share_association = utils.get_request_base_url(
            route="shares/{}/catalogs/{}".format(share._id, catalog._id)
        )

        # request
        req_share_association = self.api_client.put(
            url=url_share_association,
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_share_association)
        if isinstance(req_check, tuple):
            return req_check

        # end of method
        return req_share_association

    @ApiDecorators._check_bearer_validity
    def dissociate_catalog(self, share: Share, catalog: Catalog) -> tuple:
        """Removes the association between the specified share and the specified catalog.

        :param Share share: share model object to update
        :param Catalog catalog: object to associate
        """
        # check share UUID
        if not checker.check_is_uuid(share._id):
            raise ValueError("Share ID is not a correct UUID: {}".format(share._id))
        else:
            pass

        # check catalog UUID
        if not checker.check_is_uuid(catalog._id):
            raise ValueError("Catalog ID is not a correct UUID: {}".format(catalog._id))
        else:
            pass

        # URL
        url_share_dissociation = utils.get_request_base_url(
            route="shares/{}/catalogs/{}".format(share._id, catalog._id)
        )

        # request
        req_share_dissociation = self.api_client.delete(
            url=url_share_dissociation,
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_share_dissociation)
        if isinstance(req_check, tuple):
            return req_check

        # end of method
        return req_share_dissociation

    @ApiDecorators._check_bearer_validity
    def associate_group(self, share: Share, group: Workgroup) -> Response:
        """Associate a group with a share of type 'group'.

        If the specified group is already associated, the response is still 204.

        :param Share share: share model object to update
        :param Workgroup group: group object to associate
        """
        # check share UUID
        if not checker.check_is_uuid(share._id):
            raise ValueError("Share ID is not a correct UUID: {}".format(share._id))
        else:
            pass

        # check group UUID
        if not checker.check_is_uuid(group._id):
            raise ValueError("Workgroup ID is not a correct UUID: {}".format(group._id))
        else:
            pass

        # check share type
        if share.type != "group":
            raise TypeError(
                "Bad share type. Must be 'group', found {}".format(share.type)
            )
        else:
            pass

        # URL
        url_share_association = utils.get_request_base_url(
            route="shares/{}/groups/{}".format(share._id, group._id)
        )

        # request
        req_share_association = self.api_client.put(
            url=url_share_association,
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_share_association)
        if isinstance(req_check, tuple):
            return req_check

        # end of method
        return req_share_association

    @ApiDecorators._check_bearer_validity
    def dissociate_group(self, share: Share, group: Workgroup) -> tuple:
        """Removes the association between the specified share and the specified group.

        If the specified group is associated, the association is removed, Response is 204.
        If not, the Response is 500.

        :param Share share: share model object to update
        :param Workgroup group: object to associate
        """
        # check share UUID
        if not checker.check_is_uuid(share._id):
            raise ValueError("Share ID is not a correct UUID: {}".format(share._id))
        else:
            pass

        # check group UUID
        if not checker.check_is_uuid(group._id):
            raise ValueError("Workgroup ID is not a correct UUID: {}".format(group._id))
        else:
            pass

        # check share type
        if share.type != "group":
            raise TypeError(
                "Bad share type. Must be 'group', found {}".format(share.type)
            )
        else:
            pass

        # URL
        url_share_dissociation = utils.get_request_base_url(
            route="shares/{}/groups/{}".format(share._id, group._id)
        )

        # request
        req_share_dissociation = self.api_client.delete(
            url=url_share_dissociation,
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_share_dissociation)
        if isinstance(req_check, tuple):
            return req_check

        # end of method
        return req_share_dissociation


# ##############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    """standalone execution."""
    api_share = ApiShare()
