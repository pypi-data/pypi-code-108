'''_1505.py

TorquePerUnitTemperature
'''


from mastapy.utility.units_and_measurements import _1398
from mastapy._internal.python_net import python_net_import

_TORQUE_PER_UNIT_TEMPERATURE = python_net_import('SMT.MastaAPI.Utility.UnitsAndMeasurements.Measurements', 'TorquePerUnitTemperature')


__docformat__ = 'restructuredtext en'
__all__ = ('TorquePerUnitTemperature',)


class TorquePerUnitTemperature(_1398.MeasurementBase):
    '''TorquePerUnitTemperature

    This is a mastapy class.
    '''

    TYPE = _TORQUE_PER_UNIT_TEMPERATURE

    __hash__ = None

    def __init__(self, instance_to_wrap: 'TorquePerUnitTemperature.TYPE'):
        super().__init__(instance_to_wrap)
        self._freeze()
