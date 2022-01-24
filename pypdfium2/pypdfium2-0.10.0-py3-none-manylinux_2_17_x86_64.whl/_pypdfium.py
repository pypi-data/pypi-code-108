r"""Wrapper for fpdf_annot.h

Generated with:
~/.local/bin/ctypesgen --library pdfium . -L . ./build_tar/include/fpdf_annot.h ./build_tar/include/fpdf_attachment.h ./build_tar/include/fpdf_catalog.h ./build_tar/include/fpdf_dataavail.h ./build_tar/include/fpdf_doc.h ./build_tar/include/fpdf_edit.h ./build_tar/include/fpdf_ext.h ./build_tar/include/fpdf_flatten.h ./build_tar/include/fpdf_formfill.h ./build_tar/include/fpdf_fwlevent.h ./build_tar/include/fpdf_javascript.h ./build_tar/include/fpdf_ppo.h ./build_tar/include/fpdf_progressive.h ./build_tar/include/fpdf_save.h ./build_tar/include/fpdf_searchex.h ./build_tar/include/fpdf_signature.h ./build_tar/include/fpdf_structtree.h ./build_tar/include/fpdf_sysfontinfo.h ./build_tar/include/fpdf_text.h ./build_tar/include/fpdf_thumbnail.h ./build_tar/include/fpdf_transformpage.h ./build_tar/include/fpdfview.h -o ./_pypdfium.py

Do not modify this file.
"""

__docformat__ = "restructuredtext"

# Begin preamble for Python

import ctypes
import sys
from ctypes import *  # noqa: F401, F403

_int_types = (ctypes.c_int16, ctypes.c_int32)
if hasattr(ctypes, "c_int64"):
    # Some builds of ctypes apparently do not have ctypes.c_int64
    # defined; it's a pretty good bet that these builds do not
    # have 64-bit pointers.
    _int_types += (ctypes.c_int64,)
for t in _int_types:
    if ctypes.sizeof(t) == ctypes.sizeof(ctypes.c_size_t):
        c_ptrdiff_t = t
del t
del _int_types



class UserString:
    def __init__(self, seq):
        if isinstance(seq, bytes):
            self.data = seq
        elif isinstance(seq, UserString):
            self.data = seq.data[:]
        else:
            self.data = str(seq).encode()

    def __bytes__(self):
        return self.data

    def __str__(self):
        return self.data.decode()

    def __repr__(self):
        return repr(self.data)

    def __int__(self):
        return int(self.data.decode())

    def __long__(self):
        return int(self.data.decode())

    def __float__(self):
        return float(self.data.decode())

    def __complex__(self):
        return complex(self.data.decode())

    def __hash__(self):
        return hash(self.data)

    def __le__(self, string):
        if isinstance(string, UserString):
            return self.data <= string.data
        else:
            return self.data <= string

    def __lt__(self, string):
        if isinstance(string, UserString):
            return self.data < string.data
        else:
            return self.data < string

    def __ge__(self, string):
        if isinstance(string, UserString):
            return self.data >= string.data
        else:
            return self.data >= string

    def __gt__(self, string):
        if isinstance(string, UserString):
            return self.data > string.data
        else:
            return self.data > string

    def __eq__(self, string):
        if isinstance(string, UserString):
            return self.data == string.data
        else:
            return self.data == string

    def __ne__(self, string):
        if isinstance(string, UserString):
            return self.data != string.data
        else:
            return self.data != string

    def __contains__(self, char):
        return char in self.data

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        return self.__class__(self.data[index])

    def __getslice__(self, start, end):
        start = max(start, 0)
        end = max(end, 0)
        return self.__class__(self.data[start:end])

    def __add__(self, other):
        if isinstance(other, UserString):
            return self.__class__(self.data + other.data)
        elif isinstance(other, bytes):
            return self.__class__(self.data + other)
        else:
            return self.__class__(self.data + str(other).encode())

    def __radd__(self, other):
        if isinstance(other, bytes):
            return self.__class__(other + self.data)
        else:
            return self.__class__(str(other).encode() + self.data)

    def __mul__(self, n):
        return self.__class__(self.data * n)

    __rmul__ = __mul__

    def __mod__(self, args):
        return self.__class__(self.data % args)

    # the following methods are defined in alphabetical order:
    def capitalize(self):
        return self.__class__(self.data.capitalize())

    def center(self, width, *args):
        return self.__class__(self.data.center(width, *args))

    def count(self, sub, start=0, end=sys.maxsize):
        return self.data.count(sub, start, end)

    def decode(self, encoding=None, errors=None):  # XXX improve this?
        if encoding:
            if errors:
                return self.__class__(self.data.decode(encoding, errors))
            else:
                return self.__class__(self.data.decode(encoding))
        else:
            return self.__class__(self.data.decode())

    def encode(self, encoding=None, errors=None):  # XXX improve this?
        if encoding:
            if errors:
                return self.__class__(self.data.encode(encoding, errors))
            else:
                return self.__class__(self.data.encode(encoding))
        else:
            return self.__class__(self.data.encode())

    def endswith(self, suffix, start=0, end=sys.maxsize):
        return self.data.endswith(suffix, start, end)

    def expandtabs(self, tabsize=8):
        return self.__class__(self.data.expandtabs(tabsize))

    def find(self, sub, start=0, end=sys.maxsize):
        return self.data.find(sub, start, end)

    def index(self, sub, start=0, end=sys.maxsize):
        return self.data.index(sub, start, end)

    def isalpha(self):
        return self.data.isalpha()

    def isalnum(self):
        return self.data.isalnum()

    def isdecimal(self):
        return self.data.isdecimal()

    def isdigit(self):
        return self.data.isdigit()

    def islower(self):
        return self.data.islower()

    def isnumeric(self):
        return self.data.isnumeric()

    def isspace(self):
        return self.data.isspace()

    def istitle(self):
        return self.data.istitle()

    def isupper(self):
        return self.data.isupper()

    def join(self, seq):
        return self.data.join(seq)

    def ljust(self, width, *args):
        return self.__class__(self.data.ljust(width, *args))

    def lower(self):
        return self.__class__(self.data.lower())

    def lstrip(self, chars=None):
        return self.__class__(self.data.lstrip(chars))

    def partition(self, sep):
        return self.data.partition(sep)

    def replace(self, old, new, maxsplit=-1):
        return self.__class__(self.data.replace(old, new, maxsplit))

    def rfind(self, sub, start=0, end=sys.maxsize):
        return self.data.rfind(sub, start, end)

    def rindex(self, sub, start=0, end=sys.maxsize):
        return self.data.rindex(sub, start, end)

    def rjust(self, width, *args):
        return self.__class__(self.data.rjust(width, *args))

    def rpartition(self, sep):
        return self.data.rpartition(sep)

    def rstrip(self, chars=None):
        return self.__class__(self.data.rstrip(chars))

    def split(self, sep=None, maxsplit=-1):
        return self.data.split(sep, maxsplit)

    def rsplit(self, sep=None, maxsplit=-1):
        return self.data.rsplit(sep, maxsplit)

    def splitlines(self, keepends=0):
        return self.data.splitlines(keepends)

    def startswith(self, prefix, start=0, end=sys.maxsize):
        return self.data.startswith(prefix, start, end)

    def strip(self, chars=None):
        return self.__class__(self.data.strip(chars))

    def swapcase(self):
        return self.__class__(self.data.swapcase())

    def title(self):
        return self.__class__(self.data.title())

    def translate(self, *args):
        return self.__class__(self.data.translate(*args))

    def upper(self):
        return self.__class__(self.data.upper())

    def zfill(self, width):
        return self.__class__(self.data.zfill(width))


class MutableString(UserString):
    """mutable string objects

    Python strings are immutable objects.  This has the advantage, that
    strings may be used as dictionary keys.  If this property isn't needed
    and you insist on changing string values in place instead, you may cheat
    and use MutableString.

    But the purpose of this class is an educational one: to prevent
    people from inventing their own mutable string class derived
    from UserString and than forget thereby to remove (override) the
    __hash__ method inherited from UserString.  This would lead to
    errors that would be very hard to track down.

    A faster and better solution is to rewrite your program using lists."""

    def __init__(self, string=""):
        self.data = string

    def __hash__(self):
        raise TypeError("unhashable type (it is mutable)")

    def __setitem__(self, index, sub):
        if index < 0:
            index += len(self.data)
        if index < 0 or index >= len(self.data):
            raise IndexError
        self.data = self.data[:index] + sub + self.data[index + 1 :]

    def __delitem__(self, index):
        if index < 0:
            index += len(self.data)
        if index < 0 or index >= len(self.data):
            raise IndexError
        self.data = self.data[:index] + self.data[index + 1 :]

    def __setslice__(self, start, end, sub):
        start = max(start, 0)
        end = max(end, 0)
        if isinstance(sub, UserString):
            self.data = self.data[:start] + sub.data + self.data[end:]
        elif isinstance(sub, bytes):
            self.data = self.data[:start] + sub + self.data[end:]
        else:
            self.data = self.data[:start] + str(sub).encode() + self.data[end:]

    def __delslice__(self, start, end):
        start = max(start, 0)
        end = max(end, 0)
        self.data = self.data[:start] + self.data[end:]

    def immutable(self):
        return UserString(self.data)

    def __iadd__(self, other):
        if isinstance(other, UserString):
            self.data += other.data
        elif isinstance(other, bytes):
            self.data += other
        else:
            self.data += str(other).encode()
        return self

    def __imul__(self, n):
        self.data *= n
        return self


class String(MutableString, ctypes.Union):

    _fields_ = [("raw", ctypes.POINTER(ctypes.c_char)), ("data", ctypes.c_char_p)]

    def __init__(self, obj=b""):
        if isinstance(obj, (bytes, UserString)):
            self.data = bytes(obj)
        else:
            self.raw = obj

    def __len__(self):
        return self.data and len(self.data) or 0

    def from_param(cls, obj):
        # Convert None or 0
        if obj is None or obj == 0:
            return cls(ctypes.POINTER(ctypes.c_char)())

        # Convert from String
        elif isinstance(obj, String):
            return obj

        # Convert from bytes
        elif isinstance(obj, bytes):
            return cls(obj)

        # Convert from str
        elif isinstance(obj, str):
            return cls(obj.encode())

        # Convert from c_char_p
        elif isinstance(obj, ctypes.c_char_p):
            return obj

        # Convert from POINTER(ctypes.c_char)
        elif isinstance(obj, ctypes.POINTER(ctypes.c_char)):
            return obj

        # Convert from raw pointer
        elif isinstance(obj, int):
            return cls(ctypes.cast(obj, ctypes.POINTER(ctypes.c_char)))

        # Convert from ctypes.c_char array
        elif isinstance(obj, ctypes.c_char * len(obj)):
            return obj

        # Convert from object
        else:
            return String.from_param(obj._as_parameter_)

    from_param = classmethod(from_param)


def ReturnString(obj, func=None, arguments=None):
    return String.from_param(obj)


# As of ctypes 1.0, ctypes does not support custom error-checking
# functions on callbacks, nor does it support custom datatypes on
# callbacks, so we must ensure that all callbacks return
# primitive datatypes.
#
# Non-primitive return values wrapped with UNCHECKED won't be
# typechecked, and will be converted to ctypes.c_void_p.
def UNCHECKED(type):
    if hasattr(type, "_type_") and isinstance(type._type_, str) and type._type_ != "P":
        return type
    else:
        return ctypes.c_void_p


# ctypes doesn't have direct support for variadic functions, so we have to write
# our own wrapper class
class _variadic_function(object):
    def __init__(self, func, restype, argtypes, errcheck):
        self.func = func
        self.func.restype = restype
        self.argtypes = argtypes
        if errcheck:
            self.func.errcheck = errcheck

    def _as_parameter_(self):
        # So we can pass this variadic function as a function pointer
        return self.func

    def __call__(self, *args):
        fixed_args = []
        i = 0
        for argtype in self.argtypes:
            # Typecheck what we can
            fixed_args.append(argtype.from_param(args[i]))
            i += 1
        return self.func(*fixed_args + list(args[i:]))


def ord_if_char(value):
    """
    Simple helper used for casts to simple builtin types:  if the argument is a
    string type, it will be converted to it's ordinal value.

    This function will raise an exception if the argument is string with more
    than one characters.
    """
    return ord(value) if (isinstance(value, bytes) or isinstance(value, str)) else value

# End preamble

_libs = {}
_libdirs = ['.']

# Begin loader

"""
Load libraries - appropriately for all our supported platforms
"""
# ----------------------------------------------------------------------------
# Copyright (c) 2008 David James
# Copyright (c) 2006-2008 Alex Holkner
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
#  * Neither the name of pyglet nor the names of its
#    contributors may be used to endorse or promote products
#    derived from this software without specific prior written
#    permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# ----------------------------------------------------------------------------

import ctypes
import ctypes.util
import glob
import os.path
import platform
import re
import sys


def _environ_path(name):
    """Split an environment variable into a path-like list elements"""
    if name in os.environ:
        return os.environ[name].split(":")
    return []


class LibraryLoader:
    """
    A base class For loading of libraries ;-)
    Subclasses load libraries for specific platforms.
    """

    # library names formatted specifically for platforms
    name_formats = ["%s"]

    class Lookup:
        """Looking up calling conventions for a platform"""

        mode = ctypes.DEFAULT_MODE

        def __init__(self, path):
            super(LibraryLoader.Lookup, self).__init__()
            self.access = dict(cdecl=ctypes.CDLL(path, self.mode))

        def get(self, name, calling_convention="cdecl"):
            """Return the given name according to the selected calling convention"""
            if calling_convention not in self.access:
                raise LookupError(
                    "Unknown calling convention '{}' for function '{}'".format(
                        calling_convention, name
                    )
                )
            return getattr(self.access[calling_convention], name)

        def has(self, name, calling_convention="cdecl"):
            """Return True if this given calling convention finds the given 'name'"""
            if calling_convention not in self.access:
                return False
            return hasattr(self.access[calling_convention], name)

        def __getattr__(self, name):
            return getattr(self.access["cdecl"], name)

    def __init__(self):
        self.other_dirs = []

    def __call__(self, libname):
        """Given the name of a library, load it."""
        paths = self.getpaths(libname)

        for path in paths:
            # noinspection PyBroadException
            try:
                return self.Lookup(path)
            except Exception:  # pylint: disable=broad-except
                pass

        raise ImportError("Could not load %s." % libname)

    def getpaths(self, libname):
        """Return a list of paths where the library might be found."""
        if os.path.isabs(libname):
            yield libname
        else:
            # search through a prioritized series of locations for the library

            # we first search any specific directories identified by user
            for dir_i in self.other_dirs:
                for fmt in self.name_formats:
                    # dir_i should be absolute already
                    yield os.path.join(dir_i, fmt % libname)

            # check if this code is even stored in a physical file
            try:
                this_file = __file__
            except NameError:
                this_file = None

            # then we search the directory where the generated python interface is stored
            if this_file is not None:
                for fmt in self.name_formats:
                    yield os.path.abspath(os.path.join(os.path.dirname(__file__), fmt % libname))

            # now, use the ctypes tools to try to find the library
            for fmt in self.name_formats:
                path = ctypes.util.find_library(fmt % libname)
                if path:
                    yield path

            # then we search all paths identified as platform-specific lib paths
            for path in self.getplatformpaths(libname):
                yield path

            # Finally, we'll try the users current working directory
            for fmt in self.name_formats:
                yield os.path.abspath(os.path.join(os.path.curdir, fmt % libname))

    def getplatformpaths(self, _libname):  # pylint: disable=no-self-use
        """Return all the library paths available in this platform"""
        return []


# Darwin (Mac OS X)


class DarwinLibraryLoader(LibraryLoader):
    """Library loader for MacOS"""

    name_formats = [
        "lib%s.dylib",
        "lib%s.so",
        "lib%s.bundle",
        "%s.dylib",
        "%s.so",
        "%s.bundle",
        "%s",
    ]

    class Lookup(LibraryLoader.Lookup):
        """
        Looking up library files for this platform (Darwin aka MacOS)
        """

        # Darwin requires dlopen to be called with mode RTLD_GLOBAL instead
        # of the default RTLD_LOCAL.  Without this, you end up with
        # libraries not being loadable, resulting in "Symbol not found"
        # errors
        mode = ctypes.RTLD_GLOBAL

    def getplatformpaths(self, libname):
        if os.path.pathsep in libname:
            names = [libname]
        else:
            names = [fmt % libname for fmt in self.name_formats]

        for directory in self.getdirs(libname):
            for name in names:
                yield os.path.join(directory, name)

    @staticmethod
    def getdirs(libname):
        """Implements the dylib search as specified in Apple documentation:

        http://developer.apple.com/documentation/DeveloperTools/Conceptual/
            DynamicLibraries/Articles/DynamicLibraryUsageGuidelines.html

        Before commencing the standard search, the method first checks
        the bundle's ``Frameworks`` directory if the application is running
        within a bundle (OS X .app).
        """

        dyld_fallback_library_path = _environ_path("DYLD_FALLBACK_LIBRARY_PATH")
        if not dyld_fallback_library_path:
            dyld_fallback_library_path = [
                os.path.expanduser("~/lib"),
                "/usr/local/lib",
                "/usr/lib",
            ]

        dirs = []

        if "/" in libname:
            dirs.extend(_environ_path("DYLD_LIBRARY_PATH"))
        else:
            dirs.extend(_environ_path("LD_LIBRARY_PATH"))
            dirs.extend(_environ_path("DYLD_LIBRARY_PATH"))
            dirs.extend(_environ_path("LD_RUN_PATH"))

        if hasattr(sys, "frozen") and getattr(sys, "frozen") == "macosx_app":
            dirs.append(os.path.join(os.environ["RESOURCEPATH"], "..", "Frameworks"))

        dirs.extend(dyld_fallback_library_path)

        return dirs


# Posix


class PosixLibraryLoader(LibraryLoader):
    """Library loader for POSIX-like systems (including Linux)"""

    _ld_so_cache = None

    _include = re.compile(r"^\s*include\s+(?P<pattern>.*)")

    name_formats = ["lib%s.so", "%s.so", "%s"]

    class _Directories(dict):
        """Deal with directories"""

        def __init__(self):
            dict.__init__(self)
            self.order = 0

        def add(self, directory):
            """Add a directory to our current set of directories"""
            if len(directory) > 1:
                directory = directory.rstrip(os.path.sep)
            # only adds and updates order if exists and not already in set
            if not os.path.exists(directory):
                return
            order = self.setdefault(directory, self.order)
            if order == self.order:
                self.order += 1

        def extend(self, directories):
            """Add a list of directories to our set"""
            for a_dir in directories:
                self.add(a_dir)

        def ordered(self):
            """Sort the list of directories"""
            return (i[0] for i in sorted(self.items(), key=lambda d: d[1]))

    def _get_ld_so_conf_dirs(self, conf, dirs):
        """
        Recursive function to help parse all ld.so.conf files, including proper
        handling of the `include` directive.
        """

        try:
            with open(conf) as fileobj:
                for dirname in fileobj:
                    dirname = dirname.strip()
                    if not dirname:
                        continue

                    match = self._include.match(dirname)
                    if not match:
                        dirs.add(dirname)
                    else:
                        for dir2 in glob.glob(match.group("pattern")):
                            self._get_ld_so_conf_dirs(dir2, dirs)
        except IOError:
            pass

    def _create_ld_so_cache(self):
        # Recreate search path followed by ld.so.  This is going to be
        # slow to build, and incorrect (ld.so uses ld.so.cache, which may
        # not be up-to-date).  Used only as fallback for distros without
        # /sbin/ldconfig.
        #
        # We assume the DT_RPATH and DT_RUNPATH binary sections are omitted.

        directories = self._Directories()
        for name in (
            "LD_LIBRARY_PATH",
            "SHLIB_PATH",  # HP-UX
            "LIBPATH",  # OS/2, AIX
            "LIBRARY_PATH",  # BE/OS
        ):
            if name in os.environ:
                directories.extend(os.environ[name].split(os.pathsep))

        self._get_ld_so_conf_dirs("/etc/ld.so.conf", directories)

        bitage = platform.architecture()[0]

        unix_lib_dirs_list = []
        if bitage.startswith("64"):
            # prefer 64 bit if that is our arch
            unix_lib_dirs_list += ["/lib64", "/usr/lib64"]

        # must include standard libs, since those paths are also used by 64 bit
        # installs
        unix_lib_dirs_list += ["/lib", "/usr/lib"]
        if sys.platform.startswith("linux"):
            # Try and support multiarch work in Ubuntu
            # https://wiki.ubuntu.com/MultiarchSpec
            if bitage.startswith("32"):
                # Assume Intel/AMD x86 compat
                unix_lib_dirs_list += ["/lib/i386-linux-gnu", "/usr/lib/i386-linux-gnu"]
            elif bitage.startswith("64"):
                # Assume Intel/AMD x86 compatible
                unix_lib_dirs_list += [
                    "/lib/x86_64-linux-gnu",
                    "/usr/lib/x86_64-linux-gnu",
                ]
            else:
                # guess...
                unix_lib_dirs_list += glob.glob("/lib/*linux-gnu")
        directories.extend(unix_lib_dirs_list)

        cache = {}
        lib_re = re.compile(r"lib(.*)\.s[ol]")
        # ext_re = re.compile(r"\.s[ol]$")
        for our_dir in directories.ordered():
            try:
                for path in glob.glob("%s/*.s[ol]*" % our_dir):
                    file = os.path.basename(path)

                    # Index by filename
                    cache_i = cache.setdefault(file, set())
                    cache_i.add(path)

                    # Index by library name
                    match = lib_re.match(file)
                    if match:
                        library = match.group(1)
                        cache_i = cache.setdefault(library, set())
                        cache_i.add(path)
            except OSError:
                pass

        self._ld_so_cache = cache

    def getplatformpaths(self, libname):
        if self._ld_so_cache is None:
            self._create_ld_so_cache()

        result = self._ld_so_cache.get(libname, set())
        for i in result:
            # we iterate through all found paths for library, since we may have
            # actually found multiple architectures or other library types that
            # may not load
            yield i


# Windows


class WindowsLibraryLoader(LibraryLoader):
    """Library loader for Microsoft Windows"""

    name_formats = ["%s.dll", "lib%s.dll", "%slib.dll", "%s"]

    class Lookup(LibraryLoader.Lookup):
        """Lookup class for Windows libraries..."""

        def __init__(self, path):
            super(WindowsLibraryLoader.Lookup, self).__init__(path)
            self.access["stdcall"] = ctypes.windll.LoadLibrary(path)


# Platform switching

# If your value of sys.platform does not appear in this dict, please contact
# the Ctypesgen maintainers.

loaderclass = {
    "darwin": DarwinLibraryLoader,
    "cygwin": WindowsLibraryLoader,
    "win32": WindowsLibraryLoader,
    "msys": WindowsLibraryLoader,
}

load_library = loaderclass.get(sys.platform, PosixLibraryLoader)()


def add_library_search_dirs(other_dirs):
    """
    Add libraries to search paths.
    If library paths are relative, convert them to absolute with respect to this
    file's directory
    """
    for path in other_dirs:
        if not os.path.isabs(path):
            path = os.path.abspath(path)
        load_library.other_dirs.append(path)


del loaderclass

# End loader

add_library_search_dirs(['.'])

# Begin libraries
_libs["pdfium"] = load_library("pdfium")

# 1 libraries
# End libraries

# No modules

enum_anon_2 = c_int# build_tar/include/fpdfview.h: 51

FPDF_TEXTRENDERMODE_UNKNOWN = (-1)# build_tar/include/fpdfview.h: 51

FPDF_TEXTRENDERMODE_FILL = 0# build_tar/include/fpdfview.h: 51

FPDF_TEXTRENDERMODE_STROKE = 1# build_tar/include/fpdfview.h: 51

FPDF_TEXTRENDERMODE_FILL_STROKE = 2# build_tar/include/fpdfview.h: 51

FPDF_TEXTRENDERMODE_INVISIBLE = 3# build_tar/include/fpdfview.h: 51

FPDF_TEXTRENDERMODE_FILL_CLIP = 4# build_tar/include/fpdfview.h: 51

FPDF_TEXTRENDERMODE_STROKE_CLIP = 5# build_tar/include/fpdfview.h: 51

FPDF_TEXTRENDERMODE_FILL_STROKE_CLIP = 6# build_tar/include/fpdfview.h: 51

FPDF_TEXTRENDERMODE_CLIP = 7# build_tar/include/fpdfview.h: 51

FPDF_TEXTRENDERMODE_LAST = FPDF_TEXTRENDERMODE_CLIP# build_tar/include/fpdfview.h: 51

FPDF_TEXT_RENDERMODE = enum_anon_2# build_tar/include/fpdfview.h: 51

# build_tar/include/fpdfview.h: 54
class struct_fpdf_action_t__(Structure):
    pass

FPDF_ACTION = POINTER(struct_fpdf_action_t__)# build_tar/include/fpdfview.h: 54

# build_tar/include/fpdfview.h: 55
class struct_fpdf_annotation_t__(Structure):
    pass

FPDF_ANNOTATION = POINTER(struct_fpdf_annotation_t__)# build_tar/include/fpdfview.h: 55

# build_tar/include/fpdfview.h: 56
class struct_fpdf_attachment_t__(Structure):
    pass

FPDF_ATTACHMENT = POINTER(struct_fpdf_attachment_t__)# build_tar/include/fpdfview.h: 56

# build_tar/include/fpdfview.h: 57
class struct_fpdf_avail_t__(Structure):
    pass

FPDF_AVAIL = POINTER(struct_fpdf_avail_t__)# build_tar/include/fpdfview.h: 57

# build_tar/include/fpdfview.h: 58
class struct_fpdf_bitmap_t__(Structure):
    pass

FPDF_BITMAP = POINTER(struct_fpdf_bitmap_t__)# build_tar/include/fpdfview.h: 58

# build_tar/include/fpdfview.h: 59
class struct_fpdf_bookmark_t__(Structure):
    pass

FPDF_BOOKMARK = POINTER(struct_fpdf_bookmark_t__)# build_tar/include/fpdfview.h: 59

# build_tar/include/fpdfview.h: 60
class struct_fpdf_clippath_t__(Structure):
    pass

FPDF_CLIPPATH = POINTER(struct_fpdf_clippath_t__)# build_tar/include/fpdfview.h: 60

# build_tar/include/fpdfview.h: 61
class struct_fpdf_dest_t__(Structure):
    pass

FPDF_DEST = POINTER(struct_fpdf_dest_t__)# build_tar/include/fpdfview.h: 61

# build_tar/include/fpdfview.h: 62
class struct_fpdf_document_t__(Structure):
    pass

FPDF_DOCUMENT = POINTER(struct_fpdf_document_t__)# build_tar/include/fpdfview.h: 62

# build_tar/include/fpdfview.h: 63
class struct_fpdf_font_t__(Structure):
    pass

FPDF_FONT = POINTER(struct_fpdf_font_t__)# build_tar/include/fpdfview.h: 63

# build_tar/include/fpdfview.h: 64
class struct_fpdf_form_handle_t__(Structure):
    pass

FPDF_FORMHANDLE = POINTER(struct_fpdf_form_handle_t__)# build_tar/include/fpdfview.h: 64

# build_tar/include/fpdfview.h: 65
class struct_fpdf_glyphpath_t__(Structure):
    pass

FPDF_GLYPHPATH = POINTER(struct_fpdf_glyphpath_t__)# build_tar/include/fpdfview.h: 65

# build_tar/include/fpdfview.h: 66
class struct_fpdf_javascript_action_t(Structure):
    pass

FPDF_JAVASCRIPT_ACTION = POINTER(struct_fpdf_javascript_action_t)# build_tar/include/fpdfview.h: 66

# build_tar/include/fpdfview.h: 67
class struct_fpdf_link_t__(Structure):
    pass

FPDF_LINK = POINTER(struct_fpdf_link_t__)# build_tar/include/fpdfview.h: 67

# build_tar/include/fpdfview.h: 68
class struct_fpdf_page_t__(Structure):
    pass

FPDF_PAGE = POINTER(struct_fpdf_page_t__)# build_tar/include/fpdfview.h: 68

# build_tar/include/fpdfview.h: 69
class struct_fpdf_pagelink_t__(Structure):
    pass

FPDF_PAGELINK = POINTER(struct_fpdf_pagelink_t__)# build_tar/include/fpdfview.h: 69

# build_tar/include/fpdfview.h: 70
class struct_fpdf_pageobject_t__(Structure):
    pass

FPDF_PAGEOBJECT = POINTER(struct_fpdf_pageobject_t__)# build_tar/include/fpdfview.h: 70

# build_tar/include/fpdfview.h: 71
class struct_fpdf_pageobjectmark_t__(Structure):
    pass

FPDF_PAGEOBJECTMARK = POINTER(struct_fpdf_pageobjectmark_t__)# build_tar/include/fpdfview.h: 71

# build_tar/include/fpdfview.h: 72
class struct_fpdf_pagerange_t__(Structure):
    pass

FPDF_PAGERANGE = POINTER(struct_fpdf_pagerange_t__)# build_tar/include/fpdfview.h: 72

# build_tar/include/fpdfview.h: 73
class struct_fpdf_pathsegment_t(Structure):
    pass

FPDF_PATHSEGMENT = POINTER(struct_fpdf_pathsegment_t)# build_tar/include/fpdfview.h: 73

FPDF_RECORDER = POINTER(None)# build_tar/include/fpdfview.h: 74

# build_tar/include/fpdfview.h: 75
class struct_fpdf_schhandle_t__(Structure):
    pass

FPDF_SCHHANDLE = POINTER(struct_fpdf_schhandle_t__)# build_tar/include/fpdfview.h: 75

# build_tar/include/fpdfview.h: 76
class struct_fpdf_signature_t__(Structure):
    pass

FPDF_SIGNATURE = POINTER(struct_fpdf_signature_t__)# build_tar/include/fpdfview.h: 76

# build_tar/include/fpdfview.h: 77
class struct_fpdf_structelement_t__(Structure):
    pass

FPDF_STRUCTELEMENT = POINTER(struct_fpdf_structelement_t__)# build_tar/include/fpdfview.h: 77

# build_tar/include/fpdfview.h: 78
class struct_fpdf_structtree_t__(Structure):
    pass

FPDF_STRUCTTREE = POINTER(struct_fpdf_structtree_t__)# build_tar/include/fpdfview.h: 78

# build_tar/include/fpdfview.h: 79
class struct_fpdf_textpage_t__(Structure):
    pass

FPDF_TEXTPAGE = POINTER(struct_fpdf_textpage_t__)# build_tar/include/fpdfview.h: 79

# build_tar/include/fpdfview.h: 80
class struct_fpdf_widget_t__(Structure):
    pass

FPDF_WIDGET = POINTER(struct_fpdf_widget_t__)# build_tar/include/fpdfview.h: 80

# build_tar/include/fpdfview.h: 81
class struct_fpdf_xobject_t__(Structure):
    pass

FPDF_XOBJECT = POINTER(struct_fpdf_xobject_t__)# build_tar/include/fpdfview.h: 81

FPDF_BOOL = c_int# build_tar/include/fpdfview.h: 84

FPDF_RESULT = c_int# build_tar/include/fpdfview.h: 85

FPDF_DWORD = c_ulong# build_tar/include/fpdfview.h: 86

FS_FLOAT = c_float# build_tar/include/fpdfview.h: 87

enum__FPDF_DUPLEXTYPE_ = c_int# build_tar/include/fpdfview.h: 95

DuplexUndefined = 0# build_tar/include/fpdfview.h: 95

Simplex = (DuplexUndefined + 1)# build_tar/include/fpdfview.h: 95

DuplexFlipShortEdge = (Simplex + 1)# build_tar/include/fpdfview.h: 95

DuplexFlipLongEdge = (DuplexFlipShortEdge + 1)# build_tar/include/fpdfview.h: 95

FPDF_DUPLEXTYPE = enum__FPDF_DUPLEXTYPE_# build_tar/include/fpdfview.h: 95

FPDF_WCHAR = c_ushort# build_tar/include/fpdfview.h: 98

FPDF_BYTESTRING = String# build_tar/include/fpdfview.h: 102

FPDF_WIDESTRING = POINTER(c_ushort)# build_tar/include/fpdfview.h: 106

# build_tar/include/fpdfview.h: 114
class struct_FPDF_BSTR_(Structure):
    pass

struct_FPDF_BSTR_.__slots__ = [
    'str',
    'len',
]
struct_FPDF_BSTR_._fields_ = [
    ('str', String),
    ('len', c_int),
]

FPDF_BSTR = struct_FPDF_BSTR_# build_tar/include/fpdfview.h: 114

FPDF_STRING = String# build_tar/include/fpdfview.h: 123

# build_tar/include/fpdfview.h: 140
class struct__FS_MATRIX_(Structure):
    pass

struct__FS_MATRIX_.__slots__ = [
    'a',
    'b',
    'c',
    'd',
    'e',
    'f',
]
struct__FS_MATRIX_._fields_ = [
    ('a', c_float),
    ('b', c_float),
    ('c', c_float),
    ('d', c_float),
    ('e', c_float),
    ('f', c_float),
]

FS_MATRIX = struct__FS_MATRIX_# build_tar/include/fpdfview.h: 140

# build_tar/include/fpdfview.h: 143
class struct__FS_RECTF_(Structure):
    pass

struct__FS_RECTF_.__slots__ = [
    'left',
    'top',
    'right',
    'bottom',
]
struct__FS_RECTF_._fields_ = [
    ('left', c_float),
    ('top', c_float),
    ('right', c_float),
    ('bottom', c_float),
]

FS_LPRECTF = POINTER(struct__FS_RECTF_)# build_tar/include/fpdfview.h: 152

FS_RECTF = struct__FS_RECTF_# build_tar/include/fpdfview.h: 152

FS_LPCRECTF = POINTER(FS_RECTF)# build_tar/include/fpdfview.h: 155

# build_tar/include/fpdfview.h: 158
class struct_FS_SIZEF_(Structure):
    pass

struct_FS_SIZEF_.__slots__ = [
    'width',
    'height',
]
struct_FS_SIZEF_._fields_ = [
    ('width', c_float),
    ('height', c_float),
]

FS_LPSIZEF = POINTER(struct_FS_SIZEF_)# build_tar/include/fpdfview.h: 161

FS_SIZEF = struct_FS_SIZEF_# build_tar/include/fpdfview.h: 161

FS_LPCSIZEF = POINTER(FS_SIZEF)# build_tar/include/fpdfview.h: 164

# build_tar/include/fpdfview.h: 167
class struct_FS_POINTF_(Structure):
    pass

struct_FS_POINTF_.__slots__ = [
    'x',
    'y',
]
struct_FS_POINTF_._fields_ = [
    ('x', c_float),
    ('y', c_float),
]

FS_LPPOINTF = POINTER(struct_FS_POINTF_)# build_tar/include/fpdfview.h: 170

FS_POINTF = struct_FS_POINTF_# build_tar/include/fpdfview.h: 170

FS_LPCPOINTF = POINTER(FS_POINTF)# build_tar/include/fpdfview.h: 173

FPDF_ANNOTATION_SUBTYPE = c_int# build_tar/include/fpdfview.h: 176

FPDF_ANNOT_APPEARANCEMODE = c_int# build_tar/include/fpdfview.h: 177

FPDF_OBJECT_TYPE = c_int# build_tar/include/fpdfview.h: 180

# build_tar/include/fpdfview.h: 217
if _libs["pdfium"].has("FPDF_InitLibrary", "cdecl"):
    FPDF_InitLibrary = _libs["pdfium"].get("FPDF_InitLibrary", "cdecl")
    FPDF_InitLibrary.argtypes = []
    FPDF_InitLibrary.restype = None

# build_tar/include/fpdfview.h: 247
class struct_FPDF_LIBRARY_CONFIG_(Structure):
    pass

