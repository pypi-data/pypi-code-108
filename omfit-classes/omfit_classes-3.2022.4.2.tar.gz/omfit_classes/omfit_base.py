try:
    # framework is running
    from .startup_choice import *
except ImportError as _excp:
    # class is imported by itself
    if (
        'attempted relative import with no known parent package' in str(_excp)
        or 'No module named \'omfit_classes\'' in str(_excp)
        or "No module named '__main__.startup_choice'" in str(_excp)
    ):
        from startup_choice import *
    else:
        raise

from omfit_classes.omfit_namelist import OMFITnamelist
from omfit_classes.omfit_weblink import OMFITwebLink
from omfit_classes.omfit_ascii import OMFITascii
from omfit_classes.omfit_json import OMFITsettings, SettingsName
from omfit_classes.omfit_error import OMFITexpressionError, OMFITerror, OMFITobjectError
from omfit_classes.omfit_harvest import harvest_send
from omfit_classes import utils_base

from omfit_classes import namelist
import zipfile
import traceback
import numpy as np
import xarray
import pandas
import errno
import os as _os

__all__ = [
    'OMFITtree',
    'OMFITlist',
    'module_selective_deepcopy',
    'module_noscratch_deepcopy',
    'OMFITcollection',
    'OMFITmcTree',
    'OMFITstorage',
    'OMFITtreeCompressed',
    'OMFITmodule',
    'OMFITtmp',
    'OMFITproject',
    'OMFIThelp',
    '_OMFITnoSave',
    'OMFITexpressionsReturnNone',
    'OMFITexpression',
    'OMFITiterableExpression',
    'OMFITlazyLoad',
    'relativeLocations',
    'absLocation',
    'isinstance',
    'type',
    'hasattr',
    'shotBookmarks',
    'OMFITshotBookmarks',
    'OMFITmainSettings',
    'OMFITtypes',
    'OMFITtypesStr',
    'OMFITdictypes',
    'OMFITdictypesStr',
    'omfit_log',
    'ismodule',
    'diffTreeGUI',
    'exportTreeGUI',
    'diffViewer',
    'askDescription',
    'all_pylab_imports',
    'evalExpr',
]

# Adding `from pylab import *` to OMFIT scripts namespace to simplify users life. This makes OMFIT behave a-la matlab.
# NOTE: `from pylab import *` will override `__builtin__.all`, `__builtin__.any`, `__builtin__.sum`  but not `__builtin__.max` and `__builtin__.min`
# For backward compatibility with the do some subsequent import statements that reproduce how the OMFIT externalImports was done in the past
all_pylab_imports = {}
exec('from pylab import *', all_pylab_imports)
exec('import copy', all_pylab_imports)
exec('from matplotlib import pyplot as plt', all_pylab_imports)

# ---------------------
# OMFIT dynamic expressions
# ---------------------
class OMFITunevaluatedExpression:
    pass


class OMFITexpression:
    """This class handles so called OMFIT `dynamic expressions`.

    If you generate dynamic expressions in a Python script, note that the relative location of the expression
    (root,parent,DEPENDENCIES,...) is evaluated with respect to where the expression is in the tree,
    not relative to where the script which generated the expression resides

    If you are using relative locations in your expression, things may not work if you have the same expression into
    two locations in the tree. A classic of this happening is if you do a memory copy of something (e.g. namelist) containing
    an expression to some other location in the tree. If this happens the results are unpredictable.

    :param expression: string containing python code to be dynamically evaluated every time an attribute of this object is accessed
    """

    def __init__(self, expression):
        if not isinstance(expression, str):
            raise OMFITexception('OMFITexpression argument can only be a string')
        self.expression = expression
        self.lastEval = OMFITunevaluatedExpression()
        try:
            self._value_()
        except Exception as _excp:
            self.lastEval = OMFITexpressionError(self.expression)

    def __getattr__(self, attr):
        if attr == '__getinitargs__':
            raise AttributeError('bad attribute `%s`' % attr)
        elif attr in ['_OMFITcopyOf', '_OMFITparent', '_OMFITkeyName']:
            raise AttributeError('OMFITexpressions must be contained in SortedDict dictionaries')
        return getattr(self._value_(), attr)

    def __coerce__(self, other):
        # Unfortunately obsolete and no longer supported for Python3.x
        # Because of this the built-in type methods (eg. __add__, __radd__, ...)
        # need to be explicitly specified in the OMFITexpression class
        return self._value_(), other

    # ==================
    # We must explicitly implement methods that are always defined for classes in Python3.x
    # https://docs.python.org/3.7/library/operator.html
    # Use of explicit operators (eg. +, rather than __add__) is due to the fact that some objects
    # (like strings) are handled in somewhat special ways
    # ==================
    def bool(self):
        if self._value_():
            return True
        return False

    def __bool__(self):
        if self._value_():
            return True
        return False

    def __nonzero__(self):
        return bool(self._value_())

    def real(self):
        return self._value_().real()

    def imag(self):
        return self._value_().imag()

    def lt(self, b):
        return self._value_() < b

    def le(self, b):
        return self._value_() <= b

    def eq(self, b):
        return self._value_() == b

    def ne(self, b):
        return self._value_() != b

    def ge(self, b):
        return self._value_() >= b

    def gt(self, b):
        return self._value_() > b

    def __lt__(self, b):
        return self._value_() < b

    def __le__(self, b):
        return self._value_() <= b

    def __eq__(self, b):
        return self._value_() == b

    def __ne__(self, b):
        return self._value_() != b

    def __ge__(self, b):
        return self._value_() >= b

    def __gt__(self, b):
        return self._value_() > b

    # ==================
    def not_(self):
        return not self._value_()

    def __not__(self):
        return not self._value_()

    def truth(self):
        return self._value_().truth()

    def is_(self, b):
        return self._value_() is b

    def is_not(self, b):
        return self._value_() is not b

    def abs(self):
        return abs(self._value_())

    def __abs__(self):
        return abs(self._value_())

    def add(self, b):
        return self._value_() + b

    def __add__(self, b):
        return self._value_() + b

    def __radd__(self, b):
        return b + self._value_()

    def and_(self, b):
        return self._value_() & b

    def __and__(self, b):
        return self._value_() & b

    def __rand__(self, b):
        return b & self._value_()

    def floordiv(self, b):
        return self._value_() // b

    def __floordiv__(self, b):
        return self._value_() // b

    def __rfloordiv__(self, b):
        return self._value_().__rfloordiv__(b)

    def index(self):
        return self._value_().index()

    def __index__(self):
        return self._value_().__index__()

    def inv(self):
        return self._value_().inv()

    def invert(self):
        return self._value_().invert()

    def __inv__(self):
        return self._value_().__inv__()

    def __invert__(self):
        return self._value_().__invert__()

    def lshift(self, b):
        return self._value_().lshift(b)

    def __lshift__(self, b):
        return self._value_().__lshift__(b)

    def __rlshift__(self, b):
        return self._value_().__rlshift__(b)

    def mod(self, b):
        return self._value_() % b

    def __mod__(self, b):
        return self._value_() % b

    def __rmod__(self, b):
        return self._value_().__rmod__(b)

    def mul(self, b):
        return self._value_() * b

    def __mul__(self, b):
        return self._value_() * b

    def __rmul__(self, b):
        return b * self._value_()

    def matmul(self, b):
        return self._value_().matmul(b)

    def __matmul__(self, b):
        return self._value_().__matmul__(b)

    def neg(self):
        return -self._value_()

    def __neg__(self):
        return -self._value_()

    def or_(self, b):
        return self._value_() | b

    def __or__(self, b):
        return self._value_() | b

    def __ror__(self, b):
        return self._value_() | b

    def pos(self):
        return +self._value_()

    def __pos__(self):
        return +self._value_()

    def pow(self, b):
        return self._value_().pow(b)

    def __pow__(self, b):
        return self._value_().__pow__(b)

    def __rpow__(self, b):
        return self._value_().__rpow__(b)

    def rshift(self, b):
        return self._value_().rshift(b)

    def __rshift__(self, b):
        return self._value_().__rshift__(b)

    def __rrshift__(self, b):
        return self._value_().__rrshift__(b)

    def sub(self, b):
        return self._value_() - b

    def __sub__(self, b):
        return self._value_() - b

    def __rsub__(self, b):
        return b - self._value_()
        # return self._value_().__rsub__(b) # Try to revert if https://github.com/gafusion/OMFIT-source/issues/4163 gets fixed

    def truediv(self, b):
        return self._value_() / b

    def __truediv__(self, b):
        return self._value_() / b

    def __rtruediv__(self, b):
        return self._value_().__rtruediv__(b)

    def __divmod__(self, b):
        return self._value_().__divmod__(b)

    def __rdivmod__(self, b):
        return self._value_().__rdivmod__(b)

    def xor(self, b):
        return self._value_() ^ b

    def __xor__(self, b):
        return self._value_() ^ b

    def __rxor__(self, b):
        return self._value_().__rxor__(b)

    # ==================
    @property
    def __dict__(self):
        return self._value_().__dict__

    def __dir__(self):
        return dir(self._value_())

    def __eq__(self, other):
        return self._value_() == other

    def __format__(self, *args, **kw):
        return self._value_().__format__(*args, **kw)

    def __ge__(self, other):
        return self._value_() >= other

    def __gt__(self, other):
        return self._value_() > other

    def __hash__(self, *args, **kw):
        return self._value_().__hash__(*args, **kw)

    #    def __init_subclass__(self, *args, **kw):
    #        return self._value_().__init_subclass__(*args, **kw)

    def __le__(self, other):
        return self._value_() <= other

    def __lt__(self, other):
        return self._value_() < other

    def __ne__(self, other):
        return self._value_() != other

    def __repr__(self):
        return repr(self._value_())

    def __sizeof__(self):
        return sizeof(self._value_())

    def __str__(self):
        return str(self._value_())

    def __unicode__(self):
        return str(self._value_())

    def __int__(self):
        return int(self._value_())

    def __float__(self):
        return float(self._value_())

    def __complex__(self):
        return complex(self._value_())

    def __oct__(self):
        return oct(self._value_())

    def __hex__(self):
        return hex(self._value_())

    def __trunc__(self):
        import math

        return math.trunc(self._value_())

    # =====================

    def __deepcopy__(self, memo):
        return self.__class__(self.expression)

    def __getstate__(self):
        return {'expression': self.expression}

    def __setstate__(self, dict):
        self.__init__(dict['expression'])

    def _value_(self, executed_expr_ids=[]):
        global OMFITexpressionsReturnNone
        if OMFITexpressionsReturnNone:
            return None

        # first try to get an answer without evaluating any relativelocations at all
        self.lastEval = self._godeep(self.__value__(dependencies=None), executed_expr_ids=executed_expr_ids)

        # then try to get an answer with the relative locations but no dependencies
        if isinstance(self.lastEval, OMFITexpressionError):
            self.lastEval = self._godeep(self.__value__(dependencies=False), executed_expr_ids=executed_expr_ids)

            # finally try evaluating the module dependencies
            if isinstance(self.lastEval, OMFITexpressionError):
                self.lastEval = self._godeep(self.__value__(dependencies=True), executed_expr_ids=executed_expr_ids)

        if isinstance(self.lastEval, OMFITexpressionError):
            self.__class__ = OMFITiterableExpression
        elif isinstance(self.lastEval, OMFITexpression):
            self.__class__ = self.lastEval.__class__
        else:
            try:
                iter(self.lastEval)
                self.__class__ = OMFITiterableExpression
            except TypeError:
                self.__class__ = OMFITexpression
        return self.lastEval

    def _godeep(self, val, executed_expr_ids=[]):
        # __godeep__ has to use _value_() to resolve layered expressions
        if id(val) in executed_expr_ids:
            errmsg = 'Error! OMFITexpression recursion loop detected!'
            printe(errmsg)
            return OMFITerror(errmsg)
        elif isinstance(val, OMFITexpression):
            return val._value_(executed_expr_ids=executed_expr_ids + [id(val)])
        else:
            return val

    def __value__(self, dependencies):
        locals = {}
        locals.update(all_pylab_imports)
        locals.update(relativeLocations(self, dependencies=dependencies))

        try:
            tmp = eval(self.expression, globals(), locals)

        except Exception:
            try:
                locals['testExpr'] = False
                exec(self.expression, globals(), locals)
                tmp = locals.get('return_variable', None)
            except Exception as _excp:
                printd('OMFITexpressionError: %s' % _excp)
                return OMFITexpressionError(repr(_excp))
        return tmp


class OMFITiterableExpression(OMFITexpression):
    """
    Subclass of OMFITexpression used for iterable objects
    The distinction between iterable and not iterable expressions
    is used in case someone tests for iterability of an object
    """

    # ==================
    def __len__(self):
        return self._value_().__len__()

    def concat(self, b):
        return self._value_().concat(b)

    def __concat__(self, b):
        return self._value_().__concat__(b)

    def contains(self, b):
        return self._value_().contains(b)

    def __contains__(self, b):
        return self._value_().__contains__(b)

    def countOf(self, b):
        return self._value_().countOf(b)

    def delitem(self, b):
        return self._value_().delitem(b)

    def __delitem__(self, b):
        return self._value_().__delitem__(b)

    def getitem(self, b):
        return self._value_().getitem(b)

    def __getitem__(self, b):
        return self._value_().__getitem__(b)

    def indexOf(self, b):
        return self._value_().indexOf(b)

    def setitem(self, b, c):
        return self._value_().setitem(b, c)

    def __setitem__(self, b, c):
        return self._value_().__setitem__(b, c)

    def length_hint(self, default=0):
        return self._value_().length_hint(default)

    def attrgetter(self, *attrs):
        return self._value_().attrgetter(*attrs)

    def itemgetter(self, *items):
        return self._value_().itemgetter(*items)

    def methodcaller(self, name, *args):
        return self._value_().methodcaller(name, *args)


def relativeLocations(location, dependencies=True):
    """
    This function provides a dictionary references to some useful quantities with respect to the object specified in `location`.
    Note that the variables in the returned dictionary are the same ones that are available within the namespace of OMFIT scripts and expressions.

    :param location: location in the OMFIT tree

    :return: dictionary containing the following variables:

    * OMFITlocation : list of references to the tree items that compose the OMFIT-tree path

    * OMFITlocationName : list of path strings to the tree items that compose the OMFIT-tree path

    * parent : reference to the parent object

    * parentName : path string to the parent object

    * this : reference to the current object

    * thisName : path string to the current object

    * OMFITmodules : list of modules to the current module

    * OMFITmodulesName : list of string paths to the current module

    * MainSettings : reference to OMFIT['MainSettings']

    * MainScratch: reference to OMFIT['scratch']

    * scratch : reference to module scratch

    * scratchName : string path to module scratch

    * root : reference to this module

    * rootName : string path to this module

    * DEPENDENCIES variables defined within the module
    """
    locations = {}

    # global locations (some will be overwritten if treeLocation(location) is not None)
    locations['OMFIT'] = OMFIT
    locations['rootName'] = 'OMFIT'
    locations['root'] = OMFIT
    locations['MainSettings'] = OMFIT['MainSettings']
    locations['scratchName'] = "OMFIT['scratch']"
    locations['MainScratch'] = locations['scratch'] = OMFIT['scratch']
    locations['this'] = location
    locations['parent'] = getattr(location, '_OMFITparent', None)

    # location of this entry in the OMFIT tree
    OMFITlocationName = treeLocation(location)
    locations['OMFITlocationName'] = OMFITlocationName
    if OMFITlocationName:
        # if an entry is in the OMFIT tree
        if len(OMFITlocationName[0]):
            locations['OMFITlocation'] = []
            for item in copy.deepcopy(OMFITlocationName):
                try:
                    locations['OMFITlocation'].append(eval(item))
                except Exception:
                    OMFITlocationName.remove(item)
        # if an entry is not in the OMFIT tree at least we can try to set root
        # by navigating upstream and seing if there is a module above it
        else:
            h = location
            if builtins.isinstance(h, OMFITmodule):
                locations['root'] = h
                locations['rootName'] = '?'
                if '__scratch__' not in h:
                    h['__scratch__'] = OMFITtmp()
                locations['scratch'] = h['__scratch__']
                locations['scratchName'] = '?'
            else:
                for item in parseLocation(OMFITlocationName[-1]):
                    if getattr(h, '_OMFITparent', None):
                        h = h._OMFITparent
                    if builtins.isinstance(h, OMFITmodule):
                        locations['root'] = h
                        locations['rootName'] = '?'
                        if '__scratch__' not in h:
                            h['__scratch__'] = OMFITtmp()
                        locations['scratch'] = h['__scratch__']
                        locations['scratchName'] = '?'

    if OMFITlocationName and len(OMFITlocationName[0]):
        locations['OMFITmodulesName'] = [OMFITlocationName[0]]
        for tmpName in OMFITlocationName[1:]:
            if eval(tmpName).__class__ is OMFITmodule or eval(tmpName).__class__ is OMFITproject:
                locations['OMFITmodulesName'].append(tmpName)
        rootName = locations['OMFITmodulesName'][-1]

        locations['OMFITmodules'] = []
        for item in locations['OMFITmodulesName']:
            locations['OMFITmodules'].append(eval(item))
        root = locations['OMFITmodules'][-1]

        locations['rootName'] = rootName
        locations['root'] = root

        locations['thisName'] = OMFITlocationName[-1]
        locations['this'] = eval(locations['thisName'])

        if len(OMFITlocationName) > 1:
            locations['parentName'] = OMFITlocationName[-2]
            locations['parent'] = eval(locations['parentName'])

        if root is OMFIT:
            locations['MainScratchName'] = "OMFIT['scratch']"
        else:
            if '__scratch__' not in root:
                root['__scratch__'] = OMFITtmp()
            locations['scratchName'] = rootName + "['__scratch__']"
            locations['scratch'] = eval(locations['scratchName'])

        if not dependencies:
            return locations

        if root.__class__ is OMFITmodule and 'SETTINGS' in root and 'DEPENDENCIES' in root['SETTINGS']:
            for dep in list(root['SETTINGS']['DEPENDENCIES'].keys()):
                if root['SETTINGS']['DEPENDENCIES'][dep] is None:
                    locations[dep] = None

                else:
                    try:
                        pathExists = True
                        error = ''

                        if root['SETTINGS']['DEPENDENCIES'][dep].__class__ not in [OMFITexpression, OMFITiterableExpression] and isinstance(
                            root['SETTINGS']['DEPENDENCIES'][dep], str
                        ):
                            locdep = str(root['SETTINGS']['DEPENDENCIES'][dep])
                        else:
                            tmp = str(root['SETTINGS']['DEPENDENCIES'][dep].expression)
                            retvar = {'return_variable': None}
                            tmpNamespace = {}
                            tmpNamespace.update(globals())
                            tmpNamespace.update(locations)
                            try:
                                retvar['return_variable'] = eval(tmp, tmpNamespace)
                            except Exception as _excp:
                                try:
                                    exec(tmp, tmpNamespace, retvar)
                                except Exception as _excp:
                                    printd(
                                        'Broken dynamic expression dependency '
                                        + rootName
                                        + "['SETTINGS']['DEPENDENCIES']['"
                                        + dep
                                        + "'] referred from "
                                        + OMFITlocationName[-1]
                                        + '\n'
                                        + _excp,
                                        level=3,
                                        topic='dependencies',
                                    )
                                    locations[dep] = None
                                    continue
                            locdep = retvar['return_variable']

                        whereFrom = re.sub(r'(^\w*)(\[.*\]$)', r'\1', locdep)
                        path = ''
                        if '[' in locdep:
                            path = re.sub(r'(^\w*)(\[.*\]$)', r'\2', locdep)

                        if whereFrom == 'scratch':
                            locdep = locations['scratchName'] + path
                        elif whereFrom == 'MainSettings':
                            locdep = "OMFIT['MainSettings']" + path
                        elif whereFrom == 'this':
                            locdep = locations['thisName'] + path
                        elif whereFrom == 'parent':
                            locdep = locations['parentName'] + path
                        elif whereFrom == 'root':
                            locdep = locations['rootName'] + path
                        elif whereFrom == 'OMFITlocation':
                            # notice that OMFITlocation is relative to the script/expression calling, not to the location of ['DEPENDENCIES'] of a module
                            locdep = locations['OMFITlocationName'][parseBuildLocation(path)[0]] + parseBuildLocation(
                                parseBuildLocation(path)[1:]
                            )
                        elif whereFrom == 'OMFITmodules':
                            locdep = locations['OMFITmodulesName'][parseBuildLocation(path)[0]] + parseBuildLocation(
                                parseBuildLocation(path)[1:]
                            )
                        else:
                            locdep = 'OMFIT' + path

                        tmp = OMFIT
                        for key in parseBuildLocation(locdep):
                            if key in tmp:
                                tmp = tmp[key]
                            else:
                                pathExists = False
                                break

                        if pathExists:
                            # the purppose of this evaluate if just to raise an exception if the evaluation fails
                            eval(locdep)

                    # this is to catch errors which are not associated with path not existing
                    except Exception as _excp:
                        pathExists = False
                        error = ': ' + repr(_excp)

                    if pathExists:
                        locations[dep] = eval(locdep)
                    else:
                        locations[dep] = None
                        printd(
                            'Broken dependency '
                            + rootName
                            + "['SETTINGS']['DEPENDENCIES']['"
                            + dep
                            + "'] referred from "
                            + OMFITlocationName[-1]
                            + '\n'
                            + error,
                            level=3,
                            topic='dependencies',
                        )

    return locations


