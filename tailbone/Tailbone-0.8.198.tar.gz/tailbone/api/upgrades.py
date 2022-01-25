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
Tailbone Web API - Upgrade Views
"""

from __future__ import unicode_literals, absolute_import

import six

from rattail.db import model

from tailbone.api import APIMasterView2 as APIMasterView


class UpgradeView(APIMasterView):
    """
    REST API views for Upgrade model.
    """
    model_class = model.Upgrade
    collection_url_prefix = '/upgrades'
    object_url_prefix = '/upgrades'

    def normalize(self, upgrade):
        data = {
            'created': upgrade.created.isoformat(),
            'description': upgrade.description,
            'enabled': upgrade.enabled,
            'executed': upgrade.executed.isoformat() if upgrade.executed else None,
            # 'executed_by': 
        }
        if upgrade.status_code is None:
            data['status_code'] = None
        else:
            data['status_code'] = self.enum.UPGRADE_STATUS.get(upgrade.status_code,
                                                               six.text_type(upgrade.status_code))
        return data


def includeme(config):
    UpgradeView.defaults(config)
