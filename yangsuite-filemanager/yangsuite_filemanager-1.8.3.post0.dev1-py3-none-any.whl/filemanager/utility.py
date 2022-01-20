# Copyright 2016 Cisco Systems, Inc
import errno
import filecmp
import io
import os
import shutil
import traceback

from contextlib import contextmanager
from slugify import slugify

from yangsuite import get_logger, get_path
from ..quickparser import name_and_revision_from_file, module_listing


log = get_logger(__name__)


def repository_path(owner, reponame):
    """Get the correctly slugified repository path.

    Args:
      owner (str): Owner of this repository
      reponame (str): Unicode or slugified ASCII name of the repository
    Returns:
      str: The correct repository path
    """
    return get_path('repository', user=owner, reponame=reponame)


def yangset_path(owner, setname):
    """Get the correctly slugified yangset path.

    Args:
      owner (str): Owner of this yangset
      setname (str): Unicode or slugified ASCII name of the yangset
    Returns:
      str: The correct yangset path
    """
    return get_path('yangset', user=owner, setname=setname)


def merge_user_set(username, set_or_repo_name):
    """Combine (username, set_or_repo_name) tuple into a single slug string.

    >>> merge_user_set('user', 'some yangset!')
    'user+some-yangset'
    >>> split_user_set('user+some-yangset')
    ('user', 'some-yangset')
    """
    return "{0}+{1}".format(username, slugify(set_or_repo_name))


def split_user_set(userset):
    """Split merge_user_set() string back to a (user, set_or_repo_name) tuple.

    Whether this returns a setname or a reponame is up to the caller to
    understand; there's no difference in the logic of this function.

    >>> split_user_set('user+yangset')
    ('user', 'yangset')
    >>> merge_user_set('user', 'yangset')
    'user+yangset'
    >>> split_user_set('user:yangset')
    ('user', 'yangset')
    """
    if '+' in userset:
        user, set_or_repo_name = userset.split('+')
    elif ':' in userset:   # backward compatibility
        user, set_or_repo_name = userset.split(':')
    else:
        raise ValueError(
            "Unable to split yangset string '{0}'".format(userset))

    log.debug('Split userset "%s" to user "%s", setname/reponame "%s"',
              userset, user, set_or_repo_name)
    return (user, set_or_repo_name)


def list_yang_files(path_or_paths, include_subdirs=False):
    """Find all .yang files in the given path or paths.

    Args:
      path_or_paths (str, list): Path to a directory or to a single .yang file,
        or a list of such paths
      include_subdirs (bool): If True, will list files in subdirectories
        of the requested directory; otherwise, will only include files in
        the directory itself.
    Returns:
      list: List of absolute paths to .yang files
    Raises:
      OSError: if a string is given but is not a path that exists
      ValueError: if a path exists but does not represent a file or dir
      TypeError: if path_or_paths is neither a string nor an iterable
    """
    if isinstance(path_or_paths, str):
        path = path_or_paths
        if not os.path.exists(path):
            raise OSError(errno.ENOENT, os.strerror(errno.ENOENT), path)
        elif os.path.isdir(path):
            if not include_subdirs:
                return [os.path.join(path, f)
                        for f in sorted(os.listdir(path))
                        if f.endswith('.yang')]
            else:
                # Walk the directory and its subdirectories
                result = []
                for root, dirs, files in os.walk(path):
                    result += [os.path.join(root, f)
                               for f in sorted(files) if f.endswith('.yang')]
                return result
        elif os.path.isfile(path) and path.endswith('.yang'):
            return [path]
        else:
            raise ValueError("{0} is neither a YANG file nor a directory."
                             .format(path))
    # Not a string or unicode.
    # Maybe it's a list, tuple, or other iterable?
    result = []
    for path in path_or_paths:
        result += list_yang_files(path, include_subdirs)
    return sorted(result)


def report_yang_files(yangdir):
    """Get list of (module, revision, filename) in the given directory.

    Differs from YSYangSet.get_modules_and_revisions in its use of filename
    rather than absolute path.

    Args:
      yangdir (str): Path to directory containing YANG files.

    Returns:
      list: [(mod1, rev1, file1), (mod2, rev2, file2), etc.]
    """
    if not os.path.isdir(yangdir):
        return []
    paths = list_yang_files(yangdir)
    results = module_listing(paths)

    results = sorted((mod, rev, os.path.basename(path))
                     for (mod, rev, path) in results)

    log.debug("YANG files in %s: %s", yangdir, results)
    return results


