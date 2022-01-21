'''_1452.py

LengthShort
'''


from mastapy.utility.units_and_measurements import _1398
from mastapy._internal.python_net import python_net_import

_LENGTH_SHORT = python_net_import('SMT.MastaAPI.Utility.UnitsAndMeasurements.Measurements', 'LengthShort')


__docformat__ = 'restructuredtext en'
__all__ = ('LengthShort',)


class LengthShort(_1398.MeasurementBase):
    '''LengthShort

    This is a mastapy class.
    '''

    TYPE = _LENGTH_SHORT

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LengthShort.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
