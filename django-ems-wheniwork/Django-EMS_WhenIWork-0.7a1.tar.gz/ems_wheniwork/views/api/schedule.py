"""

"""
import logging

from restclients_core.exceptions import DataFailureException

from ems_wheniwork.utils import serviceorders_and_shifts
from . import RESTDispatch

logger = logging.getLogger(__name__)


class Schedule(RESTDispatch):
    def GET(self, request, **kwargs):
        try:
            events = serviceorders_and_shifts(request.GET)
        except DataFailureException as ex:
            return self.error_response(ex.status, str(ex))
        except Exception as ex:
            logger.exception(ex)
            return self.error_response(500, str(ex))

        return self.json_response(events)
