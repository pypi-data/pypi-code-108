import seutils
import os
import os.path as osp
import json
import datetime
import tempfile

from seutils import add_env_kwarg

from . import pyroot
from . import _uproot


# _______________________________________________________
# Get commands

_implementations = [ _uproot, pyroot ]
_commands = [ 'trees', 'trees_and_counts', 'branches', 'iter_branches' ]

def get_implementation(name):
    """
    Takes the name of a submodule that contains implementations. Returns that module object.
    """
    for implementation in _implementations:
        if implementation.__name__.rsplit('.',1)[-1] == name:
            break
    else:
        raise Exception('No such implementation: {0}'.format(name))
    return implementation

def get_command(cmd_name, implementation=None):
    """
    Returns an implementation of a command.
    Parameter `implementation` is a module object; it can also be a name of a module.
    If it's None, a heuristic is ran to guess the best implementation.
    The `path` parameter is optional and only serves to make a better guess for the implementation.
    """
    if not cmd_name in _commands:
        raise Exception('Invalid command: {0}'.format(cmd_name))
    if implementation is None:
        implementation = best_implementation_heuristic(cmd_name)[0]
    elif seutils.is_string(implementation):
        implementation = get_implementation(implementation)
    if not hasattr(implementation, cmd_name):
        raise Exception(
            'Implementation {0} has no function {1}'
            .format(implementation.__name__, cmd_name)
            )
    return getattr(implementation, cmd_name)

def best_implementation_heuristic(cmd_name):
    """
    Determines the best implementation.
    """

    # Grid protocols
    preferred_order = []
    def check(module):
        if module.is_installed() and hasattr(module, cmd_name) and not(module in preferred_order):
            preferred_order.append(module)
    check(_uproot)
    check(pyroot)
    if not len(preferred_order):
        raise Exception(
            'No good implementation could be found for cmd {0}'
            .format(cmd_name)
            )
    seutils.logger.info('Using module %s to execute \'%s\'', preferred_order[0].__name__, cmd_name)
    return preferred_order


# _______________________________________________________
# Central entry points for root commands

@add_env_kwarg
def trees(rootfile, implementation=None):
    return get_command('trees', implementation)(rootfile)

@add_env_kwarg
def trees_and_counts(rootfile, branches=False, implementation=None):
    return get_command('trees_and_counts', implementation)(rootfile, branches)

@add_env_kwarg
def branches(rootfile, treepath=None, implementation=None):
    return get_command('branches', implementation)(rootfile, treepath)

@add_env_kwarg
def iter_branches(tree, treepath=None, implementation=None):
    return get_command('iter_branches', implementation)(tree)


# _______________________________________________________
# Algo's using the basic root functions above

# def write_count_cache(cache, dst, failure_ok=True, delete_first=False):
#     '''
#     Writes the cache to dst by first opening a tempfile, copying it, and deleting the tempfile.

#     If `failure_ok` is True, any encountered exceptions are ignored (since typically writing
#     to the cache isn't critical).

#     If `delete_first` is True it is attempted to delete the file first.

#     Returns True if cache is successfully written.
#     '''
#     try:
#         try:
#             fd, path = tempfile.mkstemp()
#             with open(path, 'w') as f:
#                 json.dump(cache, f, indent=2, sort_keys=True)
#             if delete_first:
#                 try:
#                     seutils.rm(dst)
#                 except Exception:
#                     # Not a big deal if this fails
#                     pass
#             seutils.cp(path, dst)
#         finally:
#             os.close(fd)
#     except Exception:
#         if failure_ok:
#             seutils.logger.warning('Could not write cache to %s', dst)
#             return False
#         else:
#             raise
#     return True

def write_count_cache(cache, dst=None, failure_ok=True):
    '''
    Writes the cache to dst by first opening a tempfile, copying it, and deleting the tempfile.

    If `failure_ok` is True, any encountered exceptions are ignored (since typically writing
    to the cache isn't critical).

    If `delete_first` is True it is attempted to delete the file first.

    Returns True if cache is successfully written.
    '''
    if dst is None: dst = cache.cache_path
    try:
        try:
            fd, path = tempfile.mkstemp()
            with open(path, 'w') as f:
                cache.meta['last_update'] = datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S')
                json.dump(dict(_meta=cache.meta, **cache.cache), f, indent=2, sort_keys=True)
            if cache.inode:
                try:
                    seutils.rm(dst)
                except Exception:
                    # Not a big deal if this fails
                    pass
            seutils.cp(path, dst)
        finally:
            os.close(fd)
    except Exception:
        if failure_ok:
            seutils.logger.warning('Could not write cache to %s', dst)
            return False
        else:
            raise
    return True

class Cache:
    """
    Wrapper class for a rootfile count cache.
    If noload=True, the cache is not read from the file and initialized empty.
    """
    def __init__(self, cache_path, noload=False):
        self.cache_path = cache_path
        if not(noload) and self.inode:
            self.cache = json.loads(seutils.cat(self.cache_path))
        else:
            self.cache = {}
        # The `_meta` entry of the returned dict is not a rootfile,
        # but contains some meta info about the cache
        self.meta = self.cache.pop('_meta', {})
        self.is_updated = False

    def __getitem__(self, rootfile):
        """
        Basically self.cache.__getitem__, but filters the _mtime key
        """
        # Should rightly raise a KeyError if rootfile is not in the cache
        item = self.cache[rootfile]
        item.pop('_mtime', None)
        return item

    def __contains__(self, rootfile):
        return rootfile in self.cache

    # Some standard dict methods, using the overwritten __getitem__
    def keys(self):
        return self.cache.keys()
    def values(self):
        for k in self.keys():
            yield self[k]
    def items(self):
        for k in self.keys():
            yield k, self[k]

    @property
    def inode(self):
        if not hasattr(self, '_inode'):
            self._inode = seutils.stat(self.cache_path, not_exist_ok=True)
        return self._inode

    def lastupdate(self, rootfile):
        """
        Returns the time of the last update of a specific rootfile entry
        """
        item = self.cache[rootfile]
        return datetime.datetime.strptime(item['_mtime'], '%Y%m%d_%H%M%S')

    def __setitem__(self, rootfile, counts):
        """
        Updates the cache, so an _mtime is added to the entry and the cache
        is marked as updated
        """
        counts['_mtime'] = datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        self.is_updated = True
        self.cache[rootfile] = counts


