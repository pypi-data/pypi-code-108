from omfit_classes.utils_base import *
from omfit_classes.utils_base import _available_to_user_math, _available_to_user_util, _available_to_user_plot

import numpy as np
import pickle
import functools
import ast
import filecmp
import types
import shutil
import copy
import difflib
import re
import pprint
import warnings
import traceback
from collections.abc import MutableMapping

__all__ = [
    'hide_ptrn',
    'private_ptrn',
    'comment_ptrn',
    'comment_ptrn_in_brackets',
    'number_ptrn',
    'sortHuman',
    'get_bases',
    'parseBuildLocation',
    'parseLocation',
    'traverseLocation',
    'buildLocation',
    'setLocation',
    'dirbaseLocation',
    'traverse',
    'treeLocation',
    'recursiveUpdate',
    'pretty_diff',
    'prune_mask',
    'dynaLoad',
    'dynaLoadKey',
    'dynaSave',
    'dynaLoader',
    'dynaSaver',
    'SortedDict',
    'OMFITdataset',
    'pickle',
    'size_tree_objects',
    'sorted_join_lists',
]

# Useful patterns
hide_ptrn = re.compile(r'^__.*__$')
private_ptrn = re.compile(r'^_.*[^_]+$')
comment_ptrn = re.compile(r'^__comment.*__$')
comment_ptrn_in_brackets = re.compile(r'''.*\[['"]__comment.*__['"]\].*''')
number_ptrn = re.compile(r"[-+]?\d*\.?\d+[eEdD][-+\d]+|[-+\d]+\.\d+|\d+")

_special1 = []


@_available_to_user_util
def sortHuman(inStr):
    """Sort the given list the way that humans expect"""
    outStr = str(inStr).lower()
    tmp = re.findall(number_ptrn, outStr)
    outStr = re.sub(number_ptrn, '\1', outStr)
    for kn in tmp:
        kn = re.sub(r'[dD]', 'e', kn)
        try:
            outStr = re.subn('\1', format(float(kn), "+040.16f"), outStr, 1)[0]
        except ValueError:
            pass
    outStr = re.sub(r'-', 'm', outStr)
    outStr = re.sub(r'\+', 'p', outStr)
    return outStr


def _insort(a, x, caseInsensitive=True):
    lo = 0
    hi = len(a)
    while lo < hi:
        mid = (lo + hi) // 2
        if caseInsensitive and str(x).lower() < str(a[mid]).lower():
            hi = mid
        elif not caseInsensitive and str(x) < str(a[mid]):
            hi = mid
        else:
            lo = mid + 1
    a.insert(lo, x)


def get_bases(clss, tp=[]):
    "Returns a list of strings describing the dependencies of a class"
    if tp == []:
        tp = [clss.__name__]
    bases = getattr(clss, '__bases__')
    if not len(bases):
        return tp
    else:
        for item in bases:
            tp.append(item.__name__)
            get_bases(item, tp)
    return tp


@_available_to_user_util
def different(a, b, precision=0.0):
    """
    Evaluates if two objects are different

    :param a: first object to compare

    :param b: second object to compare

    :param precision: relative precision to which objects are compared

    :return: integer to indicate equal (0) or different (1)
    """
    if isinstance_str(a, ['OMFITexpression', 'OMFITiterableExpression']) and isinstance_str(
        b, ['OMFITexpression', 'OMFITiterableExpression']
    ):
        if a.expression != b.expression:
            return 1
    elif a.__class__ != b.__class__:
        return 1
    elif hasattr(a, 'filename') and hasattr(b, 'filename'):
        if not os.path.exists(a.filename) or not os.path.exists(b.filename):
            return 1
        elif not filecmp.cmp(a.filename, b.filename):
            return 1
        elif not filecmp.cmp(a.filename, b.filename, shallow=False):
            return 1
        elif os.path.split(a.filename)[1] != os.path.split(b.filename)[1]:
            return 1
        return 0
    else:
        try:
            np.testing.assert_equal(a, b)
            return 0
        except Exception:
            if precision == 0.0:
                return 1
            try:
                np.testing.assert_allclose(a, b, rtol=precision)
                return 0
            except Exception:
                return 1
    return 0


@_available_to_user_util
def sorted_join_lists(a, b, favor_order_of_a=False, case_insensitive=False):
    """
    Join two lists in a way that minimizes the distance between them and the merged list

    :param a: first list

    :param b: second list

    :param favor_order_of_a: favor order of list `a` over order of list `b`

    :param case_insensitive: merge list in a case-insensitive way

    :return: merged list
    """
    a = list(map(repr, a))
    b = list(map(repr, b))

    # use difflib.Differ (which operates on strings) to find out differences
    if favor_order_of_a:
        keys = list(difflib.Differ(linejunk=None).compare(b, a))
    else:
        keys = list(difflib.Differ(linejunk=None).compare(a, b))

    # NOTE: change of order are done by removing (-) and adding (+) an entry
    keys = [ast.literal_eval(k[2:]) for k in keys if k[2:] and k[0] != '?' and (k[0] != '-' or (k[0] == '-' and '+' + k[1:] not in keys))]
    # unique keys, keep the ordering, allow caseInsensitive
    if case_insensitive:
        tmp = [_f.lower() if isinstance(_f, str) else _f for _f in keys]
        keys = [_f for k, _f in enumerate(keys) if (_f.lower() if isinstance(_f, str) else _f) not in tmp[:k]]
    else:
        keys = [_f for k, _f in enumerate(keys) if _f not in keys[:k]]
    return keys


@_available_to_user_util
def parseLocation(inv):
    """
    Parse string representation of the dictionary path and return list including root name
    This function can parse things like: OMFIT['asd'].attributes[u'aiy' ]["[  'bla']['asa']"][3][1:5]

    :param inv: string representation of the dictionary path

    :return: list of dictionary keys including rootname
    """
    # look for matching dictionary blocks with matching quotes
    inv = inv.strip()
    quote = False
    starts_at = 0
    splits = []
    k = 0
    char = None
    head = ['']
    while k < len(inv):
        if inv[k] not in ' \t':
            new_char = inv[k]
        if new_char == '[' and not quote:
            if inv[k + 1] in ["'", '"']:
                quote = inv[k + 1]
            elif inv[k + 1] in 'bru' and inv[k + 2] in ["'", '"']:
                quote = inv[k + 2]
            else:
                quote = True
            starts_at = k + 1
        if inv[k] == ']' and (quote is True or last_char == quote):
            quote = False
            splits.append(inv[starts_at:k])

        if not quote and inv[k] not in ' \t[]':
            splits = []
            head = [inv[: k + 1]]
        if inv[k] not in ' \t':
            last_char = inv[k]
        k = k + 1

    # if quote was not closed then the parentheses do not match
    if quote:
        raise SyntaxError('Unbalanced parentheses in ' + inv)

    # eval splits
    for k, item in enumerate(splits):
        try:
            splits[k] = ast.literal_eval(item)
        except SyntaxError:
            if ':' in item:
                splits[k] = item
            else:
                raise
    return head + splits


