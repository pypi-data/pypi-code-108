# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os.path as osp
import logging, subprocess, os, glob, time, datetime, argparse
from contextlib import contextmanager

N_COPY_ATTEMPTS = 1
DEFAULT_LOGGING_LEVEL = logging.WARNING
N_SECONDS_SLEEP = 10

INCLUDE_DIR = osp.join(osp.abspath(osp.dirname(__file__)), "include")

def version():
    with open(osp.join(INCLUDE_DIR, "VERSION"), "r") as f:
        return(f.read().strip())

def setup_logger(name='seutils'):
    if name in logging.Logger.manager.loggerDict:
        logger = logging.getLogger(name)
        logger.info('Logger %s is already defined', name)
    else:
        fmt = logging.Formatter(
            fmt = (
                '\033[33m%(levelname)7s:%(asctime)s:%(module)s:%(lineno)s\033[0m'
                + ' %(message)s'
                ),
            datefmt='%Y-%m-%d %H:%M:%S'
            )
        handler = logging.StreamHandler()
        handler.setFormatter(fmt)
        logger = logging.getLogger(name)
        logger.setLevel(DEFAULT_LOGGING_LEVEL)
        logger.addHandler(handler)
    return logger
logger = setup_logger()

def debug(flag=True):
    """Sets the logger level to debug (for True) or warning (for False)"""
    logger.setLevel(logging.DEBUG if flag else DEFAULT_LOGGING_LEVEL)

DRYMODE = False
def drymode(flag=True):
    global DRYMODE
    DRYMODE = flag

@contextmanager
def drymode_context(flag=True):
    global DRYMODE
    _saved_DRYMODE = DRYMODE
    DRYMODE = flag
    try:
        yield DRYMODE
    finally:
        DRYMODE = _saved_DRYMODE

def is_string(string):
    """
    Checks strictly whether `string` is a string
    Python 2/3 compatibility (https://stackoverflow.com/a/22679982/9209944)
    """
    try:
        basestring
    except NameError:
        basestring = str
    return isinstance(string, basestring)

ENV = None
def set_env(env):
    """
    Sets the env in which command line arguments are ran by default
    """
    global ENV
    ENV = env

@contextmanager
def env_context(env):
    """
    Temporarily sets an environment, and then reverts to the old environment
    """
    global ENV
    old_ENV = ENV
    ENV = env
    try:
        yield None
    finally:
        ENV = old_ENV

def add_env_kwarg(fn):
    """
    Function decorator that gives the function the `env` keyword argument
    """
    def wrapper(*args, **kwargs):
        if 'env' in kwargs:
            with env_context(kwargs.pop('env')):
                return fn(*args, **kwargs)
        else:
            return fn(*args, **kwargs)
    return wrapper

RM_BLACKLIST = [
    '/',
    '/store',
    '/store/user',
    '/store/user/*',
    ]
RM_WHITELIST = []

def rm_safety(fn):
    """
    Safety wrapper around any rm function: Raise an exception for some paths
    """
    import re
    def wrapper(*args, **kwargs):
        path = args[1]
        if not has_protocol(path):
            logger.error('Remote rm operation called on local path')
            raise RmSafetyTrigger(path)
        path = split_mgm(normpath(path))[1]
        depth = path.count('/')
        logger.debug('In rm_safety wrapper')
        # Check if the passed `path` is in the blacklist:
        for bl_path in RM_BLACKLIST:
            if bl_path == path:
                raise RmSafetyTrigger(path)
            elif bl_path.count('/') != depth:
                continue
            elif re.match(bl_path.replace('*', '.*'), path):
                raise RmSafetyTrigger(path)
        # Check if the passed `path` is in the whitelist:
        if RM_WHITELIST:
            for wl_path in RM_WHITELIST:
                if path.startswith(wl_path):
                    break
            else:
                logger.error('Path is outside of the whitelist: ' + ', '.join(RM_WHITELIST))
                raise RmSafetyTrigger(path)
        return fn(*args, **kwargs)
    return wrapper

def listdir_check_isdir(fn):
    """
    Wrapper around listdir implementations, that first checks if the directory exists
    """
    def wrapper(*args, **kwargs):
        if not kwargs.pop('assume_isdir', False):
            if not args[0].isdir(args[1]):
                raise Exception('Cannot listdir {0}: not a directory'.format(args[1]))
        return fn(*args, **kwargs)
    return wrapper

