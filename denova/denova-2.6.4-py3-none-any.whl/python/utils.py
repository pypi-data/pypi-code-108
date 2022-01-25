'''
    Python programming utilities.

    Utility classes and functions. Mostly utiities about python,
    not just in python.

    This module also holds code that hasn't been categorized into
    other packages. For example, many functions could go in
    denova.os.fs.

    Copyright 2009-2022 DeNova
    Last modified: 2022-01-10

    This file is open source, licensed under GPLv3 <http://www.gnu.org/licenses/>.
'''

import bz2
import gzip as gz
import importlib
import io
import locale
import os
import os.path
import string
import re
import sys
import trace
import traceback
import types
import unicodedata
import zipfile
from contextlib import contextmanager
from fnmatch import fnmatch
from glob import glob
from io import StringIO
from subprocess import CalledProcessError
from urllib.parse import urlparse
from tempfile import gettempdir

#from denova.python._log import log

version = sys.version_info[0]
prefered_encoding = 'utf-8'

# we can't use denova.python.log here because denova.python.log uses this module
_debug = False
if _debug:
    def log(msg):
        print(msg)
else:
    def log(msg):
        pass

Http_Separator = '://'

# linux allows almost any characters, but this is cross platform pathnames
valid_pathname_chars = f"-_.()/\\: {string.ascii_letters}{string.digits}"

class NotImplementedException(Exception):
    ''' Operation not implemented exception. '''
    pass

class MovedPermanentlyException(Exception):
    ''' Object moved permanently exception.

        Always say where it was moved. '''
    pass

def set_default_encoding(encoding=prefered_encoding):
    '''
        >>> set_default_encoding(prefered_encoding)
        >>> encoding = sys.getdefaultencoding()
        >>> encoding == 'utf-8'
        True
    '''

    # only available in python2
    pass

def dynamically_import_module(name):
    '''
        Dynamically import a module. See python docs on __import__()

        >>> module_str = str(dynamically_import_module('denova.python'))
        >>> module_str.startswith("<module 'denova.python' from ")
        True
        >>> module_str.endswith("denova/python/__init__.py'>")
        True
     '''

    module = __import__(name)
    components = name.split('.')
    for component in components[1:]:
        module = getattr(module, component)
    return module

def dynamic_import(name):
    '''
        >>> module_str = str(dynamic_import('denova.python'))
        >>> module_str.startswith("<module 'denova.python' from ")
        True
        >>> module_str.endswith("denova/python/__init__.py'>")
        True
    '''
    # from Python Library Reference, Built-in Functions, __import__
    mod = __import__(name)
    components = name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod

def print_imported_modules(filename):
    ''' Print modules imported by filename.

        Warning: Runs filename.

        >>> # how do we test this? how we generally use it:
        >>> # print_imported_modules(__file__)
    '''

    import modulefinder

    if filename.endswith('.pyc') or filename.endswith('.pyo'):
        filename = filename[:-1]
    print(filename)

    finder = modulefinder.ModuleFinder()
    finder.run_script(filename)

    # See /usr/share/doc/python2.7/html/library/modulefinder.html
    print('Loaded modules:')
    for name in sorted(finder.modules.keys()):
        mod = finder.modules[name]
        print(f'    {name}: {mod}')
        globalnames = list(mod.globalnames.keys())
        modules = sorted(globalnames[:3])
        print(','.join(modules))

    print('Modules not imported:')
    keys = finder.badmodules.keys()
    for name in keys:
        print(f'    {name}')

def object_name(obj, include_repr=False):
    ''' Get a human readable type name of a module, function, class, class method, or instance.

        The name is not guaranteed to be unique.

        If include_repr is True, an instance has its string representation appended.

        >>> import datetime
        >>> object_name(datetime.date)
        'datetime.date'

        >>> object_name('test string')
        'builtins.str instance'

        >>> class TestClass():
        ...     pass
        >>> name =object_name(TestClass)
        >>> name == 'denova.python.utils.TestClass' or name == '__main__.TestClass'
        True
        >>> inst = object_name(TestClass())
        >>> inst == 'denova.python.utils.TestClass instance' or inst == '__main__.TestClass instance'
        True

        To do: Consider using 'inspect' module.
    '''

    #package_name = getattr(obj, '__package__', None)
    module_name = getattr(obj, '__module__', None)
    local_object_name = getattr(obj, '__name__', None)

    """
    print(f'obj: {obj}, type(obj): {type(obj)}') #DEBUG
    print(f'initial package_name: {package_name}, type(package_name): {type(package_name)}') #DEBUG
    print(f'initial module_name: {module_name}, type(module_name): {type(module_name)}') #DEBUG
    print(f'initial local_object_name: {local_object_name}, type(local_object_name): {type(local_object_name)}') #DEBUG
    """

    name = None

    if module_name and local_object_name:
        name = f'{module_name}.{local_object_name}'

    elif local_object_name:
        name = local_object_name

    else:
        class_obj = getattr(obj, '__class__', None)
        class_module_name = getattr(class_obj, '__module__', None)
        local_object_name = getattr(class_obj, '__name__', None)

        """
        print(f'obj.__class__: {obj.__class__}, type(obj.__class__): {type(obj.__class__)}') #DEBUG
        print(f'class_obj: {class_obj}, type(class_obj): {type(class_obj)}') #DEBUG
        print(f'class_module_name: {class_module_name}, type(class_module_name): {type(class_module_name)}') #DEBUG
        print(f'local_object_name: {local_object_name}, type(local_object_name): {type(local_object_name)}') #DEBUG
        """

        name = f'{class_module_name}.{local_object_name} instance'
        if include_repr:
            name = f'{name}: {repr(obj)}'

    return name

