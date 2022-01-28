import logging

from django.db import transaction

from history.models.visitor import Visitor
from isc_common.http.DSRequest import DSRequest
from isc_common.http.RPCResponse import RPCResponseConstant

logger = logging.getLogger(__name__)


class LogoutRequest(DSRequest):
    def __init__(self, request):
        DSRequest.__init__(self, request)
        data = self.get_data()

        with transaction.atomic():
            Visitor.objects.using('history').select_for_update()
            Visitor.objects.using('history').filter(username=data.get('login')).delete()

        self.response = dict(status=RPCResponseConstant.statusSuccess)