def run_command_rcode_and_output(cmd, env=None, dry=None):
    """Runs a command and captures output.
    Returns return code and captured output.
    """
    if dry is None: dry = DRYMODE
    if env is None: env = ENV
    logger.info('%sIssuing command %s', '(dry) ' if dry else '', ' '.join(cmd))
    if dry: return 0, '<dry output>'
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=env,
        universal_newlines=True,
        )
    # Start running command and capturing output
    output = []
    for stdout_line in iter(process.stdout.readline, ''):
        logger.debug('CMD: ' + stdout_line.strip('\n'))
        output.append(stdout_line)
    process.stdout.close()
    process.wait()
    return process.returncode, output

def run_command_rcode_and_output_with_retries(cmd, *args, **kwargs):
    """
    Wrapper around run_command_rcode_and_output that repeats on a non-zero exit code
    """
    n_attempts = kwargs.pop('n_attempts', 1)
    for i_attempt in range(n_attempts):
        if n_attempts > 1:
            logger.info(
                'Running command %s with retries: attempt %s of %s',
                cmd, i_attempt+1, n_attempts
                )
        rcode, output = run_command_rcode_and_output(cmd, *args, **kwargs)
        if rcode != 0:
            return rcode, output
        if n_attempts > 1:
            logger.info(
                'Return code %s for attempt %s of %s',
                rcode, i_attempt+1, n_attempts
                )
        if i_attempt+1 < n_attempts: time.sleep(N_SECONDS_SLEEP)
    else:
        if n_attempts > 1: logger.info('Non-zero return code after %s attempt(s)!', n_attempts)
        return rcode, output

def run_command(cmd, *args, **kwargs):
    """
    Main entrypoint for implementations.
    Raises an exception on non-zero exit codes.

    If `path` is specified as a keyword argument, it is used for a more descriptive
    exception, but otherwise it is not used.
    """
    rcodes = kwargs.pop('rcodes', {})
    path = kwargs.pop('path', '')
    rcode, output = run_command_rcode_and_output_with_retries(cmd, *args, **kwargs)
    if rcode == 0:
        logger.info('Command exited with status 0 - all good')
        return output
    else:
        logger.error(
            '\033[31mExit status {0} for command {1}\nOutput:\n{2}\033[0m'
            .format(rcode, cmd, '\n'.join(output))
            )
        if rcode in rcodes:
            raise rcodes[rcode](path)
        else:
            raise NonZeroExitCode(rcode, cmd)

def get_exitcode(cmd, *args, **kwargs):
    """
    Runs a command and returns the exit code.
    """
    rcode, _ = run_command_rcode_and_output(cmd, *args, **kwargs)
    logger.debug('Got exit code %s', rcode)
    return rcode

def bytes_to_human_readable(num, suffix='B'):
    """
    Convert number of bytes to a human readable string
    """
    for unit in ['','k','M','G','T','P','E','Z']:
        if abs(num) < 1024.0:
            return '{0:3.1f} {1}b'.format(num, unit)
        num /= 1024.0
    return '{0:3.1f} {1}b'.format(num, 'Y')

def is_macos():
    """
    Checks if the platform is Mac OS
    """
    return os.uname()[0] == 'Darwin'

# _______________________________________________________
# Path management

DEFAULT_MGM = None
MGM_ENV_KEY = 'SEU_DEFAULT_MGM'

def set_default_mgm(mgm):
    """
    Sets the default mgm
    """
    global DEFAULT_MGM
    DEFAULT_MGM = mgm
    logger.info('Default mgm set to %s', mgm)

def read_default_mgm_from_env():
    if MGM_ENV_KEY in os.environ: set_default_mgm(os.environ[MGM_ENV_KEY])
# Set the default once at import time
read_default_mgm_from_env()

def get_default_mgm():
    if DEFAULT_MGM is None:
        raise RuntimeError(
            'A request relied on the default mgm to be set. '
            'Either use `seutils.set_default_mgm` or '
            'pass use the full path (starting with "root:") '
            'in your request.'
            )
    return DEFAULT_MGM

PROTOCOLS = [ 'root', 'srm', 'gsiftp', 'dcap' ] # Probably to be expanded

