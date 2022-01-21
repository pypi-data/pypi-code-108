'''_1450.py

LengthMedium
'''


from mastapy.utility.units_and_measurements import _1398
from mastapy._internal.python_net import python_net_import

_LENGTH_MEDIUM = python_net_import('SMT.MastaAPI.Utility.UnitsAndMeasurements.Measurements', 'LengthMedium')


__docformat__ = 'restructuredtext en'
__all__ = ('LengthMedium',)


class LengthMedium(_1398.MeasurementBase):
    '''LengthMedium

    This is a mastapy class.
    '''

    TYPE = _LENGTH_MEDIUM

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LengthMedium.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