@_available_to_user_util
def buildLocation(inv):
    """
    Assemble list of keys into dictionary path string

    :param inv: list of dictionary keys including rootname

    :return: string representation of the dictionary path
    """
    tmp = inv[0]
    for item in inv[1:]:
        if isinstance(item, str):
            if ':' in item and not re.findall('[a-zA-Z]', item):
                tmp += '[' + item + ']'
            else:
                tmp += '[' + repr(item) + ']'
        else:
            tmp += '[' + repr(item) + ']'
    return tmp


@_available_to_user_util
def dirbaseLocation(location):
    """
    Takes a string or a list of stirings output by parseLocation()
    and returns two strings for convenient setting of dictionary locations

    >> d, b=dirbaseLocation("OMFIT['dir']['base']")
    >> eval(d)[b]
    d = OMFIT['dir']
    b = 'base'

    :param location: string or a list of stirings output by parseLocation()

    :return: two string, the first one with the path leading to the leaf, the second with the name of the leaf
    """
    if not isinstance(location, list):
        location = parseLocation(location)
    return buildLocation(location[:-1]), location[-1]


@_available_to_user_util
def setLocation(location, value, globals=None, locals=None):
    """
    Takes a string or a list of stirings output by parseLocation()
    and set the leaf to the value provided

    :param location:  string or a list of stirings output by parseLocation()

    :param value: value to set the leaf

    :param globals: global namespace for the evaluation of the location

    :param locals: local namespace for the evaluation of the location

    :return: value
    """
    d, b = dirbaseLocation(location)
    eval(d, globals, locals)[b] = value
    return value


def parseBuildLocation(inv):
    """
    DEPRECATED: use `parseLocation` and `buildLocation` functions instead

    Function to handle locations in the OMFIT tree (i.e. python dictionaries)

    :param inv: input location

    :return:

    * if `inv` is a string, then the dictionary path is split and a list is returned (Note that this function strips the root name)

    * if it's a list, then the dictionary path is assembled and a string is returned (Note that this function assumes that the root name is missing)
    """
    if isinstance(inv, str):
        return parseLocation(inv)[1:]
    elif isinstance(inv, list):
        return buildLocation([''] + inv)
    else:
        raise ValueError('parseBuildLocation accepts either a string or a list')


@_available_to_user_util
def traverseLocation(inv):
    """
    returns list of locations to reach input location

    :param inv: string representation of the dictionary path

    :return: list of locations including rootname to reach input location
    """
    tmp = parseLocation(inv)
    return [buildLocation(tmp[:k]) for k in range(1, len(tmp) + 1)]


@_available_to_user_util
def traverse(
    self,
    string='',
    level=100,
    split=True,
    onlyDict=False,
    onlyLeaf=False,
    skipDynaLoad=False,
    noSubmodules=False,
    traverse_classes=(MutableMapping,),
):
    """
    Returns a string or list of strings describing the path of every entry/subentries in the dictionary

    :param string: string to be appended in front of all entries

    :param level: maximum depth

    :param split: split the output string into a list of strings

    :param onlyDict: return only dictionary entries (can be a tuple of classes)

    :param onlyLeaf: return only non-dictionary entries (can be a tuple of classes)

    :param skipDynaLoad: skip entries that have .dynaLoad==True

    :param noSubmodules: controls whether to traverse submodules or not

    :param traverse_classes: tuple of classes to traverse

    :return: string or list of string
    """
    string_in = string
    string_out = ''
    if isinstance(self, (MutableMapping,)):
        keys = list(self.keys())
    elif isinstance(self, (list, tuple)):
        keys = list(range(len(self)))
    else:
        keys = []
    for kid in keys:
        kidName = "[" + repr(kid) + "]"
        string = string_in + kidName
        # skip also expressions when skipDynaLoad
        if skipDynaLoad and isinstance_str(self[kid], ['OMFITexpression', 'OMFITiterableExpression']):
            continue
        # mention this entry according to `onlyDict` and `onlyLeaf` filters
        if (
            (not onlyDict and not onlyLeaf)
            or (onlyDict is True and isinstance(self[kid], traverse_classes))
            or (isinstance(onlyDict, tuple) and isinstance(self[kid], onlyDict))
            or (onlyLeaf is True and not isinstance(self[kid], traverse_classes))
            or (isinstance(onlyLeaf, tuple) and isinstance(self[kid], onlyLeaf))
        ):
            string_out += string + '\n'
        # do not go deeper if skipDynaLoad and the file has not been loaded
        if skipDynaLoad and hasattr(self[kid], 'dynaLoad') and self[kid].dynaLoad:
            continue
        # go deeper
        if noSubmodules:
            from omfit_classes.omfit_base import OMFITmodule
        if (
            isinstance(self[kid], traverse_classes)
            and (not isinstance(onlyDict, tuple) or isinstance(self[kid], onlyDict))
            and level > 0
            and len(self[kid])
            and not (noSubmodules and isinstance(self[kid], OMFITmodule))
        ):
            level -= 1
            string_out += traverse(self[kid], string, level, False, onlyDict, onlyLeaf, skipDynaLoad, noSubmodules, traverse_classes)
            level += 1
    if split:
        return string_out.strip().strip('\n').split('\n') if string_out else []
    else:
        return string_out


