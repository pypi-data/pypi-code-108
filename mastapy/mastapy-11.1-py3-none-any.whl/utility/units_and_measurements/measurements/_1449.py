'''_1449.py

LengthLong
'''


from mastapy.utility.units_and_measurements import _1398
from mastapy._internal.python_net import python_net_import

_LENGTH_LONG = python_net_import('SMT.MastaAPI.Utility.UnitsAndMeasurements.Measurements', 'LengthLong')


__docformat__ = 'restructuredtext en'
__all__ = ('LengthLong',)


class LengthLong(_1398.MeasurementBase):
    '''LengthLong

    This is a mastapy class.
    '''

    TYPE = _LENGTH_LONG

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LengthLong.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
