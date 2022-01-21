'''_1455.py

LengthVeryShort
'''


from mastapy.utility.units_and_measurements import _1398
from mastapy._internal.python_net import python_net_import

_LENGTH_VERY_SHORT = python_net_import('SMT.MastaAPI.Utility.UnitsAndMeasurements.Measurements', 'LengthVeryShort')


__docformat__ = 'restructuredtext en'
__all__ = ('LengthVeryShort',)


class LengthVeryShort(_1398.MeasurementBase):
    '''LengthVeryShort

    This is a mastapy class.
    '''

    TYPE = _LENGTH_VERY_SHORT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LengthVeryShort.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
