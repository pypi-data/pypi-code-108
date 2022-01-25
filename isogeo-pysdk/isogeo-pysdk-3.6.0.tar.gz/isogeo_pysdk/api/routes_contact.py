# -*- coding: UTF-8 -*-
#! python3  # noqa E265

"""
    Isogeo API v1 - API Routes for Contacts entities

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
from isogeo_pysdk.enums import ContactRoles
from isogeo_pysdk.models import Contact, Metadata
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
class ApiContact:
    """Routes as methods of Isogeo API used to manipulate contacts."""

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
        super(ApiContact, self).__init__()

    @lru_cache()
    @ApiDecorators._check_bearer_validity
    def listing(
        self, workgroup_id: str = None, include: tuple = ("count",), caching: bool = 1
    ) -> list:
        """Get workgroup contacts.

        :param str workgroup_id: identifier of the owner workgroup
        :param tuple include: identifier of the owner workgroup
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
        url_contacts = utils.get_request_base_url(
            route="groups/{}/contacts".format(workgroup_id)
        )

        # request
        req_wg_contacts = self.api_client.get(
            url_contacts,
            headers=self.api_client.header,
            params=payload,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_wg_contacts)
        if isinstance(req_check, tuple):
            return req_check

        wg_contacts = req_wg_contacts.json()

        # if caching use or store the workgroup contacts
        if (
            caching
            and not self.api_client._wg_contacts_emails
            and not self.api_client._wg_contacts_names
        ):
            for i in wg_contacts:
                self.api_client._wg_contacts_emails[i.get("email")] = i.get("_id")
                self.api_client._wg_contacts_names[i.get("name")] = i.get("_id")

        # end of method
        return wg_contacts

    @ApiDecorators._check_bearer_validity
    def get(self, contact_id: str) -> Contact:
        """Get details about a specific contact.

        :param str contact_id: contact UUID
        """
        # check contact UUID
        if not checker.check_is_uuid(contact_id):
            raise ValueError("Contact ID is not a correct UUID.")
        else:
            pass

        # contact route
        url_contact = utils.get_request_base_url(route="contacts/{}".format(contact_id))

        # request
        req_contact = self.api_client.get(
            url_contact,
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_contact)
        if isinstance(req_check, tuple):
            return req_check

        # end of method
        return Contact(**req_contact.json())

    @ApiDecorators._check_bearer_validity
    def create(
        self, workgroup_id: str, contact: Contact, check_exists: int = 1
    ) -> Contact:
        """Add a new contact to a workgroup.

        :param str workgroup_id: identifier of the owner workgroup
        :param class contact: Contact model object to create
        :param int check_exists: check if a contact already exists inot the workgroup:

            - 0 = no check
            - 1 = compare name [DEFAULT]
            - 2 = compare email

        :returns: the created contact or the existing contact if case oof a matching name or email or a tuple with response error code
        :rtype: Contact
        """
        # check workgroup UUID
        if not checker.check_is_uuid(workgroup_id):
            raise ValueError("Workgroup ID is not a correct UUID.")
        else:
            pass

        # check if contact has a name (required by API)
        if not contact.name:
            raise ValueError("To create a contact, a name is required by the API.")
        else:
            pass

        # check if contact already exists in workgroup
        if check_exists == 1:
            # retrieve workgroup contacts
            if not self.api_client._wg_contacts_names:
                self.listing(workgroup_id=workgroup_id, include=())
            # check
            if contact.name in self.api_client._wg_contacts_names:
                logger.debug(
                    "Contact with the same name already exists: {}. Use 'contact_update' instead.".format(
                        contact.name
                    )
                )
                return self.get(self.api_client._wg_contacts_names.get(contact.name))
        elif check_exists == 2:
            # retrieve workgroup contacts
            if not self.api_client._wg_contacts_emails:
                self.listing(workgroup_id=workgroup_id, include=())
            # check
            if contact.email in self.api_client._wg_contacts_emails:
                logging.debug(
                    "Contact with the same email already exists: {}. Use 'contact_update' instead.".format(
                        contact.email
                    )
                )
                return self.get(self.api_client._wg_contacts_emails.get(contact.email))
        else:
            pass

        # build request url
        url_contact_create = utils.get_request_base_url(
            route="groups/{}/contacts".format(workgroup_id)
        )

        # request
        req_new_contact = self.api_client.post(
            url_contact_create,
            json=contact.to_dict_creation(),
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_new_contact)
        if isinstance(req_check, tuple):
            return req_check

        # load new contact and save it to the cache
        new_contact = Contact(**req_new_contact.json())
        self.api_client._wg_contacts_names[new_contact.name] = new_contact._id
        self.api_client._wg_contacts_emails[new_contact.email] = new_contact._id

        # end of method
        return new_contact

    @ApiDecorators._check_bearer_validity
    def delete(self, workgroup_id: str, contact_id: str):
        """Delete a contact from Isogeo database.

        :param str workgroup_id: identifier of the owner workgroup
        :param str contact_id: identifier of the resource to delete
        """
        # check workgroup UUID
        if not checker.check_is_uuid(workgroup_id):
            raise ValueError(
                "Workgroup ID is not a correct UUID: {}".format(workgroup_id)
            )
        else:
            pass

        # check contact UUID
        if not checker.check_is_uuid(contact_id):
            raise ValueError("Contact ID is not a correct UUID: {}".format(contact_id))
        else:
            pass

        # request URL
        url_contact_delete = utils.get_request_base_url(
            route="groups/{}/contacts/{}".format(workgroup_id, contact_id)
        )

        # request
        req_contact_deletion = self.api_client.delete(
            url_contact_delete,
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_contact_deletion)
        if isinstance(req_check, tuple):
            return req_check

        return req_contact_deletion

    @ApiDecorators._check_bearer_validity
    def exists(self, contact_id: str) -> bool:
        """Check if the specified contact exists and is available for the authenticated user.

        :param str contact_id: identifier of the contact to verify
        """
        # check contact UUID
        if not checker.check_is_uuid(contact_id):
            raise ValueError("Contact ID is not a correct UUID: {}".format(contact_id))
        else:
            pass

        # URL builder
        url_contact_exists = "{}{}".format(
            utils.get_request_base_url("contacts"), contact_id
        )

        # request
        req_contact_exists = self.api_client.get(
            url_contact_exists,
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_contact_exists)
        if isinstance(req_check, tuple):
            return req_check

        return req_contact_exists

    @ApiDecorators._check_bearer_validity
    def update(self, contact: Contact, caching: bool = 1) -> Contact:
        """Update a contact owned by a workgroup.

        :param class contact: Contact model object to update
        :param bool caching: option to cache the response
        """
        # check contact UUID
        if not checker.check_is_uuid(contact._id):
            raise ValueError("Contact ID is not a correct UUID: {}".format(contact._id))
        else:
            pass

        # URL
        url_contact_update = utils.get_request_base_url(
            route="groups/{}/contacts/{}".format(contact.owner.get("_id"), contact._id)
        )

        # request
        req_contact_update = self.api_client.put(
            url=url_contact_update,
            json=contact.to_dict(),
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_contact_update)
        if isinstance(req_check, tuple):
            return req_check

        # update contact in cache
        new_contact = Contact(**req_contact_update.json())
        if caching:
            self.api_client._wg_contacts_names[new_contact.name] = new_contact._id

        # end of method
        return new_contact

    # -- Routes to manage the related objects ------------------------------------------
    @ApiDecorators._check_bearer_validity
    def associate_metadata(
        self, metadata: Metadata, contact: Contact, role: str = "pointOfContact"
    ) -> Response:
        """Associate a metadata with a contact.

        If the specified contact is already associated, the response is still 200.

        :param Metadata metadata: metadata object to update
        :param Contact contact: contact model object to associate
        :param str role: role to assign to the contact

        :Example:

        .. code-block:: python

            # retrieve a metadata
            md = isogeo.metadata.get(METADATA_UUID)
            # retrieve a contact
            ctct = isogeo.contact.get(CONTACT_UUID)
            # associate a contact to a metadata
            isogeo.contact.associate_metadata(metadata = md, contact = ctct)
        """
        # check metadata UUID
        if not checker.check_is_uuid(metadata._id):
            raise ValueError(
                "Metadata ID is not a correct UUID: {}".format(metadata._id)
            )
        else:
            pass

        # check contact UUID
        if not checker.check_is_uuid(contact._id):
            raise ValueError("Contact ID is not a correct UUID: {}".format(contact._id))
        else:
            pass

        # check contact type
        if contact.type == "group" and not contact.available:
            raise TypeError(
                "Contact can't be associated because it's a group contact and it's not available."
            )
        else:
            pass

        # check role contact
        if role not in ContactRoles.__members__:
            raise ValueError(
                "Role '{}' is not an accepted value. Must be one of: {}".format(
                    role, " | ".join([e.name for e in ContactRoles])
                )
            )
        else:
            pass

        # URL
        url_contact_association = utils.get_request_base_url(
            route="resources/{}/contacts/{}".format(metadata._id, contact._id)
        )

        # request
        req_contact_association = self.api_client.put(
            url=url_contact_association,
            json={"role": role},
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_contact_association)
        if isinstance(req_check, tuple):
            return req_check

        # end of method
        return req_contact_association

    @ApiDecorators._check_bearer_validity
    def dissociate_metadata(self, metadata: Metadata, contact: Contact) -> Response:
        """Removes the association between a metadata and a contact.

        If the specified contact is not associated, the response is 404.

        :param Metadata metadata: metadata object to update
        :param Contact contact: contact model object to associate
        """
        # check metadata UUID
        if not checker.check_is_uuid(metadata._id):
            raise ValueError(
                "Metadata ID is not a correct UUID: {}".format(metadata._id)
            )
        else:
            pass

        # check contact UUID
        if not checker.check_is_uuid(contact._id):
            raise ValueError("Contact ID is not a correct UUID: {}".format(contact._id))
        else:
            pass

        # URL
        url_contact_dissociation = utils.get_request_base_url(
            route="resources/{}/contacts/{}".format(metadata._id, contact._id)
        )

        # request
        req_contact_dissociation = self.api_client.delete(
            url=url_contact_dissociation,
            headers=self.api_client.header,
            proxies=self.api_client.proxies,
            verify=self.api_client.ssl,
            timeout=self.api_client.timeout,
        )

        # checking response
        req_check = checker.check_api_response(req_contact_dissociation)
        if isinstance(req_check, tuple):
            return req_check

        # end of method
        return req_contact_dissociation


# ##############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    """standalone execution."""
    api_contact = ApiContact()
    print(api_contact)
