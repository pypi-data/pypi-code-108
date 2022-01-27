# Copyright (c) AppDynamics, Inc., and its affiliates
# 2015
# All Rights Reserved

"""Utilities for AppDynamics Python code.

"""

from __future__ import unicode_literals
from collections import Mapping
import errno
from itertools import chain
from logging import Formatter
import ast
import os
import sys
import random
import time
from uuid import uuid4
import wsgiref.util

from appdynamics.lang import items, parse_qsl, SimpleCookie, str, thread

default_log_formatter = Formatter('%(asctime)s [%(levelname)s] %(name)s <%(process)d>: %(message)s')
structlog_formatter = Formatter('%(message)s')

# get_ident will fallback to greenlets if asyncio is not available
# If greenlets isn't available either, get_ident fallbacks to thread.get_ident
get_ident = thread.get_ident
# set_ident will do nothing for greenlets and thread implementation of get_ident
# For contextvars implementation, set_ident sets the contextvar to current context
# set_ident should be called just before creating a new bt, otherwise the bt will be
# created in the parent's context
set_ident = lambda: None
GREENLETS_ENABLED = False
try:
    import greenlet
    get_ident = lambda: hash(greenlet.getcurrent())
    GREENLETS_ENABLED = True
except ImportError:
    pass
if sys.version_info >= (3, 5, 3):
    try:
        from appdynamics.agent.core.context import ContextVar, get_state
        curr_context = ContextVar('active_context')
        _get_state = lambda: id(get_state())
        curr_context.set(_get_state())

        set_ident = lambda: curr_context.set(_get_state())
        get_ident = lambda: hash(curr_context.get(None))
    except ImportError:
        pass


class Counter(dict):
    """A minimal version of collections.Counter.

    Counter was added in Python 2.7. Its implementation is no
    more efficient than this, so we may as well just use our
    own minimalist version always.

    """
    def __init__(self, iterable=None, **kwargs):
        super(Counter, self).__init__()
        self.update(iterable, **kwargs)

    def update(self, iterable=None, **kwargs):
        if iterable is not None:
            _get = self.get
            if isinstance(iterable, Mapping):
                if not self:
                    super(Counter, self).update(iterable)
                else:
                    for k, count in items(iterable):
                        self[k] = _get(k, 0) + count
            else:
                for elt in iterable:
                    self[elt] = _get(elt, 0) + 1
        if kwargs:
            self.update(kwargs)

    def __missing__(self, key):
        return 0


def make_uuid():
    return uuid4().hex


_RNG = None


def get_rng():
    """Get the random number generator.

    This attempts to use the SystemRandom generator backed by urandom if it's
    available. Otherwise, it uses Random with a seed that is the current
    time mixed with the PID. This fallback should work fine (although we warn
    abou)

    We generate a warning when we don't have SystemRandom, but Random should
    actually work fine given that we aren't sharing the same seed across
    processes.

    """
    global _RNG

    if _RNG is None:
        try:
            _RNG = random.SystemRandom()
            _RNG.random()
        except NotImplementedError:
            seed = os.getpid() ^ int(time.time() * 1000)

            import logging
            logger = logging.getLogger('appdynamics')
            logger.warning('os.urandom unavailable; falling back to random.Random with seed %d', seed)

            _RNG = random.Random(seed)

    return _RNG


_MAX_RANDOM_ID = 2**63 - 1


def make_random_id():
    rng = get_rng()
    random_id = rng.randint(1, _MAX_RANDOM_ID)
    return random_id


def search(pred, items, default=None):
    for item in items:
        if pred(item):
            return item
    return default


def set_fields(obj, **kwargs):
    for k, v in items(kwargs):
        setattr(obj, k, v)
    return obj


def getenv(envkey, default, mapper=None):
    value = os.getenv(envkey, default)

    if mapper and value is not None:
        try:
            value = mapper(value)
        except:
            value = default

    return value


def normalize_header(hdr):
    """Normalize a header name.

    Normalization involves stripping leading and trailing spaces, turning
    underscores into dashes, and lowercasing the name.

    NOTE: WSGI headers come in like "HTTP_USER_AGENT". The caller is
    responsible for removing the "HTTP_" prefix before normalizing the header.

    """
    return hdr.strip().lower().replace('_', '-')


