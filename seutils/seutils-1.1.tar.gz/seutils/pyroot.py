import seutils
import os.path as osp
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
            import ROOT
            IS_INSTALLED = True
        except ImportError:
            IS_INSTALLED = False
    return IS_INSTALLED

def is_tdir(thing):
    import ROOT
    return isinstance(thing, ROOT.TDirectory)

@contextmanager
def open_root(path, mode='READ'):
    '''
    Does nothing if a TDirectory-like object is passed
    '''
    do_open = not(is_tdir(path))
    with suppress_root_warnings():
        try:
            if do_open:
                import ROOT
                tfile = ROOT.TFile.Open(path, mode)
                yield tfile
            else:
                yield path
        finally:
            if do_open: tfile.Close()

@contextmanager
def suppress_root_warnings():
    import ROOT
    _root_log_level = int(ROOT.gErrorIgnoreLevel)
    try:
        ROOT.gErrorIgnoreLevel = ROOT.kError
        yield None
    finally:
        ROOT.gErrorIgnoreLevel = _root_log_level


def _iter_treepaths_recursively_root(node, prefix=''):
    """
    Takes a ROOT TDirectory-like node, and traverses through
    possible sub-TDirectories to yield the names of all TTrees.
    Can take a TFile.
    """
    listofkeys = node.GetListOfKeys()
    n_keys = listofkeys.GetEntries()
    for i_key in range(n_keys):
        key = listofkeys[i_key]
        classname = key.GetClassName()
        # Recurse through TDirectories
        if classname == 'TDirectoryFile':
            dirname = key.GetName()
            lower_node = node.Get(dirname)
            for tree in _iter_treepaths_recursively_root(lower_node, prefix=prefix+dirname+'/'):
                yield tree
        elif not classname == 'TTree':
            continue
        else:
            treename = key.GetName()
            yield prefix + treename

def trees(rootfile):
    with open_root(rootfile) as tf:
        return list(sorted(_iter_treepaths_recursively_root(tf)))

def trees_and_counts(rootfile, branches=False):
    r = []
    with open_root(rootfile) as tf:
        for treepath in _iter_treepaths_recursively_root(tf):
            tree = tf.Get(treepath)
            nentries = tree.GetEntries()
            if branches:
                r.append((treepath, nentries, list(b.GetName() for b, l in iter_branches(tree))))
            else:
                r.append((treepath, nentries))
    r.sort()
    return r

def branches(rootfile, treepath=None):
    with open_root(rootfile) as tf:
        if treepath is None:
            treepath = seutils.root.select_most_likely_tree(trees(tf))
        tree = tf.Get(treepath)
        return list(iter_branches(tree))

def iter_branches(node, level=1):
    """
    Yields branches in a ttree recursively
    """
    listofbranches = node.GetListOfBranches()
    n_branches = listofbranches.GetEntries()
    for i_branch in range(n_branches):
        branch = listofbranches[i_branch]
        yield branch, level
        for subbranch, sublevel in iter_branches(branch, level=level+1):
            yield subbranch, sublevel