struct_FPDF_LIBRARY_CONFIG_.__slots__ = [
    'version',
    'm_pUserFontPaths',
    'm_pIsolate',
    'm_v8EmbedderSlot',
    'm_pPlatform',
]
struct_FPDF_LIBRARY_CONFIG_._fields_ = [
    ('version', c_int),
    ('m_pUserFontPaths', POINTER(POINTER(c_char))),
    ('m_pIsolate', POINTER(None)),
    ('m_v8EmbedderSlot', c_uint),
    ('m_pPlatform', POINTER(None)),
]

FPDF_LIBRARY_CONFIG = struct_FPDF_LIBRARY_CONFIG_# build_tar/include/fpdfview.h: 247

# build_tar/include/fpdfview.h: 259
if _libs["pdfium"].has("FPDF_InitLibraryWithConfig", "cdecl"):
    FPDF_InitLibraryWithConfig = _libs["pdfium"].get("FPDF_InitLibraryWithConfig", "cdecl")
    FPDF_InitLibraryWithConfig.argtypes = [POINTER(FPDF_LIBRARY_CONFIG)]
    FPDF_InitLibraryWithConfig.restype = None

# build_tar/include/fpdfview.h: 272
if _libs["pdfium"].has("FPDF_DestroyLibrary", "cdecl"):
    FPDF_DestroyLibrary = _libs["pdfium"].get("FPDF_DestroyLibrary", "cdecl")
    FPDF_DestroyLibrary.argtypes = []
    FPDF_DestroyLibrary.restype = None

# build_tar/include/fpdfview.h: 285
if _libs["pdfium"].has("FPDF_SetSandBoxPolicy", "cdecl"):
    FPDF_SetSandBoxPolicy = _libs["pdfium"].get("FPDF_SetSandBoxPolicy", "cdecl")
    FPDF_SetSandBoxPolicy.argtypes = [FPDF_DWORD, FPDF_BOOL]
    FPDF_SetSandBoxPolicy.restype = None

# build_tar/include/fpdfview.h: 366
if _libs["pdfium"].has("FPDF_LoadDocument", "cdecl"):
    FPDF_LoadDocument = _libs["pdfium"].get("FPDF_LoadDocument", "cdecl")
    FPDF_LoadDocument.argtypes = [FPDF_STRING, FPDF_BYTESTRING]
    FPDF_LoadDocument.restype = FPDF_DOCUMENT

# build_tar/include/fpdfview.h: 390
if _libs["pdfium"].has("FPDF_LoadMemDocument", "cdecl"):
    FPDF_LoadMemDocument = _libs["pdfium"].get("FPDF_LoadMemDocument", "cdecl")
    FPDF_LoadMemDocument.argtypes = [POINTER(None), c_int, FPDF_BYTESTRING]
    FPDF_LoadMemDocument.restype = FPDF_DOCUMENT

# build_tar/include/fpdfview.h: 415
if _libs["pdfium"].has("FPDF_LoadMemDocument64", "cdecl"):
    FPDF_LoadMemDocument64 = _libs["pdfium"].get("FPDF_LoadMemDocument64", "cdecl")
    FPDF_LoadMemDocument64.argtypes = [POINTER(None), c_size_t, FPDF_BYTESTRING]
    FPDF_LoadMemDocument64.restype = FPDF_DOCUMENT

# build_tar/include/fpdfview.h: 439
class struct_anon_3(Structure):
    pass

struct_anon_3.__slots__ = [
    'm_FileLen',
    'm_GetBlock',
    'm_Param',
]
struct_anon_3._fields_ = [
    ('m_FileLen', c_ulong),
    ('m_GetBlock', CFUNCTYPE(UNCHECKED(c_int), POINTER(None), c_ulong, POINTER(c_ubyte), c_ulong)),
    ('m_Param', POINTER(None)),
]

FPDF_FILEACCESS = struct_anon_3# build_tar/include/fpdfview.h: 439

# build_tar/include/fpdfview.h: 535
class struct_FPDF_FILEHANDLER_(Structure):
    pass

struct_FPDF_FILEHANDLER_.__slots__ = [
    'clientData',
    'Release',
    'GetSize',
    'ReadBlock',
    'WriteBlock',
    'Flush',
    'Truncate',
]
struct_FPDF_FILEHANDLER_._fields_ = [
    ('clientData', POINTER(None)),
    ('Release', CFUNCTYPE(UNCHECKED(None), POINTER(None))),
    ('GetSize', CFUNCTYPE(UNCHECKED(FPDF_DWORD), POINTER(None))),
    ('ReadBlock', CFUNCTYPE(UNCHECKED(FPDF_RESULT), POINTER(None), FPDF_DWORD, POINTER(None), FPDF_DWORD)),
    ('WriteBlock', CFUNCTYPE(UNCHECKED(FPDF_RESULT), POINTER(None), FPDF_DWORD, POINTER(None), FPDF_DWORD)),
    ('Flush', CFUNCTYPE(UNCHECKED(FPDF_RESULT), POINTER(None))),
    ('Truncate', CFUNCTYPE(UNCHECKED(FPDF_RESULT), POINTER(None), FPDF_DWORD)),
]

FPDF_FILEHANDLER = struct_FPDF_FILEHANDLER_# build_tar/include/fpdfview.h: 535

# build_tar/include/fpdfview.h: 558
if _libs["pdfium"].has("FPDF_LoadCustomDocument", "cdecl"):
    FPDF_LoadCustomDocument = _libs["pdfium"].get("FPDF_LoadCustomDocument", "cdecl")
    FPDF_LoadCustomDocument.argtypes = [POINTER(FPDF_FILEACCESS), FPDF_BYTESTRING]
    FPDF_LoadCustomDocument.restype = FPDF_DOCUMENT

# build_tar/include/fpdfview.h: 571
if _libs["pdfium"].has("FPDF_GetFileVersion", "cdecl"):
    FPDF_GetFileVersion = _libs["pdfium"].get("FPDF_GetFileVersion", "cdecl")
    FPDF_GetFileVersion.argtypes = [FPDF_DOCUMENT, POINTER(c_int)]
    FPDF_GetFileVersion.restype = FPDF_BOOL

# build_tar/include/fpdfview.h: 595
if _libs["pdfium"].has("FPDF_GetLastError", "cdecl"):
    FPDF_GetLastError = _libs["pdfium"].get("FPDF_GetLastError", "cdecl")
    FPDF_GetLastError.argtypes = []
    FPDF_GetLastError.restype = c_ulong

# build_tar/include/fpdfview.h: 610
if _libs["pdfium"].has("FPDF_DocumentHasValidCrossReferenceTable", "cdecl"):
    FPDF_DocumentHasValidCrossReferenceTable = _libs["pdfium"].get("FPDF_DocumentHasValidCrossReferenceTable", "cdecl")
    FPDF_DocumentHasValidCrossReferenceTable.argtypes = [FPDF_DOCUMENT]
    FPDF_DocumentHasValidCrossReferenceTable.restype = FPDF_BOOL

# build_tar/include/fpdfview.h: 627
if _libs["pdfium"].has("FPDF_GetTrailerEnds", "cdecl"):
    FPDF_GetTrailerEnds = _libs["pdfium"].get("FPDF_GetTrailerEnds", "cdecl")
    FPDF_GetTrailerEnds.argtypes = [FPDF_DOCUMENT, POINTER(c_uint), c_ulong]
    FPDF_GetTrailerEnds.restype = c_ulong

# build_tar/include/fpdfview.h: 640
if _libs["pdfium"].has("FPDF_GetDocPermissions", "cdecl"):
    FPDF_GetDocPermissions = _libs["pdfium"].get("FPDF_GetDocPermissions", "cdecl")
    FPDF_GetDocPermissions.argtypes = [FPDF_DOCUMENT]
    FPDF_GetDocPermissions.restype = c_ulong

# build_tar/include/fpdfview.h: 651
if _libs["pdfium"].has("FPDF_GetSecurityHandlerRevision", "cdecl"):
    FPDF_GetSecurityHandlerRevision = _libs["pdfium"].get("FPDF_GetSecurityHandlerRevision", "cdecl")
    FPDF_GetSecurityHandlerRevision.argtypes = [FPDF_DOCUMENT]
    FPDF_GetSecurityHandlerRevision.restype = c_int

# build_tar/include/fpdfview.h: 659
if _libs["pdfium"].has("FPDF_GetPageCount", "cdecl"):
    FPDF_GetPageCount = _libs["pdfium"].get("FPDF_GetPageCount", "cdecl")
    FPDF_GetPageCount.argtypes = [FPDF_DOCUMENT]
    FPDF_GetPageCount.restype = c_int

# build_tar/include/fpdfview.h: 671
if _libs["pdfium"].has("FPDF_LoadPage", "cdecl"):
    FPDF_LoadPage = _libs["pdfium"].get("FPDF_LoadPage", "cdecl")
    FPDF_LoadPage.argtypes = [FPDF_DOCUMENT, c_int]
    FPDF_LoadPage.restype = FPDF_PAGE

# build_tar/include/fpdfview.h: 682
if _libs["pdfium"].has("FPDF_GetPageWidthF", "cdecl"):
    FPDF_GetPageWidthF = _libs["pdfium"].get("FPDF_GetPageWidthF", "cdecl")
    FPDF_GetPageWidthF.argtypes = [FPDF_PAGE]
    FPDF_GetPageWidthF.restype = c_float

# build_tar/include/fpdfview.h: 694
if _libs["pdfium"].has("FPDF_GetPageWidth", "cdecl"):
    FPDF_GetPageWidth = _libs["pdfium"].get("FPDF_GetPageWidth", "cdecl")
    FPDF_GetPageWidth.argtypes = [FPDF_PAGE]
    FPDF_GetPageWidth.restype = c_double

# build_tar/include/fpdfview.h: 704
if _libs["pdfium"].has("FPDF_GetPageHeightF", "cdecl"):
    FPDF_GetPageHeightF = _libs["pdfium"].get("FPDF_GetPageHeightF", "cdecl")
    FPDF_GetPageHeightF.argtypes = [FPDF_PAGE]
    FPDF_GetPageHeightF.restype = c_float

# build_tar/include/fpdfview.h: 716
if _libs["pdfium"].has("FPDF_GetPageHeight", "cdecl"):
    FPDF_GetPageHeight = _libs["pdfium"].get("FPDF_GetPageHeight", "cdecl")
    FPDF_GetPageHeight.argtypes = [FPDF_PAGE]
    FPDF_GetPageHeight.restype = c_double

# build_tar/include/fpdfview.h: 728
if _libs["pdfium"].has("FPDF_GetPageBoundingBox", "cdecl"):
    FPDF_GetPageBoundingBox = _libs["pdfium"].get("FPDF_GetPageBoundingBox", "cdecl")
    FPDF_GetPageBoundingBox.argtypes = [FPDF_PAGE, POINTER(FS_RECTF)]
    FPDF_GetPageBoundingBox.restype = FPDF_BOOL

# build_tar/include/fpdfview.h: 742
if _libs["pdfium"].has("FPDF_GetPageSizeByIndexF", "cdecl"):
    FPDF_GetPageSizeByIndexF = _libs["pdfium"].get("FPDF_GetPageSizeByIndexF", "cdecl")
    FPDF_GetPageSizeByIndexF.argtypes = [FPDF_DOCUMENT, c_int, POINTER(FS_SIZEF)]
    FPDF_GetPageSizeByIndexF.restype = FPDF_BOOL

# build_tar/include/fpdfview.h: 760
if _libs["pdfium"].has("FPDF_GetPageSizeByIndex", "cdecl"):
    FPDF_GetPageSizeByIndex = _libs["pdfium"].get("FPDF_GetPageSizeByIndex", "cdecl")
    FPDF_GetPageSizeByIndex.argtypes = [FPDF_DOCUMENT, c_int, POINTER(c_double), POINTER(c_double)]
    FPDF_GetPageSizeByIndex.restype = c_int

# build_tar/include/fpdfview.h: 808
class struct_FPDF_COLORSCHEME_(Structure):
    pass

struct_FPDF_COLORSCHEME_.__slots__ = [
    'path_fill_color',
    'path_stroke_color',
    'text_fill_color',
    'text_stroke_color',
]
struct_FPDF_COLORSCHEME_._fields_ = [
    ('path_fill_color', FPDF_DWORD),
    ('path_stroke_color', FPDF_DWORD),
    ('text_fill_color', FPDF_DWORD),
    ('text_stroke_color', FPDF_DWORD),
]

FPDF_COLORSCHEME = struct_FPDF_COLORSCHEME_# build_tar/include/fpdfview.h: 808

# build_tar/include/fpdfview.h: 868
if _libs["pdfium"].has("FPDF_RenderPageBitmap", "cdecl"):
    FPDF_RenderPageBitmap = _libs["pdfium"].get("FPDF_RenderPageBitmap", "cdecl")
    FPDF_RenderPageBitmap.argtypes = [FPDF_BITMAP, FPDF_PAGE, c_int, c_int, c_int, c_int, c_int, c_int]
    FPDF_RenderPageBitmap.restype = None

# build_tar/include/fpdfview.h: 896
if _libs["pdfium"].has("FPDF_RenderPageBitmapWithMatrix", "cdecl"):
    FPDF_RenderPageBitmapWithMatrix = _libs["pdfium"].get("FPDF_RenderPageBitmapWithMatrix", "cdecl")
    FPDF_RenderPageBitmapWithMatrix.argtypes = [FPDF_BITMAP, FPDF_PAGE, POINTER(FS_MATRIX), POINTER(FS_RECTF), c_int]
    FPDF_RenderPageBitmapWithMatrix.restype = None

# build_tar/include/fpdfview.h: 914
if _libs["pdfium"].has("FPDF_ClosePage", "cdecl"):
    FPDF_ClosePage = _libs["pdfium"].get("FPDF_ClosePage", "cdecl")
    FPDF_ClosePage.argtypes = [FPDF_PAGE]
    FPDF_ClosePage.restype = None

# build_tar/include/fpdfview.h: 922
if _libs["pdfium"].has("FPDF_CloseDocument", "cdecl"):
    FPDF_CloseDocument = _libs["pdfium"].get("FPDF_CloseDocument", "cdecl")
    FPDF_CloseDocument.argtypes = [FPDF_DOCUMENT]
    FPDF_CloseDocument.restype = None

# build_tar/include/fpdfview.h: 965
if _libs["pdfium"].has("FPDF_DeviceToPage", "cdecl"):
    FPDF_DeviceToPage = _libs["pdfium"].get("FPDF_DeviceToPage", "cdecl")
    FPDF_DeviceToPage.argtypes = [FPDF_PAGE, c_int, c_int, c_int, c_int, c_int, c_int, c_int, POINTER(c_double), POINTER(c_double)]
    FPDF_DeviceToPage.restype = FPDF_BOOL

# build_tar/include/fpdfview.h: 1002
if _libs["pdfium"].has("FPDF_PageToDevice", "cdecl"):
    FPDF_PageToDevice = _libs["pdfium"].get("FPDF_PageToDevice", "cdecl")
    FPDF_PageToDevice.argtypes = [FPDF_PAGE, c_int, c_int, c_int, c_int, c_int, c_double, c_double, POINTER(c_int), POINTER(c_int)]
    FPDF_PageToDevice.restype = FPDF_BOOL

# build_tar/include/fpdfview.h: 1043
if _libs["pdfium"].has("FPDFBitmap_Create", "cdecl"):
    FPDFBitmap_Create = _libs["pdfium"].get("FPDFBitmap_Create", "cdecl")
    FPDFBitmap_Create.argtypes = [c_int, c_int, c_int]
    FPDFBitmap_Create.restype = FPDF_BITMAP

# build_tar/include/fpdfview.h: 1084
if _libs["pdfium"].has("FPDFBitmap_CreateEx", "cdecl"):
    FPDFBitmap_CreateEx = _libs["pdfium"].get("FPDFBitmap_CreateEx", "cdecl")
    FPDFBitmap_CreateEx.argtypes = [c_int, c_int, c_int, POINTER(None), c_int]
    FPDFBitmap_CreateEx.restype = FPDF_BITMAP

# build_tar/include/fpdfview.h: 1100
if _libs["pdfium"].has("FPDFBitmap_GetFormat", "cdecl"):
    FPDFBitmap_GetFormat = _libs["pdfium"].get("FPDFBitmap_GetFormat", "cdecl")
    FPDFBitmap_GetFormat.argtypes = [FPDF_BITMAP]
    FPDFBitmap_GetFormat.restype = c_int

# build_tar/include/fpdfview.h: 1126
if _libs["pdfium"].has("FPDFBitmap_FillRect", "cdecl"):
    FPDFBitmap_FillRect = _libs["pdfium"].get("FPDFBitmap_FillRect", "cdecl")
    FPDFBitmap_FillRect.argtypes = [FPDF_BITMAP, c_int, c_int, c_int, c_int, FPDF_DWORD]
    FPDFBitmap_FillRect.restype = None

# build_tar/include/fpdfview.h: 1149
if _libs["pdfium"].has("FPDFBitmap_GetBuffer", "cdecl"):
    FPDFBitmap_GetBuffer = _libs["pdfium"].get("FPDFBitmap_GetBuffer", "cdecl")
    FPDFBitmap_GetBuffer.argtypes = [FPDF_BITMAP]
    FPDFBitmap_GetBuffer.restype = POINTER(c_ubyte)
    FPDFBitmap_GetBuffer.errcheck = lambda v,*a : cast(v, c_void_p)

# build_tar/include/fpdfview.h: 1158
if _libs["pdfium"].has("FPDFBitmap_GetWidth", "cdecl"):
    FPDFBitmap_GetWidth = _libs["pdfium"].get("FPDFBitmap_GetWidth", "cdecl")
    FPDFBitmap_GetWidth.argtypes = [FPDF_BITMAP]
    FPDFBitmap_GetWidth.restype = c_int

# build_tar/include/fpdfview.h: 1167
if _libs["pdfium"].has("FPDFBitmap_GetHeight", "cdecl"):
    FPDFBitmap_GetHeight = _libs["pdfium"].get("FPDFBitmap_GetHeight", "cdecl")
    FPDFBitmap_GetHeight.argtypes = [FPDF_BITMAP]
    FPDFBitmap_GetHeight.restype = c_int

# build_tar/include/fpdfview.h: 1178
if _libs["pdfium"].has("FPDFBitmap_GetStride", "cdecl"):
    FPDFBitmap_GetStride = _libs["pdfium"].get("FPDFBitmap_GetStride", "cdecl")
    FPDFBitmap_GetStride.argtypes = [FPDF_BITMAP]
    FPDFBitmap_GetStride.restype = c_int

# build_tar/include/fpdfview.h: 1190
if _libs["pdfium"].has("FPDFBitmap_Destroy", "cdecl"):
    FPDFBitmap_Destroy = _libs["pdfium"].get("FPDFBitmap_Destroy", "cdecl")
    FPDFBitmap_Destroy.argtypes = [FPDF_BITMAP]
    FPDFBitmap_Destroy.restype = None

# build_tar/include/fpdfview.h: 1199
if _libs["pdfium"].has("FPDF_VIEWERREF_GetPrintScaling", "cdecl"):
    FPDF_VIEWERREF_GetPrintScaling = _libs["pdfium"].get("FPDF_VIEWERREF_GetPrintScaling", "cdecl")
    FPDF_VIEWERREF_GetPrintScaling.argtypes = [FPDF_DOCUMENT]
    FPDF_VIEWERREF_GetPrintScaling.restype = FPDF_BOOL

# build_tar/include/fpdfview.h: 1208
if _libs["pdfium"].has("FPDF_VIEWERREF_GetNumCopies", "cdecl"):
    FPDF_VIEWERREF_GetNumCopies = _libs["pdfium"].get("FPDF_VIEWERREF_GetNumCopies", "cdecl")
    FPDF_VIEWERREF_GetNumCopies.argtypes = [FPDF_DOCUMENT]
    FPDF_VIEWERREF_GetNumCopies.restype = c_int

# build_tar/include/fpdfview.h: 1217
if _libs["pdfium"].has("FPDF_VIEWERREF_GetPrintPageRange", "cdecl"):
    FPDF_VIEWERREF_GetPrintPageRange = _libs["pdfium"].get("FPDF_VIEWERREF_GetPrintPageRange", "cdecl")
    FPDF_VIEWERREF_GetPrintPageRange.argtypes = [FPDF_DOCUMENT]
    FPDF_VIEWERREF_GetPrintPageRange.restype = FPDF_PAGERANGE

# build_tar/include/fpdfview.h: 1227
if _libs["pdfium"].has("FPDF_VIEWERREF_GetPrintPageRangeCount", "cdecl"):
    FPDF_VIEWERREF_GetPrintPageRangeCount = _libs["pdfium"].get("FPDF_VIEWERREF_GetPrintPageRangeCount", "cdecl")
    FPDF_VIEWERREF_GetPrintPageRangeCount.argtypes = [FPDF_PAGERANGE]
    FPDF_VIEWERREF_GetPrintPageRangeCount.restype = c_size_t

# build_tar/include/fpdfview.h: 1239
if _libs["pdfium"].has("FPDF_VIEWERREF_GetPrintPageRangeElement", "cdecl"):
    FPDF_VIEWERREF_GetPrintPageRangeElement = _libs["pdfium"].get("FPDF_VIEWERREF_GetPrintPageRangeElement", "cdecl")
    FPDF_VIEWERREF_GetPrintPageRangeElement.argtypes = [FPDF_PAGERANGE, c_size_t]
    FPDF_VIEWERREF_GetPrintPageRangeElement.restype = c_int

# build_tar/include/fpdfview.h: 1249
if _libs["pdfium"].has("FPDF_VIEWERREF_GetDuplex", "cdecl"):
    FPDF_VIEWERREF_GetDuplex = _libs["pdfium"].get("FPDF_VIEWERREF_GetDuplex", "cdecl")
    FPDF_VIEWERREF_GetDuplex.argtypes = [FPDF_DOCUMENT]
    FPDF_VIEWERREF_GetDuplex.restype = FPDF_DUPLEXTYPE

# build_tar/include/fpdfview.h: 1267
if _libs["pdfium"].has("FPDF_VIEWERREF_GetName", "cdecl"):
    FPDF_VIEWERREF_GetName = _libs["pdfium"].get("FPDF_VIEWERREF_GetName", "cdecl")
    FPDF_VIEWERREF_GetName.argtypes = [FPDF_DOCUMENT, FPDF_BYTESTRING, String, c_ulong]
    FPDF_VIEWERREF_GetName.restype = c_ulong

# build_tar/include/fpdfview.h: 1279
if _libs["pdfium"].has("FPDF_CountNamedDests", "cdecl"):
    FPDF_CountNamedDests = _libs["pdfium"].get("FPDF_CountNamedDests", "cdecl")
    FPDF_CountNamedDests.argtypes = [FPDF_DOCUMENT]
    FPDF_CountNamedDests.restype = FPDF_DWORD

# build_tar/include/fpdfview.h: 1289
if _libs["pdfium"].has("FPDF_GetNamedDestByName", "cdecl"):
    FPDF_GetNamedDestByName = _libs["pdfium"].get("FPDF_GetNamedDestByName", "cdecl")
    FPDF_GetNamedDestByName.argtypes = [FPDF_DOCUMENT, FPDF_BYTESTRING]
    FPDF_GetNamedDestByName.restype = FPDF_DEST

# build_tar/include/fpdfview.h: 1312
if _libs["pdfium"].has("FPDF_GetNamedDest", "cdecl"):
    FPDF_GetNamedDest = _libs["pdfium"].get("FPDF_GetNamedDest", "cdecl")
    FPDF_GetNamedDest.argtypes = [FPDF_DOCUMENT, c_int, POINTER(None), POINTER(c_long)]
    FPDF_GetNamedDest.restype = FPDF_DEST

# build_tar/include/fpdfview.h: 1324
if _libs["pdfium"].has("FPDF_GetXFAPacketCount", "cdecl"):
    FPDF_GetXFAPacketCount = _libs["pdfium"].get("FPDF_GetXFAPacketCount", "cdecl")
    FPDF_GetXFAPacketCount.argtypes = [FPDF_DOCUMENT]
    FPDF_GetXFAPacketCount.restype = c_int

# build_tar/include/fpdfview.h: 1342
if _libs["pdfium"].has("FPDF_GetXFAPacketName", "cdecl"):
    FPDF_GetXFAPacketName = _libs["pdfium"].get("FPDF_GetXFAPacketName", "cdecl")
    FPDF_GetXFAPacketName.argtypes = [FPDF_DOCUMENT, c_int, POINTER(None), c_ulong]
    FPDF_GetXFAPacketName.restype = c_ulong

# build_tar/include/fpdfview.h: 1369
if _libs["pdfium"].has("FPDF_GetXFAPacketContent", "cdecl"):
    FPDF_GetXFAPacketContent = _libs["pdfium"].get("FPDF_GetXFAPacketContent", "cdecl")
    FPDF_GetXFAPacketContent.argtypes = [FPDF_DOCUMENT, c_int, POINTER(None), c_ulong, POINTER(c_ulong)]
    FPDF_GetXFAPacketContent.restype = FPDF_BOOL

enum_anon_4 = c_int# build_tar/include/fpdf_doc.h: 46

FILEIDTYPE_PERMANENT = 0# build_tar/include/fpdf_doc.h: 46

FILEIDTYPE_CHANGING = 1# build_tar/include/fpdf_doc.h: 46

FPDF_FILEIDTYPE = enum_anon_4# build_tar/include/fpdf_doc.h: 46

# build_tar/include/fpdf_doc.h: 57
class struct__FS_QUADPOINTSF(Structure):
    pass

struct__FS_QUADPOINTSF.__slots__ = [
    'x1',
    'y1',
    'x2',
    'y2',
    'x3',
    'y3',
    'x4',
    'y4',
]
struct__FS_QUADPOINTSF._fields_ = [
    ('x1', FS_FLOAT),
    ('y1', FS_FLOAT),
    ('x2', FS_FLOAT),
    ('y2', FS_FLOAT),
    ('x3', FS_FLOAT),
    ('y3', FS_FLOAT),
    ('x4', FS_FLOAT),
    ('y4', FS_FLOAT),
]

FS_QUADPOINTSF = struct__FS_QUADPOINTSF# build_tar/include/fpdf_doc.h: 57

# build_tar/include/fpdf_doc.h: 68
if _libs["pdfium"].has("FPDFBookmark_GetFirstChild", "cdecl"):
    FPDFBookmark_GetFirstChild = _libs["pdfium"].get("FPDFBookmark_GetFirstChild", "cdecl")
    FPDFBookmark_GetFirstChild.argtypes = [FPDF_DOCUMENT, FPDF_BOOKMARK]
    FPDFBookmark_GetFirstChild.restype = FPDF_BOOKMARK

# build_tar/include/fpdf_doc.h: 81
if _libs["pdfium"].has("FPDFBookmark_GetNextSibling", "cdecl"):
    FPDFBookmark_GetNextSibling = _libs["pdfium"].get("FPDFBookmark_GetNextSibling", "cdecl")
    FPDFBookmark_GetNextSibling.argtypes = [FPDF_DOCUMENT, FPDF_BOOKMARK]
    FPDFBookmark_GetNextSibling.restype = FPDF_BOOKMARK

# build_tar/include/fpdf_doc.h: 97
if _libs["pdfium"].has("FPDFBookmark_GetTitle", "cdecl"):
    FPDFBookmark_GetTitle = _libs["pdfium"].get("FPDFBookmark_GetTitle", "cdecl")
    FPDFBookmark_GetTitle.argtypes = [FPDF_BOOKMARK, POINTER(None), c_ulong]
    FPDFBookmark_GetTitle.restype = c_ulong

# build_tar/include/fpdf_doc.h: 111
if _libs["pdfium"].has("FPDFBookmark_Find", "cdecl"):
    FPDFBookmark_Find = _libs["pdfium"].get("FPDFBookmark_Find", "cdecl")
    FPDFBookmark_Find.argtypes = [FPDF_DOCUMENT, FPDF_WIDESTRING]
    FPDFBookmark_Find.restype = FPDF_BOOKMARK

# build_tar/include/fpdf_doc.h: 121
if _libs["pdfium"].has("FPDFBookmark_GetDest", "cdecl"):
    FPDFBookmark_GetDest = _libs["pdfium"].get("FPDFBookmark_GetDest", "cdecl")
    FPDFBookmark_GetDest.argtypes = [FPDF_DOCUMENT, FPDF_BOOKMARK]
    FPDFBookmark_GetDest.restype = FPDF_DEST

# build_tar/include/fpdf_doc.h: 134
if _libs["pdfium"].has("FPDFBookmark_GetAction", "cdecl"):
    FPDFBookmark_GetAction = _libs["pdfium"].get("FPDFBookmark_GetAction", "cdecl")
    FPDFBookmark_GetAction.argtypes = [FPDF_BOOKMARK]
    FPDFBookmark_GetAction.restype = FPDF_ACTION

# build_tar/include/fpdf_doc.h: 146
if _libs["pdfium"].has("FPDFAction_GetType", "cdecl"):
    FPDFAction_GetType = _libs["pdfium"].get("FPDFAction_GetType", "cdecl")
    FPDFAction_GetType.argtypes = [FPDF_ACTION]
    FPDFAction_GetType.restype = c_ulong

# build_tar/include/fpdf_doc.h: 160
if _libs["pdfium"].has("FPDFAction_GetDest", "cdecl"):
    FPDFAction_GetDest = _libs["pdfium"].get("FPDFAction_GetDest", "cdecl")
    FPDFAction_GetDest.argtypes = [FPDF_DOCUMENT, FPDF_ACTION]
    FPDFAction_GetDest.restype = FPDF_DEST

# build_tar/include/fpdf_doc.h: 178
if _libs["pdfium"].has("FPDFAction_GetFilePath", "cdecl"):
    FPDFAction_GetFilePath = _libs["pdfium"].get("FPDFAction_GetFilePath", "cdecl")
    FPDFAction_GetFilePath.argtypes = [FPDF_ACTION, POINTER(None), c_ulong]
    FPDFAction_GetFilePath.restype = c_ulong

# build_tar/include/fpdf_doc.h: 194
if _libs["pdfium"].has("FPDFAction_GetURIPath", "cdecl"):
    FPDFAction_GetURIPath = _libs["pdfium"].get("FPDFAction_GetURIPath", "cdecl")
    FPDFAction_GetURIPath.argtypes = [FPDF_DOCUMENT, FPDF_ACTION, POINTER(None), c_ulong]
    FPDFAction_GetURIPath.restype = c_ulong

# build_tar/include/fpdf_doc.h: 205
if _libs["pdfium"].has("FPDFDest_GetDestPageIndex", "cdecl"):
    FPDFDest_GetDestPageIndex = _libs["pdfium"].get("FPDFDest_GetDestPageIndex", "cdecl")
    FPDFDest_GetDestPageIndex.argtypes = [FPDF_DOCUMENT, FPDF_DEST]
    FPDFDest_GetDestPageIndex.restype = c_int

# build_tar/include/fpdf_doc.h: 218
if _libs["pdfium"].has("FPDFDest_GetView", "cdecl"):
    FPDFDest_GetView = _libs["pdfium"].get("FPDFDest_GetView", "cdecl")
    FPDFDest_GetView.argtypes = [FPDF_DEST, POINTER(c_ulong), POINTER(FS_FLOAT)]
    FPDFDest_GetView.restype = c_ulong

# build_tar/include/fpdf_doc.h: 235
if _libs["pdfium"].has("FPDFDest_GetLocationInPage", "cdecl"):
    FPDFDest_GetLocationInPage = _libs["pdfium"].get("FPDFDest_GetLocationInPage", "cdecl")
    FPDFDest_GetLocationInPage.argtypes = [FPDF_DEST, POINTER(FPDF_BOOL), POINTER(FPDF_BOOL), POINTER(FPDF_BOOL), POINTER(FS_FLOAT), POINTER(FS_FLOAT), POINTER(FS_FLOAT)]
    FPDFDest_GetLocationInPage.restype = FPDF_BOOL

# build_tar/include/fpdf_doc.h: 253
if _libs["pdfium"].has("FPDFLink_GetLinkAtPoint", "cdecl"):
    FPDFLink_GetLinkAtPoint = _libs["pdfium"].get("FPDFLink_GetLinkAtPoint", "cdecl")
    FPDFLink_GetLinkAtPoint.argtypes = [FPDF_PAGE, c_double, c_double]
    FPDFLink_GetLinkAtPoint.restype = FPDF_LINK

# build_tar/include/fpdf_doc.h: 268
if _libs["pdfium"].has("FPDFLink_GetLinkZOrderAtPoint", "cdecl"):
    FPDFLink_GetLinkZOrderAtPoint = _libs["pdfium"].get("FPDFLink_GetLinkZOrderAtPoint", "cdecl")
    FPDFLink_GetLinkZOrderAtPoint.argtypes = [FPDF_PAGE, c_double, c_double]
    FPDFLink_GetLinkZOrderAtPoint.restype = c_int

# build_tar/include/fpdf_doc.h: 280
if _libs["pdfium"].has("FPDFLink_GetDest", "cdecl"):
    FPDFLink_GetDest = _libs["pdfium"].get("FPDFLink_GetDest", "cdecl")
    FPDFLink_GetDest.argtypes = [FPDF_DOCUMENT, FPDF_LINK]
    FPDFLink_GetDest.restype = FPDF_DEST

# build_tar/include/fpdf_doc.h: 290
if _libs["pdfium"].has("FPDFLink_GetAction", "cdecl"):
    FPDFLink_GetAction = _libs["pdfium"].get("FPDFLink_GetAction", "cdecl")
    FPDFLink_GetAction.argtypes = [FPDF_LINK]
    FPDFLink_GetAction.restype = FPDF_ACTION

# build_tar/include/fpdf_doc.h: 300
if _libs["pdfium"].has("FPDFLink_Enumerate", "cdecl"):
    FPDFLink_Enumerate = _libs["pdfium"].get("FPDFLink_Enumerate", "cdecl")
    FPDFLink_Enumerate.argtypes = [FPDF_PAGE, POINTER(c_int), POINTER(FPDF_LINK)]
    FPDFLink_Enumerate.restype = FPDF_BOOL

# build_tar/include/fpdf_doc.h: 313
if _libs["pdfium"].has("FPDFLink_GetAnnot", "cdecl"):
    FPDFLink_GetAnnot = _libs["pdfium"].get("FPDFLink_GetAnnot", "cdecl")
    FPDFLink_GetAnnot.argtypes = [FPDF_PAGE, FPDF_LINK]
    FPDFLink_GetAnnot.restype = FPDF_ANNOTATION

# build_tar/include/fpdf_doc.h: 321
if _libs["pdfium"].has("FPDFLink_GetAnnotRect", "cdecl"):
    FPDFLink_GetAnnotRect = _libs["pdfium"].get("FPDFLink_GetAnnotRect", "cdecl")
    FPDFLink_GetAnnotRect.argtypes = [FPDF_LINK, POINTER(FS_RECTF)]
    FPDFLink_GetAnnotRect.restype = FPDF_BOOL

# build_tar/include/fpdf_doc.h: 329
if _libs["pdfium"].has("FPDFLink_CountQuadPoints", "cdecl"):
    FPDFLink_CountQuadPoints = _libs["pdfium"].get("FPDFLink_CountQuadPoints", "cdecl")
    FPDFLink_CountQuadPoints.argtypes = [FPDF_LINK]
    FPDFLink_CountQuadPoints.restype = c_int

# build_tar/include/fpdf_doc.h: 339
if _libs["pdfium"].has("FPDFLink_GetQuadPoints", "cdecl"):
    FPDFLink_GetQuadPoints = _libs["pdfium"].get("FPDFLink_GetQuadPoints", "cdecl")
    FPDFLink_GetQuadPoints.argtypes = [FPDF_LINK, c_int, POINTER(FS_QUADPOINTSF)]
    FPDFLink_GetQuadPoints.restype = FPDF_BOOL

# build_tar/include/fpdf_doc.h: 354
if _libs["pdfium"].has("FPDF_GetPageAAction", "cdecl"):
    FPDF_GetPageAAction = _libs["pdfium"].get("FPDF_GetPageAAction", "cdecl")
    FPDF_GetPageAAction.argtypes = [FPDF_PAGE, c_int]
    FPDF_GetPageAAction.restype = FPDF_ACTION