def caller_id(ignore=None):
    ''' Return standard caller id string. '''

    filename, line = caller(ignore=ignore)
    return f'{filename}:{line}'

def caller(ignore=None, this_module_valid=False):
    ''' Returns (filename, linenumber) of the caller.

        To ignore calls from the current module::
            filename, line = caller(ignore=[__file__])
        This could conceivably ignore extra files if __file__ contains '.' etc.

        If this function is called from this module, set this_module_valid=True.
    '''

    def ignore_filename(filename):
        ''' Ignore files in ignore list and runpy.py. '''

        ignored = False
        if filename.endswith('/runpy.py'):
            ignored = True
        else:
            for pattern in _ignore:
                if re.match(pattern, filename):
                    ignored = True

        return ignored

    if ignore:
        _ignore = ignore
    else:
        _ignore = []
    # ignore denova.python.utils unless this_module_valid=True
    if not this_module_valid:
        _ignore = _ignore + [__file__]

    call_line = None

    stack = list(traceback.extract_stack())
    stack.reverse()
    for filename, linenumber, _, _ in stack:
        if not call_line:
            if not ignore_filename(filename):
                __, __, filename = filename.rpartition('/') # DEBUG
                call_line = (filename, linenumber)

    return call_line

def caller_module_name(ignore=None, this_module_valid=False):
    ''' Get the caller's fully qualified module name.

        If this function is called from this module, set this_module_valid=True.

        To do: Test linked package dirs in parent dirs.

        To get the parent caller instead of the module that actually
        calls caller_module_name():

            name = caller_module_name(ignore=[__file__])

        >>> # this code really needs to be tested from a different module
        >>> name = caller_module_name(this_module_valid=True)
        >>> name.endswith('utils')
        True
        >>> name = caller_module_name(ignore=[__file__], this_module_valid=True)
        >>> 'caller_module_name' in name
        True
    '''

    def ignore_filename(filename):
        ''' Ignore files in ignore list and runpy.py. '''

        if _debug_caller_module_name: print(f'in ignore_filename() ignore: {repr(ignore)}') #DEBUG
        return (filename in ignore) or filename.endswith('/runpy.py')

    def is_python_module_dir(dirname):
        # a python module dir has an __init__.py file
        init_path = os.path.join(dirname, '__init__.py')
        return os.path.exists(init_path)

    def strip_py(filename):
        if filename.endswith('.py'):
            filename, _, _ = filename.rpartition('.')
        return filename

    _debug_caller_module_name = False

    if _debug_caller_module_name: print(f'ignore: {repr(ignore)}') #DEBUG

    # make ignore list
    if ignore:
        _ignore = ignore
    else:
        _ignore = []
    # ignore denova.python.utils unless this_module_valid=True
    if not this_module_valid:
        _ignore = _ignore + [__file__]
    # make stack and __file__ filenames match
    ignore = []
    for filename in _ignore:
        # the ignore=[...] param is usually ignore=[__file__]
        # stack filenames end in .py; __file__ filenames end in .pyc or .pyo
        # make them all .py
        basename, _, extension = filename.rpartition('.')
        if extension == 'pyc' or extension == 'pyo':
            filename = basename + '.py'
        ignore.append(filename)

    name = None

    if _debug_caller_module_name:
        print('caller_module_name traceback.extract_stack():') #DEBUG
        for stack_item in traceback.extract_stack():
            print(f'    {stack_item}') #DEBUG

    stack = list(traceback.extract_stack())
    stack.reverse()
    # filename, line number, function name, text
    for filename, _, _, _ in stack:

        if not name:
            if ignore_filename(filename):
                if _debug_caller_module_name: print(f'caller_module_name ignored filename: {filename}') #DEBUG

            else:
                if _debug_caller_module_name: print(f'caller_module_name filename: {filename}') #DEBUG
                # find python module dirs in filename
                modules = []
                dirname, _, basename = filename.rpartition('/')
                while dirname and is_python_module_dir(dirname):
                    #if _debug_caller_module_name: print(f'caller_module_name is_python_module_dir: {dirname}') #DEBUG
                    modules.append(os.path.basename(dirname))
                    dirname, _, _ = dirname.rpartition('/')
                modules.reverse()

                # if the filename is a __main__.py for a package, just use the package name
                if basename != '__main__.py':
                    modules.append(strip_py(basename))
                #if _debug_caller_module_name: print(f'caller_module_name modules: {repr(modules))}' #DEBUG

                name = '.'.join(modules)

    if _debug_caller_module_name: print(f'caller_module_name: {name}') #DEBUG
    return name

