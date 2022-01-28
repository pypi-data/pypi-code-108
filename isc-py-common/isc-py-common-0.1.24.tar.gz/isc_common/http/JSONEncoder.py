from bitfield import BitHandler
from django.core.serializers.json import DjangoJSONEncoder


class JSONEncoder(DjangoJSONEncoder):
    """
    JSONEncoder subclass that knows how to encode date/time, decimal types, and
    UUIDs.
    """

    def default(self, o):
        if isinstance(o, BitHandler):
            return o._value
        else:
            return super().default(o)
