# Copyright 2017 - Nokia Corporation
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

import pecan

from oslo_log import log
from osprofiler import profiler
from pecan.core import abort

from datetime import datetime
from vitrage.api.controllers.rest import RootRestController
from vitrage.api.policy import enforce
from vitrage.datasources.prometheus.driver import PROMETHEUS_EVENT_TYPE


LOG = log.getLogger(__name__)


# noinspection PyBroadException
@profiler.trace_cls("event controller",
                    info={}, hide_args=False, trace_private=False)
class EventController(RootRestController):

    @pecan.expose('json')
    def post(self, **kwargs):
        LOG.info('Post event called with args: %s', kwargs)

        enforce("event post", pecan.request.headers,
                pecan.request.enforcer, {})

        prom_event_type = None
        user_agent = pecan.request.headers.get('User-Agent')
        if user_agent and user_agent.startswith("Alertmanager"):
            prom_event_type = PROMETHEUS_EVENT_TYPE

        event_time = kwargs.get('time', datetime.utcnow())
        event_type = kwargs.get('type', prom_event_type)
        details = kwargs.get('details', kwargs)

        self.post_event(event_time, event_type, details)

    @staticmethod
    def post_event(event_time, event_type, details):
        try:
            pecan.request.client.call(pecan.request.context,
                                      'post',
                                      event_time=event_time,
                                      event_type=event_type,
                                      details=details)
        except Exception:
            LOG.exception('Failed to post an event')
            abort(404, 'Failed to post event')