def treeLocation(obj, memo=None):
    """
    Identifies location in the OMFIT tree of an OMFIT object

    NOTE: Typical users should not need to use this function as part of their modules.
    If you find yourself using this function in your modules, it is likely that OMFIT
    already provides the functionality that you are looking for in some other way.
    We recommend reaching out the OMFIT developers team to see if there is an easy
    way to get what you want.

    :param obj: object in the OMFIT tree

    :param memo: used internally to avoid infinite recursions

    :return: string with tree location
    """
    if hasattr(obj, '_OMFITcopyOf') and obj._OMFITcopyOf is not None:
        obj = obj._OMFITcopyOf()

    _nil = []
    if memo is None:
        memo = {}
    y = memo.get(id(obj), _nil)
    if y is not _nil:
        return y

    if not hasattr(obj, '_OMFITparent'):
        try:
            obj._OMFITkeyName = ''
            obj._OMFITparent = None
        except AttributeError:
            # this is for objects which do not accept ._OMFITparent (e.g. int, None, float,...)
            # these are only leafs in the tree and do not need their location in the tree
            # to function anyways.
            return None

    if obj._OMFITparent is None:
        # this is when to treat the head node
        tmp = [obj._OMFITkeyName]
    else:
        # this is for all of the middle nodes
        tmp = treeLocation(obj._OMFITparent)
        if tmp is not None:
            tmp.append(tmp[-1] + obj._OMFITkeyName)

    memo[id(obj)] = tmp
    _keep_alive(obj, memo)
    return tmp


def _keep_alive(x, memo):
    """Keeps a reference to the object x in the memo.

    Because we remember objects by their id, we have
    to assure that possibly temporary objects are kept
    alive by referencing them.
    We store a reference at the id of the memo, which should
    normally not be used unless someone tries to deepcopy
    the memo itself...
    """
    try:
        memo[id(memo)].append(x)
    except KeyError:
        # aha, this is the first one :-)
        memo[id(memo)] = [x]


@_available_to_user_util
def recursiveUpdate(A, B, overwrite=True, **kw):
    """
    Recursive update of dictionary A based on data from dictionary B

    :param A: dictionary A

    :param B: dictionary B

    :param overwrite: force overwrite of duplicates

    :return: updated dictionary
    """
    # for backward compatibility
    if 'overWrite' in kw:
        overwrite = kw.pop('overWrite')
    if len(kw):
        raise TypeError('recursiveUpdate() got an unexpected keyword argument: ' + str(list(kw.keys())))

    def f_traverse(A, B):
        for kid in list(B.keys()):
            if isinstance(B[kid], dict):
                if kid not in A:
                    A[kid] = copy.deepcopy(B[kid])
                elif isinstance(A[kid], dict) and isinstance(B[kid], dict):
                    f_traverse(A[kid], B[kid])
            else:
                if (overwrite and kid in A) or (kid not in A):
                    A[kid] = copy.deepcopy(B[kid])

    f_traverse(A, B)
    return A


def pretty_diff(d, ptrn={}):
    """
    generate "human readable" dictionary output from SortedDict.diff()
    """
    for k in list(d[0].keys()):
        if isinstance(d[0][k][0], dict):
            ptrn[k] = SortedDict()
            pretty_diff(d[0][k], ptrn=ptrn[k])
        else:
            ptrn[k] = d[0][k][0]
    return ptrn


def prune_mask(what, ptrn):
    """
    prune dictionary structure based on mask
    The mask can be in the form of of a `pretty_diff` dictionary or a list of `traverse` strings
    """
    if isinstance(ptrn, dict):
        for k in list(what.keys()):
            if k not in list(ptrn.keys()):
                del what[k]
            elif isinstance(what[k], dict) and isinstance(ptrn[k], dict):
                prune_mask(what[k], ptrn[k])
        return what

    elif isinstance(ptrn, (tuple, list)):

        ptrn = list(ptrn)

        # disregard non-existent paths
        for k, item in list(enumerate(ptrn))[::-1]:
            try:
                eval('what' + item)
            except Exception:
                ptrn.pop(k)

        # expand subtrees
        for item in list(ptrn):
            if isinstance(eval('what' + item), SortedDict):
                ptrn.extend([item + x for x in eval('what' + item).traverse()])

        # expand add parents
        ptrn = set(ptrn)
        for item in list(ptrn):
            rootName = []
            for level in parseLocation(item)[:-1]:
                rootName = rootName + [level]
                ptrn.add(buildLocation(rootName))

        # do the pruning
        for item in what.traverse():
            if item not in ptrn:
                try:
                    exec('del what' + item, globals(), locals())
                except Exception:
                    pass
        return what

    else:
        raise Exception('prune_mask: only list/tuple/dict supported')


def size_tree_objects(location):
    """
    Returns file sizes of objects in the dictionary based on the size of their filename attribute

    :param location: string of the tree location to be analyzed

    :return: dictionary with locations sorted by size
    """
    tmp = traverse(eval(location), onlyDict=False, skipDynaLoad=True)
    sizes = {}
    for item in tmp:
        if hasattr(eval(location + item), 'filename'):
            try:
                obj = eval(location + item)
                if not obj.filename:
                    continue
                size = os.stat(obj.filename).st_size
                if size not in sizes:
                    sizes[size] = []
                sizes[size].append(location + item)
            except Exception as _excp:
                printe('Error sizing object %s : %s' % (location + item, repr(_excp)))
    return sizes


def dynaLoad(f):
    """
    Decorator which calls `dynaLoader` method

    :param f: function to decorate

    :return: decorated function
    """

    @functools.wraps(f)
    def dynamicLoading(self, *args, **kw):
        dynaLoader(self, f)
        return f(self, *args, **kw)

    return dynamicLoading


def dynaLoadKey(f):
    """
    Decorator which calls `dynaLoad` method only if key is not found

    :param f: function to decorate

    :return: decorated function
    """

    @functools.wraps(f)
    def dynamicLoading(self, *args, **kw):
        if args[0] not in self.keyOrder:
            dynaLoader(self, f)
        return f(self, *args, **kw)

    return dynamicLoading


def dynaSave(f):
    """
    Decorator which calls `dynaSaver` method

    :param f: function to decorate

    :return: decorated function
    """

    def doNothing():
        pass

    @functools.wraps(f)
    def dynamicSaving(self, *args, **kw):
        if hasattr_no_dynaLoad(self, 'readOnly') and self.readOnly:
            if hasattr_no_dynaLoad(self, 'modifyOriginal'):
                if self.modifyOriginal and os.path.exists(self.filename) and os.path.samefile(self.link, self.filename):
                    return doNothing
                elif hasattr_no_dynaLoad(self, '_save_by_copy'):
                    return self._save_by_copy(**kw)
        if dynaSaver(self):
            return doNothing
        return f(self, *args, **kw)

    return dynamicSaving


def _docFromDict(f):
    """
    Use the same docstring as for dict

    :param f: function to decorate

    :return: decorated function
    """
    try:
        f.__doc__ = getattr(dict, f.__name__).__doc__
    except AttributeError:
        pass
    return f


