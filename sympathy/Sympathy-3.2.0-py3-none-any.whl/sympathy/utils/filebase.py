# This file is part of Sympathy for Data.
# Copyright (c) 2013, Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.
"""
Utility functions needed to read and write tables from/to different
formats.
"""
from .. datasources.info import (get_fileinfo_from_scheme,
                                 get_scheme_from_file)
from .. platform.types import (from_string_alias, from_type_expand,
                               from_string_expand)
from .. types import sylist
from .. platform.types import manager as type_manager
from .. types.factory import typefactory
from .. platform import types
from .. platform import exceptions
from . import port as port_util
from . import complete
from . import names as _names


class PPrintUnicode(object):
    """
    Base class for pretty printing in IPython.

    Any subclass will be printed with unicode(obj) instead of the default
    repr(obj) when they are the result of an expression in IPython. This allows
    for higher interactivity when working in IPython.
    """
    def _repr_mimebundle_(self, include=None, exclude=None):
        """
        For ipython integration, determines how values of this type are written
        to the console.

        Can be customized in subclasses and can be used to add support for
        other kinds of output such as text/html.
        """
        return {'text/plain': str(self)}


def typeutil(typealias):
    def inner(cls):
        declaration = from_string_alias(typealias)
        cls.container_type = declaration
        type_manager.set_typealias_util(declaration.name(), cls)
        return cls
    return inner


def from_file(filename, scheme=None, sytype=None, external=True):

    if scheme is None:
        scheme = get_scheme_from_file(filename)

    if scheme is None:
        return None

    fileinfo_ = fileinfo(filename, scheme)

    if sytype is None:
        sytype = fileinfo_.type()

    return port_util.port_maker(
        {'file': filename, 'scheme': scheme,
         'type': sytype}, 'r', external, True)


def to_file(filename, scheme, sytype, dstype=None, external=True):
    return port_util.port_maker(
        {'file': filename, 'scheme': scheme,
         'type': sytype, 'dstype': dstype}, 'w', external, True)


def from_type(sytype):
    return typefactory.from_type(sytype)


def empty_from_type(sytype):
    return typefactory.from_type(sytype)


def fileinfo(filename, scheme=None):
    if scheme is None:
        scheme = get_scheme_from_file(filename)

    return get_fileinfo_from_scheme(scheme)(filename)


def filetype(filename):
    try:
        fileinfo_ = fileinfo(filename)
        return fileinfo_.type()
    except:
        pass


def is_type(sytype, filename, scheme='hdf5'):
    info = fileinfo(filename, scheme)
    try:
        return fileinfo.type() == str(sytype)
    except (KeyError, AttributeError, TypeError):
        pass
    try:
        return (str(from_string_expand(info.datatype())) ==
                str(from_type_expand(sytype)))
    except TypeError:
        return False


class FileManager(PPrintUnicode):
    """FileManager handles data contexts for File and FileList."""
    container_type = None
    ELEMENT = None

    def __init__(self, fileobj, data, filename, mode, scheme,
                 import_links=False):
        """
        Fileobj is a file owned. It should be closed by self.
        Data is a borrowed file. It shall not be closed by self.
        Filename is used to construct a new fileobj.
        Mode and scheme are used together with filename to construct
        the filename.
        Import_links is only usable together with filename and enables links
        to the file source to be written.

        Fileobj, data and filename are mutually exclusive.
        """
        self._external_input_file = False

        if filename is not None:
            if mode == 'r':
                self._external_input_file = True

            elif mode != 'w':
                raise AssertionError(
                    "Supported values for mode are: 'r' and 'w', but '{}'"
                    " was given.".format(mode))
        self._data = data
        self.__fileobj = fileobj

        if fileobj is not None:
            self._data = fileobj
        elif data is not None:
            pass
        elif filename is not None:
            if mode == 'w' and import_links:
                exceptions.sywarn(
                    "Argument: 'import_links' must be False for mode 'w'.")
                import_links = False

            self.__fileobj = open_file(
                filename=filename, mode=mode, external=not import_links,
                sytype=self._storage_type(), dstype=self.container_type, scheme='hdf5')
            self._data = self.__fileobj
        else:
            self._data = typefactory.from_type(self.container_type)._data

        if isinstance(self._data, type(self)):
            # TODO(erik): Handle per case above, not for all cases at once.
            # Avoiding double wrapping with non-managed nodes.
            assert False, '2.1.0: Should be finished with double-wrapping now!'
            self._data = self._data._data

    def _storage_type(self):
        return self.container_type

    def _copy_base(self):
        cls = type(self)
        obj = cls.__new__(cls)
        obj._data = self._data
        obj.__fileobj = self.__fileobj
        obj._external_input_file = self._external_input_file
        return obj

    def __copy__(self):
        return self._copy_base()

    def __deepcopy__(self, memo=None):
        obj = self._copy_base()
        obj._data = self._data.__deepcopy__()
        return obj

    def writeback(self):
        self._data.writeback()

    def sync(self):
        pass

    def _writeback(self, datasource, link=None):
        return self._data._writeback(datasource, link)

    @classmethod
    def is_type(cls, filename, scheme='hdf5'):
        return is_type(cls.container_type, filename, scheme)

    @staticmethod
    def is_valid():
        return True

    def close(self):
        """Close the referenced data file."""
        # TODO(erik): Handle ownership on close.
        if not self._external_input_file:
            self.sync()
        if self.__fileobj is not None:
            self.__fileobj.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


