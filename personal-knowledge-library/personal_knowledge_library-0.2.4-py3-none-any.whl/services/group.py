# -*- coding: utf-8 -*-
# Copyright © 2021 Wacom. All rights reserved.
import urllib.parse
from typing import Dict, List, Any

import requests
from requests import Response

from knowledge.base.access import GroupAccessRight
from knowledge.base.ontology import NAME_TAG
from knowledge.services.base import WacomServiceAPIClient, WacomServiceException
from knowledge.services.graph import AUTHORIZATION_HEADER_FLAG, CONTENT_TYPE_HEADER_FLAG

# -------------------------------------- Constant flags ----------------------------------------------------------------

GROUP_USER_RIGHTS_TAG: str = "groupUserRights"
JOIN_KEY_PARAM: str = "joinKey"
USER_TO_ADD_PARAM: str = "userToAddId"
USER_TO_REMOVE_PARAM: str = "userToRemoveId"


class Group(object):
    """
    Group
    -----
    In Personal Knowledge backend users can be logically grouped.

    Parameters
    ----------
    tenant_id: str
        Tenant id
    group_id: str
        Group id
    owner: str
        User id who has created the group.
    name: str
        Name of the group.
    join_key: str
        Key which is required to join the group
    rights: GroupAccessRight
        Access right for group
    """

    def __init__(self, tenant_id: str, group_id: str, owner: str, name: str, join_key: str, rights: GroupAccessRight):
        self.__tenant_id: str = tenant_id
        self.__group_id: str = group_id
        self.__owner_id: str = owner
        self.__name: str = name
        self.__join_key: str = join_key
        self.__rights: GroupAccessRight = rights

    @property
    def id(self) -> str:
        """Group id."""
        return self.__group_id

    @property
    def tenant_id(self) -> str:
        """Tenant ID."""
        return self.__tenant_id

    @property
    def owner_id(self) -> str:
        """Owner id (internal id) of the user, who owns the group."""
        return self.__owner_id

    @property
    def name(self) -> str:
        """Name of the group."""
        return self.__name

    @property
    def join_key(self) -> str:
        """Key for joining the group."""
        return self.__join_key

    @property
    def group_access_rights(self) -> GroupAccessRight:
        """Rights for group."""
        return self.__rights

    @classmethod
    def parse(cls, param: Dict[str, Any]) -> 'Group':
        tenant_id: str = param.get('tenantId')
        owner_id: str = param.get('ownerId')
        join_key: str = param.get('joinKey')
        group_id: str = param.get('id')
        name: str = param.get('name')
        rights: GroupAccessRight = GroupAccessRight.parse(param.get('groupUserRights', ['Read']))
        return Group(tenant_id=tenant_id, group_id=group_id, owner=owner_id, join_key=join_key, name=name,
                     rights=rights)

    def __repr__(self):
        return f'<Group: id:={self.id}, name:={self.name}, group access right:={self.group_access_rights}]>'


