import json
import logging
import multiprocessing
import os
import requests
import time
import jwt

try:
    from urllib import parse
except ImportError:
    import urlparse as parse

from ciocore import config
from ciocore import common, auth


from ciocore.common import CONDUCTOR_LOGGER_NAME

logger = logging.getLogger(CONDUCTOR_LOGGER_NAME)

# A convenience tuple of network exceptions that can/should likely be retried by the retry decorator
try:
    CONNECTION_EXCEPTIONS = (
        requests.exceptions.HTTPError,
        requests.exceptions.ConnectionError,
        requests.exceptions.Timeout,
    )
except AttributeError:
    CONNECTION_EXCEPTIONS = (
        requests.HTTPError,
        requests.ConnectionError,
        requests.Timeout,
    )



# TODO: appspot_dot_com_cert = os.path.join(common.base_dir(),'auth','appspot_dot_com_cert2') load
# appspot.com cert into requests lib verify = appspot_dot_com_cert


class ApiClient:
    http_verbs = ["PUT", "POST", "GET", "DELETE", "HEAD", "PATCH"]

    def __init__(self):
        logger.debug("")

    def _make_request(self, verb, conductor_url, headers, params, data, raise_on_error=True):
        response = requests.request(
            method=verb, url=conductor_url, headers=headers, params=params, data=data
        )

        logger.debug("verb: %s", verb)
        logger.debug("conductor_url: %s", conductor_url)
        logger.debug("headers: %s", headers)
        logger.debug("params: %s", params)
        logger.debug("data: %s", data)

        # If we get 300s/400s debug out the response. TODO(lws): REMOVE THIS
        if response.status_code and 300 <= response.status_code < 500:
            logger.debug("*****  ERROR!!  *****")
            logger.debug("Reason: %s" % response.reason)
            logger.debug("Text: %s" % response.text)

        # trigger an exception to be raised for 4XX or 5XX http responses
        if raise_on_error:
            response.raise_for_status()

        return response

    def make_prepared_request(
        self,
        verb,
        url,
        headers=None,
        params=None,
        json=None,
        data=None,
        stream=False,
        remove_headers_list=None,
        raise_on_error=True,
        tries=5,
    ):

        """
        Primarily used to removed enforced headers by requests.Request. Requests 2.x will add
        Transfer-Encoding: chunked with file like object that is 0 bytes, causing s3 failures (501)
        - https://github.com/psf/requests/issues/4215#issuecomment-319521235

        To get around this bug make_prepared_request has functionality to remove the enforced header
        that would occur when using requests.request(...). Requests 3.x resolves this issue, when
        client is built to use Requests 3.x this function can be deprecated.

        args:
            verb: (str) of HTTP verbs
            url: (str) url
            headers: (dict)
            params: (dict)
            json: (dict)
            data: (varies)
            stream: (bool)
            remove_headers_list: list of headers to remove i.e ["Transfer-Encoding"]
            raise_on_error: (bool)
            tries: (int) number of attempts to perform request


        return: request.Response
        """

        req = requests.Request(
            method=verb,
            url=url,
            headers=headers,
            params=params,
            json=json,
            data=data,
        )
        prepped = req.prepare()

        if remove_headers_list:
            for header in remove_headers_list:
                prepped.headers.pop(header, None)

        # Create a retry wrapper function
        retry_wrapper = common.DecRetry(retry_exceptions=CONNECTION_EXCEPTIONS, tries=tries)

        # requests sessions potentially not thread-safe, but need to potentially removed enforced
        # headers by using a prepared request.create which can only be done through an
        # request.Session object. Create Session object per call of make_prepared_request, it will
        # not benefit from connection pooling reuse. https://github.com/psf/requests/issues/1871
        session = requests.Session()

        # wrap the request function with the retry wrapper
        wrapped_func = retry_wrapper(session.send)

        # call the wrapped request function
        response = wrapped_func(prepped, stream=stream)

        logger.debug("verb: %s", prepped.method)
        logger.debug("url: %s", prepped.url)
        logger.debug("headers: %s", prepped.headers)
        logger.debug("params: %s", req.params)

        # trigger an exception to be raised for 4XX or 5XX http responses
        if raise_on_error:
            response.raise_for_status()

        return response

    def make_request(
        self,
        uri_path="/",
        headers=None,
        params=None,
        data=None,
        verb=None,
        conductor_url=None,
        raise_on_error=True,
        tries=5,
        use_api_key=False,
    ):
        """
        verb: PUT, POST, GET, DELETE, HEAD, PATCH
        """
        cfg = config.config().config
        # TODO: set Content Content-Type to json if data arg
        if not headers:
            headers = {"Content-Type": "application/json", "Accept": "application/json"}

        logger.debug("read_conductor_credentials({})".format(use_api_key))
        bearer_token = read_conductor_credentials(use_api_key)
        if not bearer_token:
            raise Exception("Error: Could not get conductor credentials!")

        headers["Authorization"] = "Bearer %s" % bearer_token

        # Construct URL
        if not conductor_url:
            conductor_url = parse.urljoin(cfg["url"], uri_path)

        if not verb:
            if data:
                verb = "POST"
            else:
                verb = "GET"

        assert verb in self.http_verbs, "Invalid http verb: %s" % verb

        # Create a retry wrapper function
        retry_wrapper = common.DecRetry(retry_exceptions=CONNECTION_EXCEPTIONS, tries=tries)

        # wrap the request function with the retry wrapper
        wrapped_func = retry_wrapper(self._make_request)

        # call the wrapped request function
        response = wrapped_func(
            verb, conductor_url, headers, params, data, raise_on_error=raise_on_error
        )

        return response.text, response.status_code


