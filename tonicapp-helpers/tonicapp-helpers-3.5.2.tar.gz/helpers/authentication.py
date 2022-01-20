# -*- coding: utf-8 -*-
"""
Authentication backend for handling firebase user.idToken from incoming
Authorization header, verifying, and locally authenticating
"""

import json
import uuid
import sys
import firebase_admin

from firebase_admin import auth

from django.conf import settings
from django.utils.encoding import smart_text
from django.utils import timezone

from rest_framework import HTTP_HEADER_ENCODING, exceptions

settings_auth = settings.AUTHENTICATION
if 'test' in sys.argv and 'FIREBASE_SERVICE_ACCOUNT_KEY' not in settings_auth.keys():
    firebase_credentials = None
    firebase = None
else:
    firebase_credentials = firebase_admin.credentials.Certificate(
        settings_auth["FIREBASE_SERVICE_ACCOUNT_KEY"]
    )
    firebase = firebase_admin.initialize_app(firebase_credentials)


class TonicAuthentication():
    www_authenticate_realm = 'api'

    def get_authorization_header(self, request):
        """
        Return request's 'Authorization:' header, as a bytestring.

        Hide some test client ickyness where the header can be unicode.
        """
        auth = request.META.get('HTTP_AUTHORIZATION', b'')
        if isinstance(auth, str):
            # Work around django test client oddness
            auth = auth.encode(HTTP_HEADER_ENCODING)
        return auth

    def authenticate(self, request):
        """
        With ALLOW_ANONYMOUS_REQUESTS, set request.user to an AnonymousUser,
        allowing us to configure access at the permissions level.
        """
        authorization_header = self.get_authorization_header(request)
        if settings_auth["ALLOW_ANONYMOUS_REQUESTS"] and not authorization_header:
            return (None, None)
        """
        Returns a tuple of len(2) of `User` and the decoded firebase token if
        a valid signature has been supplied using Firebase authentication.
        """

        prefix, token = self.get_token(request)

        decoded_token = self.decode_token(token, prefix)

        return (decoded_token, None)

    def get_token(self, request):
        """
        Parse Authorization header and retrieve JWT
        """
        authorization_header = self.get_authorization_header(request).split()

        if 'AUTH_HEADER_PREFIX' in settings_auth.keys():
            auth_header_prefix = settings_auth["AUTH_HEADER_PREFIX"]
        else:
            auth_header_prefix = settings_auth["FIREBASE_AUTH_HEADER_PREFIX"]

        if not authorization_header or len(authorization_header) != 2:
            raise exceptions.AuthenticationFailed(
                'Invalid Authorization header format, expecting: <prefix> <token>.'
            )

        if smart_text(authorization_header[0].upper()) not in auth_header_prefix:
            raise exceptions.AuthenticationFailed(
                f'Invalid Authorization header prefix, expecting one of this options: {auth_header_prefix}.'
            )

        return smart_text(authorization_header[0].upper()), authorization_header[1]

    def decode_token(self, token, prefix):
        """
        Attempt to verify JWT from Authorization header with Firebase or others authentications methods
        Return the decoded token
        """
        if prefix != 'JWT':
            if prefix == 'CWT' and token.decode('utf-8') in settings_auth["CUSTOM_WEB_TOKEN"].keys():
                return settings_auth['CUSTOM_WEB_TOKEN'][token.decode('utf-8')]

            if prefix == 'TWT' and token.decode('utf-8') == settings_auth['TONIC_WEB_TOKEN']:
                return {
                    'name': 'Tonic Admin',
                    'is_admin': True,
                    'user_id': '9999999',
                    'uid': '9999999'
                }
            raise exceptions.AuthenticationFailed('Token is invalid.')
        try:
            return auth.verify_id_token(
                token,
                check_revoked=settings_auth["FIREBASE_CHECK_JWT_REVOKED"]
            )
        except ValueError as exc:
            raise exceptions.AuthenticationFailed(
                'JWT was found to be invalid, or the App’s project ID cannot '
                'be determined.'
            )
        except (auth.InvalidIdTokenError,
                auth.ExpiredIdTokenError,
                auth.RevokedIdTokenError,
                auth.CertificateFetchError) as exc:
            if exc.code == 'ID_TOKEN_REVOKED':
                raise exceptions.AuthenticationFailed(
                    'Token revoked, inform the user to reauthenticate or '
                    'signOut().'
                )
            else:
                raise exceptions.AuthenticationFailed('Token is invalid.')

    def authenticate_header(self, request):
        return request
