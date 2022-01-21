# encoding=utf-8

from abc import abstractmethod
from getpass import getpass, getuser
from os import environ
import re
from threading import RLock
import warnings

from logbook import Logger
import requests
from requests import codes, RequestException
from requests.auth import _basic_auth_str, AuthBase
from requests.sessions import extract_cookies_to_jar

from hansken import envvars
from hansken.util import b64encode, glue_url, omit_empty


log = Logger(__name__)


try:
    from requests_kerberos import HTTPKerberosAuth, OPTIONAL
    kerberos_available = True
except ImportError:
    log.debug('failed to load HTTPKerberosAuth from requests_kerberos, OpenAMKerberosAuth will not be available')
    kerberos_available = False


# namespace for SAML SOAP bindings
SAML_SOAP_NS = 'urn:oasis:names:tc:SAML:2.0:bindings:SOAP'
# mime type of PAOS requests/responses
PAOS_ACCEPT = 'application/vnd.paos+xml'
# value of the PAOS header, declaring versions to be used
PAOS_HEADER = 'ver="urn:liberty:paos:2003-08"; "urn:oasis:names:tc:SAML:2.0:profiles:SSO:ecp"'
# name of the cookie set and expected by OpenAM for authentication
OPENAM_AUTH_COOKIE = 'iPlanetDirectoryPro'


class HanskenAuthError(RequestException):
    """
    Error raised when authentication fails without HTTP error codes in the 400
    or 500 range.
    """
    pass


def encode_header(text, encoding='utf-8', force=False):
    """
    Encodes a text value to RFC 2047 format, using 'b' (base64) encoding if
    the value is not ascii-safe. This can be used to send non-ISO-8859-1
    values as HTTP headers, where the server is expected to support it.

    :param text: the text to be encoded
    :param encoding: text encoding to be used
    :param force: whether to force RFC 2047 format
    :return: *text*, or an RFC 2047 encoded version of it
    """
    if not force:
        try:
            # not forcing encoding, attempt to turn text into ascii (…)
            text.encode('ascii')
            # (…) which works, value is header-safe
            return text
        except UnicodeEncodeError:
            # (…) fall through to actual rfc2047 encoding
            pass

    # decode text into bytes in the requested encoding, then base64-encode those bytes
    payload = b64encode(bytes(text, encoding))
    # encode the whole thing into rfc2047-format (using b/base64 encoding)
    return '=?{charset}?b?{payload}?='.format(charset=encoding, payload=payload)


def get_idps(base_url,
             verify=True):
    """
    Request the list of IDPs from remote, at ``base_url/saml/idps``.

    :param base_url: full url for the Hansken REST API
    :return: `dict` mapping IDP entity ids to the full IDP entry
    """
    idps = requests.get(glue_url(base_url, '/saml', '/idps'),
                        headers={'Accept': 'application/json'},
                        verify=verify)

    if idps.status_code == codes.ok:
        return {idp.get('entityID'): idp for idp in idps.json()}
    elif idps.status_code == codes.not_found:
        # an allinone will simply not know about SAML, responding with a 404
        log.warn('remote does not understand SAML: {}: {}', idps.status_code, idps.reason)
        return {}
    else:
        # only an OK response (empty or not) or a 404 are valid
        raise HanskenAuthError('cannot query remote for SAML IDPs: {}: {}'.format(idps.status_code, idps.reason))


def probe_openam_idp(idp_url,
                     verify=True):
    """
    Probes an OpenAM identity provider to figure out the kind of
    authentication it uses. The realm used for this is first parsed from the
    provided url.

    :param idp_url: full url for the selected identity provider (this ought to
        be the IDP's SOAP endpoint)
    :return: a 2-tuple, *(idp_realm, sso_url)*, both of which can be `None`
    """
    # parse realm from the idp url (the IDP's soap endpoint)
    idp_realm = re.search(r'/SSOSoap/metaAlias(?P<realm>/.+)/idp', idp_url)
    idp_realm = idp_realm.group('realm') if idp_realm else None

    # probe the 'regular' login page to see whether we should be using Kerberos
    probe = glue_url(idp_url[:idp_url.index('/SSOSoap/')], '/UI', '/Login')
    log.info('probing OpenAM login URL {} (realm {})', probe, idp_realm)
    probe = requests.get(probe, params=omit_empty({
        'realm': idp_realm
    }), allow_redirects=False, verify=verify)

    if probe.headers.get('WWW-Authenticate') == 'Negotiate':
        # idp wants us to use Kerberos, construct the info we need
        params = omit_empty({
            'realm': idp_realm,
            'module': 'WindowsDesktopSSO'
        })
        # pre-create the query string for later use, we're passing only the full url
        params = '&'.join('{}={}'.format(*item) for item in sorted(params.items()))
        sso_url = glue_url(idp_url[:idp_url.index('/SSOSoap')], '/UI', '/Login')
        return idp_realm, '{}?{}'.format(sso_url, params)
    else:
        return idp_realm, None