# build_tar/include/fpdf_doc.h: 372
if _libs["pdfium"].has("FPDF_GetFileIdentifier", "cdecl"):
    FPDF_GetFileIdentifier = _libs["pdfium"].get("FPDF_GetFileIdentifier", "cdecl")
    FPDF_GetFileIdentifier.argtypes = [FPDF_DOCUMENT, FPDF_FILEIDTYPE, POINTER(None), c_ulong]
    FPDF_GetFileIdentifier.restype = c_ulong

# build_tar/include/fpdf_doc.h: 398
if _libs["pdfium"].has("FPDF_GetMetaText", "cdecl"):
    FPDF_GetMetaText = _libs["pdfium"].get("FPDF_GetMetaText", "cdecl")
    FPDF_GetMetaText.argtypes = [FPDF_DOCUMENT, FPDF_BYTESTRING, POINTER(None), c_ulong]
    FPDF_GetMetaText.restype = c_ulong

# build_tar/include/fpdf_doc.h: 416
if _libs["pdfium"].has("FPDF_GetPageLabel", "cdecl"):
    FPDF_GetPageLabel = _libs["pdfium"].get("FPDF_GetPageLabel", "cdecl")
    FPDF_GetPageLabel.argtypes = [FPDF_DOCUMENT, c_int, POINTER(None), c_ulong]
    FPDF_GetPageLabel.restype = c_ulong

# build_tar/include/fpdf_formfill.h: 52
class struct__IPDF_JsPlatform(Structure):
    pass

struct__IPDF_JsPlatform.__slots__ = [
    'version',
    'app_alert',
    'app_beep',
    'app_response',
    'Doc_getFilePath',
    'Doc_mail',
    'Doc_print',
    'Doc_submitForm',
    'Doc_gotoPage',
    'Field_browse',
    'm_pFormfillinfo',
    'm_isolate',
    'm_v8EmbedderSlot',
]
struct__IPDF_JsPlatform._fields_ = [
    ('version', c_int),
    ('app_alert', CFUNCTYPE(UNCHECKED(c_int), POINTER(struct__IPDF_JsPlatform), FPDF_WIDESTRING, FPDF_WIDESTRING, c_int, c_int)),
    ('app_beep', CFUNCTYPE(UNCHECKED(None), POINTER(struct__IPDF_JsPlatform), c_int)),
    ('app_response', CFUNCTYPE(UNCHECKED(c_int), POINTER(struct__IPDF_JsPlatform), FPDF_WIDESTRING, FPDF_WIDESTRING, FPDF_WIDESTRING, FPDF_WIDESTRING, FPDF_BOOL, POINTER(None), c_int)),
    ('Doc_getFilePath', CFUNCTYPE(UNCHECKED(c_int), POINTER(struct__IPDF_JsPlatform), POINTER(None), c_int)),
    ('Doc_mail', CFUNCTYPE(UNCHECKED(None), POINTER(struct__IPDF_JsPlatform), POINTER(None), c_int, FPDF_BOOL, FPDF_WIDESTRING, FPDF_WIDESTRING, FPDF_WIDESTRING, FPDF_WIDESTRING, FPDF_WIDESTRING)),
    ('Doc_print', CFUNCTYPE(UNCHECKED(None), POINTER(struct__IPDF_JsPlatform), FPDF_BOOL, c_int, c_int, FPDF_BOOL, FPDF_BOOL, FPDF_BOOL, FPDF_BOOL, FPDF_BOOL)),
    ('Doc_submitForm', CFUNCTYPE(UNCHECKED(None), POINTER(struct__IPDF_JsPlatform), POINTER(None), c_int, FPDF_WIDESTRING)),
    ('Doc_gotoPage', CFUNCTYPE(UNCHECKED(None), POINTER(struct__IPDF_JsPlatform), c_int)),
    ('Field_browse', CFUNCTYPE(UNCHECKED(c_int), POINTER(struct__IPDF_JsPlatform), POINTER(None), c_int)),
    ('m_pFormfillinfo', POINTER(None)),
    ('m_isolate', POINTER(None)),
    ('m_v8EmbedderSlot', c_uint),
]

IPDF_JSPLATFORM = struct__IPDF_JsPlatform# build_tar/include/fpdf_formfill.h: 321

TimerCallback = CFUNCTYPE(UNCHECKED(None), c_int)# build_tar/include/fpdf_formfill.h: 339

# build_tar/include/fpdf_formfill.h: 353
class struct__FPDF_SYSTEMTIME(Structure):
    pass

struct__FPDF_SYSTEMTIME.__slots__ = [
    'wYear',
    'wMonth',
    'wDayOfWeek',
    'wDay',
    'wHour',
    'wMinute',
    'wSecond',
    'wMilliseconds',
]
struct__FPDF_SYSTEMTIME._fields_ = [
    ('wYear', c_ushort),
    ('wMonth', c_ushort),
    ('wDayOfWeek', c_ushort),
    ('wDay', c_ushort),
    ('wHour', c_ushort),
    ('wMinute', c_ushort),
    ('wSecond', c_ushort),
    ('wMilliseconds', c_ushort),
]

FPDF_SYSTEMTIME = struct__FPDF_SYSTEMTIME# build_tar/include/fpdf_formfill.h: 353

# build_tar/include/fpdf_formfill.h: 375
class struct__FPDF_FORMFILLINFO(Structure):
    pass

struct__FPDF_FORMFILLINFO.__slots__ = [
    'version',
    'Release',
    'FFI_Invalidate',
    'FFI_OutputSelectedRect',
    'FFI_SetCursor',
    'FFI_SetTimer',
    'FFI_KillTimer',
    'FFI_GetLocalTime',
    'FFI_OnChange',
    'FFI_GetPage',
    'FFI_GetCurrentPage',
    'FFI_GetRotation',
    'FFI_ExecuteNamedAction',
    'FFI_SetTextFieldFocus',
    'FFI_DoURIAction',
    'FFI_DoGoToAction',
    'm_pJsPlatform',
    'xfa_disabled',
    'FFI_DisplayCaret',
    'FFI_GetCurrentPageIndex',
    'FFI_SetCurrentPage',
    'FFI_GotoURL',
    'FFI_GetPageViewRect',
    'FFI_PageEvent',
    'FFI_PopupMenu',
    'FFI_OpenFile',
    'FFI_EmailTo',
    'FFI_UploadTo',
    'FFI_GetPlatform',
    'FFI_GetLanguage',
    'FFI_DownloadFromURL',
    'FFI_PostRequestURL',
    'FFI_PutRequestURL',
    'FFI_OnFocusChange',
    'FFI_DoURIActionWithKeyboardModifier',
]
struct__FPDF_FORMFILLINFO._fields_ = [
    ('version', c_int),
    ('Release', CFUNCTYPE(UNCHECKED(None), POINTER(struct__FPDF_FORMFILLINFO))),
    ('FFI_Invalidate', CFUNCTYPE(UNCHECKED(None), POINTER(struct__FPDF_FORMFILLINFO), FPDF_PAGE, c_double, c_double, c_double, c_double)),
    ('FFI_OutputSelectedRect', CFUNCTYPE(UNCHECKED(None), POINTER(struct__FPDF_FORMFILLINFO), FPDF_PAGE, c_double, c_double, c_double, c_double)),
    ('FFI_SetCursor', CFUNCTYPE(UNCHECKED(None), POINTER(struct__FPDF_FORMFILLINFO), c_int)),
    ('FFI_SetTimer', CFUNCTYPE(UNCHECKED(c_int), POINTER(struct__FPDF_FORMFILLINFO), c_int, TimerCallback)),
    ('FFI_KillTimer', CFUNCTYPE(UNCHECKED(None), POINTER(struct__FPDF_FORMFILLINFO), c_int)),
    ('FFI_GetLocalTime', CFUNCTYPE(UNCHECKED(FPDF_SYSTEMTIME), POINTER(struct__FPDF_FORMFILLINFO))),
    ('FFI_OnChange', CFUNCTYPE(UNCHECKED(None), POINTER(struct__FPDF_FORMFILLINFO))),
    ('FFI_GetPage', CFUNCTYPE(UNCHECKED(FPDF_PAGE), POINTER(struct__FPDF_FORMFILLINFO), FPDF_DOCUMENT, c_int)),
    ('FFI_GetCurrentPage', CFUNCTYPE(UNCHECKED(FPDF_PAGE), POINTER(struct__FPDF_FORMFILLINFO), FPDF_DOCUMENT)),
    ('FFI_GetRotation', CFUNCTYPE(UNCHECKED(c_int), POINTER(struct__FPDF_FORMFILLINFO), FPDF_PAGE)),
    ('FFI_ExecuteNamedAction', CFUNCTYPE(UNCHECKED(None), POINTER(struct__FPDF_FORMFILLINFO), FPDF_BYTESTRING)),
    ('FFI_SetTextFieldFocus', CFUNCTYPE(UNCHECKED(None), POINTER(struct__FPDF_FORMFILLINFO), FPDF_WIDESTRING, FPDF_DWORD, FPDF_BOOL)),
    ('FFI_DoURIAction', CFUNCTYPE(UNCHECKED(None), POINTER(struct__FPDF_FORMFILLINFO), FPDF_BYTESTRING)),
    ('FFI_DoGoToAction', CFUNCTYPE(UNCHECKED(None), POINTER(struct__FPDF_FORMFILLINFO), c_int, c_int, POINTER(c_float), c_int)),
    ('m_pJsPlatform', POINTER(IPDF_JSPLATFORM)),
    ('xfa_disabled', FPDF_BOOL),
    ('FFI_DisplayCaret', CFUNCTYPE(UNCHECKED(None), POINTER(struct__FPDF_FORMFILLINFO), FPDF_PAGE, FPDF_BOOL, c_double, c_double, c_double, c_double)),
    ('FFI_GetCurrentPageIndex', CFUNCTYPE(UNCHECKED(c_int), POINTER(struct__FPDF_FORMFILLINFO), FPDF_DOCUMENT)),
    ('FFI_SetCurrentPage', CFUNCTYPE(UNCHECKED(None), POINTER(struct__FPDF_FORMFILLINFO), FPDF_DOCUMENT, c_int)),
    ('FFI_GotoURL', CFUNCTYPE(UNCHECKED(None), POINTER(struct__FPDF_FORMFILLINFO), FPDF_DOCUMENT, FPDF_WIDESTRING)),
    ('FFI_GetPageViewRect', CFUNCTYPE(UNCHECKED(None), POINTER(struct__FPDF_FORMFILLINFO), FPDF_PAGE, POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double))),
    ('FFI_PageEvent', CFUNCTYPE(UNCHECKED(None), POINTER(struct__FPDF_FORMFILLINFO), c_int, FPDF_DWORD)),
    ('FFI_PopupMenu', CFUNCTYPE(UNCHECKED(FPDF_BOOL), POINTER(struct__FPDF_FORMFILLINFO), FPDF_PAGE, FPDF_WIDGET, c_int, c_float, c_float)),
    ('FFI_OpenFile', CFUNCTYPE(UNCHECKED(POINTER(FPDF_FILEHANDLER)), POINTER(struct__FPDF_FORMFILLINFO), c_int, FPDF_WIDESTRING, String)),
    ('FFI_EmailTo', CFUNCTYPE(UNCHECKED(None), POINTER(struct__FPDF_FORMFILLINFO), POINTER(FPDF_FILEHANDLER), FPDF_WIDESTRING, FPDF_WIDESTRING, FPDF_WIDESTRING, FPDF_WIDESTRING, FPDF_WIDESTRING)),
    ('FFI_UploadTo', CFUNCTYPE(UNCHECKED(None), POINTER(struct__FPDF_FORMFILLINFO), POINTER(FPDF_FILEHANDLER), c_int, FPDF_WIDESTRING)),
    ('FFI_GetPlatform', CFUNCTYPE(UNCHECKED(c_int), POINTER(struct__FPDF_FORMFILLINFO), POINTER(None), c_int)),
    ('FFI_GetLanguage', CFUNCTYPE(UNCHECKED(c_int), POINTER(struct__FPDF_FORMFILLINFO), POINTER(None), c_int)),
    ('FFI_DownloadFromURL', CFUNCTYPE(UNCHECKED(POINTER(FPDF_FILEHANDLER)), POINTER(struct__FPDF_FORMFILLINFO), FPDF_WIDESTRING)),
    ('FFI_PostRequestURL', CFUNCTYPE(UNCHECKED(FPDF_BOOL), POINTER(struct__FPDF_FORMFILLINFO), FPDF_WIDESTRING, FPDF_WIDESTRING, FPDF_WIDESTRING, FPDF_WIDESTRING, FPDF_WIDESTRING, POINTER(FPDF_BSTR))),
    ('FFI_PutRequestURL', CFUNCTYPE(UNCHECKED(FPDF_BOOL), POINTER(struct__FPDF_FORMFILLINFO), FPDF_WIDESTRING, FPDF_WIDESTRING, FPDF_WIDESTRING)),
    ('FFI_OnFocusChange', CFUNCTYPE(UNCHECKED(None), POINTER(struct__FPDF_FORMFILLINFO), FPDF_ANNOTATION, c_int)),
    ('FFI_DoURIActionWithKeyboardModifier', CFUNCTYPE(UNCHECKED(None), POINTER(struct__FPDF_FORMFILLINFO), FPDF_BYTESTRING, c_int)),
]

FPDF_FORMFILLINFO = struct__FPDF_FORMFILLINFO# build_tar/include/fpdf_formfill.h: 1136

# build_tar/include/fpdf_formfill.h: 1150
if _libs["pdfium"].has("FPDFDOC_InitFormFillEnvironment", "cdecl"):
    FPDFDOC_InitFormFillEnvironment = _libs["pdfium"].get("FPDFDOC_InitFormFillEnvironment", "cdecl")
    FPDFDOC_InitFormFillEnvironment.argtypes = [FPDF_DOCUMENT, POINTER(FPDF_FORMFILLINFO)]
    FPDFDOC_InitFormFillEnvironment.restype = FPDF_FORMHANDLE

# build_tar/include/fpdf_formfill.h: 1165
if _libs["pdfium"].has("FPDFDOC_ExitFormFillEnvironment", "cdecl"):
    FPDFDOC_ExitFormFillEnvironment = _libs["pdfium"].get("FPDFDOC_ExitFormFillEnvironment", "cdecl")
    FPDFDOC_ExitFormFillEnvironment.argtypes = [FPDF_FORMHANDLE]
    FPDFDOC_ExitFormFillEnvironment.restype = None

# build_tar/include/fpdf_formfill.h: 1178
if _libs["pdfium"].has("FORM_OnAfterLoadPage", "cdecl"):
    FORM_OnAfterLoadPage = _libs["pdfium"].get("FORM_OnAfterLoadPage", "cdecl")
    FORM_OnAfterLoadPage.argtypes = [FPDF_PAGE, FPDF_FORMHANDLE]
    FORM_OnAfterLoadPage.restype = None

# build_tar/include/fpdf_formfill.h: 1192
if _libs["pdfium"].has("FORM_OnBeforeClosePage", "cdecl"):
    FORM_OnBeforeClosePage = _libs["pdfium"].get("FORM_OnBeforeClosePage", "cdecl")
    FORM_OnBeforeClosePage.argtypes = [FPDF_PAGE, FPDF_FORMHANDLE]
    FORM_OnBeforeClosePage.restype = None

# build_tar/include/fpdf_formfill.h: 1210
if _libs["pdfium"].has("FORM_DoDocumentJSAction", "cdecl"):
    FORM_DoDocumentJSAction = _libs["pdfium"].get("FORM_DoDocumentJSAction", "cdecl")
    FORM_DoDocumentJSAction.argtypes = [FPDF_FORMHANDLE]
    FORM_DoDocumentJSAction.restype = None

# build_tar/include/fpdf_formfill.h: 1226
if _libs["pdfium"].has("FORM_DoDocumentOpenAction", "cdecl"):
    FORM_DoDocumentOpenAction = _libs["pdfium"].get("FORM_DoDocumentOpenAction", "cdecl")
    FORM_DoDocumentOpenAction.argtypes = [FPDF_FORMHANDLE]
    FORM_DoDocumentOpenAction.restype = None

# build_tar/include/fpdf_formfill.h: 1255
if _libs["pdfium"].has("FORM_DoDocumentAAction", "cdecl"):
    FORM_DoDocumentAAction = _libs["pdfium"].get("FORM_DoDocumentAAction", "cdecl")
    FORM_DoDocumentAAction.argtypes = [FPDF_FORMHANDLE, c_int]
    FORM_DoDocumentAAction.restype = None

# build_tar/include/fpdf_formfill.h: 1280
if _libs["pdfium"].has("FORM_DoPageAAction", "cdecl"):
    FORM_DoPageAAction = _libs["pdfium"].get("FORM_DoPageAAction", "cdecl")
    FORM_DoPageAAction.argtypes = [FPDF_PAGE, FPDF_FORMHANDLE, c_int]
    FORM_DoPageAAction.restype = None

# build_tar/include/fpdf_formfill.h: 1299
if _libs["pdfium"].has("FORM_OnMouseMove", "cdecl"):
    FORM_OnMouseMove = _libs["pdfium"].get("FORM_OnMouseMove", "cdecl")
    FORM_OnMouseMove.argtypes = [FPDF_FORMHANDLE, FPDF_PAGE, c_int, c_double, c_double]
    FORM_OnMouseMove.restype = FPDF_BOOL

# build_tar/include/fpdf_formfill.h: 1330
if _libs["pdfium"].has("FORM_OnMouseWheel", "cdecl"):
    FORM_OnMouseWheel = _libs["pdfium"].get("FORM_OnMouseWheel", "cdecl")
    FORM_OnMouseWheel.argtypes = [FPDF_FORMHANDLE, FPDF_PAGE, c_int, POINTER(FS_POINTF), c_int, c_int]
    FORM_OnMouseWheel.restype = FPDF_BOOL

# build_tar/include/fpdf_formfill.h: 1355
if _libs["pdfium"].has("FORM_OnFocus", "cdecl"):
    FORM_OnFocus = _libs["pdfium"].get("FORM_OnFocus", "cdecl")
    FORM_OnFocus.argtypes = [FPDF_FORMHANDLE, FPDF_PAGE, c_int, c_double, c_double]
    FORM_OnFocus.restype = FPDF_BOOL

# build_tar/include/fpdf_formfill.h: 1377
if _libs["pdfium"].has("FORM_OnLButtonDown", "cdecl"):
    FORM_OnLButtonDown = _libs["pdfium"].get("FORM_OnLButtonDown", "cdecl")
    FORM_OnLButtonDown.argtypes = [FPDF_FORMHANDLE, FPDF_PAGE, c_int, c_double, c_double]
    FORM_OnLButtonDown.restype = FPDF_BOOL

# build_tar/include/fpdf_formfill.h: 1390
if _libs["pdfium"].has("FORM_OnRButtonDown", "cdecl"):
    FORM_OnRButtonDown = _libs["pdfium"].get("FORM_OnRButtonDown", "cdecl")
    FORM_OnRButtonDown.argtypes = [FPDF_FORMHANDLE, FPDF_PAGE, c_int, c_double, c_double]
    FORM_OnRButtonDown.restype = FPDF_BOOL

# build_tar/include/fpdf_formfill.h: 1409
if _libs["pdfium"].has("FORM_OnLButtonUp", "cdecl"):
    FORM_OnLButtonUp = _libs["pdfium"].get("FORM_OnLButtonUp", "cdecl")
    FORM_OnLButtonUp.argtypes = [FPDF_FORMHANDLE, FPDF_PAGE, c_int, c_double, c_double]
    FORM_OnLButtonUp.restype = FPDF_BOOL

# build_tar/include/fpdf_formfill.h: 1422
if _libs["pdfium"].has("FORM_OnRButtonUp", "cdecl"):
    FORM_OnRButtonUp = _libs["pdfium"].get("FORM_OnRButtonUp", "cdecl")
    FORM_OnRButtonUp.argtypes = [FPDF_FORMHANDLE, FPDF_PAGE, c_int, c_double, c_double]
    FORM_OnRButtonUp.restype = FPDF_BOOL

# build_tar/include/fpdf_formfill.h: 1445
if _libs["pdfium"].has("FORM_OnLButtonDoubleClick", "cdecl"):
    FORM_OnLButtonDoubleClick = _libs["pdfium"].get("FORM_OnLButtonDoubleClick", "cdecl")
    FORM_OnLButtonDoubleClick.argtypes = [FPDF_FORMHANDLE, FPDF_PAGE, c_int, c_double, c_double]
    FORM_OnLButtonDoubleClick.restype = FPDF_BOOL

# build_tar/include/fpdf_formfill.h: 1465
if _libs["pdfium"].has("FORM_OnKeyDown", "cdecl"):
    FORM_OnKeyDown = _libs["pdfium"].get("FORM_OnKeyDown", "cdecl")
    FORM_OnKeyDown.argtypes = [FPDF_FORMHANDLE, FPDF_PAGE, c_int, c_int]
    FORM_OnKeyDown.restype = FPDF_BOOL

# build_tar/include/fpdf_formfill.h: 1484
if _libs["pdfium"].has("FORM_OnKeyUp", "cdecl"):
    FORM_OnKeyUp = _libs["pdfium"].get("FORM_OnKeyUp", "cdecl")
    FORM_OnKeyUp.argtypes = [FPDF_FORMHANDLE, FPDF_PAGE, c_int, c_int]
    FORM_OnKeyUp.restype = FPDF_BOOL

# build_tar/include/fpdf_formfill.h: 1503
if _libs["pdfium"].has("FORM_OnChar", "cdecl"):
    FORM_OnChar = _libs["pdfium"].get("FORM_OnChar", "cdecl")
    FORM_OnChar.argtypes = [FPDF_FORMHANDLE, FPDF_PAGE, c_int, c_int]
    FORM_OnChar.restype = FPDF_BOOL

# build_tar/include/fpdf_formfill.h: 1526
if _libs["pdfium"].has("FORM_GetFocusedText", "cdecl"):
    FORM_GetFocusedText = _libs["pdfium"].get("FORM_GetFocusedText", "cdecl")
    FORM_GetFocusedText.argtypes = [FPDF_FORMHANDLE, FPDF_PAGE, POINTER(None), c_ulong]
    FORM_GetFocusedText.restype = c_ulong

# build_tar/include/fpdf_formfill.h: 1549
if _libs["pdfium"].has("FORM_GetSelectedText", "cdecl"):
    FORM_GetSelectedText = _libs["pdfium"].get("FORM_GetSelectedText", "cdecl")
    FORM_GetSelectedText.argtypes = [FPDF_FORMHANDLE, FPDF_PAGE, POINTER(None), c_ulong]
    FORM_GetSelectedText.restype = c_ulong

# build_tar/include/fpdf_formfill.h: 1569
if _libs["pdfium"].has("FORM_ReplaceSelection", "cdecl"):
    FORM_ReplaceSelection = _libs["pdfium"].get("FORM_ReplaceSelection", "cdecl")
    FORM_ReplaceSelection.argtypes = [FPDF_FORMHANDLE, FPDF_PAGE, FPDF_WIDESTRING]
    FORM_ReplaceSelection.restype = None

# build_tar/include/fpdf_formfill.h: 1586
if _libs["pdfium"].has("FORM_SelectAllText", "cdecl"):
    FORM_SelectAllText = _libs["pdfium"].get("FORM_SelectAllText", "cdecl")
    FORM_SelectAllText.argtypes = [FPDF_FORMHANDLE, FPDF_PAGE]
    FORM_SelectAllText.restype = FPDF_BOOL

# build_tar/include/fpdf_formfill.h: 1599
if _libs["pdfium"].has("FORM_CanUndo", "cdecl"):
    FORM_CanUndo = _libs["pdfium"].get("FORM_CanUndo", "cdecl")
    FORM_CanUndo.argtypes = [FPDF_FORMHANDLE, FPDF_PAGE]
    FORM_CanUndo.restype = FPDF_BOOL

# build_tar/include/fpdf_formfill.h: 1613
if _libs["pdfium"].has("FORM_CanRedo", "cdecl"):
    FORM_CanRedo = _libs["pdfium"].get("FORM_CanRedo", "cdecl")
    FORM_CanRedo.argtypes = [FPDF_FORMHANDLE, FPDF_PAGE]
    FORM_CanRedo.restype = FPDF_BOOL

# build_tar/include/fpdf_formfill.h: 1626
if _libs["pdfium"].has("FORM_Undo", "cdecl"):
    FORM_Undo = _libs["pdfium"].get("FORM_Undo", "cdecl")
    FORM_Undo.argtypes = [FPDF_FORMHANDLE, FPDF_PAGE]
    FORM_Undo.restype = FPDF_BOOL

# build_tar/include/fpdf_formfill.h: 1639
if _libs["pdfium"].has("FORM_Redo", "cdecl"):
    FORM_Redo = _libs["pdfium"].get("FORM_Redo", "cdecl")
    FORM_Redo.argtypes = [FPDF_FORMHANDLE, FPDF_PAGE]
    FORM_Redo.restype = FPDF_BOOL

# build_tar/include/fpdf_formfill.h: 1654
if _libs["pdfium"].has("FORM_ForceToKillFocus", "cdecl"):
    FORM_ForceToKillFocus = _libs["pdfium"].get("FORM_ForceToKillFocus", "cdecl")
    FORM_ForceToKillFocus.argtypes = [FPDF_FORMHANDLE]
    FORM_ForceToKillFocus.restype = FPDF_BOOL

# build_tar/include/fpdf_formfill.h: 1679
if _libs["pdfium"].has("FORM_GetFocusedAnnot", "cdecl"):
    FORM_GetFocusedAnnot = _libs["pdfium"].get("FORM_GetFocusedAnnot", "cdecl")
    FORM_GetFocusedAnnot.argtypes = [FPDF_FORMHANDLE, POINTER(c_int), POINTER(FPDF_ANNOTATION)]
    FORM_GetFocusedAnnot.restype = FPDF_BOOL

# build_tar/include/fpdf_formfill.h: 1698
if _libs["pdfium"].has("FORM_SetFocusedAnnot", "cdecl"):
    FORM_SetFocusedAnnot = _libs["pdfium"].get("FORM_SetFocusedAnnot", "cdecl")
    FORM_SetFocusedAnnot.argtypes = [FPDF_FORMHANDLE, FPDF_ANNOTATION]
    FORM_SetFocusedAnnot.restype = FPDF_BOOL

# build_tar/include/fpdf_formfill.h: 1754
if _libs["pdfium"].has("FPDFPage_HasFormFieldAtPoint", "cdecl"):
    FPDFPage_HasFormFieldAtPoint = _libs["pdfium"].get("FPDFPage_HasFormFieldAtPoint", "cdecl")
    FPDFPage_HasFormFieldAtPoint.argtypes = [FPDF_FORMHANDLE, FPDF_PAGE, c_double, c_double]
    FPDFPage_HasFormFieldAtPoint.restype = c_int

# build_tar/include/fpdf_formfill.h: 1773
if _libs["pdfium"].has("FPDFPage_FormFieldZOrderAtPoint", "cdecl"):
    FPDFPage_FormFieldZOrderAtPoint = _libs["pdfium"].get("FPDFPage_FormFieldZOrderAtPoint", "cdecl")
    FPDFPage_FormFieldZOrderAtPoint.argtypes = [FPDF_FORMHANDLE, FPDF_PAGE, c_double, c_double]
    FPDFPage_FormFieldZOrderAtPoint.restype = c_int

# build_tar/include/fpdf_formfill.h: 1801
if _libs["pdfium"].has("FPDF_SetFormFieldHighlightColor", "cdecl"):
    FPDF_SetFormFieldHighlightColor = _libs["pdfium"].get("FPDF_SetFormFieldHighlightColor", "cdecl")
    FPDF_SetFormFieldHighlightColor.argtypes = [FPDF_FORMHANDLE, c_int, c_ulong]
    FPDF_SetFormFieldHighlightColor.restype = None

# build_tar/include/fpdf_formfill.h: 1820
if _libs["pdfium"].has("FPDF_SetFormFieldHighlightAlpha", "cdecl"):
    FPDF_SetFormFieldHighlightAlpha = _libs["pdfium"].get("FPDF_SetFormFieldHighlightAlpha", "cdecl")
    FPDF_SetFormFieldHighlightAlpha.argtypes = [FPDF_FORMHANDLE, c_ubyte]
    FPDF_SetFormFieldHighlightAlpha.restype = None

# build_tar/include/fpdf_formfill.h: 1835
if _libs["pdfium"].has("FPDF_RemoveFormFieldHighlight", "cdecl"):
    FPDF_RemoveFormFieldHighlight = _libs["pdfium"].get("FPDF_RemoveFormFieldHighlight", "cdecl")
    FPDF_RemoveFormFieldHighlight.argtypes = [FPDF_FORMHANDLE]
    FPDF_RemoveFormFieldHighlight.restype = None

# build_tar/include/fpdf_formfill.h: 1874
if _libs["pdfium"].has("FPDF_FFLDraw", "cdecl"):
    FPDF_FFLDraw = _libs["pdfium"].get("FPDF_FFLDraw", "cdecl")
    FPDF_FFLDraw.argtypes = [FPDF_FORMHANDLE, FPDF_BITMAP, FPDF_PAGE, c_int, c_int, c_int, c_int, c_int, c_int]
    FPDF_FFLDraw.restype = None

# build_tar/include/fpdf_formfill.h: 1907
if _libs["pdfium"].has("FPDF_GetFormType", "cdecl"):
    FPDF_GetFormType = _libs["pdfium"].get("FPDF_GetFormType", "cdecl")
    FPDF_GetFormType.argtypes = [FPDF_DOCUMENT]
    FPDF_GetFormType.restype = c_int

# build_tar/include/fpdf_formfill.h: 1933
if _libs["pdfium"].has("FORM_SetIndexSelected", "cdecl"):
    FORM_SetIndexSelected = _libs["pdfium"].get("FORM_SetIndexSelected", "cdecl")
    FORM_SetIndexSelected.argtypes = [FPDF_FORMHANDLE, FPDF_PAGE, c_int, FPDF_BOOL]
    FORM_SetIndexSelected.restype = FPDF_BOOL

# build_tar/include/fpdf_formfill.h: 1958
if _libs["pdfium"].has("FORM_IsIndexSelected", "cdecl"):
    FORM_IsIndexSelected = _libs["pdfium"].get("FORM_IsIndexSelected", "cdecl")
    FORM_IsIndexSelected.argtypes = [FPDF_FORMHANDLE, FPDF_PAGE, c_int]
    FORM_IsIndexSelected.restype = FPDF_BOOL

# build_tar/include/fpdf_formfill.h: 1970
if _libs["pdfium"].has("FPDF_LoadXFA", "cdecl"):
    FPDF_LoadXFA = _libs["pdfium"].get("FPDF_LoadXFA", "cdecl")
    FPDF_LoadXFA.argtypes = [FPDF_DOCUMENT]
    FPDF_LoadXFA.restype = FPDF_BOOL

enum_FPDFANNOT_COLORTYPE = c_int# build_tar/include/fpdf_annot.h: 90

FPDFANNOT_COLORTYPE_Color = 0# build_tar/include/fpdf_annot.h: 90

FPDFANNOT_COLORTYPE_InteriorColor = (FPDFANNOT_COLORTYPE_Color + 1)# build_tar/include/fpdf_annot.h: 90

FPDFANNOT_COLORTYPE = enum_FPDFANNOT_COLORTYPE# build_tar/include/fpdf_annot.h: 90

# build_tar/include/fpdf_annot.h: 112
if _libs["pdfium"].has("FPDFAnnot_IsSupportedSubtype", "cdecl"):
    FPDFAnnot_IsSupportedSubtype = _libs["pdfium"].get("FPDFAnnot_IsSupportedSubtype", "cdecl")
    FPDFAnnot_IsSupportedSubtype.argtypes = [FPDF_ANNOTATION_SUBTYPE]
    FPDFAnnot_IsSupportedSubtype.restype = FPDF_BOOL

# build_tar/include/fpdf_annot.h: 125
if _libs["pdfium"].has("FPDFPage_CreateAnnot", "cdecl"):
    FPDFPage_CreateAnnot = _libs["pdfium"].get("FPDFPage_CreateAnnot", "cdecl")
    FPDFPage_CreateAnnot.argtypes = [FPDF_PAGE, FPDF_ANNOTATION_SUBTYPE]
    FPDFPage_CreateAnnot.restype = FPDF_ANNOTATION

# build_tar/include/fpdf_annot.h: 133
if _libs["pdfium"].has("FPDFPage_GetAnnotCount", "cdecl"):
    FPDFPage_GetAnnotCount = _libs["pdfium"].get("FPDFPage_GetAnnotCount", "cdecl")
    FPDFPage_GetAnnotCount.argtypes = [FPDF_PAGE]
    FPDFPage_GetAnnotCount.restype = c_int

# build_tar/include/fpdf_annot.h: 143
if _libs["pdfium"].has("FPDFPage_GetAnnot", "cdecl"):
    FPDFPage_GetAnnot = _libs["pdfium"].get("FPDFPage_GetAnnot", "cdecl")
    FPDFPage_GetAnnot.argtypes = [FPDF_PAGE, c_int]
    FPDFPage_GetAnnot.restype = FPDF_ANNOTATION

# build_tar/include/fpdf_annot.h: 154
if _libs["pdfium"].has("FPDFPage_GetAnnotIndex", "cdecl"):
    FPDFPage_GetAnnotIndex = _libs["pdfium"].get("FPDFPage_GetAnnotIndex", "cdecl")
    FPDFPage_GetAnnotIndex.argtypes = [FPDF_PAGE, FPDF_ANNOTATION]
    FPDFPage_GetAnnotIndex.restype = c_int

# build_tar/include/fpdf_annot.h: 163
if _libs["pdfium"].has("FPDFPage_CloseAnnot", "cdecl"):
    FPDFPage_CloseAnnot = _libs["pdfium"].get("FPDFPage_CloseAnnot", "cdecl")
    FPDFPage_CloseAnnot.argtypes = [FPDF_ANNOTATION]
    FPDFPage_CloseAnnot.restype = None

# build_tar/include/fpdf_annot.h: 172
if _libs["pdfium"].has("FPDFPage_RemoveAnnot", "cdecl"):
    FPDFPage_RemoveAnnot = _libs["pdfium"].get("FPDFPage_RemoveAnnot", "cdecl")
    FPDFPage_RemoveAnnot.argtypes = [FPDF_PAGE, c_int]
    FPDFPage_RemoveAnnot.restype = FPDF_BOOL

# build_tar/include/fpdf_annot.h: 182
if _libs["pdfium"].has("FPDFAnnot_GetSubtype", "cdecl"):
    FPDFAnnot_GetSubtype = _libs["pdfium"].get("FPDFAnnot_GetSubtype", "cdecl")
    FPDFAnnot_GetSubtype.argtypes = [FPDF_ANNOTATION]
    FPDFAnnot_GetSubtype.restype = FPDF_ANNOTATION_SUBTYPE

# build_tar/include/fpdf_annot.h: 193
if _libs["pdfium"].has("FPDFAnnot_IsObjectSupportedSubtype", "cdecl"):
    FPDFAnnot_IsObjectSupportedSubtype = _libs["pdfium"].get("FPDFAnnot_IsObjectSupportedSubtype", "cdecl")
    FPDFAnnot_IsObjectSupportedSubtype.argtypes = [FPDF_ANNOTATION_SUBTYPE]
    FPDFAnnot_IsObjectSupportedSubtype.restype = FPDF_BOOL

# build_tar/include/fpdf_annot.h: 207
if _libs["pdfium"].has("FPDFAnnot_UpdateObject", "cdecl"):
    FPDFAnnot_UpdateObject = _libs["pdfium"].get("FPDFAnnot_UpdateObject", "cdecl")
    FPDFAnnot_UpdateObject.argtypes = [FPDF_ANNOTATION, FPDF_PAGEOBJECT]
    FPDFAnnot_UpdateObject.restype = FPDF_BOOL