def migrate_yang_files(src_path, dest_path,
                       remove=True, include_subdirs=False):
    """Move or copy yang files, fixing up filenames on the way.

    Schemas with a revision will be named '<name>@<revision>.yang', while
    schemas with no revision will be named '<name>.yang'

    Args:
      src_path (str): File or directory path to copy from
      dest_path (str): Directory path to copy to
      remove (bool): If True (default), delete the file(s) from src_path
        after copying them to dest_path. If False, leave them alone.
      include_subdirs (bool): If False (default), only get files from
        the src_path directory itself; if True, get files from subdirectories
        of src_path as well.
    Returns:
      dict: with format::

            {'added': [list of (module, revision) added to dest_path],
             'updated': [list of (module, revision) replaced with new files]
             'unchanged': [list of (module, rev) already in dest_path],
             'errors': [list of (filename, error message)],
            }
    """
    src_files = list_yang_files(src_path, include_subdirs)
    log.debug("Adding %d files from %s to %s",
              len(src_files), src_path, dest_path)

    results = {'added': [], 'updated': [], 'unchanged': [], 'errors': []}
    if not os.path.isdir(dest_path):
        results['errors'].append((dest_path, 'No such directory'))
        return results

    for src_file in src_files:
        filename = os.path.basename(src_file)
        try:
            name, revision = name_and_revision_from_file(
                src_file, assume_correct_name=False)
        except ValueError as exc:
            results['errors'].append((filename, str(exc)))
            continue

        # For us, 'name.yang' and 'name@unknown.yang' both mean the same thing,
        # but pyang.FileRepository only understands the former - so comply.
        if revision not in [None, 'unknown', '']:
            dest_filename = "{0}@{1}.yang".format(name, revision)
        else:
            dest_filename = "{0}.yang".format(name)
        dest_file = os.path.join(dest_path, dest_filename)

        if not os.path.exists(dest_file):
            shutil.copyfile(src_file, dest_file)
            results['added'].append((name, revision))
        elif filecmp.cmp(src_file, dest_file):
            results['unchanged'].append((name, revision))
        else:
            shutil.copyfile(src_file, dest_file)
            results['updated'].append((name, revision))

    if not (results['added'] or results['unchanged']
            or results['updated'] or results['errors']):
        results['errors'].append((src_path, "No YANG files found"))
        return results

    if remove:
        for src_file in src_files:
            try:
                os.remove(src_file)
            except OSError as e:
                log.debug(traceback.format_exc())
                log.warning("Unable to delete source file %s: %s",
                            src_file, e)

    log.debug("File add/upload completed. "
              "%d files added, %d updated, %d unchanged, %d errors",
              len(results['added']), len(results['updated']),
              len(results['unchanged']), len(results['errors']))

    return results


@contextmanager
def atomic_create(filepath, reraise, encoding='ascii'):
    """Open the specified filepath for writing and yield.

    If an error occurs while writing, delete the file in order to avoid
    leaving garbage behind in the form of a half-written file.

    Example::

        with atomic_create('/path/to/file') as fd:
            fd.write("Hello")
            raise RuntimeError
            fd.write("Goodbye")
        # as an error was raised, file is removed before returning

    Args:
      filepath (str): File path to create and open
      reraise (bool): Whether to re-raise any exceptions after cleaning up
      encoding (str): 'ascii', 'utf-8', etc.
    """
    try:
        with io.open(filepath, 'w', encoding=encoding) as fd:
            yield fd
    except Exception:
        log.debug(traceback.format_exc())
        # Don't leave a half-written file around to cause trouble
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
            except:
                log.debug(traceback.format_exc)
                if reraise:
                    raise
        if reraise:
            raise


user_status = {}


def do_validation(user, yangset, quick=True):
    """Check and report the validity of the given yangset.

    Args:
      user (str): Username owning this request
      yangset (YSYangSet): YANG set to validate
      quick (bool, str): if 'true' or True, only call the yangset's own
        validate() function; if 'false' or False, create a YSContext around
        this yangset and call its validate() (more thorough but slower)
    Returns:
      dict: {'reply': list of dicts - see YSYangSet.validate()}
    """
    global user_status

    if not yangset.get_modules_and_revisions():
        return {'reply': {}}

    user_status[user] = {
        'value': 0,
        'max': 0,
        'info': 'Validation in progress',
    }

    if quick and quick != 'false':
        result = yangset.validate()
    else:
        from ysyangtree import YSContext
        ctx = YSContext(yangset, user)
        result = ctx.validate()

    reply = {'reply': result}
    if user in user_status:
        del user_status[user]
    return reply


def validation_status(user):
    """Report on the current status of a do_validation() request.

    Args:
      user (str): User whose request we are interested in.
    Returns:
      dict: {'value': x, 'max': x+y, 'info': string}
    """
    global user_status

    if user not in user_status:
        return {
            'value': 0,
            'max': 0,
            'info': 'No request in progress'
        }
    result = user_status[user].copy()
    from ysyangtree import YSContext
    ctx = YSContext.get_instance(user)
    if ctx:
        result['value'] += ctx.load_status['count']
        result['max'] += ctx.load_status['total']
        result['info'] = ctx.load_status['info']

    return result


if __name__ == '__main__':   # pragma: no cover
    import doctest
    doctest.testmod()
