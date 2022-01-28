import logging

from django.forms import model_to_dict
from isc_common import setAttr, delAttr
from isc_common.http.DSRequest import DSRequest
from isc_common.models.audit import AuditManager

logger = logging.getLogger(__name__)


class CommonTreeGridManager(AuditManager):

    def createFromRequest(self, request, printRequest=False, function=None):
        request = DSRequest(request=request)
        data = request.get_data()
        res = model_to_dict(super().create(**data))
        setAttr(data, 'isFolder', False)
        res.update(data)
        return res

    def updateFromRequest(self, request):
        request = DSRequest(request=request)
        data = request.get_data()
        _data = data.copy()
        delAttr(_data, 'isFolder')
        super().filter(id=request.get_id()).update(**_data)
        return data