# build_tar/include/fpdf_annot.h: 222
if _libs["pdfium"].has("FPDFAnnot_AddInkStroke", "cdecl"):
    FPDFAnnot_AddInkStroke = _libs["pdfium"].get("FPDFAnnot_AddInkStroke", "cdecl")
    FPDFAnnot_AddInkStroke.argtypes = [FPDF_ANNOTATION, POINTER(FS_POINTF), c_size_t]
    FPDFAnnot_AddInkStroke.restype = c_int

# build_tar/include/fpdf_annot.h: 235
if _libs["pdfium"].has("FPDFAnnot_RemoveInkList", "cdecl"):
    FPDFAnnot_RemoveInkList = _libs["pdfium"].get("FPDFAnnot_RemoveInkList", "cdecl")
    FPDFAnnot_RemoveInkList.argtypes = [FPDF_ANNOTATION]
    FPDFAnnot_RemoveInkList.restype = FPDF_BOOL

# build_tar/include/fpdf_annot.h: 249
if _libs["pdfium"].has("FPDFAnnot_AppendObject", "cdecl"):
    FPDFAnnot_AppendObject = _libs["pdfium"].get("FPDFAnnot_AppendObject", "cdecl")
    FPDFAnnot_AppendObject.argtypes = [FPDF_ANNOTATION, FPDF_PAGEOBJECT]
    FPDFAnnot_AppendObject.restype = FPDF_BOOL

# build_tar/include/fpdf_annot.h: 258
if _libs["pdfium"].has("FPDFAnnot_GetObjectCount", "cdecl"):
    FPDFAnnot_GetObjectCount = _libs["pdfium"].get("FPDFAnnot_GetObjectCount", "cdecl")
    FPDFAnnot_GetObjectCount.argtypes = [FPDF_ANNOTATION]
    FPDFAnnot_GetObjectCount.restype = c_int

# build_tar/include/fpdf_annot.h: 268
if _libs["pdfium"].has("FPDFAnnot_GetObject", "cdecl"):
    FPDFAnnot_GetObject = _libs["pdfium"].get("FPDFAnnot_GetObject", "cdecl")
    FPDFAnnot_GetObject.argtypes = [FPDF_ANNOTATION, c_int]
    FPDFAnnot_GetObject.restype = FPDF_PAGEOBJECT

# build_tar/include/fpdf_annot.h: 278
if _libs["pdfium"].has("FPDFAnnot_RemoveObject", "cdecl"):
    FPDFAnnot_RemoveObject = _libs["pdfium"].get("FPDFAnnot_RemoveObject", "cdecl")
    FPDFAnnot_RemoveObject.argtypes = [FPDF_ANNOTATION, c_int]
    FPDFAnnot_RemoveObject.restype = FPDF_BOOL

# build_tar/include/fpdf_annot.h: 291
if _libs["pdfium"].has("FPDFAnnot_SetColor", "cdecl"):
    FPDFAnnot_SetColor = _libs["pdfium"].get("FPDFAnnot_SetColor", "cdecl")
    FPDFAnnot_SetColor.argtypes = [FPDF_ANNOTATION, FPDFANNOT_COLORTYPE, c_uint, c_uint, c_uint, c_uint]
    FPDFAnnot_SetColor.restype = FPDF_BOOL

# build_tar/include/fpdf_annot.h: 310
if _libs["pdfium"].has("FPDFAnnot_GetColor", "cdecl"):
    FPDFAnnot_GetColor = _libs["pdfium"].get("FPDFAnnot_GetColor", "cdecl")
    FPDFAnnot_GetColor.argtypes = [FPDF_ANNOTATION, FPDFANNOT_COLORTYPE, POINTER(c_uint), POINTER(c_uint), POINTER(c_uint), POINTER(c_uint)]
    FPDFAnnot_GetColor.restype = FPDF_BOOL

# build_tar/include/fpdf_annot.h: 330
if _libs["pdfium"].has("FPDFAnnot_HasAttachmentPoints", "cdecl"):
    FPDFAnnot_HasAttachmentPoints = _libs["pdfium"].get("FPDFAnnot_HasAttachmentPoints", "cdecl")
    FPDFAnnot_HasAttachmentPoints.argtypes = [FPDF_ANNOTATION]
    FPDFAnnot_HasAttachmentPoints.restype = FPDF_BOOL

# build_tar/include/fpdf_annot.h: 346
if _libs["pdfium"].has("FPDFAnnot_SetAttachmentPoints", "cdecl"):
    FPDFAnnot_SetAttachmentPoints = _libs["pdfium"].get("FPDFAnnot_SetAttachmentPoints", "cdecl")
    FPDFAnnot_SetAttachmentPoints.argtypes = [FPDF_ANNOTATION, c_size_t, POINTER(FS_QUADPOINTSF)]
    FPDFAnnot_SetAttachmentPoints.restype = FPDF_BOOL

# build_tar/include/fpdf_annot.h: 361
if _libs["pdfium"].has("FPDFAnnot_AppendAttachmentPoints", "cdecl"):
    FPDFAnnot_AppendAttachmentPoints = _libs["pdfium"].get("FPDFAnnot_AppendAttachmentPoints", "cdecl")
    FPDFAnnot_AppendAttachmentPoints.argtypes = [FPDF_ANNOTATION, POINTER(FS_QUADPOINTSF)]
    FPDFAnnot_AppendAttachmentPoints.restype = FPDF_BOOL

# build_tar/include/fpdf_annot.h: 371
if _libs["pdfium"].has("FPDFAnnot_CountAttachmentPoints", "cdecl"):
    FPDFAnnot_CountAttachmentPoints = _libs["pdfium"].get("FPDFAnnot_CountAttachmentPoints", "cdecl")
    FPDFAnnot_CountAttachmentPoints.argtypes = [FPDF_ANNOTATION]
    FPDFAnnot_CountAttachmentPoints.restype = c_size_t

# build_tar/include/fpdf_annot.h: 382
if _libs["pdfium"].has("FPDFAnnot_GetAttachmentPoints", "cdecl"):
    FPDFAnnot_GetAttachmentPoints = _libs["pdfium"].get("FPDFAnnot_GetAttachmentPoints", "cdecl")
    FPDFAnnot_GetAttachmentPoints.argtypes = [FPDF_ANNOTATION, c_size_t, POINTER(FS_QUADPOINTSF)]
    FPDFAnnot_GetAttachmentPoints.restype = FPDF_BOOL

# build_tar/include/fpdf_annot.h: 396
if _libs["pdfium"].has("FPDFAnnot_SetRect", "cdecl"):
    FPDFAnnot_SetRect = _libs["pdfium"].get("FPDFAnnot_SetRect", "cdecl")
    FPDFAnnot_SetRect.argtypes = [FPDF_ANNOTATION, POINTER(FS_RECTF)]
    FPDFAnnot_SetRect.restype = FPDF_BOOL

# build_tar/include/fpdf_annot.h: 406
if _libs["pdfium"].has("FPDFAnnot_GetRect", "cdecl"):
    FPDFAnnot_GetRect = _libs["pdfium"].get("FPDFAnnot_GetRect", "cdecl")
    FPDFAnnot_GetRect.argtypes = [FPDF_ANNOTATION, POINTER(FS_RECTF)]
    FPDFAnnot_GetRect.restype = FPDF_BOOL

# build_tar/include/fpdf_annot.h: 421
if _libs["pdfium"].has("FPDFAnnot_GetVertices", "cdecl"):
    FPDFAnnot_GetVertices = _libs["pdfium"].get("FPDFAnnot_GetVertices", "cdecl")
    FPDFAnnot_GetVertices.argtypes = [FPDF_ANNOTATION, POINTER(FS_POINTF), c_ulong]
    FPDFAnnot_GetVertices.restype = c_ulong

# build_tar/include/fpdf_annot.h: 433
if _libs["pdfium"].has("FPDFAnnot_GetInkListCount", "cdecl"):
    FPDFAnnot_GetInkListCount = _libs["pdfium"].get("FPDFAnnot_GetInkListCount", "cdecl")
    FPDFAnnot_GetInkListCount.argtypes = [FPDF_ANNOTATION]
    FPDFAnnot_GetInkListCount.restype = c_ulong

# build_tar/include/fpdf_annot.h: 448
if _libs["pdfium"].has("FPDFAnnot_GetInkListPath", "cdecl"):
    FPDFAnnot_GetInkListPath = _libs["pdfium"].get("FPDFAnnot_GetInkListPath", "cdecl")
    FPDFAnnot_GetInkListPath.argtypes = [FPDF_ANNOTATION, c_ulong, POINTER(FS_POINTF), c_ulong]
    FPDFAnnot_GetInkListPath.restype = c_ulong

# build_tar/include/fpdf_annot.h: 462
if _libs["pdfium"].has("FPDFAnnot_GetLine", "cdecl"):
    FPDFAnnot_GetLine = _libs["pdfium"].get("FPDFAnnot_GetLine", "cdecl")
    FPDFAnnot_GetLine.argtypes = [FPDF_ANNOTATION, POINTER(FS_POINTF), POINTER(FS_POINTF)]
    FPDFAnnot_GetLine.restype = FPDF_BOOL

# build_tar/include/fpdf_annot.h: 478
if _libs["pdfium"].has("FPDFAnnot_SetBorder", "cdecl"):
    FPDFAnnot_SetBorder = _libs["pdfium"].get("FPDFAnnot_SetBorder", "cdecl")
    FPDFAnnot_SetBorder.argtypes = [FPDF_ANNOTATION, c_float, c_float, c_float]
    FPDFAnnot_SetBorder.restype = FPDF_BOOL

# build_tar/include/fpdf_annot.h: 494
if _libs["pdfium"].has("FPDFAnnot_GetBorder", "cdecl"):
    FPDFAnnot_GetBorder = _libs["pdfium"].get("FPDFAnnot_GetBorder", "cdecl")
    FPDFAnnot_GetBorder.argtypes = [FPDF_ANNOTATION, POINTER(c_float), POINTER(c_float), POINTER(c_float)]
    FPDFAnnot_GetBorder.restype = FPDF_BOOL

# build_tar/include/fpdf_annot.h: 506
if _libs["pdfium"].has("FPDFAnnot_HasKey", "cdecl"):
    FPDFAnnot_HasKey = _libs["pdfium"].get("FPDFAnnot_HasKey", "cdecl")
    FPDFAnnot_HasKey.argtypes = [FPDF_ANNOTATION, FPDF_BYTESTRING]
    FPDFAnnot_HasKey.restype = FPDF_BOOL

# build_tar/include/fpdf_annot.h: 517
if _libs["pdfium"].has("FPDFAnnot_GetValueType", "cdecl"):
    FPDFAnnot_GetValueType = _libs["pdfium"].get("FPDFAnnot_GetValueType", "cdecl")
    FPDFAnnot_GetValueType.argtypes = [FPDF_ANNOTATION, FPDF_BYTESTRING]
    FPDFAnnot_GetValueType.restype = FPDF_OBJECT_TYPE

# build_tar/include/fpdf_annot.h: 530
if _libs["pdfium"].has("FPDFAnnot_SetStringValue", "cdecl"):
    FPDFAnnot_SetStringValue = _libs["pdfium"].get("FPDFAnnot_SetStringValue", "cdecl")
    FPDFAnnot_SetStringValue.argtypes = [FPDF_ANNOTATION, FPDF_BYTESTRING, FPDF_WIDESTRING]
    FPDFAnnot_SetStringValue.restype = FPDF_BOOL

# build_tar/include/fpdf_annot.h: 550
if _libs["pdfium"].has("FPDFAnnot_GetStringValue", "cdecl"):
    FPDFAnnot_GetStringValue = _libs["pdfium"].get("FPDFAnnot_GetStringValue", "cdecl")
    FPDFAnnot_GetStringValue.argtypes = [FPDF_ANNOTATION, FPDF_BYTESTRING, POINTER(FPDF_WCHAR), c_ulong]
    FPDFAnnot_GetStringValue.restype = c_ulong

# build_tar/include/fpdf_annot.h: 567
if _libs["pdfium"].has("FPDFAnnot_GetNumberValue", "cdecl"):
    FPDFAnnot_GetNumberValue = _libs["pdfium"].get("FPDFAnnot_GetNumberValue", "cdecl")
    FPDFAnnot_GetNumberValue.argtypes = [FPDF_ANNOTATION, FPDF_BYTESTRING, POINTER(c_float)]
    FPDFAnnot_GetNumberValue.restype = FPDF_BOOL

# build_tar/include/fpdf_annot.h: 584
if _libs["pdfium"].has("FPDFAnnot_SetAP", "cdecl"):
    FPDFAnnot_SetAP = _libs["pdfium"].get("FPDFAnnot_SetAP", "cdecl")
    FPDFAnnot_SetAP.argtypes = [FPDF_ANNOTATION, FPDF_ANNOT_APPEARANCEMODE, FPDF_WIDESTRING]
    FPDFAnnot_SetAP.restype = FPDF_BOOL

# build_tar/include/fpdf_annot.h: 606
if _libs["pdfium"].has("FPDFAnnot_GetAP", "cdecl"):
    FPDFAnnot_GetAP = _libs["pdfium"].get("FPDFAnnot_GetAP", "cdecl")
    FPDFAnnot_GetAP.argtypes = [FPDF_ANNOTATION, FPDF_ANNOT_APPEARANCEMODE, POINTER(FPDF_WCHAR), c_ulong]
    FPDFAnnot_GetAP.restype = c_ulong

# build_tar/include/fpdf_annot.h: 622
if _libs["pdfium"].has("FPDFAnnot_GetLinkedAnnot", "cdecl"):
    FPDFAnnot_GetLinkedAnnot = _libs["pdfium"].get("FPDFAnnot_GetLinkedAnnot", "cdecl")
    FPDFAnnot_GetLinkedAnnot.argtypes = [FPDF_ANNOTATION, FPDF_BYTESTRING]
    FPDFAnnot_GetLinkedAnnot.restype = FPDF_ANNOTATION

# build_tar/include/fpdf_annot.h: 630
if _libs["pdfium"].has("FPDFAnnot_GetFlags", "cdecl"):
    FPDFAnnot_GetFlags = _libs["pdfium"].get("FPDFAnnot_GetFlags", "cdecl")
    FPDFAnnot_GetFlags.argtypes = [FPDF_ANNOTATION]
    FPDFAnnot_GetFlags.restype = c_int

# build_tar/include/fpdf_annot.h: 639
if _libs["pdfium"].has("FPDFAnnot_SetFlags", "cdecl"):
    FPDFAnnot_SetFlags = _libs["pdfium"].get("FPDFAnnot_SetFlags", "cdecl")
    FPDFAnnot_SetFlags.argtypes = [FPDF_ANNOTATION, c_int]
    FPDFAnnot_SetFlags.restype = FPDF_BOOL

# build_tar/include/fpdf_annot.h: 651
if _libs["pdfium"].has("FPDFAnnot_GetFormFieldFlags", "cdecl"):
    FPDFAnnot_GetFormFieldFlags = _libs["pdfium"].get("FPDFAnnot_GetFormFieldFlags", "cdecl")
    FPDFAnnot_GetFormFieldFlags.argtypes = [FPDF_FORMHANDLE, FPDF_ANNOTATION]
    FPDFAnnot_GetFormFieldFlags.restype = c_int

# build_tar/include/fpdf_annot.h: 668
if _libs["pdfium"].has("FPDFAnnot_GetFormFieldAtPoint", "cdecl"):
    FPDFAnnot_GetFormFieldAtPoint = _libs["pdfium"].get("FPDFAnnot_GetFormFieldAtPoint", "cdecl")
    FPDFAnnot_GetFormFieldAtPoint.argtypes = [FPDF_FORMHANDLE, FPDF_PAGE, POINTER(FS_POINTF)]
    FPDFAnnot_GetFormFieldAtPoint.restype = FPDF_ANNOTATION

# build_tar/include/fpdf_annot.h: 686
if _libs["pdfium"].has("FPDFAnnot_GetFormFieldName", "cdecl"):
    FPDFAnnot_GetFormFieldName = _libs["pdfium"].get("FPDFAnnot_GetFormFieldName", "cdecl")
    FPDFAnnot_GetFormFieldName.argtypes = [FPDF_FORMHANDLE, FPDF_ANNOTATION, POINTER(FPDF_WCHAR), c_ulong]
    FPDFAnnot_GetFormFieldName.restype = c_ulong

# build_tar/include/fpdf_annot.h: 702
if _libs["pdfium"].has("FPDFAnnot_GetFormFieldType", "cdecl"):
    FPDFAnnot_GetFormFieldType = _libs["pdfium"].get("FPDFAnnot_GetFormFieldType", "cdecl")
    FPDFAnnot_GetFormFieldType.argtypes = [FPDF_FORMHANDLE, FPDF_ANNOTATION]
    FPDFAnnot_GetFormFieldType.restype = c_int

# build_tar/include/fpdf_annot.h: 718
if _libs["pdfium"].has("FPDFAnnot_GetFormFieldValue", "cdecl"):
    FPDFAnnot_GetFormFieldValue = _libs["pdfium"].get("FPDFAnnot_GetFormFieldValue", "cdecl")
    FPDFAnnot_GetFormFieldValue.argtypes = [FPDF_FORMHANDLE, FPDF_ANNOTATION, POINTER(FPDF_WCHAR), c_ulong]
    FPDFAnnot_GetFormFieldValue.restype = c_ulong

# build_tar/include/fpdf_annot.h: 733
if _libs["pdfium"].has("FPDFAnnot_GetOptionCount", "cdecl"):
    FPDFAnnot_GetOptionCount = _libs["pdfium"].get("FPDFAnnot_GetOptionCount", "cdecl")
    FPDFAnnot_GetOptionCount.argtypes = [FPDF_FORMHANDLE, FPDF_ANNOTATION]
    FPDFAnnot_GetOptionCount.restype = c_int

# build_tar/include/fpdf_annot.h: 755
if _libs["pdfium"].has("FPDFAnnot_GetOptionLabel", "cdecl"):
    FPDFAnnot_GetOptionLabel = _libs["pdfium"].get("FPDFAnnot_GetOptionLabel", "cdecl")
    FPDFAnnot_GetOptionLabel.argtypes = [FPDF_FORMHANDLE, FPDF_ANNOTATION, c_int, POINTER(FPDF_WCHAR), c_ulong]
    FPDFAnnot_GetOptionLabel.restype = c_ulong

# build_tar/include/fpdf_annot.h: 773
if _libs["pdfium"].has("FPDFAnnot_IsOptionSelected", "cdecl"):
    FPDFAnnot_IsOptionSelected = _libs["pdfium"].get("FPDFAnnot_IsOptionSelected", "cdecl")
    FPDFAnnot_IsOptionSelected.argtypes = [FPDF_FORMHANDLE, FPDF_ANNOTATION, c_int]
    FPDFAnnot_IsOptionSelected.restype = FPDF_BOOL

# build_tar/include/fpdf_annot.h: 790
if _libs["pdfium"].has("FPDFAnnot_GetFontSize", "cdecl"):
    FPDFAnnot_GetFontSize = _libs["pdfium"].get("FPDFAnnot_GetFontSize", "cdecl")
    FPDFAnnot_GetFontSize.argtypes = [FPDF_FORMHANDLE, FPDF_ANNOTATION, POINTER(c_float)]
    FPDFAnnot_GetFontSize.restype = FPDF_BOOL

# build_tar/include/fpdf_annot.h: 803
if _libs["pdfium"].has("FPDFAnnot_IsChecked", "cdecl"):
    FPDFAnnot_IsChecked = _libs["pdfium"].get("FPDFAnnot_IsChecked", "cdecl")
    FPDFAnnot_IsChecked.argtypes = [FPDF_FORMHANDLE, FPDF_ANNOTATION]
    FPDFAnnot_IsChecked.restype = FPDF_BOOL

# build_tar/include/fpdf_annot.h: 818
if _libs["pdfium"].has("FPDFAnnot_SetFocusableSubtypes", "cdecl"):
    FPDFAnnot_SetFocusableSubtypes = _libs["pdfium"].get("FPDFAnnot_SetFocusableSubtypes", "cdecl")
    FPDFAnnot_SetFocusableSubtypes.argtypes = [FPDF_FORMHANDLE, POINTER(FPDF_ANNOTATION_SUBTYPE), c_size_t]
    FPDFAnnot_SetFocusableSubtypes.restype = FPDF_BOOL

# build_tar/include/fpdf_annot.h: 831
if _libs["pdfium"].has("FPDFAnnot_GetFocusableSubtypesCount", "cdecl"):
    FPDFAnnot_GetFocusableSubtypesCount = _libs["pdfium"].get("FPDFAnnot_GetFocusableSubtypesCount", "cdecl")
    FPDFAnnot_GetFocusableSubtypesCount.argtypes = [FPDF_FORMHANDLE]
    FPDFAnnot_GetFocusableSubtypesCount.restype = c_int

# build_tar/include/fpdf_annot.h: 847
if _libs["pdfium"].has("FPDFAnnot_GetFocusableSubtypes", "cdecl"):
    FPDFAnnot_GetFocusableSubtypes = _libs["pdfium"].get("FPDFAnnot_GetFocusableSubtypes", "cdecl")
    FPDFAnnot_GetFocusableSubtypes.argtypes = [FPDF_FORMHANDLE, POINTER(FPDF_ANNOTATION_SUBTYPE), c_size_t]
    FPDFAnnot_GetFocusableSubtypes.restype = FPDF_BOOL

# build_tar/include/fpdf_annot.h: 858
if _libs["pdfium"].has("FPDFAnnot_GetLink", "cdecl"):
    FPDFAnnot_GetLink = _libs["pdfium"].get("FPDFAnnot_GetLink", "cdecl")
    FPDFAnnot_GetLink.argtypes = [FPDF_ANNOTATION]
    FPDFAnnot_GetLink.restype = FPDF_LINK

# build_tar/include/fpdf_annot.h: 872
if _libs["pdfium"].has("FPDFAnnot_GetFormControlCount", "cdecl"):
    FPDFAnnot_GetFormControlCount = _libs["pdfium"].get("FPDFAnnot_GetFormControlCount", "cdecl")
    FPDFAnnot_GetFormControlCount.argtypes = [FPDF_FORMHANDLE, FPDF_ANNOTATION]
    FPDFAnnot_GetFormControlCount.restype = c_int

# build_tar/include/fpdf_annot.h: 886
if _libs["pdfium"].has("FPDFAnnot_GetFormControlIndex", "cdecl"):
    FPDFAnnot_GetFormControlIndex = _libs["pdfium"].get("FPDFAnnot_GetFormControlIndex", "cdecl")
    FPDFAnnot_GetFormControlIndex.argtypes = [FPDF_FORMHANDLE, FPDF_ANNOTATION]
    FPDFAnnot_GetFormControlIndex.restype = c_int

# build_tar/include/fpdf_annot.h: 903
if _libs["pdfium"].has("FPDFAnnot_GetFormFieldExportValue", "cdecl"):
    FPDFAnnot_GetFormFieldExportValue = _libs["pdfium"].get("FPDFAnnot_GetFormFieldExportValue", "cdecl")
    FPDFAnnot_GetFormFieldExportValue.argtypes = [FPDF_FORMHANDLE, FPDF_ANNOTATION, POINTER(FPDF_WCHAR), c_ulong]
    FPDFAnnot_GetFormFieldExportValue.restype = c_ulong

# build_tar/include/fpdf_annot.h: 915
if _libs["pdfium"].has("FPDFAnnot_SetURI", "cdecl"):
    FPDFAnnot_SetURI = _libs["pdfium"].get("FPDFAnnot_SetURI", "cdecl")
    FPDFAnnot_SetURI.argtypes = [FPDF_ANNOTATION, String]
    FPDFAnnot_SetURI.restype = FPDF_BOOL

# build_tar/include/fpdf_attachment.h: 22
if _libs["pdfium"].has("FPDFDoc_GetAttachmentCount", "cdecl"):
    FPDFDoc_GetAttachmentCount = _libs["pdfium"].get("FPDFDoc_GetAttachmentCount", "cdecl")
    FPDFDoc_GetAttachmentCount.argtypes = [FPDF_DOCUMENT]
    FPDFDoc_GetAttachmentCount.restype = c_int

# build_tar/include/fpdf_attachment.h: 35
if _libs["pdfium"].has("FPDFDoc_AddAttachment", "cdecl"):
    FPDFDoc_AddAttachment = _libs["pdfium"].get("FPDFDoc_AddAttachment", "cdecl")
    FPDFDoc_AddAttachment.argtypes = [FPDF_DOCUMENT, FPDF_WIDESTRING]
    FPDFDoc_AddAttachment.restype = FPDF_ATTACHMENT

# build_tar/include/fpdf_attachment.h: 46
if _libs["pdfium"].has("FPDFDoc_GetAttachment", "cdecl"):
    FPDFDoc_GetAttachment = _libs["pdfium"].get("FPDFDoc_GetAttachment", "cdecl")
    FPDFDoc_GetAttachment.argtypes = [FPDF_DOCUMENT, c_int]
    FPDFDoc_GetAttachment.restype = FPDF_ATTACHMENT

# build_tar/include/fpdf_attachment.h: 59
if _libs["pdfium"].has("FPDFDoc_DeleteAttachment", "cdecl"):
    FPDFDoc_DeleteAttachment = _libs["pdfium"].get("FPDFDoc_DeleteAttachment", "cdecl")
    FPDFDoc_DeleteAttachment.argtypes = [FPDF_DOCUMENT, c_int]
    FPDFDoc_DeleteAttachment.restype = FPDF_BOOL

# build_tar/include/fpdf_attachment.h: 72
if _libs["pdfium"].has("FPDFAttachment_GetName", "cdecl"):
    FPDFAttachment_GetName = _libs["pdfium"].get("FPDFAttachment_GetName", "cdecl")
    FPDFAttachment_GetName.argtypes = [FPDF_ATTACHMENT, POINTER(FPDF_WCHAR), c_ulong]
    FPDFAttachment_GetName.restype = c_ulong

# build_tar/include/fpdf_attachment.h: 84
if _libs["pdfium"].has("FPDFAttachment_HasKey", "cdecl"):
    FPDFAttachment_HasKey = _libs["pdfium"].get("FPDFAttachment_HasKey", "cdecl")
    FPDFAttachment_HasKey.argtypes = [FPDF_ATTACHMENT, FPDF_BYTESTRING]
    FPDFAttachment_HasKey.restype = FPDF_BOOL

# build_tar/include/fpdf_attachment.h: 95
if _libs["pdfium"].has("FPDFAttachment_GetValueType", "cdecl"):
    FPDFAttachment_GetValueType = _libs["pdfium"].get("FPDFAttachment_GetValueType", "cdecl")
    FPDFAttachment_GetValueType.argtypes = [FPDF_ATTACHMENT, FPDF_BYTESTRING]
    FPDFAttachment_GetValueType.restype = FPDF_OBJECT_TYPE

# build_tar/include/fpdf_attachment.h: 108
if _libs["pdfium"].has("FPDFAttachment_SetStringValue", "cdecl"):
    FPDFAttachment_SetStringValue = _libs["pdfium"].get("FPDFAttachment_SetStringValue", "cdecl")
    FPDFAttachment_SetStringValue.argtypes = [FPDF_ATTACHMENT, FPDF_BYTESTRING, FPDF_WIDESTRING]
    FPDFAttachment_SetStringValue.restype = FPDF_BOOL

# build_tar/include/fpdf_attachment.h: 129
if _libs["pdfium"].has("FPDFAttachment_GetStringValue", "cdecl"):
    FPDFAttachment_GetStringValue = _libs["pdfium"].get("FPDFAttachment_GetStringValue", "cdecl")
    FPDFAttachment_GetStringValue.argtypes = [FPDF_ATTACHMENT, FPDF_BYTESTRING, POINTER(FPDF_WCHAR), c_ulong]
    FPDFAttachment_GetStringValue.restype = c_ulong

# build_tar/include/fpdf_attachment.h: 146
if _libs["pdfium"].has("FPDFAttachment_SetFile", "cdecl"):
    FPDFAttachment_SetFile = _libs["pdfium"].get("FPDFAttachment_SetFile", "cdecl")
    FPDFAttachment_SetFile.argtypes = [FPDF_ATTACHMENT, FPDF_DOCUMENT, POINTER(None), c_ulong]
    FPDFAttachment_SetFile.restype = FPDF_BOOL

# build_tar/include/fpdf_attachment.h: 170
if _libs["pdfium"].has("FPDFAttachment_GetFile", "cdecl"):
    FPDFAttachment_GetFile = _libs["pdfium"].get("FPDFAttachment_GetFile", "cdecl")
    FPDFAttachment_GetFile.argtypes = [FPDF_ATTACHMENT, POINTER(None), c_ulong, POINTER(c_ulong)]
    FPDFAttachment_GetFile.restype = FPDF_BOOL

# build_tar/include/fpdf_catalog.h: 28
if _libs["pdfium"].has("FPDFCatalog_IsTagged", "cdecl"):
    FPDFCatalog_IsTagged = _libs["pdfium"].get("FPDFCatalog_IsTagged", "cdecl")
    FPDFCatalog_IsTagged.argtypes = [FPDF_DOCUMENT]
    FPDFCatalog_IsTagged.restype = FPDF_BOOL

# build_tar/include/fpdf_dataavail.h: 33
class struct__FX_FILEAVAIL(Structure):
    pass

struct__FX_FILEAVAIL.__slots__ = [
    'version',
    'IsDataAvail',
]
struct__FX_FILEAVAIL._fields_ = [
    ('version', c_int),
    ('IsDataAvail', CFUNCTYPE(UNCHECKED(FPDF_BOOL), POINTER(struct__FX_FILEAVAIL), c_size_t, c_size_t)),
]

FX_FILEAVAIL = struct__FX_FILEAVAIL# build_tar/include/fpdf_dataavail.h: 52

# build_tar/include/fpdf_dataavail.h: 62
if _libs["pdfium"].has("FPDFAvail_Create", "cdecl"):
    FPDFAvail_Create = _libs["pdfium"].get("FPDFAvail_Create", "cdecl")
    FPDFAvail_Create.argtypes = [POINTER(FX_FILEAVAIL), POINTER(FPDF_FILEACCESS)]
    FPDFAvail_Create.restype = FPDF_AVAIL

# build_tar/include/fpdf_dataavail.h: 68
if _libs["pdfium"].has("FPDFAvail_Destroy", "cdecl"):
    FPDFAvail_Destroy = _libs["pdfium"].get("FPDFAvail_Destroy", "cdecl")
    FPDFAvail_Destroy.argtypes = [FPDF_AVAIL]
    FPDFAvail_Destroy.restype = None

# build_tar/include/fpdf_dataavail.h: 71
class struct__FX_DOWNLOADHINTS(Structure):
    pass

struct__FX_DOWNLOADHINTS.__slots__ = [
    'version',
    'AddSegment',
]
struct__FX_DOWNLOADHINTS._fields_ = [
    ('version', c_int),
    ('AddSegment', CFUNCTYPE(UNCHECKED(None), POINTER(struct__FX_DOWNLOADHINTS), c_size_t, c_size_t)),
]

FX_DOWNLOADHINTS = struct__FX_DOWNLOADHINTS# build_tar/include/fpdf_dataavail.h: 90

# build_tar/include/fpdf_dataavail.h: 109
if _libs["pdfium"].has("FPDFAvail_IsDocAvail", "cdecl"):
    FPDFAvail_IsDocAvail = _libs["pdfium"].get("FPDFAvail_IsDocAvail", "cdecl")
    FPDFAvail_IsDocAvail.argtypes = [FPDF_AVAIL, POINTER(FX_DOWNLOADHINTS)]
    FPDFAvail_IsDocAvail.restype = c_int

# build_tar/include/fpdf_dataavail.h: 124
if _libs["pdfium"].has("FPDFAvail_GetDocument", "cdecl"):
    FPDFAvail_GetDocument = _libs["pdfium"].get("FPDFAvail_GetDocument", "cdecl")
    FPDFAvail_GetDocument.argtypes = [FPDF_AVAIL, FPDF_BYTESTRING]
    FPDFAvail_GetDocument.restype = FPDF_DOCUMENT

# build_tar/include/fpdf_dataavail.h: 135
if _libs["pdfium"].has("FPDFAvail_GetFirstPageNum", "cdecl"):
    FPDFAvail_GetFirstPageNum = _libs["pdfium"].get("FPDFAvail_GetFirstPageNum", "cdecl")
    FPDFAvail_GetFirstPageNum.argtypes = [FPDF_DOCUMENT]
    FPDFAvail_GetFirstPageNum.restype = c_int

# build_tar/include/fpdf_dataavail.h: 157
if _libs["pdfium"].has("FPDFAvail_IsPageAvail", "cdecl"):
    FPDFAvail_IsPageAvail = _libs["pdfium"].get("FPDFAvail_IsPageAvail", "cdecl")
    FPDFAvail_IsPageAvail.argtypes = [FPDF_AVAIL, c_int, POINTER(FX_DOWNLOADHINTS)]
    FPDFAvail_IsPageAvail.restype = c_int

# build_tar/include/fpdf_dataavail.h: 182
if _libs["pdfium"].has("FPDFAvail_IsFormAvail", "cdecl"):
    FPDFAvail_IsFormAvail = _libs["pdfium"].get("FPDFAvail_IsFormAvail", "cdecl")
    FPDFAvail_IsFormAvail.argtypes = [FPDF_AVAIL, POINTER(FX_DOWNLOADHINTS)]
    FPDFAvail_IsFormAvail.restype = c_int

# build_tar/include/fpdf_dataavail.h: 198
if _libs["pdfium"].has("FPDFAvail_IsLinearized", "cdecl"):
    FPDFAvail_IsLinearized = _libs["pdfium"].get("FPDFAvail_IsLinearized", "cdecl")
    FPDFAvail_IsLinearized.argtypes = [FPDF_AVAIL]
    FPDFAvail_IsLinearized.restype = c_int

__time_t = c_long# /usr/include/x86_64-linux-gnu/bits/types.h: 160

# build_tar/include/fpdf_edit.h: 93
class struct_FPDF_IMAGEOBJ_METADATA(Structure):
    pass

struct_FPDF_IMAGEOBJ_METADATA.__slots__ = [
    'width',
    'height',
    'horizontal_dpi',
    'vertical_dpi',
    'bits_per_pixel',
    'colorspace',
    'marked_content_id',
]
struct_FPDF_IMAGEOBJ_METADATA._fields_ = [
    ('width', c_uint),
    ('height', c_uint),
    ('horizontal_dpi', c_float),
    ('vertical_dpi', c_float),
    ('bits_per_pixel', c_uint),
    ('colorspace', c_int),
    ('marked_content_id', c_int),
]

FPDF_IMAGEOBJ_METADATA = struct_FPDF_IMAGEOBJ_METADATA# build_tar/include/fpdf_edit.h: 93

# build_tar/include/fpdf_edit.h: 102
if _libs["pdfium"].has("FPDF_CreateNewDocument", "cdecl"):
    FPDF_CreateNewDocument = _libs["pdfium"].get("FPDF_CreateNewDocument", "cdecl")
    FPDF_CreateNewDocument.argtypes = []
    FPDF_CreateNewDocument.restype = FPDF_DOCUMENT

# build_tar/include/fpdf_edit.h: 117
if _libs["pdfium"].has("FPDFPage_New", "cdecl"):
    FPDFPage_New = _libs["pdfium"].get("FPDFPage_New", "cdecl")
    FPDFPage_New.argtypes = [FPDF_DOCUMENT, c_int, c_double, c_double]
    FPDFPage_New.restype = FPDF_PAGE

# build_tar/include/fpdf_edit.h: 126
if _libs["pdfium"].has("FPDFPage_Delete", "cdecl"):
    FPDFPage_Delete = _libs["pdfium"].get("FPDFPage_Delete", "cdecl")
    FPDFPage_Delete.argtypes = [FPDF_DOCUMENT, c_int]
    FPDFPage_Delete.restype = None

# build_tar/include/fpdf_edit.h: 138
if _libs["pdfium"].has("FPDFPage_GetRotation", "cdecl"):
    FPDFPage_GetRotation = _libs["pdfium"].get("FPDFPage_GetRotation", "cdecl")
    FPDFPage_GetRotation.argtypes = [FPDF_PAGE]
    FPDFPage_GetRotation.restype = c_int