def read_conductor_credentials(use_api_key=False):
    """
    Read the conductor credentials file, if it exists. This will contain a bearer token from either
    the user or the API key (if that's desired). If the credentials file doesn't exist, or is
    expired, or is from a different domain, try and fetch a new one in the API key scenario or
    prompt the user to log in. Args: use_api_key: Whether or not to use the API key

    Returns: A Bearer token in the event of a success or None if things couldn't get figured out

    """
    cfg = config.config().config
    logger.debug("Reading conductor credentials...")
    if use_api_key:
        if not cfg.get("api_key"):
            use_api_key = False
        if use_api_key and not cfg["api_key"].get("client_id"):
            use_api_key = False
    logger.debug("use_api_key = %s" % use_api_key)
    creds_file = get_creds_path(use_api_key)

    logger.debug("Creds file is %s" % creds_file)
    logger.debug("Auth url is %s" % cfg["url"])
    if not os.path.exists(creds_file):
        if use_api_key:
            if not cfg["api_key"]:
                logger.debug("Attempted to use API key, but no api key in in config!")
                return None

            #  Exchange the API key for a bearer token
            logger.debug("Attempting to get API key bearer token")
            get_api_key_bearer_token(creds_file)

        else:
            auth.run(creds_file, cfg["url"])

    if not os.path.exists(creds_file):
        return None

    logger.debug("Reading credentials file...")
    with open(creds_file) as fp:
        file_contents = json.loads(fp.read())

    expiration = file_contents.get("expiration")

    same_domain = creds_same_domain(file_contents)

    if same_domain and expiration and expiration >= int(time.time()):
        return file_contents["access_token"]

    logger.debug("Credentials have expired or are from a different domain")

    if use_api_key:
        logger.debug("Refreshing API key bearer token!")
        get_api_key_bearer_token(creds_file)
    else:
        logger.debug("Sending to auth page...")
        auth.run(creds_file, cfg["url"])

    #  Re-read the creds file, since it has been re-upped
    with open(creds_file) as fp:
        file_contents = json.loads(fp.read())
        return file_contents["access_token"]