def has_protocol(filename):
    """
    Checks whether the filename contains a protocol.
    Currently a very basic string check, which so far has been enough
    """
    return ('://' in filename)

def is_ssh(path):
    return (':/' in path and not('://' in path))

def split_protocol_pfn(filename):
    """
    Splits protocol, server and logical file name from a physical file name.
    Throws an exception of format-ensuring checks fail.
    """
    if not has_protocol(filename):
        raise ValueError(
            'Attempted to get protocol from {0}, but there'
            ' does not seem to be any.'
            .format(filename)
            )
    protocol, rest = filename.split('://',1)
    if not '//' in rest:
        raise ValueError(
            'Could not determine server and logical file name from {0}'
            .format(filename)
            )
    server, lfn = rest.split('//',1)
    lfn = '/' + lfn # Restore the opening slash that was dropped in the split
    return protocol, server, lfn

def _split_mgm_pfn(filename):
    """
    Splits mgm and logical file name from a physical file name.
    Throws an exception of format-ensuring checks fail.
    """
    protocol, server, lfn = split_protocol_pfn(filename)
    return protocol + '://' + server, lfn

def _join_protocol_server_lfn(protocol, server, lfn):
    """
    Joins protocol, server and lfn into a physical filename.
    Ensures formatting to some extent.
    """
    protocol = protocol.replace(':', '') # Remove any ':' from the protocol
    server = server.strip('/') # Strip trailing or opening slashes
    if not lfn.startswith('/'):
        raise ValueError(
            'Logical file name {0} does not seem to be formatted correctly'
            .format(lfn)
            )
    return protocol + '://' + server + '/' + lfn

def split_mgm(path, mgm=None):
    """
    Returns the mgm and lfn that the user most likely intended to
    if path has a protocol string (e.g. 'root://...'), the mgm is taken from the path
    if mgm is passed, it is used as is
    if mgm is passed AND the path starts with 'root://' AND the mgm's don't agree,
      an exception is thrown
    if mgm is None and path has no mgm, the default variable DEFAULT_MGM is taken
    """
    if has_protocol(path):
        mgm_from_path, lfn = _split_mgm_pfn(path)
        if not(mgm is None) and not mgm_from_path == mgm:
            raise ValueError(
                'Conflicting mgms determined from path and passed argument: '
                'From path {0}: {1}, from argument: {2}'
                .format(path, mgm_from_path, mgm)
                )
        mgm = mgm_from_path
    elif mgm is None:
        mgm = get_default_mgm()
        lfn = path
    else:
        lfn = path
    # Sanity check
    if not lfn.startswith('/'):
        raise ValueError(
            'LFN {0} does not start with \'/\'; something is wrong'
            .format(lfn)
            )
    return mgm, lfn

def _join_mgm_lfn(mgm, lfn):
    """
    Joins mgm and lfn, ensures correct formatting.
    Will throw an exception of the lfn does not start with '/'
    """
    if not lfn.startswith('/'):
        raise ValueError(
            'This function expects filenames that start with \'/\''
            )
    if not mgm.endswith('/'): mgm += '/'
    # logger.error('mgm=%s lfn=%s', mgm, lfn)
    return mgm + lfn

def format(path, mgm=None):
    """
    Formats a path to ensure it is a path on the SE.
    Can take:
    - Just path starting with 'root:' - nothing really happens
    - Just path starting with '/' - the default mgm is used
    - Path starting with 'root:' and an mgm - an exception is thrown in case of conflict
    - Path starting with '/' and an mgm - mgm and path are joined
    """
    if is_ssh(path): return path
    mgm, lfn = split_mgm(path, mgm=mgm)
    lfn = osp.normpath(lfn)
    return _join_mgm_lfn(mgm, lfn)

def dirname(path):
    """
    Like osp.dirname, but works with an mgm.
    """
    is_remote = has_protocol(path)
    if is_remote:
        mgm, path = split_mgm(path)
    path = osp.dirname(osp.normpath(path))
    return format(path, mgm) if is_remote else path

def normpath(path):
    """
    Like osp.normpath, but works with an mgm.
    """
    is_remote = has_protocol(path)
    if is_remote:
        mgm, path = split_mgm(path)
    path = osp.normpath(path)
    return format(path, mgm) if is_remote else path

