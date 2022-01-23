from . import unix_os as os
import sys
import stat
import copy
import shutil
import time
import uuid
import zipfile
import ast
import platform
import warnings
import functools
import builtins
import queue as Queue
import pickle
from io import StringIO
import locale

# Keep track of what classes have been loaded
# This is used internally for identifying what classes are
# used by different OMFIT modules/scripts/workflows/regressions
_loaded_classes = set()

# set default locale to be en_US.UTF-8
for _item in ['LC_ALL', 'LC_CTYPE']:
    os.environ[_item] = 'en_US.UTF-8'

# monkey patch open so to enforce UNIX style newline also on windows
def open(file, mode='r', buffering=-1, encoding=None, errors=None, newline=None, closefd=True, opener=None):
    if mode == 'w':
        newline = '\n'
    return builtins.open(
        file=file, mode=mode, buffering=buffering, encoding=encoding, errors=errors, newline=newline, closefd=closefd, opener=opener
    )


open.__doc__ = builtins.open.__doc__

if os.name == 'nt':
    import wexpect as pexpect

    EOF = pexpect.EOF
else:
    import pexpect

    EOF = pexpect.exceptions.EOF

if 'omfit_tree' in sys.modules:
    print('Loading base utility functions...')


def deprecated(func):
    """This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used."""

    @functools.wraps(func)
    def new_func(*args, **kwargs):
        with warnings.catch_warnings():
            warnings.simplefilter('always', DeprecationWarning)
            warnings.warn("Call to deprecated function `{}`".format(func.__name__), category=DeprecationWarning)
        return func(*args, **kwargs)

    return new_func


def b2s(obj):
    if isinstance(obj, bytes):
        for error_handling in ['strict', 'replace', 'ignore']:
            try:
                return obj.decode("utf-8", errors=error_handling)
            except Exception:
                pass
        raise RuntimeError('A bytes object was passed to b2s, but not handled')
    import numpy as np

    if isinstance(obj, np.ndarray) and (
        obj.dtype.name.startswith('bytes')
        or (obj.dtype.name.startswith('object') and np.all(map(lambda x: isinstance(x, (bytes, str)), obj.flat)))
    ):
        return np.reshape(np.array(list(map(b2s, obj.flat))), obj.shape)
    else:
        return obj


# This is the pickle protocol used for long term storage and deployment of OMFIT objects
pickle.OMFIT_PROTOCOL = max([4, pickle.HIGHEST_PROTOCOL])

# Windows defines USERNAME instead of the Unix USER environmental variable
if os.name == 'nt' and 'USER' not in os.environ and 'USERNAME' in os.environ:
    os.environ['USER'] = os.environ['USERNAME']

# Debug slow imports
if float(os.environ.get('OMFIT_TIME_IMPORTS', '0')) > 0:
    _orig_import = builtins.__import__

    def new_import(*args, **kw):
        time = _orig_import('time')
        t0 = time.time()
        tmp = _orig_import(*args, **kw)
        if args and (time.time() - t0) > float(os.environ['OMFIT_TIME_IMPORTS']):
            sys.__stderr__.write('Import of `%s` has taken time: %3.3f s\n' % (args[0], time.time() - t0))
        return tmp

    builtins.__import__ = new_import

# remove SSH_ASKPASS environmental varaible to avoid graphical SSH prompt
if 'SSH_ASKPASS' in os.environ:
    del os.environ['SSH_ASKPASS']

# set the environmental variable HOME based on HOMEPATH (for windows installations)
os.environ.setdefault('HOME', os.path.expanduser('~'))

# the OMFITsrc variable stores the directory where OMFIT is running from
# note that this is defined from the omfit/omfit_classes folder
OMFITsrc = os.path.abspath(os.path.dirname(__file__) + os.sep + '..')

# the OMFITsettingsDir variable stores the default users settins, bookmarks, open sessions, ...
OMFITsettingsDir = os.environ['HOME'] + os.sep + '.OMFIT'
firstOMFITexecution = False
if not os.path.exists(OMFITsettingsDir):
    os.makedirs(OMFITsettingsDir)
    firstOMFITexecution = True
os.chmod(OMFITsettingsDir, 0o700)

# The OMFITtmpDir variable stores the temporary directory where working
# directories from multiple instances of OMFIT coexist
# It is important that OMFITtmpDir is defined in a directory that is not shared among multiple nodes of a cluster
_tmp = os.path.abspath(os.environ.get('OMFIT_TMPDIR', os.sep + 'tmp'))
OMFITtmpDir = os.sep.join([_tmp, os.environ['USER'], 'OMFIT'])
if not os.path.exists(OMFITtmpDir):
    try:
        os.makedirs(OMFITtmpDir)
    except OSError:
        if os.path.exists(OMFITtmpDir):
            pass  # to handle simultaneous start of OMFIT sessions
        else:
            OMFITtmpDir = os.environ['HOME'] + os.sep + 'tmp' + os.sep + 'OMFIT'
            if not os.path.exists(OMFITtmpDir):
                try:
                    os.makedirs(OMFITtmpDir)
                except OSError:
                    if os.path.exists(OMFITtmpDir):
                        pass  # to handle simultaneous start of OMFIT sessions
                    else:
                        raise

# create an OMFITsessionsDir directory for each workstation
OMFITsessionsDir = OMFITtmpDir + '_local' + os.sep + 'sessions'
if not os.path.exists(OMFITsessionsDir):
    try:
        os.makedirs(OMFITsessionsDir)
    except OSError:
        if os.path.exists(OMFITsessionsDir):
            pass  # to handle simultaneous start of OMFIT sessions
        else:
            raise

# create an OMFITbinsDir directory for each workstation
OMFITbinsDir = OMFITtmpDir + '_local' + os.sep + 'bins'
if not os.path.exists(OMFITbinsDir):
    try:
        os.makedirs(OMFITbinsDir)
    except OSError:
        if os.path.exists(OMFITbinsDir):
            pass  # to handle simultaneous start of OMFIT sessions
        else:
            raise

# the OMFITcontrolmastersDir stores the sockets for SSH controlmaster functionality
OMFITcontrolmastersDir = OMFITtmpDir + '_local' + os.sep + 'controlmasters'
if not os.path.exists(OMFITcontrolmastersDir):
    try:
        os.makedirs(OMFITcontrolmastersDir)
    except OSError:
        if os.path.exists(OMFITcontrolmastersDir):
            pass  # to handle simultaneous start of OMFIT sessions
        else:
            raise
os.chmod(OMFITcontrolmastersDir, 0o700)


def safe_eval_environment_variable(var, default):
    '''
    Safely evaluate environmental variable

    :param var: string with environmental variable to evaluate

    :param default: default value for the environmental variable
    '''
    try:
        return eval(os.environ.get(var, repr(default)))
    except Exception:
        return os.environ.get(var, repr(default))


# If we are runnnig the whole OMFIT framework, and it's a public installation
# then by default users' Python modules paths are rejected
# Users can set OMFIT_CLEAN_PYTHON_ENVIRONMENT=0 to disable all clearing
# or at least set OMFIT_CLEAN_PYTHON_ENVIRONMENT=1 to disable the warning related to such clearing
if 'omfit_classes.startup_framework' in sys.modules and safe_eval_environment_variable('OMFIT_CLEAN_PYTHON_ENVIRONMENT', True):
    _unacceptable_paths = ['/usr/local', os.environ['HOME'] + '/.local', os.environ['HOME'] + '/Library'] + os.environ.get(
        'PYTHONPATH', ''
    ).split(':')
    _unacceptable_paths = [_up for _up in _unacceptable_paths if _up]
    _invalid_paths = []
    for _path in sys.path:
        for _up in _unacceptable_paths:
            if (
                _path.startswith(os.path.abspath(_up))
                and _path in sys.path
                and _path not in _invalid_paths
                and os.path.exists(_path)
                and os.path.abspath(_path) != OMFITsrc
                and not os.path.abspath(_path).startswith(sys.executable.split('bin')[0])
            ):
                _invalid_paths.append(_path)
    _invalid_paths = sorted(_invalid_paths)
    if len(_invalid_paths):
        if os.path.exists(os.sep.join([OMFITsrc, '..', 'public'])) or 'OMFIT_CLEAN_PYTHON_ENVIRONMENT' in os.environ:
            if 'OMFIT_CLEAN_PYTHON_ENVIRONMENT' not in os.environ:
                print('=' * 80)
                print('Warning: The following user-defined paths have been removed from your Python environment:')
                for _path in _invalid_paths:
                    print('  %s' % _path)
                print('To use your original Python environment set OMFIT_CLEAN_PYTHON_ENVIRONMENT=0')
                print('=' * 80)
            for _path in _invalid_paths:
                sys.path.remove(_path)
        else:
            print('=' * 80)
            print('Warning: The following user-defined paths are in your Python environment:')
            for _path in _invalid_paths:
                print('  %s' % _path)
            print('To use a clean Python environment set OMFIT_CLEAN_PYTHON_ENVIRONMENT=1')
            print('To suppress this warning message  set OMFIT_CLEAN_PYTHON_ENVIRONMENT=0')
            print('=' * 80)

# Keep track of original environment versions before they get modified within OMFIT
for k in ['PATH', 'LD_LIBRARY_PATH', 'DYLD_LIBRARY_PATH']:
    if f'ORIGINAL_{k}' not in os.environ and k in os.environ:
        os.environ[f'ORIGINAL_{k}'] = os.environ[k]
# Add directory of python executable to PATH
if os.path.split(sys.executable)[0] not in os.environ['PATH']:
    os.environ['PATH'] = os.path.split(sys.executable)[0] + os.path.pathsep + os.environ['PATH']

# warnings
import warnings


def warning_on_one_line(message, category, filename, lineno, file=None, line=None):
    # Suppress DeprecationWarning and FutureWarning for imports to avoid lots of red-text from 3rd party packages
    # when running Python 2 with `-3` option to warn about Python 3.x incompatibilities
    if category in [DeprecationWarning, FutureWarning] and OMFITsrc not in filename and OMFITtmpDir not in filename:
        return ''
    message = str(message)
    where = os.path.split(filename)[1] + '@' + str(lineno)
    text = []
    for k, line in enumerate(message.strip('\n').split('\n')):
        if k == 0:
            text.append(category.__name__ + ': ' + line + '\n')
        else:
            text.append(' ' * (len(category.__name__) + 2) + line + '\n')
    text = ''.join(text).strip('\n')
    # do not let Python 2 int division slip
    if 'classic int division' in text or "'U' mode is deprecated" in text:
        raise Exception(text)
    return text + ' (' + where + ')\n'


warnings.formatwarning = warning_on_one_line
warnings.filterwarnings('always', message='classic int division')
if os.environ['USER'] in ['meneghini', 'smithsp', 'eldond']:
    warnings.filterwarnings('always', category=DeprecationWarning)
    warnings.filterwarnings('always', category=FutureWarning)
warnings.filterwarnings('ignore', message='invalid escape sequence')
if os.environ['USER'] in [
    'meneghini',
    'smithsp',
    'eldond',
    'bpatel2',
    'logannc',
    'thomek',
    'avdeevag',
    'jmcclena',
    'slendebroekt',
    'haskeysr',
]:
    warnings.filterwarnings('error', category=DeprecationWarning, message='Using a DataArray object to construct a variable is ambiguous.*')
else:
    warnings.filterwarnings(
        'always', category=DeprecationWarning, message='Using a DataArray object to construct a variable is ambiguous.*'
    )

if os.environ['USER'] in ['eldond']:
    behavior = 'always'  # Behavior for not serious but not 100% trivial things; choose 'ignore', 'once', or 'always'
    warnings.filterwarnings('error')  # TODO: take this out when done?
    warnings.filterwarnings('ignore', category=ResourceWarning)
    warnings.filterwarnings('ignore', message='OMFIT is unable to create script backup copies')  # I don't care
    warnings.filterwarnings('ignore', category=UserWarning, message='.*Font family .* not found.*')  # Fallback is fine
    warnings.filterwarnings('ignore', category=UserWarning, message='No `boutdata`.*')
    warnings.filterwarnings(behavior, category=UserWarning, message='Tight layout not applied.*')  # Not serious
    warnings.filterwarnings(behavior, category=DeprecationWarning, message='the imp module is deprecated in favour of importlib.*')
    warnings.filterwarnings(behavior, category=DeprecationWarning, message='PILLOW_VERSION is deprecated.*')

    # This is not serious, but it is annoying
    from numpy import VisibleDeprecationWarning

    warnings.filterwarnings('once', category=VisibleDeprecationWarning)
    # From importing old? xarray versions. Can't be solved but by changing/upgrading xarray, or ignoring.
    warnings.filterwarnings("ignore", category=DeprecationWarning, message='Using or importing the ABCs*')  # xarray
    # TODO: update OMFIT's xarray requirement to a newer version

    warnings.filterwarnings(behavior, category=SyntaxWarning)  # Needed for MDSplus with py3.8: "is not" with literal


# These should never be elevated to errors:
warnings.filterwarnings('always', category=UserWarning, message='Unable to import omfit_plot.*')

# base imports
import ast
import socket
import re
import subprocess
import distutils
import time
import platform
import difflib
import tempfile
import datetime
import inspect
import functools
import glob
from collections import OrderedDict
from pprint import pprint
from omfit_classes.exceptions_omfit import *

special1 = []

# store file location for later OMFITobject files garbage collection
_allOMFITobjects = {}

# The content of this file is loaded by OMFITsetup and as such
# it should not depend on the add-on Python package that OMFIT
# requires (Numpy, Matplotlib, Tk, ...)

# ---------------------
# OMFITaux: dictionary is used to keep track of auxiliary informations of OMFIT
# ---------------------
class _OMFITauxiliary(dict):
    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls, *args, **kwargs)
        instance.defaults = {}
        return instance

    def __init__(self):
        self.defaults['lastUserError'] = ['']
        self.defaults['lastReportedUserError'] = ['']

        self.defaults['lastBrowsedDirectory'] = ''
        self.defaults['lastBrowsed'] = {}

        self.defaults['GUI'] = None
        self.defaults['rootGUI'] = None
        self.defaults['treeGUI'] = None
        self.defaults['console'] = None
        self.defaults['virtualKeys'] = False

        self.defaults['hardLinks'] = False

        self.defaults['quickPlot'] = {}

        self.defaults['prun_process'] = []
        self.defaults['prun_nprocs'] = []
        self.defaults['pythonRunWindows'] = []
        self.defaults['haltWindow'] = None

        self.defaults['MDSserverReachable'] = {}
        self.defaults['RDBserverReachable'] = {}
        self.defaults['batch_js'] = {}
        self.defaults['sysinfo'] = {}
        self.defaults['sshTunnel'] = {}

        self.defaults['lastActivity'] = time.time()

        self.defaults['noCopyToCWD'] = False

        self.defaults['lastRunModule'] = ''
        self.defaults['moduleSkeletonCache'] = None

        self.defaults['debug'] = 0

        self.defaults['dynaLoad_switch'] = True

        self.update(copy.deepcopy(self.defaults))

    def __getitem__(self, key):
        # if 'lastBrowsedDirectory' does not exisits recurse directory backwards to find valid directory root
        if key == 'lastBrowsedDirectory' and key in self:
            tmp = super().__getitem__(key)
            tmp = os.path.abspath(os.path.expandvars(os.path.expanduser(tmp)))
            for k in range(len(tmp)):
                if os.path.exists(tmp):
                    return tmp
                tmp = os.path.split(tmp)[0]
            return os.environ['HOME']
        return super().__getitem__(key)


OMFITaux = _OMFITauxiliary()


def hasattr_no_dynaLoad(object, attribute):
    """
    same as `hasattr` function but does not trigger dynamic loading
    """
    try:
        dynaLoadBkp = OMFITaux['dynaLoad_switch']
        OMFITaux['dynaLoad_switch'] = False
        return hasattr(object, attribute)
    finally:
        OMFITaux['dynaLoad_switch'] = dynaLoadBkp


# ---------------------
# Decorators @_available_to_user are used to define which functions should appear in the OMFIT documentation
# ---------------------
OMFITaux['OMFITmath_functions'] = []


def _available_to_user_math(f):
    OMFITaux['OMFITmath_functions'].append(f)
    return f


OMFITaux['OMFITutil_functions'] = []


def _available_to_user_util(f):
    OMFITaux['OMFITutil_functions'].append(f)
    return f


OMFITaux['OMFITplot_functions'] = []


def _available_to_user_plot(f):
    OMFITaux['OMFITplot_functions'].append(f)
    return f


# ---------------------
# evaluate expressions
# ---------------------
def isinstance_str(inv, cls):
    """
    checks if an object is of a certain type by looking at the class name (not the class object)
    This is useful to circumvent the need to load import Python modules.

    :param inv: object of which to check the class

    :param cls: string or list of string with the name of the class(es) to be checked

    :return: True/False
    """
    if isinstance(cls, str):
        cls = [cls]
    if hasattr(inv, '__class__') and hasattr(inv.__class__, '__name__') and inv.__class__.__name__ in cls:
        return True
    return False


def evalExpr(inv):
    """
    Return the object that dynamic expressions return when evaluated
    This allows OMFITexpression('None') is None to work as one would expect.
    Epxressions that are invalid they will raise an OMFITexception when evaluated

    :param inv: input object

    :return:

        * If inv was a dynamic expression, returns the object that dynamic expressions return when evaluated

        * Else returns the input object

    """
    if isinstance_str(inv, 'OMFITexpressionError'):
        raise OMFITexception('Invalid expression')
    elif isinstance_str(inv, ['OMFITexpression', 'OMFITiterableExpression']) and hasattr(inv, '_value_'):
        tmp = inv._value_()
        if isinstance_str(tmp, 'OMFITexpressionError'):
            raise OMFITexception('Invalid expression:\n' + inv.error)
        return tmp
    else:
        return inv


