# encoding=utf-8

from collections import namedtuple, OrderedDict
from collections.abc import Collection, Iterable, Mapping, Sequence
from datetime import timedelta
from functools import lru_cache, partial
from io import BufferedReader
from itertools import islice
import os
import re
from urllib.parse import quote
from uuid import UUID
import warnings

from decorator import decorator
from ijson.backends.python import UnexpectedSymbol
from ijson.common import IncompleteJSONError
from iso8601 import parse_date
from logbook import Logger
import requests
from requests import codes
from requests.adapters import HTTPAdapter
from requests.exceptions import ChunkedEncodingError, HTTPError, RequestException
from requests.utils import default_user_agent as requests_user_agent

from hansken import __version__, fetch
from hansken.auth import HanskenAuthError
from hansken.query import Facet, HQLHuman, Query, Range, Sort, to_facet, to_query, to_sort
from hansken.trace import image_from_trace, image_from_uid, Snippet, trace_class_from_model, TraceBuilder, TraceModel
from hansken.util import b64decode, b64encode
from hansken.util import ChunkedIO, DictView, glue_url, json_events, json_items, Namespace, omit_empty, to_property_name

try:
    # 'old' deployments would carry 'old' requests, using a shipped urllib3
    # if this is installed, this would be the types being used
    # (remove when hansken.py depends on requests>=2.16.0)
    from requests.packages.urllib3.exceptions import IncompleteRead, ProtocolError
except ImportError:
    # 'newer' deployments would carry a requests that *depends* on urllib3, requiring a direct import from urllib3
    from urllib3.exceptions import IncompleteRead, ProtocolError


log = Logger(__name__)


# image metadata properties known to be read only
IMAGE_READ_ONLY = ('info', 'states')
# remote's max value for search count (max value for 32-bit signed int)
MAX_RESULTS = (1 << 31) - 1
# error types that are all symptoms of broken search results streams (Hansken will 'print' an error inside JSON content)
# these are recoverable if we track the last successfully read trace uid and submit a new search request using that uid
# as an offset
RECOVERABLE_JSON_STREAM_ERRORS = (
    ChunkedEncodingError,
    IncompleteJSONError,
    IncompleteRead,
    ProtocolError,
    UnexpectedSymbol,
)


def _expect_ok(response, ok=codes.ok, *more):
    """
    Returns response when the response is deemed ok, raises a RequestException
    otherwise (either an HTTPError created by requests or a custom one).

    :param response: the response to check
    :param ok: the response code to be interpreted as ok
    :param more: additional response codes to be interpreted as ok
    :return: response
    """
    expected = (ok,) + more  # create a single tuple of all allowed response codes
    if response.status_code in expected:
        return response

    try:
        response.raise_for_status()
    except HTTPError as e:
        if e.response.text:
            # raise new exception with actual error message from the response
            message = '{}: {}'.format(str(e), e.response.text)
            raise HTTPError(message, response=e.response) from e
        else:
            # no detailed error message, leave the exception in place
            raise

    # requests apparently doesn't think this is worth an HTTPError, but we don't want to let this slide…
    # in order to create a readable error message, join the codes on a comma, but they need to be str for this
    raise RequestException('expected response {}; got {}'.format(', '.join(map(str, expected)), response.status_code),
                           response=response)


def _ensure_binary_io(response, chunk_size=64 << 10):
    """
    Creates a file-like object from *response*, letting requests deal with
    decoding response content, if it claims to be encoded.

    :param response: the response object from which to create a readable
        file-like object
    :param chunk_size: the chunk size to use when content is encoded
    :return: a readable file-like object reading the 'plain' response content
    """
    if 'transfer-encoding' in response.headers or 'content-encoding' in response.headers:
        # avoid handing over the raw file descriptor when the response claims encoded content
        # dealing with the actual content encoding is handled by iter_content
        return ChunkedIO(response.iter_content(chunk_size))
    else:
        # assume raw content
        return response.raw


class drain:  # noqa: N801
    """
    Context manager to make sure a `Response` object is drained of content.
    Can be used to return a connection used to retrieve a response back to the
    connection pool it came from in case the actual response content of the
    response is not needed, e.g.:

    .. code-block:: python

        response = session.get('https://example.com/')

        with drain(response):
            # we're only interested in the status code here and ignore the
            # response content, drain will make sure the content is consumed
            # and the underlying connection can be reused
            return response.status_code == 200
    """

    def __init__(self, response):
        """
        Creates a new draining context manager for *response*.

        :param response: the `Response` to drain on exit
        """
        self.response = response

    def __enter__(self):
        return self.response

    def __exit__(self, exc_type, exc_val, exc_tb):
        # accessing response.content will make sure it is drained
        self.response.content
        return False


def _safe_format(value, default=str):
    """
    Conditionally formats value to default if value is not safe for
    serialization in json.

    :param value: the value to format if unsafe
    :param default: type to coerce value to if not a safe format (default str)
    :return: value or default(value)
    """
    if value is not None and not isinstance(value, (bool, int, float, Sequence, Mapping)):
        # coerce value to the default type
        return default(value)
    return value


def _preference(visibility, key, value, project_id=None):
    """
    Creates dict representing a preference

    :param visibility: visibility;
    :param key: key of the preference
    :param value: value of the preference
    :param project_id: if the visibility is project, id of the project of the preference
    :return:
    """
    preference = {
        'key': _safe_format(key),
        'visibility': _safe_format(visibility),
        'value': _safe_format(value)
    }
    if project_id is not None:
        preference['project'] = _safe_format(project_id)

    return preference


def query_to_dict(query):
    """
    Turns a provided query into a `dict`, performing any wrapping needed.

    :param query: the query to wrap or transform
    :return: a (possibly empty) `dict`
    """
    # make sure query is a dict to be encoded as HQL-JSON
    if isinstance(query, str):
        query = HQLHuman(query)
    if isinstance(query, Query):
        query = query.as_dict()
    if query is None:
        query = {}

    return query


class select_all:  # noqa: N801
    """
    Sentinel value to indicate that all properties should be selected for a
    search call.
    """

    def __repr__(self):
        return '<all>'

    __str__ = __repr__


# turn select_all into an instance of itself for easy comparison
select_all = select_all()


def _quantify_projects(project_selection):
    """
    Selects *project_selection* to be either a singular project, expressed as a `str`,
    or multiple projects, expressed as a collection (`list`, `set`, …).

    :param project_selection: an ambiguous singular or plural project id(s)
    :return: a 2-tuple: *(singular, plural)* one of which is always `None`
    """
    if isinstance(project_selection, (str, UUID)):
        return project_selection, None
    elif isinstance(project_selection, Collection):
        return None, project_selection
    else:
        # avoid confusion down the line, failed to select something meaningful here
        raise TypeError(f'project_selection should be a singular string or multiple strings, got '
                        f'{type(project_selection).__name__}')


