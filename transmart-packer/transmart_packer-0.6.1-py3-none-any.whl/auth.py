import functools
import json
import logging
from typing import Mapping, Dict

import jwt
import requests
from jwt.algorithms import RSAAlgorithm
from tornado.log import app_log as log
from tornado.web import HTTPError

from .config import keycloak_config, http_config

logger = logging.getLogger(__name__)


def authorize(token: str) -> Mapping:
    """
    Validate the token to authorize the access
    :param token: request token
    :return: user's token
    """
    if token is None or len(token) == 0:
        error_msg = 'No authorisation token found in the request'
        logger.error(error_msg)
        raise HTTPError(401, 'Unauthorized.')
    decoded_token_header = jwt.get_unverified_header(token)
    token_kid = decoded_token_header.get('kid')
    algorithm, public_key = get_keycloak_public_key_and_algorithm(token_kid)
    user_token = jwt.decode(token, public_key, algorithms=algorithm, audience=keycloak_config.get("client_id"))
    return user_token


@functools.lru_cache(maxsize=2)
def get_keycloak_public_key_and_algorithm(token_kid):
    """
    Get Keycloak public key and token signing algorithm
    :param token_kid: Token kid
    :return: Algorithm and public_key pair
    """
    handle = f'{keycloak_config.get("oidc_server_url")}/protocol/openid-connect/certs'
    log.info(f'Getting public key for the kid={token_kid} from the keycloak...')
    r = requests.get(handle, verify=http_config.get('verify_cert'))
    if not r.ok:
        error = "Could not get certificates from Keycloak. " \
                "Reason: [{}]: {}".format(r.status_code, r.text)
        logger.error(error)
        raise ValueError(error)
    try:
        json_response = r.json()
    except Exception:
        error = "Could not retrieve the public key. " \
                "Got unexpected response: '{}'".format(r.text)
        logging.error(error)
        raise ValueError(error)
    try:
        matching_key = next((item for item in json_response.get('keys') if item['kid'] == token_kid), None)
        if matching_key is None:
            error = "No public key found for kid {}".format(token_kid)
            logger.error(error)
            raise ValueError(error)
        matching_key_json = json.dumps(matching_key)
        public_key = RSAAlgorithm.from_jwk(matching_key_json)
    except Exception as e:
        error = f'Invalid public key!. Reason: {e}'
        logger.error(error)
        raise ValueError(error)
    logger.info(f'The public key for the kid={token_kid} has been fetched.')
    return matching_key.get('alg'), public_key


def get_impersonated_token_for_user(current_user: str) -> str:
    """
    Exchange offline token for (impersonated) current task user’s token
    :param current_user: current task user
    :return: task user's access token
    """
    offline_user_access_token = get_access_token_by_offline_token()
    handle = f'{keycloak_config.get("oidc_server_url")}/protocol/openid-connect/token'
    params = {'grant_type': 'urn:ietf:params:oauth:grant-type:token-exchange',
              'requested_subject': current_user,
              'client_id': f'{keycloak_config.get("client_id")}',
              'subject_token': offline_user_access_token}
    return get_access_token(handle, params)


def get_access_token_by_offline_token() -> str:
    """
    Get access token based on offline token
    :return: offline user's access token
    """
    handle = f'{keycloak_config.get("oidc_server_url")}/protocol/openid-connect/token'
    params = {'grant_type': 'refresh_token',
              'scope': 'offline_access',
              'client_id': f'{keycloak_config.get("client_id")}',
              'refresh_token': f'{keycloak_config.get("offline_token")}'}
    return get_access_token(handle, params)


def get_access_token(url: str, params: Dict) -> str:
    """
    Get access token from Keycloak
    :param url: Keycloak server URL
    :param params: Request body params
    :return: access token
    """
    response = requests.post(url=url, data=params, verify=http_config.get('verify_cert'))
    if not response.ok:
        error = "Could not get a token from Keycloak. " \
                "Reason: [{}]: {}".format(response.status_code, response.text)
        logger.error(error)
        raise ValueError(error)
    try:
        json_response = response.json()
        return json_response['access_token']
    except Exception:
        error = "Could not retrieve the access token. " \
                "Got unexpected response: '{}'".format(response.text)
        logger.error(error)
        raise ValueError(error)