def freezeExpr(me, remove_OMFITexpressionError=False):
    """
    Traverse a dictionary and evaluate OMFIT dynamic expressions in it
    NOTE: This function operates in place

    :param me: input dictionary

    :param remove_OMFITexpressionError: remove entries that evaluate as OMFITexpressionError

    :return: updated dictionary
    """
    for kid in list(me.keys()):
        if isinstance_str(me[kid], ['OMFITexpression', 'OMFITiterableExpression']):
            try:
                me[kid] = evalExpr(me[kid])
            except Exception:
                del me[kid]
                continue
        elif isinstance_str(me[kid], 'OMFITexpressionError'):
            if remove_OMFITexpressionError:
                del me[kid]
                continue
            else:
                raise OMFITexception('Invalid expression:\n' + me[kid].error)
        if isinstance(me[kid], dict):
            freezeExpr(me[kid], remove_OMFITexpressionError=remove_OMFITexpressionError)


# ---------------------
# checktypes
# ---------------------
def is_none(inv):
    """
    This is a convenience function to evaluate if a object or an expression is None
    Use of this function is preferred over testing if an expression is None
    by using the == function. This is because np arrays evaluate == on a per item base

    :param inv: input object

    :return: True/False
    """
    if inv is None:
        return True
    elif isinstance_str(inv, ['OMFITexpression', 'OMFITiterableExpression']):
        return evalExpr(inv) is None
    return False


def is_bool(value):
    """
    Convenience function check if value is boolean

    :param value: value to check

    :return: True/False
    """
    return value in [True, False]


def is_int(value):
    """
    Convenience function check if value is integer

    :param value: value to check

    :return: True/False
    """
    import numpy as np

    return isinstance(value, (int, np.integer))


def is_float(value):
    """
    Convenience function check if value is float

    :param value: value to check

    :return: True/False
    """
    import numpy as np

    return isinstance(value, (float, np.floating))


def is_numeric(value):
    """
    Convenience function check if value is numeric

    :param value: value to check

    :return: True/False
    """
    try:
        0 + value
        return True
    except TypeError:
        return False


def is_number_string(my_string):
    """
    Determines whether a string may be parsed as a number
    :param my_string: string
    :return: bool
    """
    try:
        float(my_string)
    except ValueError:
        return False
    else:
        return True


def is_alphanumeric(value):
    """
    Convenience function check if value is alphanumeric

    :param value: value to check

    :return: True/False
    """
    if isinstance(value, str):
        return True
    try:
        0 + value
        return True
    except TypeError:
        return False


def is_array(value):
    """
    Convenience function check if value is list/tuple/array

    :param value: value to check

    :return: True/False
    """
    import numpy as np

    return isinstance(value, (list, tuple, np.ndarray))


def is_string(value):
    """
    Convenience function check if value is string

    :param value: value to check

    :return: True/False
    """
    return isinstance(value, str)


def is_email(value):
    if isinstance(value, str):
        return re.findall('i?[\w\-\.]+@[\w\-\.]+\.[\w\-\.]+', value)


def is_int_array(val):
    """
    Convenience function check if value is a list/tuple/array of integers

    :param value: value to check

    :return: True/False
    """
    import numpy as np

    if is_array(val):
        try:
            tmp = np.atleast_1d(val).astype(int)
        except TypeError:
            return False
        if np.all(np.atleast_1d(val) == tmp):
            return True
    return False


# ---------------------
# Printing
# ---------------------
streams_q = Queue.Queue()


class qRedirector(object):
    '''A class for redirecting stdout and stderr to this Text widget'''

    def __init__(self, tag='STDOUT'):
        self.tag = tag

    def write(self, string):
        streams_q.put((string, self.tag), block=False, timeout=0)

    def flush(self):
        pass


class _Streams(dict):
    tags = {
        'STDOUT': ('black', 'RESET'),
        'STDERR': ('red3', 'RED'),
        'DEBUG': ('gold4', 'YELLOW'),
        'PROGRAM_OUT': ('blue', 'BLUE'),
        'PROGRAM_ERR': ('purple', 'MAGENTA'),
        'INFO': ('forest green', 'GREEN'),
        'WARNING': ('DarkOrange2', 'YELLOW'),
        'HIST': ('dark slate gray', 'CYAN'),
        'HELP': ('PaleGreen4', 'CYAN'),
    }

    def __new__(cls):
        return dict.__new__(cls)

    def __init__(self):
        self.stderr = sys.stderr
        self.stdout = sys.stdout
        self.setDefaults()
        self.bkpStack = []

    def setDefaults(self):
        for k in self.tags:
            if 'ERR' in k:
                self[k] = self.stderr
            else:
                self[k] = self.stdout

    def backup(self):
        self.bkpStack.append(list(self.items()))

    def restore(self):
        for k, v in self.bkpStack.pop():
            self[k] = v
        sys.stdout = self['STDOUT']
        sys.stderr = self['STDERR']


_streams = _Streams()


class console_color:
    @staticmethod
    def BLACK(x=''):
        return '\033[30m' + str(x) + '\033[0m'

    @staticmethod
    def RED(x=''):
        return '\033[31m' + str(x) + '\033[0m'

    @staticmethod
    def GREEN(x=''):
        return '\033[32m' + str(x) + '\033[0m'

    @staticmethod
    def YELLOW(x=''):
        return '\033[33m' + str(x) + '\033[0m'

    @staticmethod
    def BLUE(x=''):
        return '\033[34m' + str(x) + '\033[0m'

    @staticmethod
    def MAGENTA(x=''):
        return '\033[35m' + str(x) + '\033[0m'

    @staticmethod
    def CYAN(x=''):
        return '\033[36m' + str(x) + '\033[0m'

    @staticmethod
    def WHITE(x=''):
        return '\033[37m' + str(x) + '\033[0m'

    @staticmethod
    def UNDERLINE(x=''):
        return '\033[4m' + str(x) + '\033[0m'

    @staticmethod
    def RESET(x=''):
        return '\033[0m' + str(x) + '\033[0m'


def tag_print(*objects, **kw):
    """
    Works like the print function, but used to print to GUI (if GUI is available).
    The coloring of the GUI print is determined by the `tag` parameter.

    :param \*objects: string/objects to be printed

    :param sep: separator (default: ' ')

    :param sep: new line character (default: '\\\\n')

    :param tag: one of the following:

        * 'STDOUT'
        * 'STDERR'
        * 'DEBUG'
        * 'PROGRAM_OUT'
        * 'PROGRAM_ERR'
        * 'INFO'
        * 'WARNING'
        * 'HIST'
        * 'HELP'
    """
    tag = kw.get('tag', '')
    tag_override = os.environ.get('OMFIT_TAG_PRINT_STREAM_OVERRIDE', '')
    if tag_override in _streams:
        tag = tag_override
    if sys.stdout is not sys.__stdout__ and tag in _streams:  # <--- check if the stdout is redirected and tag is recognized
        return print(*objects, sep=kw.pop('sep', ' '), end=kw.pop('end', '\n'), file=_streams[tag])
    else:
        file = sys.__stderr__ if 'ERR' in tag else sys.__stdout__
        # colored terminal
        if sys.stdout.isatty():
            tmp = StringIO()
            print(*objects, sep=kw.pop('sep', ' '), end=kw.pop('end', '\n'), file=tmp)
            return print(getattr(console_color, _streams.tags[tag][1])(tmp.getvalue()), sep='', end='', file=file)
        # standard terminal
        return print(*objects, sep=kw.pop('sep', ' '), end=kw.pop('end', '\n'), file=file)


def printi(*objects, **kw):
    """
    Function to print with `INFO` style

    :param \*objects: what to print

    :param \**kw: keywords passed to the `print` function

    :return: return from `print` function
    """
    kw['tag'] = 'INFO'
    if int(os.environ.get('OMFIT_VISUAL_CUES', '0')):
        objects = ['^' + '\n^'.join(str(x).splitlines()) for x in objects]
    return tag_print(*objects, **kw)


def pprinti(*objects, **kw):
    """
    Function to pretty-print with `INFO` style

    :param \*objects: what to print

    :param \**kw: keywords passed to the `print` function

    :return: return from `pprint` function
    """
    kw['stream'] = _streams['INFO']
    return pprint(*objects, **kw)


def printe(*objects, **kw):
    """
    Function to print with `ERROR` style

    :param \*objects: what to print

    :param \**kw: keywords passed to the `print` function

    :return: return from `print` function
    """
    kw['tag'] = 'STDERR'
    if int(os.environ.get('OMFIT_VISUAL_CUES', '0')):
        objects = ['!' + '\n!'.join(str(x).splitlines()) for x in objects]
    return tag_print(*objects, **kw)


def pprinte(*objects, **kw):
    """
    Function to pretty-print with `STDERR` style

    :param \*objects: what to print

    :param \**kw: keywords passed to the `pprint` function

    :return: return from `pprint` function
    """
    kw['stream'] = _streams['STDERR']
    return pprint(*objects, **kw)


def printw(*objects, **kw):
    """
    Function to print with `WARNING` style

    :param \*objects: what to print

    :param \**kw: keywords passed to the `print` function

    :return: return from `print` function
    """
    kw['tag'] = 'WARNING'
    if int(os.environ.get('OMFIT_VISUAL_CUES', '0')):
        objects = ['@' + '\n@'.join(str(x).splitlines()) for x in objects]
    return tag_print(*objects, **kw)


def pprintw(*objects, **kw):
    """
    Function to pretty-print with `WARNING` style

    :param \*objects: what to print

    :param \**kw: keywords passed to the `pprint` function

    :return: return from `pprint` function
    """
    kw['stream'] = _streams['WARNING']
    return pprint(*objects, **kw)


OMFITaux['debug_logs'] = _debug_logs = {}


def printd(*objects, **kw):
    """
    Function to print with `DEBUG` style.
    Printing is done based on environmental variable OMFIT_DEBUG
    which can either be a string with an integer (to indicating a debug level)
    or a string with a debug topic as defined in OMFITaux['debug_logs']

    :param \*objects: what to print

    :param level: minimum value of debug for which printing will occur

    :param \**kw: keywords passed to the `print` function

    :return: return from `print` function
    """
    # log debug history
    debug_topic = kw.pop('topic', 'uncategorized')
    if debug_topic not in _debug_logs:
        _debug_logs[debug_topic] = []
    _tmp_stream = StringIO()
    if int(os.environ.get('OMFIT_VISUAL_CUES', '0')):
        objects = ['$' + '\n$'.join(str(x).splitlines()) for x in objects]
    print(*objects, sep=kw.get('sep', ' '), end=kw.get('end', '\n'), file=_tmp_stream)
    _debug_logs[debug_topic].append(str(time.time()) + ": " + _tmp_stream.getvalue())
    _debug_logs[debug_topic] = _debug_logs[debug_topic][-100:]

    kw['tag'] = 'DEBUG'

    doPrint = False
    try:
        # print by level
        debug_level = int(os.environ.get('OMFIT_DEBUG', '0'))  # this will raise an ValueError if OMFIT_DEBUG is a string
        if debug_level >= kw.pop('level', 1) or debug_level < 0:
            doPrint = True
    except ValueError:
        # print by topic
        if os.environ.get('OMFIT_DEBUG', '') == debug_topic:
            doPrint = True
    finally:
        if doPrint:
            terminal_debug = safe_eval_environment_variable('OMFIT_TERMINAL_DEBUG', False)
            if terminal_debug > 0:
                printt(*objects, **kw)
            if (terminal_debug % 2) == 0:  # Even numbers print to the OMFIT console
                return tag_print(*objects, **kw)


def printt(*objects, **kw):
    """
    Function to force print to terminal instead of GUI

    :param \*objects: what to print

    :param err: print to standard error

    :param \**kw: keywords passed to the `print` function

    :return: return from `print` function
    """
    if int(os.environ.get('OMFIT_VISUAL_CUES', '0')):
        objects = ['%' + '\n%'.join(str(x).splitlines()) for x in objects]
    try:
        file = sys.__stderr__ if kw.pop('err', False) else sys.__stdout__
        return print(*objects, sep=kw.pop('sep', ' '), end=kw.pop('end', '\n'), file=file)
    except IOError:
        pass


class quiet_environment(object):
    """
    This environment quiets all output (stdout and stderr)

    >> print('hello A')
    >> with quiet_environment() as f:
    >>     print('hello B')
    >>     print('hello C')
    >>     tmp=f.stdout
    >> print('hello D')
    >> print(tmp)
    """

    def __enter__(self):
        self.streams_bkp = {}
        self.streams_bkp.update(_streams)
        sys.stdout = StringIO()
        sys.stderr = StringIO()
        for k in _streams:
            if 'ERR' in k:
                _streams[k] = sys.stderr
            else:
                _streams[k] = sys.stdout
        return self

    @property
    def stdout(self):
        return sys.stdout.getvalue()

    @property
    def stderr(self):
        return sys.stderr.getvalue()

    def __exit__(self, type, value, traceback):
        _streams.update(self.streams_bkp)
        sys.stdout = _streams['STDOUT']
        sys.stderr = _streams['STDERR']


def size_of_dir(folder):
    """
    function returns the folder size as a number

    :param folder: directory path

    :return: size in bytes
    """
    size = 0
    if isinstance(folder, str) and os.path.exists(folder) and os.path.isdir(folder):
        for path, dirs, files in os.walk(folder):
            for f in files:
                try:
                    size += os.path.getsize(os.path.join(path, f))
                except OSError:
                    pass
    return size


def sizeof_fmt(filename, separator='', format=None, unit=None):
    """
    function returns a string with nicely formatted filesize

    :param filename: string with path to the file or integer representing size in bytes

    :param separator: string between file size and units

    :param format: default None, format for the number

    :param unit: default None, unit of measure

    :return: string with file size
    """

    if unit in ['b', 'B']:
        unit = 'bytes'

    def _size(num):
        for u in ['bytes', 'kB', 'MB', 'GB']:
            if u == unit or (unit is None and num < 1024.0):
                break
            num /= 1024.0
        else:
            u = 'TB'
        if isinstance(format, str):
            f = format
        elif isinstance(format, dict) and u in list(format.keys()):
            f = format[u]
        else:
            f = '%3.1f'
        return f % num + separator + u

    if is_int(filename) and filename >= 0:
        return _size(filename)

    if isinstance(filename, str) and os.path.exists(filename):
        return _size(os.path.getsize(filename))

    else:
        return 'N/A'


def encode_ascii_ignore(string):
    """
    This function provides fail-proof conversion of str to ascii

    Note: not ASCII characters are ignored

    :param string: str string

    :return: ascii scring
    """
    import numpy as np

    string = np.array([ord(x) for x in string])
    return ''.join([chr(x) for x in string[np.where(string < 128)[0]]])


def is_binary_file(filename):
    """
    Detect if a file is binary or ASCII

    :param filename: path to the file

    :return: True if binary file else False
    """
    textchars = bytearray({7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100)) - {0x7F})
    with open(filename, 'rb') as f:
        return bool(f.read().translate(None, textchars))


def wrap(text, width):
    r"""
    A word-wrap function that preserves existing line breaks
    and most spaces in the text. Expects that existing line
    breaks are posix newlines (\n).

    :param text: text to be wrapped

    :param width: maximum line width
    """
    from functools import reduce

    return reduce(
        lambda line, word, width=width: '%s%s%s'
        % (line, ' \n'[(len(line) - line.rfind('\n') - 1 + len(word.split('\n', 1)[0]) >= width)], word),
        text.split(' '),
    )


@_available_to_user_util
def ascii_progress_bar(
    n,
    a=0,
    b=100,
    mess='',
    newline=False,
    clean=False,
    width=20,
    fill='#',
    void='-',
    style=' [{sfill}{svoid}] {perc:3.2f}% {mess}',
    tag='INFO',
    quiet=False,
):
    """
    Displays an ASCII progress bar

    :param n: current value OR iterable

    :param a: default 0, start value (ignored if n is an iterable)

    :param b: default 100, end value  (ignored if n is an iterable)

    :param mess: default blank, message to be displayed

    :param newline: default False, use newlines rather than carriage returns

    :param clean: default False, clean out progress bar when end is reached

    :param width: default 20, width in characters of the progress bar

    :param fill: default '#', filled progress bar character

    :param void: default '-', empty progress bar character

    :param style: default ' [{sfill}{svoid}] {perc:3.2f}% {mess}' full format string

    :param tag: default 'HELP', see tag_print()

    :param quiet: do not print

    Example::
        for n in ascii_progress_bar(np.linspace(12.34, 56.78, 4), mess=lambda x:f'{x:3.3}'):
            OMFITx.Refresh() # will slow things down
    """

    def ascii_progress_bar_base(n, a, b, mess, newline, clean, width, fill, void, style, tag, quiet, dtime=0):
        # handle manual iteration
        if not (a < b and a <= n and n <= b):
            return
        perc = 100.0 * (n + 1 - a) / (b + 1 - a)
        nfill = int(round(width * perc / 100.0))
        sfill = fill * nfill
        svoid = void * (width - nfill)
        if newline:
            buff = ''
        else:
            buff = '\r'
        buff += style.format(**locals())
        if newline or (n == b and not clean):
            buff += '\n'
        elif n == b and clean:
            buff = '\r' + ' ' * len(buff) + '\r'
        if not quiet:
            tag_print(buff, tag=tag, end='')
        return n

    def ascii_progress_bar_iterable(n, **kw):
        data = list(n)  # we need to know the length of the data in case `n` was a generator
        kw['a'] = 0
        kw['b'] = len(data) - 1
        if callable(kw['mess']):
            messages = list(map(kw['mess'], data))
        else:
            messages = kw['mess']
            if isinstance(kw['mess'], str):
                messages = [kw['mess']] * len(data)
            elif isinstance(kw['mess'], np.ndarray):
                messages = list(messages)
        if not kw['newline']:
            messages = copy.copy(messages)
            if not len(messages):
                messages.append('')
            messages[-1] = ''
        for n, d in enumerate(data):
            kw['mess'] = messages[n]
            if '{dtime' in style:
                t0 = time.time()
                yield d
                kw['dtime'] = time.time() - t0
                ascii_progress_bar_base(n, **kw)
            else:
                ascii_progress_bar_base(n, **kw)
                yield d
        return

    import numpy as np

    if np.iterable(n):
        return ascii_progress_bar_iterable(
            n, a=a, b=b, mess=mess, newline=newline, clean=clean, width=width, fill=fill, void=void, style=style, tag=tag, quiet=quiet
        )
    else:
        return ascii_progress_bar_base(
            n, a=a, b=b, mess=mess, newline=newline, clean=clean, width=width, fill=fill, void=void, style=style, tag=tag, quiet=quiet
        )


