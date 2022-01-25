from .objectlist import ObjectList
from .api import api
from .library import library
from .triggerinput import TriggerInput


class TriggerInputs(ObjectList):
    """"""

    def __init__(self, handle):
        super(TriggerInputs, self).__init__()
        self._handle = handle
        self._items = [TriggerInput(handle, i)
                       for i in range(api.DevTrGetInputCount(handle))]

    def get_by_id(self, id):
        index = api.DevTrGetInputIndexById(self._handle, id)
        library.check_last_status_raise_on_error()
        if index < len(self._items):
            return self._items[index]
        return None