def absLocation(location, base, base_is_relativeLocations_output=False):
    """
    This method translates relative location strings to absolute location strings in the OMFIT tree

    :param location: string (or list of strings) with relative/absolute location in the OMFIT tree

    :param base: tree object with respect to which the query is made

    :param base_is_relativeLocations_output: is the `base` parameter the output of the relativeLocations() function

    :return: absolute location string (or list of strings) in the OMFIT tree
    """
    multiple = not isinstance(location, str)
    locations = np.atleast_1d(location).tolist()

    if not base_is_relativeLocations_output:
        base = relativeLocations(base)

    for k, location in enumerate(locations):
        # skip if it's already an absolute location
        if re.match(r'^OMFIT\[.*\]$', location):
            locations[k] = location
            continue

        # evaluate location based on relativeLocation of the running topGUI script
        if location.startswith("OMFITmodules"):
            tmp = parseLocation(location)
            whereFrom = buildLocation(tmp[:2])
            path = buildLocation([''] + tmp[2:])
        else:
            whereFrom = re.sub(r'(^\w*)(\[.*\]$)', r'\1', location)
            path = location[len(whereFrom) :]
        exec("location = treeLocation(" + whereFrom + ")[-1]", globals(), base)
        location = base['location']
        locations[k] = location + path

    if multiple:
        return locations
    else:
        return locations[0]


# This variable is used to force all expressions to return None
# This is used when saving the OMFITtree and is useful since the information in the Namelist, NETcdf, etc... is already
# saved as an expression. Expressions entry tend to change depending on the user and result in differences which are
# caught by git. By forcing expressions to be evaluated as None when saving, git should not see these differences.
global OMFITexpressionsReturnNone
OMFITexpressionsReturnNone = False


def isinstance(a, b):
    if b is type:
        return builtins.isinstance(a, builtins.type)

    elif builtins.isinstance(a, OMFITlazyLoad):
        for bb in tolist(b):
            if bb.__name__ == 'OMFITlazyLoad':
                return True
        for bb in tolist(b):
            if a.cls == bb.__name__:
                return True
        for bb in tolist(b):
            if hasattr(eval(a.cls), '__subclasses__'):
                for cls in eval(a.cls).__subclasses__():
                    if isinstance_str(cls.__name__, bb.__name__):
                        return True
        return False
    if builtins.isinstance(a, OMFITdataset):
        for bb in tolist(b):
            if bb is xarray.Dataset:
                return True
    if builtins.isinstance(a, OMFITexpression) and b not in [OMFITexpression, OMFITiterableExpression]:
        a = a._value_()
    elif (
        builtins.isinstance(a, OMFITcollection)
        and a.selector is not None
        and not (inspect.isclass(b) and builtins.issubclass(b, OMFITcollection))
    ):
        a = a.GET(a.selector)
    try:
        b = tuple(b)  # builtins.isinstance specifically wants a tuple, not a list (which it gets sometimes)
    except TypeError:
        pass  # b is not iterable; don't need to convert list to tuple
    return builtins.isinstance(a, b)


isinstance.__doc__ = (
    builtins.isinstance.__doc__
    + '\n\nThis function is modified to account for special behavior of some OMFIT classes, such as OMFITexpression.'
)


def type(a, *args, **kw):
    if builtins.isinstance(a, OMFITexpression):
        a = a._value_()
    elif builtins.isinstance(a, OMFITcollection) and a.selector is not None:
        a = a.GET(a.selector)
    return builtins.type(a, *args, **kw)


def issubclass(a, b):
    if builtins.isinstance(a, OMFITexpression) and b not in [OMFITexpression, OMFITiterableExpression]:
        a = a._value_()
    elif builtins.isinstance(a, OMFITcollection) and a.selector is not None and b != OMFITcollection:
        a = a.GET(a.selector)
    if not inspect.isclass(a):
        raise TypeError('issubclass() arg 1 must be a class, not type %s' % (type(a)))
    return builtins.issubclass(a, b)


def hasattr(object, attribute):
    # this should be lastEval because in __getattr__(), getattr is called after _lastEval_()
    if builtins.isinstance(object, OMFITexpression):
        return hasattr(object.lastEval, attribute)
    return builtins.hasattr(object, attribute)


_deepcopy = copy.deepcopy


def _OMFITdeepcopy(object, memo=None, _nil=[]):
    if isinstance(object, OMFITexpression):
        global OMFITexpressionsReturnNone
        tmpExp = OMFITexpressionsReturnNone
        OMFITexpressionsReturnNone = True
        try:
            obj = _deepcopy(object, memo=memo, _nil=_nil)
            try:
                if hasattr(object, '_OMFITcopyOf'):
                    obj._OMFITcopyOf = object._OMFITcopyOf
                else:
                    obj._OMFITcopyOf = weakref.ref(object)
            except Exception:
                pass
        finally:
            OMFITexpressionsReturnNone = tmpExp
    else:
        if hasattr(object, 'dynaLoad'):
            if hasattr(object, 'duplicate') and object.dynaLoad:
                obj = object.duplicate()
            elif not object.dynaLoad:
                obj = _deepcopy(object, memo=memo, _nil=_nil)
            else:
                tmp = object.dynaLoad
                object.dynaLoad = False
                try:
                    obj = _deepcopy(object, memo=memo, _nil=_nil)
                    obj.dynaLoad = tmp
                finally:
                    object.dynaLoad = tmp
        else:
            obj = _deepcopy(object, memo=memo, _nil=_nil)

        if framework and isinstance(obj, OMFITobject):
            from omfit_classes.utils_base import _allOMFITobjects

            _allOMFITobjects.setdefault(obj.filename, []).append(weakref.ref(obj))

    return obj


_OMFITdeepcopy.__doc__ = _deepcopy.__doc__
copy.deepcopy = _OMFITdeepcopy

# monkey patch validation of path objects in os and unix_os Python modules
_fspath = os.fspath


def fspath(path):
    return _fspath(evalExpr(path))


os.fspath = fspath
_os.fspath = fspath

# ---------------------
# OMFIT tree
# ---------------------
class _OMFITnoSave(object):
    # objects that are derived from this class will not be saved
    # Note: not even an entry in OMFITsave.txt will be made
    pass


