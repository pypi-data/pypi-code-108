"""
Simple synchronization & caching for Flask apps.

sync.py

Implements simple/inefficient shared state through the filesystem. For
read-only access w/ caching to reduce disk overhead, provides
load_or_get_cached: a thread-safe way of loading from a file (if multiple
WSGI processes are used, each will have its own cache). For read/write
access to control application global state, access_state_file is
provided: a process-safe method (using a Manager that gets started
automatically) to read or write file contents. By default, both functions
are JSON-in, JSON-out, but raw strings can be requested instead.
"""

__version__ = "0.9.1"

from flask import json
import os, sys, copy, time
import threading
import multiprocessing, multiprocessing.connection, multiprocessing.managers

# Python 2/3 dual compatibility
if sys.version_info[0] < 3:
    reload(sys) # noqa F821
    sys.setdefaultencoding('utf-8')
    import socket
    ConnectionRefusedError = socket.error
    IOError_or_FileNotFoundError = IOError
    OSError_or_FileNotFoundError = OSError
    AuthenticationError = multiprocessing.AuthenticationError
else:
    IOError_or_FileNotFoundError = FileNotFoundError
    OSError_or_FileNotFoundError = FileNotFoundError
    AuthenticationError = multiprocessing.context.AuthenticationError

# Python 2.7.5 multiprocessing bug workaround
# Bug thread of same behavior:
# https://bugzilla.redhat.com/show_bug.cgi?id=1717330
# Python bugfix:
# https://github.com/python/cpython/commit/e8a57b98ec8f2b161d4ad68ecc1433c9e3caad57
# Source for this workaround: https://github.com/oamg/leapp/pull/533/files

# Implements:
# https://github.com/python/cpython/commit/e8a57b98ec8f2b161d4ad68ecc1433c9e3caad57
#
# Detection of fix: os imported to compare pids, before the fix os has not
# been imported
import multiprocessing.util
if getattr(multiprocessing.util, 'os', None):
    # we're on a version that has the fix; no need to apply it
    pass
else:
    # we'd better apply the fix
    class FixedFinalize(multiprocessing.util.Finalize):
        def __init__(self, *args, **kwargs):
            super(FixedFinalize, self).__init__(*args, **kwargs)
            self._pid = os.getpid()

        def __call__(self, *args, **kwargs):
            if self._pid != os.getpid():
                return None
            return super(FixedFinalize, self).__call__(*args, **kwargs)

    setattr(multiprocessing.util, 'Finalize', FixedFinalize)


#----------------------#
# Core caching routine #
#----------------------#

class AbortGeneration:
    """
    Class to signal that generation of a cached item should not proceed.
    Holds a default value to return instead.
    """
    def __init__(self, replacement):
        self.replacement = replacement


class NotInCache:
    """
    Placeholder for recognizing that a value is not in the cache (when
    e.g., None might be a valid cache value).
    """
    pass


def _gen_or_get_cached(lock, cache, cache_key, check_dirty, result_generator):
    """
    Common functionality that uses a reentrant lock and a cache
    dictionary to return a cached value if the cached value is fresh. The
    value from the cache is deep-copied before being returned, so that
    any modifications to the returned value shouldn't alter the cache.
    Parameters are:

        lock: Specifies the lock to use. Should be a threading.RLock.
        cache: The cache dictionary.
        cache_key: String key for this cache item.
        check_dirty: Function which will be given the cache_key and a
            timestamp and must return True if the cached value (created
            at that instant) is dirty (needs to be updated) and False
            otherwise. May also return an AbortGeneration instance with a
            default value inside to be returned directly. If there is no
            cached value, check_dirty will be given a timestamp of None.
        result_generator: Function to call to build a new result if the
            cached value is stale. This new result will be cached. It
            will be given the cache_key as a parameter.
    """
    with lock:
        # We need to read the file contents and return them.
        cache_ts, cached = cache.get(cache_key, (None, NotInCache))
        safe_cached = copy.deepcopy(cached)

    # Get mtime of file, or find out it's missing. No point in
    # caching the missing value, because the mtime check the
    # next time will hit the same branch.
    is_dirty = check_dirty(cache_key, cache_ts)
    if isinstance(is_dirty, AbortGeneration):
        # check_fresh calls for an abort: return replacement value
        return is_dirty.replacement
    elif not is_dirty and cached != NotInCache:
        # Cache is fresh: return cached value
        return safe_cached
    else:
        # Cache is stale

        # Get timestamp before we even start generating value:
        ts = time.time()

        # Generate reuslt:
        result = result_generator(cache_key)

        # Safely store new result value + timestamp in cache:
        with lock:
            cache[cache_key] = (ts, result)
            # Don't allow outside code to mess with internals of
            # cached value (JSON results could be mutable):
            safe_result = copy.deepcopy(result)

        # Return fresh deep copy of cached value:
        return safe_result