class LazyWsgiRequest(object):
    """Lazily read request line and headers from a WSGI environ.

    This matches enough of the Werkzeug Request API for the agent's needs: it
    only provides access to the information in the request line and the
    headers that is needed for the agent. (Since the agent doesn't inspect
    the request body, we don't touch any of that.)

    Parameters
    ----------
    environ : dict
        A WSGI environment.

    Attributes
    ----------
    headers : dict
        A dictionary of the HTTP headers. The headers are lowercase with
        dashes separating words.
    method : str
        The request method (e.g., GET).
    url : str
        The URL of the request (reconstructed according to PEP 333).
    cookies : dict
        The cookies passed in the request header (if any).
    path : str
        The path part of the request. Note that unlike raw WSGI, this will be
        just '/' if it would otherwise be empty.
    args : dict
        The query parameters. This is not a multi-dict: if a parameter is
        repeated multiple times, one of them wins.
    referer : str
        The HTTP Referer string.
    user_agent : str
        The HTTP User-Agent string.
    is_ajax : bool
        True if this request is AJAX.
    is_mobile : bool
        True if this request is from mobile.

    """
    DEFAULT_PORTS = {
        'http': 80,
        'https': 443,
    }

    def __init__(self, environ):
        super(LazyWsgiRequest, self).__init__()
        self.environ = environ.copy()

        self._headers = None
        self._host = None
        self._port = None
        self._http_host = None
        self._url = None
        self._path = None
        self._args = None
        self._cookies = None

    @property
    def headers(self):
        if self._headers is not None:
            return self._headers

        headers = {}
        for key, value in items(self.environ):
            if key.startswith('HTTP_'):
                header_name = normalize_header(key[5:])
                headers[header_name] = value

        self._headers = headers
        return headers

    @property
    def method(self):
        return self.environ['REQUEST_METHOD']

    @property
    def is_secure(self):
        return self.environ['wsgi.url_scheme'] == 'https'

    @property
    def host(self):
        if self._host is None:
            host = self.environ.get('HTTP_X_FORWARDED_HOST')

            if host:
                self._host = host.split(',')[0].strip()
            else:
                self._host = self.environ.get('HTTP_HOST')

            if self._host is None:
                host = self.environ['SERVER_NAME']
                port = str(self.environ['SERVER_PORT'])

                if (self.environ['wsgi.url_scheme'], port) not in (('http', '80'), ('https', '443')):
                    self._host = '%s:%s' % (host, port)
                else:
                    self._host = host

        return self._host

    @property
    def url(self):
        if self._url is None:
            self._url = wsgiref.util.request_uri(self.environ)
        return self._url

    @property
    def cookies(self):
        if self._cookies is not None:
            return self._cookies

        cookies = {}
        cookie_header = self.environ.get('HTTP_COOKIE', None)

        if cookie_header:
            cookie_jar = SimpleCookie()

            try:
                cookie_jar.load(cookie_header)
            except:
                self._cookies = {}
                return self._cookies

            for name in cookie_jar:
                cookies[name] = cookie_jar[name].value

        self._cookies = cookies
        return cookies

    @property
    def path(self):
        # request's url path is composed of SCRIPT_NAME and PATH_INFO
        # reference: https://wsgi.readthedocs.io/en/latest/definitions.html
        if self._path is not None:
            return self._path

        script_name = self.environ.get('SCRIPT_NAME', '')
        path_info = self.environ.get('PATH_INFO', '')

        # add a forward / in path_info if it doesn't exist
        if path_info and path_info[0] != '/':
            path_info = '/' + path_info

        self._path = script_name + path_info or '/'
        return self._path

    @property
    def args(self):
        if self._args is not None:
            return self._args

        query_string = self.environ.get('QUERY_STRING', '')
        self._args = dict((k, v) for k, v in parse_qsl(query_string))
        return self._args

    @property
    def referer(self):
        return self.environ.get('HTTP_REFERER')

    @property
    def user_agent(self):
        return self.environ.get('HTTP_USER_AGENT')

    @property
    def is_ajax(self):
        rum_header = self.environ.get('HTTP_ADRUM')
        if rum_header and 'isAjax:true' in rum_header:
            return True
        x_requested_header = self.environ.get('HTTP_X_REQUESTED_WITH')
        if x_requested_header == 'XMLHttpRequest':
            return True
        return False

    @property
    def is_mobile(self):
        rum_header = self.environ.get('HTTP_ADRUM_1')
        return rum_header and 'isMobile:true' in rum_header

    @property
    def server_port(self):
        return self.environ['SERVER_PORT']


