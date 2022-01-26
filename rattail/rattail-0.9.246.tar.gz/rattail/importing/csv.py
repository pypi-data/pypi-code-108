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
CSV -> Rattail data import
"""

from __future__ import unicode_literals, absolute_import

import os
import csv
import datetime

import six
import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy_utils.functions import get_primary_keys

from rattail import importing, csvutil
from rattail.importing.handlers import FromFileHandler
from rattail.importing.files import FromFile
from rattail.db.util import make_topo_sortkey
from rattail.util import OrderedDict
from rattail.config import parse_bool


class FromCSVToSQLAlchemyMixin(object):

    host_key = 'csv'
    generic_host_title = "CSV"

    # subclass must define this
    ToParent = None

    def get_importers(self):
        """
        Here we build the set of available importers on the fly.  This avoids
        having to define things over and over since really we're just going to
        piggy-back on the existing logic, for storing new data.
        """
        importers = {}
        model = self.get_model()

        # mostly try to make an importer for every data model
        for name in dir(model):
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
        return type(name, (FromCSV, self.ToParent), {
            'model_class': cls,
            'supported_fields': fields,
            'simple_fields': fields,
            'key': list(pkeys),
            'coercers': self.make_coercers(cls, fields),
        })

    def make_coercers(self, cls, fields):
        coercers = {}
        for field in fields:
            attr = getattr(cls, field)
            assert len(attr.prop.columns) == 1
            column = attr.prop.columns[0]

            # String
            if isinstance(attr.type, sa.String):
                if column.nullable:
                    coercers[field] = self.coerce_string_nullable
                else:
                    coercers[field] = self.coerce_string

            # Boolean
            elif isinstance(attr.type, sa.Boolean):
                if column.nullable:
                    coercers[field] = self.coerce_boolean_nullable
                else:
                    coercers[field] = self.coerce_boolean

            # Integer
            elif isinstance(attr.type, sa.Integer):
                if column.nullable:
                    coercers[field] = self.coerce_integer_nullable
                else:
                    coercers[field] = self.coerce_integer

            # Float
            elif isinstance(attr.type, sa.Float):
                if column.nullable:
                    coercers[field] = self.coerce_float_nullable
                else:
                    coercers[field] = self.coerce_float

            # DateTime
            elif isinstance(attr.type, sa.DateTime):
                if column.nullable:
                    coercers[field] = self.coerce_datetime_nullable
                else:
                    coercers[field] = self.coerce_datetime

            else: # unknown type; do not coerce
                coercers[field] = lambda value: value

        return coercers

    def coerce_boolean(self, value):
        return parse_bool(value)

    def coerce_boolean_nullable(self, value):
        if value == '':
            return None
        return self.coerce_boolean(value)

    def coerce_integer(self, value):
        if value == '':
            return None
        return int(value)

    def coerce_integer_nullable(self, value):
        if value == '':
            return None
        return self.coerce_integer(value)

    def coerce_float(self, value):
        if value == '':
            return None
        return float(value)

    def coerce_float_nullable(self, value):
        if value == '':
            return None
        return self.coerce_float(value)

    def coerce_datetime(self, value):
        if value == '':
            return
        return datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S')

    def coerce_datetime_nullable(self, value):
        if value == '':
            return None
        return self.coerce_datetime(value)

    def coerce_string(self, value):
        return value

    def coerce_string_nullable(self, value):
        if value == '':
            return None
        return self.coerce_string(value)


class FromCSVToRattail(FromCSVToSQLAlchemyMixin, FromFileHandler, importing.ToRattailHandler):
    """
    Handler for CSV -> Rattail data import
    """
    host_title = "CSV"
    ToParent = importing.model.ToRattail

    @property
    def local_title(self):
        return self.config.node_title()

    def get_model(self):
        if self.config:
            return self.config.get_model()

        from rattail.db import model
        return model


class FromCSV(FromFile):
    """
    Base class for importers coming from CSV
    """
    csv_encoding = 'utf_8'

    def get_input_file_name(self):
        return '{}.csv'.format(self.model_name)

    def open_input_file(self):
        if six.PY2:
            self.input_file = open(self.input_file_path, 'rb')
            self.input_reader = csvutil.UnicodeDictReader(self.input_file, encoding=self.csv_encoding)
        else: # PY3
            self.input_file = open(self.input_file_path, 'rt', encoding=self.csv_encoding)
            self.input_reader = csv.DictReader(self.input_file)

    def close_input_file(self):
        self.input_file.close()

    def get_host_objects(self):
        return list(self.input_reader)

    def normalize_host_object(self, data):
        return self.coerce_local(data)

    def coerce_local(self, data):
        coerced = {}
        for field in self.fields:
            value = data[field]
            coerced[field] = self.coercers[field](value)
        return coerced