def set_new_cached_value(lock, cache, cache_key, value):
    """
    Directly overrides a cached value, inserting a new value timestamped
    when this function is called.
    """
    with lock:
        # Create timestamp first
        ts = time.time()
        # Store new value in cache:
        cache[cache_key] = (ts, copy.deepcopy(value))


def cache_key_for(target, view):
    """
    Builds a hybrid cache key value with a certain target and view.
    """
    return target + "::" + view.__name__


def cache_key_filename(cache_key):
    """
    Returns just the filename given a cache key.
    """
    if '::' not in cache_key:
        raise ValueError("Value '{}' is not a cache key!".format(cache_key))
    return '::'.join(cache_key.split('::')[:-1])


#----------------------------------#
# View objects for managing caches #
#----------------------------------#

class View:
    """
    Abstract View class to organize decoding/encoding of views. Each View
    must define encode and decode class methods which are each others'
    inverse. The class name is used as part of the cache key.
    """
    @staticmethod
    def encode(obj):
        """
        The encode function of a View must return a string (to be written
        to a file).
        """
        raise NotImplementedError("Don't use the base View class.")

    @staticmethod
    def decode(string):
        """
        The encode function of a View must accept a string, and if given
        a string produced by encode, should return an equivalent object.
        """
        raise NotImplementedError("Don't use the base View class.")


class AsIs(View):
    """
    A pass-through view that returns strings unaltered.
    """
    @staticmethod
    def encode(obj):
        """Returns the object it is given unaltered."""
        return obj

    @staticmethod
    def decode(string):
        """Returns the string it is given unaltered."""
        return string


class AsJSON(View):
    """
    A view that converts objects to JSON for file storage and back on
    access. It passes through None.
    """
    @staticmethod
    def encode(obj):
        """Returns the JSON encoding of the object."""
        return json.dumps(obj)

    @staticmethod
    def decode(string):
        """
        Returns a JSON object parsed from the string.
        Returns None if it gets None.
        """
        if string is None:
            return None
        return json.loads(string)


def build_view(name, encoder, decoder, pass_none=True):
    """
    Function for building a view given a name, an encoding function, and
    a decoding function. Unless pass_none is given as False, the decoder
    will be skipped if the decode argument is None and the None will pass
    through, in which case the decoder will *always* get a string as an
    argument.
    """
    class SyntheticView(View):
        """
        View class created using build_view.
        """
        @staticmethod
        def encode(obj):
            return encoder(obj)

        @staticmethod
        def decode(string):
            if pass_none and string is None:
                return None
            return decoder(string)

    SyntheticView.__name__ = name
    SyntheticView.__doc__ = (
        "View that uses '{}' for encoding and '{}' for decoding."
    ).format(encoder.__name__, decoder.__name__)
    SyntheticView.encode.__doc__ = encoder.__doc__
    SyntheticView.decode.__doc__ = decoder.__doc__

    return SyntheticView