def relpath(path, start):
    """
    Like osp.relpath, but works with an mgm.
    """
    if has_protocol(path) != has_protocol(start):
        raise TypeError('{0} / {1}: either both or neither must have mgms'.format(path, start))
    mgm1 = ''
    mgm2 = ''
    if has_protocol(path): mgm1, path = split_mgm(path)
    if has_protocol(start): mgm2, start = split_mgm(start)
    if mgm1 != mgm2:
        raise TypeError('mgm mismatch: {0} vs. {1}'.format(mgm1, mgm2))
    path = osp.normpath(path)
    return osp.relpath(path, start)

def iter_parent_dirs(path):
    """
    Iterates through all the parent directories of a path
    E.g.:
    `'/foo/bar'` --> `['/foo', '/']`
    """
    dir = dirname(path)
    previous_dir = None
    while dir != previous_dir:
        yield dir
        previous_dir = dir
        dir = dirname(dir)

def get_protocol(path, mgm=None):
    """
    Returns the protocol contained in the path string
    """
    path = format(path, mgm)
    return path.split('://')[0]

def cmd_exists(executable):
    """
    Checks if a command can be found on the system path.
    Not a very smart implementation but does the job usually.
    See https://stackoverflow.com/a/28909933/9209944 .
    """
    return any(os.access(os.path.join(path, executable), os.X_OK) for path in os.environ["PATH"].split(os.pathsep))

class Inode(object):
    """
    Basic container of information representing an inode on a
    storage element: isdir/isfile, modification time, size, and path.
    """
    @classmethod
    def from_path(cls, path, mgm=None):
        path = format(path, mgm)
        return stat(path)

    def __init__(self, path, modtime, isdir, size):
        self.path = normpath(path)
        self.modtime = modtime
        self.isdir = isdir
        self.size = size

    @property
    def isfile(self):
        return not(self.isdir)

    @property
    def size_human(self):
        return bytes_to_human_readable(float(self.size))

    @property
    def basename(self):
        return osp.basename(self.path)

    @property
    def dirname(self):
        return dirname(self.path)

    @property
    def path_no_mgm(self):
        return split_mgm(self.path)[1]

    @property
    def mgm(self):
        return split_mgm(self.path)[0]

    def __repr__(self):
        if len(self.path) > 40:
            shortpath = self.path[:10] + '...' + self.path[-15:]
        else:
            shortpath = self.path
        return super(Inode, self).__repr__().replace('object', shortpath)

    def __eq__(self, other):
        return (self.path == other.path
            and self.modtime == other.modtime
            and self.isdir == other.isdir
            and self.size == other.size
            )

class ExceptionWithPath(Exception):
    """
    Exception that optionally formats the error string with a path, if it is specified.
    """
    def __init__(self, msg, path=''):
        super(Exception, self).__init__(msg + ((': ' + path) if path else ''))

class NoSuchPath(ExceptionWithPath):
    def __init__(self, path=''):
        super(ExceptionWithPath, self).__init__('No such path', path)

class PermissionDenied(ExceptionWithPath):
    def __init__(self, path=''):
        super(ExceptionWithPath, self).__init__('Permission denied', path)

class HostUnreachable(ExceptionWithPath):
    def __init__(self, path=''):
        super(ExceptionWithPath, self).__init__('Host unreachable', path)

class RmSafetyTrigger(ExceptionWithPath):
    def __init__(self, path=''):
        super(ExceptionWithPath, self).__init__('rm operation attempted on unsafe path', path)

class NonZeroExitCode(subprocess.CalledProcessError):
    def __init__(self, exitcode='?', cmd='?'):
        super(Exception, self).__init__('Exit code {} for command {}'.format(cmd, exitcode))


# _______________________________________________________
# Cache

USE_CACHE = False
CACHEDIR = osp.abspath('.seutils-cache')
CACHES = {}

def use_cache(flag=True):
    """
    Convenience function to turn on and off caching
    """
    global USE_CACHE
    USE_CACHE = flag

def make_cache(subcache_name, make_if_not_exist=True):
    """
    Returns a FileCache object. Will be created if it doesn't exist already
    """
    if not USE_CACHE: return
    global CACHES
    if not subcache_name in CACHES:
        from .cache import FileCache
        cache = FileCache(subcache_name, app_cache_dir=CACHEDIR)
        CACHES[subcache_name] = cache
    return CACHES[subcache_name]