def is_package_type(object):
    '''
        Returns True if object is a python package, else False.

        >>> import denova.python
        >>> is_package_type(denova.python)
        True
        >>> import denova.python.utils
        >>> is_package_type(denova.python.utils)
        False
    '''

    # this seems to be roughly what python does internally
    return (is_module_type(object) and
        (os.path.basename(object.__file__).endswith('__init__.py') or
         os.path.basename(object.__file__).endswith('__init__.pyc') or
         os.path.basename(object.__file__).endswith('__init__.pyo')))

def is_module_type(object):
    ''' Returns True if object is a python module, else False.

        Convenience function for symmetry with is_package_type().

        >>> import denova.python
        >>> is_module_type(denova.python)
        True
        >>> import denova.python.utils
        >>> is_module_type(denova.python.utils)
        True
    '''

    return isinstance(object, types.ModuleType)

def is_instance(obj, cls):
    '''
        More reliable version of python builtin isinstance()

        >>> is_instance('denova.python', str)
        True
    '''

    log(f'is_instance(obj={obj}, cls={cls})')
    log(f'is_instance() type: obj={type(obj)}, cls={type(cls)}')
    try:
        mro = obj.__mro__
    except AttributeError:
        mro = type(obj).__mro__
    log(f'is_instance() mro: {mro}')
    match = cls in mro

    log(f'is_instance() match: {match}')
    return match

def is_class_instance(obj):
    ''' Returns whether the object is an instance of any class.

        You can't reliably detect a class instance with

            isinstance(obj, types.InstanceType)

        as of Python 2.6 2013-05-02. The types module only handles old style
        python defined classes, so types.InstanceType only detects instances
        of the same style.

        >>> import datetime
        >>> c_style_class_instance = datetime.date(2000, 12, 1)
        >>> is_class_instance(c_style_class_instance)
        True

        >>> class OldStyleClass:
        ...     class_data = 27
        ...
        ...     def __init__(self):
        ...         self.instance_data = 'idata'

        ...     def instance_function(self):
        ...         return 3
        >>> old_c = OldStyleClass()
        >>> is_class_instance(old_c)
        True

        >>> class NewStyleClass(object):
        ...     class_data = 27
        ...
        ...     def __init__(self):
        ...         self.instance_data = 'idata'

        ...     def instance_function(self):
        ...         return 3
        >>> new_c = NewStyleClass()
        >>> is_class_instance(new_c)
        True

        >>> # base types are not instances
        >>> is_class_instance(2)
        False
        >>> is_class_instance([])
        False
        >>> is_class_instance({})
        False

        >>> # classes are not instances
        >>> is_class_instance(datetime.date)
        False
        >>> is_class_instance(OldStyleClass)
        False
        >>> is_class_instance(NewStyleClass)
        False

        >>> # test assumptions and python imlementation details

        >>> t = type(2)
        >>> str(t) == "<class 'int'>"
        True
        >>> t = type([])
        >>> str(t) == "<class 'list'>"
        True
        >>> t = type({})
        >>> str(t) == "<class 'dict'>"
        True

        >>> cls = getattr(2, '__class__')
        >>> str(cls) == "<class 'int'>"
        True
        >>> superclass = getattr(cls, '__class__')
        >>> str(superclass) == "<class 'type'>"
        True

        >>> t = str(type(datetime.date))
        >>> t == "<class 'type'>"
        True
        >>> t = str(type(c_style_class_instance))
        >>> t == "<class 'datetime.date'>"
        True
        >>> t = repr(datetime.date)
        >>> t == "<class 'datetime.date'>"
        True
        >>> repr(c_style_class_instance)
        'datetime.date(2000, 12, 1)'
        >>> isinstance(c_style_class_instance, types.MethodType)
        False
        >>> hasattr(c_style_class_instance, '__class__')
        True
        >>> '__dict__' in dir(c_style_class_instance)
        False
        >>> cls = c_style_class_instance.__class__
        >>> hasattr(cls, '__class__')
        True
        >>> '__dict__' in dir(cls)
        False
        >>> hasattr(cls, '__slots__')
        False
        >>> cls = getattr(c_style_class_instance, '__class__')
        >>> str(cls) == "<class 'datetime.date'>"
        True
        >>> superclass = getattr(cls, '__class__')
        >>> str(superclass) == "<class 'type'>"
        True

        >>> ok = '__dict__' in dir(old_c)
        >>> ok == True
        True
        >>> hasattr(old_c, '__slots__')
        False

        >>> '__dict__' in dir(new_c)
        True
        >>> hasattr(new_c, '__slots__')
        False

        '''

    type_str = str(type(obj))

    # old style python defined classes
    if type_str == "<class 'instance'>":
        is_instance = True

    # C defined classes
    elif type_str.startswith('<class '):
        # base types don't have a dot
        is_instance =  '.' in type_str

    # new style python defined classes
    elif type_str.startswith('<'):
        # if it has an address, it's an instance, not a class
        is_instance =  ' 0x' in repr(obj)

    else:
        is_instance = False

    return is_instance

    """ does not detect c-style classes e.g. datetime.xyz
    def is_old_style_instance(obj):
        return isinstance(obj, types.InstanceType)

    def is_new_style_instance(obj):
        # http://stackoverflow.com/questions/14612865/how-to-check-if-object-is-instance-of-new-style-user-defined-class
        is_instance = False
        if hasattr(obj, '__class__'):
            cls = obj.__class__
            if hasattr(cls, '__class__'):
                is_instance = ('__dict__' in dir(cls)) or hasattr(cls, '__slots__')
        return is_instance

    return is_new_style_instance(obj) or is_old_style_instance(obj)
    """