def dynaLoader(self, f=None):
    """
    Call `load` function if object has `dynaLoad` attribute set to True
    After calling `load` function the `dynaLoad` attribute is set to False
    """
    if OMFITaux['dynaLoad_switch'] and self.dynaLoad:
        self.dynaLoad = False
        if f is None or f.__name__ != 'load':
            try:
                return self.load()
            except Exception as _excp_load:
                # If an error occurs during loading
                # Clear and reset the dynamic load switch to allow re-tries
                # note: errors could occur because user stops the process
                try:
                    self.clear()
                except Exception as _excp_clear:
                    # if clear() fails, then its exception should be printed but not raised.
                    # the user is interested in the original exception raised by load().
                    printe('The clear() method raised an exception: ' + repr(_excp_clear))
                self.dynaLoad = True
                raise


def dynaSaver(self):
    """
    This function is meant to be called in the .save() function of objects of the class
    `OMFITobject` that support dynamic loading. The idea is that if an object has not
    been loaded, then its file representation has not changed and the original file can be resued.
    This function returns True/False to say if it was successful at saving.
    If True, then the original .save() function can return, otherwise it should go through
    saving the data from memory to file.
    """
    if self.dynaLoad and hasattr_no_dynaLoad(self, 'link') and hasattr_no_dynaLoad(self, 'filename'):
        try:
            printd('Dynamic save: ' + self.filename, level=2, topic='save')
            if os.path.abspath(self.link) != os.path.abspath(self.filename):
                if os.path.exists(self.filename):
                    if filecmp.cmp(self.link, self.filename, shallow=False):
                        self.link = self.filename
                        return True
                    else:
                        os.remove(self.filename)
                try:
                    if OMFITaux.setdefault('hardLinks', False):
                        os.link(self.link, self.filename)
                        printd('Hard link: %s --> %s' % (self.link, self.filename), level=2, topic='save')
                    else:
                        raise Exception('skip')
                except Exception:
                    if os.path.isdir(self.link):
                        shutil.copytree(self.link, self.filename)
                    else:
                        shutil.copy2(self.link, self.filename)
                self.link = self.filename
            return True
        except Exception as _excp:
            printe('Error dynamic save: ' + self.filename + '\n' + repr(_excp))
            return False
    return False