def is_keycloak_idp(url):
    """
    Determines whether the provided IDP URL is a Keycloak URL.

    :param url: the IDP URL to check
    :return: `True` when *url* is a Keycloak URL, `False` when it isn't
    """
    # detect Keycloak as it's endpoint url ending in /protocol/saml
    return url.endswith('/protocol/saml')


def from_env(*args, **kwargs):
    warnings.warn('from_env is deprecated, use resolve', DeprecationWarning)
    return resolve(*args, **kwargs)


def resolve(username=None, password=None, base_url=None, idp_id=None, idp_url=None, idp_realm=None, sso_url=None,
            verify=True, interactive=True):
    """
    Creates a `.HanskenAuthBase` instance of an applicable type, reading
    environment variables ``HANSKEN_ENDPOINT``, ``HANSKEN_IDP``,
    ``HANSKEN_IDP_ENDPOINT``, ``HANSKEN_IDP_REALM`` and
    ``HANSKEN_SSO_ENDPOINT`` before determining the type to be used:

    - only *base URL* specified: query the Hansken REST API for options, auto-
      select IDP only if a single one is available ('automatic mode')
    - both *base URL* and *IDP ID* and specified: resolve from options
      specified by the Hansken REST API, select requested IDP
    - both *IDP URL* and *SSO URL* specified: `.OpenAMKerberosAuth`
    - *IDP URL* and *username* specified: `.OpenAMAuth` or `.KeycloakAuth`

    Automatic mode will fail if multiple IDPs are configured for the remote
    REST API; ``hansken.py`` will not guess which one to use. Should the
    remote not understand SAML (e.g. an all-in-one deployment of Hansken),
    ``hansken.py`` will assume no authentication should be used.

    Supplying *base_url*, *idp_id*, *idp_url*, *idp_realm* or *sso_url* as
    parameters overrides values from
    :ref:`environment variables <environment_vars>`.

    Whenever *username* or *password* are required, values will be prompted if
    not supplied (see `getpass
    <https://docs.python.org/3/library/getpass.html>`_)

    :param username: the username to authenticate as
    :param password: password to be used (omit to have it prompted on the
        command line)
    :param base_url: full url for the Hansken REST API
    :param idp_id: 'name' of the identity provider to select
    :param idp_url: full url for the identity provider
    :param idp_realm: identity provider realm to authenticate to (optional)
    :param sso_url: full url of the single sign-on endpoint of the identity
        provider
    :param interactive: whether to allow user interaction (prompts) to collect
        information needed to create a `.HanskenAuthBase`
    :return: an authentication object (see also `hansken.remote` and
        `hansken.admin`) or `None`
    :rtype: `.HanskenAuthBase`
    :raise HanskenAuthError: when no combination of supplied or environment
        values can be used to construct an authentication object
    """
    base_url = base_url or environ.get(envvars.endpoint)
    idp_id = idp_id or environ.get(envvars.idp)
    idp_url = idp_url or environ.get(envvars.idp_url)
    idp_realm = idp_realm or environ.get(envvars.idp_realm)
    sso_url = sso_url or environ.get(envvars.sso_url)

    log.debug('constructing authentication method from the following provided information: '
              'base_url={base_url}, '
              'idp_id={idp_id}, idp_url={idp_url}, idp_realm={idp_realm}, '
              'sso_url={sso_url}'.format(**locals()))

    idps = get_idps(base_url, verify=verify) if base_url else {}

    if idps and not idp_id:
        if len(idps) == 1:
            # exactly one choice, user did not pre-select one, unpack the single key as the idp_id to be used
            idp_id, = idps.keys()
        else:
            # multiple choices, user did not pre-select one, refuse guessing
            raise HanskenAuthError('{} IDPs available at {}, none requested, choose from {}'.format(
                len(idps),
                base_url,
                ', '.join(sorted(idps.keys()))
            ))

    if idp_id:
        # got an idp to select, find the urls and probe for auth method to use
        idp_url = idps.get(idp_id)
        if not idp_url or 'signOnServices' not in idp_url or SAML_SOAP_NS not in idp_url['signOnServices']:
            raise HanskenAuthError('selected IDP ID {} not available at {}'.format(idp_id, base_url))
        idp_url = idp_url['signOnServices'][SAML_SOAP_NS]
        log.info('selected IDP ID {} with SOAP endpoint {}', idp_id, idp_url)

        if not is_keycloak_idp(idp_url):
            # update values for realm and sso by parsing the url and probing it at the right spot
            idp_realm, sso_url = probe_openam_idp(idp_url, verify=verify)
            # now fall back to code below: construct an auth from the determined / constructed values

    if idp_url and sso_url:
        # both idp and sso available, use OpenAM SAML with Kerberos sso
        log.info('both identity provider and single sign-on urls provided or known, '
                 'using OpenAM SAML at {}, with Kerberos auth at {}', idp_url, sso_url)
        return OpenAMKerberosAuth(idp_url, sso_url, idp_realm=idp_realm)

    if idp_url and not username:
        if not interactive:
            raise HanskenAuthError('no username supplied, value required, interactivity disabled')

        # after the probe, we won't be using Kerberos, but there's also no username (yet)
        log.warn('IDP url known, user+pass auth required but no username supplied')
        env_user = getuser()
        # prompt the user for a username, default to the system username
        username = input('username [{}]: '.format(env_user)).strip()
        if not username:
            # default to system username if input left empty
            username = env_user

        log.info('user acknowledged environment username or supplied custom username: {}', username)

    if username and idp_url:
        # need user/pass without sso
        if callable(username):
            log.debug('provided username is callable, resolving it now')
            username = username()

        if not password:
            if not interactive:
                raise HanskenAuthError('no password supplied, value required, interactivity disabled')
            # even if password is None, we can't run on just a username
            password = getpass('password for user {}: '.format(username))

        if is_keycloak_idp(idp_url):
            # Keycloak url path, user/pass with idp, use Keycloak SAML Basic
            log.info('identity provider url and user+pass provided or known, using Keycloak SAML with Basic auth')
            return KeycloakAuth(username, password, idp_url)
        else:
            # no Keycloak url path, user/pass with idp, use OpenAM SAML REST
            log.info('identity provider url and user+pass provided or known, using OpenAM SAML with OpenAM REST auth')
            return OpenAMAuth(username, password, idp_url, idp_realm=idp_realm)

    if base_url and not idps:
        # a working base_url but no known IDPs makes authentication impossible
        # we have to assume we're dealing with an all-in-one Hansken, which uses no authentication at all
        return None

    # known IDPs, but no idp+sso urls, but also no username, can't create a valid combination
    raise HanskenAuthError('no valid combination of authentication parameters')


