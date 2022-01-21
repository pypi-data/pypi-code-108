'''_1456.py

LengthVeryShortPerLengthShort
'''


from mastapy.utility.units_and_measurements import _1398
from mastapy._internal.python_net import python_net_import

_LENGTH_VERY_SHORT_PER_LENGTH_SHORT = python_net_import('SMT.MastaAPI.Utility.UnitsAndMeasurements.Measurements', 'LengthVeryShortPerLengthShort')


__docformat__ = 'restructuredtext en'
__all__ = ('LengthVeryShortPerLengthShort',)


class LengthVeryShortPerLengthShort(_1398.MeasurementBase):
    '''LengthVeryShortPerLengthShort

    This is a mastapy class.
    '''

    TYPE = _LENGTH_VERY_SHORT_PER_LENGTH_SHORT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LengthVeryShortPerLengthShort.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