def read_cache(subcache_name, key):
    """
    Attempts to get a value from a cache. Returns None if it was not found
    """
    if not USE_CACHE: return None
    val = make_cache(subcache_name).get(key, None)
    if not(val is None): logger.debug('Using cached result for %s from cache %s', key, subcache_name)
    return val

_LAST_CACHE_WRITE = None
def write_cache(subcache_name, key, value):
    """
    Writes a value to a cache
    """
    if USE_CACHE:
        logger.debug('Writing key %s to cache %s', key, subcache_name)
        subcache = make_cache(subcache_name)
        subcache[key] = value
        subcache.sync()
        global _LAST_CACHE_WRITE
        _LAST_CACHE_WRITE = datetime.datetime.now()

def cache(fn):
    """
    Function decorator to cache output of certain commands
    """
    cache_name = 'seutils-cache.' + fn.__name__
    def wrapper(path, *args, **kwargs):
        # Cache is basically a key-value dump; determine the key to use
        # For most purposes, just the path works well enough
        cache_key = fn.keygen(path, *args, **kwargs) if hasattr(fn, 'keygen') else path.strip()
        # Try to read the cache; if not possible, evaluate cmd and store the result
        val = read_cache(cache_name, cache_key)
        if val is None:
            val = fn(path, *args, **kwargs)
            write_cache(cache_name, cache_key, val)
        return val
    return wrapper

_LAST_TARBALL_CACHE = None
_LAST_TARBALL_PATH = None
def tarball_cache(dst='seutils-cache.tar.gz', only_if_updated=False):
    """
    Dumps the cache to a tarball.
    If only_if_updated is True, an additional check is made to see whether
    the last call to tarball_cache() was made after the last call to write_cache();
    if so, the last created tarball presumably still reflects the current state of
    the cache, and no new tarball is created. This will only work within the same python
    session (timestamps are not saved to files).
    """
    global _LAST_TARBALL_CACHE, _LAST_TARBALL_PATH
    if not USE_CACHE: raise Exception('No active cache to save to a file')
    if not dst.endswith('.tar.gz'): dst += '.tar.gz'
    dst = osp.abspath(dst)
    if only_if_updated:
        if _LAST_TARBALL_CACHE:
            if _LAST_CACHE_WRITE is None or _LAST_CACHE_WRITE < _LAST_TARBALL_CACHE:
                # Either no write has taken place or it was before the last tarball creation;
                # use the last created tarball and don't run again
                logger.info('Detected no change w.r.t. last tarball %s; using it instead', _LAST_TARBALL_PATH)
                return _LAST_TARBALL_PATH
    try:
        _return_dir = os.getcwd()
        if not osp.isdir(CACHEDIR): os.makedirs(CACHEDIR) # Empty dir can be tarballed too for consistency
        os.chdir(CACHEDIR)
        cmd = ['tar', '-zcvf', dst, '.']
        logger.info('Dumping %s --> %s', CACHEDIR, dst)
        run_command(cmd)
        _LAST_TARBALL_CACHE = datetime.datetime.now()
        _LAST_TARBALL_PATH = dst
        return dst
    finally:
        os.chdir(_return_dir)
    return dst

def load_tarball_cache(tarball, dst=None):
    """
    Extracts a cache tarball to cachedir and activates that cache
    """
    global USE_CACHE, CACHEDIR
    if dst is None: dst = CACHEDIR
    dst = osp.abspath(dst)
    logger.info('Extracting %s --> %s', tarball, dst)
    if not osp.isdir(dst): os.makedirs(dst)
    cmd = [
        'tar', '-xvf', tarball,
        '-C', dst
        ]
    run_command(cmd)
    # Activate it
    USE_CACHE = True
    CACHEDIR = dst
    logger.info('Activated cache for path %s', CACHEDIR)

# _______________________________________________________
# Helpers for interactions with SE


_valid_commands = [
    'mkdir', 'rm', 'stat', 'exists', 'isdir',
    'isfile', 'is_file_or_dir', 'listdir', 'cp', 'cat'
    ]