class FileBase(FileManager):
    """File represents the top level of a table"""
    container_type = None

    def __init__(self, fileobj=None, data=None, filename=None, mode='r',
                 scheme='hdf5', source=None, managed=False,
                 import_links=False):
        if filename is not None and mode is None:
            mode = 'r'
        super().__init__(fileobj, data, filename, mode, scheme,
                         import_links=import_links)
        self._extra_init(fileobj, data, filename, mode, scheme, source)

    def _extra_init(self, fileobj, data, filename, mode, scheme, source):
        if source:
            self.source(source)
        else:
            self.init()

    def init(self):
        pass

    def source(self, other, shallow=False):
        """
        Update self with a deepcopy of the data from other, without keeping the
        old state.

        self and other must be of the exact same type.
        """
        self._data.source(other._data, shallow=shallow)


class TypeAlias(FileBase):
    """
    Base for implementing custom sympathy types. Data serialization is
    performed through self._data which is setup by __init__ and contains the
    storage level representation of the data.

    If the object introduces additional instance fields, __deepcopy__ and sync
    likely have to be re-implemented. Carefully, read the relevant docstrings.

    Do not implement __init__, instead implement init.

    """
    container_type = None

    @classmethod
    def port(cls, description, name=None, **kwargs):
        """
        Return a new port for cls.
        """
        return port_util.CustomPort(
            cls.container_type.name(), description, name=name, **kwargs)

    @classmethod
    def viewer(cls):
        """
        Return viewer class, which must be a subclass of
        sympathy.api.typeutil.ViewerBase
        """
        return None

    @classmethod
    def icon(cls):
        """
        Return full path to svg icon.
        """
        return None

    def names(self, kind=None, fields=None, **kwargs):
        """
        Return data related to names of some kind.  In fact, names can go
        beyond finding names and find for example types.

        Useful if this type has some kind of names that would be
        useful in adjust_parameters.

        Parameters
        ----------
        kind: str
            The kind of names your are interested in.

        fields: str or [str]
            The fields you would like to include in the result.
            For example, name and type.

        Returns
        -------
        list or iterator
            Normally, containing scalar elements if fields is scalar
            and tuple of multiple such elements when fields is list.
        """
        return []

    def types(self, kind=None, **kwargs):
        """
        Obsoleted by names. Use names instead.
        types(kind=X) === names(kind=X, fields='type').

        Return types associated with names().
        """
        return self.names(kind='cols', fields='type')

    def completions(self, **kwargs):
        """
        Return completions builder for this object.
        """
        return complete.builder()

    def init(self):
        """
        Perform any initialization, such as, defining local fields.
        """
        pass

    def index(self, limit=None) -> dict:
        """
        INTERNAL use only!

        Return READ-ONLY index of internal storage including typealiases.
        Caller may view but not modify returned structure.

        Limit can be used, for performance reasons, to exclude certain items
        from the output.
        """
        if limit:
            data = self._data.index(limit['data'])
        else:
            data = self._data.index()

        return {
            'type': 'sytypealias',
            'name': self.container_type.name(),
            'data': data,
        }

    def set_index(self, index: dict) -> None:
        """
        INTERNAL use only!

        Set index to provided index (produced by matching index()).
        Does nothing unless implemented. Provided index need to match
        the internal storage data-structure exactly and can therefore not be
        set after modifications.

        Caller hands over ownership of index and may not modify the argument
        structure.
        """
        assert index['type'] == 'sytypealias', (
            'Index has incorrect type.')
        assert index['name'] == self.container_type.name(), (
            'Index has incorrect type alias.')
        assert 'data' in index, (
            'Index is missing data.')

    def source(self, other, shallow=False):
        """
        Update self with the data from other, discarding any previous state
        in self.

        Parameters
        ----------
        other: type of self
            Object used as the source for (to update) self.

        shallow: bool
            When shallow is True a deepcopy of other will be avoided to improve
            performance, shallow=True must only be used in operations that do
            not modify other.

            When shallow is False the result should be similar to performing
            the shallow=True with a deepcopy of other so that no modifications
            of either self or other, after the source operation, can affect the
            other object.
        """
        raise NotImplementedError

    def sync(self):
        """
        Synchronize data fields that are kept in memory to self._data.

        Called before data is written to disk and must be re-implemented by
        subclasses that introduce additional fields to ensure that the fields
        will be written through self._data.
        """
        pass

    def __deepcopy__(self, memo=None):
        """
        Return new TypeAlias object that does not share references with self.

        Must be re-implemented by subclasses that introduce additional fields
        to ensure that the fields are copied to the returned object.
        """
        return super().__deepcopy__()

    def _storage_type(self):
        return self.container_type.get()


