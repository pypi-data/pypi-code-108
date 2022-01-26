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
Data Models for IFPS
"""

from __future__ import unicode_literals, absolute_import

import six
import sqlalchemy as sa

from rattail.db.model import Base, uuid_column


@six.python_2_unicode_compatible
class IFPS_PLU(Base):
    """
    IFPS PLU codes
    """
    __tablename__ = 'ifps_plu'
    __table_args__ = (
        sa.UniqueConstraint('plu', name='ifps_plu_uq_plu'),
    )
    __versioned__ = {}
    model_title = "IFPS PLU Code"

    uuid = uuid_column()

    plu = sa.Column(sa.Integer(), nullable=False)
    category = sa.Column(sa.String(length=100), nullable=True)
    commodity = sa.Column(sa.String(length=100), nullable=True)
    variety = sa.Column(sa.Text(), nullable=True)
    size = sa.Column(sa.String(length=100), nullable=True)
    measurements_north_america = sa.Column(sa.String(length=255), nullable=True)
    measurements_rest_of_world = sa.Column(sa.String(length=255), nullable=True)
    restrictions_notes = sa.Column(sa.Text(), nullable=True)
    botanical_name = sa.Column(sa.String(length=100), nullable=True)
    aka = sa.Column(sa.Text(), nullable=True)
    revision_date = sa.Column(sa.DateTime(), nullable=True)
    date_added = sa.Column(sa.DateTime(), nullable=True)
    gpc = sa.Column(sa.String(length=100), nullable=True)
    image = sa.Column(sa.String(length=255), nullable=True)
    image_source = sa.Column(sa.String(length=100), nullable=True)

    def __str__(self):
        return str(self.plu)
