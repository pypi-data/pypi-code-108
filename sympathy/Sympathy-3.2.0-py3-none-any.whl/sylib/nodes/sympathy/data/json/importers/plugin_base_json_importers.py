# This file is part of Sympathy for Data.
# Copyright (c) 2018, Combine Control Systems AB
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
import os
import io
import json
import xmltodict
from sympathy.api import importers
from sympathy.api.exceptions import SyDataError
from sympathy.api import qt as qt_compat

QtGui = qt_compat.import_module('QtGui')


def _sniff_type(filename):
    """
    Guess if it is a JSON or XML file by looking
    at the file extension or the first line
    """
    ext = os.path.splitext(filename)[1].lower()
    if ext in [".json", ".xml"]:
        return ext[1:]

    with open(filename, "rb") as f:
        for line in f:
            line = line.lstrip()
            if line:
                if line.startswith(b"<"):
                    return "xml"
                else:
                    return "json"


def import_data(obj, filename, filetype):
    """
    Load a Json structure from a datasource or a filepath

    :param datasource: the datasource or the filepath to load the Json from
    :param filetype: can be either ``json`` or ``xml`` and determines what type
                     of file to load
    """
    filetype = filetype.lower()
    with io.open(filename, "rb") as f:
        if filetype == "json":
            _dict = json.load(f)
        elif filetype == "xml":
            _dict = xmltodict.parse(f.read())
        else:
            assert False, 'Unknown filetype'
    obj.set(_dict)


class DataImportAuto(importers.AutoImporterMixin,
                     importers.JsonDataImporterBase):

    IMPORTER_NAME = "Auto"
    _IMPORTER_BASE = importers.JsonDataImporterBase


class DataImportXml(importers.JsonDataImporterBase):
    IMPORTER_NAME = "XML"

    def valid_for_file(self):
        try:
            return _sniff_type(self._fq_infilename) == 'xml'
        except Exception:
            return False

    def parameter_view(self, parameters):
        if not self.valid_for_file():
            return QtGui.QLabel(
                'File does not exist or cannot be read.')
        return QtGui.QLabel()

    def import_data(self, out_datafile, parameters=None, progress=None):
        try:
            import_data(out_datafile, self._fq_infilename, filetype='xml')
        except Exception as e:
            raise self.import_failed(e)


class DataImportJson(importers.JsonDataImporterBase):
    IMPORTER_NAME = "JSON"

    def valid_for_file(self):
        try:
            return _sniff_type(self._fq_infilename) == 'json'
        except Exception:
            return False

    def parameter_view(self, parameters):
        if not self.valid_for_file():
            return QtGui.QLabel(
                'File does not exist or cannot be read.')
        return QtGui.QLabel()

    def import_data(self, out_datafile, parameters=None, progress=None):
        try:
            import_data(out_datafile, self._fq_infilename, filetype='json')
        except Exception as e:
            raise self.import_failed(e)
