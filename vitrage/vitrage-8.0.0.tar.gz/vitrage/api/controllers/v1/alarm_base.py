# Copyright 2018 - Nokia Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


from oslo_log import log
from oslo_utils.strutils import bool_from_string
import pecan
from pecan.core import abort

from vitrage.api.controllers.rest import RootRestController
from vitrage.api.policy import enforce
from vitrage.common.constants import TenantProps
from vitrage.common.constants import VertexProperties as Vprops
from vitrage.common.utils import decompress_obj

LOG = log.getLogger(__name__)


# noinspection PyBroadException
class BaseAlarmsController(RootRestController):

    @staticmethod
    def _get_alarms(**kwargs):
        vitrage_id = kwargs.get(Vprops.VITRAGE_ID)
        start = kwargs.get('start')
        end = kwargs.get('end')
        limit = kwargs.get('limit', 10000)
        sort_by = kwargs.get('sort_by', ['start_timestamp', 'vitrage_id'])
        sort_dirs = kwargs.get('sort_dirs', ['asc', 'asc'])
        filter_by = kwargs.get('filter_by', [])
        filter_vals = kwargs.get('filter_vals', [])
        next_page = kwargs.get('next_page', True)
        marker = kwargs.get('marker')
        only_active_alarms = kwargs.get('only_active_alarms', False)
        all_tenants = kwargs.get(TenantProps.ALL_TENANTS, False)
        all_tenants = bool_from_string(all_tenants)
        if all_tenants:
            enforce("list alarms:all_tenants", pecan.request.headers,
                    pecan.request.enforcer, {})
        else:
            enforce("list alarms", pecan.request.headers,
                    pecan.request.enforcer, {})

        alarms = \
            pecan.request.client.call(pecan.request.context,
                                      'get_alarms',
                                      vitrage_id=vitrage_id,
                                      all_tenants=all_tenants,
                                      start=start,
                                      end=end,
                                      limit=limit,
                                      sort_by=sort_by,
                                      sort_dirs=sort_dirs,
                                      filter_by=filter_by,
                                      filter_vals=filter_vals,
                                      next_page=next_page,
                                      marker=marker,
                                      only_active_alarms=only_active_alarms
                                      )

        try:
            alarms_list = decompress_obj(alarms)['alarms']
            return alarms_list

        except Exception:
            LOG.exception('Failed to get alarms')
            abort(404, 'Failed to get alarms')
