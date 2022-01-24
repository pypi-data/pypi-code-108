# Copyright 2021 StreamSets Inc.
"""Abstractions to interact with the Aster REST API."""
import base64
import datetime
import json
import logging
import os
import urllib3
from collections import namedtuple

import javaproperties
import requests
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15

from .exceptions import BadRequestError, InternalServerError
from .utils import get_params, join_url_parts

logger = logging.getLogger(__name__)

# The `#:` constructs at the end of assignments are part of Sphinx's autodoc functionality.
DEFAULT_ASTER_API_VERSION = 3  #:

# Headers required to get an access token (after passing authentication_token to POST).
ACCESS_TOKEN_REQUIRED_HEADERS = {'content-Type': 'application/x-www-form-urlencoded',
                                 'X-Requested-By': 'Aster'}

# Any headers that Aster requires for all calls should be added to this dictionary.
REQUIRED_HEADERS = {'X-Requested-By': 'Aster',
                    'X-SS-REST-CALL': 'true',
                    'content-type': 'application/json'}

EXPIRATION_EPOCH_MILLIS_PROP = 'expiration.epoch.millis'
EXPIRATION_WARNING_SECONDS = 60 * 60 * 24 * 7  # seconds in a week
PUBLIC_KEY = RSA.import_key("""-----BEGIN PUBLIC KEY-----
MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEA0zS736JSVr96i1vdrhyE
4rSGBu6Z1aMoWJN5KTEG6VektfubE70bwy+er6E1HAAmzxvf5SPfChIUbfzu6SSq
y/PCq+Z9waJ6XtvpbsNtREUTmuJeKGG3QCdt5jZtsVcZkDS6ECKSBB5MDvR5j2B6
fpyxzxyZDbPC8XzwU23kDDp+kks7gjHP4yq5niBx8bt5uegttrU3+z1jKuwhELaJ
rE7sjaJYhaCL/rSXy+5TYVXDPHbFbaAsUnyrDaGx615r+Pv2Hh3aZ8f3UihXVosa
Q/hsgBue6WyVggXyLOxQkJIO5ucZD3uzGmSaCsy0SqHOcKS6ijE4nWiT4nuw+vxH
4SNM5KOdzHewOEu7hcjixzxyrC4n9IWc+KboM34anigwUEZaXQouiUxP5mMwcxth
4sxj65HV5Fi7Hx63d+NAVefDgsd4SnLIZGEq+8aNCJPNgs8fHcgclcYjLpnoIIVG
Pss+mafT4com2FaPnaUQTHeWd1tdbkj8WthX3klKMCE/V/37sJdfPPWX8jM2nnaj
LRr2RStMuISF4Sdu/jQhM4lIpiRnmH8kRZXFl96xgZjVITDDQ50Mk+Q68MLUs9Zg
fP1NpydErGHV78PDyA6KIStnJdRRG6qzPUbxqhRWafhMRflsaGrFBZi+eg6QloI5
I5BMEDmwZ9fTBRVkzq3AVcECAwEAAQ==
-----END PUBLIC KEY-----""")