class HanskenAuthBase(AuthBase):
    """
    Base class for authentication to Hansken. Registers a handler for the
    response hook on all requests being passed through this auth. Subclasses
    can define response handlers named handle_x, where x is an HTTP status
    code.
    """

    _session = None

    @property
    def session(self):
        """
        Reference to a Session object usable to submit requests needed to
        perform authentication.
        """
        if self._session:
            return self._session

        raise AttributeError('no session available')

    @session.setter
    def session(self, value):
        if value:
            self._session = value
        else:
            # treat any falsy value as a 'reset'
            self._session = None

    def handle_response(self, response, **kwargs):
        """
        Handles a single response, taking action when required. Whether any
        action is required depends on the authentication scheme implemented by
        subclasses (HTTP response status 401 being the most likely case).

        :param response: the response to be handled
        :param kwargs: any keyword arguments
        :return: response, or any equivalent response after handling
                 authentication
        """
        if self._session:
            # the response hook is fired before handling the cookies
            # we need the cookies (session with the gatekeeper, for example), so force the extraction now
            extract_cookies_to_jar(self._session.cookies, response.request, response.raw)

        handler = getattr(self, 'handle_{}'.format(response.status_code), None)
        if callable(handler):
            return handler(response, **kwargs)

        return response

    def __call__(self, request):
        # register a response handle for each and every request
        request.register_hook('response', self.handle_response)
        return request

    def redo_request(self, request, *history):
        """
        Sends *request* using the available session, after replacing its
        ``Cookie`` header with the current state of events. Meant to be used
        for redoing a request that was caught by `.handle_response` after
        handling whatever needed to be handled.

        :param request: a prepared request
        :param history: the history of responses that lead to this point
        :return: the response to *request*, its history extended with
            *history*
        """
        # make sure to put the newly acquired cookies on the original request
        # (prepare_cookies will *only* 'update' Cookie header if we first delete the old one)
        request.headers.pop('Cookie', None)
        request.prepare_cookies(self.session.cookies)

        # work around requests not really supporting 'redoing' a request, merge all of its own stuff into more of its
        # own stuff to be used as kwargs when (re)sending request
        settings = self.session.merge_environment_settings(request.url,
                                                           proxies=self.session.proxies,
                                                           stream=self.session.stream,
                                                           verify=self.session.verify,
                                                           cert=self.session.cert)

        log.debug('resending original {request.method} request to {request.url}', request=request)
        # redo the original request, return its response including all the history we've collected during authentication
        response = self.session.send(request, **settings)
        response.history.extend(history)
        return response


