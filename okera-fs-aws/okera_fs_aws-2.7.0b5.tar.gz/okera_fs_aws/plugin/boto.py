# Copyright 2021 Okera Inc. All Rights Reserved.

import botocore
import requests
import logging
import getpass
import warnings
import urllib
from pathlib import Path
import os
import errno

from botocore.credentials import DeferredRefreshableCredentials, CredentialProvider
from botocore.utils import S3RegionRedirector
from botocore.compat import ( urlunsplit, urlsplit )
from botocore.regions import EndpointResolver


# required to avoid warnings about ssl validation with python2.7
from urllib3.exceptions import InsecureRequestWarning
warnings.simplefilter('ignore', InsecureRequestWarning)
try:
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    warnings.simplefilter('ignore',InsecureRequestWarning)
except Exception:
    pass

RELATIVE_TOKEN_PATH = '.okera/token'
DEFAULT_AUTH_SERVER_ENDPOINT = "http://localhost:5001"

LOG = logging.getLogger(__name__)

class OkeraException(Exception):
    pass

class OkeraCredentialProvider(CredentialProvider):
    CANONICAL_NAME = "okera-aws-creds"

    def __init__(self, rest_api_url, auth_uri, token, token_source, verify_ssl=False):
        super(OkeraCredentialProvider, self).__init__()
        self._okera_rest_api_url = rest_api_url.rstrip('/')
        self._auth_server_uri = auth_uri
        self._okera_token = self._resolve_token(token, token_source)
        self._verify_ssl = verify_ssl

    def load(self):
        creds = DeferredRefreshableCredentials(refresh_using=self._refresh, method="okera-assume-role")
        return creds

    def _refresh(self):
        response = self._custom_aws_cred_refresh()
        credentials = {
            "access_key": response.get("key"),
            "secret_key": response.get("secret"),
            "expiry_time": response.get("expiry"),
            "token": None,
        }
        return credentials

    def _custom_aws_cred_refresh(self):
        api_url = "%s/%s" % (self._okera_rest_api_url, "api/v2/aws-tokens")
        headers = {"Authorization": "Bearer %s" % self._okera_token}
        res = requests.post(api_url, headers=headers, verify=self._verify_ssl)
        if res.status_code in (401, 403):
            raise OkeraException("Error in authenticating credentials request: %s" % res.text)
        else:
            return res.json()

    def _read_token(self, token_file):
        try:
            with open(str(token_file), 'r') as file:
                data = file.read().strip()
                return data
        except OSError as e:
            if (e.errno == errno.EACCES):
                LOG.warn("Not able to access user's token file.", e)
            else:
                LOG.warn("Not able to read user's token file.", e)

    def _get_user(self):
        user = getpass.getuser()
        if not user:
            raise OkeraException("The USER environment variable is not defined.")
        return user

    def _resolve_token(self, token, token_source):
        # aws config directs us to find token with auth server
        read_token = ""
        if "authserver" == token_source:
            user = self._get_user()
            LOG.debug("Trying auth server at %s." % self._auth_server_uri )
            auth_uri=(self._auth_server_uri + "/" + user)
            res = requests.get(auth_uri)
            if res.status_code in (401, 403):
                LOG.warn("Error retrieving user's JWT token from auth server: %s" % res.text)
            else:
                token_file = res.text
            if token_file:
                data = self._read_token(token_file)
                if data:
                    LOG.debug("Token configured by auth server.")
                    read_token = data

        # otherwise check for implicit token in the aws config
        if not read_token:
            LOG.debug("Using token defined in configuration file.")
            read_token = token

        # lastly look for token in user's home dir
        if not read_token:
            home_dir = os.getenv('HOME')
            if not home_dir:
                raise OkeraException("The HOME environment variable is not defined.")
            users_token_path = os.path.join( home_dir, RELATIVE_TOKEN_PATH )
            home_token = Path(users_token_path)
            if home_token.is_file():
                LOG.debug("Trying to read token from %s." % users_token_path)
                read_token = self._read_token(home_token)

        if not read_token:
            raise OkeraException("Not able to configure token from user's home, AWS confg or auth server.")

        return read_token

# If the user's region is not configured to be the the same as
# the bucket they're trying to access, they will receive a
# redirect from S3.  This will replace any custom endpoint configured
# for the original request.  To work around this, from the session,
# we can intercept the attempted update to the endpoint URL
# and re-insert the custom one so that the request is signed
# using the region from the correct AWS endpoint, but sent
# to the proxy service URL.
class OkeraEndpointResolver(EndpointResolver):

    def __init__(self, proxy_uri, endpoint_data):
        super(OkeraEndpointResolver, self).__init__(endpoint_data)
        self._proxy_uri = proxy_uri

    def _resolve(self, partition, service_name, service_data, endpoint_name):
        result = super()._resolve(partition, service_name, service_data, endpoint_name)

        # overide derived endpoint
        parsed = urllib.parse.urlparse(self._proxy_uri)
        scheme = "%s://" % parsed.scheme
        hostport = parsed.geturl().replace(scheme, '', 1)
        result['hostname'] = hostport
        return result

def okera_session(session, token, token_source, rest_uri, proxy_uri, mode, auth_uri=None):

    bc_session = None
    if isinstance(session, botocore.session.Session):
        bc_session = session
    else:
        bc_session = session._session

    boto3_session = session
    # TODO: don't assume it's a cred resolver
    cred_chain = bc_session.get_component('credential_provider')
    auth_endpoint = auth_uri or DEFAULT_AUTH_SERVER_ENDPOINT
    okera_cred_provider = OkeraCredentialProvider(rest_uri, auth_endpoint, token, token_source)
    if cred_chain.providers:
        first_provider = cred_chain.providers[0].METHOD
        cred_chain.insert_before(first_provider, okera_cred_provider)
    else:
        cred_chain.providers.insert(0, okera_cred_provider)
    config = botocore.config.Config()
    if mode == "proxy":
        config.merge(botocore.config.Config(
            proxies={'https': proxy_uri}))

    orig_config = bc_session.get_default_client_config()
    if not orig_config:
        orig_config = botocore.config.Config()

    bc_session.set_default_client_config(orig_config.merge(config))

    # in endpoint mode, register the EndpointResolver to keep the endpoint
    # fixed on the Okera proxy service
    if not mode or mode == "endpoint":
        resolver = bc_session.get_component('endpoint_resolver')
        # copy the curreent resolvers state to the new one
        new_resolver = OkeraEndpointResolver(proxy_uri, resolver._endpoint_data)
        # ignore warnings and overwrite crucial SDK compoenent
        bc_session._internal_components.register_component(
            'endpoint_resolver', new_resolver)

    return boto3_session