#--------------------------#
# Process-local singletons #
#--------------------------#

def build_or_get_singleton(cache_key, builder):
    """
    Caches the result of the given builder function under the given cache
    key, always returning the cached result once it's been created.
    This is thread-safe, but each singleton is unique to the process that
    created it.
    """
    return _gen_or_get_cached(
        _CACHE_LOCK,
        _CACHE,
        cache_key,
        lambda key, ts: ts is not None,
        builder
    )


#--------------------------------------#
# Process-local read-only file caching #
#--------------------------------------#

def build_file_freshness_checker(missing=Exception):
    """
    Builds a freshness checker that checks the mtime of a filename, but
    if that file doesn't exist, it returns AbortGeneration with the given
    missing value (unless missing is left as the default of Exception, in
    which case it lets the exception bubble out).
    """
    def check_file_is_changed(cache_key, ts):
        """
        Checks whether a file has been modified more recently than the given
        timestamp.
        """
        filename = cache_key_filename(cache_key)
        try:
            mtime = os.path.getmtime(filename)
        except OSError_or_FileNotFoundError:
            if missing == Exception:
                raise
            else:
                return AbortGeneration(missing)

        # File is changed if the mtime is after the given cache
        # timestamp, or if the timestamp is None
        return ts is None or mtime >= ts

    return check_file_is_changed


def build_file_reader(view=AsJSON):
    """
    Builds a file reader function which returns the result of the given
    view on the file contents.
    """
    def read_file(cache_key):
        """
        Reads a file and returns the result of calling a view's decode
        function on the file contents. Returns None if there's an error,
        and prints the error unless it's a FileNotFoundError.
        """
        filename = cache_key_filename(cache_key)
        try:
            with open(filename, 'r') as fin:
                return view.decode(fin.read())
        except IOError_or_FileNotFoundError:
            return None
        except Exception as e:
            sys.stderr.write(
                "[sync module] Exception viewing file:\n" + str(e) + '\n'
            )
            return None

    return read_file


# Note: by using a threading.RLock and a global variable here, we are not
# process-safe, which is fine, because this is just a cache: each process
# in a multi-process environment can safely maintain its own cache which
# will waste a bit of memory but not lead to corruption. As a corollary,
# load_or_get_cached should be treated as read-only, and
# access_state_file should be used to access a file which needs to have
# consistent state viewable by potentially multiple processes.

# TODO: We should probably have some kind of upper limit on the cache
# size, and maintain staleness so we can get rid of stale items...
_CACHE_LOCK = threading.RLock() # Make this reentrant just in case...
_CACHE = {}


def load_or_get_cached(
    filename,
    view=AsJSON,
    missing=Exception
):
    """
    Loads the contents of the given file and returns the result of the
    given view function on it (or the contents as a string if the view is
    None). It first checks the modification time and returns a cached
    copy of the view result if one exists. Uses a lock for thread safety.
    The default view parses file contents as JSON and returns the
    resulting object. If the file is missing, an exception would normally
    be raised, but if the missing value is provided as something other
    than Exception, a deep copy of that value will be returned instead.
    The __name__ of the view class will be used to compute a cache key
    for that view; avoid view name collisions.

    Note: On a cache hit, a deep copy of the cached value is returned, so
    modifying that value should not affect what is stored in the cache.
    """

    # Figure out our view object (& cache key):
    if view is None:
        view = AsIs

    cache_key = cache_key_for(filename, view)

    # Build functions for checking freshness and reading the file
    check_mtime = build_file_freshness_checker(missing)
    read_file = build_file_reader(view)

    return _gen_or_get_cached(
        _CACHE_LOCK,
        _CACHE,
        cache_key,
        check_mtime,
        read_file
    )


#-------------------------------------#
# Cross-process file access & caching #
#-------------------------------------#

# A lock and cache for access_file
_ACCESS_LOCK = threading.RLock()
_ACCESS_CACHE = {}

