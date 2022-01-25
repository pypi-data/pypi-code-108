# -*- coding: UTF-8 -*-
#! python3  # noqa E265

"""
    Isogeo API v1 - API Routes for Invitations entities

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
from isogeo_pysdk.models import Invitation
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
class ApiInvitation:
    """Routes as methods of Isogeo API used to manipulate invitations."""

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
        super(ApiInvitation, self).__init__()

    # -- Routes to manage the  Invitation objects within a workgroup ---------------------------------------

    @ApiDecorators._check_bearer_validity
    def listing(self, workgroup_id: str) -> list:
        """Returns pending invitations (including expired) for the specified workgroup.

        :param str workgroup_id: workgroup UUID
        """
        # check workgroup UUID
        if not checker.check_is_uuid(workgroup_id):
            raise ValueError(
                "Workgroup ID is not a correct UUID: {}".format(workgroup_id)
            )
        else:
            pass

        # URL builder
        url_workgroup_invitations = utils.get_request_base_url(
            route="groups/{}/invitations".format(workgroup_id)
        )

        # request
        req_workgroup_invitations = self.api_client.get(
            url=url_workgroup_invitations,
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_workgroup_invitations)
        if isinstance(req_check, tuple):
            return req_check

        return req_workgroup_invitations.json()

    @ApiDecorators._check_bearer_validity
    def create(
        self, workgroup_id: str, invitation: object = Invitation()
    ) -> Invitation:
        """Add a new invitation to Isogeo.

        :param class invitation: Invitation model object to create

        :rtype: Invitation

        :Example:
        >>> # create the invitation locally
        >>> invit = Invitation(
            email="prenom.nom@organisation.com",
            role="admin"
            )
        >>> # send the invitation
        >>> isogeo.invitation.create(WORKGROUP_UUID, new_invit)
        """
        # URL
        url_invitation_create = utils.get_request_base_url(
            route="groups/{}/invitations".format(workgroup_id)
        )

        # request
        req_new_invitation = self.api_client.post(
            url=url_invitation_create,
            data=invitation.to_dict_creation(),
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_new_invitation)
        if isinstance(req_check, tuple):
            return req_check

        # end of method
        return Invitation(**req_new_invitation.json())

    # -- Routes to manage the  Invitation objects at teh global level ---------------------------------------
    @ApiDecorators._check_bearer_validity
    def get(self, invitation_id: str) -> Invitation:
        """Get details about a specific invitation.

        :param str invitation_id: invitation UUID
        """
        # check invitation UUID
        if not checker.check_is_uuid(invitation_id):
            raise ValueError("Invitation ID is not a correct UUID.")
        else:
            pass

        # URL
        url_invitation = utils.get_request_base_url(
            route="invitations/{}".format(invitation_id)
        )

        # request
        req_invitation = self.api_client.get(
            url=url_invitation,
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_invitation)
        if isinstance(req_check, tuple):
            return req_check

        # end of method
        return Invitation(**req_invitation.json())

    @ApiDecorators._check_bearer_validity
    def accept(self, invitation: object = Invitation) -> Invitation:
        """Accept the invitation to join an Isogeo Workgroup.

        :param class invitation: Invitation model object to accept
        """
        # URL
        url_invitation_accept = utils.get_request_base_url(
            route="invitations/{}/accept".format(invitation._id)
        )

        # request
        req_new_invitation = self.api_client.post(
            url=url_invitation_accept,
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_new_invitation)
        if isinstance(req_check, tuple):
            return req_check

        print(req_new_invitation.json())

        # load new invitation and save it to the cache
        new_invitation = Invitation(**req_new_invitation.json())
        self.api_client._invitations_names[
            new_invitation.group.get("name")
        ] = new_invitation._id

        # end of method
        return new_invitation

    @ApiDecorators._check_bearer_validity
    def decline(self, invitation: object = Invitation) -> Invitation:
        """Decline the invitation to join an Isogeo Workgroup.

        :param class invitation: Invitation model object to decline
        """
        # URL
        url_invitation_refuse = utils.get_request_base_url(
            route="invitations/{}/refuse".format(invitation._id)
        )

        # request
        req_new_invitation = self.api_client.post(
            url=url_invitation_refuse,
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_new_invitation)
        if isinstance(req_check, tuple):
            return req_check

        print(req_new_invitation.json())

        # load new invitation and save it to the cache
        new_invitation = Invitation(**req_new_invitation.json())
        self.api_client._invitations_names[
            new_invitation.group.get("name")
        ] = new_invitation._id

        # end of method
        return new_invitation

    @ApiDecorators._check_bearer_validity
    def delete(self, invitation_id: str):
        """Delete an invitation from Isogeo database.

        :param str invitation_id: identifier of the invitation
        """
        # check invitation UUID
        if not checker.check_is_uuid(invitation_id):
            raise ValueError(
                "Invitation ID is not a correct UUID: {}".format(invitation_id)
            )
        else:
            pass

        # URL
        url_invitation_delete = utils.get_request_base_url(
            route="invitations/{}".format(invitation_id)
        )

        # request
        req_invitation_deletion = self.api_client.delete(
            url=url_invitation_delete,
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_invitation_deletion)
        if isinstance(req_check, tuple):
            return req_check

        return req_invitation_deletion

    @ApiDecorators._check_bearer_validity
    def update(self, invitation: Invitation) -> Invitation:
        """Update a invitation owned by a invitation.

        :param class invitation: Invitation model object to update
        """
        # check invitation UUID
        if not checker.check_is_uuid(invitation._id):
            raise ValueError(
                "Invitation ID is not a correct UUID: {}".format(invitation._id)
            )
        else:
            pass

        # URL
        url_invitation_update = utils.get_request_base_url(
            route="invitations/{}".format(invitation._id)
        )

        # request
        req_invitation_update = self.api_client.put(
            url=url_invitation_update,
            json=invitation.to_dict(),
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_invitation_update)
        if isinstance(req_check, tuple):
            return req_check

        # end of method
        return Invitation(**req_invitation_update.json())


# ##############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    """standalone execution."""
    api_invitation = ApiInvitation()