class OMFITtree(SortedDict):
    """
    A branch in the tree is represented in the filesystem as a directory.
    Note that the OMFIT object itself belongs to the OMFITmainTree class,
    which is a subclass of the OMFITtree class.
    """

    _save_method = '_save'

    def __init__(
        self,
        filename='',
        only=None,
        modifyOriginal=False,
        readOnly=False,
        quiet=False,
        developerMode=False,
        serverPicker=None,
        remote='',
        server='localhost',
        tunnel='',
        **kw,
    ):
        r"""
        :param filename: 'directory/bla/OMFITsave.txt' or 'directory/bla.zip' where the OMFITtree will be saved
                         (if '' it will be saved in the same folder of the parent OMFITtree)

        :param only: list of strings used to load only some of the branches from the tree (eg.  ["['MainSettings']","['myModule']['SCRIPTS']"]

        :param modifyOriginal: by default OMFIT will save a copy and then overwrite previous save only if successful.
                               If `modifyOriginal=True` and filename is not .zip, will write data directly at destination,
                               which will be faster but comes with the risk of deleting a good save if the new save
                               fails for some reason

        :param readOnly: will place entry in OMFITsave.txt of the parent so that this OMFITtree can be loaded,
                         but will not save the actual content of this subtree. `readOnly=True` is meant to be
                         used only after this subtree is deployed where its fileneme says it will be. Using this
                         feature could result in much faster projects save if the content of this tree is large.

        :param quiet: Verbosity level

        :param developerMode: load OMFITpython objects within the tree as modifyOriginal

        :param serverPicker: take server/tunnel info from MainSettings['SERVER']

        :param remote: access the filename in the remote directory

        :param server: if specified the file will be downsync from the server

        :param tunnel: access the filename via the tunnel

        :param \**kw: Extra keywords are passed to the SortedDict class
        """
        if serverPicker or (server and server != 'localhost'):
            if developerMode:
                raise OMFITexception('Cannot load remote data in developerMode')
            if modifyOriginal:
                raise OMFITexception('Cannot load remote data as modifyOriginal')
            omfitsave = None
            if filename.endswith('OMFITsave.txt'):
                filename, omfitsave = os.path.split(filename)
            tmp = OMFITobject(filename, serverPicker=serverPicker, remote=remote, server=server, tunnel=tunnel)
            filename = tmp.filename
            if os.path.isdir(filename):
                omfitsave = 'OMFITsave.txt'
            if omfitsave:
                filename = filename + os.sep + omfitsave
        SortedDict.__init__(self, **kw)
        self.modifyOriginal = False
        self.readOnly = False
        self.load(filename, only=only, modifyOriginal=modifyOriginal, readOnly=readOnly, quiet=quiet, developerMode=developerMode)

    def addBranchPath(self, location, leaf=special1, upTo=None):
        """
        Creates a path in the tree, without overwriting branches which already exist

        :param location: string containing the path to be added

        :param leaf: Value to set the destination if not present

        :param upTo: location is traversed up to `upTo`

        e.g. OMFIT['branch'].addBranchPath("['branch2']['branch3']")
        """
        path = parseBuildLocation(location)
        if upTo is not None:
            path = path[:upTo]
        addedPath = []
        loc = self
        for k, branch in enumerate(path):
            from omas import ODS

            if isinstance(loc, ODS):
                from omas.omas_utils import p2l, l2o

                ods_branch = list(flatten_iterable(list(map(p2l, path[k:]))))
                try:
                    loc[ods_branch]
                    addedPath.append((loc, l2o(ods_branch), 0))
                except ValueError:  # catch ValueError: `...` has no data
                    tmp = ODS()
                    tmp.omas_data = {}
                    loc[ods_branch] = tmp
                    addedPath.append((loc, l2o(ods_branch), 1))
                break
            if not isinstance(loc, dict):
                raise OMFITexception(
                    'Tree variable [\'' + path[k - 1] + '\'] is of type ' + str(type(loc).__name__) + ' and can not have sub-branches'
                )
            if branch in loc:
                addedPath.append((loc, branch, 0))
            else:
                if k + 1 < len(path) or leaf is special1:
                    loc[branch] = OMFITtree()
                else:
                    loc[branch] = leaf
                addedPath.append((loc, branch, 1))
            loc = loc[branch]
        return addedPath

    def duplicate(self, filename='', modifyOriginal=False, readOnly=False, quiet=True):
        """
        Similarly to the duplicate method for OMFITobjects, this method makes a copy by files.
        This means that the returned subtree objects will be pointing to different files from the one of the original object.
        This is to be contrasted to a deepcopy of an object, which copies the objects in memory, but does not duplicate the objects themselves.

        :param filename: if filename='' then the duplicated subtree and its files will live in the OMFIT working directory,
                         if filename='directory/OMFITsave.txt' then the duplicated subtree and its files will live in directory specified

        :param modifyOriginal: only if filename!=''
                               by default OMFIT will save a copy and then overwrite previous save only if successful.
                               If `modifyOriginal=True` and filename is not .zip, will write data directly at destination,
                               which will be faster but comes with the risk of deleting a good save if the new save
                               fails for some reason

        :param readOnly: only if filename!=''
                         will place entry in OMFITsave.txt of the parent so that this OMFITtree can be loaded,
                         but will not save the actual content of this subtree. `readOnly=True` is meant to be
                         used only after this subtree is deployed where its fileneme says it will be. Using this
                         feature could result in much faster projects save if the content of this tree is large.

        :param quiet: Verbosity level

        :return: new subtree, with objects pointing to different files from the one of the original object

        NOTE: readOnly+modifyOriginal is useful because one can get significant read (modifyOriginal) and write (readOnly) speed-ups,
              but this feature relies on the users pledging they will not modify the content under this subtree.
        """

        # duplicate internally
        if not filename:
            # generate a temporary directory name (safe for parallel runs)
            file_type = self.__class__.__name__
            subprocess_dir = '_'.join(map(str, OMFITaux['prun_process']))
            if len(subprocess_dir):
                subprocess_dir = '__p' + subprocess_dir
            directory = (
                OMFITcwd
                + os.sep
                + 'objects'
                + os.sep
                + file_type
                + '_'
                + utils_base.now("%Y-%m-%d__%H_%M" + subprocess_dir + os.sep + "%S__%f")
            )
            while os.path.exists(directory):
                directory += "_"
            filename = directory + os.sep + 'OMFITsave.txt'

            # deploy
            self.deploy(filename, quiet=quiet)

            # Reload and return new object, here we use modifyOriginal just to avoid making
            # yet another copy of the subtree since we are already in the OMFITcwd directory
            tmp = self.__class__(filename, modifyOriginal=True, readOnly=False, quiet=quiet)
            tmp.modifyOriginal = False

        # duplicate externally
        else:
            # Deploy
            self.deploy(filename, quiet=quiet)

            # reload and return new object (we do this explicitly here just to provide documentation)
            tmp = self.__class__(filename, modifyOriginal=modifyOriginal, readOnly=readOnly, quiet=quiet)

        return tmp

    def duplicateGUI(self, initial=None, modifyOriginal=False, readOnly=False, quiet=True):
        if initial is None:
            if OMFITaux['lastBrowsedDirectory']:
                initial = OMFITaux['lastBrowsedDirectory']
            else:
                initial = self.filename

        if os.path.isdir(initial):
            initialdir = initial
            initialfile = None
        else:
            initialdir = os.path.split(initial)[0]
            initialfile = os.path.split(initial)[1]

        location = tkFileDialog.asksaveasfilename(initialdir=initialdir, initialfile=initialfile, parent=OMFITaux['rootGUI'])

        if len(location):
            OMFITaux['lastBrowsedDirectory'] = os.path.split(location)[0]
            return self.duplicate(location + os.sep + 'OMFITsave.txt', modifyOriginal=modifyOriginal, readOnly=readOnly, quiet=quiet)

    def deploy(
        self,
        filename='',
        zip=False,
        quiet=False,
        updateExistingDir=False,
        serverPicker=None,
        server='localhost',
        tunnel='',
        s3bucket=None,
        ignoreReturnCode=False,
    ):
        """
        Writes the content of the branch on the filesystem

        :param filename: contains all of the information to reconstruct the tree and can be loaded with the load() function

        :param zip: whether the deploy should occur as a zip file

        :param updateExistingDir: if not `zip` and not `onlyOMFITsave` this option does not delete original directory but just updates it

        :param serverPicker: take server/tunnel info from MainSettings['SERVER']

        :param server: server to which to upload the file

        :param tunnel: tunnel to connect to the server

        :param s3bucket: name of s3 bucket to upload to

        :param ignoreReturnCode: ignore return code of rsync command
        """
        if filename == '' and self.filename:
            filename = os.path.split(self.filename)[1]

        # from serverPicker to server/tunnel
        if serverPicker is not None:
            server = SERVER[serverPicker]['server']
            tunnel = SERVER[serverPicker]['tunnel']

        # local deploy
        if is_localhost(server):
            getattr(self, self._save_method)(filename, zip=zip, quiet=quiet, updateExistingDir=updateExistingDir)
            return filename, server, tunnel

        # remote deploy
        else:
            if not len(os.path.split(os.path.abspath(filename))[0]):
                raise ValueError('Must specify full path for remote deployment')
            tmpDir = OMFITtmpDir + os.sep + 'scratch' + os.sep
            if not os.path.exists(tmpDir):
                os.makedirs(tmpDir)
            filename_save = getattr(self, self._save_method)(
                tmpDir + os.path.basename(filename), zip=zip, quiet=quiet, updateExistingDir=False
            )
            if not os.path.splitext(filename_save)[1] == '.zip':
                filename_save = os.path.split(filename_save)[0]
            filename = os.path.split(filename)[0] + os.sep + os.path.split(filename_save)[1]
            tmp = OMFITobject(filename_save, modifyOriginal=True, readOnly=True)
            tmp_return = tmp.deploy(filename, server=server, tunnel=tunnel, s3bucket=s3bucket, ignoreReturnCode=ignoreReturnCode)
            import shutil

            del tmp
            shutil.rmtree(tmpDir)
            return tmp_return

    def deployGUI(self, filename='', **kw):
        """
        Opens GUI for .deploy() method

        :param initial: Starting filename used in the GUI.
                        If None, then the last browsed directory is used (OMFITaux['lastBrowsedDirectory'])

        :return: if deployment was successful
        """

        if filename:
            if isinstance(filename, str):
                filename = (filename, 'localhost', '')
            kw['directory'] = os.path.split(filename[0])[0]
            kw['default'] = os.path.split(filename[0])[1]
            kw['server'] = filename[1]
            kw['tunnel'] = filename[2]

        from omfit_classes.OMFITx import SaveFileDialog

        fd = SaveFileDialog()

        if fd.how:
            self.deploy(filename=fd.how[0], server=fd.how[1], tunnel=fd.how[2], **kw)
            if is_localhost(fd.how[1]):
                printi('Deploy ' + fd.how[0])
            else:
                printi('Deploy ' + str(fd.how))

        return fd.how

    def _save(
        self,
        filename,
        only=None,
        zip=False,
        onlyOMFITsave=False,
        quiet=False,
        skipStorage=True,
        updateExistingDir=False,
        skip_save_errors=False,
    ):
        """
        the save() and saveas() method exists only for the OMFITmodule and OMFITmaintree class

        :param filename: filename to save to

        :param only: list of strings used to save only some of the branches in the tree (eg.  ["['MainSettings']","['myModule']['SCRIPTS']"]

        :param zip: save as zip file (used to force save as zip, even if filename is 'directory/OMFITsave.txt'

        :param onlyOMFITsave: only create the OMFITsave.txt file

        :param quiet: verbose output

        :param skipStorage: Skip OMFITstorage objects

        :param updateExistingDir: if not `zip` and not `onlyOMFITsave` this option does not delete original directory but just updates it

        :param skip_save_errors: skip errors when saving objects
        """
        if not isinstance(filename, str) or not len(filename):
            raise IOError('The specified OMFITtree filename is not valid: `' + str(filename) + '`')

        if not onlyOMFITsave and not quiet:
            types = OMFITtypes + OMFITdictypes
            for item in [SortedDict, SettingsName, NamelistName, OMFITtmp]:
                types.remove(item)
            nodes = OMFIT.traverse(onlyDict=tuple(types), skipDynaLoad=True)

        if not isinstance(quiet, dict):
            quiet = {'quiet': quiet}
        newline = quiet.get('newline', False)
        clean = quiet.get('clean', False)
        style = quiet.get('style', ' [{sfill}{svoid}] {perc:3.2f}% {mess}')
        quiet = quiet.get('quiet', quiet)

        def _print(text):
            if not onlyOMFITsave and not quiet:
                if text.startswith('['):
                    if text in nodes and not text.startswith("['__COMMANDBOX__']"):
                        ascii_progress_bar(
                            nodes.index(text), 0, len(nodes) - 1, text, quiet=quiet, newline=newline, clean=clean, style=style, width=10
                        )
                else:
                    printi(text)
                    print('', end='')

        def generateOMFITproperties(me, kid):
            # query item directly for OMFITproperties string
            tmp = {}
            if hasattr(me[kid], '__save_kw__'):
                tmp.update(me[kid].__save_kw__())
            if isinstance(me[kid], _OMFITpython):
                tmp.pop('modifyOriginal', None)
            if isinstance(me[kid], OMFITascii) and kid == 'help':
                tmp.pop('modifyOriginal', None)
            return re.sub(r'\n', r'\\n', repr(tmp))

        def f_traverse(me, myLocation, path):
            # store all paths in OMFITsave.txt the UNIX way
            mypath = path.replace('\\', '/')
            if isinstance(me, (SortedDict, OMFITlist)):
                if isinstance(me, SortedDict):
                    keys = me.keys()
                else:
                    keys = range(len(me))
                same_filename_counter = {}
                for kid in keys:
                    if isinstance(me, OMFITlist):
                        kidName = "[+]"
                    else:
                        kidName = "[" + repr(kid) + "]"
                    entryID = myLocation + kidName

                    if only is None or any(entryID.startswith(k) for k in tolist(only)):
                        if isinstance(me[kid], OMFITlazyLoad):
                            tp = me[kid].tp
                        elif not isinstance(me[kid], OMFITobjectError):
                            tp = me[kid].__class__.__name__
                        else:
                            tp = me[kid].className

                        changed_dir = False
                        if isinstance(me[kid], _OMFITnoSave):
                            pass
                        elif isinstance(me[kid], OMFITstorage) and skipStorage:
                            pass
                        elif isinstance(me[kid], OMFITlist):
                            path = mypath + str(kid) + '/'
                            if not onlyOMFITsave:
                                if not os.path.exists(str(kid)):
                                    os.makedirs(str(kid))
                                os.chdir(str(kid))
                                changed_dir = True
                            f.write(entryID + ' <-:-:-> ' + tp + ' <-:-:->  <-:-:-> ' + generateOMFITproperties(me, kid) + '\n')
                            _print(entryID)
                        elif isinstance(me[kid], OMFITtree):
                            path = mypath + str(kid) + '/'
                            if not onlyOMFITsave:
                                if not (isinstance(me[kid], OMFITcollection) and me[kid].OMFITproperties['no_subdir']):
                                    if not os.path.exists(str(kid)):
                                        os.makedirs(str(kid))
                                    os.chdir(str(kid))
                                    changed_dir = True
                                else:
                                    path = mypath + '/'
                            if me[kid].filename and not me[kid].readOnly and me[kid].modifyOriginal:
                                # if not readOnly and modifyOriginal then we have to update the deploy
                                me[kid].deploy(me[kid].filename)
                            if me[kid].filename and (me[kid].modifyOriginal or me[kid].readOnly):
                                filename = me[kid].filename.replace('\\', '/')
                                f.write(
                                    entryID
                                    + ' <-:-:-> '
                                    + tp
                                    + ' <-:-:-> '
                                    + filename
                                    + ' <-:-:-> '
                                    + generateOMFITproperties(me, kid)
                                    + '\n'
                                )
                            else:
                                f.write(entryID + ' <-:-:-> ' + tp + ' <-:-:->  <-:-:-> ' + generateOMFITproperties(me, kid) + '\n')
                            _print(entryID)
                        elif isinstance(me[kid], OMFITexpression):
                            f.write(entryID + ' <-:-:-> OMFITexpression <-:-:-> ' + '_' + repr(me[kid].expression) + ' <-:-:-> {}\n')
                            _print(entryID)
                        else:
                            saved = False
                            if isinstance(me[kid], (OMFITmds, OMFITmdsValue, OMFITtoksearch, OMFITwebLink)):
                                f.write(entryID + ' <-:-:-> ' + tp + ' <-:-:->  <-:-:-> ' + generateOMFITproperties(me, kid) + '\n')
                                saved = True
                                _print(entryID)
                            elif isinstance(me[kid], tuple(OMFITtypes)) and me[kid].filename is not None:
                                _print(entryID)
                                # NOTE: OMFITpython scripts are --always-- saved within a project, even if these are set to be modifyOriginal=True.
                                #      This means that scripts that are loaded as modifyOriginal they will be so only within that OMFIT session.
                                #      If a project is saved and then re-opened, then all scripts will be local to the project and will have modifyOriginal=False.
                                #      This is done to ensure consistency between the data in the project and the scripts that have been used to generate them.
                                try:
                                    if (
                                        not hasattr(me[kid], 'modifyOriginal')
                                        or not me[kid].modifyOriginal
                                        or isinstance(me[kid], _OMFITpython)
                                        or (isinstance(me[kid], OMFITascii) and kid == 'help')
                                    ):
                                        # this prevents overwriting of files with the same filename
                                        # directory naming is better if it's deterministic, so that files changes can be tracked with git
                                        if os.path.split(me[kid].filename)[1] not in same_filename_counter:
                                            same_filename_counter[os.path.split(me[kid].filename)[1]] = 0
                                        same_filename_counter[os.path.split(me[kid].filename)[1]] += 1
                                        count = same_filename_counter[os.path.split(me[kid].filename)[1]]
                                        if count > 1:
                                            tmpdir = os.path.split(me[kid].filename)[1] + '_' + str(count)
                                            # adding an hashing reduces the chances of filename clash to a minimum
                                            tmpdir += '_' + omfit_hash(tmpdir, 10) + os.sep
                                        else:
                                            tmpdir = ''
                                        # now for the actual saving...
                                        tmpfilename = tmpdir + os.path.split(me[kid].filename)[1]
                                        filename = mypath + tmpfilename
                                        if not onlyOMFITsave:
                                            if len(tmpdir) and not os.path.exists(tmpdir):
                                                os.makedirs(tmpdir)
                                            me[kid].deploy(tmpfilename)
                                    else:
                                        filename = os.path.abspath(me[kid].filename)
                                        if not onlyOMFITsave:
                                            me[kid].save()
                                except Exception as _excp:
                                    if isinstance(_excp, OSError) and _excp.errno == errno.ENOSPC:
                                        raise
                                    elif not skip_save_errors:
                                        raise
                                    else:
                                        printw('Error saving %s: %s' % (entryID, repr(_excp)))
                                filename = filename.replace('\\', '/')
                                f.write(
                                    entryID
                                    + ' <-:-:-> '
                                    + tp
                                    + ' <-:-:-> '
                                    + filename
                                    + ' <-:-:-> '
                                    + generateOMFITproperties(me, kid)
                                    + '\n'
                                )
                                saved = True
                            elif isinstance(me[kid], xarray.Dataset):
                                try:
                                    filename = 'OMFITxarray_' + omfit_hash(repr(kid), 10) + '.nc'
                                    exportDataset(me[kid], filename)
                                    f.write(entryID + ' <-:-:-> importDataset <-:-:-> ' + mypath + filename + ' <-:-:-> \n')
                                    saved = True
                                    _print(entryID)
                                except Exception as _excp:
                                    if isinstance(_excp, OSError) and _excp.errno == errno.ENOSPC:
                                        raise
                                    pass  # if the save as NetCDF fails, the data will be saved as pickle
                            elif isinstance(me[kid], pandas.DataFrame):
                                try:
                                    filename = 'OMFITpandas_' + omfit_hash(repr(kid), 10) + '.json'
                                    me[kid].to_json(filename)
                                    f.write(entryID + ' <-:-:-> pandas_read_json <-:-:-> ' + mypath + filename + ' <-:-:-> \n')
                                    saved = True
                                    _print(entryID)
                                except Exception as _excp:
                                    if isinstance(_excp, OSError) and _excp.errno == errno.ENOSPC:
                                        raise
                                    pass  # if the save as NetCDF fails, the data will be saved as pickle
                            elif (isinstance(me[kid], np.ndarray) and me[kid].dtype != 'object') and isinstance(me, (OMFITtree, OMFITlist)):
                                try:
                                    filename = 'OMFITndarray_' + omfit_hash(repr(kid), 10) + '.npy'
                                    np.save(filename, me[kid], allow_pickle=False)
                                    f.write(entryID + ' <-:-:-> importNdarray <-:-:-> ' + mypath + filename + ' <-:-:-> \n')
                                    saved = True
                                    _print(entryID)
                                except Exception as _excp:
                                    if isinstance(_excp, OSError) and _excp.errno == errno.ENOSPC:
                                        raise
                                    pass  # if the save as npy fails, the data will be saved as pickle
                            if not saved and isinstance(
                                me, (OMFITtree, OMFITlist)
                            ):  # this is to save quantities which are under a OMFITtree/OMFITlist but are not associated to a OMFITobject etc...
                                # Keep track of entries that are pickled
                                if os.environ.get('USER', '') in ['meneghini', 'smithsp', 'eldond']:
                                    pickled_objects.append(entryID)
                                try:
                                    tmp = pickle.dumps(me[kid], pickle.OMFIT_PROTOCOL)
                                    filename = 'OMFITpickled_' + omfit_hash(repr(kid), 10)
                                    if not onlyOMFITsave:
                                        with open(filename, 'wb') as f1:
                                            f1.write(tmp)
                                    f.write(
                                        entryID
                                        + ' <-:-:-> pickle <-:-:-> '
                                        + mypath
                                        + filename
                                        + ' <-:-:-> '
                                        + generateOMFITproperties(me, kid)
                                        + '\n'
                                    )
                                except Exception as _excp1:
                                    if isinstance(_excp1, OSError) and _excp1.errno == errno.ENOSPC:
                                        raise
                                    try:
                                        import dill

                                        filename = 'OMFITdilled_' + omfit_hash(repr(kid), 10)
                                        if not onlyOMFITsave:
                                            with open(filename, 'wb') as f1:
                                                dill.dump(me[kid], f1)
                                        f.write(
                                            entryID
                                            + ' <-:-:-> dill <-:-:-> '
                                            + mypath
                                            + filename
                                            + ' <-:-:-> '
                                            + generateOMFITproperties(me, kid)
                                            + '\n'
                                        )
                                    except Exception as _excp2:
                                        if isinstance(_excp2, OSError) and _excp2.errno == errno.ENOSPC:
                                            raise
                                        printe(
                                            entryID
                                            + ' is not an OMFITobject and could not be pickled and has been repr(...) instead!\nPICKLE:%s\nDILL:%s\nThis may not load correctly, please try to fix this if you can.'
                                            % (repr(_excp1), repr(_excp2))
                                        )
                                        f.write(
                                            entryID
                                            + ' <-:-:-> '
                                            + tp
                                            + ' <-:-:-> '
                                            + re.sub(r'\n', r'\\n', repr(me[kid]))
                                            + ' <-:-:-> '
                                            + generateOMFITproperties(me, kid)
                                            + '\n'
                                        )

                        # list of all the reasons for which the save should not go deeper into an object
                        if isinstance(me[kid], OMFITexpression):
                            pass
                        elif isinstance(me[kid], OMFITtree) and me[kid].filename and (me[kid].modifyOriginal or me[kid].readOnly):
                            # if readOnly we skip because we should not save
                            # if modifyOriginal we skip because we have deployed separately
                            pass
                        elif isinstance(me[kid], OMFITdir):
                            pass
                        elif isinstance(me[kid], OMFITmds):
                            pass
                        elif isinstance(me[kid], _OMFITnoSave):
                            pass
                        elif hasattr(me[kid], 'dynaLoad') and me[kid].dynaLoad:
                            pass
                        elif isinstance(me[kid], OMFITstorage) and skipStorage:
                            pass
                        elif (
                            isinstance(me[kid], tuple(OMFITtypes))
                            and not isinstance(me[kid], OMFITsettings)
                            and not isinstance(me[kid], OMFITmainSettings)
                            and not isinstance(me[kid], OMFITnamelist)
                        ):
                            # do not go inside of OMFITtypes, unless it's OMFITsettings, OMFITmainSettings or OMFITnamelists, since there can be OMFITexpressions that need to be saved there
                            pass
                        else:
                            kidName = "[" + repr(kid) + "]"
                            entryID = myLocation + kidName
                            f_traverse(me[kid], entryID, path)
                        if changed_dir:
                            if not onlyOMFITsave:
                                os.chdir('..')

        # setup the save filenames and directories
        oldDir = os.getcwd()
        if onlyOMFITsave:
            if not os.path.splitext(filename)[1] == '.txt':
                filename = filename + os.sep + 'OMFITsave.txt'
            file = os.path.abspath(filename)
        else:
            filename = os.path.abspath(filename)
            if zipfile.is_zipfile(filename) or os.path.splitext(filename)[1] == '.zip':
                filename = os.path.splitext(filename)[0] + os.sep + 'OMFITsave.txt'
                zip = True
            elif not os.path.splitext(filename)[1] == '.txt':
                filename = filename + os.sep + 'OMFITsave.txt'

            file = os.path.split(filename)[1]
            directoryOrig = os.path.split(filename)[0]
            # `directory` is the temporary save directory
            tmpSaveDir = OMFITcwd + os.sep + 'tmpSaveDir_' + utils_base.now("%Y-%m-%d__%H_%M_%S__%f")
            directory = tmpSaveDir + os.sep + os.path.split(directoryOrig)[1]
            if not os.path.exists(directory):
                os.makedirs(directory)
            os.chdir(directory)

        try:
            with open(file, 'w') as f:
                global OMFITexpressionsReturnNone
                tmpExp = OMFITexpressionsReturnNone
                OMFITexpressionsReturnNone = True
                pickled_objects = []
                try:
                    if only is None:
                        f_traverse(self, '', '.' + os.sep)
                    else:
                        f_traverse(
                            eval('self' + buildLocation(parseLocation(only)[:-1])), buildLocation(parseLocation(only)[:-1]), '.' + os.sep
                        )
                finally:
                    OMFITexpressionsReturnNone = tmpExp

            if not onlyOMFITsave:

                if pickled_objects:
                    # If printe or printw then fails to quick-save
                    _print('The following objects were pickled:')
                    for item in pickled_objects:
                        _print(f"- {item}")

                if not zip:
                    # if you got here, over-write original directory
                    _print('\nMoving files to save directory: ' + directoryOrig + '   ' + directory)
                    if not updateExistingDir:
                        if os.path.exists(directoryOrig):
                            shutil.rmtree(directoryOrig)
                        try:
                            shutil.move(directory, directoryOrig)
                        except PermissionError as _excp:
                            # on windows it raise an error, but content of folders is moved
                            if os.name == 'nt':
                                printe(_excp)
                            else:
                                raise

                    else:
                        update_dir(directory, directoryOrig)
                        if os.path.exists(directory):
                            shutil.rmtree(directory)
                    return filename
                else:
                    # compress directory
                    os.chdir('..')
                    filenameZip = os.path.abspath(directoryOrig + '.zip')
                    _print('\nCompressing files to archive: ' + filenameZip)
                    zipfolder(os.path.split(directoryOrig)[1], filenameZip)
                    return filenameZip

        finally:
            os.chdir(oldDir)
            # remove compress directory if still present
            if not onlyOMFITsave and directoryOrig != directory and os.path.exists(directory):
                shutil.rmtree(directory)

    def _load(
        self,
        filename,
        only=None,
        modifyOriginal=False,
        readOnly=False,
        quiet=False,
        developerMode=False,
        lazyLoad=bool(safe_eval_environment_variable('OMFIT_LAZYLOAD', False)),
    ):
        global OMFITexpressionsReturnNone
        tmpExp = OMFITexpressionsReturnNone
        OMFITexpressionsReturnNone = True

        if not isinstance(quiet, dict):
            quiet = {'quiet': quiet}
        newline = quiet.get('newline', False)
        clean = quiet.get('clean', False)
        mess = quiet.get('mess', lambda x: x[0])
        style = quiet.get('style', ' [{sfill}{svoid}] {perc:3.2f}% {mess}')
        quiet = quiet.get('quiet', quiet)

        oldDir = os.getcwd()

        if isinstance(only, str):
            only = [only]

        try:
            # extract archive if it's a zip file
            OMFITaux['noCopyToCWD'] = modifyOriginal
            if zipfile.is_zipfile(filename):
                if not quiet:
                    printi('Deflating ZIP save file...')
                    print('', end='')
                filenameZip = filename
                # use cherry_pick_OMFITsave for partial extraction of data from zip file (faster)
                deflate_dir = OMFITcwd + os.sep + 'deflate_' + utils_base.now("%Y-%m-%d__%H_%M_%S__%f")
                filename = cherry_pick_OMFITsave(filename, only, deflate_dir=deflate_dir)
                OMFITaux['noCopyToCWD'] = True

            # read save file OMFITsave.txt
            if not quiet and not os.path.abspath(filename).startswith(os.path.abspath(OMFITsrc + '/../modules/')):
                printi('Reading ' + os.path.abspath(filename))
            os.chdir(os.path.split(filename)[0])
            with open(filename, 'r') as f:
                text = f.read().split('\n')

            # split each line in the save file
            split_pttrn = re.compile(' *<-:-:-> *')
            split_text = []
            for line in text:
                if len(line):
                    split_text.append(re.split(split_pttrn, line))

            # load all tree objects
            for line in ascii_progress_bar(split_text, mess=mess, quiet=quiet, newline=newline, clean=clean, style=style, width=10):
                only_match = [line[0].startswith(str(k)) for k in tolist(only)]
                if only is None or np.any(only_match):
                    if np.any(only_match):
                        need_path = only[only_match.index(True)]
                        self.addBranchPath(need_path)

                    # these are for backward compatibility
                    if line[1] == 'OMFITpython':
                        line[1] = 'OMFITpythonTask'
                    elif line[1] == 'OMFITdict':
                        line[1] = 'SortedDict'
                    elif line[1] == 'OMFITfileASCII':
                        line[1] = 'OMFITascii'
                    elif line[1] == 'OMFIT_Ufile':
                        line[1] = 'OMFITuFile'
                    elif line[1] == 'gksoutClass':
                        line[1] = 'OMFITgksout'
                    elif line[1].startswith('OMFIT_tglf'):
                        line[1] = line[1].replace('OMFIT_tglf', 'OMFITtglf')
                    elif line[0] == "['help']" and line[1] == 'OMFITascii' and line[2].endswith('help.rst'):
                        line[1] = 'OMFIThelp'

                    try:
                        issubclass(eval(line[1]), OMFITmds)
                        classicClass = True
                    except Exception:
                        classicClass = False

                    if line[0].strip().endswith('[+]'):
                        line[0] = line[0].strip()[:-3]
                        exec('self%s.append(None)' % line[0])
                        n = eval('len(self%s)' % line[0]) - 1
                        line[0] = line[0] + "[%d]" % n

                    try:
                        if line[1] in ['OMFITexpression', 'OMFITiterableExpression']:
                            exec('self' + line[0] + '={}')  # these entries will be over-written later during the load
                        elif classicClass and issubclass(eval(line[1]), OMFITlist):
                            exec('self' + line[0] + '=' + line[1] + '()')
                        elif classicClass and issubclass(eval(line[1]), OMFITtree):
                            developerModeString = {False: '', True: ',developerMode=True', 3: ',developerMode=3'}[developerMode]
                            if len(line[3]):
                                exec(
                                    'self' + line[0] + '=' + line[1] + '(' + repr(line[2]) + developerModeString + ',**' + line[3] + ')',
                                    globals(),
                                    locals(),
                                )
                            else:
                                exec(
                                    'self' + line[0] + '=' + line[1] + '(' + repr(line[2]) + developerModeString + ')', globals(), locals()
                                )
                        elif line[1] in OMFITtypesStr or line[1] in ['importDataset', 'OMFITeqdsk', 'pandas_read_json']:
                            kw = {}
                            if len(line) > 3 and len(line[3]):
                                kw = eval(line[3])
                            if lazyLoad and line[1] in ['importDataset', 'pandas_read_json']:
                                exec(
                                    'self'
                                    + line[0]
                                    + '=OMFITlazyLoad('
                                    + repr('OMFIT' + line[0])
                                    + ','
                                    + repr(line[1])
                                    + ','
                                    + repr(line[2])
                                    + ',**'
                                    + repr(kw)
                                    + ')'
                                )
                            else:
                                if os.path.abspath(line[2]) == line[2] or (developerMode and line[1].startswith('OMFITpython')):
                                    kw['modifyOriginal'] = True
                                exec('self' + line[0] + '=' + line[1] + '(' + repr(line[2]) + ',**' + repr(kw) + ')')
                        elif classicClass and issubclass(eval(line[1]), OMFITmds):
                            if len(line[2]):
                                # backward compatibility
                                line[3] = {}
                                line[3]['treename'], tmp = line[2].split(' #')[:2]
                                line[3]['shot'], line[3]['server'] = tmp.split(' @ ')[:2]
                                line[3]['shot'] = line[3]['shot'].strip('\'"')
                                line[3]['subtree'] = ''
                                line[3] = repr(line[3])
                            tmp = eval(line[1])(**eval(line[3]))
                            exec('self' + line[0] + "=tmp")
                        elif classicClass and issubclass(eval(line[1]), OMFITmdsValue):
                            if len(line[2]):
                                # backward compatibility
                                line[3] = {}
                                line[3]['treename'], tmp = line[2].split(' #')[:2]
                                line[3]['shot'], tmp = tmp.split(' @ ')[:2]
                                line[3]['shot'] = line[3]['shot'].strip('\'"')
                                line[3]['server'], line[3]['TDI'] = tmp.split('|')[:2]
                                line[3] = repr(line[3])
                            tmp = eval(line[1])(**eval(line[3]))
                            exec('self' + line[0] + "=tmp")
                        elif line[1] in ['OMFITtoksearch', 'OMFITwebLink']:
                            tmp = eval(line[1])(**eval(line[3]))
                            exec('self' + line[0] + "=tmp")
                        elif line[1] == 'importNdarray':
                            exec(f'self{line[0]}=np.load({repr(line[2])})')
                        elif line[1] in ['pickle', 'OMFITpickle']:
                            if lazyLoad and os.stat(line[2]).st_size > 1024.0:
                                exec(
                                    'self' + line[0] + '=OMFITlazyLoad(' + repr('OMFIT' + line[0]) + ',"OMFITpickle",' + repr(line[2]) + ')'
                                )
                            else:
                                exec('self' + line[0] + '=OMFITpickle(' + repr(line[2]) + ')')
                        elif line[1] == 'dill':
                            import dill

                            with open(line[2], 'rb') as f1:
                                exec('self' + line[0] + '=dill.load(f1)')
                        else:
                            exec('self' + line[0] + "=" + re.sub(r'\\n', r'\n', line[2]))
                    except Exception as _excp:
                        try:
                            ctb = ", traceback=" + repr(''.join(traceback.format_exception(*sys.exc_info())).strip())
                        except Exception:
                            ctb = ''
                        try:
                            exec(
                                'self'
                                + line[0]
                                + '=OMFITobjectError('
                                + repr(line[2])
                                + ','
                                + repr(line[1])
                                + ',error='
                                + repr(repr(_excp))
                                + ctb
                                + ')'
                            )
                        except Exception:
                            try:
                                exec('self' + line[0] + '=OMFITerror(' + repr(repr(_excp)) + ctb + ')')
                            except Exception:
                                pass
                        printe(f'\n{repr(line)}:{repr(_excp)}')
                        printd(
                            '-' * 20
                            + '\n'
                            + repr(line)
                            + ': '
                            + repr(_excp)
                            + '\n'
                            + ''.join(traceback.format_exception(*sys.exc_info())).strip(),
                            topic='project load errors',
                        )

            # now load all of the expressions
            for line in split_text:
                if only is None or np.any([line[0].startswith(k) for k in tolist(only)]):
                    if line[1] in ['OMFITexpression', 'OMFITiterableExpression']:
                        if line[2][0] == '_':
                            # read new way of saving OMFITexpressions
                            expr = line[2][1:]
                            # backward compatibility to allow opening and running old TRANSP project
                            expr = expr.replace("datetime.date(2000, 01, 01)", "datetime.date(2000, 1, 1)")
                            tmp = OMFITexpression(eval(expr))
                        else:
                            # read old way of saving OMFITexpressions (backward compatibility)
                            tmp = OMFITexpression(re.sub(r'\\n', r'\n', line[2]))
                        try:
                            exec('self' + line[0] + "=tmp")
                        except Exception as _excp:
                            printe(repr(line) + ': ' + repr(_excp))

            # add __scratch__ if this is a OMFITmodule class
            # (needs to happen before expression evaluation)
            if isinstance(self, OMFITmodule):
                self['__scratch__'] = OMFITtmp()

            # now evaluate all expressions
            # to determine if these are iterable or not
            OMFITexpressionsReturnNone = False
            for line in split_text:
                if (only is None or np.any([line[0].startswith(k) for k in tolist(only)])) and not line[0].startswith(
                    "['SETTINGS']['DEPENDENCIES']"
                ):
                    if line[1] in ['OMFITexpression', 'OMFITiterableExpression']:
                        if quiet > 1:
                            printi('eval expression: ' + line[0])
                        try:
                            exec('self' + line[0] + "._value_()")
                        except Exception:
                            pass

        except Exception:
            printe('Not a valid OMFITsave file')
            raise

        finally:
            os.chdir(oldDir)
            OMFITexpressionsReturnNone = tmpExp

    def load(
        self,
        filename=None,
        only=None,
        modifyOriginal=False,
        readOnly=False,
        quiet=False,
        developerMode=False,
        lazyLoad=bool(safe_eval_environment_variable('OMFIT_LAZYLOAD', False)),
    ):
        """
        method for loading OMFITtree from disk

        :param filename: 'directory/bla/OMFITsave.txt' or 'directory/bla.zip' where the OMFITtree will be saved
                         (if '' it will be saved in the same folder of the parent OMFITtree)

        :param only: list of strings used to load only some of the branches from the tree (eg.  ["['MainSettings']","['myModule']['SCRIPTS']"]

        :param modifyOriginal: by default OMFIT will save a copy and then overwrite previous save only if successful.
                               If `modifyOriginal=True` and filename is not .zip, will write data directly at destination,
                               which will be faster but comes with the risk of deleting a good save if the new save
                               fails for some reason

        :param readOnly: will place entry in OMFITsave.txt of the parent so that this OMFITtree can be loaded,
                         but will not save the actual content of this subtree. `readOnly=True` is meant to be
                         used only after this subtree is deployed where its fileneme says it will be. Using this
                         feature could result in much faster projects save if the content of this tree is large.

        :param quiet: Verbosity level

        :param developerMode: load OMFITpython objects within the tree as modifyOriginal

        :param lazyLoad: enable/disable lazy load of picklefiles and xarrays
        """
        if filename is None:
            # reload
            filename = self.filename
            modifyOriginal = self.modifyOriginal
            readOnly = self.readOnly
        else:
            if os.path.isdir(filename):
                if os.path.exists(filename + os.sep + 'OMFITsave.txt'):
                    filename = filename + os.sep + 'OMFITsave.txt'
                else:
                    raise ValueError(filename + ' is a directory without OMFITsave.txt in it')
            self.filename = filename
            self.modifyOriginal = modifyOriginal
            self.readOnly = readOnly

        if not hasattr(self, 'OMFITproperties'):
            self.OMFITproperties = {}

        self.clear()

        if not filename:
            return

        try:
            TMPnoCopyToCWD = OMFITaux['noCopyToCWD']
            OMFITaux['noCopyToCWD'] = False
            return self._load(
                filename,
                only=only,
                modifyOriginal=modifyOriginal,
                readOnly=readOnly,
                quiet=quiet,
                developerMode=developerMode,
                lazyLoad=lazyLoad,
            )
        finally:
            OMFITaux['noCopyToCWD'] = TMPnoCopyToCWD

    def _moduleDict(self, onlyModuleID=None, level=-1):
        """
        Returns a dictionary of currently loaded modules

        :param onlyModuleID: string or list of strings of module ID to search for

        :param level: how many modules deep to go

        The dictionary contains the modules settings for each of the modules
        """

        def f_traverse(me, myLocation, modDict, level):
            if isinstance(me, OMFITtree):
                for kid in list(me.keys()):
                    kidName = "[" + repr(kid) + "]"
                    entryID = myLocation + kidName
                    if isinstance(me[kid], OMFITtree) and not (hasattr(me[kid], 'dynaLoad') and me[kid].dynaLoad):
                        if isinstance(me[kid], OMFITmodule):
                            if 'SETTINGS' not in me[kid]:
                                continue
                            if 'MODULE' not in me[kid]['SETTINGS']:
                                me[kid]['SETTINGS']['MODULE'] = SortedDict()
                            if onlyModuleID is None or me[kid]['SETTINGS']['MODULE']['ID'] in tolist(onlyModuleID):
                                modDict[entryID] = {}
                                for item in _moduleAttrs:
                                    if item not in me[kid]['SETTINGS']['MODULE']:
                                        modDict[entryID][item] = None
                                    else:
                                        modDict[entryID][item] = evalExpr(me[kid]['SETTINGS']['MODULE'][item])
                            if level != 0:
                                f_traverse(me[kid], entryID, modDict, level=level - 1)
                        else:
                            f_traverse(me[kid], entryID, modDict, level=level)
            return modDict

        return f_traverse(self, myLocation='', modDict=OrderedDict(), level=level)

    def __setitem__(self, key, value):
        """
        Override SortedDict.__setitem__ and ensure save/load compatibility of sub-objects
        """
        if np.iterable(key) and '/' in key and 'OMFITtree' in get_bases(type(value)):
            raise OMFITexception(
                'The key `' + str(key) + '  contains the `/` character, which is invalid for an ' + self.__class__.__name__ + ' type object'
            )

        return super().__setitem__(key, value)

    def __save_kw__(self):
        """
        :return: kw dictionary used to save the attributes to be passed when reloading from OMFITsave.txt
        """
        if self.modifyOriginal:
            self.OMFITproperties['modifyOriginal'] = self.modifyOriginal
        elif 'modifyOriginal' in self.OMFITproperties:
            del self.OMFITproperties['modifyOriginal']
        if self.readOnly:
            self.OMFITproperties['readOnly'] = self.readOnly
        elif 'readOnly' in self.OMFITproperties:
            del self.OMFITproperties['readOnly']
        return self.OMFITproperties

    def close(self):
        """
        Recursively calls the .close() method on OMFITobjects and OMFITtree objects
        """
        for item in self:
            if isinstance(self[item], (OMFITobject, OMFITtree)):
                self[item].close()

    def populate_from_directory(self, dirname, extensions={}, **kw):
        """
        Load files from a directory maintaning directory structure

        :param dirname: directory path

        :param extensions: dictionary mapping filename expression to OMFIT classes, for example: {'*.dat': 'OMFITnamelist', '*.xml': 'OMFITxml'}
        """

        def traverse(obj, dd, path=''):
            for k in dd:
                if path:
                    p = path + os.sep + k
                else:
                    p = dirname + os.sep + k
                # directory
                if isinstance(dd[k], dict):
                    obj[k] = OMFITtree()
                    traverse(obj[k], dd[k], p)
                # leaf
                else:
                    match = False
                    import fnmatch

                    for ext in extensions:
                        if fnmatch.fnmatch(p, ext):
                            exec('from omfit_classes.omfit_python import ' + extensions[ext], globals(), locals())
                            obj[k] = eval(extensions[ext])(p, **kw)
                            match = True
                            break
                    if not match:
                        if is_binary_file(p):
                            obj[k] = OMFITpath(p, **kw)
                        else:
                            obj[k] = OMFITascii(p, **kw)
            return obj

        dd = dir2dict(dirname)[dirname]
        return traverse(self, dd, '')