class Connection:
    """
    Base remote connection establishing a session with a remote gatekeeper.
    Exposes many calls from the REST API as methods that perform the
    associated HTTP requests. Calls returning JSON-encoded content will
    return the decoded Python equivalent (e.g. `dict`,
    `list`).
    """

    def __init__(self, base_url, keystore_url=None, preference_url=None, auth=None, connection_pool_size=None,
                 verify=True):
        """
        Creates a new connection object facilitating communication to a
        Hansken gatekeeper, tracking session information provided by the
        remote end. Note that the username and password arguments are stored
        on the Connection object for future reuse. The value for password is
        wrapped in a lambda if it is supplied as a plain value. For production
        use, getpass.getpass should be supplied here, causing a non-echoing
        password prompt whenever a password is needed. Note that an
        authenticated session will likely be kept alive if requests are made
        periodically.

        :param base_url: HTTP endpoint to a Hansken gatekeeper (e.g.
            https://hansken.nl/gatekeeper)
        :param keystore_url: HTTP endpoint to a Hansken keystore (e.g.
            https://hansken.nl/keystore)
        :param preference_url: HTTP endpoint to a Hansken preference service (e.g.
            https://hansken.nl/preference)
        :param auth: `HanskenAuthBase <hansken.auth.HanskenAuthBase>` instance
            to handle authentication, or `None`
        :param connection_pool_size: maximum size of HTTP(S) connection pool
        """
        self.base_url = base_url
        self.keystore_url = keystore_url
        self.preference_url = preference_url
        self.auth = auth

        # store often used paths and patterns
        self.path = Namespace(backups='/backups',
                              session='/session',
                              projects='/projects',
                              images='/images',
                              resources='/resources',
                              tools='/tools',
                              keys='/entries',
                              tasks='/tasks',
                              preferences='/preferences',
                              singlefiles='/singlefiles')
        self.pattern = Namespace(
            note_id=re.compile(r'^(?:/[^/]+)*/notes/(?P<note_id>[^/]+)$', re.IGNORECASE),
            image_id=re.compile(r'^(?:/[^/]+)*/images/(?P<image_id>[0-9a-f-]+)$', re.IGNORECASE),
            project_id=re.compile(r'^(?:/[^/]+)*/projects/(?P<project_id>[0-9a-f-]+)$', re.IGNORECASE),
            singlefile_id=re.compile(r'^(?:/[^/]+)*/singlefiles/(?P<singlefile_id>[0-9a-f-]+)$', re.IGNORECASE),
            resource_id=re.compile(r'^(?:/[^/]+)*/resources/(?P<resource_id>[0-9a-f-]+)$', re.IGNORECASE),
            # accept both old /projects and new /tasks Location headers
            extraction_id=re.compile(r'^(?:/[^/]+)*/(?:projects/[0-9a-f-]+/extractions|tasks)'
                                     r'/(?P<extraction_id>[0-9a-f-]+)$', re.IGNORECASE),
            task_id=re.compile(r'^(?:/[^/]+)*/tasks/(?P<task_id>[0-9a-f-]+)$', re.IGNORECASE),
        )

        # create a session to persist cookies we'll get
        self._session = requests.Session()
        # stream responses by default (only needed for a few cases but this makes our lives a lot easier)
        self._session.stream = True
        # use a set of default headers (auth might update this as needed)
        self._session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'User-Agent': 'hansken.py/{} {}'.format(__version__, requests_user_agent()),
        })

        if auth:
            self._session.auth = auth
            auth.session = self._session
            if hasattr(auth, 'login_url'):
                # an auth instance may need a url where *we* know credentials can be posted
                auth.login_url = self.url(self.path.session, '/login')

        if connection_pool_size:
            log.info('overriding default HTTP and HTTPS adapters to pool up to {} connections', connection_pool_size)
            self._session.mount('http://', HTTPAdapter(pool_connections=connection_pool_size,
                                                       pool_maxsize=connection_pool_size))
            self._session.mount('https://', HTTPAdapter(pool_connections=connection_pool_size,
                                                        pool_maxsize=connection_pool_size))

        # override server certificate handling if requested, but be verbose and annoying about it
        if verify is not True:
            # FIXME: Remove this when no longer needed (HANSKENPY-74, won't fix?)
            self._session.verify = verify
            warnings.warn('certificate verification overridden, verify set to {}'.format(verify), RuntimeWarning)

        self._identity = None

        # convenient 'translation table' for refresh header options
        self._refresh = {
            True: 'refresh',
            False: 'no-refresh'
        }

    def open(self):
        """
        Establishes a session with the remote(s). Authentication is assumed to
        be handled by the auth within the session.

        :return: self
        """
        self._identity = self.identity_uid()

        # make sure the identities reported by secondary services match the primary if they require auth
        if self.keystore_url:
            self.match_identity(self.keystore_url)
        if self.preference_url:
            self.match_identity(self.preference_url)

        return self

    def close(self, check_response=True):
        """
        Explicitly ends the session established with the remote(s).

        :param check_response: whether to check the response(s) for the expected
            status code, raising errors on unsuccessful logout(s)
        :return: self
        """
        responses = [self._session.delete(self.url(self.path.session))]

        if self.keystore_url:
            responses.append(self._session.delete(self.key_url(self.path.session)))
        if self.preference_url:
            responses.append(self._session.delete(self.preferences_url(self.path.session)))

        # responses should always be 200, regardless of actual session details
        # accept a 404 too, for services that don't support session management
        if check_response:
            for response in responses:
                _expect_ok(response, codes.ok, codes.not_found)

        # also clear any other session cookies we might have collected
        self._session.cookies.clear_session_cookies()
        return self

    def __enter__(self):
        return self.open()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def url(self, *path):
        """
        Glues parts of a url path to the base url for this connection using
        /s, dropping any steps that are `None`.

        :param path: steps to join to the base url
        :return: a full url
        """
        return glue_url(self.base_url, *path)

    def key_url(self, *path):
        """
        Glues parts of a url path to the keystore url for this connection
        using /s, dropping any steps that are `None`.

        :param path: steps to join to the keystore url
        :return: a full url
        """
        if not self.keystore_url:
            raise ValueError('keystore base url not set')

        return glue_url(self.keystore_url, *path)

    def preferences_url(self, *path):
        """
        Glues parts of a url path to the preference url for this connection
        using /s, dropping any steps that are `None`.

        :param path: steps to join to the preference url
        :return: a full url
        """
        if not self.preference_url:
            raise ValueError('preference base url not set')

        return glue_url(self.preference_url, *path)

    def single_preference_url(self, key, visibility):
        """
        Creates url to retrieve/update/delete a single specific preference

        :param visibility: visibility of the preference
        :param key: key indicating the preference
        :return: a full url
        """
        # split key on first dot
        key_parts = key.replace('.', '/')
        return self.preferences_url(self.path.preferences, visibility, key_parts)

    def version(self):
        """
        Retrieves the version info reported by the remote.

        :return: a dict with keys ``build`` and ``timestamp``
        """
        response = self._session.get(self.url('version'))
        return _expect_ok(response).json()

    def current_user(self):
        """
        Retrieves information on the current user from the remote.

        :return: a `dict` with information and identifiers for the current user
        """
        response = self._session.get(self.url(self.path.session, '/whoami'))
        return _expect_ok(response).json()

    @property
    def identity(self):
        """
        The current user's identity for the current session.

        :return: the currently available user identity of the form
            <user>@<domain>
        """
        if self._identity is None:
            self._identity = self.identity_uid()

        return self._identity

    def _require_identity(self, identity=None):
        """
        Returns passed identity or self.identity. Raises ValueError when
        neither is available.

        :param identity: an identity or `None`
        :return: identity or self.identity
        """
        if identity is None:
            identity = self.identity
        if not identity:
            raise ValueError('no identity available')

        return identity

    def identity_uid_at(self, service_url):
        response = self._session.get(glue_url(service_url, self.path.session, '/whoami'))
        response = _expect_ok(response).json()
        # retrieve the uid version of the identity, formatted as <user>@<domain>
        # expect this to always be available
        return response['uid']

    def identity_uid(self):
        """
        Retrieves the current user's identity as seen by the remote
        gatekeeper.

        :return: uid of the form <user>@<domain>
        """
        return self.identity_uid_at(self.base_url)

    def match_identity(self, service_url):
        idps = self._session.get(glue_url(service_url, '/saml', '/idps'))
        if idps.status_code == 200:
            service_identity = self.identity_uid_at(service_url)
            if service_identity != self.identity:
                raise HanskenAuthError('mismatched identities ({} != {}) for base and service at {}'.format(
                    service_identity, self.identity,
                    service_url
                ))
        elif idps.status_code == 404:
            log.info('not matching identity to service at {}, does not seem to support authentication', service_url)
        else:
            raise HanskenAuthError('unable to determine authentication support for service at {}'.format(service_url))

    def key(self, image_id, identity=None, raise_on_not_found=True):
        """
        Retrieves the key for an image with the provided id, using the
        provided identity or that of the current user.

        .. warning::
            ``hansken.py`` cannot distinguish between an image not needing a
            key and a user that is not authorized to retrieve data from an
            image. In both cases, the remote key service would respond with a
            an error that is propagated to the caller be default. Internal uses
            of this method will typically set *raise_on_not_found* to `False`,
            potentially delaying errors to the point of (unauthorized) data
            access.

            See also `.fetch`.

        :param image_id: the image to retrieve the key for
        :param identity: the identity to retrieve the key for, defaults to the
            identity of the current user
        :param raise_on_not_found: if `False`, return `None` when no key is
            available for *(image_id, identity)*, otherwise raise an
            `HTTPError` like any other request
        :return: a key for image *image_id*
        :rtype: `bytes`
        """
        identity = self._require_identity(identity)
        response = self._session.get(self.key_url(self.path.keys, image_id, identity),
                                     headers={'Accept': 'text/plain'})  # override expected response for this request
        try:
            response = _expect_ok(response).text
            return b64decode(response)
        except RequestException as e:
            if e.response.status_code == codes.not_found and not raise_on_not_found:
                # got a 404, but we're requested to not raise, default to None
                log.warn('no key for ({}, {}) available, defaulting to None', image_id, identity)
                return None
            else:
                # raise original error
                raise

    def _maybe_fetch_key(self, image_id=None, key=None):
        if key is not fetch:
            # only take action if key *is* fetch
            return key

        log.debug('auto-fetching key for image {}', image_id)
        # make sure to not raise an error on 404, return either a key or None
        return self.key(image_id=image_id, raise_on_not_found=False)

    def store_key(self, image_id, key, identity=None):
        """
        Stores the key for an image, using the provided or current user's
        identity.

        :param image_id: the image to store the key for
        :param key: the (binary) key content
        :param identity: the identity to store the key for, defaults to the
            identity of the current user
        :return: True on success (failure will likely result in an HTTPError)
        """
        identity = self._require_identity(identity)
        response = self._session.post(self.key_url(self.path.keys, image_id, identity),
                                      headers={'Content-Type': 'text/plain'},  # override content-type for this request
                                      data=b64encode(key))
        with drain(response):
            return _expect_ok(response, ok=codes.created) is response

    def delete_key(self, image_id, identity=None):
        """
        Deletes the key for an image, using the provided or current user's
        identity.

        :param image_id: the image to delete the key for
        :param identity: the identity to delete the key for, defaults to the
            identity of the current user
        :return: True on success (failure will likely result in an HTTPError)
        """
        identity = self._require_identity(identity)
        response = self._session.delete(self.key_url(self.path.keys, image_id, identity))
        with drain(response):
            return _expect_ok(response) is response

    def preference(self, key, visibility='preferred', project_id=None):
        """
        Retrieves a preference. Requires a project id if the visibility is set to project

        :param key: key to identify the preference
        :param visibility: visibility of the preference. Can be either one of public, private, project or preferred
        :param project_id: id of the project if the preference has project wide visibility
        :return: the preference
        """
        response = self._session.get(self.single_preference_url(key, visibility),
                                     params=omit_empty({'projectId': project_id}))
        return _expect_ok(response).json()

    def preferences(self, visibility='preferred', project_id=None):
        """
        Retrieves list of preferences with the given visibility. Requires a project id if the visibility is set to
        project

        :param visibility: visibility of the preference. Can be either one of public, private, project or preferred
        :param project_id: id of the project. Required for when visibility is set to project
        :return: list of preferences
        """
        response = self._session.get(self.preferences_url(self.path.preferences),
                                     params=omit_empty({'visibility': visibility, 'projectId': project_id}))
        return _expect_ok(response).json()

    def create_preference(self, key, visibility, value, project_id=None):
        """
        Creates a new preference. Requires a project id if the visibility is set to project

        :param key: key to identify the preference
        :param visibility: visibility of the preference. Can be either one of public, private or project
        :param value: value of the preference
        :param project_id: id of the project if the preference has project wide visibility
        :return: True on success (failure will likely result in an HTTPError)
        """
        response = self._session.post(self.preferences_url(self.path.preferences),
                                      json=_preference(visibility, key, value, project_id))
        with drain(response):
            return _expect_ok(response, ok=codes.created) is response

    def edit_preference(self, key, visibility, value, project_id=None):
        """
        Edits an existing preference by updating its value. Requires a project id if the visibility is set to project

        :param key: key to identify the preference
        :param visibility: visibility of the preference. Can be either one of public, private or project
        :param value: new value of the preference
        :param project_id: id of the project if the preference has project wide visibility
        :return: True on success (failure will likely result in an HTTPError)
        """
        response = self._session.put(self.single_preference_url(key, visibility),
                                     params=omit_empty({'projectId': project_id}),
                                     json=_preference(visibility, key, value, project_id))
        with drain(response):
            return _expect_ok(response) is response

    def delete_preference(self, key, visibility, project_id=None):
        """
        Deletes an existing preference. Requires a project id if the visibility is set to project

        :param key: key to identify the preference
        :param visibility: visibility of the preference. Can be either one of public, private or project
        :param project_id: id of the project if the preference has project wide visibility
        :return: True on success (failure will likely result in an HTTPError)
        """
        response = self._session.delete(self.single_preference_url(key, visibility),
                                        params=omit_empty({'projectId': project_id}))
        with drain(response):
            return _expect_ok(response) is response

    def projects(self):
        response = self._session.get(self.url(self.path.projects))
        return _expect_ok(response).json()

    def project(self, project_id):
        response = self._session.get(self.url(self.path.projects, project_id))
        return _expect_ok(response).json()

    def activate_project(self, project_id):
        response = self._session.post(self.url(self.path.projects, project_id, '/open'))
        with drain(response):
            # response should be 200 when project was already open or was opened successfully
            _expect_ok(response)

    def deactivate_project(self, project_id):
        response = self._session.post(self.url(self.path.projects, project_id, '/close'))
        with drain(response):
            # response should be 200 when project was already closed or was closed successfully
            _expect_ok(response)

    def project_images(self, project_id):
        response = self._session.get(self.url(self.path.projects, project_id, '/images'))
        return _expect_ok(response).json()

    def create_project(self, **kwargs):
        """
        Creates a new meta project. The new project's properties are taken
        from kwargs, and translated to Hansken property names (camelCased).
        Specifying the new image's id is allowed.

        :param kwargs: metadata properties for the new project
        :return: the new project's identifier (a str(UUID))
        """
        project = omit_empty({to_property_name(key): _safe_format(kwargs[key]) for key in kwargs})
        # POST the new project to remote, expect 201 response (Created)
        response = self._session.post(self.url(self.path.projects), json=project)
        with drain(response):
            response = _expect_ok(response, ok=codes.created)
            # response will provide the uri for the new project in the Location header, we want only the uuid
            # default to empty string in case no Location header was supplied
            project = response.headers.get('Location', '')
            project = re.match(self.pattern.project_id, project)
            if project:
                return project.group('project_id').lower()
            else:
                raise ValueError('no project id in response header Location: {}'.format(
                    response.headers.get('Location')
                ))

    def edit_project(self, project_id, **kwargs):
        # user is responsible for handing *all* required data here (including id and name)
        project = {to_property_name(key): _safe_format(kwargs[key]) for key in kwargs}
        response = self._session.put(self.url(self.path.projects, project_id), json=project)
        with drain(response):
            _expect_ok(response)

    def delete_project(self, project_id, delete_images=False, delete_preferences=False):
        """
        Deletes a meta project. Note that this will also remove a project's
        search index and preferences.

        :param project_id: project to be deleted
        :param delete_images: whether to also delete the images linked to the
            project
        :param delete_preferences: whether to also delete the preferences linked
            project. This is the evidence container for example.
        :return: a success-value, whether the deletion of the project and all
            images (if requested) has succeeded (see log output for errors)
        """
        # collect project images before deleting the project (can't be collected when the project has been deleted)
        project_images = self.project_images(project_id) if delete_images else []

        response = self._session.delete(self.url(self.path.projects, project_id))
        with drain(response):
            _expect_ok(response)
            success = True

        if delete_images:
            for image in project_images:
                try:
                    self.delete_image(image['id'])
                except HTTPError as e:
                    log.warn('failed to delete image {}: {}', image['id'], e.response.text)
                    success = False

        # Collect project specific preferences, these can still be collected, even when the
        # project is already deleted.
        project_preferences = self.preferences('project', project_id) if delete_preferences else []
        for preference in project_preferences:
            try:
                self.delete_preference(preference['key'], 'project', project_id)
            except HTTPError as e:
                log.warn('failed to delete preference {}: {}', preference['key'], e.response.text)
                success = False

        return success

    def clone_project(self, source_id, target_id, filter=None, exclude=None):
        """
        Clones traces of a project identified by *source_id* to a project
        *target_id*. When *filter* (a query) is provided, only traces
        matching the filter are copied.

        :param source_id: project to copy traces from
        :param target_id: project to copy traces to
        :param filter: query to define what traces to copy
        :param exclude: properties to be excluded from the clone (not all
            properties are supported for this, supplying an unsupported
            property here will cause errors)
        """
        response = self._session.post(self.url(self.path.projects, source_id, 'clone'), json=omit_empty({
            'targetProjectId': target_id,
            'filter': query_to_dict(filter),
            'exclude': list(exclude) if exclude else None,
        }))
        with drain(response):
            response = _expect_ok(response, codes.created, codes.accepted)
            # response will provide the uri for the created / scheduled task in the Location header, we want on the uuid
            # default to empty string in case no Location header was supplied
            task = response.headers.get('Location', '')
            task = re.match(self.pattern.task_id, task)
            if task:
                return task.group('task_id').lower()
            else:
                raise ValueError('no task id in response header Location: {}'.format(
                    response.headers.get('Location')
                ))

    def link_image(self, project_id, image_id):
        response = self._session.put(self.url(self.path.projects, project_id, 'images', image_id))
        with drain(response):
            _expect_ok(response)

    def unlink_image(self, project_id, image_id):
        response = self._session.delete(self.url(self.path.projects, project_id, 'images', image_id))
        with drain(response):
            _expect_ok(response)

    def image(self, image_id, project_id=None):
        if project_id and image_id:
            # retrieving a single image *within a project* is allowed, requires a different url
            # NB: this will often yield a similar result (other than an image's states), but the calls require a
            #     different permission, making this path suitable for mortal users and a ProjectContext
            response = self._session.get(self.url(self.path.projects, project_id, '/images', image_id))
        else:
            response = self._session.get(self.url(self.path.images, image_id))

        return _expect_ok(response).json()

    def create_image(self, **kwargs):
        """
        Creates a new meta image. The new image's properties are taken from
        kwargs, and translated to Hansken property names (camelCased).
        Specifying the new image's id is allowed. Property user defaults to
        the current session's identity, overrides are accepted.

        :param kwargs: metadata properties for the new image
        :return: the new image's identifier (a str(UUID))
        """
        # default user to the current session's identity, allow override from kwargs
        image = {'user': kwargs.pop('user', None) or self.identity}
        image.update({to_property_name(key): _safe_format(kwargs[key]) for key in kwargs if key not in IMAGE_READ_ONLY})
        image = omit_empty(image)

        # POST the new image to remote, expect 201 response (Created)
        response = self._session.post(self.url(self.path.images), json=image)
        with drain(response):
            response = _expect_ok(response, ok=codes.created)
            # response will provide the uri for the new image in the Location header, we want only the uuid
            # default to empty string in case no Location header was supplied
            image = response.headers.get('Location', '')
            image = re.match(self.pattern.image_id, image)
            if image:
                return image.group('image_id').lower()
            else:
                raise ValueError('no image id in response header Location: {}'.format(
                    response.headers.get('Location')
                ))

    def edit_image(self, image_id, **kwargs):
        # user is responsible for handing *all* required data here (including id and user)
        image = {to_property_name(key): _safe_format(kwargs[key]) for key in kwargs if key not in IMAGE_READ_ONLY}
        response = self._session.put(self.url(self.path.images, image_id), json=image)
        with drain(response):
            _expect_ok(response)

    def delete_image(self, image_id):
        response = self._session.delete(self.url(self.path.images, image_id))
        with drain(response):
            _expect_ok(response)

    def images(self, **kwargs):
        # basically an image search, matching image properties to kwargs
        response = self._session.get(self.url(self.path.images), params=kwargs)
        return _expect_ok(response).json()

    def trace_model(self, project_id=None):
        # construct trace model url path; should contain be prepended with
        # /project/{project_id} if project_id is provided
        path = ['/tracemodel']
        if project_id:
            path = [self.path.projects, project_id] + path

        # use constructed path as vararg to url
        response = self._session.get(self.url(*path))
        return _expect_ok(response).json()

    def trace(self, project_id, trace_uid):
        response = self._session.get(self.url(self.path.projects, project_id, '/traces', trace_uid))
        return _expect_ok(response).json()

    def data(self, project_id, trace_uid, stream='raw', offset=0, size=None, key=fetch, bufsize=8 << 10):
        """
        Opens a streaming read request that provides the requested data stream
        of a particular trace. Note that this provides a stream that should be
        closed by the user after use.

        :param project_id: the project to associate the request with
        :param trace_uid: the trace identifier to read from
        :param stream: the stream to read (e.g. raw, plain, html)
        :param offset: the offset within the data stream
        :param size: the amount of data to provide
        :param key: the key data to be used to decrypt data, must be either
            `fetch`, `None` or binary (`bytes`)
        :param bufsize: the network buffer size
        :return: a closable file-like object
        :rtype: `io.BufferedReader`
        """
        # omit empty params to avoid confusing the gatekeeper
        params = omit_empty({
            'dataType': stream,
        })

        brange = None
        if offset or size:
            # we'll need a byte range
            # formatted as 1234- when size is not specified
            # formatted as 1234-5678 when it is
            brange = 'bytes={}-{}'.format(offset,
                                          '' if size is None else offset + size - 1)  # HTTP/1.1 range is inclusive

        key = self._maybe_fetch_key(image_id=image_from_uid(trace_uid), key=key)
        headers = omit_empty({
            'Accept': 'application/octet-stream',  # override requested response type
            'Range': brange,
            # always base64-encoded the key if provided, assume binary
            'Hansken-Image-Key': b64encode(key) if key else None,
        })

        response = self._session.get(self.url(self.path.projects, project_id, '/traces', trace_uid, '/data'),
                                     params=params,
                                     headers=headers)
        # expect either response code 200 (OK) or 206 (Partial Content)
        response = _expect_ok(response, codes.ok, codes.partial)
        # wrap a content generator with something implementing readinto to make things seem like a byte stream
        # iter_content will make sure to close the underlying connection after reading the last chunk
        return BufferedReader(ChunkedIO(response.iter_content(bufsize)))

    def create_resource(self, *, data, **kwargs):
        """
        Creates a Hansken resource in two stages, registering the resource
        metadata before uploading the corresponding data.

        .. note::
            Required parameters for a resources are not validated by
            ``hansken.py``. Missing parameters like *group*, *name* or
            *version* will likely result in `HTTPError` exceptions.

        :param data: data blob (either *bytes* or a *file-like object*) to be
            stored (the actual resource)
        :param kwargs: the resource meta data associated with *data*
        :return: the id of the newly created resource
        """
        # create a resource object from the supplied keywords, translating them to the Hansken naming scheme
        resource = omit_empty({to_property_name(key): _safe_format(value)
                               for key, value in kwargs.items()})

        response = self._session.post(self.url(self.path.resources), json=resource)

        with drain(response):
            # find the id for the newly created resource object from the response
            response = _expect_ok(response, ok=codes.created)
            resource_id = response.headers.get('Location', '')
            resource_id = re.match(self.pattern.resource_id, resource_id)
            if resource_id:
                resource_id = resource_id.group('resource_id').lower()
            else:
                raise ValueError('no resource id in response header Location: {}'.format(
                    response.headers.get('Location')
                ))

        # post the resource' data blob to the created resource id
        response = self._session.post(self.url(self.path.resources, resource_id, '/upload'),
                                      data=data)
        with drain(response):
            _expect_ok(response, ok=codes.created)

        return resource_id

    def edit_resource(self, resource_id, *, visibility):
        response = self._session.post(self.url(self.path.resources, resource_id, visibility))
        with drain(response):
            return _expect_ok(response) is response

    def delete_resource(self, resource_id):
        response = self._session.delete(self.url(self.path.resources, resource_id))
        with drain(response):
            return _expect_ok(response) is response

    def resources(self, **kwargs):
        """
        List available resources, optionally filtering by provided properties
        supplied as keyword arguments.

        :param kwargs: properties to filter for (e.g.
            ``group='nl.nfi.example'``)
        :return: `list` of resources matching *kwargs*
        """
        response = self._session.get(self.url(self.path.resources),
                                     # translate properties to Hansken naming scheme
                                     params={to_property_name(key): _safe_format(value)
                                             for key, value in kwargs.items()})
        return _expect_ok(response).json()

    def snippets(self, project_id, *snippets):
        response = self._session.post(self.url(self.path.projects, project_id, '/snippets'), json=snippets)
        return _expect_ok(response).json()

    def roots(self, project_id):
        response = self._session.get(self.url(self.path.projects, project_id, '/traces/roots'))
        return _expect_ok(response).json()

    def children(self, project_id, trace_uid, query=None, start=0, count=None, sort=None, facets=None,
                 snippets=None, select=select_all, incomplete_results=None, timeout=None):
        """
        Searches the children of a trace.

        :param project_id: id of the project to search in
        :param trace_uid: id of the trace retrieve children for
        :param query: query to apply on the children of trace_uid (default:
            retrieve all children)
        :param start: the start offset to be included
        :param count: max number of children to be retrieved
        :param sort: sort clause(s) of the form ``score-``, ``some.field``
        :param facets: facet(s) to be used for search (`str`,
            :py:class:`Facet <hansken.query.Facet>` or sequence of either)
        :param snippets: maximum number of snippets to return per trace
        :param select: property selector(s), defaults to all properties
        :param incomplete_results: whether to allow results from an incomplete
            index (defaults to letting the remote decide)
        :param timeout: the maximum amount of time to wait for a search
            response, in seconds or as a `datetime.timedelta` (defaults to
            letting the remote decide), set to 0 to disable timeout
        :return: a file-like object, streaming the raw json response from
            remote
        """
        search_request = self.create_search_request(query=query, start=start, count=count, sort=sort, facets=facets,
                                                    snippets=snippets, select=select,
                                                    incomplete_results=incomplete_results, timeout=timeout)
        response = self._session.post(
            self.url(self.path.projects, project_id, '/traces', trace_uid, '/children', '/search'),
            json=search_request)
        # make sure to return a readable file-like object for the 'plain' response
        return _ensure_binary_io(_expect_ok(response))

    def note(self, project_id, trace_uid, note, refresh=None):
        headers = omit_empty({
            'Hansken-Project-Refresh': self._refresh.get(refresh)
        })
        response = self._session.post(self.url(self.path.projects, project_id, '/traces', trace_uid, '/notes'),
                                      json={'text': note},
                                      headers=headers)
        with drain(response):
            response = _expect_ok(response, codes.created)
            # read the generated note id from the Location header
            note = response.headers.get('Location', '')
            note = re.match(self.pattern.note_id, note)
            if note:
                return note.group('note_id')
            else:
                raise ValueError('no note id in response header Location: {}'.format(response.headers.get('Location')))

    def tag(self, project_id, trace_uid, tag, refresh=None):
        headers = omit_empty({
            'Hansken-Project-Refresh': self._refresh.get(refresh)
        })
        response = self._session.put(self.url(self.path.projects, project_id, '/traces', trace_uid, '/tags',
                                              quote(tag, '')), headers=headers)
        with drain(response):
            return _expect_ok(response) is response

    def delete_tag(self, project_id, trace_uid, tag, refresh=None):
        headers = omit_empty({
            'Hansken-Project-Refresh': self._refresh.get(refresh)
        })
        response = self._session.delete(self.url(self.path.projects, project_id, '/traces', trace_uid, '/tags',
                                                 quote(tag, '')), headers=headers)
        with drain(response):
            return _expect_ok(response) is response

    def mark_privileged(self, project_id, trace_uid, status, refresh=None):
        headers = omit_empty({
            'Hansken-Project-Refresh': self._refresh.get(refresh)
        })
        # use str(status) to convert status to its name
        response = self._session.put(
            self.url(self.path.projects, project_id, '/traces', trace_uid, '/privileged', str(status)),
            headers=headers
        )
        with drain(response):
            return _expect_ok(response) is response

    def import_trace(self, project_id, trace, data=None, key=fetch, method='heuristic', properties=None,
                     overwrite=False):
        """
        Imports the requested *properties* on *trace* into a trace in *project*.

        :param project_id: the project to import *trace* into
        :param trace: the trace to be imported
        :param data: a `dict` mapping data type / stream name to bytes to be
            imported
        :param key: the key data for image *trace* belongs to, must be
            `fetch`, `None` or binary (`bytes`)
        :param method: a method to match *trace* to an existing trace in
            *project*, either ``'strict'`` or ``'heuristic'``
        :param properties: the properties to be imported
        :param overwrite: whether properties to be imported should be
            overwritten if already present
        :return: a response object encoding the import result, detailing what
            trace the imported trace was matched to and what properties were
            imported
        """
        if not properties and isinstance(trace, TraceBuilder):
            # trace was updated using a builder, take the properties to be imported from builder
            properties = trace.updates

        if isinstance(trace, DictView):
            # not interested in the view object, use the raw source dict
            trace = trace._source

        # default properties to anything annotated
        properties = properties or ('annotated.*',)

        if data:
            # prepare actual data for wire transport
            data = {name: b64encode(content) for name, content in data.items()}

        if key is fetch:
            # auto-fetch key if there's data to be imported and key is not provided
            key = self._maybe_fetch_key(image_from_trace(trace), key=key) if data else None

        response = self._session.post(
            self.url(self.path.projects, project_id, 'import'),
            headers=omit_empty({'Hansken-Image-Key': b64encode(key) if key else None}),
            json=omit_empty({'method': method,
                             'overwrite': overwrite,
                             'trace': trace,
                             'properties': properties,
                             'data': data})
        )
        return _expect_ok(response).json()

    def create_trace(self, project_id, parent_uid, child, data=None, key=fetch):
        """
        Requests a new trace to be indexed as a child trace of an existing
        trace.

        :param project_id: id of the project to index the trace into
        :param parent_uid: the trace uid of the trace to attach the new child
            to
        :param child: the new trace to be indexed
        :param data: a `dict` mapping data type / stream name to bytes to be
            attached to the new trace
        :param key: the key data for image *parent_uid* and thus *child* belong
            to
        :return: the id of the newly created trace
        """
        if isinstance(child, DictView):
            # not interested in the view object, use the raw source dict
            child = child._source

        if data:
            # prepare actual data for wire transport
            data = {name: b64encode(content) for name, content in data.items()}

        if key is fetch:
            # auto-fetch key if there's data to be imported and key is not provided
            key = self._maybe_fetch_key(image_from_uid(parent_uid), key=key) if data else None

        response = self._session.post(
            self.url(self.path.projects, project_id, 'import'),
            headers=omit_empty({'Hansken-Image-Key': b64encode(key) if key else None}),
            json={'method': 'strict',
                  'trace': {'uid': parent_uid},
                  # add the singular child to be created as the only element of the children to be imported
                  'children': [
                      omit_empty({'trace': child, 'data': data})
                  ]}
        )

        response = _expect_ok(response).json()
        # retrieve children in the import response to find the newly generated uid
        children = DictView(response)
        children = children.get('imported.children')
        if not children or 'uid' not in children[0]:
            raise ValueError('no child uid in import response')
        # return the uid of the new trace
        return children[0]['uid']

    def search(self, project_id, query=None, start=0, count=None, sort=None, facets=None, snippets=None,
               select=select_all, incomplete_results=None, timeout=None):
        """
        Performs a search request built from the parameters.

        :param project_id: id of the project to search in
        :param query: the query to submit
        :param start: the start offset to be included
        :param count: max number of traces to be retrieved
        :param sort: sort clause(s) of the form ``score-``, ``some.field``
        :param facets: facet(s) to be used for search (`str`,
            :py:class:`Facet <hansken.query.Facet>` or sequence of either)
        :param snippets: maximum number of snippets to return per trace
        :param select: property selector(s), defaults to all properties
        :param incomplete_results: whether to allow results from an incomplete
            index (defaults to letting the remote decide, which will typically
            *not* allow results from an incomplete index)
        :param timeout: the maximum amount of time to wait for a search
            response, in seconds or as a `datetime.timedelta` (defaults to
            letting the remote decide), set to 0 to disable timeout
        :return: a file-like object, streaming the raw json response from
                 remote
        """
        single_project, multiple_projects = _quantify_projects(project_id)

        search_request = self.create_search_request(query=query, start=start, count=count, sort=sort, facets=facets,
                                                    snippets=snippets, project_ids=multiple_projects, select=select,
                                                    incomplete_results=incomplete_results, timeout=timeout)
        # single_project will either be a project id or None (in which case the step is left out of the url)
        response = self._session.post(self.url(self.path.projects, single_project, '/search'),
                                      json=search_request)
        # make sure to return a readable file-like object for the 'plain' response
        return _ensure_binary_io(_expect_ok(response))

    def search_tracelets(self, project_id, tracelet_type, query=None, start=0, count=None, sort='id', select=select_all,
                         incomplete_results=None, timeout=None):
        """
        Performs a search request for tracelets built from the parameters.

        :param project_id: id of the project to search in
        :param tracelet_type: the type of tracelet to search for
        :param query: the query to submit
        :param start: the start offset to be included
        :param count: max number of traces to be retrieved
        :param sort: sort clause(s) of the form ``score-``, ``some.field``,
            defaults to sorting on ``id``
        :param select: property selector(s), defaults to all properties
        :param incomplete_results: whether to allow results from an incomplete
            index (defaults to letting the remote decide, which will typically
            *not* allow results from an incomplete index)
        :param timeout: the maximum amount of time to wait for a search
            response, in seconds or as a `datetime.timedelta` (defaults to
            letting the remote decide), set to 0 to disable timeout
        :return: a file-like object, streaming the raw json response from
                 remote
        """
        single_project, multiple_projects = _quantify_projects(project_id)

        search_request = self.create_search_request(query=query, start=start, count=count, sort=sort,
                                                    tracelet_type=tracelet_type, project_ids=multiple_projects,
                                                    select=select, incomplete_results=incomplete_results,
                                                    timeout=timeout)
        # single_project will either be a project id or None (in which case the step is left out of the url)
        response = self._session.post(self.url(self.path.projects, single_project, '/tracelets', '/search'),
                                      json=search_request)
        # make sure to return a readable file-like object for the 'plain' response
        return _ensure_binary_io(_expect_ok(response))

    def unique_values(self, project_id, select, query=None, after=None, count=None, incomplete_results=None,
                      timeout=None):
        single_project, multiple_projects = _quantify_projects(project_id)

        # make sure to turn select into a sequence if it's not already
        if isinstance(select, str):
            select = [select]

        # only set to max on None, 0 is valid
        if count is None:
            count = MAX_RESULTS

        if isinstance(timeout, timedelta):
            timeout = timeout.total_seconds()

        search_request = omit_empty({
            'select': select,
            'query': query_to_dict(query),
            'projectIds': sorted(multiple_projects) if multiple_projects else None,
            'after': after,
            'count': count,
            'incompleteResults': incomplete_results,
            'timeout': timeout,
        })

        # single_project will either be a project id or None (in which case the step is left out of the url)
        response = self._session.post(self.url(self.path.projects, single_project, '/values', '/search'),
                                      json=search_request)
        # make sure to return a readable file-like object for the 'plain' response
        return _ensure_binary_io(_expect_ok(response))

    def create_search_request(self, query=None, *,
                              start=0, count=None, sort=None, facets=None, snippets=None, tracelet_type=None,
                              project_ids=None, select=select_all, incomplete_results=None, timeout=None):
        """
        Creates a search request from the parameters, transforming parameters
        when needed.

        :param query: the query to submit
        :param start: the start offset to be included
        :param count: max number of traces to be included
        :param sort: sort clause(s) of the form ``score-``, ``some.field`` or
            instance(s) of `.Sort`
        :param facets: facet(s) to be used for search (`str`,
            :py:class:`Facet <hansken.query.Facet>` or sequence of either)
        :param snippets: maximum number of snippets to return per trace
        :param tracelet_type: the type of tracelet to search for (only
            applicable to tracelet searches)
        :param project_ids: a collection of project ids to pass this search
            request to, or `None`
        :param select: property selector(s), defaults to all properties
        :param incomplete_results: whether to allow results from an incomplete
            index (defaults to letting the remote decide)
        :param timeout: the maximum amount of time to wait for a search
            response, in seconds or as a `datetime.timedelta` (defaults to
            letting the remote decide), set to 0 to disable timeout
        """
        # force query to be a dict (directly passing a mapping has a use case, avoid hansken.query.to_query here)
        query = query_to_dict(query)

        # translate sort clause variants to Sort objects
        if sort is None:
            sort = []
        if isinstance(sort, (str, Sort)):
            sort = [sort]
        sort = [to_sort(clause).as_dict() for clause in sort]

        # translate facet request variants to Facet objects
        if facets is None:
            facets = []
        if isinstance(facets, (str, Facet)):
            facets = [facets]
        facets = [to_facet(facet).as_dict() for facet in facets]

        if count is None:  # only set to max on None, 0 is valid
            count = MAX_RESULTS

        if select is select_all:
            select = None
        if isinstance(select, str):
            select = [select]

        if isinstance(timeout, timedelta):
            timeout = timeout.total_seconds()

        return omit_empty({
            'query': query,
            'start': start,
            'count': count,
            'sort': sort,
            'projectIds': sorted(project_ids) if project_ids else None,
            'select': select,
            'allowIncompleteResults': incomplete_results,
            'timeout': timeout,
            # use explicit Nones to omit keys not supported by some search endpoints
            'facets': facets or None,
            'maxSnippets': snippets or None,
            'type': tracelet_type or None,
        })

    def suggest(self, project_id, text, query_property='text', count=100):
        """
        Expand a search term from terms in the index.

        :param project_id: the project id to suggest terms from
        :param text: the text / search term to be expanded
        :param query_property: the search property to expand terms for (e.g.
            ``'file.name'`` or ``'text'``)
        :param count: the maximum number of suggestions to return
        :return: `list` of suggestions
        """
        single_project, multiple_projects = _quantify_projects(project_id)

        request = omit_empty({'projectIds': sorted(multiple_projects) if multiple_projects else None,
                              'property': query_property,
                              'count': count,
                              'text': text})

        # single_project will either be a project id or None (in which case the step is left out of the url)
        response = self._session.post(self.url(self.path.projects, single_project, '/suggest'),
                                      json=request)
        return _expect_ok(response).json()['suggestions']

    def task(self, task_id):
        response = self._session.get(self.url(self.path.tasks, task_id))
        return _expect_ok(response).json()

    def cancel_task(self, task_id):
        response = self._session.delete(self.url(self.path.tasks, task_id))
        # expect an OK response without content
        _expect_ok(response)

    def tasks(self, state='open', project_id=None, start=None, end=None):
        """
        Request a listing of tasks.

        :param state: the state of tasks to be listed, can be either
            ``'open'`` or ``'closed'``
        :param project_id: an optional project id to list tasks for
        :param start: an optional `datetime.date`, `datetime.datetime` or
            ISO 8601-formatted `str` to limit the tasks to be listed having
            its relevant moment after *state*
        :param end: an optional `datetime.date`, `datetime.datetime` or
            ISO 8601-formatted `str` to limit the tasks to be listed having
            its relevant moment before *state*
        :return: a `list` of tasks
        """
        # determine url to be used, request only tasks for a particular project if project id is specified
        if project_id:
            url = self.url(self.path.projects, project_id, '/tasks', state)
        else:
            url = self.url(self.path.tasks, state)

        # coerce start and end dates to date(time)s
        if isinstance(start, str):
            start = parse_date(start)
        if isinstance(end, str):
            end = parse_date(end)

        # use start and end as the to and from parameters
        response = self._session.get(url, params=omit_empty({'from': start.isoformat() if start else None,
                                                             'to': end.isoformat() if end else None}))
        return _expect_ok(response).json()

    def health(self):
        response = self._session.get(self.url('/health'))
        return _expect_ok(response).json()

    def log_messages(self, project_id, image_id, message_type='log', task_id=None):
        """
        Retrieves log messages for the extraction of image *image_id* within
        the project *project_id*.

        :param project_id: the project for which the extraction was run
        :param image_id: the image id for which to retrieve the log messages
        :param message_type: the type of message to retrieve, either ``'log'``
            or ``'failedTrace'``
        :param task_id: retrieve only messages related to a particular task id
        :return: a `list` of log messages, `dict`s with keys ``"date"`` and
            ``"message"``
        """
        response = self._session.get(self.url(self.path.projects, project_id, 'images', image_id, 'log'),
                                     params=omit_empty({'messageType': message_type,
                                                        'taskId': task_id}))
        return _expect_ok(response).json()

    def tools(self, project_id=None):
        """
        Get the tools available for extraction.

        :param project_id: get the tools available for a specific project
            (leave `None` for all tools)
        :return: a `dict`, mapping the name of a tool to its version and
            human-friendly description
        """
        # path to GET is rather different for a project-wide tool list
        if project_id:
            path = self.url(self.path.projects, project_id, 'extractions', 'tools')
        else:
            path = self.url(self.path.tools)

        response = self._session.get(path)
        return _expect_ok(response).json()

    def extract(self, project_id, image_id, type='index', key=fetch, tools=None, configuration=None, query=None):
        """
        Extract traces from an image in the context of a project.

        :param project_id: the project the extraction should be part of
        :param image_id: the image to be extracted
        :param type: the type of extraction to start
        :param key: the key data to be used to decrypt data, must be either
            `fetch`, `None` or binary (`bytes`)
        :param tools: the tools to be used; either a sequence of tool names or
            `None`, indicating to use the default tools (see also `.tools`)
        :param configuration: configuration overrides for this extraction, as
            a dict (e.g. ``{'timeout': 0}``)
        :param query: a query to use for extraction types other than 'index'
        :return: the job id of the extraction that is started
        """
        extraction = omit_empty({
            'type': type,
            'image': image_id,
            'tools': tools,
            'configuration': configuration,
            'query': query_to_dict(query) if query else None,  # query_to_json would turn None into {}
        })

        key = self._maybe_fetch_key(image_id=image_id, key=key)
        headers = {
            # always base64-encoded the key if provided, assume binary
            'Hansken-Image-Key': b64encode(key) if key else None,
        }
        headers = {key: value for key, value in headers.items() if value}

        # POST the extraction to remote, expect a 201 (Created) or 202 (Accepted)
        response = self._session.post(self.url(self.path.projects, project_id, 'extractions'),
                                      headers=headers,
                                      json=extraction)
        with drain(response):
            response = _expect_ok(response, codes.created, codes.accepted)
            # response will provide the uri for the extraction in the Location header, we want only the uuid
            # default to empty string in case no Location header was supplied
            extraction = response.headers.get('Location', '')
            extraction = re.match(self.pattern.extraction_id, extraction)
            if extraction:
                return extraction.group('extraction_id').lower()
            else:
                raise ValueError('no extraction id in response header Location: {}'.format(
                    response.headers.get('Location')
                ))

    def extract_singlefile(self, singlefile_id, tools=None, configuration=None):
        """
        Schedules the extraction for the singlefile with ID {singlefile_id}.
        This is an asynchronous call that only initiates the extraction.
        To monitor the progress of the extraction, use the 'get_singlefile' call
        to retrieve the states of the singlefile image object.

        :param singlefile_id: the id of the single file
        :param tools: the tools to be used; either a sequence of tool names or
            `None`, indicating to use the default tools (see also `.tools`)
        :param configuration: configuration overrides for this extraction, as
            a dict (e.g. ``{'timeout': 0}``)
        :return: the job id of the extraction that is initiated
        """
        extraction = omit_empty({
            'type': 'index',
            'tools': tools,
            'configuration': configuration,
        })

        # POST the extraction to remote, expect a 201 (Created) or 202 (Accepted)
        response = self._session.post(self.url(self.path.singlefiles, singlefile_id, 'extract'),
                                      json=extraction)
        with drain(response):
            response = _expect_ok(response, codes.created, codes.accepted)
            # response will provide the uri for the extraction in the Location header, we want only the uuid
            extraction = response.headers.get('Location', '')
            extraction = re.match(self.pattern.extraction_id, extraction)
            if extraction:
                return extraction.group('extraction_id').lower()
            else:
                raise ValueError('no extraction id in response header Location: {}'.format(
                    response.headers.get('Location')
                ))

    def backup_project(self, project_id, user_backup_key, image_keys=fetch):
        """
        Creates a backup of a project.

        :param project_id: the project to make a backup of
        :param user_backup_key: the key data to be used to encrypt the backup data, must be binary (`bytes`)
        :param image_keys: the key data to be used to decrypt data, must be a dict whose entries
            have an image id as key and have a binary (`bytes`) value. If no dict is provided,
            the image keys are fetched from the keystore.
        :return: the job id of the backup task that is started
        """
        encoded_image_keys = {}
        images = self.project_images(project_id)
        for image in images:
            image_id = image['id']
            if image_keys is fetch:
                image_key = self._maybe_fetch_key(image_id, fetch)
            else:
                image_key = image_keys.get(image_id, None)
            if image_key:
                encoded_image_keys[image_id] = b64encode(image_key)

        preferences = self.preferences(visibility='project', project_id=project_id)

        backup_request_data = omit_empty({
            'imageKeys': encoded_image_keys,
            'preferences': preferences
        })

        # POST the backup_json to remote, expect a 201 (Created) or 202 (Accepted)
        response = self._session.post(self.url(self.path.projects, project_id, 'backup'),
                                      json=backup_request_data,
                                      headers={'Hansken-User-Backup-Key': b64encode(user_backup_key)})
        with drain(response):
            response = _expect_ok(response, codes.created, codes.accepted)
            # response will provide the uri for the backup task in the Location header, we want only the uuid
            # default to empty string in case no Location header was supplied
            backup_task = response.headers.get('Location', '')
            backup_task = re.match(self.pattern.task_id, backup_task)
            if backup_task:
                return backup_task.group('task_id').lower()
            else:
                raise ValueError('no task id in response header Location: {}'.format(
                    response.headers.get('Location')
                ))

    def download_backup(self, task_id, file_path):
        if os.path.exists(file_path):
            raise ValueError('Backup file already exists: {}'.format(file_path))
        download_url = self.url(self.path.backups, task_id, 'data')
        backup_response = self._session.get(download_url)
        with open(file_path, 'wb') as f:
            # read chunks of up to a megabyte in size
            for chunk in backup_response.iter_content(chunk_size=1 << 20):
                f.write(chunk)

    def upload_image(self, image_id, data, extension=None, offset=None):
        """
        Uploads image data. Note that data in the NFI format requires two files
        (``.nfi`` (data) and ``.nfi.idx`` (index)) and thus two upload calls.

        :param image_id: the image id of the data to be uploaded
        :param data: the image data to be uploaded, either `bytes`, a file-like
            object or an iterable providing bytes (see documentation on
            ``requests``' upload support)
        :param extension: file extension of the upload, either ``'.nfi'``,
            ``'.nfi.idx'`` or `None`
        :param offset: byte offset of *data* within the complete file to be
            uploaded
        :return: the image id of the uploaded data
        """
        # create the upload file name based on the image id and extension
        fname = image_id + (extension or '')
        headers = {}
        if offset is not None:
            headers['Content-Range'] = 'bytes {}-{}/*'.format(offset, offset + len(data) - 1)

        response = self._session.post(self.url(self.path.images, image_id, 'upload', fname), headers=headers, data=data)

        with drain(response):
            if offset is not None:
                _expect_ok(response, ok=codes.ok)
                return

            response = _expect_ok(response, ok=codes.created)
            # expect the uploaded image id to be in the response' Location header
            result = response.headers.get('Location', '')
            result = re.match(self.pattern.image_id, result)
            if result:
                result = result.group('image_id').lower()
                if result != image_id.lower():
                    # reported result id does not match the upload id, this should not happen
                    raise ValueError('resulting image id does not match requested image id: {} != {}'.format(
                        result, image_id
                    ))

                return result
            else:
                raise ValueError('no image id in response header Location: {}'.format(
                    response.headers.get('Location')
                ))

    def upload_singlefile(self, data, name):
        """
        A singlefile is a temporary single data source for quick extraction of traces.
        Upload a singlefile performs a number of steps:
            - create a project with property hidden set to true
            - create an image with property hidden set to true
            - link the image to the project
            - upload the singlefile data

        :param data: the image data to be uploaded, either `bytes`, a file-like
            object or an iterable providing bytes (see documentation on
            ``requests``' upload support)
        :param name: the name for the singlefile project and image
        :return: the singlefile's identifier (a str(UUID))
        """
        # post data to the upload endpoint
        response = self._session.post(self.url(self.path.singlefiles, 'upload', name), data=data)

        with drain(response):
            response = _expect_ok(response, codes.created, codes.accepted)
            # expect the uploaded singlefile id to be in the response' Location header
            result = response.headers.get('Location', '')
            # response will provide the uri for the new singlefile in the Location header, we want only the uuid
            result = re.match(self.pattern.singlefile_id, result)
            if result:
                return result.group('singlefile_id').lower()
            else:
                raise ValueError('no singlefile id in response header Location: {}'.format(
                    response.headers.get('Location')
                ))

    def singlefiles(self):
        response = self._session.get(self.url(self.path.singlefiles))
        return _expect_ok(response).json()

    def singlefile(self, singlefile_id):
        response = self._session.get(self.url(self.path.singlefiles, singlefile_id))
        return _expect_ok(response).json()

    def singlefile_traces(self, singlefile_id):
        """
        Get all traces within a singlefile.

        :param singlefile_id: unique id of the singlefile, UUID
        :return: a file-like object, streaming the raw json response from remote
        """
        response = self._session.get(self.url(self.path.singlefiles, singlefile_id, 'traces'))
        return _ensure_binary_io(_expect_ok(response))

    def singlefile_tracelets(self, singlefile_id, tracelet_type):
        """
        Get tracelets of a certain type within a singlefile.

        :param singlefile_id: id of the singlefile
        :param tracelet_type: the type of tracelet to search for
        :return: a file-like object, streaming the raw json response from remote
        """
        response = self._session.get(self.url(self.path.singlefiles, singlefile_id, 'tracelets', tracelet_type))
        return _ensure_binary_io(_expect_ok(response))

    def delete_singlefile(self, singlefile_id):
        """
        Delete a singlefile with a given singlefileId.

        :param singlefile_id: singlefile to be deleted
        :return: a success-value, whether the deletion of the singlefile has succeeded
        """
        response = self._session.delete(self.url(self.path.singlefiles, singlefile_id))
        with drain(response):
            _expect_ok(response)
        return True

    def __repr__(self):
        return '<{0.__class__.__module__}.{0.__class__.__name__} endpoint={1} ({2})>'.format(
            self,
            self.base_url + ('' if self._session.verify else ' (!)'),
            'authenticated' if self.auth else 'anonymous'
        )