class GroupManagementServiceAPI(WacomServiceAPIClient):
    """
    Group Management Service API
    -----------------------------
    The service is managing groups.

    Functionality:
        - List all groups
        - Create group
        - Assign users to group
        - Share entities with group

    Parameters
    ----------
    service_url: str
        URL of the service
    service_endpoint: str
        Base endpoint
    """

    GROUP_ENDPOINT: str = 'group'
    """"Endpoint for all group related functionality."""
    SERVICE_URL: str = 'https://stage-private-knowledge.wacom.com'

    def __init__(self, service_url: str = SERVICE_URL, service_endpoint: str = 'graph'):
        super().__init__("GroupManagementServiceAPI", service_url=service_url, service_endpoint=service_endpoint)

    # ------------------------------------------ Groups handling ------------------------------------------------------

    def create_group(self, auth_key: str, name: str, rights: GroupAccessRight = GroupAccessRight(read=True)) \
            -> Group:
        """
        Creates a group.

        Parameters
        ----------
        auth_key: str
            User key.
        name: str
            Name of the tenant
        rights: GroupAccessRight
            Access rights

        Returns
        -------
        group: Group
            Instance of the group.

        Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.
        """
        url: str = f'{self.service_base_url}{GroupManagementServiceAPI.GROUP_ENDPOINT}'
        headers: Dict[str, str] = {
            AUTHORIZATION_HEADER_FLAG: f'Bearer {auth_key}',
            CONTENT_TYPE_HEADER_FLAG: 'application/json'
        }
        payload: Dict[str, str] = {
            NAME_TAG: name,
            GROUP_USER_RIGHTS_TAG: rights.to_list()
        }
        response: Response = requests.post(url, headers=headers, json=payload, verify=self.verify_calls)
        if response.ok:
            return Group.parse(response.json())
        raise WacomServiceException(f'Creation of group failed.'
                                    f'Response code:={response.status_code}, exception:= {response.text}')

    def update_group(self, auth_key: str, group_id: str, name: str, rights: GroupAccessRight = GroupAccessRight):
        """
        Updates a group.

        Parameters
        ----------
        auth_key: str
            User key.
        group_id: str
            ID of the group.
        name: str
            Name of the tenant
        rights: GroupAccessRight
            Access rights

        Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.
        """
        url: str = f'{self.service_base_url}{GroupManagementServiceAPI.GROUP_ENDPOINT}/{group_id}'
        headers: Dict[str, str] = {
            AUTHORIZATION_HEADER_FLAG: f'Bearer {auth_key}',
            CONTENT_TYPE_HEADER_FLAG: 'application/json'
        }
        payload: Dict[str, str] = {
            NAME_TAG: name,
            GROUP_USER_RIGHTS_TAG: rights.to_list()
        }
        response: Response = requests.patch(url, headers=headers, json=payload, verify=self.verify_calls)
        if not response.ok:
            raise WacomServiceException(f'Update of group failed.'
                                        f'Response code:={response.status_code}, exception:= {response.text}')

    def delete_group(self, auth_key: str, group_id: str):
        """
         Delete a group.

         Parameters
         ----------
         auth_key: str
             User key.
         group_id: str
             ID of the group.

         Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.
        """
        url: str = f'{self.service_base_url}{GroupManagementServiceAPI.GROUP_ENDPOINT}/{group_id}'
        headers: Dict[str, str] = {
            AUTHORIZATION_HEADER_FLAG: f'Bearer {auth_key}'
        }
        response: Response = requests.delete(url, headers=headers, verify=self.verify_calls)
        if not response.ok:
            raise WacomServiceException(f'Deletion of group failed.'
                                        f'Response code:={response.status_code}, exception:= {response.text}')

    def listing_groups(self, auth_key: str, admin: bool = False) -> List[Group]:
        """
        Listing all groups configured for this instance.

        Parameters
        ----------
        auth_key: str
            API key for authentication

        admin: bool (default:= False)
            Uses admin privilege to show all groups of the tenant.
            Requires user to have the role: TenantAdmin

        Returns
        -------
        user:  List[Groups]
            List of groups.
        """
        url: str = f'{self.service_base_url}{GroupManagementServiceAPI.GROUP_ENDPOINT}'
        if admin:
            url += '/admin'
        headers: Dict[str, str] = {
            AUTHORIZATION_HEADER_FLAG: f'Bearer {auth_key}'
        }
        response: Response = requests.get(url, headers=headers, verify=self.verify_calls)
        if response.ok:
            groups: List[Dict[str, Any]] = response.json()
            return [Group.parse(g) for g in groups]
        raise WacomServiceException(f'Listing of group failed.'
                                    f'Response code:={response.status_code}, exception:= {response.text}')

    def group(self, auth_key: str, group_id: str) -> Group:
        """Get a group.

        Parameters
        ----------
        auth_key: str
            API key for user.
        group_id: str
            Id of group

        Returns
        -------
        group: Group
            Instance of the group

        Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.
        """
        url: str = f'{self.service_base_url}{GroupManagementServiceAPI.GROUP_ENDPOINT}/{group_id}'
        headers: Dict[str, str] = {
            AUTHORIZATION_HEADER_FLAG: f'Bearer {auth_key}'
        }
        response: Response = requests.get(url, headers=headers, verify=self.verify_calls)
        if response.ok:
            group: Dict[str, Any] = response.json()
            return Group.parse(group)
        raise WacomServiceException(f'Listing of users failed.'
                                    f'Response code:={response.status_code}, exception:= {response.text}')

    def join_group(self, auth_key: str, group_id: str, join_key: str):
        """User joining a group with his auth token.

        Parameters
        ----------
        auth_key: str
            API key for user.
        group_id: str
            Id of group
        join_key: str
            Key which is used to join the group.

        Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.
        """
        url: str = f'{self.service_base_url}{GroupManagementServiceAPI.GROUP_ENDPOINT}/{group_id}/join'
        headers: Dict[str, str] = {
            AUTHORIZATION_HEADER_FLAG: f'Bearer {auth_key}'
        }
        params: Dict[str, str] = {
            JOIN_KEY_PARAM: join_key,
        }
        response: Response = requests.post(url, headers=headers, params=params, verify=self.verify_calls)
        if not response.ok:
            raise WacomServiceException(f'Joining the group failed.'
                                        f'Response code:={response.status_code}, exception:= {response.text}')

    def leave_group(self, auth_key: str, group_id: str):
        """User leaving a group with his auth token.

        Parameters
        ----------
        auth_key: str
            API key for user.
        group_id: str
            Id of group

        Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.
        """
        url: str = f'{self.service_base_url}{GroupManagementServiceAPI.GROUP_ENDPOINT}/{group_id}/leave'
        headers: Dict[str, str] = {
            AUTHORIZATION_HEADER_FLAG: f'Bearer {auth_key}'
        }

        response: Response = requests.post(url, headers=headers, verify=self.verify_calls)
        if not response.ok:
            raise WacomServiceException(f'Leaving group failed.'
                                        f'Response code:={response.status_code}, exception:= {response.text}')

    def add_user_to_group(self, auth_key: str, group_id: str, user_id: str):
        """Adding a user to group.

        Parameters
        ----------
        auth_key: str
            API key for user.
        group_id: str
            Id of group
        user_id: str
            User who is added to the group

        Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.
        """
        url: str = f'{self.service_base_url}{GroupManagementServiceAPI.GROUP_ENDPOINT}/{group_id}/user/add'
        headers: Dict[str, str] = {
            AUTHORIZATION_HEADER_FLAG: f'Bearer {auth_key}'
        }
        params: Dict[str, str] = {
            USER_TO_ADD_PARAM: user_id,
        }
        response: Response = requests.post(url, headers=headers, params=params, verify=self.verify_calls)
        if not response.ok:
            raise WacomServiceException(f'Adding of user to group failed.'
                                        f'Response code:={response.status_code}, exception:= {response.text}')

    def remove_user_to_group(self, auth_key: str, group_id: str, user_id: str):
        """Remove a user to group.

        Parameters
        ----------
        auth_key: str
            API key for user.
        group_id: str
            Id of group
        user_id: str
            User who is remove from the group

        Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.
        """
        url: str = f'{self.service_base_url}{GroupManagementServiceAPI.GROUP_ENDPOINT}/{group_id}/user/remove'
        headers: Dict[str, str] = {
            AUTHORIZATION_HEADER_FLAG: f'Bearer {auth_key}'
        }
        params: Dict[str, str] = {
            USER_TO_ADD_PARAM: user_id,
        }
        response: Response = requests.post(url, headers=headers, params=params, verify=self.verify_calls)
        if not response.ok:
            raise WacomServiceException(f'Removing of user from group failed.'
                                        f'Response code:={response.status_code}, exception:= {response.text}')

    def add_entity_to_group(self, auth_key: str, group_id: str, entity_uri: str):
        """Adding a entity to group.

        Parameters
        ----------
        auth_key: str
            API key for user.
        group_id: str
            Id of group
        entity_uri: str
            Entity URI

        Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.
        """
        uri: str = urllib.parse.quote(entity_uri)
        url: str = f'{self.service_base_url}{GroupManagementServiceAPI.GROUP_ENDPOINT}/{group_id}/entity/{uri}/add'
        headers: Dict[str, str] = {
            AUTHORIZATION_HEADER_FLAG: f'Bearer {auth_key}'
        }

        response: Response = requests.post(url, headers=headers, verify=self.verify_calls)
        if not response.ok:
            raise WacomServiceException(f'Adding of entity to group failed.'
                                        f'Response code:={response.status_code}, exception:= {response.text}')

    def remove_entity_to_group(self, auth_key: str, group_id: str, entity_uri: str):
        """Remove a entity from group.

        Parameters
        ----------
        auth_key: str
            API key for user.
        group_id: str
            Id of group
        entity_uri: str
            URI of entity

        Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.
        """
        uri: str = urllib.parse.quote(entity_uri)
        url: str = f'{self.service_base_url}{GroupManagementServiceAPI.GROUP_ENDPOINT}/{group_id}/entity/{uri}/remove'
        headers: Dict[str, str] = {
            AUTHORIZATION_HEADER_FLAG: f'Bearer {auth_key}'
        }

        response: Response = requests.post(url, headers=headers, verify=self.verify_calls)
        if not response.ok:
            raise WacomServiceException(f'Removing of entity to group failed.'
                                        f'Response code:={response.status_code}, exception:= {response.text}')
