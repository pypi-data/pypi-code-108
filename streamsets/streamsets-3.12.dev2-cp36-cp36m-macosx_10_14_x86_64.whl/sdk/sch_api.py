# Copyright 2021 StreamSets Inc.

"""Abstractions to interact with the ControlHub REST API."""

import base64
import datetime
import json
import logging
import os
from collections import namedtuple

import javaproperties
import requests
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15

from .exceptions import (ConnectionError, LegacyDeploymentInactiveError, InvalidCredentialsError, JobInactiveError,
                         JobRunnerError)
from .sdc_api import ConnectError, RunError, RunningError, StartError, StartingError
from .utils import SDC_DEFAULT_EXECUTION_MODE, get_params, join_url_parts, wait_for_condition

logger = logging.getLogger(__name__)

# The `#:` constructs at the end of assignments are part of Sphinx's autodoc functionality.
DEFAULT_SCH_API_VERSION = 1 #:
DEFAULT_SDP_API_VERSION = 2 #:

# Any headers that DPM requires for all calls should be added to this dictionary.
REQUIRED_HEADERS = {'X-Requested-By': 'sch',
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
    API client to communicate with a ControlHub instance.

    Args:
        server_url (:obj:`str`): ControlHub instance's server URL.
        component_id (:obj:`str`): ControlHub componentID.
        auth_token (:obj:`str`): ControlHub auth token.
        api_version (:obj:`int`, optional): The DPM API version. Default: :py:const:`DEFAULT_DPM_API_VERSION`
        session_attributes (:obj:`dict`, optional): A dictionary of attributes to set on the underlying
            :py:class:`requests.Session` instance at initialization. Default: ``None``
    """
    # pylint: disable=R0913
    def __init__(self,
                 server_url,
                 component_id,
                 auth_token,
                 api_version=DEFAULT_SCH_API_VERSION,
                 sdp_api_version=DEFAULT_SDP_API_VERSION,
                 session_attributes=None,
                 **kwargs):
        self.base_url = server_url
        self.component_id = component_id
        self.auth_token = auth_token
        self.api_version = api_version
        self.sdp_api_version = sdp_api_version

        self.session = requests.Session()
        self.session.headers.update({'X-SS-App-Component-Id': self.component_id,
                                     'X-SS-App-Auth-Token': self.auth_token})
        self.session.headers.update(REQUIRED_HEADERS)
        if session_attributes:
            for attribute, value in session_attributes.items():
                setattr(self.session, attribute, value)

        self.connection_pool_disabled = False

    def get_available_add_ons(self):
        """Get lists of available and unavailable add-ons.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._get(app='security',
                             endpoint='/v{}/currentUser/availableAddOns'.format(self.api_version))
        return Command(self, response)

    def get_current_user(self):
        """Get current user.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._get(app='security',
                             endpoint='/v{}/currentUser'.format(self.api_version))
        return Command(self, response)

    def get_component_types(self):
        """Returns component types.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._get(app='security',
                             endpoint='/v{}/componentTypes'.format(self.api_version))
        return Command(self, response)

    def get_components(self, org_id, component_type_id, offset, len, order_by='LAST_VALIDATED_ON', order='ASC',
                       with_wrapper=False):
        """Get all registered components for given Organization ID.

        Args:
            org_id (:obj:`str`)
            component_type_id (:obj:`str`)
            offset (:obj:`str`)
            len (:obj:`str`)
            order_by (:obj:`str`, optional): Default: ``'LAST_VALIDATED_ON'``
            order (:obj:`str`, optional): Default: ``'ASC'``
            with_wrapper (:obj:`bool`, optional): Default: ``False``

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self', 'org_id'))
        response = self._get(app='security',
                             endpoint='/v{}/organization/{}/components'.format(self.api_version,
                                                                               org_id),
                             params=params)
        return Command(self, response)

    def create_components(self, org_id, component_type, number_of_components, active=True):
        """Create components for given organization ID.

        Args:
            org_id (:obj:`str`): Organization ID.
            component_type (:obj:`str`)
            number_of_components (:obj:`int`)
            active (:obj:`bool`, optional): Whether component is active. Default: ``True``

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        # pylint: disable=unused-argument

        # We call get_params using local(), so we define a local variable called `organization` to make sure
        # it ends up in the data dictionary we generate.
        organization = org_id  # pylint: disable=unused-variable

        data = get_params(parameters=locals(), exclusions=('self', 'org_id'))
        response = self._put(app='security',
                             endpoint='/v{}/organization/{}/components'.format(self.api_version,
                                                                               org_id),
                             data=data)
        return CreateComponentsCommand(self, response)

    def activate_components(self, org_id, components_json):
        """Activate Components for all given Component IDs.

        Args:
            org_id (:obj:`str`): Organization ID.
            components_json (:obj:`str`): Components in JSON format.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='security',
                              endpoint='/v{}/organization/{}/components/activate'.format(self.api_version, org_id),
                              data=components_json)
        return Command(self, response)

    def deactivate_components(self, org_id, components_json):
        """Deactivate Components for all given Component IDs.

        Args:
            org_id (:obj:`str`): Organization ID.
            components_json (:obj:`str`): Components in JSON format.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='security',
                              endpoint='/v{}/organization/{}/components/deactivate'.format(self.api_version, org_id),
                              data=components_json)
        return Command(self, response)

    def delete_components(self, org_id, components_json):
        """Delete Components for all given list of components IDs.

        Args:
            org_id (:obj:`str`): Organization ID.
            components_json (:obj:`str`): Components in JSON format.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='security',
                              endpoint='/v{}/organization/{}/components/delete'.format(self.api_version, org_id),
                              data=components_json)
        return Command(self, response)

    def get_all_login_audits(self, org_id, offset=None, len_=None, sort_field=None, sort_order=None, start_time=0,
                             end_time=-1):
        """Get all login audits between a time frame.

        Args:
            org_id (:obj:`str`)
            offset (:obj:`str`, optional): Default: ``None``
            len_ (:obj:`int`, optional): Default: ``None``
            sort_field (:obj:`str`, optional): Default: ``None``
            sort_order (:obj:`str`, optional): Default: ``None``
            start_time (:obj:`long`, optional): Default: ``0``
            end_time (:obj:`long`, optional): Default: ``-1``

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self', 'org_id'))

        endpoint = '/v{}/metrics/{}/loginAudits'.format(self.api_version, org_id)
        response = self._get(app='security',
                             endpoint=endpoint,
                             params=params)
        return Command(self, response)

    def get_all_action_audits(self, org_id, offset=None, len_=None, sort_field=None, sort_order=None, start_time=0,
                              end_time=-1):
        """Get all action audits between a time frame.

        Args:
            org_id (:obj:`str`)
            offset (:obj:`str`, optional): Default: ``None``
            len_ (:obj:`int`, optional): Default: ``None``
            sort_field (:obj:`str`, optional): Default: ``None``
            sort_order (:obj:`str`, optional): Default: ``None``
            start_time (:obj:`long`, optional): Default: ``0``
            end_time (:obj:`long`, optional): Default: ``-1``

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self', 'org_id'))

        endpoint = '/v{}/metrics/{}/actionAudits'.format(self.api_version, org_id)
        response = self._get(app='security',
                             endpoint=endpoint,
                             params=params)
        return Command(self, response)

    def create_organization(self, body):
        """Create a new organization.

        Args:
            body (:obj:`str`): Organization in JSON format. Complies to Swagger NewOrganizationJson definition.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._put(app='security',
                             endpoint='/v{}/organizations'.format(self.api_version),
                             data=body)
        return Command(self, response)

    def update_organization(self, org_id, body):
        response = self._post(app='security',
                              endpoint='/v{}/organization/{}'.format(self.api_version, org_id),
                              data=body)
        return Command(self, response)

    def get_all_organizations(self, offset=None, len=None, orderBy='ID', order='ASC',
                              active=None, filterText=None, with_wrapper=False):
        params = get_params(parameters=locals(), exclusions=('self'))
        response = self._get(app='security',
                             endpoint='/v{}/organizations'.format(self.api_version),
                             params=params)
        return Command(self, response)

    def get_organization_configuration(self, org_id):
        response = self._get(app='security',
                             endpoint='/v{}/organization/{}/configs'.format(self.api_version, org_id))
        return Command(self, response)

    def update_organization_configuration(self, org_id, body):
        response = self._post(app='security',
                              endpoint='/v{}/organization/{}/configs'.format(self.api_version, org_id),
                              data=body)
        return Command(self, response)

    def get_organization_global_configurations(self):
        response = self._get(app='security',
                             endpoint='/v{}/organizations/globalConfigs'.format(self.api_version))
        return Command(self, response)

    def update_organization_global_configurations(self, body):
        response = self._post(app='security',
                              endpoint='/v{}/organizations/globalConfigs'.format(self.api_version),
                              data=body)
        return Command(self, response)

    def create_user(self, org_id, body):
        """Create a new user for the given User model.

        Args:
            org_id (:obj:`str`): Organization ID
            body (:obj:`dict`): User object that complies to Swagger UserJson definition

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        endpoint = '/v{}/organization/{}/users'.format(self.api_version, org_id)
        response = self._put(app='security',
                             data=body,
                             endpoint=endpoint)
        return Command(self, response)

    def update_user_password(self, org_id, user_id, body):
        """Update user password.

        Args:
            org_id (:obj:`str`): Organization ID.
            user_id (:obj:`str`): User ID.
            body (:obj:`dict`): Passwords object that complies to Swagger PasswordsJson definition.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        endpoint = '/v{}/organization/{}/user/{}/updatePassword'.format(self.api_version, org_id, user_id)
        response = self._post(app='security',
                              data=body,
                              endpoint=endpoint)
        return Command(self, response)

    def get_all_users(self, org_id, offset=None, len=None, order_by='ID', order='ASC',
                      active=None, filter_text=None, deleted=None, with_wrapper=False):
        """Get all users.

        Args:
            org_id (:obj:`str`)
            offset (:obj:`str`, optional): Default: ``None``
            len (:obj:`int`, optional): Default: ``None``
            order_by (:obj:`str`, optional): Default: ``'ID'``
            order (:obj:`str`, optional): Default: ``'ASC'``
            active (:obj:`str`, optional): Default: ``None``
            filter_text (:obj:`str`, optional): Default: ``None``
            deleted (:obj:`str`, optional): Default: ``None``
            with_wrapper (:obj:`bool`, optional): Default: ``False``

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self', 'org_id'))
        endpoint = '/v{}/organization/{}/users'.format(self.api_version, org_id)
        response = self._get(app='security',
                             endpoint=endpoint,
                             params=params)
        return Command(self, response)

    def get_user(self, org_id, user_id):
        """Get the user for the given user ID.

        Args:
            org_id (:obj:`str`): Organization ID
            user_id (:obj:`str`): User ID

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        endpoint = '/v{}/organization/{}/user/{}'.format(self.api_version, org_id, user_id)
        response = self._get(app='security',
                             endpoint=endpoint)
        return Command(self, response)

    def update_user(self, org_id, user_id, body):
        """Update a user for the given User model.

        Args:
            org_id (:obj:`str`): Organization ID
            user_id (:obj:`str`): User ID
            body (:obj:`dict`): User object that complies to Swagger UserJson definition

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        endpoint = '/v{}/organization/{}/user/{}'.format(self.api_version, org_id, user_id)
        response = self._post(app='security',
                              data=body,
                              endpoint=endpoint)
        return Command(self, response)

    def deactivate_users(self, org_id, body):
        """Deactivate Users for all given User IDs.

        Args:
            org_id (:obj:`str`): Organization ID
            body (:obj:`list`): User IDs

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='security',
                              data=body,
                              endpoint='/v{}/organization/{}/users/deactivate'.format(self.api_version, org_id))
        return Command(self, response)

    def delete_user(self, org_id, user_id):
        """Delete a user for the given user ID.

        Args:
            org_id (:obj:`str`): Organization ID
            user_id (:obj:`str`): User ID

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`
        """
        endpoint = '/v{}/organization/{}/user/{}'.format(self.api_version, org_id, user_id)
        response = self._delete(app='security',
                                endpoint=endpoint)
        return Command(self, response)

    def delete_users(self, org_id, body):
        """Delete all users for the given user IDs.

        Args:
            org_id (:obj:`str`): Organization ID
            body (:obj:`list`): User IDs

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`
        """
        endpoint = '/v{}/organization/{}/users/delete'.format(self.api_version, org_id)
        response = self._post(app='security',
                              data=body,
                              endpoint=endpoint)
        return Command(self, response)

    def create_group(self, org_id, body):
        """Create a new group for the given Group model.

        Args:
            org_id (:obj:`str`): Organization ID.
            body (:obj:`dict`): Group object that complies to Swagger GroupJson definition.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        endpoint = '/v{}/organization/{}/groups'.format(self.api_version, org_id)
        response = self._put(app='security',
                             data=body,
                             endpoint=endpoint)
        return Command(self, response)

    def get_all_groups(self, org_id, offset=None, len=None, order_by='ID', order='ASC', filter_text=None,
                       deleted=None, with_wrapper=False):
        """Get all groups.

        Args:
            org_id (:obj:`str`)
            offset (:obj:`str`, optional): Default: ``None``.
            len (:obj:`int`, optional): Default: ``None``.
            order_by (:obj:`str`, optional): Default: ``'ID'``.
            order (:obj:`str`, optional): Default: ``'ASC'``.
            filter_text (:obj:`str`, optional): Default: ``None``.
            deleted (:obj:`str`, optional): Default: ``None``.
            with_wrapper (:obj:`bool`, optional): Default: ``False``.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self', 'org_id'))
        endpoint = '/v{}/organization/{}/groups'.format(self.api_version, org_id)
        response = self._get(app='security',
                             endpoint=endpoint,
                             params=params)
        return Command(self, response)

    def get_group(self, org_id, group_id):
        """Get the group for the given group ID.

        Args:
            org_id (:obj:`str`): Organization ID.
            group_id (:obj:`str`): Group ID.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        endpoint = '/v{}/organization/{}/group/{}'.format(self.api_version, org_id, group_id)
        response = self._get(app='security',
                             endpoint=endpoint)
        return Command(self, response)

    def update_group(self, org_id, group_id, body):
        """Update a group for the given Group model.

        Args:
            org_id (:obj:`str`): Organization ID.
            group_id (:obj:`str`): Group ID.
            body (:obj:`dict`): Group object that complies to Swagger GroupJson definition.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        endpoint = '/v{}/organization/{}/group/{}'.format(self.api_version, org_id, group_id)
        response = self._post(app='security',
                              data=body,
                              endpoint=endpoint)
        return Command(self, response)

    def delete_group(self, org_id, group_id):
        """Delete a group for the given group ID.

        Args:
            org_id (:obj:`str`): Organization ID.
            group_id (:obj:`str`): Group ID.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        endpoint = '/v{}/organization/{}/group/{}'.format(self.api_version, org_id, group_id)
        response = self._delete(app='security',
                                endpoint=endpoint)
        return Command(self, response)

    def delete_groups(self, org_id, body):
        """Delete all groups for the given group IDs.

        Args:
            org_id (:obj:`str`): Organization ID.
            body (:obj:`list`): Group IDs.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        endpoint = '/v{}/organization/{}/groups/delete'.format(self.api_version, org_id)
        response = self._post(app='security',
                              data=body,
                              endpoint=endpoint)
        return Command(self, response)

    def create_connection(self, body):
        """Create a new connection.

        Args:
            body (:obj:`dict`): Connection object that complies to Swagger ConnectionJson definition

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        endpoint = '/v{}/connections'.format(self.api_version)
        response = self._put(app='connection',
                             data=body,
                             endpoint=endpoint)
        return Command(self, response)

    def get_all_connections(self, organization, connection_type=None, filter_text=None, offset=None, len=None,
                            order_by='NAME', order='ASC', with_total_count=False):
        """Get all connections.

        Args:
            organization (:obj:`str`)
            connection_type (:obj:`str`, optional): Default: ``None``
            filter_text (:obj:`str`, optional): Default: ``None``
            offset (:obj:`str`, optional): Default: ``None``
            len (:obj:`int`, optional): Default: ``None``
            order_by (:obj:`str`, optional): Default: ``'NAME'``
            order (:obj:`str`, optional): Default: ``'ASC'``
            with_total_count (:obj:`bool`, optional): Default: ``False``

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self'))
        endpoint = '/v{}/connections'.format(self.api_version)
        response = self._get(app='connection',
                             endpoint=endpoint,
                             params=params)
        return Command(self, response)

    def get_connection(self, connection_id):
        """Get the connection for the given connection ID.

        Args:
            connection_id (:obj:`str`): Connection ID

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        endpoint = '/v{}/connection/{}'.format(self.api_version, connection_id)
        response = self._get(app='connection',
                             endpoint=endpoint)
        return Command(self, response)

    def update_connection(self, connection_id, body):
        """Update connection.

        Args:
            connection_id (:obj:`str`): Connection ID
            body (:obj:`dict`): Connection object that complies to Swagger ConnectionJson definition

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        endpoint = '/v{}/connection/{}'.format(self.api_version, connection_id)
        response = self._post(app='connection',
                              data=body,
                              endpoint=endpoint)
        return Command(self, response)

    def delete_connection(self, connection_id):
        """Delete connection.

        Args:
            connection_id (:obj:`str`): Connection ID

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`
        """
        endpoint = '/v{}/connection/{}'.format(self.api_version, connection_id)
        response = self._delete(app='connection',
                                endpoint=endpoint)
        return Command(self, response)

    def get_pipeline_commits_using_connection(self, connection_id):
        """Get all pipeline commits using given connection.

        Args:
            connection_id (:obj:`str`)

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        endpoint = '/v{}/connection/{}/getPipelineCommits'.format(self.api_version, connection_id)
        response = self._get(app='connection',
                             endpoint=endpoint)
        return Command(self, response)

    def get_pipeline_commit_counts_using_connection(self, connection_id):
        """Get count of pipeline commits using given connection.

        Args:
            connection_id (:obj:`str`)

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        endpoint = '/v{}/connection/{}/countPipelineCommits'.format(self.api_version, connection_id)
        response = self._get(app='connection',
                             endpoint=endpoint)
        return Command(self, response)

    def get_all_connection_audits(self, org_id, offset=None, len_=None, sort_field=None, sort_order=None, start_time=0,
                                  end_time=-1):
        """Get all connection audits between a time frame.

        Args:
            org_id (:obj:`str`)
            offset (:obj:`str`, optional): Default: ``None``
            len_ (:obj:`int`, optional): Default: ``None``
            sort_field (:obj:`str`, optional): Default: ``None``
            sort_order (:obj:`str`, optional): Default: ``None``
            start_time (:obj:`long`, optional): Default: ``0``
            end_time (:obj:`long`, optional): Default: ``-1``

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self', 'org_id'))
        if 'len_' in params:
            params['len'] = params.pop('len_')
        endpoint = '/v{}/connections/{}/connectionAuditsTime'.format(self.api_version, org_id)
        response = self._get(app='connection',
                             endpoint=endpoint,
                             params=params)
        return Command(self, response)

    def get_all_connection_audits_last_30_days(self, org_id, offset=None, len_=None, sort_field=None, sort_order=None):
        """Get all connection audits for last 30 days.

        Args:
            org_id (:obj:`str`)
            offset (:obj:`str`, optional): Default: ``None``
            len_ (:obj:`int`, optional): Default: ``None``
            sort_field (:obj:`str`, optional): Default: ``None``
            sort_order (:obj:`str`, optional): Default: ``None``

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self', 'org_id'))
        if 'len_' in params:
            params['len'] = params.pop('len_')
        # This endpoint returns connection audits for last 30 days even though the endpoint name is generic
        endpoint = '/v{}/connections/{}/connectionAudits'.format(self.api_version, org_id)
        response = self._get(app='connection',
                             endpoint=endpoint,
                             params=params)
        return Command(self, response)

    def get_audits_for_connection(self, connection_id):
        """Get all audits for connection.

        Args:
            connection_id (:obj:`str`)

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        endpoint = '/v{}/connections/{}/audit'.format(self.api_version, connection_id)
        response = self._get(app='connection',
                             endpoint=endpoint)
        return Command(self, response)

    def get_all_connection_tags(self, organization, parent_id=None, offset=None, len_=None, order='ASC'):
        """Get all connections.

        Args:
            organization (:obj:`str`)
            parent_id (:obj:`str`, optional): Default: ``None``
            offset (:obj:`str`, optional): Default: ``None``
            len_ (:obj:`str`, optional): Default: ``None``
            order (:obj:`str`, optional): Default: ``'ASC'``

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self'))
        if 'len_' in params:
            params['len'] = params.pop('len_')
        endpoint = '/v{}/connections/tags'.format(self.api_version)
        response = self._get(app='connection',
                             endpoint=endpoint,
                             params=params)
        return Command(self, response)

    def get_classification_catalog_list(self):
        response = self._get(app='sdp_classification',
                             endpoint=('/v{}/classification/catalog/'
                                       'o:list/pageId=CatalogListPage').format(self.sdp_api_version))
        return Command(self, response)

    def commit_classification_rules(self, id_):
        response = self._post(app='sdp_classification',
                              endpoint=('/v{}/classification/catalog/'
                                        'o:commit/{}/pageId=CatalogManagePage').format(self.sdp_api_version, id_))
        return Command(self, response)

    def get_new_classification_rule(self, id_):
        response = self._get(app='sdp_classification',
                             endpoint=('/v{}/classification/rule/'
                                       'o:new/{}/pageId=RuleNewPage').format(self.sdp_api_version, id_))
        return Command(self, response)

    def get_protection_policy_list(self):
        response = self._get(app='policy',
                             endpoint='/v{}/policy/o:list/pageId=PolicyListPage'.format(self.sdp_api_version))
        return Command(self, response)

    def get_new_protection_policy(self):
        response = self._get(app='policy',
                             endpoint='/v{}/policy/o:new/pageId=PolicyNewPage'.format(self.sdp_api_version))
        return Command(self, response)

    def create_protection_policy(self, body):
        response = self._put(app='policy',
                             endpoint='/v{}/policy/o:create/pageId=PolicyManagePage'.format(self.sdp_api_version),
                             data=body)
        return Command(self, response)

    def set_default_write_protection_policy(self, policy_id):
        response = self._post(app='policy',
                              endpoint=('/v{}/policy/o:default/write/'
                                        '{}/pageId=PolicyManagePage').format(self.sdp_api_version, policy_id))
        return Command(self, response)

    def set_default_read_protection_policy(self, policy_id):
        response = self._post(app='policy',
                              endpoint=('/v{}/policy/o:default/read/'
                                        '{}/pageId=PolicyManagePage').format(self.sdp_api_version, policy_id))
        return Command(self, response)

    def export_protection_policies(self, policy_ids):
        response = self._get(app='policy',
                             endpoint=('/v{}/policy/o:exportPolicies'
                                       '/pageId=PolicyManagePage').format(self.sdp_api_version),
                             params={'id': policy_ids})
        return Command(self, response)

    def import_protection_policies(self, policies_file):
        response = self._post(app='policy',
                              endpoint=('/v{}/policy/o:importPolicies/'
                                        'pageId=PolicyManagePage').format(self.sdp_api_version),
                              files={'file': policies_file},
                              headers={'content-type': None})
        return Command(self, response)

    def get_new_policy_procedure(self, id_):
        response = self._get(app='policy',
                             endpoint='/v{}/procedure/o:new/{}/pageId=ProcedureNewPage'.format(self.sdp_api_version,
                                                                                               id_))
        return Command(self, response)

    def create_policy_procedure(self, body):
        response = self._put(app='policy',
                             endpoint='/v{}/procedure/o:create/pageId=ProcedureManagePage'.format(self.sdp_api_version),
                             data=body)
        return Command(self, response)

    def create_classification_rule(self, body):
        response = self._put(app='sdp_classification',
                             endpoint=('/v{}/classification/rule/'
                                       'o:create/pageId=RuleManagePage').format(self.sdp_api_version),
                             data=body)
        return Command(self, response)

    def get_new_classification_classifier(self, id_):
        response = self._get(app='sdp_classification',
                             endpoint=('/v{}/classification/classifier/'
                                       'o:new/{}/pageId=ClassifierNewPage').format(self.sdp_api_version,
                                                                                   id_))
        return Command(self, response)

    def create_classification_classifier(self, body):
        response = self._put(app='sdp_classification',
                             endpoint=('/v{}/classification/classifier/'
                                       'o:create/pageId=ClassifierManagePage').format(self.sdp_api_version),
                             data=body)
        return Command(self, response)

    def get_classification_classifier_list(self, id_):
        response = self._get(app='sdp_classification',
                             endpoint=('/v{}/classification/classifier/'
                                       'o:list/{}/pageId=ClassifierListPage').format(self.sdp_api_version, id_))
        return Command(self, response)

    def delete_classification_classifier(self, id_):
        response = self._delete(app='sdp_classification',
                                endpoint=('/v{}/classification/classifier/'
                                          'o:delete/{}/pageId=ClassifierManagePage').format(self.sdp_api_version, id_))
        return Command(self, response)

    def commit_pipeline(self, organization=None, new_pipeline=None, execution_mode=SDC_DEFAULT_EXECUTION_MODE,
                        template_commit_id=None, import_pipeline=None, fragment=None, pipeline_type=None, body=None):
        params = get_params(parameters=locals(), exclusions=('self', 'body'))
        response = self._put(app='pipelinestore',
                             endpoint='/v{}/pipelines'.format(self.api_version),
                             params=params,
                             data=body)
        return Command(self, response)

    def get_pipeline_commit(self, commit_id):
        response = self._get(app='pipelinestore',
                             endpoint='/v{}/pipelineCommit/{}'.format(self.api_version, commit_id))
        return Command(self, response)

    def get_pipeline_commits(self, pipeline_id, organization=None, offset=None, len_=None,
                             order='ASC', only_published=None):
        params = get_params(parameters=locals(), exclusions=('self', 'pipeline_id'))
        response = self._get(app='pipelinestore',
                             endpoint='/v{}/pipeline/{}/log'.format(self.api_version, pipeline_id),
                             params=params)
        return Command(self, response)

    def get_pipelines_commit(self, body):
        response = self._post(app='pipelinestore',
                              endpoint='/v{}/pipelineCommit'.format(self.api_version),
                              data=body)
        return Command(self, response)

    def get_latest_pipeline_commit(self, pipeline_id, user=None, only_published=None):
        """Get the latest pipeline commit for a given pipeline ID.

        Args:
            pipeline_id (:obj:`str`): Pipeline ID.
            user (:obj:`str`, optional): Default: ``None``.
            only_published (:obj:`boolean`, optional): Default: ``None``.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self', 'pipeline_id'))
        response = self._get(app='pipelinestore',
                             endpoint='/v{}/pipeline/{}/latest'.format(self.api_version, pipeline_id),
                             params=params)
        return Command(self, response)

    def save_pipeline_commit(self, commit_id, validate=None, include_library_definitions=None, body=None):
        params = get_params(parameters=locals(), exclusions=('self', 'commit_id', 'body'))
        response = self._post(app='pipelinestore',
                              endpoint='/v{}/pipelineCommit/{}'.format(self.api_version, commit_id),
                              params=params,
                              data=body)
        return Command(self, response)

    def publish_pipeline_commit(self, commit_id, commit_message=None):
        params = get_params(parameters=locals(), exclusions=('self', 'commit_id'))
        response = self._post(app='pipelinestore',
                              endpoint='/v{}/pipelineCommit/{}/publish'.format(self.api_version, commit_id),
                              params=params)
        return Command(self, response)

    def get_all_pipeline_labels(self, organization, parent_id=None, offset=None, len=None, order=None):
        """Get pipeline labels for a given organization.

        Args:
            organization (:obj:`str`)
            parent_id (:obj:`str`, optional): Default: ``None``
            offset (:obj:`int`, optional): Default: ``None``
            len (obj:`int`, optional): Default: ``None``
            order (:obj:`str`, optional): Default: ``None``

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self'))
        response = self._get(app='pipelinestore',
                             endpoint='/v{}/pipelineLabels'.format(self.api_version),
                             params=params)
        return Command(self, response)

    def delete_pipeline_labels(self, body):
        """Delete pipeline labels.

        Args:
            body (:obj:`list`)

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='pipelinestore',
                              endpoint='/v{}/pipelineLabels/deleteLabels'.format(self.api_version),
                              data=body)
        return Command(self, response)

    def get_pipelines_count(self, organization, system):
        """Returns the number of pipelines for the current user.

        Args:
            organization (:obj:`str`).
            system (:obj:`bool`).

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self'))
        response = self._get(app='pipelinestore',
                             endpoint='/v{}/pipelines/count'.format(self.api_version),
                             params=params)
        return Command(self, response)

    def get_pipeline_tags(self, pipeline_id):
        """Get pipeline tags.

        Args:
            pipeline_id (:obj:`str`): Pipeline ID.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._get(app='pipelinestore',
                             endpoint='/v{}/pipeline/{}/tags'.format(self.api_version, pipeline_id))
        return Command(self, response)

    def create_pipeline_draft(self, commit_id, authoring_sdc_id=None, authoring_sdc_version=None):
        params = get_params(parameters=locals(), exclusions=('self', 'commit_id'))
        response = self._post(app='pipelinestore',
                              endpoint='/v{}/pipelineCommit/{}/createDraft'.format(self.api_version, commit_id),
                              params=params)
        return Command(self, response)

    def delete_pipeline(self, pipeline_id):
        """Delete all versions of pipeline.

        Args:
            pipeline_id (:obj:`str`)

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._delete(app='pipelinestore',
                                endpoint='/v{}/pipeline/{}'.format(self.api_version, pipeline_id))
        return Command(self, response)

    def delete_pipeline_commit(self, pipeline_commit_id):
        """Delete only the selected version of pipeline.

        Args:
            pipeline_commit_id (:obj:`str`)

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._delete(app='pipelinestore',
                                endpoint='/v{}/pipelineCommit/{}'.format(self.api_version, pipeline_commit_id))
        return Command(self, response)

    def duplicate_pipeline(self, pipeline_commit_id, body):
        """Duplicate an existing pipleine.

        Args:
            pipeline_commit_id (:obj:`str`)
            body (:obj:`dict`)

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='pipelinestore',
                              endpoint='/v{}/pipelineCommit/{}/duplicate'.format(self.api_version,
                                                                                 pipeline_commit_id),
                              data=body)
        return Command(self, response)

    def export_pipelines(self, fragments=None, body=None, include_plain_text_credentials=False):
        """Export pipelines.

        Args:
            body (:obj:`list`): A list of :obj:`str` commit ids.
            fragments (:obj:`bool`): Indicates if exporting fragments is needed.
            include_plain_text_credentials (:obj:`bool`): Indicates if plain text credentials should be included.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self', 'body'))
        response = self._post(app='pipelinestore',
                              endpoint='/v{}/pipelines/exportPipelineCommits'.format(self.api_version),
                              params=params,
                              data=body)
        return Command(self, response)

    def return_all_pipelines(self, organization, pipeline_label_id, offset, len, order_by, order, system,
                             filter_text, only_published, execution_modes, start_time=-1, end_time=-1, user_ids=None,
                             draft=None):
        """Returns all pipelines.

        Args:
            organization (:obj:`str`)
            pipeline_label_id (:obj:`str`)
            offset (:obj:`str`)
            len (:obj:`str`)
            order_by (:obj:`str`)
            order (:obj:`str`)
            system (:obj:`str`)
            filter_text (:obj:`str`)
            only_published (:obj:`bool`)
            execution_modes (:obj:`str`)
            start_time (:obj:`int`, optional): Default: ``-1``
            end_time (:obj:`int`, optional): Default: ``-1``
            user_ids (:obj:`list`, optional): List of strings. Default: ``None``
            draft (:obj:`bool`, optional): Default: ``None``

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`
        """
        params = get_params(parameters=locals(), exclusions=('self'))
        response = self._get(app='pipelinestore',
                             endpoint='/v{}/pipelines'.format(self.api_version),
                             params=params)
        return Command(self, response)

    def return_all_pipeline_fragments(self, organization, pipeline_label_id, offset, len, order_by, order, system,
                                      filter_text, only_published, execution_modes, start_time=-1, end_time=-1,
                                      user_ids=None, draft=None):
        """Returns all pipeline fragments.

        Args:
            organization (:obj:`str`)
            pipeline_label_id (:obj:`str`)
            offset (:obj:`str`)
            len (:obj:`str`)
            order_by (:obj:`str`)
            order (:obj:`str`)
            system (:obj:`str`)
            filter_text (:obj:`str`)
            only_published (:obj:`bool`)
            execution_modes (:obj:`str`)
            start_time (:obj:`int`, optional): Default: ``-1``
            end_time (:obj:`int`, optional): Default: ``-1``
            user_ids (:obj:`list`, optional): List of strings. Default: ``None``
            draft (:obj:`bool`, optional): Default: ``None``
        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`
        """
        params = get_params(parameters=locals(), exclusions=('self'))
        response = self._get(app='pipelinestore',
                             endpoint='/v{}/pipelines/fragments'.format(self.api_version),
                             params=params)
        return Command(self, response)

    def import_pipelines(self, commit_message, pipelines_file, fragments):
        """Import pipelines from archived zip directory.

        Args:
            commit_message (:obj:`str`): Commit message
            pipelines_file (:obj:`file`): file containing the pipelines
            fragments (:obj:`bool`): Indicates if pipeline contains fragments.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command` that wraps a list of
            :py:class:`streamsets.sdk.sch_models.Pipeline`.
        """
        params = get_params(parameters=locals(), exclusions=('self', 'pipelines_file'))
        response = self._post(app='pipelinestore',
                              endpoint='/v{}/pipelines/importPipelineCommits'.format(self.api_version),
                              files={'file': pipelines_file},
                              params=params,
                              headers={'content-type': None})
        return Command(self, response)

    def get_pipeline_acl(self, pipeline_id):
        """Get pipeline ACL.

        Args:
            pipeline_id (:obj:`str`)

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._get(app='pipelinestore', endpoint='/v{}/pipeline/{}/acl'.format(self.api_version, pipeline_id))
        return Command(self, response)

    def set_pipeline_acl(self, pipeline_id, pipeline_acl_json):
        """Update pipeline ACL.

        Args:
            pipeline_id (:obj:`str`)
            pipeline_acl_json (:obj:`str`): Pipeline ACL in JSON format.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`
        """
        response = self._post(app='pipelinestore', endpoint='/v{}/pipeline/{}/acl'.format(self.api_version,
                                                                                          pipeline_id),
                              data=pipeline_acl_json)
        return Command(self, response)

    def get_topology_acl(self, topology_id):
        """Get the ACL of a Topology.

        Args:
            topology_id (:obj:`str`): ID of the Topology.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._get(app='topology', endpoint='/v{}/topology/{}/acl'.format(self.api_version, topology_id))
        return Command(self, response)

    def set_topology_acl(self, topology_id, topology_acl_json):
        """Update the ACL of a Topology.

        Args:
            topology_id (:obj:`str`): ID of the Topology.
            topology_acl_json (:obj:`str`): ACL of the Topology in JSON format.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`
        """
        response = self._post(app='topology', endpoint='/v{}/topology/{}/acl'.format(self.api_version, topology_id),
                              data=topology_acl_json)
        return Command(self, response)

    def update_topology_permissions(self, body, topology_id, subject_id):
        """Update the permissions of a Topology for a specific subject.

        Args:
            body (:obj:`dict`): JSON representation of permission attributes to update.
            topology_id (:obj:`str:): ID of the Topology.
            subject_id (:obj:`str`): ID of the subject.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`
        """
        response = self._post(app='topology', endpoint='/v{}/topology/{}/permissions/{}'.format(self.api_version,
                                                                                                topology_id,
                                                                                                subject_id),
                              data=body)
        return Command(self, response)

    def get_subscription_acl(self, subscription_id):
        """Get the ACL of an Event Subscription.

        Args:
            subscription_id (:obj:`str`): ID of the Subscription.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._get(app='notification', endpoint='/v{}/eventsub/{}/acl'.format(self.api_version,
                                                                                        subscription_id))
        return Command(self, response)

    def set_subscription_acl(self, subscription_id, subscription_acl_json):
        """Set the ACL of an Event Subscription.

        Args:
            subscription_id (:obj:`str`): ID of the Subscription.
            subscription_acl_json (:obj:`str`): ACL of the Subscription in JSON format.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='notification', endpoint='/v{}/eventsub/{}/acl'.format(self.api_version,
                                                                                         subscription_id),
                              data=subscription_acl_json)
        return Command(self, response)

    def update_subscription_permissions(self, body, subscription_id, subject_id):
        """Update the permissions of an Event Subscription for a specific subject.

        Args:
            body (:obj:`dict`): JSON representation of permission attributes to update.
            subscription_id (:obj:`str:): ID of the Subscription.
            subject_id (:obj:`str`): ID of the subject.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='notification', endpoint='/v{}/eventsub/{}/permissions/{}'.format(self.api_version,
                                                                                                    subscription_id,
                                                                                                    subject_id),
                              data=body)
        return Command(self, response)

    def get_provisioning_agent_acl(self, dpm_agent_id):
        """Get the ACL of a Provisioning Agent.

        Args:
            dpm_agent_id (:obj:`str`): ID of the Provisioning Agent.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._get(app='provisioning', endpoint='/v{}/dpmAgent/{}/acl'.format(self.api_version,
                                                                                        dpm_agent_id))
        return Command(self, response)

    def set_provisioning_agent_acl(self, dpm_agent_id, dpm_agent_acl_json):
        """Set the ACL of a Provisioning Agent.

        Args:
            dpm_agent_id (:obj:`str`): ID of the Provisioning Agent.
            dpm_agent_acl_json (:obj:`str`): ACL of the Subscription in JSON format.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='provisioning', endpoint='/v{}/dpmAgent/{}/acl'.format(self.api_version,
                                                                                         dpm_agent_id),
                              data=dpm_agent_acl_json)
        return Command(self, response)

    def update_provisioning_agent_permissions(self, body, dpm_agent_id, subject_id):
        """Update the permissions of a Provisioning Agent for a specific subject.

        Args:
            body (:obj:`dict`): JSON representation of permission attributes to update.
            dpm_agent_id (:obj:`str:): ID of the Provisioning Agent.
            subject_id (:obj:`str`): ID of the subject.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='provisioning', endpoint='/v{}/dpmAgent/{}/permissions/{}'
                                                           .format(self.api_version, dpm_agent_id, subject_id),
                              data=body)
        return Command(self, response)

    def get_legacy_deployment_acl(self, deployment_id):
        """Get the ACL of a Deployment.

        Args:
            deployment_id (:obj:`str`): ID of the Deployment.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._get(app='provisioning', endpoint='/v{}/deployment/{}/acl'.format(self.api_version,
                                                                                        deployment_id))
        return Command(self, response)

    def set_legacy_deployment_acl(self, deployment_id, deployment_acl_json):
        """Set the ACL of a Deployment.

        Args:
            deployment_id (:obj:`str`): ID of the Deployment.
            deployment_acl_json (:obj:`str`): ACL of the Deployment in JSON format.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='provisioning', endpoint='/v{}/deployment/{}/acl'.format(self.api_version,
                                                                                           deployment_id),
                              data=deployment_acl_json)
        return Command(self, response)

    def update_legacy_deployment_permissions(self, body, deployment_id, subject_id):
        """Update the permissions of a Deployment for a specific subject.

        Args:
            body (:obj:`dict`): JSON representation of permission attributes to update.
            deployment_id (:obj:`str:): ID of the Deployment.
            subject_id (:obj:`str`): ID of the subject.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='provisioning', endpoint='/v{}/deployment/{}/permissions/{}'.format(self.api_version,
                                                                                                      deployment_id,
                                                                                                      subject_id),
                              data=body)
        return Command(self, response)

    def get_scheduled_task_acl(self, scheduled_task_id):
        """Get the ACL of a Scheduled Task.

        Args:
            scheduled_task_id (:obj:`str`): ID of the Scheduled Task.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._get(app='scheduler', endpoint='/v{}/jobs/{}/acl'.format(self.api_version, scheduled_task_id))
        return Command(self, response)

    def set_scheduled_task_acl(self, scheduled_task_id, scheduled_task_acl_json):
        """Set the ACL of a Scheduled Task.

        Args:
            scheduled_task_id (:obj:`str`): ID of the Scheduled Task.
            scheduled_task_acl_json (:obj:`str`): ACL of the Scheduled Task in JSON format.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='scheduler', endpoint='/v{}/jobs/{}/acl'.format(self.api_version, scheduled_task_id),
                              data=scheduled_task_acl_json)
        return Command(self, response)

    def update_scheduled_task_permissions(self, body, scheduled_task_id, subject_id):
        """Update the permissions of a Scheduled Task for a specific subject.

        Args:
            body (:obj:`dict`): JSON representation of permission attributes to update.
            scheduled_task_id (:obj:`str:): ID of the Scheduled Task.
            subject_id (:obj:`str`): ID of the subject.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='scheduler', endpoint='/v{}/jobs/{}/permissions/{}'.format(self.api_version,
                                                                                             scheduled_task_id,
                                                                                             subject_id),
                              data=body)
        return Command(self, response)

    def get_alert_acl(self, alert_id):
        """Get the ACL of an Alert.

        Args:
            alert_id (:obj:`str`): ID of the Alert.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._get(app='notification', endpoint='/v{}/alerts/{}/acl'.format(self.api_version, alert_id))
        return Command(self, response)

    def set_alert_acl(self, alert_id, alert_acl_json):
        """Set the ACL of an Alert.

        Args:
            alert_id (:obj:`str`): ID of the Alert.
            alert_acl_json (:obj:`str`): ACL of the Alert in JSON format.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='notification', endpoint='/v{}/alerts/{}/acl'.format(self.api_version, alert_id),
                              data=alert_acl_json)
        return Command(self, response)

    def update_alert_permissions(self, body, alert_id, subject_id):
        """Update the permissions of an Alert for a specific subject.

        Args:
            body (:obj:`dict`): JSON representation of permission attributes to update.
            alert_id (:obj:`str:): ID of the Alert.
            subject_id (:obj:`str`): ID of the subject.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='notification', endpoint='/v{}/alerts/{}/permissions/{}'.format(self.api_version,
                                                                                                  alert_id,
                                                                                                  subject_id),
                              data=body)
        return Command(self, response)

    def wait_for_job_status(self, job_id, status, timeout_sec=300):
        """Wait for job status.

        Args:
            job_id (:obj:`str`)
            status (:obj:`str`): Job status.
            timeout_sec (:obj:`int`): Timeout for wait, in seconds. Default: 300
        """
        def condition(job_id):
            current_status = self.get_current_job_status(job_id).response.json()['status']
            logger.debug('Status of job (id: %s) is %s ...', job_id, current_status)
            if current_status == 'INACTIVE_ERROR':
                raise JobInactiveError('Job status changed to INACTIVE_ERROR')
            return current_status == status

        def failure(timeout):
            raise Exception('Timed out after {} seconds while waiting for status.'.format(timeout))

        def success(time):
            logger.debug('Job reached desired status after %s s.', time)

        logger.debug('Job %s waiting for status %s ...', job_id, status)
        wait_for_condition(condition=condition, condition_kwargs={'job_id': job_id}, timeout=timeout_sec,
                           failure=failure, success=success)

    def return_all_jobs(self, organization, order_by, order, system, removed, filter_text, job_status, job_label, edge,
                        offset, len, executor_type, archived=False, job_tag=None, job_template=None,
                        template_job_id=None, with_wrapper=False):
        """Returns all jobs. Offset and length are deliberately set to default values because of their limited usage.

        Args:
            organization (:obj:`str`).
            order_by (:obj:`str`).
            order (:obj:`str`).
            removed (:obj:`bool`).
            system (:obj:`bool`).
            filter_text (:obj:`str`).
            job_status (:obj:`str`).
            job_label (:obj:`str`).
            edge (:obj:`bool`).
            offset (:obj:`str`).
            len (:obj:`str`).
            executor_type (:obj:`str`).
            archived (:obj:`bool`, optional): Default: ``False``
            job_tag (:obj:`str`, optional): Default: ``None``
            job_template (:obj:`str`, optional): Default: ``None``
            template_job_id (:obj:`str`, optional): ID of the Job Template. Default: ``None``
            with_wrapper (:obj:`bool`, optional): Default: ``False``

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self'))
        response = self._get(app='jobrunner',
                             endpoint='/v{}/jobs'.format(self.api_version),
                             params=params)
        return Command(self, response)

    def get_jobs_count(self, organization, removed, system):
        """Returns the number of jobs for the current user.

        Args:
            organization (:obj:`str`).
            removed (:obj:`bool`).
            system (:obj:`bool`).

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self'))
        response = self._get(app='jobrunner',
                             endpoint='/v{}/jobs/count'.format(self.api_version),
                             params=params)
        return Command(self, response)

    def get_jobs(self, body):
        """Returns Jobs for all give Job IDs.

        Args:
            body (:obj:`list`): A list of job IDs.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='jobrunner',
                              endpoint='/v{}/jobs'.format(self.api_version),
                              data=body)
        return Command(self, response)

    def get_active_jobs(self, organization, pipeline_commit_id, offset=None, len=None, order_by='NAME',
            order='ASC', template_job_id=None, job_template=None):
        """Returns all active Jobs for given Pipeline Commit ID.

        Args:
            organization (:obj:`str`)
            pipeline_commit_id (:obj:`str`)
            offset (:obj:`int`, optional): Default: ``'None'``
            len (:obj:`int`, optional): Default: ``'None'``
            order_by (:obj:`str`, optional): Default: ``'NAME'``
            order (:obj:`str`, optional): Default: ``'ASC'``
            with_wrapper (:obj:`bool`, optional): Default: ``False``
            template_job_id (:obj:`str`, optional): ID of the Job Template. Default: ``'None'``
            job_template (:obj:`str`, optional): Default: ``'None'``

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self'))
        response = self._get(app='jobrunner',
                             endpoint='/v{}/jobs/forPipelineCommit'.format(self.api_version),
                             params=params)
        return Command(self, response)

    def get_template_history(self, template_job_id, offset=None, len=None, with_total_count=False):
        """Returns Run History of a Job Template.

        Args:
            template_job_id (:obj:`str`): ID of the Job Template.
            offset (:obj:`int`, optional): Default: ``None``
            len (:obj:`int`, optional): Default: ``None``
            with_total_count (:obj:`bool`, optional): Default: ``False``

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self', 'template_job_id'))
        response = self._get(app='jobrunner',
                             endpoint='/v{}/job/{}/runHistory'.format(self.api_version,
                                                                      template_job_id),
                             params=params)
        return Command(self, response)

    def archive_templates(self, body):
        """Archive Job Template for all given Job Template IDs.

        Args:
            body (:obj:`list`): List of Job Template IDs.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='jobrunner',
                              endpoint='/v{}/jobs/archiveJobTemplates'.format(self.api_version),
                              data=body)
        return Command(self, response)

    def create_job(self, body):
        """Create a new job.

        Args:
           body (:obj:`str`): Job in JSON format. Complies to Swagger NewJobJson definition.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._put(app='jobrunner',
                             endpoint='/v{}/jobs'.format(self.api_version),
                             data=body)
        return Command(self, response)

    def create_and_start_job_instances(self, template_job_id, body):
        """Create and Start Job Instances from Job Template.

        Args:
            template_job_id (:obj:`str`): ID of the Job Template.
            body (:obj:`dict`): Job instance in JSON format. Complies to Swagger JobTemplateCreationInfoJson definition.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='jobrunner',
                              endpoint='/v{}/job/{}/createAndStartJobInstances'.format(self.api_version,
                                                                                       template_job_id),
                              data=body)
        return Command(self, response)

    def get_job(self, job_id):
        """Returns the job for given job id.

        Args:
            job_id (:obj:`str`)

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`
        """
        response = self._get(app='jobrunner',
                             endpoint='/v{}/job/{}'.format(self.api_version, job_id))
        return Command(self, response)

    def get_job_committed_offsets(self, job_id):
        """Returns the committed offsets for a given job id.

        Args:
            job_id (:obj:`str`)

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`
        """
        response = self._get(app='jobrunner',
                             endpoint='/v{}/job/{}/committedOffsets'.format(self.api_version, job_id))
        return Command(self, response)

    def update_job(self, job_id, job_json):
        """Update a job.

        Args:
            job_id (:obj:`str`)
            job_json (:obj:`str`): Job in JSON format. Complies to Swagger JobJson definition.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`
        """
        response = self._post(app='jobrunner',
                              endpoint='/v{}/job/{}'.format(self.api_version, job_id),
                              data=job_json)
        return Command(self, response)

    def upgrade_jobs(self, job_ids):
        """Upgrade a job to the latest version of pipeline.

        Args:
          job_ids (:obj:`list`): List of job ids to upgrade.

        Returns:
          An instance of :py:class:`streamsets.sdk.sch_api.Command`
        """
        repsonse = self._post(app='jobrunner',
                              endpoint='/v{}/jobs/upgradeJobs'.format(self.api_version),
                              data=job_ids)
        return Command(self, repsonse)

    def delete_job(self, job_id, api_version=None):
        """Delete job.

        Args:
            job_id (:obj:`str`)
            api_version (:obj:`int`, optional): Control Hub API version. Default: :py:const:`DEFAULT_SCH_API_VERSION`

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`
        """
        if api_version is None:
            api_version = self.api_version
        response = self._delete(app='jobrunner',
                                endpoint='/v{}/job/{}'.format(api_version, job_id))
        return Command(self, response)

    def delete_jobs(self, job_ids_json):
        """Deletes Job for all given Job IDs.

        Args:
            job_ids_json (:obj:`str`): Job IDs in JSON format.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='jobrunner',
                              endpoint='/v{}/jobs/deleteJobs'.format(self.api_version),
                              data=job_ids_json)
        return Command(self, response)

    def import_jobs(self, jobs_file, update_pipeline_refs=True, update_num_instances=False,
                    update_runtime_parameters=False, update_labels=False, update_migrate_offsets=True):
        """Import jobs from archived zip directory.

        Args:
            jobs_file (:obj:`file`): file containing the jobs.
            update_pipeline_refs (:obj:`boolean`, optional): Default: ``True``.
            update_num_instances (:obj:`boolean`, optional): Default: ``False``.
            update_runtime_parameters (:obj:`boolean`, optional): Default: ``False``.
            update_labels (:obj:`boolean`, optional): Default: ``False``.
            update_migrate_offsets (:obj:`boolean`, optional): Default: ``True``.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self', 'jobs_file'))
        response = self._post(app='jobrunner',
                              endpoint='/v{}/jobs/importJobs'.format(self.api_version),
                              files={'file': jobs_file},
                              params=params,
                              headers={'content-type': None})
        return Command(self, response)

    def duplicate_job(self, job_id, body):
        """Duplicate an existing job.

        Args:
            job_id (:obj:`str`)
            body (:obj:`dict`)

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='jobrunner',
                              endpoint='/v{}/job/{}/duplicate'.format(self.api_version,
                                                                      job_id),
                              data=body)
        return Command(self, response)

    def export_jobs(self, body):
        """Export jobs as a compressed archive.

        Args:
            body (:obj:`list`): A list of job IDs.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='jobrunner',
                              endpoint='/v{}/jobs/exportJobs'.format(self.api_version),
                              data=body)
        return Command(self, response)

    def get_jobs_status(self, body):
        """Return job status for all given job IDs.

        Args:
            body (:obj:`list`): A list of job IDs.

        Returns:
            A :obj:`dict` with job ID keys and job data as values.
        """
        response = self._post(app='jobrunner',
                              endpoint='/v{}/jobs/status'.format(self.api_version),
                              data=body)
        return Command(self, response)

    def get_current_job_status(self, job_id):
        """Returns the current job status for given job id.

        Args:
            job_id (:obj:`str`)

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`
        """
        response = self._get(app='jobrunner',
                             endpoint='/v{}/job/{}/currentStatus'.format(self.api_version, job_id))
        return Command(self, response)

    def get_all_jobs_status(self, organization, offset, len, with_wrapper=False):
        """Return all job status.

        Args:
            organization (:obj:`str`).
            offset (:obj:`str`).
            len (:obj:`str`).
            with_wrapper (:obj:`bool`, optional): Default: ``False``

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self'))
        response = self._get(app='jobrunner',
                             endpoint='/v{}/jobs/status'.format(self.api_version),
                             params=params)
        return Command(self, response)

    def get_job_status_history(self, job_id, offset, len, with_wrapper=False):
        """Returns history of Job Status for given Job ID.

        Args:
            job_id (:obj:`str`)
            offset (:obj:`int`)
            len (:obj:`int`)
            with_wrapper (:obj:`bool`, optional): Default: ``False``

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self', 'job_id'))
        response = self._get(app='jobrunner',
                             endpoint='/v{}/job/{}/history'.format(self.api_version, job_id),
                             params=params)
        return Command(self, response)

    def get_job_status_history_for_run(self, job_status_id, offset, len, with_wrapper=False):
        """Returns Job Status History of a Job for a particular run.

        Args:
            job_status_id (:obj:`str`)
            offset (:obj:`int`)
            len (:obj:`int`)
            with_wrapper (:obj:`bool`, optional): Default: ``False``

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self', 'job_status_id'))
        response = self._get(app='jobrunner',
                             endpoint='/v{}/job/{}/jobStatusHistory'.format(self.api_version, job_status_id),
                             params=params)
        return Command(self, response)

    def get_job_acl(self, job_id):
        """Get job ACL.

        Args:
            job_id (:obj:`str`).

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._get(app='jobrunner', endpoint='/v{}/job/{}/acl'.format(self.api_version, job_id))
        return Command(self, response)

    def set_job_acl(self, job_id, job_acl_json):
        """Update job ACL.

        Args:
            job_id (:obj:`str`).
            job_acl_json (:obj:`str`): Job ACL in JSON format.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='jobrunner', endpoint='/v{}/job/{}/acl'.format(self.api_version,
                                                                                 job_id),
                              data=job_acl_json)
        return Command(self, response)

    def start_job(self, job_id):
        """Starts the job.

        Args:
            job_id (:obj:`str`)

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.JobStartStopCommand`.
        """
        response = self._post(app='jobrunner',
                              endpoint='/v{}/job/{}/start'.format(self.api_version, job_id))
        return JobStartStopCommand(self, response)

    def start_jobs(self, job_ids_json):
        """Starts Job for all given Job IDs.

        Args:
            job_ids_json (:obj:`str`): Job IDs in JSON format.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='jobrunner',
                              endpoint='/v{}/jobs/startJobs'.format(self.api_version),
                              data=job_ids_json)
        return StartJobsCommand(self, response)

    def stop_job(self, job_id):
        """Stops the job.

        Args:
            job_id (:obj:`str`)

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.JobStartStopCommand`.
        """
        response = self._post(app='jobrunner',
                              endpoint='/v{}/job/{}/stop'.format(self.api_version, job_id))
        return JobStartStopCommand(self, response)

    def force_stop_job(self, job_id):
        """Force stop Job for given Job ID.

        Args:
            job_id (:obj:`str`)

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.JobStartStopCommand`.
        """
        response = self._post(app='jobrunner',
                              endpoint='/v{}/job/{}/forceStop'.format(self.api_version, job_id))
        return JobStartStopCommand(self, response)

    def stop_jobs(self, job_ids_json):
        """Stops Job for all given Job IDs.

        Args:
            job_ids_json (:obj:`str`): Job IDs in JSON format.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='jobrunner',
                              endpoint='/v{}/jobs/stopJobs'.format(self.api_version),
                              data=job_ids_json)
        return Command(self, response)

    def force_stop_jobs(self, job_ids_json):
        """Force Stops Job for all given Job IDs.

        Args:
            job_ids_json (:obj:`str`): Job IDs in JSON format.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='jobrunner',
                              endpoint='/v{}/jobs/forceStopJobs'.format(self.api_version),
                              data=job_ids_json)
        return Command(self, response)

    def job_acknowledge_error(self, job_id):
        """Acknowledge Error for given Job ID.

        Args:
            job_id (:obj:`str`)

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='jobrunner',
                              endpoint='/v{}/job/{}/acknowledgeError'.format(self.api_version, job_id))
        return Command(self, response)

    def jobs_acknowledge_errors(self, job_ids_json):
        """Acknowledge Errors for all given Job IDs.

        Args:
            job_ids_json (:obj:`str`): Job IDs in JSON format.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='jobrunner',
                              endpoint='/v{}/jobs/acknowledgeErrors'.format(self.api_version),
                              data=job_ids_json)
        return Command(self, response)

    def sync_job(self, job_id):
        """Sync job.

        Args:
            job_id (:obj:`str`)

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='jobrunner',
                              endpoint='/v{}/job/{}/sync'.format(self.api_version, job_id))
        return Command(self, response)

    def sync_jobs(self, job_ids_json):
        """Sync Job for all given Job IDs.

        Args:
            job_ids_json (:obj:`str`): Job IDs in JSON format.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='jobrunner',
                              endpoint='/v{}/jobs/syncJobs'.format(self.api_version),
                              data=job_ids_json)
        return Command(self, response)

    def balance_jobs(self, job_ids_json):
        """Balance Jobs for all given Job IDs.

        Args:
            job_ids_json (:obj:`str`): Job IDs in JSON format.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='jobrunner',
                              endpoint='/v{}/jobs/balanceJobs'.format(self.api_version),
                              data=job_ids_json)
        return Command(self, response)

    def update_job_policies(self, body, organization=None):
        """Update a Job's configured Policies.

        Args:
            body (:obj:`dict`)
            organization (:obj:`str`, optional): Default: ``None``

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self', 'body'))
        response = self._post(app='jobrunner',
                              endpoint='/v{}/jobPolicy'.format(self.api_version),
                              data=body)
        return Command(self, response)

    def get_job_policies(self, job_id, organization=None):
        """Get a Job's configured Policies.

        Args:
            job_id (:obj:`str`)
            organization (:obj:`str`, optional): Default: ``None``

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self', 'job_id'))
        response = self._get(app='jobrunner',
                             endpoint='/v{}/jobPolicy/{}'.format(self.api_version, job_id),
                             params=params)
        return Command(self, response)

    def get_job_sankey_metrics(self, job_id, metric_type, pipeline_version, sdc_id, time_filter_condition,
                               include_error_count):
        """Get a Job's metrics.

        Args:
            job_id (:obj:`str`)
            metric_type (:obj:`str`)
            pipeline_version (:obj:`str`)
            sdc_id (:obj:`str`)
            time_filter_condition (:obj:`str`)
            include_error_count (:obj:`str`)

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self', 'job_id'))
        response = self._get(app='timeseries',
                             endpoint='/v{}/metrics/job/{}/sankey'.format(self.api_version, job_id),
                             params=params)
        return Command(self, response)

    def get_job_time_series_metrics(self, body, time_filter_condition, limit=1000):
        """Get a Job's time series metrics.

        Args:
            body (:obj:`dict`)
            time_filter_condition (:obj:`str`)
            limit (:obj:`str`, optional): Default: ``1000``.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self', 'body'))
        response = self._post(app='timeseries',
                              endpoint='/v{}/metrics/query'.format(self.api_version),
                              params=params,
                              data=body)
        return Command(self, response)

    def reset_jobs_offset(self, job_ids):
        """Reset all pipeline offsets for given job ids.

        Args:
            job_ids (:obj:`list`)

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='jobrunner',
                              endpoint='/v{}/jobs/resetOffset'.format(self.api_version),
                              data=job_ids)
        return Command(self, response)

    def upload_job_offset(self, job_id, offset_file):
        """Upload offset for a given job.

        Args:
            job_id (:obj:`str`)
            offset_file (:obj:`file`): File containing offsets.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='jobrunner',
                              endpoint='/v{}/job/{}/uploadOffset'.format(self.api_version, job_id),
                              files={'file': offset_file},
                              headers={'content-type': None})
        return Command(self, response)

    def upload_job_offset_as_json(self, job_id, offset_json):
        """Upload offset for a given job as json.

        Args:
            job_id (:obj:`str`)
            offset_json (:obj:`dict`): offsets json.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='jobrunner',
                              endpoint='/v{}/job/{}/uploadOffsetAsJson'.format(self.api_version, job_id),
                              data=offset_json)
        return Command(self, response)

    def get_all_registered_executors(self, organization, executor_type, edge, label, version, offset, len_, order_by,
                                     order, with_wrapper=False):
        """Gets all registered Executors.

        Args:
            organization (:obj:`str`)
            edge (:obj:`str`)
            label (:obj:`str`)
            version (:obj:`str`)
            offset (:obj:`str`)
            len_ (:obj:`str`)
            order_by (:obj:`str`)
            order (:obj:`str`)
            with_wrapper (:obj:`bool`, optional): Default: ``False``
        """
        params = get_params(parameters=locals(), exclusions=('self'))
        response = self._get(app='jobrunner',
                             endpoint='/v{}/sdcs'.format(self.api_version),
                             params=params)
        return Command(self, response)

    def get_all_registered_executor_labels(self, organization, executor_type, edge=False, offset=0, len=-1,
                                           with_wrapper=False):
        """Return labels for all registered SDC instances.

        Args:
            organization (:obj:`str`)
            executor_type (:obj:`str`)
            edge (:obj:`bool`, optional): Default: ``False``
            offset (:obj:`int`, optional): Default: ``0``
            len (:obj:`int`, optional): Default: ``-1``
            with_wrapper (:obj:`bool`): Default: ``False``

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self'))
        response = self._get(app='jobrunner',
                             endpoint='/v{}/sdcs/labels'.format(self.api_version),
                             params=params)
        return Command(self, response)

    def get_all_registered_executor_versions(self, organization, executor_type, edge=False, offset=0, len=-1,
                                             with_wrapper=False):
        """Return versions for all registered SDC instances.

        Args:
            organization (:obj:`str`)
            executor_type (:obj:`str`)
            edge (:obj:`bool`, optional): Default: ``False``
            offset (:obj:`int`, optional): Default: ``0``
            len (:obj:`int`, optional): Default: ``-1``
            with_wrapper (:obj:`bool`): Default: ``False``

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self'))
        response = self._get(app='jobrunner',
                             endpoint='/v{}/sdcs/versions'.format(self.api_version),
                             params=params)
        return Command(self, response)

    def get_sdc(self, data_collector_id):
        """Return SDC for given SDC ID.

        Args:
            data_collector_id (:obj:`str`)

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._get(app='jobrunner',
                             endpoint='/v{}/sdc/{}'.format(self.api_version, data_collector_id))
        return Command(self, response)

    def delete_sdc(self, data_collector_id):
        """Delete SDC for given SDC ID.

        Args:
            data_collector_id (:obj:`str`)

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._delete(app='jobrunner',
                                endpoint='/v{}/sdc/{}'.format(self.api_version, data_collector_id))
        return Command(self, response)

    def update_sdc_labels(self, data_collector_id, data_collector_json):
        """Update labels for given SDC ID.

        Args:
            data_collector_id (:obj:`str`)
            data_collector_json (:obj:`str`): Data collector in JSON format. Complies to Swagger SDCJson definition.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='jobrunner',
                              endpoint='/v{}/sdc/{}/updateLabels'.format(self.api_version, data_collector_id),
                              data=data_collector_json)
        return Command(self, response)

    def get_sdc_lables(self, data_collector_id):
        """Returns all labels assigned to SDC.

        Args:
            data_collector_id (:obj:`str`)

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._get(app='jobrunner',
                             endpoint='/v{}/sdc/{}/labels'.format(self.api_version, data_collector_id))
        return Command(self, response)

    def get_pipelines_running_in_sdc(self, data_collector_id):
        """Returns pipelines running inside an sdc.

        Args:
            data_collector_id (:obj:`str`)

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._get(app='jobrunner',
                             endpoint='/v{}/sdc/{}/pipelines'.format(self.api_version, data_collector_id))
        return Command(self, response)

    def balance_data_collectors(self, body):
        """Balance all jobs running on given Data Collectors.

        Args:
            body (:obj:`list`): List of pipeline ids.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='jobrunner',
                              endpoint='/v{}/jobs/balanceSDCs'.format(self.api_version),
                              data=body)
        return Command(self, response)

    def update_sdc_resource_thresholds(self, data_collector_id, data_collector_json):
        """Update data collector resource thresholds.

        Args:
            data_collector_id (:obj:`str`)
            data_collector_json (:obj:`str`): Data collector in JSON format. Complies to Swagger SDCJson definition.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='jobrunner',
                              endpoint='/v{}/sdc/{}/updateSdcResourceThresholds'.format(self.api_version,
                                                                                        data_collector_id),
                              data=data_collector_json)
        return Command(self, response)

    def clear_pipelines_committed_from_data_collector(self, data_collector_id):
        """Clear pipelines committed set for given Data Collector Instance.

        Args:
            data_collector_id (:obj:`str`)

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='jobrunner',
                              endpoint='/v{}/sdc/clearPipelinesCommitted/{}'.format(self.api_version,
                                                                                    data_collector_id))
        return Command(self, response)

    def get_all_job_tags(self, organization, parent_id=None, offset=None, len=None, order=None):
        """Get job tags for a given organization.

        Args:
            organization (:obj:`str`)
            parent_id (:obj:`str`, optional): Default: ``None``
            offset (:obj:`int`, optional): Default: ``None``
            len (obj:`int`, optional): Default: ``None``
            order (:obj:`str`, optional): Default: ``None``

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self'))
        response = self._get(app='jobrunner',
                             endpoint='/v{}/jobs/tags'.format(self.api_version),
                             params=params)
        return Command(self, response)

    def return_all_provisioning_agents(self, organization, offset, len, order_by, order):
        """Returns all provisioning agents.

        Args:
            organization (:obj:`str`)
            offset (:obj:`str`)
            len (:obj:`str`)
            order_by (:obj:`str`)
            order (:obj:`str`)

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self'))
        response = self._get(app='provisioning',
                             endpoint='/v{}/dpmAgents'.format(self.api_version),
                             params=params)
        return Command(self, response)

    def get_provisioning_agent(self, agent_id):
        """Returns a provisioning agent by id.

        Args:
            agent_id (:obj:`str`)

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._get(app='provisioning',
                             endpoint='/v{}/dpmAgent/{}'.format(self.api_version, agent_id))
        return Command(self, response)

    def delete_provisioning_agent(self, agent_id):
        """Deletes a provisioning agent by id.

        Args:
            agent_id (:obj:`str`)

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._delete(app='provisioning',
                                endpoint='/v{}/dpmAgent/{}'.format(self.api_version, agent_id))
        return Command(self, response)

    def return_all_legacy_deployments(self, organization, offset, len, order_by, order, dpm_agent_id,
                                      deployment_status):
        """Returns all provisioning agents.

        Args:
            organization (:obj:`str`)
            offset (:obj:`str`)
            len (:obj:`str`)
            order_by (:obj:`str`)
            order (:obj:`str`)
            dpm_agent_id (:obj:`str`)
            deployment_status (:obj:`str`)

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self'))
        response = self._get(app='provisioning',
                             endpoint='/v{}/deployments'.format(self.api_version),
                             params=params)
        return Command(self, response)

    def get_legacy_deployment(self, deployment_id):
        """Returns a deployment by id.

        Args:
            deployment_id (:obj:`str`)

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._get(app='provisioning',
                             endpoint='/v{}/deployment/{}'.format(self.api_version, deployment_id))
        return Command(self, response)

    def create_legacy_deployment(self, body):
        """Create a new deployment for the given Deployment model.

        Args:
            body (:obj:`dict`): JSON representation of deployment object.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._put(app='provisioning',
                             data=body,
                             endpoint='/v{}/deployments'.format(self.api_version))
        return Command(self, response)

    def update_legacy_deployment(self, deployment_id, body):
        """Update a deployment for the given Deployment model.

        Args:
            deployment_id (:obj:`str`): Deployment ID.
            body (:obj:`dict`): Deployment object json.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='provisioning',
                              data=body,
                              endpoint='/v{}/deployment/{}'.format(self.api_version, deployment_id))
        return Command(self, response)

    def scale_legacy_deployment(self, deployment_id, num_instances):
        """Scale up/down active deployment.

        Args:
            deployment_id (:obj:`str`): Deployment ID.
            num_instances (:obj:`int`): Number of sdc instances.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self', 'deployment_id'))
        response = self._post(app='provisioning',
                              endpoint='/v{}/deployment/{}/scale'.format(self.api_version, deployment_id),
                              params=params)
        return Command(self, response)

    def wait_for_legacy_deployment_statuses(self, deployment_id, statuses, timeout_sec=300):
        """Wait for deployment status.

        Args:
            deployment_id (:obj:`str`)
            statuses (:obj:`list`): List of Deployment statuses.
            timeout_sec (:obj:`int`, optional): Timeout for wait, in seconds. Default: ``300``.
        """
        def condition(deployment_id):
            current_status = self.get_legacy_deployment(deployment_id).response.json()['currentDeploymentStatus']['status']
            logger.debug('Status of deployment (id: %s) is %s ...', deployment_id, current_status)
            if current_status == 'INACTIVE_ERROR':
                raise LegacyDeploymentInactiveError('Deployment status changed to INACTIVE_ERROR')
            return current_status in statuses

        def failure(timeout):
            raise Exception('Timed out after {} seconds while waiting for status.'.format(timeout))

        def success(time):
            logger.debug('Deployment reached desired status after %s s.', time)

        logger.debug('Deployment %s waiting for status %s ...', deployment_id, statuses)
        wait_for_condition(condition=condition, condition_kwargs={'deployment_id': deployment_id}, timeout=timeout_sec,
                           failure=failure, success=success)

    def start_legacy_deployment(self, deployment_id, dpm_agent_id):
        """Starts a deployment.

        Args:
            deployment_id (:obj:`str`)
            dpm_agent_id (:obj:`str`)

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self', 'deployment_id'))
        response = self._post(app='provisioning',
                              endpoint='/v{}/deployment/{}/start'.format(self.api_version, deployment_id),
                              params=params)
        return DeploymentStartStopCommand(self, response)

    def stop_legacy_deployment(self, deployment_id):
        """Starts a deployment.

        Args:
            deployment_id (:obj:`str`)

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='provisioning',
                              endpoint='/v{}/deployment/{}/stop'.format(self.api_version, deployment_id))
        return DeploymentStartStopCommand(self, response)

    def legacy_deployments_acknowledge_errors(self, body):
        """Acknowledge deployment errors.

        Args:
            body (:obj:`list`): Deployment IDs.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='provisioning',
                              data=body,
                              endpoint='/v{}/deployments/acknowledgeErrors'.format(self.api_version))
        return Command(self, response)

    def delete_legacy_deployment(self, deployment_id):
        """Delete a deployment for the given deployment ID.

        Args:
            deployment_id (:obj:`str`): Deployment ID.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._delete(app='provisioning',
                                endpoint='/v{}/deployment/{}'.format(self.api_version, deployment_id))
        return Command(self, response)

    def delete_legacy_deployments(self, body):
        """Delete all deployments for the given deployment IDs.

        Args:
            body (:obj:`list`): Deployment IDs.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='provisioning',
                              data=body,
                              endpoint='/v{}/deployments/deleteDeployments'.format(self.api_version))
        return Command(self, response)

    def return_all_topologies(self, organization, offset, len, order_by, order, with_wrapper=False, filter_text=None):
        """Returns all jobs.

        Args:
            organization (:obj:`str`)
            offset (:obj:`str`)
            len (:obj:`str`)
            order_by (:obj:`str`)
            order (:obj:`str`)
            with_wrapper (:obj:`bool`, optional): Default: ``False``
            filter_text (:obj:`str`, optional): Default: ``None``

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self'))
        response = self._get(app='topology',
                             endpoint='/v{}/topologies'.format(self.api_version),
                             params=params)
        return Command(self, response)

    def get_topology_for_commit_id(self, commit_id, organization=None, validate=None):
        """Get topology for given commit ID.

        Args:
            commit_id (:obj:`str`)
            organization (:obj:`str`)
            validate (:obj:`bool`)

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self', 'commit_id'))
        response = self._get(app='topology',
                             endpoint='/v{}/topology/{}'.format(self.api_version, commit_id),
                             params=params)
        return Command(self, response)

    def get_topology_commits(self, topology_id, organization, offset=0, len=-1, order='ASC', with_wrapper=False):
        """Get all topology commits for given topology ID.

        Args:
            topology_id (:obj:`str`)
            organization (:obj:`str`)
            offset (:obj:`int`, optional): Default: ``0``
            len (:obj:`int`, optional): Default: ``-1``
            order (:obj:`str`, optional): Default: ``'ASC'``
            with_wrapper (:obj:`bool`, optional): Default: ``False``

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self', 'topology_id'))
        response = self._get(app='topology',
                             endpoint='v{}/topology/{}/log'.format(self.api_version, topology_id),
                             params=params)
        return Command(self, response)

    def create_topology(self, topology_json):
        """Create new topology.

        Args:
           topology_json (:obj:`str`): Topology in JSON format. Complies to Swagger TopologyJson definition.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._put(app='topology',
                             endpoint='/v{}/topologies'.format(self.api_version),
                             data=topology_json)
        return Command(self, response)

    def create_topology_draft(self, commit_id):
        """Create a new draft for an existing Topology

        Args:
            commit_id (:obj:`str`): Commit ID for the topology you wish to create a draft. This should usually be the
            latest commit ID.
        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='topology',
                              endpoint='/v{}/topology/{}/createDraft'.format(self.api_version, commit_id))
        return Command(self, response)

    def update_topology(self, commit_id, topology_json):
        """Update topology.

        Args:
            commit_id (:obj:`str`)
            topology_json (:obj:`str`): Topology in JSON format. Complies to Swagger TopologyJson definition.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='topology',
                              endpoint='/v{}/topology/{}'.format(self.api_version, commit_id),
                              data=topology_json)
        return Command(self, response)

    def validate_topology(self, commit_id):
        """Validate an existing topology.

        Args:
            commit_id (:obj:`str`): The commit ID for the topology to be validated.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='topology',
                              endpoint='/v{}/topology/{}/validate'.format(self.api_version, commit_id))
        return Command(self, response)

    def import_topologies(self, topologies_file, update_num_instances=False, update_runtime_parameters=False,
                          update_labels=False, update_migrate_offsets=False):
        """Import topologies from compressed archive.

        Args:
            topologies_file (:obj:`file`): file containing the topologies.
            update_num_instances (:obj:`boolean`, optional): Default: ``False``.
            update_runtime_parameters (:obj:`boolean`, optional): Default: ``False``.
            update_labels (:obj:`boolean`, optional): Default: ``False``.
            update_migrate_offsets (:obj:`boolean`, optional): Default: ``False``.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self', 'topologies_file'))
        response = self._post(app='topology',
                              endpoint='/v{}/topologies/importTopologies'.format(self.api_version),
                              files={'file': topologies_file},
                              params=params,
                              headers={'content-type': None})
        return Command(self, response)

    def export_topologies(self, body=None):
        """Export topologies.

        Args:
            body (:obj:`list`): A list of :obj:`str` commit ids.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='topology',
                              endpoint='/v{}/topologies/exportTopologies'.format(self.api_version),
                              data=body)
        return Command(self, response)

    def delete_topologies(self, topologies_json):
        """Delete topologies for all given topology IDs.

        Args:
            topologies_json (:obj:`str`): Topologies in JSON format.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='topology',
                              endpoint='/v{}/topologies/deleteTopologies'.format(self.api_version),
                              data=topologies_json)
        return Command(self, response)

    def delete_topology_versions(self, commits_json):
        """Delete topologies commit for all given topology commit IDs.

        Args:
            commits_json (:obj:`str`): Topology commit IDs in JSON format.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='topology',
                              endpoint='/v{}/topologies/deleteTopologyVersions'.format(self.api_version),
                              data=commits_json)
        return Command(self, response)

    def publish_topology(self, commit_id, commit_message):
        """Publish topology.

        Args:
            commit_id (:obj:`str`)
            commit_message (:obj:`str`)

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='topology',
                              endpoint='/v{}/topology/{}/publish'.format(self.api_version, commit_id),
                              params={'commitMessage': commit_message})
        return Command(self, response)

    def return_all_report_definitions(self, organization, offset, len, order_by, order, filter_text):
        """Returns all jobs.

        Args:
            organization (:obj:`str`)
            offset (:obj:`str`)
            len (:obj:`str`)
            order_by (:obj:`str`)
            order (:obj:`str`)
            filter_text (:obj:`str`)

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self'))
        response = self._get(app='reporting',
                             endpoint='/v{}/reports'.format(self.api_version),
                             params=params)
        return Command(self, response)

    def return_all_reports_from_definition(self, report_definition_id, offset, len):
        """Return all Reports generated using given Report Definition Id.

        Args:
            report_definition_id (:obj:`str`): Report Definition Id.
            offset (:obj:`int`): Offset for the results returned.
            len (:obj:`int`): Total number of results returned.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self', report_definition_id))
        response = self._get(app='reporting',
                             endpoint='/v{}/report/{}/reports'.format(self.api_version, report_definition_id),
                             params=params)
        return Command(self, response)

    def get_report_for_given_report_id(self, report_definition_id, report_id):
        """Get report for given Report Id and Report Definition Id.

        Args:
            report_definition_id (:obj:`str`): Report Definition Id.
            report_id (:obj:`str`): Report Id.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._get(app='reporting',
                             endpoint='/v{}/report/{}/{}'.format(self.api_version, report_definition_id, report_id))
        return Command(self, response)

    def create_new_report_definition(self, body):
        """Create a new Report Definition.

        Args:
            body (:obj:`dict`): Report Definition in JSON format.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._put(app='reporting',
                             endpoint='/v{}/reports'.format(self.api_version),
                             data=body)
        return Command(self, response)

    def update_report_definition(self, report_definition_id, body):
        """Update an existing Report Definition.

        Args:
            body (:obj:`dict`): Report Definition in JSON format.
            report_definition_id (:obj:`str`): Report Definition Id.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='reporting',
                              endpoint='/v{}/report/{}'.format(self.api_version, report_definition_id),
                              data=body)
        return Command(self, response)

    def delete_report_definition(self, report_definition_id):
        """Delete an existing Report Definition.

        Args:
            report_definition_id (:obj:`str`): Report Definition id.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._delete(app='reporting',
                                endpoint='/v{}/report/{}'.format(self.api_version, report_definition_id))
        return Command(self, response)

    def generate_report_for_report_definition(self, report_definition_id, trigger_time):
        """Generate Report for given Report Definition.

        Args:
            report_definition_id (:obj:`str`): Report Definition id.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self', 'report_definition_id'))
        response = self._post(app='reporting',
                              endpoint='/v{}/report/{}/generateReport'.format(self.api_version, report_definition_id),
                              params=params)
        return Command(self, response)

    def download_report(self, report_definition_id, report_id, report_format):
        """Download Report in a report format for given report definition and report id.

        Args:
            report_definition_id (:obj:`str`): Report Definition id.
            report_id (:obj:`str`): Report id.
            report_format (:obj:`str`): Report Format ('PDF')

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self', 'report_definition_id', 'report_id'))
        response = self._get(app='reporting',
                             endpoint='/v{}/report/{}/{}/download'.format(self.api_version,
                                                                          report_definition_id,
                                                                          report_id),
                             params=params)
        return Command(self, response)

    def get_report_definition_acl(self, report_definition_id):
        """Get Report Definition ACL.

        Args:
            report_definition_id (:obj:`str`): Report Definition id.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._get(app='reporting',
                             endpoint='/v{}/report/{}/acl'.format(self.api_version, report_definition_id))
        return Command(self, response)

    def set_report_definition_acl(self, report_definition_id, report_definition_acl_json):
        """Update Report Definition ACL.

        Args:
            report_definition_id (:obj:`str`): Report Definition id.
            report_definition_acl_json (:obj:`str`): Report Definition ACL in JSON format.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='reporting',
                              endpoint='/v{}/report/{}/acl'.format(self.api_version, report_definition_id),
                              data=report_definition_acl_json)
        return Command(self, response)

    def update_report_definition_permissions(self, data, report_definition_id, subject_id):
        """Update the Report Definition permissions.

        Args:
            data (:obj:`dict`): JSON representation of permission attributes to update.
            report_definition_id (:obj:`str`): Report Definition id.
            subject_id (:obj:`str`): Id of the subject.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='reporting',
                              endpoint='/v{}/report/{}/permissions/{}'.format(self.api_version,
                                                                              report_definition_id,
                                                                              subject_id),
                              data=data)
        return Command(self, response)

    def return_all_pipeline_templates(self, pipeline_label_id, offset, len, order_by, order, system, filter_text,
                                      execution_modes, start_time=-1, end_time=-1, user_ids=None):
        """Returns all pipeline templates.

        Args:
            pipeline_label_id (:obj:`str`)
            offset (:obj:`str`)
            len (:obj:`str`)
            order_by (:obj:`str`)
            order (:obj:`str`)
            system (:obj:`str`)
            filter_text (:obj:`str`)
            execution_modes (:obj:`str`)
            start_time (:obj:`int`, optional): Default: ``-1``
            end_time (:obj:`int`, optional): Default: ``-1``
            user_ids (:obj:`list`, optional): List of strings. Default: ``None``

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`
        """
        params = get_params(parameters=locals(), exclusions=('self'))
        response = self._get(app='pipelinestore',
                             endpoint='v{}/pipelines/templates'.format(self.api_version),
                             params=params)
        return Command(self, response)

    def get_pipelines_using_fragment(self, fragment_commit_id, offset, len, order_by, order):
        """Get Latest Committed Pipelines using given fragment Commit ID.

        Args:
            fragment_commit_id (:obj:`str`): Pipeline Commit Id of fragment.
            offset (:obj:`str`)
            len (:obj:`str`)
            order_by (:obj:`str`)
            order (:obj:`str`)

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`
        """
        params = get_params(parameters=locals(), exclusions=('self', 'fragment_commit_id'))
        response = self._get(app='pipelinestore',
                             endpoint='/v{}/pipelineCommit/{}/pipelinesUsingFragment'.format(self.api_version,
                                                                                             fragment_commit_id),
                             params=params)
        return Command(self, response)

    def update_pipelines_with_fragment_commit_version(self, body, from_fragment_commit_id, to_fragment_commit_id):
        """Update pipelines with latest pipeline fragment commit version.

        Args:
            body (:obj:`list`): List of pipeline commit IDs.
            from_fragment_commit_id (:obj:`str`): commit ID of fragment from which the pipeline needs to be updated.
            to_fragment_commit_id (obj: `str`): commit ID of fragment to which the pipeline needs to be updated.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`
        """
        response = self._post(app='pipelinestore',
                              endpoint='/v{}/pipelines/updateFragmentVersion/{}/{}'.format(self.api_version,
                                                                                           from_fragment_commit_id,
                                                                                           to_fragment_commit_id),
                              data=body)
        return Command(self, response)

    def get_all_user_roles(self):
        response = self._get(app='security',
                             endpoint='/v{}/roles'.format(self.api_version))
        return response.json()

    def get_server_info(self):
        """Get the Control Hub server info.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._get(app=None,
                             endpoint='/v{}/server/info'.format(self.api_version),
                             rest='rest')
        return Command(self, response)

    def update_job_permissions(self, data, job_id, subject_id):
        """Update the job permissions.

        Args:
            data (:obj:`dict`): JSON representation of permission attributes to update.
            job_id (:obj:`str`): Id of the job.
            subject_id (:obj:`str`): Id of the subject.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='jobrunner',
                              endpoint='/v{}/job/{}/permissions/{}'.format(self.api_version, job_id, subject_id),
                              data=data)
        return Command(self, response)

    def update_pipeline_permissions(self, data, pipeline_id, subject_id):
        """Update the pipeline permissions.

        Args:
            data (:obj:`dict`): JSON representation of permission attributes to update.
            pipeline_id (:obj:`str`): Id of the pipeline.
            subject_id (:obj:`str`): Id of the subject.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='pipelinestore',
                              endpoint='/v{}/pipeline/{}/permissions/{}'.format(self.api_version,
                                                                                pipeline_id,
                                                                                subject_id),
                              data=data)
        return Command(self, response)

    def update_sdc_permissions(self, data, sdc_id, subject_id):
        """Update the DataCollector permissions.

        Args:
            data (:obj:`dict`): JSON representation of permission attributes to update.
            sdc_id (:obj:`str`): Id of the DataCollector.
            subject_id (:obj:`str`): Id of the subject.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='jobrunner',
                              endpoint='/v{}/sdc/{}/permissions/{}'.format(self.api_version,
                                                                           sdc_id,
                                                                           subject_id),
                              data=data)
        return Command(self, response)

    def get_executor_acl(self, executor_id):
        """Get Executor ACL.

        Args:
            executor_id (:obj:`str`): Id of the Executor.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._get(app='jobrunner', endpoint='/v{}/sdc/{}/acl'.format(self.api_version, executor_id))
        return Command(self, response)

    def set_executor_acl(self, executor_id, executor_acl_json):
        """Set Executor ACL.

        Args:
            executor_id (:obj:`str`): Id of the Executor.
            executor_acl_json (:obj:`dict`): Python Object representation of ACL JSON.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='jobrunner',
                              endpoint='/v{}/sdc/{}/acl'.format(self.api_version, executor_id),
                              data=executor_acl_json)
        return Command(self, response)

    def get_connection_acl(self, connection_id):
        """Get Connection ACL.

        Args:
            connection_id (:obj:`str`): ID of the Connection.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._get(app='connection',
                             endpoint='/v{}/connection/{}/acl'.format(self.api_version, connection_id))
        return Command(self, response)

    def update_connection_acl(self, connection_id, body):
        """Set Connection ACL.

        Args:
            connection_id (:obj:`str`): ID of the Connection.
            body (:obj:`dict`): Python Object representation of ACL JSON.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='connection',
                              endpoint='/v{}/connection/{}/acl'.format(self.api_version, connection_id),
                              data=body)
        return Command(self, response)

    def update_connection_permissions(self, body, connection_id, subject_id):
        """Update the connection permissions.

        Args:
            body (:obj:`dict`): JSON representation of permission attributes to update.
            connection_id (:obj:`str`): ID of the connection.
            subject_id (:obj:`str`): ID of the subject.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='connection',
                              endpoint='/v{}/connection/{}/permissions/{}'.format(self.api_version,
                                                                                  connection_id,
                                                                                  subject_id),
                              data=body)
        return Command(self, response)

    def get_job_selection_types(self, api_version):
        """Fetches available job selection type in Scheduler.

        Args:
            api_version (:obj:`int`): Control Hub API Version to use.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        pageId = 'SchedulerJobTypeSelectorPage'
        response = self._get(app='scheduler',
                             endpoint='/v{}/jobs/o:jobTypeSelector/pageId={}'.format(api_version, pageId))
        return Command(self, response)

    def trigger_selection_info(self, data, api_version):
        """Triggers selection info for a given job type.

        Args:
            data (:obj:`dict`): Python Object representation for RestRequestRSchedulerTypeJobSelector.
            api_version (:obj:`int`): Control Hub API Version to use.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        pageId = 'SchedulerJobCreatePage'
        response = self._post(app='scheduler',
                              endpoint='/v{}/jobs/o:new/pageId={}'.format(api_version, pageId),
                              data=data)
        return Command(self, response)

    def get_scheduled_tasks(self, order_by, offset, len, api_version):
        """List the scheduled tasks.

        Args:
            order_by (:obj:`str`): Order results by this field.
            offset (:obj:`int`): Offset for the results returned.
            len (:obj:`int`): Total number of results returned.
            api_version (:obj:`int`): Control Hub API Version to use.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self', 'api_version'))
        pageId = 'SchedulerJobListPage'
        response = self._get(app='scheduler',
                             endpoint='/v{}/jobs/pageId={}'.format(api_version, pageId),
                             params=params)
        return Command(self, response)

    def get_scheduled_task(self, id, run_info, audit_info, api_version):
        """Fetch the scheduled task for a given job.

        Args:
            id (:obj:`str`): Task id.
            run_info (:obj:`boolean`): Param to specify if run info is needed.
            audit_info (:obj:`boolean`): Param to specify if audit info is needed.
            api_version (:obj:`int`): Control Hub API Version to use.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self', 'id', 'api_version'))
        pageId = 'SchedulerJobManagePage'
        response = self._get(app='scheduler',
                             endpoint='/v{}/jobs/{}/pageId={}'.format(api_version, id, pageId),
                             params=params)
        return Command(self, response)

    def create_scheduled_task(self, data, api_version):
        """Creates a new Scheduled Task.

        Args:
            data (:obj:`dict`): Python Object representation for RestRequestRSchedulerJob.
            api_version (:obj:`int`): Control Hub API Version to use.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        pageId = 'SchedulerJobManagePage'
        response = self._put(app='scheduler',
                             endpoint='/v{}/jobs/pageId={}'.format(api_version, pageId),
                             data=data)
        return Command(self, response)

    def perform_action_on_scheduled_task(self, id, action, api_version):
        """Perform an action on a scheduled task.

        Args:
            id (:obj:`str`): Id of the scheduled task.
            action (:obj:`str`): Action to be performed on task (['PAUSE', 'RESUME', 'KILL', 'DELETE']).
            api_version (:obj:`int`): Control Hub API Version to use.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self', 'id', 'api_version'))
        pageId = 'SchedulerJobManagePage'
        response = self._post(app='scheduler',
                              endpoint='/v{}/jobs/{}/o:action/pageId={}'.format(api_version, id, pageId),
                              params=params)
        return Command(self, response)

    def get_all_event_subscriptions(self, organization, offset, len, order_by, order, with_wrapper=False):
        """Get all event subscriptions.

        Args:
            organization (:obj:`str`): Id of the organization.
            offset (:obj:`int`): Offset for the results returned.
            len (:obj:`int`): Total number of results returned.
            order_by (:obj:`str`): Order results by this field.
            order (:obj:`str`): One of {``'ASC'``, ``'DESC'``}.
            with_wrapper (:obj:`bool`, optional): Default: ``False``

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self'))
        response = self._get(app='notification',
                             endpoint='/v{}/eventsub'.format(self.api_version),
                             params=params)
        return Command(self, response)

    def create_event_subscription(self, body):
        """Create a new event subscription.

        Args:
            body (:obj:`dict`): Subscription object that complies to Swagger EventSubscriptionJson definition.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._put(app='notification',
                             endpoint='/v{}/eventsub/createEventSub'.format(self.api_version),
                             data=body)
        return Command(self, response)

    def update_event_subscription(self, body):
        """Update an existing event subscription.

        Args:
            body (:obj:`dict`): Subscription object that complies to Swagger EventSubscriptionJson definition.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='notification',
                              endpoint='/v{}/eventsub/updateEventSub'.format(self.api_version),
                              data=body)
        return Command(self, response)

    def delete_event_subscription(self, subscription_id):
        """Delete an existing event subscription.

        Args:
            subscription_id (:obj:`str`): Id of the Subscription.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='notification',
                              endpoint='/v{}/eventsub/deleteEventSub'.format(self.api_version),
                              data=subscription_id)
        return Command(self, response)

    def event_subscription_acknowledge_error(self, subscription_id):
        """Acknowledge an error on given Event Subscription.

        Args:
            subscription_id (:obj:`str`): Id of the Subscription.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='notification',
                              endpoint='/v{}/eventsub/ackEventSubError'.format(self.api_version),
                              data=subscription_id)
        return Command(self, response)

    def get_all_subscription_audits(self, offset=None, len_=None, order_by='CREATED_TIME', order='ASC',
                                    with_wrapper=False):
        """Get all external action audits.

        Args:
            offset (:obj:`str`, optional): Default: ``None``
            len_ (:obj:`str`, optional): Default: ``None``
            order_by (:obj:`str`, optional): Default: ``'CREATED_TIME'``
            order (:obj:`str`, optional): Default: ``'ASC'``
            with_wrapper (:obj:`bool`, optional): Default: ``False``

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self'))
        if 'len_' in params:
            params['len'] = params.pop('len_')
        endpoint = '/v{}/externalActions/audits'.format(self.api_version)
        response = self._get(app='notification',
                             endpoint=endpoint,
                             params=params)
        return Command(self, response)

    def is_ldap_enabled(self):
        """Check if ldap is enabled.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._get(app='security',
                             endpoint='/v{}/ldap'.format(self.api_version))
        return Command(self, response)

    def get_all_executor_stats(self, label=None, offset=None, len=None, order_by='LAST_REPORTED_TIME', order='ASC',
                               executor_type='COLLECTOR'):
        """Returns executor uptime, Memory/CPU usage by executor at JVM level.

        Args:
            label (:obj:`str`, optional): Default: ``None``.
            offset (:obj:`int`, optional): Default: ``None``.
            len (obj:`int`, optional): Default: ``None``.
            order_by (:obj:`str`, optional): Default: ``LAST_REPORTED_TIME``.
            order (:obj:`str`, optional): Default: ``ASC``.
            executor_type (:obj:`str`, optional): Default: ``COLLECTOR``.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self'))
        response = self._get(app='jobrunner',
                             endpoint='/v{}/metrics/executors'.format(self.api_version),
                             params=params)
        return Command(self, response)

    def get_job_metrics(self, job_id, run_count=None, sdc_id=None):
        """Get job metrics. If runCount is empty or 0, latest run metrics are returned. Otherwise, metrics for the given
        run count are returned.

        Args:
            job_id (:obj:`str`)
            run_count (:obj:`int`, optional): Default ``None``.
            sdc_id (:obj:`str`, optional): Default: ``None``.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self'))
        response = self._get(app='jobrunner',
                             endpoint='/v{}/metrics/job/{}'.format(self.api_version, job_id),
                             params=params)
        return Command(self, response)

    def get_tunneling_instance_id(self, engine_id):
        """Get tunneling instance id related to an execution engine.

        Args:
            engine_id (:obj:`str`): Id of an execution engine.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        fetched_response = None

        def _fetch_tunneling_instance_id(api_client):
            try:
                url = '{}/tunneling/rest/connection/{}'.format(self.base_url, engine_id)
                response = self._get(absolute_endpoint=True, endpoint=url)
                if not response:
                    raise Exception('This Engine is not accessible. There is no active WebSocket session to the'
                                    'Tunneling application from this engine. Trying again ...')
                tunneling_instance_id = response.json()['instanceId']
                logger.debug('Fetched tunneling_instance_id is %s', tunneling_instance_id)
                nonlocal fetched_response
                fetched_response = response
                return response
            except requests.exceptions.HTTPError as http_error:
                logger.debug('Call to fetch tunneling instance id endpoint failed. Trying again ...')
            except KeyError:
                logger.debug('Invalid tunneling instance id received. Trying again ...')
            except Exception as ex:
                logger.debug(ex)
        wait_for_condition(_fetch_tunneling_instance_id, [self], timeout=300)
        return Command(self, fetched_response)

    def get_job_realtime_summary(self, engine_id, pipeline_id):
        """Get job realtime summary.

        Args:
            engine_id (:obj:`str`)
            pipeline_id (:obj:`str`)

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self', 'engine_id', 'pipeline_id'))

        tunneling_instance_id = self.get_tunneling_instance_id(engine_id).response.json()['instanceId']
        url_template = '{}/tunneling/rest/{}/rest/v{}/pipeline/{}/metrics'
        url = url_template.format(self.base_url,  engine_id, self.api_version, pipeline_id)
        params.update({'onlyIfExists': True, 'TUNNELING_INSTANCE_ID': tunneling_instance_id})

        response = self._get(absolute_endpoint=True, endpoint=url, params=params)
        return Command(self, response)

    def get_job_latest_metrics(self, job_id, sdc_id=None):
        """Returns latest job metrics.

        Args:
            job_id (:obj:`str`)
            sdc_id (:obj:`str`, optional): Default: ``None``.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self', 'job_id'))
        response = self._get(app='timeseries',
                             endpoint='/v{}/metrics/job/{}/latestMetrics'.format(self.api_version, job_id),
                             params=params)
        return Command(self, response)

    def get_job_count_by_status(self):
        """Get job status and job counts mapping.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._get(app='jobrunner',
                             endpoint='/v{}/metrics/jobCountByStatus'.format(self.api_version))
        return Command(self, response)

    def get_job_record_count_for_all_runs(self, job_id, sdc_id=None):
        """Get record counts of all runs of a job.

        Args:
            job_id (:obj:`str`)
            sdc_id (:obj:`str`, optional): Default: ``None``.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self', 'job_id'))
        response = self._get(app='timeseries',
                             endpoint='/v{}/metrics/job/{}/recordCountsForAllRuns'.format(self.api_version, job_id),
                             params=params)
        return Command(self, response)

    def list_acl_audits(self, organization=None, offset=None, len=None, sort_field=None, sort_order=None):
        """Get all user actions for given Organization ID.

        Args:
            organization (:obj:`str`, optional): Default: ``None``.
            offset (:obj:`int`, optional): Default: ``None``.
            len (:obj:`int`, optional): Default: ``None``.
            sort_field (:obj:`str`, optional): Default: ``None``.
            sort_order (:obj:`str`, optional): Default: ``None``.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self'))
        response = self._get(app='jobrunner',
                             endpoint='/v{}/metrics/listAclAudits'.format(self.api_version),
                             params=params)
        return Command(self, response)

    def get_problematic_jobs(self, organization=None, offset=None, len=None, order_by='NAME', order='ASC', removed=None,
                             system=None, filter_text=None, job_status='INACTIVE', job_label=None,
                             executor_type='COLLECTOR'):
        """Get all jobs with red state.

        Args:
            organization (:obj:`str`, optional): Default: ``None``.
            offset (:obj:`int`, optional): Default: ``None``.
            len (:obj:`int`, optional): Default: ``None``.
            order_by (:obj:`str`, optional): Default: ``'NAME'``.
            order (:obj:`str`, optional): Default: ``'ASC'``.
            removed (:obj:`boolean`, optional): Default: ``None``.
            system (:obj:`boolean`, optional): Default: ``None``.
            filter_text (:obj:`str`, optional): Default: ``None``.
            job_status (:obj:`str`, optional): Default: ``'INACTIVE'``.
            job_label (:obj:`str`, optional): Default: ``None``.
            executor_type (:obj:`str`, optional): Default: ``'COLLECTOR'``.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self'))
        response = self._get(app='jobrunner',
                             endpoint='/v{}/metrics/problematicJobs'.format(self.api_version),
                             params=params)
        return Command(self, response)

    def get_executor_cpu_usage_time_series(self, executor_id, time_filter_condition='LAST_5M', limit=None,
                                           start_time=None, end_time=None):
        """Returns CPU usage by executor at JVM level overtime.

        Args:
            executor_id (:obj:`str`)
            time_filter_condition (:obj:`str`, optional): Default: ``'LAST_5M'``.
            limit (:obj:`str`, optional): Default: ``None``.
            start_time (:obj:`int`, optional): Default: ``None``.
            end_time (:obj:`int`, optional): Default: ``None``.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self', 'executor_id'))
        response = self._get(app='timeseries',
                             endpoint='/v{}/metrics/executor/{}/cpu'.format(self.api_version, executor_id),
                             params=params)
        return Command(self, response)

    def get_executor_memory_usage_time_series(self, executor_id, time_filter_condition='LAST_5M', limit=None,
                                              start_time=None, end_time=None):
        """Returns memory usage by executor at JVM level overtime.

        Args:
            executor_id (:obj:`str`)
            time_filter_condition (:obj:`str`, optional): Default: ``'LAST_5M'``.
            limit (:obj:`str`, optional): Default: ``None``.
            start_time (:obj:`int`, optional): Default: ``None``.
            end_time (:obj:`int`, optional): Default: ``None``.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self', 'executor_id'))
        response = self._get(app='timeseries',
                             endpoint='/v{}/metrics/executor/{}/memory'.format(self.api_version, executor_id),
                             params=params)
        return Command(self, response)

    def get_job_record_count_time_series(self, job_id, sdc_id=None, time_filter_condition='LAST_5M', limit=None,
                                         start_time=None, end_time=None):
        """Returns input, output, and error record count for the job run overtime.

        Args:
            job_id (:obj:`str`)
            sdc_id (:obj:`str`, optional): Default: ``None``.
            ime_filter_condition (:obj:`str`, optional): Default: ``'LAST_5M'``.
            limit (:obj:`str`, optional): Default: ``None``.
            start_time (:obj:`int`, optional): Default: ``None``.
            end_time (:obj:`int`, optional): Default: ``None``.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self', 'job_id'))
        response = self._get(app='timeseries',
                             endpoint='/v{}/metrics/job/{}/recordCount'.format(self.api_version, job_id),
                             params=params)
        return Command(self, response)

    def get_job_record_throughput_time_series(self, job_id, sdc_id=None, time_filter_condition='LAST_5M', limit=None,
                                              start_time=None, end_time=None):
        """Returns input, output, and error record throughput for the job run overtime.

        Args:
            job_id (:obj:`str`)
            sdc_id (:obj:`str`, optional): Default: ``None``.
            ime_filter_condition (:obj:`str`, optional): Default: ``'LAST_5M'``.
            limit (:obj:`str`, optional): Default: ``None``.
            start_time (:obj:`int`, optional): Default: ``None``.
            end_time (:obj:`int`, optional): Default: ``None``.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self', 'job_id'))
        response = self._get(app='timeseries',
                             endpoint='/v{}/metrics/job/{}/recordThroughput'.format(self.api_version, job_id),
                             params=params)
        return Command(self, response)

    def get_pipelines_created_by_users_in_a_group(self, group, organization, offset, len, order_by, order, system,
                                                  filter_text, only_published, execution_modes, start_time, end_time):
        """Returns all Pipelines created by users in a group between a start and end time.

        Args:
            group (:obj:`str`)
            organization (:obj:`str`)
            offset (:obj:`str`)
            len (:obj:`str`)
            order_by (:obj:`str`)
            order (:obj:`str`)
            system (:obj:`str`)
            filter_text (:obj:`str`)
            only_published (:obj:`bool`)
            execution_modes (:obj:`str`)
            start_time (:obj:`int`)
            end_time (:obj:`int`)
        """
        params = get_params(parameters=locals(), exclusions=('self'))
        response = self._get(app='pipelinestore',
                             endpoint='/v{}/metrics/pipelines'.format(self.api_version),
                             params=params)
        return Command(self, response)

    def get_users_not_belonging_to_group(self, org_id, offset, len, sort_field, sort_order, group):
        """Get all users that don't belong to group specified.

        Args:
            org_id (:obj:`str`)
            offset (:obj:`int`)
            len (:obj:`int`)
            sort_field (:obj:`str`)
            sort_order (:obj:`str`)
            group (:obj:`str`)

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self', 'org_id'))
        response = self._get(app='security',
                             endpoint='/v{}/metrics/{}/usersNotInGroup'.format(self.api_version, org_id),
                             params=params)
        return Command(self, response)

    def get_logged_in_users(self, org_id, offset, len, sort_field, sort_order, group, start_time, end_time):
        """Get all users with login activity between start time and end time.

        Args:
            org_id (:obj:`str`)
            offset (:obj:`int`)
            len (:obj:`int`)
            sort_field (:obj:`str`)
            sort_order (:obj:`str`)
            group (:obj:`str`)
            start_time (:obj:`int`)
            end_time (:obj:`int`)

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self', 'org_id'))
        response = self._get(app='security',
                             endpoint='/v{}/metrics/{}/loggedInUsers'.format(self.api_version, org_id),
                             params=params)
        return Command(self, response)

    def get_user_with_no_login_activity(self, org_id, offset, len, sort_field, sort_order, group, start_time, end_time):
        """Get all users with no login activity between start time and end time.

        Args:
            org_id (:obj:`str`)
            offset (:obj:`int`)
            len (:obj:`int`)
            sort_field (:obj:`str`)
            sort_order (:obj:`str`)
            group (:obj:`str`)
            start_time (:obj:`int`)
            end_time (:obj:`int`)

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self', 'org_id'))
        response = self._get(app='security',
                             endpoint='/v{}/metrics/{}/notLoggedInUsers'.format(self.api_version, org_id),
                             params=params)
        return Command(self, response)

    def get_users_created_during_time_frame(self, org_id, group, offset, len, sort_field, sort_order, start_time,
                                            end_time):
        """Get all users created between start time and end time.

        Args:
            org_id (:obj:`str`)
            group (:obj:`str`)
            offset (:obj:`int`)
            len (:obj:`int`)
            sort_field (:obj:`str`)
            sort_order (:obj:`str`)
            start_time (:obj:`int`)
            end_time (:obj:`int`)

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self', 'org_id'))
        response = self._get(app='security',
                             endpoint='/v{}/metrics/{}/usersCreated'.format(self.api_version, org_id),
                             params=params)
        return Command(self, response)

    def get_all_alerts(self, offset=None, len=None, order_by='TRIGGERED_ON', order='ASC',
                       alert_status='ACTIVE', filter_text=None, with_wrapper=False):
        """Get all alerts.

        Args:
            offset (:obj:`str`, optional): Default: ``None``
            len (:obj:`int`, optional): Default: ``None``
            order_by (:obj:`str`, optional): Default: ``'TRIGGERED_ON'``
            order (:obj:`str`, optional): Default: ``'ASC'``
            alert_status (:obj:`str`, optional): Default: ``'ACTIVE'``
            filter_text (:obj:`str`, optional): Default: ``None``
            with_wrapper (:obj:`bool`, optional): Default: ``False``

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self'))
        endpoint = '/v{}/alerts'.format(self.api_version)
        response = self._get(app='notification',
                             endpoint=endpoint,
                             params=params)
        return Command(self, response)

    def acknowledge_alert(self, body):
        """Acknowledge an active Alert.

        Args:
            body (:obj:`list`): ID of an Active Alert in JSON format.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='notification', endpoint='/v{}/alerts/ackAlerts'.format(self.api_version),
                              data=body)
        return Command(self, response)

    def delete_alert(self, body):
        """Delete an acknowledged Alert.

        Args:
            body (:obj:`list`): ID of an Acknowledged Alert in JSON format.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='notification', endpoint='/v{}/alerts/deleteAlerts'.format(self.api_version),
                              data=body)
        return Command(self, response)

    def get_resource_alerts(self, resource_id, offset=None, len=None, order_by='TRIGGERED_ON', order='ASC',
                            alert_status='ACTIVE'):
        """Get all alerts for a given Resource ID.

        Args:
            resource_id (:obj:`list`): ID of the Resource.
            offset (:obj:`str`, optional): Default: ``None``
            len (:obj:`int`, optional): Default: ``None``
            order_by (:obj:`str`, optional): Default: ``'TRIGGERED_ON'``
            order (:obj:`str`, optional): Default: ``'ASC'``
            alert_status (:obj:`str`, optional): Default: ``'ACTIVE'``

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self', 'resource_id'))
        endpoint = '/v{}/alerts/resource/{}'.format(self.api_version, resource_id)
        response = self._get(app='notification',
                             endpoint=endpoint,
                             params=params)
        return Command(self, response)

    def get_all_user_actions_for_user(self, user_id, org_id, offset=None, len=None, sort_field='TIME', sort_order=None,
                                      with_wrapper=False):
        """Get user actions done for given user ID.

        Args:
            user_id (:obj:`str`)
            org_id (:obj:`str`)
            offset (:obj:`str`, optional): Default: ``None``
            len (:obj:`int`, optional): Default: ``None``
            sort_field (:obj:`str`, optional): Default: ``'TIME'``
            sort_order (:obj:`str`, optional): Default: ``None``
            with_wrapper (:obj:`bool`, optional): Default: ``False``

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self', 'user_id', 'org_id'))
        endpoint = '/v{}/organization/{}/user/{}/listActions'.format(self.api_version, org_id, user_id)
        response = self._get(app='security',
                             endpoint=endpoint,
                             params=params)
        return Command(self, response)

    def get_all_user_actions_for_org(self, org_id, offset=None, len=None, sort_field='TIME', sort_order=None,
                                     with_wrapper=False):
        """Get user actions done for given user ID.

        Args:
            org_id (:obj:`str`)
            offset (:obj:`str`, optional): Default: ``None``
            len (:obj:`int`, optional): Default: ``None``
            sort_field (:obj:`str`, optional): Default: ``'TIME'``
            sort_order (:obj:`str`, optional): Default: ``None``
            with_wrapper (:obj:`bool`, optional): Default: ``False``

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self', 'org_id'))
        endpoint = '/v{}/organization/{}/users/listActions'.format(self.api_version, org_id)
        response = self._get(app='security',
                             endpoint=endpoint,
                             params=params)
        return Command(self, response)

    def get_all_user_actions_requested_by_user(self, user_id, org_id, offset=None, len=None, sort_field='TIME',
                                               sort_order=None, with_wrapper=False):
        """Get user actions requested by given user ID.

        Args:
            user_id (:obj:`str`)
            org_id (:obj:`str`)
            offset (:obj:`str`, optional): Default: ``None``
            len (:obj:`int`, optional): Default: ``None``
            sort_field (:obj:`str`, optional): Default: ``'TIME'``
            sort_order (:obj:`str`, optional): Default: ``None``
            with_wrapper (:obj:`bool`, optional): Default: ``False``

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self', 'user_id', 'org_id'))
        endpoint = '/v{}/organization/{}/user/{}/listActionsRequested'.format(self.api_version, org_id, user_id)
        response = self._get(app='security',
                             endpoint=endpoint,
                             params=params)
        return Command(self, response)

    def get_all_login_audits_for_user(self, user_id, org_id, offset=None, len=None, sort_field=None, sort_order=None,
                                      with_wrapper=False):
        """List audit logs for user logins for given User ID and Organization ID.

        Args:
            user_id (:obj:`str`)
            org_id (:obj:`str`)
            offset (:obj:`str`, optional): Default: ``None``
            len (:obj:`int`, optional): Default: ``None``
            sort_field (:obj:`str`, optional): Default: ``'None'``
            sort_order (:obj:`str`, optional): Default: ``None``
            with_wrapper (:obj:`bool`, optional): Default: ``False``

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self', 'user_id', 'org_id'))
        endpoint = '/v{}/organization/{}/user/{}/listLogins'.format(self.api_version, org_id, user_id)
        response = self._get(app='security',
                             endpoint=endpoint,
                             params=params)
        return Command(self, response)

    def get_all_login_audits_for_org(self, org_id, offset=None, len=None, sort_field=None, sort_order=None,
                                     with_wrapper=False):
        """List audit logs for all user logins in the organization for given Organization ID.

        Args:
            org_id (:obj:`str`)
            offset (:obj:`str`, optional): Default: ``None``
            len (:obj:`int`, optional): Default: ``None``
            sort_field (:obj:`str`, optional): Default: ``None``
            sort_order (:obj:`str`, optional): Default: ``None``
            with_wrapper (:obj:`bool`, optional): Default: ``False``

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self', 'org_id'))
        endpoint = '/v{}/organization/{}/users/listLogins'.format(self.api_version, org_id)
        response = self._get(app='security',
                             endpoint=endpoint,
                             params=params)
        return Command(self, response)

    def get_all_active_user_sessions_for_org(self, org_id, offset=None, len=None, sort_field='EXPIRY_TIME',
                                             sort_order='DESC', with_wrapper=False):
        """Get all active user sessions for given Organization ID.

        Args:
            org_id (:obj:`str`)
            offset (:obj:`str`, optional): Default: ``None``
            len (:obj:`int`, optional): Default: ``None``
            sort_field (:obj:`str`, optional): Default: ``'EXPIRY_TIME'``
            sort_order (:obj:`str`, optional): Default: ``'DESC'``
            with_wrapper (:obj:`bool`, optional): Default: ``False``

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self', 'org_id'))
        endpoint = '/v{}/sessions/{}/active'.format(self.api_version, org_id)
        response = self._get(app='security',
                             endpoint=endpoint,
                             params=params)
        return Command(self, response)

    def get_all_active_user_sessions_for_all_orgs(self, offset=None, len=None, sort_field='EXPIRY_TIME',
                                                  sort_order='DESC', with_wrapper=False):
        """Get all active user sessions for all organizations.

        Args:
            offset (:obj:`str`, optional): Default: ``None``
            len (:obj:`int`, optional): Default: ``None``
            sort_field (:obj:`str`, optional): Default: ``'EXPIRY_TIME'``
            sort_order (:obj:`str`, optional): Default: ``'DESC'``
            with_wrapper (:obj:`bool`, optional): Default: ``False``

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self'))
        endpoint = '/v{}/sessions/active'.format(self.api_version)
        response = self._get(app='security',
                             endpoint=endpoint,
                             params=params)
        return Command(self, response)

    def add_data_sla(self, sla_json):
        """Add Data SLA.

        Args:
            sla_json (:obj:`dict`)

        Returns:
          An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._put(app='sla',
                              endpoint='/v{}/dataSlas'.format(self.api_version),
                              data=sla_json)
        return Command(self, response)

    def get_data_sla(self, organization, topology_commit_id):
        """Get Data SLAs for given topology.

        Args:
            organization (:obj:`str`): Organization ID.
            topology_commit_id (:obj:`str`): Topology commit ID.

        Returns:
          An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self'))
        endpoint = '/v{}/dataSlas'.format(self.api_version)
        response = self._get(app='sla',
                             endpoint=endpoint,
                             params=params)
        return Command(self, response)

    def create_environment(self, body, complete=False, process_if_enabled=False):
        """Create a new environment.

        Args:
           body (:obj:`str`): environment in JSON format. Complies to Swagger CreateCspEnvironmentJson definition.
           complete (:obj:`bool`, optional): Default: ``False``
           process_if_enabled (:obj:`bool`, optional): Default: ``False``

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self'))
        response = self._put(app='provisioning',
                             endpoint='/v{}/csp/environments'.format(self.api_version),
                             data=body,
                             params=params)
        return Command(self, response)

    def delete_environment(self, environment_id):
        """Delete an existing environment.

        Args:
            environment_id (:obj:`str`): Id of the environment.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._delete(app='provisioning',
                                endpoint='/v{}/csp/environment/{}'.format(self.api_version, environment_id))
        return Command(self, response)

    def delete_environments(self, environment_ids):
        """Delete existing environments.

        Args:
            environment_ids (:obj:`list`): Environment IDs.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='provisioning',
                              endpoint='/v{}/csp/environments/deleteEnvironments'.format(self.api_version),
                              data=environment_ids)
        return Command(self, response)

    def update_environment(self, environment_id, body, complete='undefined', process_if_enabled='undefined'):
        """Update an existing environment.

        Args:
            environment_id (:obj:`str`): Id of the environment.
            body (:obj:`str`): environment in JSON format. Complies to Swagger CspEnvironmentJson definition.
            complete (:obj:`str`, optional): Default: ``undefined``
            process_if_enabled (:obj:`str`, optional): Default: ``undefined``

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self'))
        response = self._post(app='provisioning',
                              endpoint='/v{}/csp/environment/{}'.format(self.api_version, environment_id),
                              data=body,
                              params=params)
        return Command(self, response)

    def get_api_user_credentials_for_org(self, org_id, user_id=None):
        """List API User Credentials for the organization.

        Args:
            org_id (:obj:`str`): Organization id.
            user_id (:obj:`str`): User id. Default: ``None``

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self', 'org_id'))
        endpoint = '/v{}/organization/{}/api-user-credentials-for-org'.format(self.api_version, org_id)
        response = self._get(app='security', endpoint=endpoint, params=params)
        return Command(self, response)

    def get_api_user_credentials(self, org_id):
        """List API User Credentials for the current user.

        Args:
            org_id (:obj:`str`): Organization id.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self', 'org_id'))
        endpoint = '/v{}/organization/{}/api-user-credentials'.format(self.api_version, org_id)
        response = self._get(app='security', endpoint=endpoint, params=params)
        return Command(self, response)

    def delete_api_user_credential(self, org_id, credential_id):
        """Delete an API User Credentials.

        Args:
            org_id (:obj:`str`): Organization id.
            credential_id (:obj:`str`): Credential id.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        endpoint = '/v{}/organization/{}/api-user-credentials/{}'.format(self.api_version, org_id, credential_id)
        response = self._delete(app='security', endpoint=endpoint)
        return Command(self, response)

    def create_api_user_credential(self, org_id, api_user_credential_json):
        """Create an API User Credential.

        Args:
            org_id (:obj:`str`): Organization id.
            api_user_credential_json (:obj:`str`): Credential in JSON format.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        endpoint = '/v{}/organization/{}/api-user-credentials'.format(self.api_version, org_id)
        response = self._post(app='security', endpoint=endpoint, data=api_user_credential_json)
        return Command(self, response)

    def update_api_user_credential(self, org_id, credential_id, api_user_credential_json):
        """Update an API User Credential.

        Args:
            org_id (:obj:`str`): Organization id.
            credential_id (:obj:`str`): Credential id.
            api_user_credential_json (:obj:`str`): Credential in JSON format.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        endpoint = '/v{}/organization/{}/api-user-credentials/{}'.format(self.api_version, org_id, credential_id)
        response = self._post(app='security', endpoint=endpoint, data=api_user_credential_json)
        return Command(self, response)

    def get_environment(self, environment_id):
        """Get the environment for the given environment ID.

        Args:
            environment_id (:obj:`str`): environment ID

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        endpoint = '/v{}/csp/environment/{}'.format(self.api_version, environment_id)
        response = self._get(app='provisioning',
                             endpoint=endpoint)
        return Command(self, response)

    def get_all_environments(self, organization, type=None, state_display_label=None, status=None, offset=None,
                             len=None, order_by='NAME', order='ASC', with_total_count=False, tag=None):
        """Get environments a user has access to.

        Args:
            org_id (:obj:`str`)
            type (:obj:`str`, optional): Default: ``None``
            state_display_labelf (:obj:`str`, optional): Default: ``None``
            status (:obj:`str`, optional): Default: ``'OK'``
            offset (:obj:`str`, optional): Default: ``None``
            len (:obj:`int`, optional): Default: ``None``
            order_by (:obj:`str`, optional): Default: ``'NAME'``
            order (:obj:`str`, optional): Default: ``'DESC'``
            with_total_count (:obj:`bool`, optional): Default: ``True``
            tag (:obj:`str`, optional): Default: ``None``

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self'))
        endpoint = '/v{}/csp/environments'.format(self.api_version)
        response = self._get(app='provisioning',
                             endpoint=endpoint,
                             params=params)
        return Command(self, response)

    def get_all_environment_tags(self, organization, parent_id=None, offset=None, len=None, order=None):
        """Get environment tags for a given organization.

        Args:
            organization (:obj:`str`)
            parent_id (:obj:`str`, optional): Default: ``None``
            offset (:obj:`int`, optional): Default: ``None``
            len (obj:`int`, optional): Default: ``None``
            order (:obj:`str`, optional): Default: ``None``

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self'))
        response = self._get(app='provisioning',
                             endpoint='/v{}/csp/environments/tags'.format(self.api_version),
                             params=params)
        return Command(self, response)

    def get_environment_acl(self, environment_id):
        """Get environment ACL.

        Args:
            environment_id (:obj:`str`).

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._get(app='provisioning',
                             endpoint='/v{}/csp/environment/{}/acl'.format(self.api_version, environment_id))
        return Command(self, response)

    def set_environment_acl(self, environment_id, environment_acl_json):
        """Update environment ACL.

        Args:
            environment_id (:obj:`str`).
            environment_acl_json (:obj:`str`): environment ACL in JSON format.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='provisioning', endpoint='/v{}/csp/environment/{}/acl'.format(self.api_version,
                                                                                                environment_id),
                              data=environment_acl_json)
        return Command(self, response)

    def get_environment_permissions(self, deployment_id, subject_id):
        """Get permissions on a given deployment for a given subject.

        Args:
            deployment_id (:obj:`str`): Deployment ID
            subject_id (:obj:`str`): Subject ID

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        endpoint = '/v{}/csp/environment/{}/permissions/{}'.format(self.api_version, deployment_id, subject_id)
        response = self._get(app='provisioning', endpoint=endpoint)
        return Command(self, response)

    def update_environment_permissions(self, body, deployment_id, subject_id):
        """Update permissions on a given deployment for a given subject.

        Args:
            body (:obj:`str`): deployment ACL in JSON format. Complies to Swagger CspEngineEventJson definition.
            deployment_id (:obj:`str`): Id of the deployment.
            subject_id (:obj:`str`): Subject ID

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        endpoint = '/v{}/csp/environment/{}/permissions/{}'.format(self.api_version, deployment_id, subject_id)
        response = self._post(app='provisioning', endpoint=endpoint, data=body)
        return Command(self, response)

    def get_aws_external_id(self, organization):
        """Get the external id to use for Cross Account Roles for the user's Org.

        Args:
            organization (:obj:`str`).

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self'))
        endpoint = '/v{}/csp/aws/externalId'.format(self.api_version)
        response = self._get(app='provisioning',
                             endpoint=endpoint,
                             params=params)
        return Command(self, response)

    def get_azure_network_security_groups(self, environment_id, region):
        """Returns the available network security groups for the given environment and region

        Args:
            environment_id (:obj:`str`): Environment id
            region (:obj:`str`): region

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        endpoint = '/v{}/csp/azure/{}/networkSecurityGroups/{}'.format(self.api_version, environment_id, region)
        response = self._get(app='provisioning', endpoint=endpoint)
        return Command(self, response)

    def get_azure_subnets(self, environment_id, network_id):
        """Returns the available subnets for the given environment and network

        Args:
            environment_id (:obj:`str`): Environment id
            network_id (:obj:`str`): network id

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self', 'environment_id'))
        endpoint = '/v{}/csp/azure/{}/subnets'.format(self.api_version, environment_id)
        response = self._get(app='provisioning', endpoint=endpoint, params=params)
        return Command(self, response)

    def get_azure_networks(self, environment_id, region):
        """Returns the available networks for the given environment

        Args:
            environment_id (:obj:`str`): Environment id
            region (:obj:`str`): region

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        endpoint = '/v{}/csp/azure/{}/networks/{}'.format(self.api_version, environment_id, region)
        response = self._get(app='provisioning', endpoint=endpoint)
        return Command(self, response)

    def get_azure_managed_entities(self, environment_id, region):
        """Returns the available managed identities for the given environment

        Args:
            environment_id (:obj:`str`): Environment id
            region (:obj:`str`): region

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        endpoint = '/v{}/csp/azure/{}/identities/{}'.format(self.api_version, environment_id, region)
        response = self._get(app='provisioning', endpoint=endpoint)
        return Command(self, response)

    def get_azure_vm_sizes(self, environment_id, region, zones=None):
        """Returns the available VM sizes for the given environment, Azure region

        Args:
            environment_id (:obj:`str`): Environment id
            region (:obj:`str`): region
            zones (:obj:`list`, optional): List of zones. Default: ``None``

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self', 'environment_id', 'region'))
        endpoint = '/v{}/csp/azure/{}/regions/{}/vmSizes'.format(self.api_version, environment_id, region)
        response = self._get(app='provisioning', endpoint=endpoint, params=params)
        return Command(self, response)

    def get_azure_resource_groups(self, environment_id, region):
        """Returns the available resource groups for the given environment and region

        Args:
            environment_id (:obj:`str`): Environment id
            region (:obj:`str`): region

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        endpoint = '/v{}/csp/azure/{}/resourceGroups/{}'.format(self.api_version, environment_id, region)
        response = self._get(app='provisioning', endpoint=endpoint)
        return Command(self, response)

    def get_azure_sshkeypairs(self, environment_id):
        """Returns the available Azure SSH key pairs for the given environment

        Args:
            environment_id (:obj:`str`): Environment id

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        endpoint = '/v{}/csp/azure/{}/sshkeypairs'.format(self.api_version, environment_id)
        response = self._get(app='provisioning', endpoint=endpoint)
        return Command(self, response)

    def get_azure_regions(self):
        """Returns the available regions for Azure

        Args:
            environment_id (:obj:`str`): Environment id

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        endpoint = '/v{}/csp/azure/regions'.format(self.api_version)
        response = self._get(app='provisioning', endpoint=endpoint)
        return Command(self, response)

    def get_azure_zones(self, environment_id, region):
        """Returns the available zones for for the given environment, Azure region

        Args:
            environment_id (:obj:`str`): Environment id
            region (:obj:`str`): Region

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        endpoint = '/v{}/csp/azure/{}/regions/{}/zones'.format(self.api_version, environment_id, region)
        response = self._get(app='provisioning', endpoint=endpoint)
        return Command(self, response)

    def activate_data_sla(self, sla_ids):
        """Activate SLAs.

        Args:
            sla_ids (:obj:`list`): List of string IDs of SLAs

        Returns:
          An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='sla',
                              endpoint='/v{}/dataSlas/activateSlas'.format(self.api_version),
                              data=sla_ids)
        return Command(self, response)

    def deactivate_data_sla(self, sla_ids):
        """Deactivate SLAs.

        Args:
            sla_ids (:obj:`list`): List of string IDs of SLAs

        Returns:
          An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='sla',
                              endpoint='/v{}/dataSlas/deactivateSlas'.format(self.api_version),
                              data=sla_ids)
        return Command(self, response)

    def delete_data_sla(self, sla_ids):
        """Delete SLAs.

        Args:
            sla_ids (:obj:`list`): List of string IDs of SLAs

        Returns:
          An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='sla',
                              endpoint='/v{}/dataSlas/deleteSlas'.format(self.api_version),
                              data=sla_ids)
        return Command(self, response)

    def get_component_version_range(self, id):
        """Get the min/max component versions that can work with Control Hub.

        Args:
            id (:obj:`str`): Type of component you wish to retrieve the version range for.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self'))
        endpoint = '/v{}/componentVersionRange'.format(self.api_version)
        response = self._get(app='security', endpoint=endpoint, params=params)
        return Command(self, response)

    def get_aws_environment_regions(self, environment_id):
        """Returns the available regions for the given Environment.

        Args:
            environment_id (:obj:`str`): environment ID

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        endpoint = '/v{}/csp/aws/{}/regions'.format(self.api_version, environment_id)
        response = self._get(app='provisioning',
                             endpoint=endpoint)
        return Command(self, response)

    def get_aws_environment_ec2_instance_types(self, environment_id, region_id):
        """Returns the available EC2 instance types for the given Environment and AWS Region.

        Args:
            environment_id (:obj:`str`): environment ID
            region_id (:obj:`str`): Region ID

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        endpoint = '/v{}/csp/aws/{}/regions/{}/ec2/instancetypes'.format(self.api_version,
                                                                         environment_id, region_id)
        response = self._get(app='provisioning',
                             endpoint=endpoint)
        return Command(self, response)

    def get_aws_environment_ec2_ssh_key_pairs(self, environment_id, region_id):
        """Returns the available EC2 SSH Key Pairs for the given Environment and AWS Region.

        Args:
            environment_id (:obj:`str`): environment ID
            region_id (:obj:`str`): Region ID

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        endpoint = '/v{}/csp/aws/{}/regions/{}/ec2/sshkeypairs'.format(self.api_version,
                                                                       environment_id, region_id)
        response = self._get(app='provisioning',
                             endpoint=endpoint)
        return Command(self, response)

    def get_aws_environment_vpcs(self, environment_id, region_id):
        """Returns the available VPCs for the given Environment and AWS Region.

        Args:
            environment_id (:obj:`str`): environment ID
            region_id (:obj:`str`): Region ID

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        endpoint = '/v{}/csp/aws/{}/regions/{}/vpcs'.format(self.api_version,
                                                            environment_id, region_id)
        response = self._get(app='provisioning',
                             endpoint=endpoint)
        return Command(self, response)

    def get_aws_environment_security_groups(self, environment_id, region_id, vpc_id):
        """Returns the available Security Groups for the given Environment, AWS Region, and VPC.

        Args:
            environment_id (:obj:`str`): environment ID
            region_id (:obj:`str`): Region ID
            vpc_id (:obj:`str`): VPC ID

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        endpoint = '/v{}/csp/aws/{}/regions/{}/vpcs/{}/securitygroups'.format(self.api_version, environment_id,
                                                                              region_id, vpc_id)
        response = self._get(app='provisioning',
                             endpoint=endpoint)
        return Command(self, response)

    def get_aws_environment_subnets(self, environment_id, region_id, vpc_id):
        """Returns the available Subnets for the given Environment, AWS Region, and VPC.

        Args:
            environment_id (:obj:`str`): environment ID
            region_id (:obj:`str`): Region ID
            vpc_id (:obj:`str`): VPC ID

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        endpoint = '/v{}/csp/aws/{}/regions/{}/vpcs/{}/subnets'.format(self.api_version, environment_id,
                                                                       region_id, vpc_id)
        response = self._get(app='provisioning',
                             endpoint=endpoint)
        return Command(self, response)

    def get_gcp_environment_projects(self, environment_id):
        """Returns the available projects for the given Environment.

        Args:
            environment_id (:obj:`str`): environment ID

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        endpoint = '/v{}/csp/gcp/{}/projects'.format(self.api_version, environment_id)
        response = self._get(app='provisioning', endpoint=endpoint)
        return Command(self, response)

    def get_gcp_environment_networks(self, environment_id, project_id):
        """Returns the available Networks for the given Environment and GCP Project.

        Args:
            environment_id (:obj:`str`): environment ID
            project_id (:obj:`str`): project ID

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        endpoint = '/v{}/csp/gcp/{}/projects/{}/networks'.format(self.api_version, environment_id, project_id)
        response = self._get(app='provisioning', endpoint=endpoint)
        return Command(self, response)

    def get_gcp_environment_regions(self, environment_id, project_id):
        """Returns the available regions for the given Environment and GCP Project.

        Args:
            environment_id (:obj:`str`): environment ID
            project_id (:obj:`str`): project ID

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        endpoint = '/v{}/csp/gcp/{}/projects/{}/regions'.format(self.api_version, environment_id, project_id)
        response = self._get(app='provisioning', endpoint=endpoint)
        return Command(self, response)

    def get_gcp_environment_service_accounts(self, environment_id, project_id):
        """Returns the available service accounts for the given Environment and GCP Project.

        Args:
            environment_id (:obj:`str`): environment ID
            project_id (:obj:`str`): project ID

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        endpoint = '/v{}/csp/gcp/{}/projects/{}/serviceAccounts'.format(self.api_version, environment_id, project_id)
        response = self._get(app='provisioning', endpoint=endpoint)
        return Command(self, response)

    def get_gcp_environment_zones(self, environment_id, project_id, region_id):
        """Returns the available zones for the given environment and GCP project and GCP region.

        Args:
            environment_id (:obj:`str`): environment ID
            project_id (:obj:`str`): project ID
            region (:obj:`str`): region

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        endpoint = '/v{}/csp/gcp/{}/projects/{}/zones/{}'.format(self.api_version, environment_id,
                                                                 project_id, region_id)
        response = self._get(app='provisioning', endpoint=endpoint)
        return Command(self, response)

    def get_gcp_environment_machine_types(self, environment_id, project_id, zone_id):
        """Returns the available machine types for the given Environment and GCP Project and GCP Zone.

        Args:
            environment_id (:obj:`str`): environment ID
            project_id (:obj:`str`): project ID
            zone_id (:obj:`str`): project ID

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        endpoint = '/v{}/csp/gcp/{}/projects/{}/zones/{}/machineTypes'.format(self.api_version, environment_id,
                                                                              project_id, zone_id)
        response = self._get(app='provisioning', endpoint=endpoint)
        return Command(self, response)

    def get_gcp_external_id(self, organization):
        """Get the external id to use for Service Accounts for the user's Org.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self'))

        endpoint = '/v{}/csp/gcp/externalId'.format(self.api_version)
        response = self._get(app='provisioning',
                             endpoint=endpoint,
                             params=params)
        return Command(self, response)

    def enable_environment(self, environment_id):
        """Enable the Environment for the given Environment ID.

        Args:
            environment_id (:obj:`str`): Id of the environment.
            body (:obj:`str`): environment in JSON format. Complies to Swagger CspEnvironmentJson definition.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='provisioning',
                              endpoint='/v{}/csp/environment/{}/enable'.format(self.api_version, environment_id))
        return Command(self, response)

    def enable_environments(self, environment_ids):
        """Enable the environments.

        Args:
            environment_ids (:obj:`str`): environment IDs.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='provisioning',
                              endpoint='/v{}/csp/environments/enableEnvironments'.format(self.api_version),
                              data=environment_ids)
        return Command(self, response)

    def disable_environment(self, environment_id):
        """Disable the Environment for the given Environment ID.

        Args:
            environment_id (:obj:`str`): Id of the environment.
            body (:obj:`str`): environment in JSON format. Complies to Swagger CspEnvironmentJson definition.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='provisioning',
                              endpoint='/v{}/csp/environment/{}/disable'.format(self.api_version, environment_id))
        return Command(self, response)

    def disable_environments(self, environment_ids):
        """Disable the environments.

        Args:
            environment_ids (:obj:`list`): environment IDs.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='provisioning',
                              endpoint='/v{}/csp/environments/disableEnvironments'.format(self.api_version),
                              data=environment_ids)
        return Command(self, response)

    def wait_for_environment_state_display_label(self, environment_id, state_display_label, timeout_sec=300):
        """Block until an environment reaches the desired status.

        Args:
            environment_id (:obj:`str`): The environment id.
            state_display_label (:obj:`str`): The desired state_display_label to wait for.
            timeout_sec (:obj:`int`, optional): Timeout to wait for ``environment`` to reach ``status``, in seconds.
                Default: ``300``.

        Raises:
            TimeoutError: If ``timeout_sec`` passes without ``environment`` reaching ``state_display_label``.
        """
        def condition():
            response_json = self.get_environment(environment_id).response.json()
            current_state_display_label = response_json['stateDisplayLabel']
            logger.debug('Environment has current current_state_display_label %s  ...', current_state_display_label)
            return current_state_display_label == state_display_label

        def failure(timeout_sec):
            raise Exception('Timed out after {} seconds while waiting for state_display_label.'.format(timeout_sec))

        def success(time):
            logger.debug('Environment reached desired state_display_label after %s s.', time)

        logger.debug('Environment with id %s waiting for state_display_label %s ...', environment_id,
                     state_display_label)
        wait_for_condition(condition=condition, timeout=timeout_sec, failure=failure, success=success)

    def get_deployment_engine_acl_audits(self, organization, offset=None, len=None,
                                         sort_field='NAME', sort_order='ASC'):
        """Get all user actions for given Organization ID.

        Args:
            organization (:obj:`str`)
            offset (:obj:`str`, optional): Default: ``None``
            len (:obj:`int`, optional): Default: ``None``
            sort_field (:obj:`str`, optional): Default: ``'NAME'``
            sort_order (:obj:`str`, optional): Default: ``'ASC'``

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self'))
        endpoint = '/v{}/csp/deployment/engine/listAclAudits'.format(self.api_version)
        response = self._get(app='provisioning', endpoint=endpoint, params=params)
        return Command(self, response)

    def get_deployment_post_stop_script(self, deployment_id):
        """Get Post Stop Script for the Engine for the given deployment ID.

        Args:
            deployment_id (:obj:`str`): Deployment ID

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        endpoint = '/v{}/csp/deployment/engine/{}/postStopScript'.format(self.api_version, deployment_id)
        response = self._get(app='provisioning', endpoint=endpoint)
        return Command(self, response)

    def get_deployment_pre_start_script(self, deployment_id):
        """Get Post Stop Script for the Engine for the given deployment ID.

        Args:
            deployment_id (:obj:`str`): Deployment ID

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        endpoint = '/v{}/csp/deployment/engine/{}/preStartScript'.format(self.api_version, deployment_id)
        response = self._get(app='provisioning', endpoint=endpoint)
        return Command(self, response)

    def get_deployment_acl_audits(self, organization, offset=None, len=None, sort_field='NAME', sort_order='ASC'):
        """Get all user actions for given Organization ID.

        Args:
            organization (:obj:`str`)
            offset (:obj:`str`, optional): Default: ``None``
            len (:obj:`int`, optional): Default: ``None``
            sort_field (:obj:`str`, optional): Default: ``'NAME'``
            sort_order (:obj:`str`, optional): Default: ``'ASC'``

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self'))
        endpoint = '/v{}/csp/deployment/listAclAudits'.format(self.api_version)
        response = self._get(app='provisioning', endpoint=endpoint, params=params)
        return Command(self, response)

    def get_deployment_self_acl_audits(self, organization, offset=None, len=None, sort_field='NAME', sort_order='ASC'):
        """Get all user actions for given Organization ID.

        Args:
            organization (:obj:`str`)
            offset (:obj:`str`, optional): Default: ``None``
            len (:obj:`int`, optional): Default: ``None``
            sort_field (:obj:`str`, optional): Default: ``'NAME'``
            sort_order (:obj:`str`, optional): Default: ``'ASC'``

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self'))
        endpoint = '/v{}/csp/deployment/self/listAclAudits'.format(self.api_version)
        response = self._get(app='provisioning', endpoint=endpoint, params=params)
        return Command(self, response)

    def get_self_managed_deployment_download_and_start_script(self, deployment_id):
        """Get download and start script for Self Managed Deployment with Tarball installation.

        Args:
            deployment_id (:obj:`str`): Deployment ID

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.Response content-type is application/octet-stream.
        """
        endpoint = '/v{}/csp/deployment/self/{}/downloadAndStartEngine'.format(self.api_version, deployment_id)
        response = self._get(app='provisioning', endpoint=endpoint)
        return Command(self, response)

    def get_self_managed_deployment_install_command(self, deployment_id):
        """Get install Command for Self Managed Deployment.

        Args:
            deployment_id (:obj:`str`): Deployment ID

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.Response content-type is text/plain.
        """
        endpoint = '/v{}/csp/deployment/self/{}/installCommand'.format(self.api_version, deployment_id)
        response = self._get(app='provisioning', endpoint=endpoint)
        return Command(self, response)

    def get_deployment(self, deployment_id):
        """Return deployment for given deployment ID.

        Args:
            deployment_id (:obj:`str`): Deployment ID

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        endpoint = '/v{}/csp/deployment/{}'.format(self.api_version, deployment_id)
        response = self._get(app='provisioning', endpoint=endpoint)
        return Command(self, response)

    def delete_deployment(self, deployment_id):
        """Delete an existing deployment.

        Args:
            deployment_id (:obj:`str`): Id of the deployment.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._delete(app='provisioning',
                                endpoint='/v{}/csp/deployment/{}'.format(self.api_version, deployment_id))
        return Command(self, response)

    def can_delete_deployment(self, deployment_id):
        """Check if the user can delete a given deployment ID.

        Args:
            deployment_id (:obj:`str`): Id of the deployment.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._get(app='provisioning',
                             endpoint='/v{}/csp/deployment/{}/canDelete'.format(self.api_version, deployment_id))
        return Command(self, response)

    def delete_deployments(self, deployment_ids):
        """Delete existing deployments.

        Args:
            deployment_ids (:obj:`str`): Ids of the deployments.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='provisioning',
                              endpoint='/v{}/csp/deployments/deleteDeployments'.format(self.api_version),
                              data=deployment_ids)
        return Command(self, response)

    def update_deployment(self, deployment_id, body, complete='undefined', process_if_enabled='undefined'):
        """Update an existing deployment.

        Args:
            deployment_id (:obj:`str`): Id of the deployment.
            body (:obj:`str`): deployment in JSON format. Complies to Swagger CspEnvironmentJson definition.
            complete (:obj:`str`, optional): Default: ``undefined``
            process_if_enabled (:obj:`str`, optional): Default: ``undefined``

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self'))
        response = self._post(app='provisioning',
                              endpoint='/v{}/csp/deployment/{}'.format(self.api_version, deployment_id),
                              data=body,
                              params=params)
        return Command(self, response)

    def get_deployment_acl(self, deployment_id):
        """Return ACL for a given deployment.

        Args:
            deployment_id (:obj:`str`): Deployment ID

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        endpoint = '/v{}/csp/deployment/{}/acl'.format(self.api_version, deployment_id)
        response = self._get(app='provisioning', endpoint=endpoint)
        return Command(self, response)

    def update_deployment_acl(self, deployment_id, body):
        """Update ACL for a given deployment.

        Args:
            deployment_id (:obj:`str`): Id of the deployment.
            body (:obj:`str`): deployment ACL in JSON format. Complies to Swagger AclJson definition.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='provisioning',
                              endpoint='/v{}/csp/deployment/{}/acl'.format(self.api_version, deployment_id),
                              data=body)
        return Command(self, response)

    def enable_deployments(self, deployment_ids):
        """Enable deployments for the given deployment IDs.

        Args:
            deployment_ids (:obj:`list`): Ids of the deployments.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='provisioning',
                              endpoint='/v{}/csp/deployments/enableDeployments'.format(self.api_version),
                              data=deployment_ids)
        return Command(self, response)

    def enable_deployment(self, deployment_id):
        """Enable the deployment for the given deployment ID.

        Args:
            deployment_id (:obj:`str`): Id of the deployment.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='provisioning',
                              endpoint='/v{}/csp/deployment/{}/enable'.format(self.api_version, deployment_id))
        return Command(self, response)

    def disable_deployment(self, deployment_id):
        """Disable the deployment for the given deployment ID.

        Args:
            deployment_id (:obj:`str`): Id of the deployment.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='provisioning',
                              endpoint='/v{}/csp/deployment/{}/disable'.format(self.api_version, deployment_id))
        return Command(self, response)

    def disable_deployments(self, deployment_ids):
        """Disable the deployments for the given deployment IDs.

        Args:
            deployment_ids (:obj:`list`): Ids of the deployments.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='provisioning',
                              endpoint='/v{}/csp/deployments/disableDeployments'.format(self.api_version),
                              data=deployment_ids)
        return Command(self, response)

    def wait_for_deployment_status(self, deployment_id, status, timeout_sec=600):
        """Block until a deployment reaches the desired status.

        Args:
            deployment_id (:obj:`str`): The deployment id.
            status (:obj:`str`): The desired status to wait for.
            timeout_sec (:obj:`int`, optional): Timeout to wait for ``deployment`` to reach ``status``, in seconds.
                Default: ``300``.

        Raises:
            TimeoutError: If ``timeout_sec`` passes without ``deployment`` reaching ``status``.
        """
        def condition():
            response_json = self.get_deployment(deployment_id).response.json()
            current_status = response_json['status']
            logger.debug('Deployment has current status %s and status_detail as %s ...', current_status,
                         response_json['statusDetail'])
            return current_status == status

        def failure(timeout_sec):
            raise Exception('Timed out after {} seconds while waiting for status.'.format(timeout_sec))

        def success(time):
            logger.debug('deployment reached desired status after %s s.', time)

        logger.debug('deployment %s waiting for status %s ...', deployment_id, status)
        wait_for_condition(condition=condition, timeout=timeout_sec, failure=failure, success=success)

    def wait_for_deployment_state_display_label(self, deployment_id, state_display_label, timeout_sec=600):
        """Block until a deployment reaches the desired state_display_label.

        Args:
            deployment_id (:obj:`str`): The deployment id.
            state_display_label (:obj:`str`): The desired state_display_label to wait for.
            timeout_sec (:obj:`int`, optional): Timeout to wait for ``deployment`` to reach ``status``, in seconds.
                Default: ``300``.

        Raises:
            TimeoutError: If ``timeout_sec`` passes without ``deployment`` reaching ``state_display_label``.
        """
        def condition():
            response_json = self.get_deployment(deployment_id).response.json()
            current_state_display_label = response_json['stateDisplayLabel']
            logger.debug('Deployment has current current_state_display_label %s  ...', current_state_display_label)
            return current_state_display_label == state_display_label

        def failure(timeout_sec):
            raise Exception('Timed out after {} seconds while waiting for state_display_label.'.format(timeout_sec))

        def success(time):
            logger.debug('deployment reached desired state_display_label after %s s.', time)

        logger.debug('deployment %s waiting for state_display_label %s ...', deployment_id, state_display_label)
        wait_for_condition(condition=condition, timeout=timeout_sec, failure=failure, success=success)

    def get_deployment_engine_token(self, deployment_id):
        """Fetches a Engine Token for the Deployment.

        Args:
            deployment_id (:obj:`str`): Id of the deployment.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='provisioning',
                              endpoint='/v{}/csp/deployment/{}/engineToken'.format(self.api_version, deployment_id))
        return Command(self, response)

    def get_deployment_engine_configs(self, deployment_id):
        """Get Engine Configuration for Deployment.

        Args:
            deployment_id (:obj:`str`): Deployment ID

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        endpoint = '/v{}/csp/deployment/{}/engineConfigs'.format(self.api_version, deployment_id)
        response = self._get(app='provisioning', endpoint=endpoint)
        return Command(self, response)

    def get_deployment_events(self, deployment_id, source_type='SCH', source_id=None, hostname=None,
                              offset=None, len=None):
        """Get Deployment events.

        Args:
            deployment_id (:obj:`str`): Deployment ID
            source_type (:obj:`str`, optional): Default: ``'SCH'``
            source_id (:obj:`str`, optional): Default: ``None``
            hostname (:obj:`str`, optional): Default: ``None``
            offset (:obj:`str`, optional): Default: ``None``
            len (:obj:`int`, optional): Default: ``None``

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self', 'deployment_id'))
        endpoint = '/v{}/csp/deployment/{}/events'.format(self.api_version, deployment_id)
        response = self._get(app='provisioning', endpoint=endpoint, params=params)
        return Command(self, response)

    def report_deployment_engine_event(self, deployment_id, body):
        """Report an event from an engine.

        Args:
            deployment_id (:obj:`str`): Id of the deployment.
            body (:obj:`str`): deployment ACL in JSON format. Complies to Swagger CspEngineEventJson definition.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='provisioning',
                              endpoint='/v{}/csp/deployment/{}/events'.format(self.api_version, deployment_id),
                              data=body)
        return Command(self, response)

    def get_deployment_permissions(self, deployment_id, subject_id):
        """Get permissions on a given deployment for a given subject.

        Args:
            deployment_id (:obj:`str`): Deployment ID
            subject_id (:obj:`str`): Subject ID

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        endpoint = '/v{}/csp/deployment/{}/permissions/{}'.format(self.api_version, deployment_id, subject_id)
        response = self._get(app='provisioning', endpoint=endpoint)
        return Command(self, response)

    def update_deployment_permissions(self, body, deployment_id, subject_id):
        """Update permissions on a given deployment for a given subject.

        Args:
            body (:obj:`str`): deployment ACL in JSON format. Complies to Swagger CspEngineEventJson definition.
            deployment_id (:obj:`str`): Id of the deployment.
            subject_id (:obj:`str`): Subject ID

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        endpoint = '/v{}/csp/deployment/{}/permissions/{}'.format(self.api_version, deployment_id, subject_id)
        response = self._post(app='provisioning', endpoint=endpoint, data=body)
        return Command(self, response)

    def restart_deployment_engines(self, engine_ids):
        """Request a restart for all given Deployment managed Engine IDs.

        Args:
            engine_ids (:obj:`list`): Ids of the engines.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='jobrunner',
                              endpoint='/v{}/sdcs/restartEngines'.format(self.api_version),
                              data=engine_ids)
        return Command(self, response)

    def shutdown_deployment_engines(self, engine_ids):
        """Request a shutdown for all given Deployment managed Engine IDs.

        Args:
            engine_ids (:obj:`list`): Ids of the engines.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='jobrunner',
                              endpoint='/v{}/sdcs/shutdownEngines'.format(self.api_version),
                              data=engine_ids)
        return Command(self, response)

    def restart_deployment_all_engines(self, deployment_id):
        """Restart all engines from a deployment.

        Args:
            deployment_id (:obj:`str`): Id of the deployment.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='provisioning',
                              endpoint='/v{}/csp/deployment/{}/restartEngines'.format(self.api_version, deployment_id))
        return Command(self, response)

    def get_deployment_registered_engines(self, deployment_id, offset=0, len=5,
                                          order_by='LAST_REPORTED_TIME', order='ASC', with_wrapper=True):
        """Returns all registered engines' list for a Deployment ID.

        Args:
            deployment_id (:obj:`str`): Deployment ID
            offset (:obj:`str`, optional): Default: ``None``
            len (:obj:`int`, optional): Default: ``None``
            order_by (:obj:`str`, optional): Default: ``'NAME'``
            order (:obj:`str`, optional): Default: ``'ASC'``
            with_total_count (:obj:`bool`, optional): Default: ``None``

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self', 'deployment_id'))
        endpoint = '/v{}/sdcs/cspDeployment/{}'.format(self.api_version, deployment_id)
        response = self._get(app='jobrunner', endpoint=endpoint, params=params)
        return Command(self, response)

    def get_deployment_stale_engines(self, deployment_id):
        """Get Engines with stale configuration for the Deployment.

        Args:
            deployment_id (:obj:`str`): Deployment ID

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        endpoint = '/v{}/csp/deployment/{}/staleEngines'.format(self.api_version, deployment_id)
        response = self._get(app='provisioning', endpoint=endpoint)
        return Command(self, response)

    def get_all_deployments(self, organization, type=None, state_display_label=None, status=None, environment=None,
                            tag=None, engine_type=None, offset=None, len=None,
                            order_by='NAME', order='ASC', with_total_count=False):
        """Returns deployments a user has access to.

        Args:
            organization (:obj:`str`)
            type (:obj:`str`, optional): deployment type Default: ``None``
            state_display_label (:obj:`str`, optional): Default: ``None``
            status (:obj:`str`, optional): Default: ``None``
            environment (:obj:`str`, optional): Default: ``None``
            tag (:obj:`str`, optional): Default: ``None``
            engine_type (:obj:`str`, optional): Default: ``None``
            offset (:obj:`str`, optional): Default: ``None``
            len (:obj:`int`, optional): Default: ``None``
            order_by (:obj:`str`, optional): Default: ``'NAME'``
            order (:obj:`str`, optional): Default: ``'ASC'``
            with_total_count (:obj:`bool`, optional): Default: ``False``

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self'))
        endpoint = '/v{}/csp/deployments'.format(self.api_version)
        response = self._get(app='provisioning', endpoint=endpoint, params=params)
        return Command(self, response)

    def create_deployment(self, body):
        """Create a new deployment.

        Args:
           body (:obj:`str`): deployment in JSON format. Complies to Swagger CreateCspdeploymentJson definition.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._put(app='provisioning',
                             endpoint='/v{}/csp/deployments'.format(self.api_version),
                             data=body)
        return Command(self, response)

    def get_deployment_acls(self, body):
        """Returns Acls for all given Deployment IDs.

        Args:
            body (:obj:`str`): deployment ACL in JSON format. Complies to Swagger AclJson definition.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._post(app='provisioning',
                              endpoint='/v{}/csp/deployments/acls'.format(self.api_version),
                              data=body)
        return Command(self, response)

    def get_all_deployment_audits(self, organization, offset=None, len=None, sort_field='NAME', sort_order='ASC'):
        """Get all deployment audits.

        Args:
            organization (:obj:`str`)
            offset (:obj:`str`, optional): Default: ``None``
            len (:obj:`int`, optional): Default: ``None``
            sort_field (:obj:`str`, optional): Default: ``'NAME'``
            sort_order (:obj:`str`, optional): Default: ``'ASC'``

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self'))
        response = self._get(app='provisioning',
                             endpoint='/v{}/csp/deployments/audits'.format(self.api_version),
                             params=params)
        return Command(self, response)

    def get_all_deployment_acl_audits(self, organization, offset=None, len=None, order_by='NAME', sort_order='ASC'):
        """Get all user actions for given Organization ID.

        Args:
            organization (:obj:`str`)
            offset (:obj:`str`, optional): Default: ``None``
            len (:obj:`int`, optional): Default: ``None``
            order_by (:obj:`str`, optional): Default: ``'NAME'``
            sort_order (:obj:`str`, optional): Default: ``'ASC'``

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self'))
        response = self._get(app='provisioning',
                             endpoint='/v{}/csp/deployments/listAclAudits'.format(self.api_version),
                             params=params)
        return Command(self, response)

    def get_all_deployment_tags(self, organization, parent_id=None, offset=None, len=None, order='ASC'):
        """Returns all available deployment Tags.

        Args:
            organization (:obj:`str`)
            parent_id (:obj:`str`, optional): Default: ``None``
            offset (:obj:`str`, optional): Default: ``None``
            len (:obj:`int`, optional): Default: ``None``
            order (:obj:`str`, optional): Default: ``'ASC'``

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self'))
        response = self._get(app='provisioning',
                             endpoint='/v{}/csp/deployments/tags'.format(self.api_version),
                             params=params)
        return Command(self, response)

    def get_all_engine_versions(self, offset=None, len=None, order_by='CREATE_TIME', order='ASC',
                                engine_type='DC', with_total_count=None):
        """Returns all Engine Versions.

        Args:
            offset (:obj:`str`, optional): Default: ``None``
            len (:obj:`int`, optional): Default: ``None``
            order_by (:obj:`str`, optional): Default: ``'CREATE_TIME'``
            order (:obj:`str`, optional): Default: ``'ASC'``
            engine_type (:obj:`str`, optional): Default: ``'DC'``
            with_total_count (:obj:`str`, optional): Default: ``None``

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self'))
        response = self._get(app='provisioning',
                             endpoint='/v{}/csp/engineVersions'.format(self.api_version),
                             params=params)
        return Command(self, response)

    def get_engine_version(self, engine_version_id):
        """Returns Engine Version for given Engine Version Id.

        Args:
            engine_version_id (:obj:`str`): engine version ID.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        endpoint = '/v{}/csp/engineVersion/{}'.format(self.api_version, engine_version_id)
        response = self._get(app='provisioning', endpoint=endpoint)
        return Command(self, response)

    def get_provisioning_api(self):
        response = self._get(app='provisioning',
                             endpoint='swagger.json')
        return response.json()

    def get_connection_api(self):
        response = self._get(app='connection',
                             endpoint='swagger.json')
        return response.json()

    def get_security_api(self):
        response = self._get(app='security',
                             endpoint='swagger.json')
        return response.json()

    def get_pipelinestore_api(self):
        response = self._get(app='pipelinestore',
                             endpoint='swagger.json')
        return response.json()

    def get_job_api(self):
        response = self._get(app='jobrunner',
                             endpoint='swagger.json')
        return response.json()

    def get_topology_api(self):
        response = self._get(app='topology',
                             endpoint='swagger.json')
        return response.json()

    def get_scheduler_api(self):
        response = self._get(app='scheduler',
                             endpoint='swagger.json')
        return response.json()

    def get_notification_api(self):
        response = self._get(app='notification',
                             endpoint='swagger.json')
        return response.json()

    def get_translations_json(self):
        response = self._get(app='assets',
                             rest='i18n',
                             endpoint='en.json')
        return response.json()

    # Internal functions only below.
    def _delete(self, app, endpoint, rest='rest', params=None):
        url = join_url_parts(self.base_url, app, '/{}'.format(rest), endpoint)
        try:
            response = self.session.delete(url, params=params or {})
        except requests.exceptions.ConnectionError:
            if not self.connection_pool_disabled:
                self.disable_connection_pool()
            response = self.session.delete(url, params=params or {})
        self._handle_http_error(response)
        return response

    def _get(self, endpoint, app=None, rest='rest', params=None, absolute_endpoint=False):
        url = endpoint if absolute_endpoint else join_url_parts(self.base_url, app, '/{}'.format(rest), endpoint)
        try:
            response = self.session.get(url, params=params or {})
        except requests.exceptions.ConnectionError:
            if not self.connection_pool_disabled:
                self.disable_connection_pool()
            response = self.session.get(url, params=params or {})
        self._handle_http_error(response)
        return response

    def _post(self, app, endpoint, rest='rest', params=None, data=None, files=None, headers=None):
        url = join_url_parts(self.base_url, app, '/{}'.format(rest), endpoint)
        if not data:
            data = None
        else:
            data = data if isinstance(data, str) else json.dumps(data)
        try:
            response = self.session.post(url, params=params or {}, data=data, files=files, headers=headers)
        except requests.exceptions.ConnectionError:
            if not self.connection_pool_disabled:
                self.disable_connection_pool()
            response = self.session.post(url, params=params or {}, data=data, files=files, headers=headers)
        self._handle_http_error(response)
        return response

    def _put(self, app, endpoint, rest='rest', params=None, data=None):
        url = join_url_parts(self.base_url, app, '/{}'.format(rest), endpoint)
        try:
            response = self.session.put(url, params=params or {}, data=json.dumps(data or {}))
        except requests.exceptions.ConnectionError:
            if not self.connection_pool_disabled:
                self.disable_connection_pool()
            response = self.session.put(url, params=params or {}, data=json.dumps(data or {}))
        self._handle_http_error(response)
        return response

    def _handle_http_error(self, response):
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            try:
                for issue in response.json().get('ISSUES', []):
                    code = issue.get('code', '')
                    if code.startswith('JOBRUNNER'):
                        raise JobRunnerError(code=code, message=issue['message'])
                    elif code.startswith('CONNECTION'):
                        raise ConnectionError(code=code, message=issue['message'])
            except ValueError:
                # If response cannot be decoded using json, do the normal re-raise below
                pass
            # If the HTTPError isn't handled above, re-raise it with the response text as the message and the
            # response itself as an attribute for further handling.
            raise requests.exceptions.HTTPError(response.text, response=response)

    def disable_connection_pool(self):
        logger.debug('Remote disconnected. Retrying with connection pool disabled ...')
        self.session.mount('https://', requests.adapters.HTTPAdapter(pool_connections=1))
        self.session.mount('http://', requests.adapters.HTTPAdapter(pool_connections=1))
        self.connection_pool_disabled = True


