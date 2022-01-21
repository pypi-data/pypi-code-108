'''_1407.py

AnglePerUnitTemperature
'''


from mastapy.utility.units_and_measurements import _1398
from mastapy._internal.python_net import python_net_import

_ANGLE_PER_UNIT_TEMPERATURE = python_net_import('SMT.MastaAPI.Utility.UnitsAndMeasurements.Measurements', 'AnglePerUnitTemperature')


__docformat__ = 'restructuredtext en'
__all__ = ('AnglePerUnitTemperature',)


class AnglePerUnitTemperature(_1398.MeasurementBase):
    '''AnglePerUnitTemperature

    This is a mastapy class.
    '''

    TYPE = _ANGLE_PER_UNIT_TEMPERATURE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'AnglePerUnitTemperature.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