def get_request_host_and_port(request):
    """Return a tuple of the host and port from an incoming HTTP request.

    Parameters
    ----------
    request : request-like object
        The request must have `environ` and `host` attributes with the same
        meaning as those attributes in Werkzeug's BaseRequest class.

    Returns
    -------
    (host, port)
        The host and the port. The port is set even if it's the default for
        requests of this scheme.

    """
    host = request.host
    port = None

    if ':' in host:
        host, port = host.split(':', 1)

    return host, (port or request.server_port)


def make_name_value_pairs(*dicts):
    """Convert dicts into a list of name value pairs for use in a 'Common.NameValuePair' protobuf field.

    """

    result = []
    for item in dicts:
        result.extend([
            dict(name=str(k), value=str(v))
            for k, v in items(item)
        ])
    return result


def parse_args(args, kwargs):
    """Convert function arguments into a neat string.

    e.g.
       def foo(*args, **kwargs):
           print(parse_args(args, kwargs))

       info = {'name': 'Dan', 'beard': True}
       foo(info, expires='2015-03-18')

    would print "{'name': 'Dan', 'beard': True}, expires='2015-03-18'"

    """
    args = (repr(x) for x in args)
    kwargs = ('%s=%r' % x for x in items(kwargs))
    return ', '.join(chain(args, kwargs))


def mkdir(path):
    """Create the directory in path, creating any intermediate directories.

    Does not complain if the directory already exists.

    """
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise


def get_tcp_addr(host, port):
    return 'tcp://%s:%s' % (host, port)


def get_ipc_addr(base_addr, socket_name):
    return 'ipc://%s/%s' % (base_addr, socket_name)


def _get_ast_node_value(node):
    """
    Gets value of the ast node passed as parameter
    This was added to handle the inconsistencies in the format of how node values
    are packed inside the node between <3.8, 3.8 and >3.8

    Only Num, Str and Bytes are supported values to be passed as method parameters in getter_chains
    """
    if isinstance(node, ast.Num):
        return node.n
    elif isinstance(node, ast.Str):
        return node.s
    elif isinstance(node, ast.Bytes):
        return node.s
    if hasattr(ast, 'Constant'):
        # ast.Constant was introduced in 3.8 and from 3.9 it'll be always used instead of Num,
        # Str or other primitives
        if isinstance(node, ast.Constant):
            return node.value
    return node


def execute_getter_chain(obj, getter_str):
    """
    Executes the getter chain on the obj passed as parameter
    getter_str: getter chain as a string (eg. getString().name.last_name[0])

    Returns getter_str called on the object
    eg. if obj is bank and getter_str is getBranch().next.getEmployees()[0].name
    will return bank.getBranch().next.getEmployees()[0].name

    NOTE - Doesn't handle exceptions, exceptions have to be handled by the caller
    """
    if not getter_str:
        return obj

    # will change as the getter_str is parsed
    # eg for getter_str a.name.test()
    # 1st iteration = a.name
    # 2nd iteration = a.name.test
    # 3rd iteration = a.name.test()
    current_obj = obj

    tree = reversed([node for node in ast.walk(ast.parse('obj' + getter_str)) if
                    isinstance(node, (ast.Attribute, ast.Call, ast.Subscript))])

    for node in tree:
        if isinstance(node, ast.Call):
            # Calling current_obj
            args = [_get_ast_node_value(c) for c in node.args]
            kwargs = {kw.arg: _get_ast_node_value(kw.value) for kw in node.keywords}
            current_obj = current_obj(*args, **kwargs)

        elif isinstance(node, ast.Attribute):
            # Accessing property of current_obj
            current_obj = getattr(current_obj, node.attr)

        elif isinstance(node, ast.Subscript):
            # Accessing index of current_obj
            subscript_slice = _get_ast_node_value(node.slice.value)
            current_obj = current_obj[subscript_slice]

    return current_obj


class MissingConfigException(Exception):
    pass


def validate_file_permissions(file_path, octal_mask, check_only_given_permissions=False):
    """
    Check file permissions with given path

    :param file_path: absolute file path
    :param octal_mask: octal number denoting the file permissions
    :param check_only_given_permissions: set true if just want to check the specific permissions
    Eg. file with permissions 0o640 will return False for octal_mask 0o240 when check_only_given_permissions is False,
    but it will return True if check_only_given_permissions is True because 0o240 checks for Write permission for Owner
    and Read permission for Group both of which are available to the file.
    """
    if not os.path.exists(file_path):
        return False
    filePermissions = os.stat(file_path).st_mode & 0o777
    if check_only_given_permissions:
        return (filePermissions & octal_mask) == octal_mask
    else:
        return filePermissions == octal_mask