def run(sourcecode):
    '''
        Run source code text.

        >>> run('print("hi")')
        hi
    '''

    # magic. bad. but wasted too many hours trying pythonic solutions
    # in python 2.7 importlib doesn't know spec.Specs is the same as dbuild.spec.Specs

    import tempfile

    __, exec_path = tempfile.mkstemp(
        suffix='.py',
        dir=gettempdir())

    log(f'sourcecode:\n{sourcecode.strip()}')

    with open(exec_path, 'w') as exec_file:
        exec_file.write(sourcecode)

    try:
        exec(compile(open(exec_path).read(), exec_path, 'exec'), globals())
    finally:
        os.remove(exec_path)

def import_module(name):
    '''
        Import with debugging

        >>> module_str = str(import_module("denova.os.user"))
        >>> module_str.startswith("<module 'denova.os.user' from ")
        True
        >>> module_str.endswith("denova/os/user.py'>")
        True
    '''

    try:
        log(f'import_module({name})') #DEBUG
        module = importlib.import_module(name)
        log(f'import_module() result: {module}') #DEBUG
    except ImportError as imp_error:
        log(f'unable to import {name}')
        log('ImportError: ' + str(imp_error))
        msg = f'could not import {name}'
        log(msg)
        # find out why
        from denova.os import command
        log(command.run(['python3', '-c', f'import {name}']).stderr)
        raise ImportError(msg)
    return module

def import_file(name, path):
    '''
        Import source file with debugging

        <<< module = import_file(__file__, '/usr/local/lib/python3.9/dist-packages/denova/os/user.py')
        <<< print(str(module))
        <module 'python.py' from '/usr/local/lib/python3.9/dist-packages/denova/os/user.py'>
    '''

    import importlib

    try:
        log(f'import_file({path})') #DEBUG
        # deprecated in python 3.3
        # the 'right' way to do this varies greatly with the specific python version
        # see http://stackoverflow.com/questions/19009932/import-arbitrary-python-source-file-python-3-3
        #     http://bugs.python.org/issue21436
        # the following is undocumented in python 3, and may not work in all versions
        module = importlib.find_loader(name, path)
        log(f'import_file() result: {module}') #DEBUG
    except ImportError as imp_error:
        log(f'unable to import {path}')
        log('ImportError: ' + str(imp_error))
        msg = f'could not import {path}'
        log(msg)
        raise ImportError(msg)

    return module

def stacktrace():
    '''
        Returns a printable stacktrace.

        Contrary to the python docs, python often limits the number of
        frames in a stacktrace. This is a full stacktrace.

        >>> text = stacktrace()
        >>> assert text.strip().startswith('Traceback ')
        >>> assert 'utils.py' in text
    '''

    s = io.StringIO()
    s.write('Traceback (most recent call last):\n')
    traceback.print_stack(file=s)
    return s.getvalue()

def last_exception(noisy=False):
    ''' Returns a printable string of the last exception.

        If noisy=True calls say() with last_exception_only(). '''

    from denova.python.utils import say

    if noisy:
        say(last_exception_only())
    return traceback.format_exc()