class SortedDict(dict):
    # originally inspired from django/trunk/django/utils/datastructures.py @ 17464
    r"""
    A dictionary that keeps its keys in the order in which they're inserted

    :param data: A dict object or list of (key,value) tuples from which to initialize the new SortedDict object

    :param \**kw: Optional keyword arguments given below

    kw:
        :param caseInsensitive: (bool)  If True, allows self['UPPER'] to yield self['upper'].

        :param sorted: (bool) If True, keep keys sorted alphabetically, instead of by insertion order.

        :param limit: (int) keep only the latest `limit` number of entries (useful for data cashes)

        :param dynaLoad: (bool) Not sure what this does
    """

    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls, *args, **kwargs)
        instance._OMFITkeyName = ''
        instance._OMFITparent = None
        instance.keyOrder = []
        instance.caseInsensitive = kwargs.pop('caseInsensitive', False)
        instance.sorted = kwargs.pop('sorted', False)
        instance.limit = kwargs.pop('limit', 0)
        instance.dynaLoad = False
        return instance

    def __init__(self, data=None, *args, **kwargs):
        self.clear()
        self.caseInsensitive = kwargs.pop('caseInsensitive', False)
        self.sorted = kwargs.pop('sorted', False)
        self.limit = kwargs.pop('limit', 0)
        self.dynaLoad = False

        if data is None:
            data = {}
        elif isinstance(data, types.GeneratorType):
            # Unfortunately we need to be able to read a generator twice.  Once
            # to get the data into self with our super().__init__ call and a
            # second time to setup keyOrder correctly
            data = list(data)

        if isinstance(data, dict):
            for key in list(data.keys()):
                self[key] = data[key]
        else:
            for key, value in data:
                self[key] = value

        if self.sorted:
            self.sort()

        self.dynaLoad = kwargs.pop('dynaLoad', False)

        # keep track of what classes have been loaded
        from omfit_classes.utils_base import _loaded_classes

        _loaded_classes.add(self.__class__.__name__)

    def __getattr__(self, attr):
        if attr.startswith('_OMFIT') or attr.startswith('OMFIT'):
            raise AttributeError('bad attribute `%s`' % attr)
        if (
            OMFITaux['dynaLoad_switch']
            and self.dynaLoad
            and attr not in ['__save_kw__', '__tree_repr__', 'modifyOriginal', 'readOnly']
            and 'getattr_infiniteloop_block' not in self.__dict__
        ):
            try:
                if os.environ['USER'] == 'meneghini':
                    print('%s dynaloading because %s attribute was requested' % (self.__class__.__name__, attr), file=sys.__stderr__)
                    traceback.print_stack(file=sys.__stderr__)
                self.__dict__['getattr_infiniteloop_block'] = True
                dynaLoader(self)
                return getattr(self, attr)
            finally:
                del self.__dict__['getattr_infiniteloop_block']

        raise AttributeError('bad attribute `%s`' % attr)

    def _setLocation(self, key, value):
        if not hasattr(self, '_OMFITparent') or value is not self._OMFITparent:

            # check if the parent is the OMFIT tree
            inOMFITtree = False
            tmp = self
            while tmp != None and hasattr(tmp, '_OMFITparent'):
                if tmp._OMFITparent is None and tmp._OMFITkeyName == 'OMFIT':
                    inOMFITtree = True
                    break
                tmp = tmp._OMFITparent

            if not (key in self and id(self[key]) == id(value)) and inOMFITtree:
                if isinstance_str(value, ['OMFITexpression', 'OMFITiterableExpression']):
                    value = copy.deepcopy(value)

            try:
                value._OMFITkeyName = "[" + repr(key) + "]"
                value._OMFITparent = self
                value._OMFITcopyOf = None  # this copy goes directly into the tree, so we can set it to None
            except (AttributeError, TypeError):
                pass

        return value

    @_docFromDict
    @dynaLoad
    def __len__(self):
        return super().__len__()

    @_docFromDict
    @dynaLoad
    def __hash__(self):
        return ''.join(list(self.keys())).__hash__()

    @_docFromDict
    @dynaLoad
    def __setitem__(self, key, value):
        key, value = self._checkSetitem(key, value)
        if isinstance_str(key, ['OMFITexpression', 'OMFITiterableExpression']):
            raise ValueError('OMFITexpressions are not valid keys for ' + self.__class__.__name__)
        keyL = self._keyCaseInsensitive(key)
        if keyL != key:
            tmp = self.index(keyL)
            del self[keyL]
            self.keyOrder.insert(tmp, key)
        if key not in self.keyOrder:
            if hasattr(self, 'sorted') and self.sorted:
                _insort(self.keyOrder, key)
            else:
                self.keyOrder.append(key)
        elif self.caseInsensitive:
            self.keyOrder[self.index(key)] = key

        super().__setitem__(key, self._setLocation(key, value))

        # make whatever SortedDict is under a caseInsensitive SortedDict, caseInsensitive itself
        if isinstance(self[key], SortedDict) and self.caseInsensitive:
            self[key].caseInsensitive = self.caseInsensitive

        # if limit>0 limit the number of entries
        while self.limit > 0 and len(self.keyOrder) > self.limit:
            delkey = self.keyOrder[0]
            super().__delitem__(delkey)
            self.keyOrder.remove(delkey)

    def _checkSetitem(self, key, value):
        """
        This method is provided so that subclasses can use it to either:
         1) change the key/value tuple as passed to the __setitem__ method
         2) raise an error because the key-value pair is not acceptable

        :param key: key as passed by the user to the __setitem__ method

        :param value: value as passed by the user to the __setitem__ method

        :return: updated (key, value) tuple
        """
        return key, value

    @_docFromDict
    @dynaLoad
    def __delitem__(self, key):
        key = self._keyCaseInsensitive(key)
        super().__delitem__(key)
        self.keyOrder.remove(key)

    # does not need @dynaLoadKey, because functions that call _keyCaseInsensitive already do
    def _keyCaseInsensitive(self, key):
        if not hasattr(self, 'caseInsensitive'):
            self.caseInsensitive = False
        found = key
        if self.caseInsensitive and key not in self.keyOrder and isinstance(key, str):
            for keyL in self.keyOrder:
                if isinstance(keyL, str) and keyL.lower() == key.lower():
                    found = keyL
                    break
        return found

    @_docFromDict
    @dynaLoadKey
    def __getitem__(self, key):
        key = self._keyCaseInsensitive(key)
        try:
            return super().__getitem__(key)
        except KeyError:
            # if this instance has a fetch method, then call it and try it __getitem__ again
            if hasattr(self, 'fetch'):
                self.fetch()
                return super().__getitem__(key)
            else:
                raise

    @_docFromDict
    @dynaLoadKey
    def __contains__(self, key):
        return super().__contains__(self._keyCaseInsensitive(key))

    def __getstate__(self):
        tmp = copy.copy(self.__dict__)
        for k in list(tmp.keys()):
            if k[:6] == '_OMFIT':
                del tmp[k]
        return tmp, list(self.values())

    def __setstate__(self, tmp):
        if isinstance(tmp, dict):
            # old way of loading sortedDict
            self.__dict__ = tmp
            for key in list(self.keys()):
                self[key] = self._setLocation(key, self[key])
        else:
            # new way of loading sortedDict
            self.limit = False
            self.__dict__.update(tmp[0])
            for key, value in zip(self.keyOrder, tmp[1]):
                self[key] = self._setLocation(key, value)

    @dynaLoad
    def index(self, item):
        """
        returns the index of the item
        """
        return self.keyOrder.index(self._keyCaseInsensitive(item))

    @_docFromDict
    @dynaLoad
    def __iter__(self):
        return iter(self.keyOrder)

    @_docFromDict
    @dynaLoad
    def pop(self, key, *args):
        key = self._keyCaseInsensitive(key)
        result = super().pop(key, *args)
        try:
            self.keyOrder.remove(key)
        except ValueError:
            # Key wasn't in the dictionary in the first place. No problem.
            pass
        return result

    @_docFromDict
    @dynaLoad
    def popitem(self):
        result = super().popitem()
        self.keyOrder.remove(result[0])
        return result

    @_docFromDict
    @dynaLoad
    def items(self):
        return list(zip(self.keyOrder, list(self.values())))

    @_docFromDict
    @dynaLoad
    def iteritems(self):
        for key in self.keyOrder:
            yield key, self[key]

    @dynaLoad
    def keys(self, filter=None, matching=False):
        """
        returns the sorted list of keys in the dictionary

        :param filter: regular expression for filtering keys

        :param matching: boolean to indicate whether to return the keys that match (or not)

        :return: list of keys
        """
        if filter is None:
            return self.keyOrder[:]
        elif not matching:
            return [kkk for kkk in self.keyOrder[:] if not re.match(filter, str(kkk))]
        else:
            return [kkk for kkk in self.keyOrder[:] if re.match(filter, str(kkk))]

    @_docFromDict
    @dynaLoad
    def iterkeys(self):
        return iter(self.keyOrder)

    @_docFromDict
    @dynaLoad
    def values(self):
        return list(map(self.__getitem__, self.keyOrder))

    @_docFromDict
    @dynaLoad
    def itervalues(self):
        for key in self.keyOrder:
            yield self[key]

    @_docFromDict
    @dynaLoad
    def update(self, dict_):
        for key, value in list(dict_.items()):
            self[key] = self._setLocation(key, value)

    @dynaLoad
    def recursiveUpdate(self, other, overwrite=False):
        return recursiveUpdate(self, other, overwrite)

    @dynaLoad
    def setdefault(self, key, default):
        """
        The method setdefault() is similar to get(), but will set dict[key]=default if key is not already in dict

        :param key: key to be accessed

        :param default: default value if key does not exist

        :return: value
        """
        if key not in self:
            if hasattr(self, 'sorted') and self.sorted:
                _insort(self.keyOrder, key)
            else:
                self.keyOrder.append(key)
            self[key] = default
        return self[key]

    @_docFromDict
    @dynaLoad
    def get(self, key, default):
        if key not in self:
            return default
        return self[key]

    @dynaLoad
    def value_for_index(self, index):
        """Returns the value of the item at the given zero-based index"""
        return self[self.keyOrder[index]]

    @dynaLoad
    def insert(self, index, key, value):
        """Inserts the key, value pair before the item with the given index"""
        key = self._keyCaseInsensitive(key)
        if key in self.keyOrder:
            n = self.keyOrder.index(key)
            del self.keyOrder[n]
            if n < index:
                index -= 1
        self.keyOrder.insert(index, key)
        self[key] = value

    @dynaLoad
    def copy(self):
        """Returns a copy of this object"""
        obj = self.__class__(self)
        obj.keyOrder = self.keyOrder[:]
        return obj

    @dynaLoad
    def __repr__(self):
        """returns the keys in their sorted order"""
        return '{%s}' % ', '.join(['%r: %r' % (k, v) for k, v in list(self.items())])

    @_docFromDict
    def clear(self):
        super().clear()
        self.keyOrder = []

    @dynaLoad
    def moveUp(self, index):
        """
        Shift up in key list the item at a given index

        :param index: index to be shifted

        :return: None
        """
        if index < len(self.keyOrder):
            self.keyOrder.insert(index + 1, self.keyOrder.pop(index))

    @dynaLoad
    def moveDown(self, index):
        """
        Shift down in key list the item at a given index

        :param index: index to be shifted

        :return: None
        """
        if index > 0:
            self.keyOrder.insert(index - 1, self.keyOrder.pop(index))

    def __repr__(self):
        return self.__class__.__name__ + '(' + str(list(self.items())) + ')'

    @dynaLoad
    def across(self, what='', sort=False, returnKeys=False):
        """
        Aggregate objects across the tree

        :param what: string with the regular expression to be cut across

        :param sort: sorting of results alphabetically

        :param returnKeys: return keys of elements in addition to objects

        :return: list of objects or tuple with with objects and keys

        >> OMFIT['test']=OMFITtree()
        >> for k in range(5):
        >>   OMFIT['test']['aaa'+str(k)]=OMFITtree()
        >>   OMFIT['test']['aaa'+str(k)]['var']=k
        >> OMFIT['test']['bbb'+str(k)]=-1
        >> print(OMFIT['test'].across("['aaa*']['var']"))
        """
        location = parseBuildLocation(what)
        keys = []
        for k in list(self.keys()):
            if isinstance(k, str):
                if re.match('%r' % location[0], '%r' % k):
                    keys.append(k)
            else:
                if re.match('%r' % location[0], '%r' % repr(k)):
                    keys.append(k)
        if len(location) > 1:
            what = parseBuildLocation(location[1:])
        else:
            what = ''

        if sort:
            index = np.argsort(list(map(float, keys)))
        else:
            index = list(range(len(keys)))

        tmp = []
        for k in index:
            tmp_ = self[keys[k]]
            tmp.append(b2s(eval("tmp_" + what)))
            tmp_
        if returnKeys:
            return tmp, [k for k in np.array(keys)[np.array(index, int)]]
        else:
            return tmp

    @dynaLoad
    def sort(self, key=None, **kw):
        r"""
        :param key: function that returns a string that is used for sorting or dictionary key whose content is used for sorting

        >> tmp=SortedDict()
        >> for k in range(5):
        >>     tmp[k]={}
        >>     tmp[k]['a']=4-k
        >> # by dictionary key
        >> tmp.sort(key='a')
        >> # or equivalently
        >> tmp.sort(key=lambda x:tmp[x]['a'])

        :param \**kw: additional keywords passed to the underlying list sort command

        :return: sorted keys
        """
        if key is None:
            self.keyOrder.sort(key=sortHuman, **kw)

        elif not callable(key):
            self.sort(key=lambda x: self[x][key])

        else:
            self.keyOrder.sort(key=key, **kw)

        return self.keyOrder

    def sort_class(self, class_order=[dict]):
        """
        sort items based on their class

        :param class_order: list containing order of class

        :return: sorted keys
        """
        lst = {}
        for k in self.keyOrder:
            oo = len(class_order)
            for o, c in list(enumerate(class_order)):
                if isinstance(self[k], c):
                    oo = o
                    break
            if hasattr(self[k], '__class__'):
                for o, c in list(enumerate(class_order)):
                    if self[k].__class__.__name__ == c.__name__:
                        oo = o
                        break
            lst.setdefault(oo, []).append(k)
        self.keyOrder = []
        for k in range(len(class_order) + 1):
            if k in lst:
                self.keyOrder += lst[k]
        return self.keyOrder

    @dynaLoad
    def diff(
        self,
        other,
        ignoreComments=False,
        ignoreContent=False,
        skipClasses=(),
        noloadClasses=(),
        precision=0.0,
        order=True,
        favor_my_order=False,
        modify_order=False,
        quiet=True,
    ):
        """
        Comparison of a SortedDict

        :param other: other dictionary to compare to

        :param ignoreComments: ignore keys that start and end with "__" (e.g. "__comment__")

        :param ignoreContent: ignore content of the objects

        :param skipClasses: list of class of objects to ignore

        :param noloadClasses: list of class of objects to not load

        :param precision: relative precision to which the comparison is carried out

        :param order: does the order of the keys matter

        :param favor_my_order: favor my order of keys

        :param modify_order: update order of input dictionaries based on diff

        :param quiet: verbosity of the comparison

        :return: comparison dictionary
        """
        # todo: should allow taking differences among any type of dictionary, not only sorted dict

        # sorted join of self.keys() with other.keys()
        keys = sorted_join_lists(self.keys(), other.keys(), favor_my_order, self.caseInsensitive or other.caseInsensitive)

        # update order of input dictionaries based on diff
        if modify_order:
            self.keyOrder = [k for k in keys if k in self.keys()]
            other.keyOrder = [k for k in keys if k in other.keys()]

        if ignoreComments:
            keys = [key for key in keys if not re.match(comment_ptrn, str(key))]

        ndiffs = 0.0
        switch = SortedDict()
        for key in keys:
            if not quiet:
                printi('Compare: ' + str(key))

            if key not in self:
                switch[key] = ['added', False]
                ndiffs += 1.0

            elif key not in other:
                switch[key] = ['removed', False]
                ndiffs += 1.0

            else:
                if isinstance(self[key], skipClasses) or isinstance(other[key], skipClasses):
                    continue

                if isinstance(self[key], noloadClasses) or isinstance(other[key], noloadClasses):
                    if (
                        isinstance(self[key], SortedDict)
                        and isinstance(other[key], SortedDict)
                        and (self[key].dynaLoad or other[key].dynaLoad)
                    ):
                        switch[key] = ['noLoad', False]
                        continue

                if isinstance(self[key], SortedDict) and isinstance(other[key], SortedDict):  # any changes in the subdirs, even order
                    tmp = self[key].diff(
                        other[key],
                        ignoreComments=ignoreComments,
                        ignoreContent=ignoreContent,
                        skipClasses=skipClasses,
                        noloadClasses=noloadClasses,
                        precision=precision,
                        order=order,
                        favor_my_order=favor_my_order,
                        modify_order=modify_order,
                        quiet=quiet,
                    )
                    if np.sum([len(tmp[0][k]) for k in tmp[0]]) or (
                        order and len([v for k, v in enumerate(self[key]) if list(other[key].keys())[k] != v])
                    ):
                        switch[key] = tmp
                        ndiffs += 1.0

                elif not ignoreContent and different(self[key], other[key], precision=precision):
                    switch[key] = ['changed', False]
                    ndiffs += 1.0

        return [switch, False, keys]

    @dynaLoad
    def pretty_diff(
        self,
        other,
        ignoreComments=False,
        ignoreContent=False,
        skipClasses=(),
        noloadClasses=(),
        precision=0.0,
        order=True,
        favor_my_order=False,
        quiet=True,
    ):
        """
        Comparison of a SortedDict in human readable format

        :param other: other dictionary to compare to

        :param ignoreComments: ignore keys that start and end with "__" (e.g. "__comment__")

        :param ignoreContent: ignore content of the objects

        :param skipClasses: list of class of objects to ignore

        :param noloadClasses: list of class of objects to not load

        :param precision: relative precision to which the comparison is carried out

        :param order: does the order of the keys matter

        :param favor_my_order: favor my order of keys

        :param quiet: verbosity of the comparison

        :return: comparison dictionary in pretty to print format
        """
        tmp = self.diff(
            other,
            ignoreComments=ignoreComments,
            ignoreContent=ignoreContent,
            skipClasses=skipClasses,
            noloadClasses=noloadClasses,
            precision=precision,
            order=order,
            favor_my_order=favor_my_order,
            quiet=quiet,
        )
        return pretty_diff(tmp)

    @dynaLoad
    def diffKeys(self, other):
        """
        :param other: other dictionary to compare to

        :return: floating point to indicate the ratio of keys that are similar
        """
        # notice that selfKeys and otherKeys are generated with traverse() and do not include comment_ptrn_in_brackets
        selfKeys = set(
            [
                key.lower().split('(')[0]
                for key in traverse(self)
                if isinstance(key, str) and not re.match(comment_ptrn_in_brackets, str(key))
            ]
        )
        otherKeys = set(
            [
                key.lower().split('(')[0]
                for key in traverse(other)
                if isinstance(key, str) and not re.match(comment_ptrn_in_brackets, str(key))
            ]
        )
        if len(selfKeys) < len(otherKeys):
            keys = selfKeys
        else:
            keys = otherKeys

        if len(keys) < 2:
            return 0.0

        ndiffs = 0.0
        for key in keys:
            if len(selfKeys) < len(otherKeys) and key not in otherKeys:
                ndiffs += 1.0
            elif len(selfKeys) >= len(otherKeys) and key not in selfKeys:
                ndiffs += 1.0

        lk = len(keys) * 1.0
        lE = lk - ndiffs
        if lk > 0:
            score = lE * 1.0 / lk
        else:
            score = 1.0
        return score

    @dynaLoad
    def changeKeysCase(self, case=None, recursive=False):
        """
        Change all the keys in the dictionary to be upper/lower case

        :param case: 'upper' or 'lower'

        :param recursive: apply this recursively

        :return: None
        """
        if case is None:
            return
        elif case == 'upper' or case == 'lower':
            for kid in list(self.keys()):
                tmp = self.pop(kid)
                if case == 'upper':
                    self[kid.upper()] = tmp
                elif case == 'lower':
                    self[kid.lower()] = tmp
            for kid in list(self.keys()):
                if recursive and isinstance(self[kid], SortedDict):
                    self[kid].changeKeysCase(case, recursive=True)

    @dynaLoad
    def traverse(self, string='', level=100, onlyDict=False, onlyLeaf=False, skipDynaLoad=False):
        """
        Equivalent to the `tree` command in UNIX

        :param string: prepend this string

        :param level: depth

        :param onlyDict: only subtrees and not the leafs

        :return: list of strings containing the dictionary path to each object
        """
        return traverse(self, string, level, split=True, onlyDict=onlyDict, onlyLeaf=onlyLeaf, skipDynaLoad=skipDynaLoad)

    @dynaLoad
    def walk(self, function, **kw):
        r"""
        Walk every member and call a function on the keyword and value

        :param function: `function(self,kid,**kw)`

        :param \**kw: kw passed to the function

        :return: self
        """
        for kid in list(self.keys()):
            if hasattr(self[kid], 'walk'):
                self[kid].walk(function, **kw)
            else:
                self[kid] = function(self, kid, **kw)
        return self

    @dynaLoad
    def safe_del(self, key):
        """
        Delete key entry only if it is present

        :param key: key to be deleted
        """
        if key in self:
            del self[key]

    @dynaLoad
    def flatten(self):
        """
        The hierarchical structure of the dictionaries is flattened

        :return: SortedDict populated with the flattened content of the dictionary
        """
        tmp = SortedDict(caseInsensitive=self.caseInsensitive)
        for item in list(self.keys()):
            if isinstance(self[item], SortedDict):
                tmp.update(self[item].flatten())
            else:
                tmp[item] = self[item]
        return tmp

    @dynaLoad
    def setFlat(self, key, value):
        """
        recursively searches dictionary for key in order to set a value
        raises KeyError if key could not be found, so this method cannot
        be used to set new entries in the dictionary

        :param key: key to be set

        :param value: value to set
        """
        if key in self:
            self[key] = value
            return
        else:
            for item in list(self.keys()):
                if isinstance(self[item], SortedDict):
                    try:
                        self[item].setFlat(key, value)
                        return
                    except KeyError:
                        pass
        raise KeyError('`%s` could not be found throughout the dictionary' % key)

    @dynaLoad
    def check_location(self, location, value=_special1):
        """
        check if location exist and equals value (if value is specified)

        :param location: location as string

        :param value: value for which to return equal

        :return: True/False

        >> root['SETTINGS'].check_location("['EXPERIMENT']['shot']", 133221)
        """
        try:
            eval('self' + location)
        except KeyError:
            return False
        if value is not _special1 and evalExpr(eval('self' + location)) != evalExpr(value):
            return False
        return True

    def __popup_menu__(self):
        """
        Dummy method to avoid dynamic loading for classes that do not override it

        :return: empty list
        """
        return []

    def todict(self):
        """
        Return a standard Python dictionary representation of the SortedDict

        :return: dictionary
        """
        flat = self.traverse()
        tmp = {}
        for item in flat:
            value = eval(f'self{item}')
            d, b = dirbaseLocation('tmp' + item)
            if isinstance(value, dict):
                eval(d)[b] = {}
            else:
                eval(d)[b] = value
        return tmp