def cherry_pick_OMFITsave(filename, only=None, deflate_dir=None):
    """
    Cherry pick data from a OMFIT save data file

    :param filename: path to the OMFIT save file (zipped or not)

    :param only: string or list of strings of the data to be loaded
    If None, then all of the data is extracted

    :param deflate_dir: extract data     to this folder

    :return: either data or path to the OMFITsave.txt file that was extracted
    """

    if isinstance(only, str):
        only = [only]

    if deflate_dir is None:
        deflate_dir = OMFITcwd + os.sep + 'projects_preview' + os.sep
    deflate_dir = os.path.abspath(deflate_dir) + os.sep
    if not os.path.exists(deflate_dir):
        os.makedirs(deflate_dir)

    # zip file extraction
    if zipfile.is_zipfile(filename):
        isZip = True
        myzipfile = zipfile.ZipFile(filename, 'r', allowZip64=True)
        basepath = os.path.split(myzipfile.namelist()[0])[0]
        if basepath:
            basepath = basepath + os.sep
        omfitsavetxt = deflate_dir + basepath + 'OMFITsave.txt'
        if only is None:
            myzipfile.extractall(deflate_dir)
            # return the omfitsavetxt
            return omfitsavetxt
        else:
            myzipfile.extract(basepath + 'OMFITsave.txt', deflate_dir)
    # "fake" zipfile extraction if not compressed
    else:
        basepath = ''
        omfitsavetxt = deflate_dir + 'OMFITsave.txt'
        shutil.copy2(filename, deflate_dir)
        load_dir = os.path.split(filename)[0] + os.sep
        isZip = False

    # OMFITsave
    with open(omfitsavetxt, 'r') as f:
        lines = f.read().split('\n')

    # filter only the data to be loaded
    mini_OMFITsave = []
    for line in lines:
        if any(line.startswith(location) for location in only):
            mini_OMFITsave.append(line)

    # only extract the files that are needed
    for line in mini_OMFITsave:
        tmp = line.split(' <-:-:-> ')
        if tmp[2].startswith('./'):
            filename = re.sub(r'^\./', '', tmp[2])
            if isZip:
                for fi in myzipfile.namelist():
                    if fi.startswith(basepath + filename):
                        myzipfile.extract(fi, deflate_dir)
            else:
                shutil.copy2(load_dir + filename, deflate_dir)

    # Update OMFITsave.txt with only the relevant entries
    with open(omfitsavetxt, 'w') as f:
        f.write('\n'.join(mini_OMFITsave))

    # return the omfitsavetxt
    return omfitsavetxt


class OMFITlist(list):
    """
    list of which the individual values are saved to disk as it is done for the key:value pairs in an OMFITtree object
    """

    pass


class specialList(list):
    def __call__(self, *args, **kw):
        out = specialList()
        for k in self:
            out.append(k.__call__(*args, **kw))
        if len(out) and is_numeric(out[0]):
            out = np.array(out).T
        return out

    def __getattr__(self, key):
        if key in ['__array_struct__', '__array_interface__', '__array__']:
            raise AttributeError('bad attribute `%s`' % key)
        out = specialList()
        for k in self:
            out.append(getattr(k, key))
        if len(out) and is_numeric(out[0]):
            out = np.array(out).T
        return out


def _collection_decorator(f):
    def ff(*args, **kw):
        self = args[0]
        fname = f.__name__
        global OMFITexpressionsReturnNone
        if OMFITexpressionsReturnNone or self.selector is None:
            return f(*args, **kw)
        elif fname in ['_keyCaseInsensitive']:  # discard existing class decorators
            return f(*args, **kw)
        else:
            return getattr(super().__getitem__(self.selector), fname)(*args[1:], **kw)

    return ff


def _for_all_inherited_methods(decorator):
    def decorate(cls):
        for name, fn in inspect.getmembers(cls, inspect.ismethod):
            if name not in cls.__dict__:  # decorate inherited methods only, not overloaded or new methods
                setattr(cls, name, decorator(fn))
        return cls

    return decorate


def module_selective_deepcopy(location, classes):
    """
    Function that returns the equivalent of a module copy.deepcopy
    but can selectively include entries based on their class

    :param location: string with OMFIT tree location where the module resides

    :param classes: list of strings with allwed classes

    :return: copy of the module containing a deepcopy of the allowed classes
    """
    treeClasses = ['OMFITtree', 'OMFITmodule']

    # traverse the tree and avoid going deeper in the classes that are not of interet
    tmp_tree = traverse(eval(location), onlyDict=tuple(map(eval, classes + treeClasses)), skipDynaLoad=True)
    tmp_cls = traverse(eval(location), onlyLeaf=tuple(map(eval, classes)), skipDynaLoad=True)

    # prune empty trees
    for k, tr in list(enumerate(tmp_tree))[::-1]:
        keep = False
        for cl in tmp_cls:
            if tr in cl:
                keep = True
                break
        if not keep:
            tmp_tree.pop(k)

    # build structure and deepcopy
    module = OMFITmodule()
    for item in tmp_tree:
        obj = eval(location + item)
        if obj.__class__.__name__ in treeClasses:
            exec('module%s=%s()' % (item, obj.__class__.__name__))
        else:
            exec('module%s=copy.deepcopy(obj)' % (item))

    return module


def module_noscratch_deepcopy(module_root):
    """
    deepcopy of a module (and submodules) but neglecting the scratch '__scratch__' directories

    :param module_root: instance of the module to be copied

    :return: module deepcopy
    """
    tmp = traverse(module_root, onlyLeaf=(OMFITtmp,), skipDynaLoad=True)
    try:
        bkp = []
        for item in tmp:
            if '__scratch__' in item:
                bkp.append(eval('module_root' + item))
                exec('module_root' + item + '=OMFITtmp()')
        return copy.deepcopy(module_root)
    finally:
        for item in tmp:
            if '__scratch__' in item:
                exec('module_root' + item + '=bkp.pop(0)')


class env_from_import(dict):
    """
    This class is used to expose the namespace
    of an import as a dictionary, which is useful
    to pass such namespace to eval() or exec() statements
    """

    import_namespace = None

    def __getitem__(self, key):
        if key in self:
            return dict.__getitem__(self, key)
        elif self.import_namespace is not None:
            return getattr(self.import_namespace, key)
        else:
            raise KeyError(key)


@_for_all_inherited_methods(_collection_decorator)
class OMFITcollection(OMFITtree):
    """
    A class for holding sets of similar objects

    :param selector: sets selection of a specific realization (`None` for all realizations, `'random'` for a random realization). This can also be an OMFITexpression.

    :param strategy: sets operation to be performed on all realizations (if `.selector == None`)

    :param raise_errors: sets how to proceed in case of errors (eg. missing objects, attributes)

        * `None`: print warning on errors

        * `True`: raise errors

        * `False`: ignore errors

    :param no_subdir: This keyword affects how the OMFITcollection is deployed.

        * `False` (default) the OMFITcollection is deployed like a normal OMFITtree, such that the files of the
            collection are deployed under a subdirectory, whose name comes from the entry in the tree

        * `True` the files are deployed in the same level directory as the parent

    `.selector`, `.strategy`, `.raise_errors` can be modified after the object is instantiated

    >> tmp=OMFITcollection(raise_errors=True)
    >> for k in range(1,10):
    >>     tmp[k]={}
    >>     tmp[k]['hello']=np.linspace(0,1,100)**k
    >>
    >> #return a single realization
    >> tmp.selector=5
    >> tmp.strategy=None
    >> pyplot.plot(tmp['hello'],'--r',lw=2)
    >>
    >> #return all realizations
    >> tmp.selector=None
    >> tmp.strategy=None
    >> plotc(tmp['hello'])
    >>
    >> #attribute on all realizations
    >> tmp.selector=None
    >> tmp.strategy=None
    >> print(tmp['hello'].mean())
    >>
    >> #perform operation on all realizations
    >> tmp.selector=None
    >> tmp.strategy='np.mean(x,axis=1)'
    >> pyplot.plot(tmp['hello'],'k--',lw=2)
    >>
    >> OMFIT['variable']=3
    >> tmp.selector=OMFITexpression("OMFIT['variable']")
    >> print(tmp)
    >>
    >> print(tmp.GET(3)['hello']-tmp['hello'])
    >>
    >> # to update values, you can use the UPDATE method
    >> tmp.UPDATE(location="['hello'][0]",values=-1e6)
    >> tmp.selector=None
    >> tmp.strategy=None
    >> print(tmp['hello'].mean())
    """

    def __init__(
        self,
        filename='',
        modifyOriginal=False,
        readOnly=False,
        quiet=False,
        selector=None,
        strategy=None,
        raise_errors=None,
        no_subdir=False,
        **kw,
    ):
        OMFITtree.__init__(self, filename=filename, modifyOriginal=modifyOriginal, readOnly=readOnly, quiet=quiet, **kw)
        self.OMFITproperties = {'modifyOriginal': modifyOriginal, 'readOnly': readOnly}
        self.selector = selector
        self.strategy = strategy
        self.raise_errors = raise_errors
        self._filename = filename
        self.OMFITproperties['no_subdir'] = no_subdir

    def _warning(self, k, _excp):
        printw('Error accessing item `' + str(k) + '` : ' + repr(_excp))

    @property
    def selector(self):
        global OMFITexpressionsReturnNone
        if OMFITexpressionsReturnNone:
            return None

        if 'OMFITproperties' not in self.__dict__:
            return None

        if isinstance(self.OMFITproperties['selector'], str) and self.OMFITproperties['selector'].startswith('_!OMFITexpression!_'):
            selector_string = self.OMFITproperties['selector'][len('_!OMFITexpression!_') :]
            locals = {}
            if self._OMFITparent is not None:
                locals.update(relativeLocations(self))
            try:
                selector = eval(selector_string, globals(), locals)

            except Exception:
                try:
                    exec(selector_string, globals(), locals)
                    if 'return_variable' in locals:
                        selector = locals['return_variable']
                    else:
                        selector = None
                except Exception:
                    raise
        else:
            selector = self.OMFITproperties['selector']

        return selector

    @selector.setter
    def selector(self, value):
        if value == 'random':
            import random

            self.OMFITproperties['selector'] = random.choice(self.KEYS())
        elif isinstance(value, OMFITexpression):
            self.OMFITproperties['selector'] = '_!OMFITexpression!_' + value.expression
        else:
            self.OMFITproperties['selector'] = value

    @selector.deleter
    def selector(self):
        self.OMFITproperties['selector'] = None

    @property
    def filename(self):
        global OMFITexpressionsReturnNone
        if OMFITexpressionsReturnNone or self.selector is None:
            return self._filename
        else:
            return self.GET(self.selector).filename

    @filename.setter
    def filename(self, value):
        if self.selector is None:
            self._filename = value
        else:
            self.GET(self.selector).filename = value

    @property
    def strategy(self):
        if self.OMFITproperties['strategy'] is None:
            return 'x'
        else:
            return self.OMFITproperties['strategy']

    @strategy.setter
    def strategy(self, value):
        if not (isinstance(value, str) or value is None):
            raise OMFITexception('strategy should be either a string or `None`')
        if isinstance(value, str) and 'x' not in value:
            raise OMFITexception('strategy string should cointain `x`')
        self.OMFITproperties['strategy'] = value

    @strategy.deleter
    def strategy(self):
        self.OMFITproperties['strategy'] = None

    @property
    def raise_errors(self):
        return self.OMFITproperties['raise_errors']

    @raise_errors.setter
    def raise_errors(self, value):
        self.OMFITproperties['raise_errors'] = value

    @raise_errors.deleter
    def raise_errors(self):
        self.OMFITproperties['raise_errors'] = None

    def __getstate__(self):
        global OMFITexpressionsReturnNone
        tmpExp = OMFITexpressionsReturnNone
        OMFITexpressionsReturnNone = True
        try:
            tmp = super().__getstate__()
            return tmp
        finally:
            OMFITexpressionsReturnNone = tmpExp

    def __setstate__(self, dict):
        global OMFITexpressionsReturnNone
        tmpExp = OMFITexpressionsReturnNone
        OMFITexpressionsReturnNone = True
        try:
            return super().__setstate__(dict)
        finally:
            OMFITexpressionsReturnNone = tmpExp

    def __deepcopy__(self, memo):
        global OMFITexpressionsReturnNone
        tmpExp = OMFITexpressionsReturnNone
        OMFITexpressionsReturnNone = True
        try:
            return pickle.loads(pickle.dumps(self, pickle.HIGHEST_PROTOCOL))
        finally:
            OMFITexpressionsReturnNone = tmpExp

    def KEYS(self):
        """
        Returns list of keys within the OMFITcollection, regardless of the value of the `.selector`.
        This is equivalent to `self.keys()` when `self.selector=None`.
        """
        return self.keyOrder

    def SET(self, key, value):
        """
        Writes the `key` entry in the collection dictionary, regardless of the value of the `.selector`.
        This is equivalent to `self[key]=value` when `self.selector=None`.

        :param key: entry of the collection

        :param value: value to be given
        """
        return super().__setitem__(key, value)

    def GET(self, key):
        """
        Returns the `key` entry from the collection dictionary, regardless of the value of the `.selector`.
        This is equivalent to `self[key]` when `self.selector=None`.

        :param key: entry of the collection
        """
        return super().__getitem__(key)

    def CONTAINS(self, key):
        """
        Returns whether `key`  is in the collection dictionary, regardless of the value of the `.selector`.
        This is equivalent to key in self when `self.selector=None`.

        :param key: entry of the collection
        """
        return super().__contains__(key)

    def __contains__(self, key):
        global OMFITexpressionsReturnNone
        if OMFITexpressionsReturnNone or key in self.KEYS():
            return self.CONTAINS(key)

        elif self.selector is not None:
            return key in self.GET(self.selector)

        else:
            if not self.CONTAINS(key):
                if not len(self.KEYS()):
                    return False
                for k in self.KEYS():
                    try:
                        self.GET(k)[key]
                    except Exception:
                        return False
            return True

    def __getitem__(self, key):
        global OMFITexpressionsReturnNone
        if OMFITexpressionsReturnNone or key in self.KEYS():
            return self.GET(key)

        elif self.selector is not None:
            return self.GET(self.selector).__getitem__(key)

        else:
            is_dict = False
            for k in self.KEYS():
                try:
                    tmp = self.GET(k)[key]
                    if isinstance(tmp, (dict, xarray.Dataset)):
                        is_dict = True
                        break
                except Exception as _excp:
                    if self.raise_errors is True:
                        raise
                    elif self.raise_errors is None:
                        self._warning(k, _excp)
                    else:
                        continue

            if is_dict:
                tmp = self.__class__()
                tmp.selector = self.selector
                tmp.strategy = self.strategy
                tmp.raise_errors = self.raise_errors
                for k in self.KEYS():
                    try:
                        tmp[k] = self.GET(k)[key]
                    except Exception as _excp:
                        if self.raise_errors is True:
                            raise
                        elif self.raise_errors is None:
                            self._warning(k, _excp)
                        else:
                            continue
                return tmp
            else:
                out = specialList()
                for k in self.KEYS():
                    try:
                        out.append(self.GET(k)[key])
                    except Exception as _excp:
                        if self.raise_errors is True:
                            raise
                        elif self.raise_errors is None:
                            self._warning(k, _excp)
                        else:
                            continue

                if len(out) and is_numeric(out[0]):
                    out = np.array(out).T
                if self.strategy is None:
                    return out
                else:
                    from omfit_classes import omfit_python

                    namespace = env_from_import()
                    namespace['x'] = out
                    namespace.import_namespace = omfit_python
                    return eval(self.strategy, namespace)

    def __setitem__(self, key, value):
        global OMFITexpressionsReturnNone
        if OMFITexpressionsReturnNone or self.selector is None or key in self.KEYS():
            return self.SET(key, value)
        else:
            return self.GET(self.selector).__setitem__(key, value)

    def __getattr__(self, key):
        if key in ['__getnewargs__', '__tree_keys__']:
            raise AttributeError('bad attribute `%s`' % key)
        # print key

        global OMFITexpressionsReturnNone
        if OMFITexpressionsReturnNone or key in self.__dict__:
            return super().__getattr__(key)

        elif self.selector is not None:
            return self.GET(self.selector).__getattr__(key)

        else:
            out = specialList()
            for k in self.KEYS():
                try:
                    out.append(getattr(self.GET(k), key))
                except Exception as _excp:
                    if self.raise_errors is True:
                        raise
                    elif self.raise_errors is None:
                        self._warning(k, _excp)
                    else:
                        continue

            if len(out) and is_numeric(out[0]):
                out = np.array(out).T

            return out

    def __tree_repr__(self):
        if self.selector is None:
            strategy = 'STRATEGY:%s' % repr(self.strategy) if self.strategy != 'x' else ''
            count = '--{\t%d\t}--' % len(self) if self.selector is None else ''
            modifyOriginal = 'modifyOriginal' if hasattr(self, 'modifyOriginal') and getattr(self, 'modifyOriginal') else ''
            readOnly = 'readOnly' if hasattr(self, 'readOnly') and getattr(self, 'readOnly') else ''
            return '  '.join([count, strategy, modifyOriginal, readOnly]), []
        else:
            selector = 'SELECTOR[%s]: ' % repr(self.selector) if self.selector is not None else ''
            tmp = itemTagsValues(self.GET(self.selector))[1]
            return selector + tmp[0], tolist(tmp[1])

    def UPDATE(self, location, values, verbose=False):
        """
        Update the location of the ith key of self.KEYS() with the ith value of values

        :param location: A string indicating the the common part that will be updated
        :param values: An iterable of the same length as ``self.KEYS()``
                       or a single value to be broadcast to all keys
        :returns: ``None``

        Example::
            coll.UPDATE(location="['SAT_RULE']",values=[1]*len(coll.KEYS()))
            coll.UPDATE(location="['SAT_RULE']",values=1)
        """
        if np.size(values) == 1:
            values = [np.atleast_1d(values)[0]] * len(self.KEYS())
        if verbose:
            printi('OMFITcollection.UPDATE of "%s":' % location)
            printi('   Values (old):', eval("self" + location))
        for k, v in zip(self.KEYS(), values):
            exec("self[k]{location} = v".format(location=location))
        if verbose:
            printi('   Values (new):', eval("self" + location))