def last_exception_only():
    ''' Returns a printable string of the last exception without a traceback. '''

    type, value, traceback = sys.exc_info()
    if type:
        s = str(type).split('.')[-1].strip('>').strip("'")
        if value is not None and len(str(value)):
            s += f': {value}'
    else:
        s = ''
    return s

def get_module(name):
    ''' Get the module based on the module name.

        The module name is available within a module as __name__.

        >>> module_str = str(get_module(__name__)) # doctest: +ELLIPSIS
        >>> module_str.startswith("<module 'denova.python.utils' from ") or module_str.startswith("<module '__main__' from 'utils.py'>")
        True
        >>> module_str.endswith("utils.py'>")
        True
    '''

    return sys.modules[name]

def caller_dir():
    ''' Get the caller's dir.

        This is actually the source dir for the caller of the caller of this module.
    '''

    stack = traceback.extract_stack()[:-2]
    (filename, line_number, function_name, text) = stack[0]
    return os.path.dirname(filename) or os.getcwd()

def caller_file():
    ''' Get the caller's file.

        This is actually the source file for the caller of the caller of this module.
    '''

    stack = traceback.extract_stack()[:-2]
    (filename, line_number, function_name, text) = stack[0]
    return filename

def format_exception(exc):
    ''' Format exception for printing.

        Bug: If exc is not the most recent, but is the same value
        as the most recent exception, we print the most recent traceback.
        This probably will almost never happen in practice.
    '''

    exc_type, exc_value, exc_traceback = sys.exc_info()
    # bug: if exc is not the most recent, but is the same exc_value
    if exc_value == exc:
        exc_str = traceback.format_exc()

    else:
        # the exc Exception is not the most recent, so no traceback
        log('log.debug() called with an exception but no traceback available')
        exc_str = traceback.format_exception_only(type(exc), exc)

    return exc_str

def is_string(obj):
    '''
        Return True iff obj is a string.

        >>> is_string('test')
        True
    '''

    return isinstance(obj, str)

def is_list(obj):
    '''
        Return True iff obj is a list.

        >>> is_list([])
        True
    '''

    log(type(obj))
    return isinstance(obj, list)


def is_tuple(obj):
    '''
        Return True iff obj is a tuple.

        >>> is_string('test')
        True
    '''

    return isinstance(obj, tuple)

def is_dict(obj):
    '''
        Return True iff obj is a dictionary.

        >>> is_string('test')
        True
    '''

    return isinstance(obj, dict)

def exec_trace(code, ignoredirs=[sys.prefix, sys.exec_prefix], globals=None, locals=None, coverdir='/tmp'):
    ''' Trace code.

        Code must be a string. Code must start without leading spaces in the string.

        exec_trace() usually requires passing "globals=globals(), locals=locals()".

        Example:
            from denova.python.utils import exec_trace
            exec_trace("""
from reinhardt.events import log_event
log_event(name, request=request, details=details)
                """,
                globals=globals(), locals=locals())
        '''

    tracer = trace.Trace(ignoredirs=ignoredirs)
    tracer.runctx(code.strip(), globals=globals, locals=locals)
    r = tracer.results()
    r.write_results(show_missing=True, coverdir=coverdir)

def pdb_break():
    ''' Breakpoint for pdb command line debugger.

    Usage:
        from denova.python.utils import pdb_break ; pdb_break()
    '''

    import pdb
    log('breakpointing for pdb')
    pdb.set_trace()

def winpdb_break():
    ''' Breakpoint for winpdb debugger.

        Example:
            from denova.python.utils import winpdb_break; winpdb_break() #DEBUG
    '''

    import rpdb2 #DEBUG
    log('breakpointing for winpdb')
    rpdb2.start_embedded_debugger("password") #DEBUG

def to_bytes(source, encoding=None):
    ''' Convenience method to convert to bytes. '''

    # if source is a string, encoding is required
    # in other cases it doesn't hurt
    if encoding is None:
        encoding = locale.getpreferredencoding(False)

    return bytes(source, encoding=encoding)

def get_scheme_netloc(url):
    ''' Return (scheme, netloc) from url.

        If the port is non-standard, the netloc is 'domain:port'. Otherwise
        netloc is the domain.

       This is used because python 2.4 and 2.5
       give slightly different results from urlparse.

        >>> get_scheme_netloc('http://DeNova.com')
        ('http', 'DeNova.com')
        >>> get_scheme_netloc('https://test:8211')
        ('https', 'test:8211')
    '''

    parsed_url = urlparse(url)

    try:
        scheme = parsed_url.scheme
        netloc = parsed_url.netloc
    except:   # 'bare except' because it catches more than "except Exception"
        scheme = parsed_url[0]
        netloc = parsed_url[1]

    return (scheme, netloc)

