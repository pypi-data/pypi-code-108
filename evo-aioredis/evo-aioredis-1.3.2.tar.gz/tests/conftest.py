import argparse
import asyncio
import pytest
import socket
import subprocess
import sys
import contextlib
import os
import ssl
import time
import inspect

from collections import namedtuple
from urllib.parse import urlencode, urlunparse
from async_timeout import timeout as async_timeout

import aioredis
import aioredis.sentinel
from aioredis.connection import parse_url

default_redis_url = 'redis://redis:6379/0'
default_redis_b_url = 'redis://redis_b:6379/0'
default_sentinel = ('redis-sentinel', 26379)

TCPAddress = namedtuple('TCPAddress', 'host port')

RedisServer = namedtuple('RedisServer',
                         'name tcp_address unixsocket version password')

SentinelServer = namedtuple('SentinelServer',
                            'name tcp_address unixsocket version masters')


# Taken from python3.9
class BooleanOptionalAction(argparse.Action):
    def __init__(
        self,
        option_strings,
        dest,
        default=None,
        type=None,
        choices=None,
        required=False,
        help=None,
        metavar=None,
    ):

        _option_strings = []
        for option_string in option_strings:
            _option_strings.append(option_string)

            if option_string.startswith("--"):
                option_string = "--no-" + option_string[2:]
                _option_strings.append(option_string)

        if help is not None and default is not None:
            help += f" (default: {default})"

        super().__init__(
            option_strings=_option_strings,
            dest=dest,
            nargs=0,
            default=default,
            type=type,
            choices=choices,
            required=required,
            help=help,
            metavar=metavar,
        )

    def __call__(self, parser, namespace, values, option_string=None):
        if option_string in self.option_strings:
            setattr(
                namespace, self.dest, not option_string.startswith("--no-"))

    def format_usage(self):
        return " | ".join(self.option_strings)

# Public fixtures


@pytest.yield_fixture
def loop():
    """Creates new event loop."""
    loop = asyncio.new_event_loop()
    if sys.version_info < (3, 8):
        asyncio.set_event_loop(loop)

    try:
        yield loop
    finally:
        if hasattr(loop, 'is_closed'):
            closed = loop.is_closed()
        else:
            closed = loop._closed   # XXX
        if not closed:
            loop.call_soon(loop.stop)
            loop.run_forever()
            loop.close()


@pytest.fixture(scope='session')
def unused_port():
    """Gets random free port."""
    def fun():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('127.0.0.1', 0))
            return s.getsockname()[1]
    return fun


@pytest.fixture
def create_connection(_closable):
    """Wrapper around aioredis.create_connection."""

    async def f(*args, **kw):
        conn = await aioredis.create_connection(*args, **kw)
        _closable(conn)
        return conn
    return f


@pytest.fixture(params=[
    aioredis.create_redis,
    aioredis.create_redis_pool],
    ids=['single', 'pool'])
def create_redis(_closable, request):
    """Wrapper around aioredis.create_redis."""
    factory = request.param

    async def f(*args, **kw):
        redis = await factory(*args, **kw)
        _closable(redis)
        return redis
    return f


@pytest.fixture
def create_pool(_closable):
    """Wrapper around aioredis.create_pool."""

    async def f(*args, **kw):
        redis = await aioredis.create_pool(*args, **kw)
        _closable(redis)
        return redis
    return f


@pytest.fixture
def config_set(request, loop):
    async def f(address, parameter, value):
        redis = await aioredis.create_redis(address)
        last_value = (await redis.config_get(parameter))[parameter]

        def finalizer():
            async def rollback_value():
                kwargs = {}
                if parameter == 'requirepass':
                    kwargs['password'] = value
                redis = await aioredis.create_redis(address, **kwargs)
                await redis.config_set(parameter, last_value)
            loop.run_until_complete(rollback_value())
        request.addfinalizer(finalizer)

        await redis.config_set(parameter, value)
    return f