class SAMLProxyAuth(HanskenAuthBase):
    """
    Authentication using username and password, submitted as a POST request to
    a specified endpoint. Endpoint to be passed to constructor or set
    post-init. Will raise HanskenAuthError on failures.
    """

    def __init__(self, username, password, login_url=None):
        # wrap username and password
        self.username = username if callable(username) else lambda: username
        self.password = password if callable(password) else lambda: password
        self.login_url = login_url

        self._lock = RLock()
        self._active = 0

    def __enter__(self):
        self._active += 1
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._active -= 1

    def handle_401(self, response, **kwargs):
        if not self.login_url:
            raise HanskenAuthError('cannot handle {response.status_code}: {response.reason}, '
                                   'no login url available'.format(response=response),
                                   response=response)

        with self._lock, self:
            if self._active > 1:
                raise HanskenAuthError('login failed, got a {response.status_code}: {response.reason} response '
                                       'while handling authentication trigger'.format(response=response),
                                       response=response)

            log.info('submitting credentials to {login}', login=self.login_url)
            auth_response = self.session.post(self.login_url, json={
                # include provided credentials (username and password are always (made) callable)
                'username': self.username(),
                'password': self.password()
            })

            if auth_response.status_code != codes.ok:
                # base error message on original (401) response (which we failed to handle), supply auth failure
                # response
                raise HanskenAuthError('failed to handle {response.status_code}: {response.reason}, '
                                       'login failed'.format(response=response),
                                       response=auth_response)

            # construct a history list for everything we've done
            history = response.history
            history.append(response)
            history.extend(auth_response.history)
            history.append(auth_response)
            # redo original request, pass along the entire history
            return self.redo_request(response.request.copy(), *history)


class SAMLAuthBase(HanskenAuthBase):
    def __init__(self):
        self._active = 0
        self._lock = RLock()

        super().__init__()

    def __enter__(self):
        self._active += 1
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._active -= 1

    def handle_200(self, response, **kwargs):
        # avoid race conditions between handling regular 200 responses and those that are part of the SAML auth
        # self._lock is reentrant, a thread other than the one handling the current auth exchange will be blocked until
        # the auth has been handled (see aldo __call__)
        with self._lock:
            if self._active or not response.headers.get('SOAPAction'):
                # an actual 200 OK or we're currently doing auth, nothing to do / don't do recursive auth
                return response
            else:
                with self:
                    # a reverse saml/soap message, to be handled by implementers
                    saml_response, history = self.handle_paos_request(response)

                    # find out where to push our SAML response
                    # (somewhere on the gatekeeper, but the idp will always provide the full url)
                    response_consumer_url = re.search(r'responseConsumerURL="(?P<url>.+?)"', response.text,
                                                      flags=re.IGNORECASE)
                    response_consumer_url = response_consumer_url.group('url')

                    # post the saml response from the idp back to the response consumer url
                    self.do_saml_response(saml_response, response_consumer_url)

                    # redo the original request, passing any history collected while doing auth
                    return self.redo_request(response.request.copy(), *history)

    @abstractmethod
    def handle_paos_request(self, response):
        """
        Handles a PAOS request received from the Hansken remote, intended to
        be answered by a SAML-capable identity provider. Implementers should
        perform an authenticated SAML message exchange with the identity
        provider, returning the raw SAML response and any history (responses)
        collected on the way, including *response* itself.

        :param response: the response carrying a PAOS request in its content
        :return: a 2-tuple, (*SAML response content*, [*response history*])
        """
        raise NotImplementedError('handle_paos_request should be overridden by implementers')

    def do_saml_response(self, saml_response, response_consumer_url):
        log.debug('posting SAML response back to {sp}', sp=response_consumer_url)
        saml_response = self.session.post(response_consumer_url,
                                          headers={'Content-Type': 'application/vnd.paos+xml'},
                                          data=saml_response,
                                          # following the redirect won't help us a lot, request method is lost
                                          allow_redirects=False)

        if not saml_response.is_redirect:
            # posting the response back to the service provider went wrong, return the failed response
            saml_response.raise_for_status()
            raise HanskenAuthError('got unexpected response {response.status_code}: {response.reason} from SP, '
                                   'expected a redirect'.format(response=saml_response),
                                   response=saml_response)

        return saml_response

    def __call__(self, request):
        # in case there's a SAML exchange in progress, block requests from other sources until auth has been handled
        # self._lock is reentrant, so the active exchange will not be blocked
        with self._lock:
            # extend or set the accept header, make sure we accept PAOS responses, indicative of auth required
            accept = request.headers.get('Accept')
            request.headers['Accept'] = ', '.join([accept, PAOS_ACCEPT] if accept else [PAOS_ACCEPT])
            request.headers['PAOS'] = PAOS_HEADER

            return super().__call__(request)


