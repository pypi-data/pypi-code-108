#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
from urllib.parse import urlencode

URL_TOKEN = "{url}/realms/{realm}/protocol/openid-connect/token"

def get_token(base_url, auth_realm, client_id,
              auth_username, auth_password, client_secret=None, validate_certs=True):
    auth_url = URL_TOKEN.format(url=base_url, realm=auth_realm)
    temp_payload = {
        'grant_type': 'password',
        'client_id': client_id,
        'client_secret': client_secret,
        'username': auth_username,
        'password': auth_password,
    }
    r = {}
    # Remove empty items, for instance missing client_secret
    payload = dict(
        (k, v) for k, v in temp_payload.items() if v is not None)
    try:
        resp = requests.post(url=auth_url, data=payload, verify=validate_certs)
        r = resp.json()
    except ValueError as e:
        raise KeycloakException(
            'API returned invalid JSON when trying to obtain access token from %s: %s'
            % (auth_url, str(e)))
    except Exception as e:
        raise KeycloakException('Could not obtain access token from %s: %s'
                            % (auth_url, str(e)))

    try:
        return r['access_token']
    except KeyError:
        raise KeycloakException(
            'Could not obtain access token from %s' % auth_url)

class KeycloakException(Exception):
    """ Keycloak Exception """
