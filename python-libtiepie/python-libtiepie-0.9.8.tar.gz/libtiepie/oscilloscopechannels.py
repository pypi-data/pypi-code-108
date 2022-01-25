from .objectlist import ObjectList
from .api import api
from .oscilloscopechannel import OscilloscopeChannel


class OscilloscopeChannels(ObjectList):
    """"""

    def __init__(self, handle):
        super(OscilloscopeChannels, self).__init__()
        self._items = [OscilloscopeChannel(handle, i)
                       for i in range(api.ScpGetChannelCount(handle))]