def count_dataset(directory, read_cache=True, write_cache=True, rootfiles=None):
    '''
    Looks for all root files in `directory` and counts the number of entries in all trees.

    By default a cache is created in `{directory}/.seucounts.json`, so that subsequent calls
    are faster.

    If `read_cache` is False, the cache is not read and assumed empty.
    If `write_cache` is False, the (potentially updated) cache will not be written.

    If `rootfiles` is specified, only those root files will be attempted to be read
    from the cache, and only those will be updated in the cache
    '''
    dir_inode = seutils.stat(directory)
    if dir_inode.isfile:
        raise Exception('{} is a file, not a directory'.format(directory))
    
    # If rootfiles are passed, make sure they have a proper mgm
    if rootfiles: rootfiles = [seutils.format(r) for r in rootfiles]

    cache = Cache(osp.join(directory, '.seucounts.json'), noload=not(read_cache))

    # If cache exists, and is up to date (i.e. newer or as old as the dir modtime),
    # it might be possible to do a shortcut and save some interactions
    # with the storage element
    if cache.inode and dir_inode.modtime <= cache.inode.modtime:
        rootfiles_in_cache = set(cache.keys())
        if rootfiles:
            set_rootfiles = set(osp.basename(p) for p in rootfiles)
        else:
            set_rootfiles = set(osp.basename(p) for p in seutils.ls_wildcard(osp.join(directory, '*.root')))
        if set_rootfiles.issubset(rootfiles_in_cache):
            # All the requested rootfiles are in the cache
            # Remove the rootfiles in the cache that were not 
            # asked for, and return
            seutils.logger.warning(
                'All requested rootfiles contained; Returning cached result (%s)',
                cache.inode.modtime
                )
            cache.cache = { k:v for k,v in cache.items() if k in set_rootfiles }
            return cache

    # Get list of inodes of contained rootfiles, or only the specified rootfiles
    if rootfiles is None:
        rootfiles = seutils.ls_wildcard(osp.join(directory, '*.root'), stat=True)
    else:
        rootfiles = [seutils.stat(r) for r in rootfiles]

    # Update the cache for the rootfiles
    for inode in rootfiles:
        # Double-check the rootfile is actually in the directory
        if osp.dirname(inode.path).rstrip('/') != directory.rstrip('/'):
            raise Exception('rootfile {} is not in {}'.format(inode.path, directory))
        rootfile = inode.basename
        if rootfile in cache and cache.lastupdate(rootfile) > inode.modtime:
            seutils.logger.debug('Cache is up to date for %s', inode.path)
        else:
            # Have to update the cache
            seutils.logger.debug('Updating cache for %s', inode.path)
            cache[rootfile] = { k:v for k, v in seutils.root.trees_and_counts(inode.path) }

    # If the cache is updated, dump it to the cache file
    if write_cache and cache.is_updated: write_count_cache(cache)

    # Filter unasked rootfiles, if any
    set_rootfiles = set(osp.basename(i.path) for i in rootfiles)
    cache.cache = { k:v for k,v in cache.items() if k in set_rootfiles }
    return cache

def sum_dataset(directory, treepath=None, **kwargs):
    '''
    Returns only the sums of all entries
    If treepath is specified it returns a single int,
    otherwise it returns a dict of { treepath : count }
    '''
    output = count_dataset(directory, **kwargs)
    # Compute the tree total counts
    tree_totals = {}
    for rootfile, values in output.items():
        for key, value in values.items():
            if key == '_mtime': continue
            tree_totals.setdefault(key, 0)
            tree_totals[key] += value
    return tree_totals if treepath is None else tree_totals[treepath]

def select_most_likely_tree(trees):
    """
    Selects the 'most likely' tree the user intended from a list of trees.
    Typically this is the first one, minus some default CMSSW trees.
    """
    # Prefer other trees over these standard CMSSW trees
    filtered_trees = [ t for t  in trees if not t in [
        'MetaData', 'ParameterSets', 'Parentage', 'LuminosityBlocks', 'Runs'
        ]]
    # Pick the most likely tree
    if len(filtered_trees) == 0 and len(trees) >= 1:
        tree = trees[0]
        ignored_trees = trees[1:]
    elif len(filtered_trees) >= 1:
        tree = filtered_trees[0]
        ignored_trees = [ t for t in trees if not t == tree ]
    seutils.logger.info(
        'Using tree %s%s',
        tree,
        ' (ignoring {0})'.format(', '.join(ignored_trees)) if len(ignored_trees) else ''
        )
    return tree

def nentries(rootfile, treepath=None, **kwargs):
    '''
    Like count_dataset, but for a single file.
    If treepath is specified, returns the counts for that tree only
    '''
    directory = osp.dirname(rootfile)
    kwargs['rootfiles'] = [rootfile]
    entry = list(count_dataset(osp.dirname(rootfile), **kwargs).values())[0]
    return entry if treepath is None else entry[treepath]
