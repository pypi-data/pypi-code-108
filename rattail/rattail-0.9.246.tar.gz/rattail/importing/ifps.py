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
IFPS -> Rattail data import
"""

from __future__ import unicode_literals, absolute_import

import datetime
import logging

import sqlalchemy as sa

from rattail import importing
from rattail.importing.handlers import FromFileHandler
from rattail.importing.files import FromExcelFile
from rattail.util import OrderedDict
from rattail.time import localtime, make_utc
from rattail.db.util import maxlen


log = logging.getLogger(__name__)


class FromIFPSToRattail(FromFileHandler, importing.ToRattailHandler):
    """
    Handler for IFPS -> Rattail data import.
    """
    host_key = 'ifps'
    generic_host_title = "IFPS"
    host_title = "IFPS"
    local_title = "Rattail"

    def get_importers(self):
        importers = OrderedDict()
        importers['IFPS_PLU'] = IFPS_PLUImporter
        return importers


class FromIFPS(FromExcelFile):
    """
    Base class for IFPS -> Rattail data importers.
    """


class IFPS_PLUImporter(FromIFPS, importing.model.IFPS_PLUImporter):
    """
    Imports PLU data from IFPS
    """
    key = 'plu'
    supported_fields = [
        'plu',
        'category',
        'commodity',
        'variety',
        'size',
        'measurements_north_america',
        'measurements_rest_of_world',
        'restrictions_notes',
        'botanical_name',
        'aka',
        'revision_date',
        'date_added',
        'gpc',
        'image',
        'image_source',
    ]

    def normalize_host_object(self, xlrow):
        plu = int(xlrow['PLU'])
        data = {
            'plu': plu,
            'category': xlrow['CATEGORY'].strip() or None,
            'commodity': xlrow['COMMODITY'].strip() or None,
            'variety': xlrow['VARIETY'].strip() or None,
            'size': xlrow['SIZE'].strip() or None,
            'measurements_north_america': xlrow['MEASUREMENTS: NORTH AMERICA'].strip() or None,
            'measurements_rest_of_world': xlrow['MEASUREMENTS: REST OF WORLD'].strip() or None,
            'restrictions_notes': xlrow['RESTRICTIONS / NOTES'].strip() or None,
            'botanical_name': xlrow['BOTANICAL NAME'].strip() or None,
            'aka': xlrow['AKA'].strip() or None,
            'gpc': xlrow['GPC'].strip() or None,
            'image': xlrow['IMAGE'].strip() or None,
            'image_source': xlrow['IMAGE_SOURCE'].strip() or None,
        }

        # TODO: these two date fields are being interpreted as if they were in
        # the *local* time zone, but then we of course convert them to UTC when
        # importing to Rattail DB.  however, the IFPS website and data do not
        # actually indicate which time zone should apply to their values.

        if 'revision_date' in self.fields:
            dt = datetime.datetime.strptime(xlrow['REVISION DATE'], '%Y-%m-%d %H:%M:%S')
            dt = localtime(self.config, dt)
            data['revision_date'] = make_utc(dt)

        if 'date_added' in self.fields:
            dt = datetime.datetime.strptime(xlrow['DATE ADDED'], '%Y-%m-%d %H:%M:%S')
            dt = localtime(self.config, dt)
            data['date_added'] = make_utc(dt)

        # i think our schema is good enough, but just in case this it's not,
        # this should help track down any lingering issues.
        for field in self.fields:
            column = getattr(self.model_class, field)
            if isinstance(column.type, sa.String):
                length = maxlen(column)
                if length and data[field] and len(data[field]) > length:
                    log.warning("field %s is too long (%s chars) for %s: %s",
                                field, len(data[field]), plu, data[field])
                    data[field] = data[field][:length]

        return data
