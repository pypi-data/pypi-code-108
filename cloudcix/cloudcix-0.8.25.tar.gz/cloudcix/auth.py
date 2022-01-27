# -*- coding: utf-8 -*-

"""
This file implements features related to Authentication for the CloudCIX API.
"""

import requests

import cloudcix.api
import cloudcix.conf
import cloudcix.exceptions


def get_token(email, password, api_key):
    """
    Attempts to generate a CloudCIX token for any given email, password, and api_key combination.
    This method will return the token if it was successfully created.
    If any errors are returned from the API, a `CloudCIXAuthException` will be raised by this method.

    If there is an error connecting to the API, or the API has an internal error, a normal Exception will be raised.
    This Exception will contain the content of the response as its message.

    :param email: The email address to use for authentication.
    :type email: str
    :param password: The password to use for authentication.
    :type password: str
    :param api_key: The api_key of the Member the user is logging in under.
    :type api_key: str
    """
    data = {
        'email': email,
        'password': password,
        'api_key': api_key,
    }
    response = cloudcix.api.Membership.token.create(data=data)
    if response.status_code == 201:
        return response.json()['token']
    elif response.status_code == 400:
        data = response.json()
        raise cloudcix.exceptions.CloudCIXAuthException(
            data['error_code'],
            data['detail'],
        )
    else:
        raise Exception(response.content)


def get_admin_token():
    """
    Generates an `admin` token using the credentials specified in the settings module
    (``CLOUDCIX_API_USERNAME``, ``CLOUDCIX_API_PASSWORD``, and ``CLOUDCIX_API_KEY``).
    """
    return get_token(
        cloudcix.conf.settings.CLOUDCIX_API_USERNAME,
        cloudcix.conf.settings.CLOUDCIX_API_PASSWORD,
        cloudcix.conf.settings.CLOUDCIX_API_KEY,
    )


class TokenAuth(requests.auth.AuthBase):
    """
    Wrapper around :py:class:`requests.auth.AuthBase` that is designed to put a token into the correct header for use
    with our API.
    """

    def __init__(self, token):
        """
        Create an instance of the TokenAuth class with a specified token

        :param token: The token that will be used to authenticate the request.
        :type token: str
        """
        self.token = token

    def __call__(self, request):
        """
        Used to set the correct header in the request when the request is about to be sent.

        :param request: The request that this TokenAuth instance has been used for.
        :type request: requests.Request
        """
        request.headers['X-Auth-Token'] = self.token
        return request

    def __eq__(self, other):
        """
        Compares two instances of the TokenAuth class to check if they have the same token.

        :param other: Another instance of TokenAuth that will be compared against this one.
        :type other: cloudcix.auth.TokenAuth
        """
        return self.token == other.token
