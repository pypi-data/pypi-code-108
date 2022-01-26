import json
import logging
import re

from uw_wheniwork.shifts import Shifts

from .exceptions import InvalidParamException
from . import RESTDispatch

logger = logging.getLogger(__name__)


class Shift(RESTDispatch):
    def __init__(self):
        self._shift_api = Shifts()
        self._audit_log = logging.getLogger('audit')

    def POST(self, request, **kwargs):
        try:
            data = json.loads(request.body)
            name = self._valid_shift_name(data.get("name", "").strip())
            user_id = data.get("user_id", None)
            account_id = data.get("account_id", None)
            site_id = data.get("site_id", None)
            location_id = data.get("location_id", None)
            position_id = data.get("position_id", None)
            start_time = self._valid_time(data.get("start_time", "").strip())
            end_time = self._valid_time(data.get("end_time", "").strip())

            shift = self._shift_api.create_shift({'notes': name,
                                                  'start_time': start_time,
                                                  'end_time': end_time,
                                                  'user_id': user_id,
                                                  'account_id': account_id,
                                                  'site_id': site_id,
                                                  'location_id': location_id,
                                                  'position_id': position_id,
                                                  'published': True})

            shift_id = shift.shift_id

            self._audit_log.info('%s scheduled %s from %s to %s' % (
                request.user, name, start_time, end_time))

            return self.json_response({'shift_id': shift_id})
        except InvalidParamException as ex:
            return self.error_response(400, "%s" % ex)
        except Exception as ex:
            return self.error_response(500, "Unable to save shift: %s" % ex)

    def DELETE(self, request, **kwargs):
        try:
            shift_id = self._valid_shift_id(kwargs.get('shift_id'))

            self._shift_api.delete_shifts([shift_id])
            self._audit_log.info(
                '%s deleted shift %s' % (request.user, shift_id))
            return self.json_response({'deleted_shift_id': shift_id})
        except InvalidParamException as err:
            return self.error_response(400, "Invalid Parameter: %s" % err)

    def _valid_shift_id(self, shift_id):
        if re.match(r'^\d+$', shift_id):
            return shift_id

        raise InvalidParamException('missing shift id')

    def _valid_shift_name(self, name):
        if name and len(name):
            return name

        raise InvalidParamException('bad shift name')

    def _valid_time(self, time):
        if time and len(time):
            return time

        raise InvalidParamException('bad time value')
