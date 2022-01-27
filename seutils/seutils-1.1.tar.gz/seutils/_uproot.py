import seutils
import os.path as osp, sys
from contextlib import contextmanager
from seutils import run_command, get_exitcode, Inode, split_mgm
logger = seutils.logger

IS_INSTALLED = None
def is_installed():
    """
    Checks whether ROOT is on the python path
    """
    global IS_INSTALLED
    if IS_INSTALLED is None:
        try:
            import uproot
            IS_INSTALLED = True
        except ImportError:
            IS_INSTALLED = False
    return IS_INSTALLED

@contextmanager
def open_root(path, mode='READ'):
    '''
    Does nothing if an open uproot object is passed
    '''
    do_open = seutils.is_string(path)
    try:
        yieldable = path
        if do_open:
            import uproot
            logger.debug('Opening %s with uproot', path)
            yieldable = uproot.open(path)
        yield yieldable
    finally:
        if do_open:
            try:
                yieldable.close()
            except Exception:
                pass

def trees(rootfile):
    with open_root(rootfile) as f:
        return [ k.rsplit(';',1)[0] for k, v in sorted(f.items()) if repr(v).startswith('<TTree') ]


def _make_str(s):
    if sys.version_info[0] >= 3 and isinstance(s, bytes):
        return s.decode()
    return s

def _iter_trees(f, prefix='', seen=None, depth=0):
    # Keep a memo of seen memory addresses to avoid double counting
    if seen is None: seen = set()
    if id(f) in seen: return
    seen.add(id(f))
    # Get a name; some 2/3 and uproot version compatibility issues here
    try:
        name = _make_str(f.name)
    except AttributeError:
        if len(f.path) == 0:
            name = ''
        else:
            name = '/'.join([_make_str(p) for p in f.path])
    name = prefix + name.rsplit('/',1)[-1]
    classname = repr(f)
    if classname.startswith('<ROOTDirectory') \
        or classname.startswith('<ReadOnlyDirectory'):
        for value in f.values():
            # `yield from` is python 3 only
            for _ in _iter_trees(
                value,
                prefix=name + '/' if depth>0 else '',
                seen=seen, depth=depth+1
                ):
                yield _
    elif classname.startswith('<TTree'):
        yield name, f

def trees_and_counts(rootfile, branches=False):
    r = []
    with open_root(rootfile) as f:
        for treename, tree in sorted(_iter_trees(f)):
            treename = treename.rsplit(';',1)[0]
            # Some uproot version incompatibilities
            try:
                numentries = tree.num_entries
            except AttributeError:
                numentries = tree.numentries
            if branches:
                try:
                    branches_ = [_make_str(b.name) for b in tree.branches]
                except AttributeError:
                    branches_ = [_make_str(k) for k in tree.keys()]
            r.append(
                (treename, numentries, branches_)
                if branches else (treename, numentries)
                )
    return r


def branches(rootfile, treepath=None):
    with open_root(rootfile) as f:
        if treepath is None:
            treepath = seutils.root.select_most_likely_tree(trees(f))
        tree = f[treepath]
        for key in tree.keys(recursive=True):
            value = tree[key]
            yield (value, 1)