class Implementation:

    rcodes = {}

    def __init__(self):
        self._is_installed = None

    def run_command(self, *args, **kwargs):
        """
        Wrapper around `run_command` that inserts the return codes dict for proper
        error handling
        """
        kwargs['rcodes'] = self.rcodes
        return run_command(*args, **kwargs)

    def is_installed(self):
        if self._is_installed is None:
            self._is_installed = self.check_is_installed()
        return self._is_installed

    def check_is_installed(self):
        raise NotImplementedError

    @add_env_kwarg
    def exists(self, path):
        try:
            self.stat(path)
            return True
        except NoSuchPath:
            return False

    @add_env_kwarg
    def isfile(self, path):
        try:
            inode = self.stat(path)
            return inode.isfile
        except NoSuchPath:
            return False

    @add_env_kwarg
    def is_file_or_dir(self, path):
        try:
            inode = self.stat(path)
            return 2 if inode.isfile else 1
        except NoSuchPath:
            return 0

    @add_env_kwarg
    def isdir(self, directory):
        try:
            inode = self.stat(directory)
            return inode.isdir
        except NoSuchPath:
            return False


from .gfal_implementation import GfalImplementation
gfal = GfalImplementation()

# from .pyxrd_implementation import PyxrdImplementation
# pyxrd = PyxrdImplementation()

from .xrd_implementation import XrdImplementation
xrd = XrdImplementation()


class PlaceholderImplementation(Implementation):
    def check_is_installed(self):
        return False

pyxrd = PlaceholderImplementation()
eos = PlaceholderImplementation()
ssh = PlaceholderImplementation()


implementations = dict(gfal=gfal, pyxrd=pyxrd, xrd=xrd, eos=eos, ssh=ssh)

def get_implementation(implementation_name):
    """
    Returns an implementation instance corresponding to the passed name.
    Returns None if `implementation_name` is 'auto' or None.
    """
    if implementation_name in ['auto', None]:
        return None
    return implementations[implementation_name]

def best_implementation(cmd_name, path=None):
    """
    Given a command name, returns an installed implementation that has this command
    """
    if path and is_ssh(path):
        logger.debug('Path is ssh-like')
        preferred_order = [ssh]
    elif cmd_name == 'rm':
        preferred_order = [ eos, gfal, pyxrd, xrd]
    else:
        preferred_order = [ xrd, gfal, pyxrd, eos ]
    # Return first one that's installed
    for implementation in preferred_order:
        if implementation.is_installed() and hasattr(implementation, cmd_name):
            logger.info(
                'Using implementation %s to execute \'%s\' (path: %s)',
                implementation.__class__.__name__, cmd_name, path
                )
            return implementation
    raise Exception('No installed implementation found for cmd {0}, path {1}'.format(cmd_name, path))


def make_global_scope_command(cmd_name):
    """
    Creates a global scope command in case the user does not care about the
    underlying implementation.
    """
    def wrapper(path, *args, **kwargs):
        implementation = kwargs.pop('implementation', None)
        if implementation is None:
            implementation = best_implementation(cmd_name, path)
        elif is_string(implementation):
            implementation = implementations[implementation]
        return getattr(implementation, cmd_name)(path, *args, **kwargs)
    return wrapper
        
mkdir = make_global_scope_command('mkdir')
rm = make_global_scope_command('rm')
stat = make_global_scope_command('stat')
exists = make_global_scope_command('exists')
isdir = make_global_scope_command('isdir')
isfile = make_global_scope_command('isfile')
is_file_or_dir = make_global_scope_command('is_file_or_dir')
listdir = make_global_scope_command('listdir')
cat = make_global_scope_command('cat')
cp = make_global_scope_command('cp')
stat_fn = stat # Alias for if stat is a keyword in a function in this module


# _______________________________________________________
# Actual interactions with SE
# The functions below are just wrappers for the actual implementations in
# separate modules. All functions have an `implementation` keyword; If set
# to None, the 'best' implementation is guessed.

@add_env_kwarg
def put(path, contents='', make_parent_dirs=True, tmpfile_path='seutils_tmpfile', **cp_kwargs):
    """
    Creates a file on a storage element.
    `path` should contain an mgm
    """
    path = normpath(path)
    tmpfile_path = osp.abspath(tmpfile_path)
    if not has_protocol(path):
        raise TypeError('Path {0} does not contain an mgm'.format(path))
    # Open a local file
    with open(tmpfile_path, 'w') as f:
        f.write(contents)
    try:
        cp(tmpfile_path, path, **cp_kwargs)
    finally:
        os.remove(tmpfile_path)