class OMFITmcTree(OMFITcollection):
    """
    A class for holding results from a Monte Carlo set of runs

    Effectively this is a `OMFITcollection` class with default strategy set to: `uarray(np.mean(x,1),np.std(x,1))`

    """

    def __init__(self, *args, **kw):
        kw.setdefault('strategy', 'np.atleast_1d(uarray(np.mean(x,-1),np.std(x,-1)))')
        OMFITcollection.__init__(self, *args, **kw)

    def get_mean_std(self, path):
        printe('WARNING: get_mean_std() will be deprecated in the future')
        tmp_list = []
        for k in self:
            try:
                eval("tmp_list.append(self[k]%s)" % path)
            except KeyError:
                continue
        tmp_array = np.array(tmp_list)
        return (tmp_array.mean(axis=0), tmp_array.std(axis=0))


class OMFITstorage(OMFITtree):
    pass


class OMFITtreeCompressed(OMFITobject):
    def __init__(self, input, **kw):
        quiet = kw.pop('quiet', False)
        if isinstance(input, str):
            OMFITobject.__init__(self, input, quiet=quiet, **kw)
        elif isinstance(input, OMFITtree):
            filename = input.__class__.__name__ + '__compressed_' + utils_base.now("%Y-%m-%d_%H_%M_%S_%f")
            OMFITobject.__init__(self, filename + '.zip', quiet=quiet, **kw)
            location = self.filename[:-4]
            input.deploy(location + os.sep + 'OMFITsave.txt', zip=True, quiet=quiet)


_moduleAttrs = ['ID', 'edited_by', 'date', 'contact', 'defaultGUI', 'commit', 'comment']


class OMFITmodule(OMFITtree):
    """
    Class for OMFIT modules

    :param filename: None: create new module from skeleton, '': create an empty module
    """

    _settings_class = OMFITsettings

    def __init__(self, filename='', modifyOriginal=False, readOnly=False, quiet=False, developerMode=False, **kw):
        # new module from skeleton
        if filename is None:
            OMFITtree.__init__(
                self,
                os.path.split(os.path.abspath(__file__))[0] + os.sep + 'skeleton' + os.sep + 'NEW_MODULE' + os.sep + 'OMFITsave.txt',
                quiet=quiet,
            )
            date = utils_base.now()
            self['SETTINGS']['MODULE']['edited_by'] = os.environ['USER']
            self['SETTINGS']['MODULE']['date'] = date
            self['SETTINGS']['MODULE']['contact'] = tolist(self['SETTINGS']['MODULE']['contact'], empty_lists=[None, ''])
            if is_email(OMFIT['MainSettings']['SETUP']['email']):
                self['SETTINGS']['MODULE']['contact'] += [OMFIT['MainSettings']['SETUP']['email']]
            self['SETTINGS']['MODULE']['python3'] = '.'.join(map(str, sys.version_info[:2]))
            self.filename = ''

        # load module from file
        elif len(filename):
            OMFITtree.__init__(
                self, filename, modifyOriginal=modifyOriginal, readOnly=readOnly, quiet=quiet, developerMode=developerMode, **kw
            )

            # update old modules so they have all required attributes
            self._check_module_attributes()

            # convert documentation
            converted_legacy_help = False
            if 'help' in self:
                if not isinstance(self['help'], OMFIThelp):
                    if os.path.split(self['help'].filename)[1] != 'help.rst':
                        converted_legacy_help = True
                    self['help'] = OMFIThelp('help.rst', fromString=self['help'].read())
            else:
                self['help'] = OMFIThelp('help.rst')
            if isinstance(self['help'], OMFIThelp) and 'version' in self['SETTINGS']['MODULE']:
                self['help'].write(self['SETTINGS']['MODULE']['version'] + '\n\n' + self['help'].read())
                del self['SETTINGS']['MODULE']['version']
                converted_legacy_help = True
            if converted_legacy_help and self['help'].read().strip():
                old_help = self['help'].read()
                self['help'].write(
                    re.sub(r'\.\. \.(\. |\.)', '.. ', '.. ' + '\n.. '.join(OMFITaux['moduleSkeletonCache']['help'].read().split('\n')))
                )
                self['help'].append(
                    '\n.. \n.. the following module documentation should be updated to comply with the schema provided above\n\n'
                )
                self['help'].append('.. code-block:: none\n\n    ' + '\n    '.join(map(encode_ascii_ignore, old_help.split('\n'))))
                printw(str(self.ID) + "['help'] is out of date -- please consider updating it --")

            # store settings at import time
            # NOTE: this is done both here and in OMFIT.loadModule because here is needed when reloading a module and the other will execute OMFITlib_startup
            self._save_settings_at_import()

        # empty module
        else:
            OMFITtree.__init__(
                self, filename, modifyOriginal=modifyOriginal, readOnly=readOnly, quiet=quiet, developerMode=developerMode, **kw
            )

        # sort objects by their class
        self.sort_class([OMFITtmp, OMFITmodule, OMFITtree, OMFITnamelist, OMFITsettings, OMFITascii, OMFITwebLink])

    def _save_settings_at_import(self):
        """
        Generate __SETTINGS_AT_IMPORT__ by freezing all OMFITexpressions under self['SETTINGS']
        """
        self.insert(self.index('SETTINGS') + 1, '__SETTINGS_AT_IMPORT__', copy.deepcopy(self['SETTINGS']))
        self['__SETTINGS_AT_IMPORT__'].__class__ = OMFITjson  # use json since places may assume that OMFITsettings is only root['SETTINGS']
        # does not make sense to store shot/time/device etc...
        if 'EXPERIMENT' in self['__SETTINGS_AT_IMPORT__']:
            del self['__SETTINGS_AT_IMPORT__']['EXPERIMENT']
        # we remove workdirs since these will always change when reloading a module
        if 'SETUP' in self['__SETTINGS_AT_IMPORT__'] and 'workDir' in self['__SETTINGS_AT_IMPORT__']['SETUP']:
            del self['__SETTINGS_AT_IMPORT__']['SETUP']['workDir']
        if 'REMOTE_SETUP' in self['__SETTINGS_AT_IMPORT__'] and 'workDir' in self['__SETTINGS_AT_IMPORT__']['REMOTE_SETUP']:
            del self['__SETTINGS_AT_IMPORT__']['REMOTE_SETUP']['workDir']
        # remove dependencies (these sometimes have expressions that are used to dynamically load modules!)
        if 'DEPENDENCIES' in self['__SETTINGS_AT_IMPORT__']:
            del self['__SETTINGS_AT_IMPORT__']['DEPENDENCIES']
        # remove all expressions
        freezeExpr(self['__SETTINGS_AT_IMPORT__'], remove_OMFITexpressionError=True)

    def _get_module_attribute(self, attr):
        """
        This function gets the attribute and sets it from the MODULES skeleton, if the attribute is missing
        Setting from the skeleton is not done if OMFITexpressionsReturnNone is True, which occurs when exporting/saving modules

        :param attr: attribute to get

        :return: value of the attribute
        """
        if 'SETTINGS' not in self:
            self['SETTINGS'] = OMFITaux['moduleSkeletonCache']['SETTINGS'].duplicate()
        if 'MODULE' not in self['SETTINGS']:
            self['SETTINGS']['MODULE'] = SortedDict()
        if not isinstance(self['SETTINGS'], self._settings_class):
            self['SETTINGS'].__class__ = self._settings_class
        if attr not in self['SETTINGS']['MODULE']:
            return self._set_module_attribute(attr, copy.deepcopy(OMFITaux['moduleSkeletonCache']['SETTINGS']['MODULE'][attr]))
        return self['SETTINGS']['MODULE'][attr]

    def _check_module_attributes(self):
        for item in _moduleAttrs:
            setattr(self, item, getattr(self, item))

    def _set_module_attribute(self, attr, value):
        """
        This function is used to sets the attribute, unless OMFITexpressionsReturnNone is True, which occurs when exporting/saving modules

        :param attr: attribute to set

        :param value: value to set the attribute to

        :return: value of the attribute
        """
        if 'MODULE' not in self['SETTINGS']:
            self['SETTINGS']['MODULE'] = SortedDict()
        global OMFITexpressionsReturnNone
        if not OMFITexpressionsReturnNone:
            self['SETTINGS']['MODULE'][attr] = value
        return value

    @property
    def settings_class(self):
        return self._settings_class

    @settings_class.setter
    def settings_class(self, value):
        tmp = self['SETTINGS']
        try:
            self['SETTINGS'] = value('SettingsNamelist.txt')
            self['SETTINGS'].update(tmp)
            self['SETTINGS'].save()
            self._settings_class = value
        except Exception as _excp:
            printe(repr(_excp))
            self['SETTINGS'] = tmp

    @property
    def ID(self):
        return self._get_module_attribute('ID')

    @ID.setter
    def ID(self, value):
        return self._set_module_attribute('ID', value)

    @property
    def edited_by(self):
        return self._get_module_attribute('edited_by')

    @edited_by.setter
    def edited_by(self, value):
        return self._set_module_attribute('edited_by', value)

    @property
    def date(self):
        return self._get_module_attribute('date')

    @date.setter
    def date(self, value):
        return self._set_module_attribute('date', value)

    @property
    def description(self):
        return self['help'].txt()

    @property
    def contact(self):
        # make sure contacts is a list
        return tolist(self._get_module_attribute('contact'), empty_lists=[None, ''])

    @contact.setter
    def contact(self, value):
        return tolist(self._set_module_attribute('contact', value), empty_lists=[None, ''])

    @property
    def defaultGUI(self):
        return self._get_module_attribute('defaultGUI')

    @defaultGUI.setter
    def defaultGUI(self, value):
        return self._set_module_attribute('defaultGUI', value)

    @property
    def commit(self):
        return self._get_module_attribute('commit')

    @commit.setter
    def commit(self, value):
        return self._set_module_attribute('commit', value)

    @property
    def comment(self):
        return self._get_module_attribute('comment')

    @comment.setter
    def comment(self, value):
        return self._set_module_attribute('comment', value)

    def moduleDict(self, onlyModuleID=None, level=-1):
        """
        Returns a dictionary of currently loaded modules

        :param onlyModuleID: string or list of strings of module ID to search for

        :param level: how many modules deep to go

        The dictionary contains the modules settings for each of the modules
        """
        return self._moduleDict(onlyModuleID=onlyModuleID, level=level)

    def _storeDecorator(f):
        """
        Decorator which calls `storage` methods
        """

        @functools.wraps(f)
        def decoratedStorage(self, *args, **kw):
            if not len(args):
                args = [None]
            args = list(args)
            if 'runid' in kw:
                args = [kw.pop('runid')]
            runid = args[0]
            if runid is None:
                runid = self['SETTINGS']['EXPERIMENT']['runid']
            modID = self['SETTINGS']['MODULE']['ID']
            if not isinstance(runid, str):
                raise OMFITexception(f.__name__ + ': Need to specify a runid for module ' + str(modID))
            if '__STORAGE__' not in self:
                self['__STORAGE__'] = OMFITstorage()
            printi(f.__name__[:-1] + 'ing ' + str(modID) + ' runid ' + runid + ' ...')
            args[0] = runid
            try:
                old_runid = self['SETTINGS']['EXPERIMENT']['runid']
                self['SETTINGS']['EXPERIMENT']['runid'] = runid
                tmp = f(self, *args, **kw)
            finally:
                self['SETTINGS']['EXPERIMENT']['runid'] = old_runid
            return tmp

        return decoratedStorage

    @_storeDecorator
    def store(self, runid, metadata={}):
        """
        Method to store a snapshot of the current module status and save it under self['__STORAGE__'][runid]
        where runid is set under self['SETTINGS']['EXPERIMENT']['runid']

        :param runid: runid to be de-stored. If None the runid is taken from self['SETTINGS']['EXPERIMENT']['runid']
        """
        self['SETTINGS']['EXPERIMENT']['runid'] = runid
        tmp = OMFITtreeCompressed(self, quiet=True)
        self['__STORAGE__'][runid] = OMFITtree()
        self['__STORAGE__'][runid]['comment'] = self['SETTINGS']['EXPERIMENT'].setdefault('comment', '')
        self['__STORAGE__'][runid].update(metadata)
        self['__STORAGE__'][runid]['data'] = tmp
        self['__STORAGE__'].setdefault('__restoreScripts__', False)

    @_storeDecorator
    def restore(self, runid, restoreScripts=None):
        """
        Method to restore a snapshot of the current module status as it was saved under self['__STORAGE__'][runid]

        :param runid: runid to be restored. If None the runid is taken from self['SETTINGS']['EXPERIMENT']['runid']
        """
        tmp = OMFITtree(self['__STORAGE__'][runid]['data'].filename, quiet=True)

        if restoreScripts is None:
            restoreScripts = self['__STORAGE__'].setdefault('__restoreScripts__', False)
        if not restoreScripts:

            def f_traverse(me, myLocation='', scriptDict={}):
                if isinstance(me, dict):
                    for kid in list(me.keys()):
                        kidName = "[" + repr(kid) + "]"
                        entryID = myLocation + kidName
                        if isinstance(me[kid], OMFITtree):
                            f_traverse(me[kid], entryID, scriptDict)
                        if isinstance(me[kid], _OMFITpython):
                            scriptDict[entryID] = me[kid]
                return scriptDict

            currentScriptDict = f_traverse(self, 'self', {})
            restoreScriptDict = f_traverse(tmp, 'self', {})

        storage = self['__STORAGE__']
        self.clear()
        self.update(tmp)
        self['__STORAGE__'] = storage

        if not restoreScripts:
            for item in list(restoreScriptDict.keys()):
                del eval(buildLocation(parseLocation(item)[:-1]))[parseLocation(item)[-1]]

            for item in list(currentScriptDict.keys()):
                tmp.addBranchPath(item)
                eval(buildLocation(parseLocation(item)[:-1]))[parseLocation(item)[-1]] = currentScriptDict[item]

    @_storeDecorator
    def destore(self, runid):
        """
        Method to de-store a snapshot of the current module status as it was saved under self['__STORAGE__'][runid]

        :param runid: runid to be de-stored. If None the runid is taken from self['SETTINGS']['EXPERIMENT']['runid']
        """
        del self['__STORAGE__'][runid]

    @staticmethod
    def info(filename):
        """
        This (static) method returns a dictionary with the module information, including the content of the ['help'] file

        :param filename: module filename

        :return: dictionary with module info
        """
        with open(filename, 'r') as f:
            lines = f.readlines()
        settings = {}
        subs = []
        help = None
        catchSubmodule = False
        for line in lines:
            if catchSubmodule:
                for ll in lines:
                    if catchSubmodule + "['SETTINGS'] <-:-:->" in ll and (
                        " <-:-:-> OMFITsettings <-:-:-> ./" in line or " <-:-:-> OMFITnamelist <-:-:-> ./" in line
                    ):
                        tmp = os.path.split(filename)[0] + os.sep + ll.split(' <-:-:-> ')[2]
                        try:
                            subs.append(OMFITsettings(tmp, modifyOriginal=True)['MODULE']['ID'])
                        except Exception as _excp:
                            printe('Error loading dependency info (%s): %s' % (tmp, repr(_excp)))
                        break
                catchSubmodule = False
            elif " <-:-:-> OMFITmodule <-:-:->" in line:
                catchSubmodule = line.split(' <-:-:-> ')[0]
                continue
            elif line.startswith("['SETTINGS'] <-:-:-> OMFITsettings <-:-:-> ./") or line.startswith(
                "['SETTINGS'] <-:-:-> OMFITnamelist <-:-:-> ./"
            ):
                tmp = os.path.split(filename)[0] + os.sep + line.split(' <-:-:-> ')[2]
                try:
                    settings.update(OMFITsettings(tmp, modifyOriginal=True, readOnly=True)['MODULE'])
                except Exception as _excp:
                    printe('Error loading module info (%s): %s' % (tmp, repr(_excp)))
            elif line.startswith("['help'] <-:-:-> OMFIThelp <-:-:-> ./"):
                tmp = os.path.split(filename)[0] + os.sep + line.split(' <-:-:-> ')[2]
                try:
                    help = OMFITascii(tmp, modifyOriginal=True).read()
                except Exception as _excp:
                    printw('Error loading module help.rst (%s): %s' % (tmp, repr(_excp)))
            if help is not None and len(settings):
                break
        if len(settings):
            # convert old date format to new one
            if 'date' in settings and '/' in settings['date']:
                settings['date'] = utils_base.convertDateFormat(settings['date'], '%d/%m/%Y %H:%M')
            # set module description in `version`
            if help is not None:
                settings['description'] = help
            else:
                settings['description'] = ''
            # add modules submodules info
            settings['submodules'] = np.unique(subs).tolist()
            # add status info
            settings.setdefault('status', '')
        return settings

    @staticmethod
    def directories(return_associated_git_branch=False, separator=None, checkIsWriteable=False, directories=None):
        """
        return lists of valid modules paths

        :param return_associated_git_branch: whether to return just the path of each directory or also the remote/branch info.
                                             This requires parsing of the OMFIT modules in a directory and it can be quite slow,
                                             however the info is buffered, so later accesses are faster.

        :param separator: text to use to separate the path and the remote/branch info

        :param checkIsWriteable: checks if user has write access.
                                 Note: if checkIsWriteable='git' will return a directory even if it is not writable, but it is a git repository

        :param directories: list of directories to check. If None the list of directories is taken from OMFIT['MainSettings']['SETUP']['modulesDir']

        :return: list of valid modules directories
        """

        # make sure that OMFITsrc/../modules is always there and is the first option
        if directories is None:
            directories = tolist(evalExpr(OMFIT['MainSettings']['SETUP']['modulesDir']))
            if not checkIsWriteable or checkIsWriteable == 'git' or not os.path.exists(os.sep.join([OMFITsrc, '..', 'public'])):
                directories.insert(0, os.sep.join([OMFITsrc, '..', 'modules']))
            if 'lastModulesDir' in OMFITaux:
                directories.insert(0, OMFITaux['lastModulesDir'])
        else:
            directories = tolist(directories)
        directories = list(map(os.path.abspath, directories))
        directories = list(map(os.path.realpath, directories))

        if not os.path.exists(os.path.abspath(os.environ['HOME'] + os.sep + 'OMFITdata' + os.sep + 'modules') + os.sep):
            try:
                os.makedirs(os.path.abspath(os.environ['HOME'] + os.sep + 'OMFITdata' + os.sep + 'modules') + os.sep)
            except Exception as _excp:
                printe(
                    'Error creating directory %s: %s'
                    % (os.path.abspath(os.environ['HOME'] + os.sep + 'OMFITdata' + os.sep + 'modules') + os.sep, repr(_excp))
                )

        # remove invalid paths and duplicates (while keeping order)
        validPaths = []
        for item in directories:

            is_git_repo = True
            try:
                repo = OMFITgit(item)
            except Exception:
                if item.endswith('modules'):
                    try:
                        repo = OMFITgit(item + os.sep + '..')
                    except Exception:
                        is_git_repo = False

            if item.endswith('modules'):
                is_public = os.path.exists(os.sep.join([item, '..', 'public']))
            else:
                is_public = os.path.exists(os.sep.join([item, 'public']))

            if not os.path.exists(item):
                printd('Modules directory does not exist: %s' % item)
            elif not os.access(item, os.R_OK):
                printd('No read permission to modules directory: %s' % item)
            elif checkIsWriteable and is_public and not (is_git_repo and checkIsWriteable == 'git'):
                printd('No write permission to modules directory of public installation: %s' % item)
            elif checkIsWriteable and not os.access(item, os.W_OK) and not (is_git_repo and checkIsWriteable == 'git'):
                printd('No write permission to modules directory: %s' % item)
            elif item not in validPaths:
                validPaths.append(item)

        # add branch info
        if return_associated_git_branch:

            for k, item in enumerate(validPaths):

                directory = validPaths[k]

                cases_errors = []
                cases = []
                if os.path.split(directory)[1] == 'modules':
                    cases.append([os.path.split(directory)[0], 'modules'])
                cases.append([directory, ''])

                for repo_dir, modules_subpath in cases:
                    try:
                        # try to access as a git repository
                        repo = OMFITgit(repo_dir)
                        commit = repo("log -1 --pretty='%H'")
                        branch = repo('rev-parse --abbrev-ref HEAD')
                        remote = repo.get_branches().get(branch, {'remote': ''})['remote']

                        validPaths[k] = (directory, remote + '/' + branch)
                        if separator:
                            validPaths[k] = validPaths[k][0] + separator + validPaths[k][1]

                        break

                    except Exception as _excp:
                        pass

        return validPaths

    @staticmethod
    def submodules(go_deep=True, directory=None):
        """
        This (static) method returns a dictionary with the list of submodules for each of the modules in a directory

        :param go_deep: include submodules of submodules

        :param directory: modules directory to use, by default the one of the repository where OMFIT is running

        :return: dictionary with submodule info for all modules in a directory
        """
        if directory is None:
            directory = OMFITmodule.directories()[0]

        availableModulesList = OMFIT.availableModules(quiet=True, directories=tolist(directory))

        submodules = {module['ID']: module['submodules'] for filename, module in availableModulesList.items()}

        while go_deep:
            go_deep = False
            for mod in submodules:
                for submod in submodules[mod]:
                    for subsubmod in submodules[submod]:
                        if subsubmod not in submodules[mod]:
                            submodules[mod].append(subsubmod)
                            go_deep = True

        return submodules

    def __delitem__(self, key):
        super().__delitem__(key)
        # cannot delete __scratch__
        if key == '__scratch__':
            self.insert(0, '__scratch__', OMFITtmp())

    def __tree_repr__(self):
        if 'MODULE' not in self['SETTINGS'] or 'COMMENT' not in self['SETTINGS']['MODULE'] or not self.comment:
            return -1, []
        else:
            return '--- ' + self.comment + ' ' + '-' * 300, []

    def saveUserSettings(self, variant='__default__', locations=["['PHYSICS']"]):
        """
        Save user settings in ~/.OMFIT/modulesSettings/

        :param variant: variant name of the user setting to save

        :param locations: by default only save ['PHYSICS']
        """
        if self.ID is None:
            raise OMFITexception('Module ID must be set to save the module settings')
        filename = os.sep.join([_f for _f in [os.environ['HOME'], '.OMFIT', 'modulesSettings', self.ID] + [variant, 'OMFITsave.txt'] if _f])
        tmp = copy.deepcopy(self['SETTINGS'])
        tmp = prune_mask(tmp, locations)
        try:
            orig = self['SETTINGS']
            self['SETTINGS'] = tmp
            self._save(filename=filename, only="['SETTINGS']", quiet=True)
        finally:
            self['SETTINGS'] = orig
        printi('Saved user settings for module %s%s' % (self.ID, [' variant ' + variant, ''][variant == '__default__']))

    def loadUserSettings(self, variant='__default__', diff=False):
        """
        Load user settings in ~/.OMFIT/modulesSettings/

        :param variant: variant name of the user setting to load

        :param diff: open a diff GUI to let users choose what to merge
        """
        if self.ID is None:
            raise OMFITexception('Module ID must be set to load the module settings')
        filename = os.sep.join([_f for _f in [os.environ['HOME'], '.OMFIT', 'modulesSettings', self.ID] + [variant, 'OMFITsave.txt'] if _f])
        if not os.path.exists(filename):
            printi('User settings for module %s%s not found' % (self.ID, [' variant ' + variant, ''][variant == '__default__']))
            return
        tmp = OMFITtree(filename, quiet=True)
        if not diff:
            self['SETTINGS'].recursiveUpdate(tmp['SETTINGS'], overwrite=True)
        else:
            tmp['SETTINGS'].recursiveUpdate(self['SETTINGS'], overwrite=False)
            diffTreeGUI(self['SETTINGS'], tmp['SETTINGS'])
        printi('Loaded user settings for module %s%s' % (self.ID, [' variant ' + variant, ''][variant == '__default__']))

    def listUserSettings(self, verbose=False):
        """
        List user settings in ~/.OMFIT/modulesSettings/
        """
        if self.ID is None:
            raise OMFITexception('Module ID must be set to load the module settings')
        filename = os.sep.join([_f for _f in [os.environ['HOME'], '.OMFIT', 'modulesSettings', self.ID] if _f])
        variants = []
        for item in glob.glob(filename + os.sep + '*' + os.sep + 'OMFITsave.txt'):
            variants.append(os.path.split(os.path.split(item)[0])[1])
        if verbose:
            printi('Users settings variants: %s' % variants)
        return variants

    def deleteUserSettings(self, variant='__default__'):
        """
        Delete user settings in ~/.OMFIT/modulesSettings/

        :param variant: variant name of the user setting to delete
        """
        if self.ID is None:
            raise OMFITexception('Module ID must be set to load the module settings')
        filename = os.sep.join([_f for _f in [os.environ['HOME'], '.OMFIT', 'modulesSettings', self.ID] + [variant] if _f])
        if not os.path.exists(filename):
            printi('User settings for module %s%s not found' % (self.ID, [' variant ' + variant, ''][variant == '__default__']))
        else:
            printi('Deleted user settings for module %s%s' % (self.ID, [' variant ' + variant, ''][variant == '__default__']))
            shutil.rmtree(filename)

    def experiment_location(self, *args):
        r"""
        Method that resolves the OMFITexpressions that are found in a module
        root['SETTINGS']['EXPERIMENT'] and returns the location that
        those expressions points to.

        :params \*args: list of keys to return the absolute location of

        :returns: dictionary with the absolute location the expressions point to
        """

        rootName = treeLocation(self)[-1]
        root = eval(rootName)

        for item in args:
            if item not in root['SETTINGS']['EXPERIMENT']:
                raise AttributeError("%s is not in %s['SETTINGS']['EXPERIMENT']" % (item, rootName))

        tmp = parseLocation(rootName)
        OMFITlocationName = [buildLocation(tmp[: k + 1]) for k, item in enumerate(tmp)]

        OMFITmodulesName = []
        for tmpName in OMFITlocationName:
            if eval(tmpName).__class__ is OMFITmodule and tmpName != 'OMFIT':
                OMFITmodulesName.append(tmpName)
        OMFITmodules = list(map(eval, OMFITmodulesName))

        locations = {}
        for item in args:
            locations[item] = rootName + "['SETTINGS']['EXPERIMENT']"
            for moduleName in reversed(OMFITmodulesName):
                if not isinstance(eval(moduleName)['SETTINGS']['EXPERIMENT'][item], OMFITexpression):
                    locations[item] = moduleName + "['SETTINGS']['EXPERIMENT']"
                    break
            if isinstance(eval(moduleName)['SETTINGS']['EXPERIMENT'][item], OMFITexpression):
                locations[item] = "OMFIT['MainSettings']['EXPERIMENT']"
        return locations

    def experiment(self, *args, **kw):
        r"""
        method used to set the value of the entries under root['SETTINGS']['EXPERIMENT']
        This method resolves the OMFITexpressions that are found in a module
        root['SETTINGS']['EXPERIMENT'] and sets the value at the location
        that those expressions points to.

        :params \**kw: keyword arguments with the values to be set

        :returns: root['SETTINGS']['EXPERIMENT']
        """
        locations = self.experiment_location(*list(kw.keys()))
        for item in list(locations.keys()):
            # Don't allow 0-D np arrays
            if isinstance(kw[item], np.ndarray) and len(kw[item].shape) == 0:
                kw[item] = np.atleast_1d(kw[item])
            eval(locations[item])[item] = evalExpr(kw[item])
        return self['SETTINGS']['EXPERIMENT']

    def deploy_module(self, *args, **kw):
        r"""
        Method used to deploy a module in its format for being stored as part of a modules repository

        :param \*args: arguments passed to the deploy method

        :param \**kw: keywords arguments passed to the deploy method

        """
        try:
            tmp = self['SETTINGS']['EXPERIMENT']
        except Exception:
            raise
        else:
            # Always export EXPERIMENT settings that are in MainSettings as OMFITexpressions
            for item in list(OMFIT['MainSettings']['EXPERIMENT'].keys()):
                if item in self['SETTINGS']['EXPERIMENT']:
                    self['SETTINGS']['EXPERIMENT'][item] = OMFITexpression(
                        '''try:\n    return_variable=OMFITmodules[-2]['SETTINGS']['EXPERIMENT']['{}']\nexcept Exception:\n    return_variable=MainSettings['EXPERIMENT']['{}']\n'''.format(
                            item, item
                        )
                    )
            # do not store these info
            for item in ['commit', 'edited_by', 'date', 'comment']:
                if item in self['SETTINGS']['MODULE']:
                    del self['SETTINGS']['MODULE'][item]
            # make sure contacts are list
            if 'contact' in self['SETTINGS']['MODULE'] and self['SETTINGS']['MODULE']['contact'] is not None:
                self['SETTINGS']['MODULE']['contact'] = [str(k).strip('\'"') for k in tolist(self['SETTINGS']['MODULE']['contact'])]
            else:
                self['SETTINGS']['MODULE']['contact'] = []
            self.deploy(*args, **kw)
        finally:
            self['SETTINGS']['EXPERIMENT'] = tmp

    def convert_to_developer_mode(
        self,
        processSubmodules=True,
        modulesDir=os.path.abspath(OMFITsrc + os.sep + '..' + os.sep + 'modules'),
        operation='DEVEL',
        loadNewSettings=True,
        quiet=False,
    ):
        """
        Convert scripts in this module to be modifyOriginal versions of the scripts under the moduleDir
        (so called `developer mode`)

        :param processSubmodules: bool
            convert scripts in the submodules

        :param modulesDir: string
            modules directory to use

        :param operation: string
            One of ['DEVEL', 'RELOAD', 'FREEZE']
            DEVEL: reload scripts with modifyOriginal = True
            RELOAD: reload scripts with modifyOriginal = False
            FREEZE: set modifyOriginal = False

        :param loadNewSettings: bool
            Load new entries in the modules settings or not
            (ignored if operation=='FREEZE')

        :param quiet: bool
            Suppress print statements
        """
        if operation == 'FREEZE':
            loadNewSettings = False

        # options
        options = SortedDict()
        options['Developer mode'] = 'DEVEL'
        options['Non-developer mode (RELOAD)'] = 'RELOAD'
        options['Non-developer mode (FREEZE)'] = 'FREEZE'
        valueOptions = flip_values_and_keys(options)

        # Identify modules
        if processSubmodules:
            modules = traverse(self, onlyDict=(OMFITmodule,), skipDynaLoad=True, noSubmodules=False)
            if modules != ['']:
                modules = [''] + modules
        else:
            modules = ['']
        printd('convert_to_developer_mode: {} modules = {}'.format(valueOptions[operation], modules))

        # Loop over modules
        for module in modules:
            module_location = buildLocation(['self'] + parseLocation(module)[1:])
            module_name = eval(module_location)['SETTINGS']['MODULE']['ID']

            # Find _OMFITpython scripts as efficiently as possible
            locations = traverse(
                eval(module_location), onlyDict=(OMFITtree,), onlyLeaf=(_OMFITpython, OMFITsettings), skipDynaLoad=True, noSubmodules=True
            )

            if not quiet:
                printi(valueOptions[operation] + ' under ' + self['SETTINGS']['MODULE']['ID'] + module_location[4:])

            # Also module help as modifyOriginal
            if 'help' in eval(module_location):
                locations.append("['help']")

            # Parse the relative OMFITsave.txt file for the module
            try:
                with open(modulesDir + os.sep + module_name + os.sep + 'OMFITsave.txt', 'r') as f:
                    lines = f.readlines()
            except IOError as _excp_:
                printe(modulesDir + os.sep + module_name + os.sep + 'OMFITsave.txt')
                printe(repr(_excp_))
                continue

            # For each script
            for item in locations:
                if isinstance(eval(module_location + item), _OMFITpython) or (
                    loadNewSettings and isinstance(eval(module_location + item), OMFITsettings)
                ):

                    # Find corresponding filename
                    filename = None
                    if operation == 'FREEZE':
                        filename = eval(module_location + item).filename
                    else:
                        for line in lines:
                            if line.startswith(item):
                                filename = line.split(' <-:-:-> ')[2]
                                if not filename.startswith(os.sep):
                                    filename = os.path.abspath(modulesDir + os.sep + module_name + os.sep + filename)
                                break
                    if filename is None:
                        printi('skipped ' + item)
                        continue

                    # copy used later for updating settings
                    backup = eval(module_location + item)

                    # Reload script and set modifyOriginal accordingly
                    try:
                        eval(buildLocation(parseLocation(module_location + item)[:-1]))[parseLocation(item)[-1]] = eval(
                            module_location + item
                        ).__class__(
                            filename, modifyOriginal=((operation == 'DEVEL') and isinstance(eval(module_location + item), _OMFITpython))
                        )
                        if not quiet:
                            printi(item.ljust(max([len(x) for x in locations])), filename)
                    except Exception as _excp_:
                        printe(repr(_excp_))
                        continue

                    # allow new settings
                    if loadNewSettings and isinstance(eval(module_location + item), OMFITsettings):
                        eval(module_location + item).recursiveUpdate(backup, overwrite=True)