def load_dynamic(module, path):
    """
    Load and initialize a module implemented as a dynamically loadable shared library and return its module object.
    If the module was already initialized, it will be initialized again.
    Re-initialization involves copying the __dict__ attribute of the cached instance of the module over the value used in the module cached in sys.modules.
    Note: using shared libraries is highly system dependent, and not all systems support it.

    :param name: name used to construct the name of the initialization function: an external C function called initname() in the shared library is called

    :param pathname: path to the shared library.
    """
    import importlib

    spec = importlib.util.spec_from_file_location(module, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------
# processes
# ---------------------
def is_running(process):
    """
    This function retuns True or False depending on whether a process is running or not

    This relies on grep of the `ps axw` command

    :param process: string with process name or process ID

    :return: False if process is not running, otherwise line of `ps` command
    """
    process = str(process)
    s = subprocess.Popen([system_executable('ps'), "axw"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    std_out, std_err = list(map(b2s, s.communicate()))
    for item in std_out.split('\n'):
        if re.search(' ' + process + ' ', item) or re.search(r'^' + process + ' ', item):
            return item
    return False


def kill_subprocesses(process=None):
    """
    kill all of the sub-processes of a given process

    :param process: process of which sub-processes will be killed
    """
    if process is None:
        process = os.getpid()
    process = str(process)
    if int(process) == 1:
        raise Exception('Cowardly refusing to kill INIT process')

    if os.name == 'nt':  # Windows
        print('Killing ', process, os.getpid())
        os.system(f'taskkill /PID {process} /T /F')

    else:
        s = subprocess.Popen(
            [system_executable('pgrep'), "-P", process], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        std_out, std_err = list(map(b2s, s.communicate()))
        output = [_f for _f in [x.strip() for x in std_out.split('\n')] if _f]
        printi('killing sub-processes: ' + ', '.join(output))
        for item in output:
            ps = is_running(item)
            if ps:
                printi(ps)
                os.kill(int(item), 9)


def memuse(as_bytes=False, **kw):
    """
    return memory usage by current process

    :param as_bytes: return memory as number of bytes

    :param \**kw: keywords to be passed to `sizeof_fmt()`

    :return: formatted string with usage expressed in kB, MB, GB, TB
    """
    try:
        import psutil

        process = psutil.Process(os.getpid())
        memory = int(process.memory_info().rss)
    except ImportError:
        memory = -1
    if as_bytes:
        return memory
    memuse = sizeof_fmt(memory, **kw)
    return memuse


# maximum length of line in shell
def _arg_max():
    s = subprocess.Popen([system_executable('getconf'), 'ARG_MAX'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    std_out, std_err = list(map(b2s, s.communicate()))
    ARG_MAX = int(std_out.strip())
    return ARG_MAX


try:
    ARG_MAX = _arg_max()
except Exception:
    # http://www.in-ulm.de/~mascheck/various/argmax/
    ARG_MAX = 4096
# hardwire to 4096
ARG_MAX = 4096

_executables_cache = {}


def system_executable(executable, return_details=False):
    """
    function that returns the full path of the executable

    :param executable: executable to return the full path of

    :param return_details: return additional info for some commands (e.g. rsync)

    :return: string with full path of the executable
    """
    if executable not in _executables_cache or os.sep not in _executables_cache[executable]:
        _executables_cache[executable] = {}

        if os.name == 'nt':
            cygwin_executable = os.path.join(os.environ['CYGWIN'], 'bin', executable + '.exe')
            if os.path.exists(cygwin_executable):
                _executables_cache[executable]['path'] = cygwin_executable
            else:
                _executables_cache[executable]['path'] = executable
        else:
            import distutils.spawn

            _executables_cache[executable]['path'] = distutils.spawn.find_executable(executable)

        if executable == 'rsync' and _executables_cache[executable]['path']:
            kwarg = dict(stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
            if os.name == 'nt':
                kwarg['creationflags'] = subprocess.CREATE_NEW_PROCESS_GROUP
            else:
                kwarg['preexec_fn'] = os.setsid
            s = subprocess.Popen([_executables_cache['rsync']['path'], '--version'], shell=False, **kwarg)
            std_out, std_err = list(map(b2s, s.communicate()))
            _executables_cache['rsync']['version'] = re.findall('version [0-9.]+', std_out.strip().split('\n')[0])[0].split()[1]
            if float('.'.join(_executables_cache['rsync']['version'].split('.')[:2])) >= 3.1:
                _executables_cache['rsync']['progress'] = '--info=progress2'
            else:
                _executables_cache['rsync']['progress'] = '--progress'

    if return_details:
        return _executables_cache[executable]
    else:
        return _executables_cache[executable]['path']


def python_environment():
    """
    returns string with module names that have __version__ attribute (similar to what `pip freeze` would do)
    """
    python_environment = {}
    for item in sorted(sys.modules.keys()):
        if not item.startswith('_'):
            try:
                has_version_info = hasattr(sys.modules[item], '__version__')
            except Exception:
                continue
            else:
                if has_version_info:
                    version = str(sys.modules[item].__version__)
                    version = re.sub('Revision:*', '', version)
                    version = re.sub('\$', '', version)
                    version = version.strip()
                    if version:
                        python_environment[item] = version

    # remove subpackage version that matches parent package version
    for item in list(python_environment.keys()):
        if '.' in item and item.split('.')[0] in python_environment:
            if python_environment[item] == python_environment[item.split('.')[0]]:
                del python_environment[item]

    # sorted list of lists
    return [[item, python_environment[item]] for item in sorted(list(python_environment.keys()), key=lambda x: x.lower())]


# ---------------------
# identification
# ---------------------
@_available_to_user_util
def is_localhost(server, looseCheck=True):
    """
    Checks if `server` is the localhost.
    If `server` is None or an empty string then returns True.
    `server` can be a string in the format username@server:port

    :param server: server string

    :param looseCheck: loosely check if `server` string is contained in the localhost names

    :return: True/False
    """
    import numpy as np

    if server == None or not len(server) or server in ['localhost', '127.0.0.1']:
        return 'localhost'

    server = str(server)
    server = parse_server(server)[2]

    if server == 'localhost':
        return 'localhost'

    if re.match('127\.0+\.0+\.0*1', server):
        return 'localhost'

    if not len(server):
        return 'localhost'
    else:
        if set(splitDomain(server)).intersection(_localhost_names):
            return 'localhost'
        elif looseCheck:
            for servlet in splitDomain(server):
                if np.any([item.lower().startswith(servlet.lower()) for item in _localhost_names if item]):
                    return 'localhost'
    return False


@_available_to_user_util
def is_server(serverA, serverB):
    """
    Checks if `serverA` and `serverB` are the same server

    :param serverA: server string

    :param serverB: server string

    :return: True/False
    """
    if is_localhost(serverA) and is_localhost(serverB):
        return True
    elif str(serverB) in str(serverA) or str(serverA) in str(serverB):
        return True
    else:
        return False


@_available_to_user_util
def is_institution(instA, instB):
    instA = tolist(evalExpr(instA), [None])
    instB = tolist(evalExpr(instB), [None])
    for A in instA:
        for B in instB:
            if A.upper() == B.upper():
                return True
    return False


# ---------------------
# Network
# ---------------------
def splitDomain(namesIn):
    if isinstance(namesIn, set):
        namesIn = list(namesIn)
    elif not isinstance(namesIn, list):
        namesIn = [namesIn]
    names = copy.copy(namesIn)
    for item in names:
        if isinstance(item, str) and re.findall('[a-zA-Z]', item):
            tmp = item.split('.')
            if len(tmp) > 1:
                names.append(tmp[0])
    return names


def _localhost():
    os.environ.setdefault('HOST', '')

    def returnHostname():
        try:
            # issues with .get local hostname
            socket.getaddrinfo(socket.gethostname(), 22)
            return socket.gethostname()
        except Exception:
            return '127.0.0.1'

    def find_synonims(myself):
        etc_hosts = []
        if os.path.exists('/etc/hosts'):
            with open('/etc/hosts', 'r') as f:
                for line in f.readlines():
                    tmp = line.strip().split('#')[0].split()
                    if len(tmp):
                        etc_hosts.append(tmp)

        synonims = set(splitDomain(myself))
        for name in list(synonims):
            for equivalent_names in etc_hosts:
                equivalent_names = splitDomain(equivalent_names)
                if name in equivalent_names:
                    synonims = synonims.union(set(equivalent_names))
        return synonims

    myself = [returnHostname(), '127.0.0.1', 'localhost', '']
    myself.extend([k[4][0] for k in socket.getaddrinfo(myself[0], 22)])
    if 'HOST' in os.environ and os.environ['HOST']:
        myself.append(os.environ['HOST'])
    # running find_sysnonims twice allows to deduce more synonims based on the ip addresses in /etc/hosts
    myself = find_synonims(find_synonims(myself))

    return myself


_localhost_names = _localhost()


def ping(host, timeout=2):
    """
    Function for pinging remote server

    :param host: host name to be pinged

    :param timeout: timeout time

    :return: boolean indicating if ping was successful
    """
    # -W option is waiting time in seconds
    # -c packets count
    with open(os.devnull, 'w') as nul_f:
        child = subprocess.Popen([system_executable('ping'), "-c1", '-W' + str(timeout), host], stderr=nul_f, stdout=subprocess.PIPE)
        while child.poll() is None:
            pass
        return not bool(child.poll())


def parse_server(server, default_username=os.environ['USER']):
    """
    parses strings in the form of username:password@server.somewhere.com:port

    :param server: input string

    :param default_username: what username to return if username@server is not specified

    :return: tuple of four strings with user,password,server,port
    """
    server = evalExpr(server)
    if server is None:
        server = ''
    if '@' in server:
        us = server.split('@')
        username = '@'.join(us[:-1])
        server = us[-1]
    else:
        username = default_username
    if ':' in username:
        username, password = username.split(':', 1)
    else:
        password = ''
    if ':' in server:
        server, port = server.split(':')
        port = str(int(port))  # to make sure the port is an integer
    else:
        port = '22'
    return username.strip(), password.strip(), server.strip(), port.strip()


def assemble_server(username='', password='', server='', port=''):
    """
    returns assembled server string in the form username:password@server.somewhere.com:port

    :param username: username

    :param password: password

    :param server: server

    :param port: port

    :returns: assembled server string
    """
    out = ''
    if username:
        out = username
        if password:
            out = out + ':' + password
        out = out + '@'
    if server:
        out = out + server
    else:
        out = out + 'localhost'
    if port:
        out = out + ':' + str(port)
    return out


def test_connection(username, server, port, timeout=1.0, ntries=1):
    """
    Function to test if connection is available on a given host and port number

    :param server: server to connect to

    :param port: TCP port to connect to

    :param timeout: wait for `timeout` seconds for connection to become available

    :param ntries: number of retries

    * ntries==1 means: check if connection is up

    * ntries>1 means: wait for connection to come up

    :return: boolean indicating if connection is available
    """

    connected = None

    # This is needed because apparently OMFIT['MainSettings'] doesn't exist outside the framework
    try:
        is_local = is_localhost(server)
    except KeyError:
        is_local = False

    # if there is a controlmaster present check if it is live
    if username is not None and not is_local:
        connected = controlmaster(username, server, port, None, check=True)

    connection = (str(server), int(port))
    if ntries == 1:
        printd('Check if connection ' + str(connection) + ' is up...', topic='connection')
    else:
        printd('Waiting for connection ' + str(connection) + ' to become available...', topic='connection')

    timeout = float(timeout)
    ntries = max([int(ntries), 1])
    dt = timeout / ntries

    t0 = time.time()
    t = 0
    while connected is None or (not connected and t <= timeout):
        t1 = time.time()

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(dt)
        try:
            connected = s.connect_ex(connection) == 0
            s.close()
        except Exception:
            pass

        if connected:
            printd('Connection ' + str(connection) + ' is open!', topic='connection')
        else:
            if ntries == 1:
                printd('Connection ' + str(connection) + ' is not open', topic='connection')
                break
            else:
                printd('Re-checking connection ' + str(connection), topic='connection')
                sleep(max([dt - (time.time() - t1), 0]))  # make sure to wait at least a total of `dt` seconds before the next retry
                t = time.time() - t0

    if not connected and ntries > 1 and t > timeout:
        printd('Connection ' + str(connection) + ' is not open: wait timed out', topic='connection')

    return connected


def sshOptions(sshName='OMFITssh'):
    sshlink = OMFITbinsDir + os.sep + sshName
    if not os.path.exists(sshlink):
        if os.path.islink(sshlink):
            try:
                os.remove(sshlink)  # remove a broken link
            except IOError:
                pass
        try:
            os.symlink(system_executable('ssh'), sshlink)
        except OSError:  # avoid issues with parallel processes creating the symlink at the same time
            pass
    xauth_exe = system_executable('xauth')
    if xauth_exe is None:
        xauth_opt = ''
        printd('No xauth found', topic='connection')
    else:
        xauth_opt = f' -o XAuthLocation={xauth_exe}'
    return (
        sshlink + ' -o StrictHostKeyChecking=no'
        ' -o CheckHostIP=no'
        ' -o Compression=yes'
        ' -o ForwardAgent=yes'
        ' -o NoHostAuthenticationForLocalhost=yes'
        ' -o PermitLocalCommand=no'
        ' -o ConnectTimeout=10'
        ' -o ServerAliveCountMax=5'
        ' -o ServerAliveInterval=3'
        ' -o TCPKeepAlive=no' + xauth_opt
    )


_nprocs_per_controlmaster = 5

_pexpect_cmd = {}  # this is necessary to prevent garbage collection


def ssh_connect_with_password(cmd, credential, test_connected, timeout=10, check_every=0.1):
    if not OMFITaux['GUI'] and os.environ.get('OMFIT_SETUP', '0') == '1':
        # this is used by `omfit -s` and may be done for non GUI workflows
        return os.system(cmd)
    if test_connected():
        return True

    # only the first process every _nprocs_per_controlmaster processes
    # setup the connection while the others wait for timeout seconds
    if 'prun_process' in OMFITaux and len(OMFITaux['prun_process']):
        if not len(OMFITaux['prun_process']):
            index = 0
        elif len(OMFITaux['prun_process']) == 1:
            index = OMFITaux['prun_process'][-1]
        else:
            import numpy as np

            index = np.prod((np.array(OMFITaux['prun_nprocs']) * np.array(OMFITaux['prun_process']))[:-1]) + OMFITaux['prun_process'][-1]
        setter = (index % _nprocs_per_controlmaster) == 0
        if setter:
            # sleep time is necessary to stagger ssh connections
            time.sleep(index // _nprocs_per_controlmaster)
        else:
            maxk = k = int(timeout / float(check_every))
            while k > 0:  # wait 10 seconds for controlmaster of this group to be setup
                if test_connected():
                    return True
                time.sleep(check_every)
                k -= 1

    # execute command
    printd('ssh_connect_with_password: ' + cmd, topic='connection')
    p = pexpect.spawn(cmd, env={v: os.environ[v] if v != 'SSH_ASKPASS' else False for v in os.environ}, timeout=None)
    _pexpect_cmd[str(credential), str(cmd)] = p
    # check if connected
    connected = False
    printd('Waiting for connection to ' + credential, topic='connection')
    maxk = k = int(timeout / float(check_every))
    npwd = 0
    try:
        while k > 0:  # wait 10 seconds
            if p.expect([pexpect.TIMEOUT, "(?i)Verification code:"], timeout=check_every):
                npwd += 1
                # do not ask for password more than 3 times
                if npwd >= 4:
                    break
                printi(b2s(p.before + p.after).strip())
                # if there is a GUI, then OMFITaux['GUI'] is not None, and we can use AskPassGUI
                if OMFITaux.get('GUI', None):
                    from utils import AskPassGUI

                    pwd, otp = AskPassGUI(credential, OTP=True).decrypt()
                else:
                    pwd, otp = AskPass(credential, OTP=True).decrypt()
                p.sendline(otp)
                p.expect([pexpect.TIMEOUT, "(?i)password:", "(?i)password\s*\+\s*OTP:"], timeout=10)
                p.sendline(pwd)
                k = maxk
            elif p.expect([pexpect.TIMEOUT, "(?i)password:", "(?i)password\s*\+\s*OTP:"], timeout=check_every):
                npwd += 1
                # do not ask for password more than 3 times
                if npwd >= 4:
                    break
                printi(b2s(p.before + p.after).strip())
                # if there is a GUI, then OMFITaux['GUI'] is not None, and we can use AskPassGUI
                if OMFITaux.get('GUI', None):
                    from utils import AskPassGUI

                    pwd_otp = ''.join(AskPassGUI(credential, force_ask=(npwd > 2), OTP=True).decrypt())
                else:
                    pwd_otp = ''.join(AskPass(credential, force_ask=(npwd > 2), OTP=True).decrypt())
                p.sendline(pwd_otp)
                k = maxk
            # we need to wait a minimum amount of time before declaring victory
            # this is to allow the password request to show up on the terminal
            elif (maxk - k) * check_every > 2.0 and test_connected():
                connected = True
                break
            k -= 1
    except EOF as _excp:
        tmp = re.findall('before \(last 100 chars\):.*', str(_excp))
        if tmp:
            raise EOF(':'.join(tmp[0].split(':')[1:]).strip('\'" \r\n'))
        else:
            raise
    if connected:
        printd('Connected to ' + credential, topic='connection')
    else:
        printd('Failed to connect to ' + credential, topic='connection')
    return connected


def controlmaster(username, server, port, credential, check=False):
    """
    Setup controlmaster ssh socket

    :param username: username of ssh connection

    :param server: host of ssh connection

    :param port: port of ssh connection

    :param credential: credential file to use for connection

    :param check: check that control-master exists and is open

    :return: [True/False] if `check=True` else string to be included to ssh command to use controlmaster
    """
    printd(username, server, port, credential, check, topic='connection')

    # use 10 connections per controlmaster to reflect default `maxsessions` setting of sshd servers
    if not len(OMFITaux['prun_process']):
        index = 0
    elif len(OMFITaux['prun_process']) == 1:
        index = OMFITaux['prun_process'][-1]
    else:
        import numpy as np

        index = np.prod((np.array(OMFITaux['prun_nprocs']) * np.array(OMFITaux['prun_process']))[:-1]) + OMFITaux['prun_process'][-1]
    filename = (
        OMFITcontrolmastersDir
        + os.sep
        + str(omfit_numeric_hash(str(assemble_server(username, '', server, port)), 8))
        + '__%d' % (index // _nprocs_per_controlmaster)
    )

    # test if controlmaster exists and is open
    if os.path.exists(filename):
        tmp = system_executable('ssh') + ' -o ControlPath=%s -O check %s' % (filename, filename)
        child = subprocess.Popen(tmp, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        for k in range(100):
            if child.poll() is not None:
                break
            sleep(0.1)
            if k == 10:
                printi('Waiting for server response on controlmaster %s' % filename)
        if child.poll() is None or child.poll() == 255 or not os.path.exists(filename):
            printd('Controlmaster exists but is closed: ' + filename, topic='connection')
            if not check and os.path.exists(filename):
                try:
                    os.remove(filename)
                except FileNotFoundError:
                    pass
            valid = False
            if child.poll() is None:
                child.terminate()
        else:
            printd('Controlmaster exists and is open: ' + filename, topic='connection')
            valid = True
        child.stdout.close()
        child.stderr.close()
    else:
        printd('Controlmaster does not exist: ' + filename, topic='connection')
        valid = False

    if check:
        printd('Controlmaster checked, and now returning', topic='connection')
        return valid

    if valid:
        printd('Using controlmaster: ' + filename, topic='connection')
    else:
        # create controlmaster
        if os.name == 'nt':
            cmd = (
                sshOptions('OMFITsshControlmaster') + ' -N -t -t -M -Y -S ' + filename + ' ' + username + '@' + server + ' -p ' + str(port)
            )
        else:
            cmd = (
                sshOptions('OMFITsshControlmaster')
                + ' -o ControlPersist=24h -N -t -t -M -Y -S '
                + filename
                + ' '
                + username
                + '@'
                + server
                + ' -p '
                + str(port)
            )

        printd('controlmaster: ' + cmd, topic='connection')
        connected = ssh_connect_with_password(
            cmd, credential, lambda: controlmaster(username, server, port, credential, True), timeout=10, check_every=1
        )
        if connected:
            printd('Created controlmaster: ' + filename, topic='connection')
        else:
            raise OMFITexception("%s\n\n\nCould not connect with:\n%s" % (credential, cmd))

    return ' -S ' + filename + ' '


def setup_ssh_tunnel(server, tunnel, forceTunnel=False, forceRemote=False, allowEmptyServerUsername=False):
    """
    This function sets up the remote ssh tunnel (if necessary) to connect to the server
    and returns the username,server,port triplet onto which to connect.

    :param server: string with remote server

    :param tunnel: string with via tunnel (multi-hop tunneling with comma separated list of hops)

    :param forceTunnel: force tunneling even if server is directly reachable (this is useful when servers check provenance of an IP)

    :param forceRemote: force remote connection even if server is localhost

    :param allowEmptyServerUsername: allow empty server username

    :return: username, server, port
    """

    if not isinstance(evalExpr(server), str):
        raise Exception('server must be a string')

    if not isinstance(evalExpr(tunnel), str):
        raise Exception('tunnel must be a string')

    # save original entries
    server0 = server
    tunnel0 = tunnel

    # see if server is localhost
    local = is_localhost(server0)
    if forceRemote or forceTunnel:
        if local and not forceTunnel:
            return (os.environ['USER'], 'localhost', '22')
        local = False

    # resolve nested multi-hop tunnels
    if ',' in tunnel0:
        hops = tunnel.split(',')
        tunnel0 = tunnel = hops[0]
        for server in hops[1:]:
            u, s, p = setup_ssh_tunnel(server, tunnel, forceTunnel=False, forceRemote=False, allowEmptyServerUsername=False)
            tunnel0 = tunnel = assemble_server(u, '', s, p)

    # calculate tunnel port and parse server/tunnel strings
    port_l = str(omfit_numeric_hash((str(server0) + str(tunnel0))) % (65535 - 49152) + 49152)
    username, password, server, port = parse_server(str(server0), default_username='')
    username_t, password_t, server_t, port_t = parse_server(str(tunnel), default_username='')

    # buffer localshost given as hostname
    if local:
        if len(server) and server0 + '-' + tunnel0 not in OMFITaux['sshTunnel'] and server != 'localhost':
            printi(server + ' is the local workstation')
        OMFITaux['sshTunnel'][server0 + '-' + tunnel0] = (username, '', port)
        return OMFITaux['sshTunnel'][server0 + '-' + tunnel0]

    # buffered connections
    if server0 + '-' + tunnel0 in OMFITaux['sshTunnel']:
        printd('Found buffered connection %s@%s:%s' % tuple(OMFITaux['sshTunnel'][server0 + '-' + tunnel0][:]), topic='connection')
        # since connection should be buffered we expect a quick response
        connected = test_connection(
            OMFITaux['sshTunnel'][server0 + '-' + tunnel0][0],
            OMFITaux['sshTunnel'][server0 + '-' + tunnel0][1],
            int(OMFITaux['sshTunnel'][server0 + '-' + tunnel0][2]),
            timeout=0.1,
            ntries=1,
        )
        if connected:
            return OMFITaux['sshTunnel'][server0 + '-' + tunnel0]
        else:
            del OMFITaux['sshTunnel'][server0 + '-' + tunnel0]

    # start by seeing if the tunnel was already established
    # checking for tunnel on localhost is faster than checking remote...
    if len(server_t):
        connected = test_connection(username, '127.0.0.1', int(port_l), timeout=0.1, ntries=1)
        if connected:
            printi('Found existing SSH tunnel ' + username + '@127.0.0.1:' + port_l + ' = ' + tunnel0 + ' --> ' + server0)
            OMFITaux['sshTunnel'][server0 + '-' + tunnel0] = (username, '127.0.0.1', port_l)
            return OMFITaux['sshTunnel'][server0 + '-' + tunnel0]

    # check that username was specified for server connection
    if not allowEmptyServerUsername and not username:
        raise OMFITexception(
            f'Start OMFIT and specify username explicitly under `File > Preferences > Remote Servers` for connection to server `{server0}`'
        )

    # see if server is directly reachable
    # remote: here where we need to give it some time, and we cannot query too much for risk of getting blacklisted
    if not forceTunnel:
        try:
            if not controlmaster(username, server, port, server0, check=True):
                try:
                    controlmaster(username, server, port, server0)
                except OMFITexception:
                    connected = False
            connected = controlmaster(username, server, port, server0, check=True)
        except EOF:  # do not raise pexpect.EOF, we need to keep going because some servers (eg. lac.epfl.ch) keep the door open but will drop the packet if not contacted via the tunnel
            connected = False
        if connected:
            printd('Server is directly reachable at %s@%s:%s' % (username, server, port), topic='connection')
            OMFITaux['sshTunnel'][server0 + '-' + tunnel0] = (username, server, port)
            return OMFITaux['sshTunnel'][server0 + '-' + tunnel0]

    # make or re-use tunnel
    if len(server_t):
        # check that username was specified for tunnel connection
        if not username_t:
            raise Exception('Specify username explicitly for connection to tunnel `%s`' % str(tunnel0))

        connected = False
        if len(OMFITaux['prun_process']):
            import numpy as np

            n = (
                np.random.rand() * 10
            )  # give it max 10 seconds to check if other processes have setup the connection (since localhost, we can check often)
            connected = test_connection(username, '127.0.0.1', int(port_l), timeout=n, ntries=10 * np.ceil(n))
        if connected:
            printi('Found existing SSH tunnel ' + username + '@127.0.0.1:' + port_l + ' = ' + tunnel0 + ' --> ' + server0)
        else:
            # setup the tunnel
            printi(
                'Starting SSH tunnel '
                + username
                + '@127.0.0.1:'
                + port_l
                + ' = '
                + username_t
                + '@'
                + server_t
                + ':'
                + port_t
                + ' --> '
                + username
                + '@'
                + server
                + ':'
                + port
            )
            # The connection to the tunnel server gets setup by the following controlmaster call
            cmd = (
                sshOptions('OMFITsshTunnel')
                + controlmaster(username_t, server_t, port_t, tunnel0)
                + " -t -t -Y -N -L "
                + port_l
                + ":"
                + server
                + ":"
                + port
                + " "
                + username_t
                + "@"
                + server_t
                + " -p "
                + port_t
            )
            printd('tunneling command: ' + cmd, topic='connection')
            # Establish the actual tunnel
            connected = ssh_connect_with_password(
                cmd,
                server0,
                lambda username=username, port_l=port_l: test_connection(username, '127.0.0.1', int(port_l), timeout=0.1, ntries=1),
            )
            if connected:
                printi('Created SSH tunnel ' + username + '@127.0.0.1:' + port_l + ' = ' + tunnel0 + ' --> ' + server0)
        if connected:
            OMFITaux['sshTunnel'][server0 + '-' + tunnel0] = (username, '127.0.0.1', port_l)
            return OMFITaux['sshTunnel'][server0 + '-' + tunnel0]
        else:
            if not internet_on():
                raise Exception('Failed to connect since network appears to be down')
            raise Exception('Failed to create tunnel ' + username + '@127.0.0.1:' + port_l + ' = ' + tunnel0 + ' --> ' + server0)

    if len(tunnel0):
        raise Exception('Failed to connect to `%s` via `%s`' % (server0, tunnel0))

    OMFITaux['sshTunnel'][server0 + '-' + tunnel0] = (username, server, port)
    return OMFITaux['sshTunnel'][server0 + '-' + tunnel0]


def setup_socks(tunnel):
    """
    Specifies a local "dynamic" application-level port forwarding.
    Whenever a connection is made to a defined port on the local side, the connection is forwarded over the secure channel, and the application protocol is then used to determine where to connect to from the remote machine.
    The SOCKS4 and SOCKS5 protocols are supported, and ssh will act as a SOCKS server.

    :param tunnel: tunnel

    :return: local sock connection (username, localhost, port)
    """
    # save original entries
    tunnel0 = tunnel

    # buffered connections
    if tunnel0 in OMFITaux['sshTunnel']:
        printd('Found buffered connection %s@%s:%s' % tuple(OMFITaux['sshTunnel'][tunnel0][:]), topic='connection')
        # since connection should be buffered we expect a quick response
        connected = test_connection(
            OMFITaux['sshTunnel'][tunnel0][0],
            OMFITaux['sshTunnel'][tunnel0][1],
            int(OMFITaux['sshTunnel'][tunnel0][2]),
            timeout=0.1,
            ntries=1,
        )
        if connected:
            return OMFITaux['sshTunnel'][tunnel0]
        else:
            del OMFITaux['sshTunnel'][tunnel0]

    # calculate tunnel port and parse server/tunnel strings
    port_l = str(omfit_numeric_hash(tunnel0) % (65535 - 49152) + 49152)
    username, password, tunnel, port = parse_server(str(tunnel0), default_username='')

    # Check if existing connection exists
    connected = test_connection(username, '127.0.0.1', int(port_l), timeout=0.1, ntries=1)
    if connected:
        printi('Found existing SOCKS tunnel ' + username + '@127.0.0.1:' + port_l + ' --> ' + username + '@' + tunnel + ':' + port)
        OMFITaux['sshTunnel'][tunnel0] = (username, '127.0.0.1', port_l)

    # Establish the actual tunnel
    cmd = sshOptions('OMFITsshTunnel') + " -D " + str(port_l) + " " + username + "@" + tunnel + " -p " + port
    printd('sock command: ' + cmd, topic='connection')
    connected = ssh_connect_with_password(
        cmd, tunnel0, lambda username=username, port_l=port_l: test_connection(username, '127.0.0.1', port_l, timeout=0.1, ntries=1)
    )
    if connected:
        OMFITaux['sshTunnel'][tunnel0] = (username, '127.0.0.1', port_l)
        return OMFITaux['sshTunnel'][tunnel0]
    else:
        raise Exception('Failed to create tunnel ' + username + '@127.0.0.1:' + port_l + ' --> ' + username + '@' + tunnel + ':' + port)


def internet_on(website='http://www.bing.com', timeout=5):
    """
    Check internet connection by returning the ability to connect to a given website

    :param website: website to test (by default 'http://www.bing.com' since google is not accessible from China)

    :param timeout: timeout in seconds

    :return: ability to connect or not
    """
    import requests

    if bool(len(OMFITaux['prun_process'])):
        printd('prun: skipping internet connection check.', topic='connection')
        return True
    try:
        printd('Internet connection check...', topic='connection')
        response = requests.get(website, verify=False, timeout=timeout)
        response.raise_for_status()  # Raises a HTTPError if the status is 4xx, 5xxx
        return True
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, requests.exceptions.HTTPError):
        return False


def get_ip():
    """
    https://stackoverflow.com/a/28950776/6605826

    :return: current system IP address
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        ip_addr = s.getsockname()[0]
    except Exception:
        ip_addr = '127.0.0.1'
    finally:
        s.close()
    return ip_addr


class AskPass:
    """
    Class that asks for password and one-time-password secret if credential file does not exists
    """

    explain = (
        "NOTE: Your saved credentials will be encrypted\n"
        + " with your ~/.ssh/id_rsa private key\n"
        + "and stored under "
        + os.path.abspath(OMFITsettingsDir + os.sep + 'credentials')
    )

    def __init__(self, credential, force_ask=False, OTP=False, **kw):
        r"""
        :param credential: credential filename to look for under the  OMFITsettingsDir+os.sep+'credentials' directory

        :param force_ask: force asking for the password (if file exists pwd is shown for amendment)

        :param OTP: ask for one-time-password secret; if 'raw' do not pass through pyotp.now()

        :param \**kw: extra arguments used in self.ask()
        """
        self.credential = credential

        pwd, otp = decrypt_credential(self.credential)

        store = True
        if not len(pwd + otp) and os.path.exists(credential_filename(self.credential)):
            store = False
        self.store = store
        self.OTP = OTP

        if len(pwd + otp) and not force_ask:
            return
        elif len(OMFITaux['prun_process']):
            raise RuntimeError('PWD+OTP for %s is not valid. Parallel run cannot continue.' % credential)

        self.ask(pwd, otp, OTP, store, **kw)

    def ask(self, pwd, otp, OTP, store, **kw):
        """
        Ask user for the password and one-time-password secret

        :param pwd: password

        :param otp: one time password

        :param OTP: ask for one-time-password secret; if 'raw' do not pass through pyotp.now()

        :param store: save pwd + otp to credential file
        """
        print(self.explain)

        OTP_text = []
        if OTP and OTP != 'raw':
            OTP_text = ['OTP secret (32 digits)']
        else:
            OTP_text = ['OTP']

        defaults = OrderedDict()
        username, password, server, port = parse_server(self.credential)
        print(f'\nCredentials for: {username}@{server}:{port}\n')
        defaults['Password'] = pwd
        if OTP_text:
            defaults[OTP_text[0]] = otp
        defaults['Save'] = store

        defaults_txt = {}
        for field in defaults:
            if defaults[field] or field == 'Save':
                if field in ['Password'] + OTP_text:
                    defaults_txt[field] = f'[{"*" * len(defaults[field])}]'
                else:
                    defaults_txt[field] = f'[{defaults[field]}]'
            else:
                defaults_txt[field] = ''

        response = {}
        for k, field in enumerate(defaults.keys()):
            response[field] = input(f'{field} {defaults_txt[field]}: ')
            if not len(response[field]):
                response[field] = str(defaults[field])

        self.store = bool(eval(response['Save']))
        self.pwd = response['Password']
        self.otp = ''
        if OTP_text:
            self.otp = response[OTP_text[0]]

        # if we decide not to store the password, the credential file is still generated but it will contain an empty password and OTP
        if self.store:
            print('STORE')
            self.encrypt(self.pwd, self.otp)
        else:
            print('EMPTY')
            self.encrypt('', '')

    def destroy(self):
        pass

    def encrypt(self, pwd, otp):
        """
        save user password and one-time-password secret to credential file
        """
        encrypt_credential(self.credential, pwd, otp)
        self.destroy()

    def decrypt(self):
        """
        :return: password with addition of six digits one-time-password
        """
        if self.store:
            pwd, secret = decrypt_credential(self.credential)
        else:
            pwd, secret = self.pwd, self.otp
        if self.OTP == 'raw':
            return pwd, secret
        elif len(secret):
            import pyotp

            otp = pyotp.TOTP(secret).now()
            return pwd, otp
        else:
            return pwd, ''


# ---------------------
# cryptography
# ---------------------
def _crypto(in_string, encrypt=True, keys=None):
    """
    :param in_string: string to be encrypted

    :param encrypt: if True, encrypt, else decrypt

    :param keys: filename or list of filenames of RSA private keys to be used for encryption (by default `~/.ssh/id_rsa`)

    :return: encrypted/decrypted string
    """

    def _exe_GUI(cmd, key):
        printd('Executing command: `{}`'.format(cmd), topic='Crypto')
        p = pexpect.spawn(cmd, timeout=20)
        pass_str = 'Enter pass phrase for %s:' % key
        pass_str_re = pass_str.replace(key, '.*')
        index = p.expect([pass_str_re, EOF])
        if index == 0:
            key = re.match('Enter pass phrase for (.*):', b2s(p.before + p.after)).groups()[0]
            if 'rootGUI' in OMFITaux and OMFITaux['rootGUI']:
                # Get password
                from utils_widgets import password_gui

                password = password_gui(title=pass_str, key=key)
            else:
                from utils_widgets import stored_passwords
                import getpass

                if key not in stored_passwords:
                    stored_passwords[key] = getpass.getpass(pass_str)
                password = stored_passwords[key]

            printd('Entering password', topic='Crypto')
            p.sendline(password.strip())
            p.expect(EOF)

    if keys is None:
        keys = os.path.join(os.environ['HOME'], '.ssh', 'id_rsa')
    keys = tolist(keys, [])

    # private keys
    for key in keys:
        if not os.path.exists(key):
            raise ValueError(f'Cannot find private RSA key: `{key}`!\nGenerate one with `ssh-keygen -b 4096 -m PEM`')

    # filenames
    import tempfile

    tmpdir = tempfile._get_default_tempdir()
    filename_in = os.path.join(tmpdir, next(tempfile._get_candidate_names()))
    filename_out = os.path.join(tmpdir, next(tempfile._get_candidate_names()))
    filename_cert = {}

    try:
        # input file
        with open(filename_in, mode='w') as f:
            pass
        os.chmod(filename_in, 0o600)
        if encrypt:
            with open(filename_in, mode='w+') as f:
                f.write(in_string)
        else:
            with open(filename_in, mode='wb+') as f:
                f.write(in_string)

        # output file
        with open(filename_out, mode='w') as f:
            pass
        os.chmod(filename_out, 0o600)

        if encrypt:
            for key in keys:
                # certificate
                filename_cert[key] = os.path.join(tmpdir, next(tempfile._get_candidate_names()))
                cmd = "openssl req -key {key} -new -x509 -nodes -subj '/' -out {certificate}".format(
                    key=key, certificate=filename_cert[key]
                )
                _exe_GUI(cmd, key)

            # encrypt
            cmd = "openssl smime -encrypt -aes256 -in {filename_in} -out {filename_out} -outform PEM ".format(
                filename_in=filename_in, filename_out=filename_out
            )
            cmd += ' '.join(filename_cert.values())

            printd('Executing command: `{}`'.format(cmd), topic='Crypto')
            os.system(cmd)

        else:
            # decrypt
            with open(filename_in, 'rb') as f:
                header = b'-----BEGIN PKCS7-----'
                # look for SMIME signature
                if header in f.readline()[: len(header)]:
                    cmd = 'openssl smime -decrypt -inform PEM'
                # otherwise fallback on RSAUTL for backward compatibility
                else:
                    cmd = 'openssl rsautl -decrypt'
            cmd = (cmd + ' -in {filename_in} -out {filename_out} -inkey {key}').format(
                key=key, filename_in=filename_in, filename_out=filename_out
            )
            _exe_GUI(cmd, key)

        # read output file
        with open(filename_out, mode='rb') as f:
            tmp = f.read()
        if not encrypt:
            tmp = b2s(tmp)

    finally:
        # clean up temporary files
        if os.path.exists(filename_in):
            os.remove(filename_in)
        if os.path.exists(filename_out):
            os.remove(filename_out)
        for key in filename_cert:
            if os.path.exists(filename_cert[key]):
                os.remove(filename_cert[key])
    return tmp


@_available_to_user_util
def encrypt(in_string, keys=None):
    """
    Encrypts a string with user RSA private key

    :param in_string: input string to be encrypted with RSA private key

    :param keys: private keys to encrypt with. if None, default to RSA key.

    :return: encrypted string
    """
    return _crypto(in_string, encrypt=True, keys=keys)


_tested_PEM = []


@_available_to_user_util
def decrypt(in_string):
    """
    Decrypts a string with user RSA private key

    :param in_string: input string to be decrypted with RSA private key

    :return: decrypted string
    """
    if not len(_tested_PEM):
        try:
            _tested_PEM.append(True)
            # the first time encryption is used, make sure ssh keys support encryption
            assert decrypt(encrypt('OMFIT')) == 'OMFIT', 'Your SSH keys do not support PEM! Regenerate with `ssh-keygen -b 4096 -m PEM`'
        except AssertionError:
            _tested_PEM[:] = []
            raise
    return _crypto(in_string, encrypt=False)


def credential_filename(server):
    """
    generates credential filename given username@server:port

    :param server: username@server:port

    :return: credential filename
    """
    tmp = list(parse_server(server))
    tmp[1] = ''
    credential = assemble_server(*tmp)
    if not os.path.exists(OMFITsettingsDir + os.sep + 'credentials'):
        os.makedirs(OMFITsettingsDir + os.sep + 'credentials')
    return OMFITsettingsDir + os.sep + 'credentials' + os.sep + credential


def encrypt_credential(credential, password, otp, keys=None):
    """
    generate encrypted credential file

    :param credential: credential string

    :param password: user password

    :param otp: user one-time-password secret

    :param keys: private keys to encrypt with. if None, default to RSA key.
    """
    if password == 'd3dpub' or (password.strip() == '' and otp.strip() == ''):
        printd(f'Refusing to store credential {credential}, since password is {password} and otp is {otp}', topic='Crypto')
        return
    filename = credential_filename(credential)
    with open(filename, 'wb') as f:
        f.write(encrypt('\n'.join([password, otp]), keys=keys))
    os.chmod(filename, 0o600)


def decrypt_credential(credential):
    """
    read and decrypt credential file

    :param credential: credential string

    :return: password and one-time-password secret
    """
    filename = credential_filename(credential)
    if not os.path.exists(filename):
        return '', ''
    with open(filename, 'rb') as f:
        tmp = b2s(decrypt(f.read()))
    tmp = tmp.split('\n')
    otp = ''
    pwd = tmp[0]
    if len(tmp) > 1 and len(tmp[1]):
        otp = tmp[1]
    return pwd.strip(), otp.strip()


def reset_credential(credential):
    """
    delete credential file

    :param credential: credential string
    """
    filename = credential_filename(credential)
    if os.path.exists(filename):
        os.remove(filename)
        printi('Removed credential file for %s' % credential)


@_available_to_user_util
def password_encrypt(data, password, encoding="utf-8", bufferSize=64 * 1024):
    '''
    Encrypt using AES cryptography

    :param data: data in clear to be encrypted

    :param password: password

    :param encoding: encoding to be used to translate from string to bytes

    :param bufferSize: buffer size

    :return: encrypted data (bytes)
    '''
    import pyAesCrypt
    import io

    # from string to bytes
    if encoding:
        data = data.encode(encoding)

    # input plaintext binary stream
    fIn = io.BytesIO(data)

    # initialize ciphertext binary stream
    fCiph = io.BytesIO()

    # initialize decrypted binary stream
    fDec = io.BytesIO()

    # encrypt stream
    pyAesCrypt.encryptStream(fIn, fCiph, password, bufferSize)

    # encrypted data
    return fCiph.getvalue()


@_available_to_user_util
def password_decrypt(data, password, encoding="utf-8", bufferSize=64 * 1024):
    '''
    Deccrypt using AES cryptography

    :param data: encrypted data (bytes) to be decrypted

    :param password: password

    :param encoding: encoding to be used to translate from bytes to string

    :param bufferSize: buffer size

    :return: data in clear
    '''
    import pyAesCrypt
    import io

    # initialize decrypted binary stream
    fDec = io.BytesIO()

    # initialize ciphertext binary stream
    fCiph = io.BytesIO()
    fCiph.write(data)

    # get ciphertext length
    ctlen = len(fCiph.getvalue())

    # go back to the start of the ciphertext stream
    fCiph.seek(0)

    # decrypt stream
    pyAesCrypt.decryptStream(fCiph, fDec, password, bufferSize, ctlen)

    # decrypted data
    data = fDec.getvalue()

    # turn into string
    if encoding:
        data = data.decode(encoding)

    return data


# ---------------------
# PDF and DMP
# ---------------------
def PDF_add_file(pdf, file, name=None, delete_file=False):
    """
    Embed file in PDF

    :param pdf: PDF filename

    :param file: filename or file extension

    :param name: name of attachment in PDF. Uses file filename if is None.

    :param delete_file: remove file after embedding

    :return: full path to PDF file
    """
    try:
        import PyPDF2
    except ImportError:
        printw('Could not embed data in PDF because Python `PyPDF2` package is missing')
        return
    if file.startswith('.') and os.sep not in file:
        file = re.sub('.pdf$', '', pdf) + file

    unmeta = PyPDF2.PdfFileReader(pdf, "rb")

    meta = PyPDF2.PdfFileWriter()
    meta.appendPagesFromReader(unmeta)

    with open(file, "rb") as fp:
        meta.addAttachment(os.path.split(file)[1], fp.read())

    with open(pdf, "wb") as fp:
        meta.write(fp)

    # delete file if requested
    if delete_file:
        os.remove(file)

    # return path to PDF
    return os.path.abspath(pdf)


def PDF_get_file(pdf, file, name='.*'):
    """
    Extract file from PDF

    :param pdf: PDF filename

    :param file: filename or file extension

    :param name: regular expression with name(s) of attachment in PDF to get

    :return: full path to file
    """
    try:
        import PyPDF2
    except ImportError:
        printw('Could not de-embed data in PDF because Python `PyPDF2` package is missing')
        return
    if file.startswith('.') and os.sep not in file:
        file = re.sub('.pdf$', '', pdf) + file
    unmeta = PyPDF2.PdfFileReader(pdf, "rb")
    embedded = unmeta.trailer['/Root']['/Names']['/EmbeddedFiles']['/Names']
    list_files = []
    done = False
    for obj in range(len(embedded)):
        if not isinstance(embedded[obj], dict):
            continue
        filename = embedded[obj]['/F']
        list_files.append(filename)
        if re.match(name, filename):
            data = embedded[obj]['/EF']['/F']._data
            with open(file, 'wb') as f:
                f.write(data)
            done = True
            break
    # raise error if file is not found
    if not len(list_files):
        raise RuntimeError('The PDF does not contain attachments')
    elif not done:
        raise RuntimeError('The PDF does not contain `%s`.\nPossible options are: %s' % (name, list_files))
    # return path to file
    return os.path.abspath(file)


def PDF_set_DMP(pdf, dmp='.h5', delete_dmp=False):
    """
    Embed DMP file in PDF

    :param pdf: PDF filename

    :param dmp: DMP filename or extension

    :param delete_dmp: remove DMP file after embedding

    :return: full path to PDF file
    """
    if dmp.startswith('.') and os.sep not in dmp:
        dmp = re.sub('.pdf$', '', pdf) + dmp
    return PDF_add_file(pdf, dmp, name='DMP_' + os.path.splitext(os.path.split(dmp)[1])[0], delete_file=delete_dmp)


def PDF_get_DMP(pdf, dmp='.h5'):
    """
    Extract DMP file from PDF

    :param pdf: PDF filename

    :param dmp: filename or file extension

    :return: full path to DMP file
    """
    if dmp.startswith('.') and os.sep not in dmp:
        dmp = re.sub('.pdf$', '', pdf) + dmp
    return PDF_get_file(pdf, dmp, name='^DMP_.*')


# ---------------------
# Python introspection
# ---------------------
def python_imports(namespace, submodules=True, onlyWithVersion=False):
    """
    function that lists the Python modules that have been imported in a namespace

    :param namespace: usually this function should be called with namespace=globals()

    :param submodules: list only top level modules or also the sub-modules

    :param onlyWithVersion: list only (sub-)modules with __version__ attribute
    """
    import types

    mods = []
    for name, val in list(namespace.items()):
        if isinstance(val, types.ModuleType):
            version = 'N/A'
            if hasattr(val, '__version__'):
                version = val.__version__
            elif onlyWithVersion:
                continue
            if submodules:
                mods.append([val.__name__, version])
            else:
                if not '.' in val.__name__:
                    mods.append([val.__name__, version])
    return mods


def function_arguments(f, discard=None, asString=False):
    """
    Returns the arguments that a function takes

    :param f: function to inspect

    :param discard: list of function arguments to discard

    :param asString: concatenate arguments to a string

    :return: tuple of four elements

    * list of compulsory function arguments

    * dictionary of function arguments that have defaults

    * True/False if the function allows variable arguments

    * True/False if the function allows keywords
    """
    import inspect

    the_argspec = inspect.getfullargspec(f)
    the_keywords = the_argspec.varkw

    args = []
    kws = OrderedDict()
    string = ''
    for k, arg in enumerate(the_argspec.args):
        if (discard is not None) and (arg in tolist(discard)):
            continue
        d = ''
        if the_argspec.defaults is not None:
            if (-len(the_argspec.args) + k) >= -len(the_argspec.defaults):
                d = the_argspec.defaults[-len(the_argspec.args) + k]
                kws[arg] = d
                string += arg + '=' + repr(d) + ',\n'
            else:
                args.append(arg)
                string += arg + ',\n'
        else:
            args.append(arg)
            string += arg + ',\n'
        if the_argspec.varargs:
            string += '*[],\n'
        if the_keywords:
            string += '**{},\n'
        string = string.strip()
    if asString:
        return string
    else:
        return args, kws, the_argspec.varargs is not None, the_keywords is not None


def args_as_kw(f, args, kw):
    """
    Move positional arguments to kw arguments

    :param f: function

    :param args: positional arguments

    :param kw: keywords arguments

    :return: tuple with positional arguments moved to keyword arguments
    """
    a, k, astar, kstar = function_arguments(f)
    n = 0
    for name, value in zip(a + list(k.keys()), args):
        if name not in kw:
            kw[name] = value
        n += 1
    return args[n:], kw


def only_valid_kw(f, kw0=None, **kw1):
    """
    Function used to return only entries of a dictionary
    that would be accepted by a function and avoid
    TypeError: ... got an unexpected keyword argument ...

    :param f: function

    :param kw0: dictionary with potential function arguments

    :param \**kw1: keyword dictionary with potential function arguments

    >> f(**only_valid_kw(f, kw))
    """
    if kw0 is None:
        kw0 = {}
    else:
        kw = copy.copy(kw0)
    kw.update(kw1)
    a, k, astar, kstar = function_arguments(f)
    if kstar:
        return kw
    kw_out = {}
    for item, value in kw.items():
        if item in a or item in k:
            kw_out[item] = value
    return kw_out


def functions_classes_in_script(filename):
    """
    Parses a Python script and returns list of functions and classes
    that are declared there (does not execute the script)

    :params filename: filename of the Python script to parse

    :returns: dictionary with lists of 'functions' and 'classes'
    """
    with open(filename, 'r') as file:
        ast_tree = ast.parse(file.read(), filename=filename)
    objects = {'functions': [], 'classes': []}
    for item in ast_tree.body:
        if isinstance(item, ast.FunctionDef):
            objects['functions'].append(item.name)
        if isinstance(item, ast.ClassDef):
            objects['classes'].append(item.name)
    return objects


def dump_function_usage(post_operator=None, pre_operator=None):
    """
    Decorator function used to collect arguments passed to a function

    >> def printer(d):
    >>     print(d)

    >> @dump_function_usage(printer)
    >> def hello(a=1):
    >>    print('hello')

    :param post_operator: function called after the decorated function
                          (a dictionary with the function name, arguments, and keyword arguments gets passed)

    :param pre_operator: function called before the decorated function
                          (a dictionary with the function name, arguments, and keyword arguments gets passed)
    """

    def dumpArgsDeco(func):
        def wrapper(*func_args, **func_kwargs):
            arg_names = func.__code__.co_varnames[: func.__code__.co_argcount]
            defaults = func.__defaults__ or ()
            args = func_args[: len(arg_names)]
            args = args + defaults[len(defaults) - (func.__code__.co_argcount - len(args)) :]
            params = list(zip(arg_names, args))
            args = func_args[len(arg_names) :]
            if args:
                params.append(('args', args))
            if func_kwargs:
                params.append(('kwargs', func_kwargs))
            func_name = func.__name__
            func_name = func.__name__
            params.append(('func', func_name))
            # printd(func_name + ' (' + ', '.join('%s = %r' % p for p in params) + ' )',topic=func_name)
            if pre_operator is not None:
                pre_operator(dict(params))
            tmp = func(*func_args, **func_kwargs)
            if post_operator is not None:
                post_operator(dict(params))
            return tmp

        return wrapper

    return dumpArgsDeco


def function_to_tree(funct, self_ref):
    """
    Converts a function to an OMFITpythonTask instance that can be saved in the tree

    :param funct: function
        The function you want to export

    :param self_ref: object
        Reference to the object that would be called self within the script.
        Its location in the tree will be looked up and used to replace 'self' in the code.
        This is used to add a line defining the variable self within the new OMFITpythonTask's source. If the function
        doesn't use self, then it just has to be something that won't throw an exception, since it won't be used
        (e.g. self_ref=OMFIT should work if you're not using self)

    :return: An OMFITpythonTask instance
    """
    from inspect import cleandoc
    from omfit_classes.sortedDict import treeLocation
    from omfit_classes.omfit_python import OMFITpythonTask

    src = inspect.getsource(funct)

    def_part = cleandoc(src.split('):')[0]) + ')'
    body = cleandoc('):'.join(src.split('):')[1:]))
    lines = body.split('\n')
    while lines[-1].strip().startswith('return') or (not len(lines[-1].strip())):
        lines = lines[:-1]
    body = '\n'.join(lines)
    self_def = 'self = {}\n\n'.format(treeLocation(self_ref)[-1])

    name = def_part.split('(')[0].split('def ')[1]

    args = '('.join([arg.lstrip('\n ') for arg in def_part.split('(')[1:]])
    # Remove leading "self" argument and trailing ", " or ",", if present
    cut_start = ['self, ', 'self,', 'self']
    for cs in cut_start:
        if args.startswith(cs):
            args = args[len(cs) :]
            break
    args = '\n'.join([line for line in args.split('\n') if len(line.strip())])
    args = re.sub('\*\*(?P<name>[A-Z,a-z,0-9,_]*)', '\g<name>={}', args)

    return OMFITpythonTask(
        '{}.py'.format(name),
        fromString='# TEMPORARY FILE: EDITS WILL NOT BE SAVED!\n'
        '# This file was generated by omfit_classes.utils_base.function_to_tree()\n\n'
        'defaultVars(' + args + '\n' + self_def + body,
    )


OMFIT_backward_compatibility_mapper = {}

# ---------------------
# lists and dicts
# ---------------------
@_available_to_user_util
def tolist(data, empty_lists=None):
    """
    makes sure that the returned item is in the format of a list

    :param data: input data

    :param empty_lists: list of values that if found will be filtered out from the returned list

    :return: list format of the input data
    """
    import numpy as np

    data = evalExpr(data)
    if isinstance(data, str):
        data = [data]
    if empty_lists:
        if not np.iterable(data):
            if data in empty_lists:
                return []
        else:
            data0 = data
            data = []
            for k in data0:
                if k not in empty_lists:
                    data.append(k)
    if isinstance(data, np.ndarray):
        return np.atleast_1d(data).tolist()
    elif isinstance(data, dict):
        return [data]
    try:
        return list(data)
    except TypeError:
        return [data]


def common_in_list(input_list):
    """
    Finds which list element is most common (most useful for a list of strings or mixed strings & numbers)
    :param input_list: list with hashable elements (no nested lists)
    :return: The list element with the most occurrences. In a tie, one of the winning elements is picked arbitrarily.
    """
    return max(set(input_list), key=input_list.count)


def keyword_arguments(dictionary):
    """
    Returns the string that can be used to generate a dictionary from keyword arguments

    eg. keyword_arguments({'a':1,'b':'hello'}) --> 'a'=1,'b'='hello'

    :param dictionary: input dictionary

    :return: keyword arguments string
    """
    return ','.join([k[0] + '=' + repr(k[1]) for k in zip(list(dictionary.keys()), list(dictionary.values()))])


@_available_to_user_util
def select_dicts_dict(dictionary, **selection):
    """
    Select keys from a dictionary of dictionaries. This is useful to select data from a dictionary that uses a hash
    as the key for it's children dictionaries, and the hash is based on the content of the children.

    eg:
    >> parent={}
    >> parent['child1']={'a':1,'b':1}
    >> parent['child2']={'a':1,'b':2}
    >> select_dicts_dict(parent, b=1) #returns: ['child1']
    >> select_dicts_dict(parent, a=1) #returns: ['child1', 'child2']

    :param dictionary: parent dictionary

    :param \**selection: keywords to select on

    :return: list of children whose content matches the selection
    """
    ret = []
    for item in list(dictionary.keys()):
        found = True
        for sel in list(selection.keys()):
            if not (sel in dictionary[item] and selection[sel] == dictionary[item][sel]):
                found = False
        if found:
            ret.append(item)
    return ret


@_available_to_user_util
def bestChoice(options, query, returnScores=False):
    """
    This fuction returns the best heuristic choice from a list of options

    :param options: dictionary or list of strings

    :param query: string to look for

    :param returnScores: whether to return the similarity scores for each of the options

    :return: the tuple with best choice from the options provided and its matching score, or match scores if returnScores=True
    """
    scores = []
    for item in options:
        m = difflib.SequenceMatcher(None, item.lower(), query.lower())
        scores.append(m.ratio())
    i = sorted(list(range(len(scores))), key=scores.__getitem__)
    if returnScores:
        return scores
    elif isinstance(options, dict):
        return list(options.values())[i[-1]], scores[i[-1]]
    else:
        return options[i[-1]], scores[i[-1]]


def flip_values_and_keys(dictionary, modify_original=False, add_key_to_value_first=False):
    """
    Flips values and keys of a dictionary
    People sometime search the help for swap_keys, switch_keys, or flip_keys to find this function.

    :param dictionary: dict
        input dictionary to be processed

    :param modify_original: bool
        whether the original dictionary should be modified

    :param add_key_to_value_first: bool
        Append the original key to the value (which will become the new key).
        The new dictionary will look like: {'value (key)': key},
        where key and value were the original key and value.
        This will force the new key to be a string.

    :return: dict
        flipped dictionary
    """
    keys = list(dictionary.keys())
    values = list(dictionary.values())
    if modify_original:
        dictionary.clear()
    else:
        try:
            dictionary = dictionary.__class__()
        except TypeError:  # OMFITjson and other file classes won't init without a filename
            dictionary = OrderedDict()
    for k, v in zip(keys, values):
        if add_key_to_value_first:
            dictionary['{} ({})'.format(v, k)] = k
        else:
            dictionary[v] = k
    return dictionary


def dir2dict(startpath, dir_dict=OrderedDict):
    """
    python dictionary hierarchy based on filesystem hierarchy

    :param startpath: filesystem path

    :return: python dictionary
    """

    def set_leaf(tree, branches, leaf):
        """Set a terminal element to *leaf* within nested dictionaries.
        *branches* defines the path through dictionaries.

        Example:
        >>> t = {}
        >>> set_leaf(t, ['b1','b2','b3'], 'new_leaf')
        >>> print(t)
        {'b1': {'b2': {'b3': 'new_leaf'}}}
        """
        if len(branches) == 1:
            tree[branches[0]] = leaf
            return
        if branches[0] not in tree:
            tree[branches[0]] = dir_dict()
        set_leaf(tree[branches[0]], branches[1:], leaf)

    tree = dir_dict()
    for root, dirs, files in os.walk(startpath):
        dirs.sort(key=lambda x: x.lower() + x)
        files.sort(key=lambda x: x.lower() + x)
        branches = [startpath]
        if root != startpath:
            branches.extend(os.path.relpath(root, startpath).split('/'))
        set_leaf(tree, branches, dir_dict([(d, dir_dict()) for d in dirs] + [(f, None) for f in files]))
    return tree


# ---------------------
# git
# ---------------------
OMFITreposDir = None


def parse_git_message(message, commit=None, tag_commits=[]):
    ctype_color = 'RoyalBlue3'
    message = re.sub(r'<<<>>>(.*)<<<>>>', r'\n<<<>>>\1<<<>>>', message)
    summary = message.split('\n')[0]
    ctype = re.findall(r'<<<>>>.*<<<>>>', message, re.MULTILINE | re.DOTALL)

    def ctype_colors(in_c):
        in_c = in_c.lower()
        if 'bug' in in_c or 'fix' in in_c:
            return 'firebrick1'
        if 'document' in in_c or 'regression' in in_c:
            return 'orange'
        if 'module' in in_c:
            return 'purple'
        return 'RoyalBlue3'

    if commit in tag_commits:
        ctype = 'New release'
        ctype_color = 'forest green'
    elif len(ctype):
        message = message.replace(ctype[0], '')
        ctype = ctype[0].replace('\n', ' ').replace('<<<>>>', '').strip('><')
        ctype_color = ctype_colors(ctype)
    elif ':' in summary:
        summ_split = summary.split(':', 3)
        message = summ_split[-1] + ('\n' * 3)
        summary = message.strip()
        ctype_color = ctype_colors(':'.join(summ_split[:-1]))
        ctype = ':'.join(summ_split[:-1]).lstrip('!')
    else:
        ctype = 'Update'
    message = message.split('\n')

    return ctype, summary, message, ctype_color


class OMFITgit(object):
    """
    An OMFIT interface to a git repo, which does NOT leave dangling open files

    :param git_dir: the root of the git repo

    :param n: number of visible commits
    """

    def __init__(self, git_dir, n=25):
        if not os.path.exists(git_dir):
            raise OSError(f'{git_dir} does not exist')

        if not os.path.exists(git_dir + os.sep + '.git') and not git_dir.endswith('.git'):
            raise OSError(f'{git_dir} is not a git repository!')

        self.work_repo = None
        self.git_cmd = system_executable('git')
        os.environ.get(
            'GIT_SSH_COMMAND', sshOptions('OMFITsshGit')
        )  # +' -o ControlMaster=auto -o ControlPath='+OMFITcontrolmastersDir+os.sep+'%r@%h:%p -o ControlPersist=24h'
        self.git_dir = os.path.abspath(git_dir)
        self._n_visible = n

        self.install_OMFIT_hooks()

    def install_OMFIT_hooks(self, quiet=True):
        import filecmp

        if self.is_OMFIT_source and os.access(os.sep.join([self.git_dir, '.git', 'hooks']), os.W_OK):
            for source in glob.glob(os.sep.join([self.git_dir, 'install', 'git-hooks', '*'])):
                target = os.sep.join([self.git_dir, '.git', 'hooks', os.path.split(source)[1]])
                if not os.path.exists(target) or not filecmp.cmp(source, target, shallow=True):
                    try:
                        shutil.copy2(source, target)
                        printw("Installed '%s' git hook" % os.path.split(target)[1])
                    except Exception as e:
                        printe("Could not install '%s' git hook: %s" % (os.path.split(target)[1], repr(e)))
        elif not quiet:
            raise Exception('Could not install .git hooks')

    def is_OMFIT_source(self):
        if os.path.exists(os.sep.join([self.git_dir, 'omfit', 'omfit_tree.py'])):
            return True
        return False

    def __call__(self, command, verbose=False, returns='out+err', subdir=''):
        """
        Return the results of `git <command> [args]` as a string

        :param command: (str or iterable) The git command (or iterable of commands) to carry out

        :param returns: list with choice of `['out','err','code']` or 'out+err'

        :param subdir: subdirectory in the git repo where to execute the command

        :return: stdout, stderr, return code depending on `returns` list
        """
        return_dict = {}
        if verbose:
            printi('%s %s' % ('git', command))
        if 'DYLD_LIBRARY_PATH' in os.environ:
            print('Removed DYLD_LIBRARY_PATH=%s' % os.environ['DYLD_LIBRARY_PATH'])
            del os.environ['DYLD_LIBRARY_PATH']
        composite_command = '&&'.join([' %s %s' % (self.git_cmd, x) for x in tolist(command)])
        if verbose:
            print(composite_command)

        command = 'cd %s && %s' % (self.git_dir + '/' + subdir, composite_command)

        if os.name == 'nt':
            if len(command) > 8191:
                raise OMFITexception('Command for git is too long for windows command line')

        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return_dict['out'], return_dict['err'] = list(map(b2s, process.communicate()))
        return_dict['code'] = process.returncode
        return_dict['out'] = return_dict['out'].rstrip()
        return_dict['err'] = return_dict['err'].rstrip()

        if verbose and (return_dict['out'] + return_dict['err']).rstrip():
            print((return_dict['out'] + return_dict['err']).rstrip())

        if returns == 'out+err':
            return return_dict['out'] + return_dict['err']

        elif len(returns) == 1:
            return return_dict[returns[0]]

        else:
            return {ret: return_dict[ret] for ret in returns}

    def __getattr__(self, attr):
        if attr in ['status', 'log', 'tag', 'describe', 'branch']:
            return self(attr)
        if attr == 'head':
            return self.get_hash('HEAD')
        raise AttributeError('%s: Unknown attribute' % attr)

    def tag_hashes(self):
        """
        Get the full hashes for all of the tags

        :return: A list of hashes, corresponding to self.tag.splitlines()
        """
        return self.get_hash(self.tag.splitlines()).splitlines()

    def get_hash(self, ref):
        """
        Get the full hash for the given reference (tag, branch, or commit)

        :param ref:  A commitish reference (tag, commit hash, or branch) or iterable of references
        """
        return self(['log -1 --pretty="%H" ' + str(x) + ' --' for x in tolist(ref)], returns=['out'])

    def get_commit_message(self, commit):
        """
        Given the commit hash, return the commit message

        :param commit:  (str) The hash of the commit
        """
        return self('log -1 --pretty="%B" ' + commit, returns=['out'])

    def get_commit_date(self, commit):
        """
        Given the commit hash, return the commit date (in form similar to `time.time`)

        :param commit: (str) The hash of the commit

        :return: An int
        """
        return int(self('log -1 --pretty="%at" ' + str(commit), returns=['out']))

    def get_visible_commits(self, order=['author-date-order', 'date-order', 'topo-order'][0]):
        """
        Get the commits that don't have Hidden, Hide, or Minor comment tags

        :return: A tuple of the commits, their messages, their authors, their dates, and the tag_hashes
        """
        sep = '#<-:-:->#'
        recent = self(
            'log -' + str(int(self._n_visible)) + ' --no-merges --' + order + ' --pretty="%H; %aN; %at%n%B%n' + sep + '" HEAD',
            returns=['out'],
        ).split('\n' + sep + '\n')[:-1]

        commits = []
        messages = []
        authors = []
        dates = []

        tag_commits = self.tag_hashes()

        for line in recent:
            split_line = line.strip().splitlines()
            commit, author, date = split_line[0].split(';')
            message_orig = '\n'.join(split_line[1:])

            ctype, summary, message, ctype_color = parse_git_message(message_orig, commit, tag_commits)

            if message[0] == summary:
                title = summary.strip()
            else:
                title = ''

            if ctype.lower() not in ['hide', 'hidden', 'minor'] and (commit in tag_commits or not title.startswith("Merge ")):
                commits.append(commit)
                messages.append(message_orig)
                authors.append(author)
                dates.append(date)

        return commits, messages, authors, dates, tag_commits

    def get_tag_version(self, tag_family):
        """
        Get a version similar to the results of self.describe, but restricted to tags containing a specific string. This
        is for finding the tagged version of a module: one might use ``repo.get_tag_version('cake_')`` to get the
        version of the CAKE module (like 'cake_00.01.684e4d226a' or 'cake_00.01')

        :param tag_family: A substring defining a family of tags. It is assumed that splitting this substring out of the
            git tags will leave behind version numbers for that family.

        :return: A string with the most recent tag in the family, followed by a commit short hash if there have been
            commits since the tag was defined.
        """
        printd('Getting version for tag_family = {}...'.format(tag_family))
        return self('describe --match "{}[0-9]*" --tags'.format(tag_family))

    def active_branch(self):
        """
        Get the active branch, the (shortened) hash of HEAD, and the standard string containing those
            where the standard string is "Commit <shortened hash> on branch <active_branch>"

        :return: active_branch, active_branch_hash, standard_string
        """
        t0 = time.time()
        active_branch = 'DETACHED_HEAD'
        for branch in self('branch').splitlines():
            if branch.startswith('*') and 'HEAD detached' not in branch:
                active_branch = branch.split('*')[1].strip()
                break
        active_branch_commit = self.get_hash('HEAD')
        tags = list([x for x in self('tag --contains', returns=['out']).split() if x not in ['HEAD', active_branch_commit]])
        if len(tags):
            active_branch_commit = ','.join(tags)
        else:
            active_branch_commit = active_branch_commit[:10]
        repo_str = '%s on branch %s' % (self('describe'), active_branch)
        return active_branch, active_branch_commit, repo_str

    def get_module_params(self, path='modules', key='ID', quiet=True, modules=None):
        """
        Return a dictionary whose keys are the modules available in this repo

        :param path: The path (relative to the root of the repo) where the modules are stored

        :param key: attribute used for the returned dictorary (eg. `ID` (default) or `path`)

        :param quiet: whether to print the modules loaded (if `None` uses progress bar)

        :param modules: list of modules to track (full path, minus OMFITsave.txt)

        :return: A dictionary whose keys are the modules available in this repo,
            the values are dictionaries whose keys are author, date, commit,
            path, version.

        A return example::

            {
                'EFITtime':
                {
                    'edited_by': 'Sterling Smith',

                    'commit': '64a213fb03e14a154567f8eb7b260f10acbe48f3',

                    'date': '1456297324', #time.time format

                    'path': '/Users/meneghini/Coding/atom/OMFIT-source/modules/EFITtime/OMFITsave.txt',

                    'version': u'Module to execute time-dependent EFIT equilibrium reconstructions'
                }
            }
        """

        def sortByModule(command):
            byMod = {}
            for filename in self(command + ' ' + path).split():
                tmp = list([_f for _f in filename[len(path) :].split(os.sep) if _f])
                if len(tmp):
                    byMod.setdefault(tmp[0], [])
                    byMod[tmp[0]].append(self.git_dir + os.sep + filename)
            return byMod

        tracked_files = sortByModule('ls-tree --name-only -r HEAD')
        untracked_files = sortByModule('ls-files --other --exclude-standard')
        modified_files = sortByModule('ls-files -m --exclude-standard')

        if modules is None:
            modules = [
                os.path.split(x)[0] for x in list(map(os.path.abspath, glob.glob(os.sep.join([self.git_dir, path, '*', 'OMFITsave.txt']))))
            ]
        else:
            modules = [re.sub(os.sep + 'OMFITsave.txt$', '', x) for x in modules]

        result = {}
        commands = []
        mod_keys = sorted(modules, key=lambda x: x.lower())
        for k, mod in enumerate(mod_keys):
            commands.append('log -1 --pretty="%H; %aN; %at" HEAD -- ' + mod + '; echo ' + mod)
        mod_tmp = [_f for _f in self(commands, returns=['out']).splitlines() if _f]
        mod_out = {}
        details = untracked_details = '? ; %s ; %d' % (os.environ['USER'], int(time.time()))
        for line in mod_tmp:
            if line.count(';'):
                details = line
            elif not line.count(';'):
                mod_out[line] = details
                details = untracked_details

        for mod in ascii_progress_bar(mod_keys, mess=mod_keys, quiet=quiet is not None):
            try:

                mod_name = os.path.split(mod)[1]

                tmp = {}
                tmp['ID'] = mod_name
                tmp['path'] = os.sep.join([mod, 'OMFITsave.txt'])
                tmp['untracked'] = untracked_files.get(mod_name, '')
                tmp['modified'] = modified_files.get(mod_name, '')
                tmp['date'] = time.time()
                tmp['edited_by'] = os.environ['USER']
                tmp['commit'] = ''
                tmp['description'] = ''

                if len(tmp['modified']) or os.path.abspath(mod + os.sep + 'OMFITsave.txt') in tmp['untracked']:
                    pass
                else:
                    for param, val in zip(['commit', 'edited_by', 'date'], mod_out[mod].split(';')):
                        tmp[param] = val.strip()

                if quiet is False:
                    if os.path.abspath(mod + os.sep + 'OMFITsave.txt') in tmp['untracked']:
                        printi(tmp['ID'].ljust(20) + "(untracked)")
                    elif len(tmp['modified']):
                        printi(tmp['ID'].ljust(20) + "(modified)")
                    else:
                        printi(tmp['ID'])

                tmp['date'] = convertDateFormat(int(tmp['date']))

                # get additional module informations that is in the modules settings
                from omfit_classes.omfit_base import OMFITmodule

                info = OMFITmodule.info(tmp['path'])
                info.pop('date', None)
                info.pop('edited_by', None)
                info.pop('commit', None)
                tmp.update(info)

                result[tmp[key]] = tmp

            except Exception as _excp:
                printe('git error for module %s: %s' % (mod_name, repr(_excp)))
                raise

        return result

    def get_remotes(self):
        '''returns dictionary with remotes as keys and their properties'''
        remotes = {}
        remote_keys = self('remote').split()
        for i, remote in enumerate(remote_keys):
            remotes[remote] = {}
            remotes[remote]['url'] = self('ls-remote --get-url ' + remote)
        return remotes

    def get_branches(self, remote=''):
        '''returns dictionary with branches as keys and their properties'''
        branches = {}
        if not remote:
            for branch in [_f for _f in self('branch').strip().split('\n') if _f]:
                current = False
                if branch.startswith('*'):
                    current = True
                branch = branch.strip('* ')
                branches[branch] = {}
                branches[branch]['remote'] = self('config branch.%s.remote' % branch).strip()
                branches[branch]['current'] = current
        else:
            returns = self('ls-remote --heads %s' % remote, returns=['out', 'err'])
            for branch in [_f for _f in returns['out'].strip('\n ').split('\n') if _f]:
                branch = '/'.join(branch.split()[1].split('/')[2:])
                branches[branch] = {}
                branches[branch]['remote'] = remote
        return branches

    def clone(self):
        """
        Clone of the repository in the OMFITworking environment `OMFITtmpDir+os.sep+'repos'`
        and maintain remotes information. Note: `original_git_repository` is the remote that points
        to the original repository that was cloned

        :return: OMFITgit object pointing to cloned repository
        """
        if not os.path.exists(OMFITreposDir):
            os.makedirs(OMFITreposDir)
        repository_directory = OMFITreposDir + os.sep + os.path.split(os.path.abspath(self.git_dir))[1] + "_" + omfit_hash(self.git_dir, 10)
        if not os.path.exists(repository_directory):
            tmp = self.active_branch()
            self('clone -n file://$PWD %s' % repository_directory, verbose=True)
            self.work_repo = OMFITgit(repository_directory, n=self._n_visible)

            self.work_repo('remote rename %s %s' % ('origin', 'original_git_repository'), verbose=True)
            # copy remotes (origin points to original repo)
            remotes = self.get_remotes()
            for remote in list(remotes.keys()):
                if 'gafusion/OMFIT-source.git' in remotes[remote]['url'] and 'gafusion' not in remotes:
                    remotes['gafusion'] = remotes[remote]
            for remote in list(remotes.keys()):
                self.work_repo('remote add %s %s' % (remote, remotes[remote]['url']), verbose=True)
        else:
            if not self.work_repo:
                self.work_repo = OMFITgit(repository_directory, n=self._n_visible)
                out = self.work_repo('status')
                if 'fatal: Not a git repository' in out:
                    shutil.rmtree(repository_directory)
                    self.work_repo = self.clone()
            printd('work repo already exists: %s' % self.work_repo.git_dir, topic='OMFITgit')
        return self.work_repo

    def switch_branch(self, branch, remote=''):
        """
        Switch to branch

        :param branch: branch

        :param remote: optional remote repository
        """

        # get local branches
        branches = self.get_branches()

        # get remote branches
        if remote:
            remote_branches = self.get_branches(remote=remote)

            # fetch remote/branch
            if branch in remote_branches:
                self('fetch %s %s' % (remote, branch), verbose=True)

        # checkout new branch and make it point to the remote
        if branch not in branches and remote and branch not in remote_branches:
            self('checkout -b %s' % (branch), verbose=True)
            out = self('branch %s -u %s/%s' % (branch, remote, branch), verbose=True)
            if 'error: the requested upstream branch ' in out and ' does not exist' in out:
                self('push --set-upstream %s %s' % (remote, branch), verbose=True)

        # if there is a local copy already
        elif branch in branches:
            if branches[branch]['remote'] == remote or not branches[branch]['remote'] or not remote:
                self('checkout %s' % (branch), verbose=True)
            else:
                self('branch %s -u %s/%s' % (branch, remote, branch), verbose=True)
            if remote and branches[branch]['remote']:
                self('merge --no-edit %s/%s' % (remote, branch), verbose=True)

        # if there is a remote branch
        else:
            self('checkout --track %s/%s' % (remote, branch), verbose=True)

    def branch_containing_commit(self, commit):
        """
        Returns a list with the names of the branches that contain the specified commit

        :param commit: commit to search for

        :return: list of strings (remote is separated by `/`)
        """
        tmp = self('branch -a --contains %s' % commit)
        tmp = [x.strip(' *') for x in tmp.strip().split('\n')]
        lst = []
        for item in list(tmp):
            if 'remotes/origin/HEAD' in item:
                continue
            if item.startswith('remotes/'):
                lst.append('/'.join(item.split('/')[1:]))
            else:
                lst.append(item)
        return sorted(set(lst))

    def switch_branch_GUI(self, branch='', remote='', parent=None, title=None, only_existing_branches=False):
        import tkinter as tk
        from tkinter import ttk
        from utils_tk import tk_center

        top = tk.Toplevel()
        top.withdraw()
        if title is None:
            title = 'Switch branch'
        top.wm_title(title)

        out = [None, None]

        if parent is None:
            parent = OMFITaux['rootGUI']
        top.wm_transient(parent)

        def onRemote(event=None):
            top.update_idletasks()
            branchSelectorOptions = list(self.get_branches(remoteSelector.get()).keys())
            branchSelectorOptions = sorted(branchSelectorOptions, key=lambda x: x.lower())
            branchSelector.configure(values=tuple(branchSelectorOptions))

        def onReturn(event=None):
            top.update_idletasks()
            self.switch_branch(branchSelector.get(), remoteSelector.get())
            out[:] = [branchSelector.get(), remoteSelector.get()]
            top.destroy()

        def onEscape(event=None):
            top.destroy()

        frm = ttk.Frame(top)
        frm.pack(side=tk.TOP, padx=5, pady=2, fill=tk.X, expand=tk.NO)
        ttk.Label(frm, text='git repository: ' + self.git_dir, justify=tk.LEFT).pack(side=tk.LEFT, anchor=tk.W)

        frm = ttk.Frame(top)
        frm.pack(side=tk.TOP, padx=5, pady=2, fill=tk.X, expand=tk.NO)
        ttk.Label(frm, text='Remote: ').pack(side=tk.LEFT)
        remoteSelector = ttk.Combobox(frm, width=50)
        remoteSelector.pack(side=tk.LEFT, fill=tk.X, expand=tk.YES)
        remoteSelector.bind('<<ComboboxSelected>>', func=onRemote)
        remoteSelectorOptions = sorted(self.get_remotes(), key=lambda x: x.lower())
        remoteSelector.configure(values=tuple(remoteSelectorOptions))
        remoteSelector.configure(state='readonly')

        frm = ttk.Frame(top)
        frm.pack(side=tk.TOP, padx=5, pady=2, fill=tk.X, expand=tk.NO)
        ttk.Label(frm, text='Branch: ').pack(side=tk.LEFT)
        branchSelector = ttk.Combobox(frm)
        branchSelector.pack(side=tk.LEFT, fill=tk.X, expand=tk.YES)
        if only_existing_branches:
            branchSelector.configure(state='readonly')

        top.bind('<Return>', onReturn)
        top.bind('<Escape>', onEscape)

        remoteSelector.set(remote)
        branchSelector.set(branch)
        onRemote()

        top.protocol("WM_DELETE_WINDOW", top.destroy)
        top.resizable(False, False)
        tk_center(top, parent)
        top.deiconify()
        top.update_idletasks()
        top.wait_window(top)

        if out[0] == out[1] == None:
            return None
        else:
            return out[0], out[1]

    def remote_branches_details(self, remote='origin', skip=['unstable', 'master', 'daily_.*', 'gh-pages']):
        """
        returns a list of strings with the details of the branches on a given remote
        This function is useful to identify stale branches.

        :param remote: remote repository

        :param skip: branches to skip

        :return: list of strings
        """
        skip = [remote + '/' + item for item in skip]
        lst = []
        for remote_branch in self('branch -r').split():
            if remote_branch.startswith(remote + '/') and not np.any([re.findall('^' + item + '$', remote_branch) for item in skip]):
                lst.append(self('show --format="%ci %cr %an" ' + remote_branch).split('\n')[0] + ' ' + remote_branch)
        return list(reversed(sorted(lst)))


# ---------------------
# miscellaneous
# ---------------------


def omfit_hash(string, length=-1):
    """
    Hash a string using SHA1 and truncate hash at given length
    Use this function instead of Python hash(string) since with
    Python 3 the seed used for hashing changes between Python sessions

    :param string: input string to be hashed

    :param length: lenght of the hash (max 40)

    :return: SHA1 hash of the string in hexadecimal representation
    """
    import hashlib

    m = hashlib.sha1()
    m.update(string.encode("UTF-8"))
    return m.hexdigest()[:length]


def omfit_numeric_hash(string, length=-1):
    """
    Hash a string using SHA1 and truncate integer at given length
    Use this function instead of Python hash(string) since with
    Python 3 the seed used for hashing changes between Python sessions

    :param string: input string to be hashed

    :param length: lenght of the hash (max 47)

    :return: SHA1 hash of the string in integer representation
    """
    return int(str(int(omfit_hash(string), 16))[:length])


def find_library(libname, default=None):
    """
    This function returns the path of the matching library name

    :param libname: name of the library to look for (without `lib` and extension)

    :param default: what to return if library is not found

    :return:
    """
    from ctypes.util import find_library as _find_library

    lib_tmp = 'lib' + libname + '.so'
    if platform.system() == 'Darwin':
        import ctypes.macholib.dyld

        dlib = ctypes.macholib.dyld.DEFAULT_LIBRARY_FALLBACK
        added = False
        if sys.prefix + '/lib' not in dlib:
            added = True
            dlib.insert(0, sys.prefix + '/lib')
        lib = _find_library(lib_tmp)
        if added:
            ctypes.macholib.dyld.DEFAULT_LIBRARY_FALLBACK.remove(sys.prefix + '/lib')
            if 'DYLD_LIBRARY_PATH' in os.environ:
                del os.environ['DYLD_LIBRARY_PATH']

    else:
        lib = _find_library(libname)
        for k in os.environ.get('LD_LIBRARY_PATH', '').split(':'):
            if os.path.exists(k + os.sep + lib_tmp):
                lib = k + os.sep + lib_tmp
                break

    if lib is None:
        if default is not None:
            lib = default
        else:
            raise Exception(lib_tmp + ' not found in LD_LIBRARY_PATH')

    return lib


def find_file(reg_exp_filename, path):
    """
    find all filenames matching regular expression under a path

    :param reg_exp_filename: regular expression for the file to match

    :param path: folder where to look

    :return: list of filenames matching regular expression with full path
    """
    match = []
    for root, dirs, names in os.walk(path):
        for name in names:
            if reg_exp_filename == name or re.match(reg_exp_filename, name):
                match.append(os.path.join(root, name))
    return match


def _isdebugging():
    """
    Function that returns True/False if function is run in debugging mode

    :return: True/False
    """
    for frame in inspect.stack():
        if frame[1].endswith("pydevd.py"):
            return True
    return False


OMFIT_is_in_debug_mode = _isdebugging()


def sleep(sleeptime):
    """
    Non blocking sleep

    :param sleeptime: time to sleep in seconds

    :return: None
    """
    if sleeptime <= 0:
        return
    if 'rootGUI' in OMFITaux and OMFITaux['rootGUI'] is not None and not len(OMFITaux['prun_process']):
        import tkinter as tk

        finished = tk.BooleanVar()
        finished.set(False)

        def goOn():
            OMFITaux['rootGUI'].update_idletasks()
            finished.set(True)
            OMFITaux['rootGUI'].update_idletasks()

        OMFITaux['rootGUI'].after(int(sleeptime * 1000), goOn)
        OMFITaux['rootGUI'].wait_variable(finished)
    else:
        time.sleep(sleeptime)


def now(format_out='%d %b %Y  %H:%M', timezone=None):
    """

    :param format_out: https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior

    :param timezone: [string] look at /usr/share/zoneinfo for available options
                     CST6CDT      Europe/?     Hongkong     MST          Portugal     WET
                     Africa/?     Canada/?     Factory      Iceland      MST7MDT      ROC
                     America/?    Chile/?      GB           Indian/?     Mexico/?     ROK
                     Antarctica/? Cuba         GB-Eire      Iran         NZ           Singapore
                     Arctic/?     EET          GMT          Israel       NZ-CHAT      Turkey
                     Asia/?       EST          GMT+0        Jamaica      Navajo       UCT
                     Atlantic/?   EST5EDT      GMT-0        Japan        PRC          US/?
                     Australia/?  Egypt        GMT0         Kwajalein    PST8PDT      UTC
                     Brazil/?     Eire         Greenwich    Libya        Pacific/?    Universal
                     CET          Etc/?        HST          MET          Poland       W-SU
                     Zulu

    :return: formatted datetime string
             if format_out is None, return datetime object
    """
    if timezone is not None:
        from dateutil import tz

        resolved_timezone = tz.gettz(timezone)
        if resolved_timezone is None:
            raise ValueError('Timezone `%s` not recognized! see /usr/share/zoneinfo/' % timezone)
        timezone = resolved_timezone
    dt = datetime.datetime.now(timezone)
    if format_out is None:
        return dt
    return dt.strftime(format_out)


def convertDateFormat(date, format_in='%d/%m/%Y %H:%M', format_out='%d %b %Y  %H:%M'):
    """
    :param date: string date or float timestamp

    :param format_in: date format of the input (ignored if date is float timestamp)

    :param format_out: date format of the wanted output

    :return: string date in new format
    """
    if is_int(date) or is_float(date):
        return datetime.datetime.fromtimestamp(date).strftime(format_out)
    else:
        return datetime.datetime.strptime(date, format_in).strftime(format_out)
    if format_out == "%s":  # "%s" is not working correctly under windows
        return DT.timestamp()
    else:
        return DT.strftime(format_out)


def update_dir(root_src_dir, root_dst_dir):
    """
    Go through the source directory, create any directories that do not already exist in destination directory,
    and move files from source to the destination directory
    Any pre-existing files will be removed first (via os.remove) before being replace by the corresponding source file.
    Any files or directories that already exist in the destination but not in the source will remain untouched

    :param root_src_dir: Source directory

    :param root_dst_dir: Destination directory
    """
    for src_dir, dirs, files in os.walk(root_src_dir):
        dst_dir = src_dir.replace(root_src_dir, root_dst_dir, 1)
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)
        for file_ in files:
            src_file = os.path.join(src_dir, file_)
            dst_file = os.path.join(dst_dir, file_)
            if os.path.exists(dst_file):
                os.remove(dst_file)
            shutil.move(src_file, dst_dir)


def permissions(path):
    """
    :path: file path

    :return: file permissions as a (user, group, other) (read, write, execute) string, such as: rwxr-xr-x
    """
    s = os.lstat(path)
    p = ['-'] * 9
    signs = 'rwx'
    for i, flag in enumerate(
        [stat.S_IRUSR, stat.S_IWUSR, stat.S_IXUSR, stat.S_IRGRP, stat.S_IWGRP, stat.S_IXGRP, stat.S_IROTH, stat.S_IWOTH, stat.S_IXOTH]
    ):
        if s.st_mode & flag:
            p[i] = signs[i % 3]

    return ''.join(p)


def zipfolder(foldername, filename, compression=zipfile.ZIP_STORED, allowZip64=True):
    """
    compress folder to zip archive

    :param foldername: folder to compress

    :param filename: zip filename to use

    :param compression: compression algorythm

    :param allowZip64: use 64bit extension to handle files >4GB
    """
    filename = os.path.abspath(filename)
    if not os.path.exists(os.path.dirname(filename)):
        os.makedirs(os.path.dirname(filename))
    os.chdir(foldername)
    foldername = './'
    empty_dirs = []
    with zipfile.ZipFile(filename, 'w', compression=compression, allowZip64=allowZip64) as zip:
        for dirpath, dirs, files in os.walk(foldername):
            empty_dirs.extend([dir for dir in dirs if not len(os.listdir(os.sep.join([dirpath, dir])))])
            for name in files:
                zip.write(os.path.join(dirpath, name))
            # include empty folders
            for dir in empty_dirs:
                zif = zipfile.ZipInfo(os.sep.join([dirpath, dir]) + "/")
                zip.writestr(zif, "")
            empty_dirs = []


def omfit_patch(obj, fun):
    """
    Patch a standard module/class with a new function/method.
    Moves original attribute to _original_<name> ONLY ONCE! If done
    blindly you will go recursive when reloading modules

    """
    import types

    name = fun.__name__.lstrip('_')
    ismod = isinstance(obj, types.ModuleType)
    if hasattr(obj, name) and not hasattr(obj, '_original_' + name):
        orig = getattr(obj, name)
        if ismod:
            setattr(obj, '_original_' + name, orig)  # save copy of original function
        else:
            setattr(obj, '_original_' + name, types.MethodType(orig, obj))  # save copy of original method
    if ismod:
        setattr(obj, name, fun)  # replace with modified method
    else:
        setattr(obj, name, types.MethodType(fun, obj))  # replace with modified method


def funny_random_name_generator(use_mood=False, digits=2):
    """
    Makes up a random name with no spaces in it. Funnier than timestamps.

    :param use_mood: bool
        Use a mood instead of a color
    :param digits: int
        Number of digits in the random number (default: 2)
    :return: string
        The default format is [color]_[animal]_[container]_[two digit number]
        Example: "blueviolet_kangaroo_prison_26"
        Colors come from matplotlib's list.
        Alternative formats selected by keywords:
        [mood]_[animal]_[container]_[two digit number]
        Example: "menacing_guppy_pen_85"

    """
    from matplotlib import colors as mcolors
    import random as rand
    import numpy as np

    colors = dict(mcolors.BASE_COLORS, **mcolors.CSS4_COLORS)
    # Sort colors by hue, saturation, value and name.
    by_hsv = sorted((tuple(mcolors.rgb_to_hsv(mcolors.to_rgba(color)[:3])), name) for name, color in colors.items())
    sorted_names = [name for hsv, name in by_hsv if len(name) > 1]
    color = rand.choice(sorted_names)

    moods = ['angry', 'happy', 'hangry', 'hungry', 'sad', 'baleful', 'menacing', 'joyful', 'benevolent', 'vindictive']
    mood = rand.choice(moods)
    animals = [
        'alligator',
        'bear',
        'beaver',
        'cat',
        'capricorn',
        'dog',
        'doggo',
        'dolphin',
        'emu',
        'fish',
        'goat',
        'gorilla',
        'guppy',
        'horse',
        'iguana',
        'ibex',
        'jackal',
        'kangaroo',
        'koala',
        'kitty',
        'lemur',
        'monkey',
        'markhor',
        'newt',
        'octopus',
        'penguin',
        'quail',
        'rat',
        'snake',
        'turtle',
        'tortoise',
        'vulture',
        'walrus',
        'yak',
        'zebra',
    ]
    animal = rand.choice(animals)
    containers = ['box', 'carton', 'vault', 'bag', 'purse', 'bowl', 'prison', 'bottle', 'cup', 'refrigerator', 'pen', 'paddock', 'barn']
    container = rand.choice(containers)
    number = rand.choice(range(int(10 ** digits)))

    name_format = '{}_{}_{}_{:0' + str(int(np.ceil(digits))) + 'd}'
    name = name_format.format(mood if use_mood else color, animal, container, number).replace(' ', '-')

    return name


def developer_mode(module_link=None, **kw):
    """
    Calls the OMFITmodule.convert_to_developer_mode() method for every top-level module in OMFIT

    Intended for convenient access in a command box script that can be called as soon as the project is reloaded.

    Accepts keywords related to OMFITmodule.convert_to_developer_mode() and passes them to that function.

    :param module_link: OMFITmodule or OMFIT instance
        Refence to the module to be converted or to top-level OMFIT
        If None, defaults to OMFIT (affecting all top-level modules)
    """
    from omfit_classes.omfit_base import OMFIT, OMFITmodule, relativeLocations

    if module_link is None:
        module_link = OMFIT

    MainScratch = OMFIT['scratch']
    MainScratch.setdefault('developerMode_convert_submodules', True)
    MainScratch.setdefault('developerMode_load_new_settings', True)
    MainScratch.setdefault('developerMode_operation', 'DEVEL')
    dirs = OMFITmodule.directories(checkIsWriteable=(MainScratch['developerMode_operation'] == 'DEVEL'))
    MainScratch.setdefault('developerMode_modules_directory', dirs[0])
    MainScratch.setdefault('developerMode_quiet', True)

    # Fill in defaults that don't depend on other settings
    keywords = dict(
        processSubmodules=True,
        loadNewSettings=True,
        operation='DEVEL',
        quiet=True,
    )
    # Replace defaults with MainScratch or supplied kw if available
    translations = dict(
        processSubmodules='developerMode_convert_submodules',
        loadNewSettings='developerMode_load_new_settings',
        operation='developerMode_operation',
        modulesDir='developerMode_modules_directory',
        quiet='developerMode_quiet',
    )
    for k, v in translations.items():
        if v in MainScratch:
            keywords[k] = copy.copy(MainScratch[v])
        if k in kw:
            keywords[k] = kw[k]
    # Finish assigning defaults for keywords whose default values depend on other keywords
    if 'modulesDir' not in keywords:
        dirs = OMFITmodule.directories(checkIsWriteable=(keywords['operation'] == 'DEVEL'))
        keywords['modulesDir'] = dirs[0]

    def announce_and_convert(the_module_, **kw2):
        options = {
            'Developer mode': 'DEVEL',
            'Standard mode': 'FREEZE',
            'Standard mode (RELOAD)': 'RELOAD',
        }
        printi(
            flip_values_and_keys(options)[MainScratch['developerMode_operation']]
            + ' '
            + relativeLocations(the_module_)['rootName']
            + ['', ' and all sub-modules'][MainScratch['developerMode_convert_submodules']]
        )
        the_module_.convert_to_developer_mode(**keywords)

    if module_link is OMFIT:
        for mname in OMFIT.moduleDict(level=0).keys():
            the_module = eval(f"OMFIT{mname}")
            announce_and_convert(the_module, **keywords)
            # the_module.convert_to_developer_mode(**keywords)
    else:
        announce_and_convert(module_link, **keywords)
        # module_link.convert_to_developer_mode(**keywords)

# ---------------------
# versions
# ---------------------
def sanitize_version_number(version):
    """Removes common non-numerical characters from version numbers obtained from git tags, such as '_rc', etc."""
    if version.startswith('.'):
        version = '-1' + version
    # Replace alpha, beta, release candidate *-a, *-b *-c endings with -3, -2, -1
    version = re.sub(r'([0-9]+)-?c', r'\1.-1', version)
    version = re.sub(r'([0-9]+)-?b', r'\1.-2', version)
    version = re.sub(r'([0-9]+)-?a', r'\1.-3', version)
    # More release candidate things
    version = re.sub(r'([0-9\-]+)_?rc([0-9\-]+)', r'\1\.-1\.\2', version)
    # Get rid of remaining non-numerics except for .-*
    version = re.sub(r'[^0-9\.\*\-]', '.', version)
    # Remove any -[char]
    version = re.sub(r'-[a-zA-Z\.]', '.', version)
    # Suppress repeated '.'
    while '..' in version:
        version = version.replace('..', '.')
    return version


def compare_version(version1, version2):
    """
    Compares two version numbers and determines which one, if any, is greater.

    This function can handle wildcards (eg. 1.1.*)
    Most non-numeric characters are removed, but some are given special treatment.
    a, b, c represent alpha, beta, and candidate versions and are replaced by numbers -3, -2, -1.
        So 4.0.1-a turns into 4.0.1.-3, 4.0.1-b turns into 4.0.1.-2, and then -3 < -2
        so the beta will be recognized as newer than the alpha version.
    rc# is recognized as a release candidate that is older than the version without the rc
        So 4.0.1_rc1 turns into 4.0.1.-1.1 which is older than 4.0.1 because 4.0.1 implies 4.0.1.0.0.
        Also 4.0.1_rc2 is newer than 4.0.1_rc1.

    :param version1: str
        First version to compare

    :param version2: str
        Second version to compare

    :return: int
        1 if version1 > version2
        -1 if version1 < version2
        0 if version1 == version2
        0 if wildcards allow version ranges to overlay. E.g. 4.* vs. 4.1.5 returns 0 (equal)
    """
    version1 = sanitize_version_number(version1)
    version2 = sanitize_version_number(version2)

    # Handle version wildcards
    if '*' in version1 or '*' in version2:
        version1 = version1.split('.')
        version2 = version2.split('.')
        start_asterix = False
        for k in range(max([len(version1), len(version2)])):
            if (k < len(version1) and version1[k] == '*') or (k < len(version2) and version2[k] == '*'):
                start_asterix = True
            if start_asterix:
                if k < len(version1):
                    version1[k] = '*'
                else:
                    version1.append('*')
                if k < len(version2):
                    version2[k] = '*'
                else:
                    version2.append('*')
        version1 = '.'.join(version1)
        version2 = '.'.join(version2)

    def version_int(x):
        if x in ['', ' ']:
            return 0
        elif x in '*':
            return x
        else:
            return int(x)

    def normalize(v):
        return [version_int(x) for x in re.sub(r'(\.0+)*$', '', v).split('.')]

    n1 = normalize(version1)
    n2 = normalize(version2)
    dn1 = len(n1) - len(n2)
    if dn1 < 0:
        n1 += [0] * -dn1
    elif dn1 > 0:
        n2 += [0] * dn1
    return (n1 > n2) - (n1 < n2)


def find_latest_version(versions):
    """
    Given a list of strings with version numbers like 1.2.12, 1.2, 1.20.5, 1.2.3.4.5, etc., find the maximum version
    number. Test with: print(repo.get_tag_version('v'))

    :param versions: List of strings like ['1.1', '1.2', '1.12', '1.1.13']

    :return: A string from the list of versions corresponding to the maximum version number.
    """
    printd('Finding latest version among {}...'.format(versions))

    versions = tolist(copy.deepcopy(versions))
    # Pre-sanitization makes find_latest_version faster: 0.15 vs 0.18 s.
    versions = [sanitize_version_number(version) for version in versions]
    v = versions.pop()
    while len(versions):
        vt = versions.pop()
        if compare_version(v, vt) < 0:
            v = vt
    printd('Found latest version = {}'.format(v))
    return v


def check_installed_packages(requirements=OMFITsrc + '/../install/requirements.txt'):
    """
    Check version of required OMFIT packages

    :param requirements: path to the requirements.txt file

    :return: summary dictionary
    """

    wrong_version_text = 'python_version >' if sys.version_info < (3, 0) else 'python_version <'
    with open(requirements, 'r') as f:
        lines = [_f for _f in [x.split('#')[0].strip() for x in f.readlines()] if _f and wrong_version_text not in _f]

    lines = [line.split(';')[0].strip() for line in lines]
    # map package names with their python import name
    import yaml

    dependency_file = OMFITsrc + '/../install/omfit_dependencies.yaml'
    with open(dependency_file, 'r') as f:
        deps_doc = yaml.load(f, Loader=yaml.Loader)
    package_mapper = {}
    for k, item in enumerate(deps_doc['dependencies']):
        name = item['name']
        if item.get('pip', None) and item['pip'].get('name', None):
            name = item['pip']['name']
        if 'import_name' in item and item['import_name']:
            package_mapper[name] = item['import_name']

    summary = {}
    bad = {}
    for line in lines:
        try:
            package, tmp, required_version = re.match('([\w\d-]+)([=\>\<,]+)(.*)', line).groups()
            required_version = tmp + required_version
        except AttributeError:
            printe('Error getting package version from `%s`' % line)
            continue
        package = package_mapper.get(package, package)
        summary[package] = {}
        summary[package]['required_version'] = required_version
        try:
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=DeprecationWarning)
                exec('import ' + package)
        except ImportError as e:
            summary[package]['installed_version'] = None
            summary[package]['state'] = None
            bad[package] = summary[package]
            continue
        if not (hasattr(eval(package), '__version__') or hasattr(eval(package), 'version')):
            summary[package]['installed_version'] = ''
            summary[package]['state'] = True
        else:
            if hasattr(eval(package), '__version__'):
                installed_version = eval(package + '.__version__')
            elif hasattr(eval(package), 'version'):
                installed_version = eval(package + '.version')
            if ' ' in installed_version:
                installed_version = installed_version.split(' ')[0]
            summary[package]['installed_version'] = installed_version
            state = version_conditions_checker(installed_version, required_version)
            summary[package]['state'] = state
        if not state:
            bad[package] = summary[package]
    return {'summary': summary, 'bad': bad}


def version_conditions_checker(version, conditions):
    """
    Check that a given version passes all version conditions

    :param version: version to check

    :param conditions: conditions to be met (multiple conditions are separated by comma)

    :return: True if all conditions are satisfied, otherwise False
    """
    condition = conditions
    if ',' in conditions:
        bit = True
        for condition in conditions.split(','):
            bit = bit and version_conditions_checker(version, condition)
        return bit
    equality, required_version = re.match('([!=\>\<]+)(.*)', condition).groups()
    state = compare_version(version, required_version)
    if equality in ['==', '='] and state != 0:
        return False
    elif equality == '!=' and state == 0:
        return False
    elif equality == '<=' and state > 0:
        return False
    elif equality == '>=' and state < 0:
        return False
    elif equality == '>' and state <= 0:
        return False
    elif equality == '<' and state >= 0:
        return False
    return True


def summarize_installed_packages(required=True, optional=True, verbose=True):
    """
    :param required: report on required packages

    :param optional: report on optional packages

    :param verbose: print to console

    :return: status code and text
    """

    from warnings import filterwarnings

    filterwarnings('ignore')

    pline = ' {note:1} {package:22} : {installed_version:15} {required_version:15}'
    phead = {'note': '', 'package': 'package', 'installed_version': 'install', 'required_version': 'compare'}

    plist = []
    if optional:
        plist += [('OPTIONAL', 'optional.txt')]
    if required:
        plist += [('REQUIRED', 'requirements.txt')]

    _print = {' ': printi, '-': printw, '?': printw, 'x': printe}

    rc = 0
    txt = []
    for ptype, pfile in plist:

        txt.append('\nStatus of ' + ptype + ' Python packages:\n')
        if verbose:
            print(txt[-1])
        txt.append(pline.format(**phead))
        if verbose:
            print(txt[-1])

        res = check_installed_packages(os.path.join(OMFITsrc, '..', 'install', pfile))['summary']
        for p in sorted(res, key=lambda k: k.lower()):
            if res[p]['state']:
                note = ' '
            elif res[p]['state'] is False:
                if res[p]['installed_version'] == '':
                    note = '?'
                else:
                    note = '-'
            elif ptype == 'REQUIRED':
                note = 'x'
                rc += 1
            else:
                note = '-'
            if res[p]['installed_version'] is None:
                res[p]['installed_version'] = ''
            txt.append(pline.format(note=note, package=p, **res[p]))
            if verbose:
                _print[note](txt[-1])
    if verbose:
        print('')
    return rc, '\n'.join(txt)


def installed_packages_summary_as_text(installed_packages):
    """
    Return a formatted string of the dictionary returned by check_installed_packages()

    :param installed_packages: dictionary generated by check_installed_packages()

    :return: text representation of the check_installed_packages() dictionary
    """
    text = []
    for package in sorted(installed_packages['summary']):
        text.append(
            '{package:22}  {installed_version:15} {required_version:15}{bad}'.format(
                package=package.ljust(max([len(x) + 1 for x in list(installed_packages['summary'].keys())])),
                bad=['', ' (!)'][package in installed_packages['bad']],
                **installed_packages['summary'][package],
            )
        )
    return '\n'.join(text)


# The current session temporary directory
OMFITsessionDir = OMFITtmpDir + os.sep + 'OMFIT_' + now("%Y-%m-%d_%H_%M_%S_%f")


def purge_omfit_temporary_files():
    """
    Utility function to purge OMFIT temporary files
    """
    from omfit_classes.utils_base import OMFITtmpDir, size_of_dir, sizeof_fmt
    from omfit_classes.startup_framework import OMFITglobaltmpDir

    def ask(question):
        return input('\n' + question + ' y/[n] ') in ['y', 'Y']

    def print_single_folder(folder, size=None, sub=False):
        if size is None:
            size = size_of_dir(folder) if os.path.exists(folder) else 0
        _print = printi if size < 1024 ** 3 else printw
        _print('   \_' if sub else ' \___', '{size:12} {folder}'.format(size=sizeof_fmt(size, separator=' '), folder=folder))

    def print_multi_folder(folder):
        empties = 0
        print_single_folder(folder)
        for path, dirs, files in os.walk(folder):
            for subdir in dirs:
                subfolder = os.path.join(path, subdir)
                subsize = size_of_dir(subfolder)
                if subsize > 0:
                    print_single_folder(subfolder, sub=True)
                else:
                    empties += 1
            break
        if empties:
            print_single_folder('%d empty subfolders' % empties, size=0, sub=True)

    def rm_dir(d):
        if os.path.exists(d):
            try:
                shutil.rmtree(d)
                printe('Deleted:', d)
            except Exception as e:
                printe('Error:', repr(e))

    # main folders
    folders = [OMFITtmpDir]
    if OMFITglobaltmpDir != OMFITtmpDir:
        folders.append(OMFITglobaltmpDir)

    # initial summary
    print('\nList and size of OMFIT temporary folders:\n')
    for folder in folders:
        print_multi_folder(folder)

    # specific logic
    if ask('Delete OMFIT_TMP in its entirety?'):
        rm_dir(OMFITtmpDir)
    else:
        if ask('Delete OMFIT_TMP/OMFIT_2* session subfolders?'):
            for path, dirs, files in os.walk(OMFITtmpDir):
                for subdir in dirs:
                    if subdir.startswith('OMFIT_2'):
                        rm_dir(os.path.join(path, subdir))
                break
    if OMFITglobaltmpDir != OMFITtmpDir:
        if ask('Delete OMFIT_GLOBAL_TMP in its entirety?'):
            rm_dir(OMFITglobaltmpDir)
        else:
            subfolder = os.path.join(OMFITglobaltmpDir, 'runs')
            if os.path.exists(subfolder) and ask('Delete OMFIT_GLOBAL_TMP/runs simulation subfolder?'):
                rm_dir(subfolder)

    # final summary
    print('\nResult:\n')
    for folder in folders:
        print_multi_folder(folder)
    print()

    # quiet cleanup
    if os.path.exists(OMFITsessionDir):
        shutil.rmtree(OMFITsessionDir)