# build_tar/include/fpdf_edit.h: 148
if _libs["pdfium"].has("FPDFPage_SetRotation", "cdecl"):
    FPDFPage_SetRotation = _libs["pdfium"].get("FPDFPage_SetRotation", "cdecl")
    FPDFPage_SetRotation.argtypes = [FPDF_PAGE, c_int]
    FPDFPage_SetRotation.restype = None

# build_tar/include/fpdf_edit.h: 155
if _libs["pdfium"].has("FPDFPage_InsertObject", "cdecl"):
    FPDFPage_InsertObject = _libs["pdfium"].get("FPDFPage_InsertObject", "cdecl")
    FPDFPage_InsertObject.argtypes = [FPDF_PAGE, FPDF_PAGEOBJECT]
    FPDFPage_InsertObject.restype = None

# build_tar/include/fpdf_edit.h: 169
if _libs["pdfium"].has("FPDFPage_RemoveObject", "cdecl"):
    FPDFPage_RemoveObject = _libs["pdfium"].get("FPDFPage_RemoveObject", "cdecl")
    FPDFPage_RemoveObject.argtypes = [FPDF_PAGE, FPDF_PAGEOBJECT]
    FPDFPage_RemoveObject.restype = FPDF_BOOL

# build_tar/include/fpdf_edit.h: 176
if _libs["pdfium"].has("FPDFPage_CountObjects", "cdecl"):
    FPDFPage_CountObjects = _libs["pdfium"].get("FPDFPage_CountObjects", "cdecl")
    FPDFPage_CountObjects.argtypes = [FPDF_PAGE]
    FPDFPage_CountObjects.restype = c_int

# build_tar/include/fpdf_edit.h: 184
if _libs["pdfium"].has("FPDFPage_GetObject", "cdecl"):
    FPDFPage_GetObject = _libs["pdfium"].get("FPDFPage_GetObject", "cdecl")
    FPDFPage_GetObject.argtypes = [FPDF_PAGE, c_int]
    FPDFPage_GetObject.restype = FPDF_PAGEOBJECT

# build_tar/include/fpdf_edit.h: 192
if _libs["pdfium"].has("FPDFPage_HasTransparency", "cdecl"):
    FPDFPage_HasTransparency = _libs["pdfium"].get("FPDFPage_HasTransparency", "cdecl")
    FPDFPage_HasTransparency.argtypes = [FPDF_PAGE]
    FPDFPage_HasTransparency.restype = FPDF_BOOL

# build_tar/include/fpdf_edit.h: 202
if _libs["pdfium"].has("FPDFPage_GenerateContent", "cdecl"):
    FPDFPage_GenerateContent = _libs["pdfium"].get("FPDFPage_GenerateContent", "cdecl")
    FPDFPage_GenerateContent.argtypes = [FPDF_PAGE]
    FPDFPage_GenerateContent.restype = FPDF_BOOL

# build_tar/include/fpdf_edit.h: 211
if _libs["pdfium"].has("FPDFPageObj_Destroy", "cdecl"):
    FPDFPageObj_Destroy = _libs["pdfium"].get("FPDFPageObj_Destroy", "cdecl")
    FPDFPageObj_Destroy.argtypes = [FPDF_PAGEOBJECT]
    FPDFPageObj_Destroy.restype = None

# build_tar/include/fpdf_edit.h: 219
if _libs["pdfium"].has("FPDFPageObj_HasTransparency", "cdecl"):
    FPDFPageObj_HasTransparency = _libs["pdfium"].get("FPDFPageObj_HasTransparency", "cdecl")
    FPDFPageObj_HasTransparency.argtypes = [FPDF_PAGEOBJECT]
    FPDFPageObj_HasTransparency.restype = FPDF_BOOL

# build_tar/include/fpdf_edit.h: 227
if _libs["pdfium"].has("FPDFPageObj_GetType", "cdecl"):
    FPDFPageObj_GetType = _libs["pdfium"].get("FPDFPageObj_GetType", "cdecl")
    FPDFPageObj_GetType.argtypes = [FPDF_PAGEOBJECT]
    FPDFPageObj_GetType.restype = c_int

# build_tar/include/fpdf_edit.h: 244
if _libs["pdfium"].has("FPDFPageObj_Transform", "cdecl"):
    FPDFPageObj_Transform = _libs["pdfium"].get("FPDFPageObj_Transform", "cdecl")
    FPDFPageObj_Transform.argtypes = [FPDF_PAGEOBJECT, c_double, c_double, c_double, c_double, c_double, c_double]
    FPDFPageObj_Transform.restype = None

# build_tar/include/fpdf_edit.h: 265
if _libs["pdfium"].has("FPDFPageObj_GetMatrix", "cdecl"):
    FPDFPageObj_GetMatrix = _libs["pdfium"].get("FPDFPageObj_GetMatrix", "cdecl")
    FPDFPageObj_GetMatrix.argtypes = [FPDF_PAGEOBJECT, POINTER(FS_MATRIX)]
    FPDFPageObj_GetMatrix.restype = FPDF_BOOL

# build_tar/include/fpdf_edit.h: 280
if _libs["pdfium"].has("FPDFPageObj_SetMatrix", "cdecl"):
    FPDFPageObj_SetMatrix = _libs["pdfium"].get("FPDFPageObj_SetMatrix", "cdecl")
    FPDFPageObj_SetMatrix.argtypes = [FPDF_PAGEOBJECT, POINTER(FS_MATRIX)]
    FPDFPageObj_SetMatrix.restype = FPDF_BOOL

# build_tar/include/fpdf_edit.h: 296
if _libs["pdfium"].has("FPDFPage_TransformAnnots", "cdecl"):
    FPDFPage_TransformAnnots = _libs["pdfium"].get("FPDFPage_TransformAnnots", "cdecl")
    FPDFPage_TransformAnnots.argtypes = [FPDF_PAGE, c_double, c_double, c_double, c_double, c_double, c_double]
    FPDFPage_TransformAnnots.restype = None

# build_tar/include/fpdf_edit.h: 310
if _libs["pdfium"].has("FPDFPageObj_NewImageObj", "cdecl"):
    FPDFPageObj_NewImageObj = _libs["pdfium"].get("FPDFPageObj_NewImageObj", "cdecl")
    FPDFPageObj_NewImageObj.argtypes = [FPDF_DOCUMENT]
    FPDFPageObj_NewImageObj.restype = FPDF_PAGEOBJECT

# build_tar/include/fpdf_edit.h: 320
if _libs["pdfium"].has("FPDFPageObj_CountMarks", "cdecl"):
    FPDFPageObj_CountMarks = _libs["pdfium"].get("FPDFPageObj_CountMarks", "cdecl")
    FPDFPageObj_CountMarks.argtypes = [FPDF_PAGEOBJECT]
    FPDFPageObj_CountMarks.restype = c_int

# build_tar/include/fpdf_edit.h: 333
if _libs["pdfium"].has("FPDFPageObj_GetMark", "cdecl"):
    FPDFPageObj_GetMark = _libs["pdfium"].get("FPDFPageObj_GetMark", "cdecl")
    FPDFPageObj_GetMark.argtypes = [FPDF_PAGEOBJECT, c_ulong]
    FPDFPageObj_GetMark.restype = FPDF_PAGEOBJECTMARK

# build_tar/include/fpdf_edit.h: 346
if _libs["pdfium"].has("FPDFPageObj_AddMark", "cdecl"):
    FPDFPageObj_AddMark = _libs["pdfium"].get("FPDFPageObj_AddMark", "cdecl")
    FPDFPageObj_AddMark.argtypes = [FPDF_PAGEOBJECT, FPDF_BYTESTRING]
    FPDFPageObj_AddMark.restype = FPDF_PAGEOBJECTMARK

# build_tar/include/fpdf_edit.h: 357
if _libs["pdfium"].has("FPDFPageObj_RemoveMark", "cdecl"):
    FPDFPageObj_RemoveMark = _libs["pdfium"].get("FPDFPageObj_RemoveMark", "cdecl")
    FPDFPageObj_RemoveMark.argtypes = [FPDF_PAGEOBJECT, FPDF_PAGEOBJECTMARK]
    FPDFPageObj_RemoveMark.restype = FPDF_BOOL

# build_tar/include/fpdf_edit.h: 373
if _libs["pdfium"].has("FPDFPageObjMark_GetName", "cdecl"):
    FPDFPageObjMark_GetName = _libs["pdfium"].get("FPDFPageObjMark_GetName", "cdecl")
    FPDFPageObjMark_GetName.argtypes = [FPDF_PAGEOBJECTMARK, POINTER(None), c_ulong, POINTER(c_ulong)]
    FPDFPageObjMark_GetName.restype = FPDF_BOOL

# build_tar/include/fpdf_edit.h: 386
if _libs["pdfium"].has("FPDFPageObjMark_CountParams", "cdecl"):
    FPDFPageObjMark_CountParams = _libs["pdfium"].get("FPDFPageObjMark_CountParams", "cdecl")
    FPDFPageObjMark_CountParams.argtypes = [FPDF_PAGEOBJECTMARK]
    FPDFPageObjMark_CountParams.restype = c_int

# build_tar/include/fpdf_edit.h: 403
if _libs["pdfium"].has("FPDFPageObjMark_GetParamKey", "cdecl"):
    FPDFPageObjMark_GetParamKey = _libs["pdfium"].get("FPDFPageObjMark_GetParamKey", "cdecl")
    FPDFPageObjMark_GetParamKey.argtypes = [FPDF_PAGEOBJECTMARK, c_ulong, POINTER(None), c_ulong, POINTER(c_ulong)]
    FPDFPageObjMark_GetParamKey.restype = FPDF_BOOL

# build_tar/include/fpdf_edit.h: 417
if _libs["pdfium"].has("FPDFPageObjMark_GetParamValueType", "cdecl"):
    FPDFPageObjMark_GetParamValueType = _libs["pdfium"].get("FPDFPageObjMark_GetParamValueType", "cdecl")
    FPDFPageObjMark_GetParamValueType.argtypes = [FPDF_PAGEOBJECTMARK, FPDF_BYTESTRING]
    FPDFPageObjMark_GetParamValueType.restype = FPDF_OBJECT_TYPE

# build_tar/include/fpdf_edit.h: 432
if _libs["pdfium"].has("FPDFPageObjMark_GetParamIntValue", "cdecl"):
    FPDFPageObjMark_GetParamIntValue = _libs["pdfium"].get("FPDFPageObjMark_GetParamIntValue", "cdecl")
    FPDFPageObjMark_GetParamIntValue.argtypes = [FPDF_PAGEOBJECTMARK, FPDF_BYTESTRING, POINTER(c_int)]
    FPDFPageObjMark_GetParamIntValue.restype = FPDF_BOOL

# build_tar/include/fpdf_edit.h: 452
if _libs["pdfium"].has("FPDFPageObjMark_GetParamStringValue", "cdecl"):
    FPDFPageObjMark_GetParamStringValue = _libs["pdfium"].get("FPDFPageObjMark_GetParamStringValue", "cdecl")
    FPDFPageObjMark_GetParamStringValue.argtypes = [FPDF_PAGEOBJECTMARK, FPDF_BYTESTRING, POINTER(None), c_ulong, POINTER(c_ulong)]
    FPDFPageObjMark_GetParamStringValue.restype = FPDF_BOOL

# build_tar/include/fpdf_edit.h: 473
if _libs["pdfium"].has("FPDFPageObjMark_GetParamBlobValue", "cdecl"):
    FPDFPageObjMark_GetParamBlobValue = _libs["pdfium"].get("FPDFPageObjMark_GetParamBlobValue", "cdecl")
    FPDFPageObjMark_GetParamBlobValue.argtypes = [FPDF_PAGEOBJECTMARK, FPDF_BYTESTRING, POINTER(None), c_ulong, POINTER(c_ulong)]
    FPDFPageObjMark_GetParamBlobValue.restype = FPDF_BOOL

# build_tar/include/fpdf_edit.h: 492
if _libs["pdfium"].has("FPDFPageObjMark_SetIntParam", "cdecl"):
    FPDFPageObjMark_SetIntParam = _libs["pdfium"].get("FPDFPageObjMark_SetIntParam", "cdecl")
    FPDFPageObjMark_SetIntParam.argtypes = [FPDF_DOCUMENT, FPDF_PAGEOBJECT, FPDF_PAGEOBJECTMARK, FPDF_BYTESTRING, c_int]
    FPDFPageObjMark_SetIntParam.restype = FPDF_BOOL

# build_tar/include/fpdf_edit.h: 511
if _libs["pdfium"].has("FPDFPageObjMark_SetStringParam", "cdecl"):
    FPDFPageObjMark_SetStringParam = _libs["pdfium"].get("FPDFPageObjMark_SetStringParam", "cdecl")
    FPDFPageObjMark_SetStringParam.argtypes = [FPDF_DOCUMENT, FPDF_PAGEOBJECT, FPDF_PAGEOBJECTMARK, FPDF_BYTESTRING, FPDF_BYTESTRING]
    FPDFPageObjMark_SetStringParam.restype = FPDF_BOOL

# build_tar/include/fpdf_edit.h: 531
if _libs["pdfium"].has("FPDFPageObjMark_SetBlobParam", "cdecl"):
    FPDFPageObjMark_SetBlobParam = _libs["pdfium"].get("FPDFPageObjMark_SetBlobParam", "cdecl")
    FPDFPageObjMark_SetBlobParam.argtypes = [FPDF_DOCUMENT, FPDF_PAGEOBJECT, FPDF_PAGEOBJECTMARK, FPDF_BYTESTRING, POINTER(None), c_ulong]
    FPDFPageObjMark_SetBlobParam.restype = FPDF_BOOL

# build_tar/include/fpdf_edit.h: 547
if _libs["pdfium"].has("FPDFPageObjMark_RemoveParam", "cdecl"):
    FPDFPageObjMark_RemoveParam = _libs["pdfium"].get("FPDFPageObjMark_RemoveParam", "cdecl")
    FPDFPageObjMark_RemoveParam.argtypes = [FPDF_PAGEOBJECT, FPDF_PAGEOBJECTMARK, FPDF_BYTESTRING]
    FPDFPageObjMark_RemoveParam.restype = FPDF_BOOL

# build_tar/include/fpdf_edit.h: 566
if _libs["pdfium"].has("FPDFImageObj_LoadJpegFile", "cdecl"):
    FPDFImageObj_LoadJpegFile = _libs["pdfium"].get("FPDFImageObj_LoadJpegFile", "cdecl")
    FPDFImageObj_LoadJpegFile.argtypes = [POINTER(FPDF_PAGE), c_int, FPDF_PAGEOBJECT, POINTER(FPDF_FILEACCESS)]
    FPDFImageObj_LoadJpegFile.restype = FPDF_BOOL

# build_tar/include/fpdf_edit.h: 588
if _libs["pdfium"].has("FPDFImageObj_LoadJpegFileInline", "cdecl"):
    FPDFImageObj_LoadJpegFileInline = _libs["pdfium"].get("FPDFImageObj_LoadJpegFileInline", "cdecl")
    FPDFImageObj_LoadJpegFileInline.argtypes = [POINTER(FPDF_PAGE), c_int, FPDF_PAGEOBJECT, POINTER(FPDF_FILEACCESS)]
    FPDFImageObj_LoadJpegFileInline.restype = FPDF_BOOL

# build_tar/include/fpdf_edit.h: 612
if _libs["pdfium"].has("FPDFImageObj_SetMatrix", "cdecl"):
    FPDFImageObj_SetMatrix = _libs["pdfium"].get("FPDFImageObj_SetMatrix", "cdecl")
    FPDFImageObj_SetMatrix.argtypes = [FPDF_PAGEOBJECT, c_double, c_double, c_double, c_double, c_double, c_double]
    FPDFImageObj_SetMatrix.restype = FPDF_BOOL

# build_tar/include/fpdf_edit.h: 629
if _libs["pdfium"].has("FPDFImageObj_SetBitmap", "cdecl"):
    FPDFImageObj_SetBitmap = _libs["pdfium"].get("FPDFImageObj_SetBitmap", "cdecl")
    FPDFImageObj_SetBitmap.argtypes = [POINTER(FPDF_PAGE), c_int, FPDF_PAGEOBJECT, FPDF_BITMAP]
    FPDFImageObj_SetBitmap.restype = FPDF_BOOL

# build_tar/include/fpdf_edit.h: 644
if _libs["pdfium"].has("FPDFImageObj_GetBitmap", "cdecl"):
    FPDFImageObj_GetBitmap = _libs["pdfium"].get("FPDFImageObj_GetBitmap", "cdecl")
    FPDFImageObj_GetBitmap.argtypes = [FPDF_PAGEOBJECT]
    FPDFImageObj_GetBitmap.restype = FPDF_BITMAP

# build_tar/include/fpdf_edit.h: 660
if _libs["pdfium"].has("FPDFImageObj_GetRenderedBitmap", "cdecl"):
    FPDFImageObj_GetRenderedBitmap = _libs["pdfium"].get("FPDFImageObj_GetRenderedBitmap", "cdecl")
    FPDFImageObj_GetRenderedBitmap.argtypes = [FPDF_DOCUMENT, FPDF_PAGE, FPDF_PAGEOBJECT]
    FPDFImageObj_GetRenderedBitmap.restype = FPDF_BITMAP

# build_tar/include/fpdf_edit.h: 675
if _libs["pdfium"].has("FPDFImageObj_GetImageDataDecoded", "cdecl"):
    FPDFImageObj_GetImageDataDecoded = _libs["pdfium"].get("FPDFImageObj_GetImageDataDecoded", "cdecl")
    FPDFImageObj_GetImageDataDecoded.argtypes = [FPDF_PAGEOBJECT, POINTER(None), c_ulong]
    FPDFImageObj_GetImageDataDecoded.restype = c_ulong

# build_tar/include/fpdf_edit.h: 689
if _libs["pdfium"].has("FPDFImageObj_GetImageDataRaw", "cdecl"):
    FPDFImageObj_GetImageDataRaw = _libs["pdfium"].get("FPDFImageObj_GetImageDataRaw", "cdecl")
    FPDFImageObj_GetImageDataRaw.argtypes = [FPDF_PAGEOBJECT, POINTER(None), c_ulong]
    FPDFImageObj_GetImageDataRaw.restype = c_ulong

# build_tar/include/fpdf_edit.h: 699
if _libs["pdfium"].has("FPDFImageObj_GetImageFilterCount", "cdecl"):
    FPDFImageObj_GetImageFilterCount = _libs["pdfium"].get("FPDFImageObj_GetImageFilterCount", "cdecl")
    FPDFImageObj_GetImageFilterCount.argtypes = [FPDF_PAGEOBJECT]
    FPDFImageObj_GetImageFilterCount.restype = c_int

# build_tar/include/fpdf_edit.h: 713
if _libs["pdfium"].has("FPDFImageObj_GetImageFilter", "cdecl"):
    FPDFImageObj_GetImageFilter = _libs["pdfium"].get("FPDFImageObj_GetImageFilter", "cdecl")
    FPDFImageObj_GetImageFilter.argtypes = [FPDF_PAGEOBJECT, c_int, POINTER(None), c_ulong]
    FPDFImageObj_GetImageFilter.restype = c_ulong

# build_tar/include/fpdf_edit.h: 730
if _libs["pdfium"].has("FPDFImageObj_GetImageMetadata", "cdecl"):
    FPDFImageObj_GetImageMetadata = _libs["pdfium"].get("FPDFImageObj_GetImageMetadata", "cdecl")
    FPDFImageObj_GetImageMetadata.argtypes = [FPDF_PAGEOBJECT, FPDF_PAGE, POINTER(FPDF_IMAGEOBJ_METADATA)]
    FPDFImageObj_GetImageMetadata.restype = FPDF_BOOL

# build_tar/include/fpdf_edit.h: 740
if _libs["pdfium"].has("FPDFPageObj_CreateNewPath", "cdecl"):
    FPDFPageObj_CreateNewPath = _libs["pdfium"].get("FPDFPageObj_CreateNewPath", "cdecl")
    FPDFPageObj_CreateNewPath.argtypes = [c_float, c_float]
    FPDFPageObj_CreateNewPath.restype = FPDF_PAGEOBJECT

# build_tar/include/fpdf_edit.h: 751
if _libs["pdfium"].has("FPDFPageObj_CreateNewRect", "cdecl"):
    FPDFPageObj_CreateNewRect = _libs["pdfium"].get("FPDFPageObj_CreateNewRect", "cdecl")
    FPDFPageObj_CreateNewRect.argtypes = [c_float, c_float, c_float, c_float]
    FPDFPageObj_CreateNewRect.restype = FPDF_PAGEOBJECT

# build_tar/include/fpdf_edit.h: 766
if _libs["pdfium"].has("FPDFPageObj_GetBounds", "cdecl"):
    FPDFPageObj_GetBounds = _libs["pdfium"].get("FPDFPageObj_GetBounds", "cdecl")
    FPDFPageObj_GetBounds.argtypes = [FPDF_PAGEOBJECT, POINTER(c_float), POINTER(c_float), POINTER(c_float), POINTER(c_float)]
    FPDFPageObj_GetBounds.restype = FPDF_BOOL

# build_tar/include/fpdf_edit.h: 781
if _libs["pdfium"].has("FPDFPageObj_SetBlendMode", "cdecl"):
    FPDFPageObj_SetBlendMode = _libs["pdfium"].get("FPDFPageObj_SetBlendMode", "cdecl")
    FPDFPageObj_SetBlendMode.argtypes = [FPDF_PAGEOBJECT, FPDF_BYTESTRING]
    FPDFPageObj_SetBlendMode.restype = None

# build_tar/include/fpdf_edit.h: 794
if _libs["pdfium"].has("FPDFPageObj_SetStrokeColor", "cdecl"):
    FPDFPageObj_SetStrokeColor = _libs["pdfium"].get("FPDFPageObj_SetStrokeColor", "cdecl")
    FPDFPageObj_SetStrokeColor.argtypes = [FPDF_PAGEOBJECT, c_uint, c_uint, c_uint, c_uint]
    FPDFPageObj_SetStrokeColor.restype = FPDF_BOOL

# build_tar/include/fpdf_edit.h: 810
if _libs["pdfium"].has("FPDFPageObj_GetStrokeColor", "cdecl"):
    FPDFPageObj_GetStrokeColor = _libs["pdfium"].get("FPDFPageObj_GetStrokeColor", "cdecl")
    FPDFPageObj_GetStrokeColor.argtypes = [FPDF_PAGEOBJECT, POINTER(c_uint), POINTER(c_uint), POINTER(c_uint), POINTER(c_uint)]
    FPDFPageObj_GetStrokeColor.restype = FPDF_BOOL

# build_tar/include/fpdf_edit.h: 823
if _libs["pdfium"].has("FPDFPageObj_SetStrokeWidth", "cdecl"):
    FPDFPageObj_SetStrokeWidth = _libs["pdfium"].get("FPDFPageObj_SetStrokeWidth", "cdecl")
    FPDFPageObj_SetStrokeWidth.argtypes = [FPDF_PAGEOBJECT, c_float]
    FPDFPageObj_SetStrokeWidth.restype = FPDF_BOOL

# build_tar/include/fpdf_edit.h: 832
if _libs["pdfium"].has("FPDFPageObj_GetStrokeWidth", "cdecl"):
    FPDFPageObj_GetStrokeWidth = _libs["pdfium"].get("FPDFPageObj_GetStrokeWidth", "cdecl")
    FPDFPageObj_GetStrokeWidth.argtypes = [FPDF_PAGEOBJECT, POINTER(c_float)]
    FPDFPageObj_GetStrokeWidth.restype = FPDF_BOOL

# build_tar/include/fpdf_edit.h: 842
if _libs["pdfium"].has("FPDFPageObj_GetLineJoin", "cdecl"):
    FPDFPageObj_GetLineJoin = _libs["pdfium"].get("FPDFPageObj_GetLineJoin", "cdecl")
    FPDFPageObj_GetLineJoin.argtypes = [FPDF_PAGEOBJECT]
    FPDFPageObj_GetLineJoin.restype = c_int

# build_tar/include/fpdf_edit.h: 852
if _libs["pdfium"].has("FPDFPageObj_SetLineJoin", "cdecl"):
    FPDFPageObj_SetLineJoin = _libs["pdfium"].get("FPDFPageObj_SetLineJoin", "cdecl")
    FPDFPageObj_SetLineJoin.argtypes = [FPDF_PAGEOBJECT, c_int]
    FPDFPageObj_SetLineJoin.restype = FPDF_BOOL

# build_tar/include/fpdf_edit.h: 862
if _libs["pdfium"].has("FPDFPageObj_GetLineCap", "cdecl"):
    FPDFPageObj_GetLineCap = _libs["pdfium"].get("FPDFPageObj_GetLineCap", "cdecl")
    FPDFPageObj_GetLineCap.argtypes = [FPDF_PAGEOBJECT]
    FPDFPageObj_GetLineCap.restype = c_int

# build_tar/include/fpdf_edit.h: 872
if _libs["pdfium"].has("FPDFPageObj_SetLineCap", "cdecl"):
    FPDFPageObj_SetLineCap = _libs["pdfium"].get("FPDFPageObj_SetLineCap", "cdecl")
    FPDFPageObj_SetLineCap.argtypes = [FPDF_PAGEOBJECT, c_int]
    FPDFPageObj_SetLineCap.restype = FPDF_BOOL

# build_tar/include/fpdf_edit.h: 884
if _libs["pdfium"].has("FPDFPageObj_SetFillColor", "cdecl"):
    FPDFPageObj_SetFillColor = _libs["pdfium"].get("FPDFPageObj_SetFillColor", "cdecl")
    FPDFPageObj_SetFillColor.argtypes = [FPDF_PAGEOBJECT, c_uint, c_uint, c_uint, c_uint]
    FPDFPageObj_SetFillColor.restype = FPDF_BOOL

# build_tar/include/fpdf_edit.h: 900
if _libs["pdfium"].has("FPDFPageObj_GetFillColor", "cdecl"):
    FPDFPageObj_GetFillColor = _libs["pdfium"].get("FPDFPageObj_GetFillColor", "cdecl")
    FPDFPageObj_GetFillColor.argtypes = [FPDF_PAGEOBJECT, POINTER(c_uint), POINTER(c_uint), POINTER(c_uint), POINTER(c_uint)]
    FPDFPageObj_GetFillColor.restype = FPDF_BOOL

# build_tar/include/fpdf_edit.h: 914
if _libs["pdfium"].has("FPDFPageObj_GetDashPhase", "cdecl"):
    FPDFPageObj_GetDashPhase = _libs["pdfium"].get("FPDFPageObj_GetDashPhase", "cdecl")
    FPDFPageObj_GetDashPhase.argtypes = [FPDF_PAGEOBJECT, POINTER(c_float)]
    FPDFPageObj_GetDashPhase.restype = FPDF_BOOL

# build_tar/include/fpdf_edit.h: 924
if _libs["pdfium"].has("FPDFPageObj_SetDashPhase", "cdecl"):
    FPDFPageObj_SetDashPhase = _libs["pdfium"].get("FPDFPageObj_SetDashPhase", "cdecl")
    FPDFPageObj_SetDashPhase.argtypes = [FPDF_PAGEOBJECT, c_float]
    FPDFPageObj_SetDashPhase.restype = FPDF_BOOL

# build_tar/include/fpdf_edit.h: 933
if _libs["pdfium"].has("FPDFPageObj_GetDashCount", "cdecl"):
    FPDFPageObj_GetDashCount = _libs["pdfium"].get("FPDFPageObj_GetDashCount", "cdecl")
    FPDFPageObj_GetDashCount.argtypes = [FPDF_PAGEOBJECT]
    FPDFPageObj_GetDashCount.restype = c_int

# build_tar/include/fpdf_edit.h: 944
if _libs["pdfium"].has("FPDFPageObj_GetDashArray", "cdecl"):
    FPDFPageObj_GetDashArray = _libs["pdfium"].get("FPDFPageObj_GetDashArray", "cdecl")
    FPDFPageObj_GetDashArray.argtypes = [FPDF_PAGEOBJECT, POINTER(c_float), c_size_t]
    FPDFPageObj_GetDashArray.restype = FPDF_BOOL

# build_tar/include/fpdf_edit.h: 958
if _libs["pdfium"].has("FPDFPageObj_SetDashArray", "cdecl"):
    FPDFPageObj_SetDashArray = _libs["pdfium"].get("FPDFPageObj_SetDashArray", "cdecl")
    FPDFPageObj_SetDashArray.argtypes = [FPDF_PAGEOBJECT, POINTER(c_float), c_size_t, c_float]
    FPDFPageObj_SetDashArray.restype = FPDF_BOOL

# build_tar/include/fpdf_edit.h: 971
if _libs["pdfium"].has("FPDFPath_CountSegments", "cdecl"):
    FPDFPath_CountSegments = _libs["pdfium"].get("FPDFPath_CountSegments", "cdecl")
    FPDFPath_CountSegments.argtypes = [FPDF_PAGEOBJECT]
    FPDFPath_CountSegments.restype = c_int

# build_tar/include/fpdf_edit.h: 980
if _libs["pdfium"].has("FPDFPath_GetPathSegment", "cdecl"):
    FPDFPath_GetPathSegment = _libs["pdfium"].get("FPDFPath_GetPathSegment", "cdecl")
    FPDFPath_GetPathSegment.argtypes = [FPDF_PAGEOBJECT, c_int]
    FPDFPath_GetPathSegment.restype = FPDF_PATHSEGMENT

# build_tar/include/fpdf_edit.h: 990
if _libs["pdfium"].has("FPDFPathSegment_GetPoint", "cdecl"):
    FPDFPathSegment_GetPoint = _libs["pdfium"].get("FPDFPathSegment_GetPoint", "cdecl")
    FPDFPathSegment_GetPoint.argtypes = [FPDF_PATHSEGMENT, POINTER(c_float), POINTER(c_float)]
    FPDFPathSegment_GetPoint.restype = FPDF_BOOL

# build_tar/include/fpdf_edit.h: 998
if _libs["pdfium"].has("FPDFPathSegment_GetType", "cdecl"):
    FPDFPathSegment_GetType = _libs["pdfium"].get("FPDFPathSegment_GetType", "cdecl")
    FPDFPathSegment_GetType.argtypes = [FPDF_PATHSEGMENT]
    FPDFPathSegment_GetType.restype = c_int

# build_tar/include/fpdf_edit.h: 1006
if _libs["pdfium"].has("FPDFPathSegment_GetClose", "cdecl"):
    FPDFPathSegment_GetClose = _libs["pdfium"].get("FPDFPathSegment_GetClose", "cdecl")
    FPDFPathSegment_GetClose.argtypes = [FPDF_PATHSEGMENT]
    FPDFPathSegment_GetClose.restype = FPDF_BOOL

# build_tar/include/fpdf_edit.h: 1018
if _libs["pdfium"].has("FPDFPath_MoveTo", "cdecl"):
    FPDFPath_MoveTo = _libs["pdfium"].get("FPDFPath_MoveTo", "cdecl")
    FPDFPath_MoveTo.argtypes = [FPDF_PAGEOBJECT, c_float, c_float]
    FPDFPath_MoveTo.restype = FPDF_BOOL

# build_tar/include/fpdf_edit.h: 1031
if _libs["pdfium"].has("FPDFPath_LineTo", "cdecl"):
    FPDFPath_LineTo = _libs["pdfium"].get("FPDFPath_LineTo", "cdecl")
    FPDFPath_LineTo.argtypes = [FPDF_PAGEOBJECT, c_float, c_float]
    FPDFPath_LineTo.restype = FPDF_BOOL

# build_tar/include/fpdf_edit.h: 1046
if _libs["pdfium"].has("FPDFPath_BezierTo", "cdecl"):
    FPDFPath_BezierTo = _libs["pdfium"].get("FPDFPath_BezierTo", "cdecl")
    FPDFPath_BezierTo.argtypes = [FPDF_PAGEOBJECT, c_float, c_float, c_float, c_float, c_float, c_float]
    FPDFPath_BezierTo.restype = FPDF_BOOL

# build_tar/include/fpdf_edit.h: 1062
if _libs["pdfium"].has("FPDFPath_Close", "cdecl"):
    FPDFPath_Close = _libs["pdfium"].get("FPDFPath_Close", "cdecl")
    FPDFPath_Close.argtypes = [FPDF_PAGEOBJECT]
    FPDFPath_Close.restype = FPDF_BOOL

# build_tar/include/fpdf_edit.h: 1071
if _libs["pdfium"].has("FPDFPath_SetDrawMode", "cdecl"):
    FPDFPath_SetDrawMode = _libs["pdfium"].get("FPDFPath_SetDrawMode", "cdecl")
    FPDFPath_SetDrawMode.argtypes = [FPDF_PAGEOBJECT, c_int, FPDF_BOOL]
    FPDFPath_SetDrawMode.restype = FPDF_BOOL

# build_tar/include/fpdf_edit.h: 1082
if _libs["pdfium"].has("FPDFPath_GetDrawMode", "cdecl"):
    FPDFPath_GetDrawMode = _libs["pdfium"].get("FPDFPath_GetDrawMode", "cdecl")
    FPDFPath_GetDrawMode.argtypes = [FPDF_PAGEOBJECT, POINTER(c_int), POINTER(FPDF_BOOL)]
    FPDFPath_GetDrawMode.restype = FPDF_BOOL

# build_tar/include/fpdf_edit.h: 1094
if _libs["pdfium"].has("FPDFPageObj_NewTextObj", "cdecl"):
    FPDFPageObj_NewTextObj = _libs["pdfium"].get("FPDFPageObj_NewTextObj", "cdecl")
    FPDFPageObj_NewTextObj.argtypes = [FPDF_DOCUMENT, FPDF_BYTESTRING, c_float]
    FPDFPageObj_NewTextObj.restype = FPDF_PAGEOBJECT

# build_tar/include/fpdf_edit.h: 1105
if _libs["pdfium"].has("FPDFText_SetText", "cdecl"):
    FPDFText_SetText = _libs["pdfium"].get("FPDFText_SetText", "cdecl")
    FPDFText_SetText.argtypes = [FPDF_PAGEOBJECT, FPDF_WIDESTRING]
    FPDFText_SetText.restype = FPDF_BOOL

# build_tar/include/fpdf_edit.h: 1117
if _libs["pdfium"].has("FPDFText_SetCharcodes", "cdecl"):
    FPDFText_SetCharcodes = _libs["pdfium"].get("FPDFText_SetCharcodes", "cdecl")
    FPDFText_SetCharcodes.argtypes = [FPDF_PAGEOBJECT, POINTER(c_uint32), c_size_t]
    FPDFText_SetCharcodes.restype = FPDF_BOOL

# build_tar/include/fpdf_edit.h: 1134
if _libs["pdfium"].has("FPDFText_LoadFont", "cdecl"):
    FPDFText_LoadFont = _libs["pdfium"].get("FPDFText_LoadFont", "cdecl")
    FPDFText_LoadFont.argtypes = [FPDF_DOCUMENT, POINTER(c_uint8), c_uint32, c_int, FPDF_BOOL]
    FPDFText_LoadFont.restype = FPDF_FONT

# build_tar/include/fpdf_edit.h: 1152
if _libs["pdfium"].has("FPDFText_LoadStandardFont", "cdecl"):
    FPDFText_LoadStandardFont = _libs["pdfium"].get("FPDFText_LoadStandardFont", "cdecl")
    FPDFText_LoadStandardFont.argtypes = [FPDF_DOCUMENT, FPDF_BYTESTRING]
    FPDFText_LoadStandardFont.restype = FPDF_FONT

# build_tar/include/fpdf_edit.h: 1162
if _libs["pdfium"].has("FPDFTextObj_GetFontSize", "cdecl"):
    FPDFTextObj_GetFontSize = _libs["pdfium"].get("FPDFTextObj_GetFontSize", "cdecl")
    FPDFTextObj_GetFontSize.argtypes = [FPDF_PAGEOBJECT, POINTER(c_float)]
    FPDFTextObj_GetFontSize.restype = FPDF_BOOL