class SearchResult(Iterable):
    """
    Stream of traces generated from a remote JSON-encoded stream. Note that
    this result itself can be iterated only once, but
    `Trace <hansken.trace.Trace>` instances obtained from it do not rely on the
    result they've been obtained from.

    See `.ProjectContext.search`.

    Getting results from a `.SearchResult` can be done in one of three ways:

    Treating the result as an iterable:

    .. code-block:: python

        for trace in result:
            print(trace.name)

    Calling `.take` to process one or more batches of traces:

    .. code-block:: python

        first_100 = result.take(100)
        process_batch(first_100)

    Calling `.takeone` to get a single trace:

    .. code-block:: python

        first = result.takeone()
        second = result.takeone()

        print(first.name, second.name)

    If indices of traces within a result are needed, iteration can be combined
    with `enumerate`:

    .. code-block:: python

        for idx, trace in enumerate(result):
            print(idx, trace.name)

    Additional result info can be including using `.including`:

    .. code-block:: python

        # note that score will only have a value if the search was sorted on it
        for trace, score in result.including('score'):
            print(score, trace.name)

    .. note::

        The underlying response from the REST API for a `.SearchResult` is a
        stream. This means that ``hansken.py`` keeps the connection used for
        the result open for as long as needed. As a side-effect, the underlying
        stream can time out if not consumed quickly enough. Consuming at least
        100 traces a minute from a `.SearchResult` should keep timeouts at bay,
        as a rule of thumb.

        Depending on the arguments to `.ProjectContext.search`, a
        `.SearchResult` might be able to auto-resume iteration of results in
        the event of errors (such as timeouts).

        To explicitly release resources used by a `.SearchResult`, use it as a
        context manager or manually call `close <.SearchResult.close>`.

    .. warning::

        The truth value of a `.SearchResult` is based on the expectation of
        additional traces that can be read from its stream. This is only known
        for sure when the end of that stream is reached. Avoid code that
        requires a `.SearchResult` to be truthy before retrieving its results;
        use iteration wherever possible.

        Additionally, the `num_results` property provides the total number of
        results for the search call that produced this `.SearchResult`, this
        does not necessarily align with the number of result objects that can
        be retrieved from it (e.g. when the ``count`` parameter of the search
        call was used).
    """

    _results_prefix = 'traces'
    _primary_prefix = 'trace'
    _resume_property = 'uid'

    def __init__(self, fd, trace_class=dict, model=None, project_id=None, connection=None, query=None,
                 **kwargs):
        self._fd = fd
        self.result_class = trace_class
        self.model = model

        # create an event generator for use with higher level interface
        self._stream = json_events(self._fd)
        self._offset = 0

        # expecting a preamble containing the size of the result and a list of facets
        # reads until a map key "traces" is found, indicating the start of the actual results
        self.num_results, self._facets = self._read_preamble()

        # track whether the stream has been consumed
        # False if num_results is at least 1
        # True if the total number of results is 0; it's exhausted on creation
        self._exhausted = self.num_results == 0

        self._facets = [FacetResult(facet) for facet in self._facets]
        # keep self._stream for trace iteration later on

        self._project_id = project_id
        self._query = query

        self._search = connection.search if connection else None

        self._kwargs = kwargs

    def _read_preamble(self):
        # initialize defaults for length and facets
        num_results = 0
        facets = []

        # consume from self._stream, advancing the result document
        for prefix, etype, value in self._stream:
            if prefix == self._results_prefix:
                # as soon as we hit the specific prefix, we'll be reading search results, signals end of preamble
                return num_results, facets

            if prefix == 'totalResults':
                # singular value, prefix "totalResults" will carry a numeric value, assign to length
                num_results = value
            if (etype, value) == ('map_key', 'facets'):
                # key "facets" signals facets to follow, use json_items to parse the entire value after it (possibly
                # an empty list)
                facets = next(json_items(self._stream, 'facets'))
            if (prefix, etype) == ('warnings.item', 'string'):
                # the optional array of warnings was supplied, warn about every single string-value in that array
                log.warn('search result carries warning message: {}', value)

        raise ValueError('failed to find key "{}" in search result stream'.format(self._results_prefix))

    @property
    def facets(self):  # defined as a property to make it show up in class doc
        """
        The facets returned with the search result, a `list` of `.FacetResult`
        instances.
        """
        return self._facets

    def takeone(self, include=None):
        """
        Takes the next trace from this result. This method may be called
        repeatedly.

        :param include: name (`str`) or names to be included in the result,
            see `.including`
        :return: the next trace in the result, or `None` if it's exhausted
        :rtype: `Trace <hansken.trace.Trace>`, `None` or a `namedtuple` if
            *include* was non-empty
        """
        if self._exhausted:
            # avoid triggering warnings from calling __iter__
            return None

        if isinstance(include, str):
            include = [include]

        return next(self.__iter__(close=False, include=include), None)

    def take(self, num, include=None):
        """
        Takes num traces from this result. Subsequent calls will produce
        batches of traces as if using slicing.

        :param num: amount of traces to take
        :param include: name (`str`) or names to be included in the result,
            see `.including`
        :return: a list of `Trace <hansken.trace.Trace>` or `namedtuple`
            instances, of at most `num` size (or empty if the result is
            exhausted)
        :rtype: `list`
        """
        if self._exhausted:
            # avoid triggering warnings from calling __iter__
            return []

        if isinstance(include, str):
            include = [include]

        # explicitly populate a list, so it'll have a length
        # make sure to not close so we can keep calling take()
        return list(islice(self.__iter__(close=False, include=include), num))

    def including(self, *names):
        """
        Iterates this result, yielding the requested named attributes
        accompanying a trace along with the trace. The trace is always the
        leftmost value in the tuples yielded by this method. Other attributes
        are included in parameter order and can be `None`.

        .. code-block:: python

            # the score for each search result is only available when sorted on score
            # iteration yields a 2-tuple, the trace with 1 additional attribute
            for trace, score in context.search(sort='score-').including('score'):
                print(score, trace.uid)

        :param names: attributes to include in the yielded tuple
        :return: a `generator`, yielding `namedtuple` instances
        """
        return self.__iter__(include=names)

    def close(self):
        """
        Closes the file descriptor used to by the underlying JSON stream.
        After calling this method, no more traces can be obtained from this
        `.SearchResult` (previously retrieved traces will remain usable).
        """
        self._fd.close()
        self._stream = None

    def _resume_from(self, value):
        # explicitly release raw connection,
        self.close()

        # construct resume query based on last successfully retrieved trace and/or the original query
        query = None
        if value:
            query = Range(self._resume_property, gt=value)
        if self._query:
            if query:
                query = query & self._query
            else:
                query = self._query

        # create a new raw json + event stream (leave self._len and self._facets, those were already read
        # from the original response)
        self._fd = self._search(project_id=self._project_id, query=query, sort=self._resume_property, **self._kwargs)
        self._stream = json_events(self._fd)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __len__(self):
        warnings.warn(DeprecationWarning('len(SearchResult) has been deprecated, use num_results property'))
        return self.num_results

    def __bool__(self):
        return not self._exhausted

    def __iter__(self, close=False, include=None):
        if self._exhausted:
            log.warn('attempting to iterate a search result that is exhausted (search results can only be read once, '
                     'issue another search request or use .take() to get a reusable batch of search results)')
            return
        if not self._stream:
            log.warn('result stream is closed')
            return

        rtype = None
        if include is not None:
            # we need to include more than just a result, collect the names of things to be yielded (including result)
            fields = [self._primary_prefix]
            fields.extend(include)
            # construct a named tuple to 'contain' the things we need
            rtype = namedtuple('result', fields)

        last_entry = None

        try:
            while not self._exhausted:
                try:
                    # get all items at prefix prefix.item (key equal to the primary prefix for elements in the array
                    # with the results prefix key)
                    for self._offset, entry in enumerate(
                            json_items(self._stream, '{}.item'.format(self._results_prefix)),
                            start=self._offset + 1
                    ):
                        # we'll always need result, wrapped with a result class
                        result = entry.get(self._primary_prefix) if self._primary_prefix else entry
                        result = self.result_class(result)

                        last_entry = result.get(self._resume_property)

                        if rtype:
                            # yield result including the additional fields as requested, all wrapped up in a named tuple
                            yield rtype(result, *[entry.get(name) for name in include])
                        else:
                            # nothing to include, yield only result
                            yield result

                    # reached a 'natural' end of the stream
                    self._exhausted = True
                except RECOVERABLE_JSON_STREAM_ERRORS as e:
                    if not self._search:
                        log.warn('result stream broken, cannot auto-resume without project id and connection object')
                        raise

                    log.warn('attempting auto-resume of search result from {} > {} (current offset {}) due to {}',
                             self._resume_property, last_entry, self._offset, repr(e))
                    self._resume_from(last_entry)
        finally:
            if close or self._exhausted:
                self.close()

    def __repr__(self):
        return '<{0.__class__.__module__}.{0.__class__.__name__}, num_results={0.num_results}>'.format(self)


