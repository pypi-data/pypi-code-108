from ctypes import c_char_p
from ...core_interface import po_interface
from orjson import orjson as json


class CoreHandler(object):
    def __init__(self, rule, method) -> None:
        super(CoreHandler, self).__init__()
        self._method = method
        self._rule = rule

    def handle_callback(self, method_data, data) -> bool:
        core_data = {
            'args': data['args'],
            'data': data['result'],
            'context': self._rule.context
        }

        str_data = json.dumps(core_data, default=lambda o: {})
        result, out_data_type, out_data_size, mem_buffer_id = po_interface.invoke(
            self._method, str_data, len(str_data))

        val = c_char_p(result).value
        result = val.decode('utf-8')
        po_interface.release(mem_buffer_id)

        try:
            return json.loads(result)
        except ValueError as e:
            return result