# build_tar/include/fpdf_edit.h: 1167
if _libs["pdfium"].has("FPDFFont_Close", "cdecl"):
    FPDFFont_Close = _libs["pdfium"].get("FPDFFont_Close", "cdecl")
    FPDFFont_Close.argtypes = [FPDF_FONT]
    FPDFFont_Close.restype = None

# build_tar/include/fpdf_edit.h: 1177
if _libs["pdfium"].has("FPDFPageObj_CreateTextObj", "cdecl"):
    FPDFPageObj_CreateTextObj = _libs["pdfium"].get("FPDFPageObj_CreateTextObj", "cdecl")
    FPDFPageObj_CreateTextObj.argtypes = [FPDF_DOCUMENT, FPDF_FONT, c_float]
    FPDFPageObj_CreateTextObj.restype = FPDF_PAGEOBJECT

# build_tar/include/fpdf_edit.h: 1188
if _libs["pdfium"].has("FPDFTextObj_GetTextRenderMode", "cdecl"):
    FPDFTextObj_GetTextRenderMode = _libs["pdfium"].get("FPDFTextObj_GetTextRenderMode", "cdecl")
    FPDFTextObj_GetTextRenderMode.argtypes = [FPDF_PAGEOBJECT]
    FPDFTextObj_GetTextRenderMode.restype = FPDF_TEXT_RENDERMODE

# build_tar/include/fpdf_edit.h: 1199
if _libs["pdfium"].has("FPDFTextObj_SetTextRenderMode", "cdecl"):
    FPDFTextObj_SetTextRenderMode = _libs["pdfium"].get("FPDFTextObj_SetTextRenderMode", "cdecl")
    FPDFTextObj_SetTextRenderMode.argtypes = [FPDF_PAGEOBJECT, FPDF_TEXT_RENDERMODE]
    FPDFTextObj_SetTextRenderMode.restype = FPDF_BOOL

# build_tar/include/fpdf_edit.h: 1216
if _libs["pdfium"].has("FPDFTextObj_GetText", "cdecl"):
    FPDFTextObj_GetText = _libs["pdfium"].get("FPDFTextObj_GetText", "cdecl")
    FPDFTextObj_GetText.argtypes = [FPDF_PAGEOBJECT, FPDF_TEXTPAGE, POINTER(FPDF_WCHAR), c_ulong]
    FPDFTextObj_GetText.restype = c_ulong

# build_tar/include/fpdf_edit.h: 1227
if _libs["pdfium"].has("FPDFTextObj_GetFont", "cdecl"):
    FPDFTextObj_GetFont = _libs["pdfium"].get("FPDFTextObj_GetFont", "cdecl")
    FPDFTextObj_GetFont.argtypes = [FPDF_PAGEOBJECT]
    FPDFTextObj_GetFont.restype = FPDF_FONT

# build_tar/include/fpdf_edit.h: 1243
if _libs["pdfium"].has("FPDFFont_GetFontName", "cdecl"):
    FPDFFont_GetFontName = _libs["pdfium"].get("FPDFFont_GetFontName", "cdecl")
    FPDFFont_GetFontName.argtypes = [FPDF_FONT, String, c_ulong]
    FPDFFont_GetFontName.restype = c_ulong

# build_tar/include/fpdf_edit.h: 1252
if _libs["pdfium"].has("FPDFFont_GetFlags", "cdecl"):
    FPDFFont_GetFlags = _libs["pdfium"].get("FPDFFont_GetFlags", "cdecl")
    FPDFFont_GetFlags.argtypes = [FPDF_FONT]
    FPDFFont_GetFlags.restype = c_int

# build_tar/include/fpdf_edit.h: 1261
if _libs["pdfium"].has("FPDFFont_GetWeight", "cdecl"):
    FPDFFont_GetWeight = _libs["pdfium"].get("FPDFFont_GetWeight", "cdecl")
    FPDFFont_GetWeight.argtypes = [FPDF_FONT]
    FPDFFont_GetWeight.restype = c_int

# build_tar/include/fpdf_edit.h: 1273
if _libs["pdfium"].has("FPDFFont_GetItalicAngle", "cdecl"):
    FPDFFont_GetItalicAngle = _libs["pdfium"].get("FPDFFont_GetItalicAngle", "cdecl")
    FPDFFont_GetItalicAngle.argtypes = [FPDF_FONT, POINTER(c_int)]
    FPDFFont_GetItalicAngle.restype = FPDF_BOOL

# build_tar/include/fpdf_edit.h: 1287
if _libs["pdfium"].has("FPDFFont_GetAscent", "cdecl"):
    FPDFFont_GetAscent = _libs["pdfium"].get("FPDFFont_GetAscent", "cdecl")
    FPDFFont_GetAscent.argtypes = [FPDF_FONT, c_float, POINTER(c_float)]
    FPDFFont_GetAscent.restype = FPDF_BOOL

# build_tar/include/fpdf_edit.h: 1302
if _libs["pdfium"].has("FPDFFont_GetDescent", "cdecl"):
    FPDFFont_GetDescent = _libs["pdfium"].get("FPDFFont_GetDescent", "cdecl")
    FPDFFont_GetDescent.argtypes = [FPDF_FONT, c_float, POINTER(c_float)]
    FPDFFont_GetDescent.restype = FPDF_BOOL

# build_tar/include/fpdf_edit.h: 1318
if _libs["pdfium"].has("FPDFFont_GetGlyphWidth", "cdecl"):
    FPDFFont_GetGlyphWidth = _libs["pdfium"].get("FPDFFont_GetGlyphWidth", "cdecl")
    FPDFFont_GetGlyphWidth.argtypes = [FPDF_FONT, c_uint32, c_float, POINTER(c_float)]
    FPDFFont_GetGlyphWidth.restype = FPDF_BOOL

# build_tar/include/fpdf_edit.h: 1331
if _libs["pdfium"].has("FPDFFont_GetGlyphPath", "cdecl"):
    FPDFFont_GetGlyphPath = _libs["pdfium"].get("FPDFFont_GetGlyphPath", "cdecl")
    FPDFFont_GetGlyphPath.argtypes = [FPDF_FONT, c_uint32, c_float]
    FPDFFont_GetGlyphPath.restype = FPDF_GLYPHPATH

# build_tar/include/fpdf_edit.h: 1342
if _libs["pdfium"].has("FPDFGlyphPath_CountGlyphSegments", "cdecl"):
    FPDFGlyphPath_CountGlyphSegments = _libs["pdfium"].get("FPDFGlyphPath_CountGlyphSegments", "cdecl")
    FPDFGlyphPath_CountGlyphSegments.argtypes = [FPDF_GLYPHPATH]
    FPDFGlyphPath_CountGlyphSegments.restype = c_int

# build_tar/include/fpdf_edit.h: 1352
if _libs["pdfium"].has("FPDFGlyphPath_GetGlyphPathSegment", "cdecl"):
    FPDFGlyphPath_GetGlyphPathSegment = _libs["pdfium"].get("FPDFGlyphPath_GetGlyphPathSegment", "cdecl")
    FPDFGlyphPath_GetGlyphPathSegment.argtypes = [FPDF_GLYPHPATH, c_int]
    FPDFGlyphPath_GetGlyphPathSegment.restype = FPDF_PATHSEGMENT

# build_tar/include/fpdf_edit.h: 1360
if _libs["pdfium"].has("FPDFFormObj_CountObjects", "cdecl"):
    FPDFFormObj_CountObjects = _libs["pdfium"].get("FPDFFormObj_CountObjects", "cdecl")
    FPDFFormObj_CountObjects.argtypes = [FPDF_PAGEOBJECT]
    FPDFFormObj_CountObjects.restype = c_int

# build_tar/include/fpdf_edit.h: 1369
if _libs["pdfium"].has("FPDFFormObj_GetObject", "cdecl"):
    FPDFFormObj_GetObject = _libs["pdfium"].get("FPDFFormObj_GetObject", "cdecl")
    FPDFFormObj_GetObject.argtypes = [FPDF_PAGEOBJECT, c_ulong]
    FPDFFormObj_GetObject.restype = FPDF_PAGEOBJECT

time_t = __time_t# /usr/include/x86_64-linux-gnu/bits/types/time_t.h: 7

# /usr/include/x86_64-linux-gnu/bits/types/struct_tm.h: 7
class struct_tm(Structure):
    pass

struct_tm.__slots__ = [
    'tm_sec',
    'tm_min',
    'tm_hour',
    'tm_mday',
    'tm_mon',
    'tm_year',
    'tm_wday',
    'tm_yday',
    'tm_isdst',
    'tm_gmtoff',
    'tm_zone',
]
struct_tm._fields_ = [
    ('tm_sec', c_int),
    ('tm_min', c_int),
    ('tm_hour', c_int),
    ('tm_mday', c_int),
    ('tm_mon', c_int),
    ('tm_year', c_int),
    ('tm_wday', c_int),
    ('tm_yday', c_int),
    ('tm_isdst', c_int),
    ('tm_gmtoff', c_long),
    ('tm_zone', String),
]

# build_tar/include/fpdf_ext.h: 51
class struct__UNSUPPORT_INFO(Structure):
    pass

struct__UNSUPPORT_INFO.__slots__ = [
    'version',
    'FSDK_UnSupport_Handler',
]
struct__UNSUPPORT_INFO._fields_ = [
    ('version', c_int),
    ('FSDK_UnSupport_Handler', CFUNCTYPE(UNCHECKED(None), POINTER(struct__UNSUPPORT_INFO), c_int)),
]

UNSUPPORT_INFO = struct__UNSUPPORT_INFO# build_tar/include/fpdf_ext.h: 62

# build_tar/include/fpdf_ext.h: 70
if _libs["pdfium"].has("FSDK_SetUnSpObjProcessHandler", "cdecl"):
    FSDK_SetUnSpObjProcessHandler = _libs["pdfium"].get("FSDK_SetUnSpObjProcessHandler", "cdecl")
    FSDK_SetUnSpObjProcessHandler.argtypes = [POINTER(UNSUPPORT_INFO)]
    FSDK_SetUnSpObjProcessHandler.restype = FPDF_BOOL

# build_tar/include/fpdf_ext.h: 79
if _libs["pdfium"].has("FSDK_SetTimeFunction", "cdecl"):
    FSDK_SetTimeFunction = _libs["pdfium"].get("FSDK_SetTimeFunction", "cdecl")
    FSDK_SetTimeFunction.argtypes = [CFUNCTYPE(UNCHECKED(time_t), )]
    FSDK_SetTimeFunction.restype = None

# build_tar/include/fpdf_ext.h: 89
if _libs["pdfium"].has("FSDK_SetLocaltimeFunction", "cdecl"):
    FSDK_SetLocaltimeFunction = _libs["pdfium"].get("FSDK_SetLocaltimeFunction", "cdecl")
    FSDK_SetLocaltimeFunction.argtypes = [CFUNCTYPE(UNCHECKED(POINTER(struct_tm)), POINTER(time_t))]
    FSDK_SetLocaltimeFunction.restype = None

# build_tar/include/fpdf_ext.h: 113
if _libs["pdfium"].has("FPDFDoc_GetPageMode", "cdecl"):
    FPDFDoc_GetPageMode = _libs["pdfium"].get("FPDFDoc_GetPageMode", "cdecl")
    FPDFDoc_GetPageMode.argtypes = [FPDF_DOCUMENT]
    FPDFDoc_GetPageMode.restype = c_int

# build_tar/include/fpdf_flatten.h: 38
if _libs["pdfium"].has("FPDFPage_Flatten", "cdecl"):
    FPDFPage_Flatten = _libs["pdfium"].get("FPDFPage_Flatten", "cdecl")
    FPDFPage_Flatten.argtypes = [FPDF_PAGE, c_int]
    FPDFPage_Flatten.restype = c_int

enum_anon_6 = c_int# build_tar/include/fpdf_fwlevent.h: 28

FWL_EVENTFLAG_ShiftKey = (1 << 0)# build_tar/include/fpdf_fwlevent.h: 28

FWL_EVENTFLAG_ControlKey = (1 << 1)# build_tar/include/fpdf_fwlevent.h: 28

FWL_EVENTFLAG_AltKey = (1 << 2)# build_tar/include/fpdf_fwlevent.h: 28

FWL_EVENTFLAG_MetaKey = (1 << 3)# build_tar/include/fpdf_fwlevent.h: 28

FWL_EVENTFLAG_KeyPad = (1 << 4)# build_tar/include/fpdf_fwlevent.h: 28

FWL_EVENTFLAG_AutoRepeat = (1 << 5)# build_tar/include/fpdf_fwlevent.h: 28

FWL_EVENTFLAG_LeftButtonDown = (1 << 6)# build_tar/include/fpdf_fwlevent.h: 28

FWL_EVENTFLAG_MiddleButtonDown = (1 << 7)# build_tar/include/fpdf_fwlevent.h: 28

FWL_EVENTFLAG_RightButtonDown = (1 << 8)# build_tar/include/fpdf_fwlevent.h: 28

FWL_EVENTFLAG = enum_anon_6# build_tar/include/fpdf_fwlevent.h: 28

enum_anon_7 = c_int# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_Back = 0x08# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_Tab = 0x09# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_NewLine = 0x0A# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_Clear = 0x0C# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_Return = 0x0D# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_Shift = 0x10# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_Control = 0x11# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_Menu = 0x12# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_Pause = 0x13# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_Capital = 0x14# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_Kana = 0x15# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_Hangul = 0x15# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_Junja = 0x17# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_Final = 0x18# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_Hanja = 0x19# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_Kanji = 0x19# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_Escape = 0x1B# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_Convert = 0x1C# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_NonConvert = 0x1D# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_Accept = 0x1E# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_ModeChange = 0x1F# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_Space = 0x20# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_Prior = 0x21# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_Next = 0x22# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_End = 0x23# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_Home = 0x24# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_Left = 0x25# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_Up = 0x26# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_Right = 0x27# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_Down = 0x28# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_Select = 0x29# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_Print = 0x2A# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_Execute = 0x2B# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_Snapshot = 0x2C# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_Insert = 0x2D# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_Delete = 0x2E# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_Help = 0x2F# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_0 = 0x30# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_1 = 0x31# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_2 = 0x32# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_3 = 0x33# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_4 = 0x34# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_5 = 0x35# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_6 = 0x36# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_7 = 0x37# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_8 = 0x38# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_9 = 0x39# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_A = 0x41# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_B = 0x42# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_C = 0x43# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_D = 0x44# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_E = 0x45# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_F = 0x46# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_G = 0x47# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_H = 0x48# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_I = 0x49# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_J = 0x4A# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_K = 0x4B# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_L = 0x4C# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_M = 0x4D# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_N = 0x4E# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_O = 0x4F# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_P = 0x50# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_Q = 0x51# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_R = 0x52# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_S = 0x53# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_T = 0x54# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_U = 0x55# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_V = 0x56# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_W = 0x57# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_X = 0x58# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_Y = 0x59# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_Z = 0x5A# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_LWin = 0x5B# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_Command = 0x5B# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_RWin = 0x5C# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_Apps = 0x5D# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_Sleep = 0x5F# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_NumPad0 = 0x60# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_NumPad1 = 0x61# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_NumPad2 = 0x62# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_NumPad3 = 0x63# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_NumPad4 = 0x64# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_NumPad5 = 0x65# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_NumPad6 = 0x66# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_NumPad7 = 0x67# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_NumPad8 = 0x68# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_NumPad9 = 0x69# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_Multiply = 0x6A# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_Add = 0x6B# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_Separator = 0x6C# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_Subtract = 0x6D# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_Decimal = 0x6E# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_Divide = 0x6F# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_F1 = 0x70# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_F2 = 0x71# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_F3 = 0x72# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_F4 = 0x73# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_F5 = 0x74# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_F6 = 0x75# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_F7 = 0x76# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_F8 = 0x77# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_F9 = 0x78# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_F10 = 0x79# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_F11 = 0x7A# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_F12 = 0x7B# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_F13 = 0x7C# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_F14 = 0x7D# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_F15 = 0x7E# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_F16 = 0x7F# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_F17 = 0x80# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_F18 = 0x81# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_F19 = 0x82# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_F20 = 0x83# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_F21 = 0x84# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_F22 = 0x85# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_F23 = 0x86# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_F24 = 0x87# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_NunLock = 0x90# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_Scroll = 0x91# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_LShift = 0xA0# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_RShift = 0xA1# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_LControl = 0xA2# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_RControl = 0xA3# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_LMenu = 0xA4# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_RMenu = 0xA5# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_BROWSER_Back = 0xA6# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_BROWSER_Forward = 0xA7# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_BROWSER_Refresh = 0xA8# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_BROWSER_Stop = 0xA9# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_BROWSER_Search = 0xAA# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_BROWSER_Favorites = 0xAB# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_BROWSER_Home = 0xAC# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_VOLUME_Mute = 0xAD# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_VOLUME_Down = 0xAE# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_VOLUME_Up = 0xAF# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_MEDIA_NEXT_Track = 0xB0# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_MEDIA_PREV_Track = 0xB1# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_MEDIA_Stop = 0xB2# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_MEDIA_PLAY_Pause = 0xB3# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_MEDIA_LAUNCH_Mail = 0xB4# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_MEDIA_LAUNCH_MEDIA_Select = 0xB5# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_MEDIA_LAUNCH_APP1 = 0xB6# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_MEDIA_LAUNCH_APP2 = 0xB7# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_OEM_1 = 0xBA# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_OEM_Plus = 0xBB# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_OEM_Comma = 0xBC# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_OEM_Minus = 0xBD# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_OEM_Period = 0xBE# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_OEM_2 = 0xBF# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_OEM_3 = 0xC0# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_OEM_4 = 0xDB# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_OEM_5 = 0xDC# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_OEM_6 = 0xDD# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_OEM_7 = 0xDE# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_OEM_8 = 0xDF# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_OEM_102 = 0xE2# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_ProcessKey = 0xE5# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_Packet = 0xE7# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_Attn = 0xF6# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_Crsel = 0xF7# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_Exsel = 0xF8# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_Ereof = 0xF9# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_Play = 0xFA# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_Zoom = 0xFB# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_NoName = 0xFC# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_PA1 = 0xFD# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_OEM_Clear = 0xFE# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEY_Unknown = 0# build_tar/include/fpdf_fwlevent.h: 201

FWL_VKEYCODE = enum_anon_7# build_tar/include/fpdf_fwlevent.h: 201

# build_tar/include/fpdf_javascript.h: 22
if _libs["pdfium"].has("FPDFDoc_GetJavaScriptActionCount", "cdecl"):
    FPDFDoc_GetJavaScriptActionCount = _libs["pdfium"].get("FPDFDoc_GetJavaScriptActionCount", "cdecl")
    FPDFDoc_GetJavaScriptActionCount.argtypes = [FPDF_DOCUMENT]
    FPDFDoc_GetJavaScriptActionCount.restype = c_int

# build_tar/include/fpdf_javascript.h: 34
if _libs["pdfium"].has("FPDFDoc_GetJavaScriptAction", "cdecl"):
    FPDFDoc_GetJavaScriptAction = _libs["pdfium"].get("FPDFDoc_GetJavaScriptAction", "cdecl")
    FPDFDoc_GetJavaScriptAction.argtypes = [FPDF_DOCUMENT, c_int]
    FPDFDoc_GetJavaScriptAction.restype = FPDF_JAVASCRIPT_ACTION

# build_tar/include/fpdf_javascript.h: 41
if _libs["pdfium"].has("FPDFDoc_CloseJavaScriptAction", "cdecl"):
    FPDFDoc_CloseJavaScriptAction = _libs["pdfium"].get("FPDFDoc_CloseJavaScriptAction", "cdecl")
    FPDFDoc_CloseJavaScriptAction.argtypes = [FPDF_JAVASCRIPT_ACTION]
    FPDFDoc_CloseJavaScriptAction.restype = None

# build_tar/include/fpdf_javascript.h: 54
if _libs["pdfium"].has("FPDFJavaScriptAction_GetName", "cdecl"):
    FPDFJavaScriptAction_GetName = _libs["pdfium"].get("FPDFJavaScriptAction_GetName", "cdecl")
    FPDFJavaScriptAction_GetName.argtypes = [FPDF_JAVASCRIPT_ACTION, POINTER(FPDF_WCHAR), c_ulong]
    FPDFJavaScriptAction_GetName.restype = c_ulong

# build_tar/include/fpdf_javascript.h: 69
if _libs["pdfium"].has("FPDFJavaScriptAction_GetScript", "cdecl"):
    FPDFJavaScriptAction_GetScript = _libs["pdfium"].get("FPDFJavaScriptAction_GetScript", "cdecl")
    FPDFJavaScriptAction_GetScript.argtypes = [FPDF_JAVASCRIPT_ACTION, POINTER(FPDF_WCHAR), c_ulong]
    FPDFJavaScriptAction_GetScript.restype = c_ulong

# build_tar/include/fpdf_ppo.h: 32
if _libs["pdfium"].has("FPDF_ImportPagesByIndex", "cdecl"):
    FPDF_ImportPagesByIndex = _libs["pdfium"].get("FPDF_ImportPagesByIndex", "cdecl")
    FPDF_ImportPagesByIndex.argtypes = [FPDF_DOCUMENT, FPDF_DOCUMENT, POINTER(c_int), c_ulong, c_int]
    FPDF_ImportPagesByIndex.restype = FPDF_BOOL

# build_tar/include/fpdf_ppo.h: 49
if _libs["pdfium"].has("FPDF_ImportPages", "cdecl"):
    FPDF_ImportPages = _libs["pdfium"].get("FPDF_ImportPages", "cdecl")
    FPDF_ImportPages.argtypes = [FPDF_DOCUMENT, FPDF_DOCUMENT, FPDF_BYTESTRING, c_int]
    FPDF_ImportPages.restype = FPDF_BOOL

# build_tar/include/fpdf_ppo.h: 72
if _libs["pdfium"].has("FPDF_ImportNPagesToOne", "cdecl"):
    FPDF_ImportNPagesToOne = _libs["pdfium"].get("FPDF_ImportNPagesToOne", "cdecl")
    FPDF_ImportNPagesToOne.argtypes = [FPDF_DOCUMENT, c_float, c_float, c_size_t, c_size_t]
    FPDF_ImportNPagesToOne.restype = FPDF_DOCUMENT

# build_tar/include/fpdf_ppo.h: 85
if _libs["pdfium"].has("FPDF_NewXObjectFromPage", "cdecl"):
    FPDF_NewXObjectFromPage = _libs["pdfium"].get("FPDF_NewXObjectFromPage", "cdecl")
    FPDF_NewXObjectFromPage.argtypes = [FPDF_DOCUMENT, FPDF_DOCUMENT, c_int]
    FPDF_NewXObjectFromPage.restype = FPDF_XOBJECT

# build_tar/include/fpdf_ppo.h: 92
if _libs["pdfium"].has("FPDF_CloseXObject", "cdecl"):
    FPDF_CloseXObject = _libs["pdfium"].get("FPDF_CloseXObject", "cdecl")
    FPDF_CloseXObject.argtypes = [FPDF_XOBJECT]
    FPDF_CloseXObject.restype = None

# build_tar/include/fpdf_ppo.h: 100
if _libs["pdfium"].has("FPDF_NewFormObjectFromXObject", "cdecl"):
    FPDF_NewFormObjectFromXObject = _libs["pdfium"].get("FPDF_NewFormObjectFromXObject", "cdecl")
    FPDF_NewFormObjectFromXObject.argtypes = [FPDF_XOBJECT]
    FPDF_NewFormObjectFromXObject.restype = FPDF_PAGEOBJECT

# build_tar/include/fpdf_ppo.h: 109
if _libs["pdfium"].has("FPDF_CopyViewerPreferences", "cdecl"):
    FPDF_CopyViewerPreferences = _libs["pdfium"].get("FPDF_CopyViewerPreferences", "cdecl")
    FPDF_CopyViewerPreferences.argtypes = [FPDF_DOCUMENT, FPDF_DOCUMENT]
    FPDF_CopyViewerPreferences.restype = FPDF_BOOL

# build_tar/include/fpdf_progressive.h: 25
class struct__IFSDK_PAUSE(Structure):
    pass

struct__IFSDK_PAUSE.__slots__ = [
    'version',
    'NeedToPauseNow',
    'user',
]
struct__IFSDK_PAUSE._fields_ = [
    ('version', c_int),
    ('NeedToPauseNow', CFUNCTYPE(UNCHECKED(FPDF_BOOL), POINTER(struct__IFSDK_PAUSE))),
    ('user', POINTER(None)),
]

IFSDK_PAUSE = struct__IFSDK_PAUSE# build_tar/include/fpdf_progressive.h: 47

# build_tar/include/fpdf_progressive.h: 83
if _libs["pdfium"].has("FPDF_RenderPageBitmapWithColorScheme_Start", "cdecl"):
    FPDF_RenderPageBitmapWithColorScheme_Start = _libs["pdfium"].get("FPDF_RenderPageBitmapWithColorScheme_Start", "cdecl")
    FPDF_RenderPageBitmapWithColorScheme_Start.argtypes = [FPDF_BITMAP, FPDF_PAGE, c_int, c_int, c_int, c_int, c_int, c_int, POINTER(FPDF_COLORSCHEME), POINTER(IFSDK_PAUSE)]
    FPDF_RenderPageBitmapWithColorScheme_Start.restype = c_int

# build_tar/include/fpdf_progressive.h: 121
if _libs["pdfium"].has("FPDF_RenderPageBitmap_Start", "cdecl"):
    FPDF_RenderPageBitmap_Start = _libs["pdfium"].get("FPDF_RenderPageBitmap_Start", "cdecl")
    FPDF_RenderPageBitmap_Start.argtypes = [FPDF_BITMAP, FPDF_PAGE, c_int, c_int, c_int, c_int, c_int, c_int, POINTER(IFSDK_PAUSE)]
    FPDF_RenderPageBitmap_Start.restype = c_int

# build_tar/include/fpdf_progressive.h: 142
if _libs["pdfium"].has("FPDF_RenderPage_Continue", "cdecl"):
    FPDF_RenderPage_Continue = _libs["pdfium"].get("FPDF_RenderPage_Continue", "cdecl")
    FPDF_RenderPage_Continue.argtypes = [FPDF_PAGE, POINTER(IFSDK_PAUSE)]
    FPDF_RenderPage_Continue.restype = c_int

# build_tar/include/fpdf_progressive.h: 153
if _libs["pdfium"].has("FPDF_RenderPage_Close", "cdecl"):
    FPDF_RenderPage_Close = _libs["pdfium"].get("FPDF_RenderPage_Close", "cdecl")
    FPDF_RenderPage_Close.argtypes = [FPDF_PAGE]
    FPDF_RenderPage_Close.restype = None

# build_tar/include/fpdf_save.h: 19
class struct_FPDF_FILEWRITE_(Structure):
    pass

struct_FPDF_FILEWRITE_.__slots__ = [
    'version',
    'WriteBlock',
]
struct_FPDF_FILEWRITE_._fields_ = [
    ('version', c_int),
    ('WriteBlock', CFUNCTYPE(UNCHECKED(c_int), POINTER(struct_FPDF_FILEWRITE_), POINTER(None), c_ulong)),
]

FPDF_FILEWRITE = struct_FPDF_FILEWRITE_# build_tar/include/fpdf_save.h: 42

# build_tar/include/fpdf_save.h: 59
if _libs["pdfium"].has("FPDF_SaveAsCopy", "cdecl"):
    FPDF_SaveAsCopy = _libs["pdfium"].get("FPDF_SaveAsCopy", "cdecl")
    FPDF_SaveAsCopy.argtypes = [FPDF_DOCUMENT, POINTER(FPDF_FILEWRITE), FPDF_DWORD]
    FPDF_SaveAsCopy.restype = FPDF_BOOL

# build_tar/include/fpdf_save.h: 76
if _libs["pdfium"].has("FPDF_SaveWithVersion", "cdecl"):
    FPDF_SaveWithVersion = _libs["pdfium"].get("FPDF_SaveWithVersion", "cdecl")
    FPDF_SaveWithVersion.argtypes = [FPDF_DOCUMENT, POINTER(FPDF_FILEWRITE), FPDF_DWORD, c_int]
    FPDF_SaveWithVersion.restype = FPDF_BOOL

# build_tar/include/fpdf_searchex.h: 24
if _libs["pdfium"].has("FPDFText_GetCharIndexFromTextIndex", "cdecl"):
    FPDFText_GetCharIndexFromTextIndex = _libs["pdfium"].get("FPDFText_GetCharIndexFromTextIndex", "cdecl")
    FPDFText_GetCharIndexFromTextIndex.argtypes = [FPDF_TEXTPAGE, c_int]
    FPDFText_GetCharIndexFromTextIndex.restype = c_int

# build_tar/include/fpdf_searchex.h: 33
if _libs["pdfium"].has("FPDFText_GetTextIndexFromCharIndex", "cdecl"):
    FPDFText_GetTextIndexFromCharIndex = _libs["pdfium"].get("FPDFText_GetTextIndexFromCharIndex", "cdecl")
    FPDFText_GetTextIndexFromCharIndex.argtypes = [FPDF_TEXTPAGE, c_int]
    FPDFText_GetTextIndexFromCharIndex.restype = c_int

# build_tar/include/fpdf_signature.h: 22
if _libs["pdfium"].has("FPDF_GetSignatureCount", "cdecl"):
    FPDF_GetSignatureCount = _libs["pdfium"].get("FPDF_GetSignatureCount", "cdecl")
    FPDF_GetSignatureCount.argtypes = [FPDF_DOCUMENT]
    FPDF_GetSignatureCount.restype = c_int

# build_tar/include/fpdf_signature.h: 35
if _libs["pdfium"].has("FPDF_GetSignatureObject", "cdecl"):
    FPDF_GetSignatureObject = _libs["pdfium"].get("FPDF_GetSignatureObject", "cdecl")
    FPDF_GetSignatureObject.argtypes = [FPDF_DOCUMENT, c_int]
    FPDF_GetSignatureObject.restype = FPDF_SIGNATURE

# build_tar/include/fpdf_signature.h: 52
if _libs["pdfium"].has("FPDFSignatureObj_GetContents", "cdecl"):
    FPDFSignatureObj_GetContents = _libs["pdfium"].get("FPDFSignatureObj_GetContents", "cdecl")
    FPDFSignatureObj_GetContents.argtypes = [FPDF_SIGNATURE, POINTER(None), c_ulong]
    FPDFSignatureObj_GetContents.restype = c_ulong

# build_tar/include/fpdf_signature.h: 74
if _libs["pdfium"].has("FPDFSignatureObj_GetByteRange", "cdecl"):
    FPDFSignatureObj_GetByteRange = _libs["pdfium"].get("FPDFSignatureObj_GetByteRange", "cdecl")
    FPDFSignatureObj_GetByteRange.argtypes = [FPDF_SIGNATURE, POINTER(c_int), c_ulong]
    FPDFSignatureObj_GetByteRange.restype = c_ulong

# build_tar/include/fpdf_signature.h: 93
if _libs["pdfium"].has("FPDFSignatureObj_GetSubFilter", "cdecl"):
    FPDFSignatureObj_GetSubFilter = _libs["pdfium"].get("FPDFSignatureObj_GetSubFilter", "cdecl")
    FPDFSignatureObj_GetSubFilter.argtypes = [FPDF_SIGNATURE, String, c_ulong]
    FPDFSignatureObj_GetSubFilter.restype = c_ulong

# build_tar/include/fpdf_signature.h: 112
if _libs["pdfium"].has("FPDFSignatureObj_GetReason", "cdecl"):
    FPDFSignatureObj_GetReason = _libs["pdfium"].get("FPDFSignatureObj_GetReason", "cdecl")
    FPDFSignatureObj_GetReason.argtypes = [FPDF_SIGNATURE, POINTER(None), c_ulong]
    FPDFSignatureObj_GetReason.restype = c_ulong

# build_tar/include/fpdf_signature.h: 136
if _libs["pdfium"].has("FPDFSignatureObj_GetTime", "cdecl"):
    FPDFSignatureObj_GetTime = _libs["pdfium"].get("FPDFSignatureObj_GetTime", "cdecl")
    FPDFSignatureObj_GetTime.argtypes = [FPDF_SIGNATURE, String, c_ulong]
    FPDFSignatureObj_GetTime.restype = c_ulong

# build_tar/include/fpdf_signature.h: 149
if _libs["pdfium"].has("FPDFSignatureObj_GetDocMDPPermission", "cdecl"):
    FPDFSignatureObj_GetDocMDPPermission = _libs["pdfium"].get("FPDFSignatureObj_GetDocMDPPermission", "cdecl")
    FPDFSignatureObj_GetDocMDPPermission.argtypes = [FPDF_SIGNATURE]
    FPDFSignatureObj_GetDocMDPPermission.restype = c_uint

# build_tar/include/fpdf_structtree.h: 25
if _libs["pdfium"].has("FPDF_StructTree_GetForPage", "cdecl"):
    FPDF_StructTree_GetForPage = _libs["pdfium"].get("FPDF_StructTree_GetForPage", "cdecl")
    FPDF_StructTree_GetForPage.argtypes = [FPDF_PAGE]
    FPDF_StructTree_GetForPage.restype = FPDF_STRUCTTREE

# build_tar/include/fpdf_structtree.h: 35
if _libs["pdfium"].has("FPDF_StructTree_Close", "cdecl"):
    FPDF_StructTree_Close = _libs["pdfium"].get("FPDF_StructTree_Close", "cdecl")
    FPDF_StructTree_Close.argtypes = [FPDF_STRUCTTREE]
    FPDF_StructTree_Close.restype = None

# build_tar/include/fpdf_structtree.h: 45
if _libs["pdfium"].has("FPDF_StructTree_CountChildren", "cdecl"):
    FPDF_StructTree_CountChildren = _libs["pdfium"].get("FPDF_StructTree_CountChildren", "cdecl")
    FPDF_StructTree_CountChildren.argtypes = [FPDF_STRUCTTREE]
    FPDF_StructTree_CountChildren.restype = c_int

# build_tar/include/fpdf_structtree.h: 56
if _libs["pdfium"].has("FPDF_StructTree_GetChildAtIndex", "cdecl"):
    FPDF_StructTree_GetChildAtIndex = _libs["pdfium"].get("FPDF_StructTree_GetChildAtIndex", "cdecl")
    FPDF_StructTree_GetChildAtIndex.argtypes = [FPDF_STRUCTTREE, c_int]
    FPDF_StructTree_GetChildAtIndex.restype = FPDF_STRUCTELEMENT

# build_tar/include/fpdf_structtree.h: 74
if _libs["pdfium"].has("FPDF_StructElement_GetAltText", "cdecl"):
    FPDF_StructElement_GetAltText = _libs["pdfium"].get("FPDF_StructElement_GetAltText", "cdecl")
    FPDF_StructElement_GetAltText.argtypes = [FPDF_STRUCTELEMENT, POINTER(None), c_ulong]
    FPDF_StructElement_GetAltText.restype = c_ulong

# build_tar/include/fpdf_structtree.h: 95
if _libs["pdfium"].has("FPDF_StructElement_GetID", "cdecl"):
    FPDF_StructElement_GetID = _libs["pdfium"].get("FPDF_StructElement_GetID", "cdecl")
    FPDF_StructElement_GetID.argtypes = [FPDF_STRUCTELEMENT, POINTER(None), c_ulong]
    FPDF_StructElement_GetID.restype = c_ulong

# build_tar/include/fpdf_structtree.h: 116
if _libs["pdfium"].has("FPDF_StructElement_GetLang", "cdecl"):
    FPDF_StructElement_GetLang = _libs["pdfium"].get("FPDF_StructElement_GetLang", "cdecl")
    FPDF_StructElement_GetLang.argtypes = [FPDF_STRUCTELEMENT, POINTER(None), c_ulong]
    FPDF_StructElement_GetLang.restype = c_ulong