class OMFIThelp(OMFITascii, SortedDict):
    """
    Class used to parse OMFIT modules help.rst files
    """

    def __init__(self, filename, **kw):
        OMFITascii.__init__(self, filename, **kw)
        SortedDict.__init__(self)
        self.dynaLoad = True

    @dynaLoad
    def load(self):
        with open(self.filename, 'r') as f:
            hlp = f.read()

        # parse module help as manually written
        sections = re.sub('\n?(.*)\n-+', r'\n>->-> \1 <-<-<', hlp)
        sections = sections.split('>->->')
        sections = [_f for _f in [x.strip() for x in sections] if _f]
        section2 = SortedDict()
        for section in sections:
            sec_split = [x.strip() for x in section.split('<-<-<')]
            if len(sec_split) > 1:
                section2[sec_split[0]] = sec_split[1]
            else:
                section2[''] = sec_split[0]
        self.update(section2)

    def verify(self):
        invalid = f"* `{os.path.split(self.filename)[1]}` module is an invalid OMFIT module help format"
        for section in ['Short Description', 'Keywords']:
            if section not in self:
                raise ValueError(invalid + f'\n  {section} should always be there')
            self[section] = self[section].strip().strip('\n').strip('.')
            if '\n' in self[section]:
                raise ValueError(invalid + f'\n  {section} should be on one line')

    @dynaSave
    def save(self):
        try:
            self.verify()
        except ValueError as _excp:
            printe(_excp)
            printe('  Your changes to this file (if any) have not been saved!')
            return self._save_by_copy()
        else:
            with open(self.filename, 'w') as f:
                f.write(self.txt())

    def txt(self):
        return '\n\n'.join(['%s\n%s\n%s' % (section, '-' * len(section), self[section]) for section in self]) + '\n'


def ismodule(module, module_ids):
    """
    convenience function to check if an OMFITmodule is one of a given set of IDs

    :param module: module

    :param module_ids: list of module IDs to check for

    :return: True if the module ID matches one of the IDs in the module_ids list
    """
    module_ids = tolist(module_ids)
    for module_id in module_ids:
        if isinstance(module, OMFITmodule) and module.ID == module_id:
            return True
    return False


class OMFITtmp(SortedDict, _OMFITnoSave):
    """
    Same class of SortedDict, but is not saved when a project is saved
    This class is used to define the __scratch__ space under each module as well as the global OMFIT['scratch']
    """

    pass


class OMFITproject(OMFITtree):
    """Similar to OMFITtree class"""

    def __init__(self, filename='', **kw):
        OMFITtree.__init__(self, filename, **kw)
        if 'scratch' not in self:
            self['scratch'] = OMFITtmp()

    def moduleDict(self, onlyModuleID=None, level=-1):
        """
        Returns a dictionary of currently loaded modules

        :param onlyModuleID: string or list of strings of module ID to search for

        :param level: how many modules deep to go

        The dictionary contains the modules settings for each of the modules
        """
        return self._moduleDict(onlyModuleID=onlyModuleID, level=level)

    @staticmethod
    def info(filename=''):
        """
        Returns dictionary with the saved project information.

        :param filename: filename of the project to return info about.
                         If filename='' then returns info about the current project.
                         Note that projects information are updated only when the project is saved.

        :return: dictionary with project infos
        """

        if not filename:
            filename = OMFIT.filename

        if not filename:
            raise Exception('Must specify a filename')

        return_dict = {}

        if zipfile.is_zipfile(filename):
            omfitsavetxt = 'OMFITsave.txt'
            myzipfile = zipfile.ZipFile(filename, 'r', allowZip64=True)
            deflate_dir = OMFITcwd + os.sep + 'projects_preview' + os.sep
            if not os.path.exists(deflate_dir):
                os.makedirs(deflate_dir)
            infos = myzipfile.infolist()
            files = list([x.filename for x in infos])
            projectName = os.path.commonprefix(files)
            myzipfile.extract(projectName + 'OMFITsave.txt', deflate_dir)
            myzipfile.extract(projectName + 'MainSettingsNamelist.txt', deflate_dir)
            isZip = True
        else:
            deflate_dir, omfitsavetxt = os.path.split(filename)
            projectName = os.path.split(deflate_dir)[1] + os.sep
            deflate_dir = os.path.split(deflate_dir)[0]
            isZip = False

        # OMFITsave
        with open(deflate_dir + os.sep + projectName + omfitsavetxt, 'r') as f:
            lines = f.readlines()

        # MainSettings
        return_dict['device'] = []
        return_dict['shot'] = []
        return_dict['time'] = []
        return_dict['MainSettings'] = namelist.NamelistFile(deflate_dir + os.sep + projectName + 'MainSettingsNamelist.txt')
        for k in ['device', 'shot', 'shots', 'time', 'times']:
            try:
                return_dict[k.rstrip('s')].extend(tolist(return_dict['MainSettings']['EXPERIMENT'][k]))
            except Exception:
                pass
        for k in ['device', 'shot', 'time']:
            return_dict[k] = np.unique([_f for _f in return_dict[k] if _f]).tolist()

        # get modules
        module_sep = " <-:-:-> OMFITmodule <-:-:-> "
        module_location = []
        return_dict['modules'] = OrderedDict()
        for line in lines:
            if module_sep in line:
                module_location.append(line.split('<-:-:->')[0].strip())
                return_dict['modules'][module_location[-1]] = ''
            if module_location and f"{module_location[-1]}['SETTINGS'] <-:-:->" in line:
                filename = line.split('<-:-:->')[2].strip().replace('./', '')
                if isZip:
                    myzipfile.extract(projectName + filename, deflate_dir)
                settings = OMFITsettings(deflate_dir + os.sep + projectName + filename)
                return_dict['modules'][module_location[-1]] = settings
                module_location.pop()

        # get notes, etc... (things are a bit clumsy here for backward compatibility)
        guisav = None
        for whereSave in ['__GUISAVE__', '__COMMANDBOX__']:
            guisav_sep = "['%s'] <-:-:-> pickle <-:-:-> " % whereSave
            for line in lines[::-1]:
                if line.startswith(guisav_sep):
                    guisav = line.split(' <-:-:-> ')[2]
            if guisav is not None:
                break
        if guisav is not None:
            if isZip:
                myzipfile.extract(projectName + guisav[2:], deflate_dir)
            tmp = OMFITpickle(deflate_dir + os.sep + projectName + guisav[2:])
            if isinstance(tmp, str):  # -------------------------------------------------v0
                return_dict['commands'] = tmp
            elif isinstance(tmp, dict):  # -----------------------------------------------------v3 and final
                for item in tmp:
                    if item not in return_dict:
                        return_dict[item] = tmp[item]
            elif isinstance(tmp, tuple) and len(tmp) == 2:  # ------------------------------------v1
                return_dict['notes'], return_dict['commands'] = tmp
            elif isinstance(tmp, tuple) and len(tmp) == 3:  # ------------------------------------v2
                return_dict['notes'], return_dict['commands'], return_dict['console'] = tmp

        return_dict.setdefault('persistent_projectID', False)
        for item in OMFIT.prj_options_choices:
            return_dict.setdefault(item, '')

        if return_dict['color'] not in list(OMFIT.prj_options_choices['color'].keys()):
            return_dict['color'] = ''
        if return_dict['type'] not in OMFIT.prj_options_choices['type']:
            return_dict['type'] = ''

        return return_dict


class shotBookmarks(namelist.NamelistFile, _OMFITnoSave):
    def __init__(self, filename):
        if not os.path.exists(os.path.split(filename)[0]):
            os.makedirs(os.path.split(filename)[0])
        if not os.path.exists(filename):
            with open(filename, 'w') as f:
                pass
        self.filename = filename
        namelist.NamelistFile.__init__(self, filename)

    @dynaLoad
    def load(self, *args, **kw):
        namelist.NamelistFile.load(self, self.filename, *args, **kw)
        updated = False
        for device in list(self.keys()):
            for shot in list(self[device].keys()):
                if 'description' not in self[device][shot]:
                    continue
                description = self[device][shot]['description']
                del self[device][shot]['description']
                if 'times' not in self[device][shot]:
                    continue
                times = list(map(str, tolist(self[device][shot]['times'])))
                del self[device][shot]['times']
                for time in times:
                    self[device][shot][time] = description
                updated = True
        if updated:
            self.save()


OMFITshotBookmarks = shotBookmarks(OMFITsettingsDir + os.sep + 'OMFITshotBookmarks.txt')