class TraceletSearchResult(SearchResult):
    """
    Stream of tracelets generated from a remote JSON-encoded stream. Note that
    this result itself can be iterated only once, but elements obtained from it
    do not rely on the result they've been obtained from.

    See `.ProjectContext.search_tracelets`.

    .. note::

        The same notes and caveats expressed for `.SearchResult` apply to the
        `.TraceletSearchResult`.
    """
    _results_prefix = 'tracelets'
    _primary_prefix = 'tracelet'
    _resume_property = 'id'

    def __init__(self, fd, trace_class=dict, model=None, project_id=None,
                 connection=None, tracelet_type=None, query=None,
                 **kwargs):
        super(TraceletSearchResult, self).__init__(fd, trace_class, model, project_id, connection, query, **kwargs)

        # make sure to set the tracelet type to be used on the resume call
        self._search = partial(connection.search_tracelets, tracelet_type=tracelet_type) if connection else None


class ValueSearchResult(SearchResult):
    """
    Stream of values generated from a remote JSON-encoded stream. Note that
    this result itself can be iterated only once, but elements obtained from it
    do not rely on the result they've been obtained from.

    The elements obtained from this result act like `dict`s, with at least the
    keys ``value`` and ``count``, representing a value for the selected
    property and the number of times it occurs respectively. Both of these
    depend on the query that was supplied to the call that created this result,
    potentially omitting values or lowering occurrence counts when compared to
    that same call without a query.

    .. note::

        The same notes and caveats expressed for `.SearchResult` apply to the
        `.TraceletSearchResult`.
    """
    _results_prefix = 'values'
    _primary_prefix = None
    _resume_property = 'value'

    def __init__(self, fd, result_class=dict, project_id=None, connection=None, select=None, query=None, **kwargs):
        super().__init__(fd, result_class, model=None, project_id=project_id, connection=connection, query=query,
                         **kwargs)

        self._search = partial(connection.unique_values, select=select) if connection else None

    def _resume_from(self, value):
        self.close()

        self._fd = self._search(project_id=self._project_id, query=self._query, after=value, **self._kwargs)
        self._stream = json_events(self._fd)