# The _FileAccess proxy to use for file access:
_ACCESS = None


def read_file(
    filename,
    view=AsJSON,
    missing=Exception,
    cache=True
):
    """
    Reads from a file, operating via proxy through a manager so that
    multiple threads/processes' requests will happen sequentially to
    avoid simultaneous reads/writes to any file. Returns the string
    contents of the file, or None if the file does not exist or there's
    some other error in accessing the file. If there's an error other
    than the file not existing, an error message will be printed to
    stderr.

    This model is pretty draconian and sets up file access as competitive
    across all files, so only use it for files that may be written to by
    the server; read-only files can use load_or_get_cached instead. This
    function does set up a local in-process cache and check file mtimes,
    to avoid the entire proxy call if it can (only if cache is True).

    The arguments behave as follows:

        filename: The full path to the file to be accessed.
        view: A View object which can encode and decode strings. AsJSON
            is the default, which converts strings in files to objects
            using JSON. The view's decode function is applied to file
            contents before they are cached. Using two different views
            with the same __name__ will cause incorrect cached values to
            be returned.
        missing: A value to be returned (but not cached or written to
            disk) if the file does not exist. Leave it as Exception and
            whatever exception causes os.path.getmtime to fail will be
            allowed to bubble out.
        cache: True by default, results will be cached, and the
            file-access-via-proxy chain of events will be skipped
            entirely if the cache value is newer than the file on disk.
            Set to False for large and/or constantly changing files where
            you expect this to be a waste of time or space. The cache is
            per-process but shared between threads.
    """

    # Figure out our view function (& cache key just in case):
    if view is None:
        view = AsIs

    # Define our reader function which incorporates our view:
    def read_file_contents(cache_key):
        """
        File reading function that accesses file contents through an
        _ACCESS proxy. Applies a view function. Returns None if the view
        function encounters an error (and prints that error to stderr).
        """
        filename = cache_key_filename(cache_key)
        return view.decode(_ACCESS.read_file(filename))

    if cache: # If we're caching, do that:
        cache_key = cache_key_for(filename, view)
        check_mtime = build_file_freshness_checker(missing)

        return _gen_or_get_cached(
            _ACCESS_LOCK,
            _ACCESS_CACHE,
            cache_key,
            check_mtime,
            read_file_contents
        )

    else: # Otherwise, just call our reader function
        # But first check whether the file exists...
        if not os.path.exists(filename):
            if missing == Exception:
                raise OSError("File not found: '{}'".format(filename))
            else:
                return missing
        else:
            return read_file_contents(cache_key_for(filename, view))


def write_file(filename, content, view=AsJSON, cache=True):
    """
    Writes the given content to the given file, encoding the content
    using the encode function of the given view. If cache is True,
    updates the _ACCESS_CACHE with the new file contents to avoid
    unnecessary round trips to disk. The original content, not the
    encoded string, will be cached. The view may be given as None to
    write the content directly to the file as a string.
    """
    if view is None:
        view = AsIs

    file_content = view.encode(content)

    _ACCESS.write_file(filename, file_content)

    if cache:
        cache_key = cache_key_for(filename, view)
        set_new_cached_value(
            _ACCESS_LOCK,
            _ACCESS_CACHE,
            cache_key,
            content
        )


class _FileAccessor:
    """
    A class for accessing files. Meant to be used via Proxy, with a
    single Manager having the real instance so that all access is
    sequential and we don't have conflicting writes or partial reads.
    Instead of instantiating this class, use FileSystemManager.get (see
    below).
    """
    def __init__(self):
        # This... really isn't necessary, surely. But just in case the
        # Manager uses multiple threads...
        self.lock = threading.RLock()

    def read_file(self, filename):
        """
        Reads file contents as a string, returning None if the file
        doesn't exist or there's some other error (e.g., encoding issue).
        If the file doesn't exist, no error is printed, but otherwise the
        error messages is printed to stderr.
        """
        with self.lock:
            try:
                with open(filename, 'r') as fin:
                    return fin.read()
            except IOError_or_FileNotFoundError:
                return None
            except Exception as e:
                sys.stderr.write("Exception reading file:\n" + str(e) + '\n')
                return None

    def write_file(self, filename, content):
        """
        Writes the given content into the given file, replacing any
        previous content.
        TODO: What happens if there's an exception here? Does the manager
        process crash entirely?
        """
        with self.lock:
            with open(filename, 'w') as fin:
                fin.write(content)


