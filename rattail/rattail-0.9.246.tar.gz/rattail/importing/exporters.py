# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2021 Lance Edgar
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
Rattail Data Exporters
"""

from __future__ import unicode_literals, absolute_import

import os
import csv

import six
from sqlalchemy import orm
from sqlalchemy_utils.functions import get_primary_keys

from rattail import csvutil
from rattail.util import OrderedDict
from rattail.db.util import make_topo_sortkey
from rattail.importing import Importer
from rattail.importing.rattail import FromRattailHandler, FromRattail
from rattail.importing.handlers import ToCSVHandler


class FromSQLAlchemyToCSVMixin(object):

    # subclass must define this
    FromParent = None

    # model names which should be omitted from the auto-magic
    ignored_model_names = []

    def get_importers(self):
        """
        Here we build the set of available importers on the fly.  This avoids
        having to define things over and over since really we're just going to
        piggy-back on the existing Rattail -> Rattail logic, for obtaining the
        source data.
        """
        importers = {}
        model = self.get_model()

        # mostly try to make an importer for every data model
        for name in dir(model):
            if self.ignored_model_names and name in self.ignored_model_names:
                continue
            obj = getattr(model, name, None)
            if isinstance(obj, type) and issubclass(obj, model.Base) and obj is not model.Base:
                importers[name] = self.make_importer_factory(name, obj)

        # sort importers according to topography
        topo_sortkey = make_topo_sortkey(model)
        importers = OrderedDict([
            (name, importers[name])
            for name in sorted(importers, key=topo_sortkey)
        ])

        return importers

    def make_importer_factory(self, name, cls):
        mapper = orm.class_mapper(cls)
        fields = list(mapper.columns.keys())
        pkeys = get_primary_keys(cls)
        name = '{}Importer'.format(name)
        if six.PY2:
            name = name.encode('utf_8')
        return type(name, (self.FromParent, ToCSV), {
            'model_class': cls,
            'supported_fields': fields,
            'simple_fields': fields,
            'key': list(pkeys),
        })


class FromRattailToCSV(FromSQLAlchemyToCSVMixin, FromRattailHandler, ToCSVHandler):
    """
    Handler for Rattail -> CSV data export.
    """
    direction = 'export'
    local_title = "CSV"
    FromParent = FromRattail

    @property
    def host_title(self):
        return self.config.node_title()

    def get_model(self):
        if self.config:
            return self.config.get_model()

        from rattail.db import model
        return model


class ToFile(Importer):
    """
    Base class for importers which target data file on the local side.
    """
    empty_local_data = True

    def setup(self):
        super(ToFile, self).setup()

        if not hasattr(self, 'output_file_path'):
            filename = self.get_output_filename()
            self.output_file_path = os.path.join(self.handler.output_dir, filename)
        self.open_output_file()

    def teardown(self):
        self.close_output_file()

    def get_output_filename(self):
        """
        This should return the filename (only) for the output file, i.e.  the
        return value should not include any path information.
        """
        return '{}.csv'.format(self.model_name)

    def open_output_file(self):
        """
        Logic to open and initialize the output file.  Please note that this
        method will be called even in dry-run mode!  So if you don't want to
        open a file in dry-run mode, you must check for that.
        """
        raise NotImplementedError

    def close_output_file(self):
        """
        Logic to finalize the writing to, and close, the output file.  Please
        note that this method will be called even in dry-run mode!  So if you
        don't want to write a file in dry-run mode, you must check for that.
        """
        raise NotImplementedError

    def create_object(self, key, data):
        """
        Only "add" file record for object if not marked as "deleted".

        Note that you probably shouldn't need to override this method, but you
        probably do want to define :meth:`update_object()` instead.
        """
        if not data.get('_deleted_', False):
            return self.update_object(None, data)


class ToCSV(ToFile):
    """
    Base class for importers which target CSV file on the local side.
    """
    empty_local_data = True

    def open_output_file(self):
        if six.PY2:
            self.output_file = open(self.output_file_path, 'wb')
            self.output_writer = csvutil.UnicodeDictWriter(self.output_file, self.fields, encoding='utf_8')
        else: # PY3
            self.output_file = open(self.output_file_path, 'wt', encoding='utf_8')
            self.output_writer = csv.DictWriter(self.output_file, self.fields)
        self.write_output_header()

    def write_output_header(self):
        self.output_writer.writeheader()

    def close_output_file(self):
        self.output_file.close()

    def update_object(self, obj, data, local_data=None):
        """
        Add objects's record to CSV output file.
        """
        data = self.coerce_csv(data)
        self.output_writer.writerow(data)
        return data

    def coerce_csv(self, data):
        """
        Coerce all field values in ``data`` to string, for CSV.
        """
        coerced = {}
        for field in self.fields:
            value = data[field]

            if value is None:
                value = ''

            else:
                value = six.text_type(value)

            coerced[field] = value
        return coerced