class Command:
    """Command to allow users to interact with commands submitted through DPM REST API.
    Args:
        api_client (:obj:`ApiClient`): DPM API client.
        response (:obj:`requests.Response`): Command reponse.
    """
    # pylint: disable=too-few-public-methods
    def __init__(self, api_client, response):
        self.api_client = api_client
        self.response = response


class CreateComponentsCommand(Command):
    """Command to interact with the response from create_components."""
    # pylint: disable=too-few-public-methods

    @property
    def full_auth_token(self):
        """Full auth token. This is needed by SDC."""
        return self.response.json()[0]['fullAuthToken']


class StartJobsCommand(Command):
    """Command returned when using startJobs endpoint."""

    def wait_for_pipelines(self, timeout_sec=300):
        """Waits for all jobs' pipelines to reach RUNNING status.

        Args:
            timeout_sec (:py:obj:`int`): Timeout for wait, in seconds. Default: ``300``

        Raises:
            An instance of :py:class:`streamsets.sdk.sdc_api.StatusError` if the pipeline reaches an error state.
        """
        # Utility function to be run by wait_for_condition that returns True when the correct number of pipeline
        # instances are running on engine instances.
        def all_pipeline_instances_running(job):
            job.refresh()
            pipeline_instance_engines = (job.data_collectors
                                         if getattr(job, 'executor_type', 'COLLECTOR') == 'COLLECTOR'
                                         else job.transformers)
            logger.debug('Pipeline instance engines: %s',
                         ', '.join(engine.url for engine in pipeline_instance_engines) or 'none')
            return len(pipeline_instance_engines) == job.number_of_instances

        # To avoid a whole bunch of if statements, we create a dictionary that maps
        # pipeline statuses to the StatusError derivative to be raised. The engine message
        # must be passed in as a dictionary with a key of 'message' because these
        # exceptions normally handle HTTP responses.
        STATUS_ERROR = {'CONNECT_ERROR': lambda message: ConnectError({'message': message}),
                        'RUN_ERROR': lambda message: RunError({'message': message}),
                        'RUNNING_ERROR': lambda message: RunningError({'message': message}),
                        'START_ERROR': lambda message: StartError({'message': message}),
                        'STARTING_ERROR': lambda message: StartingError({'message': message})}

        # Another utility function that returns True unless a non-RUNNING status is seen in running pipelines or
        # an Exception is raised. For full details on the algorithm being used, check out TLKT-523.
        def pipelines_started(job):
            job.refresh()
            logger.debug('Saw job status <%s, %s>.', job.status.status, job.status.color)
            pipeline_instance_engines = (job.data_collectors
                                         if getattr(job, 'executor_type', 'COLLECTOR') == 'COLLECTOR'
                                         else job.transformers)
            for pipeline_status in job.pipeline_status:
                logger.debug('Saw pipeline on engine (%s) in status %s.',
                             pipeline_instance_engines.get(id=pipeline_status.sdc_id).url,
                             pipeline_status.status)
                if pipeline_status.status in STATUS_ERROR:
                    raise STATUS_ERROR[pipeline_status.status](pipeline_status.message)

                if pipeline_status.status != 'RUNNING':
                    break
            else:
                return True

        # Actual execution of code starts here.
        for job in self.jobs:
            logger.debug('Waiting for %s pipeline %s ...', job.number_of_instances,
                         'instances' if job.number_of_instances > 1 else 'instance')
            wait_for_condition(all_pipeline_instances_running, [job])

            logger.debug('Waiting for job %s to start successfully ...', job.job_name)
            wait_for_condition(pipelines_started, [job], timeout=timeout_sec)