class FacetResult(Mapping):
    """
    Ordered mapping containing facet results. Iteration yields counter labels,
    values for which are a named tuple with attributes:

    - label: a provided label for a bucket
    - value: the value for a bucket (actual value of the start of a bucket)
    - count: the number of hits for the labeled bucket within a search

    Use as such:

    .. code-block:: python

        # search a project for all files and get a facet for the file extensions
        results = context.search(query=Term('type', 'file'),
                                 facets=Facet('file.extension'))
        # in case you're only interested in the facet, also supply count=0 to the search() call
        # this avoids making Hansken's REST API retrieve all the traces for that search result

        # the facet will be available on the result
        facet = results.facets[0]

        # the three loops below will output the same information
        for label in facet:
            print(label, facet[label].count)

        for label, counter in facet.items():
            print(label, counter.count)

        for counter in facet.values():
            print(counter.label, counter.count)
    """

    Counter = namedtuple('FacetCounter', ('label', 'value', 'count'))

    def __init__(self, source):
        self.field = source['field']
        self.total = source.get('total')
        self.counters = [FacetResult.Counter(**counter) for counter in source['counters']]
        self.counters = OrderedDict([
            (counter.label or str(counter.value), counter) for counter in self.counters
        ])

    def __len__(self):
        return len(self.counters)

    def __iter__(self):
        return iter(self.counters)

    def __getitem__(self, item):
        return self.counters[item]

    def __repr__(self):
        return '<{0.__class__.__module__}.{0.__class__.__name__} field={0.field}, len={1}>'.format(
            self, len(self)
        )


