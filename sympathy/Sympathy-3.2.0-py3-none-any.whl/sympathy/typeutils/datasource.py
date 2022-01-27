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
API for working with the Datasource type.

Import this module like this::

    from sympathy.api import datasource

Class :class:`datasource.File`
------------------------------
.. autoclass:: File
   :members:
   :special-members:

"""
import collections
import json
import os
import numpy as np
from .. datasources.info import get_fileinfo_from_scheme
from .. utils import prim, filebase
from .. utils.context import inherit_doc
from .. platform.parameter_types import Connection
from .. platform.exceptions import SyDataError, filename_not_empty
from . import text


def is_datasource(fq_filename):
    fileinfo = get_fileinfo_from_scheme('text')(fq_filename)
    try:
        return fileinfo.type() == str(File.container_type)
    except (KeyError, AttributeError, TypeError):
        pass
    try:
        data = File(filename=fq_filename, scheme='text')
        data.decode_path()
        data.decode_type()
        return True
    except Exception:
        pass
    return False


def is_datasources(fq_filename):
    fileinfo = get_fileinfo_from_scheme('text')(fq_filename)
    try:
        return fileinfo.type() == str(FileList.container_type)
    except (KeyError, AttributeError, TypeError):
        pass
    try:
        data = FileList(filename=fq_filename, scheme='text')
        data[0].decode_path()
        data[0].decode_type()
        return True
    except Exception:
        pass
    return False


DatasourceModes = collections.namedtuple(
    'DatasourceModes', ['file', 'db', 'db_sqlalchemy', 'url'])


@filebase.typeutil('sytypealias datasource = sytext')
@inherit_doc
class File(text.File):
    """
    Datasource covers the case of specifying data resources and supports four
    different formats: File (local file), Database (ODBC), Database SQLAlchemy
    and URL (for example, HTTP request).

    Any node port with the *Datasource* type will produce an object of this
    kind.

    Formats:

        File:
            Absolute filename to a local file.

        Database (ODBC):
            Connection string for use with a ODBC database.

        Database SQLAlchemy:
            Engine connection string for use with SQLAlchemy.

        URL:
            Arbitrary URL, can support file or http(s) schemes.  In addition to
            the URL itself this format format allows storage of a separate
            environment dictionary, for example, to use as HTTP headers.

    """

    modes = DatasourceModes(
        'FILE', 'DATABASE', 'DATABASE SQLALCHEMY', 'URL')

    def get(self):
        datasource_json = super(File, self).get()
        if not datasource_json:
            return {}
        datasource_dict = json.loads(datasource_json)
        if datasource_dict.get('type') == self.modes.file:
            datasource_dict['path'] = prim.nativepath(datasource_dict['path'])
        return datasource_dict

    def set(self, data):
        datasource_dict = dict(data)
        if datasource_dict.get('type') == self.modes.file:
            datasource_dict['path'] = prim.nativepath(
                os.path.abspath(datasource_dict['path']))
        super(File, self).set(json.dumps(datasource_dict))

    def _require_file(self):
        type = self.decode_type()
        if type and type.lower() != 'file':
            raise SyDataError(
                'File datasource is required.')

        res = self.decode_path()
        if not res:
            raise filename_not_empty()
        return res

    def decode_path(self):
        """
        Return the path.

        In a file data source this corresponds to the path of a file. In a data
        base data source this corresponds to a connection string. That can be
        used for accessing the data base. Returns None if path hasn't been set.

        .. versionchanged:: 1.2.5
            Return None instead of raising KeyError if path hasn't been set.
        """
        return self.decode().get('path')

    def decode_type(self):
        """
        Return the type of this data source.

        It can be either ``'FILE'`` or ``'DATABASE'``. Returns None if type
        hasn't been set.

        .. versionchanged:: 1.2.5
            Return None instead of raising KeyError if type hasn't been set.
        """
        return self.decode().get('type')

    def decode(self):
        """Return the full dictionary for this data source."""
        return self.get()

    @staticmethod
    def to_file_dict(fq_filename):
        """
        Create a dictionary to be used for creating a file data source.

        You usually want to use the convenience method :meth:`encode_path`
        instead of calling this method directly.
        """
        return {'path': fq_filename, 'type': File.modes.file}

    @staticmethod
    def _to_odbc_database_dict(db_driver,
                               db_servername,
                               db_databasename,
                               db_user,
                               db_password='',
                               db_connection_string=''):
        """Create a dictionary to be used for creating a data base data source.

        You usually want to use the convenience method :meth:`encode_database`
        instead of calling this method directly.
        """
        connection_string = db_connection_string

        if not connection_string:
            # Add driver, server and database information.
            connection_string = 'DRIVER={{{}}};SERVER={};DATABASE={}'.format(
                db_driver, db_servername, db_databasename)
            # Add authentication information.
            connection_string = '{0};UID={1};PWD={2}'.format(
                connection_string, db_user, db_password)

        return {'path': connection_string, 'type': File.modes.db}

    @staticmethod
    def _to_sqlalchemy_database_dict(db_url, *args, **kwarg):
        return {
            'path': db_url,
            'type': File.modes.db_sqlalchemy,
        }

    @classmethod
    def _build_credentials(cls, credentials):
        credentials = credentials or {}
        mode = credentials.get('mode')
        name = credentials.get('name') or ''
        return {'name': name, 'mode': mode}

    @classmethod
    def to_database_dict(cls, *args, credentials=None, **kwargs):
        db_method = kwargs.pop('db_method', 'ODBC')
        res = None
        if db_method == 'ODBC':
            res = cls._to_odbc_database_dict(*args, **kwargs)
        elif db_method == 'SQLAlchemy':
            res = cls._to_sqlalchemy_database_dict(*args, **kwargs)
        if res and credentials:
            res['credentials'] = cls._build_credentials(credentials.to_dict())
        return res

    @classmethod
    def to_url_dict(cls, *args, url='', env='', credentials=None, **kwargs):
        if credentials:
            credentials = credentials.to_dict()

        return {
            'path': url,
            'type': cls.modes.url,
            'env': env,
            'credentials': cls._build_credentials(credentials)
        }

    def connection(self):
        data = self.get()
        return Connection.from_dict({
            'resource': self.decode_path(),
            'credentials': self._build_credentials(data.get('credentials'))
        })

    def encode_url(self, url_dict):
        self.set(url_dict)

    def encode(self, datasource_dict):
        """
        Store the info from datasource_dict in this datasource.

        :param datasource_dict: should be a dictionary of the same format that
          you get from :meth:`to_file_dict` or :meth:`to_database_dict`.
        """
        self.set(datasource_dict)

    def encode_path(self, filename):
        """
        Store a path to a file in this datasource.

        :param filename: should be a string containing the path. Can be
          relative or absolute.
        """
        self.encode(self.to_file_dict(filename))

    def encode_database(self, *args, **kwargs):
        """Store data base access info."""
        db_method = kwargs.pop('db_method', 'ODBC')
        self.encode(
            self.to_database_dict(*args, db_method=db_method, **kwargs))

    @classmethod
    def from_filename(cls, filename):
        """
        Return new file type datasource constructed from filename.
        """
        obj = cls()
        obj.encode_path(filename)
        return obj

    def names(self, kind=None, fields=None, **kwargs):
        """
        Return a formatted list with a name and type of the data.
        columns.
        """
        names = filebase.names(kind, fields)
        kind, fields = names.updated_args()
        fields_list = names.fields()

        if kind == 'cols':
            item = names.create_item()
            for f in fields_list:
                if f == 'name':
                    item[f] = 'type'
                elif f == 'type':
                    item[f] = np.dtype('U')
                elif f == 'expr':
                    item[f] = "['type']"

            item = names.create_item()
            for f in fields_list:
                if f == 'name':
                    item[f] = 'path'
                elif f == 'type':
                    item[f] = np.dtype('U')
                elif f == 'expr':
                    item[f] = "['path']"

        return names.created_items_to_result_list()

    def __getitem__(self, key):
        return self.get()[key]

    @classmethod
    def viewer(cls):
        from .. platform import datasource_viewer
        return datasource_viewer.DatasourceViewer

    @classmethod
    def icon(cls):
        return 'ports/datasource.svg'


@inherit_doc
class FileList(filebase.FileListBase):
    """
    FileList has been changed and is now just a function which creates
    generators to sybase types.

    Old documentation follows:

    The :class:`FileList` class is used when working with lists of Datasources.

    The main interfaces in :class:`FileList` are indexing or iterating for
    reading (see the :meth:`__getitem__()` method) and the :meth:`append()`
    method for writing.
    """

    sytype = '[text]'
    scheme = 'text'