class OMFITmainSettings(OMFITnamelist):
    """Contains system wide settings"""

    def __init__(self, filename=None):
        super().__init__(filename, noCopyToCWD=True)

    def load(self, *args, **kw):
        # load the namelist
        super().load()
        # sort keys
        self.sort()
        # make sure 'shots' and 'times' are lists
        if 'EXPERIMENT' in self:
            for item in ['shots', 'times']:
                if item in self['EXPERIMENT']:
                    if self['EXPERIMENT'][item] is None:
                        self['EXPERIMENT'][item] = []
                    elif isinstance(self['EXPERIMENT'][item], (int, float)):
                        self['EXPERIMENT'][item] = [self['EXPERIMENT'][item]]

    def sort(self):
        if 'SERVER' in self:
            self['SERVER'].sort()
            self['SERVER'].sort_class([dict])
            self['SERVER'].sort(reverse=True, key=lambda x: x.endswith('_username'))

    def __tree_repr__(self):
        if id(self) == id(OMFIT['MainSettings']):
            return -1, ['MainSettings']
        else:
            return super().__tree_repr__()


class OMFITlazyLoad:
    """
    OMFIT class that imports xarray datasets with dynamic loading
    """

    def __init__(self, location, tp, filename, tree_repr=None, **kw):
        self.location = location
        self.tp = tp
        self.filename = os.path.abspath(filename)
        self.link = self.filename
        self.tree_repr = tree_repr
        self.kw = kw
        self.__loaded__ = special1
        self.dynaLoad = True

    def __lazy_load__(self, verbose=True):
        if self.__loaded__ is special1:
            self.dynaLoad = False
            if isinstance(verbose, str):
                printi('LazyLoad [%s]: %s' % (verbose, self.location))
            elif verbose:
                printi('LazyLoad: %s' % self.location)
            # location = parseLocation(treeLocation(self)[-1]) # need to fix OMFITlist before switching to this on
            location = parseLocation(self.location)
            eval(buildLocation(location[:-1]))[location[-1]] = self.__loaded__ = eval(self.tp)(self.filename, **self.kw)
        return self.__loaded__

    def __getattr__(self, attr):
        if attr in ['modifyOriginal', 'readOnly']:
            if attr in self.kw:
                return self.kw[attr]
            else:
                raise AttributeError('bad attribute `%s`' % attr)
        tmp = self.__lazy_load__()
        return getattr(tmp, attr)

    def __tree_repr__(self):
        if self.tree_repr:
            return [tree_repr, []]
        else:
            return [self.cls, []]

    def __iter__(self):
        tmp = self.__lazy_load__()
        return tmp.__iter__()

    def __getitem__(self, key):
        tmp = self.__lazy_load__(key)
        return tmp[key]

    def __deepcopy__(self, memo={}):
        tmp = self.__lazy_load__()
        return copy.deepcopy(tmp)

    def load(self):
        tmp = self.__lazy_load__()
        if self.tp != 'OMFITpickle':
            return tmp.load()
        else:
            return tmp

    def save(self):
        if os.path.abspath(self.link) != os.path.abspath(self.filename):
            if os.path.isdir(self.link):
                shutil.copytree(self.link, self.filename)
            else:
                shutil.copy2(self.link, self.filename)

    def save_as(self, filename):
        self.filename = os.path.abspath(filename)
        directory = os.path.split(os.path.abspath(filename))[0]
        if os.path.exists(directory) == 0:
            os.makedirs(directory)
        self.save()

    def deploy(self, filename):
        if os.path.abspath(filename) != os.path.abspath(self.filename):
            directory = os.path.split(os.path.abspath(filename))[0]
            if os.path.exists(directory) == 0:
                os.makedirs(directory)
            if os.path.isdir(self.filename):
                shutil.copytree(self.filename, filename)
            else:
                shutil.copy2(self.filename, filename)

    def __save_kw__(self):
        return self.kw

    @property
    def cls(self):
        mapper = {'importDataset': 'Dataset', 'pandas_read_json': 'DataFrame'}
        return mapper.get(self.tp, self.tp)


# ---------------------
# OMFIT types
# ---------------------
global OMFITtypes, OMFITtypesStr, OMFITdictypes, OMFITdictypesStr
OMFITtypes = []
OMFITtypesStr = []
OMFITdictypes = []
OMFITdictypesStr = []

# this method must be called to update the list of types
def _updateTypes():
    try:  # this try-except is used for loading omfit_base as a standalone OMFIT class (without requiring omfit_mds as a dependency)
        from omfit_classes.omfit_mds import OMFITmdsObjects

        extra_objects = [OMFITmdsObjects]
    except Exception:
        extra_objects = []
    global OMFITtypes, OMFITtypesStr, OMFITdictypes, OMFITdictypesStr

    # OMFITtypes inherit from OMFITobject
    OMFITtypes[:] = [OMFITlazyLoad]
    for _itemName in list(globals().keys()):
        _item = eval(_itemName)
        if _itemName.startswith('OMFIT') and inspect.isclass(_item) and _itemName[0] != '_' and issubclass(_item, OMFITobject):
            OMFITtypes.append(_item)
    OMFITtypesStr[:] = [re.sub(r"\<.*'(.*)'\>", r'\1', item.strip(')(')).split('.')[-1] for item in str(OMFITtypes).strip('[]').split(',')]

    # OMFITdictypes inherit from SortedDict or OMFITmdsObjects and are not OMFITtypes
    OMFITdictypes[:] = []
    for _itemName in list(globals().keys()):
        _item = eval(_itemName)
        if (
            inspect.isclass(_item)
            and _itemName[0] != '_'
            and issubclass(_item, tuple([SortedDict] + extra_objects))
            and _item not in OMFITtypes
        ):
            OMFITdictypes.append(_item)
    OMFITdictypesStr[:] = [re.sub(r"\<.*'(.*)'\>", r'\1', item.strip(')(')).split('.')[-1] for item in str(OMFITdictypes).split(',')]


_updateTypes()


def itemTagsValues(meKid, expressionsExpression=False, dictionaryContent=False, showHidden=False, treeview=None, parent_tags=[]):
    def get_bases(clss, tp):
        bases = getattr(clss, '__bases__')
        if not len(bases):
            return None
        else:
            for item in bases:
                tp.append(item.__name__)
                get_bases(item, tp)

    invisible = ''
    separator = '-' * 300

    tags = ['treeItem', 'editableTreeItem']

    # this allows expression to be treated as if they were the value itself
    if isinstance(meKid, OMFITexpression) and not expressionsExpression:
        tags.append(meKid.__class__.__name__)
        meKid = meKid._value_()

    if isinstance(meKid, dict):
        tags.append('dictTreeItem')

    # get the data type and its bases
    if hasattr(meKid, '__class__'):
        tp = meKid.__class__.__name__
    else:
        tp = 'oldStyleClass'
    values = (meKid, tp)
    tags.append(tp)

    old_dynaLoad_switch = OMFITaux['dynaLoad_switch']
    OMFITaux['dynaLoad_switch'] = False
    try:

        # refine values and tags if possible
        if hasattr(meKid, '__class__') and not inspect.isclass(meKid):
            # add all of the tags on which the data type is based on
            get_bases(meKid.__class__, tags)

            if isinstance(meKid, OMFITexpression):
                # this is used in GUIs when expressionsExpression=True
                values = (meKid.expression, tp)

            # setup values and tags depending on the data type
            elif hasattr(meKid, '__tree_repr__'):
                values, tag = meKid.__tree_repr__()
                if values is None:
                    values = invisible
                elif values is -1:
                    values = separator
                if isinstance(values, str):
                    values = (values, tp)
                else:
                    values = (treeText(values, False, -1, True), tp)
                tags = tag + tags

            elif isinstance(meKid, dict) and dictionaryContent:
                values = (treeText(list(meKid.keys()), False, -1, True), tp)

            else:
                values = (treeText(meKid, True, 500, True), tp)

        tags.extend(parent_tags)
        tags_hash = omfit_hash(str(tuple(tags)), 10)

        # generate unique tag for each individual set of treeview visualization option
        # this is to avoid some visualization issues that depend on the underlying version of TK
        if treeview is not None:
            if tags_hash not in treeview.single_tags:

                # handle modifyOriginal, readOnly, modifyOriginal_readOnly
                tags = unsorted_unique(tags)
                if len([tag for tag in tags if tag in ['modifyOriginal', 'readOnly', 'modifyOriginal_readOnly']]) >= 2:
                    i = max([tags.index(tag) for tag in tags if tag in ['modifyOriginal', 'readOnly', 'modifyOriginal_readOnly']])
                    if 'modifyOriginal_readOnly' in tags:
                        tags.remove('modifyOriginal_readOnly')
                    tags.insert(i, 'modifyOriginal_readOnly')
                    if 'modifyOriginal' in tags:
                        tags.remove('modifyOriginal')
                    if 'readOnly' in tags:
                        tags.remove('readOnly')

                tags_config = {}
                for k in tags:
                    tmp = treeview.tag_configure(k)
                    for tag in tmp:
                        if (tag not in tags_config and tmp[tag]) or tag in ['this', 'other']:
                            tags_config[tag] = tmp[tag]
                treeview.tag_configure(tags_hash, **tags_config)
                treeview.single_tags.append(tags_hash)

        tags = [tags_hash] + list([tag + '_action' for tag in tags])
        return tags, list(values)

    except Exception as _excp:
        printe('Error in loading tree representation:\n' + repr(_excp))
        return ['OMFITerror'], ('--error loading tree representation--', tp)

    finally:
        OMFITaux['dynaLoad_switch'] = old_dynaLoad_switch


# ---------------------
# Statistics
# ---------------------
def omfit_log(action, details):
    if not os.path.exists(str(OMFIT['MainSettings']['SETUP']['stats_file'])):
        try:
            with open(str(OMFIT['MainSettings']['SETUP']['stats_file']), "w") as f:
                pass
        except Exception:
            pass
    try:
        if os.access(str(OMFIT['MainSettings']['SETUP']['stats_file']), os.W_OK):
            header = (
                os.environ['USER'] + ' ' + utils_base.now("%Y/%m/%d %H_%M_%S") + ' ' + repo_active_branch_commit + ' ' + repo_active_branch
            )
            with open(str(OMFIT['MainSettings']['SETUP']['stats_file']), "a") as f:
                f.write(header + ' ' + action + ' ' + details + '\n')
        else:
            raise
    except Exception:
        warnings.warn('Unable to write to stats file: ' + str(OMFIT['MainSettings']['SETUP']['stats_file']))

    provenanceID = ''
    if 'EXPERIMENT' in OMFIT['MainSettings'] and 'provenanceID' in OMFIT['MainSettings']['EXPERIMENT']:
        provenanceID = OMFIT['MainSettings']['EXPERIMENT']['provenanceID']

    try:
        payload = {
            'version': repo_active_branch_commit,
            'institution': OMFIT['MainSettings']['SETUP']['institution'],
            'action': action,
            'details': details,
            'provenanceID': provenanceID,
            '_ip_address': '?',
            '_date': '?',
        }
        host, port = evalExpr(SERVER['gadb-harvest']['HARVEST_server']).split(':')
        harvest_send(payload, '+omfit_stats_2', host=host, port=int(port))
    except Exception as _excp:
        printt('Exception: Failed send_db: ' + repr(_excp))


# -------------------
# diff GUI functions
# NOTE: these functions rely on tk and will not be available outside of the framework
# -------------------
def diffTreeGUI(
    this,
    other,
    thisName='Original',
    otherName='Compared to',
    resultName='Final result',
    title=None,
    diffSubModules=True,
    precision=0.0,
    description=False,
    tellDescription=False,
    deepcopyOther=True,
    skipClasses=(),
    noloadClasses=(),
    flatten=False,
    allow_merge=True,
    always_show_GUI=False,
    order=True,
    favor_my_order=False,
    modify_order=False,
):
    """
    Function used to compare two dictionary objects and manage their merge

    :param this: reference object (the one where data will be written to in case of merge)

    :param other: secondary object to compare to

    :param thisName: ['Original'] representation of reference object in the GUI

    :param otherName: ['Compared to'] representation of secondary object in the GUI

    :param resultName: ['Final result'] representation of result

    :param title: [None] GUI title

    :param diffSubModules: [True] do diff of sumbmodules or not. If `None` only compare module ID and its DEPENDENCIES.

    :param precision: [0.0] relative precision to which to compare objects

    :param description: [False] commit to be input by the user

    :param tellDescription: [False] show description or not

    :param deepcopyOther: [True] Whether to perform internally `other=copy.deepcopy(other)` to avoid `diffTreeGUI` to modify the original content

    :param skipClasses: () tuple containing classes to skip

    :param noloadClasses: () tuple containing classes to not load

    :param flatten: whether to flatten the data in nested dictionaries

    :param allow_merge: whether to allow merging of data

    :param always_show_GUI: whether to show GUIs even if there are no differences

    :param order: order of the keys matters

    :param favor_my_order: favor my order of keys

    :param modify_order: update order of input dictionaries based on diff

    :return: (switch,False/True,keys)

    * switch is a dictionary which lists all of the differences

    * False/True will be used to keep track of what the user wants to switch between dictionaries

    * keys is used to keep the keys of the merged dictionary in order
    """

    if flatten:
        this = this.flatten()
        other = other.flatten()
        allow_merge = False
    elif deepcopyOther:
        other = copy.deepcopy(other)  # for how the merge is done (flipping), I need to make a copy of the `other` object

    if not diffSubModules:
        remove_submodules(this, keepModuleAndDependencies=(diffSubModules is None))
        remove_submodules(other, keepModuleAndDependencies=(diffSubModules is None))

    switch = this.diff(
        other,
        skipClasses=skipClasses,
        noloadClasses=noloadClasses,
        ignoreComments=True,
        precision=precision,
        order=order,
        favor_my_order=favor_my_order,
        modify_order=modify_order,
    )

    def set_merge_button_text(count):
        if count == 0:
            merge_button_text.set('Nothing to merge: press <spacebar> to select items to merge')
        else:
            merge_button_text.set('Merge selected %d items' % count)

    def switcher(onlyThisNode=False):
        location = parseBuildLocation(treeGUI.selection()[0])
        tree = switch[0]
        for item in location[:-1]:
            tree = tree[item][0]

        def set(a, val):
            if isinstance(a[0], SortedDict):
                a[1] = val
                if not onlyThisNode:
                    for kid in a[0]:
                        set(a[0][kid], val)
            else:
                a[1] = val

        set(tree[location[-1]], not tree[location[-1]][1])

        count = f_traverse(switch[0], '')
        set_merge_button_text(count)

        treeGUI.update_idletasks()

    def f_traverse(me, myLocation='', myLocationSwitch=''):
        count = 0
        for kid in me:
            if isinstance(me[kid][0], SortedDict):
                state = 'changed_sub'
            else:
                state = me[kid][0]

            kidName = "[" + repr(kid) + "]"
            entryID = myLocation + kidName
            entryIDswitch = myLocationSwitch + '[0]' + kidName

            try:
                this_tags, this_values = itemTagsValues(
                    eval('this' + entryID), expressionsExpression=True, dictionaryContent=True, showHidden=False, treeview=treeGUI
                )
            except Exception:
                this_tags = []
                this_values = ['', '']
            try:
                other_tags, other_values = itemTagsValues(
                    eval('other' + entryID), expressionsExpression=True, dictionaryContent=True, showHidden=False, treeview=treeGUI
                )
            except Exception:
                other_tags = []
                other_values = ['', '']

            if createTree:
                tags = []
                if allow_merge:
                    values = (this_values[0], other_values[0], this_values[0])
                else:
                    if not len(set(this_tags).difference(set(other_tags))):
                        tags.extend(this_tags)
                    values = (this_values[0], other_values[0])
                treeGUI.insert(myLocation, tk.END, entryID, text=treeText(kid, False, -1, False), values=values, tags=tuple(tags))

            values = list(treeGUI.item(entryID, 'values'))
            if allow_merge:
                if eval('switch' + entryIDswitch)[1]:
                    values = (values[0], values[1], values[1], '|')  # other
                    tags = [state, 'mergeable_action', 'other']
                    tags.extend(other_tags)
                    count += 1
                else:
                    values = (values[0], values[1], values[0], '_')  # this
                    tags = [state, 'mergeable_action', 'this']
                    tags.extend(this_tags)

                if state in ['added', 'changed', 'removed', 'order']:
                    treeGUI.item(entryID, tags=tuple(tags), values=values)
                elif state == 'changed_sub':
                    count += f_traverse(me[kid][0], entryID, entryIDswitch)
                    treeGUI.item(entryID, tags=tuple(tags), values=('', '', '', values[3]))
            else:
                if state == 'changed_sub':
                    count += f_traverse(me[kid][0], entryID, entryIDswitch)
                    treeGUI.item(entryID, tags=tuple(tags), values=('', ''))
                else:
                    treeGUI.item(entryID, tags=tuple(tags), values=values)

            # this is just to prevent the garbage collector to delete these variables
            this, other, switch
        return count

    def merger(this_, other_, switch_, flipCompare=True):
        this_k = 0
        other_k = 0
        for kid in switch_[2]:
            if kid in this_:
                this_k += 1
            if kid in other_:
                other_k += 1
            if kid in switch_[0]:
                # go deeper in dictionaries
                if isinstance(switch_[0][kid][0], SortedDict):
                    if kid not in this_:
                        this_[kid] = SortedDict()
                    if kid not in other_:
                        other_[kid] = SortedDict()
                    # go deeper
                    if switch_[0][kid][1] == flipCompare:
                        merger(this_[kid], other_[kid], switch_[0][kid], not flipCompare)
                    else:
                        merger(this_[kid], other_[kid], switch_[0][kid], flipCompare)
                # merge content
                if switch_[0][kid][1] == flipCompare:
                    printi("Merging: " + str(kid))
                    # sorting of the content
                    if len(switch_[0][kid]) > 2:
                        this_[kid].sort(key=lambda x: switch_[0][kid][2].index(x) if x in switch_[0][kid][2] else 1e10)
                        other_[kid].sort(key=lambda x: switch_[0][kid][2].index(x) if x in switch_[0][kid][2] else 1e10)

                    if kid not in other_:
                        other_.insert(other_k, kid, this_[kid])
                        del this_[kid]
                    elif kid not in this_:
                        this_.insert(this_k, kid, other_[kid])
                        del other_[kid]
                    else:
                        tmp = this_[kid]
                        this_.insert(this_k, kid, other_[kid])
                        other_.insert(other_k, kid, tmp)

    def diffDetail(event):
        entryID = treeGUI.identify_row(event.y)
        try:
            eval('this' + entryID)
            thisMisses = False
        except Exception:
            thisMisses = True
        try:
            eval('other' + entryID)
            otherMisses = False
        except Exception:
            otherMisses = True

        if (thisMisses or isinstance(eval('this' + entryID), str) or eval('this' + entryID).__class__ is OMFITexpression) and (
            otherMisses or isinstance(eval('other' + entryID), str) or eval('other' + entryID).__class__ is OMFITexpression
        ):

            if thisMisses:
                thisFile = None
            elif eval('this' + entryID).__class__ is OMFITexpression:
                thisFile = eval('this' + entryID).expression
            elif isinstance(eval('this' + entryID), str):
                thisFile = eval('this' + entryID)
            else:
                return

            if otherMisses:
                otherFile = None
            elif eval('other' + entryID).__class__ is OMFITexpression:
                otherFile = eval('other' + entryID).expression
            elif isinstance(eval('other' + entryID), str):
                otherFile = eval('other' + entryID)
            else:
                return

            diffViewer(top, thisString=thisFile, otherString=otherFile, thisName=thisName, otherName=otherName, title=entryID)

        elif (thisMisses or isinstance(eval('this' + entryID), OMFITascii)) and (
            otherMisses or isinstance(eval('other' + entryID), OMFITascii)
        ):

            if thisMisses:
                thisFile = None
            else:
                thisFile = eval('this' + entryID).filename

            if otherMisses:
                otherFile = None
            else:
                otherFile = eval('other' + entryID).filename

            diffViewer(top, thisFile, otherFile, thisName=thisName, otherName=otherName, title=entryID)

        elif (thisMisses or isinstance(eval('this' + entryID), np.ndarray)) and (
            otherMisses or isinstance(eval('other' + entryID), np.ndarray)
        ):

            if thisMisses:
                thisArray = np.tile(np.nan, eval('other' + entryID).shape)
            else:
                thisArray = eval('this' + entryID)

            if otherMisses:
                otherArray = np.tile(np.nan, eval('this' + entryID).shape)
            else:
                otherArray = eval('other' + entryID)

            # cleverly choose whether it is better to compare in 1d or 2d when there is squeezable dimension(s).
            thisArray = np.squeeze(thisArray)
            otherArray = np.squeeze(otherArray)
            s1 = len(thisArray.shape)
            s2 = len(otherArray.shape)

            if s1 == 1 and s2 == 1:
                fig = pyplot.figure()
                fig.add_subplot(1, 2, 1)
                pyplot.plot(thisArray, 'b.-', label=thisName)
                pyplot.plot(otherArray, 'gx-', label=otherName)
                pyplot.title('Compare arrays')
                fig.add_subplot(1, 2, 2)
                pyplot.plot(np.linspace(0, 1, thisArray.size), thisArray, 'b.-', label=thisName)
                pyplot.plot(np.linspace(0, 1, otherArray.size), otherArray, 'gx-', label=otherName)
                pyplot.legend(labelspacing=0.2, loc=0).draggable(state=True)
                pyplot.title('Compare arrays (x from 0 to 1)')

            elif s1 == 2 and s2 == 2:
                fig = pyplot.figure()
                fig.add_subplot(1, 2, 1)
                if not thisMisses:
                    pyplot.contour(thisArray, 20, colors='b', label=thisName)
                if not otherMisses:
                    pyplot.contour(otherArray, 20, colors='g', label=thisName)
                pyplot.title('Compare 2D arrays')
                fig.add_subplot(1, 2, 2)
                pyplot.plot(np.nan, 'b.-', label=thisName)
                if not thisMisses:
                    pyplot.contour(
                        np.linspace(0, 1, thisArray.shape[1]),
                        np.linspace(0, 1, thisArray.shape[0]),
                        thisArray,
                        20,
                        colors=pyplot.gca().lines[-1].get_color(),
                    )
                pyplot.plot(np.nan, 'gx-', label=otherName)
                if not otherMisses:
                    pyplot.contour(
                        np.linspace(0, 1, otherArray.shape[1]),
                        np.linspace(0, 1, otherArray.shape[0]),
                        otherArray,
                        20,
                        colors=pyplot.gca().lines[-1].get_color(),
                    )
                pyplot.legend(labelspacing=0.2, loc=0).draggable(state=True)
                pyplot.title('Compare 2D arrays (x and y from 0 to 1)')

        # these are here to prevent the garbage collector to remove these variables from the namespace
        this, other

    if not always_show_GUI and not len(switch[0]):
        printi('No differences found between `%s` and `%s`' % (thisName, otherName))
        if description or isinstance(description, str):
            return {}, None
        else:
            return {}

    merge_button_text = tk.StringVar()
    top = tk.Toplevel(OMFITaux['rootGUI'])
    top.withdraw()
    top.transient(OMFITaux['rootGUI'])
    top.geometry(str(int(OMFITaux['rootGUI'].winfo_width() * 8.0 / 9)) + "x" + str(int(OMFITaux['rootGUI'].winfo_height() * 8.0 / 9)))
    if allow_merge:
        top.wm_title('Tree diff/merge')
    else:
        top.wm_title('Tree diff')

    if not (title is None):
        ttk.Label(top, text=title, font=OMFITfont('bold', 2)).pack(side=tk.TOP, expand=tk.NO, fill=tk.X, padx=10)
    if allow_merge:
        ttk.Label(
            top,
            text='<space> toggle merge, <double-click> diff of strings, ASCII files and arrays, <Esc> abort merging',
            justify=tk.LEFT,
            anchor=tk.W,
        ).pack(side=tk.TOP)
    treeGUI = tk.Treeview(top)
    treeGUI.frame.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH, padx=5, pady=5)
    if allow_merge:
        treeGUI["columns"] = ('this', 'other', 'merge', 'switch')
        displaycolumns = ['merge', 'this', 'other', 'switch']
    else:
        treeGUI["columns"] = ('this', 'other')
        displaycolumns = ['this', 'other']
    if thisName is None:
        displaycolumns.remove('this')
    if otherName is None:
        displaycolumns.remove('other')
    if allow_merge and resultName is None:
        displaycolumns.remove('merge')
    treeGUI["displaycolumns"] = tuple(displaycolumns)
    treeGUI.column("#0", minwidth=150, width=180, stretch=False)
    treeGUI.column("this", minwidth=180, width=180, stretch=True)
    treeGUI.column("other", minwidth=180, width=180, stretch=True)
    treeGUI.heading("#0", text="location")
    treeGUI.heading("this", text=thisName)
    treeGUI.heading("other", text=otherName)
    if allow_merge:
        treeGUI.column("switch", minwidth=20, width=20, stretch=False, anchor=tk.CENTER)
        treeGUI.heading("switch", text="")
        treeGUI.column("merge", minwidth=180, width=180, stretch=False)
        treeGUI.heading("merge", text=resultName)
        global_event_bindings.add(
            'COMPARE/MERGE: toggle entry and sub-entries',
            treeGUI,
            '<space>',
            lambda event=None: treeGUI.after(1, switcher()),
            tag="mergeable",
        )
        global_event_bindings.add(
            'COMPARE/MERGE: toggle single entry',
            treeGUI,
            '<Shift-space>',
            lambda event=None: treeGUI.after(1, switcher(True)),
            tag="mergeable",
        )

    def onDouble(event):
        diffDetail(event)

    def onMerge(event=None):
        merger(this, other, switch)
        OMFITaux['GUI'].update_treeGUI_and_GUI()
        anySwitched.set(True)
        if description is not False:
            _description.append(desc.get(1.0, tk.END).strip())
        top.destroy()

    def onEscape(event=None):
        anySwitched.set(False)
        top.destroy()

    _description = []
    if tellDescription is not False:
        desc = askDescription(top, tellDescription, 'Description:', showInsertDate=False, showHistorySeparate=False)
        desc.config(state=tk.DISABLED)
    elif description is not False:
        desc = askDescription(top, description, 'Commit message:', showInsertDate=False, showHistorySeparate=False)
        if allow_merge:
            desc.bind(f'<{ctrlCmd()}-Return>', onMerge)

    global_event_bindings.add('COMPARE/MERGE: show difference details', treeGUI, '<Double-1>', onDouble)
    if allow_merge:
        ttk.Button(top, textvar=merge_button_text, command=onMerge).pack(side=tk.TOP, expand=tk.NO, fill=tk.X)
        top.bind('<Return>', onMerge)
        top.bind('<KP_Enter>', onMerge)
    else:
        top.bind('<Return>', onEscape)
        top.bind('<KP_Enter>', onEscape)
    top.bind('<Escape>', onEscape)
    if 'thome' in OMFIT['MainSettings']['SETUP']['email']:
        ttk.Button(top, text=['Close', 'Cancel'][allow_merge], command=onEscape).pack(side=tk.TOP, expand=tk.NO, fill=tk.X)

    anySwitched = tk.BooleanVar()
    createTree = True
    count = f_traverse(switch[0], '')
    set_merge_button_text(count)
    createTree = False

    top.protocol("WM_DELETE_WINDOW", top.destroy)
    top.update_idletasks()
    top.deiconify()
    top.wait_window(top)
    if not anySwitched.get():
        if description is not False:
            return None, None
        else:
            return None
    else:
        if description is not False:
            return switch, _description[0]
        else:
            return switch