class OMFITdataset(object):
    """
    Subclassing from this class is like subclassing from the xarray.Dataset class
    but without having to deal with the hassle of inheriting from xarrays
    (internally this class uses class composition rather than subclassing).

    Also this class makes it possible to use the OMFIT dynamic loading capabilities.
    All classes that subclass OMFITdataset must define the `.dynaLoad` attribute.

    NOTE: Classes that subclass from OMFITdataset will be identified
    as an xarray.Dataset when using isinstance(..., xarray.Dataset)
    within OMFIT
    """

    def __init__(self, data_vars=None, coords=None, attrs=None):
        r"""
        :param data_vars: see xarray.Dataset

        :param coords: see xarray.Dataset

        :param attrs: see xarray.Dataset
        """
        if self.__class__ == OMFITdataset:
            raise Exception('OMFITdataset is a class that can only be used as a subclass')
        if not hasattr(self, 'dynaLoad'):
            raise Exception(self.__class__.__name__ + ' must set .dynaLoad before calling OMFITdataset.__init__')
        with warnings.catch_warnings(record=True) as w:
            warnings.filterwarnings('ignore', category=DeprecationWarning)
            warnings.filterwarnings('ignore', category=FutureWarning)
            from xarray import Dataset
        self._dataset = Dataset(data_vars=data_vars, coords=coords, attrs=attrs)

    def __getattr__(self, attr):
        # doing this callable test first gets pickling and unpickling to work
        # it used to get stuck in a recursive loop on "dynaLoad" and just testing for attr=='dynaLoad' did not help
        if attr == '__deepcopy__':
            raise AttributeError('Raise not implemented so that we do not use the ._dataset method')
        with warnings.catch_warnings(record=True) as w:
            warnings.filterwarnings('ignore', category=DeprecationWarning)
            warnings.filterwarnings('ignore', category=FutureWarning)
            from xarray import Dataset
        is_callable = callable(getattr(Dataset, attr))
        if self.dynaLoad and (not attr.startswith('_') or attr in ['__getitem__', '__setitem__']):
            self.load()
            self.dynaLoad = False
        return getattr(self._dataset, attr)

    @dynaLoad
    def to_dataset(self):
        """
        Return an xarray.Dataset representation of the data

        :return: xarray.Dataset
        """
        with warnings.catch_warnings(record=True) as w:
            warnings.filterwarnings('ignore', category=DeprecationWarning)
            warnings.filterwarnings('ignore', category=FutureWarning)
            from xarray import Dataset
        return Dataset(self._dataset.data_vars, attrs=self._dataset.attrs)

    @dynaLoad
    def from_dataset(self, dataset):
        """
        Create from xarray.Dataset representation of the data

        """
        with warnings.catch_warnings(record=True) as w:
            warnings.filterwarnings('ignore', category=DeprecationWarning)
            warnings.filterwarnings('ignore', category=FutureWarning)
            from xarray import Dataset

        if isinstance(datatset, Dataset):
            self._dataset = dataset
        else:
            printw("Input is not a proper xarray.Dataset!")

    @dynaLoad
    def __getitem__(self, key):
        # getitem is necessary so that the object is subscriptable
        return self._dataset.__getitem__(key)

    @dynaLoad
    def __setitem__(self, key, value):
        # setitem is necessary so that the object is assignable
        return self._dataset.__setitem__(key, value)

    @dynaLoad
    def __len__(self):
        # len is necessary so that the object is iterable
        return self._dataset.__len__()

    @dynaLoad
    def __iter__(self):
        # iter is necessary so that the object is iterable
        return self._dataset.__iter__()

    @dynaLoad
    def __contains__(self, b):
        # contains is necessary so that the object is iterable
        return self._dataset.__contains__(b)

    def __delitem__(self, b):
        # delete from data set
        del self._dataset[b]


