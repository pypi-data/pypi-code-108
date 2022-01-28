# -*- coding: utf-8 -*-
# Copyright © 2021 Wacom. All rights reserved.
from abc import ABC

import requests
from requests import Response

from knowledge.services import USER_AGENT_STR


class WacomServiceException(Exception):
    """Exception thrown if Wacom service fails."""


class RESTAPIClient(ABC):
    """
    Abstract REST API client
    ------------------------
    REST API client handling the service url.

    Arguments
    ---------
    service_url: str
        Service URL for service
    verify_calls: bool (default:= False)
        Flag if the service calls should be verified
    """
    def __init__(self, service_url: str, verify_calls: bool = False):
        self.__service_url: str = service_url
        self.__verify_calls: bool = verify_calls

    @property
    def service_url(self) -> str:
        """Service URL."""
        return self.__service_url

    @property
    def verify_calls(self):
        """Certificate verification activated."""
        return self.__verify_calls

    @verify_calls.setter
    def verify_calls(self, value: bool):
        self.__verify_calls = value


class WacomServiceAPIClient(RESTAPIClient):
    """
    Wacom Service API Client
    ------------------------
    Abstract class for Wacom service APIs.

    Parameters
    ----------
    application_name: str
        Name of the application using the service
    service_url: str
        URL of the service
    service_endpoint: str
        Base endpoint
    verify_calls: bool (Default:= False)
        Flag if  API calls should be verified.
    """
    AUTH_ENDPOINT: str = 'auth/user'
    USER_ENDPOINT: str = 'user'
    USER_LOGIN_ENDPOINT: str = f'{USER_ENDPOINT}/login'

    def __init__(self, application_name: str, service_url: str, service_endpoint: str, verify_calls: bool = False):
        self.__application_name: str = application_name
        self.__service_endpoint: str = service_endpoint
        super().__init__(service_url, verify_calls)

    def request_user_token(self, tenant_key: str, external_id: str) -> str:
        """
        Login as user by using the tenant key and its external user id.

        Parameters
        ----------
        tenant_key: str
            Tenant key
        external_id: str
            External id.

        Returns
        -------
        auth_key: str
            Authentication key for identifying the user for the service calls.

        Raises
        ------
        WacomServiceException
            Exception if service returns HTTP error code.
        """
        url: str = f'{self.service_url}/graph/{WacomServiceAPIClient.USER_LOGIN_ENDPOINT}/'
        headers: dict = {
            'User-Agent': USER_AGENT_STR,
            'x-tenant-api-key': tenant_key
        }
        payload: dict = {
            'externalUserId': external_id
        }
        response: Response = requests.post(url, headers=headers, json=payload, verify=self.verify_calls)
        if response.ok:
            return response.text
        raise WacomServiceException(f'Response code:={response.status_code}, exception:= {response.text}')

    @property
    def service_endpoint(self):
        """Service endpoint."""
        return '' if len(self.__service_endpoint) == 0 else f'{self.__service_endpoint}/'

    @property
    def service_base_url(self):
        """Service endpoint."""
        return f'{self.service_url}/{self.service_endpoint}'

    @property
    def application_name(self):
        """Application name."""
        return self.__application_name