def get_remote_ip(request):
    '''Get the remote ip. If there is a forwarder, assume the first IP
       address (if there are more than 1) is the original machine's address.

       Otherwise, use the remote addr.

       Any errors, return 0.0.0.0
    '''

    Unknown_IP = '0.0.0.0'

    if request:
        try:
            # if we're using a reverse proxy, the ip is the proxy's ip address
            remote_addr = request.META.get('REMOTE_ADDR', '')
            forwarder = request.META.get('HTTP_X_FORWARDED_FOR', '')
            if forwarder and forwarder is not None and len(forwarder) > 0:
                m = re.match('(.*?),.*?', forwarder)
                if m:
                    remote_ip = m.group(1)
                else:
                    remote_ip = forwarder
            else:
                remote_ip = remote_addr

            if not remote_ip or remote_ip is None or len(remote_ip) <= 0:
                remote_ip = Unknown_IP
        except:   # 'bare except' because it catches more than "except Exception"
            log(traceback.format_exc())
            remote_ip = Unknown_IP
    else:
        remote_ip = Unknown_IP
        log('no request so returning unknown ip address')

    return remote_ip

def say(message):
    ''' Speak a message.

        Runs a "say" program, passing the message on the command line.
        Because most systems are not set up for speech, it is not an
        error if the "say" program is missing or fails.

        It is often easy to add a "say" program to a system. For example,
        a linux system using festival for speech can use a one line script:
            festival --batch "(SayText \"$*\")"

        Depending on the underlying 'say' command's implementation, say()
        probably does not work unless user is in the 'audio' group.

        >>> say('test say')
        '''

    enabled = True

    if enabled:
        try:
            from denova.os import command
            # the words are unintelligible, and usually all we want is to know something happened
            # message = 'tick' # just a sound #DEBUG
            # os.system passes successive lines to sh
            message = message.split('\n')[0]
            command.run('say', *message)
        except:   # 'bare except' because it catches more than "except Exception"
            pass

def generate_password(max_length=25, punctuation_chars='-_ .,!+?$#'):
    '''
        Generate a password.

        >>> len(generate_password())
        25
    '''

    # the password must be random, but the characters must be valid for django
    password = ''
    while len(password) < max_length:
        new_char = os.urandom(1)
        try:
            new_char = new_char.decode()
            # the character must be a printable character
            if ((new_char >= 'A' and new_char <= 'Z') or
                (new_char >= 'a' and new_char <= 'z') or
                (new_char >= '0' and new_char <= '9') or
                (new_char in punctuation_chars)):

                # and the password must not start or end with a punctuation
                if (new_char in punctuation_chars and
                    (len(password) == 0 or (len(password) + 1) == max_length)):
                    pass
                else:
                    password += new_char
        except:   # 'bare except' because it catches more than "except Exception"
            pass

    return password

def clean_pathname(pathname):
    ''' Clean a pathname by removing all invalid chars.

        See http://stackoverflow.com/questions/295135/turn-a-string-into-a-valid-pathname-in-python
        From that page, roughly:

            The unicodedata.normalize call replaces accented characters
            with the unaccented equivalent, which is better than simply
            stripping them out. After that all disallowed characters are
            removed. Doesn't avoid possible disallowed pathnames."
    '''

    ascii_pathname = unicodedata.normalize('NFKD', pathname.decode()).encode('ASCII', 'ignore')
    return ''.join(c for c in ascii_pathname if c in valid_pathname_chars)


def strip_spaces_and_blank_lines(data):
    '''
        Strip leading and trailing spaces plus blank lines.

        >>> data = "  This is the first line.  \\n   \\n\\n This is the second line.\\n"
        >>> strip_spaces_and_blank_lines(data)
        'This is the first line.\\nThis is the second line.\\n'
    '''

    try:
        if data is not None:
            new_data = []
            for line in data.split('\n'):
                line = trim(line, ' ').decode()
                if len(line.strip('\n')) > 0:
                    new_data.append(f'{line}\n')

            data = ''.join(new_data)
    except:   # 'bare except' because it catches more than "except Exception"
        print(traceback.format_exc())

    return data

def pipe(value, *fns):
    ''' Pipe data from functions a() to b() to c() to d() ...

        "pipe(x, a, b, c, d)" is more readble than "d(c(b(a(x))))".

        See http://news.ycombinator.com/item?id=3349429

        pipe() assumes every function in its list will consume and return the data.
        If you need more control such as filtering and routing, see
        the DeNova's coroutine package.

        >>> def sqr(x):
        ...     return x*x

        >>> def half(x):
        ...     return x/2.0

        >>> for i in range(5):
        ...     pipe(i, sqr, half)
        0.0
        0.5
        2.0
        4.5
        8.0
    '''

    for fn in fns:
        value = fn(value)
    return value

