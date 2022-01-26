# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2020 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Base classes for importers which have file(s) as source data
"""

from __future__ import unicode_literals, absolute_import

import os

from rattail import importing
from rattail.excel import ExcelReader


class FromFile(importing.Importer):
    """
    Base class for importers which obtain source (host) data from file.
    """

    def setup(self):
        if not hasattr(self, 'input_file_path'):
            self.input_file_path = self.get_input_file_path()
        self.open_input_file()

    def teardown(self):
        self.close_input_file()

    def get_input_file_path(self):
        return os.path.join(self.input_dir,
                            self.get_input_file_name())

    def get_input_file_name(self):
        raise NotImplementedError

    def open_input_file(self):
        raise NotImplementedError

    def close_input_file(self):
        raise NotImplementedError


class FromExcelFile(FromFile):
    """
    Base class for importers which get their data from Excel file.
    """

    def get_input_file_name(self):
        return '{}.xlsx'.format(self.model_name)

    def open_input_file(self):
        self.excel_reader = ExcelReader(self.input_file_path)

    def close_input_file(self):
        pass

    def get_host_objects(self):
        return self.excel_reader.read_rows()
