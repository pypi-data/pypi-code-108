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
Tailbone Web API - Label Batches
"""

from __future__ import unicode_literals, absolute_import

import six

from rattail.db import model

from tailbone.api.batch import APIBatchView, APIBatchRowView


class LabelBatchViews(APIBatchView):

    model_class = model.LabelBatch
    default_handler_spec = 'rattail.batch.labels:LabelBatchHandler'
    route_prefix = 'labelbatchviews'
    permission_prefix = 'labels.batch'
    collection_url_prefix = '/label-batches'
    object_url_prefix = '/label-batch'
    supports_toggle_complete = True


class LabelBatchRowViews(APIBatchRowView):

    model_class = model.LabelBatchRow
    default_handler_spec = 'rattail.batch.labels:LabelBatchHandler'
    route_prefix = 'api.label_batch_rows'
    permission_prefix = 'labels.batch'
    collection_url_prefix = '/label-batch-rows'
    object_url_prefix = '/label-batch-row'
    supports_quick_entry = True

    def normalize(self, row):
        batch = row.batch
        data = super(LabelBatchRowViews, self).normalize(row)

        data['item_id'] = row.item_id
        data['upc'] = six.text_type(row.upc)
        data['upc_pretty'] = row.upc.pretty() if row.upc else None
        data['brand_name'] = row.brand_name
        data['description'] = row.description
        data['size'] = row.size
        data['full_description'] = row.product.full_description if row.product else row.description
        return data


def includeme(config):
    LabelBatchViews.defaults(config)
    LabelBatchRowViews.defaults(config)