@pytest.fixture
def create_sentinel(_closable):
    """Helper instantiating RedisSentinel client."""

    async def f(*args, **kw):
        # make it fail fast on slow CIs (if timeout argument is ommitted)
        kw.setdefault('timeout', .001)
        client = await aioredis.sentinel.create_sentinel(*args, **kw)
        _closable(client)
        return client
    return f


@pytest.fixture
def pool(create_pool, server, loop):
    """Returns RedisPool instance."""
    return loop.run_until_complete(create_pool(server.tcp_address))


@pytest.fixture
def redis(create_redis, server, loop):
    """Returns Redis client instance."""
    redis = loop.run_until_complete(
        create_redis(server.tcp_address))

    async def clear():
        await redis.flushall()
    loop.run_until_complete(clear())
    return redis


@pytest.fixture
def redis_b(create_redis, serverB, loop):
    """Returns Redis client instance."""
    redis = loop.run_until_complete(
        create_redis(serverB.tcp_address))

    async def clear():
        await redis.flushall()
    loop.run_until_complete(clear())
    return redis


@pytest.fixture
def redis_sentinel(create_sentinel, sentinel, loop):
    """Returns Redis Sentinel client instance."""
    redis_sentinel = loop.run_until_complete(
        create_sentinel([sentinel.tcp_address], timeout=2))

    async def ping():
        return await redis_sentinel.ping()
    assert loop.run_until_complete(ping()) == b'PONG'
    return redis_sentinel


@pytest.yield_fixture
def _closable(loop):
    conns = []

    async def close():
        waiters = []
        while conns:
            conn = conns.pop(0)
            conn.close()
            waiters.append(conn.wait_closed())
        if waiters:
            await asyncio.gather(*waiters)
    try:
        yield conns.append
    finally:
        loop.run_until_complete(close())


def _server(name, redis_url):
    connect_address, connect_options = parse_url(redis_url)

    tcp_address = TCPAddress(connect_address[0], connect_address[1])
    return RedisServer(
        name=name, tcp_address=tcp_address, unixsocket=None,
        version=VERSIONS[redis_url], password=None,
    )


@pytest.fixture(scope='session')
def server(request, start_server):
    url = request.config.getoption('--redis-url')
    return _server('master-no-fail', url)


@pytest.fixture(scope='session')
def serverB(request):
    url = request.config.getoption('--redis-b-url')
    return _server('B', url)


@pytest.fixture(scope='session')
def server_docker_address(request):
    """ Temporary solution. For communication between two redises
    (MIGRATE command) """
    redis_url = (
        request.config.getoption('--redis-docker-url')
        or request.config.getoption('--redis-url')
    )
    connect_address, connect_options = parse_url(redis_url)
    return TCPAddress(connect_address[0], connect_address[1])


@pytest.fixture(scope='session')
def serverB_docker_address(request):
    """ Temporary solution. For communication between two redises
    (MIGRATE command) """
    redis_url = (
        request.config.getoption('--redis-b-docker-url')
        or request.config.getoption('--redis-b-url')
    )
    connect_address, connect_options = parse_url(redis_url)
    return TCPAddress(connect_address[0], connect_address[1])


@pytest.fixture(scope='session')
def sentinel(start_sentinel, request, server):
    """Starts redis-sentinel instance with one master -- masterA."""
    # Adding master+slave for normal (no failover) tests:
    master_no_fail = start_server('master-no-fail')
    start_server('slave-no-fail', slaveof=master_no_fail)
    # Adding master+slave for failover test;
    masterA = start_server('masterA')
    start_server('slaveA', slaveof=masterA)
    return start_sentinel('main', server)


@pytest.fixture(params=['path', 'query'])
def server_tcp_url(server, request):

    def make(**kwargs):
        netloc = '{0.host}:{0.port}'.format(server.tcp_address)
        path = ''
        if request.param == 'path':
            if 'password' in kwargs:
                netloc = ':{0}@{1.host}:{1.port}'.format(
                    kwargs.pop('password'), server.tcp_address)
            if 'db' in kwargs:
                path = '/{}'.format(kwargs.pop('db'))
        query = urlencode(kwargs)
        return urlunparse(('redis', netloc, path, '', query, ''))
    return make