#--------------------#
# Manager management #
#--------------------#

class FileSystemManager(multiprocessing.managers.BaseManager):
    """
    Custom manager class for managing read/write file system access from
    multiple threads. Go use a database instead!
    """
    pass


FileSystemManager.register("get", _FileAccessor)


# The manager connection for this process:
_MANAGER = None


def init_sync(port=51723, key=None):
    """
    init_sync should be called once per process, ideally early in the
    life of the process, like right after importing the sync module.
    Calling access_file before init_sync will fail. A file named
    'syncauth' should exist unless a key is given (should be a
    byte-string). If 'syncauth' doesn't exist, it will be created. Don't
    rely too heavily on the default port, since any two apps using sync
    with the default port on the same machine will collide.
    """
    global _MANAGER, _ACCESS
    # Get synchronization key:
    if key is None:
        try:
            if os.path.exists('syncauth'):
                with open('syncauth', 'rb') as fin:
                    key = fin.read()
            else:
                print("Creating new sync secret file 'syncauth'.")
                key = os.urandom(16)
                with open('syncauth', 'wb') as fout:
                    fout.write(key)
        except Exception:
            raise IOError_or_FileNotFoundError(
                "Unable to access 'syncauth' file.\n"
              + "  Create it and put some random bytes in there, or pass"
              + " key= to init_sync."
            )

    _MANAGER = FileSystemManager(address=('localhost', port), authkey=key)
    # Attempt to connect; if that fails, attempt to start a new manager
    # if that fails (due to simultaneous starts and one wins the port
    # that's not us) attempt to connect again. Repeat until we connect.
    while True:
        print("Attempting to connect to MP manager...")

        # Reduce multiprocessing's connection timeout value since we're
        # pretty sure we'll fail first and succeed later
        old_init_timeout = multiprocessing.connection._init_timeout
        multiprocessing.connection._init_timeout = lambda t=2.0: (
            time.time() + t
        )
        try:
            # NOTE: This call may just never return if we accidentally
            # connect to e.g., an HTTP server.
            _MANAGER.connect() # Check your port settings!
            print("...connected successfully.")
            break # only way out of loop is to connect successfully
        except ConnectionRefusedError: # Nobody listening on that port
            pass
        except AuthenticationError:
            raise ValueError(
                "Your authkey is not correct. Make sure you're not"
              + " sharing the port you chose!"
            )
        print("...failed to connect...")

        # Restore old timeout function
        multiprocessing.connection._init_timeout = old_init_timeout

        # We didn't get to connect? Let's try to start a manager:
        try:
            print("...starting manager process...")
            _MANAGER.start()
            print("...finished starting manager...")
        except EOFError: # Error generated if port is in use
            pass
        except RuntimeError:
            # Error generated as of 3.8 when attempting to start the
            # manager during the post-fork module reloading phase of a
            # manager sub-process.
            return

        # Sleep for quite a while to try to avoid calling _MANAGER.start
        # multiple times before the first call can bind the port.
        time.sleep(0.2)

        # And now we'll return to the top of the loop and attempt to
        # connect again.

    # At this point, _MANAGER is a connected manager for this process, so
    # we're done.

    # Set up _ACCESS as a proxy object:
    _ACCESS = _MANAGER.get()

    if _ACCESS is None:
        raise ValueError("_MANAGER.get() returned None")