MAX_RECURSION_DEPTH = 20

@add_env_kwarg
def ls(path, stat=False, assume_isdir=False, no_expand_directory=False, implementation=None):
    """
    Lists all files and directories in a directory on the SE.
    It first checks whether the path exists and is a file or a directory.
    If it does not exist, it raises an exception.
    If it is a file, it just returns a formatted path to the file as a 1-element list
    If it is a directory, it returns a list of the directory contents (formatted)

    If stat is True, it returns Inode objects which contain more information beyond just the path

    If assume_isdir is True, the first check is not performed and the algorithm assumes
    the user took care to pass a path to a directory. This saves a request to the SE, which might
    matter in the walk algorithm. For singular use, assume_isdir should be set to False.

    If no_expand_directory is True, the contents of the directory are not listed, and instead
    a formatted path to the directory is returned (similar to unix's ls -d)
    """
    path = format(path)
    if assume_isdir:
        status = 1
    else:
        status = is_file_or_dir(path, implementation=implementation)
    # Depending on status, return formatted path to file, directory contents, or raise
    if status == 0:
        raise NoSuchPath(path)
    elif status == 1:
        # It's a directory
        if no_expand_directory:
            # If not expanding, just return a formatted path to the directory
            return [stat_fn(path, implementation=implementation) if stat else path]
        else:
            # List the contents of the directory
            return listdir(path, assume_isdir=True, stat=stat, implementation=implementation) # No need to re-check whether it's a directory
    elif status == 2:
        # It's a file; just return the path to the file
        return [stat_fn(path, implementation=implementation) if stat else path]

class Counter:
    """
    Class to basically mimic a pointer to an int
    This is very clumsy in python
    """
    def __init__(self):
        self.i = 0
    def plus_one(self):
        self.i += 1

@add_env_kwarg
def walk(path, stat=False, implementation=None):
    """
    Entry point for walk algorithm.
    Performs a check whether the starting path is a directory,
    then yields _walk.
    A counter object is passed to count the number of requests
    made to the storage element, so that 'accidents' are limited
    """
    path = format(path)
    status = is_file_or_dir(path, implementation=implementation)
    if not status == 1:
        raise RuntimeError(
            '{0} is not a directory'
            .format(path)
            )
    counter = Counter()
    for i in _walk(path, stat, counter, implementation=implementation):
        yield i

def _walk(path, stat, counter, implementation=None):
    """
    Recursively calls ls on traversed directories.
    The yielded directories list can be modified in place
    as in os.walk.
    """
    if counter.i >= MAX_RECURSION_DEPTH:
        raise RuntimeError(
            'walk reached the maximum recursion depth of {0} requests.'
            ' If you are very sure that you really need this many requests,'
            ' set seutils.MAX_RECURSION_DEPTH to a larger number.'
            .format(MAX_RECURSION_DEPTH)
            )
    contents = ls(path, stat=True, assume_isdir=True, implementation=implementation)
    counter.plus_one()
    files = [ c for c in contents if c.isfile ]
    files.sort(key=lambda f: f.basename)
    directories = [ c for c in contents if c.isdir ]
    directories.sort(key=lambda d: d.basename)
    if stat:
        yield path, directories, files
    else:
        dirnames = [ d.path for d in directories ]
        yield path, dirnames, [ f.path for f in files ]
        # Filter directories again based on dirnames, in case the user modified
        # dirnames after yield
        directories = [ d for d in directories if d.path in dirnames ]
    for directory in directories:
        for i in _walk(directory.path, stat, counter, implementation=implementation):
            yield i