# automatic handle removing of _OMFITxxx attributes when pickling
_dumps = pickle.dumps


@functools.wraps(_dumps)
def _OMFITdumps(x, *args, **kw):
    dynaLoadBkp = OMFITaux['dynaLoad_switch']
    OMFITaux['dynaLoad_switch'] = False
    saveIt = {}
    try:
        if hasattr(x, '__dict__'):
            for k in list(x.__dict__.keys()):
                if k[:6] == '_OMFIT':
                    saveIt[k] = x.__dict__[k]
                    del x.__dict__[k]
        return _dumps(x, *args, **kw)
    finally:
        for k in list(saveIt.keys()):
            x.__dict__[k] = saveIt[k]
        OMFITaux['dynaLoad_switch'] = dynaLoadBkp


pickle.dumps = _OMFITdumps

_dump = pickle.dump


@functools.wraps(_dump)
def _OMFITdump(x, *args, **kw):
    dynaLoadBkp = OMFITaux['dynaLoad_switch']
    OMFITaux['dynaLoad_switch'] = False
    saveIt = {}
    try:
        if hasattr(x, '__dict__'):
            for k in list(x.__dict__.keys()):
                if k[:6] == '_OMFIT':
                    saveIt[k] = x.__dict__[k]
                    del x.__dict__[k]
        return _dump(x, *args, **kw)
    finally:
        for k in list(saveIt.keys()):
            x.__dict__[k] = saveIt[k]
        OMFITaux['dynaLoad_switch'] = dynaLoadBkp