@pytest.fixture
def server_unix_url(server):

    def make(**kwargs):
        query = urlencode(kwargs)
        return urlunparse(('unix', '', server.unixsocket, '', query, ''))
    return make

# Internal stuff #


def pytest_addoption(parser):
    parser.addoption(
        '--redis-url',
        default=default_redis_url,
        action='store',
        help='Redis connection string, defaults to `%(default)s`',
    )
    parser.addoption(
        '--redis-b-url',
        default=default_redis_b_url,
        action='store',
        help='Redis (second) connection string, defaults to `%(default)s`',
    )
    parser.addoption('--redis-b-docker-url', default=None, action='store')
    parser.addoption('--redis-docker-url', default=None, action='store')
    parser.addoption('--ssl-cafile', default='tests/ssl/cafile.crt',
                     help="Path to testing SSL CA file")
    parser.addoption('--ssl-dhparam', default='tests/ssl/dhparam.pem',
                     help="Path to testing SSL DH params file")
    parser.addoption('--ssl-cert', default='tests/ssl/cert.pem',
                     help="Path to testing SSL CERT file")
    parser.addoption('--uvloop',
                     action=BooleanOptionalAction,
                     help='Run tests with uvloop')


@contextlib.contextmanager
def config_writer(path):
    with open(path, 'wt') as f:
        def write(*args):
            print(*args, file=f)
        yield write


REDIS_SERVERS = []
VERSIONS = {}


def format_version(srv):
    return 'redis_v{}'.format('.'.join(map(str, VERSIONS[srv])))


@pytest.fixture(scope='session')
def start_server(_proc, request, unused_port, server_bin):
    """Starts Redis server instance.

    Caches instances by name.
    ``name`` param -- instance alias
    ``config_lines`` -- optional list of config directives to put in config
        (if no config_lines passed -- no config will be generated,
         for backward compatibility).
    """

    url = request.config.getoption('--redis-url')
    connect_address, connect_options = parse_url(url)

    def maker(name, config_lines=None, *, slaveof=None, password=None):
        tcp_address = TCPAddress(connect_address[0], connect_address[1])
        info = RedisServer(
            name=name, tcp_address=tcp_address, unixsocket=None,
            version=VERSIONS[url], password=None,
        )
        return info

    return maker


@pytest.fixture(scope='session')
def start_sentinel(_proc, request, unused_port, server_bin):
    """Starts Redis Sentinel instances."""

    url = request.config.getoption('--redis-url')
    connect_address, connect_options = parse_url(url)
    version = VERSIONS[url]

    def maker(name, *masters, quorum=1, noslaves=False,
              down_after_milliseconds=3000,
              failover_timeout=1000):
        tcp_address = TCPAddress(default_sentinel[0], default_sentinel[1])
        return SentinelServer(
            name, tcp_address, None, version, {m.name: m for m in masters})

    return maker


@pytest.fixture(scope='session')
def ssl_proxy(_proc, request, unused_port):
    by_port = {}

    cafile = os.path.abspath(request.config.getoption('--ssl-cafile'))
    certfile = os.path.abspath(request.config.getoption('--ssl-cert'))
    dhfile = os.path.abspath(request.config.getoption('--ssl-dhparam'))
    assert os.path.exists(cafile), \
        "Missing SSL CA file, run `make certificate` to generate new one"
    assert os.path.exists(certfile), \
        "Missing SSL CERT file, run `make certificate` to generate new one"
    assert os.path.exists(dhfile), \
        "Missing SSL DH params, run `make certificate` to generate new one"

    ssl_ctx = ssl.create_default_context(cafile=cafile)
    ssl_ctx.check_hostname = False
    ssl_ctx.verify_mode = ssl.CERT_NONE
    ssl_ctx.load_dh_params(dhfile)

    def sockat(unsecure_port):
        if unsecure_port in by_port:
            return by_port[unsecure_port]

        secure_port = unused_port()
        _proc('/usr/bin/socat',
              'openssl-listen:{port},'
              'dhparam={param},'
              'cert={cert},verify=0,fork'
              .format(port=secure_port, param=dhfile, cert=certfile),
              'tcp-connect:localhost:{}'
              .format(unsecure_port)
              )
        time.sleep(1)   # XXX
        by_port[unsecure_port] = secure_port, ssl_ctx
        return secure_port, ssl_ctx

    return sockat