class JobStartStopCommand(Command):
    """Command to interact with the response of Start/Stop Job."""

    def wait_for_job_status(self, status, timeout_sec=300):
        """Wait for job status.

        Args:
            status (:obj:`str`): Job status.
            timeout_sec (:obj:`int`): Timeout for wait, in seconds. Default: 300
        """
        self.api_client.wait_for_job_status(self.response.json()['jobId'], status, timeout_sec)


class DeploymentStartStopCommand(Command):
    """Command to interact with the response of Start/Stop Deployment."""

    def wait_for_legacy_deployment_statuses(self, statuses, timeout_sec=300):
        """Wait for deployment statuses.

        Args:
            statuses (:obj:`list`): List of Deployment statuses.
            timeout_sec (:obj:`int`, optional): Timeout for wait, in seconds. Default: ``300``.
        """
        self.api_client.wait_for_legacy_deployment_statuses(self.response.json()['deploymentId'], statuses, timeout_sec)


class AdminToolApiClient(object):
    """
    API client to communicate with a ControlHub admin tool.

    Args:
        base_url (:obj:`str`): ControlHub instance's server URL.
        username (:obj:`str`): ControlHub username.
        password (:obj:`str`): ControlHub password.
        api_version (:obj:`int`, optional): The DPM API version. Default: :py:const:`DEFAULT_DPM_API_VERSION`
    """
    def __init__(self, base_url, username, password, api_version=DEFAULT_SCH_API_VERSION):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.api_version = api_version
        self._base_admin_http_url = None  # This gets filled up in login and back to None in logout
        self.session = requests.Session()
        self.session.headers.update(REQUIRED_HEADERS)

    def login(self):
        """Login to ControlHub admin tool."""
        # Perform basic authentication
        binary_user_pass = '{}:{}'.format(self.username, self.password).encode()
        encoded_auth = base64.encodebytes(binary_user_pass).decode('ascii').strip()
        self.session.headers.update({'Authorization': 'Basic {}'.format(encoded_auth)})
        try:
            command = self.get_system_components()
            response_json = command.response.json()
            list_records = [ record for record in response_json if record['attributes']]
            self._base_admin_http_url = list_records[0]['attributes']['baseAdminHttpUrl']
        except requests.exceptions.HTTPError as ex:
            if ex.response.status_code == 401:
                raise InvalidCredentialsError('Invalid credentials specified')
            raise

    def logout(self):
        """Logout from the admin tool."""
        del self.session.headers['Authorization']
        self._base_admin_http_url = None

    def get_system_components(self):
        """Get system components from admin tool.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        response = self._get(app=None,
                             endpoint='v{}/system/components'.format(self.api_version))
        return Command(self, response)

    def get_system_logs(self, ending_offset=-1):
        """Get ControlHub logs.

        Args:
            ending_offset (:obj:`int`, optional): Ending offset for log. Default: ``-1``.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        params = get_params(parameters=locals(), exclusions=('self'))
        params.update({'componentURL': self._base_admin_http_url})
        response = self._get(app=None,
                             endpoint='v{}/system/log'.format(self.api_version),
                             params=params)
        return Command(self, response)

    # Internal functions only below.
    def _delete(self, app, endpoint, rest='rest', params=None):
        url = join_url_parts(self.base_url, app, '/{}'.format(rest), endpoint)
        response = self.session.get(url, params=params or {})
        self._handle_http_error(response)
        return response

    def _get(self, app, endpoint, rest='rest', params=None, base_url=None):
        url = join_url_parts(self.base_url, app, '/{}'.format(rest), endpoint)
        response = self.session.get(url, params=params or {})
        self._handle_http_error(response)
        return response

    def _post(self, app, endpoint, rest='rest', params=None, data=None, files=None, headers=None, base_url=None):
        url = join_url_parts(self.base_url, app, '/{}'.format(rest), endpoint)
        if not data:
            data = None
        else:
            data = data if isinstance(data, str) else json.dumps(data)
        response = self.session.post(url, params=params or {}, data=data, files=files, headers=headers)
        self._handle_http_error(response)
        return response

    def _put(self, app, endpoint, rest='rest', params=None, data=None, base_url=None):
        url = join_url_parts(self.base_url, app, '/{}'.format(rest), endpoint)
        response = self.session.put(url, params=params or {}, data=json.dumps(data or {}))
        self._handle_http_error(response)
        return response

    def _handle_http_error(self, response):
        # Delegating to response object error handling as last resort.
        try:
            response.raise_for_status()
        except:
            logger.error('Encountered an error while doing %s on %s. Response: %s',
                         response.request.method,
                         response.request.url,
                         response.__dict__)
            raise
