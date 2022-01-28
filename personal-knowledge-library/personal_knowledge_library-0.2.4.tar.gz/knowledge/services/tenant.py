# -*- coding: utf-8 -*-
# Copyright © 2021 Wacom. All rights reserved.
from typing import List, Dict

import requests
from requests import Response

from knowledge.services import USER_AGENT_STR
from knowledge.services.base import WacomServiceAPIClient, WacomServiceException
from knowledge.services.graph import AUTHORIZATION_HEADER_FLAG


class TenantManagementServiceAPI(WacomServiceAPIClient):
    """
    Tenant Management Service API
    -----------------------------

    Functionality:
        - List all tenants
        - Create tenants
        - Create users

    Parameters
    ----------
    tenant_token: str
        Tenant Management token
    service_url: str
        URL of the service
    service_endpoint: str
        Base endpoint
    """

    TENANT_ENDPOINT: str = 'tenant'
    USER_DETAILS_ENDPOINT: str = f'{WacomServiceAPIClient.USER_ENDPOINT}/users'
    SERVICE_URL: str = 'https://stage-private-knowledge.wacom.com'

    def __init__(self, tenant_token: str, service_url: str = SERVICE_URL, service_endpoint: str = 'graph'):
        self.__tenant_management_token: str = tenant_token
        super().__init__("TenantManagementServiceAPI", service_url=service_url, service_endpoint=service_endpoint)

    @property
    def tenant_management_token(self) -> str:
        """Tenant Management token."""
        return self.__tenant_management_token

    @tenant_management_token.setter
    def tenant_management_token(self, value: str):
        self.__tenant_management_token = value

    # ------------------------------------------ Tenants handling ------------------------------------------------------

    def create_tenant(self, name: str) -> Dict[str, str]:
        """
        Creates a tenant.

        Parameters
        ----------
        name: str -
            Name of the tenant

        Returns
        -------
        tenant_dict: Dict[str, str]

        Newly created tenant structure.
        >>>     {
        >>>       "id": "<Tenant-ID>",
        >>>       "apiKey": "<Tenant-API-Key>",
        >>>       "name": "<Tenant-Name>"
        >>>    }

        Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.
        """
        url: str = '{}/{}{}'.format(self.service_url, self.service_endpoint,
                                    TenantManagementServiceAPI.TENANT_ENDPOINT)
        headers: dict = {
            'User-Agent': USER_AGENT_STR,
            AUTHORIZATION_HEADER_FLAG: f'Bearer {self.__tenant_management_token}',
            'Content-Type': 'application/json'
        }
        payload: dict = {
            'name': name
        }
        response: Response = requests.post(url, headers=headers, json=payload, verify=self.verify_calls)
        if response.ok:
            return response.json()

    def listing_tenant(self) -> List[Dict[str, str]]:
        """
        Listing all tenants configured for this instance.

        Returns
        -------
        tenants:  List[Dict[str, str]]
            List of tenants:
            >>> [
            >>>     {
            >>>        "id": "<Tenant-ID>",
            >>>        "apiKey": "<Tenant-API-Key>",
            >>>        "name": "<Tenant-Name>"
            >>>     },
            >>>     ...
            >>> ]
        Raises
        ------
        WacomServiceException
            If the tenant service returns an error code.
        """
        url: str = f'{self.service_base_url}{TenantManagementServiceAPI.TENANT_ENDPOINT}'
        headers: dict = {
            'User-Agent': USER_AGENT_STR,
            AUTHORIZATION_HEADER_FLAG: f'Bearer {self.__tenant_management_token}'
        }
        response: Response = requests.get(url, headers=headers, data={}, verify=self.verify_calls)
        if response.ok:
            return response.json()
        raise WacomServiceException(f'Response code:={response.status_code}, exception:= {response.text}')

