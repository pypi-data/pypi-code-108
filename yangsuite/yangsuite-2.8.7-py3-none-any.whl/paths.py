# Copyright 2016 to 2021, Cisco Systems, Inc., all rights reserved.

r"""APIs for declaring, creating, and accessing storage under ``MEDIA_ROOT``.

- :func:`set_base_path` should be called from settings.py
- Plugins can define extra storage directories with :func:`register_path()`
- Plugins can access their own or other directories with :func:`get_path()`
- Admin can inspect all declarations with :func:`list_paths()`

Examples::

    >>> set_base_path("/")

    Register a path under the base_path:
    >>> register_path("tilde", "home")
    >>> get_path("tilde")
    '/home'

    Register a path under this parent path, with a parameter:
    >>> register_path("person", "{user}", parent="tilde")
    >>> get_path("person", user="me")
    '/home/me'

    Paths can be chained together and slugified:
    >>> register_path("directory", "{dirname}", parent="person")
    >>> register_path("file", "{file}.dat", parent="directory", slugify=True)
    >>> get_path("file", user="you", dirname="my-dir", file='MY File!')
    '/home/you/my-dir/my-file.dat'

    Listing registered paths thus far:
    >>> print("\n".join("{0}: {1}".format(k, v) for
    ...                 k, v in sorted(list_paths().items())))
    directory: /home/{user}/{dirname}
    file: /home/{user}/{dirname}/{file}.dat
    person: /home/{user}
    tilde: /home
"""

import errno
import logging
import os
import shutil
from slugify import slugify

_base_path = None
_paths = {}


log = logging.getLogger(__name__)


def set_base_path(path):
    """Set the root directory under which all other storage implicitly exists.

    This directory *must* exist or :func:`get_path` will throw an exception.
    Typically invoked from settings.py as ``set_base_path(MEDIA_ROOT)``.

    Args:
      path (str): Path to root directory
    """
    global _base_path
    _base_path = path


def get_base_path():
    """Get the root directory."""
    return _base_path


def register_path(key, path_segment,
                  parent=None, autocreate=False, slugify=False, replace=False):
    """Register a new storage path spec.

    Args:
      key (str): Unique key to register this storage path for later retrieval
        by get_path()
      path_segment (str): Additional path segment(s) to append to the
        parent path to generate this path. This can be a string literal
        (e.g. ``'logs'``) or a format string (e.g. ``'{user}'``) that will be
        built from the additional arguments passed to :func:`get_path`.
        See examples above.
      parent (str): Key of parent path, already registered, under which this
        path is a descendant. If not specified, this path exists directly under
        the path registered by :func:`set_base_path`.
      autocreate (bool): If true, :func:`get_path` will automatically create
        this path as a directory if it doesn't already exist.
      slugify (bool): If true, any parameters of the ``path_segment`` will be
        passed through :func:`slugify.slugify` before constructing the
        path string. This has the effect of converting these parameters
        (but not any static portion of the ``path_segment`` declaration)
        to lowercase ASCII strings without spaces (replaced by hyphens) or
        other special characters, ensuring a safe path string::

          >>> import slugify
          >>> slugify.slugify("My path segment!")
          'my-path-segment'

        This does have the caveat that multiple distinct inputs to
        :func:`get_path` may result in the same generated path string;
        if your application needs a one-to-one mapping between inputs and
        generated paths, you shouldn't use this option. For example::

          >>> import slugify
          >>> slugify.slugify("--- my path segment ---")
          'my-path-segment'
          >>> slugify.slugify("___ MY ___ PATH-SEGMENT __ ")
          'my-path-segment'

      replace (bool): If true, replace any existing path registration under
        this same key, instead of raising a KeyError as described below.

    Raises:
      KeyError:
        if key is already registered with different values, and the
        ``replace`` option was not set as True::

          >>> register_path("foo", "bar")

          Re-registering the same path is a no-op:
          >>> register_path("foo", "bar")

          But registering the same key with different args is an error:
          >>> register_path("foo", "baz/bar")
          Traceback (most recent call last):
              ...
          KeyError: 'Path key "foo" is already registered'

          If the change is intended, you can use the ``replace`` option:
          >>> register_path("foo", "baz/bar", replace=True)

      KeyError:
        if parent is specified and parent is not already registered::

          >>> register_path("plover", "plover", parent="frobozz")
          Traceback (most recent call last):
              ...
          KeyError: 'Parent path key "frobozz" is not yet registered'
    """
    global _paths
    if key in _paths:
        if _paths[key] == (parent, path_segment, autocreate, slugify):
            # Attempt at re-registering same path with same params - no-op
            return
        elif not replace:
            raise KeyError('Path key "{0}" is already registered'.format(key))
    if parent and parent not in _paths:
        raise KeyError('Parent path key "{0}" is not yet registered'
                       .format(parent))
    _paths[key] = (parent, path_segment, autocreate, slugify)