def calc_quote(text):
    return repr(text)


class FileListBase(sylist, PPrintUnicode):
    """FileList represents a list of Files."""
    sytype = None  # str.
    scheme = None  # str.

    def __new__(cls, filename=None, mode='r', import_links=False):

        if mode == 'w' and import_links:
            exceptions.sywarn(
                "Argument: 'import_links' must be False for mode 'w'.")
            import_links = False

        fileobj = open_file(filename=filename, mode=mode,
                            external=not import_links,
                            sytype=types.from_string(cls.sytype),
                            dstype=None,
                            scheme=cls.scheme)
        obj = fileobj
        obj.__class__ = cls
        obj._fileobj = fileobj
        return obj

    def __init__(self, filename=None, mode='r'):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def close(self):
        super().close()

    def is_type(self, filename, scheme=None):
        return is_type(types.from_string(self.sytype), filename, scheme)

    def set_read_through(self):
        exceptions.sywarn('set_read_through is not implemented.')

    def set_write_through(self):
        exceptions.sywarn('set_write_through is not implemented.')

    def is_read_through(self):
        return False

    def is_write_through(self):
        return False

    def __str__(self):
        repr_line = repr(self)
        elements_str = "  {} element{}".format(
            len(self), "s" if len(self) != 1 else u"")
        return repr_line + ":\n" + elements_str

    def __copy__(self):
        obj = super().__copy__()
        obj._fileobj = self._fileobj
        return obj

    def __deepcopy__(self, memo=None):
        obj = super().__deepcopy__()
        obj._fileobj = self._fileobj
        return obj

    def __repr__(self):
        mode = 'Buffered '
        id_ = hex(id(self))
        return "<{}FileList object at {}>".format(mode, id_)


def open_file(filename=None, mode='r', external=True, sytype=None,
              dstype=None, scheme='hdf5'):
    fileobj = None
    assert mode in 'rw', "Mode should be 'r' or 'w'"

    if filename is not None:
        if mode == 'r':
            fileobj = from_file(
                filename, external=external, sytype=sytype)
        elif mode == 'w':
            assert sytype is not None, "Mode 'w' requires sytype"
            assert scheme is not None, "Mode 'w' requires scheme"
            fileobj = to_file(filename, scheme, sytype, dstype, external=external)

    else:
        fileobj = from_type(sytype)
    return fileobj


def names(kind, fields):
    return _names.names(kind, fields)