pickle.dump = _OMFITdump

_load = pickle.load


@functools.wraps(_load)
def _OMFITload(*args, **kw):
    dynaLoadBkp = OMFITaux['dynaLoad_switch']
    OMFITaux['dynaLoad_switch'] = False
    try:
        kw.setdefault('encoding', 'latin1')
        return _load(*args, **kw)
    finally:
        OMFITaux['dynaLoad_switch'] = dynaLoadBkp


pickle.load = _OMFITload

_loads = pickle.loads


@functools.wraps(_loads)
def _OMFITloads(*args, **kw):
    dynaLoadBkp = OMFITaux['dynaLoad_switch']
    OMFITaux['dynaLoad_switch'] = False
    try:
        kw.setdefault('encoding', 'latin1')
        return _loads(*args, **kw)
    finally:
        OMFITaux['dynaLoad_switch'] = dynaLoadBkp


pickle.loads = _OMFITloads

if __name__ == "__main__":
    aa = SortedDict({'foo': 1, 'bar': 2, 'yo': 4})
    a = SortedDict({'foo': 1, 'bar': 2, 'yo': 4, 'dd': aa})
    bb = SortedDict({'foo': 0, 'foobar': 3, 'yo': 4})
    b = SortedDict({'foo': 0, 'foobar': 3, 'yo': 4, 'dd': bb})
    diff, switch, keys = a.diff(b)
    print(diff)