def get_api_key_bearer_token(creds_file=None):
    cfg = config.config().config
    url = "{}/api/oauth_jwt".format(cfg["url"])
    response = requests.get(
        url,
        params={
            "grant_type": "client_credentials",
            "scope": "owner admin user",
            "client_id": cfg["api_key"]["client_id"],
            "client_secret": cfg["api_key"]["private_key"],
        },
    )
    if response.status_code == 200:
        response_dict = json.loads(response.text)
        credentials_dict = {
            "access_token": response_dict["access_token"],
            "token_type": "Bearer",
            "expiration": int(time.time()) + int(response_dict["expires_in"]),
            "scope": "user admin owner",
        }

        if not creds_file:
            return credentials_dict

        if not os.path.exists(os.path.dirname(creds_file)):
            os.makedirs(os.path.dirname(creds_file))

        with open(creds_file, "w") as fp:
            fp.write(json.dumps(credentials_dict))
    return


def get_creds_path(api_key=False):

    creds_dir = os.path.join(os.path.expanduser("~"), ".config", "conductor")
    if api_key:
        creds_file = os.path.join(creds_dir, "api_key_credentials")
    else:
        creds_file = os.path.join(creds_dir, "credentials")
    return creds_file


def get_bearer_token(refresh=False):
    """
    Return the bearer token.

    TODO: Thread safe multiproc caching, like it used to be pre-python3.7.
    """
    return read_conductor_credentials(True)


def creds_same_domain(creds):
    cfg = config.config().config
    """Ensure the creds file refers to the domain in config"""
    token = creds.get("access_token")
    if not token:
        return False

    decoded = jwt.decode(creds["access_token"], verify=False)
    audience_domain = decoded.get("aud")
    return (
        audience_domain
        and audience_domain.rpartition("/")[-1] == cfg["api_url"].rpartition("/")[-1]
    )


def account_id_from_jwt(token):
    """
    Fetch the accounts id from a jwt token value.
    """
    payload = jwt.decode(token, verify=False)
    return payload.get("account")


def account_name_from_jwt(token):
    """
    Fetch the accounts name from a jwt token value.
    """
    cfg = config.config().config
    account_id = account_id_from_jwt(token)
    if account_id:
        url = "%s/api/v1/accounts/%s" % (cfg["api_url"], account_id)
        response = requests.get(url, headers={"authorization": "Bearer %s" % token})
        if response.status_code == 200:
            response_dict = json.loads(response.text)
            return response_dict["data"]["name"]
    return None


def request_instance_types(as_dict=False):
    """
    Get the list of available instances types.
    """
    api = ApiClient()
    response, response_code = api.make_request(
        "api/v1/instance-types", use_api_key=True, raise_on_error=False
    )
    if response_code not in (200,):
        msg = "Failed to get instance types"
        msg += "\nError %s ...\n%s" % (response_code, response)
        raise Exception(msg)

    instance_types = json.loads(response).get("data", [])
    logger.debug("Found available instance types: %s", instance_types)

    if as_dict:
        return dict([(instance["description"], instance) for instance in instance_types])
    return instance_types


def request_projects(statuses=("active",)):
    """
    Query Conductor for all client Projects that are in the given state(s)
    """
    api = ApiClient()

    logger.debug("statuses: %s", statuses)

    uri = "api/v1/projects/"

    response, response_code = api.make_request(
        uri_path=uri, verb="GET", raise_on_error=False, use_api_key=True
    )
    logger.debug("response: %s", response)
    logger.debug("response: %s", response_code)
    if response_code not in [200]:
        msg = "Failed to get available projects from Conductor"
        msg += "\nError %s ...\n%s" % (response_code, response)
        raise Exception(msg)
    projects = []

    # Filter for only projects of the proper status
    for project in json.loads(response).get("data") or []:
        if not statuses or project.get("status") in statuses:
            projects.append(project["name"])
    return projects


def request_software_packages():
    """
    Query Conductor for all software packages for the currently available sidecar.
    """
    api = ApiClient()

    uri = "api/v1/ee/packages"
    response, response_code = api.make_request(
        uri_path=uri, verb="GET", raise_on_error=False, use_api_key=True
    )
    print
    if response_code not in [200]:
        msg = "Failed to get software packages for latest sidecar"
        msg += "\nError %s ...\n%s" % (response_code, response)
        raise Exception(msg)
    return json.loads(response).get("data", [])