@add_env_kwarg
def ls_wildcard(pattern, stat=False, implementation=None):
    """
    Like ls, but accepts wildcards * .
    Directories are *not* expanded.

    The algorithm is like `walk`, but discards directories that don't fit the pattern
    early.
    Still the number of requests can grow quickly; a limited number of wildcards is advised.
    """
    pattern = format(pattern)
    if not '*' in pattern:
        return ls(pattern, stat=stat, no_expand_directory=True, implementation=implementation)
    import re
    if not stat and not '*' in pattern.rsplit('/',1)[0]:
        # If there is no star in any part but the last one and we don't need to stat, it is
        # much faster to do a simple listing once and do regex matching here.
        # This only saves time for the specific case of 'no need for stat' and 'pattern
        # only for the very last part'
        logger.info('Detected * only in very last part of pattern and stat=False; using shortcut')
        directory, pattern = pattern.rsplit('/',1)
        contents = ls(directory, implementation=implementation)
        if pattern == '*':
            # Skip the regex matching if set to 'match all'
            return contents
        regex = re.compile(pattern.replace('*', '.*'))
        contents = [ c for c in contents if regex.match(osp.basename(c)) ]
        return contents
    # 
    pattern_level = pattern.count('/')
    logger.debug('Level is %s for path %s', pattern_level, pattern)
    # Get the base pattern before any wild cards
    base = pattern.split('*',1)[0].rsplit('/',1)[0]
    logger.debug('Found base pattern %s from pattern %s', base, pattern)
    matches = []
    for path, directories, files in walk(base, stat=stat, implementation=implementation):
        level = path.count('/')
        logger.debug('Level is %s for path %s', level, path)
        trimmed_pattern = '/'.join(pattern.split('/')[:level+2]).replace('*', '.*')
        logger.debug('Comparing directories in %s with pattern %s', path, trimmed_pattern)
        regex = re.compile(trimmed_pattern)
        if stat:
            directories[:] = [ d for d in directories if regex.match(d.path) ]
        else:
            directories[:] = [ d for d in directories if regex.match(d) ]
        if level+1 == pattern_level:
            # Reached the depth of the pattern - save matches
            matches.extend(directories[:])
            if stat:
                matches.extend([f for f in files if regex.match(f.path)])
            else:
                matches.extend([f for f in files if regex.match(f)])
            # Stop iterating in this part of the tree
            directories[:] = []
    return matches


def listdir_recursive(directory, stat=False, implementation=None):
    """
    Returns a list of all paths (or Inodes if `stat=True`) recursively under `directory`.
    """
    contents = []
    for path, directories, files in walk(directory, stat=stat, implementation=implementation):
        contents.extend(directories)
        contents.extend(files)
    return contents


def _sorted_paths_from_set(relpaths_set, relpaths, contents):
    """
    Used internally by `diff`. For every element in `relpaths_set`,
    return the matching item from `contents`. Preserves order of `contents`.
    """
    selected_contents = []
    for rpath, content in zip(relpaths, contents):
        if rpath in relpaths_set:
            selected_contents.append(content)
    return selected_contents

@add_env_kwarg
def diff(left, right, stat=False, implementation=None):
    """
    Returns 4 lists of paths (or Inodes, if `stat=True`):
    - Paths in `left` that are also in `right` (intersection_left)
    - Paths in `right` that are also in `left` (intersection_right)
    - Paths in `left` that are not in `right` (only_in_left)
    - Paths in `right` that are not in `left` (only_in_right)

    (Note intersection_left and intersection_right) will have the same
    contents, but different mgms)

    TODO: Currently only implemented if both left and right are remote!
    """
    for path in [left, right]:
        if not has_protocol(path):
            raise NotImplementedError('diff does not support local paths yet: {0}'.format(path))

    contents_left = listdir_recursive(left, implementation=implementation, stat=stat)
    contents_right = listdir_recursive(right, implementation=implementation, stat=stat)

    if stat:
        paths_left = [ n.path for n in contents_left ]
        paths_right = [ n.path for n in contents_right ]
    else:
        paths_left = contents_left
        paths_right = contents_right
        
    relpaths_left = [ relpath(p, left) for p in paths_left ]
    relpaths_right = [ relpath(p, right) for p in paths_right ]
    set_relpaths_left = set(relpaths_left)
    set_relpaths_right = set(relpaths_right)

    intersection = set_relpaths_left.intersection(set_relpaths_right)
    only_in_left = set_relpaths_left - set_relpaths_right
    only_in_right = set_relpaths_right - set_relpaths_left

    return (
        _sorted_paths_from_set(intersection, relpaths_left, contents_left),
        _sorted_paths_from_set(intersection, relpaths_right, contents_right),
        _sorted_paths_from_set(only_in_left, relpaths_left, contents_left),
        _sorted_paths_from_set(only_in_right, relpaths_right, contents_right),
        )

# _______________________________________________________
# CLI

from . import cli

# _______________________________________________________
# root utils extension

from . import root