# build_tar/include/fpdf_structtree.h: 138
if _libs["pdfium"].has("FPDF_StructElement_GetStringAttribute", "cdecl"):
    FPDF_StructElement_GetStringAttribute = _libs["pdfium"].get("FPDF_StructElement_GetStringAttribute", "cdecl")
    FPDF_StructElement_GetStringAttribute.argtypes = [FPDF_STRUCTELEMENT, FPDF_BYTESTRING, POINTER(None), c_ulong]
    FPDF_StructElement_GetStringAttribute.restype = c_ulong

# build_tar/include/fpdf_structtree.h: 151
if _libs["pdfium"].has("FPDF_StructElement_GetMarkedContentID", "cdecl"):
    FPDF_StructElement_GetMarkedContentID = _libs["pdfium"].get("FPDF_StructElement_GetMarkedContentID", "cdecl")
    FPDF_StructElement_GetMarkedContentID.argtypes = [FPDF_STRUCTELEMENT]
    FPDF_StructElement_GetMarkedContentID.restype = c_int

# build_tar/include/fpdf_structtree.h: 169
if _libs["pdfium"].has("FPDF_StructElement_GetType", "cdecl"):
    FPDF_StructElement_GetType = _libs["pdfium"].get("FPDF_StructElement_GetType", "cdecl")
    FPDF_StructElement_GetType.argtypes = [FPDF_STRUCTELEMENT, POINTER(None), c_ulong]
    FPDF_StructElement_GetType.restype = c_ulong

# build_tar/include/fpdf_structtree.h: 189
if _libs["pdfium"].has("FPDF_StructElement_GetTitle", "cdecl"):
    FPDF_StructElement_GetTitle = _libs["pdfium"].get("FPDF_StructElement_GetTitle", "cdecl")
    FPDF_StructElement_GetTitle.argtypes = [FPDF_STRUCTELEMENT, POINTER(None), c_ulong]
    FPDF_StructElement_GetTitle.restype = c_ulong

# build_tar/include/fpdf_structtree.h: 200
if _libs["pdfium"].has("FPDF_StructElement_CountChildren", "cdecl"):
    FPDF_StructElement_CountChildren = _libs["pdfium"].get("FPDF_StructElement_CountChildren", "cdecl")
    FPDF_StructElement_CountChildren.argtypes = [FPDF_STRUCTELEMENT]
    FPDF_StructElement_CountChildren.restype = c_int

# build_tar/include/fpdf_structtree.h: 213
if _libs["pdfium"].has("FPDF_StructElement_GetChildAtIndex", "cdecl"):
    FPDF_StructElement_GetChildAtIndex = _libs["pdfium"].get("FPDF_StructElement_GetChildAtIndex", "cdecl")
    FPDF_StructElement_GetChildAtIndex.argtypes = [FPDF_STRUCTELEMENT, c_int]
    FPDF_StructElement_GetChildAtIndex.restype = FPDF_STRUCTELEMENT

# build_tar/include/fpdf_sysfontinfo.h: 44
class struct__FPDF_SYSFONTINFO(Structure):
    pass

struct__FPDF_SYSFONTINFO.__slots__ = [
    'version',
    'Release',
    'EnumFonts',
    'MapFont',
    'GetFont',
    'GetFontData',
    'GetFaceName',
    'GetFontCharset',
    'DeleteFont',
]
struct__FPDF_SYSFONTINFO._fields_ = [
    ('version', c_int),
    ('Release', CFUNCTYPE(UNCHECKED(None), POINTER(struct__FPDF_SYSFONTINFO))),
    ('EnumFonts', CFUNCTYPE(UNCHECKED(None), POINTER(struct__FPDF_SYSFONTINFO), POINTER(None))),
    ('MapFont', CFUNCTYPE(UNCHECKED(POINTER(c_ubyte)), POINTER(struct__FPDF_SYSFONTINFO), c_int, FPDF_BOOL, c_int, c_int, String, POINTER(FPDF_BOOL))),
    ('GetFont', CFUNCTYPE(UNCHECKED(POINTER(c_ubyte)), POINTER(struct__FPDF_SYSFONTINFO), String)),
    ('GetFontData', CFUNCTYPE(UNCHECKED(c_ulong), POINTER(struct__FPDF_SYSFONTINFO), POINTER(None), c_uint, POINTER(c_ubyte), c_ulong)),
    ('GetFaceName', CFUNCTYPE(UNCHECKED(c_ulong), POINTER(struct__FPDF_SYSFONTINFO), POINTER(None), String, c_ulong)),
    ('GetFontCharset', CFUNCTYPE(UNCHECKED(c_int), POINTER(struct__FPDF_SYSFONTINFO), POINTER(None))),
    ('DeleteFont', CFUNCTYPE(UNCHECKED(None), POINTER(struct__FPDF_SYSFONTINFO), POINTER(None))),
]

FPDF_SYSFONTINFO = struct__FPDF_SYSFONTINFO# build_tar/include/fpdf_sysfontinfo.h: 223

# build_tar/include/fpdf_sysfontinfo.h: 232
class struct_FPDF_CharsetFontMap_(Structure):
    pass

struct_FPDF_CharsetFontMap_.__slots__ = [
    'charset',
    'fontname',
]
struct_FPDF_CharsetFontMap_._fields_ = [
    ('charset', c_int),
    ('fontname', String),
]

FPDF_CharsetFontMap = struct_FPDF_CharsetFontMap_# build_tar/include/fpdf_sysfontinfo.h: 232

# build_tar/include/fpdf_sysfontinfo.h: 244
if _libs["pdfium"].has("FPDF_GetDefaultTTFMap", "cdecl"):
    FPDF_GetDefaultTTFMap = _libs["pdfium"].get("FPDF_GetDefaultTTFMap", "cdecl")
    FPDF_GetDefaultTTFMap.argtypes = []
    FPDF_GetDefaultTTFMap.restype = POINTER(FPDF_CharsetFontMap)

# build_tar/include/fpdf_sysfontinfo.h: 259
if _libs["pdfium"].has("FPDF_AddInstalledFont", "cdecl"):
    FPDF_AddInstalledFont = _libs["pdfium"].get("FPDF_AddInstalledFont", "cdecl")
    FPDF_AddInstalledFont.argtypes = [POINTER(None), String, c_int]
    FPDF_AddInstalledFont.restype = None

# build_tar/include/fpdf_sysfontinfo.h: 276
if _libs["pdfium"].has("FPDF_SetSystemFontInfo", "cdecl"):
    FPDF_SetSystemFontInfo = _libs["pdfium"].get("FPDF_SetSystemFontInfo", "cdecl")
    FPDF_SetSystemFontInfo.argtypes = [POINTER(FPDF_SYSFONTINFO)]
    FPDF_SetSystemFontInfo.restype = None

# build_tar/include/fpdf_sysfontinfo.h: 293
if _libs["pdfium"].has("FPDF_GetDefaultSystemFontInfo", "cdecl"):
    FPDF_GetDefaultSystemFontInfo = _libs["pdfium"].get("FPDF_GetDefaultSystemFontInfo", "cdecl")
    FPDF_GetDefaultSystemFontInfo.argtypes = []
    FPDF_GetDefaultSystemFontInfo.restype = POINTER(FPDF_SYSFONTINFO)

# build_tar/include/fpdf_sysfontinfo.h: 307
if _libs["pdfium"].has("FPDF_FreeDefaultSystemFontInfo", "cdecl"):
    FPDF_FreeDefaultSystemFontInfo = _libs["pdfium"].get("FPDF_FreeDefaultSystemFontInfo", "cdecl")
    FPDF_FreeDefaultSystemFontInfo.argtypes = [POINTER(FPDF_SYSFONTINFO)]
    FPDF_FreeDefaultSystemFontInfo.restype = None

# build_tar/include/fpdf_text.h: 31
if _libs["pdfium"].has("FPDFText_LoadPage", "cdecl"):
    FPDFText_LoadPage = _libs["pdfium"].get("FPDFText_LoadPage", "cdecl")
    FPDFText_LoadPage.argtypes = [FPDF_PAGE]
    FPDFText_LoadPage.restype = FPDF_TEXTPAGE

# build_tar/include/fpdf_text.h: 42
if _libs["pdfium"].has("FPDFText_ClosePage", "cdecl"):
    FPDFText_ClosePage = _libs["pdfium"].get("FPDFText_ClosePage", "cdecl")
    FPDFText_ClosePage.argtypes = [FPDF_TEXTPAGE]
    FPDFText_ClosePage.restype = None

# build_tar/include/fpdf_text.h: 60
if _libs["pdfium"].has("FPDFText_CountChars", "cdecl"):
    FPDFText_CountChars = _libs["pdfium"].get("FPDFText_CountChars", "cdecl")
    FPDFText_CountChars.argtypes = [FPDF_TEXTPAGE]
    FPDFText_CountChars.restype = c_int

# build_tar/include/fpdf_text.h: 75
if _libs["pdfium"].has("FPDFText_GetUnicode", "cdecl"):
    FPDFText_GetUnicode = _libs["pdfium"].get("FPDFText_GetUnicode", "cdecl")
    FPDFText_GetUnicode.argtypes = [FPDF_TEXTPAGE, c_int]
    FPDFText_GetUnicode.restype = c_uint

# build_tar/include/fpdf_text.h: 88
if _libs["pdfium"].has("FPDFText_GetFontSize", "cdecl"):
    FPDFText_GetFontSize = _libs["pdfium"].get("FPDFText_GetFontSize", "cdecl")
    FPDFText_GetFontSize.argtypes = [FPDF_TEXTPAGE, c_int]
    FPDFText_GetFontSize.restype = c_double

# build_tar/include/fpdf_text.h: 111
if _libs["pdfium"].has("FPDFText_GetFontInfo", "cdecl"):
    FPDFText_GetFontInfo = _libs["pdfium"].get("FPDFText_GetFontInfo", "cdecl")
    FPDFText_GetFontInfo.argtypes = [FPDF_TEXTPAGE, c_int, POINTER(None), c_ulong, POINTER(c_int)]
    FPDFText_GetFontInfo.restype = c_ulong

# build_tar/include/fpdf_text.h: 129
if _libs["pdfium"].has("FPDFText_GetFontWeight", "cdecl"):
    FPDFText_GetFontWeight = _libs["pdfium"].get("FPDFText_GetFontWeight", "cdecl")
    FPDFText_GetFontWeight.argtypes = [FPDF_TEXTPAGE, c_int]
    FPDFText_GetFontWeight.restype = c_int

# build_tar/include/fpdf_text.h: 146
if _libs["pdfium"].has("FPDFText_GetTextRenderMode", "cdecl"):
    FPDFText_GetTextRenderMode = _libs["pdfium"].get("FPDFText_GetTextRenderMode", "cdecl")
    FPDFText_GetTextRenderMode.argtypes = [FPDF_TEXTPAGE, c_int]
    FPDFText_GetTextRenderMode.restype = FPDF_TEXT_RENDERMODE

# build_tar/include/fpdf_text.h: 168
if _libs["pdfium"].has("FPDFText_GetFillColor", "cdecl"):
    FPDFText_GetFillColor = _libs["pdfium"].get("FPDFText_GetFillColor", "cdecl")
    FPDFText_GetFillColor.argtypes = [FPDF_TEXTPAGE, c_int, POINTER(c_uint), POINTER(c_uint), POINTER(c_uint), POINTER(c_uint)]
    FPDFText_GetFillColor.restype = FPDF_BOOL

# build_tar/include/fpdf_text.h: 195
if _libs["pdfium"].has("FPDFText_GetStrokeColor", "cdecl"):
    FPDFText_GetStrokeColor = _libs["pdfium"].get("FPDFText_GetStrokeColor", "cdecl")
    FPDFText_GetStrokeColor.argtypes = [FPDF_TEXTPAGE, c_int, POINTER(c_uint), POINTER(c_uint), POINTER(c_uint), POINTER(c_uint)]
    FPDFText_GetStrokeColor.restype = FPDF_BOOL

# build_tar/include/fpdf_text.h: 214
if _libs["pdfium"].has("FPDFText_GetCharAngle", "cdecl"):
    FPDFText_GetCharAngle = _libs["pdfium"].get("FPDFText_GetCharAngle", "cdecl")
    FPDFText_GetCharAngle.argtypes = [FPDF_TEXTPAGE, c_int]
    FPDFText_GetCharAngle.restype = c_float

# build_tar/include/fpdf_text.h: 238
if _libs["pdfium"].has("FPDFText_GetCharBox", "cdecl"):
    FPDFText_GetCharBox = _libs["pdfium"].get("FPDFText_GetCharBox", "cdecl")
    FPDFText_GetCharBox.argtypes = [FPDF_TEXTPAGE, c_int, POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double)]
    FPDFText_GetCharBox.restype = FPDF_BOOL

# build_tar/include/fpdf_text.h: 263
if _libs["pdfium"].has("FPDFText_GetLooseCharBox", "cdecl"):
    FPDFText_GetLooseCharBox = _libs["pdfium"].get("FPDFText_GetLooseCharBox", "cdecl")
    FPDFText_GetLooseCharBox.argtypes = [FPDF_TEXTPAGE, c_int, POINTER(FS_RECTF)]
    FPDFText_GetLooseCharBox.restype = FPDF_BOOL

# build_tar/include/fpdf_text.h: 279
if _libs["pdfium"].has("FPDFText_GetMatrix", "cdecl"):
    FPDFText_GetMatrix = _libs["pdfium"].get("FPDFText_GetMatrix", "cdecl")
    FPDFText_GetMatrix.argtypes = [FPDF_TEXTPAGE, c_int, POINTER(FS_MATRIX)]
    FPDFText_GetMatrix.restype = FPDF_BOOL

# build_tar/include/fpdf_text.h: 299
if _libs["pdfium"].has("FPDFText_GetCharOrigin", "cdecl"):
    FPDFText_GetCharOrigin = _libs["pdfium"].get("FPDFText_GetCharOrigin", "cdecl")
    FPDFText_GetCharOrigin.argtypes = [FPDF_TEXTPAGE, c_int, POINTER(c_double), POINTER(c_double)]
    FPDFText_GetCharOrigin.restype = FPDF_BOOL

# build_tar/include/fpdf_text.h: 322
if _libs["pdfium"].has("FPDFText_GetCharIndexAtPos", "cdecl"):
    FPDFText_GetCharIndexAtPos = _libs["pdfium"].get("FPDFText_GetCharIndexAtPos", "cdecl")
    FPDFText_GetCharIndexAtPos.argtypes = [FPDF_TEXTPAGE, c_double, c_double, c_double, c_double]
    FPDFText_GetCharIndexAtPos.restype = c_int

# build_tar/include/fpdf_text.h: 345
if _libs["pdfium"].has("FPDFText_GetText", "cdecl"):
    FPDFText_GetText = _libs["pdfium"].get("FPDFText_GetText", "cdecl")
    FPDFText_GetText.argtypes = [FPDF_TEXTPAGE, c_int, c_int, POINTER(c_ushort)]
    FPDFText_GetText.restype = c_int

# build_tar/include/fpdf_text.h: 366
if _libs["pdfium"].has("FPDFText_CountRects", "cdecl"):
    FPDFText_CountRects = _libs["pdfium"].get("FPDFText_CountRects", "cdecl")
    FPDFText_CountRects.argtypes = [FPDF_TEXTPAGE, c_int, c_int]
    FPDFText_CountRects.restype = c_int

# build_tar/include/fpdf_text.h: 392
if _libs["pdfium"].has("FPDFText_GetRect", "cdecl"):
    FPDFText_GetRect = _libs["pdfium"].get("FPDFText_GetRect", "cdecl")
    FPDFText_GetRect.argtypes = [FPDF_TEXTPAGE, c_int, POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double)]
    FPDFText_GetRect.restype = FPDF_BOOL

# build_tar/include/fpdf_text.h: 423
if _libs["pdfium"].has("FPDFText_GetBoundedText", "cdecl"):
    FPDFText_GetBoundedText = _libs["pdfium"].get("FPDFText_GetBoundedText", "cdecl")
    FPDFText_GetBoundedText.argtypes = [FPDF_TEXTPAGE, c_double, c_double, c_double, c_double, POINTER(c_ushort), c_int]
    FPDFText_GetBoundedText.restype = c_int

# build_tar/include/fpdf_text.h: 453
if _libs["pdfium"].has("FPDFText_FindStart", "cdecl"):
    FPDFText_FindStart = _libs["pdfium"].get("FPDFText_FindStart", "cdecl")
    FPDFText_FindStart.argtypes = [FPDF_TEXTPAGE, FPDF_WIDESTRING, c_ulong, c_int]
    FPDFText_FindStart.restype = FPDF_SCHHANDLE

# build_tar/include/fpdf_text.h: 466
if _libs["pdfium"].has("FPDFText_FindNext", "cdecl"):
    FPDFText_FindNext = _libs["pdfium"].get("FPDFText_FindNext", "cdecl")
    FPDFText_FindNext.argtypes = [FPDF_SCHHANDLE]
    FPDFText_FindNext.restype = FPDF_BOOL

# build_tar/include/fpdf_text.h: 476
if _libs["pdfium"].has("FPDFText_FindPrev", "cdecl"):
    FPDFText_FindPrev = _libs["pdfium"].get("FPDFText_FindPrev", "cdecl")
    FPDFText_FindPrev.argtypes = [FPDF_SCHHANDLE]
    FPDFText_FindPrev.restype = FPDF_BOOL

# build_tar/include/fpdf_text.h: 486
if _libs["pdfium"].has("FPDFText_GetSchResultIndex", "cdecl"):
    FPDFText_GetSchResultIndex = _libs["pdfium"].get("FPDFText_GetSchResultIndex", "cdecl")
    FPDFText_GetSchResultIndex.argtypes = [FPDF_SCHHANDLE]
    FPDFText_GetSchResultIndex.restype = c_int

# build_tar/include/fpdf_text.h: 496
if _libs["pdfium"].has("FPDFText_GetSchCount", "cdecl"):
    FPDFText_GetSchCount = _libs["pdfium"].get("FPDFText_GetSchCount", "cdecl")
    FPDFText_GetSchCount.argtypes = [FPDF_SCHHANDLE]
    FPDFText_GetSchCount.restype = c_int

# build_tar/include/fpdf_text.h: 506
if _libs["pdfium"].has("FPDFText_FindClose", "cdecl"):
    FPDFText_FindClose = _libs["pdfium"].get("FPDFText_FindClose", "cdecl")
    FPDFText_FindClose.argtypes = [FPDF_SCHHANDLE]
    FPDFText_FindClose.restype = None

# build_tar/include/fpdf_text.h: 528
if _libs["pdfium"].has("FPDFLink_LoadWebLinks", "cdecl"):
    FPDFLink_LoadWebLinks = _libs["pdfium"].get("FPDFLink_LoadWebLinks", "cdecl")
    FPDFLink_LoadWebLinks.argtypes = [FPDF_TEXTPAGE]
    FPDFLink_LoadWebLinks.restype = FPDF_PAGELINK

# build_tar/include/fpdf_text.h: 537
if _libs["pdfium"].has("FPDFLink_CountWebLinks", "cdecl"):
    FPDFLink_CountWebLinks = _libs["pdfium"].get("FPDFLink_CountWebLinks", "cdecl")
    FPDFLink_CountWebLinks.argtypes = [FPDF_PAGELINK]
    FPDFLink_CountWebLinks.restype = c_int

# build_tar/include/fpdf_text.h: 558
if _libs["pdfium"].has("FPDFLink_GetURL", "cdecl"):
    FPDFLink_GetURL = _libs["pdfium"].get("FPDFLink_GetURL", "cdecl")
    FPDFLink_GetURL.argtypes = [FPDF_PAGELINK, c_int, POINTER(c_ushort), c_int]
    FPDFLink_GetURL.restype = c_int

# build_tar/include/fpdf_text.h: 572
if _libs["pdfium"].has("FPDFLink_CountRects", "cdecl"):
    FPDFLink_CountRects = _libs["pdfium"].get("FPDFLink_CountRects", "cdecl")
    FPDFLink_CountRects.argtypes = [FPDF_PAGELINK, c_int]
    FPDFLink_CountRects.restype = c_int

# build_tar/include/fpdf_text.h: 595
if _libs["pdfium"].has("FPDFLink_GetRect", "cdecl"):
    FPDFLink_GetRect = _libs["pdfium"].get("FPDFLink_GetRect", "cdecl")
    FPDFLink_GetRect.argtypes = [FPDF_PAGELINK, c_int, c_int, POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double)]
    FPDFLink_GetRect.restype = FPDF_BOOL

# build_tar/include/fpdf_text.h: 618
if _libs["pdfium"].has("FPDFLink_GetTextRange", "cdecl"):
    FPDFLink_GetTextRange = _libs["pdfium"].get("FPDFLink_GetTextRange", "cdecl")
    FPDFLink_GetTextRange.argtypes = [FPDF_PAGELINK, c_int, POINTER(c_int), POINTER(c_int)]
    FPDFLink_GetTextRange.restype = FPDF_BOOL

# build_tar/include/fpdf_text.h: 630
if _libs["pdfium"].has("FPDFLink_CloseWebLinks", "cdecl"):
    FPDFLink_CloseWebLinks = _libs["pdfium"].get("FPDFLink_CloseWebLinks", "cdecl")
    FPDFLink_CloseWebLinks.argtypes = [FPDF_PAGELINK]
    FPDFLink_CloseWebLinks.restype = None

# build_tar/include/fpdf_thumbnail.h: 28
if _libs["pdfium"].has("FPDFPage_GetDecodedThumbnailData", "cdecl"):
    FPDFPage_GetDecodedThumbnailData = _libs["pdfium"].get("FPDFPage_GetDecodedThumbnailData", "cdecl")
    FPDFPage_GetDecodedThumbnailData.argtypes = [FPDF_PAGE, POINTER(None), c_ulong]
    FPDFPage_GetDecodedThumbnailData.restype = c_ulong

# build_tar/include/fpdf_thumbnail.h: 43
if _libs["pdfium"].has("FPDFPage_GetRawThumbnailData", "cdecl"):
    FPDFPage_GetRawThumbnailData = _libs["pdfium"].get("FPDFPage_GetRawThumbnailData", "cdecl")
    FPDFPage_GetRawThumbnailData.argtypes = [FPDF_PAGE, POINTER(None), c_ulong]
    FPDFPage_GetRawThumbnailData.restype = c_ulong

# build_tar/include/fpdf_thumbnail.h: 53
if _libs["pdfium"].has("FPDFPage_GetThumbnailAsBitmap", "cdecl"):
    FPDFPage_GetThumbnailAsBitmap = _libs["pdfium"].get("FPDFPage_GetThumbnailAsBitmap", "cdecl")
    FPDFPage_GetThumbnailAsBitmap.argtypes = [FPDF_PAGE]
    FPDFPage_GetThumbnailAsBitmap.restype = FPDF_BITMAP

# build_tar/include/fpdf_transformpage.h: 26
if _libs["pdfium"].has("FPDFPage_SetMediaBox", "cdecl"):
    FPDFPage_SetMediaBox = _libs["pdfium"].get("FPDFPage_SetMediaBox", "cdecl")
    FPDFPage_SetMediaBox.argtypes = [FPDF_PAGE, c_float, c_float, c_float, c_float]
    FPDFPage_SetMediaBox.restype = None

# build_tar/include/fpdf_transformpage.h: 41
if _libs["pdfium"].has("FPDFPage_SetCropBox", "cdecl"):
    FPDFPage_SetCropBox = _libs["pdfium"].get("FPDFPage_SetCropBox", "cdecl")
    FPDFPage_SetCropBox.argtypes = [FPDF_PAGE, c_float, c_float, c_float, c_float]
    FPDFPage_SetCropBox.restype = None

# build_tar/include/fpdf_transformpage.h: 56
if _libs["pdfium"].has("FPDFPage_SetBleedBox", "cdecl"):
    FPDFPage_SetBleedBox = _libs["pdfium"].get("FPDFPage_SetBleedBox", "cdecl")
    FPDFPage_SetBleedBox.argtypes = [FPDF_PAGE, c_float, c_float, c_float, c_float]
    FPDFPage_SetBleedBox.restype = None

# build_tar/include/fpdf_transformpage.h: 71
if _libs["pdfium"].has("FPDFPage_SetTrimBox", "cdecl"):
    FPDFPage_SetTrimBox = _libs["pdfium"].get("FPDFPage_SetTrimBox", "cdecl")
    FPDFPage_SetTrimBox.argtypes = [FPDF_PAGE, c_float, c_float, c_float, c_float]
    FPDFPage_SetTrimBox.restype = None

# build_tar/include/fpdf_transformpage.h: 86
if _libs["pdfium"].has("FPDFPage_SetArtBox", "cdecl"):
    FPDFPage_SetArtBox = _libs["pdfium"].get("FPDFPage_SetArtBox", "cdecl")
    FPDFPage_SetArtBox.argtypes = [FPDF_PAGE, c_float, c_float, c_float, c_float]
    FPDFPage_SetArtBox.restype = None

# build_tar/include/fpdf_transformpage.h: 104
if _libs["pdfium"].has("FPDFPage_GetMediaBox", "cdecl"):
    FPDFPage_GetMediaBox = _libs["pdfium"].get("FPDFPage_GetMediaBox", "cdecl")
    FPDFPage_GetMediaBox.argtypes = [FPDF_PAGE, POINTER(c_float), POINTER(c_float), POINTER(c_float), POINTER(c_float)]
    FPDFPage_GetMediaBox.restype = FPDF_BOOL

# build_tar/include/fpdf_transformpage.h: 122
if _libs["pdfium"].has("FPDFPage_GetCropBox", "cdecl"):
    FPDFPage_GetCropBox = _libs["pdfium"].get("FPDFPage_GetCropBox", "cdecl")
    FPDFPage_GetCropBox.argtypes = [FPDF_PAGE, POINTER(c_float), POINTER(c_float), POINTER(c_float), POINTER(c_float)]
    FPDFPage_GetCropBox.restype = FPDF_BOOL

# build_tar/include/fpdf_transformpage.h: 140
if _libs["pdfium"].has("FPDFPage_GetBleedBox", "cdecl"):
    FPDFPage_GetBleedBox = _libs["pdfium"].get("FPDFPage_GetBleedBox", "cdecl")
    FPDFPage_GetBleedBox.argtypes = [FPDF_PAGE, POINTER(c_float), POINTER(c_float), POINTER(c_float), POINTER(c_float)]
    FPDFPage_GetBleedBox.restype = FPDF_BOOL

# build_tar/include/fpdf_transformpage.h: 158
if _libs["pdfium"].has("FPDFPage_GetTrimBox", "cdecl"):
    FPDFPage_GetTrimBox = _libs["pdfium"].get("FPDFPage_GetTrimBox", "cdecl")
    FPDFPage_GetTrimBox.argtypes = [FPDF_PAGE, POINTER(c_float), POINTER(c_float), POINTER(c_float), POINTER(c_float)]
    FPDFPage_GetTrimBox.restype = FPDF_BOOL

# build_tar/include/fpdf_transformpage.h: 176
if _libs["pdfium"].has("FPDFPage_GetArtBox", "cdecl"):
    FPDFPage_GetArtBox = _libs["pdfium"].get("FPDFPage_GetArtBox", "cdecl")
    FPDFPage_GetArtBox.argtypes = [FPDF_PAGE, POINTER(c_float), POINTER(c_float), POINTER(c_float), POINTER(c_float)]
    FPDFPage_GetArtBox.restype = FPDF_BOOL

# build_tar/include/fpdf_transformpage.h: 198
if _libs["pdfium"].has("FPDFPage_TransFormWithClip", "cdecl"):
    FPDFPage_TransFormWithClip = _libs["pdfium"].get("FPDFPage_TransFormWithClip", "cdecl")
    FPDFPage_TransFormWithClip.argtypes = [FPDF_PAGE, POINTER(FS_MATRIX), POINTER(FS_RECTF)]
    FPDFPage_TransFormWithClip.restype = FPDF_BOOL

# build_tar/include/fpdf_transformpage.h: 215
if _libs["pdfium"].has("FPDFPageObj_TransformClipPath", "cdecl"):
    FPDFPageObj_TransformClipPath = _libs["pdfium"].get("FPDFPageObj_TransformClipPath", "cdecl")
    FPDFPageObj_TransformClipPath.argtypes = [FPDF_PAGEOBJECT, c_double, c_double, c_double, c_double, c_double, c_double]
    FPDFPageObj_TransformClipPath.restype = None

# build_tar/include/fpdf_transformpage.h: 233
if _libs["pdfium"].has("FPDFPageObj_GetClipPath", "cdecl"):
    FPDFPageObj_GetClipPath = _libs["pdfium"].get("FPDFPageObj_GetClipPath", "cdecl")
    FPDFPageObj_GetClipPath.argtypes = [FPDF_PAGEOBJECT]
    FPDFPageObj_GetClipPath.restype = FPDF_CLIPPATH

# build_tar/include/fpdf_transformpage.h: 241
if _libs["pdfium"].has("FPDFClipPath_CountPaths", "cdecl"):
    FPDFClipPath_CountPaths = _libs["pdfium"].get("FPDFClipPath_CountPaths", "cdecl")
    FPDFClipPath_CountPaths.argtypes = [FPDF_CLIPPATH]
    FPDFClipPath_CountPaths.restype = c_int

# build_tar/include/fpdf_transformpage.h: 251
if _libs["pdfium"].has("FPDFClipPath_CountPathSegments", "cdecl"):
    FPDFClipPath_CountPathSegments = _libs["pdfium"].get("FPDFClipPath_CountPathSegments", "cdecl")
    FPDFClipPath_CountPathSegments.argtypes = [FPDF_CLIPPATH, c_int]
    FPDFClipPath_CountPathSegments.restype = c_int

# build_tar/include/fpdf_transformpage.h: 264
if _libs["pdfium"].has("FPDFClipPath_GetPathSegment", "cdecl"):
    FPDFClipPath_GetPathSegment = _libs["pdfium"].get("FPDFClipPath_GetPathSegment", "cdecl")
    FPDFClipPath_GetPathSegment.argtypes = [FPDF_CLIPPATH, c_int, c_int]
    FPDFClipPath_GetPathSegment.restype = FPDF_PATHSEGMENT

# build_tar/include/fpdf_transformpage.h: 279
if _libs["pdfium"].has("FPDF_CreateClipPath", "cdecl"):
    FPDF_CreateClipPath = _libs["pdfium"].get("FPDF_CreateClipPath", "cdecl")
    FPDF_CreateClipPath.argtypes = [c_float, c_float, c_float, c_float]
    FPDF_CreateClipPath.restype = FPDF_CLIPPATH

# build_tar/include/fpdf_transformpage.h: 289
if _libs["pdfium"].has("FPDF_DestroyClipPath", "cdecl"):
    FPDF_DestroyClipPath = _libs["pdfium"].get("FPDF_DestroyClipPath", "cdecl")
    FPDF_DestroyClipPath.argtypes = [FPDF_CLIPPATH]
    FPDF_DestroyClipPath.restype = None

# build_tar/include/fpdf_transformpage.h: 301
if _libs["pdfium"].has("FPDFPage_InsertClipPath", "cdecl"):
    FPDFPage_InsertClipPath = _libs["pdfium"].get("FPDFPage_InsertClipPath", "cdecl")
    FPDFPage_InsertClipPath.argtypes = [FPDF_PAGE, FPDF_CLIPPATH]
    FPDFPage_InsertClipPath.restype = None

# build_tar/include/fpdfview.h: 28
try:
    FPDF_OBJECT_UNKNOWN = 0
except:
    pass

# build_tar/include/fpdfview.h: 29
try:
    FPDF_OBJECT_BOOLEAN = 1
except:
    pass

# build_tar/include/fpdfview.h: 30
try:
    FPDF_OBJECT_NUMBER = 2
except:
    pass

# build_tar/include/fpdfview.h: 31
try:
    FPDF_OBJECT_STRING = 3
except:
    pass

# build_tar/include/fpdfview.h: 32
try:
    FPDF_OBJECT_NAME = 4
except:
    pass

# build_tar/include/fpdfview.h: 33
try:
    FPDF_OBJECT_ARRAY = 5
except:
    pass

# build_tar/include/fpdfview.h: 34
try:
    FPDF_OBJECT_DICTIONARY = 6
except:
    pass

# build_tar/include/fpdfview.h: 35
try:
    FPDF_OBJECT_STREAM = 7
except:
    pass

# build_tar/include/fpdfview.h: 36
try:
    FPDF_OBJECT_NULLOBJ = 8
except:
    pass

# build_tar/include/fpdfview.h: 37
try:
    FPDF_OBJECT_REFERENCE = 9
except:
    pass

# build_tar/include/fpdfview.h: 275
try:
    FPDF_POLICY_MACHINETIME_ACCESS = 0
except:
    pass

# build_tar/include/fpdfview.h: 574
try:
    FPDF_ERR_SUCCESS = 0
except:
    pass

# build_tar/include/fpdfview.h: 575
try:
    FPDF_ERR_UNKNOWN = 1
except:
    pass

# build_tar/include/fpdfview.h: 576
try:
    FPDF_ERR_FILE = 2
except:
    pass

# build_tar/include/fpdfview.h: 577
try:
    FPDF_ERR_FORMAT = 3
except:
    pass

# build_tar/include/fpdfview.h: 578
try:
    FPDF_ERR_PASSWORD = 4
except:
    pass

# build_tar/include/fpdfview.h: 579
try:
    FPDF_ERR_SECURITY = 5
except:
    pass

# build_tar/include/fpdfview.h: 580
try:
    FPDF_ERR_PAGE = 6
except:
    pass

# build_tar/include/fpdfview.h: 768
try:
    FPDF_ANNOT = 0x01
except:
    pass

# build_tar/include/fpdfview.h: 771
try:
    FPDF_LCD_TEXT = 0x02
except:
    pass

# build_tar/include/fpdfview.h: 773
try:
    FPDF_NO_NATIVETEXT = 0x04
except:
    pass

# build_tar/include/fpdfview.h: 775
try:
    FPDF_GRAYSCALE = 0x08
except:
    pass

# build_tar/include/fpdfview.h: 777
try:
    FPDF_DEBUG_INFO = 0x80
except:
    pass

# build_tar/include/fpdfview.h: 779
try:
    FPDF_NO_CATCH = 0x100
except:
    pass

# build_tar/include/fpdfview.h: 781
try:
    FPDF_RENDER_LIMITEDIMAGECACHE = 0x200
except:
    pass

# build_tar/include/fpdfview.h: 783
try:
    FPDF_RENDER_FORCEHALFTONE = 0x400
except:
    pass

# build_tar/include/fpdfview.h: 785
try:
    FPDF_PRINTING = 0x800
except:
    pass

# build_tar/include/fpdfview.h: 788
try:
    FPDF_RENDER_NO_SMOOTHTEXT = 0x1000
except:
    pass

# build_tar/include/fpdfview.h: 790
try:
    FPDF_RENDER_NO_SMOOTHIMAGE = 0x2000
except:
    pass

# build_tar/include/fpdfview.h: 792
try:
    FPDF_RENDER_NO_SMOOTHPATH = 0x4000
except:
    pass

# build_tar/include/fpdfview.h: 795
try:
    FPDF_REVERSE_BYTE_ORDER = 0x10
except:
    pass

# build_tar/include/fpdfview.h: 799
try:
    FPDF_CONVERT_FILL_TO_STROKE = 0x20
except:
    pass

# build_tar/include/fpdfview.h: 1049
try:
    FPDFBitmap_Unknown = 0
except:
    pass

# build_tar/include/fpdfview.h: 1051
try:
    FPDFBitmap_Gray = 1
except:
    pass

# build_tar/include/fpdfview.h: 1053
try:
    FPDFBitmap_BGR = 2
except:
    pass

# build_tar/include/fpdfview.h: 1055
try:
    FPDFBitmap_BGRx = 3
except:
    pass

# build_tar/include/fpdfview.h: 1057
try:
    FPDFBitmap_BGRA = 4
except:
    pass

# build_tar/include/fpdf_doc.h: 18
try:
    PDFACTION_UNSUPPORTED = 0
except:
    pass