class ApiClient(object):
    """
    API client to communicate with a Aster instance.
    Args:
        server_url (:obj:`str`): Aster instance's server URL.
        authentication_token (:obj:`str`): Aster authentication_token.
        api_version (:obj:`int`, optional): The API version.
            Default: :py:const:`aster_api.DEFAULT_ASTER_API_VERSION`
        session_attributes (:obj:`dict`, optional): A dictionary of attributes to set on the underlying
            :py:class:`requests.Session` instance at initialization. Default: ``None``
        headers (:obj:`dict`, optional): A dictionary of headers to with the :py:class:`requests.Session` instance.
            Default: ``None``
    """
    def __init__(self,
                 server_url,
                 authentication_token,
                 api_version=DEFAULT_ASTER_API_VERSION,
                 session_attributes=None,
                 headers=None,
                 **kwargs):
        self._base_url = server_url
        self._authentication_token = authentication_token
        self._api_version = api_version
        self._session = requests.Session()
        self._session.headers.update(REQUIRED_HEADERS)
        if headers:
            self._session.headers.update(headers)
        if session_attributes:
            for attribute, value in session_attributes.items():
                setattr(self._session, attribute, value)
        if not self._session.verify:
            # If we disable SSL cert verification, we should disable warnings about having disabled it.
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def login(self):
        """Login to Aster.
        Running this endpoint will set the ``Authorization`` session header for this ApiClient instance.
        """
        self._session.headers['Authorization'] = 'Bearer {}'.format(self._authentication_token)

    def logout(self):
        """Logout of Aster.
        Running this endpoint will remove the ``Authorization`` session header.
        """
        del self._session.headers['Authorization']

    def get_current_user(self):
        """
        Get currently logged-in user info
        Returns:
            An instance of :py:class:`streamsets.sdk.aster_api.Command`
        """
        response = self._get(app='security', endpoint='v{0}/user-info'.format(self._api_version))
        return Command(self, response)

    # Organization User Resources
    def get_admin_org_users(self, org, page=None, search=None, size=None, sort=None):
        """Get the users of an organization. This is only available for sys-admin.

        Args:
            org (:obj:`str`): Org ID
            page (:obj:`int`, optional): Default: ``None``
            search (:obj:`str`, optional): Default: ``None``
            size (:obj:`int`, optional): Default: ``None``
            sort (:obj:`str`, optional): Default: ``None``

        Returns:
            An instance of :py:class:`streamsets.sdk.aster_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self', 'org'))
        response = self._get(app='security',
                             endpoint='v{}/admin/orgs/{}/users'.format(self._api_version, org),
                             params=params)
        return Command(self, response)

    def get_admin_org_user(self, org, user):
        """Get a user of an organization. This is only available for sys-admin.

        Args:
            org (:obj:`str`): Org ID
            user (:obj:`str`): User ID

        Returns:
            An instance of :py:class:`streamsets.sdk.aster_api.Command`.
        """
        endpoint = '/v{}/admin/orgs/{}/users/{}'.format(self._api_version, org, user)
        response = self._get(app='security',
                             endpoint=endpoint)
        return Command(self, response)

    def update_admin_org_user(self, org, payload, user):
        """Update a user of an organization. This is only available for sys-admin.

        Args:
            org (:obj:`str`): Org ID
            payload (:obj:`dict`): data - that complies with Swagger definition.
            user (:obj:`str`): User ID

        Returns:
            An instance of :py:class:`streamsets.sdk.aster_api.Command`.
        """
        endpoint = '/v{}/admin/orgs/{}/users/{}'.format(self._api_version, org, user)
        response = self._post(app='security',
                              data=payload,
                              endpoint=endpoint)
        return Command(self, response)

    def get_org_users(self, offset=None, page=None, size=None, paged=None, search=None,
                      sort_sorted=None, sort_unsorted=None, unpaged=None):
        """Get the org-users.

        Args:
            offset (:obj:`int`, optional): Default: ``None``
            page (:obj:`int`, optional): Default: ``None``
            size (:obj:`int`, optional): Default: ``None``
            paged (:obj:`str`, optional): Default: ``None``
            search (:obj:`str`, optional): Default: ``None``
            sort_sorted (:obj:`bool`, optional): Default: ``None``
            sort_unsorted (:obj:`bool`, optional): Default: ``None``
            unpaged (:obj:`bool`, optional): Default: ``None``

        Returns:
            An instance of :py:class:`streamsets.sdk.aster_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self', 'sort_sorted', 'sort_unsorted'))
        if sort_sorted is not None:
            params.update({'sort.sorted': sort_sorted})
        if sort_unsorted is not None:
            params.update({'sort.unsorted': sort_unsorted})
        response = self._get(app='security',
                             endpoint='v{}/org-users'.format(self._api_version),
                             params=params)
        return Command(self, response)

    def get_org_user(self, user_id):
        """Get the org-user for the given user ID.

        Args:
            user_id (:obj:`str`): User ID

        Returns:
            An instance of :py:class:`streamsets.sdk.aster_api.Command`.
        """
        response = self._get(app='security', endpoint='v{}/org-users/{}'.format(self._api_version, user_id))
        return Command(self, response)

    def update_org_user(self, user_id, body):
        """Update an org user.

        Args:
            user_id (:obj:`str`): User ID
            body (:obj:`dict`): data - that complies with Swagger definition.

        Returns:
            An instance of :py:class:`streamsets.sdk.aster_api.Command`.
        """
        endpoint = '/v{}/org-users/{}'.format(self._api_version, user_id)
        response = self._post(app='security',
                              data=body,
                              endpoint=endpoint)
        return Command(self, response)

    def delete_org_users(self, body):
        """Delete org user/s.

        Args:
            body (:obj:`dict`): data - that complies with Swagger definition.

        Returns:
            An instance of :py:class:`streamsets.sdk.aster_api.Command`.
        """
        endpoint = '/v{}/org-users.delete'.format(self._api_version)
        response = self._post(app='security',
                              data=body,
                              endpoint=endpoint)
        return Command(self, response)

    def delete_admin_org_users(self, org_id, body):
        """Delete org user/s.

        Args:
            org_id (:obj:`str`): Org ID.
            body (:obj:`dict`): data - that complies with Swagger definition.

        Returns:
            An instance of :py:class:`streamsets.sdk.aster_api.Command`.
        """
        endpoint = '/v{}/admin/orgs/{}/users.delete'.format(self._api_version, org_id)
        response = self._post(app='security',
                              data=body,
                              endpoint=endpoint)
        return Command(self, response)

    def activate_org_users(self, body):
        """Activate org user/s.

        Args:
            body (:obj:`dict`): data - that complies with Swagger definition.

        Returns:
            An instance of :py:class:`streamsets.sdk.aster_api.Command`.
        """
        endpoint = '/v{}/org-users.activate'.format(self._api_version)
        response = self._post(app='security',
                              data=body,
                              endpoint=endpoint)
        return Command(self, response)

    def deactivate_org_users(self, body):
        """Deactivate org user/s.

        Args:
            body (:obj:`dict`): data - that complies with Swagger definition.

        Returns:
            An instance of :py:class:`streamsets.sdk.aster_api.Command`.
        """
        endpoint = '/v{}/org-users.deactivate'.format(self._api_version)
        response = self._post(app='security',
                              data=body,
                              endpoint=endpoint)
        return Command(self, response)

    def invite_org_users(self, body):
        """Invite new user to join the org. An org admin can do this.

        Args:
            body (:obj:`dict`): Role and email - that complies with Swagger definition.

        Returns:
            An instance of :py:class:`streamsets.sdk.aster_api.Command`.
        """
        endpoint = '/v{}/org-users.invite'.format(self._api_version)
        response = self._post(app='security',
                              data=body,
                              endpoint=endpoint)
        return Command(self, response)

    def leave_org_users(self):
        """Leave org users.

        Returns:
            An instance of :py:class:`streamsets.sdk.aster_api.Command`.
        """
        endpoint = '/v{}/org-users.leave'.format(self._api_version)
        response = self._post(app='security', endpoint=endpoint)
        return Command(self, response)

    # Organization Resources
    def get_orgs(self, offset=None, page=None, size=None, paged=None, search=None,
                 sort_sorted=None, sort_unsorted=None, unpaged=None):
        """Get the organizations.

        Args:
            offset (:obj:`int`, optional): Default: ``None``
            page (:obj:`int`, optional): Default: ``None``
            size (:obj:`int`, optional): Default: ``None``
            paged (:obj:`str`, optional): Default: ``None``
            search (:obj:`str`, optional): Default: ``None``
            sort_sorted (:obj:`bool`, optional): Default: ``None``
            sort_unsorted (:obj:`bool`, optional): Default: ``None``
            unpaged (:obj:`bool`, optional): Default: ``None``

        Returns:
            An instance of :py:class:`streamsets.sdk.aster_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self', 'sort_sorted', 'sort_unsorted'))
        if sort_sorted is not None:
            params.update({'sort.sorted': sort_sorted})
        if sort_unsorted is not None:
            params.update({'sort.unsorted': sort_unsorted})
        response = self._get(app='security',
                             endpoint='v{}/orgs'.format(self._api_version),
                             params=params)
        return Command(self, response)

    def get_org(self, org_id):
        """Get the org for the given org ID.

        Args:
            org_id (:obj:`str`): Org ID

        Returns:
            An instance of :py:class:`streamsets.sdk.aster_api.Command`.
        """
        response = self._get(app='security', endpoint='v{}/orgs/{}'.format(self._api_version, org_id))
        return Command(self, response)

    def update_org(self, org_id, body):
        """Update an org.

        Args:
            org_id (:obj:`str`): Org ID
            body (:obj:`dict`): data - that complies with Swagger definition.

        Returns:
            An instance of :py:class:`streamsets.sdk.aster_api.Command`.
        """
        endpoint = '/v{}/orgs/{}'.format(self._api_version, org_id)
        response = self._post(app='security',
                              data=body,
                              endpoint=endpoint)
        return Command(self, response)

    # User Resources
    def get_user(self, user_id):
        """Get the users.

        Args:
            user_id (:obj:`str`): User ID

        Returns:
            An instance of :py:class:`streamsets.sdk.aster_api.Command`.
        """
        response = self._get(app='security',
                             endpoint='v{}/users/{}'.format(self._api_version, user_id))
        return Command(self, response)

    def update_user(self, user_id, body):
        """Update an user.

        Args:
            user_id (:obj:`str`): User ID
            body (:obj:`dict`): data - that complies with Swagger definition.

        Returns:
            An instance of :py:class:`streamsets.sdk.aster_api.Command`.
        """
        endpoint = '/v{}/users/{}'.format(self._api_version, user_id)
        response = self._post(app='security',
                              data=body,
                              endpoint=endpoint)
        return Command(self, response)

    def accept_tos(self):
        """Accept TOS.

        Returns:
            An instance of :py:class:`streamsets.sdk.aster_api.Command`.
        """
        endpoint = '/v{}/users.accept-tos'.format(self._api_version)
        response = self._post(app='security',
                              endpoint=endpoint)
        return Command(self, response)

    def create_org(self, body):
        """Create first org. after accepting TOS.

        Args:
            body (:obj:`dict`): Org name and zone - that complies with Swagger definition.

        Returns:
            An instance of :py:class:`streamsets.sdk.aster_api.Command`.
        """
        endpoint = '/v{}/orgs'.format(self._api_version)
        response = self._post(app='security',
                              data=body,
                              endpoint=endpoint)
        return Command(self, response)

    # Zone Resources
    def get_zones(self):
        """Get the zones.

        Returns:
            An instance of :py:class:`streamsets.sdk.aster_api.Command`.
        """
        response = self._get(app='security',
                             endpoint='v{}/zones'.format(self._api_version))
        return Command(self, response)

    # Admin organization resources
    def activate_failure(self, body):
        """Activate failure.

        Args:
            body (:obj:`dict`): data - that complies with Swagger definition.

        Returns:
            An instance of :py:class:`streamsets.sdk.aster_api.Command`.
        """
        endpoint = '/v{}/admin/failure/activate'.format(self._api_version)
        response = self._post(app='security',
                              data=body,
                              endpoint=endpoint)
        return Command(self, response)

    def deactivate_failure(self):
        """Deactivate failure.

        Returns:
            An instance of :py:class:`streamsets.sdk.aster_api.Command`.
        """
        response = self._get(app='security',
                             endpoint='/v{}/admin/failure/deactivate'.format(self._api_version))
        return Command(self, response)

    def get_admin_organizations(self, offset=None, page=None, size=None, paged=None,
                                search=None, sort_sorted=None, sort_unsorted=None, unpaged=None):
        """Get all the organizations. This is only available for sys-admin.

        Args:
            offset (:obj:`int`, optional): Default: ``None``
            page (:obj:`int`, optional): Default: ``None``
            size (:obj:`int`, optional): Default: ``None``
            paged (:obj:`str`, optional): Default: ``None``
            search (:obj:`str`, optional): Default: ``None``
            sort_sorted (:obj:`bool`, optional): Default: ``None``
            sort_unsorted (:obj:`bool`, optional): Default: ``None``
            unpaged (:obj:`bool`, optional): Default: ``None``

        Returns:
            An instance of :py:class:`streamsets.sdk.aster_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self', 'sort_sorted', 'sort_unsorted'))
        if sort_sorted is not None:
            params.update({'sort.sorted': sort_sorted})
        if sort_unsorted is not None:
            params.update({'sort.unsorted': sort_unsorted})
        response = self._get(app='security',
                             endpoint='v{}/admin/orgs'.format(self._api_version),
                             params=params)
        return Command(self, response)

    def get_admin_organization(self, org_id):
        """Get the organization. This is only available for sys-admin.

        Args:
            org_id (:obj:`str`): organization ID

        Returns:
            An instance of :py:class:`streamsets.sdk.aster_api.Command`.
        """
        response = self._get(app='security',
                             endpoint='v{}/admin/orgs/{}'.format(self._api_version, org_id))
        return Command(self, response)

    def create_admin_organization(self, body):
        """Create a new organization in a specific instance. This is only available for sys-admin.

        Args:
            body (:obj:`dict`): data - that complies with Swagger definition.

        Returns:
            An instance of :py:class:`streamsets.sdk.aster_api.Command`.
        """
        endpoint = '/v{}/admin/orgs'.format(self._api_version)
        response = self._post(app='security',
                              data=body,
                              endpoint=endpoint)
        return Command(self, response)

    def delete_admin_organizations(self, org_ids):
        """Delete the organizations. This is only available for sys-admin.

        Args:
            org_ids (:obj:`list`): the list of organization IDs to delete.

        Returns:
            An instance of :py:class:`streamsets.sdk.aster_api.Command`.
        """
        endpoint = '/v{}/admin/orgs.delete'.format(self._api_version)
        response = self._post(app='security',
                              data=org_ids,
                              endpoint=endpoint)
        return Command(self, response)

    def update_admin_organization(self, id, payload):
        """Update an organization. This is only available for sys-admin.

        Args:
            id (:obj:`str`): organization ID
            payload (:obj:`dict`): data - that complies with Swagger definition.

        Returns:
            An instance of :py:class:`streamsets.sdk.aster_api.Command`.
        """
        endpoint = '/v{}/admin/orgs/{}'.format(self._api_version, id)
        response = self._post(app='security',
                              data=payload,
                              endpoint=endpoint)
        return Command(self, response)

    # Admin instance Resources
    def get_admin_instances(self, offset=None, page=None, size=None, paged=None, search=None,
                            sort_sorted=None, sort_unsorted=None, unpaged=None):
        """Get the admin instances.

        Args:
            offset (:obj:`int`, optional): Default: ``None``
            page (:obj:`int`, optional): Default: ``None``
            size (:obj:`int`, optional): Default: ``None``
            paged (:obj:`str`, optional): Default: ``None``
            search (:obj:`str`, optional): Default: ``None``
            sort_sorted (:obj:`bool`, optional): Default: ``None``
            sort_unsorted (:obj:`bool`, optional): Default: ``None``
            unpaged (:obj:`bool`, optional): Default: ``None``

        Returns:
            An instance of :py:class:`streamsets.sdk.aster_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self', 'sort_sorted', 'sort_unsorted'))
        if sort_sorted is not None:
            params.update({'sort.sorted': sort_sorted})
        if sort_unsorted is not None:
            params.update({'sort.unsorted': sort_unsorted})
        response = self._get(app='security',
                             endpoint='v{}/admin/instances'.format(self._api_version),
                             params=params)
        return Command(self, response)

    def get_admin_instance(self, admin_instance_id):
        """Get an admin instance.

        Args:
            admin_instance_id (:obj:`str`): Admin instance ID

        Returns:
            An instance of :py:class:`streamsets.sdk.aster_api.Command`.
        """
        response = self._get(app='security',
                             endpoint='v{}/admin/instances/{}'.format(self._api_version, admin_instance_id))
        return Command(self, response)

    def create_admin_instance(self, body):
        """Create an admin instance.

        Args:
            body (:obj:`dict`): data - that complies with Swagger definition.

        Returns:
            An instance of :py:class:`streamsets.sdk.aster_api.Command`.
        """
        endpoint = '/v{}/admin/instances'.format(self._api_version)
        response = self._post(app='security',
                              data=body,
                              endpoint=endpoint)
        return Command(self, response)

    def update_admin_instance(self, admin_instance_id, body):
        """Update an admin instance.

        Args:
            admin_instance_id (:obj:`str`): Admin instance ID
            body (:obj:`dict`): data - that complies with Swagger definition.

        Returns:
            An instance of :py:class:`streamsets.sdk.aster_api.Command`.
        """
        endpoint = '/v{}/admin/instances/{}'.format(self._api_version, admin_instance_id)
        response = self._post(app='security',
                              data=body,
                              endpoint=endpoint)
        return Command(self, response)

    def delete_admin_instances(self, admin_zone_ids):
        """Delete an admin instances.

        Args:
            admin_zone_ids (:obj:`str`): Admin instance IDs

        Returns:
            An instance of :py:class:`streamsets.sdk.aster_api.Command`.
        """
        endpoint = '/v{}/admin/instances.delete'.format(self._api_version)
        response = self._post(app='security', endpoint=endpoint, data=admin_zone_ids)
        return Command(self, response)

    # Admin Zone Resources
    def get_admin_zones(self, offset=None, page=None, size=None, paged=None, search=None,
                        sort_sorted=None, sort_unsorted=None, unpaged=None):
        """Get the admin zones.

        Args:
            offset (:obj:`int`, optional): Default: ``None``
            page (:obj:`int`, optional): Default: ``None``
            size (:obj:`int`, optional): Default: ``None``
            paged (:obj:`str`, optional): Default: ``None``
            search (:obj:`str`, optional): Default: ``None``
            sort_sorted (:obj:`bool`, optional): Default: ``None``
            sort_unsorted (:obj:`bool`, optional): Default: ``None``
            unpaged (:obj:`bool`, optional): Default: ``None``

        Returns:
            An instance of :py:class:`streamsets.sdk.aster_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self', 'sort_sorted', 'sort_unsorted'))
        if sort_sorted is not None:
            params.update({'sort.sorted': sort_sorted})
        if sort_unsorted is not None:
            params.update({'sort.unsorted': sort_unsorted})
        response = self._get(app='security',
                             endpoint='v{}/admin/zones'.format(self._api_version),
                             params=params)
        return Command(self, response)

    def get_admin_zone(self, admin_zone_id):
        """Get an admin zone.

        Args:
            admin_zone_id (:obj:`str`): Admin zone ID

        Returns:
            An instance of :py:class:`streamsets.sdk.aster_api.Command`.
        """
        response = self._get(app='security',
                             endpoint='v{}/admin/zones/{}'.format(self._api_version, admin_zone_id))
        return Command(self, response)

    def create_admin_zone(self, body):
        """Create an admin zone.

        Args:
            body (:obj:`dict`): data - that complies with Swagger definition.

        Returns:
            An instance of :py:class:`streamsets.sdk.aster_api.Command`.
        """
        endpoint = '/v{}/admin/zones'.format(self._api_version)
        response = self._post(app='security',
                              data=body,
                              endpoint=endpoint)
        return Command(self, response)

    def update_admin_zone(self, admin_zone_id, body):
        """Update an admin zone.

        Args:
            admin_zone_id (:obj:`str`): Admin zone ID
            body (:obj:`dict`): data - that complies with Swagger definition.

        Returns:
            An instance of :py:class:`streamsets.sdk.aster_api.Command`.
        """
        endpoint = '/v{}/admin/zones/{}'.format(self._api_version, admin_zone_id)
        response = self._post(app='security',
                              data=body,
                              endpoint=endpoint)
        return Command(self, response)

    def delete_admin_zones(self, admin_zone_ids):
        """Delete admin zones.

        Args:
            admin_zone_ids (:obj:`str`): Admin zone IDs

        Returns:
            An instance of :py:class:`streamsets.sdk.aster_api.Command`.
        """
        endpoint = '/v{}/admin/zones.delete'.format(self._api_version)
        response = self._post(app='security', endpoint=endpoint, data=admin_zone_ids)
        return Command(self, response)

    # Admin Users Resource
    def get_admin_users(self, page=None, search=None, size=None, sort=None):
        """Get admin users. This is only available for sys-admin.

        Args:
            page (:obj:`int`, optional): Default: ``None``
            search (:obj:`str`, optional): Default: ``None``
            size (:obj:`int`, optional): Default: ``None``
            sort (:obj:`str`, optional): Default: ``None``

        Returns:
            An instance of :py:class:`streamsets.sdk.aster_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self'))
        response = self._get(app='security',
                             endpoint='v{}/admin/users'.format(self._api_version),
                             params=params)
        return Command(self, response)

    def get_admin_user(self, id):
        """Get admin users. This is only available for sys-admin.

        Args:
            id (:obj:`str`): User ID

        Returns:
            An instance of :py:class:`streamsets.sdk.aster_api.Command`.
        """
        endpoint ='v{}/admin/users/{}'.format(self._api_version, id)
        response = self._get(app='security',
                             endpoint=endpoint)
        return Command(self, response)

    # Event logs related
    def get_event_log(self, app_name, offset=None, pageNumber=None, pageSize=None,
                      paged=None, search=None, sort_sorted=None, sort_unsorted=None, unpaged=None):
        """
        Get event log for provided app

        Args:
            app_name (:obj:`str`): Name of the app e.g. security
            offset (:obj:`int`, optional): Default: ``None``
            pageNumber (:obj:`int`, optional): Default: ``None``
            pageSize (:obj:`str`, optional): Default: ``None``
            paged (:obj:`bool`, optional): Default: ``None``
            search (:obj:`str`, optional): Default: ``None``
            sort_sorted (:obj:`bool`, optional): Default: ``None``
            sort_unsorted (:obj:`bool`, optional): Default: ``None``
            unpaged (:obj:`bool`, optional): Default: ``None``

        Returns:
            An instance of :py:class:`streamsets.sdk.aster_api.Command`
        """
        params = get_params(parameters=locals(), exclusions=('self', 'app_name', 'sort_sorted', sort_unsorted))
        params.update({'sort.sorted': sort_sorted, 'sort.unsorted': sort_unsorted})
        response = self._get(app=app_name, endpoint='v{0}/eventlog'.format(self._api_version),
                             params=params)
        return Command(self, response)

    def get_event_log_for_an_event(self, app_name, event_id, offset=None, pageNumber=None,
                                   pageSize=None, paged=None, search=None, sort_sorted=None,
                                   sort_unsorted=None, unpaged=None):
        """
        Get event log for provided app for an event with passed id

        Args:
            app_name (:obj:`str`): Name of the app e.g. security
            event_id (:obj:`str`): ID of the event
            offset (:obj:`int`, optional): Default: ``None``
            pageNumber (:obj:`int`, optional): Default: ``None``
            pageSize (:obj:`str`, optional): Default: ``None``
            paged (:obj:`bool`, optional): Default: ``None``
            search (:obj:`str`, optional): Default: ``None``
            sort_sorted (:obj:`bool`, optional): Default: ``None``
            sort_unsorted (:obj:`bool`, optional): Default: ``None``
            unpaged (:obj:`bool`, optional): Default: ``None``

        Returns:
            An instance of :py:class:`streamsets.sdk.aster_api.Command`
        """
        params = get_params(parameters=locals(), exclusions=('self', 'event_id', 'app_name',
                                                             'sort_sorted', sort_unsorted))
        params.update({'sort.sorted': sort_sorted, 'sort.unsorted': sort_unsorted})
        response = self._get(app=app_name, endpoint='v{}/eventlog/{}'.format(self._api_version, event_id),
                             params=params)
        return Command(self, response)

    def return_all_releases(self):
        """
        Get all releases. e.g. SDC or Transformer

        Returns:
            An instance of :py:class:`streamsets.sdk.aster_api.Command`
        """
        response = self._get(app='entitlements', endpoint='v{0}/releases'.format(self._api_version),
                             params={'verify': True})
        return Command(self, response)

    def get_distribution(self, distribution_key, platform):
        """
        Get distribution. e.g. SDC or Transformer

        Args:
            distribution_key (:obj:`str`): Distribution key of the downloadable entity
            platform (:obj:`str`): Platform to download for

        Returns:
            An instance of :py:class:`streamsets.sdk.aster_api.Command`
        """
        params = get_params(parameters=locals(), exclusions=('self', 'distribution_key', 'platform'))
        params.update({'distributionKey': distribution_key, 'platform': platform})
        response = self._get(app='entitlements',
                             endpoint='v{}/releases/{}'.format(self._api_version, distribution_key),
                             params=params)
        return Command(self, response)

    def get_saml_configuration(self, draft, org=None):
        """Get the SAML configuration resource.

        Args:
            draft (:obj:`bool`): Whether this is a draft or not.
            org (:obj:`str`, optional): Organization id. Default: ``None``

        Returns:
            An instance of :py:class:`streamsets.sdk.aster_api.Command`
        """
        params = get_params(parameters=locals(), exclusions=('self'))
        response = self._get(app='security',
                             endpoint='v{}/saml'.format(self._api_version),
                             params=params)
        return Command(self, response)

    def create_saml_configuration(self, payload):
        """Create the SAML configuration resource.

        Args:
            payload (:obj:`dict`): data - that complies with Swagger definition.

        Returns:
            An instance of :py:class:`streamsets.sdk.aster_api.Command`
        """
        endpoint = 'v{}/saml'.format(self._api_version)
        response = self._post(app='security',
                              endpoint=endpoint,
                              data=payload)
        return Command(self, response)

    def copy_saml_configuration_to_production(self):
        """Copy the SAML configuration resource to production.

        Returns:
            An instance of :py:class:`streamsets.sdk.aster_api.Command`
        """
        endpoint = 'v{}/saml.copy-to-production'.format(self._api_version)
        response = self._post(app='security',
                              endpoint=endpoint)
        return Command(self, response)

    def delete_saml_configuration(self):
        """Delete the SAML configuration resource.

        Returns:
            An instance of :py:class:`streamsets.sdk.aster_api.Command`
        """
        endpoint = 'v{}/saml.delete'.format(self._api_version)
        response = self._post(app='security',
                              endpoint=endpoint)
        return Command(self, response)

    def disable_saml_configuration(self, org=None):
        """Disable the SAML configuration resource.

        Args:
            org (:obj:`str`): Organization id. Default: ``None``

        Returns:
            An instance of :py:class:`streamsets.sdk.aster_api.Command`
        """
        endpoint = 'v{}/saml.disable'.format(self._api_version)
        params = get_params(parameters=locals(), exclusions=('self'))
        response = self._post(app='security',
                              endpoint=endpoint,
                              params=params)
        return Command(self, response)

    def enable_saml_configuration(self):
        """Enable the SAML configuration resource.

        Returns:
            An instance of :py:class:`streamsets.sdk.aster_api.Command`
        """
        endpoint = 'v{}/saml.enable'.format(self._api_version)
        response = self._post(app='security',
                              endpoint=endpoint)
        return Command(self, response)

    def reset_saml_draft_configuration(self):
        """Reset the SAML draft configuration resource.

        Returns:
            An instance of :py:class:`streamsets.sdk.aster_api.Command`
        """
        endpoint = 'v{}/saml.reset-draft'.format(self._api_version)
        response = self._post(app='security',
                              endpoint=endpoint)
        return Command(self, response)

    def update_saml_configuration(self, payload):
        """Update the SAML configuration resource.

        Args:
            payload (:obj:`dict`): data - that complies with Swagger definition.

        Returns:
            An instance of :py:class:`streamsets.sdk.aster_api.Command`
        """
        endpoint = 'v{}/saml.update'.format(self._api_version)
        response = self._post(app='security',
                              endpoint=endpoint,
                              data=payload)
        return Command(self, response)

    def update_saml_configuration_with_idp_metadata(self, idp_metadata_xml):
        """Update the SAML configuration resource with idp metadata.

        Args:
            idp_metadata_xml (:obj:`dict`): idp metadata - that complies with Swagger definition.

        Returns:
            An instance of :py:class:`streamsets.sdk.aster_api.Command`
        """
        endpoint = 'v{}/saml.update-with-idp-metadata'.format(self._api_version)
        response = self._post(app='security',
                              endpoint=endpoint,
                              data=idp_metadata_xml)
        return Command(self, response)

    def create_saml_certificate(self, days_valid, key_len):
        """Create a SAML certificate.

        Args:
            days_valid (:obj:`int`): The number of days the certificate should be valid.
            key_len (:obj:`str`): The length of the key. Acceptable values are 'K2048', 'K3072', 'K4096'.

        Returns:
            An instance of :py:class:`streamsets.sdk.aster_api.Command`
        """
        endpoint = 'v{}/saml/certificate'.format(self._api_version)
        params = get_params(parameters=locals(), exclusions=('self'))
        response = self._post(app='security',
                              endpoint=endpoint,
                              params=params)
        return Command(self, response)

    def delete_saml_certificate(self, serial_number):
        """Delete a SAML certificate.

        Args:
            serial_number (:obj:`str`): The serial number of the certificate.

        Returns:
            An instance of :py:class:`streamsets.sdk.aster_api.Command`
        """
        endpoint = 'v{}/saml/certificate.delete'.format(self._api_version)
        params = get_params(parameters=locals(), exclusions=('self'))
        response = self._post(app='security',
                              endpoint=endpoint,
                              params=params)
        return Command(self, response)

    def get_saml_metadata(self, draft, org=None):
        """Get the SAML configuration resource.

        Args:
            draft (:obj:`bool`): Whether this is a draft or not.
            org (:obj:`str`, optional): Organization id. Default: ``None``

        Returns:
            An instance of :py:class:`streamsets.sdk.aster_api.Command`
        """
        endpoint = 'v{}/saml/metadata'.format(self._api_version)
        params = get_params(parameters=locals(), exclusions=('self'))
        response = self._get(app='security',
                             endpoint=endpoint,
                             params=params)
        return Command(self, response)

    def _delete(self, app, endpoint, params=None):
        url = join_url_parts(self._base_url, '/api/{}'.format(app), endpoint)
        response = self._session.delete(url, params=params or {})
        self._handle_http_error(response)
        return response

    def _get(self, app, endpoint, params=None):
        url = join_url_parts(self._base_url, '/api/{}'.format(app), endpoint)
        response = self._session.get(url, params=params or {})
        self._handle_http_error(response)
        return response

    def _post(self, app, endpoint, params=None, data=None, files=None, headers=None):
        url = join_url_parts(self._base_url, '/api/{}'.format(app), endpoint)
        if data and not isinstance(data, str):
            data = json.dumps(data or {})
        response = self._session.post(url, params=params or {}, data=data, files=files, headers=headers)
        self._handle_http_error(response)
        return response

    def _put(self, app, endpoint, params=None, data=None):
        url = join_url_parts(self._base_url, '/api/{}'.format(app), endpoint)
        body = {'data': (data or {})}
        response = self._session.put(url, params=params or {}, data=json.dumps(body))
        self._handle_http_error(response)
        return response

    def _handle_http_error(self, response):
        """Specific error handling for Aster, to make better error reporting where applicable."""
        if response.status_code == 500:
            raise InternalServerError(response)
        elif response.status_code == 400:
            raise BadRequestError(response)
        # Delegating to response object error handling as last resort.
        response.raise_for_status()


class Command:
    """Command to allow users to interact with commands submitted through Aster REST API.
    Args:
        api_client (:py:class:`streamsets.sdk.aster_api.ApiClient`): Aster API client.
        response (:py:class:`requests.Response`): Command response.
    """
    def __init__(self, api_client, response):
        self.api_client = api_client
        self.response = response