@pytest.yield_fixture(scope='session')
def _proc():
    processes = []
    tmp_files = set()

    def run(*commandline, _clear_tmp_files=(), **kwargs):
        proc = subprocess.Popen(commandline, **kwargs)
        processes.append(proc)
        tmp_files.update(_clear_tmp_files)
        return proc

    try:
        yield run
    finally:
        while processes:
            proc = processes.pop(0)
            proc.terminate()
            proc.wait()
        for path in tmp_files:
            try:
                os.remove(path)
            except OSError:
                pass


@pytest.mark.tryfirst
def pytest_pyfunc_call(pyfuncitem):
    """
    Run asyncio marked test functions in an event loop instead of a normal
    function call.
    """
    if inspect.iscoroutinefunction(pyfuncitem.obj):
        marker = pyfuncitem.get_closest_marker('timeout')
        if marker is not None and marker.args:
            timeout = marker.args[0]
        else:
            timeout = 15

        funcargs = pyfuncitem.funcargs
        loop = funcargs['loop']
        testargs = {arg: funcargs[arg]
                    for arg in pyfuncitem._fixtureinfo.argnames}

        loop.run_until_complete(
            _wait_coro(pyfuncitem.obj, testargs, timeout=timeout))
        return True


async def _wait_coro(corofunc, kwargs, timeout):
    with async_timeout(timeout):
        return (await corofunc(**kwargs))


def pytest_runtest_setup(item):
    is_coro = inspect.iscoroutinefunction(item.obj)
    if is_coro and 'loop' not in item.fixturenames:
        # inject an event loop fixture for all async tests
        item.fixturenames.append('loop')


def pytest_collection_modifyitems(session, config, items):
    skip_by_version = []
    for item in items[:]:
        marker = item.get_closest_marker('redis_version')
        if marker is not None:
            try:
                version = VERSIONS[item.callspec.getparam('server_bin')]
            except (KeyError, ValueError, AttributeError):
                # TODO: throw noisy warning
                continue
            if version < marker.kwargs['version']:
                skip_by_version.append(item)
                item.add_marker(pytest.mark.skip(
                    reason=marker.kwargs['reason']))
        if 'ssl_proxy' in item.fixturenames:
            item.add_marker(pytest.mark.skipif(
                "not os.path.exists('/usr/bin/socat')",
                reason="socat package required (apt-get install socat)"))
    if len(items) != len(skip_by_version):
        for i in skip_by_version:
            items.remove(i)


async def _get_info(redis_url):
    redis = await aioredis.create_redis(redis_url)
    info = await redis.info()
    redis.close()
    await redis.wait_closed()
    return info


def pytest_configure(config):
    loop = asyncio.get_event_loop()
    REDIS_SERVERS[:] = [
        config.getoption('--redis-url'),
        config.getoption('--redis-b-url'),
    ]
    for redis_url in REDIS_SERVERS:
        info = loop.run_until_complete(_get_info(redis_url))
        version = info['server']['redis_version']
        VERSIONS[redis_url] = tuple(map(int, version.split('.')))

    class DynamicFixturePlugin:
        @pytest.fixture(scope='session',
                        params=REDIS_SERVERS,
                        ids=format_version)
        def server_bin(self, request):
            """Common for start_server and start_sentinel
            server bin path parameter.
            """
            return request.param
    config.pluginmanager.register(DynamicFixturePlugin(), 'server-bin-fixture')

    if config.getoption('--uvloop'):
        try:
            import uvloop
        except ImportError:
            raise RuntimeError(
                "Can not import uvloop, make sure it is installed")
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