def get_path(key, create=False, flush=False, *args, **kwargs):
    """Get (and possibly create) the requested path.

    Args:
      key (str): Key to look up the requested path spec previously registered.
      create (bool): Force creation of this path as a directory if it doesn't
        already exist, regardless of whether the path spec was registered as
        auto-self-creating.
      flush (bool): If this path already exists, remove any existing files
        that it contains.
      *args: Applied to :meth:`string.format` on the path spec.
      **kwargs: Applied to :meth:`string.format` on the path spec.

    Returns:
      str: Requested path (may or may not exist, unless ``create=True`` is
      explicitly specified or the path spec was declared as
      ``autocreate=True``, in which case it will exist as a directory)

    Raises:
      KeyError:
        if the given key is not registered::

          >>> get_path("nothing_here")
          Traceback (most recent call last):
            ...
          KeyError: 'No such path key "nothing_here" is registered'

      RuntimeError:
        if unable to create a requested path because a required
        and not-auto-creating parent path does not yet exist::

          >>> register_path("noautocreate", "noauto")
          >>> register_path("auto", "autocreate",
          ...               parent="noautocreate", autocreate=True)
          >>> get_path("auto")
          Traceback (most recent call last):
              ...
          RuntimeError: Can't autocreate 'auto' given '/noauto' doesn't exist

      OSError:
        if a parent path exists but is not a directory::

          >>> set_base_path(__file__)
          >>> register_path("myself", 'howdy', autocreate=True)
          >>> try:
          ...     get_path("myself")
          ... except OSError as exc:
          ...     print(exc.strerror + ': ' + exc.filename)# doctest: +ELLIPSIS
          Not a directory: ...paths.py...

      TypeError:
        if a required argument is not provided::

          >>> set_base_path("/")
          >>> register_path("person", "{user}")
          >>> get_path('person')
          Traceback (most recent call last):
             ...
          TypeError: get_path() missing required keyword argument: 'user'
    """
    global _paths
    if key not in _paths:
        raise KeyError('No such path key "{0}" is registered'.format(key))
    parent, path_segment, autocreate, do_slugify = _paths[key]

    invalid_args = []
    for index, arg in enumerate(args):
        if not arg:
            invalid_args.append(
                "Positional argument {0} is empty".format(index))
    for key, val in kwargs.items():
        if not val:
            invalid_args.append('Key "{0}" has an empty value'.format(key))
    if invalid_args:
        raise ValueError("\n".join(invalid_args))

    if not parent:
        # All paths are implicitly under _base_path
        global _base_path
        if not _base_path:
            from django.conf import settings
            log.warning("set_base_path not called yet. "
                        "Implicitly setting to settings.MEDIA_ROOT (%s)",
                        settings.MEDIA_ROOT)
            set_base_path(settings.MEDIA_ROOT)
        parent_path = _base_path
    else:
        parent_path = get_path(parent, *args, create=create, **kwargs)

    if (create or autocreate) and not os.path.exists(parent_path):
        raise RuntimeError("Can't autocreate '{0}' given '{1}' doesn't exist"
                           .format(key, parent_path))
    elif os.path.exists(parent_path) and not os.path.isdir(parent_path):
        raise OSError(errno.ENOTDIR, os.strerror(errno.ENOTDIR), parent_path)

    try:
        seg_args = args
        seg_kwargs = kwargs
        if do_slugify:
            seg_args = [slugify(arg) for arg in args]
            for key, value in seg_kwargs.items():
                seg_kwargs[key] = slugify(value)
        path_segment = path_segment.format(*seg_args, **seg_kwargs)
    except KeyError as e:
        # format() throws KeyError - missing expected kwarg
        # Remap this to a TypeError such as user would get when calling a
        # function with an expected kwarg, as that's what this effectively is.
        raise TypeError("get_path() missing required keyword argument: '{0}'"
                        .format(e.args[0]))
    except IndexError:
        # IndexError - missing expected arg
        # Remap this to a TypeError such as user would get when calling a
        # function with required positional args.
        raise TypeError("get_path() missing required positional argument")

    path = os.path.join(parent_path, path_segment)
    if (create or autocreate) and not os.path.exists(path):
        log.info("Creating new '{0}' directory path {1}".format(key, path))
        os.makedirs(path)
    elif flush and os.path.exists(path):
        if not os.path.isdir(path):
            log.warning("Deleting file %s and replacing it with a directory. "
                        "This shouldn't be typical - check how this happened",
                        path)
        shutil.rmtree(path)
        os.makedirs(path)

    return path


# Set yangsuite standard paths
# Plugins will likely extend this list
register_path('users_dir', 'users', autocreate=True)
register_path('user', '{user}', parent='users_dir', autocreate=False)
register_path('log_dir', 'logs/', autocreate=True)
register_path('logfile', '{filename}', parent='log_dir', autocreate=False)


def list_paths():
    """Get the list of all currently registered paths.

    Returns:
      dict: of {key: pathspec_str}
    """
    global _base_path
    global _paths

    results = {}
    if _base_path is not None:
        for key in sorted(_paths.keys()):
            parent, path_segment, _, _ = _paths[key]
            pathspec = path_segment
            while parent is not None:
                parent, path_segment, _, _ = _paths[parent]
                pathspec = os.path.join(path_segment, pathspec)
            pathspec = os.path.join(_base_path, pathspec)
            results[key] = pathspec

    return results
