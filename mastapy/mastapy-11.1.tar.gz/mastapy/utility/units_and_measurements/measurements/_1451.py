'''_1451.py

LengthPerUnitTemperature
'''


from mastapy.utility.units_and_measurements import _1398
from mastapy._internal.python_net import python_net_import

_LENGTH_PER_UNIT_TEMPERATURE = python_net_import('SMT.MastaAPI.Utility.UnitsAndMeasurements.Measurements', 'LengthPerUnitTemperature')


__docformat__ = 'restructuredtext en'
__all__ = ('LengthPerUnitTemperature',)


class LengthPerUnitTemperature(_1398.MeasurementBase):
    '''LengthPerUnitTemperature

    This is a mastapy class.
    '''

    TYPE = _LENGTH_PER_UNIT_TEMPERATURE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'LengthPerUnitTemperature.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
