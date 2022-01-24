# Copyright 2020 OpenStack Foundation
# Copyright 2020 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import json
from unittest import mock
import os.path
import jwt
from io import StringIO
import time

from zuul.driver import auth

from tests.base import BaseTestCase, FIXTURE_DIR

with open(os.path.join(FIXTURE_DIR,
                       'auth/openid-configuration.json'), 'r') as well_known:
    FAKE_WELL_KNOWN_CONFIG = json.loads(well_known.read())


algo = jwt.algorithms.RSAAlgorithm(jwt.algorithms.RSAAlgorithm.SHA256)
with open(os.path.join(FIXTURE_DIR,
                       'auth/oidc-key'), 'r') as k:
    OIDC_PRIVATE_KEY = algo.prepare_key(k.read())
with open(os.path.join(FIXTURE_DIR,
                       'auth/oidc-key.pub'), 'r') as k:
    pub_key = algo.prepare_key(k.read())
    pub_jwk = algo.to_jwk(pub_key)
    key = {
        "kid": "OwO",
        "use": "sig",
        "alg": "RS256"
    }
    key.update(json.loads(pub_jwk))
    # not present in keycloak jwks
    if "key_ops" in key:
        del key["key_ops"]
    FAKE_CERTS = {
        "keys": [
            key
        ]
    }


class FakeResponse:
    def __init__(self, json_dict):
        self._json = json_dict

    def json(self):
        return self._json


def mock_get(url, params=None, **kwargs):
    if url == ("https://my.oidc.provider/auth/realms/realm-one/"
               ".well-known/openid-configuration"):
        return FakeResponse(FAKE_WELL_KNOWN_CONFIG)
    else:
        raise Exception("Unknown URL %s" % url)


def mock_urlopen(url, *args, **kwargs):
    if url == ("https://my.oidc.provider/auth/realms/realm-one/"
               "protocol/openid-connect/certs"):
        io = StringIO()
        json.dump(FAKE_CERTS, io)
        io.seek(0)
        return io
    else:
        raise Exception("Unknown URL %s" % url)


class TestOpenIDConnectAuthenticator(BaseTestCase):
    def test_decodeToken(self):
        """Test the decoding workflow"""
        config = {
            'issuer_id': FAKE_WELL_KNOWN_CONFIG['issuer'],
            'client_id': 'zuul-app',
            'realm': 'realm-one',
        }
        OIDCAuth = auth.jwt.OpenIDConnectAuthenticator(**config)
        payload = {
            'iss': FAKE_WELL_KNOWN_CONFIG['issuer'],
            'aud': config['client_id'],
            'exp': time.time() + 3600,
            'sub': 'someone'
        }
        token = jwt.encode(
            payload,
            OIDC_PRIVATE_KEY,
            algorithm='RS256',
            headers={'kid': 'OwO'})
        with mock.patch('requests.get', side_effect=mock_get):
            # patching call in PyJWKClient's fetch_data
            with mock.patch('urllib.request.urlopen',
                            side_effect=mock_urlopen):
                decoded = OIDCAuth.decodeToken(token)
                for claim in payload.keys():
                    self.assertEqual(payload[claim], decoded[claim])
