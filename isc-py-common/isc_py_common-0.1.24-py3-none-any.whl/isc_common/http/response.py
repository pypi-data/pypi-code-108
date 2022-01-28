import json

from bitfield import BitHandler
from django.db.models.fields.files import FieldFile
from django.http import HttpResponse

from isc_common import setAttr
from isc_common.http.JSONEncoder import JSONEncoder


class JsonResponse(HttpResponse):

    def __init__(self, data, encoder=JSONEncoder, safe=True, json_dumps_params=None, **kwargs):
        if safe and not isinstance(data, dict):
            raise TypeError(
                'In order to allow non-dict objects to be serialized set the '
                'safe parameter to False.'
            )
        if json_dumps_params is None:
            json_dumps_params = dict()
        kwargs.setdefault('content_type', 'application/json')
        self.container_data = data
        data = json.dumps(data, cls=encoder, **json_dumps_params)
        super().__init__(content=data, **kwargs)


class JsonResponseLookup(HttpResponse):

    def __init__(self, data, encoder=JSONEncoder, safe=True, json_dumps_params=None, **kwargs):
        if safe and not isinstance(data, dict):
            raise TypeError(
                'In order to allow non-dict objects to be serialized set the '
                'safe parameter to False.'
            )
        if json_dumps_params is None:
            json_dumps_params = dict()

        kwargs.setdefault('content_type', 'application/json')
        self.container_data = data.copy()

        _data = self.container_data.get('response').get('data')
        _data_clear = dict()

        for key, value in _data.items():
            if not isinstance(value, FieldFile):
                setAttr(_data_clear, key, value)
            if isinstance(value, BitHandler):
                setAttr(_data_clear, key, value._value)

        data['response']['data'] = _data_clear

        data = json.dumps(data, cls=encoder, **json_dumps_params)
        super().__init__(content=data, **kwargs)
