from isc_common import Wrapper


class Criterion(Wrapper):
    criteria = None
    end = None
    fieldName = None
    operator = None
    start = None
    value = None
    valuePath = None

    def __str__(self):
        return super().__str__()