@decorator
def _auto_open(func, self, *args, **kwargs):
    """
    Automatically opens a context if it wasn't opened yet.

    :param func: the method being decorated
    :param self: the instance func is to be bound to
    :param args: positional arguments to func
    :param kwargs: keyword arguments to func
    :return: func, calling self.open() when it wasn't yet opened
    """
    if not self.is_open:
        self.open()

    try:
        # attempt whatever we're supposed to be doing now self is open
        return func(self, *args, **kwargs)
    except HTTPError as e:
        if e.response.status_code == codes.bad_request:
            error = e.response.text
            closed_message = '{} has been deactivated'.format(self.project_id)
            if error and error.endswith(closed_message) and self.auto_activate:
                log.warn('project {} is deactivated, attempting to activate', self.project_id)
                # a bad-request-response with a message stating that the project index is closed, attempt to activate it
                self.connection.activate_project(self.project_id)
                # mark self as having activated the project
                self.auto_activated = True
                # re-attempt whatever we're supposed to be doing
                return func(self, *args, **kwargs)

        # apparently not a response we should handle here, raise original error
        raise


class ProjectContext:
    """
    Utility class adding a particular project id to each rest call that
    requires one. Provided with a url to a Hansken gatekeeper and the id of a
    project, methods of this class will make REST requests to the gatekeeper,
    wrapping results with a Trace class or iterator where applicable.

    ProjectContext instances are usable as context managers, which opens the
    context for use. Calls to methods requiring an initialized connection
    will automatically open the context if it wasn't yet opened.
    """

    def __init__(self, base_url_or_connection, project_id, keystore_url=None, preference_url=None, auth=None,
                 auto_activate=True, connection_pool_size=None,
                 verify=True):
        """
        Creates a new context object facilitating communication to a Hansken
        gatekeeper. Uses a Connection to track session state. The provided
        project id is used for all calls. Can be used with an existing
        `.Connection` instance

        :param base_url_or_connection: HTTP endpoint to a Hansken gatekeeper
            (e.g. https://hansken.nl/gatekeeper) or a `.Connection` instance
        :param project_id: project id to associate with
        :param keystore_url: HTTP endpoint to a Hansken keystore (e.g.
            https://hansken.nl/keystore)
        :param preference_url: HTTP endpoint to a Hansken preference service
        :param auth: `HanskenAuthBase <hansken.auth.HanskenAuthBase>` instance
            to handle authentication, or `None`
        :param auto_activate: whether the project should automatically be
            activated if it is currently deactivated
        :param connection_pool_size: maximum size of HTTP(S) connection pool
        """
        self.project_id = project_id
        self.project = None
        self.model = None
        self.trace_class = None

        if isinstance(base_url_or_connection, Connection):
            if keystore_url or preference_url or auth or connection_pool_size:
                # patching the Connection instance would change state of an argument, refuse this
                raise ValueError('cannot create ProjectContext from Connection while specifying keystore_url, '
                                 'preference_url, auth or connection_pool_size')

            # Connection object provided, use direct
            self.connection = base_url_or_connection
        else:
            # use a newly constructed Connection object
            self.connection = Connection(base_url_or_connection, keystore_url=keystore_url,
                                         preference_url=preference_url, auth=auth,
                                         connection_pool_size=connection_pool_size,
                                         verify=verify)

        self.is_open = False
        self.auto_activate = auto_activate
        self.auto_activated = False

    def open(self):
        self.connection.open()

        # NB: make sure to *not* hit the search index to avoid hitting a closed index
        self.project = self.connection.project(self.project_id)
        # retrieve the *global* model
        # avoid attribute errors on model properties that are not filled for a particular project
        self.model = TraceModel(self.connection.trace_model())
        self.trace_class = trace_class_from_model(self.model)
        # reassign trace class to automatically fill context, referring back to self
        self.trace_class = partial(self.trace_class, context=self)

        self.is_open = True

        return self

    def close(self):
        if self.auto_activated:
            # we were the one to auto-activate the project, leave things as they were
            log.info('deactivating auto-activated project {}', self.project_id)
            try:
                self.connection.deactivate_project(self.project_id)
                log.info('project {} deactivated', self.project_id)
            except HTTPError as e:
                # deactivation requires special permissions, this might fail
                log.warn('auto-deactivation of project {} failed', self.project_id, e)

        self.is_open = False
        self.auto_activated = False

        self.connection.close()

        self.project = None
        self.model = None
        self.trace_class = None

        # clear any cached results
        self.image_name.cache_clear()
        self.key.cache_clear()

    def __enter__(self):
        return self.open()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @_auto_open
    def image(self, image_id):
        return self.connection.image(project_id=self.project_id, image_id=image_id)

    @_auto_open
    def images(self):
        return self.connection.project_images(self.project_id)

    @lru_cache(maxsize=None)
    @_auto_open
    def image_name(self, image_id):
        """
        Retrieves the name (falling back to description if that isn't
        available) of an image, identified by its id.

        .. note::
            Results of this call are cached inside the `.ProjectContext`,
            making repeated calls to this method cheap. See Python's
            documentation on `functools.lru_cache
            <https://docs.python.org/3/library/functools.html#functools.lru_cache>`_.
            This cache is cleared when the `.ProjectContext` is closed (this
            includes it being used as a context manager).

        :param image_id: the id of the image to name
        :return: ``image_id``'s name
        """
        image = self.image(image_id)
        # retrieve an image's name, fall back to its description
        return image.get('name') or image.get('description')

    @lru_cache(maxsize=None)
    @_auto_open
    def key(self, image_id):
        """
        Retrieve the key for image identified by *image_id*.

        .. warning::
            ``hansken.py`` cannot distinguish between an image not needing a
            key and a user that is not authorized to retrieve data from an
            image. In both cases, the result of this method is `None`.

        .. note::
            Results of this call are cached inside the `.ProjectContext`,
            making repeated calls to this method cheap. See Python's
            documentation on `functools.lru_cache
            <https://docs.python.org/3/library/functools.html#functools.lru_cache>`_.
            This cache is cleared when the `.ProjectContext` is closed (this
            includes it being used as a context manager).

        :param image_id: the id of the image to retrieve the key for
        :return: ``image_id``'s key, or `None`
        """
        return self.connection.key(image_id, raise_on_not_found=False)

    @_auto_open
    def roots(self):
        traces = self.connection.roots(self.project_id)
        return [self.trace_class(trace) for trace in traces]

    @_auto_open
    def trace(self, trace_uid):
        source = self.connection.trace(self.project_id, trace_uid)
        return self.trace_class(source)

    @_auto_open
    def data(self, trace_uid, stream='raw', offset=0, size=None, key=fetch):
        if key is fetch:
            # ProjectContext caches keys, prefer cached over fetched from remote
            key = self.key(image_from_uid(trace_uid))

        return self.connection.data(self.project_id, trace_uid, stream, offset, size, key)

    @_auto_open
    def snippets(self, *snippets, keys=fetch, highlights=None):
        """
        Retrieves textual snippets of data, optionally highlighting term hits
        within the resulting text.

        :param snippets: snippet request dicts
        :param keys: keys required for data access, either `fetch` to
            automatically attach the corresponding keys to each snippet, a
            `dict` mapping image ids to (binary) key data or `None`
        :param highlights: collection of terms to be highlighted in all snippet
            results (highlights provided here are added to all requests in
            *snippets*)
        :return: a `list` of snippet response dicts, index-matched to *snippets*
        """
        def augment(request):
            overwrite = {}

            if keys and 'imageKey' not in request:
                # key needed for request is based on the image of the trace
                image_id = image_from_uid(request['uid'])
                # either retrieve the key or take it from provided keys
                key = self.key(image_id) if keys is fetch else keys.get(image_id)
                if key:
                    overwrite['imageKey'] = b64encode(key)

            if highlights:
                # add provided highlights to the highlights already present in the request
                terms = set(request.get('highlights', []))
                terms.update(highlights)
                # coerce terms back into a list for JSON serialization (sorted to force deterministic output)
                overwrite['highlights'] = sorted(terms)

            # avoid changing request in-place, return shallow copy with added / overwritten keys
            return {**request, **overwrite}

        # augment the requests with keys and/or highlights
        snippets = [augment(request) for request in snippets]

        # turn the list of responses into Snippet objects
        return [Snippet(response) for response in self.connection.snippets(self.project_id, *snippets)]

    @_auto_open
    def children(self, trace_uid, query=None, start=0, count=None, sort=None, facets=None, snippets=None, timeout=None):
        """
        Searches the children of a trace. See
        `search <.ProjectContext.search>` and `.SearchResult`.

        :param trace_uid: id of the trace retrieve children for
        :param query: the query to submit
        :param start: the start offset of the retrieved result
        :param count: max number of traces to retrieve
        :param sort: sort clause(s) of the form ``score-``, ``some.field``
        :param facets: facet(s) to be used for search (`str`,
            `Facet <hansken.query.Facet>` or sequence of either)
        :param snippets: maximum number of snippets to return per trace
        :param timeout: the maximum amount of time to wait for a search
            response, in seconds or as a `datetime.timedelta` (defaults to
            letting the remote decide), set to 0 to disable timeout
        :return: a trace stream (iterable once)
        """
        fd = self.connection.children(project_id=self.project_id,
                                      trace_uid=trace_uid,
                                      query=query,
                                      start=start,
                                      count=count,
                                      sort=sort,
                                      facets=facets,
                                      snippets=snippets,
                                      timeout=timeout)
        return SearchResult(fd, self.trace_class)

    @_auto_open
    def note(self, trace_uid, note, refresh=None):
        return self.connection.note(self.project_id, trace_uid, note, refresh=refresh)

    @_auto_open
    def tag(self, trace_uid, tag, refresh=None):
        return self.connection.tag(self.project_id, trace_uid, tag, refresh=refresh)

    @_auto_open
    def delete_tag(self, trace_uid, tag, refresh=None):
        return self.connection.delete_tag(self.project_id, trace_uid, tag, refresh=refresh)

    @_auto_open
    def mark_privileged(self, trace_uid, status, refresh=None):
        return self.connection.mark_privileged(self.project_id, trace_uid, status, refresh=refresh)

    @_auto_open
    def child_builder(self, parent_uid):
        """
        Create a `.TraceBuilder` to build a trace to be saved as a child of
        the trace identified by *parent_uid*. Note that a new trace will only
        be added to the index once explicitly saved (e.g. through
        `.TraceBuilder.build`).

        :param parent_uid: a trace identifier to create a child builder for
        :return: a `.TraceBuilder` set up to save a new trace as the child
            trace of *parent_uid*
        """
        return TraceBuilder(self.model, target=(self.project_id, parent_uid), context=self)

    @_auto_open
    def update_trace(self, trace, updates=None, data=None, key=fetch, overwrite=False):
        """
        Updates metadata of *trace* to reflect requested updates in the user
        origin. Does *not* edit *trace* in-place.

        :param trace: `.Trace` to be updated
        :param updates: metadata properties to be added or updated, mapped to
            new values in a (possibly nested) `dict`
        :param data: a `dict` mapping data type / stream name to bytes to be
            imported
        :param key: the key data for image *trace* belongs to, must be
            `fetch`, `None` or binary (`bytes`)
        :param overwrite: whether properties to be imported should be
            overwritten if already present
        :return: processing information from remote
        """
        # create a search target for the importer, using identifying properties
        target = {name: trace.get(name) for name in ('uid', 'name', 'pathItems')}
        builder = TraceBuilder(self.model, source=target)
        if updates:
            builder.update(updates)

        if data and key is fetch:
            # ProjectContext caches keys, prefer cached over fetched from remote (but only when importing new data)
            key = self.key(image_from_trace(trace))

        # supply target as the trace to be imported, request the updates to be set
        return self.connection.import_trace(self.project_id, builder,
                                            # updates can be omitted, connection will be aware of the builder
                                            data=data, key=key, method='strict', overwrite=overwrite)

    @_auto_open
    def search(self, query=None, start=0, count=None, sort='uid', facets=None, snippets=None, select=select_all,
               incomplete_results=None, timeout=None):
        """
        Performs a search request, wrapping the result in a sequence that
        allows iteration, indexing and slicing, automatically fetching batches
        of results when needed.
        The returned sequence keeps state and is *not* threadsafe.

        .. note::

            Supplying a value for *count* is **required** when using a *start*
            offset. The maximum size of such a batch is dictated by the
            Hansken REST API and will usually be 200. Requesting a batch
            larger than the maximum amount of traces will raise an error.

            Additionally, neither *start* nor *count* influence the result
            of the `len` builtin on the result set, just the amount of traces
            iteration of the result will yield, see `.SearchResult`.

        :param query: the query to submit
        :param start: the start offset of the retrieved result
        :param count: max number of traces to retrieve
        :param sort: sort clause(s) of the form ``score-``, ``some.field``,
            defaults to sorting on ``uid``
        :param facets: facet(s) to be used for search (`str`,
            `Facet <hansken.query.Facet>` or sequence of either)
        :param snippets: maximum number of snippets to return per trace
        :param select: property selector(s), defaults to all properties
        :param incomplete_results: whether to allow results from an incomplete
            index (defaults to letting the remote decide, which will typically
            *not* allow results from an incomplete index)
        :param timeout: the maximum amount of time to wait for a search
            response, in seconds or as a `datetime.timedelta` (defaults to
            letting the remote decide), set to 0 to disable timeout
        :return: a `Trace <hansken.trace.Trace>` stream (iterable once)
        :rtype: `.SearchResult`
        """
        fd = self.connection.search(project_id=self.project_id,
                                    query=query,
                                    start=start,
                                    count=count,
                                    sort=sort,
                                    facets=facets,
                                    snippets=snippets,
                                    select=select,
                                    incomplete_results=incomplete_results,
                                    timeout=timeout)
        if sort == 'uid' and not (start or count):
            # sort wasn't touched or set explicitly to uid, enable auto-resuming search result
            query = to_query(query)
            return SearchResult(fd, self.trace_class or dict, model=self.model,
                                # auto-resume information
                                project_id=self.project_id, connection=self.connection, query=query,
                                # additional search arguments to be passed along
                                snippets=snippets, select=select, timeout=timeout)
        else:
            log.warn('cannot create auto-resuming search result on custom sort or use of start/count '
                     '(sort={}, start={}, count={})', sort, start, count)
            return SearchResult(fd, self.trace_class or dict, model=self.model)

    @_auto_open
    def search_tracelets(self, tracelet_type, query=None, start=0, count=None, sort='id', select=select_all,
                         incomplete_results=None, timeout=None):
        """
        Performs a search request for tracelets, wrapping the result in an
        iterator of `DictView <hansken.util.DictView>` objects.

        :param tracelet_type: the type of tracelet to search for
        :param query: query to match tracelets
        :param start: the start offset of the retrieved result
        :param count: max number of tracelets to retrieve
        :param sort: sort clause(s) of the form ``score-``, ``some.field``,
            defaults to sorting on ``id``
        :param select: property selector(s), defaults to all properties
        :param incomplete_results: whether to allow results from an incomplete
            index (default to letting the remote decide, which will typically
            *not* allow results from an incomplete index)
        :param timeout: the maximum amount of time to wait for a search
            response, in seconds or as a `datetime.timedelta` (defaults to
            letting the remote decide), set to 0 to disable timeout
        :return: a tracelet stream containing
            `DictView <hansken.util.DictView>` instances (iterable once)
        :rtype: `.TraceletSearchResult`
        """
        fd = self.connection.search_tracelets(project_id=self.project_id,
                                              tracelet_type=tracelet_type,
                                              query=query,
                                              start=start,
                                              count=count,
                                              sort=sort,
                                              select=select,
                                              incomplete_results=incomplete_results,
                                              timeout=timeout)
        if sort == 'id' and not (start or count):
            if query:
                query = query if isinstance(query, Query) else HQLHuman(query)
            return TraceletSearchResult(fd, DictView, model=self.model,
                                        project_id=self.project_id, tracelet_type=tracelet_type,
                                        connection=self.connection, query=query, select=select,
                                        timeout=timeout)
        else:
            log.warn('cannot create auto-resuming search result on custom sort or use of start/count '
                     '(sort={}, start={}, count={})', sort, start, count)
            return TraceletSearchResult(fd, DictView, model=self.model)

    @_auto_open
    def unique_values(self, select, query=None, after=None, count=None, incomplete_results=None,
                      timeout=None):
        """
        Retrieves unique values for the selected property or properties with
        their corresponding counts. The set of traces or tracelets from which
        these values are taken can be controlled with the *query* argument
        (though also take note of the particulars of the *query* argument
        below). To retrieve unique addressees for deleted email traces, the
        following could be used:

        .. code:: python

            # define a query to select only traces that are marked as deleted
            query = Term('type', 'deleted')
            # retrieve unique values for the "email.to" property
            for result in context.unique_values('email.to', query):
                print(result['count'], result['value'])

        .. note::

            Use ``trace:{query}`` to apply a the query to the trace itself, if
            the property in ``select`` is part of a tracelet (i.e.
            ``entity.value``). To filter by traces of type email for example,
            add ``trace:{type:email}``.

        :param select: the property or properties to select values for
        :param query: query to match traces or tracelets to take values from
        :param after: starting point for the result stream
        :param count: max number of values to retrieve
        :param incomplete_results: whether to allow results from an incomplete
            index (default to letting the remote decide, which will typically
            *not* allow results from an incomplete index)
        :param timeout: the maximum amount of time to wait for a search
            response, in seconds or as a `datetime.timedelta` (defaults to
            letting the remote decide), set to 0 to disable timeout
        :return: a stream of values with counters (iterable once), sorted by
            the natural order of the values
        :rtype: `.ValueSearchResult`
        """
        fd = self.connection.unique_values(project_id=self.project_id,
                                           select=select,
                                           query=query,
                                           after=after,
                                           count=count,
                                           incomplete_results=incomplete_results,
                                           timeout=timeout)
        if count:
            log.warn('cannot create auto-resuming value search result on use of count (count={})', count)
            return ValueSearchResult(fd, DictView)
        else:
            return ValueSearchResult(fd, DictView,
                                     project_id=self.project_id, connection=self.connection,
                                     select=select, query=query,
                                     incomplete_results=incomplete_results, timeout=timeout)

    @_auto_open
    def suggest(self, text, query_property='text', count=100):
        """
        Expand a search term from terms in the index.

        Use key ``'text'`` for a plain version of the expanded term, key
        ``'highlighted'`` for a highlighted version:

        .. code-block:: python

            # get the plain expansion of terms starting with "example"
            texts = [suggestion['text'] for suggestion in context.suggest('example')]

            # get highlighted expansions for file names starting with "example"
            highlighted = [suggestion['highlighted']
                           for suggestion in context.suggest('example'
                                                             property_query='file.name')]
            # values will contain square brackets to show what was expanded, e.g.
            # 'example[[.exe]]' or 'example[[file.dat]]'

        :param text: the text / search term to be expanded
        :param query_property: the search property to expand terms for (e.g.
            ``'file.name'`` or ``'text'``)
        :param count: the maximum number of suggestions to return
        :return: `list` of suggestions
        """
        return self.connection.suggest(self.project_id, text, query_property=query_property, count=count)

    @_auto_open
    def task(self, task_id):
        return self.connection.task(task_id)

    @_auto_open
    def tasks(self, state='open', start=None, end=None):
        """
        Request a listing of tasks for this project.

        :param state: the state of tasks to be listed, can be either
            ``'open'`` or ``'closed'``
        :param start: an optional `datetime.date`, `datetime.datetime` or
            ISO 8601-formatted `str` to limit the tasks to be listed having
            its relevant moment after *state*
        :param end: an optional `datetime.date`, `datetime.datetime` or
            ISO 8601-formatted `str` to limit the tasks to be listed having
            its relevant moment before *state*
        :return: a `list` of tasks
        """
        return self.connection.tasks(state=state, project_id=self.project_id, start=start, end=end)

    @_auto_open
    def singlefile(self):
        return self.connection.singlefile(singlefile_id=self.project_id)

    @_auto_open
    def extract_singlefile(self, tools=None, configuration=None, query=None):
        """
        Schedules the extraction for the image of the singlefile.
        """
        return self.connection.extract_singlefile(singlefile_id=self.project_id,
                                                  tools=tools, configuration=configuration)

    @_auto_open
    def singlefile_traces(self):
        """
        Get all traces within a singlefile.

        :return: a `Trace <hansken.trace.Trace>` stream (iterable once)
        :rtype: `.SearchResult`
        """
        fd = self.connection.singlefile_traces(singlefile_id=self.project_id)
        return SearchResult(fd, self.trace_class or dict, model=self.model,
                            # auto-resume information
                            project_id=self.project_id, connection=self.connection)

    @_auto_open
    def singlefile_tracelets(self, tracelet_type):
        """
        Get tracelets of a certain type within a singlefile, wrapping the result in an
        iterator of `DictView <hansken.util.DictView>` objects.

        :param tracelet_type: the type of tracelet to search for
        :return: a tracelet stream containing `DictView <hansken.util.DictView>` instances (iterable once)
        :rtype: `.TraceletSearchResult`
        """
        fd = self.connection.singlefile_tracelets(singlefile_id=self.project_id, tracelet_type=tracelet_type)
        return TraceletSearchResult(fd, DictView, model=self.model,
                                    project_id=self.project_id, tracelet_type=tracelet_type,
                                    connection=self.connection)

    def __repr__(self):
        return '<{0.__class__.__module__}.{0.__class__.__name__} project_id={0.project_id}>'.format(self)


