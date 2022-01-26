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
Tempmon "Dashboard" View
"""

from __future__ import unicode_literals, absolute_import

import datetime

from rattail.time import localtime, make_utc
from rattail_tempmon.db import model as tempmon

from webhelpers2.html import tags

from tailbone.views import View
from tailbone.db import TempmonSession


class TempmonDashboardView(View):
    """
    Dashboard view for tempmon
    """
    session_key = 'tempmon.dashboard.appliance_uuid'

    def dashboard(self):
        use_buefy = self.get_use_buefy()

        if self.request.method == 'POST':
            appliance = None
            uuid = self.request.POST.get('appliance_uuid')
            if uuid:
                appliance = TempmonSession.query(tempmon.Appliance).get(uuid)
                if appliance:
                    self.request.session[self.session_key] = appliance.uuid
            if not appliance:
                self.request.session.flash("Appliance could not be found: {}".format(uuid), 'error')
            raise self.redirect(self.request.current_route_url())

        selected_uuid = self.request.params.get('appliance_uuid')
        selected_appliance = None
        if not selected_uuid:
            selected_uuid = self.request.session.get(self.session_key)
            if not selected_uuid:
                # must declare the "first" appliance selected
                selected_appliance = TempmonSession.query(tempmon.Appliance)\
                                                   .order_by(tempmon.Appliance.name)\
                                                   .first()
                if selected_appliance:
                    selected_uuid = selected_appliance.uuid
                    self.request.session[self.session_key] = selected_uuid

        if not selected_appliance and selected_uuid:
            selected_appliance = TempmonSession.query(tempmon.Appliance)\
                                               .get(selected_uuid)

        appliances = TempmonSession.query(tempmon.Appliance)\
                                   .order_by(tempmon.Appliance.name)\
                                   .all()
        appliance_options = tags.Options([
            tags.Option(appliance.name, appliance.uuid)
            for appliance in appliances])

        if use_buefy:
            appliance_select = None
            raise NotImplementedError
        else:
            appliance_select = tags.select('appliance_uuid', selected_uuid, appliance_options)

        return {
            'index_url': self.request.route_url('tempmon.appliances'),
            'index_title': "TempMon Appliances",
            'use_buefy': use_buefy,
            'appliance_select': appliance_select,
            'appliance': selected_appliance,
        }

    def readings(self):

        # track down the requested appliance
        uuid = self.request.params.get('appliance_uuid')
        if not uuid:
            return {'error': "Must specify valid appliance_uuid"}
        appliance = TempmonSession.query(tempmon.Appliance).get(uuid)
        if not appliance:
            return {'error': "Must specify valid appliance_uuid"}

        # remember which appliance was shown last
        self.request.session[self.session_key] = appliance.uuid

        # fetch all "current" (recent) readings for all connected probes
        probes = []
        cutoff = make_utc() - datetime.timedelta(seconds=7200) # 2 hours ago
        for probe in appliance.probes:
            probes.append({
                'uuid': probe.uuid,
                'description': probe.description,
                'location': probe.location,
                'enabled': str(probe.enabled) if probe.enabled else None,
                'readings': self.get_probe_readings(probe, cutoff),
            })
        return {'probes': probes}

    def get_probe_readings(self, probe, cutoff):

        # figure out which readings we need to graph
        readings = TempmonSession.query(tempmon.Reading)\
                                 .filter(tempmon.Reading.probe == probe)\
                                 .filter(tempmon.Reading.taken >= cutoff)\
                                 .order_by(tempmon.Reading.taken)\
                                 .all()

        # convert readings to data for scatter plot
        return [{
            'x': localtime(self.rattail_config, reading.taken, from_utc=True).isoformat(),
            'y': float(reading.degrees_f),
        } for reading in readings]

    @classmethod
    def defaults(cls, config):
        cls._defaults(config)

    @classmethod
    def _defaults(cls, config):

        # dashboard
        config.add_tailbone_permission('tempmon.appliances', 'tempmon.appliances.dashboard',
                                       "View the Tempmon Appliance \"Dashboard\" page")
        config.add_route('tempmon.dashboard', '/tempmon/dashboard',
                         request_method=('GET', 'POST'))
        config.add_view(cls, attr='dashboard', route_name='tempmon.dashboard',
                        renderer='/tempmon/dashboard.mako')

        # readings
        config.add_route('tempmon.dashboard.readings', '/tempmon/dashboard/readings',
                         request_method='GET')
        config.add_view(cls, attr='readings', route_name='tempmon.dashboard.readings',
                        renderer='json')


def includeme(config):
    TempmonDashboardView.defaults(config)