class OpenAMAuth(SAMLAuthBase):
    """
    Authentication using username and password, submitted to an OpenAM
    identity provider (IDP) as part of a SAML interaction with a service
    provider (SP). Will raise `.HanskenAuthError` on failures.
    """

    def __init__(self, username, password, idp_url, idp_realm=None):
        """
        Creates a new `.HanskenAuthBase` instance using OpenAM REST
        authentication using `username` and `password`. Both of these can be
        `callable`. Plain values are always wrapped in a lambda to obscure the
        values from view in a debugger.

        The URL where the actual authentication takes place is based on the
        value of `idp_url`.

        :param username: username to authenticate with (can be callable)
        :param password: password to authenticate with (can be callable)
        :param idp_url: the URL where OpenAM accepts SAML requests
        :param idp_realm: the realm to authenticate to
        """
        self.username = username if callable(username) else lambda: username
        self.password = password if callable(password) else lambda: password
        self.idp_url = idp_url

        if idp_realm and not idp_realm.startswith('/'):
            # make sure the realm starts with a / if set
            idp_realm = '/{}'.format(idp_realm)

        self.idp_realm = idp_realm

        super().__init__()

    def handle_paos_request(self, response):
        # establish authenticated session with OpenAM
        auth_token = self.get_auth_token()
        # pass the saml request on to the idp (use content to avoid changing the wire encoding)
        saml_response = self.do_saml_request(response.content, auth_token)
        # pass the raw saml response and all the collected history back to super
        return saml_response.content, response.history + [response, saml_response]

    def get_auth_token(self):
        login_url = glue_url(self.idp_url[:self.idp_url.index('/SSOSoap/')], 'json', 'authenticate')
        if self.idp_realm:
            # append the realm to the url (we'll be POSTing data, params would end up in the POST body)
            login_url = '{}?realm={}'.format(login_url, self.idp_realm)

        # attempt auth through OpenAM REST
        user = self.username()

        log.info('authenticating user {user} to realm {realm} using {idp_url}',
                 user=user,
                 realm=self.idp_realm if self.idp_realm else 'default',
                 idp_url=login_url)

        auth_response = self.session.post(login_url, headers={
            # explicitly request a JSON response
            'Accept': 'application/json',
            # include provided credentials, optionally encoded into MIME / rfc2047-format
            'X-OpenAM-Username': encode_header(user),
            'X-OpenAM-Password': encode_header(self.password())
        })

        if auth_response.status_code == codes.ok:
            auth_token = auth_response.json().get('tokenId')
            if auth_token:
                return auth_token

        raise HanskenAuthError('failed to get valid authentication token from OpenAM '
                               '(response {response.status_code}: {response.reason}), '
                               'cannot complete ECP login'.format(response=auth_response))

    def do_saml_request(self, saml_request, auth_token):
        log.debug('posting SAML request to IDP endpoint {idp}', idp=self.idp_url)
        saml_response = self.session.post(self.idp_url,
                                          headers={'Content-Type': 'text/xml',
                                                   'Accept': '*/*'},
                                          cookies={OPENAM_AUTH_COOKIE: auth_token},
                                          data=saml_request)

        if saml_response.status_code != codes.ok:
            # posting the request went wrong, return the failed response
            log.warn('got {response.status_code}: {response.reason} from IDP endpoint {idp}, SAML auth failed',
                     response=saml_response, idp=self.idp_url)
            saml_response.raise_for_status()
            # status is apparently not an error, but we were really expecting a 200 here…
            raise HanskenAuthError('got unexpected response {response.status_code}: {response.reason} from IDP, '
                                   'expected 200: OK'.format(response=saml_response),
                                   response=saml_response)

        return saml_response


