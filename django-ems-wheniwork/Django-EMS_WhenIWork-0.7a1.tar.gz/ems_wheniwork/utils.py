import logging
import re
from datetime import datetime, timedelta

import pytz
from dateutil import tz
from django.conf import settings
from ems_client.models import Status
from ems_client.service import Service
from uw_wheniwork.account import Accounts
from uw_wheniwork.locations import Locations
from uw_wheniwork.positions import Positions
from uw_wheniwork.shifts import Shifts
from uw_wheniwork.sites import Sites
from uw_wheniwork.users import Users


logger = logging.getLogger(__name__)


def serviceorders_and_shifts(params):
    search = {
        'start_date': params.get('StartDate'),
        'end_date': params.get('EndDate')
    }
    _ems = Service()

    event_shifts = []

    if not (search['start_date'] and search['end_date']):
        return None

    serviceorder_details = _ems.get_service_order_details(**search)
    bookings = _ems.get_bookings(**search)

    # build shifts
    assigned_serviceorders = {}
    for detail in serviceorder_details:
        if (detail.service_order_start_time is None or
                detail.service_order_end_time is None):
            continue

        # If this detail has an external reference,
        # then its parent service order is "assigned"
        if detail.resource_external_reference:
            assigned_serviceorders[detail.service_order_id] = detail
            continue

        for b in bookings:
            if b.id == detail.booking_id:
                break

        # Skip cancelled bookings
        if b.status_type_id == Status.STATUS_TYPE_CANCEL:
            continue

        event_shift = {
            'room': b.room_description,
            'roomname': b.dv_room,
            'name': None,
            'event_name': b.event_name,
            'resource_description': detail.resource_description,
            'start_time': detail.service_order_start_time.strftime("%-I:%M%p"),
            'end_time': detail.service_order_end_time.strftime("%-I:%M%p"),
            'hours': None,
            'service_order_id': detail.service_order_id,
            'booking_id': detail.booking_id,
            'building': b.dv_building,
            'room_code': b.room_code,
            'schedulable': True,
            'assigned_to': {
                'name': None,
                'netid': None,
            },
            'shift': {
                'name': None,
                'id': None,
                'user_id': None,
                'account_id': None,
                'site_id': None,
                'location_id': None,
                'position_id': None,
                'start_time': None,
                'end_time': None,
            },
        }

        emstz = pytz.timezone('America/Los_Angeles')
        start_time = emstz.localize(
            datetime.combine(detail.booking_date,
                             detail.service_order_start_time))
        end_time = emstz.localize(
            datetime.combine(detail.booking_date,
                             detail.service_order_end_time))
        if start_time > end_time:
            end_time += timedelta(days=1)
        start_utc = start_time.astimezone(tz.tzutc())
        end_utc = end_time.astimezone(tz.tzutc())

        event_shift['hours'] = re.sub(r'(\d+):(\d\d):\d\d', r'\1h\2m',
                                      str(end_utc - start_utc))
        event_shift['shift']['start_time'] = start_utc.isoformat()
        event_shift['shift']['end_time'] = end_utc.isoformat()
        event_shift['shift']['name'] = event_shift['name'] = \
            "%s - %s (Service Order %s) (%s-%s, %s)" % (
                event_shift['event_name'],
                event_shift['resource_description'],
                event_shift['service_order_id'],
                event_shift['start_time'],
                event_shift['end_time'],
                event_shift['hours'],
            )

        if event_shift:
            event_shifts.append(event_shift)

    mash_in_assigned_serviceorders(event_shifts, assigned_serviceorders)
    mash_in_wheniwork_shifts(event_shifts, params)

    return event_shifts


def mash_in_assigned_serviceorders(event_shifts, assigned_serviceorders):
    for e in event_shifts:
        id = e['service_order_id']
        if id in assigned_serviceorders:
            e['assigned_to']['name'] = \
                assigned_serviceorders[id].resource_description
            e['assigned_to']['netid'] = \
                assigned_serviceorders[id].resource_external_reference
            e['shift']['name'] = e['name'] = \
                "%s - %s (Service Order %s) (%s-%s, %s)" % (
                    e['event_name'],
                    e['assigned_to']['name'],
                    e['service_order_id'],
                    e['start_time'],
                    e['end_time'],
                    e['hours'],
                )


def mash_in_wheniwork_shifts(event_shifts, params):
    # mash in when i work shift schedule
    search = {
        'start': "%sT00:00:00" % params.get('StartDate'),
        'end': "%sT23:59:59" % params.get('EndDate'),
        'include_allopen': True,
    }

    # Populate account record
    account_id = Accounts().get_account().account_id

    shifts = Shifts().get_shifts(search)
    for shift in shifts if shifts else []:
        for e in event_shifts:
            if "Service Order %s" % e['service_order_id'] in shift.notes:
                e['shift']['name'] = shift.notes
                e['shift']['id'] = shift.shift_id
                e['shift']['user_id'] = shift.user_id
                e['shift']['account_id'] = shift.account_id
                e['shift']['site_id'] = shift.site_id
                e['shift']['location_id'] = shift.location_id
                e['shift']['position_id'] = shift.position_id

                # actual shift start and end
                start_utc = shift.start_time.astimezone(pytz.utc)
                end_utc = shift.end_time.astimezone(pytz.utc)
                e['shift']['start'] = start_utc.isoformat()
                e['shift']['end'] = end_utc.isoformat()

    locations = Locations().get_locations()
    for location in locations:
        if location.name == settings.EMS_WHENIWORK_SCHEDULE_LOCATION:
            location_id = location.location_id
            break

    positions = Positions().get_positions()
    for p in positions:
        if p.name == settings.EMS_WHENIWORK_SCHEDULE_POSITION:
            position_id = p.position_id
            break

    users = Users().get_users({'location_id': location_id})

    _sites = Sites()
    sites = _sites.get_sites()

    for e in event_shifts:
        if not e['shift']['account_id']:
            e['shift']['account_id'] = account_id

        if location_id and not e['shift']['location_id']:
            e['shift']['location_id'] = location_id

        if position_id and not e['shift']['position_id']:
            e['shift']['position_id'] = position_id

        if not e['shift']['site_id']:
            for s in sites:
                if e['room'] in s.name:
                    e['shift']['site_id'] = s.site_id
                    break

        # create site if not found
        if not e['shift']['site_id']:
            new_site = {
                'location_id': location_id,
                'name': e['room'],
                # 'address': "%s %s, University of Washington" %
                #            (e['room_code'], e['building'])
            }
            if e['roomname'] != e['room']:
                new_site['name'] = new_site['name'] + " (%s)" % e['roomname']

            s = _sites.create_site(new_site)
            sites.append(s)
            e['shift']['site_id'] = s.site_id

        if not e['shift']['user_id']:
            for u in users:
                if u.employee_code == e['assigned_to']['netid']:
                    e['shift']['user_id'] = u.user_id
                    break
        if not e['shift']['user_id']:
            e['schedulable'] = False
