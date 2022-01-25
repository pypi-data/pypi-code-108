import os
from functools import cached_property
from urllib.parse import urlencode

import requests
import jwcrypto.jwk
import jwcrypto.jwt
import json
import datetime
from rdflib import Graph

from solidclient.utils.utils import make_random_string, make_verifier_challenge
from oic.oic import Client as OicClient
from oic.utils.authn.client import CLIENT_AUTHN_METHOD

_HOST = os.environ.get("APP_HOST", "localhost")
_SCHEME = os.environ.get("APP_SCHEME", "http")
_PORT = os.environ.get("APP_PORT", "8069")
_ISSUER = os.environ.get("OIDC_SERVER_URL", "http://localhost:3000/")
_OID_CALLBACK_PATH = os.environ.get("OIDC_CALLBACK_ENDPOINT", "/casemanagement/oauth/callback")


class SolidSession:

    def __init__(self, keypair=None, access_token=None, state_storage=None, redirect_url='/casemanagement'):
        """
        Init SolidSession with key and access token
        :param keypair: jwcrypto.jwk.JWK
        :param access_token: jwcrypto.jwt.JWT
        """
        self.keypair = keypair
        self.access_token = access_token
        self.state_storage = state_storage if state_storage else dict()
        self.redirect_url = redirect_url
        self.client_id = None
        self.client_secret = None

    @cached_property
    def provider_info(self):
        return requests.get(_ISSUER + ".well-known/openid-configuration").json()

    def register_client(self):
        # Client registration.
        # https://pyoidc.readthedocs.io/en/latest/examples/rp.html#client-registration
        registration_response = OicClient(
            client_authn_method=CLIENT_AUTHN_METHOD).register(
            self.provider_info['registration_endpoint'],
            redirect_uris=[self.get_callback_url()])

        self.client_id = registration_response['client_id']
        self.client_secret = registration_response['client_secret']

        return registration_response

    @staticmethod
    def get_callback_url():
        return f"{_SCHEME}://{_HOST}:{_PORT}{_OID_CALLBACK_PATH}"

    def get_authorization_endpoint_uri(self, redirect_url=None):
        """
        Returns URL for authorization endpoint
        :param redirect_url: URL to redirect to
        :return: URL to redirect to
        """
        code_verifier, code_challenge = make_verifier_challenge()

        state = make_random_string()
        assert state not in self.state_storage
        self.state_storage[state] = {
            'solid_code_verifier': code_verifier,
            'solid_redirect_url': redirect_url if redirect_url else self.redirect_url
        }

        query = urlencode({
            "code_challenge": code_challenge,
            "state": state,
            "response_type": "code",
            "redirect_uri": self.get_callback_url(),
            "code_challenge_method": "S256",
            "client_id": self.client_id,
            # offline_access: also asks for refresh token
            "scope": "openid offline_access",
        })
        url = self.provider_info['authorization_endpoint'] + '?' + query

        return url

    @staticmethod
    def make_token(keypair, uri, method):
        """
        Get a DPoP token
        :param keypair: JSON string representation of jwcrypto.jwk.JWK
        :param uri: URI to bind token to
        :param method: Method to bind token to
        :return: Serialized jwcrypto.jwt.JWT
        """
        key = jwcrypto.jwk.JWK.from_json(keypair) if type(keypair) == str else keypair
        jwt = jwcrypto.jwt.JWT(
            header={
                "typ": "dpop+jwt",
                "alg": "ES256",
                "jwk": key.export(private_key=False, as_dict=True)
            },
            claims={
                "jti": make_random_string(),
                "htm": method,
                "htu": uri,
                "iat": int(datetime.datetime.now().timestamp())
            })

        jwt.make_signed_token(key)
        return jwt.serialize()

    def make_headers(self, uri, method):
        if not self.access_token:
            return {}
        else:
            return {
                "Authorization": ("DPoP " + self.access_token),
                "DPoP": self.make_token(self.keypair, uri, method)
            }

    def send_request(self, uri, method, data=None, content_type="text/turtle"):
        """
        Issue request to Solid server
        :param uri: URI target
        :param method: Method to be used
        :param data: Body data if any
        :param content_type: Content-Type header
        :rtype: SolidResponse
        """
        headers = self.make_headers(uri, method)

        if method == "GET":
            resp = requests.get(uri, headers=headers)
            auth_url = self.get_authorization_endpoint_uri()
            return SolidResponse(resp, self, auth_url=auth_url)

        elif method == "DELETE":
            resp = requests.delete(uri, headers=headers)

            return SolidResponse(resp, self)

        # Is POST needed? Just PUT 4Head
        elif method == "POST":
            headers["Content-Type"] = content_type
            resp = requests.post(uri, data=data, headers=headers)

            return SolidResponse(resp, self)

        elif method == "PUT":
            headers["Content-Type"] = content_type
            resp = requests.put(uri, headers=headers, data=data)

            return SolidResponse(resp, self)

    def get(self, uri):
        return self.send_request(uri, "GET")

    # data = rdflib.Graph
    def put(self, uri, data):
        return self.send_request(uri, "PUT", data=data)

    def delete(self, uri):
        return self.send_request(uri, "DELETE")

    def post(self, uri, data, content_type="application/json"):
        return self.send_request(uri, "POST", data=data, content_type=content_type)


class SolidResponse:

    def __init__(self, response, solid_session, auth_url=None):
        """
        Init SolidResponse
        :param response: Response object
        :type response: requests.Response
        :param solid_session: SolidSession object
        :type solid_session: SolidSession
        """
        self.response = response
        self.status_code = response.status_code
        self.content_type = response.headers["Content-Type"] if "Content-Type" in response.headers else None
        self.raw_text = response.text
        self.solid_session = solid_session
        self.rdf_graph = None
        self.auth_url = auth_url

    def get_graph(self):
        # Or other RDF types
        if self.content_type == "text/turtle":
            self.rdf_graph = Graph().parse(data=self.raw_text)
        return self.rdf_graph


class SolidClient:

    def __init__(self, key, access_token, state_storage):
        """
        Init SolidClient with key and access token
        :param key: jwcrypto.jwk.JWK
        :param access_token: jwcrypto.jwt.JWT
        """
        self.key = key
        self.access_token = access_token
        self.state_storage = state_storage

    # Refresh_token
    @staticmethod
    def login(key, token):
        return SolidSession(key, token)

    def login_key_access_token(self):
        return SolidSession(
            jwcrypto.jwk.JWK.from_json(json.dumps(self.key)),
            self.access_token,
            self.state_storage
        )