class KeycloakAuth(SAMLAuthBase):
    """
    Authentication using username and password, submitted to a Keycloak
    identity provider (IDP) as part of a SAML interaction with a service
    provider (SP). Will raise `.HanskenAuthError` on failures.
    """

    def __init__(self, username, password, idp_url):
        """
        Creates a new `.HanskenAuthBase` instance using Keycloak
        authentication using `username` and `password`. Both of these can be
        `callable`. Plain values are always wrapped in a lambda to obscure the
        values from view in a debugger.

        The URL where the actual authentication takes place is based on the
        value of `idp_url`.

        :param username: username to authenticate with (can be callable)
        :param password: password to authenticate with (can be callable)
        :param idp_url: the URL where Keycloak accepts SAML requests
        """
        self.username = username if callable(username) else lambda: username
        self.password = password if callable(password) else lambda: password
        self.idp_url = idp_url

        super().__init__()

    def handle_paos_request(self, response):
        log.info('posting SAML request with authorization for user {user} to IDP endpoint {idp}',
                 user=self.username(), idp=self.idp_url)
        saml_response = self.session.post(self.idp_url,
                                          headers={'Content-Type': 'text/xml',
                                                   'Accept': '*/*',
                                                   'Authorization': _basic_auth_str(self.username(), self.password())},
                                          data=response.content)

        if saml_response.status_code != codes.ok:
            # posting the request went wrong, return the failed response
            log.warn('got {response.status_code}: {response.reason} from IDP endpoint {idp}, SAML auth failed',
                     response=saml_response, idp=self.idp_url)
            saml_response.raise_for_status()
            # status is apparently not an error, but we were really expecting a 200 here…
            raise HanskenAuthError('got unexpected response {response.status_code}: {response.reason} from IDP, '
                                   'expected 200: OK'.format(response=saml_response),
                                   response=saml_response)

        # provide raw saml response and any gathered history
        return saml_response.content, response.history + [response, saml_response]


if kerberos_available:
    # Use knowledge of the inner workings of HTTPKerberosAuth: when mutual authentication is set to OPTIONAL, we're
    # interested in its implementation of handle_401, handling the HTTP Authentication header for us. All we need to do
    # is submit a request to OpenAM's SSO endpoint, triggering a 401 response with a negotiation request.

    class OpenAMKerberosAuth(OpenAMAuth, HTTPKerberosAuth):
        """
        Authentication using Kerberos, negotiated with OpenAM identity
        provider (IDP) as part of a SAML interaction with a service provider
        (SP). Will raise HanskenAuthError on failures.
        """

        def __init__(self, idp_url, sso_url, idp_realm=None):
            # call constructors for both super classes (super() / MRO not useful here, (kw)arguments differ)
            OpenAMAuth.__init__(self, username=None, password=None, idp_url=idp_url, idp_realm=idp_realm)
            HTTPKerberosAuth.__init__(self, mutual_authentication=OPTIONAL)
            self.sso_url = sso_url

        def get_auth_token(self):
            # no need to take action if there's still a valid cookie
            auth_token = self.session.cookies.get(OPENAM_AUTH_COOKIE)
            if not auth_token:
                # visit the single-sign-on url (don't care about the actual response),
                # trigger a 401 with negotiation (…)
                self.session.get(self.sso_url, headers={'Accept': '*/*'}, allow_redirects=False)
                # (…) resulting in an OpenAM auth cookie in our session
                auth_token = self.session.cookies.get(OPENAM_AUTH_COOKIE)

            return auth_token
else:
    # make sure it's importable, but we can't actually use it…
    def missing_lib(*args, **kwargs):
        raise ImportError('requests_kerberos')

    OpenAMKerberosAuth = missing_lib