def exportTreeGUI(this, title=None, description=False):
    # returns [switch,False/True,keys]
    # switch is a dictionary which lists all of the differences
    # False/True will be used to keep track of what the user wants to switch between dictionaries
    # keys is used to keep the keys of the merged dictionary in order

    # create an empty structure
    def s_traverse(me):
        switch = SortedDict()

        for key in list(me.keys()):
            if isinstance(me[key], OMFITmodule):
                for item in list(me[key].keys()):
                    if item == 'SETTINGS':
                        for sett in list(me[key]['SETTINGS'].keys()):
                            if sett not in ['MODULE', 'DEPENDENCIES']:
                                del me[key]['SETTINGS'][sett]
                            elif sett == 'MODULE':
                                for k in list(me[key]['SETTINGS']['MODULE'].keys()):
                                    if k not in ['ID']:
                                        del me[key]['SETTINGS']['MODULE'][k]
                    elif not isinstance(me[key][item], OMFITmodule):
                        del me[key][item]
            # deleting items will prevent them to show up
            if key == '__scratch__':
                del me[key]
            # _OMFITnoSave and OMFITobject items that are not OMFITnamelist will be showed in their entirety
            elif isinstance(me[key], _OMFITnoSave) or (
                isinstance(me[key], OMFITobject) and not isinstance(me[key], OMFITnamelist) and not isinstance(me[key], OMFITsettings)
            ):
                switch[key] = ['bla', True]
            elif isinstance(me[key], SortedDict):
                switch[key] = s_traverse(me[key])
            else:
                switch[key] = ['bla', True]

        return [switch, True, list(me.keys())]

    switch = s_traverse(this)

    def switcher(onlyThisNode=False):
        location = parseBuildLocation(treeGUI.selection()[0])
        tree = switch[0]
        for item in location[:-1]:
            tree = tree[item][0]

        def set(a, val):
            if isinstance(a[0], SortedDict):
                a[1] = val
                if not onlyThisNode:
                    for kid in a[0]:
                        set(a[0][kid], val)
            else:
                a[1] = val

        set(tree[location[-1]], not tree[location[-1]][1])

        # if the last thing that I switched was "other"
        # then I should set to "other" also the parents
        if tree[location[-1]][1]:
            tree = switch[0]
            for item in location[:-1]:
                tree[item][1] = True
                tree = tree[item][0]

        f_traverse(switch[0], '')
        treeGUI.update_idletasks()

    def deleter(this_, switch_, flipCompare=True):
        for this_k, kid in enumerate(switch_[2]):
            if kid in switch_[0]:
                if isinstance(switch_[0][kid][0], SortedDict):
                    if switch_[0][kid][1] != flipCompare:
                        deleter(this_[kid], switch_[0][kid], not flipCompare)
                    else:
                        deleter(this_[kid], switch_[0][kid], flipCompare)
                if switch_[0][kid][1] != flipCompare:
                    printi("Deleter: " + str(kid))
                    del this_[kid]

    def f_traverse(me, myLocation='', myLocationSwitch=''):
        for kid in me:
            kidName = "[" + repr(kid) + "]"
            entryID = myLocation + kidName
            entryIDswitch = myLocationSwitch + '[0]' + kidName

            try:
                this_tags, this_values = itemTagsValues(
                    eval('this' + entryID), expressionsExpression=True, showHidden=False, treeview=treeGUI
                )
            except Exception:
                this_tags = []
                this_values = ['']

            if createTree:
                treeGUI.insert(myLocation, tk.END, entryID, text=treeText(kid, False, -1, False), values=(this_values[0],))

            if me[kid][1]:
                tags = ['exportable_action', 'other']
            else:
                tags = ['exportable_action', 'this']
            tags.extend(this_tags)

            treeGUI.item(entryID, tags=tuple(tags))

            if isinstance(me[kid][0], SortedDict):
                f_traverse(me[kid][0], entryID, entryIDswitch)

            this, switch

    top = tk.Toplevel(OMFITaux['rootGUI'])
    top.withdraw()
    top.transient(OMFITaux['rootGUI'])
    top.geometry(str(int(OMFITaux['rootGUI'].winfo_width() * 8.0 / 9)) + "x" + str(int(OMFITaux['rootGUI'].winfo_height() * 8.0 / 9)))
    top.wm_title('Export tree')

    if not (title is None):
        ttk.Label(top, text=title, font=OMFITfont('bold', 2)).pack(side=tk.TOP, expand=tk.NO, fill=tk.X, padx=10)
    ttk.Label(
        top, text='<space> toggle export, <Shift-space> toggle export single entry, <Esc> to abort', justify=tk.LEFT, anchor=tk.W
    ).pack(side=tk.TOP)
    treeGUI = tk.Treeview(top)
    treeGUI.frame.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH, padx=5, pady=5)
    treeGUI["columns"] = ('value', 'dummy')
    displaycolumns = ['value']
    treeGUI["displaycolumns"] = tuple(displaycolumns)
    treeGUI.column("#0", minwidth=150, width=180, stretch=False)
    treeGUI.column("value", minwidth=180, width=180, stretch=True)
    treeGUI.column("dummy", minwidth=180, width=180, stretch=True)
    treeGUI.heading("#0", text="location")
    treeGUI.heading("value", text='value')
    global_event_bindings.add(
        'COMPARE/MERGE: toggle entry and sub-entries', treeGUI, '<space>', lambda event=None: treeGUI.after(1, switcher()), tag="exportable"
    )
    global_event_bindings.add(
        'COMPARE/MERGE: toggle single entry',
        treeGUI,
        '<Shift-space>',
        lambda event=None: treeGUI.after(1, switcher(True)),
        tag="exportable",
    )

    def onExport(event=None):
        deleter(this, switch)
        OMFITaux['GUI'].update_treeGUI_and_GUI()
        anySwitched.set(True)
        if description is not False:
            _description.append(desc.get(1.0, tk.END).strip())
        top.destroy()

    def onEscape(event=None):
        anySwitched.set(False)
        top.destroy()

    _description = []
    if description is not False:
        desc = askDescription(top, '', 'Description:', showInsertDate=False)
        desc.bind(f'<{ctrlCmd()}-Return>', onExport)

    ttk.Button(top, text='Export highlighted entries', command=onExport).pack(side=tk.TOP, expand=tk.NO, fill=tk.X)
    if 'thome' in OMFIT['MainSettings']['SETUP']['email']:
        ttk.Button(top, text='Cancel', command=onEscape).pack(side=tk.TOP, expand=tk.NO, fill=tk.X)
    top.bind('<Return>', onExport)
    top.bind('<KP_Enter>', onExport)
    top.bind('<Escape>', onEscape)

    anySwitched = tk.BooleanVar()
    createTree = True
    f_traverse(switch[0], '')
    createTree = False

    top.protocol("WM_DELETE_WINDOW", top.destroy)
    top.update_idletasks()
    top.deiconify()
    top.wait_window(top)
    if not anySwitched.get():
        if description is not False:
            return None, None
        else:
            return None
    else:
        if description is not False:
            return switch, _description[0]
        else:
            return switch


def diffViewer(
    root, thisFilename=None, otherFilename=None, thisName='Original', otherName='New', title=None, thisString=None, otherString=None
):
    """
    Present a side by side visual comparison of two strings

    :param root: A tk master GUI
    """

    if thisFilename is None and thisString is None:
        this = ''
    elif thisFilename is not None:
        with open(thisFilename, 'r') as f:
            this = f.read().splitlines(1)
    elif thisString is not None:
        this = str(thisString).splitlines(1)

    if otherFilename is None and otherString is None:
        other = ''
    elif otherFilename is not None:
        with open(otherFilename, 'r') as f:
            other = f.read().splitlines(1)
    elif otherString is not None:
        other = str(otherString).splitlines(1)

    inputDiffText = list(difflib.Differ(linejunk=None).compare(this, other))

    def yview(*args):
        textA.yview(*args)
        textB.yview(*args)

    def mouse_wheel(event):
        # respond to Linux or Windows wheel event
        if event.num == 5 or event.delta == -120:
            yview('scroll', 1, 'units')
        elif event.num == 4 or event.delta == 120:
            yview('scroll', -1, 'units')
        return 'break'

    top = tk.Toplevel(root)
    top.withdraw()
    top.transient(root)
    top.geometry(str(int(OMFITaux['rootGUI'].winfo_width() * 8.0 / 9)) + "x" + str(int(OMFITaux['rootGUI'].winfo_height() * 8.0 / 9)))

    if title is None:
        top.wm_title('ASCII files diff')
    else:
        top.wm_title(title)

    # GUI items
    labelA = ttk.Label(top, text=thisName, font=OMFITfont('bold', 2))
    labelB = ttk.Label(top, text=otherName, font=OMFITfont('bold', 2))
    textA = tk.Text(top, relief=tk.SOLID, borderwidth=1, font=OMFITfont('normal', 0, 'Courier'), wrap=tk.NONE)
    sb = ttk.Scrollbar(top, command=yview, orient='vertical')
    textB = tk.Text(top, relief=tk.SOLID, borderwidth=1, font=OMFITfont('normal', 0, 'Courier'), wrap=tk.NONE)
    sbA = ttk.Scrollbar(top, command=textA.xview, orient='horizontal')
    sbB = ttk.Scrollbar(top, command=textB.xview, orient='horizontal')

    # arrange GUI items
    top.rowconfigure(1, weight=1)
    top.columnconfigure(0, weight=1)
    top.columnconfigure(2, weight=1)
    labelA.grid(column=0, row=0, sticky='ew')
    labelB.grid(column=2, row=0, sticky='ew')
    textA.grid(column=0, row=1, sticky='nsew')
    sb.grid(column=1, row=1, sticky='ns')
    textB.grid(column=2, row=1, sticky='nsew')
    sbA.grid(column=0, row=2, sticky='ew')
    sbB.grid(column=2, row=2, sticky='ew')

    # synchronized scrolling
    textA['xscrollcommand'] = sbA.set
    textB['xscrollcommand'] = sbB.set
    textA['yscrollcommand'] = sb.set
    textB['yscrollcommand'] = sb.set
    for k in ["<Button-4>", "<Button-5>", "<MouseWheel>"]:
        textA.bind(k, mouse_wheel)
        textB.bind(k, mouse_wheel)

    # colors
    for text in textA, textB:
        text.tag_configure('+', background='DarkSeaGreen1')
        text.tag_configure('-', background='RosyBrown2')
        text.tag_configure('?', background='light blue')
        text.tag_configure(' ', background='white')
        text.tag_configure('/', background='gray85')
        text.tag_configure('#', foreground='gray50')

    # differences
    offset = 2
    lines = 0
    lineA = 1
    lineB = 1
    lno_offset = len(str(len(inputDiffText))) + 1  # for the colon
    lno_format = '{:0%sd}:{}' % (lno_offset - 1)  # for the colon

    def format_lno(text_obj, line_no):
        for ki in range(lno_offset):
            text_obj.tag_add('#', '%s.%s' % (line_no, ki))

    for kk in range(len(inputDiffText)):
        item = inputDiffText[kk]
        if item[0] == '+':
            textA.insert('end', '\n', '/')
            textB.insert('end', lno_format.format(lineB, item[offset:]), '+')
            lineB += 1
            lastText = textB
            notLastText = textA
            lines += 1
            format_lno(textB, lines)
        elif item[0] == '-':
            textA.insert('end', lno_format.format(lineA, item[offset:]), '-')
            lineA += 1
            textB.insert('end', '\n', '/')
            lastText = textA
            notLastText = textB
            lines += 1
            format_lno(textA, lines)
        elif item[0] == '?':
            for k, c in enumerate(item[offset:]):
                if c in ['-', '+', '^']:
                    lastText.tag_add('?', str(lines) + '.' + str(k + lno_offset))
        else:
            textA.insert('end', lno_format.format(lineA, item[offset:]))
            lineA += 1
            textB.insert('end', lno_format.format(lineB, item[offset:]))
            lineB += 1
            lines += 1
            format_lno(textA, lines)
            format_lno(textB, lines)

    textA.config(state=tk.DISABLED)
    textB.config(state=tk.DISABLED)

    top.bind('<Escape>', lambda event=None: top.destroy())

    top.protocol("WM_DELETE_WINDOW", top.destroy)
    top.update_idletasks()
    top.deiconify()
    top.wait_window(top)


def askDescription(parent, txt, label, showInsertDate=False, showHistorySeparate=False, expand=0, scrolledTextKW={}):
    top = ttk.Frame(parent)
    top.pack(side=tk.TOP, padx=5, expand=expand, fill=tk.BOTH)

    lblFrame = ttk.Frame(top)
    lblFrame.pack(side=tk.TOP, padx=5, expand=tk.NO, fill=tk.X)
    ttk.Label(lblFrame, text=label, justify=tk.LEFT, anchor=tk.W).pack(side=tk.LEFT, expand=tk.NO, fill=tk.X)

    def onInsertDate(msglist):
        desc.insert('insert', ' '.join(msglist))
        desc.see('insert')
        desc.focus_set()

    def onInsertDateLong(event=None):
        onInsertDate(['-->>>', utils_base.now(), os.environ['USER'], '<<<--\n'])

    def onInsertDateShort(event=None):
        onInsertDate([utils_base.now(), '|| '])

    if showInsertDate:
        ttk.Label(lblFrame, text='   ', justify=tk.LEFT, anchor=tk.W).pack(side=tk.LEFT, expand=tk.NO, fill=tk.X)
        bsho = ttk.Button(lblFrame, text="Insert user/date/time (long)", command=onInsertDateLong)
        bsho.pack(side=tk.LEFT, padx=5, pady=5)
        blon = ttk.Button(lblFrame, text="Insert date/time (short)", command=onInsertDateShort)
        blon.pack(side=tk.LEFT, padx=5, pady=5)

    descFrame = ttk.Frame(top)
    descFrame.pack(side=tk.TOP, padx=5, expand=tk.YES, fill=tk.BOTH)
    desc = tk.ScrolledText(descFrame, height=8, undo=tk.TRUE, maxundo=-1, **scrolledTextKW)
    desc.tag_configure('historic', foreground='dark slate gray')

    if showHistorySeparate:
        hist = tk.ScrolledText(descFrame, height=8, undo=tk.TRUE, maxundo=-1)
        hist.tag_configure('historic', foreground='dark slate gray')
        where = hist

        desc.grid(column=0, row=0, sticky='nsew')
        hist.grid(column=1, row=0, sticky='nsew')
        descFrame.columnconfigure(0, weight=1)
        descFrame.columnconfigure(1, weight=1)
        descFrame.rowconfigure(0, weight=1)
    else:
        where = desc
        desc.pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH)

    if isinstance(txt, str):
        txt = txt.strip()
        if len(txt):
            where.insert(1.0, txt.strip() + '\n\n', 'historic')
            where.see('insert')

    if showHistorySeparate:
        hist.configure(state=tk.DISABLED)

    def insertReturn(event=None):
        desc.insert('insert', '\n')
        desc.see('insert')
        return 'break'

    desc.bind('<Return>', insertReturn)
    desc.bind('<KP_Enter>', insertReturn)

    desc.frame = top
    return desc


def remove_submodules(module, keepModuleAndDependencies=True):
    """
    This function removes all submodules from the current module (operates in place)

    :param module: module to cleanup

    :param keepModuleAndDependencies: whether to keep the MODULE and DEPENDENCIES entries of the submodules SETTINGS
    """
    for key in list(module.keys()):
        if isinstance(module[key], OMFITmodule) and keepModuleAndDependencies:
            for item in list(module[key].keys()):
                if item == 'SETTINGS':
                    for sett in list(module[key]['SETTINGS'].keys()):
                        if sett not in ['MODULE', 'DEPENDENCIES']:
                            del module[key]['SETTINGS'][sett]
                        elif sett == 'MODULE':
                            for k in list(module[key]['SETTINGS']['MODULE'].keys()):
                                if k not in ['ID']:
                                    del module[key]['SETTINGS']['MODULE'][k]
                elif not isinstance(module[key][item], OMFITmodule):
                    del module[key][item]
        elif isinstance(module[key], OMFITmodule) and not keepModuleAndDependencies:
            del module[key]
            continue
        # deleting items will prevent them to show up
        elif key == '__scratch__':
            del module[key]
            continue
        # skipping items will prevents pruning further down
        elif isinstance(module[key], _OMFITnoSave) or (hasattr(module[key], 'dynaLoad') and module[key].dynaLoad):
            continue
        if isinstance(module[key], SortedDict):
            remove_submodules(module[key], keepModuleAndDependencies=keepModuleAndDependencies)


############################################
if '__main__' == __name__:
    test_classes_main_header()

    with open(OMFITsrc + '/../regression/test_expressions.py') as f:
        exec(compile(f.read(), OMFITsrc + '/../regression/test_expressions.py', 'exec'))
