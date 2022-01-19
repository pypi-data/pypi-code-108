# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2019 Lance Edgar
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
Forms for Receiving
"""

from __future__ import unicode_literals, absolute_import

from rattail.db import model

import colander


@colander.deferred
def valid_purchase_batch_row(node, kw):
    session = kw['session']
    def validate(node, value):
        row = session.query(model.PurchaseBatchRow).get(value)
        if not row:
            raise colander.Invalid(node, "Batch row not found")
        if row.batch.executed:
            raise colander.Invalid(node, "Batch has already been executed")
        return row.uuid
    return validate


class ReceiveRow(colander.MappingSchema):

    row = colander.SchemaNode(colander.String(),
                              validator=valid_purchase_batch_row)

    mode = colander.SchemaNode(colander.String(),
                               validator=colander.OneOf([
                                   'received',
                                   'damaged',
                                   'expired',
                                   # 'mispick',
                               ]))

    cases = colander.SchemaNode(colander.Decimal(),
                                missing=colander.null)

    units = colander.SchemaNode(colander.Decimal(),
                                missing=colander.null)

    expiration_date = colander.SchemaNode(colander.Date(),
                                          missing=colander.null)

    quick_receive = colander.SchemaNode(colander.Boolean())