def ltrim(string, prefix):
    ''' Trim all prefixes from string. '''

    length = len(prefix)
    while string.startswith(prefix):
        string = string[length:]
    return string

def rtrim(string, suffix):
    ''' Trim all suffixes from string. '''

    length = len(suffix)
    while string.endswith(suffix):
        string = string[:-length]
    return string

def trim(string, xfix):
    ''' Trim all prefixes or suffixes of xfix from string. '''

    if is_string(string):
        string = string.encode()
    if is_string(xfix):
        xfix = xfix.encode()

    length = len(xfix)
    while string.startswith(xfix):
        string = string[length:]
    while string.endswith(xfix):
        string = string[:-length]
    return string

def remove_lines(string, count):
    ''' Remove lines from string.

        If count is negative, removes lines from end of string. '''

    if count > 0:
        string = '\n'.join(string.split('\n')[count:])
    elif count < 0:
        string = '\n'.join(string.split('\n')[:count])
    return string

def pathmatch(path, pattern):
    ''' Test whether the path matches the pattern.

        This is a mess that needs to be replaced with an ant-style path match.

        The pattern is a shell-style wildcard, not a regular expression.
        fnmatch.fnmatch tests filenames, not paths.

        '**' at the beginning of a pattern matches anything at the beginning
        of a path, but no other wildcards are allowed in the pattern. '''

    def split(path):
        path = os.path.expanduser(path)
        path = os.path.abspath(path)
        return path.split('/')

    if pattern.startswith('**'):
        result = path.endswith(pattern[2:])

    else:
        path = split(path)
        pattern = split(pattern)
        result = (len(path) == len(pattern) and
            all(fnmatch(path[i], pattern[i]) for i in range(len(path))))

    return result

def resolve_path(path):
    ''' Resolves file path wildcards, links, and relative directories.

        To resolve a wildcard path that matches more than one file, use
        glob() and pass each result to resolve_path().

        Returns None if wildcard does not match any files. Raises
        ValueError if wildcard matches more than one file. '''

    paths = glob(path)
    if paths:
        if len(paths) > 1:
            raise ValueError(f'Matches more than one path: {path}')
            path = os.path.normpath(os.path.realpath(paths[0]))
    else:
        path = None
    return path

def domain_base(domain):
    ''' Returns base name from domain.

        I.e. base.tld or base.co.countrydomain or base.com.countrydomain
        all have the same base name.

        E.g. google.com, google.bg, google.de, google.co.in all are based
        on google.

        This can be fooled by domain spoofers or squatters.

        >>> domain_base('denova.com')
        'denova'
    '''

    if type(domain) is bytes:
        domain = domain.decode()
    # regexes might be clearer (or not) but would be slower
    parts = domain.split('.')
    if len(parts) > 1:
        # toss the top level domain
        parts = parts[:-1]
        if len(parts) > 1:
            # toss generic second level domains
            if parts[-1] in ['com', 'co', 'org', 'net']:
                parts = parts[:-1]
    # top level left is the base name
    return parts[-1]

class textfile(object):
    ''' Open possibly gzipped text file as file using contextmanager.

        E.g. "with textfile('mytext.gz') as f".

        Avoids "AttributeError: GzipFile instance has no attribute '__exit__'"
        prior to Python 3.1.

        As of Python 2.6 contextlib.closing() doesn't work. It doesn't expose underlying
        gzip functions because its __enter__() returns the inner object, and it has no
        __getattr__()
        to expose the inner gzip.open(). '''

    def __init__(self, filename, rwmode='r'):
        if filename.endswith('.gz'):
            self.f = gz.open(filename, f'{rwmode}b')
        elif filename.endswith('.bz2'):
            self.f = bz2.BZ2File(filename, f'{rwmode}b')
        elif filename.endswith('.zip'):
            self.f = zipfile.ZipFile(filename, f'{rwmode}b')
        else:
            self.f = open(filename, rwmode)
        self.opened = True

    def __iter__(self):
        return iter(self.f)

    def __enter__(self):
        return self.f

    def __exit__(self, *exc_info):
        self.close()

    def unused_close(self):
        if self.opened:
            self.f.close()
            self.opened = False

    def __getattr__(self, name):
        return getattr(self.f, name)

def gzip(uncompressed):
    ''' Gzip a string '''

    compressed_fileobj = StringIO()
    with gz.GzipFile(fileobj=compressed_fileobj, mode='w') as f:  #, compresslevel=5) as f:
        f.write(uncompressed)
    return compressed_fileobj.getvalue()

