"""
    lager_cli.util

    Catchall for utility functions
"""
import sys
import math
from distutils.version import StrictVersion
import pathlib
import enum
import os
import json
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED
from io import BytesIO
import yaml
import requests
import click
import trio
import lager_trio_websocket as trio_websocket
import wsproto.frame_protocol as wsframeproto
from .matchers import iter_streams
from .safe_unpickle import restricted_loads
from .exceptions import OutputFormatNotSupported
from . import __version__


FAILED_TO_RETRIEVE_EXIT_CODE = -1
SIGTERM_EXIT_CODE = 124
SIGKILL_EXIT_CODE = 137

def stream_output(response, chunk_size=1):
    """
        Stream an http response to stdout
    """
    for chunk in response.iter_content(chunk_size=chunk_size):
        click.echo(chunk, nl=False)
        sys.stdout.flush()

EXIT_FILENO = -1
STDOUT_FILENO = 1
STDERR_FILENO = 2
OUTPUT_CHANNEL_FILENO = 3

def stdout_is_stderr():
    """
        Determine if stdout and stderr are going to the same place
    """
    return os.stat(STDOUT_FILENO) == os.stat(STDERR_FILENO)

class StreamDatatypes(enum.Enum):
    """
        The various chunks that can be returned by Lager python
    """
    EXIT = enum.auto()
    STDOUT = enum.auto()
    STDERR = enum.auto()
    OUTPUT = enum.auto()

    def __repr__(self):
        return '<%s.%s>' % (self.__class__.__name__, self.name)

def identity(x):
    return x

class OutputHandler:
    def __init__(self):
        self.encoder = None
        self.len = None
        self.buffer = b''

    DECODERS = {
        1: identity,
        2: restricted_loads,
        3: json.loads,
        4: yaml.safe_load,
    }

    def parse(self):
        while True:
            if self.encoder is None:
                parts = self.buffer.split(b' ', 1)
                if len(parts) == 1:
                    break
                self.encoder = int(parts[0], 10)
                self.buffer = parts[1]

            if self.len is None:
                parts = self.buffer.split(b' ', 1)
                if len(parts) == 1:
                    break
                self.len = int(parts[0], 10)
                self.buffer = parts[1]

            if len(self.buffer) >= self.len:
                encoded = self.buffer[:self.len]
                decoder = self.DECODERS[self.encoder]
                self.buffer = self.buffer[self.len:]
                self.encoder = None
                self.len = None
                yield (StreamDatatypes.OUTPUT, decoder(encoded))

    def receive(self, chunk):
        self.buffer += chunk
        yield from self.parse()


def stream_python_output_v1(response, output_handler=None):
    if output_handler is None:
        output_handler = OutputHandler()

    for (fileno, chunk) in iter_streams(response):
        if fileno == EXIT_FILENO:
            yield (StreamDatatypes.EXIT, int(chunk.decode(), 10))

        if fileno == STDOUT_FILENO:
            yield (StreamDatatypes.STDOUT, chunk)
        elif fileno == STDERR_FILENO:
            yield (StreamDatatypes.STDERR, chunk)
        elif fileno == OUTPUT_CHANNEL_FILENO:
            yield from output_handler.receive(chunk)

def stream_python_output(response, output_handler=None):
    version = response.headers.get('Lager-Output-Version')
    if version == '1':
        yield from stream_python_output_v1(response, output_handler)
    else:
        raise OutputFormatNotSupported

async def heartbeat(websocket, timeout, interval):
    '''
    Send periodic pings on WebSocket ``ws``.

    Wait up to ``timeout`` seconds to send a ping and receive a pong. Raises
    ``TooSlowError`` if the timeout is exceeded. If a pong is received, then
    wait ``interval`` seconds before sending the next ping.

    This function runs until cancelled.

    :param ws: A WebSocket to send heartbeat pings on.
    :param float timeout: Timeout in seconds.
    :param float interval: Interval between receiving pong and sending next
        ping, in seconds.
    :raises: ``ConnectionClosed`` if ``ws`` is closed.
    :raises: ``TooSlowError`` if the timeout expires.
    :returns: This function runs until cancelled.
    '''
    try:
        while True:
            with trio.fail_after(timeout):
                await websocket.ping()
            await trio.sleep(interval)
    except trio_websocket.ConnectionClosed as exc:
        if exc.reason is None:
            return
        if exc.reason.code != wsframeproto.CloseReason.NORMAL_CLOSURE or exc.reason.reason != 'EOF':
            raise


def handle_error(error):
    """
        os.walk error handler, just raise it
    """
    raise error

class SizeLimitExceeded(RuntimeError):
    """
        Raised if zip file size limit exceeded
    """


def zip_dir(root, max_content_size=math.inf):
    """
        Zip a directory into memory
    """
    rootpath = pathlib.Path(root)
    exclude = ['.git']
    archive = BytesIO()
    total_size = 0
    with ZipFile(archive, 'w') as zip_archive:
        # Walk once to find and exclude any python virtual envs
        for (dirpath, dirnames, filenames) in os.walk(root, onerror=handle_error):
            for name in filenames:
                full_name = os.path.join(dirpath, name)
                if 'pyvenv.cfg' in full_name:
                    exclude.append(os.path.relpath(os.path.dirname(full_name)))

        # Walk again to grab everything that's not excluded
        for (dirpath, dirnames, filenames) in os.walk(root, onerror=handle_error):
            dirnames[:] = [d for d in dirnames if not d.startswith(tuple(exclude))]

            for name in filenames:
                if name.endswith('.pyc'):
                    continue
                full_name = pathlib.Path(dirpath) / name
                total_size += os.path.getsize(full_name)
                if total_size > max_content_size:
                    raise SizeLimitExceeded

                fileinfo = ZipInfo(str(full_name.relative_to(rootpath)))
                with open(full_name, 'rb') as f:
                    zip_archive.writestr(fileinfo, f.read(), ZIP_DEFLATED)
    return archive.getbuffer()


_VERSION_MESSAGE = """WARNING: You are using {package_name} version {this_version}; however, version {newest_version} is available.
You should consider upgrading via the 'pip install -U {package_name}' command."""


def check_version(package_name, current_version):
    """
    Check whether `package_name` has a version available that is newer than `current_version`
    """
    url = 'https://pypi.org/pypi/{package_name}/json'.format(package_name=package_name)
    this_version = StrictVersion(current_version)
    try:
        data = requests.get(url, timeout=(3, 3)).json()
        newest_version = max(StrictVersion(key) for key in data["releases"].keys())
        if this_version < newest_version:
            formatted_message = _VERSION_MESSAGE.format(
                package_name=package_name,
                this_version=this_version,
                newest_version=newest_version)
            click.secho(formatted_message, err=True, fg='yellow')
    except Exception as exc:
        pass