# build_tar/include/fpdf_doc.h: 20
try:
    PDFACTION_GOTO = 1
except:
    pass

# build_tar/include/fpdf_doc.h: 22
try:
    PDFACTION_REMOTEGOTO = 2
except:
    pass

# build_tar/include/fpdf_doc.h: 24
try:
    PDFACTION_URI = 3
except:
    pass

# build_tar/include/fpdf_doc.h: 26
try:
    PDFACTION_LAUNCH = 4
except:
    pass

# build_tar/include/fpdf_doc.h: 28
try:
    PDFACTION_EMBEDDEDGOTO = 5
except:
    pass

# build_tar/include/fpdf_doc.h: 31
try:
    PDFDEST_VIEW_UNKNOWN_MODE = 0
except:
    pass

# build_tar/include/fpdf_doc.h: 32
try:
    PDFDEST_VIEW_XYZ = 1
except:
    pass

# build_tar/include/fpdf_doc.h: 33
try:
    PDFDEST_VIEW_FIT = 2
except:
    pass

# build_tar/include/fpdf_doc.h: 34
try:
    PDFDEST_VIEW_FITH = 3
except:
    pass

# build_tar/include/fpdf_doc.h: 35
try:
    PDFDEST_VIEW_FITV = 4
except:
    pass

# build_tar/include/fpdf_doc.h: 36
try:
    PDFDEST_VIEW_FITR = 5
except:
    pass

# build_tar/include/fpdf_doc.h: 37
try:
    PDFDEST_VIEW_FITB = 6
except:
    pass

# build_tar/include/fpdf_doc.h: 38
try:
    PDFDEST_VIEW_FITBH = 7
except:
    pass

# build_tar/include/fpdf_doc.h: 39
try:
    PDFDEST_VIEW_FITBV = 8
except:
    pass

# build_tar/include/fpdf_formfill.h: 16
try:
    FORMTYPE_NONE = 0
except:
    pass

# build_tar/include/fpdf_formfill.h: 17
try:
    FORMTYPE_ACRO_FORM = 1
except:
    pass

# build_tar/include/fpdf_formfill.h: 18
try:
    FORMTYPE_XFA_FULL = 2
except:
    pass

# build_tar/include/fpdf_formfill.h: 19
try:
    FORMTYPE_XFA_FOREGROUND = 3
except:
    pass

# build_tar/include/fpdf_formfill.h: 21
try:
    FORMTYPE_COUNT = 4
except:
    pass

# build_tar/include/fpdf_formfill.h: 23
try:
    JSPLATFORM_ALERT_BUTTON_OK = 0
except:
    pass

# build_tar/include/fpdf_formfill.h: 24
try:
    JSPLATFORM_ALERT_BUTTON_OKCANCEL = 1
except:
    pass

# build_tar/include/fpdf_formfill.h: 25
try:
    JSPLATFORM_ALERT_BUTTON_YESNO = 2
except:
    pass

# build_tar/include/fpdf_formfill.h: 26
try:
    JSPLATFORM_ALERT_BUTTON_YESNOCANCEL = 3
except:
    pass

# build_tar/include/fpdf_formfill.h: 27
try:
    JSPLATFORM_ALERT_BUTTON_DEFAULT = JSPLATFORM_ALERT_BUTTON_OK
except:
    pass

# build_tar/include/fpdf_formfill.h: 29
try:
    JSPLATFORM_ALERT_ICON_ERROR = 0
except:
    pass

# build_tar/include/fpdf_formfill.h: 30
try:
    JSPLATFORM_ALERT_ICON_WARNING = 1
except:
    pass

# build_tar/include/fpdf_formfill.h: 31
try:
    JSPLATFORM_ALERT_ICON_QUESTION = 2
except:
    pass

# build_tar/include/fpdf_formfill.h: 32
try:
    JSPLATFORM_ALERT_ICON_STATUS = 3
except:
    pass

# build_tar/include/fpdf_formfill.h: 33
try:
    JSPLATFORM_ALERT_ICON_ASTERISK = 4
except:
    pass

# build_tar/include/fpdf_formfill.h: 34
try:
    JSPLATFORM_ALERT_ICON_DEFAULT = JSPLATFORM_ALERT_ICON_ERROR
except:
    pass

# build_tar/include/fpdf_formfill.h: 36
try:
    JSPLATFORM_ALERT_RETURN_OK = 1
except:
    pass

# build_tar/include/fpdf_formfill.h: 37
try:
    JSPLATFORM_ALERT_RETURN_CANCEL = 2
except:
    pass

# build_tar/include/fpdf_formfill.h: 38
try:
    JSPLATFORM_ALERT_RETURN_NO = 3
except:
    pass

# build_tar/include/fpdf_formfill.h: 39
try:
    JSPLATFORM_ALERT_RETURN_YES = 4
except:
    pass

# build_tar/include/fpdf_formfill.h: 41
try:
    JSPLATFORM_BEEP_ERROR = 0
except:
    pass

# build_tar/include/fpdf_formfill.h: 42
try:
    JSPLATFORM_BEEP_WARNING = 1
except:
    pass

# build_tar/include/fpdf_formfill.h: 43
try:
    JSPLATFORM_BEEP_QUESTION = 2
except:
    pass

# build_tar/include/fpdf_formfill.h: 44
try:
    JSPLATFORM_BEEP_STATUS = 3
except:
    pass

# build_tar/include/fpdf_formfill.h: 45
try:
    JSPLATFORM_BEEP_DEFAULT = 4
except:
    pass

# build_tar/include/fpdf_formfill.h: 324
try:
    FXCT_ARROW = 0
except:
    pass

# build_tar/include/fpdf_formfill.h: 325
try:
    FXCT_NESW = 1
except:
    pass

# build_tar/include/fpdf_formfill.h: 326
try:
    FXCT_NWSE = 2
except:
    pass

# build_tar/include/fpdf_formfill.h: 327
try:
    FXCT_VBEAM = 3
except:
    pass

# build_tar/include/fpdf_formfill.h: 328
try:
    FXCT_HBEAM = 4
except:
    pass

# build_tar/include/fpdf_formfill.h: 329
try:
    FXCT_HAND = 5
except:
    pass

# build_tar/include/fpdf_formfill.h: 1234
try:
    FPDFDOC_AACTION_WC = 0x10
except:
    pass

# build_tar/include/fpdf_formfill.h: 1235
try:
    FPDFDOC_AACTION_WS = 0x11
except:
    pass

# build_tar/include/fpdf_formfill.h: 1236
try:
    FPDFDOC_AACTION_DS = 0x12
except:
    pass

# build_tar/include/fpdf_formfill.h: 1237
try:
    FPDFDOC_AACTION_WP = 0x13
except:
    pass

# build_tar/include/fpdf_formfill.h: 1238
try:
    FPDFDOC_AACTION_DP = 0x14
except:
    pass

# build_tar/include/fpdf_formfill.h: 1261
try:
    FPDFPAGE_AACTION_OPEN = 0
except:
    pass

# build_tar/include/fpdf_formfill.h: 1262
try:
    FPDFPAGE_AACTION_CLOSE = 1
except:
    pass

# build_tar/include/fpdf_formfill.h: 1703
try:
    FPDF_FORMFIELD_UNKNOWN = 0
except:
    pass

# build_tar/include/fpdf_formfill.h: 1704
try:
    FPDF_FORMFIELD_PUSHBUTTON = 1
except:
    pass

# build_tar/include/fpdf_formfill.h: 1705
try:
    FPDF_FORMFIELD_CHECKBOX = 2
except:
    pass

# build_tar/include/fpdf_formfill.h: 1706
try:
    FPDF_FORMFIELD_RADIOBUTTON = 3
except:
    pass

# build_tar/include/fpdf_formfill.h: 1707
try:
    FPDF_FORMFIELD_COMBOBOX = 4
except:
    pass

# build_tar/include/fpdf_formfill.h: 1708
try:
    FPDF_FORMFIELD_LISTBOX = 5
except:
    pass

# build_tar/include/fpdf_formfill.h: 1709
try:
    FPDF_FORMFIELD_TEXTFIELD = 6
except:
    pass

# build_tar/include/fpdf_formfill.h: 1710
try:
    FPDF_FORMFIELD_SIGNATURE = 7
except:
    pass

# build_tar/include/fpdf_formfill.h: 1725
try:
    FPDF_FORMFIELD_COUNT = 8
except:
    pass

# build_tar/include/fpdf_annot.h: 22
try:
    FPDF_ANNOT_UNKNOWN = 0
except:
    pass

# build_tar/include/fpdf_annot.h: 23
try:
    FPDF_ANNOT_TEXT = 1
except:
    pass

# build_tar/include/fpdf_annot.h: 24
try:
    FPDF_ANNOT_LINK = 2
except:
    pass

# build_tar/include/fpdf_annot.h: 25
try:
    FPDF_ANNOT_FREETEXT = 3
except:
    pass

# build_tar/include/fpdf_annot.h: 26
try:
    FPDF_ANNOT_LINE = 4
except:
    pass

# build_tar/include/fpdf_annot.h: 27
try:
    FPDF_ANNOT_SQUARE = 5
except:
    pass

# build_tar/include/fpdf_annot.h: 28
try:
    FPDF_ANNOT_CIRCLE = 6
except:
    pass

# build_tar/include/fpdf_annot.h: 29
try:
    FPDF_ANNOT_POLYGON = 7
except:
    pass

# build_tar/include/fpdf_annot.h: 30
try:
    FPDF_ANNOT_POLYLINE = 8
except:
    pass

# build_tar/include/fpdf_annot.h: 31
try:
    FPDF_ANNOT_HIGHLIGHT = 9
except:
    pass

# build_tar/include/fpdf_annot.h: 32
try:
    FPDF_ANNOT_UNDERLINE = 10
except:
    pass

# build_tar/include/fpdf_annot.h: 33
try:
    FPDF_ANNOT_SQUIGGLY = 11
except:
    pass

# build_tar/include/fpdf_annot.h: 34
try:
    FPDF_ANNOT_STRIKEOUT = 12
except:
    pass

# build_tar/include/fpdf_annot.h: 35
try:
    FPDF_ANNOT_STAMP = 13
except:
    pass

# build_tar/include/fpdf_annot.h: 36
try:
    FPDF_ANNOT_CARET = 14
except:
    pass

# build_tar/include/fpdf_annot.h: 37
try:
    FPDF_ANNOT_INK = 15
except:
    pass

# build_tar/include/fpdf_annot.h: 38
try:
    FPDF_ANNOT_POPUP = 16
except:
    pass

# build_tar/include/fpdf_annot.h: 39
try:
    FPDF_ANNOT_FILEATTACHMENT = 17
except:
    pass

# build_tar/include/fpdf_annot.h: 40
try:
    FPDF_ANNOT_SOUND = 18
except:
    pass

# build_tar/include/fpdf_annot.h: 41
try:
    FPDF_ANNOT_MOVIE = 19
except:
    pass

# build_tar/include/fpdf_annot.h: 42
try:
    FPDF_ANNOT_WIDGET = 20
except:
    pass

# build_tar/include/fpdf_annot.h: 43
try:
    FPDF_ANNOT_SCREEN = 21
except:
    pass

# build_tar/include/fpdf_annot.h: 44
try:
    FPDF_ANNOT_PRINTERMARK = 22
except:
    pass

# build_tar/include/fpdf_annot.h: 45
try:
    FPDF_ANNOT_TRAPNET = 23
except:
    pass

# build_tar/include/fpdf_annot.h: 46
try:
    FPDF_ANNOT_WATERMARK = 24
except:
    pass

# build_tar/include/fpdf_annot.h: 47
try:
    FPDF_ANNOT_THREED = 25
except:
    pass

# build_tar/include/fpdf_annot.h: 48
try:
    FPDF_ANNOT_RICHMEDIA = 26
except:
    pass

# build_tar/include/fpdf_annot.h: 49
try:
    FPDF_ANNOT_XFAWIDGET = 27
except:
    pass

# build_tar/include/fpdf_annot.h: 50
try:
    FPDF_ANNOT_REDACT = 28
except:
    pass

# build_tar/include/fpdf_annot.h: 53
try:
    FPDF_ANNOT_FLAG_NONE = 0
except:
    pass

# build_tar/include/fpdf_annot.h: 54
try:
    FPDF_ANNOT_FLAG_INVISIBLE = (1 << 0)
except:
    pass

# build_tar/include/fpdf_annot.h: 55
try:
    FPDF_ANNOT_FLAG_HIDDEN = (1 << 1)
except:
    pass

# build_tar/include/fpdf_annot.h: 56
try:
    FPDF_ANNOT_FLAG_PRINT = (1 << 2)
except:
    pass

# build_tar/include/fpdf_annot.h: 57
try:
    FPDF_ANNOT_FLAG_NOZOOM = (1 << 3)
except:
    pass

# build_tar/include/fpdf_annot.h: 58
try:
    FPDF_ANNOT_FLAG_NOROTATE = (1 << 4)
except:
    pass

# build_tar/include/fpdf_annot.h: 59
try:
    FPDF_ANNOT_FLAG_NOVIEW = (1 << 5)
except:
    pass

# build_tar/include/fpdf_annot.h: 60
try:
    FPDF_ANNOT_FLAG_READONLY = (1 << 6)
except:
    pass

# build_tar/include/fpdf_annot.h: 61
try:
    FPDF_ANNOT_FLAG_LOCKED = (1 << 7)
except:
    pass

# build_tar/include/fpdf_annot.h: 62
try:
    FPDF_ANNOT_FLAG_TOGGLENOVIEW = (1 << 8)
except:
    pass

# build_tar/include/fpdf_annot.h: 64
try:
    FPDF_ANNOT_APPEARANCEMODE_NORMAL = 0
except:
    pass

# build_tar/include/fpdf_annot.h: 65
try:
    FPDF_ANNOT_APPEARANCEMODE_ROLLOVER = 1
except:
    pass

# build_tar/include/fpdf_annot.h: 66
try:
    FPDF_ANNOT_APPEARANCEMODE_DOWN = 2
except:
    pass

# build_tar/include/fpdf_annot.h: 67
try:
    FPDF_ANNOT_APPEARANCEMODE_COUNT = 3
except:
    pass

# build_tar/include/fpdf_annot.h: 71
try:
    FPDF_FORMFLAG_NONE = 0
except:
    pass

# build_tar/include/fpdf_annot.h: 72
try:
    FPDF_FORMFLAG_READONLY = (1 << 0)
except:
    pass

# build_tar/include/fpdf_annot.h: 73
try:
    FPDF_FORMFLAG_REQUIRED = (1 << 1)
except:
    pass

# build_tar/include/fpdf_annot.h: 74
try:
    FPDF_FORMFLAG_NOEXPORT = (1 << 2)
except:
    pass

# build_tar/include/fpdf_annot.h: 78
try:
    FPDF_FORMFLAG_TEXT_MULTILINE = (1 << 12)
except:
    pass

# build_tar/include/fpdf_annot.h: 79
try:
    FPDF_FORMFLAG_TEXT_PASSWORD = (1 << 13)
except:
    pass

# build_tar/include/fpdf_annot.h: 83
try:
    FPDF_FORMFLAG_CHOICE_COMBO = (1 << 17)
except:
    pass

# build_tar/include/fpdf_annot.h: 84
try:
    FPDF_FORMFLAG_CHOICE_EDIT = (1 << 18)
except:
    pass

# build_tar/include/fpdf_annot.h: 85
try:
    FPDF_FORMFLAG_CHOICE_MULTI_SELECT = (1 << 21)
except:
    pass

# build_tar/include/fpdf_dataavail.h: 15
try:
    PDF_LINEARIZATION_UNKNOWN = (-1)
except:
    pass

# build_tar/include/fpdf_dataavail.h: 16
try:
    PDF_NOT_LINEARIZED = 0
except:
    pass

# build_tar/include/fpdf_dataavail.h: 17
try:
    PDF_LINEARIZED = 1
except:
    pass

# build_tar/include/fpdf_dataavail.h: 19
try:
    PDF_DATA_ERROR = (-1)
except:
    pass

# build_tar/include/fpdf_dataavail.h: 20
try:
    PDF_DATA_NOTAVAIL = 0
except:
    pass

# build_tar/include/fpdf_dataavail.h: 21
try:
    PDF_DATA_AVAIL = 1
except:
    pass

# build_tar/include/fpdf_dataavail.h: 23
try:
    PDF_FORM_ERROR = (-1)
except:
    pass

# build_tar/include/fpdf_dataavail.h: 24
try:
    PDF_FORM_NOTAVAIL = 0
except:
    pass

# build_tar/include/fpdf_dataavail.h: 25
try:
    PDF_FORM_AVAIL = 1
except:
    pass

# build_tar/include/fpdf_dataavail.h: 26
try:
    PDF_FORM_NOTEXIST = 2
except:
    pass

# build_tar/include/fpdf_edit.h: 15
def FPDF_ARGB(a, r, g, b):
    return (c_uint32 (ord_if_char((((((c_uint32 (ord_if_char(b))).value & 0xff) | (((c_uint32 (ord_if_char(g))).value & 0xff) << 8)) | (((c_uint32 (ord_if_char(r))).value & 0xff) << 16)) | (((c_uint32 (ord_if_char(a))).value & 0xff) << 24))))).value

# build_tar/include/fpdf_edit.h: 18
def FPDF_GetBValue(argb):
    return (c_uint8 (ord_if_char(argb))).value

# build_tar/include/fpdf_edit.h: 19
def FPDF_GetGValue(argb):
    return (c_uint8 (ord_if_char(((c_uint16 (ord_if_char(argb))).value >> 8)))).value

# build_tar/include/fpdf_edit.h: 20
def FPDF_GetRValue(argb):
    return (c_uint8 (ord_if_char((argb >> 16)))).value

# build_tar/include/fpdf_edit.h: 21
def FPDF_GetAValue(argb):
    return (c_uint8 (ord_if_char((argb >> 24)))).value

# build_tar/include/fpdf_edit.h: 24
try:
    FPDF_COLORSPACE_UNKNOWN = 0
except:
    pass

# build_tar/include/fpdf_edit.h: 25
try:
    FPDF_COLORSPACE_DEVICEGRAY = 1
except:
    pass

# build_tar/include/fpdf_edit.h: 26
try:
    FPDF_COLORSPACE_DEVICERGB = 2
except:
    pass

# build_tar/include/fpdf_edit.h: 27
try:
    FPDF_COLORSPACE_DEVICECMYK = 3
except:
    pass

# build_tar/include/fpdf_edit.h: 28
try:
    FPDF_COLORSPACE_CALGRAY = 4
except:
    pass

# build_tar/include/fpdf_edit.h: 29
try:
    FPDF_COLORSPACE_CALRGB = 5
except:
    pass

# build_tar/include/fpdf_edit.h: 30
try:
    FPDF_COLORSPACE_LAB = 6
except:
    pass

# build_tar/include/fpdf_edit.h: 31
try:
    FPDF_COLORSPACE_ICCBASED = 7
except:
    pass

# build_tar/include/fpdf_edit.h: 32
try:
    FPDF_COLORSPACE_SEPARATION = 8
except:
    pass

# build_tar/include/fpdf_edit.h: 33
try:
    FPDF_COLORSPACE_DEVICEN = 9
except:
    pass

# build_tar/include/fpdf_edit.h: 34
try:
    FPDF_COLORSPACE_INDEXED = 10
except:
    pass

# build_tar/include/fpdf_edit.h: 35
try:
    FPDF_COLORSPACE_PATTERN = 11
except:
    pass

# build_tar/include/fpdf_edit.h: 38
try:
    FPDF_PAGEOBJ_UNKNOWN = 0
except:
    pass

# build_tar/include/fpdf_edit.h: 39
try:
    FPDF_PAGEOBJ_TEXT = 1
except:
    pass

# build_tar/include/fpdf_edit.h: 40
try:
    FPDF_PAGEOBJ_PATH = 2
except:
    pass

# build_tar/include/fpdf_edit.h: 41
try:
    FPDF_PAGEOBJ_IMAGE = 3
except:
    pass

# build_tar/include/fpdf_edit.h: 42
try:
    FPDF_PAGEOBJ_SHADING = 4
except:
    pass

# build_tar/include/fpdf_edit.h: 43
try:
    FPDF_PAGEOBJ_FORM = 5
except:
    pass

# build_tar/include/fpdf_edit.h: 46
try:
    FPDF_SEGMENT_UNKNOWN = (-1)
except:
    pass

# build_tar/include/fpdf_edit.h: 47
try:
    FPDF_SEGMENT_LINETO = 0
except:
    pass

# build_tar/include/fpdf_edit.h: 48
try:
    FPDF_SEGMENT_BEZIERTO = 1
except:
    pass

# build_tar/include/fpdf_edit.h: 49
try:
    FPDF_SEGMENT_MOVETO = 2
except:
    pass

# build_tar/include/fpdf_edit.h: 51
try:
    FPDF_FILLMODE_NONE = 0
except:
    pass

# build_tar/include/fpdf_edit.h: 52
try:
    FPDF_FILLMODE_ALTERNATE = 1
except:
    pass

# build_tar/include/fpdf_edit.h: 53
try:
    FPDF_FILLMODE_WINDING = 2
except:
    pass

# build_tar/include/fpdf_edit.h: 55
try:
    FPDF_FONT_TYPE1 = 1
except:
    pass

# build_tar/include/fpdf_edit.h: 56
try:
    FPDF_FONT_TRUETYPE = 2
except:
    pass

# build_tar/include/fpdf_edit.h: 58
try:
    FPDF_LINECAP_BUTT = 0
except:
    pass

# build_tar/include/fpdf_edit.h: 59
try:
    FPDF_LINECAP_ROUND = 1
except:
    pass

# build_tar/include/fpdf_edit.h: 60
try:
    FPDF_LINECAP_PROJECTING_SQUARE = 2
except:
    pass

# build_tar/include/fpdf_edit.h: 62
try:
    FPDF_LINEJOIN_MITER = 0
except:
    pass

# build_tar/include/fpdf_edit.h: 63
try:
    FPDF_LINEJOIN_ROUND = 1
except:
    pass

# build_tar/include/fpdf_edit.h: 64
try:
    FPDF_LINEJOIN_BEVEL = 2
except:
    pass

# build_tar/include/fpdf_edit.h: 67
try:
    FPDF_PRINTMODE_EMF = 0
except:
    pass

# build_tar/include/fpdf_edit.h: 68
try:
    FPDF_PRINTMODE_TEXTONLY = 1
except:
    pass

# build_tar/include/fpdf_edit.h: 69
try:
    FPDF_PRINTMODE_POSTSCRIPT2 = 2
except:
    pass

# build_tar/include/fpdf_edit.h: 70
try:
    FPDF_PRINTMODE_POSTSCRIPT3 = 3
except:
    pass

# build_tar/include/fpdf_edit.h: 71
try:
    FPDF_PRINTMODE_POSTSCRIPT2_PASSTHROUGH = 4
except:
    pass

# build_tar/include/fpdf_edit.h: 72
try:
    FPDF_PRINTMODE_POSTSCRIPT3_PASSTHROUGH = 5
except:
    pass

# build_tar/include/fpdf_edit.h: 73
try:
    FPDF_PRINTMODE_EMF_IMAGE_MASKS = 6
except:
    pass

# build_tar/include/fpdf_edit.h: 74
try:
    FPDF_PRINTMODE_POSTSCRIPT3_TYPE42 = 7
except:
    pass

# build_tar/include/fpdf_edit.h: 75
try:
    FPDF_PRINTMODE_POSTSCRIPT3_TYPE42_PASSTHROUGH = 8
except:
    pass

# build_tar/include/fpdf_ext.h: 20
try:
    FPDF_UNSP_DOC_XFAFORM = 1
except:
    pass

# build_tar/include/fpdf_ext.h: 22
try:
    FPDF_UNSP_DOC_PORTABLECOLLECTION = 2
except:
    pass

# build_tar/include/fpdf_ext.h: 24
try:
    FPDF_UNSP_DOC_ATTACHMENT = 3
except:
    pass

# build_tar/include/fpdf_ext.h: 26
try:
    FPDF_UNSP_DOC_SECURITY = 4
except:
    pass

# build_tar/include/fpdf_ext.h: 28
try:
    FPDF_UNSP_DOC_SHAREDREVIEW = 5
except:
    pass

# build_tar/include/fpdf_ext.h: 30
try:
    FPDF_UNSP_DOC_SHAREDFORM_ACROBAT = 6
except:
    pass

# build_tar/include/fpdf_ext.h: 32
try:
    FPDF_UNSP_DOC_SHAREDFORM_FILESYSTEM = 7
except:
    pass

# build_tar/include/fpdf_ext.h: 34
try:
    FPDF_UNSP_DOC_SHAREDFORM_EMAIL = 8
except:
    pass

# build_tar/include/fpdf_ext.h: 36
try:
    FPDF_UNSP_ANNOT_3DANNOT = 11
except:
    pass

# build_tar/include/fpdf_ext.h: 38
try:
    FPDF_UNSP_ANNOT_MOVIE = 12
except:
    pass

# build_tar/include/fpdf_ext.h: 40
try:
    FPDF_UNSP_ANNOT_SOUND = 13
except:
    pass

# build_tar/include/fpdf_ext.h: 42
try:
    FPDF_UNSP_ANNOT_SCREEN_MEDIA = 14
except:
    pass

# build_tar/include/fpdf_ext.h: 44
try:
    FPDF_UNSP_ANNOT_SCREEN_RICHMEDIA = 15
except:
    pass

# build_tar/include/fpdf_ext.h: 46
try:
    FPDF_UNSP_ANNOT_ATTACHMENT = 16
except:
    pass

# build_tar/include/fpdf_ext.h: 48
try:
    FPDF_UNSP_ANNOT_SIG = 17
except:
    pass

# build_tar/include/fpdf_ext.h: 92
try:
    PAGEMODE_UNKNOWN = (-1)
except:
    pass

# build_tar/include/fpdf_ext.h: 94
try:
    PAGEMODE_USENONE = 0
except:
    pass

# build_tar/include/fpdf_ext.h: 96
try:
    PAGEMODE_USEOUTLINES = 1
except:
    pass

# build_tar/include/fpdf_ext.h: 98
try:
    PAGEMODE_USETHUMBS = 2
except:
    pass

# build_tar/include/fpdf_ext.h: 100
try:
    PAGEMODE_FULLSCREEN = 3
except:
    pass

# build_tar/include/fpdf_ext.h: 102
try:
    PAGEMODE_USEOC = 4
except:
    pass

# build_tar/include/fpdf_ext.h: 104
try:
    PAGEMODE_USEATTACHMENTS = 5
except:
    pass

# build_tar/include/fpdf_flatten.h: 14
try:
    FLATTEN_FAIL = 0
except:
    pass

# build_tar/include/fpdf_flatten.h: 16
try:
    FLATTEN_SUCCESS = 1
except:
    pass

# build_tar/include/fpdf_flatten.h: 18
try:
    FLATTEN_NOTHINGTODO = 2
except:
    pass

# build_tar/include/fpdf_flatten.h: 21
try:
    FLAT_NORMALDISPLAY = 0
except:
    pass

# build_tar/include/fpdf_flatten.h: 23
try:
    FLAT_PRINT = 1
except:
    pass

# build_tar/include/fpdf_progressive.h: 15
try:
    FPDF_RENDER_READY = 0
except:
    pass

# build_tar/include/fpdf_progressive.h: 16
try:
    FPDF_RENDER_TOBECONTINUED = 1
except:
    pass

# build_tar/include/fpdf_progressive.h: 17
try:
    FPDF_RENDER_DONE = 2
except:
    pass

# build_tar/include/fpdf_progressive.h: 18
try:
    FPDF_RENDER_FAILED = 3
except:
    pass

# build_tar/include/fpdf_save.h: 45
try:
    FPDF_INCREMENTAL = 1
except:
    pass

# build_tar/include/fpdf_save.h: 46
try:
    FPDF_NO_INCREMENTAL = 2
except:
    pass

# build_tar/include/fpdf_save.h: 47
try:
    FPDF_REMOVE_SECURITY = 3
except:
    pass

# build_tar/include/fpdf_sysfontinfo.h: 15
try:
    FXFONT_ANSI_CHARSET = 0
except:
    pass

# build_tar/include/fpdf_sysfontinfo.h: 16
try:
    FXFONT_DEFAULT_CHARSET = 1
except:
    pass

# build_tar/include/fpdf_sysfontinfo.h: 17
try:
    FXFONT_SYMBOL_CHARSET = 2
except:
    pass

# build_tar/include/fpdf_sysfontinfo.h: 18
try:
    FXFONT_SHIFTJIS_CHARSET = 128
except:
    pass

# build_tar/include/fpdf_sysfontinfo.h: 19
try:
    FXFONT_HANGEUL_CHARSET = 129
except:
    pass

# build_tar/include/fpdf_sysfontinfo.h: 20
try:
    FXFONT_GB2312_CHARSET = 134
except:
    pass

# build_tar/include/fpdf_sysfontinfo.h: 21
try:
    FXFONT_CHINESEBIG5_CHARSET = 136
except:
    pass

# build_tar/include/fpdf_sysfontinfo.h: 22
try:
    FXFONT_ARABIC_CHARSET = 178
except:
    pass

# build_tar/include/fpdf_sysfontinfo.h: 23
try:
    FXFONT_CYRILLIC_CHARSET = 204
except:
    pass

# build_tar/include/fpdf_sysfontinfo.h: 24
try:
    FXFONT_EASTERNEUROPEAN_CHARSET = 238
except:
    pass

# build_tar/include/fpdf_sysfontinfo.h: 27
try:
    FXFONT_FF_FIXEDPITCH = (1 << 0)
except:
    pass

# build_tar/include/fpdf_sysfontinfo.h: 28
try:
    FXFONT_FF_ROMAN = (1 << 4)
except:
    pass

# build_tar/include/fpdf_sysfontinfo.h: 29
try:
    FXFONT_FF_SCRIPT = (4 << 4)
except:
    pass

# build_tar/include/fpdf_sysfontinfo.h: 32
try:
    FXFONT_FW_NORMAL = 400
except:
    pass

# build_tar/include/fpdf_sysfontinfo.h: 33
try:
    FXFONT_FW_BOLD = 700
except:
    pass

# build_tar/include/fpdf_text.h: 434
try:
    FPDF_MATCHCASE = 0x00000001
except:
    pass

# build_tar/include/fpdf_text.h: 436
try:
    FPDF_MATCHWHOLEWORD = 0x00000002
except:
    pass

# build_tar/include/fpdf_text.h: 438
try:
    FPDF_CONSECUTIVE = 0x00000004
except:
    pass

fpdf_action_t__ = struct_fpdf_action_t__# build_tar/include/fpdfview.h: 54

fpdf_annotation_t__ = struct_fpdf_annotation_t__# build_tar/include/fpdfview.h: 55

fpdf_attachment_t__ = struct_fpdf_attachment_t__# build_tar/include/fpdfview.h: 56

fpdf_avail_t__ = struct_fpdf_avail_t__# build_tar/include/fpdfview.h: 57

fpdf_bitmap_t__ = struct_fpdf_bitmap_t__# build_tar/include/fpdfview.h: 58

fpdf_bookmark_t__ = struct_fpdf_bookmark_t__# build_tar/include/fpdfview.h: 59

fpdf_clippath_t__ = struct_fpdf_clippath_t__# build_tar/include/fpdfview.h: 60

fpdf_dest_t__ = struct_fpdf_dest_t__# build_tar/include/fpdfview.h: 61

fpdf_document_t__ = struct_fpdf_document_t__# build_tar/include/fpdfview.h: 62

fpdf_font_t__ = struct_fpdf_font_t__# build_tar/include/fpdfview.h: 63

fpdf_form_handle_t__ = struct_fpdf_form_handle_t__# build_tar/include/fpdfview.h: 64

fpdf_glyphpath_t__ = struct_fpdf_glyphpath_t__# build_tar/include/fpdfview.h: 65

fpdf_javascript_action_t = struct_fpdf_javascript_action_t# build_tar/include/fpdfview.h: 66

fpdf_link_t__ = struct_fpdf_link_t__# build_tar/include/fpdfview.h: 67

fpdf_page_t__ = struct_fpdf_page_t__# build_tar/include/fpdfview.h: 68

fpdf_pagelink_t__ = struct_fpdf_pagelink_t__# build_tar/include/fpdfview.h: 69

fpdf_pageobject_t__ = struct_fpdf_pageobject_t__# build_tar/include/fpdfview.h: 70

fpdf_pageobjectmark_t__ = struct_fpdf_pageobjectmark_t__# build_tar/include/fpdfview.h: 71

fpdf_pagerange_t__ = struct_fpdf_pagerange_t__# build_tar/include/fpdfview.h: 72

fpdf_pathsegment_t = struct_fpdf_pathsegment_t# build_tar/include/fpdfview.h: 73

fpdf_schhandle_t__ = struct_fpdf_schhandle_t__# build_tar/include/fpdfview.h: 75

fpdf_signature_t__ = struct_fpdf_signature_t__# build_tar/include/fpdfview.h: 76

fpdf_structelement_t__ = struct_fpdf_structelement_t__# build_tar/include/fpdfview.h: 77

fpdf_structtree_t__ = struct_fpdf_structtree_t__# build_tar/include/fpdfview.h: 78

fpdf_textpage_t__ = struct_fpdf_textpage_t__# build_tar/include/fpdfview.h: 79

fpdf_widget_t__ = struct_fpdf_widget_t__# build_tar/include/fpdfview.h: 80

fpdf_xobject_t__ = struct_fpdf_xobject_t__# build_tar/include/fpdfview.h: 81

FPDF_BSTR_ = struct_FPDF_BSTR_# build_tar/include/fpdfview.h: 114

_FS_MATRIX_ = struct__FS_MATRIX_# build_tar/include/fpdfview.h: 140

_FS_RECTF_ = struct__FS_RECTF_# build_tar/include/fpdfview.h: 143

FS_SIZEF_ = struct_FS_SIZEF_# build_tar/include/fpdfview.h: 158

FS_POINTF_ = struct_FS_POINTF_# build_tar/include/fpdfview.h: 167

FPDF_LIBRARY_CONFIG_ = struct_FPDF_LIBRARY_CONFIG_# build_tar/include/fpdfview.h: 247

FPDF_FILEHANDLER_ = struct_FPDF_FILEHANDLER_# build_tar/include/fpdfview.h: 535

FPDF_COLORSCHEME_ = struct_FPDF_COLORSCHEME_# build_tar/include/fpdfview.h: 808

_FS_QUADPOINTSF = struct__FS_QUADPOINTSF# build_tar/include/fpdf_doc.h: 57

_IPDF_JsPlatform = struct__IPDF_JsPlatform# build_tar/include/fpdf_formfill.h: 52

_FPDF_SYSTEMTIME = struct__FPDF_SYSTEMTIME# build_tar/include/fpdf_formfill.h: 353

_FPDF_FORMFILLINFO = struct__FPDF_FORMFILLINFO# build_tar/include/fpdf_formfill.h: 375

_FX_FILEAVAIL = struct__FX_FILEAVAIL# build_tar/include/fpdf_dataavail.h: 33

_FX_DOWNLOADHINTS = struct__FX_DOWNLOADHINTS# build_tar/include/fpdf_dataavail.h: 71

FPDF_IMAGEOBJ_METADATA = struct_FPDF_IMAGEOBJ_METADATA# build_tar/include/fpdf_edit.h: 93

_UNSUPPORT_INFO = struct__UNSUPPORT_INFO# build_tar/include/fpdf_ext.h: 51

_IFSDK_PAUSE = struct__IFSDK_PAUSE# build_tar/include/fpdf_progressive.h: 25

FPDF_FILEWRITE_ = struct_FPDF_FILEWRITE_# build_tar/include/fpdf_save.h: 19

_FPDF_SYSFONTINFO = struct__FPDF_SYSFONTINFO# build_tar/include/fpdf_sysfontinfo.h: 44

FPDF_CharsetFontMap_ = struct_FPDF_CharsetFontMap_# build_tar/include/fpdf_sysfontinfo.h: 232

# No inserted files

# No prefix-stripping