def gunzip(compressed):
    ''' Gunzip a string '''

    compressed_fileobj = StringIO(compressed)
    with gz.GzipFile(fileobj=compressed_fileobj, mode='r') as f:
        uncompressed = f.read()
    return uncompressed

@contextmanager
def chdir(dirname=None):
    ''' Chdir contextmanager that restores current dir.

        From http://www.astropython.org/snippet/2009/10/chdir-context-manager

        This context manager restores the value of the current working
        directory (cwd) after the enclosed code block completes or
        raises an exception.  If a directory name is supplied to the
        context manager then the cwd is changed prior to running the
        code block.
    '''

    curdir = os.getcwd()
    try:
        if dirname is not None:
            os.chdir(dirname)
        yield
    finally:
        os.chdir(curdir)

def different(file1, file2):
    ''' Returns whether the files are different. '''

    # diff succeeds if there is a difference, and fails if no difference
    try:
        from denova.os import command
        command.run('diff', file1, file2, brief=True)
        different = False

    except CalledProcessError:
        different = True

    return different

def slugify(value):
    ''' Converts string to a form usable in a url withjout encoding.

        Strips white space from ends, converts to lowercase,
        converts spaces to hyphens, and removes non-alphanumeric characters.
    '''
    value = value.strip().lower()
    value = re.sub('[\s-]+', '-', value)

    newvalue = ''
    for c in value:
        if (
              (c >= 'A' and c <= 'Z') or
              (c >= 'a' and c <= 'z') or
              (c >= '0' and c <= '9') or
              c == '-' or
              c == '_'
              ):
            newvalue += c
    return newvalue

def replace_strings(text, replacements, regexp=False):
    """ Replace text. Returns new text.

        'replacements' is a dict of {old: new, ...}.
        Every occurence of each old string is replaced with the
        matching new string.

        If regexp=True, the old string is a regular expression.

        >>> text = 'ABC DEF 123 456'
        >>> replacements = {
        ...     'ABC': 'abc',
        ...     '456': 'four five six'
        ... }
        >>> replace_strings(text, replacements)
        'abc DEF 123 four five six'
    """

    for old in replacements:
        new = replacements[old]
        if regexp:
            text = re.sub(old, new, text)
        else:
            text = text.replace(old, new)
    return text

def delete_empty_files(directory):
    ''' Delete empty files in directory.

        Does not delete any subdirectories or files in them.

        >>> from tempfile import mkdtemp, mkstemp
        >>> directory = mkdtemp()
        >>> assert os.path.isdir(directory)
        >>> handle, filename1 = mkstemp(dir=directory)
        >>> os.close(handle)
        >>> assert os.path.exists(filename1)
        >>> handle, filename2 = mkstemp(dir=directory)
        >>> os.close(handle)
        >>> assert os.path.exists(filename2)
        >>> with open(filename2, 'w') as f2:
        ...     len = f2.write('data')
        >>> delete_empty_files(directory)
        >>> assert not os.path.exists(filename1)
        >>> assert os.path.exists(filename2)
        >>> os.remove(filename2)
        >>> assert not os.path.exists(filename2)
        >>> os.rmdir(directory)
        >>> assert not os.path.isdir(directory)
    '''

    wildcard = os.path.join(directory, '*')
    for filename in glob(wildcard):
        if os.path.getsize(filename) <= 0:
            os.remove(filename)

def randint(min=None, max=None):
    ''' Get a random int.

        random.randint() requires that you specify the min and max of
        the integer range for a random int. But you almost always want
        the min and max to be the system limits for an integer.
        If not use random.randint().

        'min' defaults to system minimum integer.
        'max' defaults to system maximum integer.
    '''

    import random

    maxsize = sys.maxsize

    if min is None:
        min = -(maxsize-1)
    if max is None:
        max = maxsize

    return random.randint(min, max)

def strip_youtube_hash(filename):
    ''' Strip youtube hash from end of filename '''

    if '.' in filename:
        rootname, _, extension = filename.rpartition('.')
        youtube_match = re.match(r'(.*)-[a-zA-Z0-9\-_]{11}$', rootname)
        if youtube_match:
            cleanroot = youtube_match.group(1)
            filename = cleanroot + '.' + extension
    return filename

def simplify_episode_filename(filename):
    ''' Strip junk from end of tv episode filename '''

    if '.' in filename:
        rootname, _, extension = filename.rpartition('.')
        cleanroot = re.sub(r'(.*)[Ss](\d\d)[Ee](\d\d).*', r'\1S\2E\3', rootname)
        filename = cleanroot + '.' + extension
    return filename

@contextmanager
def os_environ_context(environ):
    """ Context manager to restore os environment variables. """

    old_environ = dict(os.environ)
    os.environ.update(environ)

    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(old_environ)


if __name__ == "__main__":
    import doctest
    doctest.testmod()