class MultiProjectContext(ProjectContext):
    """
    Utility class adding a set of project ids to each rest call that
    requires them. Provided with a url to a Hansken gatekeeper and the set of ids of
    projects, methods of this class will make REST requests to the gatekeeper,
    wrapping results with a Trace class or iterator where applicable.

    MultiProjectContext instances are usable as context managers, which opens the
    context for use. Calls to methods requiring an initialized connection
    will automatically open the context if it wasn't yet opened.
    """

    def __init__(self, base_url_or_connection, project_ids, keystore_url=None, preference_url=None, auth=None,
                 auto_activate=True, connection_pool_size=None,
                 verify=True):
        # pass project ids through set(), removing duplicates, making the set available as self._project_id
        try:
            num_projects = len(project_ids)
            project_ids = set(project_ids)
            if num_projects != len(project_ids):
                log.warn('de-duplicating project ids for MultiProjectContext: {} -> {} projects',
                         num_projects, len(project_ids))
        except TypeError:
            # no len() for project_ids (maybe a generator?), no problem, but also no warning
            project_ids = set(project_ids)

        super().__init__(base_url_or_connection, project_ids, keystore_url, preference_url, auth,
                         auto_activate, connection_pool_size, verify)

    def open(self):
        self.connection.open()

        # NB: make sure to *not* hit the search index to avoid hitting a closed index
        # retrieve the *global* model
        # avoid attribute errors on model properties that are not filled for a particular project
        self.model = TraceModel(self.connection.trace_model())
        self.trace_class = trace_class_from_model(self.model)

        self.is_open = True

        return self

    def close(self):
        if self.auto_activated:
            log.warn('projects are not auto-closed in multi project context')

        self.is_open = False
        self.auto_activated = False

        self.connection.close()

        self.project = None
        self.model = None
        self.trace_class = None

        # clear any cached results
        self.key.cache_clear()

    def image(self, image_id):
        raise TypeError('method not supported in multi-project search, use a regular ProjectContext')

    def image_name(self, image_id):
        raise TypeError('method not supported in multi-project search, use a regular ProjectContext')

    def roots(self):
        raise TypeError('method not supported in multi-project search, use a regular ProjectContext')

    def trace(self, trace_uid):
        raise TypeError('method not supported in multi-project search, use a regular ProjectContext')

    def data(self, trace_uid, stream='raw', offset=0, size=None, key=fetch):
        raise TypeError('method not supported in multi-project search, use a regular ProjectContext')

    def children(self, trace_uid, query=None, start=0, count=None, sort=None, facets=None, snippets=None, timeout=None):
        raise TypeError('method not supported in multi-project search, use a regular ProjectContext')

    def note(self, trace_uid, note, refresh=None):
        raise TypeError('method not supported in multi-project search, use a regular ProjectContext')

    def tag(self, trace_uid, tag, refresh=None):
        raise TypeError('method not supported in multi-project search, use a regular ProjectContext')

    def delete_tag(self, trace_uid, tag, refresh=None):
        raise TypeError('method not supported in multi-project search, use a regular ProjectContext')

    def mark_privileged(self, trace_uid, status, refresh=None):
        raise TypeError('method not supported in multi-project search, use a regular ProjectContext')

    def child_builder(self, parent_uid):
        raise TypeError('method not supported in multi-project search, use a regular ProjectContext')

    def update_trace(self, trace, updates=None, data=None, key=fetch, overwrite=False):
        raise TypeError('method not supported in multi-project search, use a regular ProjectContext')
